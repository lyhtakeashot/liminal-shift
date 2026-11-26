extends Control

## L16 · 单页纸（自绘 Control）。假本 / 真本共用这一个类，只换纸色与段数据。
##
## 🔴 删除线**必须自绘**：富文本控件自带的下划线标签（方括号里一个 s）线宽由字体决定，
##    实测太细看不清（`docs/diary-markup.md:52-63`）。所以本文件不用任何富文本控件，
##    一个字都用 draw 画。
##
## 排版参数全部照 `docs/diary-markup.md:36-50` 的实测定稿值：
##   字号 17 / 行高 26 / 被划掉的字 #8f8474 / 改正的字 #8b2f2f / 墨色 #3a2f22
##   删除线 2px，位置 `y + ascent - font_size * 0.30`
##
## 结构上把「排版」和「绘制」拆开（`layout()` 只吐指令，不碰 draw_*）：
##   ① headless 里也能拿到行位/高度，可以进回归断言（画不出图不代表量不出字）；
##   ② 正文超高时 diary_view 能拿到准确的滚动量。
##
## 用法（位置/尺寸由 diary_view.gd 手动给，不靠容器）：
##   var page := DiaryPage.new()
##   page.set_page("真本 · 原稿", true, DiaryMarkup.parse(raw, true))
##
## ⚠️ 动态 add_child 出来的节点必须用 set_anchors_and_OFFSETS_preset：只设 anchors 的话
##    offsets 还是 0，size 会是 (0,0)（`scripts/evidence_archive.gd:59-61` 踩过）。

const DiaryMarkup = preload("res://scripts/diary_markup.gd")

## —— 实测定稿参数（docs/diary-markup.md:36-50）——
const FS := 17                  # 正文字号
const LINE_H := 26.0            # 行高
const TITLE_FS := 13            # 小标题字号（照 _mdtest/render3.gd:113-117）
const STRIKE_W := 2.0           # 删除线粗细
const STRIKE_DY := 0.30         # 删除线位置：y + ascent - FS * 0.30
const INDENT_W := 34.0          # 行首制表符的缩进量（≈ 两个汉字宽）

const PAD := 18.0               # 纸内边距（照 _mdtest/render3.gd:106 的 content margin）
const TITLE_GAP := 8.0

## —— 配色 ——
const INK := Color("#3a2f22")          # 墨色
const OLD_COL := Color("#8f8474")      # 被划掉的字（灰，退到背景）
const NEW_COL := Color("#8b2f2f")      # 改正的字（暗红）
const SEP_COL := Color("#b0a080")      # 分隔点
const TITLE_COL := Color("#6a5a48")    # 小标题
const BORDER_COL := Color("#c0ae88")   # 纸边
const PAPER_FAKE := Color("#e8ddc0")   # 假本纸色
const PAPER_RAW := Color("#e2d6b4")    # 真本纸色（稍深，旧）

## 分隔行（照 _mdtest/render3.gd:27）
const SEP_TEXT := "· · · · · · · ·"

var font: Font = ThemeDB.fallback_font

var title := ""
var is_raw_book := false
var segments: Array = []
var scroll := 0.0

## 正文的实际高度（`layout()` 量出来；diary_view 用它算最大滚动量）
var content_h := 0.0
var _body_top := 0.0

var _sb_fake: StyleBoxFlat
var _sb_raw: StyleBoxFlat


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	# 正文超高时靠滚动看，纸面以外不许漏字
	clip_contents = true
	_sb_fake = _make_style(PAPER_FAKE)
	_sb_raw = _make_style(PAPER_RAW)


func _make_style(paper: Color) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = paper
	sb.set_corner_radius_all(3)
	sb.set_border_width_all(1)
	sb.border_color = BORDER_COL
	return sb


# ---- 对外接口 ------------------------------------------------------------

## 灌一页：标题 / 是不是真本（决定纸色）/ 段数组（DiaryMarkup.parse 的结果）。
func set_page(p_title: String, p_raw: bool, p_segments: Array) -> void:
	title = p_title
	is_raw_book = p_raw
	segments = p_segments
	scroll = 0.0
	queue_redraw()


func set_scroll(v: float) -> void:
	var nv := clampf(v, 0.0, max_scroll())
	if not is_equal_approx(nv, scroll):
		scroll = nv
		queue_redraw()


func max_scroll() -> float:
	return maxf(0.0, _body_top + content_h - (size.y - PAD))


## 正文区起点（标题下方）。排版与绘制共用，测试也拿它算预期值。
func body_top() -> float:
	return PAD + font.get_height(TITLE_FS) + TITLE_GAP


## 可用文字宽度。
func text_width() -> float:
	return maxf(64.0, size.x - PAD * 2.0)


# ---- 排版：只吐绘制指令，不碰 draw_*（headless 可测）---------------------

## 返回 {"ops": [...], "height": 正文高度}。
## ops 三种：
##   {"t": "ch",  "x":, "y":(基线), "k":段 kind, "c": 单字}
##   {"t": "ln",  "x0":, "x1":, "y":}      删除线
##   {"t": "sep", "x":, "y":(基线)}       分隔点
## top 是正文第一行的「行首 y」（含滚动偏移由调用方扣掉）。
func compute_layout(top: float, width: float) -> Dictionary:
	var ops: Array = []
	if font == null:
		return {"ops": ops, "height": 0.0}

	var asc: float = font.get_ascent(FS)
	var right := PAD + width
	var st := {
		"x": PAD, "y": top, "indent": 0.0, "has": false, "from": -1.0,
	}

	for seg in segments:
		var kind := String(seg.get("kind", DiaryMarkup.KIND_TEXT))
		match kind:
			DiaryMarkup.KIND_INDENT:
				st.indent = INDENT_W
				if not bool(st.has):
					st.x = PAD + INDENT_W
			DiaryMarkup.KIND_SEP:
				if bool(st.has):
					_break_line(st, ops)
				var w := font.get_string_size(SEP_TEXT, HORIZONTAL_ALIGNMENT_LEFT, -1, FS).x
				var sx := PAD + maxf(0.0, (width - w) * 0.5)
				ops.append({"t": "sep", "x": sx, "y": float(st.y) + asc})
				st.y = float(st.y) + LINE_H
				st.indent = 0.0
				st.x = PAD
				st.has = false
			_:
				_emit_run(String(seg.get("text", "")), kind, st, right, asc, ops)

	_end_strike(st, ops)
	# 最后一行是空的（原稿以换行结尾）就别算进高度，否则底部多出可滚的一行空白
	var h: float = float(st.y) + LINE_H - top
	if not bool(st.has):
		h = float(st.y) - top
	return {"ops": ops, "height": maxf(0.0, h)}


func _emit_run(text: String, kind: String, st: Dictionary, right: float,
		asc: float, ops: Array) -> void:
	# 要不要压删除线：只有 strike 段要（…折记号跟旧字同色但不划线）
	var press := kind == DiaryMarkup.KIND_STRIKE

	for i in text.length():
		var ch := text[i]
		if ch == "\n":
			_break_line(st, ops)
			continue

		var cw: float = font.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1, FS).x
		# 中文没有空格，按累积宽度硬折行（draw_string 自己不会换，只会裁掉）
		if bool(st.has) and float(st.x) + cw > right:
			_break_line(st, ops)

		if press and float(st.from) < 0.0:
			st.from = float(st.x)
		ops.append({"t": "ch", "x": float(st.x), "y": float(st.y) + asc, "k": kind, "c": ch})
		st.x = float(st.x) + cw
		st.has = true

	_end_strike(st, ops)


## 换行：把没闭合的删除线画完，光标移到下一行行首。
## ⚠️ 缩进只管它所在的那一行，换行必须把它清掉（否则制表符之后整篇都会缩进去）。
func _break_line(st: Dictionary, ops: Array) -> void:
	_end_strike(st, ops)
	st.y = float(st.y) + LINE_H
	st.indent = 0.0
	st.x = PAD
	st.has = false


## 本行删除线：从起笔位置画到落笔位置，粗细 2px，位置 y + ascent - fs*0.30。
func _end_strike(st: Dictionary, ops: Array) -> void:
	var from := float(st.from)
	if from < 0.0:
		return
	var ly: float = float(st.y) + font.get_ascent(FS) - FS * STRIKE_DY
	ops.append({"t": "ln", "x0": from, "x1": float(st.x), "y": ly})
	st.from = -1.0


# ---- 绘制：把指令画出来 ------------------------------------------------

func _draw() -> void:
	draw_style_box(_sb_raw if is_raw_book else _sb_fake, Rect2(Vector2.ZERO, size))

	# 小标题固定，不跟着正文滚
	if title != "":
		draw_string(font, Vector2(PAD, PAD + font.get_ascent(TITLE_FS)), title,
			HORIZONTAL_ALIGNMENT_LEFT, -1, TITLE_FS, TITLE_COL)
	_body_top = body_top()

	var res := compute_layout(_body_top - scroll, text_width())
	content_h = float(res.height)

	for op in res.ops:
		match String(op.t):
			"ch":
				var col := _col_of(String(op.k))
				var px := float(op.x)
				var py := float(op.y)
				if _visible(py):
					draw_string(font, Vector2(px, py), String(op.c),
						HORIZONTAL_ALIGNMENT_LEFT, -1, FS, col)
					if String(op.k) == DiaryMarkup.KIND_RED:
						# 「加粗」：同字再画一遍、右移 0.6px（默认字体没有 bold 变体，也不许引字体文件）
						draw_string(font, Vector2(px + 0.6, py), String(op.c),
							HORIZONTAL_ALIGNMENT_LEFT, -1, FS, col)
			"ln":
				if _visible(float(op.y)):
					draw_line(Vector2(float(op.x0), float(op.y)),
						Vector2(float(op.x1), float(op.y)), OLD_COL, STRIKE_W, true)
			"sep":
				if _visible(float(op.y)):
					draw_string(font, Vector2(float(op.x), float(op.y)), SEP_TEXT,
						HORIZONTAL_ALIGNMENT_LEFT, -1, FS, SEP_COL)


func _col_of(kind: String) -> Color:
	match kind:
		DiaryMarkup.KIND_STRIKE, DiaryMarkup.KIND_ELLIPSIS:
			return OLD_COL
		DiaryMarkup.KIND_RED:
			return NEW_COL
		_:
			return INK


## 上下越界的行不画（clip_contents 之外再加一道，免得依赖裁剪实现）。
func _visible(baseline: float) -> bool:
	return baseline > _body_top - LINE_H and baseline < size.y + LINE_H