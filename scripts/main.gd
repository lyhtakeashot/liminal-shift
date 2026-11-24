extends Control

## 主控：输入分发 + 双轴状态。
##
## 输入一律用轮询（Input.is_action_pressed）而不是 _unhandled_input 里的事件。
## 原因：键盘按住会自动重复，事件会被连续收到，一按 W 就可能直接冲到 A5。
## 轮询 + 自己做重复计时，才能精确控制「推一帧」的节奏。
##
## 复用 move_up / move_down 做时间推进（HANDOFF §2.5），
## 语义靠 axis 分派，不另建 time_forward / time_back。

const PLAYER_SPEED := 120.0
const STEP_DELAY := 0.30      # 按住后多久开始自动重复
const STEP_INTERVAL := 0.13   # 自动重复的间隔

const Timeline = preload("res://scripts/timeline.gd")
const FrameData = preload("res://scripts/frame_data.gd")
const EvidenceStore = preload("res://scripts/evidence_store.gd")
const EvidenceArchive = preload("res://scripts/evidence_archive.gd")

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

var _step_active := false    # 这一轮按住是否已经推过第一帧
var _repeating := false      # 是否已经进入连发阶段
var _hold_time := 0.0
var _last_hotspot: Dictionary = {}
var _f11_down := false       # F11 边沿检测（轮询，不用事件）


func _ready() -> void:
	tl = Timeline.new()
	if not tl.load_frames():
		push_error("帧表加载失败，游戏没法继续")
		return

	tl.axis_changed.connect(_on_axis_changed)
	tl.frame_changed.connect(_on_frame_changed)
	tl.bump.connect(_on_bump)

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
	# 读回上次存档的证物（跨启动持久化）。读不到就当空档案。
	EvidenceStore.load()
	_refresh_all()


## 建证物档案界面：动态挂 Main 下（与 HUD 同层，建在 HUD 之后 → 画在 HUD 上面）。
## 不改 scenes/main.tscn 的结构。
func _make_archive() -> void:
	archive = EvidenceArchive.new()
	archive.name = "EvidenceArchive"
	add_child(archive)


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

	# 档案开着的时候，游戏逻辑全停（不响应行走 / 时间轴推帧 / SHIFT 切时代 / E 检视）。
	# ⚠️ SHIFT 与 E 的处理必须放在这个判断**之后** —— 开着档案时世界是停的，
	#    否则玩家能一边翻档案一边切时代、顺手把新年代证物也收了。
	if archive != null and archive.is_open():
		player.walking = false
		_set_hud_hidden(true)
		return
	_set_hud_hidden(false)

	# ↓↓↓ 开档时不响应的两个动作放在这里 ↓↓↓
	# SHIFT 切时代：档案开着就跳过（档案是跨时代卷宗，翻它不该动世界）。
	if Input.is_action_just_pressed("shift_axis"):
		tl.toggle_axis()

	# E 检视：档案开着就跳过（免得关档瞬间误收一件）。
	if Input.is_action_just_pressed("inspect"):
		_do_inspect()

	if tl.axis == Timeline.Axis.SPACE:
		_process_space(delta)
	else:
		_process_time(delta)

	player.position = tl.char_pos
	camera_rig.set_target(tl.char_pos)
	# 屋顶要不要画取决于「玩家站没站在 wings 里」（house-spec §4.8.4）。
	# 遮挡顺序取决于玩家脚线（y-sort）。所以整套玩家状态都喂给 world_view。
	# set_player_state 内部有等值判断，不动就不重绘。
	world.set_player_state(tl.char_pos, player.facing, player.walking,
		player.walk_phase, player.bump_kick, tl.axis == Timeline.Axis.TIME)


func _process_space(delta: float) -> void:
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

	player.walking = dir != 0
	if dir != 0:
		player.walk_phase += delta
		player.facing = Vector2.UP if dir > 0 else Vector2.DOWN

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


func _on_bump(_index: int) -> void:
	# §3.4：不要弹回去，要「顶住了」
	hud.flash_bump()
	world.kick_shake(2.2)
	player.bump_kick = 4.8
	player.queue_redraw()


func _refresh_all() -> void:
	var f := tl.current()
	var is_time := tl.axis == Timeline.Axis.TIME

	world.show_frame(f, is_time)
	world.set_year_tint(_tint_for(tl.index))
	# 换帧后 wings 会变，屋顶显隐必须按新数据重算（§4.8.4 陷阱：不能缓存布尔）
	# 玩家状态也一并同步 —— 排序键靠脚线，切帧时脚线不变也要保证状态新鲜。
	world.set_player_state(tl.char_pos, player.facing, player.walking,
		player.walk_phase, player.bump_kick, is_time)

	player.time_mode = is_time
	player.queue_redraw()

	hud.sync(is_time, tl.index, tl.frame_max(), f)


func _tint_for(i: int) -> Color:
	if i >= 0 and i < YEAR_TINTS.size():
		return YEAR_TINTS[i]
	return Color.WHITE