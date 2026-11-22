extends Node2D

## 主角。灰盒阶段就是一个圆 + 一个小三角（朝向）。
##
## 时间轴模式下：位置完全不动，但播放走路动画 + 残影拖尾。
## HANDOFF §2.4 说这三个条件缺一不可，本题三件都做：
##   镜头不动（本来就没有 camera）、世界在动（帧在推）、身后有残影。
##
## 2026-11-22 星露谷视觉机制（DECIDE D4）：本节点**只存状态**，不再自己画。
##   以前靠 z_index = 10 把自己叠在全世界最上 —— 绕到房子后面仍然盖在屋顶上，
##   伪 3D 直接失效。现在像素由 world_view 的 y-sort 循环在正确深度上画出来
##   （world_view 调 draw_self()）。所以这里**不能**再设 z_index。

const BODY := Color(0.96, 0.88, 0.62)
const BODY_DIM := Color(0.62, 0.60, 0.52)
const OUTLINE := Color(0.12, 0.10, 0.08)
const RADIUS := 14.0
const TRAIL := 4

var time_mode := false
var facing := Vector2.DOWN
var walk_phase := 0.0
var walking := false
var bump_kick := 0.0     # 撞墙时的一个小位移，0.12 秒内衰减

## 绘制目标（world_view）。由 world_view.set_player_ref() 注入。
## 画到谁身上，决定了玩家在 y-sort 链里的深度顺序。
var draw_target: CanvasItem = null


## 本节点不再自己绘制（见文件头注释）。
## 留着这个空函数是为了让「Player 节点只当状态载体」这件事在代码里看得见。
func _draw() -> void:
	pass


## 画玩家。offset = 色差/震屏偏移（世界坐标）。
## 坐标基准 = 本节点的 position（世界坐标，由 main.gd 每帧设成 tl.char_pos）。
## world_view 在排序循环里按 sort_y 轮到玩家时才调它 —— 深度由调用顺序决定。
func draw_self(offset: Vector2 = Vector2.ZERO) -> void:
	var c := draw_target
	if c == null:
		return

	var base := position + offset

	var bob := 0.0
	if walking:
		bob = absf(sin(walk_phase * 9.0)) * 3.2

	# 时间轴模式的残影：沿朝向反方向排开，越远越淡
	if time_mode and walking:
		for i in range(TRAIL, 0, -1):
			var t := float(i) / float(TRAIL + 1)
			var off := -facing * (float(i) * 6.4)
			var a := 0.30 * (1.0 - t)
			c.draw_circle(base + off, RADIUS - 0.5,
				Color(BODY_DIM.r, BODY_DIM.g, BODY_DIM.b, a))

	var kick := facing * bump_kick * -1.0
	var col := BODY
	c.draw_circle(base + kick, RADIUS + 1.0, OUTLINE)
	c.draw_circle(base + kick + Vector2(0, -bob), RADIUS, col)

	# 朝向小三角
	var tip: Vector2 = base + kick + Vector2(0, -bob) + facing * (RADIUS + 6.0)
	var left: Vector2 = base + kick + Vector2(0, -bob) + facing.rotated(2.4) * (RADIUS + 2.0)
	var right: Vector2 = base + kick + Vector2(0, -bob) + facing.rotated(-2.4) * (RADIUS + 2.0)
	c.draw_colored_polygon(PackedVector2Array([tip, left, right]), col)

	# 空间轴模式下的脚下影子，帮玩家判断站立点
	if not time_mode:
		c.draw_circle(base + Vector2(0, RADIUS * 0.7), RADIUS * 0.9, Color(0, 0, 0, 0.16))


func _process(delta: float) -> void:
	if bump_kick > 0.0:
		bump_kick = maxf(0.0, bump_kick - delta * 40.0)
		queue_redraw()
