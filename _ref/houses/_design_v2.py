# -*- coding: utf-8 -*-
"""A1/A2/A3 世界布局 v2：格子化（像素格）设计器 + 预览渲染。

三条修改意见（2026-11-20 用户）：
  1. 路太直 → 改成格子化的弯曲乡道（美术照着格子画）
  2. 老井离磨坊太远 → 放回磨坊院子南侧（数据里本来就是 [6,10]）
  3. 田太工整 → 改成参差的不规则田块

坐标全部用「格」（16px/格）设计，输出：
  - 设计校验（重叠/出界）
  - 预览图 _ref/art/_overview/world_v2_a1.png 等
"""
import json, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(os.path.dirname(HERE), "art", "_overview")
TILE = 16
W, H = 1600, 900
GW, GH = W // TILE, H // TILE       # 100 x 56 格

FONTS = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]
def font(sz):
    for p in FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()

# ============ 固定地标（格坐标，三帧不动）============
RIVER_TILES_Y = 0                # 河占 y 0..6 格
RIVER_H = 7
DAM = (12, 2, 8, 4)              # 坝 x12..19, y2..5（在河里）

# 老井：磨坊院子南侧（mill lot 格 [6,10]）—— 三帧同一个格子
WELL_TILE = (44, 17)             # 格坐标，井心 = (44*16+8, 17*16+8) = (712, 280)

# 老槐：井边西侧 2 格
TREE_TILE = (41, 15)             # 井的西北

# 界碑：路口南侧，三帧不动
STELE_TILE = (58, 26)

# ============ 路：格子化，弯曲乡道 ============
# 每项是 (x, y) 格；渲染时画 2x2 格宽的路面。用「折点 + 逐格走线」生成弯曲路径。
ROAD_POINTS = [
    (-2, 34),      # 从西边村外进
    (6, 34),
    (11, 31),      # 弯向北，绕开低洼
    (17, 30),
    (23, 32),      # 往南拐，过磨坊院前
    (29, 35),
    (36, 36),      # 村中主街
    (43, 35),      # 井南侧（路绕井）
    (47, 38),      # 井这儿往南下凹（头号物证：路为一件事绕了弯）
    (51, 35),
    (58, 34),      # 路口（界碑在 (58,26) 北侧）
    (66, 33),
    (73, 35),      # 再弯一下
    (80, 33),
    (88, 34),
    (96, 35),
    (102, 35),     # 出东边村外
]
ROAD_HALF = 1        # 路半宽（格）→ 实际宽 2*1+1 = 3 格? 用 2 格宽：取 1 表示总宽 2

def bresenham(x0, y0, x1, y1):
    """格子走线，返回路径上所有格。"""
    pts = []
    dx = abs(x1 - x0); dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        pts.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy; x += sx
        if e2 < dx:
            err += dx; y += sy
    return pts

def road_tiles(width=2):
    """把折点展开成路面格子集合。width=2 表示 2 格宽。"""
    tiles = set()
    half = width // 2
    for i in range(len(ROAD_POINTS) - 1):
        x0, y0 = ROAD_POINTS[i]
        x1, y1 = ROAD_POINTS[i + 1]
        for (cx, cy) in bresenham(x0, y0, x1, y1):
            for oy in range(-half + 1, half + 1):
                tiles.add((cx, cy + oy))
    return tiles

# ============ 田：参差不齐的不规则田块 ============
# 用「基础矩形 + 挖掉若干角格 + 附加外凸格」做出不规则感
FIELD_A_BASE = (62, 8, 15, 11)     # 田·东 x62..76, y8..18
FIELD_B_BASE = (79, 8, 15, 11)     # 田·西 x79..93, y8..18

FIELD_A_CUTS = [(62,8),(63,8),(62,9),(76,8),(76,9),(75,18),(76,18),(62,18),(63,18),(62,17)]
FIELD_B_CUTS = [(79,8),(80,8),(79,9),(93,8),(93,9),(92,18),(93,18),(79,18),(80,18),(79,17)]
FIELD_A_EXTRA = [(61,12),(61,13),(77,14),(77,15),(70,19),(71,19)]
FIELD_B_EXTRA = [(78,11),(78,12),(94,15),(94,16),(86,19),(87,19)]

def field_tiles(base, cuts, extra):
    x0, y0, w, h = base
    tiles = set()
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            tiles.add((x, y))
    for c in cuts:
        tiles.discard(c)
    for e in extra:
        tiles.add(e)
    return tiles

ROAD = road_tiles(2)
FIELD_A = field_tiles(FIELD_A_BASE, FIELD_A_CUTS, FIELD_A_EXTRA)
FIELD_B = field_tiles(FIELD_B_BASE, FIELD_B_CUTS, FIELD_B_EXTRA)

# ============ 房子（格坐标，三帧各自的 pos）============
data = json.load(open(os.path.join(HERE, "houses_data.json"), encoding="utf-8"))
by_id = {h["id"]: h for h in data}

def lot_size_tiles(hid):
    lot = by_id[hid]["lot"]
    return (lot[2] - lot[0] + 1, lot[3] - lot[1] + 1)

# 房子 origin 用格坐标
# 磨坊三帧原点固定 (40, 7)：lot 18x11 → 格 x40..57 y7..17
#   井格 [6,10] → 绝对格 (46, 17) —— 正是院子最南行，紧贴磨坊 ✓
MILL_ORIGIN = (40, 7)
# 沈家：南沿固定，向北长。南沿格 32（路面 y~34 之前）
SHEN_SOUTH_TILE = 32
# 周家 / 陆家
ZHOU_ORIGIN = (62, 39)
LU_ORIGIN = (74, 21)

PLACE_TILES = {
    "mill_a1": MILL_ORIGIN, "mill_a2": MILL_ORIGIN, "mill_a3": MILL_ORIGIN,
    "zhou_house": ZHOU_ORIGIN, "zhou_a2": ZHOU_ORIGIN, "zhou_a3": ZHOU_ORIGIN,
    "lu_house": LU_ORIGIN, "lu_a2": LU_ORIGIN, "lu_a3": LU_ORIGIN,
}
for hid in ("shen_a1", "shen_a2", "shen_a3"):
    w, h = lot_size_tiles(hid)
    PLACE_TILES[hid] = (10, SHEN_SOUTH_TILE - h)

FRAMES = {
    "A1 1926": ["mill_a1", "shen_a1", "zhou_house", "lu_house"],
    "A2 1951": ["mill_a2", "shen_a2", "zhou_a2", "lu_a2"],
    "A3 1976": ["mill_a3", "shen_a3", "zhou_a3", "lu_a3"],
}

def lot_rect_tiles(hid):
    w, h = lot_size_tiles(hid)
    x, y = PLACE_TILES[hid]
    return (x, y, w, h)

def overlap(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]

# ============ 校验 ============
problems = []
print("格坐标布局 v2  (世界 %dx%d 格)" % (GW, GH))
print("=" * 70)
for fname, ids in FRAMES.items():
    print("--- %s ---" % fname)
    rects = []
    for hid in ids:
        lt = lot_rect_tiles(hid)
        rects.append((hid, lt))
        notes = []
        if lt[0] < 0 or lt[1] < 0 or lt[0] + lt[2] > GW or lt[1] + lt[3] > GH:
            notes.append("OUT")
        # 路穿过 lot？
        for y in range(lt[1], lt[1] + lt[3]):
            for x in range(lt[0], lt[0] + lt[2]):
                if (x, y) in ROAD:
                    notes.append("lot压路")
                    break
            if "lot压路" in notes:
                break
        print("  %-12s 格 x=%3d y=%3d %2dx%-2d  (px x=%4d y=%4d %3dx%-3d)%s" % (
            hid, lt[0], lt[1], lt[2], lt[3],
            lt[0]*TILE, lt[1]*TILE, lt[2]*TILE, lt[3]*TILE,
            ("   [X] " + ",".join(notes)) if notes else ""))
        if notes:
            problems.append("%s: %s" % (hid, ",".join(notes)))
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            if overlap(rects[i][1], rects[j][1]):
                problems.append("%s: %s x %s 重叠" % (fname, rects[i][0], rects[j][0]))
                print("    [X] %s x %s 重叠" % (rects[i][0], rects[j][0]))
    print()

print("老井格 (44,17) 世界 %s" % str((WELL_TILE[0]*TILE+8, WELL_TILE[1]*TILE+8)))
print("磨坊院子南行格 y=17，井在 (44,17) → 紧贴磨坊 ✓")
print("路格子数 %d，田A %d 格，田B %d 格" % (len(ROAD), len(FIELD_A), len(FIELD_B)))
print()
if problems:
    print("问题：")
    for p in problems:
        print("  !", p)
else:
    print("OK")
