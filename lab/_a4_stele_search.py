"""A4 界碑候选搜索：工地（market）以东的空地，路边、可站、不压任何东西。
剧情：1951 埋土 → 2001 推到工地东边空地 → 2026 砌进小学围墙。
"""
import json, math

TILE = 32
W, H = 4800, 3600
OX, OY = 2048, 1664
R_OUT = 304
ROAD_Y0, ROAD_Y1 = 1600, 1728

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

DAM = (384, 96, 640, 224)
FIELD = (3600, 320, 4480, 704)
HILLS = [(4288, 2624, 4800, 3008), (64, 2624, 576, 3008), (4288, 3040, 4672, 3328)]
SIGNS = [(x, 1732, x + 16, 1764) for x in (800, 1600, 2600, 3400)]
POS = {"shen_a4": (64, 416), "market": (2144, 320), "zhou_a4": (2272, 1984), "zheng_a4": (2304, 2400)}
RECTS = {k: lot_rect(k, v) for k, v in POS.items()}

def free_at(p):
    for r in RECTS.values():
        if r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]: return False
    if DAM[0] <= p[0] <= DAM[2] and DAM[1] <= p[1] <= DAM[3]: return False
    for h in HILLS:
        if h[0] <= p[0] <= h[2] and h[1] <= p[1] <= h[3]: return False
    for s in SIGNS:
        if s[0] <= p[0] <= s[2] and s[1] <= p[1] <= s[3]: return False
    return True

cands = []
for y in range(320, 1600, 16):
    for x in range(3488, 4200, 16):
        r = (x, y, x + 16, y + 32)
        if ov(r, FIELD): continue
        if ov(r, DAM): continue
        for h in HILLS:
            if ov(r, h): continue
        for s in SIGNS:
            if ov(r, s): continue
        for k, fr in RECTS.items():
            if ov(r, fr): continue
        if not (r[2] <= 0 or r[0] >= 0) and (r[1] < ROAD_Y0 and r[3] > ROAD_Y0):
            continue   # 压在主路带上
        if ring_hit(r): continue
        n = 0
        for dx in range(-68, 69, 8):
            for dy in range(-68, 69, 8):
                if dx * dx + dy * dy > 68 * 68: continue
                if free_at((x + 8 + dx, y + 16 + dy)): n += 1
        if n > 0:
            cands.append((x, y, n, min(abs(y + 16 - ROAD_Y0), abs(y + 16 - ROAD_Y1))))

print("候选数", len(cands))
if cands:
    best = min(cands, key=lambda c: c[3])
    print("离主路最近的:", best)
    for c in cands[:10]: print("  ", c)
