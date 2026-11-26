extends Control

## 主控：输入分发 + 双轴状态。
##
## 输入一律用轮询（Input.is_action_pressed）而不是 _unhandled_input 里的事件。
## 原因：键盘按住会自动重复，事件会被连续收到，一按 W 就可能直接冲到 A5。
## 轮询 + 自己做重复计时，才能精确控制「推一帧」的节奏。
##
## 复用 move_up / move_down 做时间推进（HANDOFF §2.5），
## 语义靠 axis 分派，不另建 time_forward / time_back。

const PLAYER_SPEED := 180.0    # L12/M6：120→180（×1.5，世界同步放大 1.5 倍 ⇒ 观感不突变）
const STEP_DELAY := 0.30      # 按住后多久开始自动重复
const STEP_INTERVAL := 0.13   # 自动重复的间隔

const Timeline = preload("res://scripts/timeline.gd")
const FrameData = preload("res://scripts/frame_data.gd")
const EvidenceStore = preload("res://scripts/evidence_store.gd")
const EvidenceArchive = preload("res://scripts/evidence_archive.gd")
const DiaryView = preload("res://scripts/diary_view.gd")
const DiaryTexts = preload("res://scripts/diary_texts.gd")
const EndingForm = preload("res://scripts/ending_form.gd")

# 五个年代的时间轴色偏：越往后越冷、越灰
const YEAR_TINTS: Array = [
	Color(1.12, 1.04, 0.86),   # 1926 暖黄
	Color(1.02, 1.00, 0.90),   # 1951 稍冷
	Color(0.94, 0.96, 0.86),   # 1976 病绿
	Color(0.90, 0.92, 0.94),   # 2001 灰蓝
	Color(0.98, 0.98, 1.02),   # 2026 中性
]

@onready var world: Control = $CameraRig/WorldView
@onready var player: Node2D = $CameraRig/Player
@onready var camera_rig: Node2D = $CameraRig
@onready var hud: Control = $HUD

@onready var display: Node = $DisplayManager

var tl: Timeline
var archive: Control = null          # 证物档案界面（代码动态建，挂 Main 下）
var _archive_i_down := false          # I 键边沿检测（轮询，不用事件）
var diary: Control = null            # 双日记对照界面（代码动态建，挂 Main 下）
var ending_form: Control = null      # 归档表（推理—结案，代码动态建，挂 Main 下）
var _ending_g_down := false          # G 键边沿检测（轮询，不用事件）

var _step_active := false    # 这一轮按住是否已经推过第一帧
var _repeating := false      # 是否已经进入连发阶段
var _hold_time := 0.0
var _phase_active := false   # 虚化位移的按住状态（A/D，边沿 + 连发）
var _phase_repeating := false
var _phase_hold := 0.0
var _last_hotspot: Dictionary = {}
var _f11_down := false       # F11 边沿检测（轮询，不用事件）


func _ready() -> void:
	tl = Timeline.new()
	if not tl.load_frames():
		push_error("帧表加载失败，游戏没法继续")
		return

	tl.axis_changed.connect(_on_axis_changed)
	tl.frame_changed.connect(_on_frame_changed)
	# house-spec §8.3：推时间不再被拒，改为「时代前进 + 卡墙虚化」。
	tl.out_of_range.connect(_on_out_of_range)
	tl.phasing_changed.connect(_on_phasing_changed)

	player.position = tl.char_pos
	camera_rig.setup_viewport(tl.world_size)
	# WorldView 是 Control 且挂在 Node2D（CameraRig）下：锚点不生效，必须显式给尺寸，
	# 否则 _draw 画在 0×0 上，整个场景看不到（只有玩家可见）。
	# set_deferred：等布局阶段结束后再设，避免「非对等锚点覆盖 size」WARNING。
	world.set_deferred("size", tl.world_size)
	camera_rig.set_target(tl.char_pos)
	# 玩家像素由 world_view 的 y-sort 循环画（DECIDE D4 方案 B）。
	# 这里只做注入：让 world_view 拿到节点引用，玩家状态靠 set_player_state() 每帧同步。
	world.set_player_ref(player)
	_make_archive()
	_make_diary()
	_make_ending_form()
	# 读回上次存档的证物（跨启动持久化）。读不到就当空档案。
	EvidenceStore.load()
	_refresh_all()


## 建证物档案界面：动态挂 Main 下（与 HUD 同层，建在 HUD 之后 → 画在 HUD 上面）。
## 不改 scenes/main.tscn 的结构。
func _make_archive() -> void:
	archive = EvidenceArchive.new()
	archive.name = "EvidenceArchive"
	add_child(archive)


## 建双日记界面：动态挂 Main 下（与档案同层，建在 HUD 之后 → 画在 HUD 上面）。
## 正常情况下在世界里按 E 翻开书本（见 _try_open_diary）：磨坊账房的「账桌北头
## 柜格」那一格在 data/frames.json 里带 `"diary": "mill"`（A1/A2/A3 三帧各一条）。
func _make_diary() -> void:
	diary = DiaryView.new()
	diary.name = "DiaryView"
	add_child(diary)
	# 入档时让档案闪一下「已收集」
	diary.set("archive_hook", archive)


## 建归档表界面：动态挂 Main 下（建在日记之后 → 画在最上面）。
## G 键开关（见 _process）。理由是这张表是跨时代卷宗，随时可翻、随时可填；
## 填不填得完只影响记述变体，不影响能不能开。
func _make_ending_form() -> void:
	ending_form = EndingForm.new()
	ending_form.name = "EndingForm"
	add_child(ending_form)


## 脚下那一格如果是一条「书」热点，就翻开它。返回是否翻开了。
## 契约：热点字典里加 `"diary": "<书 id>"`；现在只有 "mill"（《水簿》一对）。
func _try_open_diary() -> bool:
	if diary == null:
		return false
	var f: FrameData = tl.current()
	if f == null:
		return false
	var h: Dictionary = f.hotspot_at(tl.char_pos)
	if h.is_empty():
		return false
	if String(h.get("diary", "")) != "mill":
		return false
	var pair := DiaryTexts.mill_pair()
	diary.show_pair(String(pair.fake), String(pair.raw),
		String(pair.left_title), String(pair.right_title))
	# 「获取的时候复刻一份」：翻开这一刻就入档（同一年代只入一次）
	diary.collect_copy(f.year)
	diary.open_view()
	_set_hud_hidden(true)
	return true


## 档案开着的时候把 HUD 让开。
## ⚠️ 兄弟节点里 HUD 排在 archive 前面，档案面板只盖住中间一块，
## HUD 的顶栏（y<36）和检视卡（x=40 起）会露在面板边缘 —— 直接隐藏 HUD 更干净。
func _set_hud_hidden(hidden: bool) -> void:
	if hud == null:
		return
	if hud.visible == not hidden:
		return
	hud.visible = not hidden
	if not hidden:
		# 重新显示时把检视文字补回来（visible=false 期间 show_hotspot 的状态还在）
		hud.queue_redraw()


func _process(delta: float) -> void:
	if tl == null:
		return

	# F11 全屏：轮询 + 边沿检测（事件版收不到，见 display_manager.gd 注释）
	# 多路触发，任一可用即生效：
	#   1. project.godot 的 toggle_fullscreen action（物理键 F11）
	#   2. 裸键 is_key_pressed(KEY_F11)（不依赖 InputMap 是否重载）
	#   3. Alt+Enter（传统全屏快捷键，副作用是 F11 被别的程序占用时还有后路）
	# 编辑器里改过 project.godot 的输入映射后**必须重启编辑器**，InputMap 才会重新载入。
	var fs_now := false
	if InputMap.has_action("toggle_fullscreen") and Input.is_action_pressed("toggle_fullscreen"):
		fs_now = true
	elif Input.is_key_pressed(KEY_F11) or Input.is_physical_key_pressed(KEY_F11):
		fs_now = true
	elif Input.is_key_pressed(KEY_ENTER) and Input.is_key_pressed(KEY_ALT):
		fs_now = true
	if fs_now and not _f11_down and display != null:
		var before := DisplayServer.window_get_mode()
		display.toggle()
		var after := DisplayServer.window_get_mode()
		if after == before:
			# 引擎拒绝了切换。最常见原因：游戏被嵌在 Godot 编辑器里运行
			# （日志里会出现 "Embedded window only supports Windowed mode."）。
			# 这种情况下全屏在引擎层就被禁止，代码怎么改都没用。
			print("[全屏] 切换失败（mode 仍是 ", after, "）。若控制台出现 ",
				"'Embedded window only supports Windowed mode'，说明游戏跑在编辑器",
				"嵌入式窗口里 —— 请关掉嵌入，或用命令行启动游戏。")
		else:
			print("[全屏] 切换完成 → mode=", after, " size=", DisplayServer.window_get_size())
	_f11_down = fs_now

	# 证物档案：I 键开关（边沿检测 + 轮询，和 F11 同一套路子）。
	# 输入映射 archive 动作（project.godot，物理键 I）为主，裸键 KEY_I 兜底
	# （改了 project.godot 没重启编辑器时 InputMap 可能还是旧的）。
	var archive_now := false
	if InputMap.has_action("archive") and Input.is_action_pressed("archive"):
		archive_now = true
	elif Input.is_key_pressed(KEY_I) or Input.is_physical_key_pressed(KEY_I):
		archive_now = true
	if archive_now and not _archive_i_down and archive != null:
		archive.toggle()
	_archive_i_down = archive_now

	# 归档表：G 键开关（边沿检测 + 轮询，和 I / F11 同一套路子）。
	# 开表时传当前年代进去当「归档员」依据（归档员随帧，见 ending_report.gd）。
	# ⚠️ 这一段必须留在下面的停世界 return **之前**，否则表开着按 G 关不掉。
	var ending_now := Input.is_key_pressed(KEY_G) or Input.is_physical_key_pressed(KEY_G)
	if ending_now and not _ending_g_down and ending_form != null and tl.current() != null:
		ending_form.toggle(tl.current().year)
	_ending_g_down = ending_now

	# 档案 / 书本 / 归档表开着的时候，游戏逻辑全停（不响应行走 / 时间轴推帧 / SHIFT 切时代 / E 检视）。
	# ⚠️ SHIFT 与 E 的处理必须放在这个判断**之后** —— 开着档案时世界是停的，
	#    否则玩家能一边翻档案一边切时代、顺手把新年代证物也收了。
	# 书本的「合上」走 DiaryView._input（E / Esc），不吃这一段；
	# 归档表自己吃 ↑↓←→ / Tab / Enter / Esc / F（见 ending_form.gd 的 _handle_keys）。
	if (archive != null and archive.is_open()) or (diary != null and diary.is_open()) \
			or (ending_form != null and ending_form.is_open()):
		player.walking = false
		_set_hud_hidden(true)
		return
	_set_hud_hidden(false)

	# ↓↓↓ 开档时不响应的两个动作放在这里 ↓↓↓
	# SHIFT 切时代：档案开着就跳过（档案是跨时代卷宗，翻它不该动世界）。
	if Input.is_action_just_pressed("shift_axis"):
		tl.toggle_axis()

	# E：脚下有「书」就翻开（顺手入档一份副本），没有就照旧检视。
	# 书开着时到不了这里（上面那条 return 挡着）；合书由 DiaryView 自己吃 E，
	# just_closed() 防止同一次按键「合上又被立刻翻开」。
	if Input.is_action_just_pressed("inspect"):
		if diary != null and diary.just_closed():
			pass
		elif not _try_open_diary():
			_do_inspect()

	if tl.axis == Timeline.Axis.SPACE:
		_process_space(delta)
	else:
		_process_time(delta)

	player.position = tl.char_pos
	# 小地图每帧要玩家坐标（hud.sync 只在切帧/切轴时调，不够）。
	# 档案开着时 _process 在上面已 return ⇒ 开档小地图停更，符合「开档世界停」。
	hud.sync_player(tl.char_pos)
	camera_rig.set_target(tl.char_pos)
	# 屋顶要不要画取决于「玩家站没站在 wings 里」（house-spec §4.8.4）。
	# 遮挡顺序取决于玩家脚线（y-sort）。所以整套玩家状态都喂给 world_view。
	# set_player_state 内部有等值判断，不动就不重绘。
	world.set_player_state(tl.char_pos, player.facing, player.walking,
		player.walk_phase, tl.phasing, tl.axis == Timeline.Axis.TIME)


func _process_space(delta: float) -> void:
	# 虚化中不走普通行走：is_walkable() 在虚化期间只守边界（恒为真），
	# 走 move_space 会变成无限穿墙。这里只留 A/D 的「往里 / 往外」（house-spec §8.3）。
	if tl.phasing:
		var held := _process_phasing(delta)
		player.walking = held
		if held and not _last_hotspot.is_empty():
			_clear_hotspot()
		return

	var dir := Vector2(
		Input.get_action_strength("move_right") - Input.get_action_strength("move_left"),
		Input.get_action_strength("move_down") - Input.get_action_strength("move_up")
	)
	if dir.length() > 1.0:
		dir = dir.normalized()

	var moving := dir != Vector2.ZERO
	if moving:
		tl.move_space(dir * PLAYER_SPEED * delta)
		player.facing = dir
		player.walk_phase += delta
	player.walking = moving

	# 走到别处就收起上一次的检视文字
	if moving and not _last_hotspot.is_empty():
		_clear_hotspot()


func _process_time(delta: float) -> void:
	var dir := 0
	if Input.is_action_pressed("move_up"):
		dir = 1
	elif Input.is_action_pressed("move_down"):
		dir = -1

	if dir != 0:
		player.walk_phase += delta
		player.facing = Vector2.UP if dir > 0 else Vector2.DOWN

	# 虚化中 W/S 照旧推时间（house-spec §8.3：时间轴手感不变），
	# A/D 额外提供往里 / 往外 —— 所以这里不 return，两条输入同时有效。
	var phased := false
	if tl.phasing:
		phased = _process_phasing(delta)

	player.walking = dir != 0 or phased
	if dir == 0:
		_step_active = false
		_repeating = false
		_hold_time = 0.0
		return

	if not _step_active:
		# 第一次按下：立刻推一帧，然后开始计时等长按
		_step_active = true
		_repeating = false
		_hold_time = 0.0
		tl.step_time(dir)
		_after_time_step()
		return

	# 长按：超过 STEP_DELAY 后开始按 STEP_INTERVAL 连发
	_hold_time += delta
	if not _repeating:
		if _hold_time >= STEP_DELAY:
			_repeating = true
			_hold_time = 0.0
			tl.step_time(dir)
			_after_time_step()
		return

	if _hold_time >= STEP_INTERVAL:
		_hold_time -= STEP_INTERVAL
		tl.step_time(dir)
		_after_time_step()


func _after_time_step() -> void:
	# 时间变了，脚下的检视点也变了，收起旧文字
	_clear_hotspot()


func _do_inspect() -> void:
	var f := tl.current()
	var h := f.hotspot_at(tl.char_pos)
	if h.is_empty():
		_clear_hotspot()
		hud.show_hotspot({})
		return
	_last_hotspot = h
	hud.show_hotspot(h)
	_collect_evidence(h, f)


## 检视命中 → 证物入档（逆转裁判式收集）。
## 模型（v2）：一件物件 = 一张卡，卡内按年代追加观察记录。
## 归一键（任务书 §2.1）：
##   规则 A 家具 = "<房屋族>::<家具名>"（同一栋房子换 id 仍是同一件）
##   规则 B 地标 = title 第一个「·」之前的主体名（地标状态变了还是同一件）
##   规则 C 家具带 "族::" 前缀、地标不带 ⇒ 两个命名空间互不混
##             （mill::老井 永远不会跟 老井 合成一张卡，这是有意保留）。
func _collect_evidence(h: Dictionary, f: FrameData) -> void:
	var title := String(h.get("title", ""))
	if title == "":
		return
	var house_id := String(h.get("house_id", ""))
	var key := ""
	var source := ""

	if house_id != "":
		# 房屋家具：归一键 = 族::家具名；来源 = 房子名 · 年份
		key = EvidenceStore.furniture_key(house_id, String(h.get("furniture", title)))
		source = "%s · %d" % [_short_house_name(String(h.get("house_name", ""))), f.year]
	else:
		# 世界地标：归一键 = 「·」之前的主体名；来源 = 年份 · 村中
		key = EvidenceStore.landmark_key(title)
		source = "%d · 村中" % f.year

	var res := EvidenceStore.try_collect(key, title, source, String(h.get("text", "")), f.year)
	if res == EvidenceStore.RESULT_DUPLICATE:
		# 同年代已经记过了 → 什么都不做（去重）。
		return
	EvidenceStore.save()
	if archive != null:
		archive.flash_collected(title, res == EvidenceStore.RESULT_NEW_CARD)


## 房子全名形如「磨坊 · A1 1926（旧砖、无暗龛）· 加害方根」，
## 来源标签只要房子名，后面是设定备注，不给玩家看。
## 名字形态很杂（「陆家（一字形）」「周家 · 长工房」「磨坊 → 粮站」「粮站」），
## 所以取第一段后剪掉括号注记；改名链（磨坊 → 粮站）保留 —— 那是那栋房子的本名。
func _short_house_name(full: String) -> String:
	if full == "":
		return "旧屋"
	var head := full.split("·")[0].strip_edges()
	# 「陆家（一字形）」剪掉括号里的注记
	var paren := head.split("（")[0].split("(")[0].strip_edges()
	return paren if paren != "" else "旧屋"


func _clear_hotspot() -> void:
	_last_hotspot = {}
	if hud != null:
		hud.show_hotspot({})


func _on_axis_changed(axis: int) -> void:
	camera_rig.set_time_mode(axis == Timeline.Axis.TIME)
	hud.flash_axis()
	_refresh_all()


func _on_frame_changed(_index: int, _frame: FrameData) -> void:
	_refresh_all()


func _on_out_of_range(_index: int) -> void:
	# 到时间轴这一头了：提示一下，不做位移、不改时代（house-spec §8.3）。
	hud.flash_bounds()


func _on_phasing_changed(on: bool) -> void:
	# 虚化只影响玩家自己的观感（半透明 + 冷色），不闪屏、不震屏。
	hud.set_phasing(on)
	if not on:
		# 走出来时顺手把「往里 / 往外」的按住状态清掉，避免下一步连发
		_phase_active = false
		_phase_repeating = false
		_phase_hold = 0.0
	player.queue_redraw()


## 虚化位移输入（house-spec §8.3 / 方案甲：不改 project.godot，A/D 临时解释成
## 往里 / 往外）。手感跟推时间一致：按下立刻走一步，长按 STEP_DELAY 后按
## STEP_INTERVAL 连发。返回这一帧 A/D 是否按着（给 player.walking 用）。
func _process_phasing(delta: float) -> bool:
	var inp := 0
	if Input.is_action_pressed("move_left"):
		inp = 1      # A = 往里（沿当前朝向深入实体）
	elif Input.is_action_pressed("move_right"):
		inp = -1     # D = 往外（退回最近的自由表面）
	if inp == 0:
		_phase_active = false
		_phase_repeating = false
		_phase_hold = 0.0
		return false

	if not _phase_active:
		_phase_active = true
		_phase_repeating = false
		_phase_hold = 0.0
		_do_phase_step(inp)
		return true

	_phase_hold += delta
	if not _phase_repeating:
		if _phase_hold >= STEP_DELAY:
			_phase_repeating = true
			_phase_hold = 0.0
			_do_phase_step(inp)
		return true

	if _phase_hold >= STEP_INTERVAL:
		_phase_hold -= STEP_INTERVAL
		_do_phase_step(inp)
	return true


func _do_phase_step(inp: int) -> void:
	if inp > 0:
		tl.push_in(player.facing)
	else:
		tl.push_out(player.facing)
	_clear_hotspot()


func _refresh_all() -> void:
	var f := tl.current()
	var is_time := tl.axis == Timeline.Axis.TIME

	world.show_frame(f, is_time)
	world.set_year_tint(_tint_for(tl.index))
	# 换帧后 wings 会变，屋顶显隐必须按新数据重算（§4.8.4 陷阱：不能缓存布尔）
	# 玩家状态也一并同步 —— 排序键靠脚线，切帧时脚线不变也要保证状态新鲜。
	world.set_player_state(tl.char_pos, player.facing, player.walking,
		player.walk_phase, tl.phasing, is_time)

	player.time_mode = is_time
	player.queue_redraw()

	hud.sync(is_time, tl.index, tl.frame_max(), f)


func _tint_for(i: int) -> Color:
	if i >= 0 and i < YEAR_TINTS.size():
		return YEAR_TINTS[i]
	return Color.WHITE