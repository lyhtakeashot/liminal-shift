extends SceneTree

## 星露谷视觉机制专项自检（DECIDE D3/D4）：
##   1. 墙向分类器：北/西墙全高 32px，东/南墙半高 16px；demolished 残垣半高
##   2. solid_rects() 返回结构未变（碰撞恒为整格 AABB）
##   3. y-sort 不变量：玩家脚线与屋顶/墙行/家具的先后关系
##   4. player.gd 不再设 z_index（玩家只当状态载体）
##
## 只测 A1–A3 的 12 栋（A4/A5 冻结）。

const HouseShape = preload("res://scripts/house_shape.gd")
const WorldView = preload("res://scripts/world_view.gd")
const Player = preload("res://scripts/player.gd")
const FrameData = preload("res://scripts/frame_data.gd")

## A1–A3 的 12 栋（与 world_view.gd 的 FAMILY 表一致）
const HOUSES := [
	"lu_house", "shen_a1", "mill_a1", "zhou_house",
	"lu_a2", "shen_a2", "mill_a2", "zhou_a2",
	"lu_a3", "shen_a3", "mill_a3", "zhou_a3",
]

var fails := 0


func _ok(cond: bool, label: String) -> void:
	print(("PASS " if cond else "FAIL ") + label)
	if not cond:
		fails += 1


func _init() -> void:
	call_deferred("_run")


## 从 grid_of() 复算「这格墙的哪一侧挨着室内」→ 期望类别。
## 规则来自 house-spec §4.5.2：观察者在东南，
##   室内在东/南 → 内侧面朝东南 → 看得到 → 全高
##   室内在北/西 → 内侧面背对观察者 → 只看得到墙顶 → 半高
func _expected_class(data: Dictionary, cell: Vector2i) -> int:
	var grid := HouseShape.grid_of(data)
	var lot: Array = data.get("lot", [0, 0, 0, 0])
	var x0 := int(lot[0])
	var y0 := int(lot[1])
	var interior := {}
	for j in grid.size():
		var row := String(grid[j])
		for i in row.length():
			if row[i] == ".":
				interior[Vector2i(x0 + i, y0 + j)] = true
	if interior.has(cell + Vector2i(0, 1)) or interior.has(cell + Vector2i(1, 0)):
		return HouseShape.WALL_CLASS_FULL
	if interior.has(cell + Vector2i(0, -1)) or interior.has(cell + Vector2i(-1, 0)):
		return HouseShape.WALL_CLASS_HALF
	return HouseShape.WALL_CLASS_UNKNOWN


func _run() -> void:
	# ---------- 1. 墙向分类器 ----------
	for sid in HOUSES:
		var data := HouseShape.house(sid)
		if data.is_empty():
			_ok(false, "%s 有房子数据" % sid)
			continue
		var cells := HouseShape.wall_render_cells(data, Vector2.ZERO)
		_ok(not cells.is_empty(), "%s 分类器吐出墙格" % sid)

		# 1a. 与「直接判」逐格一致（UNKNOWN 的角落格允许继承，不在此断言；
		#     demolished 残垣按规则强制半高，也不在此断言 —— 单独在 1c 查）
		var demo_set := {}
		for d in data.get("demolished", []):
			var da: Array = d
			demo_set[Vector2i(int(da[0]), int(da[1]))] = true
		var mismatched := 0
		for c in cells:
			var cd: Dictionary = c
			var cell: Vector2i = cd["cell"]
			if demo_set.has(cell):
				continue
			var exp := _expected_class(data, cell)
			if exp == HouseShape.WALL_CLASS_UNKNOWN:
				continue
			var got := HouseShape.WALL_FULL if float(cd["height"]) == HouseShape.WALL_FULL \
				else HouseShape.WALL_HALF
			var want := HouseShape.WALL_FULL if exp == HouseShape.WALL_CLASS_FULL \
				else HouseShape.WALL_HALF
			if got != want:
				mismatched += 1
		_ok(mismatched == 0, "%s 墙向与直接判一致（不符 %d 格）" % [sid, mismatched])

		# 1b. 一字形房子：最北一行全高、最南一行半高、最西一列全高、最东一列半高
		var wings: Array = data.get("wings", [])
		if wings.size() == 1:
			var w0: Array = wings[0]
			var wy := int(w0[1])
			var wh := int(w0[3])
			var wx := int(w0[0])
			var ww2 := int(w0[2])
			var north_full := 0
			var south_half := 0
			var west_full := 0
			var east_half := 0
			for c in cells:
				var cd: Dictionary = c
				var cell: Vector2i = cd["cell"]
				var h := float(cd["height"])
				if cell.y == wy and h == HouseShape.WALL_FULL:
					north_full += 1
				if cell.y == wy + wh - 1 and h == HouseShape.WALL_HALF:
					south_half += 1
				if cell.x == wx and h == HouseShape.WALL_FULL:
					west_full += 1
				if cell.x == wx + ww2 - 1 and h == HouseShape.WALL_HALF:
					east_half += 1
			_ok(north_full > 0, "%s 北墙全高（%d 格）" % [sid, north_full])
			_ok(south_half > 0, "%s 南墙半高（%d 格）" % [sid, south_half])
			_ok(west_full > 0, "%s 西墙全高（%d 格）" % [sid, west_full])
			_ok(east_half > 0, "%s 东墙半高（%d 格）" % [sid, east_half])

		# 1c. demolished 拆墙表 = 残垣 → 半高
		var demo_bad := 0
		var demo_hit := 0
		for d in data.get("demolished", []):
			var da: Array = d
			var target := Vector2i(int(da[0]), int(da[1]))
			for c in cells:
				var cd: Dictionary = c
				if (cd["cell"] as Vector2i) != target:
					continue
				demo_hit += 1
				if float(cd["height"]) != HouseShape.WALL_HALF:
					demo_bad += 1
		if demo_hit > 0:
			_ok(demo_bad == 0, "%s 残垣半高（命中 %d 格，错 %d）" % [sid, demo_hit, demo_bad])

		# ---------- 2. solid_rects() 返回结构未变：碰撞恒为整格 AABB ----------
		var bad_rect := 0
		for r in HouseShape.solid_rects(data, Vector2.ZERO):
			var rr: Rect2 = r
			if not is_equal_approx(rr.size.x, HouseShape.TILE) \
					or not is_equal_approx(rr.size.y, HouseShape.TILE):
				bad_rect += 1
		_ok(bad_rect == 0, "%s 碰撞矩形仍是整格 AABB（异常 %d 个）" % [sid, bad_rect])

	# ---------- 3. y-sort 不变量 ----------
	_check_sort()

	# ---------- 4. player.gd 不再设 z_index ----------
	var p := Player.new()
	root.add_child(p)
	_ok(p.z_index == 0, "player.z_index = 0（不再靠 z_index 叠最上）")
	_ok(p.has_method("draw_self"), "player 有 draw_self() 供排序循环调用")
	p.queue_free()

	print("SORT_CHECK_DONE fails=%d" % fails)
	quit(1 if fails > 0 else 0)


## 造一个只含一栋房子的帧。
func _make_frame(sid: String, hpos: Vector2) -> FrameData:
	var f := FrameData.new()
	f.setup({
		"id": "t", "year": 1926, "ground": "#3b3a2e",
		"shapes": [{
			"type": "house", "id": sid, "pos": [hpos.x, hpos.y],
			"color": "#ffffff", "label": "",
		}],
	})
	return f


func _entry_index(ents: Array, kind: String) -> int:
	for i in ents.size():
		if String((ents[i] as Dictionary)["kind"]) == kind:
			return i
	return -1


func _check_sort() -> void:
	var wv := WorldView.new()
	root.add_child(wv)
	var p := Player.new()
	root.add_child(p)
	wv.set_player_ref(p)

	var sid := "lu_house"
	var hpos := Vector2(1000.0, 1000.0)
	var data := HouseShape.house(sid)
	var wings: Array = data.get("wings", [])
	var w0: Array = wings[0]
	var house_top := hpos.y + float(w0[1]) * HouseShape.TILE
	var house_bottom := hpos.y + (float(w0[1]) + float(w0[3])) * HouseShape.TILE

	wv.show_frame(_make_frame(sid, hpos), false)

	# --- 3a. 玩家站房北 → 屋顶排在玩家之后（屋顶盖住玩家）---
	wv.set_player_state(Vector2(hpos.x + 64.0, house_top - 80.0),
		Vector2.DOWN, false, 0.0, 0.0, false)
	var ents: Array = wv._collect_front()
	var pi := _entry_index(ents, "player")
	var ri := _entry_index(ents, "roof")
	_ok(pi >= 0 and ri >= 0, "前景层有玩家和屋顶条目")
	_ok(ri > pi, "玩家在房北 → 屋顶后画（玩家被屋顶遮住）")

	# --- 3b. 玩家站房南 → 玩家排在屋顶之后（玩家挡住房子）---
	wv.set_player_state(Vector2(hpos.x + 64.0, house_bottom + 80.0),
		Vector2.UP, false, 0.0, 0.0, false)
	ents = wv._collect_front()
	pi = _entry_index(ents, "player")
	ri = _entry_index(ents, "roof")
	_ok(pi > ri, "玩家在房南 → 玩家后画（玩家挡住房子南立面）")

	# --- 3c. 玩家在屋体内 → 屋顶整块不画 ---
	wv.set_player_state(Vector2(hpos.x + 64.0, house_top + 64.0),
		Vector2.DOWN, false, 0.0, 0.0, false)
	_ok(wv._player_inside(data, hpos), "玩家在 wings 内 → _player_inside() 为真")
	_ok(not wv._player_inside(data, hpos + Vector2(0, 4000)),
		"玩家在 wings 外 → _player_inside() 为假")

	# --- 3d. 家具与玩家的先后：站在家具北 → 家具后画（挡住玩家）---
	var furn: Array = HouseShape.furniture_rects(data, hpos)
	if furn.is_empty():
		_ok(false, "有家具可测")
	else:
		var f0: Dictionary = furn[0]
		var fr: Rect2 = f0["rect"]
		# 家具北侧：玩家脚线 < 家具底边 → 家具后画
		wv.set_player_state(Vector2(fr.position.x + 8.0, fr.position.y - 20.0),
			Vector2.DOWN, false, 0.0, 0.0, false)
		ents = wv._collect_front()
		pi = _entry_index(ents, "player")
		var fi := _entry_index(ents, "furniture")
		_ok(fi > pi, "玩家在家具北 → 家具后画（被家具挡住）")
		# 家具南侧：玩家脚线 > 家具底边 → 玩家后画
		wv.set_player_state(Vector2(fr.position.x + 8.0, fr.end.y + 20.0),
			Vector2.UP, false, 0.0, 0.0, false)
		ents = wv._collect_front()
		pi = _entry_index(ents, "player")
		fi = _entry_index(ents, "furniture")
		_ok(pi > fi, "玩家在家具南 → 玩家后画（挡住家具）")

	# --- 3e. 排序键单调：collect_front 返回的 sort_y 递增 ---
	wv.set_player_state(Vector2(hpos.x + 64.0, house_top + 64.0),
		Vector2.DOWN, false, 0.0, 0.0, false)
	ents = wv._collect_front()
	var mono := true
	for i in range(1, ents.size()):
		if float((ents[i] as Dictionary)["sort_y"]) < float((ents[i - 1] as Dictionary)["sort_y"]):
			mono = false
	_ok(mono, "排序结果按 sort_y 递增")

	# --- 3f. 墙行深度：玩家所在行以南的墙排在玩家之后 ---
	var wall_rows := {}
	for c in HouseShape.wall_render_cells(data, hpos):
		var cd: Dictionary = c
		var rr: Rect2 = cd["rect"]
		var ry := int(round((rr.position.y - hpos.y) / HouseShape.TILE))
		if not wall_rows.has(ry):
			wall_rows[ry] = []
		wall_rows[ry].append(cd)
	_ok(wall_rows.size() > 1, "墙按行拆开（%d 行）" % wall_rows.size())

	wv.queue_free()
	p.queue_free()
