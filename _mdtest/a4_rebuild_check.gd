extends SceneTree

## A4 重排线专属几何自检（docs/PROMPT-a4-rebuild-exec.md §3.5）。
##
## 口径（与 lab/_a4_build.py 完全一致，两边互为交叉验证）：
##   - solid 语义照 scripts/frame_data.gd:38 —— solid:false 完全不进碰撞，
##     路 / 田 / 井 / 树 / 内岛 / 环道都不挡路；只有 house lot 与 solid:true 世界物件挡路。
##   - 空气墙 ＝ 房屋 lot 外框 ∪ 山体多边形（用户 2026-11-26 硬口径）。
##   - 压环岛必须用**真实 polygon 点包含测试**，不许用 bbox（bbox 会误报）。

const Timeline = preload("res://scripts/timeline.gd")
const HouseShape = preload("res://scripts/house_shape.gd")

const TILE := 32.0
const TILEI := 32
const OX := 2048.0
const OY := 1664.0
const R_IN := 176.0
const R_OUT := 304.0
const LANE_X0 := 1984.0
const LANE_X1 := 2112.0
const LANE_N_BOT := 1360.0
const LANE_S_TOP := 1968.0
const TREE_R := 96.0

## A4 推荐落位（§2.2）
const POS := {
	"shen_a4": Vector2(64, 416),
	"market": Vector2(2144, 320),
	"zhou_a4": Vector2(576, 1920),
	"zheng_a4": Vector2(1152, 2272),
}
## 补山 ×4（§2.6）
const FILL_HILLS := [
	Rect2(1280, 1920, 512, 352),
	Rect2(576, 2272, 576, 416),
	Rect2(576, 2688, 1216, 192),
	Rect2(2176, 1984, 672, 640),
]
const DAM := Rect2(384, 96, 256, 128)
const FIELD := Rect2(3600, 320, 880, 384)
const ROAD_W := Rect2(0, 1600, 1744, 128)
const ROAD_E := Rect2(2352, 1600, 2448, 128)
const SIGNS := [
	Rect2(800, 1732, 16, 32), Rect2(1600, 1732, 16, 32),
	Rect2(2600, 1732, 16, 32), Rect2(3400, 1732, 16, 32),
]

var fails := 0


func _init() -> void:
	call_deferred("_run")


func _ok(cond: bool, label: String) -> void:
	print(("PASS " if cond else "FAIL ") + label)
	if not cond:
		fails += 1


func _run() -> void:
	var tl = Timeline.new()
	if not tl.load_frames():
		print("FAIL load_frames")
		quit(1)
		return

	var fr4 = null
	var fr5 = null
	for fr in tl.frames:
		if fr.id == "a4_2001":
			fr4 = fr
		if fr.id == "a5_2026":
			fr5 = fr
	_ok(fr4 != null and fr5 != null, "帧表里能找到 a4_2001 / a5_2026")
	if fr4 == null or fr5 == null:
		print("A4_REBUILD_CHECK_DONE fails=%d" % fails)
		quit(1)
		return

	# ---------- 1. shapes 数量与类型分布 ----------
	var n_poly_hill := 0
	var n_shapes: int = fr4.shapes.size()
	var n_house := 0
	var n_road_rect := 0
	var n_unlabeled_rect := 0
	for s in fr4.shapes:
		var sd: Dictionary = s
		var ty := String(sd.get("type", ""))
		var lb := String(sd.get("label", ""))
		if ty == "polygon" and lb == "山":
			n_poly_hill += 1
		if ty == "house":
			n_house += 1
		if ty == "rect" and lb == "路":
			n_road_rect += 1
		if ty == "rect" and lb == "":
			n_unlabeled_rect += 1
	_ok(n_shapes == 26, "a4_2001 shapes=26（实际 %d）" % n_shapes)
	_ok(n_house == 4, "house 4 栋（实际 %d）" % n_house)
	_ok(n_poly_hill == 7, "山 polygon 7 座＝3 抄 A5 ＋ 4 补山（实际 %d）" % n_poly_hill)
	_ok(n_road_rect == 2, "主路 rect 2 段引道（实际 %d）" % n_road_rect)
	_ok(fr4.hotspots.size() == 5 + _clue_hotspot_count(fr4),
		"hotspot 数＝手写 5 ＋ clue 家具（实际 %d）" % fr4.hotspots.size())

	# ---------- 10. 只有一个无 label rect ----------
	_ok(n_unlabeled_rect == 1, "无 label rect 恰好 1 个（田）")

	# ---------- 11. 竖路 / 环道 / 内岛不许 road:true ----------
	var bad_road := []
	for s in fr4.shapes:
		var sd: Dictionary = s
		if String(sd.get("type", "")) == "polygon" and bool(sd.get("road", false)):
			bad_road.append(String(sd.get("label", "")))
	_ok(bad_road.is_empty(), "竖路/环道/内岛没有 road:true（违规 %s）" % str(bad_road))

	# ---------- 12. 没有界碑 ----------
	var has_stele_shape := false
	for s in fr4.shapes:
		if String((s as Dictionary).get("label", "")) == "碑":
			has_stele_shape = true
	var has_stele_hot := false
	for h in fr4.hotspots:
		if String((h as Dictionary).get("title", "")) == "界碑":
			has_stele_hot = true
	_ok(not has_stele_shape, "a4 帧里没有 label「碑」的 shape")
	_ok(not has_stele_hot, "a4 帧里没有 title「界碑」的 hotspot")

	# ---------- 2. 四栋房两两不重叠 + 在世界内 ----------
	var rects := {}
	for hid in POS:
		rects[hid] = HouseShape.lot_rect(HouseShape.house(hid), POS[hid])
	var ids: Array = rects.keys()
	var overlap_bad := []
	for i in ids.size():
		for j in range(i + 1, ids.size()):
			if (rects[ids[i]] as Rect2).intersects(rects[ids[j]] as Rect2):
				overlap_bad.append("%s/%s" % [ids[i], ids[j]])
	_ok(overlap_bad.is_empty(), "四栋房两两不重叠（违规 %s）" % str(overlap_bad))
	var oob := []
	for hid in ids:
		var r: Rect2 = rects[hid]
		if r.position.x < 0 or r.position.y < 0 \
				or r.end.x > tl.world_size.x or r.end.y > tl.world_size.y:
			oob.append(hid)
	_ok(oob.is_empty(), "四栋房全部在世界内（出界 %s）" % str(oob))

	# ---------- 3. 离主路 / 竖车道 / 环岛 / 坝田山路标 ----------
	var ring_pts: Array = _points_of(fr5, "路", 72)
	var island_pts: Array = _points_of(fr5, "岛", 72)
	var river_pts: Array = _points_of(fr5, "河", 152)
	_ok(not ring_pts.is_empty() and not island_pts.is_empty() and not river_pts.is_empty(),
		"A5 帧里读到 环道72 / 内岛72 / 河152 的 points")

	var road_gap_bad := []
	var lane_gap_bad := []
	var ring_bad := []
	var island_bad := []
	var misc_bad := []
	for hid in ids:
		var r: Rect2 = rects[hid]
		for rb in [ROAD_W, ROAD_E]:
			if not _gap_at_least(r, rb, 32.0):
				road_gap_bad.append("%s:%s" % [hid, str(rb)])
		for lb in [Rect2(LANE_X0, 288, LANE_X1 - LANE_X0, LANE_N_BOT - 288.0),
				Rect2(LANE_X0, LANE_S_TOP, LANE_X1 - LANE_X0, tl.world_size.y - LANE_S_TOP)]:
			if not _gap_at_least(r, lb, 32.0):
				lane_gap_bad.append("%s:%s" % [hid, str(lb)])
		# 环岛外缘 ≥32px：用「矩形到圆心的最近距离」
		var d := _rect_dist_to_point(r, Vector2(OX, OY))
		if d < R_OUT + 32.0:
			ring_bad.append("%s:%.0f" % [hid, d])
		# 真实 polygon 点包含测试（不许用 bbox）
		if _rect_hits_poly(r, ring_pts, 8.0) > 0:
			ring_bad.append("%s:poly" % hid)
		if _rect_hits_poly(r, island_pts, 8.0) > 0:
			island_bad.append(hid)
		if r.intersects(DAM):
			misc_bad.append("%s:坝" % hid)
		if r.intersects(FIELD):
			misc_bad.append("%s:田" % hid)
		for sg in SIGNS:
			if r.intersects(sg):
				misc_bad.append("%s:路标" % hid)
		for i in FILL_HILLS.size():
			if r.intersects(FILL_HILLS[i]):
				misc_bad.append("%s:补山%d" % [hid, i])
	_ok(road_gap_bad.is_empty(), "四栋房离主路带 ≥32px（违规 %s）" % str(road_gap_bad))
	_ok(lane_gap_bad.is_empty(), "四栋房离竖车道 ≥32px（违规 %s）" % str(lane_gap_bad))
	_ok(ring_bad.is_empty(), "四栋房离环岛外缘 ≥32px 且不压环道 polygon（违规 %s）" % str(ring_bad))
	_ok(island_bad.is_empty(), "四栋房不压内岛 polygon（违规 %s）" % str(island_bad))
	_ok(misc_bad.is_empty(), "四栋房不压坝/田/路标/补山（违规 %s）" % str(misc_bad))

	# ---------- 4. 房顶到河下沿净距 ≥32px（该 x 区间最大 y） ----------
	var river_bad := []
	for hid in ids:
		var r: Rect2 = rects[hid]
		var rb := _river_bottom(river_pts, r.position.x, r.end.x)
		if r.position.y < rb + 32.0:
			river_bad.append("%s(顶%.0f 河下沿%.0f)" % [hid, r.position.y, rb])
		# 顺便：补山/新增山也要不压河
	for i in FILL_HILLS.size():
		var hb: Rect2 = FILL_HILLS[i]
		var rb2 := _river_bottom(river_pts, hb.position.x, hb.end.x)
		if hb.position.y < rb2 + 32.0:
			river_bad.append("补山%d(顶%.0f 河下沿%.0f)" % [i, hb.position.y, rb2])
	_ok(river_bad.is_empty(), "房/补山顶到河下沿净距 ≥32px（违规 %s）" % str(river_bad))

	# ---------- 5. 井在竖车道 x 内 + 井心到超市西墙 ≤96 ----------
	var well := _circle_of(fr4, "老井 · 沥青补丁")
	var well_gap: float = rects["market"].position.x - well["center"].x
	_ok(well["center"].x >= LANE_X0 and well["center"].x <= LANE_X1,
		"井心 x=%.0f 落在竖车道 [%.0f,%.0f] 内" % [well["center"].x, LANE_X0, LANE_X1])
	_ok(well_gap <= 96.0, "井心到超市西墙 %.0fpx ≤96（「只隔一道墙」）" % well_gap)
	_ok(well["radius"] == 32.0, "A4 老井 radius=32（A5 是 48，刻度不同）")

	# ---------- 6. 树冠 ≤ R_IN−16 ----------
	var tree := _circle_of(fr4, "老槐")
	_ok(tree["radius"] <= R_IN - 16.0,
		"老槐 radius=%.0f ≤ R_IN−16=%.0f" % [tree["radius"], R_IN - 16.0])
	_ok(tree["center"] == Vector2(OX, OY), "老槐圆心＝环岛圆心 (2048,1664)（与 A5 同心）")
	_ok(well["center"] == Vector2(2048, 832), "老井圆心＝(2048,832)（与 A5 同心）")

	# ---------- 7-8. 环道 / 内岛 / 河 与 A5 帧逐点相同 ----------
	_ok(_same_points(fr4, fr5, "路", 72), "环道 polygon 与 A5 帧 points 逐点相同")
	_ok(_same_points(fr4, fr5, "岛", 72), "内岛 polygon 与 A5 帧 points 逐点相同")
	_ok(_same_points(fr4, fr5, "河", 152), "河 polygon 与 A5 帧 points 逐点相同")

	# ---------- 9. 每个热点 reach 内都有可站位 ----------
	var hot_bad := []
	for h in fr4.hotspots:
		var hd: Dictionary = h
		var hp: Vector2 = hd["pos"]
		var reach := float(hd["reach"])
		var free_n := 0
		var y := hp.y - reach
		while y <= hp.y + reach:
			var x := hp.x - reach
			while x <= hp.x + reach:
				var p := Vector2(x, y)
				if p.distance_to(hp) <= reach and fr4.is_free(p):
					free_n += 1
				x += 8.0
			y += 8.0
		if free_n <= 0:
			hot_bad.append(String(hd.get("title", "?")))
	_ok(hot_bad.is_empty(), "每条热点 reach 内都有可站位（不可达 %s）" % str(hot_bad))

	# ---------- 13. 空气墙一致（房屋 lot ∪ 山体多边形，逐格） ----------
	var m4 := _airwall(fr4)
	var m5 := _airwall(fr5)
	var inter := 0
	for k in m5:
		if m4.has(k):
			inter += 1
	var only4 := 0
	for k in m4:
		if not m5.has(k):
			only4 += 1
	var only5 := m5.size() - inter
	var cov5 := 100.0 * float(inter) / float(maxi(1, m5.size()))
	var cov4 := 100.0 * float(inter) / float(maxi(1, m4.size()))
	var iou := 100.0 * float(inter) / float(maxi(1, m4.size() + only5))
	print("AIRWALL a4=%d cells  a5=%d cells  cover(A5⊆A4)=%.1f%%  cover(A4⊆A5)=%.1f%%  IoU=%.1f%%  A4独有=%d  A5独有=%d"
		% [m4.size(), m5.size(), cov5, cov4, iou, only4, only5])
	_ok(cov5 >= 100.0, "cover(A5⊆A4)=100%%（实际 %.1f%%）" % cov5)
	_ok(cov4 >= 100.0, "cover(A4⊆A5)=100%%（实际 %.1f%%）" % cov4)
	_ok(only4 == 0 and only5 == 0, "A4↔A5 双向触发格数 = 0（实际 %d / %d）" % [only4, only5])

	# 跨旧帧报告（A1–A3 尚未重排，必然还很大）
	for fr in tl.frames:
		if fr.id == "a4_2001":
			continue
		var mk := _airwall(fr)
		var a := 0
		for k in m4:
			if not mk.has(k):
				a += 1
		var b := 0
		for k in mk:
			if not m4.has(k):
				b += 1
		print("AIRWALL_A4_vs_%s = A4独有 %d 格 / %s独有 %d 格（%s 共 %d 格）"
			% [fr.id, a, fr.id, b, fr.id, mk.size()])

	# ---------- 14. 补山压环岛用真实 polygon 包含测试 ----------
	var fill_bad := []
	for i in FILL_HILLS.size():
		var hb: Rect2 = FILL_HILLS[i]
		if _rect_hits_poly(hb, ring_pts, 8.0) > 0:
			fill_bad.append("补山%d压环道" % i)
		if _rect_hits_poly(hb, island_pts, 8.0) > 0:
			fill_bad.append("补山%d压内岛" % i)
	_ok(fill_bad.is_empty(), "补山 ×4 不压环道/内岛 polygon（真实点包含，非 bbox）（违规 %s）"
		% str(fill_bad))

	# ---------- 15. 补山其余冲突 ----------
	var fill_misc := []
	for i in FILL_HILLS.size():
		var hb: Rect2 = FILL_HILLS[i]
		for rb in [ROAD_W, ROAD_E]:
			if hb.intersects(rb):
				fill_misc.append("补山%d压主路" % i)
		if hb.intersects(Rect2(LANE_X0, 288, LANE_X1 - LANE_X0, LANE_N_BOT - 288.0)) \
				or hb.intersects(Rect2(LANE_X0, LANE_S_TOP, LANE_X1 - LANE_X0, tl.world_size.y - LANE_S_TOP)):
			fill_misc.append("补山%d压竖车道" % i)
		if hb.intersects(DAM):
			fill_misc.append("补山%d压坝" % i)
		if hb.intersects(FIELD):
			fill_misc.append("补山%d压田" % i)
		for sg in SIGNS:
			if hb.intersects(sg):
				fill_misc.append("补山%d压路标" % i)
		for hid in ids:
			if hb.intersects(rects[hid]):
				fill_misc.append("补山%d压房 %s" % [i, hid])
		for j in range(i + 1, FILL_HILLS.size()):
			if hb.intersects(FILL_HILLS[j]):
				fill_misc.append("补山%d/补山%d 重叠" % [i, j])
		if hb.position.x < 0 or hb.position.y < 0 \
				or hb.end.x > tl.world_size.x or hb.end.y > tl.world_size.y:
			fill_misc.append("补山%d出界" % i)
	_ok(fill_misc.is_empty(), "补山 ×4 不压主路/竖车道/坝/田/路标/房、互不重叠、在世界内（违规 %s）"
		% str(fill_misc))

	# ---------- 概况 ----------
	print("FRAME a4_2001 solids=%d hotspots=%d" % [fr4.solid_rects.size(), fr4.hotspots.size()])
	print("FRAME a5_2026 solids=%d hotspots=%d" % [fr5.solid_rects.size(), fr5.hotspots.size()])
	print("A4_REBUILD_CHECK_DONE fails=%d" % fails)
	quit(1 if fails > 0 else 0)


# ==================== 工具 ====================

func _clue_hotspot_count(fr) -> int:
	var n := 0
	for h in fr.hotspots:
		if (h as Dictionary).has("house_id"):
			n += 1
	return n


func _points_of(fr, label: String, npts: int) -> Array:
	for s in fr.shapes:
		var sd: Dictionary = s
		if String(sd.get("type", "")) == "polygon" and String(sd.get("label", "")) == label \
				and (sd.get("points", []) as Array).size() == npts:
			return sd["points"]
	return []


func _same_points(fa, fb, label: String, npts: int) -> bool:
	var a := _points_of(fa, label, npts)
	var b := _points_of(fb, label, npts)
	if a.is_empty() or b.is_empty() or a.size() != b.size():
		return false
	return JSON.stringify(a) == JSON.stringify(b)


func _circle_of(fr, label: String) -> Dictionary:
	for s in fr.shapes:
		var sd: Dictionary = s
		if String(sd.get("type", "")) == "circle" and String(sd.get("label", "")) == label:
			var c: Array = sd.get("center", [0, 0])
			return {"center": Vector2(float(c[0]), float(c[1])),
				"radius": float(sd.get("radius", 0))}
	return {"center": Vector2.ZERO, "radius": 0.0}


## 矩形与另一矩形的净距是否 ≥ gap（相交即 false）
func _gap_at_least(a: Rect2, b: Rect2, gap: float) -> bool:
	if a.intersects(b):
		return false
	var dx: float = maxf(maxf(b.position.x - a.end.x, a.position.x - b.end.x), 0.0)
	var dy: float = maxf(maxf(b.position.y - a.end.y, a.position.y - b.end.y), 0.0)
	return Vector2(dx, dy).length() >= gap


func _rect_dist_to_point(r: Rect2, p: Vector2) -> float:
	var cx: float = clampf(p.x, r.position.x, r.end.x)
	var cy: float = clampf(p.y, r.position.y, r.end.y)
	return Vector2(cx, cy).distance_to(p)


func _in_poly(p: Vector2, poly: Array) -> bool:
	var inside := false
	var n := poly.size()
	for i in n:
		var a: Array = poly[i]
		var b: Array = poly[(i + 1) % n]
		var y1 := float(a[1])
		var y2 := float(b[1])
		if (y1 > p.y) != (y2 > p.y):
			var xin: float = (float(b[0]) - float(a[0])) * (p.y - y1) / (y2 - y1) + float(a[0])
			if p.x < xin:
				inside = not inside
	return inside


## 采样式「矩形是否碰到多边形内部」（步长 8px）
func _rect_hits_poly(r: Rect2, poly: Array, step: float) -> int:
	if poly.is_empty():
		return 0
	var hits := 0
	var y := r.position.y
	while y < r.end.y:
		var x := r.position.x
		while x < r.end.x:
			if _in_poly(Vector2(x + step * 0.5, y + step * 0.5), poly):
				hits += 1
			x += step
		y += step
	return hits


## 该 x 区间（世界像素）内的河下沿最大 y。⚠️ 不许用全局最大值。
func _river_bottom(river_pts: Array, x0: float, x1: float) -> float:
	var best := 0.0
	for p in river_pts:
		var pa: Array = p
		var px := float(pa[0])
		if px >= x0 and px <= x1:
			best = maxf(best, float(pa[1]))
	return best


## 空气墙掩码：房屋 lot 外框 ∪ 山体多边形（32px 网格）
func _airwall(fr) -> Dictionary:
	var m := {}
	for s in fr.shapes:
		var sd: Dictionary = s
		var ty := String(sd.get("type", ""))
		var box := Rect2()
		var use := false
		if ty == "house":
			var hid := String(sd.get("id", ""))
			var hp: Array = sd.get("pos", [0, 0])
			box = HouseShape.lot_rect(HouseShape.house(hid),
				Vector2(float(hp[0]), float(hp[1])))
			use = true
		elif ty == "polygon" and String(sd.get("label", "")) == "山":
			var pts: Array = sd.get("points", [])
			if pts.size() >= 3:
				var mnx := INF
				var mny := INF
				var mxx := -INF
				var mxy := -INF
				for pp in pts:
					var pa: Array = pp
					mnx = minf(mnx, float(pa[0]))
					mny = minf(mny, float(pa[1]))
					mxx = maxf(mxx, float(pa[0]))
					mxy = maxf(mxy, float(pa[1]))
				box = Rect2(mnx, mny, mxx - mnx, mxy - mny)
				use = true
		if not use:
			continue
		var gy := int(box.position.y) / TILEI
		while gy < int(box.end.y) / TILEI:
			var gx := int(box.position.x) / TILEI
			while gx < int(box.end.x) / TILEI:
				m[Vector2i(gx, gy)] = true
				gx += 1
			gy += 1
	return m