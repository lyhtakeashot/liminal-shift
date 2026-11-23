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

const TILE := 32.0

## 墙高（渲染专用，DECIDE D3 / house-spec §4.5.2）。
## 观察者在东南方向：
##   墙的**室内侧**朝南/朝东 → 这是北墙/西墙 → 画全高（= 一格）
##   墙的**室内侧**朝北/朝西 → 这是南墙/东墙 → 画半高（= 半格）
## 拆墙表（demolished）里的格 = 断墙残垣 → 半高。
## ⚠️ 只影响「画多高」，**不影响碰撞**：碰撞恒为整格 AABB（solid_rects() 不变）。
const WALL_FULL := 32.0
const WALL_HALF := 16.0

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
	# ---- A4 2001：路开始取直，粮站拆，超市在建。时间线已到，可点破「一九五七」----
	"shen_a4": {
		"蜂窝煤炉": "灶间的蜂窝煤炉还在，炉身熏得发黑。旁边立着一只液化气罐，接口上的塑料封条还没拆。",
		"账桌": "账桌上摊着一份地质勘察报告，纸还是新的。结论那一栏是钢笔字：地下有暗河，不宜大开挖。桩位一栏的坐标被铅笔改过两回，擦得纸面起了毛。",
		"保险柜": "铁皮保险柜，长边贴着东墙，柜门的漆掉了两块。柜脚底下压着半张撕剩的复写纸，蓝印子还在。",
	},
	"market": {
		"文件柜": "文件柜的玻璃门里塞着牛皮纸档案袋。最上面一袋是「土地登记表（第二联）」，前手栏印着：原业主 周氏，光绪二十六年立契。底下压着的地质勘察报告，「地下有暗河」那句被人用圆珠笔圈了两道。",
		"上磨盘": "工地铁皮围挡里头，上磨盘斜靠在砖堆上，磨眼堵着一团干水泥。盘沿凿的一圈字看得清：沈氏丰源·一九五七，字口里嵌着石灰。",
	},
	"zhou_a4": {
		"保险柜": "卧室西南角蹲着一只半人高的保险柜，黑漆起皮。钥匙插在锁孔里，没转。柜顶压着一沓裁齐的纸，纸边齐得像拿尺比着裁的。",
		"账桌": "账桌是老的，桌沿给手臂磨出一条凹。抽屉拉开，里头是空的；抽屉底板却比侧板厚出一指。",
	},
	# ---- A5 2026：铁证链。同样只写看到什么 ----
	"toyshop": {
		"招牌小字": "招牌的漆重做过，底下一行小字没重做，笔画里全是灰。凑近看是：本店由沈氏物业出租。",
		"账柜": "账柜漆成深绿，柜门上钉着一块褪色的价目表，边角翘了起来。柜台下的抽屉推到一半就卡住，露着一道缝。",
	},
	"school": {
		"「周」界碑": "围墙根嵌着半截石碑，碑面和砖面抹成一个平。字磨得只剩一个「周」，旁边那个字只留着一道竖笔。",
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


## ---- 渲染专用：墙向分类器（DECIDE D3 / house-spec §4.5.2）----
##
## 观察者在东南方向，于是：
##   墙的**室内侧**朝南/朝东 → 这个内侧面朝向观察者 → 看得见 → 画全高（32px）
##   墙的**室内侧**朝北/朝西 → 内侧面背着观察者 → 只看得到墙顶 → 画矮墙（16px）
## 即：北墙/西墙全高，东墙/南墙半高。四面画满会把整个室内盖住（§4.5.2）。
##
## ⚠️ **只影响「画多高」，绝不影响碰撞**：solid_rects() 照旧返回整格 AABB。
## ⚠️ 分类器不假设矩形：任意 wings 形状、任意 partitions、demolished 拆墙表都吃得住。
##
## 返回 [{cell: Vector2i, height: float}]（格子坐标 + 该格墙高），按格给，不合并。
## 结果按房子 id 缓存（拆墙表不会在运行时变）。
static var _wall_cache: Dictionary = {}

const WALL_CLASS_FULL := 1
const WALL_CLASS_HALF := 2
const WALL_CLASS_UNKNOWN := 0


static func wall_render_cells(data: Dictionary, pos: Vector2) -> Array:
	var sid := String(data.get("id", ""))
	var cells: Array = _wall_cache.get(sid, [])
	if cells.is_empty():
		cells = _classify_walls(data)
		_wall_cache[sid] = cells
	var out: Array = []
	for c in cells:
		var cd: Dictionary = c
		var cell: Vector2i = cd["cell"]
		out.append({
			"cell": cell,
			"rect": Rect2(
				pos.x + float(cell.x) * TILE,
				pos.y + float(cell.y) * TILE,
				TILE, TILE),
			"height": float(cd["height"]),
		})
	return out


## 逐格判墙向 → 每格墙高。
## ⚠️ 坐标系：格子坐标是**绝对格坐标**（与 lot / wings / demolished 一致，
##    不是 grid_of() 返回数组里的相对下标）。lot 不从 (0,0) 起时两者会差一截。
static func _classify_walls(data: Dictionary) -> Array:
	var lot: Array = data.get("lot", [0, 0, 0, 0])
	var x0 := int(lot[0])
	var y0 := int(lot[1])
	var grid := grid_of(data)

	var interior := {}
	var walls := {}
	for j in grid.size():
		var row := String(grid[j])
		for i in row.length():
			var c := Vector2i(x0 + i, y0 + j)
			if row[i] == ".":
				interior[c] = true
			elif row[i] == "#":
				walls[c] = true

	# 第一步：直接判 —— 看这格墙的哪一侧挨着室内
	var cls := {}
	for c in walls.keys():
		cls[c] = _wall_class_direct(c, interior)

	# 第二步：角上的格子（四邻都不是室内）继承相邻墙格。
	# 「有全高就全高」是物理直觉：隔断的南端头朝着观察者 → 全高。
	for _pass in 6:
		var changed := false
		for c in walls.keys():
			if int(cls[c]) != WALL_CLASS_UNKNOWN:
				continue
			var v := _wall_class_inherit(c, walls, cls)
			if v != WALL_CLASS_UNKNOWN:
				cls[c] = v
				changed = true
		if not changed:
			break

	# 第三步：demolished 拆墙表 = 拆剩的残垣 → 半高（数据说墙已拆，只剩墙根）
	for d in data.get("demolished", []):
		var da: Array = d
		var c2 := Vector2i(int(da[0]), int(da[1]))
		if walls.has(c2):
			cls[c2] = WALL_CLASS_HALF

	var out: Array = []
	for c in walls.keys():
		var k := int(cls[c])
		if k == WALL_CLASS_UNKNOWN:
			k = WALL_CLASS_FULL
		out.append({
			"cell": c,
			"height": WALL_FULL if k == WALL_CLASS_FULL else WALL_HALF,
		})
	return out


## 室内在东/南 → 内侧面朝东南 → 全高；室内在北/西 → 半高。
static func _wall_class_direct(c: Vector2i, interior: Dictionary) -> int:
	if interior.has(c + Vector2i(0, 1)) or interior.has(c + Vector2i(1, 0)):
		return WALL_CLASS_FULL
	if interior.has(c + Vector2i(0, -1)) or interior.has(c + Vector2i(-1, 0)):
		return WALL_CLASS_HALF
	return WALL_CLASS_UNKNOWN


## 角格继承：任一相邻墙格是全高 → 全高；否则任一半高 → 半高。
static func _wall_class_inherit(c: Vector2i, walls: Dictionary, cls: Dictionary) -> int:
	var has_full := false
	var has_half := false
	for d in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
		var dd: Vector2i = d
		if not walls.has(dd):
			continue
		var v := int(cls[dd])
		if v == WALL_CLASS_FULL:
			has_full = true
		elif v == WALL_CLASS_HALF:
			has_half = true
	if has_full:
		return WALL_CLASS_FULL
	if has_half:
		return WALL_CLASS_HALF
	return WALL_CLASS_UNKNOWN


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
			"reach": 68.0,
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