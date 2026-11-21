extends Control

## 极简标记渲染器原型 v1
## 目标：一份原稿，两种渲染（假本通顺 / 真本涂改）

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

---

{{此处原有字，已被涂去}}

春，陆家{{迁|走了|不再来了}}。
"""

# ============ 解析 ============

func _parse_settle(text: String) -> String:
	# 假本：只留“改后”的内容（最后一个 | 之后），通顺
	var out := ""
	var i := 0
	var n := text.length()
	while i < n:
		if i + 1 < n and text[i] == "{" and text[i + 1] == "{":
			var end := text.find("}}", i + 2)
			if end == -1:
				out += text.substr(i)
				break
			var inner := text.substr(i + 2, end - i - 2)
			var parts := inner.split("|")
			out += parts[parts.size() - 1]
			i = end + 2
		else:
			out += text[i]
			i += 1
	return out


func _parse_raw(text: String) -> String:
	# 真本：划线保留原样，改正部分红色
	var out := ""
	var i := 0
	var n := text.length()
	while i < n:
		if i + 1 < n and text[i] == "{" and text[i + 1] == "{":
			var end := text.find("}}", i + 2)
			if end == -1:
				out += text.substr(i)
				break
			var inner := text.substr(i + 2, end - i - 2)
			var parts := inner.split("|")
			# 多段：前面全部划线，最后一段红色
			for k in range(parts.size() - 1):
				out += "[s]%s[/s]" % parts[k]
			out += "[color=#8b2f2f]%s[/color]" % parts[parts.size() - 1]
			i = end + 2
		elif text[i] == "-" and i + 2 < n and text.substr(i, 3) == "---":
			out += "[center][color=#a89880]＿＿＿＿＿＿＿＿＿＿[/color][/center]"
			i += 3
		else:
			out += text[i]
			i += 1
	return out


# ============ 界面 ============

func _ready() -> void:
	var bg := ColorRect.new()
	bg.color = Color("#efe6d0")
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	var box := HBoxContainer.new()
	box.position = Vector2(20, 16)
	box.size = Vector2(580, 410)
	box.add_theme_constant_override("separation", 20)
	add_child(box)

	box.add_child(_page("假本 · 誊清（给所有人看）", _parse_settle(RAW), Color("#e6dcc2"), false))
	box.add_child(_page("真本 · 原稿（给自己看）", _parse_raw(RAW), Color("#e0d4b4"), true))

	await RenderingServer.frame_post_draw
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var e := img.save_png("res://_mdtest/render_v1.png")
	print("SAVE=", e)
	await get_tree().create_timer(4.0).timeout
	get_tree().quit()


func _page(title: String, body: String, bgc: Color, raw: bool) -> PanelContainer:
	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(270, 400)
	var sb := StyleBoxFlat.new()
	sb.bg_color = bgc
	sb.set_corner_radius_all(2)
	sb.set_border_width_all(1)
	sb.border_color = Color("#c8b898")
	sb.content_margin_left = 14
	sb.content_margin_right = 12
	sb.content_margin_top = 12
	sb.content_margin_bottom = 12
	panel.add_theme_stylebox_override("panel", sb)

	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 6)
	panel.add_child(v)

	var t := Label.new()
	t.text = title
	t.add_theme_color_override("font_color", Color("#5a4a38"))
	t.add_theme_font_size_override("font_size", 11)
	v.add_child(t)

	var rtl := RichTextLabel.new()
	rtl.bbcode_enabled = true
	rtl.custom_minimum_size = Vector2(240, 360)
	rtl.fit_content = false
	rtl.scroll_active = false
	rtl.text = body
	rtl.add_theme_font_size_override("normal_font_size", 11)
	rtl.add_theme_color_override("default_color", Color("#3a2f22"))
	v.add_child(rtl)

	return panel