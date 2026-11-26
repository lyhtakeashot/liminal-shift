extends SceneTree

## 房屋美术验收 C1–C3（docs/PROMPT-house-art-a4a5-exec.md §4 验收）。
##
##   C1  15 张 PNG 都在，且**引擎能找到**（ResourceLoader.exists ⇒ world_view._house_tex 拿得到，
##       走美术通路；找不到就回落到色块降级，等于没交付）
##   C2  画布尺寸严格 = ((x1−x0+1)×32, (y1−y0+2)×32)，且与 _ref/houses/houses_data.json 的 lot 对得上
##   C3  RGBA 带 alpha 且透明像素占比 > 0（全不透明 = 直接塞参考图的嫌疑）
##
## 另加三条加强判定（专治「交付了一张纯色块」这种表面合规）：
##   K1  不透明颜色数 ≥ 10（base）/ ≥ 8（roof）—— 1~3 色就是色块，不是像素贴图
##   K2  roof 不是 base 的整张复制（差异 > 20%）
##   K3  废墟 lu/a3_roof 是「压色块遮罩」：翼投影区与 base 逐像素一致，区外透明
##   C5  窗口模式跑真游戏 5 帧，对准各帧的房子截屏 → **双份墙**判定（见下）
##
## 跑法：
##   headless（C1/C2/C3/K1/K2/K3）：godot --headless --path . -s res://_mdtest/house_art_check.gd
##   窗口（再加 C5 像素证据）：      godot --path . -s res://_mdtest/house_art_check.gd
## headless 是 dummy 渲染器读不到帧缓冲 ⇒ C5 自动跳过并打印 PIXEL_SKIP。
##
## C5 怎么判「双份墙」：world_view 在有 base 图时不再画引擎色块墙（_art_walls 分支），
## 但 L9 的 _draw_art_wall_strips 会把 base 里**同一条墙行**按原位置补贴回前景层（换正确
## 深度）。所以真出问题的形态是「美术立面之上又压了一层平的色块」。做法：镜头对准该栋
## 最南翼的南立面带（32px 高），在帧缓冲里量 8×8 小块的局部颜色多样性 —— 平色块的小块
## 只有 1 种颜色，真实立面（砖缝/木纹/门窗）几乎块块 ≥2 种。阈值 0.60 是按美术实测
## 0.767~0.998 留的余量。

const TILE := 32

## [族名, 帧号, house_id, 期望宽, 期望高]
const EXPECT := [
	["market", "a4", "market", 1344, 928],
	["shen", "a4", "shen_a4", 1152, 1184],
	["zhou", "a4", "zhou_a4", 704, 384],
	["zheng", "a4", "zheng_a4", 640, 448],
	["shen", "a5", "shen_a5", 1152, 1184],
	["toyshop", "a5", "toyshop", 672, 672],
	["school", "a5", "school", 1216, 992],
]
## 废墟补的 roof 层（不是美术，是压引擎色块屋顶的遮罩，见 _gen_shells.paint_ruin_roof_mask）
const RUIN_ROOF := ["lu", "a3", 640, 448]

const MIN_COLORS_BASE := 10
const MIN_COLORS_ROOF := 8
const MIN_ROOF_DIFF := 0.20

## C5：五帧各挑一栋主房截图（A1–A3 走老美术，A4/A5 走这次新落的两套房）
const C5_TARGET := {
	"a1_1926": "lu_house",
	"a2_1951": "lu_a2",
	"a3_1976": "lu_a3",
	"a4_2001": "shen_a4",
	"a5_2026": "shen_a5",
}
## A4/A5 帧里其余几栋再逐栋对一次（双份墙只会出现在有 base 图的房子上）
const C5_EXTRA := {
	"a4_2001": ["market", "zhou_a4", "zheng_a4"],
	"a5_2026": ["market", "toyshop", "school"],
}
const C5_SHOT_DIR := "res://_mdtest/house_art_preview"
const C5_PATCH_MIN := 0.60      # 立面带里「≥2 种颜色」的 8×8 小块占比下限（美术实测 0.767~0.998）
const C5_COLORS_MIN := 5        # 立面带整条的不透明颜色数下限（引擎色块只有 2~3 色）
const C5_MIN_W := 256.0         # 立面带至少这么多像素要在视口里（market 带 1344px 比视口还宽）

var fails := 0
var checks := 0
var kw_seen := {}
var lots := {}


func _init() -> void:
	call_deferred("_run")


func _ok(cond: bool, label: String) -> void:
	checks += 1
	if not cond:
		fails += 1
	for kw in ["C1", "C2", "C3"]:
		if label.contains(kw):
			kw_seen[kw] = int(kw_seen.get(kw, 0)) + 1
	print(("PASS " if cond else "FAIL ") + label)


func _run() -> void:
	lots = _read_lots()
	_check_presence_and_size()
	_check_not_color_block()
	_check_roof_is_not_base_copy()
	_check_ruin_mask()
	# C5 要读帧缓冲 ⇒ 只有窗口模式能验；headless 会打印 PIXEL_SKIP 并跳过
	await _check_window_frames()
	# 关键词覆盖自检：验收项写在文档里不算，得有一条断言真验过它
	var missing := []
	for kw in ["C1", "C2", "C3"]:
		if int(kw_seen.get(kw, 0)) == 0:
			missing.append(kw)
	_ok(missing.is_empty(), "验收关键词 C1/C2/C3 都有断言覆盖（C1×%d C2×%d C3×%d，缺 %s）"
		% [int(kw_seen.get("C1", 0)), int(kw_seen.get("C2", 0)), int(kw_seen.get("C3", 0)), str(missing)])
	print("HOUSE_ART_CHECK_DONE checks=%d fails=%d" % [checks, fails])
	quit(1 if fails > 0 else 0)


# ---------------------------------------------------------------- 工具
func _path(fam: String, fr: String, layer: String) -> String:
	return "res://assets/village/houses/%s/%s_%s.png" % [fam, fr, layer]


## base+roof 的 [路径, house_id, 期望宽, 期望高] 全表（7 栋 × 2 层 + 废墟 roof）
func _items() -> Array:
	var out := []
	for row in EXPECT:
		for layer in ["base", "roof"]:
			out.append([_path(String(row[0]), String(row[1]), layer), String(row[2]), int(row[3]), int(row[4])])
	out.append([_path(String(RUIN_ROOF[0]), String(RUIN_ROOF[1]), "roof"), "lu_a3", int(RUIN_ROOF[2]), int(RUIN_ROOF[3])])
	return out


func _read_lots() -> Dictionary:
	## houses_data.json 是只读输入：这里只读 lot 用来交叉验算 C2，不改任何东西。
	var out := {}
	var p := "res://_ref/houses/houses_data.json"
	if not FileAccess.file_exists(p):
		return out
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return out
	var txt := f.get_as_text()
	f.close()
	var arr: Variant = JSON.parse_string(txt)
	if arr is Array:
		for h in arr:
			if h is Dictionary and h.has("lot"):
				out[String(h.get("id", ""))] = h["lot"]
	return out


func _img(path: String) -> Image:
	var tex := ResourceLoader.load(path) as Texture2D
	if tex != null:
		var im := tex.get_image()
		if im != null:
			if im.is_compressed():
				im.decompress()
			return im
	if FileAccess.file_exists(path):          # 兜底：直接读源 PNG（不依赖 .import）
		var abs := ProjectSettings.globalize_path(path)
		var im2 := Image.load_from_file(abs)
		if im2 != null:
			return im2
	return null


## 透明像素占比（每 4 像素采 1 个；1152×1184 约 8.5 万次采样，够判「有没有透明」）
func _transparent_ratio(img: Image) -> float:
	var n := 0
	var t := 0
	for y in range(0, img.get_height(), 4):
		for x in range(0, img.get_width(), 4):
			n += 1
			if img.get_pixel(x, y).a < 8.0 / 255.0:
				t += 1
	return float(t) / float(max(1, n))


## 不透明颜色数（每 4 像素采 1 个，整色键进字典；1~3 色 = 色块）
func _color_count(img: Image) -> int:
	var data := img.get_data()
	var seen := {}
	var step := 16                       # 4 像素 × 4 字节
	var i := 0
	while i + 3 < data.size():
		if data[i + 3] != 0:          # 全透明像素不算
			seen[(int(data[i]) << 24) | (int(data[i + 1]) << 16) | (int(data[i + 2]) << 8) | int(data[i + 3])] = true
		i += step
	return seen.size()


func _diff_ratio(a: Image, b: Image) -> float:
	var w: int = min(a.get_width(), b.get_width())
	var h: int = min(a.get_height(), b.get_height())
	var n := 0
	var d := 0
	for y in range(0, h, 6):
		for x in range(0, w, 6):
			n += 1
			if a.get_pixel(x, y) != b.get_pixel(x, y):
				d += 1
	return float(d) / float(max(1, n))


# ---------------------------------------------------------------- C1 / C2 / C3
func _check_presence_and_size() -> void:
	for it in _items():
		var path := String(it[0])
		var hid := String(it[1])
		var ew := int(it[2])
		var eh := int(it[3])
		var short := path.get_file().replace(".png", "")
		# ---- C1：引擎找得到 ----
		if not ResourceLoader.exists(path):
			_ok(false, "C1 %s(%s) 引擎找不到 → 会回落色块降级：%s" % [hid, short, path])
			continue
		_ok(true, "C1 %s(%s) 在资源树里 → world_view._house_tex 拿得到" % [hid, short])
		# ---- C2：尺寸 ----
		var img := _img(path)
		if img == null:
			_ok(false, "C2 %s(%s) 读不出像素数据" % [hid, short])
			continue
		var sz := img.get_size()
		_ok(sz == Vector2i(ew, eh), "C2 %s(%s) 画布 %d×%d == 期望 %d×%d" % [hid, short, sz.x, sz.y, ew, eh])
		# C2 交叉验算：期望值本身要能从 houses_data 的 lot 推出来（防手抄错尺寸表）
		var lot = lots.get(hid, [])
		if lot is Array and (lot as Array).size() == 4:
			var dw := (int(lot[2]) - int(lot[0]) + 1) * TILE
			var dh := (int(lot[3]) - int(lot[1]) + 2) * TILE
			_ok(dw == ew and dh == eh, "C2 %s lot 推导 = %d×%d，与验收表 %d×%d 一致" % [hid, dw, dh, ew, eh])
		# ---- C3：alpha ----
		_ok(img.detect_alpha() != Image.ALPHA_NONE,
			"C3 %s(%s) 带 alpha 通道（format=%d）" % [hid, short, int(img.get_format())])
		var t := _transparent_ratio(img)
		_ok(t > 0.0, "C3 %s(%s) 透明像素占比 %.1f%% > 0（全不透明＝像直接塞参考图）" % [hid, short, t * 100.0])


# ---------------------------------------------------------------- K1：不是色块
func _check_not_color_block() -> void:
	for it in _items():
		var path := String(it[0])
		var hid := String(it[1])
		var layer := "base" if path.ends_with("_base.png") else "roof"
		if hid == "lu_a3":
			continue                      # 遮罩是 base 的副本，颜色数由 base 保证
		var img := _img(path)
		if img == null:
			continue
		var n := _color_count(img)
		var need := MIN_COLORS_BASE if layer == "base" else MIN_COLORS_ROOF
		_ok(n >= need, "K1 %s %s 不透明颜色数 %d ≥ %d（1~3 色=色块，不是像素贴图）" % [hid, layer, n, need])


# ---------------------------------------------------------------- K2：roof 不是 base 整张复制
func _check_roof_is_not_base_copy() -> void:
	for row in EXPECT:
		var hid := String(row[2])
		var base := _img(_path(String(row[0]), String(row[1]), "base"))
		var roof := _img(_path(String(row[0]), String(row[1]), "roof"))
		if base == null or roof == null:
			_ok(false, "K2 %s base/roof 读不出像素，无法比对" % hid)
			continue
		var d := _diff_ratio(base, roof)
		_ok(d > MIN_ROOF_DIFF, "K2 %s roof 与 base 差异 %.0f%% > 20%%（不是把 base 整张复制成 roof）" % [hid, d * 100.0])


# ---------------------------------------------------------------- K3：废墟遮罩
func _check_ruin_mask() -> void:
	## lu_a3 的 roof 不是美术而是遮罩：它必须等于 base 在翼投影区的像素，
	## 这样 world_view._draw_roof 里先画的那层色块屋顶才会被「什么也不加」地盖住。
	var base := _img(_path("lu", "a3", "base"))
	var roof := _img(_path("lu", "a3", "roof"))
	if base == null or roof == null:
		_ok(false, "K3 lu_a3 base/roof 读不出像素，无法比对遮罩")
		return
	var mism := 0
	var sampled := 0
	# 翼 [0,0,15,11] 的画布投影：x 0..480，y 0..352（_gen_shells.draw_roof 同式）
	for y in range(0, min(352, roof.get_height()), 3):
		for x in range(0, min(480, roof.get_width()), 3):
			sampled += 1
			if base.get_pixel(x, y) != roof.get_pixel(x, y):
				mism += 1
	_ok(mism == 0, "K3 lu_a3 roof 在翼投影区与 base 逐像素一致（采 %d 点，不一致 %d）" % [sampled, mism])
	# 翼外必须透明（否则等于把院子也重画一遍）
	var outside := Vector2i(min(560, roof.get_width() - 1), min(400, roof.get_height() - 1))
	_ok(roof.get_pixel(outside.x, outside.y).a < 8.0 / 255.0,
		"K3 lu_a3 roof 在翼外 (%d,%d) 透明（只压屋顶那块，不重画院子）" % [outside.x, outside.y])


# ---------------------------------------------------------------- C5：双份墙（窗口）
## frames.json 的 house 条目（pos = 世界坐标左上角）。自己解析，不依赖 Timeline 的字段名。
func _read_frame_houses() -> Array:
	var out := []
	var doc: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://data/frames.json"))
	if doc is Dictionary:
		for f in (doc as Dictionary).get("frames", []):
			var fd: Dictionary = f
			var hs := {}
			for s in fd.get("shapes", []):
				var sd: Dictionary = s
				if String(sd.get("type", "")) == "house":
					var p: Array = sd.get("pos", [0, 0])
					hs[String(sd.get("id", ""))] = Vector2(float(p[0]), float(p[1]))
			out.append({"id": String(fd.get("id", "")), "houses": hs})
	return out


## houses_data.json 全条目（要 wings 定位立面带；只读，不改）
func _read_house_data() -> Dictionary:
	var out := {}
	var p := "res://_ref/houses/houses_data.json"
	if not FileAccess.file_exists(p):
		return out
	var arr: Variant = JSON.parse_string(FileAccess.get_file_as_string(p))
	for h in (arr if arr is Array else []):
		if h is Dictionary:
			out[String((h as Dictionary).get("id", ""))] = h
	return out


## 最南翼的南立面带，返回**贴图内坐标**（base 图左上角为原点）。
## 映射：画布 row0 = 世界 row−1 ⇒ 贴图 y = lot 内 y + 32；墙格 j 的南立面在 y ∈ [j*32+32, j*32+64)。
func _facade_band(data: Dictionary) -> Rect2:
	var wings: Array = data.get("wings", [])
	if wings.is_empty():
		return Rect2()
	var best: Array = wings[0]
	for w in wings:
		var ww: Array = w
		if int(ww[1]) + int(ww[3]) > int(best[1]) + int(best[3]):
			best = ww
	var wy := int(best[1])
	var wh := int(best[3])
	return Rect2(int(best[0]) * TILE, (wy + wh - 1) * TILE + TILE, int(best[2]) * TILE, TILE)


## 五帧各跑一次真游戏、把镜头对准该帧的房子截屏，再在帧缓冲里判「双份墙」。
func _check_window_frames() -> void:
	if DisplayServer.get_name() == "headless":
		print("PIXEL_SKIP 无渲染器（headless）—— C5 双份墙证据用窗口模式再跑一次本脚本")
		return
	var frames := _read_frame_houses()
	var houses := _read_house_data()
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	await process_frame
	var tl = main.get("tl")
	var cam: Node2D = main.get_node_or_null("CameraRig")
	if tl == null or cam == null or not main.has_method("_refresh_all"):
		_ok(false, "C5 主场景缺 tl / CameraRig / _refresh_all，窗口验收无法进行")
		return
	var tl_frames: Array = tl.get("frames")
	if tl_frames.size() != frames.size():
		_ok(false, "C5 timeline 帧数 %d != frames.json %d" % [tl_frames.size(), frames.size()])
		return
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(C5_SHOT_DIR))
	var shot := 0
	for i in frames.size():
		var fmeta: Dictionary = frames[i]
		var fid := String(fmeta["id"])
		var poses: Dictionary = fmeta["houses"]
		var ids: Array = []
		if C5_TARGET.has(fid):
			ids.append(String(C5_TARGET[fid]))
		for e in C5_EXTRA.get(fid, []):
			ids.append(String(e))
		for hid in ids:
			if not poses.has(hid):
				_ok(false, "C5 %s 在 frames.json(%s) 里没有 house 条目" % [hid, fid])
				continue
			if not houses.has(hid):
				_ok(false, "C5 %s 在 houses_data.json 里没有 wings" % hid)
				continue
			var band := _facade_band(houses[hid] as Dictionary)
			if band.size.x <= 0.0:
				_ok(false, "C5 %s wings 为空，定位不到立面带" % hid)
				continue
			# 贴图内坐标 → 世界坐标：base 图左上角贴在 (pos.x, pos.y − 32)
			var wband := Rect2((poses[hid] as Vector2) + band.position - Vector2(0, TILE), band.size)
			var cam_at := wband.get_center()
			var stand := cam_at + Vector2(0, 220)      # 玩家站到立面带以南，别挡住采样区
			tl.index = i
			tl.axis = 0
			tl.char_pos = stand
			main.call("_refresh_all")
			var ply: Node2D = main.get("player")
			if ply != null:
				ply.position = stand
			cam.call("set_target", cam_at)
			for k in 40:
				await process_frame
			cam.set("offset", cam.call("_clamp", cam_at - Vector2(640, 360)))
			cam.call("_apply")
			await process_frame
			await RenderingServer.frame_post_draw
			await process_frame
			await RenderingServer.frame_post_draw
			var img: Image = root.get_texture().get_image()
			var path := "%s/c5_%s_%s.png" % [C5_SHOT_DIR, fid, hid]
			img.save_png(ProjectSettings.globalize_path(path))
			print("SHOT ", path)
			shot += 1
			# 屏幕 = 世界 + rig.position（camera_rig._apply: position = −offset.floor()）
			var screen := Rect2(wband.position + cam.position, wband.size)
			var view := Rect2(Vector2.ZERO, Vector2(img.get_width(), img.get_height()))
			var vis := screen.intersection(view)
			if vis.size.x < C5_MIN_W or vis.size.y < 24.0:
				_ok(false, "C5 %s(%s) 立面带只有 %s 落在视口内（需 ≥%d×24）"
					% [hid, fid, str(vis), int(C5_MIN_W)])
				continue
			print("BAND %s %s 视口内立面带 = %s（对应 base 图内 %s）" % [hid, fid, str(vis), str(band)])
			_check_band_pixels(img, vis, hid, fid)
	_ok(shot > 0, "C5 窗口模式确实截到了帧（张数 %d）" % shot)


## 立面带的局部颜色多样性 —— 平色块（双份墙）的 8×8 小块只有 1 色。
func _check_band_pixels(img: Image, rect: Rect2, hid: String, fid: String) -> void:
	var bx := int(rect.position.x)
	var by := int(rect.position.y)
	var bw := int(rect.size.x)
	var bh := int(rect.size.y)
	var good := 0
	var tot := 0
	var seen := {}
	# y 从 +2 起：屋顶色块/贴图的底边最多压到带顶 1px，避开它
	for py in range(by + 2, by + bh - 7, 8):
		for px in range(bx, bx + bw - 7, 8):
			var local := {}
			for y in range(py, py + 8):
				for x in range(px, px + 8):
					local[img.get_pixel(x, y).to_rgba32()] = true
			seen.merge(local, true)
			tot += 1
			if local.size() >= 2:
				good += 1
	var ratio := float(good) / float(max(1, tot))
	_ok(ratio >= C5_PATCH_MIN,
		"C5 %s(%s) 立面带 %d 个 8×8 小块里 %.0f%% 有 ≥2 种颜色（≥%.0f%% ⇒ 墙上没压平的色块段）"
		% [hid, fid, tot, ratio * 100.0, C5_PATCH_MIN * 100.0])
	_ok(seen.size() >= C5_COLORS_MIN,
		"C5 %s(%s) 立面带不透明颜色数 %d ≥ %d（引擎色块墙只有 2~3 色）"
		% [hid, fid, seen.size(), C5_COLORS_MIN])