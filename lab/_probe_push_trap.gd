extends SceneTree

## 探针：统计「在 A1 能站、推到 A5 被顶住」的点按区域分布，
## 重点看世界放大后 A1 新增的东部空地（x>=3200）会不会成为推不动的大片区域。

const Timeline = preload("res://scripts/timeline.gd")
const HouseShape = preload("res://scripts/house_shape.gd")


func _init() -> void:
	var tl = Timeline.new()
	tl.load_frames()
	print("world=", tl.world_size, " start=", tl.char_pos)

	var regions := {
		"x<3200": 0,
		"3200-4000": 0,
		"4000-4800": 0,
	}
	var region_blocked := {
		"x<3200": 0,
		"3200-4000": 0,
		"4000-4800": 0,
	}
	var by_label := {}
	var a1_free_total := 0

	for y in range(240, 3600, 32):
		for x in range(40, 4800, 32):
			var p := Vector2(x, y)
			if not tl.frames[0].is_free(p):
				continue
			a1_free_total += 1
			var key := "x<3200"
			if x >= 4000:
				key = "4000-4800"
			elif x >= 3200:
				key = "3200-4000"
			regions[key] += 1
			if tl.frames[4].is_free(p):
				continue
			region_blocked[key] += 1
			var probe := Rect2(p.x - 14.0, p.y - 14.0, 28.0, 28.0)
			for s in tl.frames[4].shapes:
				var sd: Dictionary = s
				if not bool(sd.get("solid", false)):
					continue
				var stype := String(sd.get("type", ""))
				var hit := false
				if stype == "rect":
					var r: Array = sd.get("rect", [0, 0, 0, 0])
					hit = Rect2(float(r[0]), float(r[1]), float(r[2]), float(r[3])).intersects(probe)
				elif stype == "circle":
					var c: Array = sd.get("center", [0, 0])
					var rad := float(sd.get("radius", 0))
					hit = Rect2(float(c[0]) - rad, float(c[1]) - rad, rad * 2.0, rad * 2.0).intersects(probe)
				elif stype == "house":
					var hp: Array = sd.get("pos", [0, 0])
					var hpos := Vector2(float(hp[0]), float(hp[1]))
					var hdata: Dictionary = HouseShape.house(String(sd.get("id", "")))
					for hr_item in HouseShape.solid_rects(hdata, hpos):
						var hr: Rect2 = hr_item
						if hr.intersects(probe):
							hit = true
							break
				if hit:
					var k2 := "%s/%s" % [stype, String(sd.get("label", ""))]
					by_label[k2] = int(by_label.get(k2, 0)) + 1
					break

	for k in regions.keys():
		var tot: int = regions[k]
		var blk: int = region_blocked[k]
		print("REGION %s: A1可站=%d  推到A5被挡=%d  占比=%d%%" % [k, tot, blk, int(100.0 * float(blk) / maxf(1.0, float(tot)))])

	print("A1_FREE_TOTAL=", a1_free_total)
	print("BLOCKED_BY_LABEL=", str(by_label))

	for i in tl.frames.size():
		print("START_FREE frame[%d] %s = %s" % [i, tl.frames[i].id, tl.frames[i].is_free(tl.char_pos)])

	quit(0)
