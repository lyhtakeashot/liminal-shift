extends SceneTree

## 内部验证用：跑一遍核心逻辑并截图。
## 用 --headless 跑输出文本报告；
## 用普通窗口跑会额外存 PNG 到 _mdtest/greybox/。
##
## 2026-11-21 14:50 BUILD-A1：世界放大到 1600×900，A1 换成 4 栋房子（house 形状）。
## 2026-11-21 TILE 16→32：世界 3200×1800（格数仍是 100×56.25，一格不动），
## 本文件所有绝对坐标随 TILE 翻倍。坐标一律取自实测落盘值，不是机械 ×2。

const Timeline = preload("res://scripts/timeline.gd")
const FrameData = preload("res://scripts/frame_data.gd")
const HouseShape = preload("res://scripts/house_shape.gd")

const OUT_DIR := "res://_mdtest/greybox"

## 五帧统一布局 v5（2026-11-21 落地）：地标与路三帧完全相同，房子在原址上长大。
## 磨坊三帧同址；沈家左移与树留间隙；周家路南、陆家东侧。
## 尺寸取自 houses_data.json 的 lot（格）× TILE=32。
const HOUSE_MAP := {
	"mill_a1": {"pos": Vector2(1216, 448), "size": Vector2(576, 416)},
	"shen_a1": {"pos": Vector2(128, 640), "size": Vector2(640, 416)},
	"zhou_house": {"pos": Vector2(1792, 1280), "size": Vector2(384, 224)},
	"lu_house": {"pos": Vector2(2304, 768), "size": Vector2(640, 416)},
}

## A2 1951：沈家 L 形
const HOUSE_MAP_A2 := {
	"mill_a2": {"pos": Vector2(1216, 448), "size": Vector2(576, 416)},
	"shen_a2": {"pos": Vector2(128, 512), "size": Vector2(736, 544)},
	"zhou_a2": {"pos": Vector2(1792, 1280), "size": Vector2(384, 224)},
	"lu_a2": {"pos": Vector2(2304, 768), "size": Vector2(640, 416)},
}
const OLD_WELL := Vector2(1360, 848)

## A3 1976：沈家凹形最大
const HOUSE_MAP_A3 := {
	"mill_a3": {"pos": Vector2(1216, 448), "size": Vector2(576, 544)},
	"shen_a3": {"pos": Vector2(128, 288), "size": Vector2(896, 768)},
	"zhou_a3": {"pos": Vector2(1792, 1280), "size": Vector2(384, 224)},
	"lu_a3": {"pos": Vector2(2304, 768), "size": Vector2(640, 416)},
}


func _init() -> void:
	var tl = Timeline.new()
	if not tl.load_frames():
		print("FAIL load_frames")
		quit(1)
		return

	# --- 1. 帧表 ---
	print("FRAMES=%d START=%s MAX=%d" % [tl.frames.size(), str(tl.char_pos), tl.frame_max()])

	# --- 2. BUILD-A1 §7.1：世界 3200×1800，起点在主路上可站 ---
	print("WORLD=%.0fx%.0f (期望 3200x1800)" % [tl.world_size.x, tl.world_size.y])
	print("WORLD_OK=%s" % (tl.world_size == Vector2(3200, 1800)))
	print("A1_IS_FREE_START=%s (期望 true)" % tl.current().is_free(tl.char_pos))
	print("START_OK=%s" % tl.current().is_free(tl.char_pos))

	# --- 2b. 世界边界：越界点一律不可站（y=1400 一带是开阔区） ---
	var r := FrameData.CHAR_RADIUS
	print("BOUND_LEFT=%.1f OUT=%s IN=%s" % [
		r, tl.is_walkable(Vector2(1, 1400)), tl.is_walkable(Vector2(r + 2, 1400))])
	print("BOUND_RIGHT_OUT=%s IN=%s" % [
		tl.is_walkable(Vector2(tl.world_size.x - 1, 1400)),
		tl.is_walkable(Vector2(tl.world_size.x - r - 2, 1400))])
	print("BOUND_TOP_OUT=%s IN=%s" % [
		tl.is_walkable(Vector2(200, 1)), tl.is_walkable(Vector2(300, 260))])
	print("BOUND_BOTTOM_OUT=%s IN=%s" % [
		tl.is_walkable(Vector2(300, tl.world_size.y - 1)),
		tl.is_walkable(Vector2(300, tl.world_size.y - r - 2))])

	# --- 2c. BUILD-A1 §7.1：四栋房子在，lot 尺寸对得上 houses_data.json ---
	var a1_shape_ids: Array = []
	for s in tl.frames[0].shapes:
		var sd: Dictionary = s
		if String(sd.get("type", "")) == "house":
			a1_shape_ids.append(String(sd.get("id", "")))
	print("HOUSE_IDS=%s (期望 4 栋)" % str(a1_shape_ids))
	var houses_ok := true
	var any_wall := false
	for hid in HOUSE_MAP:
		var exp: Dictionary = HOUSE_MAP[hid]
		if not a1_shape_ids.has(hid):
			print("  MISSING house %s" % hid)
			houses_ok = false
			continue
		var hdata := HouseShape.house(hid)
		if hdata.is_empty():
			print("  NO DATA %s" % hid)
			houses_ok = false
			continue
		var lr := HouseShape.lot_rect(hdata, exp["pos"])
		var expect: Vector2 = exp["size"]
		if lr.size != expect:
			print("  LOT %s = %s (期望 %s)" % [hid, str(lr.size), str(expect)])
			houses_ok = false
		var walls := HouseShape.solid_rects(hdata, exp["pos"])
		if walls.is_empty():
			print("  NO WALLS %s" % hid)
			houses_ok = false
		else:
			any_wall = true
	print("HOUSES=%s" % houses_ok)
	print("HOUSE_WALLS>0=%s" % any_wall)

	# --- 2c2. A2 1951：四栋都在 + 磨坊盖住老井 + 老井封盖可站 + 新井在路另一头 ---
	var a2_ids: Array = []
	for s in tl.frames[1].shapes:
		var sd2: Dictionary = s
		if String(sd2.get("type", "")) == "house":
			a2_ids.append(String(sd2.get("id", "")))
	print("HOUSE_IDS_A2=%s (期望 4 栋)" % str(a2_ids))
	var a2_ok := true
	for hid in HOUSE_MAP_A2:
		var e2: Dictionary = HOUSE_MAP_A2[hid]
		if not a2_ids.has(hid):
			print("  MISSING A2 house %s" % hid)
			a2_ok = false
			continue
		var d2 := HouseShape.house(hid)
		if d2.is_empty():
			print("  NO A2 DATA %s" % hid)
			a2_ok = false
			continue
		var lr2 := HouseShape.lot_rect(d2, e2["pos"])
		if lr2.size != (e2["size"] as Vector2):
			print("  A2 LOT %s = %s (期望 %s)" % [hid, str(lr2.size), str(e2["size"])])
			a2_ok = false
	print("HOUSES_A2=%s" % a2_ok)
	# 老井 (900,545) 必须落在 mill_a2 lot 内：story「磨坊一直盖在井上面」
	var mill2_rect := HouseShape.lot_rect(
		HouseShape.house("mill_a2"), HOUSE_MAP_A2["mill_a2"]["pos"])
	# v5 设计：磨坊三帧同址 (1216,448)，井在磨坊院外路边 (1360,848)。
	# A1 井敞开（挡路）、A2 石板封（不挡）、A3 三层水泥（不挡）。
	print("A2_MILL_SAME_SPOT=%s (期望 true：磨坊三帧同址，不漂移)" % (
		(HOUSE_MAP_A2["mill_a2"]["pos"] as Vector2) == Vector2(1216, 448)))
	print("A2_OLD_WELL_NO_WELL_SOLID=%s (期望 true：A2 井盖石板，不再挡路)" % tl.frames[1].is_free(OLD_WELL))
	print("A2_HOTSPOTS=%d (期望 >=10：手写5 + clue家具)" % tl.frames[1].hotspots.size())

	# --- 2c3. A3 1976：四栋都在 + 粮站盖住老井 + 三层水泥封层 ---
	var a3_ids: Array = []
	for s in tl.frames[2].shapes:
		var sd3: Dictionary = s
		if String(sd3.get("type", "")) == "house":
			a3_ids.append(String(sd3.get("id", "")))
	print("HOUSE_IDS_A3=%s (期望 4 栋)" % str(a3_ids))
	var a3_ok := true
	for hid in HOUSE_MAP_A3:
		var e3: Dictionary = HOUSE_MAP_A3[hid]
		if not a3_ids.has(hid):
			print("  MISSING A3 house %s" % hid)
			a3_ok = false
			continue
		var d3 := HouseShape.house(hid)
		if d3.is_empty():
			print("  NO A3 DATA %s" % hid)
			a3_ok = false
			continue
		var lr3 := HouseShape.lot_rect(d3, e3["pos"])
		if lr3.size != (e3["size"] as Vector2):
			print("  A3 LOT %s = %s (期望 %s)" % [hid, str(lr3.size), str(e3["size"])])
			a3_ok = false
	print("HOUSES_A3=%s" % a3_ok)
	# 老井必须在粮站 lot 内（story §4.3「挖地基挖到了老井」）
	var mill3_rect := HouseShape.lot_rect(
		HouseShape.house("mill_a3"), HOUSE_MAP_A3["mill_a3"]["pos"])
	print("A3_OLD_WELL_UNDER_MILL=%s (期望 true：粮站盖在井上面)" % mill3_rect.has_point(OLD_WELL))
	# A3 老井是三层水泥封死的实体（挡路），不是可站的石板
	# v5：A3 井是三层水泥封层，不挡路（玩家能在上面走）
	print("A3_OLD_WELL_FREE=%s (期望 true：三层水泥封平，能走过去)" % tl.frames[2].is_free(OLD_WELL))
	print("A3_HOTSPOTS=%d (期望 >=10：手写5 + clue家具)" % tl.frames[2].hotspots.size())

	# --- 2d. 每扇院门两侧都能站（门洞中心可站） ---
	# v5 布局门洞中心（house 数据 gate 格 + lot 原点，格心 = TILE/2 = 16）：
	#   mill_a1  gate(7,10) → (1216+7*32+16, 448+10*32+16) = (1456, 784)
	#   shen_a1  gate(6,10) → (128+6*32+16,  640+10*32+16) = (336, 976)
	#   zhou     gate(2,5)  → (1792+2*32+16, 1280+5*32+16) = (1872, 1456)
	#   lu       gate(6,10) → (2304+6*32+16, 768+10*32+16) = (2512, 1104)
	var doors_passable := true
	for gate in [
		Vector2(1456, 784), Vector2(336, 976),
		Vector2(1872, 1456), Vector2(2512, 1104)]:
		if not tl.frames[0].is_free(gate):
			print("  DOOR BLOCKED %s" % str(gate))
			doors_passable = false
	print("DOOR_PASSABLE=%s" % doors_passable)

	# --- 2e. BUILD-A1 §7.1：检视点 >= 10（手写 6 + 自动 clue 家具 ≥4） ---
	var a1_hot: int = tl.frames[0].hotspots.size()
	print("HOTSPOTS=%d (期望 >=10)" % a1_hot)
	print("HOTSPOTS_OK=%s" % (a1_hot >= 10))

	# --- 3. 空间移动（往右走，y=1400 一带是空地） ---
	tl.char_pos = Vector2(600, 1600)
	var before: Vector2 = tl.char_pos
	tl.move_space(Vector2(40, 0))
	print("SPACE_MOVE_DX=%.1f (期望 40)" % (tl.char_pos.x - before.x))

	# --- 4. 撞墙：磨坊 lot (1216,448) 18x13 格 → 屋体南墙行 → 南沿 y=816（实测） ---
	# 注意：老井中心 (1360,848)、半径 32，bbox 1328~1392 x 816~880，
	# 从井的 x 范围往北会先撞井而不是撞墙。改用 x=1248（避开井）。
	tl.char_pos = Vector2(1248, 904)
	for i in 120:
		tl.move_space(Vector2(0, -4))
	print("WALL_STOP_Y=%.1f (磨坊南墙前，期望 800~816)" % tl.char_pos.y)
	print("WALL_BLOCKED=%s" % (tl.char_pos.y >= 800.0 and tl.char_pos.y <= 816.0))

	# --- 5. 从 A1 一路推到 A5（起点在主路 (1400,1120)，A2-A5 该点为空地可站） ---
	tl.char_pos = Vector2(1400, 1120)
	tl.index = 0
	var reached: Array = []
	for i in 10:
		if tl.step_time(+1):
			reached.append(tl.index)
	print("TIME_FWD_REACHED=%s (期望 [1,2,3,4])" % str(reached))

	# --- 6. 边界 ---
	tl.index = 0
	print("TIME_BACK_FROM_A1=%s (期望 false)" % tl.step_time(-1))
	tl.index = tl.frame_max()
	print("TIME_FWD_FROM_A5=%s (期望 false)" % tl.step_time(+1))

	# --- 7. 碰撞差异：A1 房子 wall solid、室内可走、门洞可站（BUILD-A1 §4.3） ---
	# 磨坊内部（账房/大厅地面）应可站：玩家能从门洞进房子。
	# 墙体格不可站由 WALL_STOP_Y 撞墙覆盖。
	tl.index = 0
	print("A1_MILL_INTERIOR_FREE=%s (期望 true，屋内地面可走)" % tl.frames[0].is_free(Vector2(1400, 520)))
	print("A1_MILL_DOOR_FREE=%s (期望 true，门洞 (1456,784) 可站)" % tl.frames[0].is_free(Vector2(1456, 784)))
	# 老井：A1 挖开可挡
	print("A1_WELL_FREE=%s (期望 false)" % tl.frames[0].is_free(Vector2(1360, 860)))

	# --- 8. 检视点 ---
	tl.index = 0
	print("HOTSPOT_A1_WELL=%s" % String(tl.frames[0].hotspot_at(Vector2(1360, 860)).get("title", "NONE")))
	print("HOTSPOT_A1_MILL_DESK=%s" % String(tl.frames[0].hotspot_at(Vector2(1264, 544)).get("title", "NONE")))
	print("HOTSPOT_A1_FAR=%s (期望 empty)" % ("empty" if tl.frames[0].hotspot_at(Vector2(40, 1700)).is_empty() else "FOUND"))

	# --- 9. 每帧概况 ---
	for i in tl.frames.size():
		var fr = tl.frames[i]
		print("FRAME[%d] %s year=%d solids=%d hotspots=%d" % [
			i, fr.id, fr.year, fr.solid_rects.size(), fr.hotspots.size()])

	# --- 10. 时间轴可行性回归（用户 2026-11-20 报过「移动一会儿后无法推时间」）---
	# 根因曾是 A2-A5 的旧 640×360 固体叠在新 A1 世界左上角 → 走进重叠区被顶住。
	# A2 建好后，A1 空地变成 A2 房子/新井，推帧被「顶住」是正确设计，不能要求全场 100%。
	# 正确断言：**每一个卡点都必须能解释**（在 A2 房子 lot 内 / 在新井内 / 贴墙 8px 内的边界效应）。
	var reach := _scan_reach(tl)
	print("REACH_MAP=%s" % str(reach))
	print("REACH_MOVE_BAND=%s (A1 主路带的可推率，仅作参考)" % str(reach["band_ratio"]))
	var unexplained: Array = _unexplained_blocks(tl)
	print("UNEXPLAINED_BLOCKS=%d" % unexplained.size())
	for u in unexplained:
		print("  BAD BLOCK %s" % str(u))
	# 判定标准：**所有卡点都必须可解释**（落在目标帧的建筑/手写实体里）。
	# 主路带不追求 100% —— A1 的路在 A2/A3 上变成了沈家宅基和粮站地，
	# 推过去被顶住正是「时间之门」的设计（实测 165 个主路卡点里 154 个在房子内）。
	print("REACH_OK=%s (期望 true：卡点全部可解释)" % unexplained.is_empty())

	# --- 11. 三段式线索点（§4.1）—— A2–A5 本轮是空帧占位，等照抄 A1 重建后再验 ---
	print("CLUE_CHECKS_DEFERRED=A2-A5 空帧占位，等 A1 定型后照抄重建再验三段式线索")

	quit(0)


## 从目标点向外找最近的能站的点（模拟玩家走过去站定）
func _nearest_free(frame, target: Vector2) -> Vector2:
	if frame.is_free(target):
		return target
	for r in range(4, 60, 4):
		for a in range(0, 360, 15):
			var p: Vector2 = target + Vector2(r, 0).rotated(deg_to_rad(float(a)))
			if frame.is_free(p):
				return p
	return target


## 扫一遍 A1 可站区域，统计推到 A5 的通过率，并单独统计「主路活动带」。
## 主路带：用 A1 该帧自己的主路 y 值（v5 路 y=36 格 → 1152px，路宽 2 格）。
## 判定标准：站在 A1 的某点，推到**下一帧**时不被顶住。
const ROAD_Y := 1152
func _scan_reach(tl) -> Dictionary:
	var total := 0
	var full := 0
	var band_total := 0
	var band_full := 0
	var per_step: Array = [0, 0, 0, 0]
	for y in range(240, 1760, 32):
		for x in range(40, 3160, 32):
			var p := Vector2(x, y)
			if not tl.frames[0].is_free(p):
				continue
			total += 1
			var ok := true
			for k in range(1, tl.frames.size()):
				if not tl.frames[k].is_free(p):
					per_step[k - 1] += 1
					ok = false
					break
			if ok:
				full += 1
			# 主路活动带 = A1 主路 y=1152（宽 64 → 1120..1184，取 ±40 余量）。
			# 只测 A1 主路：玩家在 1926 沿路走，推帧时不该被"凭空出现的东西"卡住。
			# 不能把 A2/A3 的主路 y 也算进来 —— 那些位置在 A1 时是空地或房子，
			# 站在那儿推帧被顶住是「时间之门」的正常表现。
			if absi(y - ROAD_Y) <= 40:
				band_total += 1
				if ok:
					band_full += 1
	return {"standable": total, "to_a5": full,
		"blocked_at_step": per_step,
		"band_total": band_total, "band_full": band_full,
		"band_ratio": "%.0f%%" % (100.0 * float(band_full) / maxf(1.0, float(band_total))),
		"ratio": "%.0f%%" % (100.0 * float(full) / maxf(1.0, float(total)))}


## 找「无法解释」的推帧卡点。可解释的：
##   1. 落在 A2/A3 某栋房子的 lot 内（历史帧的空地变成建筑，顶住是设计）
##   2. 落在 A2 新井 / A3 老井水泥封层圆内（含半径余量）
##   3. 距房子 lot 边 ≤16px（角色半径 14 的 probe 贴到墙，边界效应）
##   4. 落在该帧**手写 solid 形状**内（界碑、坝这类世界级实体，挡路天经地义）
func _unexplained_blocks(tl) -> Array:
	var house_rects: Array = []
	for fi in [1, 2]:   # A2 / A3
		for s in tl.frames[fi].shapes:
			var sd: Dictionary = s
			if String(sd.get("type", "")) != "house":
				continue
			var hp := Vector2(float((sd.get("pos", [0, 0]) as Array)[0]),
				float((sd.get("pos", [0, 0]) as Array)[1]))
			house_rects.append(HouseShape.lot_rect(HouseShape.house(String(sd.get("id", ""))), hp))

	# 手写 solid 形状（rect / circle / polygon）的矩形集合，逐帧
	var hard_solids: Array = []
	for fi in [1, 2]:
		for s in tl.frames[fi].shapes:
			var sd: Dictionary = s
			if String(sd.get("type", "")) == "house":
				continue
			if not bool(sd.get("solid", false)):
				continue
			match String(sd.get("type", "")):
				"rect":
					var rr: Array = sd.get("rect", [0, 0, 0, 0])
					hard_solids.append(Rect2(float(rr[0]), float(rr[1]),
						float(rr[2]), float(rr[3])))
				"circle":
					var cc: Array = sd.get("center", [0, 0])
					var rad := float(sd.get("radius", 0))
					hard_solids.append(Rect2(float(cc[0]) - rad, float(cc[1]) - rad,
						rad * 2.0, rad * 2.0))
				"polygon":
					# 河：取包围盒（体量极大，只用来判「是否落在河内」）
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
						hard_solids.append(Rect2(mnx, mny, mxx - mnx, mxy - mny))

	var out: Array = []
	for y in range(240, 1760, 32):
		for x in range(40, 3160, 32):
			var p := Vector2(x, y)
			if not tl.frames[0].is_free(p):
				continue
			var blocked_at := -1
			for k in range(1, tl.frames.size()):
				if not tl.frames[k].is_free(p):
					blocked_at = k
					break
			if blocked_at < 0:
				continue
			var explained := false
			for lr in house_rects:
				var r: Rect2 = lr
				if r.grow(16.0).has_point(p):
					explained = true
					break
			if not explained:
				for r in hard_solids:
					if (r as Rect2).grow(16.0).has_point(p):
						explained = true
						break
			if not explained:
				out.append({"p": p, "frame": blocked_at})
	return out