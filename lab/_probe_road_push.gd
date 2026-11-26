extends SceneTree

## 探针：主路沿线从起点往东/往西的连续可推长度，
## 用来回答「不能出现推不过去的机制」——玩家在主路上能不能一路走到 A5 的环岛。

const Timeline = preload("res://scripts/timeline.gd")


func _init() -> void:
	var tl = Timeline.new()
	tl.load_frames()

	var road_y := 1664.0
	# 往东
	var run := 0
	var best := 0
	var xe := 1024.0
	while xe < 4800.0:
		var pe := Vector2(xe, road_y)
		if tl.frames[0].is_free(pe) and tl.frames[4].is_free(pe):
			run += 1
			best = maxi(best, run)
		else:
			run = 0
		xe += 32.0
	print("主路 y=1664 往东：连续可推最长=%d 格 (=%d px)" % [best, best * 32])

	# 主路带上（y=1568..1824 带内）逐格统计 A1 自由点中被 A5 挡住的
	var total := 0
	var blocked := 0
	for y in range(1568, 1824, 32):
		for xg in range(32, 4800, 32):
			var pg := Vector2(xg, y)
			if not tl.frames[0].is_free(pg):
				continue
			total += 1
			if not tl.frames[4].is_free(pg):
				blocked += 1
	print("A1 主路带(y1568-1824)内：A1可站=%d 推到A5被挡=%d (%.1f%%)" % [
		total, blocked, 100.0 * float(blocked) / maxf(1.0, float(total))])

	# 站在起点不动，依次推 4 次时代，每步报是否被顶住
	tl.char_pos = Vector2(1024, 1696)
	for i in range(1, tl.frames.size()):
		var ok := tl.step_time(1)
		print("从起点推到 %s : %s" % [tl.frames[i].id, "通过" if ok else "顶住了"])

	quit(0)
