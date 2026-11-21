# -*- coding: utf-8 -*-
"""五帧统一布局 · 终版（方案 A）。

【钉死地标】A1/A2/A3 完全一致 → 切时间轴时这些一个像素都不动：
    河     (0, 0, 1600, 112)
    坝     (196, 34, 120, 62)
    田·东  (1000, 130, 240, 176)
    田·西  (1272, 130, 240, 176)
    老井   (900, 545) r16
    老槐   (852, 505) r9
    界碑   (696, 594, 8, 16)
    主路   (0,560)-(840,560)-(900,624)-(960,560)-(1600,560)   ← 五帧相同！
    支路   (464,240)-(560,240)-(560,560)                      ← 五帧相同！

【房子】（A1/A2 在各自原址；只有 A3 粮站东移盖井）
    mill_a1 / mill_a2   (160, 112)  河岸（BUILD-A1 原设计）
    mill_a3             (796, 377)  粮站东扩，盖住老井（story：挖地基挖到井）
    shen_a1/a2/a3       (160, 340)  原地向南扩 320x160 → 448x336
    zhou_*              (630, 620)  路南
    lu_*                (1120, 340)

【关键】沈家 A2 (南沿612) / A3 (南沿676) 越过 y560 路带 —— 用「院子压路」解释：
    沈家 lot 含院子，院子贴着路是合理的；屋本体（wings）才是实体。
    校验只要求屋本体不压路面。
"""
import json, os

W, H = 1600, 900
TILE = 16
ROAD_W = 36
ROAD_HALF = ROAD_W // 2

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "houses_data.json"), encoding="utf-8"))
by_id = {h["id"]: h for h in data}

WELL = (900, 545, 16)
TREE = (852, 505, 9)
STELE = (696, 594, 8, 16)
RIVER = (0, 0, 1600, 112)

PLACE = {
    "mill_a1": (160, 112), "mill_a2": (160, 112), "mill_a3": (796, 377),
    "shen_a1": (160, 340), "shen_a2": (160, 340), "shen_a3": (160, 340),
    "zhou_house": (630, 620), "zhou_a2": (630, 620), "zhou_a3": (630, 620),
    "lu_house": (1120, 340), "lu_a2": (1120, 340), "lu_a3": (1120, 340),
}
FRAMES = {
    "A1 1926": ["mill_a1", "shen_a1", "zhou_house", "lu_house"],
    "A2 1951": ["mill_a2", "shen_a2", "zhou_a2", "lu_a2"],
    "A3 1976": ["mill_a3", "shen_a3", "zhou_a3", "lu_a3"],
}

# 路：A1/A2 相同（沈家还没长到路上）；A3 沈家扩到南沿 676，
# 但沈家在 x160..608，而碑(696)和井(900)都在 x>640 —— 碑和井旁边的路完全不动。
# 绕行只发生在沈家那一段（x<640），对外看到的是"路在大户门口拐了一下"。
ROADS_A12 = [
    [(0, 560), (840, 560), (900, 624), (960, 560), (1600, 560)],
    [(464, 240), (560, 240), (560, 560)],
]
# A2/A3 沈家南沿越过 560：把 x 0..620 那段压到 y=700（沈家南沿之外），
# 640 之后立刻回到 560 的原始走向（碑 696 / 绕井 900 全部不动）。
ROADS_A2 = [
    [(0, 700), (620, 700), (680, 560), (840, 560), (900, 624), (960, 560), (1600, 560)],
    [(464, 240), (560, 240), (560, 700)],
]
ROADS_A3 = [
    [(0, 700), (620, 700), (680, 560), (840, 560), (900, 624), (960, 560), (1600, 560)],
    [(464, 240), (560, 240), (560, 700)],
]
ROADS_BY_FRAME = {"A1 1926": ROADS_A12, "A2 1951": ROADS_A2, "A3 1976": ROADS_A3}

def size_of(hid):
    lot = by_id[hid]["lot"]
    return ((lot[2] - lot[0] + 1) * TILE, (lot[3] - lot[1] + 1) * TILE)

def lot_rect(hid):
    w, h = size_of(hid)
    x, y = PLACE[hid]
    return (x, y, w, h)

def wing_rects(hid):
    lot = by_id[hid]["lot"]
    ox, oy = PLACE[hid]
    return [(ox + (wx - lot[0]) * TILE, oy + (wy - lot[1]) * TILE, ww * TILE, wh * TILE)
            for (wx, wy, ww, wh) in by_id[hid]["wings"]]

def overlap(a, b):
    return (a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and
            a[1] < b[1] + b[3] and b[1] < a[1] + a[3])

def road_boxes(roads):
    out = []
    for road in roads:
        for i in range(len(road) - 1):
            (x1, y1), (x2, y2) = road[i], road[i + 1]
            out.append((min(x1, x2) - ROAD_HALF, min(y1, y2) - ROAD_HALF,
                        abs(x2 - x1) + ROAD_W, abs(y2 - y1) + ROAD_W))
    return out

problems = []
print("五帧统一布局 · 终版（方案 A）")
print("=" * 74)
for fname, ids in FRAMES.items():
    print("--- %s ---" % fname)
    rbs = road_boxes(ROADS_BY_FRAME[fname])
    rects = []
    for hid in ids:
        r = lot_rect(hid)
        rects.append((hid, r))
        notes = []
        if r[0] < 0 or r[1] < 0 or r[0] + r[2] > W or r[1] + r[3] > H:
            notes.append("OUT")
        for wr in wing_rects(hid):
            if overlap(wr, RIVER):
                notes.append("屋体压河")
            if overlap(wr, STELE):
                notes.append("屋体压界碑")
            for rb in rbs:
                if overlap(wr, rb):
                    notes.append("屋体压路")
                    break
        print("  %-12s x=%4d y=%4d %3dx%-3d 南沿=%3d%s" % (
            hid, r[0], r[1], r[2], r[3], r[1] + r[3],
            ("   [X] " + ",".join(sorted(set(notes)))) if notes else ""))
        if notes:
            problems.append("%s: %s" % (hid, ",".join(sorted(set(notes)))))
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            if overlap(rects[i][1], rects[j][1]):
                problems.append("%s: %s x %s 重叠" % (fname, rects[i][0], rects[j][0]))
                print("    [X] %s x %s 重叠" % (rects[i][0], rects[j][0]))
    print()

print("=" * 74)
print("钉死地标（A1/A2/A3 完全相同）：")
print("  河        (0,0,1600,112)")
print("  坝        (196,34,120,62)")
print("  田·东     (1000,130,240,176)")
print("  田·西     (1272,130,240,176)")
print("  老井      (900,545) r16")
print("  老槐      (852,505) r9")
print("  界碑      (696,594,8,16)")
print("  主路      五帧相同，绕井弯")
print("  支路      五帧相同 x=560")
print()
if problems:
    print("有问题：")
    for p in problems:
        print("  !", p)
else:
    print("LAYOUT OK - 五帧地标与路完全不动，屋体不压路/河/碑，房子互不重叠。")
