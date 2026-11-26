"""A4 重排：zhou_a4 / zheng_a4 成对落位搜索（两者不重叠 + 尽量靠近村庄核心）。"""
import json, math

TILE = 32
W, H = 4800, 3600
OX, OY = 2048, 1664
LANE_X0, LANE_X1 = 1984, 2112
RING_R = 304

houses = json.load(open("_ref/houses/houses_data.json", encoding="utf-8"))
by_id = {h["id"]: h for h in houses}

def lot_rect(pid, pos):
    x0, y0, x1, y1 = by_id[pid]["lot"]
    return (pos[0], pos[1], pos[0] + (x1 - x0 + 1) * TILE, pos[1] + (y1 - y0 + 1) * TILE)

def ov(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

def ring_hit(r):
    px = min(max(OX, r[0]), r[2]); py = min(max(OY, r[1]), r[3])
    return (px - OX) ** 2 + (py - OY) ** 2 < RING_R * RING_R

DAM = (384, 96, 640, 224)
FIELD = (3600, 320, 4480, 704)
HILLS = [(4288, 2624, 4800, 3008), (64, 2624, 576, 3008), (4288, 3040, 4672, 3328)]
SIGNS = [(x, 1732, x + 16, 1764) for x in (800, 1600, 2600, 3400)]
FIXED = {"market": lot_rect("market", (2144, 320)), "shen_a4": lot_rect("shen_a4", (64, 416))}

def legal(pid, pos):
    r = lot_rect(pid, pos)
    if r[0] < 64 or r[1] < 1760 or r[2] > W - 64 or r[3] > H - 64: return None
    if not (r[2] <= LANE_X0 or r[0] >= LANE_X1): return None
    if ring_hit(r): return None
    if ov(r, DAM) or ov(r, FIELD): return None
    for h in HILLS:
        if ov(r, h): return None
    for s in SIGNS:
        if ov(r, s): return None
    for k, fr in FIXED.items():
        if ov(r, fr): return None
    return r

def dist_to_core(p):
    return (p[0] - 2300) ** 2 + (p[1] - 2200) ** 2

STEP = 32
cand = {"zhou_a4": [], "zheng_a4": []}
for c in cand:
    for y in range(1760, H - 64, STEP):
        for x in range(64, W - 64, STEP):
            r = legal(c, (x, y))
            if r: cand[c].append((x, y, r))
    print(c, "候选", len(cand[c]))

best = None
for zx, zy, zr in cand["zhou_a4"]:
    if dist_to_core((zx, zy)) > 900 ** 2: continue
    for gx, gy, gr in cand["zheng_a4"]:
        if ov(zr, gr): continue
        # 两家之间留 64px 缝
        gap = max(zr[0] - gr[2], gr[0] - zr[2], zr[1] - gr[3], gr[1] - zr[3])
        if gap < 64: continue
        cost = dist_to_core((zx, zy)) + dist_to_core((gx, gy)) + (0 if gx > zx else 40000)
        if best is None or cost < best[0]:
            best = (cost, (zx, zy), (gx, gy))
print("最优配对:", best[1], best[2])
print("zhou_a4 rect", lot_rect("zhou_a4", best[1]))
print("zheng_a4 rect", lot_rect("zheng_a4", best[2]))
