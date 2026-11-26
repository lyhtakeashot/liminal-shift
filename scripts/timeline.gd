extends RefCounted

## 时间轴管理器。只管三件事：当前帧、轴的状态、能不能过去。
##
## 三处刻意的设计选择，见 HANDOFF §2.5 / §3.4：
## 1. W/S 在两个轴里复用同一个 action，语义靠 axis 分派 —— 不另建 time_forward。
## 2. 推时间不做「弹回去」，也不做「顶住了」：目标帧把这个位置压进实体时，
##    时代照常前进，主角进入「卡墙虚化」(phasing)，由玩家自己 A/D 往里 / 往外走
##    （house-spec §8.3）。虚化是兜底，不是正常玩法 —— 空气墙对齐是地图线的活。
## 3. 虚化位移不查 is_free()，但**绝不允许出世界矩形**（用户 2026-11-26 口径）。

const FrameData = preload("res://scripts/frame_data.gd")

enum Axis { SPACE, TIME }

signal axis_changed(axis: int)
signal frame_changed(index: int, frame: FrameData)
signal out_of_range(index: int)    # 已经到时间轴这一头，再推也没有更远的年代
signal phasing_changed(on: bool)   # 进入 / 退出卡墙虚化

const FRAMES_PATH := "res://data/frames.json"

## 虚化位移的三档常量（house-spec §8.3 / HANDOFF §3.4.1）：
## 单步 8px（比一格 32px 小，保证不会一步跨过一堵墙）、
## 往外最多退 256px（约 8 格，够从任何房子 / 山体里退出来）、
## 往里最多推 48px（1.5 格，够避免「一直卡在同一条墙线里」）。
const PHASE_STEP := 8.0
const PHASE_OUT_MAX := 256.0
const PHASE_IN_MAX := 48.0
const PHASE_FALLBACK_R := 96.0

var axis: int = Axis.SPACE
var index: int = 0
var frames: Array = []            # Array[FrameData]
var char_pos: Vector2 = Vector2.ZERO
var world_size := Vector2(1280, 720)   # 可玩范围，从 frames.json 的 world 读
var phasing := false             # 卡墙虚化中（当前帧把 char_pos 压进实体）
var phase_origin: Vector2 = Vector2.ZERO   # 进入虚化时的坐标，对外可做落点提示


func load_frames() -> bool:
	var f := FileAccess.open(FRAMES_PATH, FileAccess.READ)
	if f == null:
		push_error("读不到帧表：%s" % FRAMES_PATH)
		return false

	var raw := f.get_as_text()
	f.close()

	var parsed: Variant = JSON.parse_string(raw)
	if parsed == null or typeof(parsed) != TYPE_DICTIONARY:
		push_error("帧表不是合法 JSON：%s" % FRAMES_PATH)
		return false

	var d: Dictionary = parsed

	# 世界边界（frames.json 的 world.width/height）；缺就退回内部分辨率
	var wd: Dictionary = d.get("world", {})
	world_size = Vector2(float(wd.get("width", 1280)), float(wd.get("height", 720)))

	frames.clear()
	for item in d.get("frames", []):
		var fd = FrameData.new()
		fd.setup(item)
		frames.append(fd)

	if frames.is_empty():
		push_error("帧表里一帧都没有")
		return false

	# 起始帧：读 frames.json 的 start_frame（house-spec 2026-11-19 拍板：从 A5 2026 开局）。
	# 缺省 / 写错 ⇒ 退回最后一帧（那正是 A5）—— 不许因为一个字符串让游戏起不来。
	var start_id := String(d.get("start_frame", ""))
	index = frames.size() - 1
	if start_id != "":
		var found := false
		for i in frames.size():
			if frames[i].id == start_id:
				index = i
				found = true
				break
		if not found:
			push_warning("start_frame「%s」不在帧表里，退回最后一帧 %s" % [start_id, frames[index].id])

	# 起点坐标：五帧共用同一个位置（玩法的「位置不变」全靠这个）
	var sp: Array = d.get("start_pos", [150, 250])
	char_pos = Vector2(float(sp[0]), float(sp[1]))
	axis = Axis.SPACE
	phasing = false
	phase_origin = char_pos
	return true


func current() -> FrameData:
	return frames[index]


func frame_max() -> int:
	return frames.size() - 1


func toggle_axis() -> void:
	axis = Axis.TIME if axis == Axis.SPACE else Axis.SPACE
	axis_changed.emit(axis)


## 沿时间轴推一步。dir = +1 向未来，-1 向过去。
## 越界返回 false（只在两头发生时），时代不变。
## 推进成功**一律返回 true**：落在实体里不拦截，改为进入 phasing（house-spec §8.3）。
func step_time(dir: int) -> bool:
	var target := index + dir
	if target < 0 or target > frame_max():
		out_of_range.emit(index)
		return false

	index = target
	frame_changed.emit(index, current())

	# 注意这里用 char_pos（空间轴冻结下来的位置），不是时间轴里的任何新坐标。
	if current().is_free(char_pos):
		exit_phasing()
	else:
		enter_phasing()
	return true


## 进入卡墙虚化。虚化期间 is_walkable() 只守世界边界，位移走 move_phasing()。
func enter_phasing() -> void:
	if phasing:
		return
	phasing = true
	phase_origin = char_pos
	phasing_changed.emit(true)


## 退出卡墙虚化（落到自由面了）。
func exit_phasing() -> void:
	if not phasing:
		return
	phasing = false
	phasing_changed.emit(false)


## 角色中心能不能落在世界矩形里（含半径）。虚化只守这一条。
func in_world(at: Vector2) -> bool:
	var r := FrameData.CHAR_RADIUS
	return at.x >= r and at.y >= r and at.x <= world_size.x - r and at.y <= world_size.y - r


## 某个点能不能站：不越界 + 不撞墙。
## 地图边缘是「隐形墙」—— 比画一圈实体墙省事，且不会挡视线。
## ⚠️ 虚化期间只守边界：人本来就站在实体里，再拿 is_free() 判会把他钉死在原地。
func is_walkable(at: Vector2) -> bool:
	if not in_world(at):
		return false
	if phasing:
		return true
	return current().is_free(at)


## 空间轴移动。返回实际落点（可能因为撞墙或越界而小于期望位移）。
func move_space(delta: Vector2) -> Vector2:
	if delta == Vector2.ZERO:
		return char_pos

	# 分轴推进：撞墙时还能沿墙滑，手感比整块移动好得多。
	var next := char_pos

	var try_x := Vector2(next.x + delta.x, next.y)
	if is_walkable(try_x):
		next.x = try_x.x

	var try_y := Vector2(next.x, next.y + delta.y)
	if is_walkable(try_y):
		next.y = try_y.y

	char_pos = next
	return char_pos


# --- 卡墙虚化位移（house-spec §8.3） ---------------------------------------

## 虚化位移：8px 一步直接改 char_pos，**不查 is_free()**。
## 每步落地若已经是自由面，就自动退出虚化并停住（「走出来就自动恢复」）。
## 唯一硬约束：不许出世界矩形 —— 到边缘就夹住并停。
func move_phasing(delta: Vector2) -> Vector2:
	var dist := delta.length()
	if dist < 0.001:
		return char_pos

	var dir := delta / dist
	var r := FrameData.CHAR_RADIUS
	while dist > 0.001:
		var step := minf(PHASE_STEP, dist)
		var next := char_pos + dir * step
		dist -= step
		if not in_world(next):
			# 贴到世界边缘：把落点夹在矩形里，然后停（不再继续往外）
			var edge := Vector2(
				clampf(next.x, r, world_size.x - r),
				clampf(next.y, r, world_size.y - r))
			if edge.distance_to(char_pos) > 0.001:
				char_pos = edge
			break
		char_pos = next
		if current().is_free(char_pos):
			exit_phasing()
			break
	return char_pos


## 「往里走」：沿 dir（玩家当前朝向）往实体深处走，最多 PHASE_IN_MAX。
## 里面如果已经是空的，那一步就会自动退出虚化。
func push_in(dir: Vector2) -> Vector2:
	if not phasing:
		return char_pos
	var d := dir.normalized() if dir.length() > 0.001 else Vector2.DOWN
	return move_phasing(d * PHASE_IN_MAX)


## 「往外走」：退到最近的自由表面。三级规则（house-spec §8.3 / §2.4）：
## 1) 沿 -dir 直线回退（8px 一步），第一个自由点即落点，最多 256px；
## 2) 还不行 ⇒ 在当前坐标周围找最近自由点（16 方向 × 半径 8..96px）；
## 3) 还不行 ⇒ 原地不动、仍是虚化（绝不把人丢进虚空；再按一次会重新试）。
func push_out(dir: Vector2) -> Vector2:
	if not phasing:
		return char_pos

	var d := dir.normalized() if dir.length() > 0.001 else Vector2.DOWN
	move_phasing(-d * PHASE_OUT_MAX)
	if not phasing:
		return char_pos

	var spot: Variant = _nearest_free(char_pos)
	if spot == null:
		return char_pos
	char_pos = spot
	exit_phasing()
	return char_pos


## 以 at 为心，按半径递增找最近的可站格心；找不到返回 null。
## 只在「往外」的直线回退失败时才用，兜底「人站在凸字形山体里、背后是更厚的墙」。
func _nearest_free(at: Vector2) -> Variant:
	var base := current()
	var radius := PHASE_STEP
	while radius <= PHASE_FALLBACK_R + 0.001:
		for k in 16:
			var ang := TAU * float(k) / 16.0
			var c := at + Vector2(cos(ang), sin(ang)) * radius
			if not in_world(c):
				continue
			if base.is_free(c):
				return c
		radius += PHASE_STEP
	return null