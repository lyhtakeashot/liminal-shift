extends SceneTree

## 几何体检：不靠肉眼看截图，自动找出五帧里的实体互相重叠、
## 热区够不着、以及每帧是否还有可站空间。
##
## 只用矩形/圆形的包围盒做粗判 —— 灰盒阶段的目的是「一眼能分辨、不打架」，
## 不是像素级完美。

const Timeline = preload("res://scripts/timeline.gd")


func _init() -> void:
	var tl = Timeline.new()
	if not tl.load_frames():
		print("FAIL load")
		quit(1)
		return

	for i in tl.frames.size():
		var f = tl.frames[i]
		print("=== FRAME %d %s (%d) ===" % [i, f.id, f.year])

		var boxes: Array = []
		for s in f.shapes:
			var sd: Dictionary = s
			var t := String(sd.get("type", ""))
			var r: Rect2
			if t == "rect":
				var a: Array = sd["rect"]
				r = Rect2(a[0], a[1], a[2], a[3])
			elif t == "circle":
				var c: Array = sd["center"]
				var rad: float = float(sd["radius"])
				r = Rect2(c[0] - rad, c[1] - rad, rad * 2, rad * 2)
			else:
				continue
			boxes.append({"label": String(sd.get("label", t)), "r": r,
				"kind": t, "solid": bool(sd.get("solid", false))})

		# 1. 实体互相重叠。道路/河是「底」，建筑树井压在上面是正常的，不算冲突；
		#    只报「实体 × 实体」，那才是真的画面上打架。
		const UNDER_LAYERS := ["路", "新路", "旧弯道", "河", "水泥", "空地", "荒",
			"田", "田·半荒", "车位", "补丁"]
		var overlaps: Array = []
		for a_i in boxes.size():
			for b_i in range(a_i + 1, boxes.size()):
				var A: Dictionary = boxes[a_i]
				var B: Dictionary = boxes[b_i]
				if UNDER_LAYERS.has(A["label"]) or UNDER_LAYERS.has(B["label"]):
					continue
				if (A["r"] as Rect2).intersects(B["r"] as Rect2):
					overlaps.append("%s × %s" % [A["label"], B["label"]])
		if overlaps.is_empty():
			print("  overlaps: none")
		else:
			print("  overlaps(%d): %s" % [overlaps.size(), ", ".join(overlaps)])

		# 2. 画到屏幕外
		var out: Array = []
		for b in boxes:
			var r: Rect2 = b["r"]
			if r.position.x < -1 or r.position.y < -1 \
				or r.end.x > 641 or r.end.y > 361:
				out.append("%s @ %s" % [b["label"], str(r)])
		if not out.is_empty():
			print("  OFFSCREEN: %s" % ", ".join(out))

		# 3. 热区能不能站到
		for h in f.hotspots:
			var stand := _nearest_free(f, h["pos"])
			var got: Dictionary = f.hotspot_at(stand)
			var ok := String(got.get("title", "")) == String(h["title"])
			print("  hotspot [%s] stand=%s -> %s" % [
				String(h["title"]), str(stand), "OK" if ok else "UNREACHABLE"])

		# 4. 可站立面积占比
		var total := 0
		var free := 0
		for y in range(20, 356, 4):
			for x in range(2, 638, 4):
				total += 1
				if f.is_free(Vector2(x, y)):
					free += 1
		print("  walkable=%.0f%%" % (100.0 * float(free) / maxf(1.0, float(total))))

	quit(0)


func _nearest_free(frame, target: Vector2) -> Vector2:
	if frame.is_free(target):
		return target
	for r in range(4, 70, 3):
		for a in range(0, 360, 12):
			var p: Vector2 = target + Vector2(r, 0).rotated(deg_to_rad(float(a)))
			if frame.is_free(p):
				return p
	return target