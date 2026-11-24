extends Control

## 证物档案界面（逆转裁判式「证物清单」）。
##
## 挂法：main.gd 动态建一个本节点挂在 Main（根 Control）下 —— 与 HUD 同层，
## 且建在 HUD 之后 → 画在 HUD 上面。开档期间主循环暂停（main.gd 那边直接 return）。
##
## 布局单位跟 hud.gd 一致：下面数字都是「640×360 时代的设计值」，写的时候乘 UI。
## UI = 2.0（视口 1280×720）。
##
## —— 模型（v2）：一件物件 = 一张卡，卡内按年代追加观察记录 ——
##   列表页：一行 = 一张卡（卡片名 + 右侧年份跨度 + 首条观察摘要）
##   详情页：卡片名 + 「已记录 N 次观察」+ 按年代升序列出每条观察（可滚动）
##
## 状态：
##   open      档案是否打开（决定画不画面板）
##   detail    详情态（列表态 ↔ 详情态）
##   selected  列表选中项下标（卡的下标）
##   scroll    详情页滚动行数
##   toast_*   「已收集」提示（关档时也能看见）
##   new_count 自上次关档以来的新增量（新增卡数 + 新增观察数，见 EvidenceStore.pending_new）
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
## footer 要两行（操作提示 + 「世界已暂停」），所以比原来高。
const FOOTER_H := 26.0

## 详情页：年份列宽（设计单位）。来源标签跟在年份右边，观察文案再往右缩进。
const YEAR_COL := 24.0

## footer 第二行：开档时世界是停的，这句话要说清楚。
const FOOTER_PAUSED := "世界已暂停 · 按 I 或 Esc 关闭档案"

var font: Font = ThemeDB.fallback_font

var open := false
var detail := false
var selected := 0
var scroll := 0
var toast_t := 0.0
var toast_text := ""
## 自上次关档以来的新增量 = 新增卡数 + 新增观察数（口径见 EvidenceStore.pending_new）。
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
	_sync_new_count()
	queue_redraw()


func close_archive() -> void:
	open = false
	detail = false
	scroll = 0
	new_count = 0     # 这批「新」提示看过了，下次开档不再标
	# 「新」标记归零：同一批新增只在下一轮开档前显示一次。
	EvidenceStore.clear_new_flags()
	queue_redraw()


func toggle() -> void:
	if open:
		close_archive()
	else:
		open_archive()


## 收集成功时叫一次：弹一行「已收集：xxx」提示。
## is_new_card = true 表示这是**新建一张卡**；false 表示已有卡追加了新年代的观察。
func flash_collected(name: String, is_new_card: bool = true) -> void:
	toast_text = ("新证物：%s" if is_new_card else "新观察：%s") % name
	toast_t = 2.4
	_sync_new_count()
	queue_redraw()


## 从数据层把新增计数同步过来（新增卡数 + 新增观察数）。
func _sync_new_count() -> void:
	var p := EvidenceStore.pending_new()
	new_count = int(p.get("cards", 0)) + int(p.get("observations", 0))


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

	_draw_title(p, entries)

	if detail:
		_draw_detail(p, entries)
	else:
		_draw_list(p, entries)

	_draw_footer(p)


## 标题栏右侧：卡数 + 观察条数（两个数字都在）。
func _draw_title(p: Rect2, entries: Array) -> void:
	var bar_h := TITLE_H * UI
	draw_rect(Rect2(p.position, Vector2(p.size.x, bar_h)), Color(0.14, 0.12, 0.10, 0.95), true)
	draw_line(p.position + Vector2(0, bar_h), p.position + Vector2(p.size.x, bar_h),
		Color(0.55, 0.47, 0.36, 0.85), 1.0 * UI)

	# ⚠️ ty 已经是绝对 y（相对整屏），不要再加 p.position.y —— 加两次字会被裁到栏外。
	var ty := p.position.y + 15.0 * UI
	draw_string(font, Vector2(p.position.x + 10.0 * UI, ty), "证物档案 · 证据清单",
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.95, 0.82, 0.60))

	var obs_total := 0
	for e in entries:
		obs_total += (e as Dictionary).get("observations", []).size()
	var cnt := "已收集 %d 件 · %d 条观察" % [entries.size(), obs_total]
	var cw: float = font.get_string_size(cnt, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x
	draw_string(font, Vector2(p.position.x + p.size.x - cw - 10.0 * UI, ty), cnt,
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.72, 0.70, 0.63))


## 列表页：一行 = 一张卡（卡片名 + 右侧年份跨度 + 首条观察摘要）。
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
		var key := String(e.get("key", ""))

		var nx := x + 8.0 * UI
		var ny := cy + 13.0 * UI
		draw_string(font, Vector2(nx, ny), name,
			HORIZONTAL_ALIGNMENT_LEFT, -1, FONT,
			Color(0.96, 0.86, 0.64) if is_sel else Color(0.86, 0.83, 0.75))

		# 新证据角标（新建卡 或 追加了新年代的观察）
		if EvidenceStore.is_new_key(key):
			var nw: float = font.get_string_size("新", HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x
			draw_string(font, Vector2(nx + font.get_string_size(
				name, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x + 5.0 * UI, ny), "新",
				HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.55, 0.85, 0.50))

		# 年份跨度（右对齐）：首条观察年份 · 末条观察年份
		var span := _year_span(e)
		if span != "":
			var sw: float = font.get_string_size(span, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x
			draw_string(font, Vector2(x + w - sw - 8.0 * UI, ny), span,
				HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.60, 0.58, 0.52))

		# 摘要：首条观察的文本（不是拼接）
		var summary := _clip(_first_observation_text(e), w - 16.0 * UI)
		draw_string(font, Vector2(x + 8.0 * UI, cy + 25.0 * UI), summary,
			HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.66, 0.64, 0.59))


## 详情页：卡片名 + 「已记录 N 次观察」+ 按年代升序的观察列表（可滚动）。
func _draw_detail(p: Rect2, entries: Array) -> void:
	if entries.is_empty():
		return
	var idx := clampi(selected, 0, entries.size() - 1)
	var e: Dictionary = entries[idx]

	var x := p.position.x + 16.0 * UI
	var y := p.position.y + TITLE_H * UI + 10.0 * UI

	draw_string(font, Vector2(x, y + 12.0 * UI), String(e.get("name", "")),
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_BIG, Color(0.96, 0.86, 0.64))

	var obs := sorted_observations(e)
	draw_string(font, Vector2(x, y + 28.0 * UI), "已记录 %d 次观察" % obs.size(),
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.64, 0.62, 0.56))

	draw_line(Vector2(x, y + 34.0 * UI), Vector2(p.position.x + p.size.x - 16.0 * UI, y + 34.0 * UI),
		Color(0.42, 0.37, 0.30, 0.80), 1.0 * UI)

	var lines := detail_lines(e, p.size.x - 16.0 * UI - YEAR_COL * UI)
	var line_h := 15.0 * UI
	var top := y + 52.0 * UI
	var bottom := p.position.y + p.size.y - FOOTER_H * UI - 6.0 * UI
	var max_lines := int(maxf(1.0, floor((bottom - top) / line_h)))

	scroll = clampi(scroll, 0, maxi(0, lines.size() - max_lines))

	var shown := 0
	for i in range(scroll, lines.size()):
		if shown >= max_lines:
			break
		var ln: Dictionary = lines[i]
		var lx := x + float(int(ln.get("col", 0))) * YEAR_COL * UI
		var col := Color(0.86, 0.84, 0.78)
		match String(ln.get("style", "body")):
			"year":
				col = Color(0.90, 0.76, 0.44)
			"source":
				col = Color(0.60, 0.58, 0.52)
		draw_string(font, Vector2(lx, top + float(shown) * line_h + line_h * 0.8),
			String(ln.get("text", "")), HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, col)
		shown += 1

	# 文本没到底时给个滚动提示
	if lines.size() > max_lines:
		var tip := "↑↓ 滚动"
		var tw: float = font.get_string_size(tip, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x
		draw_string(font, Vector2(p.position.x + p.size.x - tw - 16.0 * UI,
			p.position.y + p.size.y - FOOTER_H * UI + 2.0 * UI), tip,
			HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.52, 0.50, 0.46))


## footer 两行：操作提示 + 「世界已暂停」。
func _draw_footer(p: Rect2) -> void:
	var txt := ""
	if detail:
		txt = "↑↓ 滚动    Enter/ESC 回列表    I 关闭"
	else:
		txt = "↑↓ 选择    Enter 详情    I/ESC 关闭"
	var w: float = font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x
	draw_string(font, Vector2(p.position.x + (p.size.x - w) * 0.5,
		p.position.y + p.size.y - 14.0 * UI), txt,
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.60, 0.58, 0.52))

	var paused := FOOTER_PAUSED
	var pw: float = font.get_string_size(paused, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x
	draw_string(font, Vector2(p.position.x + (p.size.x - pw) * 0.5,
		p.position.y + p.size.y - 3.0 * UI), paused,
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.72, 0.60, 0.36))


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


## 标题栏右侧计数文案：「已收集 N 件 · M 条观察」（两个数字都在）。
func title_summary() -> String:
	var entries := _entries()
	var obs_total := 0
	for e in entries:
		obs_total += (e as Dictionary).get("observations", []).size()
	return "已收集 %d 件 · %d 条观察" % [entries.size(), obs_total]


## 观察按年代升序；同年代多条按收集顺序（order 字段）。
func sorted_observations(card: Dictionary) -> Array:
	var obs: Array = (card.get("observations", []) as Array).duplicate(true)
	obs.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		var ya := int(a.get("year", 0))
		var yb := int(b.get("year", 0))
		if ya != yb:
			return ya < yb
		return int(a.get("order", 0)) < int(b.get("order", 0)))
	return obs


## 卡片的年份跨度：首末观察年份（只有一条就一个年份）。
func _year_span(card: Dictionary) -> String:
	var obs := sorted_observations(card)
	if obs.is_empty():
		return ""
	var y0 := int((obs[0] as Dictionary).get("year", 0))
	var y1 := int((obs[obs.size() - 1] as Dictionary).get("year", 0))
	if y0 <= 0 and y1 <= 0:
		return ""
	if y0 == y1:
		return str(y0)
	return "%d · %d" % [y0, y1]


## 首条观察的文本（列表页摘要用）。
func _first_observation_text(card: Dictionary) -> String:
	var obs: Array = card.get("observations", [])
	if obs.is_empty():
		return ""
	return String((obs[0] as Dictionary).get("text", ""))


## 详情页正文行（可滚动的行表）。每年一条观察：
## 「年份 | 来源标签」一行 + 文案若干行 + 空行分隔。
## 公开（测试要断言「按年代升序」）。
func detail_lines(card: Dictionary, text_w: float) -> Array:
	var out: Array = []
	for o in sorted_observations(card):
		var od: Dictionary = o
		var year := int(od.get("year", 0))
		out.append({
			"text": (str(year) if year > 0 else "年份不详"),
			"style": "year", "col": 0,
		})
		out.append({
			"text": String(od.get("source", "")),
			"style": "source", "col": 1,
		})
		var t := String(od.get("text", ""))
		if t != "":
			for ln in _wrap(t, text_w):
				out.append({"text": String(ln), "style": "body", "col": 1})
		out.append({"text": "", "style": "gap", "col": 0})
	return out


func _max_scroll() -> int:
	# 详情页能滚的最大行数 = 正文折行数 - 一屏能放下的行数。
	# ⚠️ 这里必须真算，别写死 0 —— 写死的话长描述根本滚不动（踩过）。
	var entries := _entries()
	if entries.is_empty():
		return 0
	var idx := clampi(selected, 0, entries.size() - 1)
	var e: Dictionary = entries[idx]
	var p := _panel_rect()
	var lines := detail_lines(e, p.size.x - 16.0 * UI - YEAR_COL * UI)
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
