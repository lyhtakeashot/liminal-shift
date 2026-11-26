extends SceneTree

## L16 · 双日记渲染自检（D1–D10 + 静态自检）。
## 跑法：godot --headless --path . --script res://_mdtest/diary_render_check.gd
##
## ⚠️ headless 画不出图，所以「视觉」结论一律落到**解析结果**上断言（任务书 §3.6）：
##    D9「真本有删除线 / 假本没有」= 段里有没有 strike 段；线的粗细只看 diary_page.gd 的常量。
##
## 另外 S1–S6 是静态自检：grep 任务书 §4.4 要求的几条（RichTextLabel 零命中 / draw_line 有命中 /
## 原稿与 docs/story.md 逐字一致），让「验收口径」也进回归，不只靠人眼。

const DiaryMarkup = preload("res://scripts/diary_markup.gd")
const DiaryTexts = preload("res://scripts/diary_texts.gd")
const DiaryPage = preload("res://scripts/diary_page.gd")
const DiaryView = preload("res://scripts/diary_view.gd")

var fails := 0


func _ok(cond: bool, label: String) -> void:
	print(("PASS " if cond else "FAIL ") + label)
	if not cond:
		fails += 1


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	_d1_d7_markup()
	_d8_and_s3_texts()
	_d9_pair()
	_d10_no_bbcode()
	_layout_checks()
	_page_checks()
	_s_static()
	_view_smoke()
	_view_input_checks()
	print("DIARY_RENDER_CHECK_DONE fails=%d" % fails)
	quit(1 if fails > 0 else 0)


# ---- 小工具 --------------------------------------------------------------

## 某个 kind 的段文字，按出现顺序。
func _texts(segments: Array, kind: String) -> Array:
	var out: Array = []
	for seg in segments:
		if String(seg.get("kind", "")) == kind:
			out.append(String(seg.get("text", "")))
	return out


func _kind_at(segments: Array, idx: int) -> String:
	return String((segments[idx] as Dictionary).get("kind", "<none>"))


func _has_sub(s: String, sub: String) -> bool:
	return s.find(sub) >= 0


# ---- D1–D7：标记解析 -----------------------------------------------------

func _d1_d7_markup() -> void:
	# D1 假本 {{A|B}} → 只留 B，没有划线
	var d1 := DiaryMarkup.parse("收粮 {{三石二斗|三石}}。", false)
	_ok(not DiaryMarkup.has_kind(d1, DiaryMarkup.KIND_STRIKE), "D1 假本没有 strike 段")
	_ok(not DiaryMarkup.has_kind(d1, DiaryMarkup.KIND_RED), "D1 假本没有 red 段")
	_ok(DiaryMarkup.plain_text(d1) == "收粮 三石。",
		"D1 假本只留改正后的 B：%s" % DiaryMarkup.plain_text(d1))

	# D2 真本 {{A|B}} → strike(A) + red(B)
	var d2 := DiaryMarkup.parse("收粮 {{三石二斗|三石}}。", true)
	var st2 := _texts(d2, DiaryMarkup.KIND_STRIKE)
	var rd2 := _texts(d2, DiaryMarkup.KIND_RED)
	_ok(st2.size() == 1 and String(st2[0]) == "三石二斗",
		"D2 真本划掉的旧字：%s" % str(st2))
	_ok(rd2.size() == 1 and String(rd2[0]) == "三石",
		"D2 真本红色的新字：%s" % str(rd2))
	var i_st := -1
	var i_rd := -1
	for i in d2.size():
		var k := _kind_at(d2, i)
		if k == DiaryMarkup.KIND_STRIKE and i_st < 0:
			i_st = i
		if k == DiaryMarkup.KIND_RED and i_rd < 0:
			i_rd = i
	_ok(i_st >= 0 and i_rd > i_st, "D2 先划线后红字（顺序 %d < %d）" % [i_st, i_rd])

	# D3 真本 {{A|B|C|D}} → strike(A) + … + red(D)，B/C 一个字都不出现
	var d3 := DiaryMarkup.parse("{{甲|乙|丙|丁}}", true)
	var k3 := DiaryMarkup.kinds(d3)
	_ok(str(k3) == str([DiaryMarkup.KIND_STRIKE, DiaryMarkup.KIND_ELLIPSIS,
		DiaryMarkup.KIND_RED]), "D3 真本多段折叠成 划线/省略/红字：%s" % str(k3))
	_ok(DiaryMarkup.plain_text(d3) == "甲…丁",
		"D3 真本折叠后是「首 → … → 尾」：%s" % DiaryMarkup.plain_text(d3))
	_ok(not _has_sub(DiaryMarkup.plain_text(d3), "乙")
		and not _has_sub(DiaryMarkup.plain_text(d3), "丙"), "D3 中间段一个字都不出")

	# D4 假本 {{A|B|C|D}} → 只留 D
	var d4 := DiaryMarkup.parse("{{甲|乙|丙|丁}}", false)
	_ok(DiaryMarkup.plain_text(d4) == "丁",
		"D4 假本只留最后一段：%s" % DiaryMarkup.plain_text(d4))
	_ok(DiaryMarkup.kinds(d4) == [DiaryMarkup.KIND_TEXT], "D4 假本只有普通文字段")

	# D5 --- → sep 段（假本也要处理，别只认真本）
	for raw_book in [false, true]:
		var d5 := DiaryMarkup.parse("前\n---\n后", raw_book)
		_ok(DiaryMarkup.has_kind(d5, DiaryMarkup.KIND_SEP),
			"D5 --- 变成 sep 段（真本=%s）" % str(raw_book))
		_ok(DiaryMarkup.plain_text(d5).find("---") < 0,
			"D5 分隔线不再以「---」字符形式留在正文里（真本=%s）" % str(raw_book))

	# D6 行首制表符 → indent 段
	var d6 := DiaryMarkup.parse("\t卯时开闸。\n\t未告陆家。", false)
	var ind := _texts(d6, DiaryMarkup.KIND_INDENT)
	_ok(ind.size() == 2, "D6 两个行首制表符 → 两个 indent 段：%d" % ind.size())
	_ok(DiaryMarkup.plain_text(d6) == "卯时开闸。\n未告陆家。",
		"D6 制表符被吃掉、正文未被吞：%s" % DiaryMarkup.plain_text(d6).replace("\n", "\\n"))

	# D7 {{ 没闭合 → 原样保留，后面一个字都不能吞
	var d7 := DiaryMarkup.parse("前{{未闭合", true)
	_ok(DiaryMarkup.plain_text(d7) == "前{{未闭合",
		"D7 未闭合的 {{ 原样留着：%s" % DiaryMarkup.plain_text(d7))
	_ok(not DiaryMarkup.has_kind(d7, DiaryMarkup.KIND_STRIKE)
		and not DiaryMarkup.has_kind(d7, DiaryMarkup.KIND_RED), "D7 未闭合不产生划线/红字段")


# ---- D8：四份原稿逐字 ----------------------------------------------------

func _d8_and_s3_texts() -> void:
	var fake: String = DiaryTexts.FAKE_MILL
	var raw: String = DiaryTexts.RAW_MILL

	_ok(_has_sub(fake, "收粮 三石。"), "D8 假本里有誊清句「收粮 三石。」")
	_ok(not _has_sub(fake, "{{") and not _has_sub(fake, "}}"), "D8 假本没有任何涂改标记")
	for mk in ["{{三石二斗|三石}}", "{{。|在闸下。}}", "{{三十|三|二十|三十}}",
			"{{迁|走了|不再来了}}"]:
		_ok(_has_sub(raw, mk), "D8 真本里有标记 %s" % mk)
	_ok(_has_sub(DiaryTexts.LU_FRAGMENT, "疑非陆万山"), "D8 残页里有「疑非陆万山」")
	_ok(DiaryTexts.LU_FRAGMENT_NOTE == "到此为止。后面空白。",
		"D8 残页的说明句锚点一字不差")
	_ok(_has_sub(DiaryTexts.ZHOU_EARLY, "陆婶"), "D8 民国十六年首笔写的是「陆婶」")
	_ok(_has_sub(DiaryTexts.ZHOU_LEDGER, "陆先生"), "D8 民国三十五年四笔全是「陆先生」")
	_ok(not _has_sub(DiaryTexts.ZHOU_LEDGER, "注")
		and not _has_sub(DiaryTexts.ZHOU_EARLY, "注"), "D8 账页正文里没有注解（story.md:890）")
	_ok(fake.count("\t") == 2 and raw.count("\t") == 2, "D8 两本各有两处行首制表符")

	# S3 逐字比对：从 docs/story.md 现场重抽围栏块，必须一字不差
	var want := _story_blocks()
	_ok(String(want.get("a1", "")) == fake, "S3 假本与 docs/story.md 附一.1 逐字一致")
	_ok(String(want.get("a2", "")) == raw, "S3 真本与 docs/story.md 附一.2 逐字一致")
	_ok(String(want.get("a3_35", "")) == DiaryTexts.ZHOU_LEDGER,
		"S3 民国三十五年账与 story.md 逐字一致")
	_ok(String(want.get("a3_16", "")) == DiaryTexts.ZHOU_EARLY,
		"S3 民国十六年账与 story.md 逐字一致")
	_ok(String(want.get("a4", "")) == DiaryTexts.LU_FRAGMENT,
		"S3 残页与 story.md 逐字一致")


## 从 docs/story.md 现场抽附一的五个围栏块（只为比对，不参与游戏逻辑）。
func _story_blocks() -> Dictionary:
	var out := {}
	var f := FileAccess.open("res://docs/story.md", FileAccess.READ)
	if f == null:
		return out
	var lines := f.get_as_text().replace("\r", "").split("\n")
	f.close()

	var curve := ""
	var n := 0
	var i := 0
	while i < lines.size():
		var ln: String = lines[i]
		if ln.begins_with("## 附一."):
			curve = ln.substr(6, 1)          # "## 附一.1 · …" → "1"
		if ln.strip_edges() == "```":
			var body: Array = []
			i += 1
			while i < lines.size() and lines[i].strip_edges() != "```":
				body.append(lines[i])
				i += 1
			var block := "\n".join(body) + "\n"
			n += 1
			if curve == "1":
				out["a1"] = block
			elif curve == "2":
				out["a2"] = block
			elif curve == "3":
				if not out.has("a3_35"):
					out["a3_35"] = block
				elif not out.has("a3_16"):
					out["a3_16"] = block
			elif curve == "4":
				if not out.has("a4"):
					out["a4"] = block
		i += 1
	return out


# ---- D9：两本的实际内容 ------------------------------------------------

func _d9_pair() -> void:
	var real := DiaryMarkup.parse(DiaryTexts.RAW_MILL, true)
	var fake := DiaryMarkup.parse(DiaryTexts.FAKE_MILL, false)
	_ok(DiaryMarkup.has_kind(real, DiaryMarkup.KIND_STRIKE), "D9 真本里有划掉的旧字")
	_ok(DiaryMarkup.has_kind(real, DiaryMarkup.KIND_RED), "D9 真本里有红色改正")
	_ok(not DiaryMarkup.has_kind(fake, DiaryMarkup.KIND_STRIKE), "D9 假本里没有划线")
	_ok(not DiaryMarkup.has_kind(fake, DiaryMarkup.KIND_RED), "D9 假本里没有红字")
	# 两本的分隔线都必须在（陷阱③：假本也要处理 ---）
	_ok(DiaryMarkup.has_kind(real, DiaryMarkup.KIND_SEP), "D9 真本有分隔行")
	_ok(DiaryMarkup.has_kind(fake, DiaryMarkup.KIND_SEP), "D9 假本有分隔行")
	# 真本四处涂改 → 四处划线
	_ok(_texts(real, DiaryMarkup.KIND_STRIKE).size() == 4,
		"D9 真本正好四处涂改：%d" % _texts(real, DiaryMarkup.KIND_STRIKE).size())
	# 两本的「干净内容」应当一致：假本 = 真本去掉划线后的正文
	var real_plain := DiaryMarkup.plain_text(real)
	var fake_plain := DiaryMarkup.plain_text(fake)
	_ok(real_plain.length() > fake_plain.length(),
		"D9 真本比假本长（多出被划掉的旧字）：%d > %d" % [real_plain.length(), fake_plain.length()])


# ---- D10：不产生 BBCode --------------------------------------------------

func _d10_no_bbcode() -> void:
	var bad: Array = []
	for item in [[DiaryTexts.RAW_MILL, true], [DiaryTexts.FAKE_MILL, false],
			[DiaryTexts.ZHOU_LEDGER, true], [DiaryTexts.ZHOU_LEDGER, false],
			[DiaryTexts.LU_FRAGMENT, true], ["{{甲|乙|丙}}", true], ["x---y", false]]:
		var segs := DiaryMarkup.parse(String(item[0]), bool(item[1]))
		for seg in segs:
			var txt := String((seg as Dictionary).get("text", ""))
			for tag in ["[s]", "[/s]", "[color", "[/color]", "[b]", "[center", "[lb]"]:
				if _has_sub(txt, tag):
					bad.append(tag)
		# 段的 key 只有 kind / text，不许塞 markup 字符串
		for seg in segs:
			var keys: Array = (seg as Dictionary).keys()
			if keys.size() > 2 or not keys.has("kind"):
				bad.append(str(keys))
	_ok(bad.is_empty(), "D10 解析结果里没有 BBCode / 多余字段：%s" % str(bad))


# ---- L1–L6：排版（headless 量得出字，所以行位/行高/折行也进回归）---------

func _ops(res: Dictionary, t: String) -> Array:
	var out: Array = []
	for op in (res.ops as Array):
		if String((op as Dictionary).get("t", "")) == t:
			out.append(op)
	return out


func _new_page(raw: bool, text: String) -> Control:
	var p: Control = DiaryPage.new()
	p.size = Vector2(470.0, 648.0)      # 与 DiaryView.PAGE_W / PAGE_H 一致
	p.set_page("t", raw, DiaryMarkup.parse(text, raw))
	return p


func _layout_checks() -> void:
	var fake := _new_page(false, DiaryTexts.FAKE_MILL)
	var real := _new_page(true, DiaryTexts.RAW_MILL)
	var f_res: Dictionary = fake.compute_layout(fake.body_top(), fake.text_width())
	var r_res: Dictionary = real.compute_layout(real.body_top(), real.text_width())
	var room: float = real.size.y - real.body_top() - DiaryPage.PAD - DiaryPage.FOOTER_H
	print("LAYOUT fake_h=%.1f real_h=%.1f room=%.1f ops=%d/%d" % [
		float(f_res.height), float(r_res.height), room,
		(f_res.ops as Array).size(), (r_res.ops as Array).size()])

	# L1 一页装得下（装不下就得靠滚动，那要单独说，不能默默溢出）
	_ok(float(f_res.height) > 0.0 and float(r_res.height) > 0.0, "L1 两本都量出了正文高度")
	_ok(float(f_res.height) <= room + 0.5,
		"L1 假本一页装得下（%.1f ≤ %.1f）" % [float(f_res.height), room])
	_ok(float(r_res.height) <= room + 0.5,
		"L1 真本一页装得下（%.1f ≤ %.1f）" % [float(r_res.height), room])

	# L2 删除线：真本四条、假本零条，且压在 y + ascent - fs*0.30
	_ok(_ops(r_res, "ln").size() == 4,
		"L2 真本正好画四条删除线：%d" % _ops(r_res, "ln").size())
	_ok(_ops(f_res, "ln").size() == 0,
		"L2 假本一条删除线都不画：%d" % _ops(f_res, "ln").size())
	var ln_ok := true
	for op in _ops(r_res, "ln"):
		var found := false
		for c in _ops(r_res, "ch"):
			if String(c.k) == DiaryMarkup.KIND_STRIKE \
					and absf(float(c.y) - (float(op.y) + 17.0 * 0.30)) < 0.01:
				found = true
				break
		if not found:
			ln_ok = false
	_ok(ln_ok, "L2 删除线压在「基线 - 17*0.30」上（±0.01）")

	# L3 行首制表符：那一行右移，换行后缩进收回
	var ind := _new_page(false, "\t甲。\n乙。")
	var i_res: Dictionary = ind.compute_layout(ind.body_top(), ind.text_width())
	var xj := -1.0
	var xy := -1.0
	for op in _ops(i_res, "ch"):
		if String(op.c) == "甲":
			xj = float(op.x)
		if String(op.c) == "乙":
			xy = float(op.x)
	_ok(is_equal_approx(xj, DiaryPage.PAD + DiaryPage.INDENT_W),
		"L3 制表符那一行右移 %.0fpx（x=%.1f）" % [DiaryPage.INDENT_W, xj])
	_ok(is_equal_approx(xy, DiaryPage.PAD), "L3 换行后缩进收回（x=%.1f）" % xy)

	# L4 分隔行：一本两条，各自独占一行
	_ok(_ops(f_res, "sep").size() == 2 and _ops(r_res, "sep").size() == 2,
		"L4 两本各有两条分隔行：%d/%d" % [_ops(f_res, "sep").size(), _ops(r_res, "sep").size()])
	var sep_alone := true
	for op in _ops(f_res, "sep"):
		var y := float(op.y)
		for c in _ops(f_res, "ch"):
			if absf(float(c.y) - y) < 0.01:
				sep_alone = false
	_ok(sep_alone, "L4 分隔行独占一行（没有字和它挤在同一行）")

	# L5 行距是 26px 的整数倍（中间的空行也占一行，所以差值是 26 的倍数）
	var lines: Array = []
	for op in _ops(f_res, "ch") + _ops(f_res, "sep"):
		var y := float(op.y)
		if not lines.has(y):
			lines.append(y)
	lines.sort()
	var gap_ok := lines.size() >= 10
	for k in range(1, lines.size()):
		var gap := float(lines[k]) - float(lines[k - 1])
		if gap <= 0.0 or absf(gap / DiaryPage.LINE_H - roundf(gap / DiaryPage.LINE_H)) > 0.001:
			gap_ok = false
			print("  行距异常：%.1f → %.1f 差 %.1f" % [float(lines[k - 1]), float(lines[k]), gap])
	_ok(gap_ok, "L5 行距恒为 %.0fpx 的整数倍（%d 行有字）"
		% [DiaryPage.LINE_H, lines.size()])
	_ok(is_equal_approx(float(f_res.height), roundf(float(f_res.height) / DiaryPage.LINE_H) * DiaryPage.LINE_H),
		"L5 整页高度是行距的整数倍：%.1f" % float(f_res.height))

	# L6 折行：一行排不下就换行，不能冲出纸面右侧
	var long := _new_page(false, "甲".repeat(40))
	var l_res: Dictionary = long.compute_layout(long.body_top(), long.text_width())
	var right: float = DiaryPage.PAD + long.text_width()
	var inside := true
	var cw: float = long.font.get_string_size("甲", HORIZONTAL_ALIGNMENT_LEFT, -1, DiaryPage.FS).x
	for op in _ops(l_res, "ch"):
		if float(op.x) + cw > right + 0.01:
			inside = false
	var l_lines: Array = []
	for op in _ops(l_res, "ch"):
		if not l_lines.has(float(op.y)):
			l_lines.append(float(op.y))
	_ok(inside, "L6 折行后没有字冲出右边（右界 %.1f）" % right)
	_ok(l_lines.size() == 2, "L6 40 个汉字在 434px 里折成两行：%d" % l_lines.size())

	fake.free()
	real.free()
	ind.free()
	long.free()


# ---- P1–P6：分页 + 页脚箭头（仿 Minecraft 的书）-------------------------

func _page_checks() -> void:
	var fake := _new_page(false, DiaryTexts.FAKE_MILL)
	var real := _new_page(true, DiaryTexts.RAW_MILL)

	# P1 默认纸高（470×648）：两本都一页装得下，箭头留着但灰掉
	_ok(fake.page_count() == 1 and real.page_count() == 1,
		"P1 默认纸高两本各一页：%d/%d" % [fake.page_count(), real.page_count()])
	_ok(fake.page_text() == "1 / 1", "P1 页码文字是「1 / 1」：%s" % fake.page_text())
	_ok(not fake.can_prev() and not fake.can_next(), "P1 只有一页时两个箭头都不可用")
	_ok(fake.hit_arrow(fake.arrow_rect(-1).get_center()) == 0
		and fake.hit_arrow(fake.arrow_rect(1).get_center()) == 0,
		"P1 只有一页时点箭头没有任何反应（按钮留着，和 Minecraft 一样）")

	# P2 纸高压小就必须分页，而且按「行」切、不漏行、不多出空页
	var small := _new_page(false, DiaryTexts.FAKE_MILL)
	small.size = Vector2(470.0, 300.0)
	var n: int = small.page_count()
	var cap: int = small.per_page_lines()
	var lines: int = small.line_count()
	_ok(n >= 2, "P2 纸高压到 300 就分成多页：%d 页（每页 %d 行）" % [n, cap])
	_ok(cap * n >= lines and (n - 1) * cap < lines,
		"P2 分页刚好盖住 %d 行（%d 页 × %d 行）" % [lines, n, cap])

	# P3 翻到两头就停住，页码跟着走
	small.goto_page(0)
	_ok(small.page_text() == "1 / %d" % n, "P3 首页页码：%s" % small.page_text())
	small.prev_page()
	_ok(small.page_index() == 0, "P3 首页再往前翻不动")
	for i in n + 3:
		small.next_page()
	_ok(small.page_index() == n - 1, "P3 一直往后翻停在末页：%d/%d" % [small.page_index() + 1, n])
	_ok(small.page_text() == "%d / %d" % [n, n], "P3 末页页码：%s" % small.page_text())

	# P4 命中区：右箭头 = 后一页；首页点左、末页点右都没反应
	small.goto_page(0)
	_ok(small.hit_arrow(small.arrow_rect(1).get_center()) == 1, "P4 多页时点右箭头 = 后一页")
	_ok(small.hit_arrow(small.arrow_rect(-1).get_center()) == 0, "P4 首页点左箭头不响应")
	small.goto_page(1)
	_ok(small.hit_arrow(small.arrow_rect(-1).get_center()) == -1, "P4 第二页点左箭头 = 前一页")

	# P5 箭头画在页脚里、左右贴着内边距（不会被正文压住）
	var ar_l: Rect2 = fake.arrow_rect(-1)
	var ar_r: Rect2 = fake.arrow_rect(1)
	_ok(ar_r.position.y >= 648.0 - DiaryPage.FOOTER_H - 0.01
		and ar_r.position.y + ar_r.size.y <= 648.0 + 0.01,
		"P5 箭头落在页脚里（y=%.1f..%.1f）" % [ar_r.position.y, ar_r.position.y + ar_r.size.y])
	_ok(is_equal_approx(ar_l.position.x, DiaryPage.PAD)
		and is_equal_approx(ar_r.position.x + ar_r.size.x, 470.0 - DiaryPage.PAD),
		"P5 两个箭头贴左右内边距（x=%.1f / %.1f）"
		% [ar_l.position.x, ar_r.position.x + ar_r.size.x])
	_ok(ar_l.position.x + ar_l.size.x < ar_r.position.x, "P5 左右箭头不重叠（中间留给页码）")

	# P6 真本同样按行分页（不是只对假本生效）
	var small2 := _new_page(true, DiaryTexts.RAW_MILL)
	small2.size = Vector2(470.0, 300.0)
	_ok(small2.page_count() >= 2 and small2.line_count() == real.line_count(),
		"P6 真本按行分页：%d 页 / %d 行" % [small2.page_count(), small2.line_count()])

	fake.free()
	real.free()
	small.free()
	small2.free()


# ---- S1/S2/S4：静态自检 --------------------------------------------------

func _read(path: String) -> String:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return ""
	var s := f.get_as_text()
	f.close()
	return s


func _s_static() -> void:
	var page_src := _read("res://scripts/diary_page.gd")
	var markup_src := _read("res://scripts/diary_markup.gd")
	var view_src := _read("res://scripts/diary_view.gd")

	_ok(page_src != "" and markup_src != "" and view_src != "", "S1 三个脚本都读得到")
	# 删除线自绘：页面里不许有 RichTextLabel，必须有 draw_line
	_ok(not _has_sub(page_src, "RichTextLabel"), "S1 diary_page.gd 里没有 RichTextLabel")
	_ok(_has_sub(page_src, "draw_line("), "S1 diary_page.gd 里自己画删除线（draw_line）")
	_ok(not _has_sub(markup_src, "[s]"), "S2 diary_markup.gd 里没有 [s]")
	_ok(not _has_sub(view_src, "HBoxContainer")
		and not _has_sub(view_src, "PanelContainer"), "S4 双本不是用容器拼的（手动摆位）")
	# 参数必须是定稿值（防止有人回头抄 render3 的早期试色 #9a9080）
	_ok(_has_sub(page_src, "#8f8474") and not _has_sub(page_src, "#9a9080"),
		"S4 划掉字色是定稿 #8f8474，不是早期试色 #9a9080")
	_ok(_has_sub(page_src, "#8b2f2f") and _has_sub(page_src, "#3a2f22"),
		"S4 改正字红 #8b2f2f / 墨色 #3a2f22")
	_ok(_has_sub(page_src, "const FS := 17") and _has_sub(page_src, "const LINE_H := 26.0"),
		"S4 字号 17 / 行高 26")
	_ok(_has_sub(page_src, "const STRIKE_W := 2.0") and _has_sub(page_src, "STRIKE_DY := 0.30"),
		"S4 删除线 2px、位置 y + ascent - fs*0.30")


# ---- S5/S6：界面能建起来、开关门对 --------------------------------------

func _view_smoke() -> void:
	var v: Control = DiaryView.new()
	root.add_child(v)
	_ok(not v.is_open(), "S5 界面默认收起")
	_ok(v.left_page != null and v.right_page != null, "S5 两张纸都建出来了")
	_ok((v.left_page.segments as Array).size() > 0, "S5 左页灌进了段数据")
	_ok((v.right_page.segments as Array).size() > 0, "S5 右页灌进了段数据")
	_ok(DiaryMarkup.has_kind(v.right_page.segments, DiaryMarkup.KIND_STRIKE),
		"S5 右页是真本（有划线）")
	_ok(not DiaryMarkup.has_kind(v.left_page.segments, DiaryMarkup.KIND_STRIKE),
		"S5 左页是假本（没划线）")
	_ok(v.left_page.is_raw_book == false and v.right_page.is_raw_book == true,
		"S5 纸色跟着真假本走")
	v.open_view()
	_ok(v.is_open(), "S6 open_view 之后 is_open 为真")
	v.toggle()
	_ok(not v.is_open(), "S6 toggle 一下又收起")
	v.open_view()
	v.close_view()
	_ok(not v.is_open(), "S6 close_view 之后收起")
	v.queue_free()


# ---- V1–V6：键位与点箭头（E 开合同键 / Esc / 点箭头翻页）----------------

## 造一个「按下」的键事件（逻辑键与物理键都给，跟真实输入一致）。
func _key(code: int) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = code
	e.physical_keycode = code
	e.pressed = true
	return e


func _view_input_checks() -> void:
	var v: Control = DiaryView.new()
	root.add_child(v)
	v.size = Vector2(1280.0, 720.0)
	v._layout()

	# V1 Esc 合上
	v.open_view()
	v._input(_key(KEY_ESCAPE))
	_ok(not v.is_open(), "V1 Esc 合上书本")
	_ok(v.just_closed(),
		"V1 合上那一帧 just_closed() 为真（主流程靠它防「合上又被 E 立刻翻开」）")

	# V2 E 也能合上（开合是同一个键）
	v.open_view()
	v._input(_key(KEY_E))
	_ok(not v.is_open(), "V2 E 同样能合上书本")

	# V3 点页脚右箭头 → 两本一起往后翻一页
	v.open_view()
	v.left_page.size = Vector2(470.0, 300.0)
	v.right_page.size = Vector2(470.0, 300.0)
	var pages := int(v.left_page.page_count())
	_ok(pages >= 2, "V3 纸压小之后有多页可翻：%d 页" % pages)
	var mb := InputEventMouseButton.new()
	mb.button_index = MOUSE_BUTTON_LEFT
	mb.pressed = true
	mb.position = v.left_page.global_position + v.left_page.arrow_rect(1).get_center()
	v._input(mb)
	_ok(int(v.left_page.page_index()) == 1, "V3 点左页右箭头 → 翻到第 2 页")
	_ok(int(v.right_page.page_index()) == 1, "V3 两本一起翻（对照阅读不脱节）")

	# V4 点正文（不是箭头）不该翻页
	var before := int(v.left_page.page_index())
	mb.position = v.left_page.global_position + Vector2(200.0, 200.0)
	v._input(mb)
	_ok(int(v.left_page.page_index()) == before, "V4 点纸面正文不翻页")

	# V5 → 键继续往后翻，末页停住
	v._input(_key(KEY_RIGHT))
	_ok(int(v.left_page.page_index()) == mini(2, pages - 1),
		"V5 → 键往后翻：%d/%d" % [int(v.left_page.page_index()) + 1, pages])

	# V6 收起状态下按键不会把界面弄开
	v.close_view()
	v._input(_key(KEY_RIGHT))
	_ok(not v.is_open(), "V6 收起状态下按键不会打开界面")
	v.queue_free()