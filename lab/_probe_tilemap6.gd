extends SceneTree

## 探针 6：确认 PackedScene.pack() 的 owner 规则（子节点必须 owner = root 才会被打包）。
## 只读为主：临时文件测完即删。

func _init() -> void:
	print("PROBE6_START")

	var ts := TileSet.new()
	ts.tile_size = Vector2i(32, 32)
	var src := TileSetAtlasSource.new()
	src.texture = load("res://assets/village/scene/field_tiles_l8.png")
	src.texture_region_size = Vector2i(32, 32)
	ts.add_source(src, 0)
	ts.get_source(0).create_tile(Vector2i(0, 0))
	ResourceSaver.save(ts, "res://_probe_tileset.tres")
	var back_ts := ResourceLoader.load("res://_probe_tileset.tres") as TileSet

	var root := Node2D.new()
	root.name = "WorldA5"

	var tml := TileMapLayer.new()
	tml.name = "Ground"
	tml.tile_set = back_ts
	tml.set_cell(Vector2i(3, 4), 0, Vector2i(0, 0), 0)
	root.add_child(tml)

	var poly := Polygon2D.new()
	poly.name = "River"
	poly.texture = load("res://assets/village/scene/river_tiles_l8.png")
	poly.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	poly.polygon = PackedVector2Array([Vector2(0, 0), Vector2(640, 0), Vector2(640, 128), Vector2(0, 128)])
	poly.uv = PackedVector2Array([Vector2(0, 0), Vector2(640, 0), Vector2(640, 128), Vector2(0, 128)])
	root.add_child(poly)

	# 关键：设 owner
	for c in root.get_children():
		c.owner = root

	var packed := PackedScene.new()
	print("PACK_ERR=", packed.pack(root))
	ResourceSaver.save(packed, "res://_probe_world.tscn")

	var reloaded := ResourceLoader.load("res://_probe_world.tscn") as PackedScene
	var inst = reloaded.instantiate()
	print("INST_ROOT=", inst.get_class(), " children=", inst.get_child_count())
	for c in inst.get_children():
		print("  CHILD ", c.name, " class=", c.get_class())
		if c is TileMapLayer:
			var l2 := c as TileMapLayer
			print("    CELLS=", l2.get_used_cells().size(), " HAS_TILESET=", l2.tile_set != null)
		if c is Polygon2D:
			var p2 := c as Polygon2D
			print("    POLY_TEX=", p2.texture != null, " repeat=", p2.texture_repeat, " pts=", p2.polygon.size())
	inst.free()

	DirAccess.remove_absolute(ProjectSettings.globalize_path("res://_probe_tileset.tres"))
	DirAccess.remove_absolute(ProjectSettings.globalize_path("res://_probe_world.tscn"))
	print("CLEANED")
	print("PROBE6_DONE")
	quit()
