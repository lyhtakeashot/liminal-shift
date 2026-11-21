extends Control

## 顶部状态条 + 底部时间轴刻度 + 检视出的文字。
## 灰盒阶段把该显示的都摊在屏幕上，方便一眼看出机制对不对。

const FONT := 10
const FONT_BIG := 13

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


func _draw_top_bar() -> void:
	draw_rect(Rect2(0, 0, size.x, 18), Color(0.06, 0.05, 0.04, 0.72), true)
	var axis_name := "空间轴 · SPACE" if not time_mode else "时间轴 · TIME"
	var col := Color(0.85, 0.84, 0.78) if not time_mode else Color(0.95, 0.78, 0.62)
	draw_string(font, Vector2(8, 13), "%d · %s" % [year, frame_id], 
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.80, 0.78, 0.70))
	draw_string(font, Vector2(size.x * 0.5 - 42, 13), axis_name,
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, col)
	draw_string(font, Vector2(size.x - 78, 13), "F11 全屏/小窗",
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.55, 0.53, 0.48))

	if axis_flash > 0.0:
		var a := axis_flash * 0.5
		draw_rect(Rect2(0, 18, size.x, 2), Color(0.95, 0.72, 0.45, a), true)


func _draw_timeline() -> void:
	# 布局：整条 30px 高，上面 4~22 放刻度点，最下沿留给操作提示
	var bar_h := 30.0
	var y := size.y - bar_h
	var alpha := 0.0
	if time_mode:
		alpha = 0.92
	else:
		alpha = 0.28   # §2.3：时间轴 UI 在空间轴模式下收起（但不完全消失，给一点提示）

	draw_rect(Rect2(0, y, size.x, bar_h), Color(0.06, 0.05, 0.04, 0.78 * alpha), true)

	var dot_y := y + 13.0
	var slot := size.x / float(frame_max + 1)
	for i in range(frame_max + 1):
		var cx := slot * (float(i) + 0.5)
		var active := i == index
		var r := 3.5 if active else 2.2
		var c := Color(0.95, 0.80, 0.55, alpha) if active else Color(0.55, 0.52, 0.46, alpha)
		draw_circle(Vector2(cx, dot_y), r, c)
		if active and bump_flash > 0.0:
			draw_arc(Vector2(cx, dot_y), r + 4.0 + bump_flash * 4.0, 0, TAU, 16,
				Color(0.95, 0.45, 0.35, bump_flash * 0.8), 1.5, true)

	# 刻度线
	for i in range(frame_max + 2):
		var x := slot * float(i)
		draw_line(Vector2(x, y + 5), Vector2(x, y + 21),
			Color(0.35, 0.33, 0.30, alpha * 0.8), 1.0)


func _draw_hotspot() -> void:
	if not hotspot_visible or hotspot_text == "":
		return

	var pad := 8.0
	var w := size.x - 40.0
	var lines := _wrap(hotspot_text, w - pad * 2.0)
	var h := pad * 2.0 + 13.0 + float(lines.size()) * 13.0
	var x := 20.0
	var y := size.y - 34.0 - h

	draw_rect(Rect2(x, y, w, h), Color(0.08, 0.07, 0.06, 0.90), true)
	draw_rect(Rect2(x, y, w, h), Color(0.55, 0.48, 0.38, 0.85), false, 1.0)

	draw_string(font, Vector2(x + pad, y + pad + 9), hotspot_title,
		HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.95, 0.82, 0.60))

	var ty := y + pad + 22.0
	for ln in lines:
		draw_string(font, Vector2(x + pad, ty), String(ln),
			HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Color(0.86, 0.84, 0.78))
		ty += 13.0


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
	draw_string(font, Vector2((size.x - w) * 0.5, size.y - 2.0), txt,
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