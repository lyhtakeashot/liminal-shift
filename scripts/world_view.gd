extends Control

## 把当前帧的 shapes 直接画出来。没有图片资源、没有场景继承 —— 全是数据。
##
## 时间轴模式下做三件事（HANDOFF §2.3）：
## 1. 去饱和（世界是灰的，角色是唯一有颜色的）
## 2. 轻微色差（红/青各偏 1px 叠一层）
## 3. 暗角收紧
##
## 这些都在 _draw 里做，不用 shader —— 灰盒阶段改一个数就见效。
##
## 2026-11-22 星露谷视觉机制（DECIDE D3/D4 · house-spec §4.8.2）：
## 绘制分两层：
##   背景层 Back   地面 / 河 / 田 / 路 / 房子 lot 底色 / 房间色块 —— 固定顺序，不排序
##   前景层 Front  墙 / 屋顶 / 门洞 / 家具 / 树 / 井 / 碑 / 玩家 —— **按 sort_y 排序**
##
## sort_y = 精灵的**底边（脚那条线）**，不是中心：
##   玩家   position.y + RADIUS * 0.7
##   树/井  center.y + radius * 0.7
##   家具   占地 rect 的底边 rect.end.y
##   墙     该行墙格格子的南沿（= 行号 + 1 格）
##   屋顶   wings 的南沿
##
## 玩家画在 world_view 里（player.gd 只剩状态载体）：z_index 插不进 `_draw()` 内部顺序，
## 靠节点 z_index 做遮挡在兄弟节点（WorldView / Player）之间根本做不到。
##
## 为什么墙要**按行**拆开排：
##   一栋房子如果只当一个整体（sort_y = 屋体南沿），那么「玩家站在隔断南边」时，
##   整栋（含隔断）都排在玩家后面 → 隔断会把玩家盖住，明明玩家在隔断前面。
##   拆成「一行墙 = 一个条目」之后，玩家能和每一行墙各自比深度，
##   站在墙南边 → 玩家挡住墙；站在墙北边 → 墙挡住玩家。这才是俯视游戏的正确遮挡。

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
# 每帧由 main.gd 通过 set_player_state() 灌进来；房间是逐帧数据，不缓存布尔（§4.8.4 陷阱）。
var player_pos := Vector2.ZERO

# 玩家节点（只当状态载体）。由 main.gd 通过 set_player_ref() 注入。
var player_ref: Node2D = null

# 玩家状态缓存 —— 只为了判「要不要重画」，避免每帧整页重绘。
var _p_facing := Vector2.ZERO
var _p_walking := false
var _p_walk_phase := 0.0
var _p_bump := 0.0
var _p_time := false


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


## 玩家状态通路（排序需要的全套）：pos / facing / walking / walk_phase / bump_kick / time_mode。
## 任何一项变了才重画；走路时 walk_phase 一直在变 → 本来也会因为位置变而重绘，不额外花钱。
func set_player_state(p: Vector2, facing: Vector2, walking: bool, walk_phase: float,
		bump_kick: float, is_time: bool) -> void:
	var changed := (not p.is_equal_approx(player_pos)) \
		or (not facing.is_equal_approx(_p_facing)) \
		or (walking != _p_walking) \
		or (not is_equal_approx(walk_phase, _p_walk_phase)) \
		or (not is_equal_approx(bump_kick, _p_bump)) \
		or (is_time != _p_time)
	player_pos = p
	_p_facing = facing
	_p_walking = walking
	_p_walk_phase = walk_phase
	_p_bump = bump_kick
	_p_time = is_time
	if changed:
		queue_redraw()


## 注入玩家节点：它的像素由本节点在排序循环里画（player.gd 只剩状态）。
func set_player_ref(p: Node2D) -> void:
	player_ref = p
	if p != null:
		p.set("draw_target", self)
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
		_draw_scene(Vector2.ZERO, Color(1, 1, 1, 1), 1.0, false)
		return

	# 色差：红往左、青往右，各偏 1px，低透明度
	_draw_scene(Vector2(-1, 0) + shake_off, Color(1.0, 0.55, 0.55, 1.0), 0.45, true)
	_draw_scene(Vector2(1, 0) + shake_off, Color(0.55, 0.85, 1.0, 1.0), 0.45, true)
	_draw_scene(shake_off, Color(1, 1, 1, 1), 1.0, true)

	_draw_vignette()


## 去饱和 + 年代染色
func _grade(c: Color) -> Color:
	if not time_mode:
		return c
	var l := c.get_luminance()
	var g := Color(l, l, l, c.a)
	return g.lerp(Color(l * year_tint.r, l * year_tint.g, l * year_tint.b, c.a), 0.5)


## 一遍场景 = 背景层 + 前景层（前景层内部按 sort_y 排）。
func _draw_scene(offset: Vector2, tint: Color, alpha_mul: float, grade: bool) -> void:
	_draw_back(offset, tint, alpha_mul, grade)
	_draw_front(offset, tint, alpha_mul, grade)


## 背景层：地面铺装 + 房子的 lot 底色/房间色块。固定顺序，不参与排序。
func _draw_back(offset: Vector2, tint: Color, alpha_mul: float, grade: bool) -> void:
	for s in frame.shapes:
		var sd: Dictionary = s
		var c: Color = Color(String(sd.get("color", "#888888")))
		if grade:
			c = _grade(c)
		c = Color(c.r * tint.r, c.g * tint.g, c.b * tint.b, c.a * alpha_mul)

		var label := String(sd.get("label", ""))
		var stype := String(sd.get("type", ""))

		if stype == "house":
			_draw_house_base(sd, offset, tint, alpha_mul, grade)
		elif stype == "circle":
			# 树/井是立着的物件 → 前景层排序
			pass
		elif stype == "rect":
			if _is_standing_rect(sd):
				pass
			else:
				var r: Array = sd.get("rect", [0, 0, 0, 0])
				var rect := Rect2(float(r[0]), float(r[1]), float(r[2]), float(r[3]))
				draw_rect(Rect2(rect.position + offset, rect.size), c, true)
				if label != "" and offset == Vector2.ZERO:
					_draw_label(label, rect.position + offset + Vector2(3, 10), c)
		elif stype == "path":
			var pts: Array = []
			for p in sd.get("points", []):
				var pa: Array = p
				pts.append(Vector2(float(pa[0]), float(pa[1])) + offset)
			if pts.size() >= 2:
				draw_polyline(pts, c, float(sd.get("width", 20)), true)
		elif stype == "polygon":
			# 任意多边形填充（河这类下缘弯曲的地形，用折线描不出形状）
			var poly: PackedVector2Array = PackedVector2Array()
			for p in sd.get("points", []):
				var pa: Array = p
				poly.append(Vector2(float(pa[0]), float(pa[1])) + offset)
			if poly.size() >= 3:
				draw_colored_polygon(poly, c)


## 这个 rect 是不是「立着的物件」（该参与 y-sort）。
## 规则：solid 且占地小（宽 ≤ 一格、高 ≤ 两格）→ 立着（界碑这类）。
## 地面铺装（road:true 的路、田块、坝）→ 不参与排序，永远在背景层。
func _is_standing_rect(sd: Dictionary) -> bool:
	if bool(sd.get("road", false)):
		return false
	if not bool(sd.get("solid", false)):
		return false
	var r: Array = sd.get("rect", [0, 0, 0, 0])
	return float(r[2]) <= HouseShape.TILE and float(r[3]) <= HouseShape.TILE * 2.0


## 前景层：收集可排序物件 → 按 sort_y（底边）排 → 依次画。
## 玩家是其中一条（不再是独立的 z_index=10 节点）。
func _draw_front(offset: Vector2, tint: Color, alpha_mul: float, grade: bool) -> void:
	for ent in _collect_front():
		var e: Dictionary = ent
		match String(e["kind"]):
			"walls":
				var sid := String(e["sid"])
				var texs := _house_tex(sid)
				var wall_col := _shade(HouseShape.WALL_COLOR, tint, alpha_mul, grade)
				var top_col := _shade(HouseShape.WALL_TOP, tint, alpha_mul, grade)
				_draw_walls_row(e["cells"], offset, wall_col, top_col, texs["base"] == null)
			"door":
				var dd: Dictionary = e["d"]
				var dc: Color = HouseShape.GATE_COLOR if bool(dd["gate"]) else HouseShape.DOOR_COLOR
				var dr: Rect2 = dd["rect"]
				draw_rect(Rect2(dr.position + offset, dr.size),
					_shade(dc, tint, alpha_mul, grade), true)
			"roof":
				_draw_roof(e["data"], e["hpos"], offset, tint, alpha_mul, grade,
					_house_tex(String(e["sid"]))["roof"])
			"furniture":
				_draw_furniture(e["f"], offset, tint, alpha_mul, grade)
			"prop":
				_draw_prop(e["sd"], offset, tint, alpha_mul, grade)
			"player":
				var p := player_ref
				if p != null and p.has_method("draw_self"):
					p.call("draw_self", offset)


## 收集前景层条目并排序。
## 排序键统一 = 精灵底边（脚那条线）：
##   玩家   position.y + RADIUS * 0.7
##   树/井  center.y + radius * 0.7
##   家具   占地 rect 的底边 rect.end.y
##   墙     该行格子的南沿
##   屋顶   wings 南沿
## seq 是「同深度时的稳定序」：sort_custom 不保证稳定，必须自己带一个全序字段。
func _collect_front() -> Array:
	var ents: Array = []
	for s in frame.shapes:
		var sd: Dictionary = s
		match String(sd.get("type", "")):
			"house":
				var sid := String(sd.get("id", ""))
				var sp: Array = sd.get("pos", [0, 0])
				var hpos := Vector2(float(sp[0]), float(sp[1]))
				var data := HouseShape.house(sid)
				if data.is_empty():
					continue
				# ---- 墙：按行拆成多个排序条目（每行墙格子的南沿 = 那一行的脚线）----
				var rows := {}
				for c in HouseShape.wall_render_cells(data, hpos):
					var cd: Dictionary = c
					var rr: Rect2 = cd["rect"]
					var ry := int(round((rr.position.y - hpos.y) / HouseShape.TILE))
					if not rows.has(ry):
						rows[ry] = []
					rows[ry].append(cd)
				for ry in rows.keys():
					ents.append({
						"kind": "walls", "sid": sid, "cells": rows[ry],
						"sort_y": hpos.y + (float(int(ry)) + 1.0) * HouseShape.TILE,
						"seq": ents.size(),
					})
				# ---- 门洞：地面层的开口，跟它所在行同深度 ----
				for d in HouseShape.door_rects(data, hpos):
					var dd: Dictionary = d
					var dr: Rect2 = dd["rect"]
					var dry := int(round((dr.position.y - hpos.y) / HouseShape.TILE))
					ents.append({
						"kind": "door", "d": dd,
						"sort_y": hpos.y + (float(dry) + 1.0) * HouseShape.TILE,
						"seq": ents.size(),
					})
				# ---- 屋顶：整栋一块，深度 = wings 南沿（玩家进屋就不画）----
				ents.append({
					"kind": "roof", "sid": sid, "data": data, "hpos": hpos,
					"sort_y": _roof_sort_y(data, hpos), "seq": ents.size(),
				})
				# ---- 家具：独立物件，和玩家一起排序，才能「绕到桌后被挡」----
				for f in HouseShape.furniture_rects(data, hpos):
					var fr: Rect2 = f["rect"]
					ents.append({
						"kind": "furniture", "f": f,
						"sort_y": fr.end.y, "seq": ents.size(),
					})
			"circle":
				var cp: Array = sd.get("center", [0, 0])
				var rad := float(sd.get("radius", 4))
				ents.append({
					"kind": "prop", "sd": sd,
					"sort_y": float(cp[1]) + rad * 0.7, "seq": ents.size(),
				})
			"rect":
				if _is_standing_rect(sd):
					var r: Array = sd.get("rect", [0, 0, 0, 0])
					var rect := Rect2(float(r[0]), float(r[1]), float(r[2]), float(r[3]))
					ents.append({
						"kind": "prop", "sd": sd,
						"sort_y": rect.end.y, "seq": ents.size(),
					})

	# 玩家也进排序链（脚线 = position.y + RADIUS * 0.7）
	if player_ref != null:
		ents.append({
			"kind": "player",
			"sort_y": player_pos.y + 14.0 * 0.7, "seq": ents.size(),
		})

	ents.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		var ay := float(a["sort_y"])
		var by := float(b["sort_y"])
		if not is_equal_approx(ay, by):
			return ay < by
		return int(a["seq"]) < int(b["seq"]))
	return ents


## 屋顶的排序键 = wings 的南沿（屋体「站」着的那条线）。
static func _roof_sort_y(data: Dictionary, hpos: Vector2) -> float:
	var bottom := hpos.y
	for w in data.get("wings", []):
		var ww: Array = w
		bottom = maxf(bottom, hpos.y + (float(ww[1]) + float(ww[3])) * HouseShape.TILE)
	return bottom


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
## ⚠️ 缺图回色块的降级路径**永久保留**（DECIDE D8）——美术分批交付期间游戏始终可跑。
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


## 房子的背景部分：lot 底色（院子 + 地面）+ 房间色块。固定在背景层，不参与排序。
func _draw_house_base(sd: Dictionary, offset: Vector2, tint: Color,
		alpha_mul: float, grade: bool) -> void:
	var sid := String(sd.get("id", ""))
	var sp: Array = sd.get("pos", [0, 0])
	var hpos := Vector2(float(sp[0]), float(sp[1]))
	var data := HouseShape.house(sid)
	if data.is_empty():
		return

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


## 家具占位块 + 名字（可检视线索用橙框）。家具是独立排序条目，所以单独画。
func _draw_furniture(f: Dictionary, offset: Vector2, tint: Color,
		alpha_mul: float, grade: bool) -> void:
	var fr: Rect2 = f["rect"]
	var fc := HouseShape.FURN_COLOR if not f["clue"] else HouseShape.CLUE_COLOR
	draw_rect(Rect2(fr.position + offset, fr.size),
		_shade(fc, tint, alpha_mul, grade), true)
	if offset == Vector2.ZERO:
		_draw_label(String(f["name"]),
			fr.position + offset + Vector2(2, 10), HouseShape.WALL_COLOR)


## 立着的圆物件：树（加树干、树冠抬升）或井/水塘（平画）。
func _draw_prop(sd: Dictionary, offset: Vector2, tint: Color,
		alpha_mul: float, grade: bool) -> void:
	var stype := String(sd.get("type", ""))
	var label := String(sd.get("label", ""))
	var c: Color = Color(String(sd.get("color", "#888888")))
	if grade:
		c = _grade(c)
	c = Color(c.r * tint.r, c.g * tint.g, c.b * tint.b, c.a * alpha_mul)

	if stype == "circle":
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
	else:
		var r: Array = sd.get("rect", [0, 0, 0, 0])
		var rect := Rect2(float(r[0]), float(r[1]), float(r[2]), float(r[3]))
		draw_rect(Rect2(rect.position + offset, rect.size), c, true)
		if label != "" and offset == Vector2.ZERO:
			_draw_label(label, rect.position + offset + Vector2(3, 10), c)


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


## 墙体伪 3D（**一行**墙一次画完）。
## 每一格墙画三块（纯垂直抬升，house-spec §4.8.1：屏幕 y = 地面 y − 高度）：
##   本体   (bx, by,            w, TILE)  墙的落地格（被顶面/立面盖住）
##   顶面   (bx, by − h,        w, TILE)  墙顶，抬高 h
##   南立面 (bx, by + TILE − h, w, h)     朝南那一面，高 h
## 北/西墙 h = TILE（32px 全高），东/南墙 h = TILE/2（16px 半高）。
## 顺序不能反 —— 南北相邻的两格，南格的顶面正好盖住北格的立面，反了会看见墙格之间的缝。
## 性能：把同一行 y 上连续、**同高度**的墙格合并成一个矩形（gl_compatibility + Web 导出硬要求）。
## with_body=true 时连墙格本体一起画（缺美术图的降级路径）。
func _draw_walls_row(cells: Array, offset: Vector2, wall_col: Color,
		top_col: Color, with_body: bool) -> void:
	# 按高度分组：只有同高的连续墙格才能合并成一个矩形
	var groups := {}
	for c in cells:
		var cd: Dictionary = c
		var h := float(cd["height"])
		if not groups.has(h):
			groups[h] = []
		groups[h].append(cd["rect"])

	var heights: Array = groups.keys()
	heights.sort()
	for h in heights:
		var row: Array = groups[h]
		row.sort_custom(func(a: Rect2, b: Rect2) -> bool: return a.position.x < b.position.x)
		var hh := float(h)
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
			# 缺图降级：墙格本体也铺上（否则只有立面，地面那格是空的）
			if with_body:
				draw_rect(Rect2(Vector2(bx, by) + offset,
					Vector2(merged_w, HouseShape.TILE)), wall_col)
			# 墙顶面：地面轮廓整体抬高 h（h=32 全高 / h=16 半高）
			draw_rect(Rect2(Vector2(bx, by - hh) + offset,
				Vector2(merged_w, HouseShape.TILE)), top_col)
			# 南立面：墙高 h（正南方向看得见的那一面）
			draw_rect(Rect2(Vector2(bx, by + HouseShape.TILE - hh) + offset,
				Vector2(merged_w, hh)), wall_col)
			i = j


## 屋顶：按 wings 每翼一块，整体抬高 EXTRUDE。
## 翼必须按 y 从小到大画（南翼压北翼檐，house-spec §0.2）。
func _draw_roof(data: Dictionary, hpos: Vector2, offset: Vector2, tint: Color,
		alpha_mul: float, grade: bool, tex_roof: Texture2D) -> void:
	var wings: Array = data.get("wings", [])
	if wings.is_empty():
		return
	# 玩家在 wings 内 → 屋顶整块消失（house-spec §4.8.4，娃娃屋剖视，无渐变）
	if _player_inside(data, hpos):
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
