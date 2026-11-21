extends Control

## 主控：输入分发 + 双轴状态。
##
## 输入一律用轮询（Input.is_action_pressed）而不是 _unhandled_input 里的事件。
## 原因：键盘按住会自动重复，事件会被连续收到，一按 W 就可能直接冲到 A5。
## 轮询 + 自己做重复计时，才能精确控制「推一帧」的节奏。
##
## 复用 move_up / move_down 做时间推进（HANDOFF §2.5），
## 语义靠 axis 分派，不另建 time_forward / time_back。

const PLAYER_SPEED := 60.0
const STEP_DELAY := 0.30      # 按住后多久开始自动重复
const STEP_INTERVAL := 0.13   # 自动重复的间隔

const Timeline = preload("res://scripts/timeline.gd")
const FrameData = preload("res://scripts/frame_data.gd")

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
	_refresh_all()


func _process(delta: float) -> void:
	if tl == null:
		return

	if Input.is_action_just_pressed("shift_axis"):
		tl.toggle_axis()

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

	if Input.is_action_just_pressed("inspect"):
		_do_inspect()

	if tl.axis == Timeline.Axis.SPACE:
		_process_space(delta)
	else:
		_process_time(delta)

	player.position = tl.char_pos
	camera_rig.set_target(tl.char_pos)
	# 屋顶要不要画取决于「玩家站没站在 wings 里」（house-spec §4.8.4）。
	# set_player_pos 内部有等值判断，不动就不重绘。
	world.set_player_pos(tl.char_pos)


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
	player.bump_kick = 2.4
	player.queue_redraw()


func _refresh_all() -> void:
	var f := tl.current()
	var is_time := tl.axis == Timeline.Axis.TIME

	world.show_frame(f, is_time)
	world.set_year_tint(_tint_for(tl.index))
	# 换帧后 wings 会变，屋顶显隐必须按新数据重算（§4.8.4 陷阱：不能缓存布尔）
	world.set_player_pos(tl.char_pos)

	player.time_mode = is_time
	player.queue_redraw()

	hud.sync(is_time, tl.index, tl.frame_max(), f)


func _tint_for(i: int) -> Color:
	if i >= 0 and i < YEAR_TINTS.size():
		return YEAR_TINTS[i]
	return Color.WHITE