extends Control

## v4：自绘删除线（可调粗细）
## RichTextLabel 的 [s] 线宽固定不可调，改用 _draw() 自己画

const RAW := """民国十五年十一月十七，晴。

卯时开闸，放水三刻，溉田十二亩。
收粮 {{三石二斗|三石}}。
午，陆氏子过河{{。|在闸下。}}
夜，陆家来人，言子未归。
付洋 {{三十|三|二十|三十}}，抚。
---

二月。

	卯时开闸。
	未告陆家。

未告陆家。
---

春，陆家{{迁|走了|不再来了}}。
"""

const INK := Color("#3a2f22")
const OLD := Color("#8f8474")
const NEW := Color("#8b2f2f")
const RULE := Color("#b0a080")
const PAPER_A := Color("#e8ddc0")
const PAPER_B := Color("#e2d6b4")

const FS := 17
const LINE_H := 26.0
const PARA_GAP := 12.0

# 三档粗细对比
const THICKNESSES := [1.0, 2.0, 3.0]


func _ready() -> void:
	var bg := ColorRect.new()
	bg.color = Color("#efe6d0")
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	var title := Label.new()
	title.text = "删除线粗细对比（自绘）· 左：假本   中：真本 1px   右：真本 2px / 3px"
	title.position = Vector2(24, 10)
	title.add_theme_color_override("font_color", Color("#6a5a48"))
	title.add_theme_font_size_override("font_size", 13)
	add_child(title)

	# 左：假本
	_add_panel(Vector2(24, 40), Vector2(258, 560), PAPER_A, false, 2.0, "假本 · 誊清")
	# 中：真本 2px
	_add_panel(Vector2(300, 40), Vector2(258, 560), PAPER_B, true, 2.0, "真本 · 2px")
	# 右：真本 3px
	_add_panel(Vector2(576, 40), Vector2(258, 560), PAPER_B, true, 3.0, "真本 · 3px")

	_snap()


func _snap() -> void:
	await RenderingServer.frame_post_draw
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	print("SNAP=", get_viewport().get_texture().get_image().save_png("res://_mdtest/demo4.png"))
	# 不退出，窗口保持


func _add_panel(pos: Vector2, sz: Vector2, paper: Color, raw: bool, thick: float, title: String) -> void:
	var panel := Panel.new()
	panel.position = pos
	panel.size = sz
	var sb := StyleBoxFlat.new()
	sb.bg_color = paper
	sb.set_border_width_all(1)
	sb.border_color = Color("#c0ae88")
	sb.set_corner_radius_all(2)
	panel.add_theme_stylebox_override("panel", sb)
	add_child(panel)

	var lbl := Label.new()
	lbl.text = title
	lbl.position = Vector2(14, 8)
	lbl.add_theme_color_override("font_color", Color("#6a5a48"))
	lbl.add_theme_font_size_override("font_size", 12)
	panel.add_child(lbl)

	var cv := TextCanvas.new()
	cv.position = Vector2(14, 30)
	cv.size = sz - Vector2(28, 42)
	cv.setup(RAW, raw, thick)
	panel.add_child(cv)


# ================= 自绘文本控件 =================
class TextCanvas extends Control:
	var lines: Array = []       # Array[Array[Segment]]
	var raw: bool = false
	var thick: float = 2.0
	var font: Font
	var fs: int = 17
	var line_h: float = 26.0
	var para_gap: float = 12.0

	func setup(src: String, _raw: bool, _thick: float) -> void:
		raw = _raw
		thick = _thick
		font = ThemeDB.fallback_font
		lines = _parse(src)

	func _parse(src: String) -> Array:
		var out: Array = []
		for raw_line in src.split("\n"):
			var segs: Array = []
			var i := 0
			var n := raw_line.length()
			var buf := ""
			while i < n:
				if i + 1 < n and raw_line[i] == "{" and raw_line[i + 1] == "{":
					var end := raw_line.find("}}", i + 2)
					if end == -1:
						buf += raw_line.substr(i)
						break
					if buf != "":
						segs.append({"t": buf, "k": "n"})
						buf = ""
					segs.append_array(_emit(raw_line.substr(i + 2, end - i - 2)))
					i = end + 2
					continue
				if i + 2 < n and raw_line.substr(i, 3) == "---":
					if buf != "":
						segs.append({"t": buf, "k": "n"})
						buf = ""
					segs.append({"t": "", "k": "rule"})
					i += 3
					continue
				buf += raw_line[i]
				i += 1
			if buf != "":
				segs.append({"t": buf, "k": "n"})
			out.append(segs)
		return out

	func _emit(inner: String) -> Array:
		var parts := inner.split("|")
		if not raw:
			return [{"t": parts[parts.size() - 1], "k": "n"}]
		if parts.size() <= 2:
			return [{"t": parts[0], "k": "old"}, {"t": parts[1], "k": "new"}]
		return [
			{"t": parts[0], "k": "old"},
			{"t": "…", "k": "old"},
			{"t": parts[parts.size() - 1], "k": "new"},
		]

	func _draw() -> void:
		var y := 0.0
		var ascent := font.get_ascent(fs)
		for segs in lines:
			# 空行
			if segs.is_empty():
				y += line_h * 0.6
				continue
			# 分隔线
			if segs.size() == 1 and segs[0]["k"] == "rule":
				var cx := size.x * 0.5
				for d in range(-30, 31, 10):
					draw_circle(Vector2(cx + d, y + line_h * 0.45), 1.2, RULE)
				y += line_h
				continue

			var x := 0.0
			# 制表符缩进
			if segs.size() > 0 and segs[0]["k"] == "n" and segs[0]["t"].begins_with("\t"):
				x = 20.0
				segs[0]["t"] = segs[0]["t"].substr(1)

			for s in segs:
				var txt: String = s["t"]
				if txt == "":
					continue
				var w := font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
				var col := INK
				if s["k"] == "old":
					col = OLD
				elif s["k"] == "new":
					col = NEW

				draw_string(font, Vector2(x, y + ascent), txt,
					HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)

				# 强调：再描一遍做伪粗体
				if s["k"] == "new":
					draw_string(font, Vector2(x + 0.6, y + ascent), txt,
						HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)

				# 自绘删除线
				if s["k"] == "old":
					var ly := y + ascent - fs * 0.30
					draw_line(Vector2(x, ly), Vector2(x + w, ly), OLD, thick, true)

				x += w
			y += line_h

	func _process(_d: float) -> void:
		pass