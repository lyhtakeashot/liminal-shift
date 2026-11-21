extends Control

## 极简标记渲染器 v2
## 修正：字号放大、--- 两套都处理、增加涂黑块/多次涂改/整段划掉

const RAW := """民国十五年十一月十七，晴。

卯时开闸，放水三刻，溉田十二亩。
收粮 {{三石二斗|三石}}。
午，陆氏子过河{{。|在闸下。}}
夜，陆家来人，言子未归。
付洋 {{三十|三|二十}}十，抚。
---

二月。

	卯时开闸。
	未告陆家。

未告陆家。

未告陆家。
---

{{此处原有字，已被涂去}}

春，陆家{{迁|走了|不再来了}}。

{{==涂黑==}}
"""

const SEP_BB := "[center][color=#a89880]· · · · · · · · · · · ·[/color][/center]"

# 涂黑块标记
const BLOCK := "{{==涂黑==}}"


func _ready() -> void:
	var bg := ColorRect.new()
	bg.color = Color("#efe6d0")
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	var box := HBoxContainer.new()
	box.position = Vector2(16, 12)
	box.size = Vector2(748, 590)
	box.add_theme_constant_override("separation", 16)
	add_child(box)

	box.add_child(_page("假本 · 誊清（给人看）", _render(RAW, false)))
	box.add_child(_page("真本 · 原稿（给自己）", _render(RAW, true)))

	await RenderingServer.frame_post_draw
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	print("SAVE=", img.save_png("res://_mdtest/render_v2.png"))
	await get_tree().create_timer(4.0).timeout
	get_tree().quit()


# ============ 渲染器 ============

func _render(text: String, raw: bool) -> String:
	var out := ""
	var i := 0
	var n := text.length()
	while i < n:
		# {{...}} 标记
		if i + 1 < n and text[i] == "{" and text[i + 1] == "{":
			var end := text.find("}}", i + 2)
			if end == -1:
				out += text.substr(i)
				break
			var inner := text.substr(i + 2, end - i - 2)
			out += _emit(inner, raw)
			i = end + 2
			continue
		# --- 分隔线
		if i + 2 < n and text.substr(i, 3) == "---":
			out += SEP_BB
			i += 3
			continue
		out += text[i]
		i += 1
	return out


func _emit(inner: String, raw: bool) -> String:
	# 涂黑块
	if inner.begins_with("=="):
		var body := inner.substr(2)
		if body.ends_with("=="):
			body = body.substr(0, body.length() - 2)
		if raw:
			# 真本：真的画一个黑块，字数对应宽度
			return "[bgcolor=#1a1a1a][color=#1a1a1a]%s[/color][/bgcolor]" % body
		else:
			# 假本：整行删掉
			return ""

	var parts := inner.split("|")
	if not raw:
		# 假本：只留最后一个
		return parts[parts.size() - 1]

	# 真本：前面全划线，最后一段红色
	var s := ""
	for k in range(parts.size() - 1):
		s += "[s]%s[/s]" % parts[k]
	s += "[color=#8b2f2f]%s[/color]" % parts[parts.size() - 1]
	return s


# ============ 界面 ============

func _page(title: String, body: String) -> PanelContainer:
	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(366, 580)
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color("#e8ddc0")
	sb.set_corner_radius_all(3)
	sb.set_border_width_all(1)
	sb.border_color = Color("#c0ae88")
	sb.set_content_margin_all(16)
	panel.add_theme_stylebox_override("panel", sb)

	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 8)
	panel.add_child(v)

	var t := Label.new()
	t.text = title
	t.add_theme_color_override("font_color", Color("#5a4a38"))
	t.add_theme_font_size_override("font_size", 13)
	v.add_child(t)

	var rtl := RichTextLabel.new()
	rtl.bbcode_enabled = true
	rtl.custom_minimum_size = Vector2(334, 520)
	rtl.fit_content = false
	rtl.scroll_active = false
	rtl.text = body
	rtl.add_theme_font_size_override("normal_font_size", 15)
	rtl.add_theme_color_override("default_color", Color("#3a2f22"))
	v.add_child(rtl)

	return panel