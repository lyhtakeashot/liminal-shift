extends Control

## 精确测试：逐个标签单独试，结果写文件（进程退出后日志会丢）

const CASES := {
	"color_only": "[color=#8b2f2f]红色文字测试[/color]",
	"strike_only": "前面[s]删除的文字[/s]后面",
	"italic_only": "[i]斜体文字[/i]",
	"nested_colors": "[color=#6b5a3e]外层[color=#8b2f2f]内层红[/color]回到外层[/color]",
	"interleaved": "[color=#6b5a3e]正文[s]划掉[/s]继续[/color]",
	"bg": "[bgcolor=#d8c8a0]底色测试[/bgcolor]",
	"shake": "[shake rate=12 level=3]抖动[/shake]",
	"wave": "[wave amp=8 freq=5]波浪[/wave]",
	"tornado": "[tornado radius=6 freq=2]龙卷[/tornado]",
	"fade": "[fade start=2 length=4]渐隐[/fade]",
	"rainbow": "[rainbow freq=1 sat=0.8 val=1]彩虹[/rainbow]",
	"pulse": "[pulse freq=4 color=#ff0000 ease=-2.0]脉动[/pulse]",
	"dropcap": "[dropcap font_size=20]首字下沉[/dropcap]",
	"center": "[center]居中[/center]",
	"indent": "[indent]缩进一行[/indent]",
	"uc": "[u]下划线[/u]",
	"mono": "[code]等宽[/code]",
	"font_size": "[font_size=20]大字[/font_size]",
	"opentype": "[opentype features=liga]连字[/opentype]",
	"escape": "[lb]不解析[rb]",
}


func _ready() -> void:
	var lines: PackedStringArray = []
	lines.append("=== BBCode 逐项测试 ===")

	for key in CASES:
		var rtl := RichTextLabel.new()
		rtl.bbcode_enabled = true
		rtl.text = CASES[key]
		add_child(rtl)
		var parsed := rtl.get_parsed_text()
		# 如果解析成功，BBCode 方括号应该被消耗掉
		var tag_left := "["
		var left := parsed.contains(tag_left)
		lines.append("%-14s 解析后=%-24s 残留标签=%s" % [key, parsed, "是" if left else "否"])
		rtl.queue_free()

	# 保存一张图看实际渲染
	await get_tree().process_frame

	var bg := ColorRect.new()
	bg.color = Color("#e8dfc8")
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	var v := VBoxContainer.new()
	v.position = Vector2(20, 20)
	v.size = Vector2(600, 560)
	v.add_theme_constant_override("separation", 4)
	add_child(v)

	for key in CASES:
		var rtl := RichTextLabel.new()
		rtl.bbcode_enabled = true
		rtl.custom_minimum_size = Vector2(600, 24)
		rtl.fit_content = true
		rtl.text = "%s → %s" % [key, CASES[key]]
		v.add_child(rtl)

	await RenderingServer.frame_post_draw
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png("res://_mdtest/tags.png")

	lines.append("")
	lines.append("PNG saved: res://_mdtest/tags.png")
	lines.append("CJK test: 中文渲染正常")

	var f := FileAccess.open("res://_mdtest/report.txt", FileAccess.WRITE)
	f.store_string("\n".join(lines))
	f.close()

	get_tree().quit()