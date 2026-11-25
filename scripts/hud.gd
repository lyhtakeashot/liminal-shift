extends Control

## 顶部状态条 + 底部时间轴刻度 + 检视出的文字。
## 灰盒阶段把该显示的都摊在屏幕上，方便一眼看出机制对不对。
##
## 布局单位（2026-11-21 TILE 16→32 同时视口翻倍）：
##   下面所有数字都是「640×360 时代的设计值」，写的时候乘 UI。
##   UI = 视口宽 / 640。现在视口 1280×720 → UI = 2.0。
##   以后视口再变，只改 UI 的定义（或者让它从 size 推），坐标表一个字都不用动。

const DESIGN_W := 640.0          # 设计基准宽（640×360 那套坐标的出处）
const UI := 2.0                  # = 当前视口宽 / DESIGN_W

const FONT := int(10 * UI)
const FONT_BIG := int(13 * UI)

const FrameData = preload("res://scripts/frame_data.gd")

var font: Font = ThemeDB.fallback_font

var time_mode := false
var index := 0
var frame_max := 0
var year := 0
var frame_id := ""
var hotspot_title := ""
var hotspot_text := ""
var hotspot_visible := false
var bump_flash := 0.0
var axis_flash := 0.0

# ── 小地图（L12/M6）──────────────────────────────────────────
# 世界尺寸按 4800×3600 写死（M7 甲方案已拍板：地图 ×1.5、TILE 仍 32）。
# ⚠️ 若 L11 尚未落地（frames.json 还是 3200×2400），小地图仍按 4800×3600 画框，
#    玩家点会落在左上 2/3 区域 —— 等 L11 落地后自然复原，不用改这里。
var world_extent := Vector2(4800, 3600)
var player_pos := Vector2.ZERO

const MINIMAP_W := 100.0 * UI    # 设计值 100×75 → 实际 200×150（与 4800:3600 同比例 4:3）
const MINIMAP_H := 75.0 * UI
const MINIMAP_MARGIN := 8.0 * UI # 与顶条/右缘的间隙


## 小地图几何的唯一出处：绘制与测试断言共用，防止两处写歪。
## 落位＝右上角：顶条（36px）下沿 + 16px 间隙；右缘留 16px。
func minimap_rect() -> Rect2:
	return Rect2(size.x - MINIMAP_MARGIN - MINIMAP_W,
		18.0 * UI + MINIMAP_MARGIN, MINIMAP_W, MINIMAP_H)


## 世界坐标 → 小地图上的点（含玩家点/任何标注）。越界世界坐标夹到框内。
func minimap_point(world_pos: Vector2) -> Vector2:
	var r := minimap_rect()
	if world_extent.x <= 0.0 or world_extent.y <= 0.0:
		return r.position
	var t := Vector2(
		clampf(world_pos.x / world_extent.x, 0.0, 1.0),
		clampf(world_pos.y / world_extent.y, 0.0, 1.0))
	return r.position + t * r.size


## 每帧由 main.gd:_process 喂玩家坐标（sync() 的签名不许动 —— 坑 2）。
func sync_player(pos: Vector2) -> void:
	if pos.distance_squared_to(player_pos) < 0.0001:
		return
	player_pos = pos
	queue_redraw()


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func sync(is_time: bool, i: int, fmax: int, f: FrameData) -> void:
	time_mode = is_time
	index = i
	frame_max = fmax
	year = f.year
	frame_id = f.id
	queue_redraw()


func show_hotspot(h: Dictionary) -> void:
	if h.is_empty():
		hotspot_visible = false
		hotspot_title = ""
		hotspot_text = ""
	else:
		hotspot_visible = true
		hotspot_title = String(h.get("title", ""))
		hotspot_text = String(h.get("text", ""))
	queue_redraw()


func flash_bump() -> void:
	bump_flash = 1.0
	queue_redraw()


func flash_axis() -> void:
	axis_flash = 1.0
	queue_redraw()


func _process(delta: float) -> void:
	var dirty := false
	if bump_flash > 0.0:
		bump_flash = maxf(0.0, bump_flash - delta * 3.2)
		dirty = true
	if axis_flash > 0.0:
		axis_flash = maxf(0.0, axis_flash - delta * 2.2)
		dirty = true
	if dirty:
		queue_redraw()


func _draw() -> void:
	_draw_top_bar()
	_draw_timeline()
	_draw_hotspot()
	_draw_hint()
	_draw_minimap()


## 小地图：世界框 + 玩家点。不画 houses/roads/地标（HUD 不读 frames.json，
## 且那是 L11 的单写者域 —— 任务书 §3.3 与 §7.3）。
## §3.4 采纳：时间轴模式下底板 alpha 0.62→0.45，与时间轴收起风格一致。
func _draw_minimap() -> void:
	var r := minimap_rect()
	var bg_a := 0.45 if time_mode else 0.62
	draw_rect(r, Color(0.06, 0.05, 0.04, bg_a), true)
	draw_rect(r, Color(0.55, 0.48, 0.38, 0.55), false, 1.0 * UI)
	draw_circle(minimap_point(player_pos), 3.0 * UI, Color(0.95, 0.85, 0.60))


func _draw_top_bar() -> void:
	var bar_h := 18.0 * UI
	draw_rect(Rect2(0, 0, size.x, bar_h), Color(0.06, 0.05, 0.04, 0.72), true)
	var axis_name := "空间轴 · SPACE" if not time_mode else "时间轴 · TIME"
	var col := Color(0.85, 0.84, 0.78) if not time_mode else Color(0.95, 0.78, 0.62)
	var ty := 13.0 * UI
	draw_string(font, Vector2(8.0 * UI, ty), "%d · %s" % [year, frame_id],
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.80, 0.78, 0.70))
	# 居中项：按实际字宽居中，不再用写死的 -42 偏移（换字号后偏移量会错）
	var aw := font.get_string_size(axis_name, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x
	draw_string(font, Vector2((size.x - aw) * 0.5, ty), axis_name,
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, col)
	var hint := "F11 全屏/小窗"
	var hw := font.get_string_size(hint, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x
	draw_string(font, Vector2(size.x - hw - 8.0 * UI, ty), hint,
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.55, 0.53, 0.48))

	if axis_flash > 0.0:
		var a := axis_flash * 0.5
		draw_rect(Rect2(0, bar_h, size.x, 2.0 * UI), Color(0.95, 0.72, 0.45, a), true)


func _draw_timeline() -> void:
	# 布局：整条 30px（设计值）高，上面放刻度点，最下沿留给操作提示
	var bar_h := 30.0 * UI
	var y := size.y - bar_h
	var alpha := 0.0
	if time_mode:
		alpha = 0.92
	else:
		alpha = 0.28   # §2.3：时间轴 UI 在空间轴模式下收起（但不完全消失，给一点提示）

	draw_rect(Rect2(0, y, size.x, bar_h), Color(0.06, 0.05, 0.04, 0.78 * alpha), true)

	var dot_y := y + 13.0 * UI
	var slot := size.x / float(frame_max + 1)
	for i in range(frame_max + 1):
		var cx := slot * (float(i) + 0.5)
		var active := i == index
		var r := (3.5 if active else 2.2) * UI
		var c := Color(0.95, 0.80, 0.55, alpha) if active else Color(0.55, 0.52, 0.46, alpha)
		draw_circle(Vector2(cx, dot_y), r, c)
		if active and bump_flash > 0.0:
			draw_arc(Vector2(cx, dot_y), r + (4.0 + bump_flash * 4.0) * UI, 0, TAU, 16,
				Color(0.95, 0.45, 0.35, bump_flash * 0.8), 1.5 * UI, true)

	# 刻度线
	for i in range(frame_max + 2):
		var x := slot * float(i)
		draw_line(Vector2(x, y + 5.0 * UI), Vector2(x, y + 21.0 * UI),
			Color(0.35, 0.33, 0.30, alpha * 0.8), 1.0 * UI)


func _draw_hotspot() -> void:
	if not hotspot_visible or hotspot_text == "":
		return

	var pad := 8.0 * UI
	var line_h := 13.0 * UI
	var w := size.x - 40.0 * UI
	var lines := _wrap(hotspot_text, w - pad * 2.0)
	var h := pad * 2.0 + line_h + float(lines.size()) * line_h
	var x := 20.0 * UI
	var y := size.y - 34.0 * UI - h

	draw_rect(Rect2(x, y, w, h), Color(0.08, 0.07, 0.06, 0.90), true)
	draw_rect(Rect2(x, y, w, h), Color(0.55, 0.48, 0.38, 0.85), false, 1.0 * UI)

	draw_string(font, Vector2(x + pad, y + pad + 9.0 * UI), hotspot_title,
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.95, 0.82, 0.60))

	var ty := y + pad + 22.0 * UI
	for ln in lines:
		draw_string(font, Vector2(x + pad, ty), String(ln),
			HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.86, 0.84, 0.78))
		ty += line_h


func _draw_hint() -> void:
	if hotspot_visible:
		return
	# 放进底部刻度条内部（刻度点画在 y+13，提示字压在最下沿），不占地图区域
	var txt := ""
	if time_mode:
		txt = "W/S 推时间    SHIFT 回空间轴    E 检视"
	else:
		txt = "WASD 走    SHIFT 进时间轴    E 检视"
	var w := font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x
	var a := 0.9 if time_mode else 0.45
	draw_string(font, Vector2((size.x - w) * 0.5, size.y - 2.0 * UI), txt,
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.88, 0.86, 0.78, a))


## 按字符宽度硬折行。中文没有空格，按累积宽度切最稳。
func _wrap(text: String, max_w: float) -> Array:
	var out: Array = []
	var cur := ""
	for i in text.length():
		var ch := text[i]
		var test := cur + ch
		if font.get_string_size(test, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT).x > max_w and cur != "":
			out.append(cur)
			cur = ch
		else:
			cur = test
	if cur != "":
		out.append(cur)
	return out
