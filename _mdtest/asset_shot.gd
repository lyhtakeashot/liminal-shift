extends SceneTree

## 贴图消费点截图器（不带 --headless 跑才有像素）。
## 存到 _mdtest/assets/ 下，验证「贴图真的画出来了」。

const OUT := "res://_mdtest/assets"
const Timeline = preload("res://scripts/timeline.gd")


func _init() -> void:
	_run.call_deferred()


func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))

	var main = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	await process_frame

	var tl = main.tl
	if tl == null:
		print("FAIL: main.tl is null")
		quit(1)
		return

	var cam: Node2D = main.get_node("CameraRig")

	# 定点截图：每处挑一个能看清的消费点
	var shots := [
		# A1：沈家（长条房，墙多，家具多）
		{"idx": 0, "pos": Vector2(300, 800), "name": "a1_shen_house"},
		# A1：鲁家院子
		{"idx": 0, "pos": Vector2(2560, 950), "name": "a1_lu_house"},
		# A1：磨坊 + 主路 + 树
		{"idx": 0, "pos": Vector2(1400, 600), "name": "a1_mill_road"},
		# A1：老井 + 老槐
		{"idx": 0, "pos": Vector2(1330, 900), "name": "a1_well_tree"},
		# A3：沈家凹形三翼 + 家具
		{"idx": 2, "pos": Vector2(400, 500), "name": "a3_shen_house"},
		# A3：田 + 主路
		{"idx": 2, "pos": Vector2(2100, 500), "name": "a3_field_road"},
		# A2：周家
		{"idx": 1, "pos": Vector2(1900, 1350), "name": "a2_zhou_house"},
		# A1：磨坊，**玩家站在屋外** → 屋顶要画出来
		{"idx": 0, "pos": Vector2(1500, 900), "name": "a1_mill_outside",
			"cam": Vector2(1500, 700)},
		# A3：陆家废墟（ruin:true，base 图只有残墙基，没有墙顶面/立面）
		{"idx": 2, "pos": Vector2(2600, 900), "name": "a3_lu_ruin",
			"cam": Vector2(2600, 900)},
		# A3：磨坊
		{"idx": 2, "pos": Vector2(1400, 700), "name": "a3_mill",
			"cam": Vector2(1400, 700)},
	]

	for sh in shots:
		tl.index = int(sh["idx"])
		tl.char_pos = sh["pos"]
		tl.axis = 0
		main.call("_refresh_all")
		main.player.position = sh["pos"]
		# 镜头要停在哪：优先用 cam 字段，否则用玩家位置
		var cam_at: Vector2 = sh.get("cam", sh["pos"])
		cam.call("set_target", cam_at)
		# 等镜头 lerp 到位（钉死 offset，避免拍到半路）
		for i in 40:
			await process_frame
		cam.set("offset", cam.call("_clamp", cam_at - Vector2(640, 360)))
		cam.call("_apply")
		await process_frame
		await RenderingServer.frame_post_draw
		await process_frame
		await RenderingServer.frame_post_draw
		var img: Image = root.get_texture().get_image()
		var path := "%s/%s.png" % [OUT, String(sh["name"])]
		img.save_png(ProjectSettings.globalize_path(path))
		print("SHOT ", path)

	# 时间轴模式（去饱和 + 色差）
	tl.index = 0
	tl.char_pos = Vector2(300, 800)
	tl.axis = 1
	main.call("_refresh_all")
	main.player.position = tl.char_pos
	cam.call("set_target", tl.char_pos)
	for i in 40:
		await process_frame
	cam.set("offset", cam.call("_clamp", tl.char_pos - Vector2(640, 360)))
	cam.call("_apply")
	await process_frame
	await RenderingServer.frame_post_draw
	await process_frame
	await RenderingServer.frame_post_draw
	var img2: Image = root.get_texture().get_image()
	img2.save_png(ProjectSettings.globalize_path("%s/time_mode.png" % OUT))
	print("SHOT time_mode")

	quit(0)
