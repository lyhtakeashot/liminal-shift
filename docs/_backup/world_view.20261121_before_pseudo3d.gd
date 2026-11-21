extends Control

## 把当前帧的 shapes 直接画出来。没有图片资源、没有场景继承 —— 全是数据。
##
## 时间轴模式下做三件事（HANDOFF §2.3）：
## 1. 去饱和（世界是灰的，角色是唯一有颜色的）
## 2. 轻微色差（红/青各偏 1px 叠一层）
## 3. 暗角收紧
##
## 这些都在 _draw 里做，不用 shader —— 灰盒阶段改一个数就见效。

const FONT_SIZE := 9

const FrameData = preload("res://scripts/frame_data.gd")
const HouseShape = preload("res://scripts/house_shape.gd")

# 房子贴图缓存：id → Texture2D（null = 没有图，只查一次；不每帧 load 刷 ERROR）
static var _tex_cache := {}

var frame: FrameData = null
var time_mode := false
var font: Font = ThemeDB.fallback_font

# 时间轴模式下世界整体的一种冷暖偏移，让五个年代第一眼就能分开
var year_tint := Color(1, 1, 1, 1)

# 推不过去时的震动（§3.4 的「顶住了」反馈之一）
var _shake := 0.0
var _shake_dir := Vector2.ZERO


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func show_frame(f: FrameData, is_time: bool) -> void:
	frame = f
	time_mode = is_time
	queue_redraw()


func set_year_tint(c: Color) -> void:
	year_tint = c
	queue_redraw()


## 震屏。幅度很小，0.12 秒内衰减 —— 是「顶住了」不是「弹回去」。
func kick_shake(amount: float) -> void:
	_shake = maxf(_shake, amount)
	_shake_dir = Vector2(randf_range(-1.0, 1.0), randf_range(-1.0, 1.0)).normalized()
	queue_redraw()


func _process(delta: float) -> void:
	if _shake > 0.0:
		_shake = maxf(0.0, _shake - delta * 22.0)
		queue_redraw()


func _draw() -> void:
	if frame == null:
		return

	var shake_off := Vector2.ZERO
	if _shake > 0.0:
		shake_off = _shake_dir * _shake

	draw_rect(Rect2(Vector2.ZERO, size), _grade(frame.ground), true)

	if not time_mode:
		_draw_shapes(Vector2.ZERO, Color(1, 1, 1, 1), 1.0, false)
		return

	# 色差：红往左、青往右，各偏 1px，低透明度
	_draw_shapes(Vector2(-1, 0) + shake_off, Color(1.0, 0.55, 0.55, 1.0), 0.45, true)
	_draw_shapes(Vector2(1, 0) + shake_off, Color(0.55, 0.85, 1.0, 1.0), 0.45, true)
	_draw_shapes(shake_off, Color(1, 1, 1, 1), 1.0, true)

	_draw_vignette()


## 去饱和 + 年代染色
func _grade(c: Color) -> Color:
	if not time_mode:
		return c
	var l := c.get_luminance()
	var g := Color(l, l, l, c.a)
	return g.lerp(Color(l * year_tint.r, l * year_tint.g, l * year_tint.b, c.a), 0.5)


func _draw_shapes(offset: Vector2, tint: Color, alpha_mul: float, grade: bool) -> void:
	for s in frame.shapes:
		var sd: Dictionary = s
		var c: Color = Color(String(sd.get("color", "#888888")))
		if grade:
			c = _grade(c)
		c = Color(c.r * tint.r, c.g * tint.g, c.b * tint.b, c.a * alpha_mul)

		var label := String(sd.get("label", ""))

		match String(sd.get("type", "")):
			"rect":
				var r: Array = sd.get("rect", [0, 0, 0, 0])
				var rect := Rect2(float(r[0]), float(r[1]), float(r[2]), float(r[3]))
				draw_rect(Rect2(rect.position + offset, rect.size), c, true)
				if label != "" and offset == Vector2.ZERO:
					_draw_label(label, rect.position + offset + Vector2(3, 10), c)

			"circle":
				var cp: Array = sd.get("center", [0, 0])
				var center := Vector2(float(cp[0]), float(cp[1]))
				var rad := float(sd.get("radius", 4))
				draw_circle(center + offset, rad, c)
				if label != "" and offset == Vector2.ZERO:
					_draw_label(label, center + offset + Vector2(rad + 3, 3), c)

			"path":
				var pts: Array = []
				for p in sd.get("points", []):
					var pa: Array = p
					pts.append(Vector2(float(pa[0]), float(pa[1])) + offset)
				if pts.size() >= 2:
					draw_polyline(pts, c, float(sd.get("width", 20)), true)

			"polygon":
				# 任意多边形填充（河这类下缘弯曲的地形，用折线描不出形状）
				var poly: PackedVector2Array = PackedVector2Array()
				for p in sd.get("points", []):
					var pa: Array = p
					poly.append(Vector2(float(pa[0]), float(pa[1])) + offset)
				if poly.size() >= 3:
					draw_colored_polygon(poly, c)

			"house":
				_draw_house(sd, offset, tint, alpha_mul, grade)


## 取房子贴图（缓存；不存在只查一次，避免每帧 load 刷 ERROR）。
static func _house_tex(sid: String) -> Texture2D:
	if _tex_cache.has(sid):
		return _tex_cache[sid]
	var path := "res://assets/village/%s.png" % sid
	var tex: Texture2D = null
	if ResourceLoader.exists(path):
		tex = load(path) as Texture2D
	_tex_cache[sid] = tex
	return tex


## 画一栋房子，四层（BUILD-A1 §4.4）：
## 1. lot 底色（院子 + 地面）  2. 房间色块（rooms 配色 key）
## 3. 墙体（逐格棕色；门洞留空）  4. 家具占位块 + 名字
## 美术接进来以后第 2–4 层换贴图（assets/village/<id>.png），第 1 层保留。
## hpos 是世界坐标（不含 offset）；所有绘制统一加 offset（色差/震屏偏移）。
## 注意：颜色只做 grade/tint/alpha 处理，不乘形状的 color —— 房子每层用各自本色。
func _draw_house(sd: Dictionary, offset: Vector2, tint: Color, alpha_mul: float, grade: bool) -> void:
	var sid := String(sd.get("id", ""))
	var sp: Array = sd.get("pos", [0, 0])
	var hpos := Vector2(float(sp[0]), float(sp[1]))
	var data := HouseShape.house(sid)
	if data.is_empty():
		return

	var tex := _house_tex(sid)
	if tex != null:
		# 有美术图：直接画（占位块逻辑保留在 else 里，图缺了也不崩）
		var lot := HouseShape.lot_rect(data, Vector2.ZERO)
		var tc := Color.WHITE
		if grade:
			tc = _grade(tc)
		tc = Color(tc.r * tint.r, tc.g * tint.g, tc.b * tint.b, alpha_mul)
		draw_texture_rect(tex, Rect2(hpos + offset, lot.size), false, tc)
		return

	# ---- 第 1 层：lot 底色（院子 + 地面，可走）----
	var lot := HouseShape.lot_rect(data, hpos)
	draw_rect(Rect2(lot.position + offset, lot.size),
		_shade(HouseShape.YARD_COLOR, tint, alpha_mul, grade), true)
	draw_rect(Rect2(lot.position + offset, lot.size),
		_shade(HouseShape.LOT_OUTLINE, tint, alpha_mul, grade), false, 2.0)
	if offset == Vector2.ZERO:
		_draw_label(sid, lot.position + Vector2(2, 12), HouseShape.LOT_OUTLINE)

	# ---- 第 2 层：房间色块（按 rooms 的配色 key；房间不含墙）----
	for room in HouseShape.room_rects(data, hpos):
		var rc: Color = HouseShape.ROOM_COLORS.get(String(room["color_key"]), Color("#6b5842"))
		draw_rect(Rect2(room["rect"].position + offset, room["rect"].size),
			_shade(rc, tint, alpha_mul, grade), true)

	# ---- 第 3 层：墙体（逐格棕；门洞留空）----
	for r in HouseShape.solid_rects(data, hpos):
		draw_rect(Rect2(r.position + offset, r.size),
			_shade(HouseShape.WALL_COLOR, tint, alpha_mul, grade), true)

	# ---- 第 3b 层：门洞（房门黄、院门深棕；不参与碰撞，只是颜色）----
	for d in HouseShape.door_rects(data, hpos):
		var dc: Color = HouseShape.GATE_COLOR if bool(d["gate"]) else HouseShape.DOOR_COLOR
		var dr: Rect2 = d["rect"]
		draw_rect(Rect2(dr.position + offset, dr.size),
			_shade(dc, tint, alpha_mul, grade), true)

	# ---- 第 4 层：家具占位块 + 名字（可检视线索用橙框）----
	for f in HouseShape.furniture_rects(data, hpos):
		var fr: Rect2 = f["rect"]
		var fc := HouseShape.FURN_COLOR if not f["clue"] else HouseShape.CLUE_COLOR
		draw_rect(Rect2(fr.position + offset, fr.size),
			_shade(fc, tint, alpha_mul, grade), true)
		if offset == Vector2.ZERO:
			_draw_label(String(f["name"]),
				fr.position + offset + Vector2(2, 10), HouseShape.WALL_COLOR)


## 对一个颜色应用 grade（去饱和+年代染色）、tint、alpha 系数。
func _shade(col: Color, tint: Color, alpha_mul: float, grade: bool) -> Color:
	var c := col
	if grade:
		c = _grade(c)
	return Color(c.r * tint.r, c.g * tint.g, c.b * tint.b, c.a * alpha_mul)


func _draw_label(text: String, at: Vector2, bg: Color) -> void:
	var lum := bg.get_luminance()
	var col := Color(0.05, 0.05, 0.05, 0.75) if lum > 0.45 else Color(0.95, 0.95, 0.9, 0.7)
	draw_string(font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_SIZE, col)


func _draw_vignette() -> void:
	var steps := 10
	var depth := 56.0
	for i in steps:
		var t := float(i) / float(steps)
		var a := 0.055 * (1.0 - t) * (1.0 - t) * 6.0
		var inset := depth * t
		var col := Color(0, 0, 0, clampf(a, 0.0, 0.5))
		var r := Rect2(inset, inset, size.x - inset * 2.0, size.y - inset * 2.0)
		draw_rect(r, col, false, depth / float(steps) + 1.0)