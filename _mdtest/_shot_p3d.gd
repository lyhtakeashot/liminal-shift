extends SceneTree

## 伪 3D 第 1 步验收截图：A1 跑起来截几张（带窗口跑，不能 --headless）。

func _init() -> void:
	var scene: PackedScene = load("res://scenes/main.tscn")
	var inst := scene.instantiate()
	root.add_child(inst)
	for i in 6:
		await process_frame

	var tl = inst.get("tl")
	var cam: Node2D = inst.get_node("CameraRig")

	var shots := [
		# 磨坊（墙多、屋顶明显）
		{"idx": 0, "pos": Vector2(750, 380), "name": "p3d_a1_mill"},
		# 沈家（一字形，连续墙检验「只有最南格露立面」）
		{"idx": 0, "pos": Vector2(220, 480), "name": "p3d_a1_shen"},
		# 周家（小房，屋顶屋脊清楚）
		{"idx": 0, "pos": Vector2(990, 690), "name": "p3d_a1_zhou"},
		# 沈家 A3（凹形三翼，检验南北翼接缝谁压谁）
		{"idx": 2, "pos": Vector2(280, 400), "name": "p3d_a3_shen"},
		# 树 + 井（检验树有树干、井没有）
		{"idx": 0, "pos": Vector2(660, 460), "name": "p3d_a1_tree_well"},
	]
	for sh in shots:
		tl.index = int(sh["idx"])
		tl.char_pos = sh["pos"]
		inst.call("_refresh_all")
		if tl.axis != 0:
			tl.toggle_axis()
			inst.call("_refresh_all")
		cam.call("set_target", sh["pos"])
		for i in 30:
			await process_frame
		var img := root.get_viewport().get_texture().get_image()
		img.save_png("res://_mdtest/greybox/%s.png" % sh["name"])
		print("saved ", sh["name"], " ", img.get_size())

	# 时间轴模式（检验三倍重绘 + 伪3D共存）
	tl.index = 0
	tl.char_pos = Vector2(750, 380)
	inst.call("_refresh_all")
	tl.toggle_axis()
	inst.call("_refresh_all")
	cam.call("set_target", Vector2(750, 380))
	for i in 30:
		await process_frame
	var img2 := root.get_viewport().get_texture().get_image()
	img2.save_png("res://_mdtest/greybox/p3d_time_mode.png")
	print("saved p3d_time_mode ", img2.get_size())
	quit(0)