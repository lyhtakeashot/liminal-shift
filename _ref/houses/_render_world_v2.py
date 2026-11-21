# -*- coding: utf-8 -*-
"""渲染 v3 布局预览图（格子化，美术可直接照格画）。"""
import json, os, math, heapq
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(os.path.dirname(HERE), "art", "_overview")
TILE = 16
W, H = 1600, 900
GW, GH = W // TILE, H // TILE

FONTS = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]
def font(sz):
    for p in FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()

data = json.load(open(os.path.join(HERE, "houses_data.json"), encoding="utf-8"))
by_id = {h["id"]: h for h in data}

def lot_tiles(hid):
    lot = by_id[hid]["lot"]
    return (lot[2] - lot[0] + 1, lot[3] - lot[1] + 1)

MILL_ORIGIN = (40, 7)
SHEN_ORIGIN_X = 8
SHEN_SOUTH = 33
ZHOU_ORIGIN = (60, 40)
LU_ORIGIN = (74, 21)

PLACE = {"mill_a1": MILL_ORIGIN, "mill_a2": MILL_ORIGIN, "mill_a3": MILL_ORIGIN,
         "zhou_house": ZHOU_ORIGIN, "zhou_a2": ZHOU_ORIGIN, "zhou_a3": ZHOU_ORIGIN,
         "lu_house": LU_ORIGIN, "lu_a2": LU_ORIGIN, "lu_a3": LU_ORIGIN}
for hid in ("shen_a1", "shen_a2", "shen_a3"):
    w, h = lot_tiles(hid)
    PLACE[hid] = (SHEN_ORIGIN_X, SHEN_SOUTH - h)

FRAMES = {
    "a1_1926": ["mill_a1", "shen_a1", "zhou_house", "lu_house"],
    "a2_1951": ["mill_a2", "shen_a2", "zhou_a2", "lu_a2"],
    "a3_1976": ["mill_a3", "shen_a3", "zhou_a3", "lu_a3"],
}
FRAME_META = {
    "a1_1926": {"ground": (110, 122, 76), "river": (63, 95, 110), "field": (125, 138, 62), "title": "A1 · 1926"},
    "a2_1951": {"ground": (104, 116, 74), "river": (63, 95, 110), "field": (120, 134, 60), "title": "A2 · 1951"},
    "a3_1976": {"ground": (106, 106, 68), "river": (74, 106, 96), "field": (107, 100, 64), "title": "A3 · 1976"},
}

WELL_CELL = (46, 17)
TREE_CELL = (43, 16)
STELE_CELL = (60, 37)

FIELD_A_BASE = (62, 8, 15, 11)
FIELD_B_BASE = (79, 8, 15, 11)
FIELD_A_CUTS = [(62,8),(63,8),(62,9),(76,8),(76,9),(75,18),(76,18),(62,18),(63,18),(62,17),(68,18),(69,18)]
FIELD_B_CUTS = [(79,8),(80,8),(79,9),(93,8),(93,9),(92,18),(93,18),(79,18),(80,18),(79,17),(85,18),(86,18)]
FIELD_A_EXTRA = [(61,12),(61,13),(77,14),(77,15),(70,19),(71,19),(64,7)]
FIELD_B_EXTRA = [(78,11),(78,12),(94,15),(94,16),(86,19),(87,19),(90,7)]

def field_cells(base, cuts, extra):
    x0, y0, w, h = base
    s = set()
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            s.add((x, y))
    for c in cuts:
        s.discard(c)
    for e in extra:
        s.add(e)
    return s

FIELD_A = field_cells(FIELD_A_BASE, FIELD_A_CUTS, FIELD_A_EXTRA)
FIELD_B = field_cells(FIELD_B_BASE, FIELD_B_CUTS, FIELD_B_EXTRA)
RIVER_CELLS = set((x, y) for y in range(0, 7) for x in range(GW))
DAM_CELLS = set((x, y) for y in range(2, 6) for x in range(12, 20))

def rect_of(hid):
    w, h = lot_tiles(hid)
    x, y = PLACE[hid]
    return (x, y, w, h)

def blocked_cells(ids):
    s = set()
    for hid in ids:
        x, y, w, h = rect_of(hid)
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                s.add((xx, yy))
    return s

def a_star(start, goal, blocked, extra=None, max_iter=200000):
    def h(p):
        return abs(p[0]-goal[0]) + abs(p[1]-goal[1])
    openq = [(h(start), 0, start, None)]
    came = {}
    cost = {start: 0}
    it = 0
    while openq and it < max_iter:
        it += 1
        f, g, cur, par = heapq.heappop(openq)
        if cur in came:
            continue
        came[cur] = par
        if cur == goal:
            path = []
            c = cur
            while c is not None:
                path.append(c)
                c = came[c]
            return path[::-1]
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nb = (cur[0]+dx, cur[1]+dy)
            if nb[0] < 0 or nb[0] >= GW or nb[1] < 0 or nb[1] >= GH:
                continue
            if nb in blocked:
                continue
            add = 1 + (extra(nb) if extra else 0)
            ng = g + add
            if nb not in cost or ng < cost[nb]:
                cost[nb] = ng
                heapq.heappush(openq, (ng + h(nb), ng, nb, cur))
    return None

def sway_target(x):
    return 34 + round(2.2 * math.sin(x / 7.0) + 1.3 * math.sin(x / 3.1))

ROADS = {}
for fname, ids in FRAMES.items():
    far = blocked_cells(ids) | RIVER_CELLS | FIELD_A | FIELD_B
    def cost_cell(cell, ids=ids):
        x, y = cell
        c = abs(y - sway_target(x)) * 2
        for hid in ids:
            hx, hy, hw, hh = rect_of(hid)
            dx = max(hx - x, 0, x - (hx + hw - 1))
            dy = max(hy - y, 0, y - (hy + hh - 1))
            d = max(dx, dy)
            if d == 0:
                c += 60
            elif d == 1:
                c += 8
            elif d == 2:
                c += 2
        wd = max(abs(x - WELL_CELL[0]), abs(y - WELL_CELL[1]))
        if wd <= 1:
            c += 120
        elif wd == 2:
            c += 25
        return c
    ROADS[fname] = a_star((0, 34), (GW - 1, 33), far, cost_cell) or []

def widen(path, half=1):
    s = set()
    for (x, y) in path:
        for oy in range(-half + 1, half + 1):
            s.add((x, y + oy))
    return s

ROAD_SETS = {k: widen(v, 1) for k, v in ROADS.items()}

# ---- 房子网格（复用 build_grid 规则）----
def build_grid(hs):
    X0, Y0, X1, Y1 = hs["lot"]
    interior = set()
    for (x, y, w, h) in hs["wings"]:
        for j in range(y+1, y+h-1):
            for i in range(x+1, x+w-1):
                interior.add((i, j))
    def is_wall(i, j):
        if (i, j) in interior:
            return False
        return any((i+di, j+dj) in interior for di, dj in ((1,0),(-1,0),(0,1),(0,-1)))
    part = set()
    for (x1, y1, x2, y2) in hs.get("partitions", []):
        if x1 == x2:
            for y in range(min(y1,y2), max(y1,y2)+1):
                part.add((x1, y))
        else:
            for x in range(min(x1,x2), max(x1,x2)+1):
                part.add((x, y1))
    dset = set(tuple(d) for d in hs["doors"])
    gset = set(tuple(g) for g in hs.get("gate", []))
    rows = []
    for j in range(Y0, Y1+1):
        row = ""
        for i in range(X0, X1+1):
            c = (i, j)
            if c in gset:
                row += "G"
            elif c in dset:
                row += "D"
            elif c in part or is_wall(i, j):
                row += "#"
            elif c in interior:
                row += "."
            else:
                row += " "
        rows.append(row)
    return rows

ROOM_COLORS = {"bed":(156,132,104),"hall":(203,185,151),"store":(141,154,111),
               "kitchen":(189,208,176),"account":(168,192,208),"yard":(59,58,46),
               "shop":(185,154,166),"class":(157,186,205),"mill":(181,168,120),
               "toilet":(154,168,168)}

def render(fid, ids):
    meta = FRAME_META[fid]
    img = Image.new("RGB", (W, H), meta["ground"])
    d = ImageDraw.Draw(img, "RGBA")

    # 格线（淡）——美术按格取坐标
    for x in range(0, W, TILE):
        d.line([(x,0),(x,H)], fill=(255,255,255,10))
    for y in range(0, H, TILE):
        d.line([(0,y),(W,y)], fill=(255,255,255,10))

    # 河（带波纹线）
    d.rectangle([0, 0, W, 7*TILE], fill=meta["river"])
    for i in range(6):
        yy = 8 + i * 14
        d.line([(0,yy),(W,yy)], fill=(255,255,255,12), width=1)

    # 坝
    x0, y0, w0, h0 = DAM_CELLS and (12*TILE, 2*TILE, 8*TILE, 4*TILE)
    d.rectangle([x0, y0, x0+w0, y0+h0], fill=(106,86,72), outline=(150,124,92), width=2)
    d.text((x0+8, y0+8), "坝", font=font(14), fill=(240,228,208))

    # 田（不规则格子）
    for (x, y) in FIELD_A:
        d.rectangle([x*TILE, y*TILE, x*TILE+TILE-1, y*TILE+TILE-1], fill=meta["field"])
    for (x, y) in FIELD_B:
        d.rectangle([x*TILE, y*TILE, x*TILE+TILE-1, y*TILE+TILE-1], fill=meta["field"])
    d.text((62*TILE+6, 8*TILE-16), "田·东", font=font(12), fill=(40,50,20))
    d.text((79*TILE+6, 8*TILE-16), "田·西", font=font(12), fill=(40,50,20))

    # 路（格子化）
    for (x, y) in ROAD_SETS[fid]:
        d.rectangle([x*TILE, y*TILE, x*TILE+TILE-1, y*TILE+TILE-1], fill=(138,122,90))

    # 房子
    for hid in ids:
        hs = by_id[hid]
        px, py = PLACE[hid][0]*TILE, PLACE[hid][1]*TILE
        lot = hs["lot"]
        gw, gh = lot[2]-lot[0]+1, lot[3]-lot[1]+1
        d.rectangle([px, py, px+gw*TILE, py+gh*TILE], fill=(59,58,46), outline=(168,144,90), width=2)
        for room in hs["rooms"]:
            rx0, ry0, rx1, ry1, name, ck = room[:6]
            rc = ROOM_COLORS.get(ck, (107,88,66))
            d.rectangle([px+rx0*TILE, py+ry0*TILE, px+(rx1+1)*TILE, py+(ry1+1)*TILE], fill=rc)
        grid = build_grid(hs)
        for j, row in enumerate(grid):
            for i, ch in enumerate(row):
                bx, by = px + i*TILE, py + j*TILE
                box = [bx, by, bx+TILE-1, by+TILE-1]
                if ch == "#":
                    d.rectangle(box, fill=(140,107,74))
                    d.line([(bx,by),(bx+TILE-1,by)], fill=(201,168,120), width=2)
                elif ch == "D":
                    d.rectangle(box, fill=(224,178,90))
                elif ch == "G":
                    d.rectangle(box, fill=(154,106,58))
        for f in hs["furniture"]:
            fx, fy, fw, fh = f["rect"]
            if fx < lot[0] or fy < lot[1] or fx+fw-1 > lot[2] or fy+fh-1 > lot[3]:
                continue
            bx, by = px+(fx-lot[0])*TILE, py+(fy-lot[1])*TILE
            bw, bh = fw*TILE, fh*TILE
            if f.get("clue"):
                d.rectangle([bx+2,by+2,bx+bw-3,by+bh-3], fill=(217,139,69), outline=(240,190,120))
            else:
                d.rectangle([bx+2,by+2,bx+bw-3,by+bh-3], fill=(200,180,143), outline=(232,215,178))
        d.text((px+5, py+3), hid, font=font(12), fill=(250,240,214))

    # 井 / 槐 / 碑
    wx, wy = WELL_CELL[0]*TILE+TILE//2, WELL_CELL[1]*TILE+TILE//2
    d.ellipse([wx-11, wy-11, wx+11, wy+11], fill=(26,30,30), outline=(170,170,160), width=2)
    d.text((wx+14, wy-8), "老井", font=font(12), fill=(245,240,225))
    tx, ty = TREE_CELL[0]*TILE+TILE//2, TREE_CELL[1]*TILE+TILE//2
    d.ellipse([tx-10, ty-10, tx+10, ty+10], fill=(63,107,58), outline=(120,160,110), width=2)
    sx, sy = STELE_CELL[0]*TILE, STELE_CELL[1]*TILE
    d.rectangle([sx, sy, sx+8, sy+16], fill=(138,130,120), outline=(200,195,180))
    d.text((sx+12, sy+2), "界碑", font=font(12), fill=(240,236,224))

    # 标题
    d.rectangle([0, 0, 420, 26], fill=(18,18,16,220))
    d.text((10, 4), "%s · 世界布局 v2（格子化，1 格 = 16px）" % meta["title"],
           font=font(15), fill=(236,228,210))
    return img

def main():
    os.makedirs(OUT, exist_ok=True)
    for fid, ids in FRAMES.items():
        img = render(fid, ids)
        p = os.path.join(OUT, "world_v2_%s.png" % fid)
        img.save(p)
        print("saved", p, img.size)

if __name__ == "__main__":
    main()
