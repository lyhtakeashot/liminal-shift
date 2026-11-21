extends SceneTree

## 实机截图：A1/A2/A3 各取几个关键视角，给用户看当前效果。

func _init() -> void:
	var scene: PackedScene = load("res://scenes/main.tscn")
	var inst := scene.instantiate()
	root.add_child(inst)
	for i in 6:
		await process_frame

	var tl = inst.get("tl")
	var cam: Node2D = inst.get_node("CameraRig")

	# 视角清单：{帧, 镜头中心, 文件名}
	var shots := [
		# A1：村中主路（磨坊 + 井 + 树 + 沈家）
		{"idx": 0, "pos": Vector2(600, 500), "name": "a1_01_center"},
		# A1：西侧沈家 + 田
		{"idx": 0, "pos": Vector2(300, 450), "name": "a1_02_shen"},
		# A1：东侧陆家
		{"idx": 0, "pos": Vector2(1200, 480), "name": "a1_03_lu"},
		# A2：村中
		{"idx": 1, "pos": Vector2(600, 500), "name": "a2_01_center"},
		# A2：西侧沈家（L 形）
		{"idx": 1, "pos": Vector2(350, 450), "name": "a2_02_shen"},
		# A3：村中（粮站）
		{"idx": 2, "pos": Vector2(600, 500), "name": "a3_01_center"},
		# A3：西侧沈家（凹形最大）
		{"idx": 2, "pos": Vector2(350, 450), "name": "a3_02_shen"},
	]
	for sh in shots:
		tl.index = int(sh["idx"])
		tl.char_pos = sh["pos"]
		inst.call("_refresh_all")
		cam.call("set_target", sh["pos"])
		for i in 30:
			await process_frame
		var img := root.get_viewport().get_texture().get_image()
		img.save_png("res://_mdtest/greybox/%s.png" % sh["name"])
		print("saved ", sh["name"], " ", img.get_size())
	quit(0)