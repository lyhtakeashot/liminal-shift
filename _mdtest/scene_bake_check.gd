extends SceneTree

## 地图场景化 Stage 1 —— 烘焙产物自检（任务书 §3.4：S1–S12）
##
## 跑法：
##   headless（S1–S10，逻辑层）：
##     godot --headless --path . -s res://_mdtest/scene_bake_check.gd
##   窗口（再跑 S11–S12，像素层；headless 是 dummy 渲染器读不到帧缓冲）：
##     godot --path . -s res://_mdtest/scene_bake_check.gd
##
## 自检**只读**：不写 scenes/、不写 assets/（只往 _mdtest/assets/ 存两张实拍）。
## 格数复算一律走 `tools/world_scene_spec.gd` —— 与烘焙器同一套换算，S5 的 ±0 才有意义。

const Spec := preload("res://tools/world_scene_spec.gd")
const HouseShape := preload("res://scripts/house_shape.gd")

const OUT_DIR := "res://scenes/world"

var fails := 0
var checks := 0
var headless := false
var win: Window
var world := Vector2i(4800, 3600)
var rows: Array = []


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	headless = DisplayServer.get_name() == "headless"
	win = get_root()
	HouseShape.load_all()

	var txt := FileAccess.get_file_as_string("res://data/frames.json")
	if txt.is_empty():
		printerr("BAKE_CHECK_FAIL 读不到 data/frames.json")
		fails += 1
		print("SCENE_BAKE_CHECK_DONE fails=%d checks=%d" % [fails, checks])
		quit(0)
		return
	var doc = JSON.parse_string(txt)
	if typeof(doc) != TYPE_DICTIONARY:
		printerr("BAKE_CHECK_FAIL frames.json 解析失败")
		fails += 1
		print("SCENE_BAKE_CHECK_DONE fails=%d checks=%d" % [fails, checks])
		quit(0)
		return
	var wd: Dictionary = (doc as Dictionary).get("world", {})
	world = Vector2i(int(wd.get("width", 4800)), int(wd.get("height", 3600)))
	var frames: Array = (doc as Dictionary).get("frames", [])

	_ok("frames.json 有帧", frames.size() > 0, "count=%d" % frames.size())
	for fd in frames:
		_check_frame(fd as Dictionary)

	print("")
	print("TABLE | id | ground | field | road | poly | sprite | nodes |")
	for r in rows:
		print("TABLE | %s" % String(r))

	if headless:
		print("PIXEL 跳过 S11/S12（headless=dummy 渲染器；用不带 --headless 再跑一次）")
	else:
		await _pixel_checks(frames)

	print("")
	print("SCENE_BAKE_CHECK_DONE fails=%d checks=%d" % [fails, checks])
	quit(0)


# ============================================================
# S1–S10：一帧
# ============================================================
func _check_frame(fd: Dictionary) -> void:
	var id := String(fd.get("id", ""))
	var tscn_path := "%s/world_%s.tscn" % [OUT_DIR, id]
	var tres_path := "%s/tileset_%s.tres" % [OUT_DIR, id]

	# ---- S1 产物存在且能读 ----
	var f_ok := FileAccess.file_exists(tscn_path) and FileAccess.file_exists(tres_path)
	_ok(id + " S1 产物存在", f_ok, "%s / %s" % [tscn_path, tres_path])
	if not f_ok:
		rows.append("%s | - | - | - | - | - | - | S1 FAIL" % id)
		return
	var ps := ResourceLoader.load(tscn_path, "", ResourceLoader.CACHE_MODE_REUSE) as PackedScene
	var ts := ResourceLoader.load(tres_path, "", ResourceLoader.CACHE_MODE_REUSE) as TileSet
	_ok(id + " S1 PackedScene 可加载", ps != null, tscn_path)
	_ok(id + " S1 TileSet 可加载", ts != null, tres_path)
	if ps == null or ts == null:
		rows.append("%s | - | - | - | - | - | - | S1 FAIL" % id)
		return

	var root := ps.instantiate()
	if not (root is Node2D):
		_ok(id + " S2 根是 Node2D", false, root.get_class())
		root.free()
		return
	# ---- S2 根名 ----
	_ok(id + " S2 根名 World_<帧号>", root.name == "World_" + id, str(root.name))

	# ---- S3 七层结构与数量 ----
	_ok(id + " S3 恰好七层", root.get_child_count() == Spec.LAYERS.size(),
		"children=%d" % root.get_child_count())
	for i in Spec.LAYERS.size():
		var want := String(Spec.LAYERS[i])
		var n: Node = root.get_child(i) if i < root.get_child_count() else null
		if n == null:
			_ok(id + " S3 层 " + want, false, "缺")
			continue
		_ok(id + " S3 层名 " + want, n.name == want, str(n.name))
		var wt := String(Spec.LAYER_TYPE[want])
		var type_ok := false
		match wt:
			"TileMapLayer":
				type_ok = n is TileMapLayer
			"Polygon2D":
				type_ok = n is Polygon2D
			_:
				type_ok = n is Node2D
		_ok(id + " S3 层类型 " + want, type_ok, n.get_class())

	var ground := root.get_node_or_null("Ground") as TileMapLayer
	var field := root.get_node_or_null("Field") as TileMapLayer
	var road := root.get_node_or_null("Road") as TileMapLayer
	var water := root.get_node_or_null("Water") as Polygon2D
	var overlay := root.get_node_or_null("Overlay") as Node2D
	var houses := root.get_node_or_null("Houses") as Node2D
	var props := root.get_node_or_null("Props") as Node2D

	# ---- S4 Props y_sort=true，其余 false ----
	for lay in [ground, field, road, water, overlay, houses, props]:
		if lay == null:
			continue
		var want_sort := String((lay as Node).name) in Spec.YSORT_LAYERS
		_ok(id + " S4 y_sort " + String((lay as Node).name),
			(lay as CanvasItem).y_sort_enabled == want_sort,
			"got=%s want=%s" % [(lay as CanvasItem).y_sort_enabled, want_sort])

	# ---- S5 三个 TileMapLayer 的格数 = 复算格数（±0）----
	var want_g := Spec.ground_cells(world).size()
	var want_f := Spec.cells_for(fd.get("shapes", []), "Field").size()
	var want_r := Spec.cells_for(fd.get("shapes", []), "Road").size()
	var got_g := ground.get_used_cells().size() if ground != null else -1
	var got_f := field.get_used_cells().size() if field != null else -1
	var got_r := road.get_used_cells().size() if road != null else -1
	for pair in [["Ground", got_g, want_g], ["Field", got_f, want_f], ["Road", got_r, want_r]]:
		var nm := String(pair[0])
		var got := int(pair[1])
		var want := int(pair[2])
		_ok(id + " S5 " + nm + " 非空且格数一致", got == want and got > 0,
			"got=%d want=%d" % [got, want])

	# ---- S6 TileSet：每层都挂、source≥1、每个 source 有 tile ----
	for lay2 in [ground, field, road]:
		if lay2 == null:
			continue
		var t := (lay2 as TileMapLayer).tile_set
		var nm2 := String((lay2 as Node).name)
		_ok(id + " S6 " + nm2 + " 挂了 TileSet", t != null, "")
		if t == null:
			continue
		_ok(id + " S6 " + nm2 + " source≥1", t.get_source_count() >= 1,
			"n=%d" % t.get_source_count())
		for si in t.get_source_count():
			var s := t.get_source(si)
			if s == null or not (s is TileSetAtlasSource):
				var cls := "null" if s == null else s.get_class()
				_ok(id + " S6 " + nm2 + " source%d 是 AtlasSource" % si, false, cls)
				continue
			_ok(id + " S6 " + nm2 + " source%d 有 tile" % si,
				(s as TileSetAtlasSource).get_tiles_count() >= 1,
				"tiles=%d" % (s as TileSetAtlasSource).get_tiles_count())

	# ---- S7 背景 Polygon2D：polygon 非空；有贴图的必须 texture_repeat=ENABLED ----
	var bg_polys: Array = []
	if water != null:
		bg_polys.append(water)
	for holder in [overlay, houses]:
		if holder != null:
			bg_polys.append_array(_descendants_of_type(holder, "Polygon2D"))
	for p in bg_polys:
		var poly := p as Polygon2D
		_ok(id + " S7 polygon 非空 " + String(poly.name), poly.polygon.size() > 0,
			"pts=%d" % poly.polygon.size())
		if poly.texture != null:
			_ok(id + " S7 贴图重复模式 " + String(poly.name),
				poly.texture_repeat == CanvasItem.TEXTURE_REPEAT_ENABLED,
				"got=%d" % poly.texture_repeat)

	# ---- S8 前景 Sprite2D：centered=false，position.y 落在帧内 ----
	var fg_sprites: Array = _descendants_of_type(props, "Sprite2D") if props != null else []
	for s2 in fg_sprites:
		var spr := s2 as Sprite2D
		_ok(id + " S8 centered=false " + String(spr.name), spr.centered == false, "")
		_ok(id + " S8 排序键在帧内 " + String(spr.name),
			spr.position.y >= 0.0 and spr.position.y <= float(world.y),
			"y=%.1f" % spr.position.y)

	# ---- S9 前景层不许有 TileMapLayer（前景只能 Sprite2D / Polygon2D）----
	var bad_tm: Array = _descendants_of_type(props, "TileMapLayer") if props != null else []
	_ok(id + " S9 前景层无 TileMapLayer", bad_tm.is_empty(),
		"found=%d" % bad_tm.size())

	# ---- S10 场景里不许有玩家 ----
	var player_nodes: Array = []
	for n3 in [root] + _all_descendants(root):
		var nm3 := String((n3 as Node).name).to_lower()
		if nm3.contains("player") or nm3.contains("玩家") or nm3 == "char":
			player_nodes.append(String((n3 as Node).name))
	_ok(id + " S10 无玩家节点", player_nodes.is_empty(), str(player_nodes))

	# ---- 统计（反馈文档的表格就抄这几行）----
	var poly_n: Array = []
	for holder2 in [water, overlay, houses]:
		if holder2 != null:
			poly_n.append_array(_descendants_of_type(holder2, "Polygon2D"))
	if water != null:
		poly_n.append(water)
	var sprite_n: Array = []
	for holder3 in [overlay, houses, props]:
		if holder3 != null:
			sprite_n.append_array(_descendants_of_type(holder3, "Sprite2D"))
	var verdict := "OK"
	if fails > 0:
		verdict = "见 FAIL"
	rows.append("%s | %d | %d | %d | %d | %d | %d | S1-S10 %s" % [
		id, got_g, got_f, got_r, poly_n.size(), sprite_n.size(),
		_all_descendants(root).size(), verdict])
	root.free()


# ============================================================
# S11–S12：窗口模式像素层（证明「不是色块」）
# ============================================================
func _pixel_checks(frames: Array) -> void:
	var targets := []
	for fd in frames:
		var id := String((fd as Dictionary).get("id", ""))
		if id == "a5_2026" or id == "a1_1926":
			targets.append(fd)
	_ok("像素层找到 a1/a5 两帧", targets.size() == 2, "n=%d" % targets.size())
	for fd2 in targets:
		var id2 := String((fd2 as Dictionary).get("id", ""))
		var at := _pick_ground_cell(fd2 as Dictionary)
		_ok(id2 + " S11/S12 找到纯地面采样点", at.x >= 0.0, str(at))
		if at.x < 0.0:
			continue
		var png := "res://_mdtest/assets/scene_bake_%s.png" % id2
		var res := await _render_and_count(id2, at, png)
		_ok(id2 + " S12 地面区域颜色数≥3", int(res["colors"]) >= 3,
			"colors=%d at=%s png=%s err=%s" % [int(res["colors"]), str(at), png, str(res["err"])])


## 找一个「只可能是地面」的格：不在任何 rect / polygon / lot / circle 包围盒里。
func _pick_ground_cell(fd: Dictionary) -> Vector2:
	var shapes: Array = fd.get("shapes", [])
	var blocked := {}
	for s in shapes:
		var sd: Dictionary = s
		match String(sd.get("type", "")):
			"rect":
				for c in Spec.rect_cells(Spec.rect_of(sd)):
					blocked[c] = true
			"circle":
				var cp: Array = sd.get("center", [0, 0])
				var rad := float(sd.get("radius", 4)) + 32.0
				var lo := Vector2i(int(floor((float(cp[0]) - rad) / 32.0)), int(floor((float(cp[1]) - rad) / 32.0)))
				var hi := Vector2i(int(ceil((float(cp[0]) + rad) / 32.0)), int(ceil((float(cp[1]) + rad) / 32.0)))
				for y in range(lo.y, hi.y + 1):
					for x in range(lo.x, hi.x + 1):
						blocked[Vector2i(x, y)] = true
			"house":
				var sp: Array = sd.get("pos", [0, 0])
				var data: Dictionary = HouseShape.house(String(sd.get("id", "")))
				if not data.is_empty():
					for c in Spec.rect_cells(HouseShape.lot_rect(data, Vector2(float(sp[0]), float(sp[1])))):
						blocked[c] = true
			"polygon":
				var pts := Spec.poly_points(sd)
				if pts.size() < 3:
					continue
				var bb := _bounds(pts)
				var lo2 := Vector2i(int(floor(bb.position.x / 32.0)) - 1, int(floor(bb.position.y / 32.0)) - 1)
				var hi2 := Vector2i(int(ceil(bb.end.x / 32.0)) + 1, int(ceil(bb.end.y / 32.0)) + 1)
				for y in range(lo2.y, hi2.y + 1):
					for x in range(lo2.x, hi2.x + 1):
						if Geometry2D.is_point_in_polygon(Vector2(x * 32 + 16, y * 32 + 16), pts):
							blocked[Vector2i(x, y)] = true
	var cols := int(world.x / 32)
	var rws := int(world.y / 32)
	for y in range(4, rws - 4):
		for x in range(4, cols - 4):
			var c2 := Vector2i(x, y)
			if blocked.has(c2):
				continue
			return Vector2(x * 32 + 16, y * 32 + 16)
	return Vector2(-1, -1)


func _bounds(pts: PackedVector2Array) -> Rect2:
	var r := Rect2(pts[0], Vector2.ZERO)
	for p in pts:
		r = r.expand(p)
	return r


## 把烘焙场景挂到根窗口、按采样点摆好相机，读回 32×32 那一格的颜色数。
func _render_and_count(frame_id: String, at: Vector2, png_path: String) -> Dictionary:
	var packed := ResourceLoader.load("%s/world_%s.tscn" % [OUT_DIR, frame_id], "",
		ResourceLoader.CACHE_MODE_REUSE) as PackedScene
	if packed == null:
		return {"colors": -1, "err": "load_fail"}
	var inst := packed.instantiate() as Node2D
	win.add_child(inst)
	var vp := Vector2(win.size)
	var origin := Vector2(
		clampf(at.x - vp.x * 0.5, 0.0, float(world.x) - vp.x),
		clampf(at.y - vp.y * 0.5, 0.0, float(world.y) - vp.y))
	inst.position = -origin
	for i in 3:
		await process_frame
	var img := win.get_texture().get_image()
	img.save_png(png_path)
	var cell_o := Vector2(floorf(at.x / 32.0) * 32.0, floorf(at.y / 32.0) * 32.0)
	var bp := Vector2i(int(cell_o.x - origin.x), int(cell_o.y - origin.y))
	var colors := {}
	for y in 32:
		for x in 32:
			var p := Vector2i(bp.x + x, bp.y + y)
			if p.x < 0 or p.y < 0 or p.x >= img.get_width() or p.y >= img.get_height():
				continue
			colors[img.get_pixelv(p).to_rgba32()] = true
	inst.queue_free()
	await process_frame
	return {"colors": colors.size(), "err": 0}


# ============================================================
# 断言 / 遍历
# ============================================================
func _ok(name: String, cond: bool, detail: String) -> void:
	checks += 1
	if not cond:
		fails += 1
		print("FAIL %s %s" % [name, detail])


func _all_descendants(n: Node) -> Array:
	var out: Array = []
	for c in n.get_children():
		out.append(c)
		out.append_array(_all_descendants(c))
	return out


func _descendants_of_type(n: Node, cls: String) -> Array:
	var out: Array = []
	for c in _all_descendants(n):
		match cls:
			"Polygon2D":
				if c is Polygon2D:
					out.append(c)
			"Sprite2D":
				if c is Sprite2D:
					out.append(c)
			"TileMapLayer":
				if c is TileMapLayer:
					out.append(c)
	return out