extends RefCounted

## 证物存档（逆转裁判式证据档案）的数据层。
##
## 纯静态单例：内存里存已收集证物，JSON 落盘到 user:// 供跨启动读回。
## 刻意不用 class_name（与 frame_data.gd / house_shape.gd 同一理由：
## class_name 靠编辑器扫描写进全局类缓存，命令行 / 导出时可能是旧的）。
##
## —— 模型（v2）：一件物件 = 一张卡，卡内按年代追加观察记录 ——
##
## 卡结构：
## {
##   "key":    "老槐",              # 归一键（物件身份，不含年代）
##   "name":   "老槐",              # 显示名 = 首次收集时的 hotspot title
##   "order":  0,                   # 收集次序（列表按它排序，先收的在前）
##   "observations": [              # 观察记录，按收集顺序追加
##     {"year": 1926, "title": "老槐", "source": "1926 · 村中",
##      "text": "……", "order": 0},
##     {"year": 1951, "title": "老槐", "source": "1951 · 村中",
##      "text": "……", "order": 1},
##   ]
## }
##
## 归一键（谁算出这个 key 见 scripts/main.gd 的 _collect_evidence）：
##   规则 A 家具 = "<房屋族>::<家具名>"   （同一栋房子换 id 仍是同一件）
##   规则 B 地标 = title 第一个「·」之前的主体名（地标状态变了还是同一件）
##   规则 C 家具带 "族::" 前缀、地标不带 ⇒ 两个命名空间互不混。

const SAVE_PATH := "user://evidence_archive.json"
const SAVE_FALLBACK := "res://.evidence_archive.json"

## 存档格式版本：v1 = 一条一件（无 observations）；v2 = 一件一张卡 + 观察列表。
const SAVE_VERSION := 2

## 存档路径回退链：先试 user://（正常玩家机器），写不进去就退到 res://。
## 有些环境（受限沙箱 / 家目录只读）user:// 不可写，这时至少保证游戏内还能存。
const SAVE_CANDIDATES := [SAVE_PATH, SAVE_FALLBACK]

## try_collect 的三态返回值。
const RESULT_DUPLICATE := 0        # 同年代已记过 → 什么都不做（去重）
const RESULT_NEW_CARD := 1          # 首次见到这件物件 → 建卡 + 第 1 条观察
const RESULT_NEW_OBSERVATION := 2   # 同一件物件的新年代 → 追加一条观察

## 房屋族对照表（任务书 §2.1 规则 A）：同一栋房子在五个年代换了 id，但它是同一栋。
## 家具 key = "<族>::<家具名>"。
## ⚠️ zheng_a4 虽然与陆家同址，但是另一户人家（story：住户对陆家旧事一无所知）
##    ⇒ 族不同、卡不同。
const HOUSE_FAMILY := {
	"lu_house": "lu", "lu_a2": "lu", "lu_a3": "lu",
	"shen_a1": "shen", "shen_a2": "shen", "shen_a3": "shen", "shen_a4": "shen",
	"mill_a1": "mill", "mill_a2": "mill", "mill_a3": "mill",
	"zhou_house": "zhou", "zhou_a2": "zhou", "zhou_a3": "zhou", "zhou_a4": "zhou",
	"market": "market", "zheng_a4": "zheng", "school": "school", "toyshop": "toyshop",
}

static var _cards: Array = []          # Array[Dictionary] 卡片（收集顺序）
static var _index: Dictionary = {}      # key -> 卡片（与 _cards 里同一个字典引用）
static var _new_keys: Dictionary = {}   # key -> true（自上次结算以来动过的卡）
static var _new_cards := 0              # 新建卡计数
static var _new_observations := 0       # 追加观察计数


# ---- 归一键 ----------------------------------------------------------------

## 规则 A：家具 key = "<房屋族>::<家具名>"。
static func furniture_key(house_id: String, furniture: String) -> String:
	if furniture == "":
		return ""
	var fam := String(HOUSE_FAMILY.get(house_id, house_id))
	return "%s::%s" % [fam, furniture]


## 规则 B：地标 key = title 第一个「·」之前的主体名（没「·」就用整串）。
static func landmark_key(title: String) -> String:
	if title == "":
		return ""
	var head := title.split("·")[0].strip_edges()
	return head if head != "" else title.strip_edges()


## 归一化任意来源的 key（旧存档迁移用）：
## 带 "::" 的是旧版家具键 "<house_id>::<家具名>" → 按族表归一；
## 不带的是地标 title → 按「· 之前」规则归一。
static func normalize_key(raw: String) -> String:
	if raw == "":
		return ""
	if raw.contains("::"):
		var parts := raw.split("::", true)
		if parts.size() >= 2:
			return furniture_key(String(parts[0]), String(parts[1]))
		return raw
	return landmark_key(raw)


# ---- 收集 ------------------------------------------------------------------

## 收集一件物件的一次观察。返回三态（RESULT_*）：
##   key 首现        → 建卡 + 第 1 条观察（RESULT_NEW_CARD）
##   同年代已记过    → 什么都不做（RESULT_DUPLICATE）
##   新年代          → 该卡 observations 末尾追加一条（RESULT_NEW_OBSERVATION）
static func try_collect(key: String, name: String, source: String, text: String,
		year: int = 0) -> int:
	if key == "":
		return RESULT_DUPLICATE
	var card: Dictionary = _index.get(key, {})
	if card.is_empty():
		var c := {
			"key": key,
			"name": name,
			"order": _cards.size(),
			"observations": [_make_observation(name, source, text, year, 0)],
		}
		_cards.append(c)
		_index[key] = c
		_new_keys[key] = true
		_new_cards += 1
		return RESULT_NEW_CARD

	# 卡已存在：同年代已记过 → 什么都不做（不追加、不改顺序）
	var obs: Array = card.get("observations", [])
	for o in obs:
		if int((o as Dictionary).get("year", 0)) == year:
			return RESULT_DUPLICATE
	obs.append(_make_observation(name, source, text, year, obs.size()))
	_new_keys[key] = true
	_new_observations += 1
	return RESULT_NEW_OBSERVATION


static func _make_observation(title: String, source: String, text: String,
		year: int, order: int) -> Dictionary:
	return {
		"year": year,
		"title": title,
		"source": source,
		"text": text,
		"order": order,
	}


# ---- 读取 ------------------------------------------------------------------

## 按收集先后返回卡片副本（外部改不动内部数据）。
## 每张卡：{key, name, order, observations:[{year,title,source,text,order}]}
static func get_entries() -> Array:
	return _cards.duplicate(true)


static func is_collected(key: String) -> bool:
	return _index.has(key)


## 卡数（一张卡 = 一件物件）。
static func count() -> int:
	return _cards.size()


## 观察记录总条数（一张卡可能有多个年代的观察）。
static func observation_count() -> int:
	var n := 0
	for c in _cards:
		n += (c as Dictionary).get("observations", []).size()
	return n


## 某张卡的观察（副本）。
static func get_observations(key: String) -> Array:
	var card: Dictionary = _index.get(key, {})
	if card.is_empty():
		return []
	return (card.get("observations", []) as Array).duplicate(true)


# ---- 新增计数（列表页「新」角标用） -----------------------------------------

## 自上次结算以来新增了什么：{"cards": 卡数, "observations": 观察数}。
static func pending_new() -> Dictionary:
	return {"cards": _new_cards, "observations": _new_observations}


## 结算（关档时调）：清掉「新」标记与计数。
static func clear_new_flags() -> void:
	_new_keys.clear()
	_new_cards = 0
	_new_observations = 0


## 这张卡自上次结算以来被动过（新建卡或追加了观察）→ 列表页标「新」。
static func is_new_key(key: String) -> bool:
	return _new_keys.has(key)


# ---- 落盘 / 读回 -----------------------------------------------------------

## 清空档案（测试用；游戏里没有「删档」入口）。
static func clear() -> void:
	_cards.clear()
	_index.clear()
	clear_new_flags()


## 落盘。path 给空 = 走回退链（user:// → res://）；给了就只写那个路径。
## 返回 true = 真的写进去了。
static func save(path: String = "") -> bool:
	var payload := JSON.stringify({"version": SAVE_VERSION, "entries": _cards}, "\t")
	var targets: Array = [path] if path != "" else SAVE_CANDIDATES
	for p in targets:
		var f := FileAccess.open(p, FileAccess.WRITE)
		if f == null:
			continue
		f.store_string(payload)
		f.close()
		return true
	push_warning("证物存档写不进去（试过 %s）" % str(targets))
	return false


## 读回。文件不存在 / 坏了都返回 false（档案保持空，不崩）。
## path 给空 = 走回退链，按 SAVE_CANDIDATES 顺序找第一个存在的。
## v1 旧存档（一条一件、无 observations）会被当成「一张卡 + 一条观察」读进来。
static func load(path: String = "") -> bool:
	var target := path
	if target == "":
		target = ""
		for p in SAVE_CANDIDATES:
			if FileAccess.file_exists(p):
				target = p
				break
		if target == "":
			return false
	elif not FileAccess.file_exists(target):
		return false

	var f := FileAccess.open(target, FileAccess.READ)
	if f == null:
		return false
	var raw := f.get_as_text()
	f.close()

	var parsed: Variant = JSON.parse_string(raw)
	if parsed == null or typeof(parsed) != TYPE_DICTIONARY:
		push_warning("证物存档不是合法 JSON：%s" % target)
		return false
	var arr: Variant = (parsed as Dictionary).get("entries", [])
	if typeof(arr) != TYPE_ARRAY:
		return false
	var version := int((parsed as Dictionary).get("version", 1))

	clear()
	for item in arr:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var d: Dictionary = item
		if version >= SAVE_VERSION:
			_load_card_v2(d)
		else:
			_load_card_v1(d)
	return true


## v2：卡结构完整，直接读（key 再归一一次，防手改存档写歪）。
static func _load_card_v2(d: Dictionary) -> void:
	var key := normalize_key(String(d.get("key", "")))
	if key == "":
		return
	var name := String(d.get("name", ""))
	if name == "":
		name = key
	var card := _ensure_card(key, name, int(d.get("order", _cards.size())))
	var obs: Array = card["observations"]
	for o in d.get("observations", []):
		if typeof(o) != TYPE_DICTIONARY:
			continue
		var od: Dictionary = o
		obs.append({
			"year": int(od.get("year", 0)),
			"title": String(od.get("title", name)),
			"source": String(od.get("source", "")),
			"text": String(od.get("text", "")),
			"order": obs.size(),
		})


## v1 旧存档：一条 = 一件 = 一张卡 + 一条观察（年份从 source 里解析，解析不出当 0）。
static func _load_card_v1(d: Dictionary) -> void:
	var key := normalize_key(String(d.get("key", "")))
	if key == "":
		return
	var name := String(d.get("name", ""))
	if name == "":
		name = key
	var source := String(d.get("source", ""))
	var card := _ensure_card(key, name, int(d.get("order", _cards.size())))
	var obs: Array = card["observations"]
	obs.append({
		"year": _year_from_source(source),
		"title": name,
		"source": source,
		"text": String(d.get("text", "")),
		"order": obs.size(),
	})


## 取（或新建）一张卡。同一 key 的旧条目会并进同一张卡（观察都留着）。
static func _ensure_card(key: String, name: String, order: int) -> Dictionary:
	var card: Dictionary = _index.get(key, {})
	if card.is_empty():
		card = {"key": key, "name": name, "order": order, "observations": []}
		_cards.append(card)
		_index[key] = card
	return card


## 从来源标签里抠年份："磨坊 · 1926" / "1926 · 村中" → 1926；抠不出 → 0。
static func _year_from_source(source: String) -> int:
	for part in source.split(" · "):
		var t := part.strip_edges()
		if t.is_valid_int():
			var v := int(t)
			if v > 0:
				return v
	return 0
