extends SceneTree

## 证物存档界面实机截图（非 headless）。
## 跑法：godot --path . --script res://_mdtest/_evidence_shot.gd
##
## 出图三张：
##   evidence_01_inspect.png  按 E 刚检视完（检视文字 + 底部「已收集」提示）
##   evidence_02_list.png     档案列表（多条目 + 选中高亮）
##   evidence_03_detail.png   档案详情页（完整描述 + 来源）

const OUT := "res://lab/evidence_shot"


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))

	# ---- 第一轮：进游戏收几件证物（顺便证明存档落盘）----
	var scene: PackedScene = load("res://scenes/main.tscn")
	var inst := scene.instantiate()
	root.add_child(inst)
	for i in 8:
		await process_frame

	var tl = inst.get("tl")
	var store = load("res://scripts/evidence_store.gd")

	# 从空档案开始，别把上一轮截图留下的存档带进来
	store.clear()

	# ---- 走到 A1 磨坊账桌，按 E 检视 ----
	var ledger := {}
	for h in tl.current().hotspots:
		if String(h.get("house_id", "")) == "mill_a1" and String(h.get("furniture", "")) == "账桌":
			ledger = h
	if ledger.is_empty():
		print("SHOT_FAIL 找不到 A1 磨坊账桌热点")
		quit(1)
		return
	tl.char_pos = ledger["pos"] as Vector2
	inst.call("_refresh_all")
	inst.call("_do_inspect")
	for i in 4:
		await process_frame
	await _shot(OUT + "/evidence_01_inspect.png")

	# ---- 再收几件，让档案里有条目 ----
	for h in tl.current().hotspots:
		if String(h.get("house_id", "")) == "mill_a1" and String(h.get("furniture", "")) == "石磨":
			tl.char_pos = h["pos"] as Vector2
			inst.call("_do_inspect")
			break
	for h in tl.current().hotspots:
		if String(h.get("house_id", "")) == "" and String(h.get("title", "")) == "老井":
			tl.char_pos = h["pos"] as Vector2
			inst.call("_do_inspect")
			break
	for h in tl.current().hotspots:
		if String(h.get("house_id", "")) == "mill_a1" and String(h.get("furniture", "")) == "碾盘":
			tl.char_pos = h["pos"] as Vector2
			inst.call("_do_inspect")
			break
	for i in 3:
		await process_frame

	# ---- 开档案（列表态） ----
	var arch = inst.get("archive")
	arch.open_archive()
	for i in 5:
		await process_frame
	await _shot(OUT + "/evidence_02_list.png")

	# ---- 进详情页 ----
	arch.detail = true
	arch.selected = 0
	for i in 5:
		await process_frame
	await _shot(OUT + "/evidence_03_detail.png")

	print("SHOT_OK entries=%d" % store.count())
	quit(0)


func _shot(path: String) -> void:
	var img := root.get_viewport().get_texture().get_image()
	img.save_png(path)
	print("saved ", path, " ", img.get_size())
