extends Control

## 结局收束层（任务书 L19）：把归档表上「落定出口」这一下接住。
##
## 之前 `ending_form.exit_chosen` 全仓库零监听者 —— 玩家按完出口只存盘 + 关表，
## 画面什么都不发生。这一层就是那唯一的监听者：
##
##   黑幕 0 → 0.82（0.8s）→ 正中偏上竖排三行 → 按任意键 → 黑幕 1.0s 淡回 0 → 自由探索
##
## 三行字：
##   1) 玩家选的那个出口（「已归档」/「存疑」）
##   2) ending_report.gd 对应变体正文的**最后一行**（超长截断到 TEXT_MAX 字）
##   3) 「—— 按任意键 ——」
##
## ⚠️ 一行剧情都不自己写（任务书 §2.1）：第 2 行是从 ending_report.build() 的
##    `prose` 里原样抠出来的最后一条，不拼接、不改写。要改文案去改 ending_report.gd。
##
## ⚠️ 不引入任何美术资源：黑幕 = draw_rect，字 = draw_string，字体沿用
##    ThemeDB.fallback_font（与 hud.gd / ending_form.gd 同一条路）。
##
## ⚠️ 收束期间「世界全停」是两层保证：
##    a) main.gd 的「档案/书本/表开着 ⇒ 停世界」那条 if 加了本层的 is_playing()（任务书 §5.5）；
##    b) 本层自己把 SceneTree 暂停（get_tree().paused）—— 因为 G/I/F11 的轮询段
##       在那条 return **之前**，光靠 a) 挡不住「收束时按 G 又弹出归档表」。
##    暂停用 PROCESS_MODE_ALWAYS 绕过：黑幕照常渐变、按键照常能收。
##
## ⚠️ 不新增 InputMap action（任务书 §2.3）：「任意键」走 _input 的**边沿**，
##    不轮询按键状态 —— 免得「按下出口的那颗 Enter 还按着」把收束直接收掉。

const EndingReport = preload("res://scripts/ending_report.gd")
const EndingStore = preload("res://scripts/ending_store.gd")

# 设计单位同 ending_form.gd / hud.gd：640×360 的设计值 × UI。
const UI := 2.0
const FONT := int(10 * UI)
const FONT_BIG := int(16 * UI)
const FONT_SMALL := int(9 * UI)

const BLACK_MAX := 0.82
const FADE_IN := 0.8
const FADE_OUT := 1.0
## 第 2 行的字数上限（任务书 §3.2）。
const TEXT_MAX := 60
const HINT := "—— 按任意键 ——"

enum Phase { IDLE, IN, WAIT, OUT }

var font: Font = ThemeDB.fallback_font

var _phase := Phase.IDLE
var _t := 0.0
var _black := 0.0
var _text_a := 0.0
var _choice := ""
var _body := ""
## 树是**本层**暂停的才由本层解除（别人暂停的场景不许我们顺手放开）。
var _paused_tree := false


func _ready() -> void:
	# ⚠️ 必须用 set_anchors_AND_OFFSETS_preset：只 set_anchors_preset 的话，
	# 动态 add_child 出来的节点 offsets 还是 0，size 会是 (0,0)，黑幕画在 0×0 上
	# —— 与 ending_form.gd 踩的是同一个坑。
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	# 黑幕不吃鼠标：这一层只盖画面，不抢归档表的点击（表这时已经关了，保险起见）。
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	# 收束期间整棵树会被暂停（_pause_tree），本节点必须照常跑完渐变。
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_process(false)


# ---- 对外接口 --------------------------------------------------------------

## 收束中吗？（IN / WAIT / OUT 都算 —— 淡出没走完之前世界不许动）
func is_playing() -> bool:
	return _phase != Phase.IDLE


## 播放收束。由 ending_form.exit_chosen 连过来（main.gd 的 _make_outro）。
## 返回是否真的开始播（重复触发 / 不认识的出口 ⇒ false，什么都不做）。
func play(choice: String) -> bool:
	if _phase != Phase.IDLE:
		# 任务书 §3.6：一次落定只收一次；重开表再落定 = _phase 已回 IDLE，照常再来。
		return false
	var c := choice.strip_edges()
	if EndingReport.exit_text(c).is_empty():
		# 认不出的出口不放黑幕（宁可不演，也不要一块没人解释的黑屏）。
		return false

	# 1) 表先收 —— commit_exit 自己也会 close_form，这里兜一层：
	#    不论信号从哪儿发出来，收束开始时表必须是关的（别两样东西叠着）。
	_close_sibling_form()

	_choice = c
	_body = _pick_body(_current_report())
	_phase = Phase.IN
	_t = 0.0
	_black = 0.0
	_text_a = 0.0
	_pause_tree(true)
	set_process(true)
	queue_redraw()
	return true


## 收掉黑幕（「任意键」的真正入口；_input 边沿与测试都走这里）。
func dismiss() -> void:
	if _phase != Phase.WAIT:
		return
	_phase = Phase.OUT
	_t = 0.0
	queue_redraw()


## 三行字（第 1 行 / 第 2 行 / 提示行）。测试用，也给以后要念文本的地方用。
func lines() -> Array:
	return [_choice, _body, HINT]


## 当前黑幕 alpha（截图断言用）。
func black_level() -> float:
	return _black


## 当前阶段名（日志 / 测试用）。
func phase_name() -> String:
	match _phase:
		Phase.IN:
			return "in"
		Phase.WAIT:
			return "wait"
		Phase.OUT:
			return "out"
	return "idle"


# ---- 状态机 ----------------------------------------------------------------

func _process(delta: float) -> void:
	_advance(delta)


## 一帧推进一步。测试可以 set_process(false) 后手动调它，不受真实帧率影响。
func _advance(delta: float) -> void:
	match _phase:
		Phase.IN:
			_t += delta
			var k := clampf(_t / FADE_IN, 0.0, 1.0)
			_black = BLACK_MAX * k
			# 字比黑幕晚半拍起：黑幕铺到 ~35% 时字才开始浮出来。
			_text_a = clampf((_t - FADE_IN * 0.35) / (FADE_IN * 0.65), 0.0, 1.0)
			if _t >= FADE_IN:
				_black = BLACK_MAX
				_text_a = 1.0
				_phase = Phase.WAIT
				_t = 0.0
			queue_redraw()
		Phase.WAIT:
			# 什么都不推 —— 等 _input 里的按键边沿（或测试调 dismiss()）。
			pass
		Phase.OUT:
			_t += delta
			var k2 := clampf(_t / FADE_OUT, 0.0, 1.0)
			_black = BLACK_MAX * (1.0 - k2)
			# 字比黑幕退得快：黑幕还剩一半时字已经干净了，不会糊在半黑上。
			_text_a = clampf(1.0 - k2 * 1.8, 0.0, 1.0)
			if _t >= FADE_OUT:
				_finish()
			else:
				queue_redraw()


func _finish() -> void:
	_phase = Phase.IDLE
	_black = 0.0
	_text_a = 0.0
	_choice = ""
	_body = ""
	_t = 0.0
	_pause_tree(false)
	set_process(false)
	queue_redraw()


## 「任意键」：只认**按下**的边沿，不认按住（所以按下出口那颗键不会误收）。
func _input(event: InputEvent) -> void:
	if _phase != Phase.WAIT:
		return
	var hit := false
	if event is InputEventKey:
		var k := event as InputEventKey
		hit = k.pressed and not k.echo
	elif event is InputEventMouseButton:
		hit = (event as InputEventMouseButton).pressed
	elif event is InputEventJoypadButton:
		hit = (event as InputEventJoypadButton).pressed
	if hit:
		if get_viewport() != null:
			get_viewport().set_input_as_handled()
		dismiss()


# ---- 收束文字（只挑，不写） -------------------------------------------------

## 第 2 行 = 对应变体正文的最后一行。
##
## 为什么取最后一行：三个变体的收尾位置就是各自「把话说完」的地方 ——
##   甲 的末行是全书唯一的收官句（「没有人被平反。因为没有人是无辜的。」）
##   乙 的末行停在死者那一条（档案上他只被记成受害者）
##   丙 的末行停在最后一个可念的事实栏（档案到此为止）
## 都是 ending_report.gd 里现成的字，这里一个字都没改。
func _pick_body(rep: Dictionary) -> String:
	var t := ""
	var prose: Array = rep.get("prose", [])
	for i in range(prose.size() - 1, -1, -1):
		var s := String(prose[i]).strip_edges()
		if not s.is_empty():
			t = s
			break
	if t.is_empty():
		# prose 被降没了（理论上不会）⇒ 退到整篇正文的最后一条非空行。
		var all: Array = rep.get("lines", [])
		for i in range(all.size() - 1, -1, -1):
			var s2 := String(all[i]).strip_edges()
			if not s2.is_empty():
				t = s2
				break
	return _truncate(t, TEXT_MAX)


func _truncate(s: String, n: int) -> String:
	if s.length() <= n or n <= 1:
		return s
	return s.substr(0, n - 1) + "…"


## 当前这份记述：优先问归档表（它是唯一知道 frame_year 的人，
## report_now() 与表里画出来的那段逐字一致）；没有表就自己按存档算一份。
func _current_report() -> Dictionary:
	var f := _sibling_form()
	if f != null and f.has_method("report_now"):
		return f.report_now()
	return EndingReport.build(EndingStore.snapshot())


func _sibling_form() -> Node:
	var p := get_parent()
	if p == null:
		return null
	return p.get_node_or_null("EndingForm")


func _close_sibling_form() -> void:
	var f := _sibling_form()
	if f == null or not f.has_method("close_form"):
		return
	if f.has_method("is_open") and not f.is_open():
		return
	f.close_form()


# ---- 世界暂停 --------------------------------------------------------------

func _pause_tree(on: bool) -> void:
	var tree := get_tree()
	if tree == null:
		return
	if on:
		if not tree.paused:
			tree.paused = true
			_paused_tree = true
	elif _paused_tree:
		tree.paused = false
		_paused_tree = false


## 兜底：本节点在收束中途被摘掉（换场景 / 退出）时别把整棵树留在暂停态。
func _exit_tree() -> void:
	_pause_tree(false)


# ---- 绘制 ------------------------------------------------------------------

func _draw() -> void:
	if _black > 0.0:
		draw_rect(Rect2(Vector2.ZERO, size), Color(0.0, 0.0, 0.0, _black), true)
	if _text_a <= 0.0 or _choice.is_empty():
		return

	# 正中偏上，竖排三行，水平居中。
	var y0 := size.y * 0.40
	var a := _text_a
	draw_string(font, Vector2(0.0, y0), _choice, HORIZONTAL_ALIGNMENT_CENTER,
		size.x, FONT_BIG, Color(0.95, 0.90, 0.78, a))
	draw_string(font, Vector2(0.0, y0 + 26.0 * UI), _body, HORIZONTAL_ALIGNMENT_CENTER,
		size.x, FONT, Color(0.86, 0.84, 0.78, a))
	draw_string(font, Vector2(0.0, y0 + 62.0 * UI), HINT, HORIZONTAL_ALIGNMENT_CENTER,
		size.x, FONT_SMALL, Color(0.62, 0.60, 0.55, a))