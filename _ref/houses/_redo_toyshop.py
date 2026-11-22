"""A5 2026 玩具店（周家曾孙 · 租沈家的楼）：整栋精调重写。

口径（用户 2026-11-22 拍板「还是一栋一栋来做」）：
  - 尺寸不动：lot [0,0,14,10] = 15×11 格（240×176 px），wings 同尺寸（无院子），
    与 docs/PROMPT-overseer.md:91、docs/PROMPT-tile-32px.md:84-85 的口径一致。
  - 街面朝北：证物链要求「玩具店招牌小字『本店由沈氏物业出租』」在**店面北墙**，
    故前门（大门）开在北墙，招牌钉在店面北墙西端；南墙留后门通仓库（后巷进货）。
  - 四间：店面 / 里屋（沈家雇来看店的人的铺）/ 账房 / 仓库。
    账柜落账房北墙；周有田往来账**仍写「位置待定」，不写成定论**。
  - 家具硬规矩：不压门、不越界、不重叠、不堵门（四邻全空），室内每格有房间归属。

幂等：存在则替换，否则追加。
预览：MCS_PREVIEW=1 只出预览图到 lab/，不写 houses_data.json。
"""
import json
import os
from gen_all_houses import build_grid, render

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")
PREVIEW = os.environ.get("MCS_PREVIEW") == "1"


def F(name, x, y, w, h, note="", clue=False, short=None, zone="house",
      yard_building=False, wall_mounted=False):
    return dict(name=name, short=short or name, rect=[x, y, w, h], note=note,
                clue=clue, zone=zone, yard_building=yard_building,
                wall_mounted=wall_mounted)


toyshop = {
    "id": "toyshop",
    "name": "玩具店 · A5 2026 · 周家曾孙（租沈家的楼）",
    "lot": [0, 0, 14, 10],
    "wings": [[0, 0, 15, 11]],
    # 隔墙：
    #   y=5 整条横墙（店面 | 后排）
    #   x=5 竖墙（里屋 | 账房），门在 (5,7)
    #   x=10 竖墙（账房 | 仓库），门在 (10,7)
    "partitions": [
        [1, 5, 13, 5],
        [5, 6, 5, 9],
        [10, 6, 10, 9],
    ],
    # 房门：(7,5) 店面→账房；(5,7) 账房→里屋；(10,7) 账房→仓库
    "doors": [[7, 5], [5, 7], [10, 7]],
    # 大门：(6,0)(7,0) 北墙前门（街面）；(12,10) 南墙后门（通后巷进货）
    "gate": [[6, 0], [7, 0], [12, 10]],
    "rooms": [
        [1, 1, 13, 4, "店面", "shop"],
        [1, 6, 4, 9, "里屋", "bed"],
        [6, 6, 9, 9, "账房", "account"],
        [11, 6, 13, 9, "仓库", "store"],
    ],
    "furniture": [
        # ── 店面 x1..13,y1..4（北面开前门，通道留 x6..7）──
        F("招牌小字", 1, 1, 2, 1, "「本店由沈氏物业出租」· 店面北墙西端 · A5 铁证链一环",
          clue=True, short="招牌"),
        F("玩具架", 3, 1, 1, 3, "竖向贴墙 · 一排童车"),
        F("玩具架", 5, 1, 1, 2, "前门西侧 · 不挡通道"),
        F("玩具架", 9, 1, 1, 2, "前门东侧 · 不挡通道"),
        F("玩具架", 12, 1, 1, 3, "贴东墙"),
        F("玩具架", 1, 2, 1, 2, "贴西墙"),
        F("收银台", 8, 3, 3, 1, "前门旁 · 算盘与找零抽屉"),
        F("摇摇马", 3, 4, 1, 1, "店面西南角 · 给孩子试骑"),
        F("玩具样车", 11, 4, 2, 1, "靠南墙陈列"),
        # ── 里屋 x1..4,y6..9（沈家雇来看店的人的铺位）──
        F("单人床", 1, 6, 2, 1, "看店人的铺 · 沈家雇的人住这儿"),
        F("小桌", 3, 6, 2, 1, "看店人吃饭看账的地方"),
        F("马扎", 3, 7, 1, 1, "小桌旁"),
        F("旧衣柜", 4, 8, 1, 2, "贴东墙"),
        F("脸盆架", 1, 9, 1, 1, "里屋西南角"),
        # ── 账房 x6..9,y6..9 ──
        F("账柜", 8, 6, 2, 1, "贴北墙 · 周有田往来账可能在此（位置待定，未定论）",
          clue=True, short="账柜"),
        F("办公桌", 6, 8, 2, 1, "账房办公 · 桌上算盘与流水"),
        F("椅", 8, 8, 1, 1, "办公桌旁"),
        F("算盘", 9, 8, 1, 1, "沈家做账用同一款式"),
        F("暖水瓶", 9, 9, 1, 1, "账房角落"),
        # ── 仓库 x11..13,y6..9 ──
        F("货架", 13, 6, 1, 3, "贴东墙"),
        F("货箱", 11, 6, 2, 1, "新到的玩具箱"),
        F("玩具车", 12, 7, 1, 1, "拆了包装的样品"),
        F("货箱", 11, 8, 2, 1, "纸箱堆"),
        F("纸箱堆", 11, 9, 1, 1, "待拆的纸箱 · 让开后门 (12,10)"),
    ],
    "clue": [
        "店面北墙招牌小字「本店由沈氏物业出租」（A5 铁证链一环）",
        "账房账柜：周有田往来账可能在此（位置待定，未定论）",
    ],
    "story": "租的是沈家的楼，雇的是沈家的人；周家三代不知道替谁看店。",
    "note": ("屋本体 15×11 格 = 240×176 px（lot/wings 一致，旧 note 的「15×9」作废）。"
             "街面朝北：前门（大门）开在北墙 (6,0)(7,0)，招牌小字钉在店面北墙西端；"
             "南墙 (12,10) 后门通后巷进货。四间：店面 / 里屋（沈家雇来看店的人的铺）/ 账房 / 仓库，"
             "账房居中开门向店面，里屋与仓库分别开门向账房。店面 5 组玩具架沿墙排、"
             "收银台靠前门东侧、x6..7 留出入店通道。账柜贴账房北墙——周有田往来账"
             "位置待定，未定论。"),
}

# ── 自检 1：家具不重叠、门/大门四邻禁放家具 ──
occupied = set()
for f in toyshop["furniture"]:
    x, y, w, h = f["rect"]
    for i in range(x, x + w):
        for j in range(y, y + h):
            assert (i, j) not in occupied, f"家具重叠 ({i},{j}) · {f['name']}"
            occupied.add((i, j))
for d in [tuple(d) for d in toyshop["doors"]] + [tuple(g) for g in toyshop["gate"]]:
    x, y = d
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        assert (x + dx, y + dy) not in occupied, f"堵门：家具占门 {d} 邻格 ({x+dx},{y+dy})"

# ── 自检 2：家具不压墙/门/院门（wall_mounted 的证物除外）──
grid = build_grid(toyshop)
for f in toyshop["furniture"]:
    if f.get("wall_mounted"):
        continue
    x, y, w, h = f["rect"]
    for i in range(x, x + w):
        for j in range(y, y + h):
            assert grid[j][i] in (".", " "), f"家具压墙/门：{f['name']} ({i},{j}) = {grid[j][i]}"

# ── 自检 3：室内每个地板格都有房间归属（不露默认棕）──
room_cells = {(i, j) for (x0, y0, x1, y1, *_rest) in toyshop["rooms"]
              for j in range(y0, y1 + 1) for i in range(x0, x1 + 1)}
floor_cells = {(i, j) for j, row in enumerate(grid) for i, ch in enumerate(row) if ch == "."}
for c in sorted(floor_cells - room_cells):
    raise AssertionError(f"室内无主格（露默认色）: {c}")

if PREVIEW:
    out = os.path.join(HERE, "..", "..", "lab", "toyshop_plan_preview.png")
    render(toyshop).save(out)
    print("PREVIEW only (JSON untouched):", os.path.abspath(out))
    print("rooms", len(toyshop["rooms"]), "furniture", len(toyshop["furniture"]))
else:
    with open(DATA, encoding="utf-8") as f:
        houses = json.load(f)
    for i, h in enumerate(houses):
        if h["id"] == "toyshop":
            houses[i] = toyshop
            break
    else:
        houses.append(toyshop)
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(houses, f, ensure_ascii=False, indent=2)
    print(f"toyshop written: houses {len(houses)} lot {toyshop['lot']} "
          f"rooms {len(toyshop['rooms'])} furniture {len(toyshop['furniture'])}")
