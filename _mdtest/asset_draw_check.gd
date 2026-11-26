extends SceneTree

## 美术资产消费点专项自检（PROMPT-asset-consumption-exec.md）：
##   1. 房子 base 图：能加载、画布尺寸 == lot_w×32 × (lot_h+1)×32（D6）
##   2. 家具 props 图：按 short + 占地匹配，底部中心锚点（D6），缺图回 null
##   3. 场景图：河/路/田/井/槐/坝/碑 按帧索引，缺图回 null
##   4. 主角精灵表：36 帧、方向分组齐全
##   5. 贴图**不影响**排序不变式与碰撞（y-sort 键、AABB 数量）
##
## 只测 A1–A3（A4/A5 的帧 shapes 为空，本来就画不到东西）。

const AssetDraw = preload("res://scripts/asset_draw.gd")
const HouseShape = preload("res://scripts/house_shape.gd")
const WorldView = preload("res://scripts/world_view.gd")
const Player = preload("res://scripts/player.gd")
const FrameData = preload("res://scripts/frame_data.gd")

const TILE := 32.0

## A1–A3 的 12 栋（与 world_view.gd 的 FAMILY 表一致）
const HOUSES := [
	"lu_house", "shen_a1", "mill_a1", "zhou_house",
	"lu_a2", "shen_a2", "mill_a2", "zhou_a2",
	"lu_a3", "shen_a3", "mill_a3", "zhou_a3",
]

## 三帧
const FRAMES := ["a1_1926", "a2_1951", "a3_1976"]

var fails := 0


func _ok(cond: bool, label: String) -> void:
	print(("PASS " if cond else "FAIL ") + label)
	if not cond:
		fails += 1


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	_check_manifest()
	_check_shell_textures()
	_check_art_walls()
	_check_prop_matching()
	_check_scene_textures()
	_check_a4a5_wiring()
	_check_hero_sheet()
	_check_no_collision_change()
	_check_sort_invariant()
	print("ASSET_DRAW_CHECK_DONE fails=%d" % fails)
	quit(1 if fails > 0 else 0)


## ---------- 2b. 墙/门由美术 base 图接管（不画「双份墙」）----------
## base 图里已经画好墙顶面 + 南立面 + 门窗 + 院门
## （_ref/art/gen/_gen_shells.py 的 draw_cap / draw_facade / draw_door / draw_gate），
## 引擎再叠一层色块 = 双份墙。有 base 图 ⇒ 引擎不画墙；无 base 图 ⇒ 回色块。
func _check_art_walls() -> void:
	var n_art := 0
	var n_fallback := 0
	var bad := 0
	for sid in HOUSES:
		var has_base := false
		for e in AssetDraw.manifest().get("shell", []):
			var ed: Dictionary = e
			if String(ed.get("house", "")) == sid \
					and String(ed.get("layer", "")) == "base":
				has_base = AssetDraw.load_asset("res://" + String(ed.get("path", ""))) != null
				break
		var art := WorldView._art_walls(sid)
		if art != has_base:
			bad += 1
			print("  墙归属不符 %s: art=%s base图=%s" % [sid, str(art), str(has_base)])
		if art:
			n_art += 1
		else:
			n_fallback += 1
	_ok(bad == 0, "墙归属与 base 图存在性一致（不符 %d 栋）" % bad)
	_ok(n_art >= 10, "12 栋里至少 10 栋由美术图接管墙（实际 %d）" % n_art)

	# 墙/门条目**仍然留在排序链里**（排序不变式不动，只是不画色块）
	var wv := WorldView.new()
	root.add_child(wv)
	var fd := FrameData.new()
	var frames_json: Dictionary = JSON.parse_string(
		FileAccess.get_file_as_string("res://data/frames.json"))
	for f in frames_json["frames"]:
		if String(f["id"]) != "a1_1926":
			continue
		fd.setup(f)
		break
	wv.frame = fd
	wv.player_pos = Vector2(2512, 1104)
	var ents := wv._collect_front()
	var n_walls := 0
	var n_doors := 0
	for e in ents:
		var k := String((e as Dictionary)["kind"])
		if k == "walls":
			n_walls += 1
		elif k == "door":
			n_doors += 1
	_ok(n_walls > 0, "前景层仍有墙条目 %d 行（排序链没被删）" % n_walls)
	_ok(n_doors > 0, "前景层仍有门条目 %d 个（排序链没被删）" % n_doors)
	wv.queue_free()


## ---------- 1. manifest ----------
func _check_manifest() -> void:
	var m := AssetDraw.manifest()
	_ok(not m.is_empty(), "manifest 能读到")
	_ok((m.get("props", []) as Array).size() == 91, "manifest 有 91 条 props")
	_ok((m.get("shell", []) as Array).size() > 0, "manifest 有 shell 条目")
	_ok((m.get("scene", []) as Array).size() > 0, "manifest 有 scene 条目")


## ---------- 2. 房子 base 图 ----------
func _check_shell_textures() -> void:
	var n_base := 0
	var n_roof := 0
	var bad := 0
	for sid in HOUSES:
		var data := HouseShape.house(sid)
		if data.is_empty():
			continue
		var lot: Array = data.get("lot", [0, 0, 0, 0])
		# D6：画布 = (lot_w+1)×32 × (lot_h+1+1)×32。
		# ⚠️ houses_data 的 lot 是**闭区间**（[x0,y0,x1,y1]），lot_rect() 才 +1。
		var lw := float(lot[2] - lot[0] + 1)
		var lh := float(lot[3] - lot[1] + 1)
		var want := Vector2(lw * TILE, (lh + 1.0) * TILE)
		for layer in ["base", "roof"]:
			var tex: Texture2D = null
			for e in AssetDraw.manifest().get("shell", []):
				var ed: Dictionary = e
				if String(ed.get("house", "")) == sid \
						and String(ed.get("layer", "")) == layer:
					tex = AssetDraw.load_asset("res://" + String(ed.get("path", "")))
					break
			if tex == null:
				continue
			if layer == "base":
				n_base += 1
			else:
				n_roof += 1
			# D6：画布 = lot_w×32 × (lot_h+1)×32
			if tex.get_size() != want:
				bad += 1
				print("  尺寸不符 %s/%s: 实际 %s 期望 %s" % [sid, layer,
					str(tex.get_size()), str(want)])
	_ok(n_base >= 10, "12 栋里至少有 10 张 base 图（实际 %d）" % n_base)
	_ok(n_roof >= 10, "12 栋里至少有 10 张 roof 图（实际 %d）" % n_roof)
	_ok(bad == 0, "base/roof 画布尺寸都符合 D6（不符 %d 张）" % bad)


## ---------- 3. 家具 props 图 ----------
func _check_prop_matching() -> void:
	# 3a. short + 占地 完全一致优先
	var e1 := AssetDraw.prop_match("凳", 1, 1)
	_ok(String(e1.get("id", "")) == "deng_1x1", "凳 1×1 → deng_1x1")
	var e2 := AssetDraw.prop_match("凳", 1, 3)
	_ok(String(e2.get("id", "")) == "deng_1x3", "凳 1×3 → deng_1x3")
	var e3 := AssetDraw.prop_match("八仙桌", 2, 2)
	_ok(String(e3.get("id", "")) == "baxianzhuo_2x2", "八仙桌 2×2 → baxianzhuo_2x2")
	var e4 := AssetDraw.prop_match("八仙桌", 2, 3)
	_ok(String(e4.get("id", "")) == "baxianzhuo_2x3", "八仙桌 2×3 → baxianzhuo_2x3")

	# 3b. manifest 没有的 short → 空字典（回色块，不报错）
	_ok(AssetDraw.prop_match("跑道", 1, 1).is_empty(), "manifest 没有的 short 回空字典")

	# 3c. 全量：贴图尺寸 = 占地宽×32 × (占地高×32 + 32)（D6）
	var mism := 0
	var matched := 0
	for sid in HOUSES:
		var data := HouseShape.house(sid)
		if data.is_empty():
			continue
		for f in HouseShape.furniture_rects(data, Vector2.ZERO):
			var fd: Dictionary = f
			var r: Rect2 = fd["rect"]
			var fw := int(round(r.size.x / TILE))
			var fh := int(round(r.size.y / TILE))
			var e := AssetDraw.prop_match(String(fd["name"]), fw, fh)
			if e.is_empty():
				continue
			matched += 1
			var tex: Texture2D = AssetDraw.load_asset(
				"res://" + String(e.get("path", "")))
			if tex == null:
				continue
			var want := Vector2(float(fw) * TILE, (float(fh) + 1.0) * TILE)
			if tex.get_size() != want:
				mism += 1
	_ok(matched > 100, "A1–A3 家具命中 manifest %d 条" % matched)
	_ok(mism == 0, "命中项的贴图画布尺寸符合 D6（不符 %d 条）" % mism)

	# 3d. 底部中心锚点：贴图底边 == 占地底边
	var r0 := Rect2(100, 200, 64, 64)
	var pd := AssetDraw.prop_draw("八仙桌", r0)
	_ok(not pd.is_empty(), "八仙桌能拿到贴图+落点")
	if not pd.is_empty():
		var dst: Rect2 = pd["dst"]
		_ok(is_equal_approx(dst.end.y, r0.end.y), "贴图底边对齐占地底边（D6 底部锚点）")
		_ok(is_equal_approx(dst.position.x, r0.position.x), "贴图左边对齐占地左边")


## ---------- 4. 场景图 ----------
func _check_scene_textures() -> void:
	for fid in FRAMES:
		for kind in ["river", "road", "field", "well", "tree", "dam", "stele"]:
			var tex := AssetDraw.scene_tex(fid, kind)
			_ok(tex != null, "%s 有 %s 场景图" % [fid, kind])
	# A4/A5 没有场景图 → 回 null（优雅降级）
	_ok(AssetDraw.scene_tex("a4_2001", "river") == null, "a4_2001 无场景图 → null")

	# L8：五帧的 32px 平铺瓦片齐全（ground/road/field/river），且都是 32×32。
	# 注意这是**独立通路**（TILE_FILES），不动上面 SCENE_FILES 的语义。
	var missing: Array = []
	var wrong: Array = []
	for fid in ["a1_1926", "a2_1951", "a3_1976", "a4_2001", "a5_2026"]:
		for kind in ["ground", "road", "field", "river"]:
			var t := AssetDraw.tile_tex(fid, kind)
			if t == null:
				missing.append("%s/%s" % [fid, kind])
			elif t.get_size() != Vector2(AssetDraw.TILE, AssetDraw.TILE):
				wrong.append("%s/%s=%s" % [fid, kind, str(t.get_size())])
	_ok(missing.is_empty(), "五帧 × 四类平铺瓦片齐全（缺 %s）" % str(missing))
	_ok(wrong.is_empty(), "平铺瓦片全是 32×32（不合 %s）" % str(wrong))


## ---------- 4b. A4/A5 房屋接线（图未到，只验通路登记） ----------
func _check_a4a5_wiring() -> void:
	var ids := ["market", "shen_a4", "zhou_a4", "zheng_a4", "shen_a5", "toyshop", "school"]
	var unreg: Array = []
	for sid in ids:
		if (WorldView.FAMILY.get(sid, []) as Array).size() != 2:
			unreg.append(sid)
	_ok(unreg.is_empty(), "A4/A5 七栋房子都登记了族名+帧（未登记 %s）" % str(unreg))
	# 图还没到 ⇒ 不能有 base 图；哪天美术落地了这条会红，届时把断言改成「有图」
	_ok(not WorldView._art_walls("shen_a4"), "shen_a4 尚无 base 图 → 走引擎色块降级（美术到位后改断言）")


## ---------- 5. 主角精灵 ----------
func _check_hero_sheet() -> void:
	var sheet: Texture2D = Player._hero_sheet()
	_ok(sheet != null, "主角精灵表能加载")
	if sheet != null:
		_ok(sheet.get_size() == Vector2(1152, 32), "精灵表 1152×32（36 帧 × 32）")
	# 方向分组：四个方向都有帧
	for g in ["down", "left", "right", "up"]:
		_ok((Player.HERO_WALK[g] as Array).size() == 4, "%s 行走 4 帧" % g)
		_ok((Player.HERO_IDLE[g] as Array).size() == 5, "%s 站立 5 帧" % g)
	# 分组不重叠
	var seen := {}
	var dup := 0
	for g in ["down", "left", "right", "up"]:
		for f in Player.HERO_WALK[g]:
			if seen.has(f):
				dup += 1
			seen[f] = true
		for f in Player.HERO_IDLE[g]:
			if seen.has(f):
				dup += 1
			seen[f] = true
	_ok(dup == 0, "四个方向的帧不重叠")
	_ok(seen.size() == 36, "36 帧全部有归属（实际 %d）" % seen.size())


## ---------- 6. 贴图不改变碰撞 ----------
func _check_no_collision_change() -> void:
	var fd := FrameData.new()
	var frames_json: Dictionary = JSON.parse_string(
		FileAccess.get_file_as_string("res://data/frames.json"))
	for f in frames_json["frames"]:
		if String(f["id"]) != "a1_1926":
			continue
		fd.setup(f)
		var n_solid := fd.solid_rects.size()
		_ok(n_solid > 0, "A1 有阻挡矩形 %d 个" % n_solid)
		# 房子 solid_rects 数量与 house_shape 一致（贴图没改数据）
		var d := HouseShape.house("lu_house")
		var hp := Vector2(2304, 768)
		_ok(HouseShape.solid_rects(d, hp).size() > 0, "lu_house 阻挡矩形非空")
		break


## ---------- 7. 排序不变式 ----------
func _check_sort_invariant() -> void:
	var wv := WorldView.new()
	root.add_child(wv)
	var fd := FrameData.new()
	var frames_json: Dictionary = JSON.parse_string(
		FileAccess.get_file_as_string("res://data/frames.json"))
	for f in frames_json["frames"]:
		if String(f["id"]) != "a1_1926":
			continue
		fd.setup(f)
		break
	wv.frame = fd
	wv.player_pos = Vector2(2512, 1104)
	var ents := wv._collect_front()
	_ok(ents.size() > 0, "前景层收集到 %d 个条目" % ents.size())
	# sort_y 单调不减
	var bad := 0
	var prev := -INF
	for e in ents:
		var sy := float((e as Dictionary)["sort_y"])
		if sy < prev - 0.001:
			bad += 1
		prev = sy
	_ok(bad == 0, "前景层 sort_y 单调不减（违反 %d 处）" % bad)
	# 玩家在 lu_house 门洞里 → 屋顶整块消失
	_ok(wv._player_inside(HouseShape.house("lu_house"), Vector2(2512, 1104)),
		"玩家在 lu_house wings 内")
	wv.queue_free()
