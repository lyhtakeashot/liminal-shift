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

## 伪 3D 抬升高度 = 一整格（house-spec §4.8.1 已定）。
## 写死在代码里，不进 frames.json、不进 houses_data.json：
## 1926→2026 是同几栋实体房子，高度不随时间变。给了逐帧字段，
## 迟早有人微调成「推时间时房子在呼吸」。
const EXTRUDE := 32.0

## 屋顶用色（必须和墙有好区分，§4.8.2 明确「屋顶要能一眼区分是屋顶」）。
const ROOF_COLOR := Color("#6b4b3e")        # 瓦面：偏褐红
const ROOF_RIDGE := Color("#8f6a56")        # 屋脊：亮一档
const ROOF_EAVE := Color("#4a342c")         # 檐边：暗一档
const TRUNK_COLOR := Color("#5a4433")       # 树干

# 房子贴图缓存：id → {base, roof}（null = 没有图，只查一次；不每帧 load 刷 ERROR）
static var _tex_cache := {}

var frame: FrameData = null
var time_mode := false
var font: Font = ThemeDB.fallback_font

# 时间轴模式下世界整体的一种冷暖偏移，让五个年代第一眼就能分开
var year_tint := Color(1, 1, 1, 1)

# 推不过去时的震动（§3.4 的「顶住了」反馈之一）
var _shake := 0.0
var _shake_dir := Vector2.ZERO

# 玩家世界坐标。用来判「玩家是不是站在这栋房子的 wings 里」→ 决定画不画屋顶。
# 每帧由 main.gd 通过 set_player_pos() 灌进来；房间是逐帧数据，不缓存布尔（§4.8.4 陷阱）。
var player_pos := Vector2.ZERO


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


## 玩家位置变了才重画（每帧都在调，必须做等值判断，否则整页每帧重绘）。
func set_player_pos(p: Vector2) -> void:
	if p.is_equal_approx(player_pos):
		return
	player_pos = p
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
				# 树：label 含「槐」才加树干（老井也是 circle，label 是「老井·XX」，别误加）
				var is_tree := label.find("槐") >= 0
				if is_tree and rad >= 12.0:
					# 树干（先画，树冠抬高压在上面）
					draw_rect(Rect2(center + offset + Vector2(-2, rad * 0.22),
						Vector2(4, rad * 0.85)), _shade(TRUNK_COLOR, tint, alpha_mul, grade))
					# 树冠上抬 rad*0.7，做出立体感
					var lifted := center + offset + Vector2(0, -rad * 0.7)
					draw_circle(lifted, rad, c)
					# 树冠亮部（左上受光，house-spec §1 光从左上来）
					draw_circle(lifted + Vector2(-rad * 0.25, -rad * 0.25), rad * 0.55,
						Color(c.r * 1.18, c.g * 1.18, c.b * 1.18, c.a))
				else:
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


## 房子 id → (族, 帧)，与 _ref/houses/gen_asset_breakdown.py 的 FAMILY 表一致。
## 美术交付路径是 assets/village/houses/<族>/<帧>_base.png 和 _roof.png（house-spec §4.8.5）。
const FAMILY := {
	"lu_house": ["lu", "a1"], "lu_a2": ["lu", "a2"], "lu_a3": ["lu", "a3"],
	"shen_a1": ["shen", "a1"], "shen_a2": ["shen", "a2"], "shen_a3": ["shen", "a3"],
	"mill_a1": ["mill", "a1"], "mill_a2": ["mill", "a2"], "mill_a3": ["mill", "a3"],
	"zhou_house": ["zhou", "a1"], "zhou_a2": ["zhou", "a2"], "zhou_a3": ["zhou", "a3"],
}


## 取房子贴图（缓存；不存在只查一次，避免每帧 load 刷 ERROR）。
## 返回 {"base": Texture2D|null, "roof": Texture2D|null}。
static func _house_tex(sid: String) -> Dictionary:
	if _tex_cache.has(sid):
		return _tex_cache[sid]
	var out := {"base": null, "roof": null}
	var fam: Array = FAMILY.get(sid, [])
	if fam.size() == 2:
		var dir := "res://assets/village/houses/%s/" % fam[0]
		for key in ["base", "roof"]:
			var path: String = dir + String(fam[1]) + "_" + key + ".png"
			if ResourceLoader.exists(path):
				out[key] = load(path) as Texture2D
	_tex_cache[sid] = out
	return out


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

	var texs := _house_tex(sid)
	var tex_base: Texture2D = texs["base"]
	var tex_roof: Texture2D = texs["roof"]

	# ---- 第 1 层：lot 底色（院子 + 地面，可走）----
	var lot := HouseShape.lot_rect(data, hpos)
	draw_rect(Rect2(lot.position + offset, lot.size),
		_shade(HouseShape.YARD_COLOR, tint, alpha_mul, grade), true)
	draw_rect(Rect2(lot.position + offset, lot.size),
		_shade(HouseShape.LOT_OUTLINE, tint, alpha_mul, grade), false, 2.0)
	if offset == Vector2.ZERO:
		_draw_label(sid, lot.position + Vector2(2, 12), HouseShape.LOT_OUTLINE)

	# ---- 第 2 层：房间色块 ----
	for room in HouseShape.room_rects(data, hpos):
		var rc: Color = HouseShape.ROOM_COLORS.get(String(room["color_key"]), Color("#6b5842"))
		draw_rect(Rect2(room["rect"].position + offset, room["rect"].size),
			_shade(rc, tint, alpha_mul, grade), true)

	# ---- 第 3 层：墙（有 base 图则只画墙的立体部分，缺图才画满格）----
	var wall_col := _shade(HouseShape.WALL_COLOR, tint, alpha_mul, grade)
	var top_col := _shade(HouseShape.WALL_TOP, tint, alpha_mul, grade)
	_draw_walls_lifted(HouseShape.solid_rects(data, hpos), offset, wall_col, top_col, tex_base == null)

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

	# ---- 第 5 层：屋顶（玩家在 wings 内就不画 —— house-spec §4.8.4，娃娃屋剖视）----
	if not _player_inside(data, hpos):
		_draw_roof(data, hpos, offset, tint, alpha_mul, grade, tex_roof)


## 玩家是否站在这栋房子的屋体（wings）内。
## 与时间轴无关、精确判定、不做 alpha 渐变 —— 用户 2026-11-21 拍板（house-spec §4.8.4）。
## 必须拿当前帧的 wings 现算，不能缓存「进屋了」布尔（同一位置换帧后 wings 会变）。
func _player_inside(data: Dictionary, hpos: Vector2) -> bool:
	for w in data.get("wings", []):
		var ww: Array = w
		var wr := Rect2(
			hpos + Vector2(float(ww[0]), float(ww[1])) * HouseShape.TILE,
			Vector2(float(ww[2]), float(ww[3])) * HouseShape.TILE)
		if wr.has_point(player_pos):
			return true
	return false


## 墙体伪 3D：逐格「先南立面、后墙顶面」。
## 顺序不能反 —— 南北相邻的两格，南格的顶面正好盖住北格的立面，反了会看见墙格之间的缝。
## 性能：把同一行 y 上连续的墙格合并成一个矩形（gl_compatibility + Web 导出硬要求）。
## with_body=true 时连墙格本体一起画（缺美术图的降级路径）。
func _draw_walls_lifted(rects: Array, offset: Vector2, wall_col: Color,
		top_col: Color, with_body: bool) -> void:
	# solid_rects 已按行输出，直接按 y 分组
	var by_row := {}
	for r in rects:
		var rr: Rect2 = r
		var key := int(rr.position.y)
		if not by_row.has(key):
			by_row[key] = []
		by_row[key].append(rr)

	for y in by_row.keys():
		var row: Array = by_row[y]
		row.sort_custom(func(a: Rect2, b: Rect2) -> bool: return a.position.x < b.position.x)
		# 合并同行的连续段
		var i := 0
		while i < row.size():
			var start: Rect2 = row[i]
			var end_x: float = start.position.x + start.size.x
			var j := i + 1
			while j < row.size():
				var nxt: Rect2 = row[j]
				if absf(nxt.position.x - end_x) < 0.01:
					end_x = nxt.position.x + nxt.size.x
					j += 1
				else:
					break
			var merged_w := end_x - start.position.x
			var bx := start.position.x
			var by := start.position.y
			# 南立面：整个墙格向下延伸 EXTRUDE（EXTRUDE=TILE 时正好等于整格）
			draw_rect(Rect2(Vector2(bx, by + HouseShape.TILE - EXTRUDE) + offset,
				Vector2(merged_w, EXTRUDE)), wall_col)
			if with_body:
				# 缺图降级：墙格本体也铺上（否则只有立面，地面那格是空的）
				draw_rect(Rect2(Vector2(bx, by) + offset,
					Vector2(merged_w, HouseShape.TILE)), wall_col)
			# 墙顶面：抬高 EXTRUDE
			draw_rect(Rect2(Vector2(bx, by - EXTRUDE) + offset,
				Vector2(merged_w, HouseShape.TILE)), top_col)
			i = j


## 屋顶：按 wings 每翼一块，整体抬高 EXTRUDE。
## 翼必须按 y 从小到大画（南翼压北翼檐，house-spec §0.2）。
func _draw_roof(data: Dictionary, hpos: Vector2, offset: Vector2, tint: Color,
		alpha_mul: float, grade: bool, tex_roof: Texture2D) -> void:
	var wings: Array = data.get("wings", [])
	if wings.is_empty():
		return
	var roof_col := _shade(ROOF_COLOR, tint, alpha_mul, grade)
	var ridge_col := _shade(ROOF_RIDGE, tint, alpha_mul, grade)
	var eave_col := _shade(ROOF_EAVE, tint, alpha_mul, grade)

	var sorted_wings := wings.duplicate()
	sorted_wings.sort_custom(func(a: Array, b: Array) -> bool: return int(a[1]) < int(b[1]))

	for w in sorted_wings:
		var ww: Array = w
		var wx := float(ww[0])
		var wy := float(ww[1])
		var wpx := float(ww[2]) * HouseShape.TILE
		var wpy := float(ww[3]) * HouseShape.TILE
		# 外扩 1px 做出檐，整体抬高 EXTRUDE
		var r := Rect2(Vector2(hpos.x + wx * HouseShape.TILE - 1.0, hpos.y + wy * HouseShape.TILE - 1.0 - EXTRUDE) + offset,
			Vector2(wpx + 2.0, wpy + 2.0))
		draw_rect(r, roof_col, true)
		# 屋脊：沿该翼长轴，亮一档
		if wpx >= wpy:
			var ry := r.position.y + r.size.y * 0.5
			draw_line(Vector2(r.position.x, ry), Vector2(r.position.x + r.size.x, ry), ridge_col, 2.0)
		else:
			var rx := r.position.x + r.size.x * 0.5
			draw_line(Vector2(rx, r.position.y), Vector2(rx, r.position.y + r.size.y), ridge_col, 2.0)
		# 檐边：底边暗一档
		draw_line(Vector2(r.position.x, r.position.y + r.size.y),
			Vector2(r.position.x + r.size.x, r.position.y + r.size.y), eave_col, 1.0)

	# 有美术屋顶图：整张铺上去（画布高 = lot_h + TILE，顶部多出的一格是墙+屋顶）
	if tex_roof != null:
		var lot0 := HouseShape.lot_rect(data, Vector2.ZERO)
		var tc := Color.WHITE
		if grade:
			tc = _grade(tc)
		tc = Color(tc.r * tint.r, tc.g * tint.g, tc.b * tint.b, alpha_mul)
		draw_texture_rect(tex_roof,
			Rect2(Vector2(hpos.x, hpos.y - EXTRUDE) + offset,
				Vector2(lot0.size.x, lot0.size.y + EXTRUDE)), false, tc)


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