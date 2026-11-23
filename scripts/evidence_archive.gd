extends Control

## 证物档案界面（逆转裁判式「证物清单」）。
##
## 挂法：main.gd 动态建一个本节点挂在 Main（根 Control）下 —— 与 HUD 同层，
## 且建在 HUD 之后 → 画在 HUD 上面。开档期间主循环暂停（main.gd 那边直接 return）。
##
## 布局单位跟 hud.gd 一致：下面数字都是「640×360 时代的设计值」，写的时候乘 UI。
## UI = 2.0（视口 1280×720）。
##
## 状态：
##   open      档案是否打开（决定画不画面板）
##   detail    详情态（列表态 ↔ 详情态）
##   selected  列表选中项下标
##   scroll    详情页滚动行数
##   toast_*   「已收集」提示（关档时也能看见）
##   new_count 自上次关档以来新收集的条数（列表里标「新」）
##
## ⚠️ 本节点常驻 visible：收集提示要在关档时也能画出来。
##    面板本身由 open 决定画不画，不用 visible 切（visible=false 就画不出提示了）。

const EvidenceStore = preload("res://scripts/evidence_store.gd")

const UI := 2.0
const FONT := int(10 * UI)
const FONT_BIG := int(13 * UI)

## 面板位置（设计坐标 640×360 时代，写的时候乘 UI）。
## 底部留 60px 给「已收集」提示行 —— 提示走屏幕底部，不能压在列表卡上。
const PANEL := Rect2(40.0, 16.0, 560.0, 310.0)
const TITLE_H := 22.0
const CARD_H := 30.0
const FOOTER_H := 14.0

var font: Font = ThemeDB.fallback_font

var open := false
var detail := false
var selected := 0
var scroll := 0
var toast_t := 0.0
var toast_text := ""
var new_count := 0


func _ready() -> void:
	# ⚠️ 必须用 set_anchors_AND_OFFSETS_preset：只 set_anchors_preset 的话
	# 动态 add_child 出来的节点 offsets 还是 0，size 会是 (0,0)，
	# 全屏压暗矩形和 toast 坐标就全算错了（踩过）。
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


# ---- 对外接口 ------------------------------------------------------------

func is_open() -> bool:
	return open


func open_archive() -> void:
	open = true
	detail = false
	scroll = 0
	selected = 0
	queue_redraw()


func close_archive() -> void:
	open = false
	detail = false
	scroll = 0
	new_count = 0     # 这批「新」提示看过了，下次开档不再标
	queue_redraw()


func toggle() -> void:
	if open:
		close_archive()
	else:
		open_archive()


## 收集成功时叫一次：弹一行「已收集：xxx」提示。
func flash_collected(name: String) -> void:
	toast_text = "已收集：%s" % name
	toast_t = 2.4
	new_count += 1
	queue_redraw()


# ---- 输入 ----------------------------------------------------------------

func _process(delta: float) -> void:
	if toast_t > 0.0:
		toast_t = maxf(0.0, toast_t - delta)
		queue_redraw()
	if not open:
		return
	_handle_keys()
	queue_redraw()


func _handle_keys() -> void:
	var n := _entries().size()
	if detail:
		if Input.is_action_just_pressed("ui_cancel") \
				or Input.is_action_just_pressed("ui_accept"):
			detail = false
			scroll = 0
		elif Input.is_action_just_pressed("ui_down"):
			scroll = mini(scroll + 1, _max_scroll())
		elif Input.is_action_just_pressed("ui_up"):
			scroll = maxi(0, scroll - 1)
		return

	if Input.is_action_just_pressed("ui_cancel"):
		close_archive()
		return
	if n == 0:
		return
	if Input.is_action_just_pressed("ui_accept"):
		detail = true
		scroll = 0
	elif Input.is_action_just_pressed("ui_down"):
		selected = (selected + 1) % n
	elif Input.is_action_just_pressed("ui_up"):
		selected = (selected - 1 + n) % n


# ---- 绘制 ----------------------------------------------------------------

func _draw() -> void:
	if open:
		_draw_panel()
	_draw_toast()


func _draw_panel() -> void:
	var p := _panel_rect()
	var entries := _entries()

	# 背景压暗（游戏画面还在下面）
	draw_rect(Rect2(Vector2.ZERO, size), Color(0.03, 0.03, 0.03, 0.72), true)

	# 面板
	draw_rect(p, Color(0.09, 0.08, 0.07, 0.97), true)
	draw_rect(p, Color(0.58, 0.50, 0.38, 0.90), false, 1.0 * UI)

	_draw_title(p, entries.size())

	if detail:
		_draw_detail(p, entries)
	else:
		_draw_list(p, entries)

	_draw_footer(p)


func _draw_title(p: Rect2, n: int) -> void:
	var bar_h := TITLE_H * UI
	draw_rect(Rect2(p.position, Vector2(p.size.x, bar_h)), Color(0.14, 0.12, 0.10, 0.95), true)
	draw_line(p.position + Vector2(0, bar_h), p.position + Vector2(p.size.x, bar_h),
		Color(0.55, 0.47, 0.36, 0.85), 1.0 * UI)

	# ⚠️ ty 已经是绝对 y（相对整屏），不要再加 p.position.y —— 加两次字会被裁到栏外。
	var ty := p.position.y + 15.0 * UI
	draw_string(font, Vector2(p.position.x + 10.0 * UI, ty), "证物档案 · 证据清单",
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.95, 0.82, 0.60))

	var cnt := "已收集 %d 件" % n
	var cw: float = font.get_string_size(cnt, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x
	draw_string(font, Vector2(p.position.x + p.size.x - cw - 10.0 * UI, ty), cnt,
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.72, 0.70, 0.63))


func _draw_list(p: Rect2, entries: Array) -> void:
	var list_top := p.position.y + TITLE_H * UI + 4.0 * UI
	var list_bottom := p.position.y + p.size.y - FOOTER_H * UI - 4.0 * UI
	var list_h := list_bottom - list_top
	var card_h := CARD_H * UI
	var visible_n := int(maxf(1.0, floor(list_h / card_h)))

	if entries.is_empty():
		var msg := "尚未收集任何证物。"
		var msg2 := "靠近场景里的物件按 E 检视，证物会自动入档。"
		draw_string(font, Vector2(p.position.x + 16.0 * UI, list_top + 24.0 * UI), msg,
			HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.82, 0.80, 0.74))
		draw_string(font, Vector2(p.position.x + 16.0 * UI, list_top + 42.0 * UI), msg2,
			HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.55, 0.53, 0.48))
		return

	# 选中项滚进可视区
	if selected < _list_scroll:
		_list_scroll = selected
	elif selected >= _list_scroll + visible_n:
		_list_scroll = selected - visible_n + 1
	_list_scroll = clampi(_list_scroll, 0, maxi(0, entries.size() - visible_n))

	var first_new := entries.size() - new_count
	var x := p.position.x + 6.0 * UI
	var w := p.size.x - 12.0 * UI

	for i in range(entries.size()):
		if i < _list_scroll or i >= _list_scroll + visible_n:
			continue
		var e: Dictionary = entries[i]
		var cy := list_top + float(i - _list_scroll) * card_h
		var is_sel := i == selected

		draw_rect(Rect2(x, cy, w, card_h - 2.0 * UI),
			Color(0.16, 0.14, 0.12, 0.95) if is_sel else Color(0.11, 0.10, 0.09, 0.80), true)
		if is_sel:
			draw_rect(Rect2(x, cy, w, card_h - 2.0 * UI),
				Color(0.85, 0.68, 0.38, 0.90), false, 1.0 * UI)

		var name := String(e.get("name", ""))
		var source := String(e.get("source", ""))
		var text := String(e.get("text", ""))

		var nx := x + 8.0 * UI
		var ny := cy + 13.0 * UI
		draw_string(font, Vector2(nx, ny), name,
			HORIZONTAL_ALIGNMENT_LEFT, -1, FONT,
			Color(0.96, 0.86, 0.64) if is_sel else Color(0.86, 0.83, 0.75))

		# 新证据角标
		if i >= first_new:
			var nw: float = font.get_string_size("新", HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x
			draw_string(font, Vector2(nx + font.get_string_size(
				name, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x + 5.0 * UI, ny), "新",
				HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.55, 0.85, 0.50))

		# 来源（右对齐）
		if source != "":
			var sw: float = font.get_string_size(source, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x
			draw_string(font, Vector2(x + w - sw - 8.0 * UI, ny), source,
				HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.60, 0.58, 0.52))

		# 描述摘要（超长截断，详情页看全文）
		var summary := _clip(text, w - 16.0 * UI)
		draw_string(font, Vector2(x + 8.0 * UI, cy + 25.0 * UI), summary,
			HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.66, 0.64, 0.59))


func _draw_detail(p: Rect2, entries: Array) -> void:
	if entries.is_empty():
		return
	var idx := clampi(selected, 0, entries.size() - 1)
	var e: Dictionary = entries[idx]

	var x := p.position.x + 16.0 * UI
	var y := p.position.y + TITLE_H * UI + 10.0 * UI

	draw_string(font, Vector2(x, y + 12.0 * UI), String(e.get("name", "")),
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_BIG, Color(0.96, 0.86, 0.64))

	var source := String(e.get("source", ""))
	if source != "":
		draw_string(font, Vector2(x, y + 28.0 * UI), "来源：%s" % source,
			HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.64, 0.62, 0.56))

	draw_line(Vector2(x, y + 34.0 * UI), Vector2(p.position.x + p.size.x - 16.0 * UI, y + 34.0 * UI),
		Color(0.42, 0.37, 0.30, 0.80), 1.0 * UI)

	var body := String(e.get("text", ""))
	var lines := _wrap(body, p.size.x - 32.0 * UI)
	var line_h := 15.0 * UI
	var top := y + 52.0 * UI
	var bottom := p.position.y + p.size.y - FOOTER_H * UI - 6.0 * UI
	var max_lines := int(maxf(1.0, floor((bottom - top) / line_h)))

	scroll = clampi(scroll, 0, maxi(0, lines.size() - max_lines))

	var shown := 0
	for i in range(scroll, lines.size()):
		if shown >= max_lines:
			break
		draw_string(font, Vector2(x, top + float(shown) * line_h + line_h * 0.8),
			String(lines[i]), HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.86, 0.84, 0.78))
		shown += 1

	# 文本没到底时给个滚动提示
	if lines.size() > max_lines:
		var tip := "↑↓ 滚动"
		var tw: float = font.get_string_size(tip, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x
		draw_string(font, Vector2(p.position.x + p.size.x - tw - 16.0 * UI,
			p.position.y + p.size.y - FOOTER_H * UI + 2.0 * UI), tip,
			HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.52, 0.50, 0.46))


func _draw_footer(p: Rect2) -> void:
	var txt := ""
	if detail:
		txt = "↑↓ 滚动    Enter/ESC 回列表    I 关闭"
	else:
		txt = "↑↓ 选择    Enter 详情    I/ESC 关闭"
	var w: float = font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x
	draw_string(font, Vector2(p.position.x + (p.size.x - w) * 0.5,
		p.position.y + p.size.y - 4.0 * UI), txt,
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.60, 0.58, 0.52))


func _draw_toast() -> void:
	if toast_t <= 0.0 or toast_text == "":
		return
	var a: float = clampf(toast_t / 0.6, 0.0, 1.0)
	var w: float = font.get_string_size(toast_text, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x
	# ⚠️ 提示走屏幕底部（任务书：底部闪一行）。
	# HUD 检视卡的底边固定在 size.y - 34*UI = 652，所以提示放在 656 以下，
	# 不会压住检视文字，也不会压住列表卡。
	var box := Rect2((size.x - w) * 0.5 - 8.0 * UI, size.y - 32.0 * UI,
		w + 16.0 * UI, 20.0 * UI)
	draw_rect(box, Color(0.10, 0.09, 0.08, 0.88 * a), true)
	draw_rect(box, Color(0.55, 0.48, 0.36, 0.85 * a), false, 1.0 * UI)
	draw_string(font, Vector2(box.position.x + 8.0 * UI, box.position.y + 14.0 * UI),
		toast_text, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT,
		Color(0.62, 0.90, 0.56, a))


# ---- 小工具 --------------------------------------------------------------

var _list_scroll := 0


## 面板矩形（设计坐标 × UI）。
func _panel_rect() -> Rect2:
	return Rect2(PANEL.position * UI, PANEL.size * UI)


func _entries() -> Array:
	return EvidenceStore.get_entries()


func _max_scroll() -> int:
	# 详情页能滚的最大行数 = 全文折行数 - 一屏能放下的行数。
	# ⚠️ 这里必须真算，别写死 0 —— 写死的话长描述根本滚不动（踩过）。
	var entries := _entries()
	if entries.is_empty():
		return 0
	var idx := clampi(selected, 0, entries.size() - 1)
	var e: Dictionary = entries[idx]
	var p := _panel_rect()
	var lines := _wrap(String(e.get("text", "")), p.size.x - 32.0 * UI)
	var top := p.position.y + TITLE_H * UI + 10.0 * UI + 52.0 * UI
	var bottom := p.position.y + p.size.y - FOOTER_H * UI - 6.0 * UI
	var max_lines := int(maxf(1.0, floor((bottom - top) / (15.0 * UI))))
	return maxi(0, lines.size() - max_lines)


## 按字符宽度截断到一行，超出加「…」。
func _clip(text: String, max_w: float) -> String:
	if max_w <= 0.0:
		return ""
	var cur := ""
	for i in text.length():
		var test := cur + text[i]
		if font.get_string_size(test + "…", HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x > max_w:
			return cur + "…"
		cur = test
	return cur


## 按字符宽度硬折行（中文没空格，累积宽度切最稳）。
func _wrap(text: String, max_w: float) -> Array:
	var out: Array = []
	var cur := ""
	for i in text.length():
		var ch := text[i]
		var test := cur + ch
		if font.get_string_size(test, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x > max_w and cur != "":
			out.append(cur)
			cur = ch
		else:
			cur = test
	if cur != "":
		out.append(cur)
	return out
