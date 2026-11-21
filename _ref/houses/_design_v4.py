# -*- coding: utf-8 -*-
"""A1/A2/A3 世界布局 v4（2026-11-20 用户四条意见后重排）。

四条意见：
  1. 从 A3 开始路是直的 —— 写进 story.md，安排给沈家（沈德昌改粮站时取直）
  2. 河不能完全直 —— 要有自然弯曲
  3. 从 A2 开始田变规整（A1 不规则零散小田块 → A2/A3 集体化归并的规整大田）
  4. 磨坊位置要跟着挪

设计原则（延续前一轮）：
  - 地标（井/槐/碑）三帧同坐标
  - 房子在自己原址上长
  - 一切按格（16px）设计，美术照格画

输出：_ref/art/_overview/world_v3_a1.png 等三张预览
"""
import json, os, math, heapq
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(os.path.dirname(HERE), "art", "_overview")
TILE = 16
W, H = 1600, 900
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

# ============ 1. 河：自然弯曲（逐列深度） ============
def river_depth(x):
    """河的下缘深度（格）。低频大弯 + 高频小弯，模拟自然河道。"""
    return (6
            + 1.6 * math.sin(x / 13.0 + 0.6)
            + 0.9 * math.sin(x / 5.3 + 2.1)
            + 0.4 * math.sin(x / 2.2))

RIVER_CELLS = set()
for x in range(GW):
    d = int(round(river_depth(x)))
    d = max(4, min(9, d))
    for y in range(0, d + 1):
        RIVER_CELLS.add((x, y))

# 坝：在河身里，x 12..19（上游）
DAM_CELLS = set((x, y) for x in range(12, 20) for y in range(3, 7))

# ============ 2. 磨坊：贴河，位置东移（因河道变、路要重排） ============
# 磨坊三帧同址：lot 18x(11|15)。放在河道下方、离沈家留出间隙（A3 沈家 28 格宽到 x35）。
MILL_ORIGIN = (38, 10)          # 格 x38..55, y10..20(A1/A2) 或 y10..24(A3)
# 井：磨坊院子南行（数据 mill 家具 老井 = lot 格 [6,10]）
WELL_CELL = (MILL_ORIGIN[0] + 6, MILL_ORIGIN[1] + 10)      # (44, 20)
TREE_CELL = (WELL_CELL[0] - 3, WELL_CELL[1] - 2)           # 井西北

# ============ 3. 房子 ============
SHEN_X = 8
SHEN_SOUTH = 36
ZHOU_ORIGIN = (56, 42)
LU_ORIGIN = (72, 22)

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
# A1：不规则零散小田块（单干时代，地界碎）
FIELD_A1 = set()
for (bx, by, bw, bh) in [(58, 7, 6, 5), (65, 6, 7, 6), (60, 13, 5, 4),
                          (67, 13, 6, 5), (73, 8, 6, 5), (74, 14, 5, 4)]:
    for y in range(by, by + bh):
        for x in range(bx, bx + bw):
            FIELD_A1.add((x, y))
# 删掉几格做参差
for c in [(58,7),(63,11),(65,6),(71,6),(72,11),(60,16),(64,13),(74,18),(58,11),(69,18)]:
    FIELD_A1.discard(c)

# A2/A3：集体化归并后的规整大田（两块规整合并的大田）
FIELD_A2 = set()
for y in range(7, 19):
    for x in range(58, 74):
        FIELD_A2.add((x, y))
FIELD_A3 = set()
for y in range(7, 19):
    for x in range(58, 74):
        FIELD_A3.add((x, y))

FIELDS = {"a1_1926": FIELD_A1, "a2_1951": FIELD_A2, "a3_1976": FIELD_A3}

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

def sway(x, amp=2.6):
    return round(amp * math.sin(x / 8.0 + 0.4) + 1.4 * math.sin(x / 3.4))

ROADS = {}
for fname, ids in FRAMES.items():
    far = blocked_cells(ids) | RIVER_CELLS | FIELDS[fname]
    straight = (META[fname]["road"] == "直")
    road_y = 40 if straight else None

    def cost_cell(cell, ids=ids, straight=straight):
        x, y = cell
        c = 0
        if not straight:
            # 弯曲偏好：贴一条摆动骨架
            c += abs(y - (40 + sway(x))) * 2
        else:
            # 直线：偏离目标 y 重罚 → 直得干脆
            c += abs(y - (40 + 0)) * 8
        # 离房子远一点（乡道不贴墙）
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
        # 绕井（A1/A2 是头号物证；A3 已取直，不绕）
        if not straight:
            wd = max(abs(x - WELL_CELL[0]), abs(y - WELL_CELL[1]))
            if wd <= 1:
                c += 150
            elif wd == 2:
                c += 30
        return c

    ROADS[fname] = a_star((0, 40), (GW - 1, 40), far, cost_cell) or []
    if ROADS[fname]:
        ys = [p[1] for p in ROADS[fname]]
        xs = [p[0] for p in ROADS[fname]]
        print("%s 路长=%d  y %d..%d 振幅=%d" % (
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
print("=" * 76)
for fname, ids in FRAMES.items():
    print("--- %s (%s路) ---" % (fname, META[fname]["road"]))
    rects = []
    for hid in ids:
        r = rect_of(hid)
        rects.append((hid, r))
        notes = []
        if r[0] < 0 or r[1] < 0 or r[0]+r[2] > GW or r[1]+r[3] > GH:
            notes.append("OUT")
        hit = 0
        for yy in range(r[1], r[1]+r[3]):
            for xx in range(r[0], r[0]+r[2]):
                if (xx, yy) in ROAD_SETS[fname]:
                    hit += 1
        if hit:
            notes.append("压路%d格" % hit)
        hit_river = 0
        for yy in range(r[1], r[1]+r[3]):
            for xx in range(r[0], r[0]+r[2]):
                if (xx, yy) in RIVER_CELLS:
                    hit_river += 1
        if hit_river:
            notes.append("压河%d格" % hit_river)
        print("  %-12s 格 x=%3d y=%3d %2dx%-2d%s" % (
            hid, r[0], r[1], r[2], r[3], ("   [X] " + ",".join(notes)) if notes else ""))
        if notes:
            problems.append("%s: %s" % (hid, ",".join(notes)))
    for i in range(len(rects)):
        for j in range(i+1, len(rects)):
            a, b = rects[i][1], rects[j][1]
            if a[0] < b[0]+b[2] and b[0] < a[0]+a[2] and a[1] < b[1]+b[3] and b[1] < a[1]+a[3]:
                problems.append("%s: %s x %s 重叠" % (fname, rects[i][0], rects[j][0]))
                print("    [X] 重叠")
    print()

print("老井格 %s → 世界 (%d,%d)" % (WELL_CELL, WELL_CELL[0]*TILE+8, WELL_CELL[1]*TILE+8))
print("A1 田格数 %d（不规则） / A2 %d / A3 %d（规整）" % (
    len(FIELDS["a1_1926"]), len(FIELDS["a2_1951"]), len(FIELDS["a3_1976"])))
print("河弯曲：x=0..%d 深度 %d..%d 格" % (
    GW-1, min(int(round(river_depth(x))) for x in range(GW)),
    max(int(round(river_depth(x))) for x in range(GW))))
print()
if problems:
    for p in problems:
        print("  !", p)
else:
    print("OK - 房子不压路/不压河、不重叠")
