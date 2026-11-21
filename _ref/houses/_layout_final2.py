# -*- coding: utf-8 -*-
"""五帧统一布局 · 最终定案（方案 A 终版）。

【钉死地标】A1/A2/A3 完全一致（切时间轴一格都不动）：
    河     (0, 0, 1600, 112)
    坝     (196, 34, 120, 62)
    田·东  (1000, 130, 240, 176)
    田·西  (1272, 130, 240, 176)
    老井   (900, 545) r16
    老槐   (852, 505) r9
    界碑   (696, 594, 8, 16)
    主路   (0,560)-(840,560)-(900,624)-(960,560)-(1600,560)
    支路   (464,240)-(560,240)-(560,560)

【房子】原址长大；南墙对齐在路面北侧（542），向北长。
    mill_a1/a2  (640, 112)  河岸（不压路、不压井）
    mill_a3     (796, 377)  粮站东扩盖住老井（story：挖地基挖到老井）
    shen_a1     (160, 382)  320x160 → 南沿 542
    shen_a2     (160, 270)  368x272 → 南沿 542
    shen_a3     (160, 206)  448x336 → 南沿 542
    zhou_*      (630, 620)  路南
    lu_*        (1120, 340) 南沿 500
"""
import json, os

W, H = 1600, 900
TILE = 16
ROAD_W = 36
ROAD_HALF = ROAD_W // 2
SHEN_SOUTH = 520          # 路面带 542..578，含半幅路 524；房子南沿收到 520 才不压

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "houses_data.json"), encoding="utf-8"))
by_id = {h["id"]: h for h in data}

WELL = (900, 545, 16)
TREE = (852, 505, 9)
STELE = (696, 594, 8, 16)
RIVER = (0, 0, 1600, 112)

ROADS = [
    [(0, 560), (840, 560), (900, 624), (960, 560), (1600, 560)],
    # 支路：从磨坊南门外 (640,288 下方) 出发，沿沈家东墙外南下接主路。
    # 磨坊 A1/A2 在 (640,112) 南沿 288；沈家 x 到 608(A3) 东墙外，取 x=640。
    [(640, 300), (640, 560)],
]

def size_of(hid):
    lot = by_id[hid]["lot"]
    return ((lot[2] - lot[0] + 1) * TILE, (lot[3] - lot[1] + 1) * TILE)

PLACE = {}
# 磨坊 A1/A2：河岸
PLACE["mill_a1"] = (640, 112)
PLACE["mill_a2"] = (640, 112)
# 粮站 A3：东扩盖井
PLACE["mill_a3"] = (796, 377)
# 沈家：南沿对齐 542，向北长
for hid in ("shen_a1", "shen_a2", "shen_a3"):
    PLACE[hid] = (160, SHEN_SOUTH - size_of(hid)[1])
# 周家 / 陆家
for hid in ("zhou_house", "zhou_a2", "zhou_a3"):
    PLACE[hid] = (630, 620)
for hid in ("lu_house", "lu_a2", "lu_a3"):
    PLACE[hid] = (1120, 340)

FRAMES = {
    "A1 1926": ["mill_a1", "shen_a1", "zhou_house", "lu_house"],
    "A2 1951": ["mill_a2", "shen_a2", "zhou_a2", "lu_a2"],
    "A3 1976": ["mill_a3", "shen_a3", "zhou_a3", "lu_a3"],
}

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

def road_boxes():
    """每段路按走向生成细带矩形 —— 不要用起止点的包围盒，
    否则像 (840,560)-(900,624) 这种斜段会把整块 60x64 都算成路面，误判。"""
    out = []
    for road in ROADS:
        for i in range(len(road) - 1):
            (x1, y1), (x2, y2) = road[i], road[i + 1]
            if x1 == x2:      # 垂直段
                out.append((x1 - ROAD_HALF, min(y1, y2),
                            ROAD_W, abs(y2 - y1)))
            elif y1 == y2:    # 水平段
                out.append((min(x1, x2), y1 - ROAD_HALF,
                            abs(x2 - x1), ROAD_W))
            else:             # 斜段：按采样点生成小方块
                steps = max(abs(x2 - x1), abs(y2 - y1)) // 8 + 1
                for s in range(steps + 1):
                    t = float(s) / float(steps)
                    cx = x1 + (x2 - x1) * t
                    cy = y1 + (y2 - y1) * t
                    out.append((cx - ROAD_HALF, cy - ROAD_HALF, ROAD_W, ROAD_W))
    return out

problems = []
print("五帧统一布局 · 最终定案")
print("=" * 76)
for fname, ids in FRAMES.items():
    print("--- %s ---" % fname)
    rbs = road_boxes()
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
        # A3 粮站必须盖住井
        extra = ""
        if hid == "mill_a3":
            in_mill = (r[0] <= WELL[0] <= r[0] + r[2]) and (r[1] <= WELL[1] <= r[1] + r[3])
            extra = "  [井在院内]" if in_mill else "  [X] 井不在院内"
            if not in_mill:
                problems.append("mill_a3 没盖住老井")
        print("  %-12s x=%4d y=%4d %3dx%-3d 南沿=%3d%s%s" % (
            hid, r[0], r[1], r[2], r[3], r[1] + r[3],
            ("   [X] " + ",".join(sorted(set(notes)))) if notes else "", extra))
        if notes:
            problems.append("%s: %s" % (hid, ",".join(sorted(set(notes)))))
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            if overlap(rects[i][1], rects[j][1]):
                problems.append("%s: %s x %s 重叠" % (fname, rects[i][0], rects[j][0]))
                print("    [X] %s x %s 重叠" % (rects[i][0], rects[j][0]))
    print()

print("=" * 76)
print("钉死地标（A1/A2/A3 完全相同）：")
print("  河 (0,0,1600,112) | 坝 (196,34,120,62)")
print("  田东 (1000,130,240,176) | 田西 (1272,130,240,176)")
print("  老井 (900,545) r16 | 老槐 (852,505) r9 | 界碑 (696,594,8,16)")
print("  主路/支路：五帧完全相同")
print()
if problems:
    print("有问题：")
    for p in problems:
        print("  !", p)
else:
    print("LAYOUT OK - 五帧地标与路完全不动，屋体不压路/河/碑，房子不重叠。")
