extends SceneTree

## 探针：统计每一对相邻时代之间「源帧可站点位被目标帧顶住」的比例，
## 用来量化「时间之门推不过去」的覆盖面（用户 m09128 第 1 问的证据）。

const Timeline = preload("res://scripts/timeline.gd")


func _init() -> void:
	var tl = Timeline.new()
	tl.load_frames()
	print("world=", tl.world_size, " start=", tl.char_pos)

	for i in range(tl.frames.size() - 1):
		var src = tl.frames[i]
		var dst = tl.frames[i + 1]
		var total := 0
		var blocked := 0
		for y in range(240, 3600, 32):
			for x in range(40, 4800, 32):
				var p := Vector2(x, y)
				if not src.is_free(p):
					continue
				total += 1
				if not dst.is_free(p):
					blocked += 1
		print("STEP %s -> %s : 源帧可站=%d  目标帧顶住=%d  占比=%d%%" % [
			src.id, dst.id, total, blocked,
			int(100.0 * float(blocked) / maxf(1.0, float(total)))])

	# 起点与主路沿线：沿主路中心 y=1664，从起点往东/往西扫，看连续可推多远
	var road_y := 1664.0
	var run_len := 0
	var max_run := 0
	var x := 1024.0
	while x >= 40.0:
		var p := Vector2(x, road_y)
		if tl.frames[0].is_free(p) and tl.frames[4].is_free(p):
			run_len += 1
			max_run = maxi(max_run, run_len)
		else:
			run_len = 0
		x -= 32.0
	print("主路 y=1664 向西：连续可推(全程A1自由且A5自由)最长=%d 格" % max_run)

	quit(0)
