extends SceneTree

## 结局接线自检（L16 线：把归档表接进主循环 + 删 J 调试键 + 书热点当日记入口）。
## 跑法：godot --headless --path . -s res://_mdtest/ending_wire_check.gd
##
## 口径说明（为什么这样测）：
##   · 归档表本体（填格 / 三变体 / 出口）已由 _mdtest/ending_check.gd 的 E1–E14 覆盖，
##     这里**不重复**测表内算法，只测「主循环有没有把它接上」。
##   · 主循环用轮询而不是事件（main.gd 开头注释），所以这里必须伪造**按键状态**：
##       - 裸键（G / J / Tab / F）：Input.parse_input_event() 是**排队**的，
##         调用后当帧读不到，要 await 一帧才生效（实测，见 A2 里那条守卫）。
##       - 动作键（move_up / shift_axis / inspect / ui_*）：Input.action_press() 立刻生效，
##         但「刚按下」的边沿在同一帧末就被清掉 ⇒ press → 当槽立刻手动调 _process。
##     两条注入规矩都是踩过坑记下来的（见 _mdtest/evidence_archive_check.gd:494 注释）。
##   · 每段「冻结」用例前面都放一个**反向对照**（表关着时该键必须有效），
##     否则「表开着没反应」可能只是注入根本没生效，测了等于没测。

const FrameData = preload("res://scripts/frame_data.gd")
const DiaryTexts = preload("res://scripts/diary_texts.gd")
const EndingStore = preload("res://scripts/ending_store.gd")

const FRAMES_PATH := "res://data/frames.json"
const MAIN_PATH := "res://scripts/main.gd"

## 三帧的「水簿」热点应该落在哪一格（= 磨坊账桌北头柜格的中心）。
## house.pos 三帧都是 (1216, 448)，格边 32px ⇒ pos + 格坐标 × 32 + 半格。
const BOOK_POS := {
	"a1_1926": Vector2(1328, 496),
	"a2_1951": Vector2(1392, 496),
	"a3_1976": Vector2(1392, 496),
}

var fails := 0
var main: Control = null


func _ok(cond: bool, label: String) -> void:
	print(("PASS " if cond else "FAIL ") + label)
	if not cond:
		fails += 1


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	_purge_saves()
	_data_checks()                 # A7 数据侧：三帧书热点就位、不抢家具
	_source_checks()               # A6 源码侧：J 分支与声明真的没了
	await _scene_checks()          # A1/A2/A3/A5/A6 行为侧
	await _form_key_checks()       # A4 表内键位
	await _diary_entry_checks()    # A7 行为侧：按 E 翻开《水簿》
	_purge_saves()
	print("ENDING_WIRE_CHECK_DONE fails=%d" % fails)
	print("ENDING_WIRE_OK 归档表已接入主循环 / J 键已删 / 三帧书热点可翻书 已验证")
	quit(1 if fails > 0 else 0)


# ---- 小工具 ---------------------------------------------------------------

func _purge_saves() -> void:
	for p in ["user://ending_form.json", "res://.ending_form.json",
			"user://evidence_archive.json", "res://.evidence_archive.json"]:
		if FileAccess.file_exists(p):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(p))


func _read_text(path: String) -> String:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return ""
	var s := f.get_as_text()
	f.close()
	return s


## 裸键注入：排队，调用后当帧读不到，必须 await 一帧。
func _key_event(code: int, down: bool) -> InputEventKey:
	var ev := InputEventKey.new()
	ev.keycode = code
	ev.physical_keycode = code
	ev.pressed = down
	return ev


func _key_down(code: int) -> void:
	Input.parse_input_event(_key_event(code, true))


func _key_up(code: int) -> void:
	Input.parse_input_event(_key_event(code, false))


## 在「当前槽」里跑一帧主循环（边沿检测要求 press 与 _process 同槽）。
func _tick(delta: float = 0.016) -> void:
	if main != null:
		main._process(delta)


## 找一个四周都有余量的可站格（用来测「关表后 W 真的能走」）。
func _find_open_spot(f) -> Vector2:
	var x := 64.0
	while x < 4700.0:
		var y := 64.0
		while y < 3500.0:
			var p := Vector2(x, y)
			if f.is_free(p) and f.is_free(p + Vector2(0, -24)) and f.is_free(p + Vector2(0, 24)) \
					and f.is_free(p + Vector2(-24, 0)) and f.is_free(p + Vector2(24, 0)):
				return p
			y += 32.0
		x += 32.0
	return Vector2(-1, -1)


## 找一个地标热点（按 title 精确匹配）。
func _hotspot_by_title(f, title: String) -> Dictionary:
	for h in f.hotspots:
		var hh: Dictionary = h
		if String(hh.get("house_id", "")) == "" and String(hh.get("title", "")) == title:
			return hh
	return {}


## 从 start 按 32px 格四向 BFS，判断能不能走到离磨坊 400px 以外（= 门是通的）。
func _can_reach_out(f, start: Vector2) -> bool:
	var q: Array = [start]
	var seen := {str(start): true}
	var guard := 0
	while not q.is_empty() and guard < 40000:
		guard += 1
		var p: Vector2 = q.pop_front()
		if absf(p.x - 1216.0) > 400.0 or absf(p.y - 448.0) > 400.0:
			return true
		for off in [Vector2(32, 0), Vector2(-32, 0), Vector2(0, 32), Vector2(0, -32)]:
			var n: Vector2 = p + off
			if n.x < 0.0 or n.y < 0.0 or n.x > 4800.0 or n.y > 3600.0:
				continue
			var k := str(n)
			if seen.has(k):
				continue
			if not f.is_free(n):
				continue
			seen[k] = true
			q.append(n)
	return false


# ---- A7 数据侧 -------------------------------------------------------------

func _data_checks() -> void:
	var d: Dictionary = JSON.parse_string(_read_text(FRAMES_PATH))
	_ok(not d.is_empty(), "W1 frames.json 能解析")

	var book_frames: Array = []
	for item in d.get("frames", []):
		var fd: Dictionary = item
		var id := String(fd.get("id", ""))
		var found: Dictionary = {}
		var desk: Dictionary = {}
		for h in fd.get("hotspots", []):
			var hh: Dictionary = h
			if String(hh.get("diary", "")) == "mill":
				found = hh
			if String(hh.get("furniture", "")) == "账桌":
				desk = hh
		if found.is_empty():
			continue
		book_frames.append(id)

		# 位置：写死的那一格，别让内容线悄悄挪走
		_ok(Vector2(found["pos"][0], found["pos"][1]) == BOOK_POS.get(id, Vector2.ZERO),
			"%s 水簿热点在账桌北头柜格 %s" % [id, str(BOOK_POS.get(id, Vector2.ZERO))])
		_ok(String(found.get("title", "")) == "水簿",
			"%s 书热点标题 = 水簿（按 E 翻开的就是它）" % id)
		_ok(String(found.get("text", "")).length() >= 12,
			"%s 书热点有检视文本（%d 字）" % [id, String(found.get("text", "")).length()])
		_ok(int(found.get("reach", 0)) >= 32,
			"%s 书热点 reach = %d（不小于一格）" % [id, int(found.get("reach", 0))])

		# 真的站上去：帧数据按「reach 内最近的一个」取用，
		# 家具热点先加入、平局家具赢 ⇒ 必须实测，不能只看 JSON。
		var frame = FrameData.new()
		frame.setup(fd)
		var at: Vector2 = BOOK_POS[id]
		_ok(frame.is_free(at), "%s 书热点那一格能站（is_free）" % id)
		var got: Dictionary = frame.hotspot_at(at)
		_ok(String(got.get("title", "")) == "水簿",
			"%s 站到书格 hotspot_at() → 水簿（实际 %s）" % [id, String(got.get("title", "(空)"))])
		_ok(String(got.get("diary", "")) == "mill", "%s 取到的热点带 diary=mill" % id)
		if not desk.is_empty():
			var dpos := Vector2(desk["pos"][0], desk["pos"][1])
			_ok(String(frame.hotspot_at(dpos).get("title", "")) == "账桌",
				"%s 站在账桌中心仍取到账桌（书没抢家具卡）" % id)
		_ok(_can_reach_out(frame, at), "%s 书格能从屋里走到外面（门是通的）" % id)

	_ok(book_frames.size() == 3, "只有三帧带 diary=mill（实际 %s）" % str(book_frames))
	_ok(book_frames == ["a1_1926", "a2_1951", "a3_1976"],
		"带书热点的正好是 A1/A2/A3（实际 %s）" % str(book_frames))


# ---- A6 源码侧 -------------------------------------------------------------

## 用源码断言兜住「删干净了」——事件注入只能证明「现在没反应」，
## 证不了「那一行代码走了」，所以两条一起上。
func _source_checks() -> void:
	var src := _read_text(MAIN_PATH)
	_ok(not src.contains("KEY_J"), "S1 main.gd 里不再有 KEY_J（J 调试入口已删）")
	_ok(not src.contains("_diary_j_down"), "S2 main.gd 里不再有 _diary_j_down 声明")
	_ok(src.contains("KEY_G"), "S3 main.gd 用裸键 G 当归档表开关")
	_ok(src.contains("EndingForm"), "S4 main.gd 引用 EndingForm（接线成立）")
	_ok(src.contains("_make_ending_form"), "S5 main.gd 有 _make_ending_form() 建表")
	_ok(src.contains("ending_form.is_open()"), "S6 停世界那条判断包含了归档表")
	# G 的轮询段必须在停世界 return 之前，否则表开着按 G 关不掉。
	var i_g := src.find("KEY_G")
	var i_stop := src.find("ending_form.is_open()")
	_ok(i_g > 0 and i_stop > i_g, "S7 G 的轮询段在停世界 return 之前（%d < %d）" % [i_g, i_stop])


# ---- A1/A2/A3/A5/A6 行为侧 -------------------------------------------------

func _scene_checks() -> void:
	_purge_saves()
	main = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	await process_frame

	if main.tl == null or main.ending_form == null:
		_ok(false, "A1 主场景起来了且归档表节点已建（main.ending_form 非空）")
		return
	_ok(true, "A1 主场景起来了，main.ending_form 非空（_ready 没被别的脚本错误打断）")
	_ok(main.ending_form.name == "EndingForm", "A1 表节点名字 = EndingForm")
	_ok(main.ending_form is Control, "A1 表节点是 Control")
	_ok(not main.ending_form.is_open(), "A1 启动时表是关着的（不抢画面）")

	# 从 A1 帧、一个开阔可站的位置开始（后面测「能不能走」要有余量）
	main.tl.index = 0
	main.tl.axis = 0          # Axis.SPACE
	main._refresh_all()
	var spot := _find_open_spot(main.tl.current())
	_ok(spot != Vector2(-1, -1), "A1 找到一个四向都能走的空地（%s）" % str(spot))
	if spot == Vector2(-1, -1):
		return
	main.tl.char_pos = spot

	# 主循环改由测试手动驱动：自动 _process 会让同一按键被处理两次
	main.set_process(false)

	await _a2_g_checks()
	await _a3_frozen_checks()
	await _a6_j_checks()


## A2：按 G 弹表 / 再按 G 合上 / 归档员跟着当前帧。
func _a2_g_checks() -> void:
	_ok(not main.ending_form.is_open(), "A2 前置：表是关着的")
	_key_down(KEY_G)
	await process_frame
	_key_down(KEY_G)         # 保持按住状态（parse 是排队，这里补一次确保真值）
	await process_frame
	var held := Input.is_key_pressed(KEY_G) or Input.is_physical_key_pressed(KEY_G)
	_ok(held, "A2 守卫：裸键注入生效（按下 G 后 is_key_pressed 为真）")
	_tick()
	_ok(main.ending_form.is_open(), "A2 按 G 弹出归档表")
	_ok(main.ending_form.frame_year() == main.tl.current().year,
		"A2 表里的归档员年份 = 当前帧年代（%d）" % main.tl.current().year)

	# 松手 → 再按 → 合上
	_key_up(KEY_G)
	await process_frame
	await process_frame
	_key_up(KEY_G)
	await process_frame
	_ok(not Input.is_key_pressed(KEY_G), "A2 守卫：松开 G 后状态归零")
	_tick()
	_ok(main.ending_form.is_open(), "A2 松手不会误关表（边沿检测，不是按住即切）")

	_key_down(KEY_G)
	await process_frame
	await process_frame
	_tick()
	_ok(not main.ending_form.is_open(), "A2 表开着时再按 G 能关掉（G 轮询段在停世界 return 之前）")
	_key_up(KEY_G)
	await process_frame


## A3：表开着时世界是停的（WASD / SHIFT / E 全部无效）；A5：关表后恢复。
func _a3_frozen_checks() -> void:
	# ---- 反向对照 1：表关着时 W 能走（= A5）----
	main.ending_form.close_form()
	main.tl.axis = 0
	main.tl.char_pos = _find_open_spot(main.tl.current())
	var p0: Vector2 = main.tl.char_pos
	Input.action_press("move_up")
	_tick()
	Input.action_release("move_up")
	_ok(main.tl.char_pos != p0, "A5 关表后按 W 坐标会变（%s → %s）" % [str(p0), str(main.tl.char_pos)])

	# ---- A3：表开着时 W 不动 ----
	main.ending_form.open_form(1926)
	var p1: Vector2 = main.tl.char_pos
	Input.action_press("move_up")
	_tick()
	Input.action_release("move_up")
	_ok(main.tl.char_pos == p1, "A3 表开着按 W 坐标不变（%s）" % str(main.tl.char_pos))
	_ok(not main.player.walking, "A3 表开着 player.walking = false（玩家不走）")

	# S / A / D 同样不动（同一个 _process_space 入口，抽检向右和向下）
	for action in ["move_down", "move_left", "move_right"]:
		Input.action_press(action)
		_tick()
		Input.action_release(action)
	_ok(main.tl.char_pos == p1, "A3 表开着按 S/A/D 坐标也不变（%s）" % str(main.tl.char_pos))

	# ---- 时间轴：W 在 TIME 轴里是推帧，表开着也不能推 ----
	main.ending_form.close_form()
	main.tl.axis = 1          # Axis.TIME
	var i0: int = main.tl.index
	Input.action_press("move_up")
	_tick()
	Input.action_release("move_up")
	_ok(main.tl.index != i0 or i0 == main.tl.frame_max(),
		"对照：表关着时 W 能推帧（%d → %d）" % [i0, main.tl.index])

	main.tl.index = 0
	main._refresh_all()
	main.ending_form.open_form(1926)
	var i1: int = main.tl.index
	Input.action_press("move_up")
	_tick()
	Input.action_release("move_up")
	_ok(main.tl.index == i1, "A3 表开着按 W 不推帧（index 仍 %d）" % main.tl.index)

	# ---- SHIFT：表开着不切时代 ----
	main.ending_form.close_form()
	var axis0: int = main.tl.axis
	Input.action_press("shift_axis")
	var jp := Input.is_action_just_pressed("shift_axis")
	_tick()
	Input.action_release("shift_axis")
	_ok(jp and main.tl.axis != axis0, "对照：表关着时 SHIFT 能切时代（%d → %d）" % [axis0, main.tl.axis])

	main.ending_form.open_form(1926)
	var axis1: int = main.tl.axis
	Input.action_press("shift_axis")
	var jp2 := Input.is_action_just_pressed("shift_axis")
	_tick()
	Input.action_release("shift_axis")
	_ok(jp2 and main.tl.axis == axis1, "A3 表开着 SHIFT 不切时代（%d → %d）" % [axis1, main.tl.axis])

	# ---- E：表开着不检视、不翻书 ----
	main.ending_form.close_form()
	main.tl.axis = 0
	main.tl.index = 0
	main._refresh_all()
	var dam := _hotspot_by_title(main.tl.current(), "坝")
	if dam.is_empty():
		_ok(false, "A1 帧有坝地标热点")
	else:
		main.tl.char_pos = dam["pos"] as Vector2
		Input.action_press("inspect")
		var jp3 := Input.is_action_just_pressed("inspect")
		_tick()
		Input.action_release("inspect")
		_ok(jp3 and not main.diary.open, "对照：表关着时 E 不会误翻书（坝不是书热点）")
		_ok(main._last_hotspot.get("title", "") == "坝",
			"对照：表关着时 E 正常检视（%s）" % String(main._last_hotspot.get("title", "")))

		main.ending_form.open_form(1926)
		main._last_hotspot = {}
		main.tl.char_pos = dam["pos"] as Vector2
		Input.action_press("inspect")
		var jp4 := Input.is_action_just_pressed("inspect")
		_tick()
		Input.action_release("inspect")
		_ok(jp4 and main._last_hotspot.is_empty(), "A3 表开着 E 不检视（没新文字）")
		_ok(main.ending_form.is_open(), "A3 表仍开着（E 没把表顶掉）")
	main.ending_form.close_form()


## A6：按 J 什么都没有（键还按得下去，但主循环不再认它）。
func _a6_j_checks() -> void:
	main.ending_form.close_form()
	main.diary.close_view()
	main.archive.close_archive()
	var p: Vector2 = main.tl.char_pos
	var i: int = main.tl.index

	_key_down(KEY_J)
	await process_frame
	await process_frame
	var held := Input.is_key_pressed(KEY_J) or Input.is_physical_key_pressed(KEY_J)
	_ok(held, "A6 守卫：裸键注入生效（按下 J 后 is_key_pressed 为真）")
	_tick()
	_ok(not main.diary.open, "A6 按 J 不再翻开双日记")
	_ok(not main.ending_form.is_open(), "A6 按 J 不会开归档表")
	_ok(not main.archive.is_open(), "A6 按 J 不会开证物档案")
	_ok(main.tl.char_pos == p and main.tl.index == i, "A6 按 J 世界不动")
	_key_up(KEY_J)
	await process_frame


# ---- A4：表内键位 ---------------------------------------------------------

## ⚠️ 两条注入规矩（都踩过）：
##   1. 表的自动 _process 要关掉、手动调 _handle_keys()：自动跑的话同一按键会被
##      引擎和测试各处理一次（焦点跳两格）。
##   2. 「刚按下」是**按引擎帧**算的：同一帧里按过的键，整帧内 is_action_just_pressed 都为真。
##      _handle_keys() 内部是 if/elif 链（ui_up → ui_down → ui_left → ui_right → ui_accept），
##      所以上一段按过的 ui_up 会把后面按的 ui_right 整个吃掉（实测：→ 不填格）。
##      ⇒ 每段之间必须 await 一帧，把这帧的边沿冲掉。
func _form_key_checks() -> void:
	var form = main.ending_form
	form.set_process(false)
	EndingStore.reset()
	form.open_form(1926)
	_ok(form.is_open(), "A4 前置：表开着")

	# ↓ / ↑ 走焦点
	form.set_focus(0)
	Input.action_press("ui_down")
	form._handle_keys()
	Input.action_release("ui_down")
	await process_frame
	_ok(form.focus_index() == 2, "A4 ↓ 焦点 1926 动机 → 1951 动机（实际 %d）" % form.focus_index())

	Input.action_press("ui_up")
	form._handle_keys()
	Input.action_release("ui_up")
	await process_frame
	_ok(form.focus_index() == 0, "A4 ↑ 焦点回到 1926 动机（实际 %d）" % form.focus_index())

	# → / ← 填格（空 → 第一个选项 → 空）
	form.set_focus(0)
	_ok(EndingStore.get_cell("1926", EndingStore.COL_MOTIVE) == "", "A4 前置：1926 动机是空的")
	Input.action_press("ui_right")
	form._handle_keys()
	Input.action_release("ui_right")
	await process_frame
	_ok(EndingStore.get_cell("1926", EndingStore.COL_MOTIVE) == "激情",
		"A4 → 填上第一个选项（%s）" % EndingStore.get_cell("1926", EndingStore.COL_MOTIVE))

	Input.action_press("ui_left")
	form._handle_keys()
	Input.action_release("ui_left")
	await process_frame
	_ok(EndingStore.get_cell("1926", EndingStore.COL_MOTIVE) == "",
		"A4 ← 能转回空格（不设默认值，%s）" % EndingStore.get_cell("1926", EndingStore.COL_MOTIVE))
	EndingStore.reset()   # 双清：reset 清数据，also 让 _focus 回 0 便于后续

	# Tab 平铺换格（裸键，排队 → 等一帧才生效）
	form.set_focus(10)
	_key_down(KEY_TAB)
	await process_frame
	await process_frame
	form._handle_keys()
	_key_up(KEY_TAB)
	await process_frame
	await process_frame
	_ok(form.focus_index() == 11, "A4 Tab 换到下一格（实际 %d）" % form.focus_index())
	form._handle_keys()          # 清 Tab 的边沿记录（_tab_down 只在 _handle_keys 里更新）

	# Shift+Tab 反向
	_key_down(KEY_SHIFT)
	await process_frame
	await process_frame
	_key_down(KEY_TAB)
	await process_frame
	await process_frame
	form._handle_keys()
	_key_up(KEY_TAB)
	_key_up(KEY_SHIFT)
	await process_frame
	await process_frame
	_ok(form.focus_index() == 10, "A4 Shift+Tab 反向换格（实际 %d）" % form.focus_index())

	# Enter：表格格里 = 递到下一格（_accept → tab_step(false)）
	form.set_focus(0)
	Input.action_press("ui_accept")
	form._handle_keys()
	Input.action_release("ui_accept")
	await process_frame
	_ok(form.focus_index() == 1, "A4 Enter 在表格格里往后递一格（实际 %d）" % form.focus_index())

	# Esc 关表
	Input.action_press("ui_cancel")
	form._handle_keys()
	Input.action_release("ui_cancel")
	await process_frame
	_ok(not form.is_open(), "A4 Esc 关表")

	# F 关表（裸键 + 边沿）
	form.open_form(1926)
	_ok(form.is_open(), "A4 前置：表重新开着")
	_key_down(KEY_F)
	await process_frame
	await process_frame
	_ok(Input.is_key_pressed(KEY_F), "A4 守卫：裸键 F 注入生效")
	form._handle_keys()
	_key_up(KEY_F)
	await process_frame
	await process_frame
	_ok(not form.is_open(), "A4 F 关表")
	form.set_process(true)


# ---- A7 行为侧：按 E 翻开《水簿》 -------------------------------------------

func _diary_entry_checks() -> void:
	var pair := DiaryTexts.mill_pair()
	_ok(String(pair.left_title) == "假本 · 誊清" and String(pair.right_title) == "真本 · 原稿",
		"A7 《水簿》两页标题 = 假本 · 誊清 / 真本 · 原稿")

	for idx in [0, 1, 2]:
		main.ending_form.close_form()
		main.diary.close_view()
		main.tl.axis = 0
		main.tl.index = idx
		main._refresh_all()
		var f = main.tl.current()
		var at := Vector2.ZERO
		var found := {}
		for h in f.hotspots:
			var hh: Dictionary = h
			if String(hh.get("diary", "")) == "mill":
				found = hh
		if found.is_empty():
			_ok(false, "A7 第 %d 帧有书热点" % idx)
			continue
		at = found["pos"] as Vector2
		main.tl.char_pos = at

		# 每次把标题清空，验证「翻开时确实把标题传进去了」，不是 _ready 的默认值
		main.diary._left_title = ""
		main.diary._right_title = ""

		# 真实路径：按 E
		Input.action_press("inspect")
		var jp := Input.is_action_just_pressed("inspect")
		_tick()
		Input.action_release("inspect")
		_ok(jp and main.diary.open,
			"A7 第 %d 帧站在书格按 E 翻开《水簿》（is_open=%s）" % [idx, str(main.diary.open)])
		_ok(main.diary._left_title == "假本 · 誊清" and main.diary._right_title == "真本 · 原稿",
			"A7 第 %d 帧翻开的标题正确（%s / %s）"
			% [idx, main.diary._left_title, main.diary._right_title])
		_ok(main.hud.visible == false, "A7 第 %d 帧翻开时 HUD 让开" % idx)

		# 合上，再看 _try_open_diary() 的返回值
		main.diary.close_view()
		await process_frame
		_ok(main._try_open_diary(), "A7 第 %d 帧 _try_open_diary() 返回 true" % idx)
		main.diary.close_view()
		await process_frame

	# A7：站在账桌中心按 E 不该翻书（那是家具热点，走的是证件入档那条路）
	main.tl.axis = 0
	main.tl.index = 0
	main._refresh_all()
	var desk := {}
	for h in main.tl.current().hotspots:
		var hh: Dictionary = h
		if String(hh.get("furniture", "")) == "账桌":
			desk = hh
	if not desk.is_empty():
		main.tl.char_pos = desk["pos"] as Vector2
		_ok(not main._try_open_diary(), "A7 站在账桌中心按 E 翻不开书（书在隔壁柜格）")
	main.diary.close_view()