"""A3 1976 周家长工房：从 zhou_a2 派生，补周家线断档。

结构（lot/wings/partitions/doors/gate/rooms）照抄 A2，只改家具与叙事。
A3 1976：周有田 1927–1951 记账二十四年，1976 年他已老/不在，长工房空了，
往来账仍藏在这里（A5 才出土），笔记/旧账桌/长工遗物留一点痕迹。
幂等：存在则替换，否则追加。
"""
import json
import os
from gen_all_houses import build_grid

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")

with open(DATA, encoding="utf-8") as f:
    houses = json.load(f)

src = next(h for h in houses if h["id"] == "zhou_a2")

a3 = {
    "id": "zhou_a3",
    "name": "周家 · 长工房 · A3 1976 · 帮凶方（已无人）",
    "lot": list(src["lot"]),
    "wings": [list(w) for w in src["wings"]],
    "partitions": [list(p) for p in src["partitions"]],
    "doors": [list(d) for d in src["doors"]],
    "gate": [list(g) for g in src["gate"]],
    "rooms": [list(r) for r in src["rooms"]],
    "furniture": [
        {"name": "旧木床", "short": "木床", "rect": [1, 1, 1, 2], "zone": "house",
         "note": "床架还在 · 草席烂成一堆"},
        {"name": "账桌", "short": "账桌", "rect": [2, 1, 2, 1], "zone": "house", "clue": True,
         "note": "周有田的账桌 · 抽屉夹层藏着往来账（A5 才出土）"},
        {"name": "条凳", "short": "条凳", "rect": [3, 2, 1, 1], "zone": "house",
         "note": "账桌前 · 坐了二十四年的那条凳"},
        {"name": "衣柜", "short": "衣柜", "rect": [1, 3, 1, 1], "zone": "house",
         "note": "搬不走的旧衣柜 · 空了"},
        {"name": "土坯灶台", "short": "灶台", "rect": [5, 1, 2, 1], "zone": "house",
         "note": "砌死在墙里 · 灶膛早凉了"},
        {"name": "旧木箱", "short": "木箱", "rect": [8, 2, 1, 1], "zone": "yard",
         "note": "长工遗物 · 里头没值钱东西"},
        {"name": "水缸", "short": "水缸", "rect": [9, 4, 1, 1], "zone": "yard",
         "note": "缸沿豁了口 · 院子角落"},
        {"name": "茅房", "short": "茅房", "rect": [9, 1, 3, 2], "zone": "yard",
         "note": "屋外独立茅房 · 塌了半边"},
    ],
    "clue": [
        "账桌还在，人没了 · 周有田的往来账压在抽屉夹层里，要等到 2026 才重见天日",
        "灶冷了，木床空了 · 长工房和陆家一样，只剩搬不走的物件",
    ],
    "story": "周有田 1927–1951 给沈家记了二十四年账，1951 年土改时照常记账，把「婶」改成「先生」。1976 年这间长工房已经没人住了，往来账还藏账桌夹层——它要再等五十年，到 A5 才被翻出来，完成陆家勒索线的反转。",
    "note": "屋本体 8×5、占地 12×6（含东侧院子），与 A1/A2 周家同尺寸同结构——同一栋长工房，1976 年已空。结构照抄 A2，只换家具与叙事；往来账位置维持夹层待定，不提前出土。",
}

# 生成器按 f["yard_building"] 直接索引，所有家具都要带这个 key；茅房才为 True
for f in a3["furniture"]:
    f["yard_building"] = f["name"] == "茅房"
    f.setdefault("clue", False)
    f.setdefault("zone", "house")
    f.setdefault("short", f["name"])

# 自检 1：门/院门四邻格禁止家具
occupied = set()
for f in a3["furniture"]:
    x, y, w, h = f["rect"]
    for i in range(x, x + w):
        for j in range(y, y + h):
            assert (i, j) not in occupied, f"家具重叠 ({i},{j})"
            occupied.add((i, j))
for d in [tuple(d) for d in a3["doors"]] + [tuple(g) for g in a3["gate"]]:
    x, y = d
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        assert (x + dx, y + dy) not in occupied, f"堵门：家具占门 {d} 邻格 ({x+dx},{y+dy})"

# 自检 2：家具不能压墙 #/门 D/院门 G
grid = build_grid(a3)
for f in a3["furniture"]:
    x, y, w, h = f["rect"]
    for i in range(x, x + w):
        for j in range(y, y + h):
            assert grid[j][i] in (".", " "), f"家具压墙/门：{f['name']} ({i},{j}) = {grid[j][i]}"

for i, h in enumerate(houses):
    if h["id"] == "zhou_a3":
        houses[i] = a3
        break
else:
    houses.append(a3)

with open(DATA, "w", encoding="utf-8") as f:
    json.dump(houses, f, ensure_ascii=False, indent=2)

print(f"zhou_a3 written: houses {len(houses)} lot {a3['lot']} rooms {len(a3['rooms'])} furniture {len(a3['furniture'])}")
