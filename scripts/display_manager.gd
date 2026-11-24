extends Node

## 显示模式：小窗 / 全屏切换。
##
## 缩放不在这里做 —— 交给 Godot 内置的 canvas_items 缩放（project.godot 里
## window/stretch/mode="canvas_items" + window/stretch/scale_mode=0 = fractional，
## 配合 aspect=keep）。逻辑分辨率永远 1280×720：
##   - 小窗：默认 1280×720（1x），用户也能直接拖窗口边随意缩放，Godot 自动适应
##   - 全屏：Exclusive Fullscreen，Godot 按显示器比例铺满
##
## 为什么之前的 F11「不可用」：手写用的是普通 Fullscreen + fractional 缩放，
## 在非 16:9 显示器上会拉伸/发糊。官方明确建议像素游戏用 Exclusive Fullscreen，
## 它不底部留 1px，配 canvas_items 缩放才能自适应任意显示器。

enum DisplayMode { WINDOW, FULLSCREEN }

const WINDOW_W := 1280
const WINDOW_H := 720

signal mode_changed(mode: int)

var mode: int = DisplayMode.WINDOW


func _ready() -> void:
	# 尊重当前窗口状态，不强行改（默认由 project.godot 的 window_width_override 决定）
	mode = DisplayMode.FULLSCREEN if DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN else DisplayMode.WINDOW


## 切换入口只保留 toggle()/set_mode()。
## ⚠️ 按键监听不在这里做：`_unhandled_input` 在这个场景里收不到 F11（已被上层 Control 吞掉，
## 2026-11-20 实测「按 F11 没反应」）。改由 main.gd 的 _process 轮询驱动（与项目其它输入同风格）。
func toggle() -> void:
	set_mode(DisplayMode.FULLSCREEN if mode == DisplayMode.WINDOW else DisplayMode.WINDOW)


func set_mode(m: int) -> void:
	mode = m
	if m == DisplayMode.FULLSCREEN:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN)
	else:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
		DisplayServer.window_set_size(Vector2i(WINDOW_W, WINDOW_H))
	mode_changed.emit(mode)
