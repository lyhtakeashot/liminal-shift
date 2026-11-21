"""A4 2001 郑家 · 外来户二层小楼：从 lu_a2 派生，补 A4 陆家地块断档。

口径（用户 m01739–m01765 拍板）：
  陆家老宅 1926 后地契归沈家，1951 空屋，1976 塌成废墟（lu_a3），
  2001 这块地盖起一栋先富起来的普通人家瓷砖外墙二层小楼——住户完全不知道
  脚下曾是陆家老宅，呼应全篇「没人知道」主题。
  图上画一层平面（二层同轮廓），房间现代化：主卧/客厅/厨卫。
  结构（lot/wings/partitions/doors/gate）照抄 lu_a2 保证 check_all 合法。
幂等：存在则替换，否则追加。
"""
import json
import os
from gen_all_houses import build_grid

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")

with open(DATA, encoding="utf-8") as f:
    houses = json.load(f)

src = next(h for h in houses if h["id"] == "lu_a2")

a4 = {
    "id": "zheng_a4",
    "name": "郑家 · 外来户二层小楼 · A4 2001（不知情）",
    "lot": list(src["lot"]),
    "wings": [list(w) for w in src["wings"]],
    "partitions": [list(p) for p in src["partitions"]],
    "doors": [list(d) for d in src["doors"]],
    "gate": [list(g) for g in src["gate"]],
    "rooms": [
        [1, 1, 4, 6, "主卧", "bed"],
        [6, 1, 9, 6, "客厅", "hall"],
        [11, 1, 13, 3, "卫生间", "toilet"],
        [11, 5, 13, 6, "厨房", "kitchen"],
    ],
    "furniture": [
        # 主卧 x1..4,y1..6（避开门(5,5)左邻 (4,5)）
        {"name": "大床", "short": "大床", "rect": [1, 1, 2, 2], "zone": "house",
         "note": "2001 新买的席梦思大床"},
        {"name": "衣柜", "short": "衣柜", "rect": [3, 1, 1, 2], "zone": "house",
         "note": "推拉门衣柜 · 瓷砖外墙小楼的新家具"},
        {"name": "梳妆台", "short": "梳妆台", "rect": [1, 4, 1, 1], "zone": "house",
         "note": "主卧一角"},
        {"name": "电视柜", "short": "电视柜", "rect": [3, 3, 1, 1], "zone": "house",
         "note": "卧室里的彩电"},
        # 客厅 x6..9,y1..6（避开 (9,2)门(10,2)邻格/(6,5)门(5,5)邻格/(9,5)门(10,5)邻格/(6,6)院门邻格）
        {"name": "沙发", "short": "沙发", "rect": [6, 1, 2, 1], "zone": "house",
         "note": "客厅 · 人造革沙发"},
        {"name": "茶几", "short": "茶几", "rect": [7, 2, 1, 1], "zone": "house",
         "note": "沙发前"},
        {"name": "彩电柜", "short": "彩电柜", "rect": [8, 2, 1, 1], "zone": "house",
         "note": "客厅彩电"},
        {"name": "饭桌", "short": "饭桌", "rect": [7, 3, 2, 1], "zone": "house",
         "note": "一家人吃饭的圆桌"},
        {"name": "空调", "short": "空调", "rect": [8, 5, 1, 1], "zone": "house",
         "note": "柜式空调 · 2001 年的体面"},
        # 卫生间 x11..13,y1..3（避开门(10,2)右邻 (11,2)）
        {"name": "坐便器", "short": "坐便器", "rect": [12, 1, 1, 1], "zone": "house",
         "note": "水冲坐便 · 新式卫生间"},
        {"name": "洗手盆", "short": "洗手盆", "rect": [12, 2, 1, 1], "zone": "house",
         "note": "瓷砖贴面"},
        {"name": "淋浴", "short": "淋浴", "rect": [13, 1, 1, 2], "zone": "house",
         "note": "燃气热水器 · 不用再烧水"},
        # 厨房 x11..13,y5..6（避开门(10,5)右邻 (11,5)）
        {"name": "煤气灶", "short": "煤气灶", "rect": [12, 5, 1, 1], "zone": "house",
         "note": "液化气灶台"},
        {"name": "橱柜", "short": "橱柜", "rect": [13, 5, 1, 2], "zone": "house",
         "note": "整体橱柜 · 现代厨房"},
        {"name": "冰箱", "short": "冰箱", "rect": [11, 6, 1, 1], "zone": "house",
         "note": "双开门冰箱 · 2001 年新添"},
        {"name": "水池", "short": "水池", "rect": [12, 6, 1, 1], "zone": "house",
         "note": "自来水水池"},
        # 院子 x15..19
        {"name": "摩托车", "short": "摩托", "rect": [16, 5, 2, 1], "zone": "yard",
         "note": "院里停的摩托 · 先富起来的人家"},
        {"name": "晾衣架", "short": "晾衣架", "rect": [17, 2, 1, 1], "zone": "yard",
         "note": "院子晾晒"},
        {"name": "花坛", "short": "花坛", "rect": [18, 7, 2, 1], "zone": "yard",
         "note": "院角花坛 · 不知道脚下埋着什么"},
    ],
    "clue": [
        "瓷砖外墙的二层小楼 · 2001 年新起的房子，住进来的人家完全不知道这块地曾是陆家老宅。",
        "客厅/主卧/卫生间都是新式的 · 陆家的痕迹一点不剩，房子从地基上就换了人家。",
    ],
    "story": "陆家老宅 1926 年后地契归沈家，1951 年空屋，1976 年塌成废墟。到 2001 年，这块地上盖起一栋先富起来的普通人家的瓷砖外墙二层小楼：席梦思、彩电、柜式空调、水冲卫生间，一样不少。这家人不知道脚下曾是陆家老宅，也不知道二十年前这里的残墙断井——他们只是买下了沈家手里的一块地。全篇「没人知道」的主题，在这栋房子上落到了最平常的一户人家。",
    "note": "屋本体 15×8、占地 19×9，与 A1/A2/A3 陆家同址同轮廓——1976 还是废墟（lu_a3），2001 已起新房。图上画一层平面，二层同轮廓（2001 农村/镇上常见的瓷砖二层小楼）；结构照抄 lu_a2 仅为校验布局合法，家具与叙事全新。住户对陆家旧事和老井一无所知，不设陆家线索格。",
}

for f in a4["furniture"]:
    f["yard_building"] = False
    f.setdefault("clue", False)
    f.setdefault("zone", "house")
    f.setdefault("short", f["name"])

# 自检 1：家具不重叠、四邻禁堵门/院门
occupied = set()
for f in a4["furniture"]:
    x, y, w, h = f["rect"]
    for i in range(x, x + w):
        for j in range(y, y + h):
            assert (i, j) not in occupied, f"家具重叠 ({i},{j})"
            occupied.add((i, j))
for d in [tuple(d) for d in a4["doors"]] + [tuple(g) for g in a4["gate"]]:
    x, y = d
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        assert (x + dx, y + dy) not in occupied, f"堵门：家具占门 {d} 邻格 ({x+dx},{y+dy})"

# 自检 2：家具不能压墙 #/门 D/院门 G
grid = build_grid(a4)
for f in a4["furniture"]:
    x, y, w, h = f["rect"]
    for i in range(x, x + w):
        for j in range(y, y + h):
            assert grid[j][i] in (".", " "), f"家具压墙/门：{f['name']} ({i},{j}) = {grid[j][i]}"

for i, h in enumerate(houses):
    if h["id"] == "zheng_a4":
        houses[i] = a4
        break
else:
    houses.append(a4)

with open(DATA, "w", encoding="utf-8") as f:
    json.dump(houses, f, ensure_ascii=False, indent=2)

print(f"zheng_a4 written: houses {len(houses)} lot {a4['lot']} rooms {len(a4['rooms'])} furniture {len(a4['furniture'])}")
