extends Control

## v3：解决两个问题
## 1. 删除线看不清 → 灰色+删除线，让划掉的部分退到背景
## 2. 多段涂改读不通 → 只保留首尾，中间用省略

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

const SEP := "[center][color=#b0a080]· · · · · · · ·[/color][/center]"

# 配色方案
const OLD_COL := "#9a9080"   # 被划掉的：灰
const NEW_COL := "#8b2f2f"   # 改写的：红
const INK_COL := "#3a2f22"   # 正常墨色


func _ready() -> void:
	var bg := ColorRect.new()
	bg.color = Color("#efe6d0")
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	var box := HBoxContainer.new()
	box.position = Vector2(24, 14)
	box.size = Vector2(700, 580)
	box.add_theme_constant_override("separation", 18)
	add_child(box)

	box.add_child(_page("假本 · 誊清", _render(RAW, false)))
	box.add_child(_page("真本 · 原稿", _render(RAW, true)))

	await RenderingServer.frame_post_draw
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	print("SAVE=", get_viewport().get_texture().get_image().save_png("res://_mdtest/render_v3.png"))
	await get_tree().create_timer(4.0).timeout
	get_tree().quit()


func _render(text: String, raw: bool) -> String:
	var out := ""
	var i := 0
	var n := text.length()
	while i < n:
		if i + 1 < n and text[i] == "{" and text[i + 1] == "{":
			var end := text.find("}}", i + 2)
			if end == -1:
				out += text.substr(i)
				break
			out += _emit(text.substr(i + 2, end - i - 2), raw)
			i = end + 2
			continue
		if i + 2 < n and text.substr(i, 3) == "---":
			out += SEP
			i += 3
			continue
		out += text[i]
		i += 1
	return out


func _emit(inner: String, raw: bool) -> String:
	var parts := inner.split("|")

	if not raw:
		return parts[parts.size() - 1]

	# 真本：多段涂改折叠成「首 → 尾」
	if parts.size() <= 2:
		return "[color=%s][s]%s[/s][/color][color=%s][b]%s[/b][/color]" % [
			OLD_COL, parts[0], NEW_COL, parts[1]
		]

	# 超过两段：首 → 末，中间用省略号，提示"改了很多次"
	return "[color=%s][s]%s[/s][/color][color=%s]…[/color][color=%s][b]%s[/b][/color]" % [
		OLD_COL, parts[0], OLD_COL, NEW_COL, parts[parts.size() - 1]
	]


func _page(title: String, body: String) -> PanelContainer:
	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(342, 570)
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color("#e8ddc0")
	sb.set_corner_radius_all(3)
	sb.set_border_width_all(1)
	sb.border_color = Color("#c0ae88")
	sb.set_content_margin_all(18)
	panel.add_theme_stylebox_override("panel", sb)

	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 8)
	panel.add_child(v)

	var t := Label.new()
	t.text = title
	t.add_theme_color_override("font_color", Color("#6a5a48"))
	t.add_theme_font_size_override("font_size", 13)
	v.add_child(t)

	var rtl := RichTextLabel.new()
	rtl.bbcode_enabled = true
	rtl.custom_minimum_size = Vector2(306, 510)
	rtl.fit_content = false
	rtl.scroll_active = false
	rtl.text = body
	rtl.add_theme_font_size_override("normal_font_size", 16)
	rtl.add_theme_color_override("default_color", Color(INK_COL))
	v.add_child(rtl)

	return panel