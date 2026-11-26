extends SceneTree

## 探针 4：方案 B 的「场景化」到底能用哪些节点（Polygon2D 平铺 / TextureRect 平铺 / Sprite2D / y_sort）。
## 只读，不改项目文件。

func _init() -> void:
	print("PROBE4_START")

	# --- A. CanvasItem.texture_repeat 存在吗（Polygon2D 平铺的关键）---
	var poly := Polygon2D.new()
	print("POLY_HAS_TEXTURE_REPEAT=", "texture_repeat" in poly)
	print("POLY_TEXTURE_REPEAT_ENUM=", CanvasItem.TEXTURE_REPEAT_ENABLED)
	print("POLY_HAS_TEXTURE=", "texture" in poly)
	print("POLY_HAS_UV=", "uv" in poly)

	# --- B. TextureRect 的 tile 拉伸 ---
	var tr := TextureRect.new()
	print("TR_HAS_STRETCH_MODE=", "stretch_mode" in tr)
	print("TR_STRETCH_TILE_ENUM=", TextureRect.STRETCH_TILE)
	print("TR_HAS_TEXTURE_REPEAT=", "texture_repeat" in tr)

	# --- C. Sprite2D：centered / offset / region ---
	var sp := Sprite2D.new()
	print("SP_CENTERED=", sp.centered)
	sp.centered = false
	sp.offset = Vector2(0, 32)
	print("SP_OFFSET=", sp.offset, " centered=", sp.centered)
	print("SP_HAS_REGION=", "region_enabled" in sp)

	# --- D. y_sort 语义：父节点 y_sort_enabled + 子节点按 position.y 排序 ---
	var parent := Node2D.new()
	parent.y_sort_enabled = true
	print("PARENT_YSORT=", parent.y_sort_enabled)

	# --- E. Node2D 的 modulate / self_modulate（时间轴三遍色差怎么办）---
	print("NODE_MODULATE=", "modulate" in parent)
	print("NODE_SELF_MODULATE=", "self_modulate" in parent)

	# --- F. TileMapLayer 是否支持 physics（墙的碰撞要不要靠它）---
	var tml := TileMapLayer.new()
	print("TML_HAS_PHYSICS=", "enabled_physics" in tml)
	print("TML_HAS_COLLISION=", "collision_enabled" in tml)
	print("TML_COLLISION_LAYER_PROP=", "collision_layer" in tml)

	# --- G. Polygon2D 的 UV 怎么铺：uv 属性是 PackedVector2Array ---
	print("POLY_UV_TYPE=", typeof(poly.uv))

	# --- H. 有没有 EditorPlugin 相关的 scripting API（能不能做自定义编辑器面板）---
	print("HAS_EDITORINTERFACE=", ClassDB.class_exists("EditorInterface"))
	print("HAS_EDITORPLUGIN=", ClassDB.class_exists("EditorPlugin"))

	# --- I. CanvasItem 的 texture_filter / texture_repeat 默认值 ---
	print("DEFAULT_TEXTURE_REPEAT=", Node.new().texture_repeat if "texture_repeat" in Node.new() else -1)

	print("PROBE4_DONE")
	quit()
