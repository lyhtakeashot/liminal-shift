#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A4 重排 v3 方案自检：按用户口径（实体空气墙 = 房屋 lot ∪ 山体）核对。

关键：压环岛判定用**真实 polygon 点包含测试**（环道 polygon 的 bbox 比实际形状大，
按 bbox 判定会误报）。
"""
import io, json, math

TILE = 32
W, H = 4800, 3600
OX, OY = 2048, 1664
R_IN, R_OUT = 176, 304
ROAD_Y0, ROAD_Y1 = 1600, 1728
LANE_X0, LANE_X1 = 1984, 2112
LANE_N_BOT, LANE_S_TOP = 1360, 1968
WELL = (2048, 832)
WELL_R = 48
TREE_R = 96
START = (1024, 1696)

DAM = (384, 96, 640, 224)
FIELD = (3600, 320, 4480, 704)

def river_depth(x):
    import math as m
    base = 5.5 + 1.5 * m.sin(x / 13.0 + 0.6) + 0.8 * m.sin(x / 5.3 + 2.1)
    center = (38 + 55) * 0.5
    sigma = 16.0
    bay = m.exp(-((x - center) / sigma) ** 2)
    base += bay * 8.0
    return int(round(max(4, min(15, base))))

RIVER_Y = [(river_depth(x) + 1) * TILE for x in range(W // TILE)]
RIVER_PTS = [[x * TILE, RIVER_Y[x]] for x in range(W // TILE)] + [[W, 0], [0, 0]]

with io.open("_ref/houses/houses_data.json", "r", encoding="utf-8") as f:
    HOUSES = json.load(f)
LOT = {h["id"]: h["lot"] for h in HOUSES}

def lot_rect(pid, pos):
    l = LOT[pid]
    x0, y0, x1, y1 = l
    return (pos[0], pos[1], pos[0] + (x1 - x0 + 1) * TILE, pos[1] + (y1 - y0 + 1) * TILE)

def ov(a, b):
    x = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    y = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    return x * y

def in_poly(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xin = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < xin:
                inside = not inside
    return inside

# 读 A5 帧的真实环道 / 内岛 polygon
with io.open("data/frames.json", "r", encoding="utf-8") as f:
    FR = json.load(f)
a5 = None
for fr in FR["frames"]:
    if fr["id"] == "a5_2026":
        a5 = fr
RING = [s for s in a5["shapes"] if s.get("type") == "polygon" and s.get("label") == "路" and len(s["points"]) == 72]
ISLAND = [s for s in a5["shapes"] if s.get("type") == "polygon" and s.get("label") == "岛"]
assert len(RING) == 1 and len(ISLAND) == 1, (len(RING), len(ISLAND))
RING_PTS = RING[0]["points"]
ISLAND_PTS = ISLAND[0]["points"]

# ---- 方案 v3 ----
POS = {
    "shen_a4": (64, 416),
    "market": (2144, 320),
    "zhou_a4": (576, 1920),
    "zheng_a4": (1152, 2272),
}
HOUSE_RECTS = {k: lot_rect(k, v) for k, v in POS.items()}
# 补山：严格覆盖 A5 的 school / toyshop 占地（A5 有房，A4 那里是山）
HILLS = [
    (4288, 2624, 4800, 3008),
    (64, 2624, 576, 3008),
    (4288, 3040, 4672, 3328),
    (1280, 1920, 1792, 2272),   # school 上缘右段
    (576, 2272, 1152, 2688),    # school 左段
    (576, 2688, 1792, 2880),    # school 下缘
    (2176, 1984, 2848, 2624),   # toyshop 整块
]
SIGNS = [(800, 1732, 816, 1764), (1600, 1732, 1616, 1764), (2600, 1732, 2616, 1764), (3400, 1732, 3416, 1764)]

errs = []
def chk(cond, msg):
    if not cond:
        errs.append(msg)

# 1) 房-房不重叠
ids = list(HOUSE_RECTS)
for i in range(len(ids)):
    for j in range(i + 1, len(ids)):
        a, b = HOUSE_RECTS[ids[i]], HOUSE_RECTS[ids[j]]
        chk(ov(a, b) == 0, "房-房重叠 %s/%s = %d" % (ids[i], ids[j], ov(a, b)))

# 2) 房-山不重叠；山-山不重叠
for k, hr in HOUSE_RECTS.items():
    for hi, h in enumerate(HILLS):
        chk(ov(hr, h) == 0, "房压山 %s vs hill#%d %s = %d" % (k, hi, h, ov(hr, h)))
for i in range(len(HILLS)):
    for j in range(i + 1, len(HILLS)):
        chk(ov(HILLS[i], HILLS[j]) == 0, "山-山重叠 #%d/#%d" % (i, j))

# 3) 山-环道/内岛：**真实 polygon 点包含**测试
def rect_hits_poly(r, poly):
    hit = 0
    for x in range(r[0], r[2], 8):
        for y in range(r[1], r[3], 8):
            if in_poly((x + 4, y + 4), poly):
                hit += 1
    return hit

for hi, h in enumerate(HILLS):
    hr = rect_hits_poly(h, RING_PTS)
    hi2 = rect_hits_poly(h, ISLAND_PTS)
    chk(hr == 0, "山#%d %s 压环道 polygon（采样命中 %d）" % (hi, h, hr))
    chk(hi2 == 0, "山#%d %s 压内岛 polygon（采样命中 %d）" % (hi, h, hi2))

# 4) 房不压环道/内岛
for k, hr in HOUSE_RECTS.items():
    chk(rect_hits_poly(hr, RING_PTS) == 0, "房 %s 压环道" % k)
    chk(rect_hits_poly(hr, ISLAND_PTS) == 0, "房 %s 压内岛" % k)

# 5) 不压主路带 / 竖车道 / 坝 / 田 / 路标 / 河
ROAD_RECTS = [(0, ROAD_Y0, 1744, ROAD_Y1), (2352, ROAD_Y0, W, ROAD_Y1)]
LANE_RECTS = [(LANE_X0, 288, LANE_X1, LANE_N_BOT), (LANE_X0, LANE_S_TOP, LANE_X1, H)]
for k, hr in HOUSE_RECTS.items():
    for r in ROAD_RECTS:
        chk(ov(hr, r) == 0, "房 %s 压主路 %s" % (k, r))
    for r in LANE_RECTS:
        chk(ov(hr, r) == 0, "房 %s 压竖车道 %s" % (k, r))
    chk(ov(hr, DAM) == 0, "房 %s 压坝" % k)
    chk(ov(hr, FIELD) == 0, "房 %s 压田" % k)
    for s in SIGNS:
        chk(ov(hr, s) == 0, "房 %s 压路标 %s" % (k, s))
    # 压河：房顶必须 ≥ 该 x 区间河下沿 + 32
    x0, x1 = hr[0] // TILE, hr[2] // TILE
    rb = max(RIVER_Y[x0:x1 + 1])
    chk(hr[1] >= rb + TILE, "房 %s 压河（顶 %d，河下沿 %d）" % (k, hr[1], rb))

for hi, h in enumerate(HILLS):
    for r in ROAD_RECTS + LANE_RECTS:
        chk(ov(h, r) == 0, "山#%d %s 压路 %s" % (hi, h, r))
    chk(ov(h, DAM) == 0, "山#%d 压坝" % hi)
    chk(ov(h, FIELD) == 0, "山#%d 压田" % hi)
    for s in SIGNS:
        chk(ov(h, s) == 0, "山#%d 压路标 %s" % (hi, s))
    x0, x1 = h[0] // TILE, h[2] // TILE
    rb = max(RIVER_Y[x0:x1 + 1])
    chk(h[1] >= rb + TILE, "山#%d 压河（顶 %d，河下沿 %d）" % (hi, h[1], rb))

# 6) 出界
for k, hr in HOUSE_RECTS.items():
    chk(hr[0] >= 0 and hr[1] >= 0 and hr[2] <= W and hr[3] <= H, "房 %s 出界 %s" % (k, hr))
for hi, h in enumerate(HILLS):
    chk(h[0] >= 0 and h[1] >= 0 and h[2] <= W and h[3] <= H, "山#%d 出界" % hi)

# 7) 树冠 ≤ R_IN-16
chk(TREE_R <= R_IN - 16, "树冠 %d > R_IN-16" % TREE_R)
# 8) 井在北车道 x 内
chk(LANE_X0 <= WELL[0] <= LANE_X1, "井不在车道 x 内")

# ---- 空气墙一致性（用户口径：房屋 lot ∪ 山）----
def airwall_mask(rects):
    m = set()
    for r in rects:
        for x in range(r[0], r[2], TILE):
            for y in range(r[1], r[3], TILE):
                m.add((x // TILE, y // TILE))
    return m

A5_HOUSES = {"shen_a5": (64, 416), "market": (2144, 320), "toyshop": (2176, 1984), "school": (576, 1920)}
A5_RECTS = {k: lot_rect(k, v) for k, v in A5_HOUSES.items()}
A5_HILLS = [(4288, 2624, 4800, 3008), (64, 2624, 576, 3008), (4288, 3040, 4672, 3328)]
s5 = airwall_mask(list(A5_RECTS.values()) + A5_HILLS)
s4 = airwall_mask(list(HOUSE_RECTS.values()) + HILLS)
inter = len(s5 & s4)
union = len(s5 | s4)
print("A5 airwall cells = %d" % len(s5))
print("A4 airwall cells = %d" % len(s4))
print("cover(A5 in A4) = %.1f%%" % (100.0 * inter / len(s5)))
print("cover(A4 in A5) = %.1f%%" % (100.0 * inter / len(s4)))
print("IoU = %.1f%%" % (100.0 * inter / union))
print("A4 有 A5 无 = %d 格 ; A5 有 A4 无 = %d 格" % (len(s4 - s5), len(s5 - s4)))
miss = sorted(s5 - s4)
if miss:
    xs = sorted(set(p[0] for p in miss)); ys = sorted(set(p[1] for p in miss))
    print("缺格 bbox: x %d..%d (px %d..%d) y %d..%d (px %d..%d)" % (
        xs[0], xs[-1], xs[0] * TILE, xs[-1] * TILE + TILE, ys[0], ys[-1], ys[0] * TILE, ys[-1] * TILE + TILE))
    print("缺格前 20:", miss[:20])
extra = sorted(s4 - s5)
if extra:
    xs = sorted(set(p[0] for p in extra)); ys = sorted(set(p[1] for p in extra))
    print("多格 bbox: x %d..%d (px %d..%d) y %d..%d (px %d..%d) 共 %d" % (
        xs[0], xs[-1], xs[0] * TILE, xs[-1] * TILE + TILE, ys[0], ys[-1], ys[0] * TILE, ys[-1] * TILE + TILE, len(extra)))

print("ERRORS = %d" % len(errs))
for e in errs:
    print("  - " + e)
