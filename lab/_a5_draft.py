# -*- coding: utf-8 -*-
"""A5 (2026) 布局草案 v4：标准环岛几何 —— 环岛就在十字路口，树在环心。

几何约定（v4 修正 v3.1 的真问题）：
  v3.1 的 E-W 主路画在 y=1696，只是从环岛南侧"擦过"，真正的十字路口在 (2048,1696)，
  与环心 (2048,1456) 差 240px ⇒ 路口不在环岛里，不成立。
  v4：E-W 主路轴线 = 环心 y = 1456；N-S 车道轴线 = 环心 x = 2048。
      两条引道都在**环岛外圆处断开**（标准环岛：引道与环道相切，不进内岛），
      内岛 R_IN=176 只装得下 A5 树冠 r160（余 16px），环道宽 128 = 路宽，外圆 R_OUT=304。
      ⇒ 两条路的轴线交点 = 环心 = 树 = 十字路口中央。路不为树绕，是路绕岛。

只读脚本：产出 lab/_a5_draft.json + 自检报告。不改任何已跟踪文件。"""
import json, io, math

TILE = 32
W, H = 4800, 3600

# ---------------- 固定锚点 ----------------
OX, OY = 2048, 1456             # 环心 = 树 = 十字路口中央
TREE = (OX, OY)
R_IN = 176                       # 内岛半径（容 A5 树冠 r160）
ROAD_W = 128                     # 环道宽 = 路宽
R_OUT = R_IN + ROAD_W            # 304 外圆

ROAD_N = OY - ROAD_W // 2        # 1392 主路带北沿
ROAD_S = OY + ROAD_W // 2        # 1520 主路带南沿（不含）
LANE_X0, LANE_X1 = OX - ROAD_W // 2, OX + ROAD_W // 2   # 1984..2112
LANE_TOP = 288                  # 北段顶端（河边）
ROAD_W_X0 = OX - R_OUT           # 1744 西引道右端
ROAD_E_X0 = OX + R_OUT           # 2352 东引道左端
LANE_N_BOT = OY - R_OUT          # 1152 北段下端（环岛外圆北缘）
LANE_S_TOP = OY + R_OUT          # 1760 南段上端（环岛外圆南缘）

WELL = (2048, 832)
WELL_R = 48

SCHOOL_POS = (448, 288)
MARKET_POS = (2128, 225)
TOYSHOP_POS = (2128, 1856)
LOT = {"school": (0, 0, 37, 29), "market": (0, 0, 41, 27), "toyshop": (0, 0, 20, 19)}
LOT_SIZE = {"lu_house": (20, 13), "zhou_house": (12, 7)}

def lot_world(pos, lot):
    x0, y0, x1, y1 = lot
    return (pos[0] + x0 * TILE, pos[1] + y0 * TILE,
            pos[0] + (x1 + 1) * TILE - 1, pos[1] + (y1 + 1) * TILE - 1)

HOUSES = {"school": lot_world(SCHOOL_POS, LOT["school"]),
          "market": lot_world(MARKET_POS, LOT["market"]),
          "toyshop": lot_world(TOYSHOP_POS, LOT["toyshop"])}

def rect(x, y, w, h):
    return (x, y, x + w - 1, y + h - 1)

def overlap(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0]) + 1
    h = min(a[3], b[3]) - max(a[1], b[1]) + 1
    return max(0, w) * max(0, h)

def dist_rect_pt(r, p):
    dx = max(r[0] - p[0], 0, p[0] - r[2])
    dy = max(r[1] - p[1], 0, p[1] - r[3])
    return math.hypot(dx, dy)

def circle_poly(c, r, n=72):
    return [[int(round(c[0] + r * math.cos(2 * math.pi * i / n))),
             int(round(c[1] + r * math.sin(2 * math.pi * i / n)))] for i in range(n)]

def river_surface(x):
    base = 64 + 96 * (0.5 + 0.5 * math.sin(x / 900.0)) + 40 * math.sin(x / 260.0 + 1.1)
    cap = 256 if x < 400 else (288 if x > 3500 else 192)
    return int(min(base, cap))

def river_poly():
    pts = [[x, river_surface(x)] for x in range(0, W + 1, 32)]
    pts += [[W, 0], [0, 0]]
    return pts

RIVER = river_poly()
RIVER_S = max(p[1] for p in RIVER)

ROAD_W_RECT = rect(0, ROAD_N, W, ROAD_W)          # 西引道 + 东引道（同一 y 带）
ROAD_RECTS = [rect(0, ROAD_N, ROAD_W_X0, ROAD_W),   # 西段 x0..1744
              rect(ROAD_E_X0, ROAD_N, W - ROAD_E_X0, ROAD_W)]  # 东段 x2352..4800
LANE_N = rect(LANE_X0, LANE_TOP, ROAD_W, LANE_N_BOT - LANE_TOP + 1)
LANE_S = rect(LANE_X0, LANE_S_TOP, ROAD_W, H - LANE_S_TOP)
FIELD_RECT = rect(3600, 320, 880, 384)
DAM_RECT = rect(64, 96, 256, 128)
PARK = (1440, 1792)
PARK_RECT = rect(PARK[0], PARK[1], 512, 256)
CAR_RECTS = [rect(PARK[0] + 16 + i * 160, PARK[1] + 16, 128, 224) for i in range(3)]
# 界碑：小学西墙实墙格（x=1 列、row18 是 partition '#'；x=0 列全程是院子空地）
STELE = (SCHOOL_POS[0] + 1 * TILE, SCHOOL_POS[1] + 18 * TILE)
# 红绿灯：车道中线 x=2048 往东 64px（两格≈两米），贴超市西墙，紧邻井的沥青补丁
TL = (2112, 816)
HILLS = [(4288, 2624, 512, 384), (64, 2624, 512, 384), (4288, 3040, 384, 288)]
SIGNS = [(800, 1520), (1600, 1520), (2600, 1520), (3400, 1520)]

# ---------------- 装饰房自动排布 ----------------
def decor_layout(count=14, gap=96, band=720):
    placed = []
    blocked = (list(HOUSES.values()) + [FIELD_RECT, DAM_RECT, PARK_RECT] + ROAD_RECTS
               + [LANE_N, LANE_S] + [rect(hx, hy, hw, hh) for (hx, hy, hw, hh) in HILLS])

    def try_place(pid, pos):
        w, h = LOT_SIZE[pid]
        r = rect(pos[0], pos[1], w * TILE, h * TILE)
        if r[0] < 0 or r[1] < 0 or r[2] > W - 1 or r[3] > H - 1:
            return False
        if min(pos[0], pos[1], W - 1 - r[2], H - 1 - r[3]) > band:
            return False
        if r[1] < RIVER_S + 32:
            return False
        for rr in blocked:
            if overlap(r, rr) > 0:
                return False
        # 与主屋也要留缝（不贴墙）
        for nm, hr2 in HOUSES.items():
            dx = max(r[0] - hr2[2], hr2[0] - r[2], 0)
            dy = max(r[1] - hr2[3], hr2[1] - r[3], 0)
            if math.hypot(dx, dy) < 48:
                return False
        if dist_rect_pt(r, TREE) < R_OUT + 48:
            return False
        for _, _, r2 in placed:
            if overlap(r, r2) > 0:
                return False
            dx = max(r[0] - r2[2], r2[0] - r[2], 0)
            dy = max(r[1] - r2[3], r2[1] - r[3], 0)
            if math.hypot(dx, dy) < gap:
                return False
        placed.append((pid, pos, r))
        return True

    order = ["lu_house", "zhou_house"] * 10
    oi = 0
    for (ylo, yhi) in [(96, 1024), (1024, 2048), (2048, 2688), (2688, 3408)]:
        for y in range(ylo, yhi, 64):
            for x in list(range(64, W - 64, 64)) + list(range(W - 128, 64, -64)):
                if len(placed) >= count:
                    return placed
                pid = order[oi % len(order)]; oi += 1
                if try_place(pid, (x, y)):
                    break
    return placed

DECOR = decor_layout(14)

# ---------------- shapes（顺序即绘制顺序） ----------------
shapes = []
shapes.append({"type": "polygon", "points": RIVER, "color": "#4a6a60", "label": "河", "solid": True})
shapes.append({"type": "rect", "rect": [DAM_RECT[0], DAM_RECT[1], DAM_RECT[2] - DAM_RECT[0] + 1, DAM_RECT[3] - DAM_RECT[1] + 1],
                "color": "#6a5648", "label": "坝", "solid": True})
# 东西主路：两段引道（road:true 只这两块；引擎会把 road rect merge 成一个 bbox 贴整张路图）
for rr in ROAD_RECTS:
    shapes.append({"type": "rect", "rect": [rr[0], rr[1], rr[2] - rr[0] + 1, rr[3] - rr[1] + 1],
                    "color": "#56564f", "label": "路", "road": True})
# 南北车道：polygon，绝不写 road:true（否则 bbox merge 会把整片空地刷成柏油）
shapes.append({"type": "polygon", "points": [[LANE_X0, LANE_TOP], [LANE_X1, LANE_TOP], [LANE_X1, LANE_N_BOT], [LANE_X0, LANE_N_BOT]],
                "color": "#56564f", "label": "路", "solid": False})
shapes.append({"type": "polygon", "points": [[LANE_X0, LANE_S_TOP], [LANE_X1, LANE_S_TOP], [LANE_X1, H], [LANE_X0, H]],
                "color": "#56564f", "label": "路", "solid": False})
# 环岛：沥青外圈（盖住路面）＋ 中心岛绿地（最后画）
shapes.append({"type": "polygon", "points": circle_poly(TREE, R_OUT), "color": "#56564f", "label": "路", "solid": False})
shapes.append({"type": "polygon", "points": circle_poly(TREE, R_IN), "color": "#6b7a4a", "label": "岛", "solid": False})
# 井 / 老槐
shapes.append({"type": "circle", "center": list(WELL), "radius": WELL_R, "color": "#3a3a38",
                "label": "老井 · 沥青补丁", "solid": False})
shapes.append({"type": "circle", "center": list(TREE), "radius": 160, "color": "#3d5230",
                "label": "老槐", "solid": False})
# 界碑（嵌小学西墙实墙格）／红绿灯
shapes.append({"type": "rect", "rect": [STELE[0], STELE[1], 16, 32], "color": "#8a8278", "label": "碑", "solid": True})
shapes.append({"type": "rect", "rect": [TL[0], TL[1], 16, 16], "color": "#3a3a38", "label": "红绿灯", "solid": True})
# 停车场＋三个车位
shapes.append({"type": "polygon", "points": [[PARK[0], PARK[1]], [PARK[0] + 512, PARK[1]], [PARK[0] + 512, PARK[1] + 256], [PARK[0], PARK[1] + 256]],
                "color": "#6a6a68", "label": "停车场", "solid": False})
for cr in CAR_RECTS:
    shapes.append({"type": "polygon", "points": [[cr[0], cr[1]], [cr[2] + 1, cr[1]], [cr[2] + 1, cr[3] + 1], [cr[0], cr[3] + 1]],
                    "color": "#79796f", "label": "车位", "solid": False})
# 田（东北，唯一的无 label rect）
shapes.append({"type": "rect", "rect": [3600, 320, 880, 384], "color": "#6b6440", "label": "", "solid": False})
# 山（三块三角，做空间约束）
for (hx, hy, hw, hh) in HILLS:
    shapes.append({"type": "polygon", "points": [[hx, hy + hh], [hx + hw // 2, hy], [hx + hw, hy + hh]],
                    "color": "#5a6a4a", "label": "山", "solid": True})
# 路标（16x32，solid 必须 true，否则 _is_standing_rect=false ⇒ 既不在背景层画、
# 也进不了前景层 ⇒ 整个隐形）
for (sx, sy) in SIGNS:
    shapes.append({"type": "rect", "rect": [sx, sy, 16, 32], "color": "#7a6a52", "label": "路标", "solid": True})
# 三栋主屋
for pid, pos in (("school", SCHOOL_POS), ("market", MARKET_POS), ("toyshop", TOYSHOP_POS)):
    shapes.append({"type": "house", "id": pid, "pos": list(pos), "solid": True})
# 装饰房（空白房子/不可探索版）
for pid, pos, _r in DECOR:
    shapes.append({"type": "house", "id": pid, "pos": list(pos), "solid": True, "decor": True})

hotspots = [
    {"pos": list(WELL), "title": "老井 · 沥青补丁", "reach": 88,
     "text": "一块圆形的沥青补丁，铺在车道正中，颜色比旁边的路面深一层。补过不止一回，接缝一圈套一圈。卡车压过去的时候，补丁的边会轻轻往下陷一下。"},
    {"pos": list(TREE), "title": "老槐", "reach": 100,
     "text": "老槐树，一百岁。树干要三个人才围得住，树冠正好顶满环岛中间，车从四周绕过去。"},
    {"pos": [192, 160], "title": "坝", "reach": 140,
     "text": "一道石坝横在河身里。水面在坝前抬高了几寸，从坝顶漫过去。"},
    {"pos": [3600 + 440, 320 + 192], "title": "田", "reach": 96,
     "text": "田还在，只是没人种了。田埂被推平了一半，靠路那头堆着几垛建材。土还是干的。"},
    {"pos": [TL[0] + 8, TL[1] + 8], "title": "路口 · 红绿灯基座", "reach": 88,
     "text": "基座没立在路口正中，往东偏了两米。桩打不下去——底下是空的，只能贴着超市墙角立。地下的排水管到这里拐了个弯：地面是直的，地下还弯着。"},
    {"pos": [PARK[0] + 256, PARK[1] + 128], "title": "停车场", "reach": 96,
     "text": "路口四个角，三个盖了楼，只有这一块空着，画了三个车位。线是新刷的，白得有点刺眼。"},
    {"pos": [STELE[0] + 8, STELE[1] + 16], "title": "界碑", "reach": 68,
     "text": "围墙里嵌着半截石碑，碑面和砖面抹成了一个平，缝里塞着旧水泥。字磨得只剩一个「周」，旁边那个字只留着一道竖笔。石头底下的土比四周高出一小截。"},
]

frame = {"id": "a5_2026", "year": 2026, "ground": "#7a7a76", "shapes": shapes, "hotspots": hotspots}

# ================= 自检 =================
errs = []
for a in HOUSES:
    for b in HOUSES:
        if a < b and overlap(HOUSES[a], HOUSES[b]):
            errs.append("房子重叠 %s x %s" % (a, b))
for nm, hr in HOUSES.items():
    for rn, rr in (("主路西", ROAD_RECTS[0]), ("主路东", ROAD_RECTS[1]), ("竖路北", LANE_N), ("竖路南", LANE_S)):
        if overlap(hr, rr) > 0:
            errs.append("%s 压%s %d px²" % (nm, rn, overlap(hr, rr)))
    if hr[1] < RIVER_S:
        errs.append("%s 压河（河最南 %d）" % (nm, RIVER_S))
    if dist_rect_pt(hr, TREE) < R_OUT:
        errs.append("%s 压环岛外缘（距 %.0f < %d）" % (nm, dist_rect_pt(hr, TREE), R_OUT))
CROWN = rect(TREE[0] - 160, TREE[1] - 160, 320, 320)
for nm, hr in HOUSES.items():
    if overlap(CROWN, hr) > 0:
        errs.append("树冠压%s %d px²" % (nm, overlap(CROWN, hr)))
# 环岛几何自洽：引道在环岛外圆处断开，轴线交点 = 环心
if R_OUT - R_IN != ROAD_W:
    errs.append("环道宽 != 路宽")
if 160 > R_IN:
    errs.append("树冠 r160 > 内岛 R%d" % R_IN)
if ROAD_RECTS[0][2] != OX - R_OUT - 1:
    errs.append("西引道没在环岛外圆处断开")
if ROAD_RECTS[1][0] != OX + R_OUT:
    errs.append("东引道没在环岛外圆处断开")
if LANE_N[3] != OY - R_OUT or LANE_S[1] != OY + R_OUT:
    errs.append("南北车道没在环岛外圆处断开")
if (ROAD_N + ROAD_S) // 2 != OY or (LANE_X0 + LANE_X1) // 2 != OX:
    errs.append("两路轴线交点 != 环心")
# 井：在南北车道正中，东缘离超市西墙一道墙
if not (LANE_X0 <= WELL[0] <= LANE_X1 and LANE_TOP <= WELL[1] <= LANE_N_BOT):
    errs.append("井不在 N-S 车道内")
gap = HOUSES["market"][0] - (WELL[0] + WELL_R)
if gap != 32:
    errs.append("井到超市西墙 %d != 32" % gap)
# 界碑必须在小学实墙格上（复刻 house_shape.gd 的 grid_of 判定）
def _school_cell(cx, cy):
    sch = [h for h in json.load(io.open("_ref/houses/houses_data.json", encoding="utf-8"))
           if h["id"] == "school"][0]
    interior = set()
    for w in sch["wings"]:
        wx, wy, ww, wh = w
        for j in range(wy + 1, wy + wh - 1):
            for i in range(wx + 1, wx + ww - 1):
                interior.add((i, j))
    if (cx, cy) in {(g[0], g[1]) for g in sch["gate"]}:
        return "G"
    if (cx, cy) in {(d[0], d[1]) for d in sch["doors"]}:
        return "D"
    for p in sch["partitions"]:
        px1, py1, px2, py2 = p
        if px1 == px2:
            if cx == px1 and min(py1, py2) <= cy <= max(py1, py2):
                return "#"
        else:
            if cy == py1 and min(px1, px2) <= cx <= max(px1, px2):
                return "#"
    if (cx, cy) in interior:
        return "."
    for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if (cx + d[0], cy + d[1]) in interior:
            return "#"
    return " "

STELE_CELL = ((STELE[0] - SCHOOL_POS[0]) // TILE, (STELE[1] - SCHOOL_POS[1]) // TILE)
if _school_cell(*STELE_CELL) != "#":
    errs.append("界碑不在小学实墙格上：格%s 判定=%r" % (STELE_CELL, _school_cell(*STELE_CELL)))
# 停车场/车位：不压路、不压环岛
if overlap(PARK_RECT, ROAD_RECTS[0]) > 0 or overlap(PARK_RECT, ROAD_RECTS[1]) > 0 or overlap(PARK_RECT, LANE_S) > 0:
    errs.append("停车场压路")
if dist_rect_pt(PARK_RECT, TREE) < R_OUT:
    errs.append("停车场压环岛")
for cr in CAR_RECTS:
    if dist_rect_pt(cr, TREE) < R_OUT:
        errs.append("车位压环岛")
# 红绿灯：贴超市西墙、偏车道中线两格、紧邻井
if dist_rect_pt(rect(TL[0], TL[1], 16, 16), TREE) < R_OUT:
    errs.append("红绿灯在环岛内")
if TL[0] - OX != 64:
    errs.append("红绿灯没有偏车道中线两格")
# 山：不压路、不压房
for (hx, hy, hw, hh) in HILLS:
    hr = rect(hx, hy, hw, hh)
    for rn, rr in (("主路西", ROAD_RECTS[0]), ("主路东", ROAD_RECTS[1]), ("竖路北", LANE_N), ("竖路南", LANE_S)):
        if overlap(hr, rr) > 0:
            errs.append("山压%s (%d,%d)" % (rn, hx, hy))
    for nm, hr2 in HOUSES.items():
        if overlap(hr, hr2) > 0:
            errs.append("山压 %s" % nm)
    if dist_rect_pt(hr, TREE) < R_OUT:
        errs.append("山压环岛 (%d,%d)" % (hx, hy))
# 路标：不压路带（在南沿外）、不压房
for (sx, sy) in SIGNS:
    sr = rect(sx, sy, 16, 32)
    for rn, rr in (("主路西", ROAD_RECTS[0]), ("主路东", ROAD_RECTS[1])):
        if overlap(sr, rr) > 0:
            errs.append("路标压%s" % rn)
    for nm, hr2 in HOUSES.items():
        if overlap(sr, hr2) > 0:
            errs.append("路标压 %s" % nm)
# 装饰房
for pid, pos, r in DECOR:
    if r[0] < 0 or r[1] < 0 or r[2] > W - 1 or r[3] > H - 1:
        errs.append("装饰房出界 %s %s" % (pid, pos))
    for nm, hr2 in HOUSES.items():
        if overlap(r, hr2) > 0:
            errs.append("装饰房压 %s %s" % (nm, pos))
    for rn, rr in (("主路西", ROAD_RECTS[0]), ("主路东", ROAD_RECTS[1]), ("竖路北", LANE_N), ("竖路南", LANE_S),
                   ("田", FIELD_RECT), ("坝", DAM_RECT), ("停车场", PARK_RECT)):
        if overlap(r, rr) > 0:
            errs.append("装饰房压%s %s" % (rn, pos))
    if r[1] < RIVER_S:
        errs.append("装饰房压河 %s" % (pos,))
    if dist_rect_pt(r, TREE) < R_OUT + 48:
        errs.append("装饰房压环岛 %s" % (pos,))
for i in range(len(DECOR)):
    for j in range(i + 1, len(DECOR)):
        if overlap(DECOR[i][2], DECOR[j][2]) > 0:
            errs.append("装饰房互压 %s %s" % (DECOR[i][1], DECOR[j][1]))
# 装饰房 vs 山（山是纯色三角，会穿屋）
for (hx, hy, hw, hh) in HILLS:
    hr = rect(hx, hy, hw, hh)
    for pid, pos, r in DECOR:
        if overlap(r, hr) > 0:
            errs.append("装饰房压山 %s %s" % (pos, (hx, hy)))

def free_point(hs, reach, owner=None):
    px, py = hs["pos"]
    for dx in range(-reach, reach + 1, 8):
        for dy in range(-reach, reach + 1, 8):
            if dx * dx + dy * dy > reach * reach:
                continue
            q = (px + dx, py + dy)
            if any(hr2[0] <= q[0] <= hr2[2] and hr2[1] <= q[1] <= hr2[3] for nm, hr2 in HOUSES.items() if nm != owner):
                continue
            return q
    return None

for hs in hotspots:
    q = free_point(hs, hs["reach"], "school" if hs["title"] == "界碑" else None)
    if q is None:
        errs.append("热点不可达 %s" % hs["title"])
    else:
        hs["_free"] = list(q)

START = (1024, OY)      # 落在西引道正中
if not (ROAD_RECTS[0][0] <= START[0] <= ROAD_RECTS[0][2] and ROAD_RECTS[0][1] <= START[1] <= ROAD_RECTS[0][3]):
    errs.append("起点不在主路上")
for nm, hr2 in HOUSES.items():
    if hr2[0] <= START[0] <= hr2[2] and hr2[1] <= START[1] <= hr2[3]:
        errs.append("起点压 %s" % nm)

rect_area = sum(s["rect"][2] * s["rect"][3] for s in shapes if s["type"] == "rect")

out = {
    "world": {"width": W, "height": H, "grid_w": W // TILE, "grid_h": H // TILE, "tile": TILE},
    "safe_top": 36, "safe_bottom": H - 160, "start_pos": list(START),
    "anchors": {
        "tree_center": list(TREE), "ring_center": list(TREE),
        "ring_inner_r": R_IN, "ring_lane_w": ROAD_W, "ring_outer_r": R_OUT,
        "road_axis_y": OY, "road_w": ROAD_W, "road_band_y": [ROAD_N, ROAD_S - 1],
        "road_w_seg": [ROAD_RECTS[0][0], ROAD_RECTS[0][2]],
        "road_e_seg": [ROAD_RECTS[1][0], ROAD_RECTS[1][2]],
        "lane_x": [LANE_X0, LANE_X1], "lane_n_y": [LANE_TOP, LANE_N_BOT], "lane_s_y": [LANE_S_TOP, H],
        "cross_center": [OX, OY],
        "well": list(WELL), "well_r": WELL_R, "well_to_market_west": gap,
        "school_pos": list(SCHOOL_POS), "school_rect": list(HOUSES["school"]),
        "market_pos": list(MARKET_POS), "market_rect": list(HOUSES["market"]),
        "toyshop_pos": list(TOYSHOP_POS), "toyshop_rect": list(HOUSES["toyshop"]),
        "stele": list(STELE), "traffic_light": list(TL), "parking": list(PARK),
        "field": [3600, 320, 880, 384], "dam": list(DAM_RECT), "river_south": RIVER_S,
    },
    "decor": [{"id": p, "pos": list(pos), "rect": list(r)} for p, pos, r in DECOR],
    "frames": [frame],
}
io.open("lab/_a5_draft.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))

print("=== 锚点 ===")
for k, v in out["anchors"].items():
    print("  %-24s %s" % (k, v))
print("=== 自检 ===")
print("errors:", len(errs))
for e in errs:
    print("  [ERR]", e)
print("shapes:", len(shapes), "hotspots:", len(hotspots), "decor:", len(DECOR),
      "rect 面积占比 %.1f%%" % (100.0 * rect_area / (W * H)))
print("=== 装饰房 ===")
for p, pos, r in DECOR:
    print("  %-10s pos=%-14s rect=%s" % (p, pos, r))
print("=== 热点可达 ===")
for hs in hotspots:
    print("  %-18s pos=%-14s free=%s" % (hs["title"], hs["pos"], hs.get("_free")))
print("=== 关键间距 ===")
print("  井东缘->超市西墙:", gap)
print("  环岛外缘->超市: %.0f  小学: %.0f  玩具店: %.0f  停车场: %.0f" % (
    dist_rect_pt(HOUSES["market"], TREE), dist_rect_pt(HOUSES["school"], TREE),
    dist_rect_pt(HOUSES["toyshop"], TREE), dist_rect_pt(PARK_RECT, TREE)))
print("  树冠 r160 / 内岛 R%d（余 %d）" % (R_IN, R_IN - 160))
print("  引道断开处: 西 x=%d 东 x=%d  车道 y=%d/%d" % (ROAD_RECTS[0][2], ROAD_RECTS[1][0], LANE_N[3], LANE_S[1]))
print("  树心->井=%d  河最南=%d  十字路口=%s" % (OY - WELL[1], RIVER_S, (OX, OY)))
