extends Node2D

## 镜头：空间轴跟随玩家，时间轴锁定。
##
## 用法：把世界层（WorldView + Player）作为本节点的子节点。
## 移动本节点 = 移动镜头；HUD 不放在这里，固定在屏幕上。
##
## 关键设计：
##   - 世界尺寸来自 frames.json 的 world.width/height。地图没视口大时
##     offset 被 clamp 到 (0,0)，镜头锁死 —— 现有 640×360 灰盒行为不变。
##   - 空间轴：把玩家放在屏幕中心，offset 限制在 [0, world_size - viewport]，
##     所以地图边缘不会露出空白。
##   - 时间轴：进入那一刻冻结 offset，推帧时镜头完全不动（HANDOFF §2.4）。
##   - 像素对齐（floor）防止亚像素采样让像素画闪烁。

const VIEWPORT := Vector2(1280, 720)
const FOLLOW := 9.0          # 跟随平滑速度，越大越紧跟；0.13s 内基本到位

var world_size := Vector2(1280, 720)
var offset := Vector2.ZERO          # 当前镜头偏移（世界坐标）
var frozen_offset := Vector2.ZERO   # 进入时间轴时冻结的视野
var time_mode := false
var target_pos := Vector2.ZERO      # 玩家世界坐标


func setup_viewport(ws: Vector2) -> void:
	world_size = ws
	_clamp_offset()
	_apply()


func set_target(pos: Vector2) -> void:
	target_pos = pos


func set_time_mode(is_time: bool) -> void:
	if is_time and not time_mode:
		frozen_offset = offset   # 锁在切轴那一刻的视野
	time_mode = is_time


func _process(delta: float) -> void:
	var target: Vector2
	if time_mode:
		target = frozen_offset
	else:
		target = _clamp(target_pos - VIEWPORT * 0.5)

	var t := clampf(delta * FOLLOW, 0.0, 1.0)
	offset = offset.lerp(target, t)
	_clamp_offset()
	_apply()


func _clamp(v: Vector2) -> Vector2:
	# 世界比视口小或相等时 max_off = (0,0)，镜头无法移动 → 锁死
	var max_off := (world_size - VIEWPORT).max(Vector2.ZERO)
	return v.clamp(Vector2.ZERO, max_off)


func _clamp_offset() -> void:
	offset = _clamp(offset)


func _apply() -> void:
	position = -offset.floor()
