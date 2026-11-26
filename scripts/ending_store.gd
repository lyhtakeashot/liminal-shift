extends RefCounted

## 归档表填格结果 + 存档（story.md §10.1）。
##
## ⚠️ 与证物档案（scripts/evidence_store.gd）是**两套数据、两套存档、两把键**：
##   证物档案 = 玩家**看到过什么**（一件物件一张卡，卡内按年追加观察）
##   归档表   = 玩家**怎么记**（把物证填成一份卷宗）
##   合并会让「看到」和「记下」互相污染（任务书 §2.7），所以本文件刻意独立。
##
## 刻意不用 class_name（与 frame_data.gd / evidence_store.gd 同一理由：
## class_name 靠编辑器扫描写进全局类缓存，命令行 / 导出时可能是旧的）。
##
## 落盘：user://ending_form.json（res:// 在导出版本里只读 ⇒ 只当回退）。
## 容错：读档时缺字段 / 值不在选项表里 ⇒ 归位成空串，绝不崩（任务书 §3.1）。

const SAVE_PATH := "user://ending_form.json"
const SAVE_FALLBACK := "res://.ending_form.json"
## 存档格式版本（照 evidence_store.gd 的 SAVE_VERSION 的做法，本线从 1 起）。
const SAVE_VERSION := 1
## 回退链：先试 user://（正常玩家机器），写不进去再退 res://。
const SAVE_CANDIDATES := [SAVE_PATH, SAVE_FALLBACK]

## ---- 选项表（story.md:633-658 原文，一个字都不许改） ----------------------
const YEARS: Array = ["1926", "1951", "1976", "2001", "2026"]
const MOTIVES: Array = ["激情", "蓄谋", "放任", "无"]
const INTENTS: Array = ["直接故意", "间接故意", "过失", "无"]
const CASE_KINDS: Array = ["杀人灭口", "债务纠纷"]
const EARLIEST: Array = ["1926", "1951", "1976", "无法确定"]
const BURIAL: Array = ["补丁下", "井下", "地基下", "无法确定"]
const COUNTS: Array = ["一", "二", "三", "无法确定"]
const EXITS: Array = ["已归档", "存疑"]

## 「无法确定」是玩家自己的选择，不是系统给的正确答案（story.md:601-603）。
const UNKNOWN := "无法确定"

## 两列的列号（表格 = 五行 × 两列）。
const COL_MOTIVE := 0     # 动机形态
const COL_INTENT := 1     # 故意形态


## ---- 状态（字段名照任务书 §3.1，别改名 —— 记述生成器按这套键读） ----------
static var motive: Dictionary = {}    # "1926"/"1951"/… → 动机形态
static var intent: Dictionary = {}    # 同上 → 故意形态
static var case_1951 := ""            # "杀人灭口" / "债务纠纷"
static var earliest := ""             # "1926"/"1951"/"1976"/"无法确定"
static var burial := ""               # "补丁下"/"井下"/"地基下"/"无法确定"
static var count := ""                # "一"/"二"/"三"/"无法确定"
static var exit_choice := ""          # "已归档" / "存疑"


# ---- 清空 ------------------------------------------------------------------

## 全部归空（测试用；也是读档前的复位）。
static func reset() -> void:
	motive.clear()
	intent.clear()
	case_1951 = ""
	earliest = ""
	burial = ""
	count = ""
	exit_choice = ""


## 一格一格都空着吗？（表格默认必须全空 —— 没有默认值，任务书 §2.1）
static func is_blank() -> bool:
	if not case_1951.is_empty() or not earliest.is_empty() \
			or not burial.is_empty() or not count.is_empty():
		return false
	for y in YEARS:
		if motive.has(y) or intent.has(y):
			return false
	return true


# ---- 表格：五行 × 两列 -----------------------------------------------------

## 选项表（列号 → 允许值）。非法列号返回空数组。
static func options_for_col(col: int) -> Array:
	if col == COL_MOTIVE:
		return MOTIVES
	if col == COL_INTENT:
		return INTENTS
	return []


## 某年某列的当前值（没填 = 空串）。
static func get_cell(year: String, col: int) -> String:
	var d: Dictionary = motive if col == COL_MOTIVE else intent
	if col != COL_MOTIVE and col != COL_INTENT:
		return ""
	return str(d.get(year, ""))


## 填一格。非法年份 / 非法值 ⇒ 返回 false 且不改状态（写歪的存档进不来）。
static func set_cell(year: String, col: int, value: String) -> bool:
	if not YEARS.has(year):
		return false
	var allowed := options_for_col(col)
	if allowed.is_empty():
		return false
	if value != "" and not allowed.has(value):
		return false
	var d: Dictionary = motive if col == COL_MOTIVE else intent
	if value == "":
		d.erase(year)
	else:
		d[year] = value
	return true


## 某年两列都填了吗？
static func is_row_filled(year: String) -> bool:
	return not get_cell(year, COL_MOTIVE).is_empty() \
		and not get_cell(year, COL_INTENT).is_empty()


## 五行十格全填满了吗？（「五代之中」那行只在填满时才算得出来）
static func is_grid_filled() -> bool:
	for y in YEARS:
		if not is_row_filled(y):
			return false
	return true


# ---- 四个单选 --------------------------------------------------------------

## 单选字段的允许值；field 不在表里返回空数组。
static func options_for_radio(field: String) -> Array:
	match field:
		"case_1951":
			return CASE_KINDS
		"earliest":
			return EARLIEST
		"burial":
			return BURIAL
		"count":
			return COUNTS
	return []


static func get_radio(field: String) -> String:
	match field:
		"case_1951":
			return case_1951
		"earliest":
			return earliest
		"burial":
			return burial
		"count":
			return count
	return ""


static func set_radio(field: String, value: String) -> bool:
	var allowed := options_for_radio(field)
	if allowed.is_empty():
		return false
	if value != "" and not allowed.has(value):
		return false
	match field:
		"case_1951":
			case_1951 = value
		"earliest":
			earliest = value
		"burial":
			burial = value
		"count":
			count = value
	return true


## 某单选字段填了吗？（空串 = 未填）
static func is_radio_filled(field: String) -> bool:
	return not get_radio(field).is_empty()


# ---- 出口 ------------------------------------------------------------------

static func get_exit() -> String:
	return exit_choice


static func set_exit(value: String) -> bool:
	if value != "" and not EXITS.has(value):
		return false
	exit_choice = value
	return true


# ---- 交给记述生成器的快照 --------------------------------------------------

## 快照（副本；外部改不动内部状态）。
## 键名与任务书 §3.1 的字段名一一对应。
static func snapshot() -> Dictionary:
	return {
		"motive": motive.duplicate(),
		"intent": intent.duplicate(),
		"case_1951": case_1951,
		"earliest": earliest,
		"burial": burial,
		"count": count,
		"exit_choice": exit_choice,
	}


# ---- 落盘 / 读回 -----------------------------------------------------------

## 落盘。path 给空 = 走回退链（user:// → res://）；给了就只写那个路径。
static func save(path: String = "") -> bool:
	var payload := JSON.stringify({
		"version": SAVE_VERSION,
		"motive": motive,
		"intent": intent,
		"case_1951": case_1951,
		"earliest": earliest,
		"burial": burial,
		"count": count,
		"exit_choice": exit_choice,
	}, "\t")
	var targets: Array = [path] if path != "" else SAVE_CANDIDATES
	for p in targets:
		var f := FileAccess.open(p, FileAccess.WRITE)
		if f == null:
			continue
		f.store_string(payload)
		f.close()
		return true
	push_warning("归档表存档写不进去（试过 %s）" % str(targets))
	return false


## 读回。文件不存在 / 坏了 / 不是字典 ⇒ 返回 false 且状态保持空（不崩）。
## 字段缺失 / 值不在选项表里 ⇒ 那一格归空串（脏存档也能读，任务书 §3.1）。
static func load(path: String = "") -> bool:
	var target := path
	if target == "":
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
		push_warning("归档表存档不是合法 JSON：%s" % target)
		return false
	_apply(parsed as Dictionary)
	return true


## 把一份（可能脏的）字典灌进状态：先复位，再逐格校验。
static func _apply(d: Dictionary) -> void:
	reset()

	var m: Variant = d.get("motive", {})
	if typeof(m) == TYPE_DICTIONARY:
		for y in YEARS:
			var v := _valid(str((m as Dictionary).get(y, "")), MOTIVES)
			if v != "":
				motive[y] = v

	var it: Variant = d.get("intent", {})
	if typeof(it) == TYPE_DICTIONARY:
		for y in YEARS:
			var v := _valid(str((it as Dictionary).get(y, "")), INTENTS)
			if v != "":
				intent[y] = v

	case_1951 = _valid(str(d.get("case_1951", "")), CASE_KINDS)
	earliest = _valid(str(d.get("earliest", "")), EARLIEST)
	burial = _valid(str(d.get("burial", "")), BURIAL)
	count = _valid(str(d.get("count", "")), COUNTS)
	exit_choice = _valid(str(d.get("exit_choice", "")), EXITS)


## 值在允许表里就原样返回，否则空串。
static func _valid(value: String, allowed: Array) -> String:
	return value if allowed.has(value) else ""