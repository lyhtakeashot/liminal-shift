"""A4 2001 郑家 · 外来户二层小楼：独立设计的一层平面（不再照抄 lu_a2）。

口径（用户 2026-11-21 拍板）：
  - 平面结构独立设计：2001 新建瓷砖二层小楼，一层不再是 1926 陆家老宅的
    三竖隔墙格局；「结构照抄 lu_a2 仅为校验合法」的说法作废。
  - 精调重点：平面结构合理性 + 家具摆放与密度；「不知情」主题叙事保持不变。
  - 一层六空间，堂屋为枢纽：主卧 / 次卧 / 堂屋(客餐一体) / 楼梯间 / 卫生间 / 厨房。
  - 新增楼梯间——二层小楼一层必须有楼梯，旧版（照抄老宅平房格局）完全缺失。
  - 门位：每间房都直接开向堂屋；院门在堂屋正南，入宅即堂屋，符合「堂屋当门面」。

网格：lot 20×13，wing [0,0,15,11] → 室内 x=1..13 / y=1..9，院子 x=15..19。
幂等：存在则替换，否则追加。
预览：MCS_PREVIEW=1 只出预览图到 lab/，不写 houses_data.json。
"""
import json
import os
from gen_all_houses import build_grid, render

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")
PREVIEW = os.environ.get("MCS_PREVIEW") == "1"

with open(DATA, encoding="utf-8") as f:
    houses = json.load(f)

a4 = {
    "id": "zheng_a4",
    "name": "郑家 · 外来户二层小楼 · A4 2001（不知情）",
    "lot": [0, 0, 19, 12],
    "wings": [[0, 0, 15, 11]],
    # 独立设计的隔墙：
    #   x=4 / x=10 两条竖墙分西-中-东三带；
    #   y=5 西段把西带分成主卧/次卧；
    #   y=4 / y=7 东段把东带分成楼梯间/卫生间/厨房。
    "partitions": [
        [4, 1, 4, 9],
        [10, 1, 10, 9],
        [1, 5, 3, 5],
        [11, 4, 13, 4],
        [11, 7, 13, 7],
    ],
    # 每间房都开向堂屋；院门在堂屋正南（7,10）
    "doors": [[4, 2], [4, 7], [10, 2], [10, 5], [10, 8]],
    "gate": [[7, 10]],
    "rooms": [
        [1, 1, 3, 4, "主卧", "bed"],
        [1, 6, 3, 9, "次卧", "bed"],
        [5, 1, 9, 9, "堂屋", "hall"],
        [11, 1, 13, 3, "楼梯间", "store"],
        [11, 5, 13, 6, "卫生间", "toilet"],
        [11, 8, 13, 9, "厨房", "kitchen"],
    ],
    "furniture": [
        # ── 主卧 x1..3,y1..4 ──
        {"name": "大床", "short": "大床", "rect": [1, 1, 2, 2], "zone": "house",
         "note": "2001 新买的席梦思双人床"},
        {"name": "衣柜", "short": "衣柜", "rect": [3, 3, 1, 2], "zone": "house",
         "note": "推拉门衣柜 · 让开 (3,2) 门口"},
        {"name": "梳妆台", "short": "梳妆台", "rect": [1, 4, 1, 1], "zone": "house",
         "note": "主卧南墙下 · 靠窗梳妆"},
        {"name": "电视柜", "short": "电视柜", "rect": [2, 4, 1, 1], "zone": "house",
         "note": "主卧南墙下 · 卧室里的彩电"},
        # ── 次卧 x1..3,y6..9 ──
        {"name": "单人床", "short": "单人床", "rect": [1, 6, 2, 1], "zone": "house",
         "note": "横向贴北墙 · 客房/孩子房"},
        {"name": "椅子", "short": "椅", "rect": [1, 8, 1, 1], "zone": "house",
         "note": "次卧 · 与书桌严格对调位置（椅子仍 1 格）"},
        {"name": "衣柜", "short": "衣柜", "rect": [3, 8, 1, 2], "zone": "house",
         "note": "次卧衣柜"},
        {"name": "书桌", "short": "书桌", "rect": [1, 9, 2, 1], "zone": "house",
         "note": "次卧 · 与椅子严格对调位置 · 贴南墙"},
        # ── 堂屋 x5..9,y1..9（客餐一体，全宅枢纽）──
        {"name": "饭桌", "short": "饭桌", "rect": [6, 2, 2, 2], "zone": "house",
         "note": "一家人吃饭的圆桌"},
        {"name": "凳", "short": "凳", "rect": [5, 3, 1, 1], "zone": "house",
         "note": "饭桌旁 · 让开 (5,2) 主卧门口"},
        {"name": "凳", "short": "凳", "rect": [8, 2, 1, 1], "zone": "house",
         "note": "饭桌旁"},
        {"name": "茶水柜", "short": "茶水柜", "rect": [8, 3, 1, 1], "zone": "house",
         "note": "堂屋待客"},
        {"name": "沙发", "short": "沙发", "rect": [5, 5, 2, 1], "zone": "house",
         "note": "人造革沙发"},
        {"name": "茶几", "short": "茶几", "rect": [6, 6, 1, 1], "zone": "house",
         "note": "沙发前"},
        {"name": "彩电柜", "short": "彩电柜", "rect": [8, 5, 1, 1], "zone": "house",
         "note": "客厅彩电 · 让开 (9,5) 卫生间门口"},
        {"name": "立式空调", "short": "空调", "rect": [8, 8, 1, 1], "zone": "house",
         "note": "立式柜机·美术按贴墙 1×2 格出图（占地(8,8)，上沿(8,9)另占1格）·不压墙门"},
        {"name": "鞋柜", "short": "鞋柜", "rect": [5, 9, 1, 1], "zone": "house",
         "note": "院门进门处 · 让开 (7,9) 入院通道"},
        # ── 楼梯间 x11..13,y1..3（二层小楼的必备）──
        {"name": "楼梯", "short": "楼梯", "rect": [12, 1, 2, 3], "zone": "house",
         "note": "通往二层的楼梯 · 旧版照抄平房格局时完全缺失"},
        {"name": "储物柜", "short": "储物", "rect": [11, 1, 1, 1], "zone": "house",
         "note": "楼梯间杂物 · 让开 (11,2) 门口"},
        # ── 卫生间 x11..13,y5..6 ──
        {"name": "坐便器", "short": "坐便器", "rect": [12, 5, 1, 1], "zone": "house",
         "note": "水冲坐便 · 新式卫生间"},
        {"name": "洗手盆", "short": "洗手盆", "rect": [13, 5, 1, 1], "zone": "house",
         "note": "瓷砖贴面"},
        {"name": "淋浴", "short": "淋浴", "rect": [11, 6, 1, 1], "zone": "house",
         "note": "燃气热水器 · 不用再烧水"},
        {"name": "洗衣机", "short": "洗衣机", "rect": [13, 6, 1, 1], "zone": "house",
         "note": "全自动洗衣机 · 2001 新添"},
        # ── 厨房 x11..13,y8..9 ──
        {"name": "煤气灶", "short": "煤气灶", "rect": [12, 8, 1, 1], "zone": "house",
         "note": "液化气灶台 · 让开 (11,8) 门口"},
        {"name": "橱柜", "short": "橱柜", "rect": [13, 8, 1, 2], "zone": "house",
         "note": "整体橱柜 · 现代厨房"},
        {"name": "水池", "short": "水池", "rect": [11, 9, 1, 1], "zone": "house",
         "note": "自来水水池"},
        {"name": "冰箱", "short": "冰箱", "rect": [12, 9, 1, 1], "zone": "house",
         "note": "双开门冰箱 · 2001 年新添"},
        # ── 院子 x15..19 ──
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
    "story": "陆家老宅 1926 年后地契归沈家，1951 年空屋，1976 年塌成废墟。到 2001 年，这块地上盖起一栋先富起来的普通人家的瓷砖外墙二层小楼：席梦思、彩电、立式空调、水冲卫生间，一样不少。这家人不知道脚下曾是陆家老宅，也不知道二十年前这里的残墙断井——他们只是买下了沈家手里的一块地。全篇「没人知道」的主题，在这栋房子上落到了最平常的一户人家。",
    "note": "屋本体 15×11 格、占地 20×13 格（lot/wings 为准；旧 note 的 15×8/19×9 是照抄 lu_a2 时的旧口径）。一层独立设计为六空间：主卧/次卧/堂屋(客餐一体)/楼梯间/卫生间/厨房，堂屋为枢纽、每间房直接开门向堂屋，院门在堂屋正南。家具：主卧梳妆台+电视柜贴南墙、次卧书桌与椅子严格对调（书桌贴南墙）、堂屋立式柜机美术按 1×2 格出图。楼梯间是二层小楼一层必备、旧版完全缺失。与 A1/A2/A3 陆家同址——1976 还是废墟(lu_a3)，2001 已起新房；结构不再照抄 lu_a2，家具与叙事全新。住户对陆家旧事和老井一无所知，不设陆家线索格。",
}

for f in a4["furniture"]:
    f["yard_building"] = False
    f.setdefault("clue", False)
    f.setdefault("zone", "house")
    f.setdefault("short", f["name"])

# 自检 1：家具不重叠、四邻禁堵门/院门（比 check_all 更严：四邻全空）
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

# 自检 3：室内每个地板格都有房间归属（不露默认棕色）
# 门格 D / 墙格 # / 院门 G 本就不涂房间色，不算无主格；只查画成 '.' 的地板。
room_cells = {(i, j) for (x0, y0, x1, y1, *_rest) in a4["rooms"]
              for j in range(y0, y1 + 1) for i in range(x0, x1 + 1)}
floor_cells = {(i, j) for j, row in enumerate(grid) for i, ch in enumerate(row) if ch == "."}
for c in sorted(floor_cells - room_cells):
    raise AssertionError(f"室内无主格（露默认色）: {c}")

if PREVIEW:
    out = os.path.join(HERE, "..", "..", "lab", "zheng_a4_plan_preview.png")
    render(a4).save(out)
    print("PREVIEW only (JSON untouched):", os.path.abspath(out))
    print("rooms", len(a4["rooms"]), "furniture", len(a4["furniture"]))
else:
    for i, h in enumerate(houses):
        if h["id"] == "zheng_a4":
            houses[i] = a4
            break
    else:
        houses.append(a4)
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(houses, f, ensure_ascii=False, indent=2)
    print(f"zheng_a4 written: houses {len(houses)} lot {a4['lot']} rooms {len(a4['rooms'])} furniture {len(a4['furniture'])}")
