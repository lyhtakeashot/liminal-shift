# -*- coding: utf-8 -*-
"""A4 2001 世界布局预览图。坐标单一真相源 = _design_a4.py。

画的是「设计稿占位块版」，非美术成稿：
  - 主路取直压过老井 → 路中央圆形沥青补丁
  - 粮站拆、超市在建（桩基绕开井那片地）
  - 农田全荒（枯黄 + 荒草点）
  - 陆家废墟 → 郑家小楼（新住户不知情）
  - 界碑、老槐（朝远离井的方向倾斜）
"""
import json, os, sys, math
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _design_a4 as D

OUT = os.path.join(HERE, "..", "art", "_overview")
W, H, TILE = D.W, D.H, D.TILE

FONTS = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]
def font(sz):
    for p in FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()
F11, F12, F13, F14, F16, F20 = (font(x) for x in (11, 12, 13, 14, 16, 20))

ROOM_COLORS = {
    "bed": (156,132,104), "hall": (203,185,151), "store": (141,154,111),
    "kitchen": (189,208,176), "account": (168,192,208), "yard": (59,58,46),
    "shop": (185,154,166), "class": (157,186,205), "mill": (181,168,120),
    "toilet": (154,168,168), "living": (172,160,140),
}
TINT = {
    "shen_a4":  ((150,110,86),  "沈家宅 · A4 四合院 · 沈建国"),
    "market":   ((168,132,104), "超市 · A4 在建（粮站已拆）"),
    "zhou_a4":  ((120,104,82),  "周家老屋 · 沈氏会计"),
    "zheng_a4": ((142,138,110), "郑家小楼 · 外来户（不知情）"),
}


def build_grid(hs):
    """从 houses_data.json 的 wings/partitions/doors/gate 推出墙/门格。
    复制自 _render_world_v3.py，保持与生成器一致。"""
    X0, Y0, X1, Y1 = hs["lot"]
    interior = set()
    for (x, y, w, h) in hs["wings"]:
        for j in range(y + 1, y + h - 1):
            for i in range(x + 1, x + w - 1):
                interior.add((i, j))
    def is_wall(i, j):
        if (i, j) in interior:
            return False
        return any((i+di, j+dj) in interior for di, dj in ((1,0),(-1,0),(0,1),(0,-1)))
    part = set()
    for (x1, y1, x2, y2) in hs.get("partitions", []):
        if x1 == x2:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                part.add((x1, y))
        else:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                part.add((x, y1))
    dset = set(tuple(x) for x in hs["doors"])
    gset = set(tuple(x) for x in hs.get("gate", []))
    rows = []
    for j in range(Y0, Y1 + 1):
        row = ""
        for i in range(X0, X1 + 1):
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


def draw_house(d, hid):
    hs = D.by_id[hid]
    px, py = D.PLACE[hid]
    lot = hs["lot"]
    gw, gh = lot[2] - lot[0] + 1, lot[3] - lot[1] + 1
    base, label = TINT[hid]

    # 院落底色
    d.rectangle([px, py, px + gw*TILE, py + gh*TILE], fill=(58,57,45),
                outline=(214,190,140), width=2)
    # 房间色块
    for room in hs["rooms"]:
        rx0, ry0, rx1, ry1, name, ck = room[:6]
        d.rectangle([px + rx0*TILE, py + ry0*TILE, px + (rx1+1)*TILE, py + (ry1+1)*TILE],
                    fill=ROOM_COLORS.get(ck, (107,88,66)))
    # 墙 / 门 / 院门
    grid = build_grid(hs)
    for j, row in enumerate(grid):
        for i, ch in enumerate(row):
            bx, by = px + i*TILE, py + j*TILE
            if ch == "#":
                d.rectangle([bx, by, bx+TILE-1, by+TILE-1], fill=(138,105,73))
                d.line([(bx, by), (bx+TILE-1, by)], fill=(196,163,116), width=2)
            elif ch == "D":
                d.rectangle([bx, by, bx+TILE-1, by+TILE-1], fill=(224,178,90))
            elif ch == "G":
                d.rectangle([bx, by, bx+TILE-1, by+TILE-1], fill=(150,104,58))
    # 家具（clue 高亮）
    for f in hs["furniture"]:
        fx, fy, fw, fh = f["rect"]
        if fx < lot[0] or fy < lot[1] or fx+fw-1 > lot[2] or fy+fh-1 > lot[3]:
            continue
        bx, by = px + (fx-lot[0])*TILE, py + (fy-lot[1])*TILE
        bw, bh = fw*TILE, fh*TILE
        if f.get("clue"):
            d.rectangle([bx+2, by+2, bx+bw-3, by+bh-3], fill=(217,139,69), outline=(246,198,124))
        else:
            d.rectangle([bx+2, by+2, bx+bw-3, by+bh-3], fill=(202,182,146), outline=(230,214,180))
    # 标签
    d.rectangle([px+2, py+2, px+min(gw*TILE-4, 300), py+38], fill=(20,20,18,210))
    d.text((px+8, py+5), label, font=F12, fill=(252,244,226))
    d.text((px+8, py+21), "%s · %dx%d格" % (hid, gw, gh), font=F11, fill=(224,210,186))

    # 超市在建：脚手架斜线 + 桩基绕开区标注
    if hid == "market":
        for gx in range(0, gw, 3):
            d.line([(px+gx*TILE, py), (px+(gx+3)*TILE, py+gh*TILE)], fill=(226,196,120,70), width=2)
        d.text((px+8, py+gh*TILE-24), "▲ 主体施工 · 桩基绕井", font=F13, fill=(255,236,170))
        rx, ry, rw, rh = D.RESERVE
        d.rectangle([rx, ry, rx+rw, ry+rh], outline=(250,214,120), width=3)
        d.text((rx+4, ry+4), "桩基绕开区（井 + 老槐）", font=F11, fill=(255,232,150))
    # 郑家：不知情标注
    if hid == "zheng_a4":
        d.text((px+8, py+gh*TILE-24), "△ 住户不知脚下是陆家老宅与老井", font=F12, fill=(244,226,180))
    # 周家：账本线索
    if hid == "zhou_a4":
        d.text((px+8, py+gh*TILE-24), "△ 账桌夹层往来账 A5 出土", font=F12, fill=(236,224,196))


def main():
    img = Image.new("RGB", (W, H), (111, 106, 82))  # A4 干燥灰绿地
    d = ImageDraw.Draw(img, "RGBA")

    # 格线
    for x in range(0, W, TILE):
        d.line([(x,0),(x,H)], fill=(255,255,255,8))
    for y in range(0, H, TILE):
        d.line([(0,y),(W,y)], fill=(255,255,255,8))

    # 河（权威坐标 0..1600, 0..112）+ 坝
    d.rectangle([0, 0, W, 112], fill=(72,104,118))
    d.rectangle([0, 100, W, 112], fill=(86,120,136))
    d.text((16, 82), "河（坝在上游 · 沈家 1926 筑）", font=F14, fill=(224,238,246))
    d.rectangle([D.DAM[0], D.DAM[1], D.DAM[0]+D.DAM[2], D.DAM[1]+D.DAM[3]],
                fill=(104,84,62), outline=(150,124,92), width=2)
    d.text((D.DAM[0]+8, D.DAM[1]+8), "坝", font=F16, fill=(240,228,208))

    # 农田全荒：枯黄底 + 荒草点
    for name, (fx, fy, fw, fh) in (("田·东（荒）", D.FIELD_E), ("田·西（荒）", D.FIELD_W)):
        d.rectangle([fx, fy, fx+fw, fy+fh], fill=(150,140,78), outline=(120,110,56), width=2)
        for gy in range(fy+12, fy+fh, 20):
            d.line([(fx+10, gy), (fx+fw-10, gy)], fill=(138,128,66), width=2)
        # 荒草点（稀疏）
        for k in range(24):
            gx = fx + 16 + ((k*53) % (fw-32))
            gy = fy + 16 + ((k*37) % (fh-32))
            d.line([(gx, gy+6), (gx-3, gy), (gx+3, gy+2)], fill=(108,112,54), width=2)
        d.text((fx+8, fy+6), name, font=F13, fill=(60,52,20))

    # 路：主路拉平取直 + 支路
    for road in (D.ROAD_MAIN, D.ROAD_BRANCH):
        d.line([(x, y) for x, y in road], fill=(104,94,80), width=D.ROAD_W, joint="curve")
    d.text((1050, 566), "主路（取直）", font=F12, fill=(246,232,206))

    # 四栋房子
    for hid in D.A4_IDS:
        draw_house(d, hid)

    # ---- 老井：埋地下，地面留圆形沥青补丁（story §7.2 头号物证）----
    # 地标在房子之后画，避免被 market 屋体盖住标注。
    wx, wy, wr = D.WELL
    d.ellipse([wx-wr-4, wy-wr-4, wx+wr+4, wy+wr+4], fill=(84,84,84), outline=(58,58,58), width=2)
    d.ellipse([wx-wr, wy-wr, wx+wr, wy+wr], fill=(70,70,70), outline=(52,52,52), width=2)
    d.text((wx+wr+10, wy-20), "圆形沥青补丁", font=F13, fill=(250,242,214))
    d.text((wx+wr+10, wy-4), "井在下方（已埋）", font=F11, fill=(236,214,170))

    # ---- 老槐：A4 树径 9 格，朝远离井的方向倾斜 ----
    tx, ty = D.TREE
    # 井(900,545)→槐(852,505)，远离井方向≈西北；树冠中心相对树干偏 -2,-2 格
    lean = (-2, -2)
    cx, cy = tx + lean[0]*TILE, ty + lean[1]*TILE
    for rr in (72, 60, 48, 36):
        d.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], fill=(66,102,58,200))
    d.rectangle([tx-5, ty-8, tx+5, ty+6], fill=(86,66,46))
    d.text((tx-70, cy-96), "老槐（向西北倾斜）", font=F12, fill=(232,244,220))

    # 界碑
    sx, sy, sw, sh = D.STELE
    d.rectangle([sx, sy, sx+sw, sy+sh], fill=(138,130,120), outline=(90,84,76), width=1)
    d.rectangle([sx, sy, sx+sw, sy+3], fill=(168,160,148))
    d.text((sx+14, sy), "界碑「周界」", font=F11, fill=(244,238,222))

    # 起点
    stx, sty = D.START
    d.ellipse([stx-9, sty-9, stx+9, sty+9], fill=(226,210,130), outline=(120,96,40), width=2)
    d.text((stx-24, sty+14), "起点", font=F12, fill=(250,240,200))

    # 标题条
    d.rectangle([0, 0, W, 30], fill=(18,18,16,215))
    d.text((14, 6), "A4 · 2001 · 世界布局设计稿（1600×900）  "
                    "路取直压井 / 粮站拆超市在建 / 农田全荒  —— 占位块版，非美术成稿",
           font=F16, fill=(238,230,210))

    # 图例
    lx, ly = 16, H-136
    d.rectangle([lx, ly, lx+470, ly+120], fill=(18,18,16,195), outline=(120,116,100))
    d.text((lx+10, ly+8), "图例 / 本帧要点", font=F14, fill=(238,230,210))
    d.ellipse([lx+12, ly+32, lx+32, ly+52], fill=(70,70,70), outline=(52,52,52))
    d.text((lx+40, ly+32), "圆形沥青补丁 = 井口沉降（人嘴只给方向）", font=F11, fill=(224,214,196))
    d.rectangle([lx+12, ly+58, lx+32, ly+74], fill=(138,105,73))
    d.text((lx+40, ly+56), "房屋墙 / 房间色块 / 家具（橙=线索格）", font=F11, fill=(224,214,196))
    d.rectangle([lx+12, ly+82, lx+32, ly+98], fill=(150,140,78))
    d.text((lx+40, ly+80), "农田全荒 · 黄框虚线 = 桩基绕开区", font=F11, fill=(224,214,196))
    d.text((lx+40, ly+102), "⚠ A1–A3 落地坐标与本稿基准分裂，落地前须统一（见 _design_a4.py 注释）",
           font=F11, fill=(246,196,140))

    os.makedirs(OUT, exist_ok=True)
    p = os.path.abspath(os.path.join(OUT, "a4_world_layout.png"))
    img.save(p)
    print("saved", p, img.size)


if __name__ == "__main__":
    main()
