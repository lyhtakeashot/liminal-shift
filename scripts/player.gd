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
##
## L17 卡墙虚化（house-spec §8.3）：phasing 时整个人半透明 + 轻微冷色，
##   影子也一起淡掉 —— 玩家一眼能看出「我现在是穿在实体里，不是我隐身了」。

const BODY := Color(0.96, 0.88, 0.62)
const BODY_DIM := Color(0.62, 0.60, 0.52)
const OUTLINE := Color(0.12, 0.10, 0.08)
const RADIUS := 14.0
const TRAIL := 4

## 虚化的不透明度。⚠️ 时间轴模式下 world_view 会把玩家画三遍（两遍色差 + 一遍实色），
## 三遍同点叠加后不透明度 = 1-(1-a)^3 ⇒ 单遍 0.40 会合成到 0.78、几乎看不见虚化，
## 所以时间轴模式单遍取 0.16（合成 ≈0.41），空间轴单遍直接 0.40。
const PHASING_ALPHA := 0.40
const PHASING_ALPHA_TIME := 0.16
const PHASING_TINT := Color(0.78, 0.90, 1.0)

## L12/M6：走路动画频率。提速 ×1.5（120→180）后频率同步 ÷1.5（9.0→6.0），
## 否则腿脚比身体快、看着像滑冰。bob 与帧索引必须共用这一个常量（改一漏一会抽搐）。
const WALK_FREQ := 6.0

## 美术主角精灵表（D6 同款约定）：1152×32 = 36 帧，一帧 32×32。
## 分组（美术同学没给方向标记，按帧内容推出来的）：
##   0-3   朝下走   4-7  朝左走   8-11 朝右走   12-15 朝上走（背面）
##   16-20 朝下站   21-25 朝左站   26-30 朝右站   31-35 朝上站（背面）
## 每组 4 帧是行走循环、5 帧是站立循环。
const HERO_SHEET := "res://美术资产/主角/Sprite-主角-Sheet.png"
const HERO_FRAME := 32
const HERO_WALK := {
	"down": [0, 1, 2, 3],
	"left": [4, 5, 6, 7],
	"right": [8, 9, 10, 11],
	"up": [12, 13, 14, 15],
}
const HERO_IDLE := {
	"down": [16, 17, 18, 19, 20],
	"left": [21, 22, 23, 24, 25],
	"right": [26, 27, 28, 29, 30],
	"up": [31, 32, 33, 34, 35],
}

var time_mode := false
var facing := Vector2.DOWN
var walk_phase := 0.0
var walking := false
var phasing := false     # 卡墙虚化中（由 world_view.set_player_state 注入）

## 主角贴图（美术资产）。加载失败 → 回退到原来的圆 + 三角画法。
static var _sheet: Texture2D = null
static var _sheet_tried := false

## 绘制目标（world_view）。由 world_view.set_player_ref() 注入。
## 画到谁身上，决定了玩家在 y-sort 链里的深度顺序。
var draw_target: CanvasItem = null


## 本节点不再自己绘制（见文件头注释）。
## 留着这个空函数是为了让「Player 节点只当状态载体」这件事在代码里看得见。
func _draw() -> void:
	pass


## 画玩家。offset = 色差偏移（世界坐标，时间轴三遍画的 ±1px）。
## 坐标基准 = 本节点的 position（世界坐标，由 main.gd 每帧设成 tl.char_pos）。
## world_view 在排序循环里按 sort_y 轮到玩家时才调它 —— 深度由调用顺序决定。
func draw_self(offset: Vector2 = Vector2.ZERO) -> void:
	var c := draw_target
	if c == null:
		return

	var base := position + offset

	var bob := 0.0
	if walking:
		bob = absf(sin(walk_phase * WALK_FREQ)) * 3.2

	# 美术主角精灵：有贴图就画精灵，没有就回退到圆 + 三角。
	var sheet := _hero_sheet()
	if sheet != null:
		_draw_hero(c, sheet, base, bob)
	else:
		_draw_fallback(c, base, bob)

	# 空间轴模式下的脚下影子，帮玩家判断站立点。
	# 虚化时影子一起淡掉：人穿在实体里却还有实心影子，看着像 bug。
	if not time_mode:
		var sa := 0.16 * (0.35 if phasing else 1.0)
		c.draw_circle(base + Vector2(0, RADIUS * 0.7), RADIUS * 0.9, Color(0, 0, 0, sa))


## 虚化的调制色：不透明度 + 轻微冷色偏（house-spec §8.3「半透明 + 轻微色差」）。
func _phase_tint() -> Color:
	if not phasing:
		return Color(1, 1, 1, 1)
	return Color(PHASING_TINT.r, PHASING_TINT.g, PHASING_TINT.b, 1.0)


## 单遍应有的不透明度（时间轴三遍叠加后才是肉眼看到的值，见常量注释）。
func _body_alpha() -> float:
	if not phasing:
		return 1.0
	return PHASING_ALPHA_TIME if time_mode else PHASING_ALPHA


## 把基色和虚化调制色乘起来（不透明部分按 tint 压暗，alpha 用单遍值）。
func _phase_color(base: Color) -> Color:
	var t := _phase_tint()
	return Color(base.r * t.r, base.g * t.g, base.b * t.b, _body_alpha())


## 画美术精灵：一帧 32×32，**脚底对齐** position.y + RADIUS（站位不变），
## 走路时按 walk_phase 在该方向的 4 帧循环里走。
func _draw_hero(c: CanvasItem, sheet: Texture2D, base: Vector2, bob: float) -> void:
	var group := _hero_group()
	var frames: Array = HERO_WALK[group] if walking else HERO_IDLE[group]
	var idx := 0
	if walking:
		idx = int(walk_phase * WALK_FREQ) % frames.size()
	else:
		# 站立：轻轻呼吸（第 0 帧和第 2 帧之间来回），不是死板不动
		idx = int(walk_phase * 2.0) % 2 * 2
	var fno: int = int(frames[idx % frames.size()])

	var src := Rect2(fno * HERO_FRAME, 0, HERO_FRAME, HERO_FRAME)
	var dst := Rect2(
		base.x - HERO_FRAME * 0.5,
		base.y + RADIUS - HERO_FRAME - bob,
		HERO_FRAME, HERO_FRAME)
	c.draw_texture_rect_region(sheet, dst, src, _phase_color(Color(1, 1, 1, 1)))

	# 时间轴模式的残影：沿朝向反方向排开，越远越淡（用精灵的第一帧）
	if time_mode and walking:
		for i in range(TRAIL, 0, -1):
			var t := float(i) / float(TRAIL + 1)
			var off := -facing * (float(i) * 6.4)
			var a := 0.30 * (1.0 - t)
			var rdst := Rect2(
				base.x - HERO_FRAME * 0.5 + off.x,
				base.y + RADIUS - HERO_FRAME - bob + off.y,
				HERO_FRAME, HERO_FRAME)
			var tc := _phase_color(Color(1, 1, 1, 1))
			tc.a = a * _body_alpha()
			c.draw_texture_rect_region(sheet, rdst, Rect2(fno * HERO_FRAME, 0,
				HERO_FRAME, HERO_FRAME), tc)


## 没有美术贴图时的灰盒画法（保留：美术资产缺失也不能把游戏画不出来）。
func _draw_fallback(c: CanvasItem, base: Vector2, bob: float) -> void:
	# 时间轴模式的残影：沿朝向反方向排开，越远越淡
	if time_mode and walking:
		for i in range(TRAIL, 0, -1):
			var t := float(i) / float(TRAIL + 1)
			var off := -facing * (float(i) * 6.4)
			var a := 0.30 * (1.0 - t) * _body_alpha()
			var tc := _phase_color(BODY_DIM)
			c.draw_circle(base + off, RADIUS - 0.5, Color(tc.r, tc.g, tc.b, a))

	var col := _phase_color(BODY)
	c.draw_circle(base, RADIUS + 1.0, _phase_color(OUTLINE))
	c.draw_circle(base + Vector2(0, -bob), RADIUS, col)

	# 朝向小三角
	var tip: Vector2 = base + Vector2(0, -bob) + facing * (RADIUS + 6.0)
	var left: Vector2 = base + Vector2(0, -bob) + facing.rotated(2.4) * (RADIUS + 2.0)
	var right: Vector2 = base + Vector2(0, -bob) + facing.rotated(-2.4) * (RADIUS + 2.0)
	c.draw_colored_polygon(PackedVector2Array([tip, left, right]), col)


## 朝向分组：down / left / right / up（facing 是世界向量，y 向下为正）。
func _hero_group() -> String:
	if absf(facing.x) > absf(facing.y):
		return "left" if facing.x < 0.0 else "right"
	return "up" if facing.y < 0.0 else "down"


## 主角精灵表（只 load 一次；缺图 → null → 回退灰盒画法）。
static func _hero_sheet() -> Texture2D:
	if _sheet_tried:
		return _sheet
	_sheet_tried = true
	if ResourceLoader.exists(HERO_SHEET):
		_sheet = load(HERO_SHEET)
	return _sheet
