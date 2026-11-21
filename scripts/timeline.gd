extends RefCounted

## 时间轴管理器。只管三件事：当前帧、轴的状态、能不能过去。
##
## 两处刻意的设计选择，见 HANDOFF §2.5 / §3.4：
## 1. W/S 在两个轴里复用同一个 action，语义靠 axis 分派 —— 不另建 time_forward。
## 2. 推时间不做「弹回去」，做「顶住了」：返回失败原因，由调用方播放反馈。

const FrameData = preload("res://scripts/frame_data.gd")

enum Axis { SPACE, TIME }

signal axis_changed(axis: int)
signal frame_changed(index: int, frame: FrameData)
signal bump(index: int)   # 推不过去时发一次，给顿帧/震屏/闷响用

const FRAMES_PATH := "res://data/frames.json"

var axis: int = Axis.SPACE
var index: int = 0
var frames: Array = []            # Array[FrameData]
var char_pos: Vector2 = Vector2.ZERO
var world_size := Vector2(640, 360)   # 可玩范围，从 frames.json 的 world 读


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
	world_size = Vector2(float(wd.get("width", 640)), float(wd.get("height", 360)))

	frames.clear()
	for item in d.get("frames", []):
		var fd = FrameData.new()
		fd.setup(item)
		frames.append(fd)

	if frames.is_empty():
		push_error("帧表里一帧都没有")
		return false

	var sp: Array = d.get("start_pos", [150, 250])
	char_pos = Vector2(float(sp[0]), float(sp[1]))
	index = 0
	axis = Axis.SPACE
	return true


func current() -> FrameData:
	return frames[index]


func frame_max() -> int:
	return frames.size() - 1


func toggle_axis() -> void:
	axis = Axis.TIME if axis == Axis.SPACE else Axis.SPACE
	axis_changed.emit(axis)


## 沿时间轴推一步。dir = +1 向未来，-1 向过去。
## 成功返回 true。失败时发 bump 信号并保持 index 不变。
func step_time(dir: int) -> bool:
	var target := index + dir
	if target < 0 or target > frame_max():
		bump.emit(index)
		return false

	# §3.4：目标帧里角色所在位置如果被固体重叠，就推不过去。
	# 注意这里用 char_pos（空间轴冻结下来的位置），不是时间轴里的任何新坐标。
	if not (frames[target] as FrameData).is_free(char_pos):
		bump.emit(index)
		return false

	index = target
	frame_changed.emit(index, current())
	return true


## 某个点能不能站：不越界 + 不撞墙。
## 地图边缘是「隐形墙」—— 比画一圈实体墙省事，且不会挡视线。
func is_walkable(at: Vector2) -> bool:
	var r := FrameData.CHAR_RADIUS
	if at.x < r or at.y < r or at.x > world_size.x - r or at.y > world_size.y - r:
		return false
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