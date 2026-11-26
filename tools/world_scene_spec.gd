extends RefCounted

## 地图场景化 Stage 1 —— 「frames.json 的 shape」→「Godot 节点」的唯一映射表（可执行版）
##
## 这里只回答四个问题，一个像素都不画：
##   ① 这个 shape 归哪一层（Ground/Field/Road/Water/Overlay/Houses/Props）；
##   ② 它该用哪种贴图 kind（ground/field/road/river/ring_road/island/hill/dam/stele/tree/well）；
##   ③ 它的贴图从 `scripts/asset_draw.gd` 的哪个函数取（**这里不写死任何贴图文件名**）；
##   ④ 它的格坐标怎么换算（rect → TileMapLayer 的 cell；ground → 整个世界）。
##
## 烘焙器 `tools/bake_world_scene.gd` 和自检 `_mdtest/scene_bake_check.gd` **都调本文件**，
## 保证「烘出来的格数」与「复算的格数」是同一套换算，S5 的 ±0 才有意义。

const AssetDraw := preload("res://scripts/asset_draw.gd")
const WorldView := preload("res://scripts/world_view.gd")

const TILE := 32.0

## ---- 七层：名字 / 顺序 / 类型 / z_index ----
const LAYERS := ["Ground", "Field", "Road", "Water", "Overlay", "Houses", "Props"]
const LAYER_Z := {
	"Ground": -100, "Field": -95, "Road": -90,
	"Water": -88, "Overlay": -84, "Houses": -70, "Props": 0,
}
const LAYER_TYPE := {
	"Ground": "TileMapLayer", "Field": "TileMapLayer", "Road": "TileMapLayer",
	"Water": "Polygon2D", "Overlay": "Node2D", "Houses": "Node2D", "Props": "Node2D",
}
const TILE_LAYERS := ["Ground", "Field", "Road"]
const YSORT_LAYERS := ["Props"]

## Overlay 里各个 kind 的**绝对** z_index（Overlay 节点本身是 LAYER_Z["Overlay"] 一层，
## 子节点用「相对偏移」把它还原成这张表里的绝对值）。
const OVERLAY_Z := {
	"ring_road": -86, "island": -85, "hill": -84, "signpost": -81, "dam": -80, "polygon": -84,
}

## 缺图时纯色降级用的颜色来源：优先 shape 自带的 color 字段（数据说了算）。
static func fallback_color(sd: Dictionary) -> Color:
	return Color(String(sd.get("color", "#888888")))


# ============================================================
# ① 归类：shape → {layer, kind}
# ============================================================
static func classify(sd: Dictionary) -> Dictionary:
	var t := String(sd.get("type", ""))
	var label := String(sd.get("label", ""))
	match t:
		"house":
			return {"layer": "Houses", "kind": "house"}
		"circle":
			var rad := float(sd.get("radius", 4))
			if WorldView._is_standing_tree(label, rad):
				return {"layer": "Props", "kind": "tree"}
			if WorldView._is_ground_landmark(label):
				return {"layer": "Props", "kind": "well"}
			return {"layer": "Props", "kind": "circle"}
		"rect":
			if bool(sd.get("road", false)):
				return {"layer": "Road", "kind": "road"}
			match label:
				"坝":
					return {"layer": "Overlay", "kind": "dam"}
				"碑":
					return {"layer": "Props", "kind": "stele"}
				"路标":
					return {"layer": "Props", "kind": "signpost"}
				"":
					return {"layer": "Field", "kind": "field"}
			return {"layer": "Props", "kind": "prop_rect"}
		"polygon":
			match label:
				"河":
					return {"layer": "Water", "kind": "river"}
				"路":
					return {"layer": "Overlay", "kind": "ring_road"}
				"岛":
					return {"layer": "Overlay", "kind": "island"}
				"山":
					return {"layer": "Overlay", "kind": "hill"}
			return {"layer": "Overlay", "kind": "polygon"}
	return {"layer": "", "kind": "unknown"}


# ============================================================
# ②③ 贴图：kind → asset_draw / world_view 的取值函数
# ============================================================
## 瓦片类（32×32 可平铺）与场景小件类都从这里取。
## 缺图返回 null —— 调用方按 C4「纯色降级 + 登记缺口」处理，不许静默当成功。
static func kind_texture(frame_id: String, kind: String, sd: Dictionary) -> Texture2D:
	match kind:
		"ground":
			return AssetDraw.ground_tex(frame_id)
		"field":
			return AssetDraw.field_tex(frame_id)
		"road":
			return AssetDraw.road_tex(frame_id)
		"river":
			return AssetDraw.river_tex(frame_id)
		"ring_road":
			return AssetDraw.polygon_tex(frame_id, "路")
		"island":
			return AssetDraw.polygon_tex(frame_id, "岛")
		"hill":
			return AssetDraw.polygon_tex(frame_id, "山")
		"dam":
			return AssetDraw.scene_tex(frame_id, "dam")
		"stele":
			return AssetDraw.scene_tex(frame_id, "stele")
		"tree", "well", "circle":
			# 槐 → tree_a*，井 → well_old_a*（认不出一律 null）
			return WorldView._prop_tex(frame_id, String(sd.get("label", "")),
				float(sd.get("radius", 0.0)))
	return null


## 房子：base/roof 两张。asset_draw 没有 house_tex，权威解析在 world_view.gd 的
## `FAMILY` + `_house_tex()`（只读调用，不复制那张族表 —— 免得两处登记走样）。
static func house_textures(sid: String) -> Dictionary:
	return WorldView._house_tex(sid)


# ============================================================
# ④ 格换算：Shape 的几何 → TileMapLayer 的 cell
# ============================================================
static func cell_of(pos: Vector2) -> Vector2i:
	return Vector2i(int(round(pos.x / TILE)), int(round(pos.y / TILE)))


static func rect_of(sd: Dictionary) -> Rect2:
	var r: Array = sd.get("rect", [0, 0, 0, 0])
	return Rect2(float(r[0]), float(r[1]), float(r[2]), float(r[3]))


## rect 是否 32 对齐（不是整数倍时只取整数区域，余量由烘焙器登记）。
static func rect_aligned(r: Rect2) -> bool:
	for v in [r.position.x, r.position.y, r.size.x, r.size.y]:
		if absf(fmod(float(v), TILE)) > 0.01:
			return false
	return true


## 一个 rect 覆盖的格（按 32 网格四舍五入；退化 rect 至少占一格）。
static func rect_cells(r: Rect2) -> Array:
	var x0 := int(round(r.position.x / TILE))
	var x1 := int(round(r.end.x / TILE))
	var y0 := int(round(r.position.y / TILE))
	var y1 := int(round(r.end.y / TILE))
	if x1 <= x0:
		x1 = x0 + 1
	if y1 <= y0:
		y1 = y0 + 1
	var out: Array = []
	for y in range(y0, y1):
		for x in range(x0, x1):
			out.append(Vector2i(x, y))
	return out


## 整个世界铺满的格（地面层用它；世界不是 32 整数倍时向上取整多铺一行/列）。
static func ground_cells(world: Vector2i) -> Array:
	var cols := int(ceil(float(world.x) / TILE))
	var rows := int(ceil(float(world.y) / TILE))
	var out: Array = []
	for y in rows:
		for x in cols:
			out.append(Vector2i(x, y))
	return out


## 某一层全部格的**去重**集合（Field / Road 用）。
## 返回 Dictionary{Vector2i: true}——同一格被两个 rect 覆盖只算一次，
## 烘焙器和自检都走这里，S5 的「±0」才不会被重叠 rect 打破。
static func cells_for(shapes: Array, layer_name: String) -> Dictionary:
	var out := {}
	for s in shapes:
		var sd: Dictionary = s
		var cl := classify(sd)
		if String(cl["layer"]) != layer_name:
			continue
		for c in rect_cells(rect_of(sd)):
			out[c] = true
	return out


static func poly_points(sd: Dictionary) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for p in sd.get("points", []):
		var pa: Array = p
		pts.append(Vector2(float(pa[0]), float(pa[1])))
	return pts