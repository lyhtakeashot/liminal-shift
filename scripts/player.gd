extends Node2D

## 主角。灰盒阶段就是一个圆 + 一个小三角（朝向）。
##
## 时间轴模式下：位置完全不动，但播放走路动画 + 残影拖尾。
## HANDOFF §2.4 说这三个条件缺一不可，本题三件都做：
##   镜头不动（本来就没有 camera）、世界在动（帧在推）、身后有残影。

const BODY := Color(0.96, 0.88, 0.62)
const BODY_DIM := Color(0.62, 0.60, 0.52)
const OUTLINE := Color(0.12, 0.10, 0.08)
const RADIUS := 7.0
const TRAIL := 4

var time_mode := false
var facing := Vector2.DOWN
var walk_phase := 0.0
var walking := false
var bump_kick := 0.0     # 撞墙时的一个小位移，0.12 秒内衰减


func _ready() -> void:
	z_index = 10


func _draw() -> void:
	var bob := 0.0
	if walking:
		bob = absf(sin(walk_phase * 9.0)) * 1.6

	# 时间轴模式的残影：沿朝向反方向排开，越远越淡
	if time_mode and walking:
		for i in range(TRAIL, 0, -1):
			var t := float(i) / float(TRAIL + 1)
			var off := -facing * (float(i) * 3.2)
			var a := 0.30 * (1.0 - t)
			draw_circle(off, RADIUS - 0.5, Color(BODY_DIM.r, BODY_DIM.g, BODY_DIM.b, a))

	var kick := facing * bump_kick * -1.0
	var c := BODY if not time_mode else BODY
	draw_circle(kick, RADIUS + 1.0, OUTLINE)
	draw_circle(kick + Vector2(0, -bob), RADIUS, c)

	# 朝向小三角
	var tip: Vector2 = kick + Vector2(0, -bob) + facing * (RADIUS + 3.0)
	var left: Vector2 = kick + Vector2(0, -bob) + facing.rotated(2.4) * (RADIUS + 1.0)
	var right: Vector2 = kick + Vector2(0, -bob) + facing.rotated(-2.4) * (RADIUS + 1.0)
	draw_colored_polygon(PackedVector2Array([tip, left, right]), c)

	# 空间轴模式下的脚下影子，帮玩家判断站立点
	if not time_mode:
		draw_circle(Vector2(0, RADIUS * 0.7), RADIUS * 0.9, Color(0, 0, 0, 0.16))


func _process(delta: float) -> void:
	if bump_kick > 0.0:
		bump_kick = maxf(0.0, bump_kick - delta * 40.0)
		queue_redraw()