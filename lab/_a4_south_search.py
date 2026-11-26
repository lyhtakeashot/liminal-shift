"""A4 重排：zhou_a4 / zheng_a4 在主路以南的候选位搜索（偏好靠近村庄核心）。"""
import json, math

TILE = 32
W, H = 4800, 3600
OX, OY = 2048, 1664
ROAD_Y0, ROAD_Y1 = 1600, 1728
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

def ok(c, pos):
    r = lot_rect(c, pos)
    if r[0] < 64 or r[1] < 1760 or r[2] > W - 64 or r[3] > H - 64:
        return None, "边界/非路南"
    if not (r[2] <= LANE_X0 or r[0] >= LANE_X1): return None, "压竖车道"
    if ring_hit(r): return None, "压环岛"
    if ov(r, DAM): return None, "压坝"
    if ov(r, FIELD): return None, "压田"
    for i, h in enumerate(HILLS):
        if ov(r, h): return None, "压山%d" % i
    for i, s in enumerate(SIGNS):
        if ov(r, s): return None, "压路标%d" % i
    for k, fr in FIXED.items():
        if ov(r, fr): return None, "压" + k
    return r, "ok"

STEP = 32
for c in ("zhou_a4", "zheng_a4"):
    found = []
    for y in range(1760, H - 64, STEP):
        for x in range(64, 3000, STEP):
            r, why = ok(c, (x, y))
            if why == "ok":
                found.append((x, y))
    print(c, "候选", len(found), "前几个", found[:5])
    # 挑靠近核心 (2048, 2000) 的
    if found:
        best = min(found, key=lambda p: (p[0] - 2048) ** 2 + (p[1] - 2100) ** 2)
        print("   最近核心", best, lot_rect(c, best))
