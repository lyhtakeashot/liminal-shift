extends RefCounted

## 证物存档（逆转裁判式证据档案）的数据层。
##
## 纯静态单例：内存里存已收集证物，JSON 落盘到 user:// 供跨启动读回。
## 刻意不用 class_name（与 frame_data.gd / house_shape.gd 同一理由：
## class_name 靠编辑器扫描写进全局类缓存，命令行 / 导出时可能是旧的）。
##
## 条目结构：{key, name, source, text, order}
##   key    唯一键。房屋家具 = "house_id::家具名"；世界地标 = 热点 title
##          （地标跨时代同名 → 同一件证物，只留首次收集那条）
##   name   证物名 = 玩家按 E 看到的标题（账桌 / 石磨 / 老井）
##   source 来源标签（房屋 = "磨坊 · 1926"；地标 = "1926 · 村中"）
##   text   完整描述（CLUE_TEXTS 文案 / 地标 text）
##   order  收集次序（列表按它排序，先收的在前）

const SAVE_PATH := "user://evidence_archive.json"
const SAVE_FALLBACK := "res://.evidence_archive.json"
const SAVE_VERSION := 1

## 存档路径回退链：先试 user://（正常玩家机器），写不进去就退到 res://。
## 有些环境（受限沙箱 / 家目录只读）user:// 不可写，这时至少保证游戏内还能存。
const SAVE_CANDIDATES := [SAVE_PATH, SAVE_FALLBACK]

static var _entries: Array = []   # Array[Dictionary]
static var _keys: Dictionary = {}  # key -> true（去重索引）


## 收集一件证物。返回 true = 新收集；false = 重复（已入过档）或 key 为空。
static func try_collect(key: String, name: String, source: String, text: String) -> bool:
	if key == "":
		return false
	if _keys.has(key):
		return false
	_entries.append({
		"key": key,
		"name": name,
		"source": source,
		"text": text,
		"order": _entries.size(),
	})
	_keys[key] = true
	return true


## 按收集先后返回条目副本（外部改不动内部数据）。
static func get_entries() -> Array:
	return _entries.duplicate(true)


static func is_collected(key: String) -> bool:
	return _keys.has(key)


static func count() -> int:
	return _entries.size()


## 清空档案（测试用；游戏里没有「删档」入口）。
static func clear() -> void:
	_entries.clear()
	_keys.clear()


## 落盘。path 给空 = 走回退链（user:// → res://）；给了就只写那个路径。
## 返回 true = 真的写进去了。
static func save(path: String = "") -> bool:
	var payload := JSON.stringify({"version": SAVE_VERSION, "entries": _entries}, "\t")
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

	clear()
	for item in arr:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var d: Dictionary = item
		var k := String(d.get("key", ""))
		if k == "" or _keys.has(k):
			continue
		_entries.append({
			"key": k,
			"name": String(d.get("name", "")),
			"source": String(d.get("source", "")),
			"text": String(d.get("text", "")),
			"order": int(d.get("order", _entries.size())),
		})
		_keys[k] = true
	return true
