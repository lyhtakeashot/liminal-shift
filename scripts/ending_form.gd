extends Control

## 结案归档表界面（story.md §10）：玩家把物证**填成一份卷宗**。
##
## 挂法：main.gd 动态建一个本节点挂在 Main（根 Control）下 —— 与 HUD / 证物档案同层，
## 建在证物档案之后 → 画在它上面。开表期间主循环暂停（main.gd 那边直接 return）。
##
## 布局单位跟 evidence_archive.gd / hud.gd 一致：「640×360 时代的设计值」，写的时候乘 UI。
##
## —— 界面三件套 ——
##   左上 5×2 表格：五行（1926/1951/1976/2001/2026）× 两列（动机形态 / 故意形态）
##      ⚠️ 默认全空、没有占位答案、没有对错提示（任务书 §2.1 / story.md:601-603）。
##   左下 四个单选：1951 案性质 / 最早一具 / 埋尸位置 / 埋葬人数
##   右上 卷宗抬头（卷宗号 / 地点 / 事件 / 归档员）+ 两个出口
##   右下 记述区：按**你填的东西**念出来（变体甲 / 乙 / 丙），可滚动
##
## —— 交互 ——
##   ↑↓    换格（表格内按列上下走、单选内上下走；到记述区 = 滚动）
##   ←→    改值（循环：空 → 各选项 → 空，**不设默认值**）
##   Tab   平铺顺序换格（Shift+Tab 反向）
##   Enter 在出口上 = 落定；在格子上 = 下一格
##   Esc / F 关表（不落定出口）
##   鼠标：点格选中、再点一次改值；滚轮改值 / 滚记述区；点出口落定
##
## ⚠️ 全部自绘：不用 OptionButton / PopupMenu（任务书 §2.3）。
## ⚠️ 不新增 InputMap action：只读 ui_* 内建动作 + 裸键轮询（改 project.godot 要重启编辑器）。

signal exit_chosen(choice: String)
signal form_closed()

const EndingStore = preload("res://scripts/ending_store.gd")
const EndingReport = preload("res://scripts/ending_report.gd")

const UI := 2.0
const FONT := int(10 * UI)
const FONT_BIG := int(13 * UI)
const FONT_SMALL := int(9 * UI)

## 面板（设计坐标）。底部留 FOOTER_H 给两行 footer。
const PANEL := Rect2(16.0, 8.0, 608.0, 344.0)
const TITLE_H := 20.0
const FOOTER_H := 30.0

# ---- 左半：表格 ------------------------------------------------------------
const CONTENT_TOP := 26.0
const HEAD_H := 12.0
const ROW_TOP := 38.0        # 第一行 y（标题行占 26..38）
const ROW_GAP := 15.0
const ROW_H := 14.0
const COL_YEAR_X := 8.0
const COL_YEAR_W := 30.0
const COL_M_X := 40.0        # 动机形态列
const COL_I_X := 160.0       # 故意形态列
const COL_CELL_W := 118.0

# ---- 左半：四个单选 --------------------------------------------------------
const RADIO_TOP := 120.0
const RADIO_GAP := 15.0
const RADIO_LABEL_W := 96.0
const RADIO_X := 106.0
const RADIO_W := 172.0

# ---- 右半：卷宗抬头 + 出口 -------------------------------------------------
const RIGHT_X := 286.0
const RIGHT_W := 314.0
const EXIT_TOP := 90.0
const EXIT_GAP := 20.0
const EXIT_H := 17.0

# ---- 下半：记述区 ----------------------------------------------------------
const REPORT_X := 8.0
const REPORT_W := 584.0
const REPORT_TOP := 190.0
const REPORT_LABEL_H := 12.0
const REPORT_PAD := 6.0
const LINE_H := 10.5

## footer 第二行：开表时世界是停的，这句话要说清楚。
const FOOTER_PAUSED := "世界已暂停 · 按 F 或 Esc 关闭归档表"
const FOOTER_HINT := "↑↓ 选格 · ←→ 改值（循环）· Tab 换格 · Enter 落定出口"

## 焦点槽位（平铺顺序 = Tab 顺序）。
##   0..9   表格十格（行优先：1926动机、1926故意、1951动机、…）
##   10..13 四个单选
##   14..15 两个出口
##   16     记述区（只用来滚）
const F_CELLS := 0
const F_RADIOS := 10
const F_EXITS := 14
const F_REPORT := 16
const FOCUS_COUNT := 17

## 单选槽位顺序 → 数据字段（下标 = 焦点 - F_RADIOS）。
const RADIO_FIELDS: Array = ["case_1951", "earliest", "burial", "count"]

var font: Font = ThemeDB.fallback_font

var open := false
var _focus := 0
var _scroll := 0
var _frame_year := 2026
## 存档一局只读一次（开表时才读；读不到就是空表）。
var _loaded := false
## 裸键边沿检测（Tab / Shift / F）。
var _tab_down := false
var _f_down := false
var _shift_down := false


func _ready() -> void:
	# ⚠️ 必须用 set_anchors_AND_OFFSETS_preset：只 set_anchors_preset 的话
	# 动态 add_child 出来的节点 offsets 还是 0，size 会是 (0,0)，坐标全算错（踩过）。
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


# ---- 对外接口 --------------------------------------------------------------

func is_open() -> bool:
	return open


## 开表。frame_year = 当前时间轴年份（决定抬头里的归档员 —— 表只在 A5 开，默认 2026）。
func open_form(year: int = 2026) -> void:
	_frame_year = year
	if not _loaded:
		_loaded = true
		EndingStore.load()     # 读不到 = 保持空表，不崩
	open = true
	_focus = 0
	_scroll = 0
	mouse_filter = Control.MOUSE_FILTER_STOP
	queue_redraw()


## 关表。**顺手落盘** —— 玩家填了一半关掉，不该白填。
func close_form() -> void:
	if not open:
		return
	open = false
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	EndingStore.save()
	queue_redraw()
	form_closed.emit()


func toggle(year: int = 2026) -> void:
	if open:
		close_form()
	else:
		open_form(year)


## 当前这份记述（测试 / main.gd 要念文本时用）。
func report_now() -> Dictionary:
	var st: Dictionary = EndingStore.snapshot()
	st["frame_year"] = _frame_year
	return EndingReport.build(st)


func frame_year() -> int:
	return _frame_year


# ---- 焦点 / 改值（测试也走这几个口子，不走 Input） --------------------------

func focus_index() -> int:
	return _focus


func set_focus(i: int) -> void:
	_focus = clampi(i, 0, FOCUS_COUNT - 1)
	queue_redraw()


## ←→ 的效果：当前格往 dir 方向循环一个值。
func cycle(dir: int) -> void:
	_cycle_value(1 if dir >= 0 else -1)


## 平铺换格（Tab）。
func tab_step(back: bool = false) -> void:
	_focus = (_focus + (-1 if back else 1) + FOCUS_COUNT) % FOCUS_COUNT
	queue_redraw()


## 上下走（在记述区 = 滚动）。
func move_focus(delta: int) -> void:
	if _focus >= F_REPORT:
		_scroll = clampi(_scroll + delta, 0, _max_scroll())
	elif _focus >= F_EXITS:
		var n := EndingStore.EXITS.size()
		_focus = F_EXITS + ((_focus - F_EXITS) + delta + n) % n
	elif _focus >= F_RADIOS:
		var rn := RADIO_FIELDS.size()
		_focus = F_RADIOS + ((_focus - F_RADIOS) + delta + rn) % rn
	else:
		var rows := EndingStore.YEARS.size()
		@warning_ignore("integer_division")
		var yi := _focus / 2
		var col := _focus % 2
		yi = (yi + delta + rows) % rows
		_focus = yi * 2 + col
	queue_redraw()


## 落定某个出口（0 = 已归档，1 = 存疑）。成功 = 存盘 + 发信号 + 关表。
func commit_exit(i: int) -> bool:
	if i < 0 or i >= EndingStore.EXITS.size():
		return false
	var choice := String(EndingStore.EXITS[i])
	if not EndingStore.set_exit(choice):
		return false
	# 出口一按就落定：先存一次盘，再关表（close_form 还会再存一次，幂等）。
	EndingStore.save()
	queue_redraw()
	exit_chosen.emit(choice)
	close_form()
	return true


func scroll_lines() -> int:
	return _scroll


# ---- 输入 ------------------------------------------------------------------

func _process(_delta: float) -> void:
	if not open:
		_tab_down = false
		_f_down = false
		_shift_down = false
		return
	_handle_keys()
	queue_redraw()


## 裸键轮询 + 边沿检测（照 main.gd 的 F11 / I 键那套路子，不新增 InputMap action）。
func _handle_keys() -> void:
	# Esc：关表（不落定出口 —— 出口是玩家按出来的，不能顺手替他选）。
	if Input.is_action_just_pressed("ui_cancel"):
		close_form()
		return

	var f_now := Input.is_key_pressed(KEY_F) or Input.is_physical_key_pressed(KEY_F)
	if f_now and not _f_down:
		_f_down = true
		close_form()
		return
	_f_down = f_now

	# Tab / Shift+Tab：平铺换格。
	var shift_now := Input.is_key_pressed(KEY_SHIFT)
	var tab_now := Input.is_key_pressed(KEY_TAB)
	if tab_now and not _tab_down:
		tab_step(shift_now)
	_tab_down = tab_now
	_shift_down = shift_now

	if Input.is_action_just_pressed("ui_up"):
		move_focus(-1)
	elif Input.is_action_just_pressed("ui_down"):
		move_focus(1)
	elif Input.is_action_just_pressed("ui_left"):
		if _focus < F_EXITS:
			_cycle_value(-1)
	elif Input.is_action_just_pressed("ui_right"):
		if _focus < F_EXITS:
			_cycle_value(1)
	elif Input.is_action_just_pressed("ui_accept"):
		_accept()


func _accept() -> void:
	if _focus >= F_EXITS and _focus < F_REPORT:
		commit_exit(_focus - F_EXITS)
	elif _focus < F_RADIOS:
		tab_step(false)


## ←→：把当前槽位的值往前/往后循环一位。
## 选项表里**带上空串当第一项** —— 所以能一路转回空格，且没有默认值。
func _cycle_value(dir: int) -> void:
	if _focus < F_RADIOS:
		@warning_ignore("integer_division")
		var yi := _focus / 2
		var col := _focus % 2
		var year := String(EndingStore.YEARS[yi])
		var opts := _with_blank(EndingStore.options_for_col(col))
		var cur := EndingStore.get_cell(year, col)
		var i := opts.find(cur)
		if i < 0:
			i = 0
		i = (i + dir + opts.size()) % opts.size()
		EndingStore.set_cell(year, col, String(opts[i]))
	elif _focus < F_EXITS:
		var field := String(RADIO_FIELDS[_focus - F_RADIOS])
		var opts := _with_blank(EndingStore.options_for_radio(field))
		var cur := EndingStore.get_radio(field)
		var i := opts.find(cur)
		if i < 0:
			i = 0
		i = (i + dir + opts.size()) % opts.size()
		EndingStore.set_radio(field, String(opts[i]))
	queue_redraw()


func _with_blank(options: Array) -> Array:
	var out: Array = [""]
	out.append_array(options)
	return out


## 鼠标：点格 / 点箭头 / 滚轮 / 点出口。
func _gui_input(event: InputEvent) -> void:
	if not open:
		return

	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if not mb.pressed:
			return
		match mb.button_index:
			MOUSE_BUTTON_WHEEL_UP:
				_wheel(-1)
				accept_event()
				return
			MOUSE_BUTTON_WHEEL_DOWN:
				_wheel(1)
				accept_event()
				return
			MOUSE_BUTTON_LEFT:
				_click(mb.position)
				accept_event()
				return
		return

	if event is InputEventMouseMotion:
		# 鼠标经过就能看出哪里能点（只在开表时）。
		queue_redraw()


func _wheel(dir: int) -> void:
	var p := _panel_rect()
	var hit := _hit(p, _mouse_pos())
	if hit["kind"] == "cell":
		set_focus(int(hit["idx"]))
		_cycle_value(dir)
	elif hit["kind"] == "radio":
		set_focus(F_RADIOS + int(hit["idx"]))
		_cycle_value(dir)
	elif hit["kind"] == "report":
		_scroll = clampi(_scroll + dir, 0, _max_scroll())


func _click(pos: Vector2) -> void:
	var p := _panel_rect()
	var hit := _hit(p, pos)
	match String(hit["kind"]):
		"cell":
			var idx := int(hit["idx"])
			# 点没选中的格 = 选中；点已选中的格 = 改一个值（鼠标也能填表）。
			if _focus == idx:
				_cycle_value(1)
			else:
				set_focus(idx)
		"radio":
			var idx := F_RADIOS + int(hit["idx"])
			if _focus == idx:
				_cycle_value(1)
			else:
				set_focus(idx)
		"exit":
			commit_exit(int(hit["idx"]))
		"report":
			set_focus(F_REPORT)


func _mouse_pos() -> Vector2:
	return get_local_mouse_position()


## 命中测试：屏幕坐标 → {"kind": cell/radio/exit/report, "idx": n}。
func _hit(p: Rect2, pos: Vector2) -> Dictionary:
	for i in EndingStore.YEARS.size() * 2:
		if _cell_rect(p, i).has_point(pos):
			return {"kind": "cell", "idx": i}
	for i in RADIO_FIELDS.size():
		if _radio_rect(p, i).has_point(pos):
			return {"kind": "radio", "idx": i}
	for i in EndingStore.EXITS.size():
		if _exit_rect(p, i).has_point(pos):
			return {"kind": "exit", "idx": i}
	if _report_rect(p).has_point(pos):
		return {"kind": "report", "idx": 0}
	return {"kind": "", "idx": 0}


# ---- 几何（设计坐标 × UI，全部转成屏幕矩形） --------------------------------

func _panel_rect() -> Rect2:
	return Rect2(PANEL.position * UI, PANEL.size * UI)


func _cell_rect(p: Rect2, idx: int) -> Rect2:
	@warning_ignore("integer_division")
	var yi := idx / 2
	var col := idx % 2
	var x := COL_M_X if col == 0 else COL_I_X
	var y := ROW_TOP + float(yi) * ROW_GAP
	return Rect2(p.position + Vector2(x * UI, y * UI), Vector2(COL_CELL_W * UI, ROW_H * UI))


func _radio_rect(p: Rect2, i: int) -> Rect2:
	var y := RADIO_TOP + float(i) * RADIO_GAP
	return Rect2(p.position + Vector2(RADIO_X * UI, y * UI), Vector2(RADIO_W * UI, ROW_H * UI))


func _exit_rect(p: Rect2, i: int) -> Rect2:
	var y := EXIT_TOP + float(i) * EXIT_GAP
	return Rect2(p.position + Vector2(RIGHT_X * UI, y * UI), Vector2(RIGHT_W * UI, EXIT_H * UI))


func _report_rect(p: Rect2) -> Rect2:
	var bottom := PANEL.size.y - FOOTER_H - 4.0
	return Rect2(p.position + Vector2(REPORT_X * UI, REPORT_TOP * UI),
		Vector2(REPORT_W * UI, (bottom - REPORT_TOP) * UI))


func _report_text_width() -> float:
	return (REPORT_W - REPORT_PAD * 2.0) * UI


func _report_text_top() -> float:
	return REPORT_TOP + REPORT_LABEL_H + 2.0


# ---- 绘制 ------------------------------------------------------------------

func _draw() -> void:
	if open:
		_draw_panel()


func _draw_panel() -> void:
	var p := _panel_rect()

	# 背景压暗（游戏画面还在下面）
	draw_rect(Rect2(Vector2.ZERO, size), Color(0.03, 0.03, 0.03, 0.72), true)
	# 面板
	draw_rect(p, Color(0.09, 0.08, 0.07, 0.97), true)
	draw_rect(p, Color(0.58, 0.50, 0.38, 0.90), false, 1.0 * UI)

	_draw_title(p)
	_draw_table(p)
	_draw_radios(p)
	_draw_right(p)
	_draw_report(p)
	_draw_footer(p)


func _draw_title(p: Rect2) -> void:
	var bar_h := TITLE_H * UI
	draw_rect(Rect2(p.position, Vector2(p.size.x, bar_h)), Color(0.14, 0.12, 0.10, 0.95), true)
	draw_line(p.position + Vector2(0, bar_h), p.position + Vector2(p.size.x, bar_h),
		Color(0.55, 0.47, 0.36, 0.85), 1.0 * UI)

	draw_string(font, Vector2(p.position.x + 10.0 * UI, p.position.y + 14.0 * UI),
		"结案归档表 · 第七十二万三千零一卷",
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_BIG, Color(0.95, 0.82, 0.60))

	var rep := report_now()
	var who := "归档员 %s" % String(rep["archivist"])
	var w: float = font.get_string_size(who, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x
	draw_string(font, Vector2(p.position.x + p.size.x - w - 10.0 * UI,
		p.position.y + 14.0 * UI), who,
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.72, 0.70, 0.63))


func _draw_table(p: Rect2) -> void:
	var ty := p.position.y + (CONTENT_TOP + 10.0) * UI
	draw_string(font, Vector2(p.position.x + COL_YEAR_X * UI, ty), "年份",
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_SMALL, Color(0.60, 0.58, 0.52))
	draw_string(font, Vector2(p.position.x + COL_M_X * UI, ty), "动机形态",
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_SMALL, Color(0.60, 0.58, 0.52))
	draw_string(font, Vector2(p.position.x + COL_I_X * UI, ty), "故意形态",
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_SMALL, Color(0.60, 0.58, 0.52))

	for i in EndingStore.YEARS.size() * 2:
		var r := _cell_rect(p, i)
		@warning_ignore("integer_division")
		var yi := i / 2
		var col := i % 2
		var year := String(EndingStore.YEARS[yi])
		var val := EndingStore.get_cell(year, col)
		var focused := _focus == i

		draw_rect(r, Color(0.16, 0.14, 0.12, 0.95) if focused else Color(0.11, 0.10, 0.09, 0.85), true)
		draw_rect(r, Color(0.85, 0.68, 0.38, 0.90) if focused else Color(0.30, 0.27, 0.22, 0.90),
			false, 1.0 * UI)

		var base := r.position.y + r.size.y - 4.0 * UI
		if focused:
			# 循环箭头（点它 / 按 ←→ 都行）
			draw_string(font, Vector2(r.position.x + 3.0 * UI, base), "‹",
				HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.85, 0.68, 0.38))
			draw_string(font, Vector2(r.position.x + r.size.x - 8.0 * UI, base), "›",
				HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.85, 0.68, 0.38))

		if val.is_empty():
			# 空格画一条短横 —— 是「还没写」，不是「答案是它」（任务书 §2.1）。
			draw_string(font, Vector2(r.position.x, base), "—",
				HORIZONTAL_ALIGNMENT_CENTER, r.size.x, FONT, Color(0.38, 0.36, 0.32))
		else:
			draw_string(font, Vector2(r.position.x, base), val,
				HORIZONTAL_ALIGNMENT_CENTER, r.size.x, FONT,
				Color(0.96, 0.86, 0.64) if focused else Color(0.86, 0.83, 0.75))

	# 行首年份（不进焦点、不可改）
	for yi in EndingStore.YEARS.size():
		var y := ROW_TOP + float(yi) * ROW_GAP
		var base := p.position.y + (y + ROW_H - 4.0) * UI
		draw_string(font, Vector2(p.position.x + COL_YEAR_X * UI, base),
			String(EndingStore.YEARS[yi]),
			HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.62, 0.60, 0.54))


func _draw_radios(p: Rect2) -> void:
	var labels := {
		"case_1951": "1951 案性质",
		"earliest": "最早一具",
		"burial": "埋尸位置",
		"count": "埋葬人数",
	}
	for i in RADIO_FIELDS.size():
		var field := String(RADIO_FIELDS[i])
		var r := _radio_rect(p, i)
		var focused := _focus == F_RADIOS + i
		var base := r.position.y + r.size.y - 4.0 * UI

		draw_string(font, Vector2(p.position.x + COL_YEAR_X * UI, base),
			String(labels.get(field, field)),
			HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.78, 0.75, 0.66))

		draw_rect(r, Color(0.16, 0.14, 0.12, 0.95) if focused else Color(0.11, 0.10, 0.09, 0.85), true)
		draw_rect(r, Color(0.85, 0.68, 0.38, 0.90) if focused else Color(0.30, 0.27, 0.22, 0.90),
			false, 1.0 * UI)

		if focused:
			draw_string(font, Vector2(r.position.x + 3.0 * UI, base), "‹",
				HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.85, 0.68, 0.38))
			draw_string(font, Vector2(r.position.x + r.size.x - 8.0 * UI, base), "›",
				HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.85, 0.68, 0.38))

		var val := EndingStore.get_radio(field)
		if val.is_empty():
			draw_string(font, Vector2(r.position.x, base), "—",
				HORIZONTAL_ALIGNMENT_CENTER, r.size.x, FONT, Color(0.38, 0.36, 0.32))
		else:
			draw_string(font, Vector2(r.position.x, base), val,
				HORIZONTAL_ALIGNMENT_CENTER, r.size.x, FONT,
				Color(0.96, 0.86, 0.64) if focused else Color(0.86, 0.83, 0.75))


func _draw_right(p: Rect2) -> void:
	var rep := report_now()
	var x := p.position.x + RIGHT_X * UI
	var y := p.position.y + CONTENT_TOP * UI
	var big := font.get_string_size("X", HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_SMALL).y

	draw_string(font, Vector2(x, y + 10.0 * UI), "卷宗 %s" % String(rep["case_no"]),
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_SMALL, Color(0.72, 0.70, 0.63))
	draw_string(font, Vector2(x, y + 10.0 * UI + big + 2.0 * UI), "地点 %s" % String(rep["place"]),
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_SMALL, Color(0.72, 0.70, 0.63))
	draw_string(font, Vector2(x, y + 10.0 * UI + (big + 2.0 * UI) * 2.0),
		"事件 %s" % String(rep["event"]),
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_SMALL, Color(0.72, 0.70, 0.63))

	# 分隔线 + 出口标题
	var sep_y := p.position.y + (EXIT_TOP - 8.0) * UI
	draw_line(Vector2(x, sep_y), Vector2(x + RIGHT_W * UI, sep_y),
		Color(0.35, 0.32, 0.26, 0.90), 1.0 * UI)
	draw_string(font, Vector2(x, sep_y - 4.0 * UI), "记完之后，二选一",
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_SMALL, Color(0.60, 0.58, 0.52))

	for i in EndingStore.EXITS.size():
		var r := _exit_rect(p, i)
		var focused := _focus == F_EXITS + i
		var chosen := EndingStore.get_exit() == String(EndingStore.EXITS[i])
		draw_rect(r, Color(0.18, 0.15, 0.12, 0.95) if focused else Color(0.11, 0.10, 0.09, 0.85), true)
		draw_rect(r, Color(0.85, 0.68, 0.38, 0.90) if focused else Color(0.30, 0.27, 0.22, 0.90),
			false, 1.0 * UI)
		var line := String(EndingReport.exit_text(String(EndingStore.EXITS[i])).split("\n")[0])
		draw_string(font, Vector2(r.position.x, r.position.y + r.size.y - 5.0 * UI),
			("▶ " if chosen else "") + line,
			HORIZONTAL_ALIGNMENT_CENTER, r.size.x, FONT,
			Color(0.96, 0.86, 0.64) if focused else Color(0.82, 0.79, 0.71))

	# 已选出口的第二行（「世界刑侦陈列馆 · 第七十二万三千零一卷」这种）
	if not EndingStore.get_exit().is_empty():
		var lines := EndingReport.exit_text(EndingStore.get_exit()).split("\n")
		if lines.size() > 1:
			draw_string(font, Vector2(x, p.position.y + (EXIT_TOP + EXIT_GAP * 2.0) * UI),
				String(lines[1]), HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_SMALL,
				Color(0.62, 0.60, 0.54))


func _draw_report(p: Rect2) -> void:
	var r := _report_rect(p)
	draw_rect(r, Color(0.12, 0.11, 0.10, 0.95), true)
	draw_rect(r, Color(0.35, 0.32, 0.26, 0.90), false, 1.0 * UI)
	draw_string(font, Vector2(r.position.x + REPORT_PAD * UI, r.position.y + 10.0 * UI),
		"记述（按你填的念）",
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_SMALL, Color(0.60, 0.58, 0.52))

	var lines := _wrapped_report()
	var max_scroll := _max_scroll()
	_scroll = clampi(_scroll, 0, max_scroll)
	var visible_n := _visible_report_lines()

	var y := p.position.y + _report_text_top() * UI
	for i in range(_scroll, mini(_scroll + visible_n, lines.size())):
		var t := String(lines[i])
		if not t.is_empty():
			draw_string(font, Vector2(r.position.x + REPORT_PAD * UI, y + LINE_H * UI - 3.0 * UI),
				t, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.88, 0.85, 0.77))
		y += LINE_H * UI

	# 滚动条（只在真有内容滚得动时画）
	if max_scroll > 0:
		var track := Rect2(r.position.x + r.size.x - 4.0 * UI, r.position.y + 2.0 * UI,
			2.0 * UI, r.size.y - 4.0 * UI)
		draw_rect(track, Color(0.20, 0.18, 0.15, 0.90), true)
		var frac := float(visible_n) / float(maxi(1, lines.size()))
		var th := maxf(8.0 * UI, track.size.y * frac)
		var ty := track.position.y + (track.size.y - th) * (
			float(_scroll) / float(maxi(1, max_scroll)))
		draw_rect(Rect2(track.position.x, ty, track.size.x, th), Color(0.60, 0.52, 0.38, 0.95), true)


func _draw_footer(p: Rect2) -> void:
	var y1 := p.position.y + (PANEL.size.y - FOOTER_H + 8.0) * UI
	var y2 := y1 + 12.0 * UI
	draw_line(Vector2(p.position.x + 6.0 * UI, y1 - 8.0 * UI),
		Vector2(p.position.x + p.size.x - 6.0 * UI, y1 - 8.0 * UI),
		Color(0.35, 0.32, 0.26, 0.90), 1.0 * UI)
	draw_string(font, Vector2(p.position.x + 8.0 * UI, y1), FOOTER_HINT,
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_SMALL, Color(0.62, 0.60, 0.54))
	draw_string(font, Vector2(p.position.x + 8.0 * UI, y2), FOOTER_PAUSED,
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_SMALL, Color(0.50, 0.48, 0.43))


# ---- 记述区文本 ------------------------------------------------------------

func _wrapped_report() -> Array:
	var out: Array = []
	var w := _report_text_width()
	for ln in report_now()["lines"]:
		var t := String(ln)
		if t.is_empty():
			out.append("")
		else:
			out.append_array(_wrap(t, w))
	# 出口文本接在末尾（选了才算落定，但先给玩家看一眼）。
	var rep := report_now()
	if not String(rep["exit_text"]).is_empty():
		out.append("")
		for ln in String(rep["exit_text"]).split("\n"):
			out.append_array(_wrap(String(ln), w))
	return out


func _visible_report_lines() -> int:
	var vh := (PANEL.size.y - FOOTER_H - 4.0 - _report_text_top()) * UI
	return maxi(1, int(floor(vh / (LINE_H * UI))))


func _max_scroll() -> int:
	return maxi(0, _wrapped_report().size() - _visible_report_lines())


## 按字符宽度硬折行（中文没空格，累积宽度切最稳 —— 同 evidence_archive.gd）。
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