extends SceneTree

## 确认 project.godot 里的 integer 缩放真的被 Godot 读进去了。
## （无头模式拿不到真实显示器，但 content_scale_* 配置值是可读的）

func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	var r := root
	print("CONTENT_SCALE_MODE=%d (期望 1=canvas_items)" % r.content_scale_mode)
	print("CONTENT_SCALE_ASPECT=%d (期望 1=keep)" % r.content_scale_aspect)
	print("CONTENT_SCALE_SIZE=%s (期望 (640,360))" % str(r.content_scale_size))
	print("默认纹理过滤=%d (期望 0=Nearest)" % \
		ProjectSettings.get_setting("rendering/textures/canvas_textures/default_texture_filter"))
	# scale_mode 是 4.2+ 才有，读 window/stretch/scale_mode 配置项确认写进去了
	var sm = ProjectSettings.get_setting("display/window/stretch/scale_mode")
	print("STRETCH_SCALE_MODE=%s (期望 1=integer)" % str(sm))
	quit(0)
