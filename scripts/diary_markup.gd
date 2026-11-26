extends RefCounted

## L16 · 极简日记标记解析器（纯逻辑，无节点、无 BBCode）。
##
## 语法权威出处：`docs/diary-markup.md`（四个标记）。
## 本文件只把原稿切成「段结构」，怎么画由 `scripts/diary_page.gd` 决定。
## **不生成 BBCode** —— 删除线要自绘（富文本控件的下划线标签线宽由字体决定，
## 实测太细，`docs/diary-markup.md:52-63`）。
##
## 四个标记：
##   {{旧|新}}          一处涂改
##   {{旧A|旧B|新}}     多处涂改（真本折叠成「首 → … → 尾」）
##   ---                分隔行
##   行首制表符          缩进
##
## 输出（按出现顺序的字典数组）：
##   {"kind": "text",     "text": "…"}  正常墨色
##   {"kind": "strike",   "text": "…"}  真本：旧字，灰 + 2px 删除线（页面自绘）
##   {"kind": "red",      "text": "…"}  真本：改正的新字，暗红（加粗靠页面重复绘制）
##   {"kind": "ellipsis", "text": "…"}  多段涂改的折叠标记，灰、不画删除线
##   {"kind": "sep"}                    ---（淡色小圆点行）
##   {"kind": "indent",   "text": ""}   行首制表符：该行起笔右移一个缩进量
##
## ⚠️ 换行不单独成段：`\n` 保留在 text/strike/red/ellipsis/indent 的 `text` 里，
##    由 `diary_page.gd` 排版时切开（它要按像素宽度折行，只有它知道可用宽度）。
##
## ⚠️ 假本（is_raw_book = false）**不产生** strike / red / ellipsis 段 —— 见 D1 / D4 / D9。
##    `{{A|B|C}}` 假本只留 C；真本留 A（划掉）+ … + C（红）。

const KIND_TEXT := "text"
const KIND_STRIKE := "strike"
const KIND_RED := "red"
const KIND_ELLIPSIS := "ellipsis"
const KIND_SEP := "sep"
const KIND_INDENT := "indent"


## 解析原稿。
## is_raw_book = false → 假本（只剩最后一段，没有任何标记）
## is_raw_book = true  → 真本（划线 + 红字，多段折叠）
static func parse(raw: String, is_raw_book: bool) -> Array:
	var out: Array = []
	var buf := ""
	var i := 0
	var n := raw.length()
	var at_line_start := true

	while i < n:
		var ch := raw[i]

		if ch == "\n":
			buf += ch
			at_line_start = true
			i += 1
			continue

		# 行首制表符 ⇒ 一个 indent 段（只认行首那一个；行中的制表符当普通字符）
		if at_line_start and ch == "\t":
			buf = _flush(buf, out)
			out.append({"kind": KIND_INDENT, "text": ""})
			at_line_start = false
			i += 1
			continue

		at_line_start = false

		# {{ … }} 涂改
		if ch == "{" and i + 1 < n and raw[i + 1] == "{":
			var end := raw.find("}}", i + 2)
			if end == -1:
				# 没闭合 ⇒ 原样保留到最后（绝对不能吞掉后面的内容，D7）
				buf += raw.substr(i)
				i = n
				break
			buf = _flush(buf, out)
			_emit_group(raw.substr(i + 2, end - i - 2), is_raw_book, out)
			i = end + 2
			continue

		# --- 分隔
		if ch == "-" and raw.substr(i, 3) == "---":
			buf = _flush(buf, out)
			out.append({"kind": KIND_SEP})
			i += 3
			# 分隔行独占一行：紧跟的换行由 sep 段本身代表。
			# 不这么做的话「---」这一行会被算成两行（sep 一行 + 空行一行），纸上多一条空白。
			if i < n and raw[i] == "\n":
				i += 1
				at_line_start = true
			continue

		buf += ch
		i += 1

	_flush(buf, out)
	return out


## 把一段 `{{…}}` 的内容摊成段。parts 不足两段 ⇒ 当普通文字（容错）。
static func _emit_group(inner: String, is_raw_book: bool, out: Array) -> void:
	var parts := inner.split("|")
	if parts.size() < 2:
		out.append({"kind": KIND_TEXT, "text": inner})
		return

	if not is_raw_book:
		# 假本：只留最后一段，不加任何标记
		out.append({"kind": KIND_TEXT, "text": parts[parts.size() - 1]})
		return

	# 真本：旧字划掉
	out.append({"kind": KIND_STRIKE, "text": parts[0]})
	if parts.size() == 2:
		out.append({"kind": KIND_RED, "text": parts[1]})
	else:
		# 超过两段直接连排会读成乱码（docs/diary-markup.md 陷阱②）⇒ 首 → … → 尾
		out.append({"kind": KIND_ELLIPSIS, "text": "…"})
		out.append({"kind": KIND_RED, "text": parts[parts.size() - 1]})


## 攒着的普通文字落成一段。返回空串（方便写成 `buf = _flush(buf, out)`）。
static func _flush(buf: String, out: Array) -> String:
	if buf != "":
		out.append({"kind": KIND_TEXT, "text": buf})
	return ""


# ---- 给测试与调用方的小工具（纯函数，不碰节点） --------------------------

## 这些段里有没有某个 kind。
static func has_kind(segments: Array, kind: String) -> bool:
	for seg in segments:
		if String(seg.get("kind", "")) == kind:
			return true
	return false


## 把段拼回成一整串纯文本（sep 记作一个换行；indent 不吃字符）。
## 用途：断言「假本只剩 B」这类内容级别的结论。
static func plain_text(segments: Array) -> String:
	var s := ""
	for seg in segments:
		var kind := String(seg.get("kind", KIND_TEXT))
		if kind == KIND_SEP:
			s += "\n"
		else:
			s += String(seg.get("text", ""))
	return s


## 所有段里出现过的 kind（去重，按首次出现顺序）。调试 / 断言用。
static func kinds(segments: Array) -> Array:
	var seen: Array = []
	for seg in segments:
		var kind := String(seg.get("kind", ""))
		if not seen.has(kind):
			seen.append(kind)
	return seen