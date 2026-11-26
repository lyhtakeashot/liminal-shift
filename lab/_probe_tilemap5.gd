extends SceneTree

## 探针 5：验证「烘焙成 .tscn / .tres 再读回」这条管线能不能通（方案 B 的地基）。
## 只读为主：写到 user:// 与 res:// 的临时路径，测完删。

func _init() -> void:
	print("PROBE5_START")

	# ---------- 1) TileSet 存 res:// ----------
	var ts := TileSet.new()
	ts.tile_size = Vector2i(32, 32)
	var src := TileSetAtlasSource.new()
	src.texture = load("res://assets/village/scene/field_tiles_l8.png")
	src.texture_region_size = Vector2i(32, 32)
	ts.add_source(src, 0)
	ts.get_source(0).create_tile(Vector2i(0, 0))
	print("TILESET_TILES=", ts.get_source(0).get_tiles_count())

	var ts_path := "res://_probe_world_tileset.tres"
	var e1 := ResourceSaver.save(ts, ts_path)
	print("SAVE_TILESET_RES_ERR=", e1)
	var back_ts := ResourceLoader.load(ts_path) as TileSet
	print("RELOAD_TILESET=", back_ts != null, " sources=", (back_ts.get_source_count() if back_ts != null else -1),
		" tiles0=", (back_ts.get_source(0).get_tiles_count() if back_ts != null else -1))
	if back_ts != null:
		var bt := back_ts.get_source(0)
		print("RELOAD_TEX=", bt.texture != null, " region=", bt.texture_region_size)

	# ---------- 2) TileMapLayer + Polygon2D + Sprite2D 打包成 .tscn 再读回 ----------
	var root := Node2D.new()
	root.name = "WorldA5"

	var tml := TileMapLayer.new()
	tml.name = "Ground"
	tml.tile_set = back_ts
	tml.set_cell(Vector2i(3, 4), 0, Vector2i(0, 0), 0)
	tml.set_cell(Vector2i(3, 5), 0, Vector2i(0, 0), 0)
	root.add_child(tml)

	var poly := Polygon2D.new()
	poly.name = "River"
	poly.texture = load("res://assets/village/scene/river_tiles_l8.png")
	poly.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	poly.polygon = PackedVector2Array([Vector2(0, 0), Vector2(640, 0), Vector2(640, 128), Vector2(0, 128)])
	poly.uv = PackedVector2Array([Vector2(0, 0), Vector2(640, 0), Vector2(640, 128), Vector2(0, 128)])
	root.add_child(poly)

	var spr := Sprite2D.new()
	spr.name = "Tree"
	spr.centered = false
	spr.texture = load("res://assets/village/scene/tree_a3.png")
	spr.offset = Vector2(0, 192)
	root.add_child(spr)

	var packed := PackedScene.new()
	var e2 := packed.pack(root)
	print("PACK_ERR=", e2)
	var tscn_path := "res://_probe_world.tscn"
	var e3 := ResourceSaver.save(packed, tscn_path)
	print("SAVE_TSCN_ERR=", e3)

	var reloaded := ResourceLoader.load(tscn_path) as PackedScene
	print("RELOAD_TSCN=", reloaded != null)
	if reloaded != null:
		var inst = reloaded.instantiate()
		print("INST_ROOT=", inst.get_class(), " children=", inst.get_child_count())
		for c in inst.get_children():
			print("  CHILD ", c.name, " class=", c.get_class())
			if c is TileMapLayer:
				var l2 := c as TileMapLayer
				print("    CELLS=", l2.get_used_cells().size())
				print("    HAS_TILESET=", l2.tile_set != null)
			if c is Polygon2D:
				var p2 := c as Polygon2D
				print("    POLY_TEX=", p2.texture != null, " repeat=", p2.texture_repeat, " pts=", p2.polygon.size())
			if c is Sprite2D:
				var s2 := c as Sprite2D
				print("    SPR_TEX=", s2.texture != null, " centered=", s2.centered)
		inst.free()

	# ---------- 3) 清理 ----------
	DirAccess.remove_absolute(ProjectSettings.globalize_path(ts_path))
	DirAccess.remove_absolute(ProjectSettings.globalize_path(tscn_path))
	print("CLEANED")

	print("PROBE5_DONE")
	quit()
