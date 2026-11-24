extends SceneTree

## 证物档案自检（L5 线：证物模型 v2 —— 一件物件一张卡 · 卡内按年追加观察记录）。
## 跑法：godot --headless --path . --script res://_mdtest/evidence_archive_check.gd
##
## 验三块：
##   1. 数据层：归一键三规则 / 三态收集 / 观察按年追加 / 存档往返 / 旧格式不崩
##   2. 界面：列表一行一卡、标题栏两个数字、详情页年代升序、长文案可滚
##   3. 主场景：真检视入档、跨年代归一到同一张卡、档案开着时 SHIFT/E 不响应
##
## ⚠️ 断言口径（任务书 §2.2）：
##   卡 = 一件物件；观察 = 该物件在某个年代的一次记录。
##   同年代重复检视 → 卡数与观察数都不变；新年份 → 卡数不变、观察 +1。

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


# ---- 小工具 ---------------------------------------------------------------

## 某张卡的观察年份列表（收集顺序）。
func _years_of(key: String) -> Array:
	var out: Array = []
	for o in EvidenceStore.get_observations(key):
		out.append(int((o as Dictionary).get("year", 0)))
	return out


## 某张卡第 n 条观察的某个字段（取不到返回 ""）。
func _obs_field(key: String, idx: int, field: String) -> String:
	var obs: Array = EvidenceStore.get_observations(key)
	if idx < 0 or idx >= obs.size():
		return ""
	return String((obs[idx] as Dictionary).get(field, ""))


## 按 key 取卡（取不到返回空字典）。
func _card_of(key: String) -> Dictionary:
	for e in EvidenceStore.get_entries():
		var d: Dictionary = e
		if String(d.get("key", "")) == key:
			return d
	return {}


# ---- 1. 数据层 ------------------------------------------------------------

func _store_checks() -> void:
	EvidenceStore.clear()
	_ok(EvidenceStore.count() == 0, "空档案卡数 0")
	_ok(EvidenceStore.observation_count() == 0, "空档案观察数 0")
	_ok(not EvidenceStore.is_collected("k1"), "空档案里没有 k1")

	# --- 归一键：规则 A 家具 = <族>::<家具名> ---
	_ok(EvidenceStore.furniture_key("mill_a1", "账桌") == "mill::账桌",
		"规则A：mill_a1 账桌 → mill::账桌")
	_ok(EvidenceStore.furniture_key("mill_a2", "账桌") == "mill::账桌",
		"规则A：mill_a2 账桌 → mill::账桌（同栋房子换 id 仍是同一件）")
	_ok(EvidenceStore.furniture_key("mill_a3", "账桌") == "mill::账桌",
		"规则A：mill_a3 账桌 → mill::账桌")
	_ok(EvidenceStore.furniture_key("zhou_house", "账桌") == "zhou::账桌",
		"规则A：周家账桌 ≠ 磨坊账桌（族不同 → 不同卡）")
	_ok(EvidenceStore.furniture_key("zheng_a4", "账桌") == "zheng::账桌",
		"规则A：zheng_a4 自成一族（与陆家同址但不同户）")
	_ok(EvidenceStore.furniture_key("mill_a1", "老井") == "mill::老井",
		"规则A：磨坊院里的井 → mill::老井")

	# --- 归一键：规则 B 地标 = 「·」之前的主体名 ---
	_ok(EvidenceStore.landmark_key("老井") == "老井", "规则B：老井 → 老井")
	_ok(EvidenceStore.landmark_key("老井 · 石板") == "老井", "规则B：老井 · 石板 → 老井")
	_ok(EvidenceStore.landmark_key("老井 · 三层水泥") == "老井", "规则B：老井 · 三层水泥 → 老井")
	_ok(EvidenceStore.landmark_key("老井 · 沥青补丁") == "老井", "规则B：老井 · 沥青补丁 → 老井")
	_ok(EvidenceStore.landmark_key("超市工地 · 南大门") == "超市工地",
		"规则B：超市工地 · 南大门 → 超市工地")
	_ok(EvidenceStore.landmark_key("路口 · 红绿灯基座") == "路口",
		"规则B：路口 · 红绿灯基座 → 路口")
	_ok(EvidenceStore.landmark_key("老槐") == "老槐", "规则B：老槐 → 老槐")

	# --- 归一键：规则 C 家具与地标是两个命名空间 ---
	_ok(EvidenceStore.furniture_key("mill_a1", "老井") != EvidenceStore.landmark_key("老井"),
		"规则C：mill::老井 ≠ 老井（两个命名空间）")

	# --- 三态收集 ---
	var r1 := EvidenceStore.try_collect("k1", "账桌", "磨坊 · 1926",
		"一本硬壳账簿摊在柜台上。", 1926)
	_ok(r1 == EvidenceStore.RESULT_NEW_CARD, "首次收集返回「新建卡」（%d）" % r1)
	_ok(EvidenceStore.count() == 1, "收集后卡数 1")
	_ok(EvidenceStore.observation_count() == 1, "收集后观察数 1")
	_ok(EvidenceStore.is_collected("k1"), "k1 已入档")

	var r2 := EvidenceStore.try_collect("k1", "账桌", "磨坊 · 1926",
		"一本硬壳账簿摊在柜台上。", 1926)
	_ok(r2 == EvidenceStore.RESULT_DUPLICATE, "同年代再收集返回「重复」（%d）" % r2)
	_ok(EvidenceStore.count() == 1, "重复收集后卡数仍是 1")
	_ok(EvidenceStore.observation_count() == 1, "重复收集后观察数仍是 1")

	var r3 := EvidenceStore.try_collect("k1", "账桌", "磨坊 → 粮站 · 1951",
		"柜台上换了一本新账簿。", 1951)
	_ok(r3 == EvidenceStore.RESULT_NEW_OBSERVATION, "新年份收集返回「追加观察」（%d）" % r3)
	_ok(EvidenceStore.count() == 1, "追加观察后卡数仍是 1")
	_ok(EvidenceStore.observation_count() == 2, "追加观察后观察数 2")
	_ok(_years_of("k1") == [1926, 1951],
		"k1 的观察年份 = 1926/1951（%s）" % str(_years_of("k1")))
	_ok(_obs_field("k1", 1, "source") == "磨坊 → 粮站 · 1951",
		"追加的观察保留自己的来源标签（%s）" % _obs_field("k1", 1, "source"))

	_ok(EvidenceStore.try_collect("", "空", "空", "空", 1926) == EvidenceStore.RESULT_DUPLICATE,
		"空 key 收集返回「重复」（不建卡）")

	# --- 顺序 = 收集顺序 ---
	EvidenceStore.try_collect("k2", "石磨", "磨坊 · 1926", "石磨靠着大厅西墙。", 1926)
	EvidenceStore.try_collect("k3", "老井", "1926 · 村中", "村口那口老井。", 1926)
	var es := EvidenceStore.get_entries()
	_ok(es.size() == 3, "三张卡")
	var names: Array = []
	for e in es:
		names.append(String((e as Dictionary).get("name", "")))
	_ok(names == ["账桌", "石磨", "老井"], "get_entries() 顺序 = 收集顺序（%s）" % str(names))

	# --- 字段完整性 ---
	var complete := true
	for e in es:
		var d: Dictionary = e
		for k in ["key", "name", "order", "observations"]:
			if not d.has(k):
				complete = false
		var obs: Array = d.get("observations", [])
		if obs.is_empty():
			complete = false
		for o in obs:
			for k in ["year", "title", "source", "text", "order"]:
				if not (o as Dictionary).has(k):
					complete = false
	_ok(complete, "每张卡有 key/name/order/observations，每条观察有 year/title/source/text/order")

	# --- save/load 往返 ---
	# ⚠️ 沙箱里 user://（APPDATA）不可写，所以这里显式用 res:// 路径测往返。
	# 真机上 save() 默认走 user:// → res:// 的回退链。
	var path := "res://_mdtest/_evidence_test.json"
	_ok(EvidenceStore.save(path), "save() 写成功")
	EvidenceStore.clear()
	_ok(EvidenceStore.count() == 0, "clear() 后卡数 0")
	_ok(EvidenceStore.load(path), "load() 读成功")
	var es2 := EvidenceStore.get_entries()
	_ok(es2.size() == 3, "load 后卡数 3")
	_ok(EvidenceStore.observation_count() == 4, "load 后观察数 4（k1 两条 + k2 一条 + k3 一条）")
	var names2: Array = []
	for e in es2:
		names2.append(String((e as Dictionary).get("name", "")))
	_ok(names2 == ["账桌", "石磨", "老井"], "load 后顺序一致（%s）" % str(names2))
	_ok(_obs_field("k1", 0, "source") == "磨坊 · 1926",
		"load 后来源标签保留（%s）" % _obs_field("k1", 0, "source"))
	_ok(_years_of("k1") == [1926, 1951],
		"load 后观察年份保留（%s）" % str(_years_of("k1")))
	_ok(EvidenceStore.is_collected("k2"), "load 后去重索引也恢复了")

	# --- 旧格式（v1）兼容：一条 = 一张卡 + 一条观察 ---
	var old_path := "res://_mdtest/_evidence_old.json"
	var old_json := JSON.stringify({
		"version": 1,
		"entries": [
			{"key": "mill_a1::账桌", "name": "账桌", "source": "磨坊 · 1926",
				"text": "旧格式的一条家具。", "order": 0},
			{"key": "老井 · 石板", "name": "老井 · 石板", "source": "1951 · 村中",
				"text": "旧格式的一条地标。", "order": 1},
		],
	}, "\t")
	var of := FileAccess.open(old_path, FileAccess.WRITE)
	if of == null:
		_ok(false, "旧格式样本写成功")
	else:
		of.store_string(old_json)
		of.close()
		_ok(EvidenceStore.load(old_path), "load() 读旧格式不崩")
		_ok(EvidenceStore.count() == 2, "旧格式 2 条 → 2 张卡（实际 %d）" % EvidenceStore.count())
		_ok(EvidenceStore.observation_count() == 2,
			"旧格式 2 条 → 2 条观察（实际 %d）" % EvidenceStore.observation_count())
		_ok(EvidenceStore.is_collected("mill::账桌"),
			"旧格式家具键按族归一（mill_a1::账桌 → mill::账桌）")
		_ok(EvidenceStore.is_collected("老井"),
			"旧格式地标键按「·」之前归一（老井 · 石板 → 老井）")
		_ok(_years_of("mill::账桌") == [1926],
			"旧格式年份从 source 解析（%s）" % str(_years_of("mill::账桌")))
		_ok(_obs_field("mill::账桌", 0, "text") == "旧格式的一条家具。",
			"旧格式文案保留")

	# --- 读一个不存在的文件 → 不崩，返回 false ---
	_ok(EvidenceStore.load("res://_mdtest/_evidence_not_exist.json") == false,
		"读不存在的文件返回 false 不崩")

	# --- 回退链：save() 不给路径时至少要落到某个能写的地方 ---
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

	# 新计数：新增卡数 + 新增观察数都算「新」
	EvidenceStore.try_collect("ui1", "账桌", "磨坊 · 1926",
		"一本硬壳账簿摊在柜台上。纸很好。", 1926)
	arch.open_archive()
	arch.flash_collected("账桌")
	_ok(arch.new_count == 1, "flash_collected 让新计数 +1")
	arch.close_archive()
	_ok(arch.new_count == 0, "关档后新计数清零")
	_ok(not EvidenceStore.is_new_key("ui1"), "关档后「新」标记清掉")

	# 追加一条新年代的观察同样算「新」（口径：新增卡数 + 新增观察数）
	EvidenceStore.try_collect("ui1", "账桌", "磨坊 → 粮站 · 1951",
		"换了一本新账簿。", 1951)
	arch.open_archive()
	arch.flash_collected("账桌", false)
	_ok(arch.new_count == 1, "追加观察也算「新」（%d）" % arch.new_count)
	_ok(EvidenceStore.is_new_key("ui1"), "追加过观察的卡带「新」标记")

	# 标题栏：卡数与观察条数两个数字都在
	_ok(arch.title_summary() == "已收集 1 件 · 2 条观察",
		"标题栏 = 已收集 1 件 · 2 条观察（实际 %s）" % arch.title_summary())
	arch.close_archive()

	# 详情页按年代升序（故意用 2026 → 1951 → 1976 的顺序收集）
	EvidenceStore.try_collect("ui3", "老槐", "2026 · 村中", "一百岁。", 2026)
	EvidenceStore.try_collect("ui3", "老槐", "1951 · 村中", "二十五岁。", 1951)
	EvidenceStore.try_collect("ui3", "老槐", "1976 · 村中", "四十九岁。", 1976)
	arch.open_archive()
	arch.selected = 1
	arch.detail = true
	var card3 := _card_of("ui3")
	_ok(card3.size() > 0, "老槐那张卡在")
	var ys: Array = []
	for o in arch.sorted_observations(card3):
		ys.append(int((o as Dictionary).get("year", 0)))
	_ok(ys == [1951, 1976, 2026],
		"详情页观察按年代升序（%s）" % str(ys))
	var line_years: Array = []
	for ln in arch.detail_lines(card3, 400.0):
		var ld: Dictionary = ln
		if String(ld.get("style", "")) == "year":
			line_years.append(String(ld.get("text", "")))
	_ok(line_years == ["1951", "1976", "2026"],
		"详情页行表里年份也是升序（%s）" % str(line_years))
	arch.scroll = 0
	arch.detail = false
	arch.close_archive()

	# 详情页能滚：长描述要能算出可滚行数（别写死 0）
	# 3000 字 ≈ 60 行，远超一屏能放下的行数
	EvidenceStore.try_collect("ui2", "长物证", "磨坊 · 1926", "长".repeat(3000), 1926)
	arch.open_archive()
	arch.selected = 2
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
## 起始卡数就不是 0，后面「检视后 1 张卡」这类断言会连环失败。
func _purge_saves() -> void:
	for p in ["user://evidence_archive.json", "res://.evidence_archive.json",
			"res://_mdtest/_evidence_test.json", "res://_mdtest/_evidence_old.json"]:
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

	# ⚠️ 守卫：main._ready() 里任何一步抛错都会**中断初始化**（后面的 _make_archive()
	#    不执行 → main.archive 为 Nil），但脚本照样往下跑、照样打 EVIDENCE_OK。
	#    曾踩过：别的脚本（world_view.gd）parse 失败 → main.archive 为 Nil →
	#    后面所有断言被静默跳过 → 「假通过」。这里必须显式拦住。
	if main.archive == null:
		_ok(false, "主场景档案界面已创建（main.archive 非空）——为空说明 main._ready() 被别的脚本错误打断")
		return
	_ok(true, "主场景档案界面已创建（main.archive 非空）")

	# 主场景 _ready() 里读过一次存档，这里再兜一次底，确保从空档案开始
	EvidenceStore.clear()
	_ok(EvidenceStore.count() == 0, "主场景检查从空档案开始（卡数 0）")

	# 找 A1 磨坊的账桌热点：直接问帧数据要家具热点
	var f = main.tl.current()
	var ledger := {}
	for h in f.hotspots:
		if String(h.get("house_id", "")) == "mill_a1" and String(h.get("furniture", "")) == "账桌":
			ledger = h

	if ledger.is_empty():
		_ok(false, "A1 磨坊有账桌热点")
		return
	_ok(true, "A1 磨坊有账桌热点")
	_ok(String(ledger.get("title", "")) == "账桌", "热点标题 = 账桌（玩家按 E 看到的名字）")

	# 传送到账桌旁，走真实检视路径
	main.tl.char_pos = ledger["pos"] as Vector2
	main._do_inspect()
	_ok(EvidenceStore.count() == 1, "检视后档案里 1 张卡")
	_ok(EvidenceStore.observation_count() == 1, "检视后 1 条观察")
	_ok(EvidenceStore.is_collected("mill::账桌"), "入档归一键 = mill::账桌")
	_ok(String(_card_of("mill::账桌").get("name", "")) == "账桌", "入档名字 = 账桌")
	_ok(_obs_field("mill::账桌", 0, "source") == "磨坊 · 1926",
		"入档来源 = 磨坊 · 1926（实际 %s）" % _obs_field("mill::账桌", 0, "source"))
	_ok(_obs_field("mill::账桌", 0, "text") != "", "入档文本非空")

	# 再检视一次：同年代 → 卡和观察都不加
	main._do_inspect()
	_ok(EvidenceStore.count() == 1, "二次检视不新增卡（去重）")
	_ok(EvidenceStore.observation_count() == 1, "二次检视不新增观察（同年代去重）")

	# 走开再回来，还是一张卡一条观察
	main.tl.char_pos += Vector2(400, 400)
	main._do_inspect()
	main.tl.char_pos = ledger["pos"] as Vector2
	main._do_inspect()
	_ok(EvidenceStore.count() == 1, "走开再回来仍不重复")
	_ok(EvidenceStore.observation_count() == 1, "走开再回来观察数不变")

	# 切时间轴（A1 → A2）不丢卡
	main.tl.index = 1
	main._refresh_all()
	_ok(EvidenceStore.count() == 1, "切时间轴后卡片仍在")
	_ok(EvidenceStore.observation_count() == 1, "切时间轴后观察数不变")

	# A2 磨坊的账桌：同一栋房子换了 id → 归一到同一张卡
	var f2 = main.tl.frames[1]
	var ledger2 := {}
	for h in f2.hotspots:
		if String(h.get("house_id", "")) == "mill_a2" and String(h.get("furniture", "")) == "账桌":
			ledger2 = h
	if ledger2.is_empty():
		_ok(false, "A2 磨坊有账桌热点")
	else:
		main.tl.char_pos = ledger2["pos"] as Vector2
		main._do_inspect()
		_ok(EvidenceStore.count() == 1,
			"A2 磨坊账桌归一到同一张卡（卡数不变，实际 %d）" % EvidenceStore.count())
		_ok(EvidenceStore.observation_count() == 2,
			"A2 磨坊账桌多一条 1951 观察（观察数 %d）" % EvidenceStore.observation_count())
		_ok(_years_of("mill::账桌") == [1926, 1951],
			"mill::账桌 观察年份 = 1926/1951（%s）" % str(_years_of("mill::账桌")))
		# mill_a2 全名是「磨坊 → 粮站 · A2 1951（新砖空暗龛）· 加害方根」，
		# 改名链保留 → 来源 = 「磨坊 → 粮站 · 1951」
		_ok(_obs_field("mill::账桌", 1, "source") == "磨坊 → 粮站 · 1951",
			"A2 那条来源 = 磨坊 → 粮站 · 1951（实际 %s）" % _obs_field("mill::账桌", 1, "source"))

	# 地标：老井在 A1 帧（地标 key = 「·」之前的主体名）
	main.tl.index = 0
	main._refresh_all()
	var well := {}
	for h in f.hotspots:
		if String(h.get("house_id", "")) == "" and String(h.get("title", "")) == "老井":
			well = h
	if well.is_empty():
		_ok(false, "A1 帧有老井地标热点")
	else:
		main.tl.char_pos = well["pos"] as Vector2
		main._do_inspect()
		_ok(EvidenceStore.count() == 2,
			"地标老井入档（卡数 %d）" % EvidenceStore.count())
		_ok(EvidenceStore.is_collected("老井"), "地标归一键 = 老井")
		_ok(EvidenceStore.is_collected("mill::账桌"), "磨坊账桌那张卡还在")
		_ok(_obs_field("老井", 0, "source") == "1926 · 村中",
			"地标来源 = 1926 · 村中（实际 %s）" % _obs_field("老井", 0, "source"))

	# 跨时代同名地标：A2 的「老井 · 石板」→ 老井卡的第 2 条观察
	main.tl.index = 1
	main._refresh_all()
	var well2 := {}
	for h in main.tl.frames[1].hotspots:
		if String(h.get("house_id", "")) == "" and String(h.get("title", "")) == "老井 · 石板":
			well2 = h
	if well2.is_empty():
		_ok(false, "A2 帧有「老井 · 石板」地标热点")
	else:
		main.tl.char_pos = well2["pos"] as Vector2
		main._do_inspect()
		_ok(EvidenceStore.count() == 2,
			"A2「老井 · 石板」归一到同一张卡（卡数不变，实际 %d）" % EvidenceStore.count())
		_ok(EvidenceStore.observation_count() == 4,
			"A2「老井 · 石板」多一条观察（观察数 %d）" % EvidenceStore.observation_count())
		_ok(_years_of("老井") == [1926, 1951],
			"老井卡 观察年份 = 1926/1951（%s）" % str(_years_of("老井")))
		_ok(_obs_field("老井", 1, "title") == "老井 · 石板",
			"第 2 条观察保留自己的 title（实际 %s）" % _obs_field("老井", 1, "title"))

	# 家具与地标不混：磨坊院里的井是 mill::老井，与村中老井两张卡
	var mill_well := {}
	for h in main.tl.frames[0].hotspots:
		if String(h.get("house_id", "")) == "mill_a1" and String(h.get("furniture", "")) == "老井":
			mill_well = h
	if mill_well.is_empty():
		_ok(false, "A1 磨坊院里的井有热点")
	else:
		main.tl.index = 0
		main._refresh_all()
		main.tl.char_pos = mill_well["pos"] as Vector2
		main._do_inspect()
		_ok(EvidenceStore.is_collected("mill::老井"), "磨坊院里的井入档为 mill::老井")
		_ok(EvidenceStore.is_collected("老井"), "村中老井那张卡还在（两张卡不混）")
		_ok(EvidenceStore.count() == 3,
			"家具与地标不混 → 三张卡（实际 %d）" % EvidenceStore.count())

	# 档案界面本身能开能关
	main.archive.open_archive()
	_ok(main.archive.is_open(), "主场景里的档案能打开")
	main.archive.close_archive()
	_ok(not main.archive.is_open(), "主场景里的档案能关闭")

	# 存档落盘/读回：卡数、观察条数、顺序都不变
	var cards_before := EvidenceStore.count()
	var obs_before := EvidenceStore.observation_count()
	var order_before: Array = []
	for e in EvidenceStore.get_entries():
		order_before.append(String((e as Dictionary).get("key", "")))
	var path2 := "res://_mdtest/_evidence_test.json"
	_ok(EvidenceStore.save(path2), "主场景存档写成功")
	EvidenceStore.clear()
	_ok(EvidenceStore.count() == 0, "清空后卡数 0")
	_ok(EvidenceStore.load(path2), "主场景存档读回成功")
	_ok(EvidenceStore.count() == cards_before,
		"读回后卡数不变（%d）" % EvidenceStore.count())
	_ok(EvidenceStore.observation_count() == obs_before,
		"读回后观察数不变（%d）" % EvidenceStore.observation_count())
	var order_after: Array = []
	for e in EvidenceStore.get_entries():
		order_after.append(String((e as Dictionary).get("key", "")))
	_ok(order_after == order_before,
		"读回后卡片顺序不变（%s）" % str(order_after))

	await _archive_pauses_world(main)


## 开档时世界是停的：SHIFT 不切时代、E 不检视。
## ⚠️ headless 里 `Input.is_action_just_pressed()` 只在**按下那一帧的槽位**里为真
##    （实测：press 后同槽查 = true；press 后 await 一帧再查 = false，
##      因为引擎在帧末清掉了「刚按下」的边沿）。
##    所以注入姿势必须是：press → （不 await）→ 立刻调 main._process() → release。
##    每段前面都放一个「反向对照」：档案关着时这两个键必须是有效的，
##    否则「开档时没反应」可能只是注入没生效，测了等于没测。
func _archive_pauses_world(main) -> void:
	main.set_process(false)

	# 对照 1：档案关着时 SHIFT 能切时代
	main.archive.close_archive()
	var axis0: int = main.tl.axis
	Input.action_press("shift_axis")
	var jp := Input.is_action_just_pressed("shift_axis")
	main._process(0.016)
	Input.action_release("shift_axis")
	_ok(jp and main.tl.axis != axis0,
		"对照：档案关着时 SHIFT 能切时代（just=%s, %d → %d）" % [str(jp), axis0, main.tl.axis])

	# 开档时：SHIFT 不切时代
	main.archive.open_archive()
	var axis1: int = main.tl.axis
	Input.action_press("shift_axis")
	var jp2 := Input.is_action_just_pressed("shift_axis")
	main._process(0.016)
	Input.action_release("shift_axis")
	_ok(jp2 and main.tl.axis == axis1,
		"开档时 SHIFT 不切时代（just=%s, %d → %d）" % [str(jp2), axis1, main.tl.axis])

	# 对照 2：档案关着时 E 能检视入档
	main.archive.close_archive()
	main.tl.index = 0
	main._refresh_all()
	var stele := {}
	for h in main.tl.frames[0].hotspots:
		if String(h.get("house_id", "")) == "" and String(h.get("title", "")) == "界碑":
			stele = h
	if stele.is_empty():
		_ok(false, "A1 帧有界碑地标热点")
	else:
		var obs_c: int = EvidenceStore.observation_count()
		main.tl.char_pos = stele["pos"] as Vector2
		Input.action_press("inspect")
		var jp3 := Input.is_action_just_pressed("inspect")
		main._process(0.016)
		Input.action_release("inspect")
		_ok(jp3 and EvidenceStore.observation_count() == obs_c + 1,
			"对照：档案关着时 E 能检视入档（just=%s, 观察数 %d → %d）"
			% [str(jp3), obs_c, EvidenceStore.observation_count()])

	# 开档时：E 不检视
	main.archive.open_archive()
	var dam := {}
	for h in main.tl.frames[0].hotspots:
		if String(h.get("house_id", "")) == "" and String(h.get("title", "")) == "坝":
			dam = h
	if dam.is_empty():
		_ok(false, "A1 帧有坝地标热点")
	else:
		var obs_d: int = EvidenceStore.observation_count()
		main.tl.char_pos = dam["pos"] as Vector2
		Input.action_press("inspect")
		var jp4 := Input.is_action_just_pressed("inspect")
		main._process(0.016)
		Input.action_release("inspect")
		_ok(jp4 and EvidenceStore.observation_count() == obs_d,
			"开档时 E 不检视（just=%s, 观察数 %d → %d）"
			% [str(jp4), obs_d, EvidenceStore.observation_count()])
		_ok(not EvidenceStore.is_collected("坝"), "开档时 E 没把坝收进档案")

	main.archive.close_archive()
	main.set_process(true)
