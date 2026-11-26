extends RefCounted

## 美术资产消费点的**纯逻辑工具**：贴图加载 / 家具匹配 / 锚点计算 / 场景图索引。
##
## 只放静态函数，**不放任何 _draw 入口** —— 绘制调用必须落在
## world_view.gd 现有的分支里（A 方案：不新建绘制节点、不设 z_index）。
##
## 缺图一律回 null，由调用方走色块降级（DECIDE D8 永久保留）。
## 本文件不碰数据（houses_data.json / frames.json / manifest 都只读）。

## manifest 路径（美术资产索引，只读）
const MANIFEST_PATH := "res://_ref/art/_assets_a1a3/_a1a3_assets.json"

## 一格 = 32px，与 house_shape.gd 的 TILE 一致（不要写第二份常量）
const TILE := 32.0

## 帧 id → 场景贴图（河/路/田/井/槐）。A4/A5 没有场景图 → 全走色块降级。
const SCENE_FILES := {
	"a1_1926": {
		"road": "assets/village/scene/road_curved_tiles.png",
		"field": "assets/village/scene/field_patch_tiles.png",
		"river": "assets/village/scene/river_a1.png",
		"well": "assets/village/scene/well_old_a1.png",
		"tree": "assets/village/scene/tree_a1.png",
	},
	"a2_1951": {
		"road": "assets/village/scene/road_curved_tiles.png",
		"field": "assets/village/scene/field_a2.png",
		"river": "assets/village/scene/river_a2.png",
		"well": "assets/village/scene/well_old_a2.png",
		"tree": "assets/village/scene/tree_a2.png",
	},
	"a3_1976": {
		"road": "assets/village/scene/road_straight_a3.png",
		"field": "assets/village/scene/field_a3.png",
		"river": "assets/village/scene/river_a3.png",
		"well": "assets/village/scene/well_old_a3.png",
		"tree": "assets/village/scene/tree_a3.png",
	},
}

## 三帧共用的场景小件
const SHARED_SCENE := {
	"dam": "assets/village/scene/dam.png",
	"stele": "assets/village/scene/stele.png",
}

## 32px 单方格**平铺**瓦片（L8 · 地图视觉口径 C1/C3）。
## kind ∈ ground / road / field / river，全部 32×32、100% 不透明，
## 一律配合 `draw_texture_rect(tex, rect, true, ...)` 用 —— 绝不整帧贴一次大图。
##
## ⚠️ 文件名带 `_l8` 的条目是**临时图**（用户 2026-11-26 裁定：A4/A5 美术正式瓦片未到，
##    先拿既有纹样按帧色重新调色顶上）。美术正式图到位后**只改下面这张表的一行路径**，
##    `world_view.gd` 一个字不用动。官方文件名（见 `docs/ART-GAP-A4A5.md` §4 B 组）：
##      ground_a4_tiles.png / ground_a5_tiles.png / road_a4_tiles.png / road_a5_tiles.png
##      field_a4_tiles.png  / field_a5_tiles.png  / river_a4_tiles.png / river_a5_tiles.png
##      （A1–A3 的路/田瓦片官方名同构：road_a1..a3_tiles.png / field_a1..a3_tiles.png）
const TILE_FILES := {
	"a1_1926": {
		"ground": "assets/village/scene/ground_a1_tiles.png",
		"road": "assets/village/scene/road_tiles_l8.png",
		"field": "assets/village/scene/field_tiles_l8.png",
		"river": "assets/village/scene/river_tiles_l8.png",
	},
	"a2_1951": {
		"ground": "assets/village/scene/ground_a2_tiles.png",
		"road": "assets/village/scene/road_tiles_l8.png",
		"field": "assets/village/scene/field_tiles_l8.png",
		"river": "assets/village/scene/river_tiles_l8.png",
	},
	"a3_1976": {
		"ground": "assets/village/scene/ground_a3_tiles.png",
		"road": "assets/village/scene/road_tiles_l8.png",
		"field": "assets/village/scene/field_tiles_l8.png",
		"river": "assets/village/scene/river_tiles_l8.png",
	},
	"a4_2001": {
		"ground": "assets/village/scene/ground_a4_tiles_l8.png",
		"road": "assets/village/scene/road_tiles_l8.png",
		"field": "assets/village/scene/field_tiles_l8.png",
		"river": "assets/village/scene/river_tiles_l8.png",
	},
	"a5_2026": {
		"ground": "assets/village/scene/ground_a5_tiles_l8.png",
		"road": "assets/village/scene/road_a5_tiles_l8.png",
		"field": "assets/village/scene/field_tiles_l8.png",
		"river": "assets/village/scene/river_tiles_l8.png",
	},
}

## polygon 的 label → TILE_FILES 的 kind（§3.2 按 label 分派）。
## 表里没有的 label（**岛 / 山**：美术还没交 roundabout_island_soil|green、山地表瓦片）
## ⇒ 回空串 ⇒ 调用方保留纯色降级，缺口登记在 docs/FEEDBACK-asset-tile-wire-exec.md §2。
const POLYGON_TILE_KIND := {
	"河": "river",
	"路": "road",
}

static var _tex_cache := {}
static var _manifest_cache := {}
static var _prop_index := {}      # short → Array[Dictionary]


## 载入贴图。缺文件回 null（**不报错**，分批交付期间游戏照跑）。
static func load_asset(path: String) -> Texture2D:
	if path.is_empty():
		return null
	if _tex_cache.has(path):
		return _tex_cache[path]
	var tex: Texture2D = null
	if ResourceLoader.exists(path):
		tex = load(path) as Texture2D
	_tex_cache[path] = tex
	return tex


## 美术 manifest（只读，缓存）
static func manifest() -> Dictionary:
	if not _manifest_cache.is_empty():
		return _manifest_cache
	var f := FileAccess.open(MANIFEST_PATH, FileAccess.READ)
	if f == null:
		push_warning("读不到美术 manifest：%s" % MANIFEST_PATH)
		return {}
	var raw := f.get_as_text()
	f.close()
	var parsed: Variant = JSON.parse_string(raw)
	if parsed == null or typeof(parsed) != TYPE_DICTIONARY:
		push_warning("美术 manifest 不是合法 JSON：%s" % MANIFEST_PATH)
		return {}
	_manifest_cache = parsed
	return _manifest_cache


## short → 候选 prop 条目。
## ⚠️ 同一个 short 可能有多条（凳 1×1 / 1×3、粮囤 2×2 / 1×1 …），
## 所以**不能只按 short 取第一条**，必须再拿占地筛。
static func props_by_short(short: String) -> Array:
	if _prop_index.is_empty():
		for p in manifest().get("props", []):
			var pd: Dictionary = p
			var s := String(pd.get("short", pd.get("name", "")))
			if s.is_empty():
				continue
			if not _prop_index.has(s):
				_prop_index[s] = []
			(_prop_index[s] as Array).append(pd)
	return _prop_index.get(short, [])


## 按 short + 占地挑最贴的一条 prop。
## 规则：占地完全一致优先；否则 |Δw|+|Δh| 最小者。
## 找不到（manifest 没有这个 short）回空字典 —— 调用方画色块，**不要报错、不要硬造 id**。
static func prop_match(short: String, fw: int, fh: int) -> Dictionary:
	var cands := props_by_short(short)
	if cands.is_empty():
		return {}
	var best := {}
	var best_score := 1 << 30
	for c in cands:
		var cd: Dictionary = c
		var w := int(cd.get("w", 0))
		var h := int(cd.get("h", 0))
		var score := absi(w - fw) + absi(h - fh)
		if score < best_score:
			best_score = score
			best = cd
	return best


## 家具贴图。短名 + 占地一起匹配；缺图回 null。
static func prop_tex(short: String, fw: int, fh: int) -> Texture2D:
	var e := prop_match(short, fw, fh)
	if e.is_empty():
		return null
	return load_asset("res://" + String(e.get("path", "")))


## 家具贴图落点（D6：底部中心锚点）。
## 画布高 = 占地高 + 1 格（多出的那一格在顶部），底边 = 占地底边。
## 宽度用**数据里的占地宽**（美术只是外观，占地/碰撞仍读 houses_data.json）。
static func prop_rect(rect: Rect2) -> Rect2:
	var h := rect.size.y + TILE
	return Rect2(rect.position.x, rect.end.y - h, rect.size.x, h)


## 家具贴图 + 落点，一次算完。
##
## 贴图画布 = 占地宽×32 × (占地高×32 + 32)，多出的那一格在**顶部**，
## 底边 = 占地底边（D6 底部中心锚点）。
##
## 占地尺寸用**数据里的 rect**（美术只是外观）：源图占地 w×h 与数据占地 fw×fh
## 不一致时按比例缩放，把源图下半部分（真正的占地部分）对齐到数据 rect，
## 多出的那一格（顶部）跟着缩放往上长。
##
## 返回 {} = 没匹配到 / 没图 → 调用方画色块。
static func prop_draw(short: String, rect: Rect2) -> Dictionary:
	var fw := int(round(rect.size.x / TILE))
	var fh := int(round(rect.size.y / TILE))
	var e := prop_match(short, fw, fh)
	if e.is_empty():
		return {}
	var tex := load_asset("res://" + String(e.get("path", "")))
	if tex == null:
		return {}
	var h := int(e.get("h", 0))
	if h <= 0:
		return {}
	var sy := rect.size.y / (float(h) * TILE)
	var dst_h := rect.size.y + TILE * sy
	var dst := Rect2(rect.position.x, rect.end.y - dst_h, rect.size.x, dst_h)
	return {"tex": tex, "dst": dst}


## 场景贴图。kind ∈ road/field/river/well/tree/dam/stele。
static func scene_tex(frame_id: String, kind: String) -> Texture2D:
	if SHARED_SCENE.has(kind):
		return load_asset("res://" + String(SHARED_SCENE[kind]))
	var m: Dictionary = SCENE_FILES.get(frame_id, {})
	if m.is_empty():
		return null
	return load_asset("res://" + String(m.get(kind, "")))


## 32px 平铺瓦片。kind ∈ ground / road / field / river（见 TILE_FILES）。
## 缺图回 null ⇒ 调用方走纯色降级（C4：降级是容错，缺口必须登记）。
static func tile_tex(frame_id: String, kind: String) -> Texture2D:
	var m: Dictionary = TILE_FILES.get(frame_id, {})
	if m.is_empty():
		return null
	var p := String(m.get(kind, ""))
	if p.is_empty():
		return null
	return load_asset("res://" + p)


static func ground_tex(frame_id: String) -> Texture2D:
	return tile_tex(frame_id, "ground")


static func road_tex(frame_id: String) -> Texture2D:
	return tile_tex(frame_id, "road")


static func field_tex(frame_id: String) -> Texture2D:
	return tile_tex(frame_id, "field")


static func river_tex(frame_id: String) -> Texture2D:
	return tile_tex(frame_id, "river")


## polygon 按 label 分派瓦片（§3.2）。分派不出来回 null（调用方画纯色）。
static func polygon_tex(frame_id: String, label: String) -> Texture2D:
	var kind := String(POLYGON_TILE_KIND.get(label, ""))
	if kind.is_empty():
		return null
	return tile_tex(frame_id, kind)


## 点是否在多边形内（射线法，边界算内）。纯逻辑，不依赖节点/渲染，可单测。
## 格心判定用它 —— **不许拿 polygon 的 bbox 近似**（环道的 bbox 比真实环大一圈，会糊到岛上）。
static func points_in_poly(poly: PackedVector2Array, p: Vector2) -> bool:
	var n := poly.size()
	if n < 3:
		return false
	var inside := false
	var j := n - 1
	for i in n:
		var a := poly[i]
		var b := poly[j]
		if ((a.y > p.y) != (b.y > p.y)):
			var x_cross := a.x + (p.y - a.y) / (b.y - a.y) * (b.x - a.x)
			if p.x < x_cross:
				inside = not inside
		j = i
	return inside


## polygon → 32px 格平铺的矩形列表（世界坐标，格对齐）。
## 先判「格心在多边形内」，再把同一行里连着的格合并成一段：
## `draw_texture_rect(tex, 段, true, ...)` 的相位天然与逐格贴一致 ⇒ 像素结果相同，
## 但绘制调用从「几千格」降到「几十段」（A4 河 150×13 格 ⇒ 约 13 段）。
static func poly_tile_rects(poly: PackedVector2Array, tile: float) -> Array:
	var out: Array = []
	if poly.size() < 3 or tile <= 0.0:
		return out
	var box := Rect2(poly[0], Vector2.ZERO)
	for q in poly:
		box = box.expand(q)
	var gy0 := int(floor(box.position.y / tile))
	var gy1 := int(floor((box.end.y - 0.001) / tile))
	var gx0 := int(floor(box.position.x / tile))
	var gx1 := int(floor((box.end.x - 0.001) / tile))
	for gy in range(gy0, gy1 + 1):
		var run_start := -1
		for gx in range(gx0, gx1 + 1):
			var center := Vector2((float(gx) + 0.5) * tile, (float(gy) + 0.5) * tile)
			var hit := points_in_poly(poly, center)
			if hit and run_start < 0:
				run_start = gx
			elif not hit and run_start >= 0:
				out.append(Rect2(float(run_start) * tile, float(gy) * tile,
					float(gx - run_start) * tile, tile))
				run_start = -1
		if run_start >= 0:
			out.append(Rect2(float(run_start) * tile, float(gy) * tile,
				float(gx1 - run_start + 1) * tile, tile))
	return out
