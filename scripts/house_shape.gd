extends RefCounted

## 房子的数据中间层（BUILD-A1 §4.2）：
## 读 _ref/houses/houses_data.json，把一栋房子展开成：
##   - grid_of()      抄 gen_all_houses.py 的 build_grid()，出 '#'/'.'/'D'/'G'/' ' 字符网格
##   - solid_rects()  墙体（'#' 格）→ 世界坐标 Rect2 列表；门洞（D/G）留空、lot 边界不做阻挡
##   - hotspots()     furniture 里 clue=true 的家具 → 检视点（落在家具矩形中心，reach 默认 34）
## 不引 physics。碰撞继续走 frame_data.gd 的纯 AABB。
##
## houses_data.json 在 _ref/ 下（项目根目录内，属 res://），用 FileAccess 直接读
## （BUILD-A1 §4.2 办法 A：一份真相源；将来配 Web 导出时把它加进 include_filter）。

const TILE := 16.0

const DATA_PATH := "res://_ref/houses/houses_data.json"

# ---- 配色（与 _ref/houses/gen_all_houses.py 的 C 表一致，占位块用）----
const WALL_COLOR := Color("#8c6b4a")
const WALL_TOP := Color("#c9a878")
const DOOR_COLOR := Color("#e0b25a")
const GATE_COLOR := Color("#9a6a3a")
const LOT_OUTLINE := Color("#a8905a")
const YARD_COLOR := Color("#3b3a2e")
const FURN_COLOR := Color("#c8b48f")
const FURN_EDGE := Color("#e8d7b2")
const CLUE_COLOR := Color("#d98b45")
const ROOM_COLORS := {
	"bed": Color("#9c8468"), "hall": Color("#cbb997"), "store": Color("#8d9a6f"),
	"kitchen": Color("#bdd0b0"), "account": Color("#a8c0d0"), "yard": Color("#3b3a2e"),
	"shop": Color("#b99aa6"), "class": Color("#9dbacd"), "mill": Color("#b5a878"),
	"toilet": Color("#9aa8a8"),
}

## A1 家具检视文本。只写看到什么（story.md「写作纪律」，BUILD-A1 §5）：
## 磨坊没有暗龛；账桌摆假《水簿》；石磨上的字不点破「一九五七」（那是 A5 回读的线，A1 不能剧透）。
## key = 房子 id；value = 家具名 → 文本。缺省退回中性占位描述。
const CLUE_TEXTS := {
	"mill_a1": {
		"账桌": "一本硬壳账簿摊在柜台上。纸很好，字极整齐。最后一页写着：收粮 三石。",
		"石磨": "石磨靠着大厅西墙。上磨盘边缘凿着一圈字，笔画被谷粒磨得发亮，看不真切。",
		"老井": "院子最南边压着一块木板，木板上又盖了一层土。踩上去是空的。",
	},
	"lu_house": {
		"旧木箱": "一只旧木箱。箱角包着铜皮，盖子没上锁，留着常开常合的手印。",
	},
	"zhou_house": {
		"小桌": "一张小桌贴着北墙。桌上一只粗碗，水还是满的。抽屉留着一道缝，里面像是纸角。",
	},
	"mill_a2": {
		"墙基暗龛": "东数第三块砖，灰缝是新的。按了一下，砖往里陷了半分。",
		"账桌": "同一本账簿，续了二十五年。字还是那么整齐。二月那页多出一行：未告陆家。",
		"石磨": "石磨靠大厅西墙。上磨盘刻着一行字：沈氏丰源。底下一行小字，被谷粒磨得看不太清。",
		"老井": "院子最南边那块地面比别处低半寸，插着一根界桩。桩上的字新刻的。",
	},
	"shen_a2": {
		"书桌": "书桌上摊着一本账，墨迹还是湿的。桌角压着一把算盘，有一颗子拨了一半。",
	},
	"zhou_a2": {
		"小桌": "小桌贴北墙，抽屉半开，露出一角纸，边都卷了。",
	},
	# ---- A3 1976：粮站改建那年。只写看到什么，不写意味着什么 ----
	"mill_a3": {
		"墙基暗龛": "墙基里凿出一个方龛，空的。龛底往下陷了半寸，是一圈油布压出来的印子。",
		"账桌": "同一本账簿还摊在桌上。纸发脆了，边角卷起来。最后几页空着，一个字也没有。",
		"弃置石磨": "上磨盘卸下来靠在晒谷场角落，边缘凿着一圈字：沈氏丰源·一九五七。底下一行小字磨平了。",
		"老井": "晒谷场正中那片地面比周围低一点，铺着水泥。边上一道没抹完的缝，能看见底下的石板角。",
		"水泥封层": "水泥是三层。最上一层颜色新，底下两层缝里嵌着碎石灰。缝隙走向朝着场子西南。",
	},
	"shen_a3": {
		"蜂窝煤炉": "灶间角落摆着蜂窝煤炉，炉膛里还有半块没烧透的煤。煤饼上印着「县煤建」三个字。",
	},
	"lu_a3": {
		"堂屋地基痕迹": "荒草里有一圈比周围硬的地，踩上去是夯过的。四边成直角，中间空着。",
	},
	"zhou_a3": {
		"账桌": "一张账桌，桌角磨圆了。桌下抽屉被抽走了一只，只剩右边的。",
	},
}

static var _by_id: Dictionary = {}


## 读 houses_data.json → {id: house}，缓存。
static func load_all() -> Dictionary:
	if not _by_id.is_empty():
		return _by_id
	var f := FileAccess.open(DATA_PATH, FileAccess.READ)
	if f == null:
		push_error("读不到房子数据：%s" % DATA_PATH)
		return {}
	var raw := f.get_as_text()
	f.close()
	var parsed: Variant = JSON.parse_string(raw)
	if parsed == null or typeof(parsed) != TYPE_ARRAY:
		push_error("房子数据不是合法 JSON 数组：%s" % DATA_PATH)
		return {}
	for hs in parsed:
		var hd: Dictionary = hs
		_by_id[String(hd.get("id", ""))] = hd
	return _by_id


static func house(id: String) -> Dictionary:
	return load_all().get(id, {})


## 抄 gen_all_houses.py 的 build_grid()：lot 范围内的字符网格。
## '#' 墙 / '.' 室内地面 / 'D' 房门 / 'G' 院门 / ' ' 院子空地。
static func grid_of(data: Dictionary) -> Array:
	var lot: Array = data.get("lot", [0, 0, 0, 0])
	var x0 := int(lot[0])
	var y0 := int(lot[1])
	var x1 := int(lot[2])
	var y1 := int(lot[3])

	var interior := {}
	for w in data.get("wings", []):
		var wx := int(w[0])
		var wy := int(w[1])
		var ww := int(w[2])
		var wh := int(w[3])
		for j in range(wy + 1, wy + wh - 1):
			for i in range(wx + 1, wx + ww - 1):
				interior[Vector2i(i, j)] = true

	# 「四邻有室内格」= 墙，墙角天然缺一格（gen_all_houses.py 已验证的规则）
	var is_wall := func(i: int, j: int) -> bool:
		if interior.has(Vector2i(i, j)):
			return false
		for d in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			if interior.has(Vector2i(i + d.x, j + d.y)):
				return true
		return false

	var part := {}
	for p in data.get("partitions", []):
		var px1 := int(p[0])
		var py1 := int(p[1])
		var px2 := int(p[2])
		var py2 := int(p[3])
		if px1 == px2:
			for j in range(min(py1, py2), max(py1, py2) + 1):
				part[Vector2i(px1, j)] = true
		else:
			for i in range(min(px1, px2), max(px1, px2) + 1):
				part[Vector2i(i, py1)] = true

	var dset := {}
	for d in data.get("doors", []):
		dset[Vector2i(int(d[0]), int(d[1]))] = true
	var gset := {}
	for g in data.get("gate", []):
		gset[Vector2i(int(g[0]), int(g[1]))] = true

	var rows: Array = []
	for j in range(y0, y1 + 1):
		var row := ""
		for i in range(x0, x1 + 1):
			var c := Vector2i(i, j)
			if gset.has(c):
				row += "G"
			elif dset.has(c):
				row += "D"
			elif part.has(c) or is_wall.call(i, j):
				row += "#"
			elif interior.has(c):
				row += "."
			else:
				row += " "
		rows.append(row)
	return rows


## 墙体 → 世界坐标 Rect2 列表（逐格；门洞处无矩形；lot 边界不做阻挡）。
## pos = lot 左上角在世界里的像素坐标。
static func solid_rects(data: Dictionary, pos: Vector2) -> Array:
	var lot: Array = data.get("lot", [0, 0, 0, 0])
	var x0 := int(lot[0])
	var y0 := int(lot[1])
	var grid := grid_of(data)
	var out: Array = []
	for j in grid.size():
		var row := String(grid[j])
		for i in row.length():
			if row[i] == "#":
				out.append(Rect2(
					pos.x + float(x0 + i) * TILE,
					pos.y + float(y0 + j) * TILE,
					TILE, TILE))
	return out


## a) solid_rects() 只返回墙（'#'）→ 碰撞用
## b) door_rects()  返回门洞格（'D'/'G'）→ 只画颜色、不参与碰撞
static func door_rects(data: Dictionary, pos: Vector2) -> Array:
	var lot: Array = data.get("lot", [0, 0, 0, 0])
	var x0 := int(lot[0])
	var y0 := int(lot[1])
	var grid := grid_of(data)
	var out: Array = []
	for j in grid.size():
		var row := String(grid[j])
		for i in row.length():
			var ch := row[i]
			if ch == "D" or ch == "G":
				out.append({
					"rect": Rect2(
						pos.x + float(x0 + i) * TILE,
						pos.y + float(y0 + j) * TILE,
						TILE, TILE),
					"gate": ch == "G",
				})
	return out


## furniture 里 clue=true 的 → 检视点（家具矩形中心，reach 34）。
## ⚠️ 只生成**落在房子 lot 内**的家具。lot 外的 clue 家具（如磨坊数据里的「老井」，
## rect [6,10] 已在 lot 下界之外）属于**世界级地标**，由 frames.json 的 hotspots 手写管理，
## 否则会和手写的同名检视点重复（2026-11-20 实测 A1/A2 各出现两个「老井」）。
static func hotspots(data: Dictionary, pos: Vector2) -> Array:
	var texts: Dictionary = CLUE_TEXTS.get(String(data.get("id", "")), {})
	var lot: Array = data.get("lot", [0, 0, 0, 0])
	var out: Array = []
	for f in data.get("furniture", []):
		var fd: Dictionary = f
		if not bool(fd.get("clue", false)):
			continue
		var r: Array = fd.get("rect", [0, 0, 1, 1])
		# 家具矩形必须整个落在 lot 格范围内（lot = [x0,y0,x1,y1]，含两端）
		if int(r[0]) < int(lot[0]) or int(r[1]) < int(lot[1]) \
				or int(r[0]) + int(r[2]) - 1 > int(lot[2]) \
				or int(r[1]) + int(r[3]) - 1 > int(lot[3]):
			continue
		var cx := pos.x + (float(r[0]) + float(r[2]) * 0.5) * TILE
		var cy := pos.y + (float(r[1]) + float(r[3]) * 0.5) * TILE
		var name := String(fd.get("name", "家具"))
		# 与手写地标同名时加房子前缀，避免玩家在 A1/A2 看到两条同名「老井」
		# （磨坊数据里的「老井」是磨坊院内的井位，不是村中那口老井）
		var title := name
		if name == "老井":
			title = "%s · 院里" % String(data.get("name", "")).split("·")[0].strip_edges()
		out.append({
			"pos": Vector2(cx, cy),
			"title": title,
			"text": String(texts.get(name, "「%s」立在这里。" % name)),
			"reach": 34.0,
		})
	return out


## 渲染辅助：lot 矩形（世界坐标）。
static func lot_rect(data: Dictionary, pos: Vector2) -> Rect2:
	var lot: Array = data.get("lot", [0, 0, 0, 0])
	return Rect2(pos.x, pos.y,
		float(lot[2] - lot[0] + 1) * TILE, float(lot[3] - lot[1] + 1) * TILE)


## 渲染辅助：房间矩形列表（每项 {rect, color_key, name}）。
static func room_rects(data: Dictionary, pos: Vector2) -> Array:
	var out: Array = []
	for room in data.get("rooms", []):
		var r: Array = room
		var rx0 := int(r[0])
		var ry0 := int(r[1])
		var rx1 := int(r[2])
		var ry1 := int(r[3])
		var ck := String(r[5]) if r.size() > 5 else "hall"
		out.append({
			"rect": Rect2(
				pos.x + float(rx0) * TILE, pos.y + float(ry0) * TILE,
				float(rx1 - rx0 + 1) * TILE, float(ry1 - ry0 + 1) * TILE),
			"color_key": ck,
			"name": String(r[4]),
		})
	return out


## 渲染辅助：家具矩形列表（每项 {rect, name, clue}）。
static func furniture_rects(data: Dictionary, pos: Vector2) -> Array:
	var out: Array = []
	for f in data.get("furniture", []):
		var fd: Dictionary = f
		var r: Array = fd.get("rect", [0, 0, 1, 1])
		out.append({
			"rect": Rect2(
				pos.x + float(r[0]) * TILE, pos.y + float(r[1]) * TILE,
				float(r[2]) * TILE, float(r[3]) * TILE),
			"name": String(fd.get("short", fd.get("name", ""))),
			"clue": bool(fd.get("clue", false)),
		})
	return out