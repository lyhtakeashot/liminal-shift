"""
一字形房子 · 陆家平面图 v4（占地缩小 + 家具标注名字 + 院子可搜证）

v4 修正（用户 m01321）:
  1) 占地缩小 24×14 → 20×10（仍容纳屋本体 15×8 + 东侧院子 + 茅房）
  2) 家具色块内标注名字（图上直接可认）
  3) 家具清单完整显示（底部留白加大，不再截断）
  4) 选 B：院子可走可搜证 → 院子里有水缸、柴堆、茅房

屋本体 15×8=240×128px；占地 20×10=320×160px（x:0..19, y:-1..8）。
输出：_ref/houses/straight_rooms.png
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
TILE = 16
SCALE = 40

FONTS = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]


def font(size):
    for p in FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


C = {
    "bg": "#191814", "text": "#e6dfd0", "gray": "#9a9284", "key": "#e0bb74",
    "grid": "#3a352c", "wall": "#8c6b4a", "wall_top": "#a98a63",
    "door": "#e0b25a", "ruler": "#c9c0ae", "measure": "#7fa8c8",
    "player": "#e8543f", "player_edge": "#ffd9c4", "lot": "#a8905a",
    "yard": "#3b3a2e", "furn": "#c8b48f", "furn_edge": "#e8d7b2",
    "clue": "#d98b45", "yard_furn": "#a9b58a", "yard_edge": "#d3dfae",
}

GRID = [
    "###############",  # y0
    "#....#....#...#",  # y1
    "#....#....D...#",  # y2  长辈房门 x10
    "#....#....#...#",  # y3
    "#....#....#####",  # y4
    "#....D....D...#",  # y5  夫妻房门 x5 / 灶间门 x10
    "#....#....#...#",  # y6
    "######D########",  # y7  大门 x6
]

ROOMS = [
    dict(name="夫妻房", x0=1, y0=1, x1=4, y1=6, color="#e0c9ae"),
    dict(name="堂屋", x0=6, y0=1, x1=9, y1=6, color="#cbb997"),
    dict(name="长辈房", x0=11, y0=1, x1=13, y1=3, color="#b7c9d6"),
    dict(name="灶间", x0=11, y0=5, x1=13, y1=6, color="#bdd0b0"),
]

# 家具：fid / 全名 / 图上短名 / 格[x,y,w,h] / 线索 / 备注 / 区域
FURNITURE = [
    dict(fid="bed_double", name="双人床", short="双人床", rect=(1, 1, 2, 2),
         clue=False, note="穷家 2×2；富家 3×3", zone="house"),
    dict(fid="wardrobe_a", name="衣柜", short="衣柜", rect=(4, 1, 1, 2),
         clue=False, note="夫妻房", zone="house"),
    dict(fid="stool_a", name="凳", short="凳", rect=(4, 4, 1, 1),
         clue=False, note="夫妻房", zone="house"),
    dict(fid="chest_a", name="旧木箱", short="木箱", rect=(2, 5, 1, 1),
         clue=True, note="夫妻房 · 可检视线索", zone="house"),
    dict(fid="table_main", name="八仙桌", short="八仙桌", rect=(7, 2, 2, 2),
         clue=False, note="堂屋", zone="house"),
    dict(fid="stool_b", name="凳", short="凳", rect=(6, 3, 1, 1),
         clue=False, note="堂屋", zone="house"),
    dict(fid="stool_c", name="凳", short="凳", rect=(9, 3, 1, 1),
         clue=False, note="堂屋", zone="house"),
    dict(fid="altar", name="祖宗牌位", short="牌位", rect=(8, 6, 2, 1),
         clue=False, note="堂屋 · 横向贴南墙靠右下角", zone="house"),
    dict(fid="bed_single", name="单人床", short="单人床", rect=(11, 1, 2, 1),
         clue=False, note="长辈房 · 老太爷 · 横向靠北墙（不挡门与柜）", zone="house"),
    dict(fid="wardrobe_b", name="柜", short="柜", rect=(13, 1, 1, 2),
         clue=False, note="长辈房 · 贴东墙", zone="house"),
    dict(fid="stove", name="灶台", short="灶台", rect=(13, 5, 1, 2),
         clue=False, note="灶间 · 竖向靠东墙", zone="house"),
    dict(fid="privy", name="茅房", short="茅房", rect=(16, 2, 3, 2),
         clue=False, note="屋外建筑", zone="yard"),
    dict(fid="privy_pit", name="茅坑", short="茅坑", rect=(17, 2, 1, 1),
         clue=False, note="茅房内", zone="yard"),
    dict(fid="waterjar", name="水缸", short="水缸", rect=(16, 5, 1, 1),
         clue=False, note="院子 · 接雨水", zone="yard"),
    dict(fid="firewood", name="柴堆", short="柴堆", rect=(18, 5, 1, 1),
         clue=False, note="院子", zone="yard"),
]

LOT = dict(x=0, y=-1, w=20, h=10)  # 占地 x:0..19 y:-1..8
HOUSE = dict(x=0, y=0, w=15, h=8)
DOORS = [(10, 2, "长辈房门"), (5, 5, "夫妻房门"), (10, 5, "灶间门"), (6, 7, "大门")]
PLAYER_AT = (7, 5)


def room_at(x, y):
    for r in ROOMS:
        if r["x0"] <= x <= r["x1"] and r["y0"] <= y <= r["y1"]:
            return r
    return None


def draw_label(d, bx, by, bw, bh, short):
    """在家具色块里写名字：2×2 横排；1×2 竖排逐字；1×1 小字。"""
    if bw >= 2:
        d.text((bx + bw / 2, by + bh / 2), short,
               font=font(14 if bh >= 2 else 12), fill="#3a2c1c", anchor="mm")
    elif bh >= 2:
        for i, ch in enumerate(short):
            d.text((bx + bw / 2, by + bh * (i + 1) / (len(short) + 1)), ch,
                   font=font(12), fill="#3a2c1c", anchor="mm")
    else:
        d.text((bx + bw / 2, by + bh / 2), short,
               font=font(11 if len(short) <= 2 else 9), fill="#3a2c1c", anchor="mm")


def main():
    ox, oy = -LOT["x"], -LOT["y"]
    pad_x, pad_y = 80, 210
    W = pad_x + LOT["w"] * SCALE + 200
    H = pad_y + LOT["h"] * SCALE + 520  # 底部留白加大：清单不再截断
    img = Image.new("RGB", (W, H), C["bg"])
    d = ImageDraw.Draw(img)

    d.text((40, 16), "陆家 · 平面图 v4（占地缩小 · 家具标名 · 院子可搜证）",
           font=font(30), fill=C["text"])
    d.text((40, 58),
           "屋本体 15×8 格 = 240×128 px ｜ 占地 20×10 格 = 320×160 px（含院子、茅房；选 B：院子可走可搜证）",
           font=font(16), fill=C["key"])
    d.text((40, 84),
           "家具：人 1×2 ｜ 双人床 2×2（穷家）/ 3×3（富家） ｜ 单人床 1×2 ｜ 一格 16×16 px ｜ 橙框=可检视线索",
           font=font(15), fill=C["gray"])
    d.text((40, 110),
           "1926 陆家 3 口人：老太爷 / 陆文+儿媳（怀陆敬之，未出生）。院子里的水缸、柴堆、茅房都可搜证。",
           font=font(14), fill=C["gray"])

    lx, ly = pad_x, pad_y
    lw, lh = LOT["w"] * SCALE, LOT["h"] * SCALE
    d.rectangle([lx, ly, lx + lw, ly + lh], fill=C["yard"],
                outline=C["lot"], width=3)
    d.text((lx + 10, ly + 10), "陆家占地 20×10 格 = 320×160 px",
           font=font(15), fill=C["lot"], anchor="la")

    def sx(gx):
        return pad_x + (gx + ox) * SCALE

    def sy(gy):
        return pad_y + (gy + oy) * SCALE

    for gx in range(LOT["x"] + 1, LOT["x"] + LOT["w"]):
        d.line([(sx(gx), ly), (sx(gx), ly + lh)], fill="#2e2d24", width=1)
    for gy in range(LOT["y"] + 1, LOT["y"] + LOT["h"]):
        d.line([(lx, sy(gy)), (lx + lw, sy(gy))], fill="#2e2d24", width=1)

    for y, row in enumerate(GRID):
        for x, ch in enumerate(row):
            bx, by = sx(x), sy(y)
            box = [bx, by, bx + SCALE - 1, by + SCALE - 1]
            if ch == "#":
                d.rectangle(box, fill=C["wall"])
                d.line([(bx, by), (bx + SCALE - 1, by)], fill=C["wall_top"], width=3)
            elif ch == "D":
                d.rectangle(box, fill=C["door"])
            else:
                r = room_at(x, y)
                d.rectangle(box, fill=(r["color"] if r else "#5a5348"))

    # 家具：室内色块 / 院子色块
    for f in FURNITURE:
        fx, fy, fw, fh = f["rect"]
        bx, by = sx(fx), sy(fy)
        bw, bh = fw * SCALE, fh * SCALE
        if f["fid"] == "privy":  # 茅房虚框
            d.rectangle([bx, by, bx + bw, by + bh],
                        outline=C["yard_furn"], width=3)
            d.text((bx + bw / 2, by + bh / 2 - 2), "茅房",
                   font=font(15), fill=C["yard_furn"], anchor="mm")
            d.text((bx + bw / 2, by + bh / 2 + 16), "3×2",
                   font=font(12), fill=C["gray"], anchor="mm")
            continue
        if f["zone"] == "yard":
            fill, edge = C["yard_furn"], C["yard_edge"]
        elif f["clue"]:
            fill, edge = C["clue"], C["clue"]
        else:
            fill, edge = C["furn"], C["furn_edge"]
        d.rectangle([bx + 3, by + 3, bx + bw - 4, by + bh - 4],
                    fill=fill, outline=edge, width=2)
        draw_label(d, bx + 3, by + 3, bw - 7, bh - 7, f["short"])

    # 主角
    px, py = sx(PLAYER_AT[0]), sy(PLAYER_AT[1])
    pw, ph = SCALE, 2 * SCALE
    top = py - (ph - SCALE)
    d.rectangle([px + 3, top + 3, px + pw - 4, py + SCALE - 4],
                fill=C["player"], outline=C["player_edge"], width=2)
    d.ellipse([px + pw * 0.27, top + ph * 0.14,
               px + pw * 0.73, top + ph * 0.42], fill=C["player_edge"])
    d.text((px + pw + 6, top + ph / 2), "主角 1×2",
           font=font(12), fill=C["key"], anchor="lm")

    # 占地尺寸线
    dy = ly + lh + 22
    d.line([(lx, dy), (lx + lw, dy)], fill=C["measure"], width=2)
    for xx in (lx, lx + lw):
        d.line([(xx, dy - 6), (xx, dy + 6)], fill=C["measure"], width=2)
    d.text((lx + lw / 2, dy + 8), f"占地 {LOT['w']} 格 = {LOT['w']*TILE} px",
           font=font(14), fill=C["measure"], anchor="ma")
    dx = lx + lw + 22
    d.line([(dx, ly), (dx, ly + lh)], fill=C["measure"], width=2)
    for yy in (ly, ly + lh):
        d.line([(dx - 6, yy), (dx + 6, yy)], fill=C["measure"], width=2)
    d.text((dx + 10, ly + lh / 2), f"{LOT['h']} 格 = {LOT['h']*TILE} px",
           font=font(14), fill=C["measure"], anchor="lm")

    # 完整家具清单（分室内/院子两组，图上名字与清单一致）
    ly2 = ly + lh + 62
    d.text((40, ly2), "家具清单（单位：格；◆=可检视线索）", font=font(18), fill=C["key"])
    yy = ly2 + 30
    for zone, title in (("house", "— 屋内 —"), ("yard", "— 院子（可搜证）—")):
        d.text((40, yy), title, font=font(14), fill=C["gray"])
        yy += 22
        for f in [x for x in FURNITURE if x["zone"] == zone]:
            fx, fy, fw, fh = f["rect"]
            mark = "◆" if f["clue"] else "·"
            col = C["clue"] if f["clue"] else C["text"]
            d.text((52, yy),
                   f"{mark} {f['name']}  {fw}×{fh} 格 = {fw*TILE}×{fh*TILE} px   {f['note']}",
                   font=font(13), fill=col, anchor="lm")
            yy += 21
        yy += 8

    out = os.path.join(OUT, "straight_rooms.png")
    img.save(out)
    print("saved", out, img.size)

    # 断言
    assert (LOT["w"], LOT["h"]) == (20, 10), "占地须为 20×10"
    assert all(len(row) == 15 for row in GRID) and len(GRID) == 8
    assert sum(row.count("D") for row in GRID) == 4
    bed = next(f for f in FURNITURE if f["fid"] == "bed_double")
    assert bed["rect"][2:] == (2, 2), "穷家双人床 2×2"
    assert not any(f["rect"][2:] == (3, 3) for f in FURNITURE), "陆家不得有 3×3 床"
    assert all(f["short"] for f in FURNITURE), "每件家具都要有图上短名"
    yard_zones = [f for f in FURNITURE if f["zone"] == "yard" and f["fid"] != "privy"]
    assert len(yard_zones) >= 2, "院子至少 2 件可搜证家具（水缸+柴堆）"
    for f in FURNITURE:
        fx, fy, fw, fh = f["rect"]
        assert LOT["x"] <= fx and fx + fw <= LOT["x"] + LOT["w"]
        assert LOT["y"] <= fy and fy + fh <= LOT["y"] + LOT["h"], f"{f['fid']} 越出占地"
        if f["zone"] == "house":
            assert 0 <= fx and fx + fw <= 15 and 0 <= fy and fy + fh <= 8
    # 门洞两侧各留一格净空：家具不得堵门（用户 m01331 发现的坑）
    def occupied(gx, gy):
        for f in FURNITURE:
            fx, fy, fw, fh = f["rect"]
            if fx <= gx < fx + fw and fy <= gy < fy + fh:
                return f["fid"]
        return None

    for (dx, dy_, label) in DOORS:
        assert GRID[dy_][dx] == "D"
        if dy_ in (0, 7):  # 横墙上的门（大门）：通行方向是上下
            neighbors = (("内侧", dx, dy_ - 1), ("外侧", dx, dy_ + 1))
        else:             # 竖墙上的门（房门）：通行方向是左右
            neighbors = (("内侧", dx + 1, dy_), ("外侧", dx - 1, dy_))
        for side, cx, cy in neighbors:
            assert occupied(cx, cy) is None, f"{label} {side}({cx},{cy}) 被家具堵住"
    print(f"ALL PASS - lot 20x10, house 15x8, {len(FURNITURE)} furn all labeled, "
          f"{len(yard_zones)} yard items, full list visible, 4 doors valid")


if __name__ == "__main__":
    main()
