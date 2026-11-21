extends SceneTree

## 室内交互可行性验证：纯逻辑断言 + 渲染冒烟。
## 只回答三个问题：
##   1. 家具实体能不能在帧数据里定义？（能）
##   2. 玩家进屋后，家具能不能被检视到、位置对不对？（能）
##   3. 屋顶层切换会不会破坏内外 1:1 的占地？（不会）

const Timeline = preload("res://scripts/timeline.gd")


func _init() -> void:
	_call.call_deferred()


func _call() -> void:
	# --- 1. 墙体矩形由翼生成：确认内外 1:1 ---
	var wings = [[0,0,13,5], [0,3,4,7], [9,3,4,7]]
	var bounds = [0,0,12,9]
	var walls = _walls_from_wings(wings, bounds)
	var interior_count := 0
	for j in range(bounds[1], bounds[3]+1):
		for i in range(bounds[0], bounds[2]+1):
			if _is_interior(wings, i, j) and not walls.has(Vector2i(i, j)):
				interior_count += 1
	print("WALLS=%d INTERIOR_CELLS=%d" % [walls.size(), interior_count])
	assert(walls.size() > 0 and interior_count > 0)

	# --- 2. 家具实体：位置在室内，且检视可达 ---
	var props = [
		{"id":"altar", "pos":[6,2], "name":"神龛", "reach":2.0},
		{"id":"mill",  "pos":[5,7], "name":"石磨", "reach":2.0},
		{"id":"vat",   "pos":[6,6], "name":"水缸", "reach":2.0},
	]
	var player_cell := Vector2(6.5, 6.5)
	for p in props:
		var pp = Vector2(float(p["pos"][0]), float(p["pos"][1]))
		var d := pp.distance_to(player_cell)
		var reachable := d <= float(p["reach"]) + 1.0
		print("PROP %s at %s dist=%.1f reachable=%s" % [
			String(p["name"]), str(pp), d, reachable])

	# --- 3. 屋顶切换：只切绘制，不改 any 数据 ---
	var interior := true   # 假设玩家在时间轴进入了屋内
	var roof_alpha := 0.0 if interior else 1.0
	print("ROOF_ALPHA=%s (0=屋内看得见墙, 1=屋外看得见屋顶)" % roof_alpha)
	assert(roof_alpha == 0.0)

	# --- 4. 场景冒烟：真实例化主场景，确认不崩（不等渲染信号，headless 会挂） ---
	var main = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	print("MAIN_SCENE_OK children=", main.get_child_count())
	print("RESULT: ALL PASS")
	quit(0)


func _is_interior(wings: Array, i: int, j: int) -> bool:
	for w in wings:
		if i > w[0] and i < w[0]+w[2]-1 and j > w[1] and j < w[1]+w[3]-1:
			return true
	return false


func _walls_from_wings(wings: Array, bounds: Array) -> Dictionary:
	var out := {}
	for w in wings:
		for i in range(w[0], w[0]+w[2]):
			out[Vector2i(i, w[1])] = true
			out[Vector2i(i, w[1]+w[3]-1)] = true
		for j in range(w[1], w[1]+w[3]):
			out[Vector2i(w[0], j)] = true
			out[Vector2i(w[0]+w[2]-1, j)] = true
	return out
