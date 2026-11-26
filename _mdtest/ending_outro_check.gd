extends SceneTree

## 结局收束自检（L19 线：落定出口 → 黑幕 + 三行字 → 任意键 → 淡回自由探索）。
##
## 跑法：
##   headless（逻辑侧 O2/O3/O5/O6，画面部分记 SKIP）
##     godot --headless --path . -s res://_mdtest/ending_outro_check.gd
##   窗口（O1/O4 真的取帧采样 + 存 PNG，lab/_l19_outro_o1_black.png 等）
##     godot --path . -s res://_mdtest/ending_outro_check.gd
##
## 口径说明（为什么这样测）：
##   · 归档表本体（填格 / 三变体 / 出口）已由 _mdtest/ending_check.gd 的 E1–E14 覆盖，
##     接线由 _mdtest/ending_wire_check.gd 覆盖。这里只测「落定之后那 2 秒」。
##   · 收束层自己不吞帧率：本脚本 play() 之后立刻 set_process(false)，
##     用 _advance() 手动推时间轴 —— 否则真实帧率会让「1s 内」「0.8s」这类断言飘。
##     「引擎真的在推进它」另有一条单独断言（黑幕自己会开始升）。
##   · 世界全停是两层：main.gd 的停世界条件（§5.5，本脚本用 _tick() 直接调
##     main._process 绕过暂停来验）+ 收束层自己暂停 SceneTree（验 can_process）。
##     两层分开断言，坏哪层都能看出来。
##   · O1/O4 必须真取帧（--headless 无帧缓冲）⇒ headless 跑时记 SKIP 而不是 FAIL。

const EndingStore = preload("res://scripts/ending_store.gd")

const SHOT_BASE := "res://lab/_l19_outro_o0_base.png"
const SHOT_BLACK := "res://lab/_l19_outro_o1_black.png"
const SHOT_CLEAR := "res://lab/_l19_outro_o4_clear.png"

## 三行字：第 2 行的字数上限（与 ending_outro.gd 的 TEXT_MAX 一致）。
const TEXT_MAX := 60
const HINT := "—— 按任意键 ——"

var fails := 0
var checks := 0
var headless := false
var main: Control = null
var outro: Control = null


func _ok(cond: bool, label: String) -> void:
	checks += 1
	print(("PASS " if cond else "FAIL ") + label)
	if not cond:
		fails += 1


func _skip(label: String) -> void:
	print("SKIP " + label)


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	headless = DisplayServer.get_name() == "headless"
	print("ENDING_OUTRO_CHECK mode=%s" % ("headless" if headless else "window"))
	_purge_saves()
	await _boot()
	_wiring_checks()
	await _pixel_checks()      # O1 / O4（窗口模式真跑）
	await _timing_checks()     # O1b 实机时长（引擎自己推进，不用手动驱动）
	await _frozen_checks()     # O3
	await _variant_checks()    # O2（甲 / 乙 / 丙 各一遍 + 允许再来一次）
	_save_checks()             # O6
	await _reopen_checks()     # O5
	paused = false             # 兜底：别把树留在暂停态拖死后续流程
	_purge_saves()
	print("ENDING_OUTRO_CHECK_DONE fails=%d checks=%d" % [fails, checks])
	if fails == 0:
		print("ENDING_OUTRO_OK 落定出口后收束层上场 / 三行字取自记述正文 / 世界全停 / 任意键淡回 已验证")
	else:
		print("ENDING_OUTRO_FAILED 见上面 FAIL 行")
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


## 按一下再松开（两个事件都排队）。
func _key(code: int) -> void:
	Input.parse_input_event(_key_event(code, true))
	Input.parse_input_event(_key_event(code, false))


## 在「当前槽」里跑一帧主循环（边沿检测要求 press 与 _process 同槽）。
func _tick(delta: float = 0.016) -> void:
	if main != null:
		main._process(delta)


## 找一个四周都有余量的可站格（用来测「没在收束时 W 真的能走」）。
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


## 取一帧画面（窗口模式；headless 下拿不到有效帧缓冲）。
func _shot(path: String) -> Image:
	await RenderingServer.frame_post_draw
	var img: Image = root.get_texture().get_image()
	if path != "":
		DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://lab"))
		img.save_png(ProjectSettings.globalize_path(path))
	return img


## 画面正中央那块的亮度（0~1）。取块而不是单像素：单像素会被一条线/一个斑点骗。
func _center_brightness(img: Image) -> float:
	var w := img.get_width()
	var h := img.get_height()
	var x0 := int(w * 0.40)
	var x1 := int(w * 0.60)
	var y0 := int(h * 0.40)
	var y1 := int(h * 0.60)
	var acc := 0.0
	var n := 0
	for y in range(y0, y1, 4):
		for x in range(x0, x1, 4):
			var c := img.get_pixel(x, y)
			acc += 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b
			n += 1
	return acc / float(maxi(n, 1))


## 落定出口（表必须先开）。play() 之后立刻关掉引擎推进，改由 _drive_* 手动推。
func _settle(exit_i: int = 0) -> bool:
	if main == null or main.ending_form == null or outro == null:
		return false
	main.ending_form.open_form(2026)
	var ok: bool = main.ending_form.commit_exit(exit_i)
	outro.set_process(false)
	return ok


## 手动推到「黑幕铺满、字全亮、等按键」。
func _drive_in() -> void:
	var guard := 0
	while outro.phase_name() == "in" and guard < 400:
		outro._advance(0.05)
		guard += 1


## 手动推到收束结束（wait 阶段会自动 dismiss）。
func _drive_through() -> void:
	var guard := 0
	while outro.is_playing() and guard < 600:
		guard += 1
		if outro.phase_name() == "wait":
			outro.dismiss()
		outro._advance(0.05)


## 填一份「甲」变体的完整表（照抄 _mdtest/ending_check.gd 的 _fill_canonical）。
func _fill_canonical() -> void:
	EndingStore.set_cell("1926", EndingStore.COL_MOTIVE, "放任")
	EndingStore.set_cell("1926", EndingStore.COL_INTENT, "间接故意")
	EndingStore.set_cell("1951", EndingStore.COL_MOTIVE, "蓄谋")
	EndingStore.set_cell("1951", EndingStore.COL_INTENT, "直接故意")
	EndingStore.set_cell("1976", EndingStore.COL_MOTIVE, "蓄谋")
	EndingStore.set_cell("1976", EndingStore.COL_INTENT, "直接故意")
	EndingStore.set_cell("2001", EndingStore.COL_MOTIVE, "蓄谋")
	EndingStore.set_cell("2001", EndingStore.COL_INTENT, "无")
	EndingStore.set_cell("2026", EndingStore.COL_MOTIVE, "无")
	EndingStore.set_cell("2026", EndingStore.COL_INTENT, "无")
	EndingStore.set_radio("case_1951", "债务纠纷")
	EndingStore.set_radio("earliest", "1951")
	EndingStore.set_radio("burial", "补丁下")
	EndingStore.set_radio("count", "二")


## 收束第 2 行必须原样来自这份记述的正文（截断尾巴的「…」先摘掉再比）。
func _body_contains(rep: Dictionary, line: String) -> bool:
	var body := String(rep.get("body", ""))
	if body.is_empty():
		body = "\n".join(PackedStringArray(rep.get("lines", [])))
	var core := line
	if core.ends_with("…"):
		core = core.substr(0, core.length() - 1)
	if core.length() < 4:
		return false
	return body.contains(core)


# ---- 起场景 ---------------------------------------------------------------

func _boot() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	await process_frame
	outro = main.get_node_or_null("EndingOutro")
	# 关掉 open_form() 第一次会做的 EndingStore.load()：本脚本每一段都自己摆状态，
	# 不能再让「上一段（或上一轮）留在 user:// 里的存档」冲进来。
	main.ending_form.set("_loaded", true)
	main.tl.index = 0
	main.tl.axis = 0        # Axis.SPACE
	main._refresh_all()
	var spot := _find_open_spot(main.tl.current())
	if spot != Vector2(-1, -1):
		main.tl.char_pos = spot
	# 主循环改由测试手动驱动：自动 _process 会让同一按键被处理两次
	main.set_process(false)


# ---- O0：接线 -------------------------------------------------------------

func _wiring_checks() -> void:
	_ok(main != null and main.tl != null, "O0 主场景起来了")
	if main == null:
		return
	_ok(outro != null, "O0 _make_outro() 建了收束层（main.outro 非空）")
	if outro == null:
		return
	_ok(outro is Control, "O0 收束层是 Control")
	_ok(outro.name == "EndingOutro", "O0 收束层节点名 = EndingOutro")
	_ok(main.get_child(main.get_child_count() - 1) == outro,
			"O0 收束层是 Main 的最后一个孩子（画在归档表 / HUD 上面）")
	_ok(outro.phase_name() == "idle" and not outro.is_playing(), "O0 启动时收束层是空的（不抢画面）")

	# exit_chosen 必须真的连到这层（全仓库在这之前零监听者）
	var connected := false
	for c in main.ending_form.exit_chosen.get_connections():
		var d: Dictionary = c
		if d.get("callable") is Callable and (d["callable"] as Callable).get_object() == outro:
			connected = String((d["callable"] as Callable).get_method()) == "play"
			break
	_ok(connected, "O0 ending_form.exit_chosen 连着收束层的 play()")

	# 认不出的出口不许放黑幕（宁可不演，也不要一块没人解释的黑屏）
	_ok(not outro.play("胡编的出口") and not outro.is_playing(),
			"O0 认不出的出口字不放黑幕（play() 返回 false 且状态不变）")


# ---- O1 / O4：黑幕真的盖上了、真的退了 ------------------------------------

func _pixel_checks() -> void:
	if headless:
		_skip("O1 落定后 1s 内黑幕出现（中心像素亮度降 ≥50%）—— headless 无帧缓冲，跑窗口模式验")
		_skip("O4 按键后黑幕消失（中心像素回 ±10%）—— headless 无帧缓冲，跑窗口模式验")
		return

	# 反向对照：先按 W 真的走一步（顺便让画面进入稳定状态）
	main.ending_form.close_form()
	main.tl.axis = 0
	main.tl.char_pos = _find_open_spot(main.tl.current())
	var pm: Vector2 = main.tl.char_pos
	Input.action_press("move_up")
	_tick()
	Input.action_release("move_up")
	_ok(main.tl.char_pos != pm, "O1 前置：收束层没在播时按 W 坐标会变（画面在动，采样才有意义）")

	for _i in range(15):
		await process_frame
	var img0: Image = await _shot(SHOT_BASE)
	_ok(img0 != null and img0.get_width() > 0, "O1 前置：截到基准帧（%dx%d）" % [img0.get_width(), img0.get_height()])
	var b0 := _center_brightness(img0)
	_ok(b0 > 0.02, "O1 前置：基准帧中心不是全黑（亮度 %.3f）" % b0)

	main.ending_form.open_form(2026)
	_ok(main.ending_form.commit_exit(0), "O1 前置：在表里落定「已归档」")
	# 先让引擎自己跑两帧：证明收束层的 _process 在**暂停的树里**也照常被派发
	# （process_mode = ALWAYS）。之后才关掉自动推进，改成手动推，免得帧率把时长拖飘。
	await process_frame
	await process_frame
	_ok(outro.black_level() > 0.0, "O1 收束层确实在被引擎推进（暂停的树里黑幕已开始升，%.3f）" % outro.black_level())
	outro.set_process(false)
	_drive_in()
	_ok(outro.phase_name() == "wait" and outro.black_level() >= 0.80,
			"O1 落定后 1s 内黑幕铺满（alpha=%.2f）" % outro.black_level())
	var img1: Image = await _shot(SHOT_BLACK)
	var b1 := _center_brightness(img1)
	var drop := 0.0 if b0 <= 0.0 else (b0 - b1) / b0
	_ok(drop >= 0.5, "O1 中心亮度 %.3f → %.3f（降 %.0f%%，要求 ≥50%%）· %s" % [b0, b1, drop * 100.0, SHOT_BLACK])

	# O4：按任意键（这里用 Esc）→ 淡出 → 画面恢复
	_key(KEY_ESCAPE)
	await process_frame
	await process_frame
	var key_took: bool = String(outro.phase_name()) == "out"
	if not key_took:
		outro.dismiss()           # 按键没被收下也要把流程跑完，免得后面全红
	_ok(key_took, "O4 按任意键（Esc）收掉黑幕（进入淡出）")
	_drive_through()
	_ok(not outro.is_playing() and outro.phase_name() == "idle", "O4 淡出结束后收束层回到 idle")
	var img2: Image = await _shot(SHOT_CLEAR)
	var b2 := _center_brightness(img2)
	var tol := b0 * 0.10
	_ok(absf(b2 - b0) <= tol, "O4 黑幕消失：中心亮度回到 %.3f（基准 %.3f，容差 ±10%%）· %s" % [b2, b0, SHOT_CLEAR])


# ---- O1b：实机时长（引擎自己推进，不手动驱动） ----------------------------

## 上面 O1/O4 是手动推的，只证明「推完的画面对」；这里让引擎按真实帧率自己跑，
## 证明两个常量（FADE_IN=0.8 / FADE_OUT=1.0）在真机上真的是这个时长。
func _timing_checks() -> void:
	if headless:
		_skip("O1b 实机时长（黑幕 800ms / 淡出 1000ms）—— headless 帧率不受控")
		return
	main.ending_form.open_form(2026)
	var t0 := Time.get_ticks_msec()
	main.ending_form.commit_exit(0)
	var guard := 0
	while String(outro.phase_name()) != "wait" and guard < 900:
		await process_frame
		guard += 1
	var in_ms := Time.get_ticks_msec() - t0
	_ok(in_ms >= 600 and in_ms <= 1300, "O1b 黑幕铺满实测 %d ms（设计 800ms）" % in_ms)
	_ok(outro.black_level() >= 0.80, "O1b 铺满时 alpha = %.2f" % outro.black_level())

	_key(KEY_SPACE)
	await process_frame
	await process_frame
	var t1 := Time.get_ticks_msec()
	var guard2 := 0
	while outro.is_playing() and guard2 < 900:
		await process_frame
		guard2 += 1
	var out_ms := Time.get_ticks_msec() - t1
	_ok(out_ms >= 800 and out_ms <= 1700, "O1b 淡出实测 %d ms（设计 1000ms）" % out_ms)
	_ok(not paused and not outro.is_playing(), "O1b 收束走完：树已恢复、层回 idle")


# ---- O3：收束期间世界全停 ------------------------------------------------

func _frozen_checks() -> void:
	# ---- 反向对照：收束层没在播时 W 有效 ----
	main.ending_form.close_form()
	main.tl.axis = 0
	main.tl.char_pos = _find_open_spot(main.tl.current())
	var p0: Vector2 = main.tl.char_pos
	Input.action_press("move_up")
	_tick()
	Input.action_release("move_up")
	_ok(main.tl.char_pos != p0, "O3 前置：收束层没在播时按 W 坐标会变（%s → %s）" % [str(p0), str(main.tl.char_pos)])

	# ---- 收束期间：主循环就算被硬调也不许动 ----
	_ok(_settle(1), "O3 前置：在表里落定「存疑」")
	var p1: Vector2 = main.tl.char_pos
	Input.action_press("move_up")
	for _i in range(3):
		_tick()
	Input.action_release("move_up")
	_ok(not main.player.walking, "O3 收束期间 player.walking = false（玩家不走）")
	_ok(main.tl.char_pos == p1, "O3 收束期间按 W 坐标不变（%s）" % str(main.tl.char_pos))
	_ok(paused, "O3 收束期间整棵树被暂停（G / I / F11 的轮询段全在停世界 return 之前，只能靠暂停挡）")
	_ok(not main.can_process(), "O3 收束期间主循环不在引擎的派发名单里（can_process = false）")

	_drive_through()
	_ok(not paused, "O3 收束结束后暂停被解开（不会把游戏卡死）")


# ---- O2：三行字取自记述正文（三个变体各一遍） ------------------------------

func _variant_checks() -> void:
	var cases := [
		{"name": "甲", "case": "债务纠纷", "count": "二", "exit_i": 0},
		{"name": "乙", "case": "杀人灭口", "count": "二", "exit_i": 0},
		{"name": "丙", "case": "债务纠纷", "count": "无法确定", "exit_i": 1},
	]
	for c in cases:
		var cc: Dictionary = c
		var tag := String(cc["name"])
		EndingStore.reset()
		_fill_canonical()
		EndingStore.set_radio("case_1951", String(cc["case"]))
		EndingStore.set_radio("count", String(cc["count"]))
		EndingStore.save()
		main.ending_form.open_form(2026)
		var rep: Dictionary = main.ending_form.report_now()
		_ok(String(rep.get("variant", "")) == tag, "O2[%s] 记述确实落在这个变体（build 回了「%s」）" % [tag, String(rep.get("variant", ""))])

		var want := String(EndingStore.EXITS[int(cc["exit_i"])])
		_ok(_settle(int(cc["exit_i"])), "O2[%s] 落定出口「%s」成功" % [tag, want])
		var rep2: Dictionary = main.ending_form.report_now()
		_ok(outro.is_playing() and outro.phase_name() == "in", "O2[%s] 落定出口后收束层立刻上场" % tag)
		_ok(not main.ending_form.is_open(), "O2[%s] 收束开始时归档表已经被收掉（不叠在画面里）" % tag)

		var l: Array = outro.lines()
		_ok(String(l[0]) == want, "O2[%s] 第 1 行 = 选的那个出口（「%s」）" % [tag, String(l[0])])
		var body_line := String(l[1])
		_ok(not body_line.is_empty() and body_line.length() <= TEXT_MAX,
				"O2[%s] 第 2 行非空且不超过 %d 字（%d 字）" % [tag, TEXT_MAX, body_line.length()])
		_ok(_body_contains(rep2, body_line),
				"O2[%s] 第 2 行原样来自该变体正文（「%s」）" % [tag, body_line])
		_ok(String(l[2]) == HINT, "O2[%s] 第 3 行 = 提示行（「%s」）" % [tag, HINT])

		_drive_through()
		_ok(not outro.is_playing(), "O2[%s] 收束能自己走完（淡出后回到 idle）" % tag)

	# §3.6：同一次落定只收一次（收束中再触发不许重入）
	_ok(_settle(0), "O2 前置：再落定一次，验证能不能再来一遍")
	_ok(not outro.play("已归档"), "O2 收束中再触发 play() 被拒（一次落定只收一次）")
	_ok(outro.is_playing(), "O2 被拒的那次不会打断正在放的收束")
	_drive_through()


# ---- O6：落定真的有落盘 --------------------------------------------------

## 存档落点的两个候选（= ending_store.gd 的 SAVE_CANDIDATES）。
## ⚠️ 本机 user:// 是只读的（沙箱），save() 会自己回退到 res://.ending_form.json，
##    所以这里两条都读、看**哪一条变了**，不写死 user:// —— 正常机器上变的是 user://。
func _save_pair() -> Array:
	return [_read_text("user://ending_form.json"), _read_text("res://.ending_form.json")]


func _save_checks() -> void:
	for p in ["user://ending_form.json", "res://.ending_form.json"]:
		if FileAccess.file_exists(p):
			print("NOTE O6 存档候选 %s 可读（%d 字节）" % [p, _read_text(p).length()])
	EndingStore.reset()
	_fill_canonical()
	EndingStore.save()
	var before: Array = _save_pair()
	_ok(String(before[0]).length() > 0 or String(before[1]).length() > 0,
			"O6 收束前存档存在（user=%d 字节 / res=%d 字节）" % [String(before[0]).length(), String(before[1]).length()])

	_ok(_settle(0), "O6 前置：落定「已归档」")
	_drive_through()
	var after: Array = _save_pair()
	_ok(String(after[0]).length() > 0 or String(after[1]).length() > 0,
			"O6 收束后存档仍存在（user=%d 字节 / res=%d 字节）" % [String(after[0]).length(), String(after[1]).length()])

	var changed := String(before[0]) != String(after[0]) or String(before[1]) != String(after[1])
	_ok(changed, "O6 收束前后存档内容不同（出口落定写进去了）")

	var hit := ""
	if String(before[1]) != String(after[1]) and String(after[1]).contains("已归档"):
		hit = "res://.ending_form.json"
	if String(before[0]) != String(after[0]) and String(after[0]).contains("已归档"):
		hit = "user://ending_form.json"
	_ok(not hit.is_empty(), "O6 变更的那份存档里带着刚落的出口字（已归档）· %s" % hit)
	_ok(EndingStore.get_exit() == "已归档", "O6 收束后 EndingStore.get_exit() = 已归档")


# ---- O5：收束之后归档表还能正常开关 -------------------------------

func _reopen_checks() -> void:
	_ok(not outro.is_playing(), "O5 收束已经结束（按钮后的状态是干净的）")
	main.ending_form.open_form(2026)
	_ok(main.ending_form.is_open(), "O5 收束之后按 G 的那条路还能把表打开（open_form）")
	main.ending_form.close_form()
	_ok(not main.ending_form.is_open(), "O5 打开之后还能关上")
	main.ending_form.toggle(2026)
	var opened: bool = main.ending_form.is_open()
	main.ending_form.toggle(2026)
	_ok(opened and not main.ending_form.is_open(), "O5 toggle 在这之后仍然正常翻转")
	# 再落定一次也必须还能正常收（§3.6 允许重开表再来一遍）
	_ok(_settle(1), "O5 收束之后能再落定一次")
	_drive_through()
	_ok(not outro.is_playing() and not paused, "O5 第二次收束也正常收场（层 idle、树未暂停）")