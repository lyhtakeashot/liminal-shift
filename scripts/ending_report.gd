extends RefCounted

## 记述生成器（story.md §10.3）：把玩家填的东西**念出来**。
##
## 纯逻辑：输入 = 归档表的填格快照（scripts/ending_store.gd 的 snapshot()），
## 输出 = 一套文本。**不碰 UI、不碰存档、不读文件。**
##
## ⚠️ 三条铁律（任务书 §2.2 / §3.2）：
##   1. 不是「每格一个正确值 + 判对错」，而是**按填的内容走分支** ——
##      填「井下」不是错，只是念成「井下」。
##   2. 填错不报错，只让记述降级（变体丙）。
##   3. 不给案子任何道德结论（story.md:780 明令：一句都不要加）。
##
## 变体分流（story.md:692-742）：
##   甲 = 四个单选都填了确定值，且 1951 性质 = 债务纠纷
##   乙 = 同上，但 1951 性质 = 杀人灭口 ⇒ 后面整段消失，只剩两行
##   丙 = 任一单选没填 / 填了「无法确定」⇒ 不报错，只降级
##   ⇒ 乙丙可叠加时**以丙为准**（丙更宽；反馈文档里写明这个优先级）。

## ---- 事实表（story.md §4.6.1 五件事怎么落 —— 两句硬句就从这张表推） -------
## 套一 = 动机形态，套二 = 故意形态。
const DEEDS: Array = [
	{"year": "1926", "who": "陆文", "age": "19", "motive": "放任", "intent": "间接故意"},
	{"year": "1951", "who": "陆敬之", "age": "24", "motive": "蓄谋", "intent": "直接故意"},
	{"year": "1976", "who": "方某", "age": "?", "motive": "蓄谋", "intent": "直接故意"},
	{"year": "2001", "who": "——", "age": "", "motive": "蓄谋", "intent": "无"},
	{"year": "2026", "who": "沈明远", "age": "", "motive": "无", "intent": "无"},
]

## 归档员名字随帧变（docs/npc.md:33-39）。
const ARCHIVIST := {
	1926: "陈阿福",
	1951: "陈志强",
	1976: "陈卫东",
	2001: "陈小军",
	2026: "陈浩",
}

## 卷宗抬头（story.md:633-637）。
const CASE_NO := "7231001"
const PLACE := "██村 东街"
const EVENT := "连续非自然死亡"

const UNKNOWN := "无法确定"

## ⚠️ 这里刻意**不写**那几个禁用词的常量表 —— story.md:780 要求本线一个字都不出现，
## 而仓库级 grep 会把常量表本身算成命中（§4.4）。禁用词清单放在测试里现拼。

## 「埋尸位置」怎么念：补丁下 = 故事原文的「北车道圆形补丁下」；
## 其余照玩家填的念（井就在补丁下，但井不是位置的下限 —— story.md:665）。
const BURIAL_TEXT := {
	"补丁下": "北车道圆形补丁下",
	"井下": "井下",
	"地基下": "地基下",
	"无法确定": "无法确定",
}

## 中文数字（「二」「三」这些档位用）。
const CN := ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
## 中文纪年用字（这里要的是「二〇〇一」那种，0 是「〇」不是「零」）。
const CN_DIGIT := ["〇", "一", "二", "三", "四", "五", "六", "七", "八", "九"]


# ---- 对外接口 ---------------------------------------------------------------

## 生成一份记述。st = 归档表快照（ending_store.gd 的 snapshot()）。
## 可选键 st["frame_year"]（int，默认 2026）—— 只影响抬头里的归档员。
##
## 返回：
##   variant     "甲" / "乙" / "丙"
##   lines       要逐行画的完整行表（含空行）
##   prose       变体专属的正文行（去掉空行和固定两句）—— 测试用
##   fixed       固定两句（永远出现，不管玩家怎么填）
##   body        lines 拼成的全文（\n 分隔）
##   exit_text   出口文本（没选出口 = ""）
##   exit_lines  exit_text 按 \n 拆开（画两行用）
##   counts      四档统计（格子没填满 = 空字典）
##   archivist / case_no / place / event   卷宗抬头
static func build(st: Dictionary) -> Dictionary:
	var variant_v := variant_of(st)
	var fixed_v := fixed_lines()
	var counts := {}
	var lines: Array = []

	match variant_v:
		"乙":
			lines = _build_yi(st)
		"丙":
			lines = _build_bing(st)
		_:
			var jia := _build_jia(st)
			lines = jia["lines"]
			counts = jia["counts"]

	# 兜底：无论走哪个变体，固定两句必须在全文里（story.md:732-736）。
	# 这是「表自己算出来的事实」，不是玩家填的内容，所以不参与变体的「消失」。
	var fixed_line := _fixed_line()
	if not _has_line(lines, fixed_line):
		lines = _append_fixed(lines)

	var body := "\n".join(_to_strings(lines))
	var exit_v := str(st.get("exit_choice", ""))
	var exit_t := exit_text(exit_v)

	return {
		"variant": variant_v,
		"lines": _to_strings(lines),
		"prose": _prose_of(lines, fixed_v),
		"fixed": fixed_v,
		"body": body,
		"exit_text": exit_t,
		"exit_lines": exit_t.split("\n") if exit_t != "" else [],
		"exit_choice": exit_v,
		"counts": counts,
		"archivist": archivist_for(int(st.get("frame_year", 2026))),
		"case_no": CASE_NO,
		"place": PLACE,
		"event": EVENT,
	}


## 变体分流：丙 > 乙 > 甲。
static func variant_of(st: Dictionary) -> String:
	for f in ["case_1951", "earliest", "burial", "count"]:
		var v := str(st.get(f, ""))
		if v.is_empty() or v == UNKNOWN:
			return "丙"
	if str(st.get("case_1951", "")) == "杀人灭口":
		return "乙"
	return "甲"


## 固定两句 —— **从 §4.6.1 的事实表推导**，不写死成一句话：
##   「无起意」＝套一的「放任」（没有工具、没有冲突，只是照常办事 —— §4.6.2）
##   「无死者」＝套二的「无」（他手上一个人都没碰）
## 口径只算 A1–A4 四起：A5 是「不知情者」，本来就没起意、也没碰人，
## 把他算进来会得出「第五起无起意。第五起无死者。」——那是废话，不是发现。
static func fixed_lines() -> Array:
	var out: Array = []
	for i in range(mini(4, DEEDS.size())):
		var d: Dictionary = DEEDS[i]
		if str(d.get("motive", "")) == "放任":
			out.append("第%s起无起意。" % _cn(i + 1))
		if str(d.get("intent", "")) == "无":
			out.append("第%s起无死者。" % _cn(i + 1))
	return out


## 「五代之中」的四档统计 —— 按**玩家填的**十格算（表格自己不会替他填）。
## 一格没填 = 算不出来 ⇒ 返回空字典（那一行就不出现，属于局部降级）。
##
## 四档互斥（加起来正好 = 5，与 story.md:701 的「一、二、一、一」对得上）：
##   不知情者        = 无 / 无
##   算计而未动手者  = 有起意（套一非「无」）/ 套二「无」
##   动手者          = 套二「直接故意」
##   起意者          = 其余（放任 + 间接故意这类「起了意、但没亲手」）
static func counts_of(st: Dictionary) -> Dictionary:
	var out := {"起意者": 0, "动手者": 0, "算计而未动手者": 0, "不知情者": 0}
	var motives: Dictionary = st.get("motive", {})
	var intents: Dictionary = st.get("intent", {})
	for d in DEEDS:
		var y := str((d as Dictionary).get("year", ""))
		var m := str(motives.get(y, ""))
		var it := str(intents.get(y, ""))
		if m.is_empty() or it.is_empty():
			return {}
		var b := bucket_of(m, it)
		if b.is_empty():
			return {}
		out[b] = int(out[b]) + 1
	return out


## 一格（动机, 故意）落到四档哪一档。填不全返回空串。
static func bucket_of(m: String, it: String) -> String:
	if m.is_empty() or it.is_empty():
		return ""
	if m == "无" and it == "无":
		return "不知情者"
	if it == "无":
		return "算计而未动手者"
	if it == "直接故意":
		return "动手者"
	return "起意者"


## 出口文本（story.md:748-760 原文两段）。
static func exit_text(choice: String) -> String:
	match choice:
		"已归档":
			return "本案已归档。\n世界刑侦陈列馆 · 第七十二万三千零一卷"
		"存疑":
			return "本案存疑。\n第七十二万三千零一卷 · 暂列待考"
	return ""


## 归档员名字（随帧变；未知帧回落 2026 的陈浩 —— 表只在 A5 开）。
static func archivist_for(year: int) -> String:
	return str(ARCHIVIST.get(year, ARCHIVIST[2026]))


## 中文纪年：「1951」→「一九五一年」（0 写「〇」，与故事里的「二〇〇一」一致）。
static func cn_year(year: String) -> String:
	if not year.is_valid_int():
		return year
	var out := ""
	for i in year.length():
		out += CN_DIGIT[int(year[i])]
	return out


# ---- 三个变体 ---------------------------------------------------------------

## 变体甲：全填确定值 + 1951 = 债务纠纷（story.md:692-709）。
static func _build_jia(st: Dictionary) -> Dictionary:
	var counts := counts_of(st)
	var out: Array = []
	out.append("自民国十五年至公元二〇〇一年，本地点历五代，五人涉事。")
	out.append("")
	out.append("最早一具：%s。" % _year_label(str(st.get("earliest", ""))))
	out.append("埋尸位置：%s。" % _burial_text(str(st.get("burial", ""))))
	out.append("埋葬人数：%s。未寻获：一（陆文，民国十五年，下游）。" % str(st.get("count", "")))
	out.append("")
	if not counts.is_empty():
		out.append("五代之中：起意者%s，动手者%s，算计而未动手者%s，不知情者%s。" % [
			_cn(int(counts["起意者"])), _cn(int(counts["动手者"])),
			_cn(int(counts["算计而未动手者"])), _cn(int(counts["不知情者"])),
		])
	out.append(_fixed_line())
	out.append("")
	out.append("一九五一年一起，性质：%s。" % str(st.get("case_1951", "")))
	out.append("死者陆敬之，男，二十四岁。")
	out.append("本地点自民国十六年起向陆家支付款项三十七笔，至四十年止。")
	out.append("")
	out.append("没有人被平反。因为没有人是无辜的。")
	return {"lines": out, "counts": counts}


## 变体乙：1951 填「杀人灭口」⇒ 同一批证据，只换一处，后面整段消失（story.md:711-721）。
## 三十七笔款一个字都不出现 —— 档案上他只是个受害者。
static func _build_yi(st: Dictionary) -> Array:
	var out: Array = []
	out.append("一九五一年一起，性质：杀人灭口。")
	out.append("死者陆敬之，男，二十四岁。")
	out.append("")
	out.append(_fixed_line())
	return out


## 变体丙：某几格「无法确定」/ 没填 ⇒ 不报错，只降级（story.md:723-742）。
## 只念三个「事实栏」，其余（五代之中 / 1951 段 / 收官句）全部降掉。
static func _build_bing(st: Dictionary) -> Array:
	var out: Array = []
	out.append("最早一具：%s。" % _year_label(str(st.get("earliest", ""))))
	out.append("埋尸位置：%s。" % _burial_text(str(st.get("burial", ""))))
	var c := str(st.get("count", ""))
	out.append("埋葬人数：%s。" % (c if not c.is_empty() else "未填"))
	out.append("")
	out.append(_fixed_line())
	return out


# ---- 小工具 -----------------------------------------------------------------

static func _fixed_line() -> String:
	# story.md:702 是**一行两句**，中间没有任何分隔符（不是两行、也不是空格隔开）。
	return "".join(fixed_lines())


## 年份怎么念：填了 → 「一九五一年」；空 → 「未填」；无法确定 → 「无法确定」。
static func _year_label(year: String) -> String:
	if year.is_empty():
		return "未填"
	if year == UNKNOWN:
		return UNKNOWN
	return cn_year(year) + "年"


static func _burial_text(burial: String) -> String:
	if burial.is_empty():
		return "未填"
	return str(BURIAL_TEXT.get(burial, burial))


## 0..9 → 中文数字；越界回落阿拉伯数字（别崩）。
static func _cn(n: int) -> String:
	if n >= 0 and n < CN.size():
		return CN[n]
	return str(n)


static func _has_line(lines: Array, text: String) -> bool:
	for ln in lines:
		if str(ln) == text:
			return true
	return false


## 末尾补固定句（空一行）。
static func _append_fixed(lines: Array) -> Array:
	var out := lines.duplicate()
	if not out.is_empty() and str(out[out.size() - 1]) != "":
		out.append("")
	out.append(_fixed_line())
	return out


## 变体专属正文行：去掉空行与固定两句。
static func _prose_of(lines: Array, fixed_v: Array) -> Array:
	var out: Array = []
	var fixed_line := "".join(fixed_v)
	for ln in lines:
		var t := str(ln)
		if t.is_empty() or t == fixed_line:
			continue
		out.append(t)
	return out


static func _to_strings(lines: Array) -> Array:
	var out: Array = []
	for ln in lines:
		out.append(str(ln))
	return out