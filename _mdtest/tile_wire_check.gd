extends SceneTree

## L8 资产接线验收：**32px 平铺通路**是否真的在画「贴图」而不是「色块」。
##
## 两种跑法：
##   窗口模式（**有像素证据**，本机可用）：
##     godot --path . -s res://_mdtest/tile_wire_check.gd
##   无窗口（只有逻辑断言，像素部分自动跳过）：
##     godot --headless --path . -s res://_mdtest/tile_wire_check.gd
##
## 为什么必须窗口模式：headless 用的 dummy 渲染器读不到帧缓冲，
## `get_texture().get_image()` 拿不到真实像素 —— 那样「这不是色块」就不算证据（§4.4）。
##
## 判据：
##   PASS  = 该区域应当有贴图，且 32×32 格内取到 ≥3 种颜色；
##   GAP   = 美术缺口（缺图走纯色降级），**只登记不静默**，计进 gaps 不计进 fails（C4）；
##   FAIL  = 该有贴图却没有 / 取到的颜色种类不足（真红）。
##
## 采样坐标 = 世界坐标。世界图层直接挂在根窗口上、`position = -origin` 把目标区域推到屏幕中央，
## 所以「屏幕像素 = 世界坐标 - origin」，不需要相机。

const AssetDraw = preload("res://scripts/asset_draw.gd")
const FrameData = preload("res://scripts/frame_data.gd")
const WorldView = preload("res://scripts/world_view.gd")

const TILE := 32.0
const FRAMES := ["a1_1926", "a2_1951", "a3_1976", "a4_2001", "a5_2026"]
const WORLD := Vector2(4800, 3600)

## 已知美术缺口：这些 label 现在只能画纯色（缺 32×32 瓦片），登记进 GAP 行。
const KNOWN_GAP := ["山"]

const WATER_PROBE := Color("#3f5f6e")   # river_tiles_l8 的主色（判「这里是水」）
const GROUND_A4_PROBE := Color("#6f6a52")

var fails := 0
var gaps := 0
var checks := 0

var win: Window
var wv: Control
var frames := {}
var headless := false
var img: Image = null


func _init() -> void:
	call_deferred("_run")


func _ok(cond: bool, label: String) -> void:
	checks += 1
	if not cond:
		fails += 1
	print(("PASS " if cond else "FAIL ") + label)


func _gap(label: String) -> void:
	gaps += 1
	print("GAP  " + label)


func _run() -> void:
	headless = DisplayServer.get_name() == "headless"
	win = get_root()
	_load_frames()

	_check_logic()
	_check_dispatch_coverage()

	if headless:
		print("PIXEL_SKIP 无渲染器（headless）—— 像素证据用窗口模式再跑一次本脚本")
	else:
		_setup_view()
		await _check_pixels()
		await _save_shots()

	print("TILE_WIRE_CHECK_DONE fails=%d gaps=%d checks=%d" % [fails, gaps, checks])
	quit(0)


# ---------------------------------------------------------------- 数据

func _load_frames() -> void:
	var parsed: Variant = JSON.parse_string(
		FileAccess.get_file_as_string("res://data/frames.json"))
	for f in (parsed as Dictionary)["frames"]:
		var fd := FrameData.new()
		fd.setup(f)
		frames[fd.id] = fd


func _poly(sd: Dictionary) -> PackedVector2Array:
	var out := PackedVector2Array()
	for p in sd.get("points", []):
		var pa: Array = p
		out.append(Vector2(float(pa[0]), float(pa[1])))
	return out


func _rect(sd: Dictionary) -> Rect2:
	var r: Array = sd.get("rect", [0, 0, 0, 0])
	return Rect2(float(r[0]), float(r[1]), float(r[2]), float(r[3]))


# ------------------------------------------------- 1. 纯逻辑（headless 也跑）

func _check_logic() -> void:
	# points_in_poly：格心判定用的射线法
	var sq := PackedVector2Array([Vector2(0, 0), Vector2(64, 0), Vector2(64, 64), Vector2(0, 64)])
	_ok(AssetDraw.points_in_poly(sq, Vector2(32, 32)), "points_in_poly 正方形内部 → true")
	_ok(not AssetDraw.points_in_poly(sq, Vector2(80, 32)), "points_in_poly 正方形外部 → false")
	# 菱形：bbox 四角必须落在外面（这条直接证明「没有拿 bbox 近似」）
	var diamond := PackedVector2Array([
		Vector2(32, 0), Vector2(64, 32), Vector2(32, 64), Vector2(0, 32)])
	_ok(not AssetDraw.points_in_poly(diamond, Vector2(4, 4)),
		"points_in_poly 菱形 bbox 角点在外 → 没用 bbox 近似")
	_ok(AssetDraw.points_in_poly(diamond, Vector2(32, 32)), "points_in_poly 菱形中心在内")

	# poly_tile_rects：64×64 正方形 → 两行、每行 2 格合并成 1 段
	var rects := AssetDraw.poly_tile_rects(sq, TILE)
	_ok(rects.size() == 2, "poly_tile_rects 64×64 正方形 → %d 段（期望 2）" % rects.size())
	var area := 0.0
	for r in rects:
		area += (r as Rect2).size.x * (r as Rect2).size.y
	_ok(is_equal_approx(area, 64.0 * 64.0), "poly_tile_rects 覆盖面积 = %d（期望 4096）" % int(area))
	# 菱形：格覆盖面积必须明显小于 bbox 面积（48×48=... 实际 64×64=4096）
	var dr := AssetDraw.poly_tile_rects(diamond, TILE)
	var darea := 0.0
	for r in dr:
		darea += (r as Rect2).size.x * (r as Rect2).size.y
	_ok(darea < 0.75 * 64.0 * 64.0,
		"poly_tile_rects 菱形覆盖 %d < bbox 4096 的 75%%（环道不会糊到内岛）" % int(darea))

	# 瓦片表：五帧 × 四类都要有图，且必须是 32×32（C1）
	var missing: Array = []
	var wrong_size: Array = []
	for fid in FRAMES:
		for kind in ["ground", "road", "field", "river"]:
			var tex := AssetDraw.tile_tex(fid, kind)
			if tex == null:
				missing.append("%s/%s" % [fid, kind])
				continue
			if tex.get_width() != 32 or tex.get_height() != 32:
				wrong_size.append("%s/%s=%dx%d" % [fid, kind, tex.get_width(), tex.get_height()])
	_ok(missing.is_empty(), "五帧 × ground/road/field/river 瓦片齐全（缺 %s）" % str(missing))
	_ok(wrong_size.is_empty(), "瓦片全是 32×32（不合 %s）" % str(wrong_size))

	# 旧整帧图索引语义不许被改：A4 仍无 scene 大图（否则 asset_draw_check:216 会红）
	_ok(AssetDraw.scene_tex("a4_2001", "river") == null,
		"scene_tex(a4_2001, river) 仍为 null（大图索引未被瓦片污染）")

	# 一个 32px 瓦片内必须有 ≥3 种颜色（1 色 = 色块，平铺出来等于没铺）
	for fid in FRAMES:
		var t := AssetDraw.ground_tex(fid)
		var n := _tex_colors(t)
		_ok(n >= 3, "%s 地面瓦片格内颜色数 = %d（≥3 才算贴图）" % [fid, n])


func _tex_colors(tex: Texture2D) -> int:
	if tex == null:
		return 0
	var im := tex.get_image()
	if im == null:
		return 0
	var seen := {}
	for y in im.get_height():
		for x in im.get_width():
			seen[im.get_pixel(x, y).to_rgba32()] = true
	return seen.size()


# --------------------------------------- 2. 分派覆盖（每个 shape 都说得出铺什么）

func _check_dispatch_coverage() -> void:
	var no_tex: Array = []
	var gap_shapes := 0
	for fid in FRAMES:
		var fd: FrameData = frames[fid]
		for s in fd.shapes:
			var sd: Dictionary = s
			var label := String(sd.get("label", ""))
			var stype := String(sd.get("type", ""))
			if stype == "polygon":
				if AssetDraw.polygon_tex(fid, label) != null:
					continue
				if label in KNOWN_GAP:
					gap_shapes += 1
					continue
				no_tex.append("%s polygon[label=%s]" % [fid, label])
			elif stype == "rect":
				if bool(sd.get("road", false)):
					if AssetDraw.road_tex(fid) == null:
						no_tex.append("%s rect[road]" % fid)
				elif label == "":
					if AssetDraw.field_tex(fid) == null:
						no_tex.append("%s rect[field]" % fid)
	_ok(no_tex.is_empty(),
		"每个 polygon/rect 都说得出铺什么贴图（说不出的 %d 条：%s）" % [no_tex.size(), str(no_tex)])
	print("INFO 已知缺口 shape = %d 个（岛/山，见反馈文档 §2 缺口表）" % gap_shapes)


# --------------------------------------------------------- 3. 真实渲染 + 像素采样

func _setup_view() -> void:
	wv = WorldView.new()
	win.add_child(wv)
	wv.set_anchors_and_offsets_preset(Control.PRESET_TOP_LEFT)
	wv.size = WORLD
	wv.position = Vector2.ZERO
	wv.time_mode = false


## 把世界坐标 `at` 推到屏幕中心，抓一帧，返回整窗像素。
func _grab(at: Vector2) -> Image:
	var origin := Vector2(
		clampf(at.x - 640.0, 0.0, WORLD.x - 1280.0),
		clampf(at.y - 360.0, 0.0, WORLD.y - 720.0))
	wv.position = -origin
	wv.queue_redraw()
	for i in 3:
		await process_frame
	var im: Image = win.get_texture().get_image()
	if im != null:
		im.set_meta("origin", origin)
	return im


func _screen(at: Vector2, origin: Vector2) -> Vector2i:
	var p := at - origin
	return Vector2i(int(clampf(p.x, 0, 1279)), int(clampf(p.y, 0, 719)))


## 采样一个 32×32 格，返回格内出现过的颜色集合大小（整格 1024 px 全采，不抽样 —— 
## 花纹可能只占十几个像素，抽样会漏掉、把贴图误判成色块）。
func _cell_colors(at: Vector2, origin: Vector2) -> Dictionary:
	var cell := Vector2(floor(at.x / TILE) * TILE, floor(at.y / TILE) * TILE)
	var seen := {}
	for dy in int(TILE):
		for dx in int(TILE):
			var p := _screen(cell + Vector2(dx, dy), origin)
			seen[img.get_pixelv(p).to_rgba32()] = true
	return {"n": seen.size(), "c": img.get_pixelv(_screen(cell + Vector2(16, 16), origin))}


func _px(at: Vector2, origin: Vector2) -> Color:
	return img.get_pixelv(_screen(at, origin))


## 两个颜色的 RGB 欧氏距离（Color 没有 get_distance_to，别拿 Vector4 之外的类型凑）。
func _dist(a: Color, b: Color) -> float:
	return Vector3(a.r, a.g, a.b).distance_to(Vector3(b.r, b.g, b.b))


func _check_pixels() -> void:
	for fid in FRAMES:
		var fd: FrameData = frames[fid]
		wv.show_frame(fd, false)

		# --- 地面：找一块没被任何 shape 盖住的空格 ---
		var gcell: Variant = _free_cell(fd)
		if gcell == null:
			_ok(false, "%s 找不到空地格采样" % fid)
			continue
		img = await _grab(gcell)
		var g := _cell_colors(gcell, img.get_meta("origin"))
		_ok(int(g["n"]) >= 3, "%s 地面 32×32 格内颜色数 = %d（≥3=贴图，1=色块）" % [fid, g["n"]])

		# --- polygon 逐 label ---
		var seen_labels := {}
		for si in fd.shapes.size():
			var sd: Dictionary = fd.shapes[si]
			if String(sd.get("type", "")) != "polygon":
				continue
			var label := String(sd.get("label", ""))
			if seen_labels.get(label, false):
				continue
			var cell: Variant = _first_inner_cell(_poly(sd), fd, si)
			if cell == null:
				# 缺口 shape 若整块被后画的东西遮住（如 A5 的岛被老槐压着），
				# 仍要登记缺口，但说明「这行是数据判定，不是像素采样」。
				if label in KNOWN_GAP:
					var ctr: Variant = _poly_center(_poly(sd))
					var who := _who_covers(fd, si, ctr)
					_gap("%s polygon[%s] 无 32×32 瓦片 ⇒ 纯色降级（采样格全被 %s 遮住，按数据色 %s 判定）"
						% [fid, label, who, String(sd.get("color", "?"))])
				continue
			seen_labels[label] = true
			img = await _grab(cell)
			var pc := _cell_colors(cell, img.get_meta("origin"))
			var info := "格(%.0f,%.0f) 采样色=%s 数据色=%s" % [
				(cell as Vector2).x, (cell as Vector2).y,
				(pc["c"] as Color).to_html(false), String(sd.get("color", "?"))]
			if label in KNOWN_GAP:
				_gap("%s polygon[%s] 32×32 格内颜色数 = %d（缺 32×32 瓦片 ⇒ 纯色降级）%s"
					% [fid, label, pc["n"], info])
			else:
				_ok(int(pc["n"]) >= 3,
					"%s polygon[%s] 32×32 格内颜色数 = %d（≥3=贴图）%s" % [fid, label, pc["n"], info])

		# --- rect：公路（road:true）与田块（label==""）各抽一块 ---
		var road_hit := false
		var field_hit := false
		for si in range(fd.shapes.size() - 1, -1, -1):
			var rsd: Dictionary = fd.shapes[si]
			if String(rsd.get("type", "")) != "rect":
				continue
			var is_road := bool(rsd.get("road", false))
			var is_field := (not is_road) and String(rsd.get("label", "")) == ""
			if (is_road and road_hit) or (is_field and field_hit):
				continue
			if not is_road and not is_field:
				continue
			var rc: Variant = _top_rect_cell(fd, si, _rect(rsd))
			if rc == null:
				continue
			img = await _grab(rc)
			var q := _cell_colors(rc, img.get_meta("origin"))
			var kind := "公路" if is_road else "田块"
			_ok(int(q["n"]) >= 3,
				"%s rect[%s] 32×32 格内颜色数 = %d（≥3=贴图）格(%.0f,%.0f) 采样色=%s"
				% [fid, kind, q["n"], (rc as Vector2).x, (rc as Vector2).y,
					(q["c"] as Color).to_html(false)])
			if is_road:
				road_hit = true
			else:
				field_hit = true

	# --- 河跨帧宽度（D1）：A4 的河数据铺到 4800，引擎必须铺得到 ---
	var a4: FrameData = frames["a4_2001"]
	for s in a4.shapes:
		var sd: Dictionary = s
		if String(sd.get("label", "")) != "河" or String(sd.get("type", "")) != "polygon":
			continue
		var pc4: Variant = _first_inside_at_x(_poly(sd), 4700.0)
		if pc4 == null:
			_ok(false, "A4 河 polygon 在 x=4700 处无内点（数据异常）")
			break
		img = await _grab(pc4)
		var c4 := _cell_colors(pc4, img.get_meta("origin"))
		var mid: Color = c4["c"]
		var near_water: bool = _dist(mid, WATER_PROBE) < _dist(mid, GROUND_A4_PROBE)
		_ok(int(c4["n"]) >= 3 and near_water,
			"A4 河在 x=4700 处仍在铺水（颜色数=%d, 采样色=%s, 更接近水=%s）"
			% [c4["n"], mid.to_html(false), str(near_water)])
		break

	# --- 河跨帧宽度（D1）数据侧诊断：A1 的河数据只到 3200 ---
	for s in frames["a1_1926"].shapes:
		var sd: Dictionary = s
		if String(sd.get("label", "")) != "河" or String(sd.get("type", "")) != "polygon":
			continue
		var poly := _poly(sd)
		var box := Rect2(poly[0], Vector2.ZERO)
		for q in poly:
			box = box.expand(q)
		print("INFO A1 河 polygon bbox = %s" % str(box))
		for x in [3100.0, 3199.0, 3200.0, 3280.0, 3400.0, 4700.0]:
			var q2: Variant = _first_inside_at_x(poly, x)
			if q2 == null:
				print("INFO A1 河 x=%d 整列不在河多边形内（数据只铺到 %d）" % [int(x), int(box.end.x)])
				continue
			img = await _grab(q2)
			var c := _px(q2, img.get_meta("origin"))
			print("INFO A1 河 x=%d y=%d 颜色=%s（更接近水=%s）" % [int(x), int((q2 as Vector2).y),
				c.to_html(false), str(_dist(c, WATER_PROBE) < _dist(c, GROUND_A4_PROBE))])
		print("INFO A1–A3 河数据只到 x=3200 ⇒ x>3200 无河是**数据缺口**（A1–A3 重排线的活），不是引擎缺口")
		break


## 一块「没被任何 shape 盖住」的空地格心（确定性：从世界底部往上、从左往右找）。
func _free_cell(fd: FrameData) -> Variant:
	var gy := int(WORLD.y / TILE) - 1
	while gy >= 0:
		for gx in int(WORLD.x / TILE):
			var c := Vector2((gx + 0.5) * TILE, (gy + 0.5) * TILE)
			if not _covered(fd, c):
				return Vector2(gx * TILE, gy * TILE)
		gy -= 3
	return null


func _covered(fd: FrameData, p: Vector2) -> bool:
	for s in fd.shapes:
		var sd: Dictionary = s
		match String(sd.get("type", "")):
			"polygon":
				if AssetDraw.points_in_poly(_poly(sd), p):
					return true
			"rect":
				if _rect(sd).has_point(p):
					return true
			"circle":
				var ct: Array = sd.get("center", [0, 0])
				if p.distance_to(Vector2(float(ct[0]), float(ct[1]))) <= float(sd.get("radius", 0)) + TILE:
					return true
			"house":
				# 房子 lot 尺寸不在这里算，直接给个宽松的 8 格外扩
				var hp: Array = sd.get("pos", [0, 0])
				if (p - Vector2(float(hp[0]), float(hp[1]))).abs().x < 400.0 \
						and (p - Vector2(float(hp[0]), float(hp[1]))).abs().y < 400.0:
					return true
	return false


## polygon 里「整个 32px 格都在多边形内」的第一格（格原点）。
func _first_inner_cell(poly: PackedVector2Array, fd: FrameData = null, idx: int = -1) -> Variant:
	if poly.size() < 3:
		return null
	var box := Rect2(poly[0], Vector2.ZERO)
	for q in poly:
		box = box.expand(q)
	var gy := int(floor(box.position.y / TILE))
	while gy * TILE < box.end.y:
		for gx in range(int(floor(box.position.x / TILE)), int(ceil(box.end.x / TILE))):
			var o := Vector2(gx * TILE, gy * TILE)
			var ok := true
			for corner in [o, o + Vector2(TILE - 1, 0), o + Vector2(0, TILE - 1),
					o + Vector2(TILE - 1, TILE - 1)]:
				if not AssetDraw.points_in_poly(poly, corner):
					ok = false
					break
			if ok and (fd == null or not _covered_after(fd, idx, o + Vector2(16, 16))):
				return o
		gy += 1
	return null


## rect 里找一个没被「数据里排在它后面」的 shape 盖住的格（排在后面 = 画在它上面）。
func _top_rect_cell(fd: FrameData, idx: int, rect: Rect2) -> Variant:
	var gy := int(floor(rect.position.y / TILE))
	while gy * TILE < rect.end.y:
		for gx in range(int(floor(rect.position.x / TILE)), int(ceil(rect.end.x / TILE))):
			var o := Vector2(gx * TILE, gy * TILE)
			if not rect.has_point(o) or not rect.has_point(o + Vector2(TILE - 1, TILE - 1)):
				continue
			if not _covered_after(fd, idx, o + Vector2(16, 16)):
				return o
		gy += 1
	return null


## 该点是否被数据里 idx 之后的任一 shape 覆盖。
func _covered_after(fd: FrameData, idx: int, p: Vector2) -> bool:
	for si in range(idx + 1, fd.shapes.size()):
		var sd: Dictionary = fd.shapes[si]
		match String(sd.get("type", "")):
			"polygon":
				if AssetDraw.points_in_poly(_poly(sd), p):
					return true
			"rect":
				if _rect(sd).has_point(p):
					return true
			"circle":
				var ct: Array = sd.get("center", [0, 0])
				if p.distance_to(Vector2(float(ct[0]), float(ct[1]))) <= float(sd.get("radius", 0)):
					return true
	return false


## 在给定 x 上，找一个落在多边形内的点（自 bbox 上沿往下扫）。
func _first_inside_at_x(poly: PackedVector2Array, x: float) -> Variant:
	var box := Rect2(poly[0], Vector2.ZERO)
	for q in poly:
		box = box.expand(q)
	var y := box.position.y + 1.0
	while y < box.end.y:
		if AssetDraw.points_in_poly(poly, Vector2(x, y)):
			return Vector2(x, y)
		y += 2.0
	return null
# ------------------------------------------------- 4. 实机截图（给人看）
## 存几张窗口渲染的实拍 PNG 到 `_mdtest/assets/`，供人工确认「这不是色块」。
const SHOTS := [
	["a1_1926", Vector2(1400, 200), "a1_river_bank"],
	["a3_1976", Vector2(1400, 1500), "a3_field"],
	["a4_2001", Vector2(2000, 1650), "a4_ring"],
	["a4_2001", Vector2(4600, 200), "a4_river_east"],
	["a5_2026", Vector2(2000, 1650), "a5_ring"],
	["a5_2026", Vector2(4300, 2700), "a5_hill"],
]


func _save_shots() -> void:
	var dir := "res://_mdtest/assets"
	DirAccess.make_dir_recursive_absolute(dir)
	for item in SHOTS:
		var fid := String(item[0])
		var at: Vector2 = item[1]
		var nm := String(item[2])
		wv.show_frame(frames[fid], false)
		var im := await _grab(at)
		var err := im.save_png("%s/l8_%s.png" % [dir, nm])
		print("SHOT %s %s → l8_%s.png err=%d" % [fid, str(at), nm, err])
## 多边形 bbox 中心（诊断用）。
func _poly_center(poly: PackedVector2Array) -> Vector2:
	var box := Rect2(poly[0], Vector2.ZERO)
	for q in poly:
		box = box.expand(q)
	return box.get_center()


## 谁盖住了这个点（诊断用，返回 "序号:类型/标签"）。
func _who_covers(fd: FrameData, idx: int, p: Vector2) -> String:
	for si in range(idx + 1, fd.shapes.size()):
		var sd: Dictionary = fd.shapes[si]
		var t := String(sd.get("type", ""))
		var hit := false
		match t:
			"polygon":
				hit = AssetDraw.points_in_poly(_poly(sd), p)
			"rect":
				hit = _rect(sd).has_point(p)
			"circle":
				var ct: Array = sd.get("center", [0, 0])
				hit = p.distance_to(Vector2(float(ct[0]), float(ct[1]))) <= float(sd.get("radius", 0))
			"house":
				hit = String(sd.get("id", "")) != ""
		if hit:
			return "%d:%s/%s" % [si, t, String(sd.get("label", sd.get("id", "")))]
	return "无"