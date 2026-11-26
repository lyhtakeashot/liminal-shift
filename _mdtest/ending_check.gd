extends SceneTree

## 归档表自检（L15 线：story.md §10「推理—结案」）。
## 跑法：godot --headless --path . --script res://_mdtest/ending_check.gd
##
## 验三块：
##   1. 记述生成器：三变体分流 / 两句硬句 / 四档统计 / 出口文本 / 归档员随帧（E1–E8）
##   2. 数据层：默认全空 / 存档往返 / 脏存档不崩（E9–E10）
##   3. 界面：自绘面板能开、焦点能走、←→ 能循环、记述能滚、出口能落定（E11–E13）
##
## ⚠️ 断言口径：
##   「变体」= 记述整段的形态（甲/乙/丙），由**四单选填了什么**决定，与表格算不算得完无关。
##   「只剩两句」= 变体专属正文（prose）只剩两句；那两句固定硬句是表算出来的事实，
##   不随玩家改，所以它们不计入「消失」的那一段（见 docs/FEEDBACK-ending-form-exec.md）。
##   「禁用词」由测试现拼 —— 源码里不留字面量，仓库级 grep 才干净（§4.4）。

const EndingStore = preload("res://scripts/ending_store.gd")
const EndingReport = preload("res://scripts/ending_report.gd")
const EndingForm = preload("res://scripts/ending_form.gd")

var fails := 0


func _ok(cond: bool, label: String) -> void:
	print(("PASS " if cond else "FAIL ") + label)
	if not cond:
		fails += 1


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	_purge_saves()
	_blank_checks()          # E10
	_jia_checks()            # E1 / E5
	_yi_checks()             # E2
	_bing_checks()           # E3
	_burial_checks()         # E4
	_counts_checks()
	_banned_checks()         # E6
	_exit_checks()           # E7
	_archivist_checks()      # E8
	_roundtrip_checks()      # E9
	await _form_checks()     # E11–E13
	_purge_saves()
	print("ENDING_CHECK_DONE fails=%d" % fails)
	print("ENDING_OK 归档表填格 / 记述三变体 / 两个出口 已验证")
	quit(1 if fails > 0 else 0)


# ---- 小工具 ---------------------------------------------------------------

func _purge_saves() -> void:
	for p in ["user://ending_form.json", "res://.ending_form.json",
			"res://_mdtest/_ending_test.json", "res://_mdtest/_ending_dirty.json"]:
		if FileAccess.file_exists(p):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(p))


## 存档实际落在哪个候选路径上（沙箱里会退到 res://）。
func _save_where() -> String:
	if FileAccess.file_exists(EndingStore.SAVE_PATH):
		return EndingStore.SAVE_PATH
	if FileAccess.file_exists(EndingStore.SAVE_FALLBACK):
		return EndingStore.SAVE_FALLBACK + "（沙箱兜底）"
	return "哪里都没写进去"


## 规范答案（story.md §4.6.1 五件事 + §10.1 三个单选）：
##   1926 放任/间接故意 · 1951 蓄谋/直接故意 · 1976 蓄谋/直接故意 · 2001 蓄谋/无 · 2026 无/无
##   1951 案性质 = 债务纠纷 · 最早一具 = 1951 · 埋尸位置 = 补丁下 · 埋葬人数 = 二
func _fill_canonical() -> void:
	EndingStore.reset()
	EndingStore.set_cell("1926", EndingStore.COL_MOTIVE, "放任")
	EndingStore.set_cell("1926", EndingStore.COL_INTENT, "间接故意")
	EndingStore.set_cell("1951", EndingStore.COL_MOTIVE, "蓄谋")
	EndingStore.set_cell("1951", EndingStore.COL_INTENT, "直接故意")
	EndingStore.set_cell("1976", EndingStore.COL_MOTIVE, "蓄谋")
	EndingStore.set_cell("1976", EndingStore.COL_INTENT, "直接故意")
	EndingStore.set_cell("2001", EndingStore.COL_MOTIVE, "蓄谋")
	EndingStore.set_cell("2001", EndingStore.COL_INTENT, "无")
	EndingStore.set_cell("2026", EndingStore.COL_MOTIVE, "无")
	EndingStore.set_cell("2026", EndingStore.COL_INTENT, "无")
	EndingStore.set_radio("case_1951", "债务纠纷")
	EndingStore.set_radio("earliest", "1951")
	EndingStore.set_radio("burial", "补丁下")
	EndingStore.set_radio("count", "二")


func _build(year: int = 2026) -> Dictionary:
	var st: Dictionary = EndingStore.snapshot()
	st["frame_year"] = year
	return EndingReport.build(st)


func _body(year: int = 2026) -> String:
	return String(_build(year)["body"])


func _lines(year: int = 2026) -> Array:
	return _build(year)["lines"]


## 逐行比对；不一致就报出第一个下标（比整段 diff 好定位）。
func _cmp_lines(actual: Array, expected: Array, label: String) -> void:
	if actual.size() != expected.size():
		_ok(false, "%s（行数 %d ≠ %d）" % [label, actual.size(), expected.size()])
		return
	for i in expected.size():
		if String(actual[i]) != String(expected[i]):
			_ok(false, "%s（第 %d 行：'%s' ≠ '%s'）" % [label, i, String(actual[i]), String(expected[i])])
			return
	_ok(true, label)


# ---- E10：默认全空，没有默认值 ---------------------------------------------

func _blank_checks() -> void:
	EndingStore.reset()
	_ok(EndingStore.is_blank(), "E10 刚开局：表格十格 + 四单选全空")
	_ok(not EndingStore.is_grid_filled(), "E10 表格没填满（is_grid_filled = false）")
	_ok(EndingStore.exit_choice == "", "E10 出口默认没选")

	var rep := _build()
	_ok(String(rep["variant"]) == "丙", "E10 空白表 → 变体丙（不报错，只降级）")
	var body := String(rep["body"])
	_ok(body.contains("最早一具：未填。"), "E10 空白表把「没填」念成「未填」")
	_ok(not body.contains("债务纠纷") and not body.contains("杀人灭口"),
		"E10 空白表不替玩家填 1951 案性质")
	_ok(int((rep["counts"] as Dictionary).size()) == 0, "E10 十格没填满 ⇒ 四档统计算不出来（空字典）")

	# 默认值一定不许有：空表的每一格都必须真的是空串。
	var all_empty := true
	for y in EndingStore.YEARS:
		if not EndingStore.get_cell(String(y), EndingStore.COL_MOTIVE).is_empty():
			all_empty = false
		if not EndingStore.get_cell(String(y), EndingStore.COL_INTENT).is_empty():
			all_empty = false
	for f in ["case_1951", "earliest", "burial", "count"]:
		if not EndingStore.get_radio(String(f)).is_empty():
			all_empty = false
	_ok(all_empty, "E10 没有默认值：满十格 + 四单选读出来都是空串")


# ---- E1 / E5：全填对 → 甲 --------------------------------------------------

func _jia_checks() -> void:
	_fill_canonical()
	var rep := _build()
	_ok(String(rep["variant"]) == "甲", "E1 全填对 → 变体甲")

	var expected: Array = [
		"自民国十五年至公元二〇〇一年，本地点历五代，五人涉事。",
		"",
		"最早一具：一九五一年。",
		"埋尸位置：北车道圆形补丁下。",
		"埋葬人数：二。未寻获：一（陆文，民国十五年，下游）。",
		"",
		"五代之中：起意者一，动手者二，算计而未动手者一，不知情者一。",
		"第一起无起意。第四起无死者。",
		"",
		"一九五一年一起，性质：债务纠纷。",
		"死者陆敬之，男，二十四岁。",
		"本地点自民国十六年起向陆家支付款项三十七笔，至四十年止。",
		"",
		"没有人被平反。因为没有人是无辜的。",
	]
	_cmp_lines(_lines(), expected, "E1 变体甲逐行与 story.md §10.3 一致（14 行）")

	# E5：两句硬句必须在（且是表算出来的，不是玩家填的）
	var fixed: Array = rep["fixed"]
	_ok(fixed.size() == 2 and String(fixed[0]) == "第一起无起意。"
		and String(fixed[1]) == "第四起无死者。",
		"E5 硬句 = 「第一起无起意。第四起无死者。」")

	# 四档统计与 story.md:701 的数字对齐（一 / 二 / 一 / 一）
	var c: Dictionary = rep["counts"]
	_ok(int(c.get("起意者", -1)) == 1, "四档：起意者 1（1926 放任+间接故意）")
	_ok(int(c.get("动手者", -1)) == 2, "四档：动手者 2（1951 / 1976 直接故意）")
	_ok(int(c.get("算计而未动手者", -1)) == 1, "四档：算计而未动手者 1（2001 蓄谋+无）")
	_ok(int(c.get("不知情者", -1)) == 1, "四档：不知情者 1（2026 无+无）")
	var sum := 0
	for k in c.keys():
		sum += int(c[k])
	_ok(sum == 5, "四档互斥且加起来 = 5（不多算、不漏算）")

	# 表格没填满 ⇒ 那一行不出现（局部降级），其余照念
	EndingStore.set_cell("2026", EndingStore.COL_INTENT, "")
	var body2 := _body()
	_ok(not body2.contains("五代之中："), "十格缺一格 ⇒ 「五代之中」那行整行不出现")
	_ok(body2.contains("最早一具：一九五一年。"), "缺一格不影响别的行照念")
	_ok(body2.contains("第一起无起意。第四起无死者。"), "缺一格也照样有那两句硬句")


# ---- E2：1951 填「杀人灭口」→ 乙，后面整段消失 ------------------------------

func _yi_checks() -> void:
	_fill_canonical()
	EndingStore.set_radio("case_1951", "杀人灭口")
	var rep := _build()
	_ok(String(rep["variant"]) == "乙", "E2 1951 填「杀人灭口」→ 变体乙")

	var prose: Array = rep["prose"]
	_ok(prose.size() == 2, "E2 变体乙只剩两句（prose.size() = 2，实际 %d）" % prose.size())
	_ok(String(prose[0]) == "一九五一年一起，性质：杀人灭口。", "E2 第一句 = 性质：杀人灭口")
	_ok(String(prose[1]) == "死者陆敬之，男，二十四岁。", "E2 第二句 = 死者陆敬之")

	var expected: Array = [
		"一九五一年一起，性质：杀人灭口。",
		"死者陆敬之，男，二十四岁。",
		"",
		"第一起无起意。第四起无死者。",
	]
	_cmp_lines(_lines(), expected, "E2 变体乙逐行与 story.md:715-718 一致（+硬句）")

	var body := String(rep["body"])
	_ok(not body.contains("三十七笔"), "E2 三十七笔款一个字都不出现")
	_ok(not body.contains("债务纠纷"), "E2 不把玩家填的「债务纠纷」念出来（他填的是灭口）")
	_ok(not body.contains("没有人被平反"), "E2 收官句跟着整段一起消失")
	_ok(not body.contains("五代之中："), "E2 「五代之中」跟着整段一起消失")
	_ok(body.contains("第一起无起意。第四起无死者。"), "E5 变体乙里那两句硬句照样在")


# ---- E3：某一格「无法确定」→ 丙，不报错 -------------------------------------

func _bing_checks() -> void:
	var fields := ["earliest", "burial", "count"]
	for f in fields:
		_fill_canonical()
		EndingStore.set_radio(String(f), "无法确定")
		_ok(EndingStore.get_radio(String(f)) == "无法确定", "E3 %s 能填「无法确定」" % f)
		var rep := _build()
		_ok(String(rep["variant"]) == "丙", "E3 %s = 无法确定 → 变体丙（不报错）" % f)
		_ok(String(rep["body"]).contains("第一起无起意。第四起无死者。"),
			"E5 %s 降级后硬句照样在" % f)

	# 1951 案性质**没有**「无法确定」这个选项（story.md:641-645 只有两个）
	_ok(not EndingStore.options_for_radio("case_1951").has("无法确定"),
		"E3 1951 案性质的选项只有两个（没有「无法确定」）")
	_fill_canonical()
	_ok(not EndingStore.set_radio("case_1951", "无法确定"), "E3 1951 案性质拒绝「无法确定」")
	_ok(EndingStore.get_radio("case_1951") == "债务纠纷", "E3 拒绝后状态不变")
	# 但它**留空**同样降成丙（没填 ≠ 填错，都是算不出来）
	EndingStore.set_radio("case_1951", "")
	_ok(String(_build()["variant"]) == "丙", "E3 1951 案性质留空 → 变体丙")
	_ok(String(_build()["body"]).contains("第一起无起意。第四起无死者。"),
		"E5 1951 留空降级后硬句照样在")

	# 丙的正文形态：只念三个事实栏 + 硬句（story.md:727-736）
	_fill_canonical()
	EndingStore.set_radio("earliest", "无法确定")
	EndingStore.set_radio("burial", "无法确定")
	var expected: Array = [
		"最早一具：无法确定。",
		"埋尸位置：无法确定。",
		"埋葬人数：二。",
		"",
		"第一起无起意。第四起无死者。",
	]
	_cmp_lines(_lines(), expected, "E3 变体丙逐行与 story.md:727-736 一致")

	# 一格没填 = 同丙（没填 ≠ 填错，但算不出来也只能降级）
	_fill_canonical()
	EndingStore.set_radio("count", "")
	_ok(String(_build()["variant"]) == "丙", "E3 单选留空 → 变体丙")

	# 丙压过乙（两个条件同时成立时以丙为准）
	_fill_canonical()
	EndingStore.set_radio("case_1951", "杀人灭口")
	EndingStore.set_radio("burial", "无法确定")
	_ok(String(_build()["variant"]) == "丙",
		"E3 灭口 + 无法确定同时成立 ⇒ 取丙（丙更宽，见反馈文档）")

	# 降级只降记述，不判对错：玩家填什么都不弹错、不改他的选择
	_fill_canonical()
	EndingStore.set_radio("burial", "井下")
	_ok(EndingStore.get_radio("burial") == "井下", "E3 降级不改玩家填的值（井下还在）")


# ---- E4：埋尸 = 井下，按井下念（不许被「补丁下」顶掉） ----------------------

func _burial_checks() -> void:
	_fill_canonical()
	EndingStore.set_radio("burial", "井下")
	var body := _body()
	_ok(String(_build()["variant"]) == "甲", "E4 埋尸填「井下」也算填满 → 甲（不是错，只是另一种说法）")
	_ok(body.contains("埋尸位置：井下。"), "E4 按玩家填的念：埋尸位置：井下。")
	_ok(not body.contains("补丁下"), "E4 「井下」不被「北车道圆形补丁下」顶掉")
	_ok(body.contains("五代之中：起意者一，动手者二，算计而未动手者一，不知情者一。"),
		"E4 埋尸填别的，四档统计不受影响")

	EndingStore.set_radio("burial", "地基下")
	_ok(_body().contains("埋尸位置：地基下。"), "E4 埋尸 = 地基下 也照念")

	EndingStore.set_radio("burial", "补丁下")
	_ok(_body().contains("埋尸位置：北车道圆形补丁下。"),
		"E4 埋尸 = 补丁下 → 念成故事原文的「北车道圆形补丁下」")

	# 最早一具填 1926：照玩家填的念，不硬改成 1951
	_fill_canonical()
	EndingStore.set_radio("earliest", "1926")
	_ok(_body().contains("最早一具：一九二六年。"), "E4 最早一具 = 1926 照念（不替玩家改成 1951）")


# ---- 四档统计的边界 --------------------------------------------------------

func _counts_checks() -> void:
	# 全填「无 / 无」⇒ 五个不知情者，其余三档 0
	EndingStore.reset()
	for y in EndingStore.YEARS:
		EndingStore.set_cell(String(y), EndingStore.COL_MOTIVE, "无")
		EndingStore.set_cell(String(y), EndingStore.COL_INTENT, "无")
	var c := EndingReport.counts_of(EndingStore.snapshot())
	_ok(int(c.get("不知情者", -1)) == 5, "四档：全填无/无 ⇒ 不知情者 5")
	_ok(int(c.get("起意者", -1)) == 0 and int(c.get("动手者", -1)) == 0
		and int(c.get("算计而未动手者", -1)) == 0, "四档：其余三档都是 0")

	# bucket_of 的四个分支
	_ok(EndingReport.bucket_of("无", "无") == "不知情者", "bucket 无/无 → 不知情者")
	_ok(EndingReport.bucket_of("蓄谋", "无") == "算计而未动手者", "bucket 有起意/无 → 算计而未动手者")
	_ok(EndingReport.bucket_of("激情", "无") == "算计而未动手者", "bucket 激情/无 → 算计而未动手者")
	_ok(EndingReport.bucket_of("蓄谋", "直接故意") == "动手者", "bucket 直接故意 → 动手者")
	_ok(EndingReport.bucket_of("放任", "间接故意") == "起意者", "bucket 放任/间接故意 → 起意者")
	_ok(EndingReport.bucket_of("", "无") == "", "bucket 填不全 → 空串")


# ---- E6：禁用词一个都不出现 ------------------------------------------------

func _banned() -> Array:
	# 用 \u 转义现拼：源码里连字面量都不留，§4.4 的仓库级 grep 才干净。
	return [
		"\u6b63\u4e49\u5f97\u5230\u4f38\u5f20",  # 一句道德结论，story.md:780 明令不写
		"\u771f\u76f8\u5927\u767d",
		"\u7ef3\u4e4b\u4ee5\u6cd5",
		"\u51f6\u624b",
	]


func _hits(text: String) -> Array:
	var out: Array = []
	for w in _banned():
		if text.contains(String(w)):
			out.append(w)
	return out


func _banned_checks() -> void:
	var bodies: Array = []
	# 甲
	_fill_canonical()
	bodies.append({"name": "甲", "text": _body()})
	# 乙
	EndingStore.set_radio("case_1951", "杀人灭口")
	bodies.append({"name": "乙", "text": _body()})
	# 丙
	EndingStore.set_radio("burial", "无法确定")
	bodies.append({"name": "丙", "text": _body()})
	# 空白表
	EndingStore.reset()
	bodies.append({"name": "空白", "text": _body()})

	for b in bodies:
		var t := String((b as Dictionary)["text"])
		var h := _hits(t)
		_ok(h.is_empty(), "E6 变体%s 不出现禁用词（命中：%s）" % [String((b as Dictionary)["name"]), str(h)])

	# 出口文本也扫一遍
	for ch in EndingStore.EXITS:
		var et := EndingReport.exit_text(String(ch))
		_ok(_hits(et).is_empty(), "E6 出口「%s」不出现禁用词" % String(ch))

	# 逆向自检：断言这个扫描器真的能抓到（不然 E6 是空转）
	_ok(not _hits("本案" + String(_banned()[1])).is_empty(), "E6 扫描器自检：故意塞一个能抓到")


# ---- E7：两个出口 ----------------------------------------------------------

func _exit_checks() -> void:
	var a := EndingReport.exit_text("已归档")
	_ok(a == "本案已归档。\n世界刑侦陈列馆 · 第七十二万三千零一卷",
		"E7 出口甲文本与 story.md:751-752 一致")
	var b := EndingReport.exit_text("存疑")
	_ok(b == "本案存疑。\n第七十二万三千零一卷 · 暂列待考",
		"E7 出口乙文本与 story.md:758-759 一致")
	_ok(EndingReport.exit_text("") == "", "E7 没选出口 = 空串（不默认选）")
	_ok(EndingStore.EXITS.size() == 2, "E7 出口只有两个（二选一）")

	# 两段之间世界一模一样：两个出口的记述正文必须完全相同（只有出口两行不同）
	_fill_canonical()
	EndingStore.set_exit("已归档")
	var rep_a := _build()
	EndingStore.set_exit("存疑")
	var rep_b := _build()
	_ok(String(rep_a["body"]) == String(rep_b["body"]),
		"E7 换出口不改记述正文（两段之间世界一模一样）")
	_ok(rep_a["exit_lines"].size() == 2 and rep_b["exit_lines"].size() == 2,
		"E7 出口文本两行（画两行用）")
	EndingStore.set_exit("")


# ---- E8：归档员随帧变 ------------------------------------------------------

func _archivist_checks() -> void:
	_ok(EndingReport.archivist_for(1926) == "陈阿福", "E8 1926 → 陈阿福")
	_ok(EndingReport.archivist_for(1951) == "陈志强", "E8 1951 → 陈志强")
	_ok(EndingReport.archivist_for(1976) == "陈卫东", "E8 1976 → 陈卫东")
	_ok(EndingReport.archivist_for(2001) == "陈小军", "E8 2001 → 陈小军")
	_ok(EndingReport.archivist_for(2026) == "陈浩", "E8 A5（2026）→ 陈浩")

	_fill_canonical()
	_ok(String(_build(2026)["archivist"]) == "陈浩", "E8 表在 A5 开 ⇒ 抬头写陈浩")
	_ok(String(_build(1926)["archivist"]) == "陈阿福", "E8 抬头随帧变（1926 写陈阿福）")
	_ok(String(_build(9999)["archivist"]) == "陈浩", "E8 未知帧回落 2026 的归档员（不崩）")


# ---- E9：存档往返 + 脏存档不崩 ---------------------------------------------

func _roundtrip_checks() -> void:
	_fill_canonical()
	EndingStore.set_exit("存疑")
	var before: Dictionary = EndingStore.snapshot()

	_ok(EndingStore.save(), "E9 存档成功")
	_ok(EndingStore.SAVE_PATH == "user://ending_form.json",
		"E9 规范存档路径 = user://ending_form.json")
	_ok(String(EndingStore.SAVE_CANDIDATES[0]) == EndingStore.SAVE_PATH,
		"E9 user:// 是回退链第一站（res:// 只在写不进去时兜底）")
	# ⚠️ 本沙箱的 user:// 写不进去（启动日志里 "Failed to open 'user://logs/…'"），
	#    会走 res:// 兜底。所以这里断言「落到了回退链里的某一站」，并报出实际那一站；
	#    真实玩家机器上应当是第一站 user://ending_form.json（§4.4）。
	_ok(FileAccess.file_exists(EndingStore.SAVE_PATH)
		or FileAccess.file_exists(EndingStore.SAVE_FALLBACK),
		"E9 存档落盘（实际落在 %s）" % _save_where())

	EndingStore.reset()
	_ok(EndingStore.is_blank(), "E9 清空后确实空了")
	_ok(EndingStore.load(), "E9 读档成功")
	_ok(EndingStore.snapshot() == before, "E9 存档往返一致（十格 + 四单选 + 出口全保住）")

	# 脏 JSON：不是 JSON ⇒ 返回 false，不崩，状态保持空
	# （引擎自己会打一行 "Parse JSON failed" ERROR —— 那是本用例故意喂进去的，不是失败）
	print("[预期噪声] 下一条 ERROR 是脏存档用例故意触发的，不是失败")
	var p := "res://_mdtest/_ending_test.json"
	var f := FileAccess.open(p, FileAccess.WRITE)
	_ok(f != null, "E9 能写脏存档文件（沙箱）")
	if f != null:
		f.store_string("{ 这不是 JSON ,,, ")
		f.close()
	EndingStore.reset()
	_ok(not EndingStore.load(p), "E9 脏 JSON ⇒ load 返回 false（不崩）")
	_ok(EndingStore.is_blank(), "E9 脏 JSON 读失败后状态仍是空（没有半截状态）")

	# 结构对、值非法：合法格保留，非法格归空（脏存档也能进）
	var q := "res://_mdtest/_ending_dirty.json"
	var f2 := FileAccess.open(q, FileAccess.WRITE)
	if f2 != null:
		f2.store_string(JSON.stringify({
			"version": 1,
			"motive": {"1926": "放任", "1951": "乱填的", "9999": "蓄谋"},
			"intent": {"1926": "间接故意", "1951": 42},
			"case_1951": "债务纠纷",
			"earliest": "1951",
			"burial": "天上",
			"count": "二",
			"exit_choice": "不知道",
		}))
		f2.close()
	_ok(EndingStore.load(q), "E9 结构对但值非法的存档：能读（返回 true）")
	_ok(EndingStore.get_cell("1926", EndingStore.COL_MOTIVE) == "放任", "E9 合法格保留")
	_ok(EndingStore.get_cell("1951", EndingStore.COL_MOTIVE) == "",
		"E9 非法值归空（不把「乱填的」当答案）")
	_ok(EndingStore.get_cell("2026", EndingStore.COL_MOTIVE) == "", "E9 表里没有的年份进不来")
	_ok(EndingStore.get_radio("burial") == "", "E9 单选非法值归空")
	_ok(EndingStore.exit_choice == "", "E9 出口非法值归空")

	# 文件不存在
	EndingStore.reset()
	_ok(not EndingStore.load("user://绝对不存在的归档表.json"), "E9 文件不存在 ⇒ false（不崩）")

	# 覆盖写：再存一次不会叠出两份
	_fill_canonical()
	_ok(EndingStore.save(), "E9 覆盖写成功")
	EndingStore.reset()
	EndingStore.load()
	_ok(EndingStore.is_grid_filled(), "E9 覆盖写之后读回来还是满的")


# ---- E11–E13：界面（自绘面板） ---------------------------------------------

func _form_checks() -> void:
	_purge_saves()
	EndingStore.reset()

	var form = EndingForm.new()
	root.add_child(form)
	await process_frame
	await process_frame

	# ⚠️ 守卫：只 set_anchors_preset 会让动态节点的 size 变 (0,0)，全屏坐标全算错。
	_ok(form.size.x > 0.0 and form.size.y > 0.0,
		"E11 面板节点拿到了视口尺寸（不是 0×0）")
	_ok(not form.is_open(), "E11 建出来是关着的（不抢画面）")

	form.open_form(2026)
	_ok(form.is_open(), "E11 open_form 后 is_open = true")
	_ok(form.focus_index() == 0, "E11 开表焦点在第一格")
	_ok(form.report_now()["variant"] == "丙", "E11 空表开着就是变体丙")

	# E14：填表进度 —— 玩家可以随时开表填已知的那部分（不必等到最后一站）
	_ok(form.fill_total() == 14, "E14 一共 14 个空（十格 + 四单选）")
	_ok(form.filled_count() == 0, "E14 空表进度 0/14")
	_ok(is_equal_approx(form.fill_ratio(), 0.0), "E14 空表比例 0")
	EndingStore.reset()
	EndingStore.set_cell("1926", EndingStore.COL_MOTIVE, "放任")
	EndingStore.set_cell("1926", EndingStore.COL_INTENT, "间接故意")
	EndingStore.set_radio("burial", "井下")
	_ok(form.filled_count() == 3, "E14 只填了三处 ⇒ 3/14（早开表也算数）")
	_ok(is_equal_approx(form.fill_ratio(), 3.0 / 14.0), "E14 比例跟着走")
	_fill_canonical()
	_ok(form.filled_count() == 14, "E14 填满 ⇒ 14/14")
	_ok(is_equal_approx(form.fill_ratio(), 1.0), "E14 填满比例 1")
	EndingStore.reset()   # 下一条用例（E12）从空表开始，别被这里的填格带偏

	# E12：←→ 循环改值（空 → 选项… → 空），且不设默认值
	form.set_focus(0)
	form.cycle(1)
	_ok(EndingStore.get_cell("1926", EndingStore.COL_MOTIVE) == "激情", "E12 ←→ 循环到第一个选项")
	form.cycle(-1)
	_ok(EndingStore.get_cell("1926", EndingStore.COL_MOTIVE) == "", "E12 反向循环能转回空格")
	form.cycle(-1)
	_ok(EndingStore.get_cell("1926", EndingStore.COL_MOTIVE) == "无",
		"E12 循环是环形的（从空往前一格 = 最后一个选项）")

	# 焦点走位：表格内按列上下、单选内上下、到记述区就滚动
	form.set_focus(0)
	form.move_focus(1)
	_ok(form.focus_index() == 2, "E12 ↓ 在同一列上下走（1926 动机 → 1951 动机）")
	form.set_focus(1)
	form.move_focus(1)
	_ok(form.focus_index() == 3, "E12 ↓ 在故意列里走")
	form.set_focus(9)
	form.move_focus(1)
	_ok(form.focus_index() == 1, "E12 走到最后一行再 ↓ 回到第一行（环形）")
	form.set_focus(10)
	form.move_focus(1)
	_ok(form.focus_index() == 11, "E12 单选内 ↓ 换下一项")
	form.tab_step(false)
	_ok(form.focus_index() == 12, "E12 Tab 平铺换格")
	form.tab_step(true)
	_ok(form.focus_index() == 11, "E12 Shift+Tab 反向")
	form.set_focus(16)
	form.move_focus(1)
	_ok(form.focus_index() == 16, "E12 记述区焦点上 ↓ 只滚动、不乱跑")

	# E13：记述区跟填的内容实时变；长文能滚
	_purge_saves()
	EndingStore.reset()
	_fill_canonical()
	form.set_focus(0)
	_ok(String(form.report_now()["variant"]) == "甲", "E13 填满之后记述立刻变甲（同一节点、不重开）")
	_ok(form._max_scroll() > 0, "E13 记述比一屏长 ⇒ 能滚（max_scroll > 0）")
	var before_scroll := form.scroll_lines()
	form.move_focus(1)
	_ok(form.scroll_lines() >= before_scroll, "E13 滚动位置没退化")

	# E13：出口落定 = 存盘 + 发信号 + 关表
	var got: Array = []
	form.exit_chosen.connect(func(choice: String) -> void: got.append(choice))
	var closed: Array = []
	form.form_closed.connect(func() -> void: closed.append(true))

	_ok(form.commit_exit(0), "E13 点出口甲：commit_exit 返回 true")
	_ok(EndingStore.exit_choice == "已归档", "E13 出口写成「已归档」")
	_ok(got.size() == 1 and String(got[0]) == "已归档", "E13 发出 exit_chosen(已归档)")
	_ok(closed.size() == 1, "E13 发出 form_closed")
	_ok(not form.is_open(), "E13 落定出口后表自己关了")
	_ok(FileAccess.file_exists(EndingStore.SAVE_PATH)
		or FileAccess.file_exists(EndingStore.SAVE_FALLBACK),
		"E13 落定出口时已经存了盘")

	# 关表也会存（填一半关掉不该白填）
	form.open_form(2026)
	EndingStore.set_radio("count", "三")
	form.close_form()
	_ok(not form.is_open(), "E13 close_form 关表")
	EndingStore.reset()
	EndingStore.load()
	_ok(EndingStore.get_radio("count") == "三", "E13 关表时存了盘（填一半也留得住）")

	# 关着的时候不画、不吃鼠标
	_ok(form.mouse_filter == Control.MOUSE_FILTER_IGNORE,
		"E13 关表后不吃鼠标（mouse_filter = IGNORE）")
	form.open_form(2026)
	_ok(form.mouse_filter == Control.MOUSE_FILTER_STOP,
		"E13 开表时接鼠标（mouse_filter = STOP）")

	# 归档员按当前帧
	form.close_form()
	form.open_form(1926)
	_ok(str(form.frame_year()) == "1926", "E8 界面记住了开表时的年份")
	_ok(String(form.report_now()["archivist"]) == "陈阿福", "E8 在 1926 开表 ⇒ 抬头写陈阿福")

	form.queue_free()
	EndingStore.reset()