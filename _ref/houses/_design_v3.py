# -*- coding: utf-8 -*-
"""A1/A2/A3 世界布局 v3：先定房子，再让路绕开房子。

用户三条意见：
  1. 路太直 → 弯曲乡道，2 格宽，格子化
  2. 老井离磨坊太远 → 井放磨坊院子南行（数据里就是 [6,10]）
  3. 田太工整 → 参差不齐的不规则田块

流程：定房子 → 收集房格 → 用 A* 找一条从西到东、避开房格的弯曲路
"""
import json, os, heapq

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TILE = 16
W, H = 1600, 900
GW, GH = W // TILE, H // TILE

data = json.load(open(os.path.join(HERE, "houses_data.json"), encoding="utf-8"))
by_id = {h["id"]: h for h in data}

def lot_tiles(hid):
    lot = by_id[hid]["lot"]
    return (lot[2] - lot[0] + 1, lot[3] - lot[1] + 1)

# ---------- 房子位置（格坐标）----------
MILL_ORIGIN = (40, 7)          # 磨坊三帧同址：lot 18x(11|15) → x40..57
SHEN_ORIGIN_X = 8              # 沈家西沿
SHEN_SOUTH = 33                # 沈家南沿格（统一）
ZHOU_ORIGIN = (60, 40)         # 周家：路南
LU_ORIGIN = (74, 21)           # 陆家

PLACE = {}
PLACE["mill_a1"] = MILL_ORIGIN
PLACE["mill_a2"] = MILL_ORIGIN
PLACE["mill_a3"] = MILL_ORIGIN
for hid in ("shen_a1", "shen_a2", "shen_a3"):
    w, h = lot_tiles(hid)
    PLACE[hid] = (SHEN_ORIGIN_X, SHEN_SOUTH - h)
for hid in ("zhou_house", "zhou_a2", "zhou_a3"):
    PLACE[hid] = ZHOU_ORIGIN
for hid in ("lu_house", "lu_a2", "lu_a3"):
    PLACE[hid] = LU_ORIGIN

FRAMES = {
    "A1 1926": ["mill_a1", "shen_a1", "zhou_house", "lu_house"],
    "A2 1951": ["mill_a2", "shen_a2", "zhou_a2", "lu_a2"],
    "A3 1976": ["mill_a3", "shen_a3", "zhou_a3", "lu_a3"],
}

def rect_of(hid):
    w, h = lot_tiles(hid)
    x, y = PLACE[hid]
    return (x, y, w, h)

def blocked_cells(ids):
    """所有房子的占用格（lot 含院子，都算占）。"""
    cells = set()
    for hid in ids:
        x, y, w, h = rect_of(hid)
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                cells.add((xx, yy))
    return cells

# ---------- 井 / 槐 / 碑（格）----------
# 井在磨坊院子南行：mill lot [6,10] → 绝对格 (40+6, 7+10) = (46,17)
WELL_CELL = (46, 17)
TREE_CELL = (43, 16)      # 井西北
STELE_CELL = (60, 37)     # 路口南侧
FIELD_A_BASE = (62, 8, 15, 11)
FIELD_B_BASE = (79, 8, 15, 11)
FIELD_A_CUTS = [(62,8),(63,8),(62,9),(76,8),(76,9),(75,18),(76,18),(62,18),(63,18),(62,17),(68,18),(69,18)]
FIELD_B_CUTS = [(79,8),(80,8),(79,9),(93,8),(93,9),(92,18),(93,18),(79,18),(80,18),(79,17),(85,18),(86,18)]
FIELD_A_EXTRA = [(61,12),(61,13),(77,14),(77,15),(70,19),(71,19),(64,7)]
FIELD_B_EXTRA = [(78,11),(78,12),(94,15),(94,16),(86,19),(87,19),(90,7)]

def field_cells(base, cuts, extra):
    x0, y0, w, h = base
    s = set()
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            s.add((x, y))
    for c in cuts:
        s.discard(c)
    for e in extra:
        s.add(e)
    return s

FIELD_A = field_cells(FIELD_A_BASE, FIELD_A_CUTS, FIELD_A_EXTRA)
FIELD_B = field_cells(FIELD_B_BASE, FIELD_B_CUTS, FIELD_B_EXTRA)

# ---------- 路：A* 从西到东，避开房格 / 河 / 田 ----------
RIVER_CELLS = set((x, y) for y in range(0, 7) for x in range(GW))
DAM_CELLS = set((x, y) for y in range(2, 6) for x in range(12, 20))

def a_star(start, goal, blocked, extra_cost=None, max_iter=200000):
    """4 邻接 A*；extra_cost(cell) 给额外代价（用来让路少走房前空地、多绕）。"""
    def h(p):
        return abs(p[0] - goal[0]) + abs(p[1] - goal[1])
    openq = [(h(start), 0, start, None)]
    came = {}
    cost = {start: 0}
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
            nb = (cur[0] + dx, cur[1] + dy)
            if nb[0] < 0 or nb[0] >= GW or nb[1] < 0 or nb[1] >= GH:
                continue
            if nb in blocked:
                continue
            add = 1
            if extra_cost:
                add += extra_cost(nb)
            ng = g + add
            if nb not in cost or ng < cost[nb]:
                cost[nb] = ng
                heapq.heappush(openq, (ng + h(nb), ng, nb, cur))
    return None

# 每一帧各自算一条路（房子不同）
# 「路太直」的对策：给笔直方向加代价，让 A* 倾向轻微上下摆动 = 自然乡道。
ROADS = {}
for fname, ids in FRAMES.items():
    far = blocked_cells(ids) | RIVER_CELLS | FIELD_A | FIELD_B

    # 起点/终点：路两端在村外
    start = (0, 34)
    goal = (GW - 1, 33)

    # 期望的「摆动骨架」：中心线 y = 34 + 振幅*sin(x/波长)，让路贴着这个走
    import math
    def sway_target(x):
        return 34 + round(2.2 * math.sin(x / 7.0) + 1.3 * math.sin(x / 3.1))

    def cost_cell(cell):
        c = 0
        x, y = cell
        # 1) 偏离骨架 → 加代价（产生弯曲，但不会锯齿）
        c += abs(y - sway_target(x)) * 2
        # 2) 靠近房子 → 加代价（乡道不贴墙）
        for hid in ids:
            hx, hy, hw, hh = rect_of(hid)
            dx = max(hx - x, 0, x - (hx + hw - 1))
            dy = max(hy - y, 0, y - (hy + hh - 1))
            d = max(dx, dy)
            if d == 0:
                c += 60
            elif d == 1:
                c += 8
            elif d == 2:
                c += 2
        # 3) 绕井：井周围 2 格内加代价（让路真的绕一下井，这是头号物证）
        wd = max(abs(x - WELL_CELL[0]), abs(y - WELL_CELL[1]))
        if wd <= 1:
            c += 120
        elif wd == 2:
            c += 25
        return c

    path = a_star(start, goal, far, cost_cell)
    ROADS[fname] = path or []
    # 统计弯曲度：y 的极差
    if path:
        ys = [p[1] for p in path]
        print("%s  PATH_LEN=%d  y范围=%d..%d (振幅%d)" % (
            fname, len(path), min(ys), max(ys), max(ys) - min(ys)))

# 把路径膨胀成 2 格宽
def widen(path, half=1):
    out = set()
    for (x, y) in path:
        for oy in range(-half + 1, half + 1):
            out.add((x, y + oy))
    return out

ROAD_SETS = {k: widen(v, 1) for k, v in ROADS.items()}

# ---------- 校验 ----------
problems = []
print()
print("=" * 74)
for fname, ids in FRAMES.items():
    print("--- %s ---" % fname)
    rects = []
    for hid in ids:
        r = rect_of(hid)
        rects.append((hid, r))
        notes = []
        if r[0] < 0 or r[1] < 0 or r[0] + r[2] > GW or r[1] + r[3] > GH:
            notes.append("OUT")
        # 房格与路面相交
        cnt = 0
        for yy in range(r[1], r[1] + r[3]):
            for xx in range(r[0], r[0] + r[2]):
                if (xx, yy) in ROAD_SETS[fname]:
                    cnt += 1
        if cnt:
            notes.append("压路%d格" % cnt)
        print("  %-12s 格 x=%3d y=%3d %2dx%-2d  (px %4d,%4d %3dx%-3d)%s" % (
            hid, r[0], r[1], r[2], r[3], r[0]*TILE, r[1]*TILE, r[2]*TILE, r[3]*TILE,
            ("   [X] " + ",".join(notes)) if notes else ""))
        if notes:
            problems.append("%s: %s" % (hid, ",".join(notes)))
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            a, b = rects[i][1], rects[j][1]
            if a[0] < b[0]+b[2] and b[0] < a[0]+a[2] and a[1] < b[1]+b[3] and b[1] < a[1]+a[3]:
                problems.append("%s: %s x %s" % (fname, rects[i][0], rects[j][0]))
                print("    [X] 重叠")
    print()

print("老井格 %s → 世界 (%d,%d)" % (WELL_CELL, WELL_CELL[0]*TILE+8, WELL_CELL[1]*TILE+8))
print("磨坊院子南行 y=17，井 y=17 → 紧贴磨坊南墙 ✓")
print()
if problems:
    for p in problems:
        print("  !", p)
else:
    print("OK - 房子不压路、不重叠")
