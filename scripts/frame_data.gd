extends RefCounted

## 一帧的静态数据：地面色、图形列表、阻挡矩形、可检视点。
##
## 关键设计：所有判定都用「纯数据 + AABB 数学」，不建任何 CollisionShape2D。
## 这样绕开了 Godot「visible=false 不关碰撞」的坑（HANDOFF §3.3），
## 也绕开了「目标帧还没激活时无法用物理引擎做重叠检测」的问题（§3.4）。
##
## 刻意不用 class_name：class_name 要靠编辑器扫描写进全局类缓存，
## 命令行 / 导出时缓存可能是旧的，会报 "Could not find type"。
## 用 preload 常量引用，任何环境都能跑。
## 同理这里也不能在脚本内部引用自己的类型名 —— 所以构造走 setup()，不是静态工厂。

const CHAR_RADIUS := 14.0

const HouseShape = preload("res://scripts/house_shape.gd")

var id: String = ""
var year: int = 0
var ground: Color = Color.BLACK
var shapes: Array = []        # 每项是 Dictionary，直接来自 frames.json
var solid_rects: Array = []   # Array[Rect2]，参与行走/推时间判定的阻挡
var hotspots: Array = []      # Array[Dictionary]


func setup(d: Dictionary) -> void:
	id = String(d.get("id", ""))
	year = int(d.get("year", 0))
	ground = Color(String(d.get("ground", "#000000")))

	shapes.clear()
	solid_rects.clear()
	hotspots.clear()

	for s in d.get("shapes", []):
		var sd: Dictionary = s
		shapes.append(sd)
		if not bool(sd.get("solid", false)):
			continue
		# 只有矩形、圆形、房子可以阻挡；路径和纯装饰不参与。
		match String(sd.get("type", "")):
			"rect":
				solid_rects.append(_rect_from(sd))
			"circle":
				var c: Array = sd.get("center", [0, 0])
				var r := float(sd.get("radius", 0))
				solid_rects.append(Rect2(
					float(c[0]) - r, float(c[1]) - r, r * 2.0, r * 2.0))
			"polygon":
				# 多边形（河）：转成若干个行切片矩形参与 AABB 判定。
				# 直接做多边形点包含判定也可以，但 AABB 与现有 is_free() 一致、更快。
				var ppts: Array = sd.get("points", [])
				if ppts.size() >= 3:
					solid_rects.append_array(_polygon_scanlines(ppts))
			"house":
				# 房子：墙逐段进 solid_rects（门洞留空、lot 边界不阻挡）；
				# clue 家具自动加成检视点（BUILD-A1 §5）
				var sid := String(sd.get("id", ""))
				var sp: Array = sd.get("pos", [0, 0])
				var hpos := Vector2(float(sp[0]), float(sp[1]))
				var hdata := HouseShape.house(sid)
				if hdata.is_empty():
					push_warning("house 形状没有对应数据：%s" % sid)
					continue
				solid_rects.append_array(HouseShape.solid_rects(hdata, hpos))
				hotspots.append_array(HouseShape.hotspots(hdata, hpos, year))

	for h in d.get("hotspots", []):
		var hd: Dictionary = (h as Dictionary).duplicate()
		var p: Array = hd.get("pos", [0, 0])
		hd["pos"] = Vector2(float(p[0]), float(p[1]))
		if not hd.has("reach"):
			hd["reach"] = 68.0
		hd["reach"] = float(hd["reach"])
		hotspots.append(hd)


func _rect_from(sd: Dictionary) -> Rect2:
	var r: Array = sd.get("rect", [0, 0, 0, 0])
	return Rect2(float(r[0]), float(r[1]), float(r[2]), float(r[3]))


## 把多边形按 16px 一条水平扫描线切成矩形（河的下缘是弯的，直接包围盒会挡住陆地）。
## 16px 一条对玩家碰撞足够精确（角色半径 14），又不会让 solid_rects 爆炸。
func _polygon_scanlines(ppts: Array) -> Array:
	var min_y := INF
	var max_y := -INF
	for p in ppts:
		var pa: Array = p
		min_y = minf(min_y, float(pa[1]))
		max_y = maxf(max_y, float(pa[1]))
	if not is_finite(min_y) or not is_finite(max_y):
		return []
	var out: Array = []
	var step: float = 16.0
	var y: float = floor(min_y / step) * step
	while y < max_y:
		# 求该扫描线与多边形各边的交点
		var xs: Array = []
		for i in ppts.size():
			var a: Array = ppts[i]
			var b: Array = ppts[(i + 1) % ppts.size()]
			var y1: float = float(a[1])
			var y2: float = float(b[1])
			if (y1 <= y and y2 > y) or (y2 <= y and y1 > y):
				var x1: float = float(a[0])
				var x2: float = float(b[0])
				var t: float = (y - y1) / (y2 - y1)
				xs.append(x1 + (x2 - x1) * t)
		if xs.size() >= 2:
			xs.sort()
			var i2 := 0
			while i2 + 1 < xs.size():
				var xa: float = float(xs[i2])
				var xb: float = float(xs[i2 + 1])
				if xb > xa:
					out.append(Rect2(xa, y, xb - xa, step))
				i2 += 2
		y += step
	return out


## 某个点能不能站（角色中心 + 半径的方形范围不与任何阻挡相交）
func is_free(at: Vector2) -> bool:
	var probe := Rect2(
		at.x - CHAR_RADIUS, at.y - CHAR_RADIUS,
		CHAR_RADIUS * 2.0, CHAR_RADIUS * 2.0)
	for r in solid_rects:
		if (r as Rect2).intersects(probe):
			return false
	return true


## 找离 pos 最近、在 reach 内的可检视点。没有就返回空字典。
func hotspot_at(pos: Vector2) -> Dictionary:
	var best: Dictionary = {}
	var best_d := INF
	for h in hotspots:
		var d: float = (h["pos"] as Vector2).distance_to(pos)
		if d <= float(h["reach"]) and d < best_d:
			best_d = d
			best = h
	return best