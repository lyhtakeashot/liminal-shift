extends SceneTree

## 地图场景化 Stage 1 —— 从 `data/frames.json` 烘焙五帧 Godot 场景
##
## 产物（都是**生成物，不是源**；改了 frames.json / 美术图要重跑本脚本）：
##   scenes/world/tileset_<帧>.tres   每帧一个 TileSet（32×32，一张贴图一个 AtlasSource）
##   scenes/world/world_<帧>.tscn     每帧一个场景，七层：
##     World_<帧>(Node2D)
##       ├ Ground  (TileMapLayer, z=-100)  整个世界铺满 ground 瓦
##       ├ Field   (TileMapLayer, z=-95)   rect label=="" 的田块
##       ├ Road    (TileMapLayer, z=-90)   rect road:true 的公路
##       ├ Water   (Polygon2D,    z=-88)   河（uv=世界坐标，texture_repeat）
##       ├ Overlay (Node2D,       z=-84)   环道/内岛/山/坝/路标（缺图降级纯色）
##       ├ Houses  (Node2D,       z=-70)   房子底色（base 图或 lot 底色+房间色块）
##       └ Props   (Node2D, y_sort=true)   墙/门/屋顶/家具/树/井/碑 —— 底边排序
##
## 铁律：**运行时一个字不动**。本脚本只写 scenes/world/**，不碰 scripts/ 与 assets/。
## 用法：
##   godot --headless --path . -s res://tools/bake_world_scene.gd
##   godot --headless --path . -s res://tools/bake_world_scene.gd -- --frame a5_2026
##
## 三条实测坑（2026-11-26 本机 Godot 4.7.2 实测，别再踩）：
##   ① `TileMapLayer` 没有 `used_cells()`，是 `get_used_cells()`；
##   ② `create_tile()` 必须在 `add_source()` 之后、经 `get_source(id)` 取回引用再调；
##   ③ `Sprite2D.offset` 会被 `scale` 缩放（`get_rect()` 返回的是局部未缩放坐标），
##      所以「底边对齐」要写成 offset.y = (落点顶 - 排序键) / scale.y。

const Spec := preload("res://tools/world_scene_spec.gd")
const AssetDraw := preload("res://scripts/asset_draw.gd")
const WorldView := preload("res://scripts/world_view.gd")
const HouseShape := preload("res://scripts/house_shape.gd")
const FrameData := preload("res://scripts/frame_data.gd")

const OUT_DIR := "res://scenes/world"
const TILE := 32.0
const EXTRUDE := 32.0
const CIRCLE_SEGS := 32

var _seq := 0
var _missing: Array = []
var _stat := {}


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	var only := ""
	var args := OS.get_cmdline_user_args()
	var i := 0
	while i < args.size():
		if String(args[i]) == "--frame" and i + 1 < args.size():
			only = String(args[i + 1])
		i += 1

	var txt := FileAccess.get_file_as_string("res://data/frames.json")
	if txt.is_empty():
		printerr("BAKE_FAIL 读不到 res://data/frames.json")
		quit(1)
		return
	var doc = JSON.parse_string(txt)
	if typeof(doc) != TYPE_DICTIONARY:
		printerr("BAKE_FAIL frames.json 解析失败")
		quit(1)
		return

	HouseShape.load_all()
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))

	var top: Dictionary = doc
	var world_d: Dictionary = top.get("world", {})
	var wsize := Vector2i(int(world_d.get("width", 4800)), int(world_d.get("height", 3600)))
	var frames: Array = top.get("frames", [])
	var baked := 0
	for fd in frames:
		var f := FrameData.new()
		f.setup(fd as Dictionary)
		if only != "" and f.id != only:
			continue
		_bake_frame(f, wsize)
		baked += 1
	if only != "" and baked == 0:
		printerr("BAKE_FAIL 没有叫 %s 的帧" % only)
		quit(1)
		return
	print("BAKE_DONE frames=%d out=%s" % [baked, OUT_DIR])
	quit(0)


# ============================================================
# 一帧
# ============================================================
func _bake_frame(f: FrameData, wsize: Vector2i) -> void:
	_seq = 0
	_missing = []
	_stat = {"ground": 0, "field": 0, "road": 0, "poly": 0, "sprite": 0, "node": 0}
	var ts_path := "%s/tileset_%s.tres" % [OUT_DIR, f.id]
	var scene_path := "%s/world_%s.tscn" % [OUT_DIR, f.id]
	var src_ids := _build_tileset(f, ts_path)
	var ts_ref: TileSet = load(ts_path)
	if ts_ref == null:
		printerr("BAKE_FAIL 载入 TileSet 失败：%s" % ts_path)
		return

	var root := Node2D.new()
	root.name = "World_" + f.id

	var ground := TileMapLayer.new()
	ground.name = "Ground"
	var field := TileMapLayer.new()
	field.name = "Field"
	var road := TileMapLayer.new()
	road.name = "Road"
	var water := Polygon2D.new()
	water.name = "Water"
	var overlay := Node2D.new()
	overlay.name = "Overlay"
	var houses := Node2D.new()
	houses.name = "Houses"
	var props := Node2D.new()
	props.name = "Props"

	for lay in [ground, field, road]:
		(lay as TileMapLayer).tile_set = ts_ref
		(lay as TileMapLayer).z_index = int(Spec.LAYER_Z[String((lay as Node).name)])
	for n in [ground, field, road, water, overlay, houses, props]:
		root.add_child(n)  # owner 统一在 pack 前设，见 _set_owner
	water.z_index = int(Spec.LAYER_Z["Water"])
	overlay.z_index = int(Spec.LAYER_Z["Overlay"])
	houses.z_index = int(Spec.LAYER_Z["Houses"])
	props.y_sort_enabled = true

	# ---- Ground：整个世界铺满 ----
	var gcells := Spec.ground_cells(wsize)
	if src_ids.has("ground"):
		for c in gcells:
			ground.set_cell(c, int(src_ids["ground"]), Vector2i.ZERO, 0)
	_stat["ground"] = ground.get_used_cells().size()

	# ---- Field / Road：rect 逐格 ----
	var fdict := Spec.cells_for(f.shapes, "Field")
	var rdict := Spec.cells_for(f.shapes, "Road")
	if src_ids.has("field"):
		for c in fdict.keys():
			field.set_cell(c, int(src_ids["field"]), Vector2i.ZERO, 0)
	else:
		_mark_missing("field:" + f.id)
	if src_ids.has("road"):
		for c in rdict.keys():
			road.set_cell(c, int(src_ids["road"]), Vector2i.ZERO, 0)
	else:
		_mark_missing("road:" + f.id)
	_stat["field"] = field.get_used_cells().size()
	_stat["road"] = road.get_used_cells().size()

	# ---- 其余 shape：Water / Overlay / Houses / Props ----
	var river_done := false
	for s in f.shapes:
		var sd: Dictionary = s
		var cl := Spec.classify(sd)
		var layer_name := String(cl["layer"])
		var kind := String(cl["kind"])
		match layer_name:
			"Water":
				# Water 节点本身就是那个 Polygon2D（任务书 §3.2 的树形）
				if not river_done:
					_fill_poly_texture(water, sd, kind, f.id)
					river_done = true
					_stat["poly"] += 1
			"Overlay":
				_bake_overlay(overlay, f, sd, kind)
			"Houses":
				_bake_house(houses, props, f, sd)
			"Props":
				if String(sd.get("type", "")) == "circle":
					_bake_circle(props, f, sd)
				else:
					_bake_rect_prop(props, f, sd)
	if not river_done:
		_mark_missing("river:" + f.id)

	# ---- 保存 ----
	_set_owner(root, root)
	var ps := PackedScene.new()
	var perr := ps.pack(root)
	if perr != OK:
		printerr("BAKE_FAIL pack 失败 %s err=%d" % [f.id, perr])
		root.free()
		return
	var serr := ResourceSaver.save(ps, scene_path)
	print("FRAME %s cells ground=%d field=%d road=%d | poly=%d sprite=%d nodes=%d | missing=%s"
		% [f.id, int(_stat["ground"]), int(_stat["field"]), int(_stat["road"]),
			int(_stat["poly"]), int(_stat["sprite"]), int(_stat["node"]),
			"none" if _missing.is_empty() else ",".join(_missing)])
	if serr != OK:
		printerr("BAKE_FAIL 保存场景失败 %s err=%d" % [scene_path, serr])
	root.free()


# ============================================================
# TileSet：一张贴图一个 AtlasSource，按 32×32 建 tile
# ============================================================
func _build_tileset(f: FrameData, ts_path: String) -> Dictionary:
	var ts := TileSet.new()
	ts.tile_size = Vector2i(32, 32)
	var ids := {}
	var next_id := 0
	for kind in ["ground", "field", "road", "river"]:
		var tex := Spec.kind_texture(f.id, kind, {})
		if tex == null:
			_mark_missing(kind + ":" + f.id)
			continue
		var cols := int(tex.get_width() / 32)
		var rows := int(tex.get_height() / 32)
		if cols < 1 or rows < 1:
			_mark_missing(kind + ":尺寸不足32:" + f.id)
			continue
		var src := TileSetAtlasSource.new()
		src.texture = tex
		src.texture_region_size = Vector2i(32, 32)
		ts.add_source(src, next_id)
		# 坑②：必须经 get_source(id) 取回引用，原引用调 create_tile 不生效
		var got := ts.get_source(next_id) as TileSetAtlasSource
		for y in rows:
			for x in cols:
				got.create_tile(Vector2i(x, y))
		ids[kind] = next_id
		next_id += 1
		# 非 32 整数倍的余量（只取整数区域，余下那几像素不用）
		var rx := tex.get_width() - cols * 32
		var ry := tex.get_height() - rows * 32
		if rx > 0 or ry > 0:
			print("TILESET %s %s atlas=%dx%d 余量=%d,%d（只取整数区域）"
				% [f.id, kind, cols, rows, rx, ry])
	var serr := ResourceSaver.save(ts, ts_path)
	if serr != OK:
		printerr("BAKE_FAIL 保存 TileSet 失败 %s err=%d" % [ts_path, serr])
	return ids


# ============================================================
# 背景多边形（Water / Overlay）
# ============================================================
## 把 Water 这个 Polygon2D 直接填成河：polygon 与 uv 都用**世界坐标**，
## texture_repeat=ENABLED ⇒ uv(0,0) 落在世界原点，32px 贴图每 32px 重复一次，
## 与 TileMapLayer 的格子天然对齐（C1 单方格可平铺）。
func _fill_poly_texture(node: Polygon2D, sd: Dictionary, kind: String, frame_id: String) -> void:
	var pts := Spec.poly_points(sd)
	node.polygon = pts
	var tex := Spec.kind_texture(frame_id, kind, sd)
	if tex != null:
		node.texture = tex
		node.uv = pts
		node.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
		node.color = Color.WHITE
	else:
		node.color = Spec.fallback_color(sd)
		_mark_missing(kind + ":" + frame_id)


func _bake_overlay(overlay: Node2D, f: FrameData, sd: Dictionary, kind: String) -> void:
	var zoff := int(Spec.OVERLAY_Z.get(kind, Spec.LAYER_Z["Overlay"])) - int(Spec.LAYER_Z["Overlay"])
	match String(sd.get("type", "")):
		"polygon":
			var pts := Spec.poly_points(sd)
			if pts.size() < 3:
				return
			var poly := Polygon2D.new()
			poly.name = _nm("Poly_" + kind)
			poly.z_index = zoff
			var tex := Spec.kind_texture(f.id, kind, sd)
			poly.polygon = pts
			if tex != null:
				poly.texture = tex
				poly.uv = pts
				poly.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
				poly.color = Color.WHITE
			else:
				poly.color = Spec.fallback_color(sd)
				_mark_missing(kind + ":" + f.id)
			overlay.add_child(poly)
			_stat["poly"] += 1
		"rect":
			var r := Spec.rect_of(sd)
			var tex2 := Spec.kind_texture(f.id, kind, sd)
			if tex2 != null:
				var spr := _mk_sprite(tex2, r.position, r.size, r.end.y, "Overlay_" + kind)
				spr.z_index = zoff
				overlay.add_child(spr)
				_stat["sprite"] += 1
			else:
				var p2 := _mk_poly_rect(r, r.end.y, Spec.fallback_color(sd), "Overlay_" + kind)
				p2.z_index = zoff
				overlay.add_child(p2)
				_mark_missing(kind + ":" + f.id)


# ============================================================
# 房子
# ============================================================
func _bake_house(houses: Node2D, props: Node2D, f: FrameData, sd: Dictionary) -> void:
	var sid := String(sd.get("id", ""))
	var sp: Array = sd.get("pos", [0, 0])
	var hpos := Vector2(float(sp[0]), float(sp[1]))
	var data: Dictionary = HouseShape.house(sid)
	if data.is_empty():
		_mark_missing("house:" + sid)
		return
	var lot := HouseShape.lot_rect(data, hpos)
	var htex := Spec.house_textures(sid)
	var tex_base: Texture2D = htex["base"]
	var tex_roof: Texture2D = htex["roof"]

	# ---- Houses 层：底色（base 图优先，缺图回 lot 底色 + 房间色块）----
	if tex_base != null:
		var want := Vector2(lot.size.x, lot.size.y + EXTRUDE)
		var spr := _mk_sprite(tex_base, Vector2(hpos.x, hpos.y - EXTRUDE), want, lot.end.y, "HouseBase_" + sid)
		houses.add_child(spr)
		_stat["sprite"] += 1
	else:
		_mark_missing("house_base:" + sid)
		# Houses 层不参与 y_sort，这些纯色块的排序键只当锚点用（取 lot 南沿，保证落在帧内）
		houses.add_child(_mk_poly_rect(lot, lot.end.y, HouseShape.YARD_COLOR, "Lot_" + sid))
		# 2px 外框（runtime 是 draw_rect(w=2) 的描边，这里拆成四条细矩形）
		var edge := HouseShape.LOT_OUTLINE
		for rr in [
			Rect2(lot.position, Vector2(lot.size.x, 2.0)),
			Rect2(Vector2(lot.position.x, lot.end.y - 2.0), Vector2(lot.size.x, 2.0)),
			Rect2(lot.position, Vector2(2.0, lot.size.y)),
			Rect2(Vector2(lot.end.x - 2.0, lot.position.y), Vector2(2.0, lot.size.y)),
		]:
			houses.add_child(_mk_poly_rect(rr, lot.end.y, edge, "LotEdge_" + sid))
		for room in HouseShape.room_rects(data, hpos):
			var rc: Color = HouseShape.ROOM_COLORS.get(String(room["color_key"]), Color("#6b5842"))
			houses.add_child(_mk_poly_rect(room["rect"], (room["rect"] as Rect2).end.y, rc,
				"Room_" + sid))

	# ---- Props 层：墙（按行）/ 门 / 屋顶 / 家具 ----
	var rows := {}
	for c in HouseShape.wall_render_cells(data, hpos):
		var cd: Dictionary = c
		var rr: Rect2 = cd["rect"]
		var ry := int(round((rr.position.y - hpos.y) / TILE))
		if not rows.has(ry):
			rows[ry] = []
		(rows[ry] as Array).append(cd)
	var keys: Array = rows.keys()
	keys.sort()
	for ry in keys:
		var sort_y := hpos.y + (float(int(ry)) + 1.0) * TILE
		if tex_base != null:
			_bake_wall_strips(props, tex_base, rows[ry], hpos, data, sort_y)
		else:
			_bake_wall_blocks(props, rows[ry], sort_y)

	if tex_base == null:
		# 门 / 院门也在 base 图里；缺图才由引擎色块补（runtime 同样只在无图时画）
		for d in HouseShape.door_rects(data, hpos):
			var dd: Dictionary = d
			var dr: Rect2 = dd["rect"]
			var dry := int(round((dr.position.y - hpos.y) / TILE))
			var sort_y_door := hpos.y + float(dry) * TILE
			var dc: Color = HouseShape.GATE_COLOR if bool(dd["gate"]) else HouseShape.DOOR_COLOR
			props.add_child(_mk_poly_rect(dr, sort_y_door, dc, "Door"))

	# 屋顶：排序键 = wings 南沿（runtime _roof_sort_y）
	var sort_y_roof := WorldView._roof_sort_y(data, hpos)
	var lot0 := HouseShape.lot_rect(data, Vector2.ZERO)
	if tex_roof != null:
		var want_roof := Vector2(lot0.size.x, lot0.size.y + EXTRUDE)
		var rspr := _mk_sprite(tex_roof, Vector2(hpos.x, hpos.y - EXTRUDE), want_roof,
			sort_y_roof, "Roof_" + sid)
		props.add_child(rspr)
		_stat["sprite"] += 1
	else:
		_mark_missing("house_roof:" + sid)
		var wings: Array = data.get("wings", []).duplicate()
		wings.sort_custom(func(a: Array, b: Array) -> bool: return int(a[1]) < int(b[1]))
		for w in wings:
			var ww: Array = w
			var wpx := float(ww[2]) * TILE
			var wpy := float(ww[3]) * TILE
			# 外扩 1px 做檐，整体抬高 EXTRUDE（与 runtime 同一公式）
			var r := Rect2(Vector2(hpos.x + float(ww[0]) * TILE - 1.0,
				hpos.y + float(ww[1]) * TILE - 1.0 - EXTRUDE), Vector2(wpx + 2.0, wpy + 2.0))
			props.add_child(_mk_poly_rect(r, sort_y_roof, WorldView.ROOF_COLOR, "RoofWing_" + sid))
			if wpx >= wpy:
				var ry2 := r.position.y + r.size.y * 0.5
				props.add_child(_mk_poly_rect(Rect2(r.position.x, ry2 - 1.0, r.size.x, 2.0),
					sort_y_roof, WorldView.ROOF_RIDGE, "Ridge_" + sid))
			else:
				var rx2 := r.position.x + r.size.x * 0.5
				props.add_child(_mk_poly_rect(Rect2(rx2 - 1.0, r.position.y, 2.0, r.size.y),
					sort_y_roof, WorldView.ROOF_RIDGE, "Ridge_" + sid))
			props.add_child(_mk_poly_rect(Rect2(r.position.x, r.end.y - 1.0, r.size.x, 1.0),
				sort_y_roof, WorldView.ROOF_EAVE, "Eave_" + sid))

	# 家具：美术 props 图优先，缺图回色块（clue 家具橙色）
	for fr in HouseShape.furniture_rects(data, hpos):
		var rect: Rect2 = fr["rect"]
		var sort_y := rect.end.y
		var pd := AssetDraw.prop_draw(String(fr["name"]), rect)
		if not pd.is_empty():
			var tex: Texture2D = pd["tex"]
			var dst: Rect2 = pd["dst"]
			var fspr := _mk_sprite(tex, dst.position, dst.size, sort_y, "Furn_" + String(fr["name"]))
			props.add_child(fspr)
			_stat["sprite"] += 1
			if bool(fr["clue"]):
				_bake_clue_frame(props, rect, sort_y)
		else:
			var fc: Color = HouseShape.CLUE_COLOR if bool(fr["clue"]) else HouseShape.FURN_COLOR
			props.add_child(_mk_poly_rect(rect, sort_y, fc, "FurnBlock_" + String(fr["name"])))


## base 图的墙行补贴：与 runtime `_draw_art_wall_strips` 同一套落点公式
## （src = base 图里 [该格列, 该格行] 起 64 高的条；dst 顶 = hpos.y + oy*32 - EXTRUDE）。
## 排序键 = 该行南沿；Sprite2D 的 offset 会被 scale 缩放，但这里 scale 恒为 1。
func _bake_wall_strips(props: Node2D, tex: Texture2D, cells: Array, hpos: Vector2,
		data: Dictionary, sort_y: float) -> void:
	var lot: Array = data.get("lot", [0, 0, 0, 0])
	var x0 := int(lot[0])
	var y0 := int(lot[1])
	var xs: Array = []
	for c in cells:
		xs.append(int((c as Dictionary)["cell"].x))
	xs.sort()
	var i := 0
	while i < xs.size():
		var start := int(xs[i])
		var j := i + 1
		while j < xs.size() and int(xs[j]) == start + (j - i):
			j += 1
		var ox := start - x0
		var oy := int((cells[0] as Dictionary)["cell"].y) - y0
		var w := j - i
		var spr := Sprite2D.new()
		spr.name = _nm("Wall_" + String(data.get("id", "")))
		_stat["node"] += 1
		spr.texture = tex
		spr.centered = false
		spr.region_enabled = true
		spr.region_rect = Rect2(float(ox) * TILE, float(oy) * TILE,
			float(w) * TILE, TILE * 2.0)
		var draw_top := hpos.y + float(oy) * TILE - EXTRUDE
		spr.position = Vector2(hpos.x + float(ox) * TILE, sort_y)
		spr.offset = Vector2(0.0, draw_top - sort_y)
		props.add_child(spr)
		_stat["sprite"] += 1
		i = j


## 缺底图时的墙：本体 + 顶面（抬高 h）+ 南立面（高 h），同高连续段合并
## —— 与 runtime `_draw_walls_row` 的分组/合并规则逐条对齐。
func _bake_wall_blocks(props: Node2D, cells: Array, sort_y: float) -> void:
	var groups := {}
	for c in cells:
		var cd: Dictionary = c
		var h := float(cd["height"])
		if not groups.has(h):
			groups[h] = []
		(groups[h] as Array).append(cd["rect"])
	var heights: Array = groups.keys()
	heights.sort()
	for h in heights:
		var row: Array = groups[h]
		row.sort_custom(func(a: Rect2, b: Rect2) -> bool: return a.position.x < b.position.x)
		var hh := float(h)
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
			var bx := start.position.x
			var by := start.position.y
			var w := end_x - bx
			props.add_child(_mk_poly_rect(Rect2(bx, by, w, TILE), sort_y,
				HouseShape.WALL_COLOR, "WallBody"))
			props.add_child(_mk_poly_rect(Rect2(bx, by - hh, w, TILE), sort_y,
				HouseShape.WALL_TOP, "WallTop"))
			props.add_child(_mk_poly_rect(Rect2(bx, by + TILE - hh, w, hh), sort_y,
				HouseShape.WALL_COLOR, "WallFace"))
			i = j


## 线索家具的橙框（runtime 用 draw_rect(w=1) 描边；这里拆四条）
func _bake_clue_frame(props: Node2D, rect: Rect2, sort_y: float) -> void:
	for rr in [
		Rect2(rect.position, Vector2(rect.size.x, 1.0)),
		Rect2(Vector2(rect.position.x, rect.end.y - 1.0), Vector2(rect.size.x, 1.0)),
		Rect2(rect.position, Vector2(1.0, rect.size.y)),
		Rect2(Vector2(rect.end.x - 1.0, rect.position.y), Vector2(1.0, rect.size.y)),
	]:
		props.add_child(_mk_poly_rect(rr, sort_y, HouseShape.CLUE_COLOR, "ClueEdge"))


# ============================================================
# 圆（树 / 井）与立着的 rect（碑 / 路标）
# ============================================================
func _bake_circle(props: Node2D, f: FrameData, sd: Dictionary) -> void:
	var cp: Array = sd.get("center", [0, 0])
	var center := Vector2(float(cp[0]), float(cp[1]))
	var rad := float(sd.get("radius", 4))
	var label := String(sd.get("label", ""))
	var sort_y := WorldView._circle_sort_y(sd)
	var tex := Spec.kind_texture(f.id, "tree" if WorldView._is_standing_tree(label, rad) else "well", sd)
	if tex != null:
		var box := WorldView._prop_box(center, rad, tex)
		var spr := _mk_sprite(tex, box.position, box.size, sort_y, "Prop_" + label)
		props.add_child(spr)
		_stat["sprite"] += 1
		return
	# 缺图 → 纯色降级（C4：是容错，不是验收通过）
	var col := Spec.fallback_color(sd)
	if WorldView._is_standing_tree(label, rad):
		_mark_missing("tree:" + f.id)
		props.add_child(_mk_poly_rect(
			Rect2(center + Vector2(-2.0, rad * 0.22), Vector2(4.0, rad * 0.85)),
			sort_y, WorldView.TRUNK_COLOR, "Trunk"))
		props.add_child(_mk_circle(center, rad, sort_y, col, "Crown"))
		props.add_child(_mk_circle(center + Vector2(-rad * 0.25, -rad * 0.25), rad * 0.55,
			sort_y, Color(col.r * 1.18, col.g * 1.18, col.b * 1.18, col.a), "CrownLit"))
	else:
		_mark_missing("well:" + f.id)
		props.add_child(_mk_circle(center, rad, sort_y, col, "Disc"))


func _bake_rect_prop(props: Node2D, f: FrameData, sd: Dictionary) -> void:
	var rect := Spec.rect_of(sd)
	var label := String(sd.get("label", ""))
	var sort_y := rect.end.y
	var tex := Spec.kind_texture(f.id, "stele", sd)
	if tex != null:
		var spr := _mk_sprite(tex, rect.position, rect.size, sort_y, "Prop_" + label)
		props.add_child(spr)
		_stat["sprite"] += 1
	else:
		_mark_missing("prop_rect:" + label + ":" + f.id)
		props.add_child(_mk_poly_rect(rect, sort_y, Spec.fallback_color(sd), "PropBlock_" + label))


# ============================================================
# 小工具
# ============================================================
## Sprite2D：底边对齐「排序键」，落点左上 = draw_pos，绘制尺寸 = draw_size。
## 坑③：offset 在局部空间、会被 scale 缩放 ⇒ offset = (draw_pos - position) / scale。
func _mk_sprite(tex: Texture2D, draw_pos: Vector2, draw_size: Vector2, sort_y: float,
		nm: String) -> Sprite2D:
	var spr := Sprite2D.new()
	spr.name = _nm(nm)
	_stat["node"] += 1
	spr.texture = tex
	spr.centered = false
	var ts := tex.get_size()
	var sc := Vector2(1.0, 1.0)
	if ts.x > 0.0 and ts.y > 0.0:
		sc = Vector2(draw_size.x / ts.x, draw_size.y / ts.y)
	spr.scale = sc
	spr.position = Vector2(draw_pos.x, sort_y)
	spr.offset = Vector2(0.0, (draw_pos.y - sort_y) / maxf(0.0001, sc.y))
	if absf(sc.x - 1.0) > 0.001:
		spr.offset.x = 0.0  # position.x 已对齐左沿，横向不需要偏移
	return spr


## y-sort 层里的一个实心矩形：节点 position 就是这个 rect 的**排序键 y**，
## 多边形点用相对坐标（这样 y_sort_enabled 的父节点按 position.y 排，和 runtime sort_y 一致）。
func _mk_poly_rect(r: Rect2, sort_y: float, col: Color, nm: String) -> Polygon2D:
	var p := Polygon2D.new()
	p.name = _nm(nm)
	_stat["node"] += 1
	p.position = Vector2(0.0, sort_y)
	p.polygon = _rect_points(r, sort_y)
	p.color = col
	return p


func _mk_circle(center: Vector2, rad: float, sort_y: float, col: Color, nm: String) -> Polygon2D:
	var p := Polygon2D.new()
	p.name = _nm(nm)
	_stat["node"] += 1
	p.position = Vector2(0.0, sort_y)
	var pts := PackedVector2Array()
	for i in CIRCLE_SEGS:
		var ang := TAU * float(i) / float(CIRCLE_SEGS)
		pts.append(center + Vector2(cos(ang), sin(ang)) * rad - Vector2(0.0, sort_y))
	p.polygon = pts
	p.color = col
	return p


func _rect_points(r: Rect2, sort_y: float) -> PackedVector2Array:
	return PackedVector2Array([
		Vector2(r.position.x, r.position.y - sort_y),
		Vector2(r.end.x, r.position.y - sort_y),
		Vector2(r.end.x, r.end.y - sort_y),
		Vector2(r.position.x, r.end.y - sort_y),
	])


func _nm(prefix: String) -> String:
	_seq += 1
	var clean := prefix
	for bad in [":", "/", "@", ".", "\"", " "]:
		clean = clean.replace(bad, "_")
	return "%s_%d" % [clean, _seq]


func _mark_missing(tag: String) -> void:
	if not _missing.has(tag):
		_missing.append(tag)


## 打包：每个子节点必须 owner=root，否则 tscn 里只存根节点（坑②）
func _set_owner(n: Node, root: Node) -> void:
	for c in n.get_children():
		c.owner = root
		_set_owner(c, root)