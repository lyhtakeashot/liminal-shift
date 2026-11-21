extends SceneTree

## 截图器：把五个时间点的空间轴 / 时间轴画面都存成 PNG。

const OUT := "res://_mdtest/greybox"
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

	for mode in [0, 1]:
		for i in tl.frames.size():
			tl.index = i
			tl.axis = mode
			main._refresh_all()
			await process_frame
			await RenderingServer.frame_post_draw
			await process_frame
			await RenderingServer.frame_post_draw
			var img: Image = root.get_texture().get_image()
			var tag := "space" if mode == 0 else "time"
			var path := "%s/a%d_%s.png" % [OUT, i + 1, tag]
			img.save_png(ProjectSettings.globalize_path(path))
			print("SHOT ", path)

	# 附带一张：撞墙瞬间（顶住了）
	tl.index = 0
	tl.axis = 0
	main._refresh_all()
	main._on_bump(0)
	await process_frame
	await RenderingServer.frame_post_draw
	await process_frame
	await RenderingServer.frame_post_draw
	var img2: Image = root.get_texture().get_image()
	img2.save_png(ProjectSettings.globalize_path("%s/bump.png" % OUT))
	print("SHOT bump")

	quit(0)