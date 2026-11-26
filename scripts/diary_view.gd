extends Control

## L16 · 双本对照界面（假本 | 真本 并排）。
##
## 布局照 `_mdtest/render3.gd` 的实验结论，但**不用「水平容器 + 面板容器」那种拼法**：
## 两个 DiaryPage 手动摆位（任务书 §3.4）—— 容器会把纸页拉伸/留白，实测量出来的
## 字号线高就不对了，纸页尺寸必须是我们自己给的定值。
##
## 本文件只负责「摆两张纸 + 背景 + 翻页 + 关闭」，正文怎么画全在 `diary_page.gd`。
##
## 交互（2026-11-26 定）：
##   · 翻页：纸页页脚上两个箭头（点一下翻一页，仿 Minecraft 的书）+ 键盘 ← → / ↑ ↓
##   · 合书：E 或 Esc —— E 与「在世界里打开」用的是同一个键，开合对称
##   · 滚轮：上下各翻一页（鼠标习惯，不是滚动条；纸上没有滚动条了）

const DiaryPage = preload("res://scripts/diary_page.gd")
const DiaryMarkup = preload("res://scripts/diary_markup.gd")
const DiaryTexts = preload("res://scripts/diary_texts.gd")
const EvidenceStore = preload("res://scripts/evidence_store.gd")

## —— 版式（照 _mdtest/render3.gd:36-44 的比例，按 1280×720 重算）——
const PAGE_W := 470.0     # 单页宽
const PAGE_H := 648.0     # 单页高
const GAP := 18.0         # 页间距（render3.gd:44 的 separation）
const HINT_H := 22.0      # 底部提示条预留

const BG_COL := Color("#efe6d0")      # 整页压暗底（render3.gd:36-39）
const HINT_COL := Color("#6a5a48")
const HINT_FS := 12
const HINT := "← → 翻页        E / Esc 合上"

## 合上书本时通知外面（主流程用它把 HUD 放回来）
signal closed

var font: Font = ThemeDB.fallback_font

## 界面是否展开（接线方只读这个，别自己再存一份状态）
var open := false

var bg: ColorRect
var left_frame: Control
var right_frame: Control
## 这两页要用动态访问（page.goto_page / page.hit_arrow），故意不写 static 类型
var left_page = null
var right_page = null

var _fake_raw := ""
var _raw_raw := ""
var _left_title := "假本 · 誊清"
var _right_title := "真本 · 原稿"

## 合上动作发生在哪一帧：主流程用 just_closed() 避免「E 关掉又立刻被 E 打开」
var _close_frame := -1

## 证物档案界面（可选）：给了就在入档时闪一下「已收集」。不塞自己的依赖，接线方决定。
var archive_hook: Object = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_build()
	var pair := DiaryTexts.mill_pair()
	show_pair(String(pair.fake), String(pair.raw),
		String(pair.left_title), String(pair.right_title))
	visible = false
	resized.connect(_layout)
	_layout()


func _build() -> void:
	bg = ColorRect.new()
	bg.color = BG_COL
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)

	left_frame = _make_frame()
	right_frame = _make_frame()
	left_page = _make_page(left_frame)
	right_page = _make_page(right_frame)


func _make_frame() -> Control:
	var f := Control.new()
	f.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(f)
	return f


func _make_page(frame: Control):
	var p: Control = DiaryPage.new()
	frame.add_child(p)
	# 纸页填满它自己的框（框的尺寸由 _layout 给），不能自己去抢全屏
	p.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return p


## 摆两张纸。屏幕尺寸变了要重摆（resized 会调）。
func _layout() -> void:
	var sw: float = size.x if size.x > 1.0 else 1280.0
	var sh: float = size.y if size.y > 1.0 else 720.0
	var total := PAGE_W * 2.0 + GAP
	var x0 := roundf((sw - total) * 0.5)
	var y0 := roundf(maxf(8.0, (sh - PAGE_H - HINT_H) * 0.5))
	left_frame.position = Vector2(x0, y0)
	left_frame.size = Vector2(PAGE_W, PAGE_H)
	right_frame.position = Vector2(x0 + PAGE_W + GAP, y0)
	right_frame.size = Vector2(PAGE_W, PAGE_H)


# ---- 对外接口（接线方只用这几个）----------------------------------------

## 灌内容：左页原稿（假本，无标记）/ 右页原稿（真本，带 {{}} 标记）。
## 标题不传就沿用上一次的（默认「假本 · 誊清」「真本 · 原稿」）。
func show_pair(fake_raw: String, raw_raw: String,
		left_title: String = "", right_title: String = "") -> void:
	_fake_raw = fake_raw
	_raw_raw = raw_raw
	if left_title != "":
		_left_title = left_title
	if right_title != "":
		_right_title = right_title
	if left_page == null:
		return
	left_page.set_page(_left_title, false, DiaryMarkup.parse(_fake_raw, false))
	right_page.set_page(_right_title, true, DiaryMarkup.parse(_raw_raw, true))


func is_open() -> bool:
	return open


func open_view() -> void:
	open = true
	left_page.goto_page(0)
	right_page.goto_page(0)
	visible = true
	queue_redraw()


func close_view() -> void:
	if not open:
		return
	open = false
	visible = false
	_close_frame = Engine.get_process_frames()
	closed.emit()


## 这一帧刚刚合上书（E 键在 _input 里合上，主流程的 E 轮询会晚一帧看到）。
## 没有这道闸，按一次 E 会「合上 → 又打开」。
func just_closed() -> bool:
	return _close_frame == Engine.get_process_frames()


func toggle() -> void:
	if open:
		close_view()
	else:
		open_view()


## 把这本书按证物入档（"复刻一份在背包里"）：返回 EvidenceStore.RESULT_*。
## 档案里是一张「书」卡；正文不进档案（档案是清单 + 摘要），全文仍只在 DiaryTexts 里。
## 举证环节（对质时把书呈上）还没做，等那条线自己按 key 取这本书。
func collect_copy(year: int) -> int:
	var e := DiaryTexts.mill_evidence(year)
	var res := EvidenceStore.try_collect(String(e.key), String(e.name),
		String(e.source), String(e.text), int(e.year))
	if res != EvidenceStore.RESULT_DUPLICATE:
		EvidenceStore.save()
		if archive_hook != null and archive_hook.has_method("flash_collected"):
			archive_hook.call("flash_collected", String(e.name), res == EvidenceStore.RESULT_NEW_CARD)
	return res


# ---- 翻页 ----------------------------------------------------------------

## 两本一起翻（对照阅读：左页看到的和右页永远是同一处上下文）。
func turn(delta: int) -> void:
	if delta == 0:
		return
	left_page.goto_page(int(left_page.page_index()) + delta)
	right_page.goto_page(int(right_page.page_index()) + delta)
	queue_redraw()


func page_text() -> String:
	return "%s    %s" % [String(left_page.page_text()), String(right_page.page_text())]


# ---- 输入（只在自己的展开期间吃键，不吃 WASD/SHIFT/I）--------------------

func _input(event: InputEvent) -> void:
	if not open:
		return

	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if not mb.pressed:
			return
		# 点页脚上的两个箭头（仿 Minecraft 的书）
		if mb.button_index == MOUSE_BUTTON_LEFT:
			for p in [left_page, right_page]:
				if p == null:
					continue
				var d := int(p.hit_arrow(mb.position - p.global_position))
				if d != 0:
					turn(d)
					get_viewport().set_input_as_handled()
					return
		elif mb.button_index == MOUSE_BUTTON_WHEEL_UP:
			turn(-1)
			get_viewport().set_input_as_handled()
		elif mb.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			turn(1)
			get_viewport().set_input_as_handled()
		return

	if event is InputEventKey:
		var k := event as InputEventKey
		if not k.pressed or k.echo:
			return
		# 直接用物理键判断，不依赖 InputMap 有没有重载（和 F11 的兜底同一理由）
		var code := k.keycode if k.keycode != 0 else k.physical_keycode
		match code:
			KEY_ESCAPE, KEY_E:
				close_view()
			KEY_LEFT, KEY_UP, KEY_PAGEUP:
				turn(-1)
			KEY_RIGHT, KEY_DOWN, KEY_PAGEDOWN:
				turn(1)
			_:
				return
		get_viewport().set_input_as_handled()


# ---- 底部提示 ------------------------------------------------------------

func _draw() -> void:
	var w := font.get_string_size(HINT, HORIZONTAL_ALIGNMENT_LEFT, -1, HINT_FS).x
	draw_string(font, Vector2((size.x - w) * 0.5, size.y - 5.0), HINT,
		HORIZONTAL_ALIGNMENT_LEFT, -1, HINT_FS, Color(HINT_COL, 0.75))