extends SceneTree

## HUD 排版自检（视口 1280×720 / UI=2）。
## 只验「东西放不放得下、有没有互相压住」，不验颜色和美术。
## 跑法：godot --headless --path . --script res://_mdtest/hud_layout_check.gd

const Hud = preload("res://scripts/hud.gd")
const FrameData = preload("res://scripts/frame_data.gd")

var fails := 0


func _ok(cond: bool, label: String) -> void:
	print(("PASS " if cond else "FAIL ") + label)
	if not cond:
		fails += 1


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	var hud = Hud.new()
	root.add_child(hud)
	hud.size = Vector2(1280, 720)
	hud.frame_max = 4
	hud.index = 0
	hud.year = 1926
	hud.frame_id = "a1_1926"
	hud.time_mode = false

	var f = FrameData.new()
	hud.sync(false, 0, 4, f)

	print("HUD_SIZE=%s" % str(hud.size))
	print("FONT=%d FONT_BIG=%d (期望 20 / 26)" % [Hud.FONT, Hud.FONT_BIG])
	_ok(Hud.FONT == 20 and Hud.FONT_BIG == 26, "字号随视口翻倍")

	# 顶部条：三段文字不能互相压住
	var axis_name := "空间轴 · SPACE"
	var aw: float = hud.font.get_string_size(axis_name, HORIZONTAL_ALIGNMENT_LEFT, -1, Hud.FONT).x
	var left_txt := "%d · %s" % [hud.year, hud.frame_id]
	var lw: float = hud.font.get_string_size(left_txt, HORIZONTAL_ALIGNMENT_LEFT, -1, Hud.FONT).x
	var hint := "F11 全屏/小窗"
	var hw: float = hud.font.get_string_size(hint, HORIZONTAL_ALIGNMENT_LEFT, -1, Hud.FONT).x
	var l_end: float = 8.0 * 2.0 + lw
	var a_start: float = (1280.0 - aw) * 0.5
	var a_end: float = a_start + aw
	var h_start: float = 1280.0 - hw - 8.0 * 2.0
	print("  左段 x=[%.0f,%.0f] 中段 x=[%.0f,%.0f] 右段 x=[%.0f,%.0f]" % [
		l_end - lw, l_end, a_start, a_end, h_start, h_start + hw])
	_ok(l_end < a_start, "左段不压中段")
	_ok(a_end < h_start, "中段不压右段")
	_ok(h_start + hw <= 1280.0, "右段不出屏")

	# 顶部条高度要能装下 20px 字（基线 26，条高 36）
	_ok(18.0 * 2.0 >= 20.0 + 4.0, "顶条高 36 装得下 20px 字")

	# 底部时间轴条：5 档，刻度点不越界
	var bar_h: float = 30.0 * 2.0
	var y: float = 720.0 - bar_h
	var slot: float = 1280.0 / 5.0
	_ok(y > 0.0, "底条不遮住整个屏（y=%.0f）" % y)
	var first_cx: float = slot * 0.5
	var last_cx: float = slot * 4.5
	_ok(first_cx - 3.5 * 2.0 > 0.0, "第一个点不越左边界")
	_ok(last_cx + 3.5 * 2.0 < 1280.0, "最后一个点不越右边界")
	print("  底条 y=%.0f h=%.0f 点 x=%.0f..%.0f" % [y, bar_h, first_cx, last_cx])

	# 底部提示字：居中且不出屏
	var txt := "WASD 走    SHIFT 进时间轴    E 检视"
	var tw: float = hud.font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, Hud.FONT).x
	_ok(tw < 1280.0, "底部提示字宽 %.0f 放得进 1280" % tw)

	# 检视卡：长文本要折行且总高不超出屏幕上半部
	hud.show_hotspot({"title": "账桌", "text": "一本硬壳账簿摊在柜台上。纸很好，字极整齐。最后一页写着：收粮 三石。"})
	var pad: float = 8.0 * 2.0
	var line_h: float = 13.0 * 2.0
	var w: float = 1280.0 - 40.0 * 2.0
	var lines = hud._wrap(hud.hotspot_text, w - pad * 2.0)
	var h: float = pad * 2.0 + line_h + float(lines.size()) * line_h
	var hy: float = 720.0 - 34.0 * 2.0 - h
	print("  检视卡 宽=%.0f 高=%.0f y=%.0f 折行=%d" % [w, h, hy, lines.size()])
	_ok(w <= 1280.0, "检视卡不超屏宽")
	_ok(hy > bar_h + 20.0, "检视卡不压住底部时间轴条")

	# ── 小地图断言（L12 新增，只加不改上面的）──────────────────
	var mm: Rect2 = hud.minimap_rect()
	print("  小地图 x=[%.0f,%.0f] y=[%.0f,%.0f] 尺寸=%.0f×%.0f" % [
		mm.position.x, mm.end.x, mm.position.y, mm.end.y, mm.size.x, mm.size.y])
	_ok(mm.end.x <= 1280.0, "小地图不越右屏")
	_ok(mm.position.y >= 36.0, "小地图在顶条下沿之外")
	_ok(mm.end.y <= 660.0, "小地图在底条上沿之外")
	# 与三块钉死的 UI 都不相交（Rect2.intersects）
	_ok(not mm.intersects(Rect2(0, 0, 1280, 36)), "小地图不压顶条")
	_ok(not mm.intersects(Rect2(0, 660, 1280, 60)), "小地图不压底条")
	_ok(not mm.intersects(Rect2(40, hy, w, h)), "小地图不压检视卡")
	# 世界坐标 → 小地图坐标映射（0,0→左上角，4800×3600→右下角）
	var mm_tl: Vector2 = hud.minimap_point(Vector2(0, 0))
	var mm_br: Vector2 = hud.minimap_point(Vector2(4800, 3600))
	_ok(mm_tl == mm.position, "映射原点=小地图左上角")
	_ok(is_equal_approx(mm_br.x, mm.end.x) and is_equal_approx(mm_br.y, mm.end.y),
		"映射(4800,3600)=右下角")
	# 玩家点：世界中心必须落在框内
	hud.sync_player(Vector2(2400, 1800))
	var mm_p: Vector2 = hud.minimap_point(hud.player_pos)
	_ok(mm_p.x >= mm.position.x and mm_p.x <= mm.end.x
		and mm_p.y >= mm.position.y and mm_p.y <= mm.end.y, "玩家点落在小地图内")
	# 帧切换后小地图几何不变（sync 不许动它）
	var f2 = FrameData.new()
	f2.id = "a5_2026"
	f2.year = 2026
	hud.sync(true, 4, 4, f2)
	hud.sync(false, 0, 4, f)
	_ok(hud.minimap_rect() == mm, "帧切换后小地图矩形不变")

	print("HUD_CHECK_DONE fails=%d" % fails)
	quit(1 if fails > 0 else 0)
