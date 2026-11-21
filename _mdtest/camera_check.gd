extends SceneTree

## 镜头专项自检：
##   1. 地图 = 视口（1280×720）时镜头锁死在 (0,0)
##   2. 地图 > 视口时空间轴跟随玩家
##   3. 切到时间轴那一刻冻结，推帧 / 玩家乱动都不影响镜头
##   4. 回空间轴恢复跟随
##
## 2026-11-21 TILE 16→32：世界 3200×1800；视口方案 = 2a'（1×逻辑，1280×720），
## 即「一屏 40×22.5 格」与原 640×360 的视野完全一致。

const CameraRig = preload("res://scripts/camera_rig.gd")

var fails := 0


func _init() -> void:
	call_deferred("_run")


func _ok(cond: bool, label: String) -> void:
	print(("PASS " if cond else "FAIL ") + label)
	if not cond:
		fails += 1


func _step(rig, target: Vector2, delta := 0.2) -> void:
	rig.set_target(target)
	rig._process(delta)


func _run() -> void:
	# --- 1. 地图 = 视口：锁死 ---
	var rig = CameraRig.new()
	root.add_child(rig)
	rig.setup_viewport(Vector2(1280, 720))
	_step(rig, Vector2(1200, 640), 1.0)
	_ok(rig.offset == Vector2.ZERO, "小地图镜头锁死 offset=(0,0)")
	_ok(rig.position == Vector2.ZERO, "小地图节点位置=(0,0)")

	# --- 2. 大地图：空间轴跟随 ---
	var big = CameraRig.new()
	root.add_child(big)
	big.setup_viewport(Vector2(3200, 1800))   # 2.5× 视口
	# 玩家在 (2400, 1400)，理想 offset = (1760, 1040)
	# clamp 上限 = (3200-1280, 1800-720) = (1920, 1080) → 不触发 clamp
	for i in 5:
		_step(big, Vector2(2400, 1400), 0.2)
	_ok(big.offset.x > 1600.0 and big.offset.y > 900.0,
		"大地图跟随玩家 offset=(%.1f,%.1f)" % [big.offset.x, big.offset.y])
	_ok(big.offset.x <= 1920.0 and big.offset.y <= 1080.0,
		"offset 不超地图边界")

	# 玩家回到左上角 → offset 回 0
	for i in 8:
		_step(big, Vector2(50, 50), 0.2)
	_ok(big.offset.x < 5.0 and big.offset.y < 5.0,
		"玩家回左上 offset 归零 (%.1f,%.1f)" % [big.offset.x, big.offset.y])

	# --- 3. 时间轴冻结 ---
	for i in 5:
		_step(big, Vector2(2400, 1400), 0.2)
	var frozen: Vector2 = big.offset
	big.set_time_mode(true)
	_ok(big.frozen_offset == frozen, "切时间轴瞬间冻结视野")
	# 时间轴里玩家坐标乱动、甚至 _process 多跑，镜头都不该变
	for i in 10:
		_step(big, Vector2(10, 10), 0.2)
	_ok(big.offset.distance_to(frozen) < 0.001,
		"时间轴中推帧/移动不改镜头 (%.2f)" % big.offset.distance_to(frozen))

	# --- 4. 回空间轴恢复跟随 ---
	big.set_time_mode(false)
	for i in 8:
		_step(big, Vector2(50, 50), 0.2)
	_ok(big.offset.x < 5.0, "回空间轴恢复跟随 offset.x=%.1f" % big.offset.x)

	print("CAMERA_CHECK_DONE fails=%d" % fails)
	quit(1 if fails > 0 else 0)
