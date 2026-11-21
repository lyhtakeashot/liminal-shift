extends Control

## 常驻演示版：不自动退出，窗口保持开着供观察
## 按 空格 切换 假本/真本 单页对比；按 → ← 切换整页

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
const OLD_COL := "#9a9080"
const NEW_COL := "#8b2f2f"
const INK_COL := "#3a2f22"


func _ready() -> void:
	var bg := ColorRect.new()
	bg.color = Color("#efe6d0")
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	var box := HBoxContainer.new()
	box.position = Vector2(28, 20)
	box.add_theme_constant_override("separation", 24)
	add_child(box)

	box.add_child(_page("假本 · 誊清（给所有人看）", _render(RAW, false), "#e8ddc0"))
	box.add_child(_page("真本 · 原稿（给自己看）", _render(RAW, true), "#e2d6b4"))

	var hint := Label.new()
	hint.text = "极简标记渲染演示 · {{旧|新}} = 涂改    --- = 分节"
	hint.position = Vector2(28, 620)
	hint.add_theme_color_override("font_color", Color("#8a7a62"))
	hint.add_theme_font_size_override("font_size", 12)
	add_child(hint)


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
	if parts.size() <= 2:
		return "[color=%s][s]%s[/s][/color][color=%s][b]%s[/b][/color]" % [
			OLD_COL, parts[0], NEW_COL, parts[1]
		]
	return "[color=%s][s]%s[/s][/color][color=%s]…[/color][color=%s][b]%s[/b][/color]" % [
		OLD_COL, parts[0], OLD_COL, NEW_COL, parts[parts.size() - 1]
	]


func _page(title: String, body: String, bgc: String) -> PanelContainer:
	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(380, 580)
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(bgc)
	sb.set_corner_radius_all(3)
	sb.set_border_width_all(1)
	sb.border_color = Color("#c0ae88")
	sb.set_content_margin_all(20)
	panel.add_theme_stylebox_override("panel", sb)

	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 8)
	panel.add_child(v)

	var t := Label.new()
	t.text = title
	t.add_theme_color_override("font_color", Color("#6a5a48"))
	t.add_theme_font_size_override("font_size", 14)
	v.add_child(t)

	var rtl := RichTextLabel.new()
	rtl.bbcode_enabled = true
	rtl.custom_minimum_size = Vector2(340, 520)
	rtl.fit_content = false
	rtl.scroll_active = false
	rtl.text = body
	rtl.add_theme_font_size_override("normal_font_size", 17)
	rtl.add_theme_color_override("default_color", Color(INK_COL))
	v.add_child(rtl)

	return panel