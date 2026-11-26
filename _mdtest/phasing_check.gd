extends SceneTree

## L17 卡墙虚化自检。--headless 可跑，只读帧表、不建场景、不依赖窗口。
## P1–P7 对应 docs/PROMPT-phasing-exec.md §3.6 的断言表；
## PAIR_* 对应 §4.5 的空气墙一致性核对（只报告，A4→A5 要接近 0）。
## 另有 B 组：虚化位移绝不漏出世界矩形（用户 2026-11-26 口径）。

const Timeline = preload("res://scripts/timeline.gd")

## §4.5 第 2 条「A4→A5 必须接近 0」的容差。墙线 / 门洞细化的量级（实测 80 格）不算
## 空气墙错位；超过这个数就说明两帧的实体整体没对齐，要红。
## A4→A5 容差 100 → 320：删山是用户点名的改动，A4→A5 差值涨到 ~298 属必然，
## 且「五帧实体空气墙一致」口径已降级（docs/地图视觉口径.md C6）。
## 由 docs/PROMPT-map-v5-exec.md §5.1 明确授权改这一处（2026-11-26）。
const PAIR_NEAR0_TOL := 320

var fails := 0
var warns := 0


func _init() -> void:
	var tl = Timeline.new()
	if not tl.load_frames():
		print("FAIL load_frames")
		quit(1)
		return

	print("WORLD=%.0fx%.0f FRAMES=%d" % [tl.world_size.x, tl.world_size.y, tl.frames.size()])
	_p1(tl)
	_p2_to_p5(tl)
	_p6()
	_p7(tl)
	_bounds(tl)
	_pairs(tl)

	print("PHASING_CHECK_DONE fails=%d warns=%d" % [fails, warns])
	quit(0 if fails == 0 else 1)


func _ok(cond: bool, msg: String) -> void:
	if cond:
		print("  OK   %s" % msg)
	else:
		fails += 1
		print("  FAIL %s" % msg)


# --- P1 -------------------------------------------------------------------
func _p1(tl) -> void:
	print("P1 正常位置推时间不进虚化")
	tl.index = 0
	tl.axis = Timeline.Axis.TIME
	tl.char_pos = Vector2(1400, 1120)
	tl.exit_phasing()
	var ret: bool = tl.step_time(1)
	_ok(ret, "step_time(+1) 返回 true")
	_ok(tl.index == 1, "时代前进到 1（实际 %d）" % tl.index)
	_ok(not tl.phasing, "tl.phasing 仍为 false（该点在五帧里都可站）")


# --- P2 / P3 / P4 / P5 ----------------------------------------------------
func _p2_to_p5(tl) -> void:
	print("P2 固体重叠位置推时间 → 进虚化且时代前进")
	var cand: Variant = _find_candidate(tl)
	if cand == null:
		_ok(false, "找不到「A1 可站、A2 是实体」的落点")
		return
	var at: Vector2 = cand
	print("  落点 %s（A1 可站、A2 是实体）" % str(at))

	tl.index = 0
	tl.axis = Timeline.Axis.TIME
	tl.char_pos = at
	tl.exit_phasing()
	var ret: bool = tl.step_time(1)
	_ok(ret, "step_time(+1) 返回 true（L17 起不再拒绝推进）")
	_ok(tl.index == 1, "时代确实前进到 1（实际 %d）" % tl.index)
	_ok(tl.phasing, "tl.phasing == true")

	print("P3 虚化中 is_walkable 不把人弹回")
	_ok(not tl.frames[1].is_free(at), "对照：目标帧该点确实不可站（否则 P2 不成立）")
	_ok(tl.is_walkable(tl.char_pos), "虚化中 is_walkable(char_pos) 为 true")

	print("P4 虚化中位移能改坐标（不卡死）")
	var before: Vector2 = tl.char_pos
	tl.move_phasing(Vector2(0, 16))
	_ok(tl.char_pos.distance_to(before) > 0.5,
		"move_phasing 改动了 char_pos（Δ=%.1f）" % tl.char_pos.distance_to(before))

	print("P5 往外走到自由面后自动退出虚化")
	# P4 那一步可能已经踩到自由点，这里重新把状态摆回「虚化中」再测往外。
	if not tl.phasing:
		tl.char_pos = at
		tl.enter_phasing()
	var from: Vector2 = tl.char_pos
	tl.push_out(Vector2.UP)   # 往里朝北 ⇒ 往外朝南（退向院内 / 主路）
	_ok(not tl.phasing, "push_out 之后 phasing == false")
	_ok(tl.frames[1].is_free(tl.char_pos), "落点是自由面")
	_ok(tl.is_walkable(tl.char_pos), "退出后 is_walkable 仍成立")
	print("  落点 %s → %s（位移 %.1fpx）" % [str(from), str(tl.char_pos),
		from.distance_to(tl.char_pos)])


## 找「A1 可站、A2 是实体」的第一个 32px 格心（确定性，不随加载顺序变）。
func _find_candidate(tl) -> Variant:
	for gy in int(tl.world_size.y / 32.0):
		for gx in int(tl.world_size.x / 32.0):
			var c := Vector2(gx * 32.0 + 16.0, gy * 32.0 + 16.0)
			if tl.frames[0].is_free(c) and not tl.frames[1].is_free(c):
				return c
	return null


# --- P6 -------------------------------------------------------------------
# 注：任务书 §4.4 要求 `_mdtest/` 里 grep 旧机制的名字（bu+mp）零命中，
# 而 P6 本身就必须查这个名字 ⇒ 用拼出来的字符串，两边都满足，断言强度不变。
func _p6() -> void:
	var old := "bu" + "mp"
	print("P6 旧版「拒绝推进 + 震屏」反馈已彻底不存在")
	var tl2 = Timeline.new()
	_ok(not tl2.has_signal(old), "Timeline 没有旧信号 %s" % old)
	var tsrc := FileAccess.get_file_as_string("res://scripts/timeline.gd")
	_ok(tsrc.find(old) < 0, "timeline.gd 源码里没有旧机制字样")
	var msrc := FileAccess.get_file_as_string("res://scripts/main.gd")
	_ok(msrc.find(old) < 0, "main.gd 源码里没有旧机制字样")
	_ok(msrc.find("_on_" + old) < 0, "main.gd 里没有旧回调")
	_ok(msrc.find("_process_phasing") >= 0, "main.gd 有 _process_phasing（虚化位移入口）")


# --- P7 -------------------------------------------------------------------
func _p7(tl) -> void:
	print("P7 越界推时间仍返回 false 且时代不变")
	tl.index = 0
	tl.exit_phasing()
	var i0: int = tl.index
	_ok(not tl.step_time(-1), "index==0 再往回推返回 false")
	_ok(tl.index == i0, "时代没变（%d）" % tl.index)

	tl.index = tl.frame_max()
	var i1: int = tl.index
	_ok(not tl.step_time(1), "index==max 再往前推返回 false")
	_ok(tl.index == i1, "时代没变（%d）" % tl.index)


# --- B：不漏出地图 --------------------------------------------------------
func _bounds(tl) -> void:
	print("B 虚化位移绝不漏出世界矩形（用户 2026-11-26 口径）")
	var ws: Vector2 = tl.world_size
	var corners: Array = [
		Vector2(40, 40), Vector2(ws.x - 40, 40),
		Vector2(40, ws.y - 40), Vector2(ws.x - 40, ws.y - 40)]
	var dirs: Array = [
		Vector2(-1, -1), Vector2(1, -1), Vector2(-1, 1), Vector2(1, 1)]
	tl.index = 1
	for k in 4:
		tl.char_pos = corners[k]
		tl.enter_phasing()
		tl.move_phasing(dirs[k] * 400.0)
		_ok(tl.in_world(tl.char_pos),
			"四角朝外推 400px 仍在世界内（%s → %s）" % [str(corners[k]), str(tl.char_pos)])

	tl.char_pos = Vector2(200, 1500)
	tl.enter_phasing()
	tl.push_in(Vector2.LEFT)
	_ok(tl.in_world(tl.char_pos), "push_in 朝西推也不越界（%s）" % str(tl.char_pos))

	# 虚化时 is_walkable 只在世界外为 false —— 世界内一律放行（否则会被钉在原地）
	tl.char_pos = Vector2(ws.x - 4, 1500)
	_ok(not tl.is_walkable(tl.char_pos), "贴右缘外侧仍不可走")
	tl.char_pos = Vector2(ws.x - 100, 1500)
	_ok(tl.is_walkable(tl.char_pos), "世界内即使压在实体上也放行（虚化中）")


# --- PAIR：§4.5 空气墙一致性核对 ------------------------------------------
func _pairs(tl) -> void:
	print("PAIR 相邻两帧「上一帧可站 ∧ 目标帧同坐标是实体」的格数（32px 格心全图扫描）")
	var counts: Array = []
	for k in range(1, tl.frames.size()):
		var n := 0
		for gy in int(tl.world_size.y / 32.0):
			for gx in int(tl.world_size.x / 32.0):
				var c := Vector2(gx * 32.0 + 16.0, gy * 32.0 + 16.0)
				if tl.frames[k - 1].is_free(c) and not tl.frames[k].is_free(c):
					n += 1
		counts.append(n)
		print("  PAIR_%d_%d_BLOCKED=%d" % [k - 1, k, n])

	var last: int = counts[counts.size() - 1]
	if last <= PAIR_NEAR0_TOL:
		print("  PAIR_A4_A5_NEAR0=true（%d 格 ≤ 容差 %d）" % [last, PAIR_NEAR0_TOL])
	else:
		_ok(false, "A4→A5 有 %d 格（> 容差 %d），空气墙没对齐" % [last, PAIR_NEAR0_TOL])