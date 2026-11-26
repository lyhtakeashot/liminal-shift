# -*- coding: utf-8 -*-
"""A1–A3 重排（v5 世界 4800×3600）帧生成器 + 全量几何自检。

任务书：docs/PROMPT-a1-a3-rebuild-exec.md
只重写 data/frames.json 里 a1_1926 / a2_1951 / a3_1976 三个帧对象；
a4_2001 / a5_2026 / world / 顶层字段一字不动（写盘前逐字节验）。

用法：
  python lab/_a13_plan.py           # 只算 + 自检，打印报告，不写盘
  python lab/_a13_plan.py --write   # 写回 data/frames.json
"""
import io
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FRAMES = os.path.join(ROOT, "data", "frames.json")
HOUSES = os.path.join(ROOT, "_ref", "houses", "houses_data.json")

TILE = 32
W, H = 4800, 3600
GW = W // TILE

# ---------- 权威河：与 _ref/houses/_design_v5.py:59 river_depth() 逐字同式 ----------
MILL_X0, MILL_X1 = 38, 55


def river_depth(x):
    base = (5.5
            + 1.5 * math.sin(x / 13.0 + 0.6)
            + 0.8 * math.sin(x / 5.3 + 2.1))
    c = (MILL_X0 + MILL_X1) * 0.5
    base += math.exp(-((x - c) / 16.0) ** 2) * 8.0
    return int(round(max(4, min(15, base))))


RIVER_Y = {x: (river_depth(x) + 1) * TILE for x in range(GW)}
RIVER_PTS = [[x * TILE, RIVER_Y[x]] for x in range(GW)] + [[W, 0], [0, 0]]

# ---------- 锚点（照抄 lab/_a5_v5fix.py） ----------
OX, OY = 2048, 1664
R_IN, ROAD_W, R_OUT = 176, 128, 304
ROAD_N, ROAD_S = OY - ROAD_W // 2, OY + ROAD_W // 2      # 1600 / 1728
LANE_X0, LANE_X1 = OX - ROAD_W // 2, OX + ROAD_W // 2    # 1984 / 2112
LANE_TOP = 288
LANE_N_BOT, LANE_S_TOP = OY - R_OUT, OY + R_OUT          # 1360 / 1968
WELL = (2048, 832)
TREE = (OX, OY)
DAM = (384, 96, 256, 128)
FIELD = (3600, 320, 880, 384)

# ---------- 本线落位 ----------
# 磨坊：旧 (1216,448) 会压进延长后的引水湾（cols 44..49 河下沿 y=512）。
# 抬到 y=512 ⇒ 北墙正好压在河沿上（水车贴河），且(1400,1120) 在三帧都仍是空地。
MILL_POS = (1216, 512)
SHEN_POS = (64, 416)     # 与 A4/A5 四合院同址（任务书 §1）
ZHOU_POS = (576, 1920)   # 对齐 A5 小学地块
LU_POS = (2304, 768)     # 任务书 §1 未给新址；原址不压河/环道/车道，原地不动

FRAME_SPEC = [
    # id, 磨坊, 沈家, 周家, 陆家, 井(label, solid), 槐半径, 井 reach, 槐 reach
    ("a1_1926", "mill_a1", "shen_a1", "zhou_house", "lu_house",
     "老井", True, 32, 80, 68),
    ("a2_1951", "mill_a2", "shen_a2", "zhou_a2", "lu_a2",
     "老井 · 石板", False, 64, 80, 80),
    ("a3_1976", "mill_a3", "shen_a3", "zhou_a3", "lu_a3",
     "老井 · 三层水泥", False, 96, 88, 88),
]

RIVER_COLOR = {"a1_1926": "#3f5f6e", "a2_1951": "#3f5f6e", "a3_1976": "#4a6a60"}
ROAD_COLOR = {"a1_1926": "#8a7a5a", "a2_1951": "#8a7a5a", "a3_1976": "#8a7a5a"}
FIELD_COLOR = {"a1_1926": "#7d8a3e", "a2_1951": "#78863c", "a3_1976": "#6b6440"}

# A1 零散小田（A2 起归并成整块 [3600,320,880,384]）；P5 特意包住热点 (4040,512)
FIELD_A1 = [
    (3616, 352, 192, 128),
    (3840, 352, 192, 128),
    (4064, 352, 256, 128),
    (3616, 512, 160, 160),
    (3808, 496, 256, 176),
    (4096, 512, 224, 160),
]

# 南侧补满（村界/大田）。全部 label:"" + solid:false ⇒ 走田瓦、可通行。
# y 起 1984：主路南沿 1728、环岛外圈最低 1968，都不压。
SOUTH_FILL = [
    (64, 1984, 512, 1568),     # 西南（周家西侧）
    (960, 1984, 768, 1568),    # 西南（周家东侧）
    (576, 2176, 384, 1376),    # 周家正南
    (1792, 1984, 192, 1568),   # 南车道西肩
    (2176, 1984, 2624, 1568),  # 东南整片
]

HD = json.load(io.open(HOUSES, encoding="utf-8"))
BY_ID = {h["id"]: h for h in HD}


# ==================== 几何小工具 ====================
def rect(x, y, w, h):
    """(x0, y0, x1, y1) 含端点。"""
    return (x, y, x + w - 1, y + h - 1)


def r2(t):
    return rect(t[0], t[1], t[2], t[3])


def overlap(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0]) + 1
    h = min(a[3], b[3]) - max(a[1], b[1]) + 1
    return max(0, w) * max(0, h)


def lot_rect(hid, pos):
    l = BY_ID[hid]["lot"]
    return (pos[0], pos[1],
            pos[0] + (l[2] - l[0] + 1) * TILE - 1,
            pos[1] + (l[3] - l[1] + 1) * TILE - 1)


def circle_poly(c, r, n=72):
    return [[int(round(c[0] + r * math.cos(2 * math.pi * i / n))),
             int(round(c[1] + r * math.sin(2 * math.pi * i / n)))] for i in range(n)]


def in_poly(p, poly):
    n = len(poly)
    inside = False
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        y1, y2 = a[1], b[1]
        if (y1 > p[1]) != (y2 > p[1]):
            xin = (b[0] - a[0]) * (p[1] - y1) / (y2 - y1) + a[0]
            if p[0] < xin:
                inside = not inside
    return inside


def river_max_y(r):
    return max(RIVER_Y[x] for x in range(max(0, r[0] // TILE), min(GW - 1, r[2] // TILE) + 1))


def rect_hits_poly(r, poly, step=8.0):
    hits = 0
    y = float(r[1])
    while y < r[3]:
        x = float(r[0])
        while x < r[2]:
            if in_poly((x + step * 0.5, y + step * 0.5), poly):
                hits += 1
            x += step
        y += step
    return hits


# ---- 墙网格：逐字照抄 scripts/house_shape.gd grid_of() ----
def grid_of(hid):
    data = BY_ID[hid]
    lot = data["lot"]
    x0, y0, x1, y1 = int(lot[0]), int(lot[1]), int(lot[2]), int(lot[3])
    interior = set()
    for w in data.get("wings", []):
        wx, wy, ww, wh = int(w[0]), int(w[1]), int(w[2]), int(w[3])
        for j in range(wy + 1, wy + wh - 1):
            for i in range(wx + 1, wx + ww - 1):
                interior.add((i, j))

    def is_wall(i, j):
        if (i, j) in interior:
            return False
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (i + d[0], j + d[1]) in interior:
                return True
        return False

    part = set()
    for p in data.get("partitions", []):
        px1, py1, px2, py2 = int(p[0]), int(p[1]), int(p[2]), int(p[3])
        if px1 == px2:
            for j in range(min(py1, py2), max(py1, py2) + 1):
                part.add((px1, j))
        else:
            for i in range(min(px1, px2), max(px1, px2) + 1):
                part.add((i, py1))
    doors = {(int(d[0]), int(d[1])) for d in data.get("doors", [])}
    gates = {(int(g[0]), int(g[1])) for g in data.get("gate", [])}
    rows = []
    for j in range(y0, y1 + 1):
        row = ""
        for i in range(x0, x1 + 1):
            if (i, j) in gates:
                row += "G"
            elif (i, j) in doors:
                row += "D"
            elif (i, j) in part or is_wall(i, j):
                row += "#"
            elif (i, j) in interior:
                row += "."
            else:
                row += " "
        rows.append(row)
    return rows, x0, y0


def wall_rects(hid, pos):
    rows, x0, y0 = grid_of(hid)
    out = []
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == "#":
                out.append(rect(pos[0] + (x0 + i) * TILE, pos[1] + (y0 + j) * TILE, TILE, TILE))
    return out


def gate_cells(hid):
    return [(int(g[0]), int(g[1])) for g in BY_ID[hid].get("gate", [])]


# ==================== 组帧 ====================
def build_frame(fid, mill, shen, zhou, lu, well_label, well_solid, tree_r,
                well_reach, tree_reach):
    rc = RIVER_COLOR[fid]
    kc = ROAD_COLOR[fid]
    fc = FIELD_COLOR[fid]
    shapes = []
    shapes.append({"type": "polygon", "points": RIVER_PTS, "color": rc,
                   "label": "河", "solid": True})
    shapes.append({"type": "rect", "rect": [DAM[0], DAM[1], DAM[2], DAM[3]],
                   "color": "#6a5648", "label": "坝", "solid": True})
    shapes.append({"type": "rect", "rect": [0, ROAD_N, OX - R_OUT, ROAD_W],
                   "color": kc, "label": "路", "road": True})
    shapes.append({"type": "rect", "rect": [OX + R_OUT, ROAD_N, W - (OX + R_OUT), ROAD_W],
                   "color": kc, "label": "路", "road": True})
    shapes.append({"type": "polygon",
                   "points": [[LANE_X0, LANE_TOP], [LANE_X1, LANE_TOP],
                              [LANE_X1, LANE_N_BOT], [LANE_X0, LANE_N_BOT]],
                   "color": kc, "label": "路", "solid": False})
    shapes.append({"type": "polygon",
                   "points": [[LANE_X0, LANE_S_TOP], [LANE_X1, LANE_S_TOP],
                              [LANE_X1, H], [LANE_X0, H]],
                   "color": kc, "label": "路", "solid": False})
    shapes.append({"type": "polygon", "points": circle_poly(TREE, R_OUT),
                   "color": kc, "label": "路", "solid": False})
    shapes.append({"type": "polygon", "points": circle_poly(TREE, R_IN),
                   "color": "#6b7a4a", "label": "岛", "solid": False})
    shapes.append({"type": "circle", "center": [WELL[0], WELL[1]], "radius": 32,
                   "color": "#4a4a46", "label": well_label, "solid": well_solid})
    shapes.append({"type": "circle", "center": [TREE[0], TREE[1]], "radius": tree_r,
                   "color": "#3f6b3a", "label": "老槐", "solid": False})

    fields = FIELD_A1 if fid == "a1_1926" else [FIELD]
    for f in fields:
        shapes.append({"type": "rect", "rect": [f[0], f[1], f[2], f[3]],
                       "color": fc, "label": "", "solid": False})
    for f in SOUTH_FILL:
        shapes.append({"type": "rect", "rect": [f[0], f[1], f[2], f[3]],
                       "color": fc, "label": "", "solid": False})

    for hid, pos in ((mill, MILL_POS), (shen, SHEN_POS), (zhou, ZHOU_POS), (lu, LU_POS)):
        shapes.append({"type": "house", "id": hid, "pos": [pos[0], pos[1]], "solid": True})

    # 水簿：磨坊账桌。保持与旧数据的相对偏移（A1 +112,+48；A2/A3 +176,+48）。
    desk_dx = {"a1_1926": 112, "a2_1951": 176, "a3_1976": 176}[fid]
    hotspots = [
        {"pos": [WELL[0], WELL[1]], "title": well_label, "reach": well_reach,
         "text": None},
        {"pos": [TREE[0], TREE[1]], "title": "老槐", "reach": tree_reach, "text": None},
        {"pos": [512, 160], "title": "坝", "reach": 140, "text": None},
        {"pos": [4040, 512], "title": "田", "reach": 96, "text": None},
        {"pos": [MILL_POS[0] + desk_dx, MILL_POS[1] + 48], "title": "水簿", "reach": 68,
         "diary": "mill", "text": None},
    ]
    return shapes, hotspots


# ==================== 自检 ====================
def main():
    raw = io.open(FRAMES, encoding="utf-8").read()
    doc = json.loads(raw)
    assert json.dumps(doc, indent=2, ensure_ascii=False) == raw, "原文件不是 json.dumps(indent=2) 口径"

    frames = doc["frames"]
    by_id = {f["id"]: f for f in frames}
    a4 = by_id["a4_2001"]
    a5 = by_id["a5_2026"]

    # 旧基线：优先读 lab/_a13_head.json（开工时 HEAD 版快照），保证脚本可重复运行
    BASE = os.path.join(HERE, "_a13_head.json")
    if os.path.exists(BASE):
        base = json.loads(io.open(BASE, encoding="utf-8-sig").read())
        print("BASELINE lab/_a13_head.json")
    else:
        base = doc
        print("BASELINE 当前 frames.json（无快照，旧/新对比无意义）")
    base_by_id = {f["id"]: f for f in base["frames"]}

    fails = []

    def ck(name, cond, detail=""):
        print(("PASS " if cond else "FAIL ") + name + (("  " + detail) if detail else ""))
        if not cond:
            fails.append(name)

    # ---------- 0. 河 / 环岛 / 内岛 与 A5 逐点相同 ----------
    def get_poly(fr, label):
        for s in fr["shapes"]:
            if s.get("type") == "polygon" and s.get("label") == label:
                return s["points"]
        return None

    a4_river = get_poly(a4, "河")
    diff = sum(1 for i in range(min(len(a4_river), len(RIVER_PTS)))
               if a4_river[i] != RIVER_PTS[i])
    ck("河 152 点与 A4/A5 逐点相同", len(RIVER_PTS) == 152 and len(a4_river) == 152 and diff == 0,
       "len=%d a4_len=%d mismatches=%d" % (len(RIVER_PTS), len(a4_river), diff))
    ck("河铺到 x=4800", RIVER_PTS[-2][0] == 4800)

    def get_ring(fr):
        # 「路」有多条：引道 rect 不算，车道 polygon 4 点，环道 polygon 72 点
        for s in fr["shapes"]:
            if s.get("type") == "polygon" and s.get("label") == "路" and len(s["points"]) == 72:
                return s["points"]
        return None

    ring = circle_poly(TREE, R_OUT)
    island = circle_poly(TREE, R_IN)
    ck("环道 polygon 与 A4 逐点相同", get_ring(a4) == ring, str((get_ring(a4) or [])[:2]))
    ck("A4 环道也是 72 点", get_ring(a4) is not None and len(get_ring(a4)) == 72)
    ck("内岛 polygon 与 A4 逐点相同", get_poly(a4, "岛") == island)

    # ---------- 1. 组帧 ----------
    new_frames = []
    for (fid, mill, shen, zhou, lu, wl, ws, tr, wr, trr) in FRAME_SPEC:
        shapes, hots = build_frame(fid, mill, shen, zhou, lu, wl, ws, tr, wr, trr)
        src = base_by_id[fid]
        # 文案一个字不许改：从基线帧按 title 取回 text（水簿/井/槐/坝/田）
        old_hots = {h["title"]: h for h in src["hotspots"]}
        for h in hots:
            old = old_hots[h["title"]]
            h["text"] = old["text"]
            for k in old:
                if k not in h:
                    h[k] = old[k]
        # 键顺序与 a4/a5 对齐：id, year, ground, _note, shapes, hotspots
        fr = {"id": src["id"], "year": src["year"], "ground": src["ground"]}
        fr["_note"] = ("v5 世界重排（docs/PROMPT-a1-a3-rebuild-exec.md）：环岛/车道/引道逐点照抄 A4，"
                       "井槐沈家周家五帧同址；磨坊抬到 y=512 让开引水湾；路面材质逐年待美术补图。")
        fr["shapes"] = shapes
        fr["hotspots"] = hots
        new_frames.append(fr)

    nf = {f["id"]: f for f in new_frames}

    # ---------- 2. 房屋 lot 与冲突 ----------
    world = doc["world"]
    solid_polys = {"河": RIVER_PTS}
    road_rects = [r2((0, ROAD_N, OX - R_OUT, ROAD_W)), r2((OX + R_OUT, ROAD_N, W - (OX + R_OUT), ROAD_W))]
    lane_rects = [rect(LANE_X0, LANE_TOP, LANE_X1 - LANE_X0, LANE_N_BOT - LANE_TOP),
                  rect(LANE_X0, LANE_S_TOP, LANE_X1 - LANE_X0, H - LANE_S_TOP)]

    for fid, mill, shen, zhou, lu, wl, ws, tr, wr, trr in FRAME_SPEC:
        fr = nf[fid]
        lots = {}
        for s in fr["shapes"]:
            if s["type"] == "house":
                lots[s["id"]] = lot_rect(s["id"], tuple(s["pos"]))
        for hid, lr in lots.items():
            ck("%s %s lot 在世界内" % (fid, hid), lr[0] >= 0 and lr[1] >= 0 and lr[2] < W and lr[3] < H, str(lr))
            rb = river_max_y(lr)
            ck("%s %s 不压河" % (fid, hid), river_max_y(lr) < lr[1] or rect_hits_poly(lr, RIVER_PTS, 16) == 0,
               "lot.top=%d 河下沿(区间)=%d" % (lr[1], rb))
            for rname, rr in (("坝", rect(*DAM)), ("主路西", road_rects[0]), ("主路东", road_rects[1]),
                              ("车道北", lane_rects[0]), ("车道南", lane_rects[1])):
                ck("%s %s 不压%s" % (fid, hid, rname), overlap(lr, rr) == 0, str(overlap(lr, rr)))
            ck("%s %s 不压环道/内岛" % (fid, hid),
               rect_hits_poly(lr, ring, 8) == 0 and rect_hits_poly(lr, island, 8) == 0)
        # 房与房不重叠
        ids = sorted(lots)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                ck("%s %s/%s 不重叠" % (fid, ids[i], ids[j]), overlap(lots[ids[i]], lots[ids[j]]) == 0)
        # 门洞中心可站 + 不朝车道/环道开
        for hid, lr in lots.items():
            pos = (lr[0], lr[1])
            for (gx, gy) in gate_cells(hid):
                gp = (pos[0] + gx * TILE + TILE // 2, pos[1] + gy * TILE + TILE // 2)
                ck("%s %s 门 %s 不朝车道/环道" % (fid, hid, str(gp)),
                   not any(rr[0] <= gp[0] <= rr[2] and rr[1] <= gp[1] <= rr[3] for rr in lane_rects)
                   and not in_poly(gp, ring))
                # 门洞中心不能被任何墙盖住（自己或其他房子的墙）
                blocked = False
                for h2, l2 in lots.items():
                    p2 = (l2[0], l2[1])
                    for wr in wall_rects(h2, p2):
                        if wr[0] - 0 <= gp[0] <= wr[2] and wr[1] <= gp[1] <= wr[3]:
                            blocked = True
                ck("%s %s 门 %s 没有墙" % (fid, hid, str(gp)), not blocked)

    # ---------- 3. 田/南片：不压河、不压路 ----------
    for fid in ("a1_1926", "a2_1951", "a3_1976"):
        fr = nf[fid]
        fields = [s for s in fr["shapes"] if s["type"] == "rect" and s.get("label") == ""]
        ck("%s 田/南片数量 = %d" % (fid, len(fields)), len(fields) == (6 + 5 if fid == "a1_1926" else 1 + 5))
        for i, s in enumerate(fields):
            rr = r2(tuple(s["rect"]))
            tag = "%s 田rect%d %s" % (fid, i, str(rr))
            ck(tag + " 世界内", rr[0] >= 0 and rr[1] >= 0 and rr[2] < W and rr[3] < H)
            ck(tag + " 不压河", rect_hits_poly(rr, RIVER_PTS, 8) == 0,
               "河下沿(区间)=%d top=%d" % (river_max_y(rr), rr[1]))
            ck(tag + " 不压环道/内岛", rect_hits_poly(rr, ring, 8) == 0 and rect_hits_poly(rr, island, 8) == 0)
            ck(tag + " 不压主路/车道",
               overlap(rr, road_rects[0]) == 0 and overlap(rr, road_rects[1]) == 0
               and overlap(rr, lane_rects[0]) == 0 and overlap(rr, lane_rects[1]) == 0)
            ck(tag + " 不压房子",
               all(overlap(rr, lot_rect(s2["id"], tuple(s2["pos"]))) == 0
                   for s2 in fr["shapes"] if s2["type"] == "house"))
        # 田 hotspot 落在田里
        hot = [h for h in fr["hotspots"] if h["title"] == "田"][0]
        p = (hot["pos"][0], hot["pos"][1])
        ck("%s 田热点 (4040,512) 落在田瓦上" % fid,
           any(s["rect"][0] <= p[0] < s["rect"][0] + s["rect"][2]
               and s["rect"][1] <= p[1] < s["rect"][1] + s["rect"][3] for s in fields))

    # ---------- 4. is_free 复刻（探测 28×28） ----------
    def frame_solids(fr):
        rs = []
        polys = []
        for s in fr["shapes"]:
            if s["type"] == "house":
                rs += wall_rects(s["id"], tuple(s["pos"]))
            elif not s.get("solid", False):
                continue
            elif s["type"] == "rect":
                rr = s["rect"]
                rs.append(rect(rr[0], rr[1], rr[2], rr[3]))
            elif s["type"] == "circle":
                c, r = s["center"], s["radius"]
                rs.append(rect(c[0] - r, c[1] - r, 2 * r, 2 * r))
            elif s["type"] == "polygon":
                polys.append(s["points"])
        return rs, polys

    def is_free(fr, p):
        sol, polys = frame_solids(fr)
        for poly in polys:
            for dx, dy in ((-14, -14), (14, -14), (-14, 14), (14, 14), (0, 0)):
                if in_poly((p[0] + dx, p[1] + dy), poly):
                    return False
        for rr in sol:
            if p[0] + 14 > rr[0] and p[0] - 14 < rr[2] + 1 and p[1] + 14 > rr[1] and p[1] - 14 < rr[3] + 1:
                return False
        return True

    for p in ((1400, 1120), (1400, 1300)):
        for fid in ("a1_1926", "a2_1951", "a3_1976"):
            ck("%s 试验点 %s 可站" % (fid, str(p)), is_free(nf[fid], p))

    # ---------- 5. 井/槐/沈家/周家 五帧同址 ----------
    for probe in ("井", "槐"):
        pass
    for fid in ("a1_1926", "a2_1951", "a3_1976"):
        fr = nf[fid]
        w = [s for s in fr["shapes"] if s["type"] == "circle" and s["label"].startswith("老井")][0]
        t = [s for s in fr["shapes"] if s["type"] == "circle" and s["label"] == "老槐"][0]
        ck("%s 井 (2048,832)" % fid, w["center"] == [2048, 832], str(w["center"]))
        ck("%s 槐 (2048,1664)" % fid, t["center"] == [2048, 1664], str(t["center"]))
        shen = [s for s in fr["shapes"] if s["type"] == "house" and s["id"].startswith("shen")][0]
        zhou = [s for s in fr["shapes"] if s["type"] == "house" and (s["id"].startswith("zhou"))][0]
        ck("%s 沈家 (64,416)" % fid, shen["pos"] == [64, 416], str(shen["pos"]))
        ck("%s 周家 (576,1920)" % fid, zhou["pos"] == [576, 1920], str(zhou["pos"]))

    # ---------- 6. 热点点得到 + 文字没改 ----------
    for fid in ("a1_1926", "a2_1951", "a3_1976"):
        fr = nf[fid]
        old = {h["title"]: h["text"] for h in base_by_id[fid]["hotspots"]}
        ck("%s 热点标题集合不变" % fid, set(h["title"] for h in fr["hotspots"]) == set(old),
           str([h["title"] for h in fr["hotspots"]]))
        for h in fr["hotspots"]:
            ck("%s 热点 %s 文案逐字未改" % (fid, h["title"]), h["text"] == old[h["title"]])
            p = (h["pos"][0], h["pos"][1])
            found = False
            for y in range(int(p[1] - h["reach"]), int(p[1] + h["reach"]) + 1, 8):
                for x in range(int(p[0] - h["reach"]), int(p[0] + h["reach"]) + 1, 8):
                    if (x - p[0]) ** 2 + (y - p[1]) ** 2 <= h["reach"] ** 2 and is_free(fr, (x, y)):
                        found = True
                        break
                if found:
                    break
            ck("%s 热点 %s reach 内有可站位" % (fid, h["title"]), found)

    # ---------- 7. 空气墙（房屋 lot ∪ 山体 bbox）双向格数 ----------
    def airwall(fr):
        m = set()
        for s in fr["shapes"]:
            box = None
            if s["type"] == "house":
                box = lot_rect(s["id"], tuple(s["pos"]))
            elif s["type"] == "polygon" and s.get("label") == "山":
                xs = [p[0] for p in s["points"]]
                ys = [p[1] for p in s["points"]]
                box = (min(xs), min(ys), max(xs), max(ys))
            if box is None:
                continue
            for gy in range(box[1] // TILE, box[3] // TILE + 1):
                for gx in range(box[0] // TILE, box[2] // TILE + 1):
                    m.add((gx, gy))
        return m

    m4 = airwall(a4)
    print("AIRWALL a4=%d cells" % len(m4))
    for fid in ("a1_1926", "a2_1951", "a3_1976"):
        old_m = airwall(base_by_id[fid])
        new_m = airwall(nf[fid])
        o_a = len(old_m - m4)
        o_b = len(m4 - old_m)
        n_a = len(new_m - m4)
        n_b = len(m4 - new_m)
        print("AIRWALL_A4_vs_%s 旧: A4独有 %d / %s独有 %d   →  新: A4独有 %d / %s独有 %d"
              % (fid, o_b, fid, o_a,
                 n_b, fid, n_a))
        ck("%s 空气墙双向格数比旧的小" % fid, n_a < o_a or n_b < o_b,
           "旧 %d+%d 新 %d+%d" % (o_a, o_b, n_a, n_b))

    # ---------- 8. S1：a4/a5/world 零变化 ----------
    d2 = dict(doc)
    d2["frames"] = [nf[f["id"]] if f["id"] in nf else f for f in frames]
    ck("a4_2001 零变化", d2["frames"][3] == base["frames"][3])
    ck("a5_2026 零变化", d2["frames"][4] == base["frames"][4])
    ck("world/safe/start 零变化",
       all(d2[k] == doc[k] for k in doc if k != "frames"))
    ck("顶层键顺序不变", list(d2.keys()) == list(base.keys()))
    ck("world/safe/start 与基线逐字段相同", all(d2[k] == base[k] for k in base if k != "frames"))

    # ---------- 9. 概况 ----------
    for fid in ("a1_1926", "a2_1951", "a3_1976"):
        fr = nf[fid]
        sol, polys = frame_solids(fr)
        print("FRAME %s shapes=%d 手写solid=%d 房墙=%d hotspots=%d" % (
            fid, len(fr["shapes"]),
            sum(1 for s in fr["shapes"] if s.get("solid") and s["type"] != "house"),
            len(sol), len(fr["hotspots"])))

    out = json.dumps(d2, indent=2, ensure_ascii=False)
    print("BYTES old=%d new=%d" % (len(raw.encode("utf-8")), len(out.encode("utf-8"))))
    print("A13_PLAN_DONE fails=%d" % len(fails))
    if fails:
        print("FAILS: " + str(fails[:10]))
        return 1

    if "--write" in sys.argv:
        assert json.dumps(json.loads(out), indent=2, ensure_ascii=False) == out, "round-trip 不一致"
        io.open(FRAMES, "w", encoding="utf-8", newline="\n").write(out)
        print("WROTE data/frames.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())