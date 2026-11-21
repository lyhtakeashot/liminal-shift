# -*- coding: utf-8 -*-
"""A1/A2/A3 世界布局 v5（2026-11-20 用户第二轮意见）。

本轮意见：
  1. 树不要种在磨坊里 → 老槐移到井边的公共空地（路北小场）
  2. 磨坊处的河岸要往陆地凹（水磨坊靠引水推磨），且磨坊要离路近

四条历史意见（沿用）：
  1. A3 起路取直（沈德昌改粮站时做的，要写进 story）
  2. 河整体要有自然弯曲
  3. A1 田零散不规则 → A2 起归并成规整大田
  4. 磨坊位置随上述调整

设计（格坐标，1 格 = 32px）：
  河道：常规深 4~8 格起伏；磨坊处（x36..57）凹到 13 格 = 引水湾
  磨坊：(38, 14) 贴凹口，南沿 24（A1/A2）/ 28（A3）
  路：y = 32（磨坊南沿下 4~8 格，很近），A1/A2 弯、A3 直
  井：磨坊院外南侧路边 (42, 26)，公用水井
  槐：井旁路北空地 (39, 24)
"""
import json, os, math, heapq
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(os.path.dirname(HERE), "art", "_overview")
TILE = 32
W, H = 3200, 1800
GW, GH = W // TILE, H // TILE

FONTS = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]
def font(sz):
    for p in FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()

data = json.load(open(os.path.join(HERE, "houses_data.json"), encoding="utf-8"))
by_id = {h["id"]: h for h in data}

def lot_tiles(hid):
    lot = by_id[hid]["lot"]
    return (lot[2] - lot[0] + 1, lot[3] - lot[1] + 1)

# ============ 1. 河：自然弯曲 + 磨坊处引水凹口 ============
MILL_X0, MILL_X1 = 38, 55          # 磨坊 lot 横向范围

def river_depth(x):
    """河的下缘深度（格）。

    基础河道：低频大弯 + 高频小弯，模拟自然河床的摆动。
    磨坊处的引水凹口：用**高斯型宽缓剖面**（σ=16 格，影响半径约 ±32 格），
    而不是窄钟形 —— 窄钟形两端曲率太大，看着像人工挖的坑；
    真实河湾是几十上百米的缓慢下凹，磨坊只是恰好修在湾里。
    """
    base = (5.5
            + 1.5 * math.sin(x / 13.0 + 0.6)
            + 0.8 * math.sin(x / 5.3 + 2.1))
    center = (MILL_X0 + MILL_X1) * 0.5
    sigma = 16.0
    bay = math.exp(-((x - center) / sigma) ** 2)
    base += bay * 8.0
    return int(round(max(4, min(15, base))))

RIVER_CELLS = set()
for x in range(GW):
    d = river_depth(x)
    for y in range(0, d + 1):
        RIVER_CELLS.add((x, y))

# 坝：上游，x 12..19，在河身里
DAM_CELLS = set((x, y) for x in range(12, 20) for y in range(3, 7))

# ============ 2. 磨坊：贴凹口 ============
MILL_ORIGIN = (MILL_X0, 14)        # 格 x38..55, y14..24(A1/A2) / y14..28(A3)

# 井：磨坊院墙外南侧、路边（公用水井，不在磨坊院里）
WELL_CELL = (42, 26)
# 槐：井旁、磨坊院外、路边的小空地（用户要求：距井 ≤6 格、不在磨坊内、离路近）
# (40,30) 距井 4.5 格、在磨坊 lot 南墙外 2 格、距路 6 格
TREE_CELL = (40, 30)
# 界碑：路口南侧
STELE_CELL = (58, 30)

# ============ 3. 房子 ============
# 沈家左移到 x=4：A3 沈家右边 31、A5 树冠左沿 36 → 留 4 格间隙，
# 避免「树冠插进房子里」（现实里不会出现，视觉上也像 bug）。
SHEN_X = 4
SHEN_SOUTH = 33
ZHOU_ORIGIN = (56, 40)
LU_ORIGIN = (72, 24)

PLACE = {"mill_a1": MILL_ORIGIN, "mill_a2": MILL_ORIGIN, "mill_a3": MILL_ORIGIN,
         "zhou_house": ZHOU_ORIGIN, "zhou_a2": ZHOU_ORIGIN, "zhou_a3": ZHOU_ORIGIN,
         "lu_house": LU_ORIGIN, "lu_a2": LU_ORIGIN, "lu_a3": LU_ORIGIN}
for hid in ("shen_a1", "shen_a2", "shen_a3"):
    w, h = lot_tiles(hid)
    PLACE[hid] = (SHEN_X, SHEN_SOUTH - h)

FRAMES = {
    "a1_1926": ["mill_a1", "shen_a1", "zhou_house", "lu_house"],
    "a2_1951": ["mill_a2", "shen_a2", "zhou_a2", "lu_a2"],
    "a3_1976": ["mill_a3", "shen_a3", "zhou_a3", "lu_a3"],
}
META = {
    "a1_1926": {"ground": (110, 122, 76), "river": (63, 95, 110), "field": (125, 138, 62),
                "title": "A1 · 1926", "road": "弯"},
    "a2_1951": {"ground": (104, 116, 74), "river": (63, 95, 110), "field": (120, 134, 60),
                "title": "A2 · 1951", "road": "弯"},
    "a3_1976": {"ground": (106, 106, 68), "river": (74, 106, 96), "field": (107, 100, 64),
                "title": "A3 · 1976", "road": "直"},
    "a5_2026": {"ground": (122, 122, 118), "river": (74, 106, 96), "field": (110, 110, 106),
                "title": "A5 · 2026", "road": "十字路口+环岛"},
}

def rect_of(hid):
    w, h = lot_tiles(hid)
    x, y = PLACE[hid]
    return (x, y, w, h)

def blocked_cells(ids):
    s = set()
    for hid in ids:
        x, y, w, h = rect_of(hid)
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                s.add((xx, yy))
    return s

# ============ 4. 田 ============
FIELD_A1 = set()
for (bx, by, bw, bh) in [(58, 6, 6, 5), (65, 5, 7, 6), (60, 12, 5, 4),
                          (67, 12, 6, 5), (73, 7, 6, 5), (74, 13, 5, 4)]:
    for y in range(by, by + bh):
        for x in range(bx, bx + bw):
            FIELD_A1.add((x, y))
for c in [(58,6),(63,10),(65,5),(71,5),(72,10),(60,15),(64,12),(74,17),(58,10),(69,17)]:
    FIELD_A1.discard(c)

FIELD_BIG = set()
for y in range(6, 18):
    for x in range(58, 74):
        FIELD_BIG.add((x, y))

FIELDS = {"a1_1926": FIELD_A1, "a2_1951": FIELD_BIG, "a3_1976": FIELD_BIG}

# ============ 6. A5 2026：十字路口 + 环岛（树在环岛中央）============
# 树径方案（直径，格）：A1=3 A2=5 A3=7 A4=9 A5=13
# 像素圆必须奇数直径（有中心格），阶梯才对称。
# A1 是刚栽下的树苗，3 格（48px）就够了 —— 5 格是角色宽的 5 倍，太大。
# 3 格像素圆会退化成十字形，等美术套上树皮枝叶后就自然了。
# A5 跳到 13 格：百年老槐冠幅舒展，且要撑起环岛。
TREE_DIAMETER = {"a1_1926": 3, "a2_1951": 5, "a3_1976": 7, "a4_2001": 9, "a5_2026": 13}

RING_CENTER = TREE_CELL              # 与 A1/A2/A3 同一棵树
A5_CANOPY_R = TREE_DIAMETER["a5_2026"] // 2      # 6 格
RING_INNER = 7                       # 环岛内圈（树冠半径 6 + 1 格路肩）
RING_OUTER = 11                      # 环岛外圈（车道 4 格宽）

# 东西主路 y = RING_CENTER[1]，南北路 x = RING_CENTER[0]
# 环岛范围内用圆环替代直路
def ring_cells():
    """环岛车道格（内圈外、外圈内）。"""
    cx, cy = RING_CENTER
    s = set()
    for y in range(cy - RING_OUTER, cy + RING_OUTER + 1):
        for x in range(cx - RING_OUTER, cx + RING_OUTER + 1):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if RING_INNER < d <= RING_OUTER:
                s.add((x, y))
    return s

def tree_canopy(tag="a5_2026"):
    """该帧的树冠格 —— 像素圆（逐格阶梯收边，不是数学圆）。

    像素圆必须奇数直径才有中心格，阶梯才对称。
    用 x²+y² <= r² + r*0.3 的判定，实测各行列宽为理想的
    3,5,7,9,9,9,7,5,3（r=4），边缘是整格像素块。
    """
    cx, cy = RING_CENTER
    diam = TREE_DIAMETER.get(tag, 3)
    r = diam // 2
    s = set()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r + r * 0.3:
                s.add((cx + dx, cy + dy))
    return s if s else {(cx, cy)}

RING = ring_cells()
CANOPY_A5 = tree_canopy("a5_2026")


def road_a5_props():
    """A5 环岛之外的东西路与南北路；环岛圈内由 RING 提供。"""
    cx, cy = RING_CENTER
    s = set()
    # 东西双向（路宽 2 格，中心线上下各 1）
    for x in range(0, GW):
        if abs(x - cx) <= RING_OUTER:
            continue
        for oy in (-1, 0):
            s.add((x, cy + oy))
    # 南北双向
    for y in range(0, GH):
        if abs(y - cy) <= RING_OUTER:
            continue
        for ox in (-1, 0):
            s.add((cx + ox, y))
    return s


ROAD_A5 = road_a5_props() | RING

# ============ 5. 路 ============
def a_star(start, goal, blocked, extra=None, max_iter=300000):
    def h(p):
        return abs(p[0]-goal[0]) + abs(p[1]-goal[1])
    openq = [(h(start), 0, start, None)]
    came, cost = {}, {start: 0}
    it = 0
    while openq and it < max_iter:
        it += 1
        f, g, cur, par = heapq.heappop(openq)
        if cur in came:
            continue
        came[cur] = par
        if cur == goal:
            path = []
            c = cur
            while c is not None:
                path.append(c)
                c = came[c]
            return path[::-1]
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nb = (cur[0]+dx, cur[1]+dy)
            if nb[0] < 0 or nb[0] >= GW or nb[1] < 0 or nb[1] >= GH:
                continue
            if nb in blocked:
                continue
            add = 1 + (extra(nb) if extra else 0)
            ng = g + add
            if nb not in cost or ng < cost[nb]:
                cost[nb] = ng
                heapq.heappush(openq, (ng + h(nb), ng, nb, cur))
    return None

ROAD_Y = 36

def sway(x, amp=2.4):
    return round(amp * math.sin(x / 8.0 + 0.4) + 1.2 * math.sin(x / 3.4))

ROADS = {}
for fname, ids in FRAMES.items():
    far = blocked_cells(ids) | RIVER_CELLS | FIELDS[fname]
    straight = (META[fname]["road"] == "直")

    def cost_cell(cell, ids=ids, straight=straight):
        x, y = cell
        c = 0
        if straight:
            c += abs(y - ROAD_Y) * 40         # A3：一条直路，偏移代价极高
        else:
            c += abs(y - (ROAD_Y + sway(x))) * 2   # A1/A2：弯
        for hid in ids:
            hx, hy, hw, hh = rect_of(hid)
            dx = max(hx - x, 0, x - (hx + hw - 1))
            dy = max(hy - y, 0, y - (hy + hh - 1))
            d = max(dx, dy)
            if d == 0:
                c += 80
            elif d == 1:
                c += 10
            elif d == 2:
                c += 3
        if not straight:
            # 绕井：井在 (42,26)，路要往南绕开它
            wd = max(abs(x - WELL_CELL[0]), abs(y - WELL_CELL[1]))
            if wd <= 1:
                c += 150
            elif wd == 2:
                c += 30
        return c

    ROADS[fname] = a_star((0, ROAD_Y), (GW - 1, ROAD_Y), far, cost_cell) or []
    if ROADS[fname]:
        ys = [p[1] for p in ROADS[fname]]
        print("%s 路长=%d y %d..%d 振幅=%d" % (
            fname, len(ROADS[fname]), min(ys), max(ys), max(ys) - min(ys)))

def widen(path, half=1):
    s = set()
    for (x, y) in path:
        for oy in range(-half + 1, half + 1):
            s.add((x, y + oy))
    return s

ROAD_SETS = {k: widen(v, 1) for k, v in ROADS.items()}

# ============ 校验 ============
problems = []
print()
print("=" * 78)
for fname, ids in FRAMES.items():
    print("--- %s (%s路) ---" % (fname, META[fname]["road"]))
    rects = []
    for hid in ids:
        r = rect_of(hid)
        rects.append((hid, r))
        notes = []
        if r[0] < 0 or r[1] < 0 or r[0]+r[2] > GW or r[1]+r[3] > GH:
            notes.append("OUT")
        hit = sum(1 for yy in range(r[1], r[1]+r[3]) for xx in range(r[0], r[0]+r[2])
                  if (xx, yy) in ROAD_SETS[fname])
        if hit:
            notes.append("压路%d格" % hit)
        # 屋体压河？
        wr_hit = 0
        for (wx, wy, ww, wh) in by_id[hid]["wings"]:
            for yy in range(r[1]+wy, r[1]+wy+wh):
                for xx in range(r[0]+wx, r[0]+wx+ww):
                    if (xx, yy) in RIVER_CELLS:
                        wr_hit += 1
        if wr_hit:
            notes.append("屋体入水%d格" % wr_hit)
        print("  %-12s 格 x=%3d y=%3d %2dx%-2d  南沿%2d%s" % (
            hid, r[0], r[1], r[2], r[3], r[1]+r[3],
            ("   [X] " + ",".join(notes)) if notes else ""))
        if notes:
            problems.append("%s: %s" % (hid, ",".join(notes)))
    for i in range(len(rects)):
        for j in range(i+1, len(rects)):
            a, b = rects[i][1], rects[j][1]
            if a[0] < b[0]+b[2] and b[0] < a[0]+a[2] and a[1] < b[1]+b[3] and b[1] < a[1]+a[3]:
                problems.append("%s: %s x %s 重叠" % (fname, rects[i][0], rects[j][0]))
                print("    [X] 重叠")
    print()

print("河深范围 %d..%d 格；磨坊处凹口最深 %d 格" % (
    min(river_depth(x) for x in range(GW)), max(river_depth(x) for x in range(GW)),
    max(river_depth(x) for x in range(MILL_X0-3, MILL_X1+4))))
print("磨坊 (%d,%d) 南沿 %d 格；路 y=%d 格 → 相距 %d 格 = %d px" % (
    MILL_ORIGIN[0], MILL_ORIGIN[1], MILL_ORIGIN[1]+11, ROAD_Y,
    ROAD_Y-(MILL_ORIGIN[1]+11), (ROAD_Y-(MILL_ORIGIN[1]+11))*TILE))
print("老井 %s → 世界 (%d,%d)  在磨坊院外、路边" % (
    WELL_CELL, WELL_CELL[0]*TILE+8, WELL_CELL[1]*TILE+8))
print("老槐 %s → 世界 (%d,%d)  井旁路北空地，不在磨坊里" % (
    TREE_CELL, TREE_CELL[0]*TILE+8, TREE_CELL[1]*TILE+8))
print()
if problems:
    for p in problems:
        print("  !", p)
else:
    print("OK")
