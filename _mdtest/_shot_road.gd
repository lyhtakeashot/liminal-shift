extends SceneTree

## 截三帧的路，检验格子化效果。

func _init() -> void:
	var scene: PackedScene = load("res://scenes/main.tscn")
	var inst := scene.instantiate()
	root.add_child(inst)
	for i in 6:
		await process_frame

	var tl = inst.get("tl")
	var cam: Node2D = inst.get_node("CameraRig")

	var shots := [
		{"idx": 0, "pos": Vector2(600, 620), "name": "road_a1"},
		{"idx": 1, "pos": Vector2(600, 620), "name": "road_a2"},
		{"idx": 2, "pos": Vector2(600, 620), "name": "road_a3"},
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
	quit(0)