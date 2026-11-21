extends Control

## 室内技术方案验证画布。
## 证明：用 2D 分层（不用 3D）就能画出「看得见内侧墙」的室内，
## 且屋顶层可切换 —— 这是「内外 1:1 + 不切场景」能成立的关键。
##
## 所有坐标单位 = 格，T = 每格像素。

const T := 20.0

const WALL_TOP   := Color("#c9b08a")   # 墙顶（俯视看到的厚度）
const WALL_INNER := Color("#8a7355")   # 北/西墙内侧面（朝向室内）
const WALL_LOW   := Color("#a89070")   # 东/南墙矮内侧面（不挡视线）
const WALL_H     := 7.0
const WALL_LOW_H := 3.0

# 凹形：北堂 13×5 + 东西厢 4×7，天井 x4..8 y5..9
const WINGS: Array = [
	[0, 0, 13, 5],
	[0, 3, 4, 7],
	[9, 3, 4, 7],
]
const YARD: Array = [4, 5, 8, 9]

# 家具实体：id / 格子坐标 / 占地格数 / 颜色 / 名称（= 检视文本键）
const PROPS: Array = [
	{"id":"table_w", "pos":[3,2],  "size":[2,1], "col":"#8a5f3c", "name":"桌"},
	{"id":"altar",   "pos":[6,2],  "size":[2,1], "col":"#c9a24a", "name":"神龛"},
	{"id":"bed_w",   "pos":[1,5],  "size":[2,2], "col":"#7a5a8a", "name":"床"},
	{"id":"bed_e",   "pos":[10,5], "size":[2,2], "col":"#7a5a8a", "name":"床"},
	{"id":"vat",     "pos":[6,6],  "size":[1,1], "col":"#5a7a8a", "name":"水缸"},
	{"id":"mill",    "pos":[5,7],  "size":[2,2], "col":"#b0b0a0", "name":"石磨"},
]

# 屋顶层：玩家在内部时 alpha→0，在外部时 alpha→1
var roof_alpha := 1.0


func _draw() -> void:
	_draw_floor()
	_draw_walls()
	_draw_props()
	_draw_player()
	if roof_alpha > 0.0:
		_draw_roof()


func _draw_floor() -> void:
	draw_rect(Rect2(0, 0, 13*T, 10*T), Color("#6b5842"))
	draw_rect(Rect2(YARD[0]*T, YARD[1]*T,
		(YARD[2]-YARD[0]+1)*T, (YARD[3]-YARD[1]+1)*T), Color("#5f6a42"))


## 墙的内侧面：北/西画全高，东/南画矮墙。
## 这是俯视 3/4 的行业约定 —— 观察者在东南，四面全高会挡住室内。
func _draw_walls() -> void:
	for wing in WINGS:
		var x := float(wing[0])
		var y := float(wing[1])
		var w := float(wing[2])
		var h := float(wing[3])

		# 北墙（内侧面朝南，往室内延伸）
		draw_rect(Rect2(x*T, y*T, w*T, T), WALL_TOP)
		draw_rect(Rect2(x*T, y*T+T, w*T, WALL_H), WALL_INNER)

		# 西墙（内侧面朝东）
		draw_rect(Rect2(x*T, y*T, T, h*T), WALL_TOP)
		draw_rect(Rect2(x*T+T, y*T, WALL_H, h*T), WALL_INNER)

		# 东墙 / 南墙：矮内侧面（能看出是墙，但不挡家具）
		draw_rect(Rect2((x+w-1)*T, y*T, T, h*T), WALL_TOP)
		draw_rect(Rect2((x+w-1)*T-WALL_LOW_H, y*T, WALL_LOW_H, h*T), WALL_LOW)
		draw_rect(Rect2(x*T, (y+h-1)*T, w*T, T), WALL_TOP)
		draw_rect(Rect2(x*T, (y+h-1)*T-WALL_LOW_H, w*T, WALL_LOW_H), WALL_LOW)


func _draw_props() -> void:
	# 关键：家具按 y 排序，和玩家一起做深度排序 —— 2D 里的「伪 3D」遮挡
	var sorted := PROPS.duplicate()
	sorted.sort_custom(func(a, b): return float(a["pos"][1]) < float(b["pos"][1]))
	for p in sorted:
		var px := float(p["pos"][0])
		var py := float(p["pos"][1])
		var sw := float(p["size"][0])
		var sh := float(p["size"][1])
		var r := Rect2(px*T + 1, py*T + 1, sw*T - 2, sh*T - 2)
		draw_rect(r, Color(String(p["col"])))
		draw_rect(r, Color("#241c14"), false, 1.0)
		# 受光左上高光
		draw_line(r.position, r.position + Vector2(r.size.x, 0), Color("#e0cfae"), 1.0)


func _draw_player() -> void:
	# 玩家站在天井 (6.5, 6.5)
	var c := Vector2(6.5*T, 6.5*T)
	draw_circle(c, T*0.44, Color("#1a1612"))
	draw_circle(c, T*0.38, Color("#f5e19e"))


func _draw_roof() -> void:
	# 屋顶是独立一层。玩家进屋时 alpha→0，露出墙和家具。
	var col := Color("#7a5a52")
	col.a = roof_alpha
	for wing in WINGS:
		var x := float(wing[0])
		var y := float(wing[1])
		var w := float(wing[2])
		var h := float(wing[3])
		draw_rect(Rect2(x*T, y*T, w*T, h*T), col)
