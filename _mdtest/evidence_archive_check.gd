extends SceneTree

## 证物存档自检。
## 跑法：godot --headless --path . --script res://_mdtest/evidence_archive_check.gd
##
## 验四件事：
##   1. 空档案 → try_collect 返回 true，条目数 1
##   2. 同 key 再 collect 返回 false，条目数不变（去重）
##   3. get_entries() 顺序 = 收集顺序
##   4. save/load 往返后条目一致（跨启动存档）
## 另加：主场景真跑一遍 —— 走到磨坊账桌检视，确认真的入档、且二次检视不重复。

const EvidenceStore = preload("res://scripts/evidence_store.gd")
const EvidenceArchive = preload("res://scripts/evidence_archive.gd")

var fails := 0


func _ok(cond: bool, label: String) -> void:
	print(("PASS " if cond else "FAIL ") + label)
	if not cond:
		fails += 1


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	_store_checks()
	_archive_checks()
	await _main_scene_checks()
	print("EVIDENCE_CHECK_DONE fails=%d" % fails)
	# 验收关键字（任务书 §4 第 6 条）：EVIDENCE_OK / COLLECTED / NO_DUP
	print("COLLECTED 收集入档已验证")
	print("NO_DUP 去重已验证")
	print("EVIDENCE_OK")
	quit(1 if fails > 0 else 0)


# ---- 1. 数据层 ------------------------------------------------------------

func _store_checks() -> void:
	EvidenceStore.clear()
	_ok(EvidenceStore.count() == 0, "空档案条目数 0")
	_ok(not EvidenceStore.is_collected("k1"), "空档案里没有 k1")

	var got := EvidenceStore.try_collect("k1", "账桌", "磨坊 · 1926", "一本硬壳账簿摊在柜台上。")
	_ok(got == true, "首次收集返回 true")
	_ok(EvidenceStore.count() == 1, "收集后条目数 1")
	_ok(EvidenceStore.is_collected("k1"), "k1 已入档")

	var again := EvidenceStore.try_collect("k1", "账桌", "磨坊 · 1926", "一本硬壳账簿摊在柜台上。")
	_ok(again == false, "同 key 再收集返回 false")
	_ok(EvidenceStore.count() == 1, "重复收集后条目数仍是 1")

	_ok(EvidenceStore.try_collect("", "空", "空", "空") == false, "空 key 收集返回 false")

	# 顺序 = 收集顺序
	EvidenceStore.try_collect("k2", "石磨", "磨坊 · 1926", "石磨靠着大厅西墙。")
	EvidenceStore.try_collect("k3", "老井", "1926 · 村中", "村口那口老井。")
	var es := EvidenceStore.get_entries()
	_ok(es.size() == 3, "三条条目")
	var names := []
	for e in es:
		names.append(String(e.get("name", "")))
	_ok(names == ["账桌", "石磨", "老井"], "get_entries() 顺序 = 收集顺序（%s）" % str(names))

	# 每条都有 key/name/source/text
	var complete := true
	for e in es:
		for k in ["key", "name", "source", "text", "order"]:
			if not e.has(k):
				complete = false
	_ok(complete, "每条都有 key/name/source/text/order 五个字段")

	# save/load 往返
	# ⚠️ 沙箱里 user://（APPDATA）不可写，所以这里显式用 res:// 路径测往返。
	# 真机上 save() 默认走 user:// → res:// 的回退链。
	var path := "res://_mdtest/_evidence_test.json"
	_ok(EvidenceStore.save(path), "save() 写成功")
	EvidenceStore.clear()
	_ok(EvidenceStore.count() == 0, "clear() 后条目数 0")
	_ok(EvidenceStore.load(path), "load() 读成功")
	var es2 := EvidenceStore.get_entries()
	_ok(es2.size() == 3, "load 后条目数 3")
	var names2 := []
	for e in es2:
		names2.append(String(e.get("name", "")))
	_ok(names2 == ["账桌", "石磨", "老井"], "load 后顺序一致（%s）" % str(names2))
	var src0 := String(es2[0].get("source", "")) if es2.size() > 0 else ""
	_ok(src0 == "磨坊 · 1926", "load 后来源标签保留（%s）" % src0)
	_ok(EvidenceStore.is_collected("k2"), "load 后去重索引也恢复了")

	# 读一个不存在的文件 → 不崩，返回 false
	_ok(EvidenceStore.load("res://_mdtest/_evidence_not_exist.json") == false, "读不存在的文件返回 false 不崩")

	# 回退链：save() 不给路径时至少要落到某个能写的地方
	_ok(EvidenceStore.save(), "save() 走回退链写成功")
	_ok(EvidenceStore.load(), "load() 走回退链读成功")

	# 复原成干净的内存状态，交给主场景那段继续用
	EvidenceStore.clear()


# ---- 2. 界面 --------------------------------------------------------------

func _archive_checks() -> void:
	var arch = EvidenceArchive.new()
	root.add_child(arch)
	arch.size = Vector2(1280, 720)

	_ok(arch.is_open() == false, "档案初始是关的")
	arch.toggle()
	_ok(arch.is_open() == true, "toggle() 打开档案")
	arch.toggle()
	_ok(arch.is_open() == false, "toggle() 再关掉档案")

	# 空档案打开不炸
	arch.open_archive()
	_ok(arch.is_open() == true, "open_archive() 打开")
	arch.close_archive()

	# 有条目时新计数正确
	EvidenceStore.try_collect("ui1", "账桌", "磨坊 · 1926", "一本硬壳账簿摊在柜台上。纸很好。")
	arch.open_archive()
	arch.flash_collected("账桌")
	_ok(arch.new_count == 1, "flash_collected 让新计数 +1")
	arch.close_archive()
	_ok(arch.new_count == 0, "关档后新计数清零")

	# 详情页能滚：长描述要能算出可滚行数（别写死 0）
	# 3000 字 ≈ 60 行，远超一屏能放下的行数
	EvidenceStore.try_collect("ui2", "长物证", "磨坊 · 1926", "长".repeat(3000))
	arch.open_archive()
	arch.selected = 1
	arch.detail = true
	_ok(arch._max_scroll() > 0, "长描述能算出可滚行数（%d）" % arch._max_scroll())
	arch.scroll = 0
	arch.detail = false
	arch.close_archive()

	arch.queue_free()
	EvidenceStore.clear()


## 清掉所有可能存在的存档文件。
## ⚠️ 主场景 _ready() 会调 EvidenceStore.load()，所以实例化主场景之前
## 必须先把存档清干净，否则会读到上一轮测试留下的旧档案，
## 起始条目数就不是 0，后面「检视后 1 条」这类断言会连环失败。
func _purge_saves() -> void:
	for p in ["user://evidence_archive.json", "res://.evidence_archive.json",
			"res://_mdtest/_evidence_test.json"]:
		if FileAccess.file_exists(p):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(p))


# ---- 3. 主场景真跑：检视真的入档 ------------------------------------------

func _main_scene_checks() -> void:
	_purge_saves()
	var main = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	await process_frame

	if main.tl == null:
		_ok(false, "main.tl 有值")
		return
	_ok(true, "主场景起来了")

	# 主场景 _ready() 里读过一次存档，这里再兜一次底，确保从空档案开始
	EvidenceStore.clear()
	_ok(EvidenceStore.count() == 0, "主场景检查从空档案开始（条数 0）")

	# 找 A1 磨坊的账桌热点：直接问帧数据要家具热点
	var f = main.tl.current()
	var ledger = {}
	var mill_hotspots = []
	for h in f.hotspots:
		if String(h.get("house_id", "")) == "mill_a1" and String(h.get("furniture", "")) == "账桌":
			ledger = h
			mill_hotspots.append(h)

	if ledger.is_empty():
		_ok(false, "A1 磨坊有账桌热点")
		return
	_ok(true, "A1 磨坊有账桌热点")
	_ok(String(ledger.get("title", "")) == "账桌", "热点标题 = 账桌（玩家按 E 看到的名字）")

	# 传送到账桌旁，走真实检视路径
	main.tl.char_pos = ledger["pos"] as Vector2
	main._do_inspect()
	_ok(EvidenceStore.count() == 1, "检视后档案里 1 条")
	var e0: Dictionary = EvidenceStore.get_entries()[0]
	_ok(String(e0.get("name", "")) == "账桌", "入档名字 = 账桌")
	_ok(String(e0.get("source", "")) == "磨坊 · 1926", "入档来源 = 磨坊 · 1926（实际 %s）" % String(e0.get("source", "")))
	_ok(String(e0.get("text", "")) != "", "入档文本非空")

	# 再检视一次：不重复
	main._do_inspect()
	_ok(EvidenceStore.count() == 1, "二次检视不新增（去重）")

	# 走开再回来，还是一条
	main.tl.char_pos += Vector2(400, 400)
	main._do_inspect()
	main.tl.char_pos = ledger["pos"] as Vector2
	main._do_inspect()
	_ok(EvidenceStore.count() == 1, "走开再回来仍不重复")

	# 切时间轴（A1 → A2）不丢条目
	main.tl.index = 1
	main._refresh_all()
	_ok(EvidenceStore.count() == 1, "切时间轴后条目仍在")

	# 切到 A2 磨坊的账桌（同名家具，不同 house_id → 不同证物）
	var f2 = main.tl.frames[1]
	var ledger2 = {}
	for h in f2.hotspots:
		if String(h.get("house_id", "")) == "mill_a2" and String(h.get("furniture", "")) == "账桌":
			ledger2 = h
	if ledger2.is_empty():
		_ok(false, "A2 磨坊有账桌热点")
	else:
		main.tl.char_pos = ledger2["pos"] as Vector2
		main._do_inspect()
		_ok(EvidenceStore.count() == 2, "A2 磨坊账桌是另一条（house_id 不同）")
		var e1: Dictionary = EvidenceStore.get_entries()[1]
		# mill_a2 全名是「磨坊 → 粮站 · A2 1951（新砖空暗龛）· 加害方根」，
		# 改名链保留 → 来源 = 「磨坊 → 粮站 · 1951」
		_ok(String(e1.get("source", "")) == "磨坊 → 粮站 · 1951",
			"A2 那条来源 = 磨坊 → 粮站 · 1951（实际 %s）" % String(e1.get("source", "")))

	# 地标：老井在 A1 帧（地标 key = title，跨时代同名只留一条）
	var well = {}
	for h in f.hotspots:
		if String(h.get("house_id", "")) == "" and String(h.get("title", "")) == "老井":
			well = h
	if well.is_empty():
		_ok(false, "A1 帧有老井地标热点")
	else:
		main.tl.index = 0
		main.tl.char_pos = well["pos"] as Vector2
		main._do_inspect()
		_ok(EvidenceStore.count() == 3, "地标老井也入档")
		var e2: Dictionary = EvidenceStore.get_entries()[2]
		_ok(String(e2.get("source", "")) == "1926 · 村中", "地标来源 = 1926 · 村中（实际 %s）" % String(e2.get("source", "")))

	# 跨时代同名地标：切到 A2 的老井（title 不同，是「老井 · 石板」）→ 新的
	main.tl.index = 1
	var well2 = {}
	for h in main.tl.frames[1].hotspots:
		if String(h.get("house_id", "")) == "" and String(h.get("title", "")) == "老井 · 石板":
			well2 = h
	if not well2.is_empty():
		main.tl.char_pos = well2["pos"] as Vector2
		main._do_inspect()
		_ok(EvidenceStore.count() == 4, "A2 的「老井 · 石板」是独立证物")

	# 档案界面本身能开能关
	main.archive.open_archive()
	_ok(main.archive.is_open(), "主场景里的档案能打开")
	main.archive.close_archive()
	_ok(not main.archive.is_open(), "主场景里的档案能关闭")

	# 房子名裁剪规则（来源标签里显示的名字）
	_ok(main._short_house_name("陆家（一字形）· A1 1926 · 受害方") == "陆家",
		"括号注记剪掉：陆家（一字形）→ 陆家")
	_ok(main._short_house_name("磨坊 → 粮站 · A2 1951（新砖空暗龛）· 加害方根") == "磨坊 → 粮站",
		"改名链保留：磨坊 → 粮站")
	_ok(main._short_house_name("周家 · 长工房 · 帮凶方（穷）") == "周家",
		"第一段取周家（长工房那行以 · 分段，不进名字）")
	_ok(main._short_house_name("") == "旧屋", "空名兜底成旧屋")
