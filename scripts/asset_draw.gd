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
