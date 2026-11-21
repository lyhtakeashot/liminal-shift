# -*- coding: utf-8 -*-
"""渲染 v4 布局预览（弯河 / 田演变 / A3 直路）。复用 _design_v4 的算法。"""
import json, os, math, heapq, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.join(os.path.dirname(HERE), "art", "_overview")
TILE = 16
W, H = 1600, 900
GW, GH = W // TILE, H // TILE

# 直接 import 设计模块（会用它的全局量）
import importlib.util
spec = importlib.util.spec_from_file_location("design_v5", os.path.join(HERE, "_design_v5.py"))
dv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dv)

FONTS = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]
def font(sz):
    for p in FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()

by_id = dv.by_id
ROOM_COLORS = {"bed":(156,132,104),"hall":(203,185,151),"store":(141,154,111),
               "kitchen":(189,208,176),"account":(168,192,208),"yard":(59,58,46),
               "shop":(185,154,166),"class":(157,186,205),"mill":(181,168,120),
               "toilet":(154,168,168)}

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

def render(fid, ids):
    meta = dv.META[fid]
    img = Image.new("RGB", (W, H), meta["ground"])
    d = ImageDraw.Draw(img, "RGBA")

    # 格线
    for x in range(0, W, TILE):
        d.line([(x,0),(x,H)], fill=(255,255,255,9))
    for y in range(0, H, TILE):
        d.line([(0,y),(W,y)], fill=(255,255,255,9))

    # 河（逐列弯曲）
    for (x, y) in dv.RIVER_CELLS:
        d.rectangle([x*TILE, y*TILE, x*TILE+TILE-1, y*TILE+TILE-1], fill=meta["river"])
    # 波纹
    for i in range(8):
        yy = 10 + i * 12
        d.line([(0,yy),(W,yy)], fill=(255,255,255,14), width=1)

    # 坝
    for (x, y) in dv.DAM_CELLS:
        d.rectangle([x*TILE, y*TILE, x*TILE+TILE-1, y*TILE+TILE-1],
                    fill=(106,86,72), outline=(150,124,92))
    d.text((12*TILE+6, 2*TILE+6), "坝", font=font(14), fill=(240,228,208))

    # 田（A5 没有田）
    if fid in dv.FIELDS:
        for (x, y) in dv.FIELDS[fid]:
            d.rectangle([x*TILE, y*TILE, x*TILE+TILE-1, y*TILE+TILE-1], fill=meta["field"])
        d.text((58*TILE+6, 6*TILE-14), "田", font=font(13), fill=(40,50,20))

    # 路
    if fid == "a5_2026":
        for (x, y) in dv.ROAD_A5:
            d.rectangle([x*TILE, y*TILE, x*TILE+TILE-1, y*TILE+TILE-1],
                        fill=(92,92,92))
    else:
        for (x, y) in dv.ROAD_SETS[fid]:
            d.rectangle([x*TILE, y*TILE, x*TILE+TILE-1, y*TILE+TILE-1], fill=(138,122,90))

    # A5 环岛（树被马路环绕）
    if fid == "a5_2026":
        for (x, y) in dv.CANOPY_A5:
            d.rectangle([x*TILE, y*TILE, x*TILE+TILE-1, y*TILE+TILE-1], fill=(63,107,58))

    # 房子
    for hid in ids:
        hs = by_id[hid]
        px, py = dv.PLACE[hid][0]*TILE, dv.PLACE[hid][1]*TILE
        lot = hs["lot"]
        gw, gh = lot[2]-lot[0]+1, lot[3]-lot[1]+1
        d.rectangle([px, py, px+gw*TILE, py+gh*TILE], fill=(59,58,46),
                    outline=(168,144,90), width=2)
        for room in hs["rooms"]:
            rx0, ry0, rx1, ry1, name, ck = room[:6]
            d.rectangle([px+rx0*TILE, py+ry0*TILE, px+(rx1+1)*TILE, py+(ry1+1)*TILE],
                        fill=ROOM_COLORS.get(ck, (107,88,66)))
        grid = build_grid(hs)
        for j, row in enumerate(grid):
            for i, ch in enumerate(row):
                bx, by = px + i*TILE, py + j*TILE
                if ch == "#":
                    d.rectangle([bx,by,bx+TILE-1,by+TILE-1], fill=(140,107,74))
                    d.line([(bx,by),(bx+TILE-1,by)], fill=(201,168,120), width=2)
                elif ch == "D":
                    d.rectangle([bx,by,bx+TILE-1,by+TILE-1], fill=(224,178,90))
                elif ch == "G":
                    d.rectangle([bx,by,bx+TILE-1,by+TILE-1], fill=(154,106,58))
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

    # ---- 井：先画井，再画树（用户 2026-11-21：井后续要被封上，
    #      被树冠盖住没关系，所以树冠盖在井上是对的）----
    wx, wy = dv.WELL_CELL[0]*TILE, dv.WELL_CELL[1]*TILE
    WELL_STATE = {
        "a1_1926": {"fill": (46,50,50), "mouth": (16,18,18), "label": "老井"},
        "a2_1951": {"fill": (74,74,70), "mouth": None, "label": "老井·石板"},
        "a3_1976": {"fill": (96,96,92), "mouth": None, "label": "老井·水泥"},
        "a5_2026": {"fill": (88,88,88), "mouth": None, "label": "补丁"},
    }
    ws = WELL_STATE.get(fid, WELL_STATE["a1_1926"])
    if fid == "a5_2026":
        pcx, pcy = dv.WELL_CELL[0], dv.WELL_CELL[1]
        for (dx, dy) in [(0,-1),(1,-1),(-1,0),(0,0),(1,0),(2,0),(0,1),(1,1)]:
            d.rectangle([(pcx+dx)*TILE, (pcy+dy)*TILE,
                         (pcx+dx)*TILE+TILE-1, (pcy+dy)*TILE+TILE-1], fill=(68,68,68))
    else:
        for (dx, dy) in [(0,0),(1,0),(0,1),(1,1)]:
            d.rectangle([wx+dx*TILE, wy+dy*TILE,
                         wx+(dx+1)*TILE-1, wy+(dy+1)*TILE-1], fill=ws["fill"])
        if ws["mouth"] is not None:
            d.rectangle([wx+5, wy+5, wx+TILE*2-6, wy+TILE*2-6], fill=ws["mouth"])

    # ---- 树：像素圆（逐格阶梯），盖在井之上 ----
    tx, ty = dv.TREE_CELL[0]*TILE+8, dv.TREE_CELL[1]*TILE+8
    diam = dv.TREE_DIAMETER.get(fid, 3)
    if fid == "a5_2026":
        # A5 树冠由环岛那段按格画好；这里补树干
        d.rectangle([tx-5, ty-5, tx+5, ty+5], fill=(74,58,42))
        d.rectangle([tx-5, ty-5, tx+5, ty-1], fill=(98,76,54))
    else:
        canopy = dv.tree_canopy(fid)
        for (cellx, celly) in canopy:
            d.rectangle([cellx*TILE, celly*TILE,
                         cellx*TILE+TILE-1, celly*TILE+TILE-1], fill=(48,82,46))
        for (cellx, celly) in canopy:
            d.rectangle([cellx*TILE+1, celly*TILE+1,
                         cellx*TILE+TILE-2, celly*TILE+TILE-2], fill=(63,107,58))
        if diam >= 5:
            d.rectangle([tx-2, ty-2, tx+2, ty+2], fill=(74,58,42))
    d.text((dv.TREE_CELL[0]*TILE + (diam//2+2)*TILE, ty-7),
           "槐%d格" % diam, font=font(11), fill=(228,244,226))
    d.text((wx+TILE*2+3, wy-16), ws["label"], font=font(11), fill=(245,240,225))

    # 界碑（像素方块）
    sx, sy = dv.STELE_CELL[0]*TILE, dv.STELE_CELL[1]*TILE
    d.rectangle([sx, sy, sx+TILE-1, sy+TILE*2-1], fill=(138,130,120))
    d.rectangle([sx, sy, sx+TILE-1, sy+3], fill=(168,160,148))
    d.text((sx+18, sy+2), "界碑", font=font(11), fill=(240,236,224))

    # 标题
    d.rectangle([0, 0, 470, 26], fill=(18,18,16,225))
    d.text((10, 4), "%s · 世界布局 v3（河弯曲 / 田%s / 路%s）" % (
        meta["title"],
        "零散" if fid == "a1_1926" else "规整",
        meta["road"]), font=font(15), fill=(236,228,210))
    return img

def main():
    os.makedirs(OUT, exist_ok=True)
    render_frames = dict(dv.FRAMES)
    render_frames["a5_2026"] = []        # A5 房子数据未定，先只出环岛
    for fid, ids in render_frames.items():
        img = render(fid, ids)
        p = os.path.join(OUT, "world_v3_%s.png" % fid)
        img.save(p)
        print("saved", p, img.size)

if __name__ == "__main__":
    main()
