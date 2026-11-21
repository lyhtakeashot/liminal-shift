extends Control

## 测试三件事：
## 1. 中文能不能渲染（默认字体有没有 CJK）
## 2. BBCode 的 [s] [color] [i] [shake] [wave] 能不能用
## 3. 把结果存成 PNG 看实际效果

const CLEAN := """[color=#6b5a3e]民国十五年十一月十七，晴。

卯时开闸，放水三刻，溉田十二亩。
收粮三石二斗。
午，陆氏子过河。
夜，陆家来人，言子未归。
付洋三十，抚。[/color]"""

const DIRTY := """[color=#6b5a3e]民国十五年十一月十七，晴。

卯时开闸，放水三刻，[s]溉田十二亩[/s][color=#8b2f2f]未告陆家[/color]。
收粮[s]三石二斗[/s][color=#8b2f2f]三石[/color]。
午，陆氏子过河[s]。[/s][color=#8b2f2f]在闸下。[/color]
夜，陆家来人，言子未归。
付洋[s]三十[/s][color=#8b2f2f]三[/color]十，抚。[/color]

[color=#7a6a58][i]（此处有一行被反复涂改，看不清）[/i][/color]"""


func _ready() -> void:
	var bg := ColorRect.new()
	bg.color = Color("#e8dfc8")
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	var box := HBoxContainer.new()
	box.position = Vector2(24, 24)
	box.size = Vector2(640, 520)
	box.add_theme_constant_override("separation", 28)
	add_child(box)

	box.add_child(_make_page("假本 · 誊清", CLEAN))
	box.add_child(_make_page("真本 · 涂改", DIRTY))

	# 底部：特效测试
	var fx := RichTextLabel.new()
	fx.bbcode_enabled = true
	fx.position = Vector2(24, 440)
	fx.size = Vector2(640, 60)
	fx.fit_content = false
	fx.text = "[shake rate=12 level=2]抖动[/shake]  [wave amp=6 freq=4]波浪[/wave]  [u]下划线[/u]  [font_size=20]大字[/font_size]  [bgcolor=#d8c8a0]底色[/bgcolor]"
	add_child(fx)

	await RenderingServer.frame_post_draw
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var err := img.save_png("res://_mdtest/out.png")
	print("SAVE_PNG err=", err, " size=", img.get_size())

	# 顺便验证 bbcode 解析：unsupported 的标签会留在 parsed_text 里
	var probe := RichTextLabel.new()
	probe.bbcode_enabled = true
	probe.text = "[s]删[/s][i]斜[/i][shake]抖[/shake][nonexistent]X[/nonexistent]"
	print("PARSED_TEXT=[", probe.get_parsed_text(), "]")

	await get_tree().create_timer(0.3).timeout
	get_tree().quit()


func _make_page(title: String, body: String) -> VBoxContainer:
	var v := VBoxContainer.new()
	v.custom_minimum_size = Vector2(300, 0)
	v.add_theme_constant_override("separation", 8)

	var t := Label.new()
	t.text = title
	t.add_theme_color_override("font_color", Color("#3a2f22"))
	t.add_theme_font_size_override("font_size", 15)
	v.add_child(t)

	var rtl := RichTextLabel.new()
	rtl.bbcode_enabled = true
	rtl.custom_minimum_size = Vector2(300, 380)
	rtl.text = body
	rtl.fit_content = false
	rtl.add_theme_font_size_override("normal_font_size", 12)
	v.add_child(rtl)

	return v
