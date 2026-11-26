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
## 结构上把「排版」和「绘制」拆开（`compute_layout()` 只吐指令，不碰 draw_*）：
##   ① headless 里也能拿到行位/高度，可以进回归断言（画不出图不代表量不出字）；
##   ② 分页能按「行」精确切，不用担心把一行字劈成两半。
##
## 翻页（2026-11-26 加）：纸面不再靠滚动看全文，改成「一页一页翻」，页脚左右各一个箭头
## （仿《Minecraft》的书）。分页单位是**行**：一行字绝不会跨两页。装得下就只有一页，
## 这时两个箭头是灰的（照 Minecraft 的做法，按钮留着但不响应）。
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

## —— 页脚（两个翻页箭头 + 页码，仿 Minecraft 的书）——
const FOOTER_H := 30.0          # 页脚占高（正文不许画进来）
const ARROW_W := 30.0           # 箭头命中区宽
const ARROW_H := 22.0           # 箭头命中区高
const PAGE_FS := 12             # 页码字号

## —— 配色 ——
const INK := Color("#3a2f22")          # 墨色
const OLD_COL := Color("#8f8474")      # 被划掉的字（灰，退到背景）
const NEW_COL := Color("#8b2f2f")      # 改正的字（暗红）
const SEP_COL := Color("#b0a080")      # 分隔点
const TITLE_COL := Color("#6a5a48")    # 小标题
const BORDER_COL := Color("#c0ae88")   # 纸边
const PAPER_FAKE := Color("#e8ddc0")   # 假本纸色
const PAPER_RAW := Color("#e2d6b4")    # 真本纸色（稍深，旧）

## 页脚箭头 / 页码的墨色（灰掉时就是同一个色降透明度）
const ARROW_COL := Color("#6a5a48")
const ARROW_DIM := Color("#6a5a48", 0.22)
const PAGE_COL := Color("#6a5a48", 0.75)

## 分隔行（照 _mdtest/render3.gd:27）
const SEP_TEXT := "· · · · · · · ·"

var font: Font = ThemeDB.fallback_font

var title := ""
var is_raw_book := false
var segments: Array = []

## 正文的实际高度（`compute_layout()` 量出来；假本 520 / 真本 494）
var content_h := 0.0
var _body_top := 0.0

var _sb_fake: StyleBoxFlat
var _sb_raw: StyleBoxFlat

## 分页结果：[{"from": 起始行号, "to": 结束行号（不含）}]，行号从 0 起
var _pages: Array = []
var _page := 0
var _line_count := 0
var _stale := true


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	# 分页之后不该有任何字落到纸外面，但窗口被压得极小时仍留一道保险
	clip_contents = true
	_sb_fake = _make_style(PAPER_FAKE)
	_sb_raw = _make_style(PAPER_RAW)
	resized.connect(_on_resized)


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
	_page = 0
	_stale = true
	queue_redraw()


## 正文区起点（标题下方）。排版与绘制共用，测试也拿它算预期值。
func body_top() -> float:
	return PAD + font.get_height(TITLE_FS) + TITLE_GAP


## 可用文字宽度。
func text_width() -> float:
	return maxf(64.0, size.x - PAD * 2.0)


## 一页能放多少行（页脚与标题都扣掉）。
func per_page_lines() -> int:
	var h: float = size.y - PAD - FOOTER_H - body_top()
	return maxi(1, int(floor(maxf(0.0, h) / LINE_H)))


# ---- 分页 ----------------------------------------------------------------

func _ensure_pages() -> void:
	if not _stale:
		return
	_stale = false
	_pages.clear()
	_line_count = 0
	if font == null:
		_pages.append({"from": 0, "to": 0})
		return

	# 用 top=0 排一遍：行长一样，只为了拿总行数（op 里的 "l" 是行号）
	var res := compute_layout(0.0, text_width())
	for op in (res.ops as Array):
		var l := int((op as Dictionary).get("l", 0)) + 1
		if l > _line_count:
			_line_count = l

	var cap := per_page_lines()
	var i := 0
	while i < _line_count:
		var to := mini(_line_count, i + cap)
		_pages.append({"from": i, "to": to})
		i = to
	if _pages.is_empty():
		_pages.append({"from": 0, "to": 0})
	_page = clampi(_page, 0, _pages.size() - 1)


func page_count() -> int:
	_ensure_pages()
	return _pages.size()


func page_index() -> int:
	_ensure_pages()
	return clampi(_page, 0, _pages.size() - 1)


## 总行数（含空行与分隔行）—— 测试用它核对分页有没有漏行。
func line_count() -> int:
	_ensure_pages()
	return _line_count


func can_prev() -> bool:
	return page_index() > 0


func can_next() -> bool:
	return page_index() < page_count() - 1


func goto_page(i: int) -> void:
	_ensure_pages()
	var n := clampi(i, 0, _pages.size() - 1)
	if n == _page:
		return
	_page = n
	queue_redraw()


func next_page() -> void:
	if can_next():
		goto_page(page_index() + 1)


func prev_page() -> void:
	if can_prev():
		goto_page(page_index() - 1)


## 页码文字（页脚正中）：装得下就只有「1 / 1」。
func page_text() -> String:
	return "%d / %d" % [page_index() + 1, maxi(1, page_count())]


# ---- 页脚箭头（几何 + 命中）---------------------------------------------

## side: -1 前一页（左）、+1 后一页（右）。返回的是纸内局部坐标。
func arrow_rect(side: int) -> Rect2:
	var y: float = size.y - FOOTER_H + (FOOTER_H - ARROW_H) * 0.5
	var x: float = PAD if side < 0 else size.x - PAD - ARROW_W
	return Rect2(Vector2(x, y), Vector2(ARROW_W, ARROW_H))


## 点在哪个箭头上：返回 -1 / +1 / 0（0 = 没点到，或者那一页已经到头了）。
## local 是相对本纸的坐标。命中区比画出来的三角大一圈，好按。
func hit_arrow(local: Vector2) -> int:
	if page_count() <= 1:
		return 0
	if can_prev() and arrow_rect(-1).grow(6.0).has_point(local):
		return -1
	if can_next() and arrow_rect(1).grow(6.0).has_point(local):
		return 1
	return 0


func _on_resized() -> void:
	_stale = true
	_page = 0
	queue_redraw()


# ---- 排版：只吐绘制指令，不碰 draw_*（headless 可测）---------------------

## 返回 {"ops": [...], "height": 正文高度}。
## ops 四种（每条都带 "l": 行号，分页靠它切，不必重新算）：
##   {"t": "ch",  "x":, "y":(基线), "k":段 kind, "c": 单字, "l": 行号}
##   {"t": "ln",  "x0":, "x1":, "y":}      删除线
##   {"t": "sep", "x":, "y":(基线)}       分隔点
## top 是正文第一行的「行首 y」。
func compute_layout(top: float, width: float) -> Dictionary:
	var ops: Array = []
	if font == null:
		return {"ops": ops, "height": 0.0}

	var asc: float = font.get_ascent(FS)
	var right := PAD + width
	var st := {
		"x": PAD, "y": top, "indent": 0.0, "has": false, "from": -1.0, "line": 0,
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
				ops.append({"t": "sep", "x": sx, "y": float(st.y) + asc, "l": int(st.line)})
				st.y = float(st.y) + LINE_H
				st.line = int(st.line) + 1
				st.indent = 0.0
				st.x = PAD
				st.has = false
			_:
				_emit_run(String(seg.get("text", "")), kind, st, right, asc, ops)

	_end_strike(st, ops)
	# 最后一行是空的（原稿以换行结尾）就别算进高度，否则底部多出一行空白
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
		ops.append({"t": "ch", "x": float(st.x), "y": float(st.y) + asc,
			"k": kind, "c": ch, "l": int(st.line)})
		st.x = float(st.x) + cw
		st.has = true

	_end_strike(st, ops)


## 换行：把没闭合的删除线画完，光标移到下一行行首。
## ⚠️ 缩进只管它所在的那一行，换行必须把它清掉（否则制表符之后整篇都会缩进去）。
func _break_line(st: Dictionary, ops: Array) -> void:
	_end_strike(st, ops)
	st.y = float(st.y) + LINE_H
	st.line = int(st.line) + 1
	st.indent = 0.0
	st.x = PAD
	st.has = false


## 本行删除线：从起笔位置画到落笔位置，粗细 2px，位置 y + ascent - fs*0.30。
func _end_strike(st: Dictionary, ops: Array) -> void:
	var from := float(st.from)
	if from < 0.0:
		return
	var ly: float = float(st.y) + font.get_ascent(FS) - FS * STRIKE_DY
	ops.append({"t": "ln", "x0": from, "x1": float(st.x), "y": ly, "l": int(st.line)})
	st.from = -1.0


# ---- 绘制：把指令画出来 ------------------------------------------------

func _draw() -> void:
	draw_style_box(_sb_raw if is_raw_book else _sb_fake, Rect2(Vector2.ZERO, size))

	# 小标题固定，不跟着翻页
	if title != "":
		draw_string(font, Vector2(PAD, PAD + font.get_ascent(TITLE_FS)), title,
			HORIZONTAL_ALIGNMENT_LEFT, -1, TITLE_FS, TITLE_COL)
	_body_top = body_top()

	_ensure_pages()
	var from := 0
	var to := 0
	if not _pages.is_empty():
		var pg: Dictionary = _pages[clampi(_page, 0, _pages.size() - 1)]
		from = int(pg.get("from", 0))
		to = int(pg.get("to", 0))

	# 当前页从第 from 行开始：整块上移到纸顶（行的 y 减去 from 行的偏移）
	var shift := -float(from) * LINE_H
	var res := compute_layout(_body_top + shift, text_width())
	content_h = float(res.height)

	for op in (res.ops as Array):
		var d: Dictionary = op
		var l := int(d.get("l", 0))
		if l < from or l >= to:
			continue
		match String(d.get("t", "")):
			"ch":
				var col := _col_of(String(d.get("k", "")))
				var px := float(d.get("x", 0.0))
				var py := float(d.get("y", 0.0))
				if _visible(py):
					draw_string(font, Vector2(px, py), String(d.get("c", "")),
						HORIZONTAL_ALIGNMENT_LEFT, -1, FS, col)
					if String(d.get("k", "")) == DiaryMarkup.KIND_RED:
						# 「加粗」：同字再画一遍、右移 0.6px（默认字体没有 bold 变体，也不许引字体文件）
						draw_string(font, Vector2(px + 0.6, py), String(d.get("c", "")),
							HORIZONTAL_ALIGNMENT_LEFT, -1, FS, col)
			"ln":
				if _visible(float(d.get("y", 0.0))):
					draw_line(Vector2(float(d.get("x0", 0.0)), float(d.get("y", 0.0))),
						Vector2(float(d.get("x1", 0.0)), float(d.get("y", 0.0))),
						OLD_COL, STRIKE_W, true)
			"sep":
				if _visible(float(d.get("y", 0.0))):
					draw_string(font, Vector2(float(d.get("x", 0.0)), float(d.get("y", 0.0))),
						SEP_TEXT, HORIZONTAL_ALIGNMENT_LEFT, -1, FS, SEP_COL)

	_draw_footer()


## 页脚：左箭头 —— 页码 —— 右箭头（仿 Minecraft 的书）。
## 只有一页时箭头灰掉（还是画出来，玩家知道"这里是能翻的"）。
func _draw_footer() -> void:
	_draw_arrow(-1, can_prev())
	_draw_arrow(1, can_next())

	var txt := page_text()
	var w := font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, PAGE_FS).x
	var r := arrow_rect(1)
	var cy := r.position.y + r.size.y * 0.5
	draw_string(font, Vector2((size.x - w) * 0.5, cy + font.get_ascent(PAGE_FS) * 0.5 - 1.0),
		txt, HORIZONTAL_ALIGNMENT_LEFT, -1, PAGE_FS, PAGE_COL)


## 三角箭头：朝 side 方向。用多边形画，不依赖字体里有没有 ◀ ▶ 字形。
func _draw_arrow(side: int, enabled: bool) -> void:
	var r := arrow_rect(side)
	var pad := 7.0
	var x0: float = r.position.x + pad
	var x1: float = r.position.x + r.size.x - pad
	var y0: float = r.position.y + 3.0
	var y1: float = r.position.y + r.size.y - 3.0
	var ym: float = (y0 + y1) * 0.5
	var pts := PackedVector2Array()
	if side < 0:
		pts.append(Vector2(x1, y0))
		pts.append(Vector2(x1, y1))
		pts.append(Vector2(x0, ym))
	else:
		pts.append(Vector2(x0, y0))
		pts.append(Vector2(x0, y1))
		pts.append(Vector2(x1, ym))
	draw_colored_polygon(pts, ARROW_COL if enabled else ARROW_DIM)


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
	return baseline > _body_top - LINE_H and baseline < size.y - FOOTER_H + LINE_H