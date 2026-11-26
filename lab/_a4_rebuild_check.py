"""A4 重排 v2 候选自检：以 A5 v5 已落地几何为基准反推 A4。
solid 语义照 scripts/frame_data.gd:38（solid:false 不进碰撞：路/田/井/树/内岛/环道都不挡路）。
"""
import json, math

TILE = 32
W, H = 4800, 3600
OX, OY = 2048, 1664
R_IN, R_OUT = 176, 304
ROAD_W = 128
ROAD_Y0, ROAD_Y1 = OY - ROAD_W // 2, OY + ROAD_W // 2      # 1600..1728
LANE_X0, LANE_X1 = 1984, 2112
LANE_N_BOT, LANE_S_TOP = 1360, 1968
WELL, WELL_R = (2048, 832), 48
TREE_R = 96                                                 # A4 老槐 75 岁（比 A5 的 160 小）
START = (1024, 1696)

def river_depth(x):
    base = 5.5 + 1.5 * math.sin(x / 13.0 + 0.6) + 0.8 * math.sin(x / 5.3 + 2.1)
    bay = math.exp(-((x - (38 + 55) * 0.5) / 16.0) ** 2)
    return int(round(max(4, min(15, base + bay * 8.0))))

RIVER_Y = [(river_depth(x) + 1) * TILE for x in range(W // TILE)]
RIVER_PTS = [[x * TILE, RIVER_Y[x]] for x in range(W // TILE)] + [[W, 0], [0, 0]]

houses = json.load(open("_ref/houses/houses_data.json", encoding="utf-8"))
by_id = {h["id"]: h for h in houses}

def lot_rect(pid, pos):
    x0, y0, x1, y1 = by_id[pid]["lot"]
    return (pos[0], pos[1], pos[0] + (x1 - x0 + 1) * TILE, pos[1] + (y1 - y0 + 1) * TILE)

def ov(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

def ring_hit(r):
    px = min(max(OX, r[0]), r[2]); py = min(max(OY, r[1]), r[3])
    return (px - OX) ** 2 + (py - OY) ** 2 < R_OUT * R_OUT

def river_bottom(x0, x1):
    i0, i1 = x0 // TILE, min(x1 // TILE, len(RIVER_Y) - 1)
    return max(RIVER_Y[i0:i1 + 1])

DAM = (384, 96, 640, 224)
FIELD = (3600, 320, 4480, 704)
HILLS = [(4288, 2624, 4800, 3008), (64, 2624, 576, 3008), (4288, 3040, 4672, 3328)]
SIGNS = [(x, 1732, x + 16, 1764) for x in (800, 1600, 2600, 3400)]
STELE_CANDIDATES = [(3488, 1584), (3520, 1536), (3568, 1504)]

POS = {
    "shen_a4":  (64, 416),
    "market":   (2144, 320),
    "zhou_a4":  (2272, 1984),
    "zheng_a4": (2304, 2400),
}
RECTS = {k: lot_rect(k, v) for k, v in POS.items()}

errs = []
for a in RECTS:
    for b in RECTS:
        if a < b and ov(RECTS[a], RECTS[b]):
            errs.append("房-房重叠 %s/%s" % (a, b))
for k, r in RECTS.items():
    if r[0] < 0 or r[1] < 0 or r[2] > W or r[3] > H: errs.append("出界 %s" % k)
    rb = river_bottom(r[0], r[2])
    if r[1] < rb + TILE:
        errs.append("压河 %s (顶%d 河下沿%d)" % (k, r[1], rb))
    if not (r[3] <= ROAD_Y0 or r[1] >= ROAD_Y1): errs.append("压主路 %s" % k)
    if not (r[2] <= LANE_X0 or r[0] >= LANE_X1): errs.append("压竖车道 %s" % k)
    if ring_hit(r): errs.append("压环岛 %s" % k)
    if ov(r, DAM): errs.append("压坝 %s" % k)
    if ov(r, FIELD): errs.append("压田 %s" % k)
    for i, h in enumerate(HILLS):
        if ov(r, h): errs.append("压山%d %s" % (i, k))
    for i, s in enumerate(SIGNS):
        if ov(r, s): errs.append("压路标%d %s" % (i, k))

if TREE_R > R_IN - 16: errs.append("树冠超出内岛")
if not (LANE_X0 <= WELL[0] <= LANE_X1): errs.append("井不在竖车道 x 内")
if not (LANE_N_BOT <= LANE_S_TOP): errs.append("车道南北段倒挂")

def solid_at(p):
    for k, r in RECTS.items():
        if r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]: return True
    if DAM[0] <= p[0] <= DAM[2] and DAM[1] <= p[1] <= DAM[3]: return True
    for h in HILLS:
        if h[0] <= p[0] <= h[2] and h[1] <= p[1] <= h[3]: return True
    for s in SIGNS:
        if s[0] <= p[0] <= s[2] and s[1] <= p[1] <= s[3]: return True
    return False

def free_count(pos, reach):
    n = 0
    for dx in range(-reach, reach + 1, 8):
        for dy in range(-reach, reach + 1, 8):
            if dx * dx + dy * dy > reach * reach: continue
            if not solid_at((pos[0] + dx, pos[1] + dy)): n += 1
    return n

print("== 界碑候选（rect 16x32，须不压房/路/田/坝/山/路标，且热点有可站点）==")
for sx, sy in STELE_CANDIDATES:
    r = (sx, sy, sx + 16, sy + 32)
    bad = []
    for k, fr in RECTS.items():
        if ov(r, fr): bad.append(k)
    if not (r[3] <= ROAD_Y0 or r[1] >= ROAD_Y1): bad.append("主路")
    if ov(r, DAM): bad.append("坝")
    if ov(r, FIELD): bad.append("田")
    for i, h in enumerate(HILLS):
        if ov(r, h): bad.append("山%d" % i)
    for i, s in enumerate(SIGNS):
        if ov(r, s): bad.append("路标%d" % i)
    fr = free_count((sx + 8, sy + 16), 68)
    print("  碑(%d,%d) 冲突=%s 热点可站点=%d" % (sx, sy, bad or "无", fr))

HOTSPOTS = {
    "老井 · 沥青补丁": ((WELL[0], WELL[1]), 88),
    "老槐": ((OX, OY), 88),
    "界碑": ((3520 + 8, 1536 + 16), 68),
    "坝": ((512, 160), 140),
    "田": ((4040, 512), 96),
    "超市工地 · 南大门": ((2816, 1184), 88),
}
print("== 热点可达 ==")
for title, (pos, reach) in HOTSPOTS.items():
    fc = free_count(pos, reach)
    print("  %-16s pos=%-12s reach=%-4d 可站采样点=%d" % (title, pos, reach, fc))
    if fc == 0: errs.append("热点不可达 %s" % title)

print("-" * 60)
for k, r in RECTS.items():
    print("%-9s pos=%-12s rect=%s 河下沿=%d" % (k, POS[k], r, river_bottom(r[0], r[2])))
print("井", WELL, "r", WELL_R, " 树", (OX, OY), "r", TREE_R, " 碑候选", STELE_CANDIDATES)
print("河点数", len(RIVER_PTS))
print("ERRORS", len(errs))
for e in errs: print("  !", e)
