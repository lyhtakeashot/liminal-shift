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

	# 附带一张：卡墙虚化中（L17；推时间落进固体重叠 → 时代前进 + 主角半透明）
	var cand: Variant = _phase_candidate(tl)
	if cand == null:
		print("SHOT phasing SKIP（没找到 free→solid 的落点）")
		quit(0)
		return
	var at: Vector2 = cand
	tl.index = 0
	tl.axis = 1
	tl.char_pos = at
	tl.exit_phasing()
	main.player.facing = Vector2.UP
	tl.step_time(1)
	print("PHASING_SHOT at=%s index=%d phasing=%s" % [str(at), tl.index, str(tl.phasing)])
	main._refresh_all()
	await process_frame
	await RenderingServer.frame_post_draw
	await process_frame
	await RenderingServer.frame_post_draw
	var img2: Image = root.get_texture().get_image()
	img2.save_png(ProjectSettings.globalize_path("%s/phasing.png" % OUT))
	print("SHOT phasing")

	quit(0)


## 找一个「A1 可站、A2 是实体」的点：虚化截图和 phasing_check 都用这一种落点。
## 按 32px 格心顺序扫，第一个命中即返回（确定性，不随加载顺序变）。
func _phase_candidate(tl) -> Variant:
	var ws: Vector2 = tl.world_size
	for gy in int(ws.y / 32.0):
		for gx in int(ws.x / 32.0):
			var c := Vector2(gx * 32.0 + 16.0, gy * 32.0 + 16.0)
			if tl.frames[0].is_free(c) and not tl.frames[1].is_free(c):
				return c
	return null