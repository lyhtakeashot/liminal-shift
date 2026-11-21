"""
建筑方格图 v2 —— 放大版，按「人=1×2格」的真实居住尺度重定房型。

改动（针对「尺寸小了，沈家尤其小」）：
  - 房间按家具占位反推：一张床 = 2×1 格（§4.6.2 档位），人 = 1×2 格
  - 陆家：夫妻+长辈 = 主卧(2×1床+柜) + 次卧(2×1床) + 灶台 + 堂屋 + 如厕角，
    一字形从 11×6 放大到 15×8（室内 13×6=78格）
  - 沈家逐代放大：一字形 15×8 → L形 17×14 → 凹形 19×16 → 四合院 21×19
    院/天井保持宽敞，房间数逐代增加（阶级上升写在面积上）
  - 出图每格 32 屏幕像素；主角标记仍按真实比例 1 格宽 2 格高（占地 1 格）

输出：_ref/houses/house_grid_chart.png
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
SCALE = 32          # 显示用：每格 32 屏幕像素
TILE = 16           # 逻辑：每格 16px
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
    "bg": "#191814", "text": "#e6dfd0", "dim": "#9a9284", "key": "#e0bb74",
    "grid": "#38342c", "wall": "#b89a72", "floor": "#6b5842", "yard": "#5f6a42",
    "door": "#3a2a1c", "gate": "#5a4030", "player": "#e8543f",
    "player_edge": "#ffd9c4", "ruler": "#c9c0ae", "dimline": "#7fa8c8",
}


def wings_to_grid(wings, bounds, doors=(), gate=None):
    X0, Y0, X1, Y1 = bounds
    interior = set()
    for (x, y, w, h) in wings:
        for j in range(y + 1, y + h - 1):
            for i in range(x + 1, x + w - 1):
                interior.add((i, j))

    def is_wall(i, j):
        if (i, j) in interior:
            return False
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (i + di, j + dj) in interior:
                return True
        return False

    dset, gset = set(doors), set(gate or ())
    rows = []
    for j in range(Y0, Y1 + 1):
        row = ""
        for i in range(X0, X1 + 1):
            if (i, j) in gset:
                row += "G"
            elif (i, j) in dset:
                row += "D"
            elif (i, j) in interior:
                row += "."
            elif is_wall(i, j):
                row += "#"
            else:
                row += " "
        rows.append(row)
    return rows


# ---------- 放大后的房型（翼坐标含墙，单位格） ----------
HOUSES = [
    dict(name="一字形 · 放大（陆家 / 周家原型）", frame="A1 · 1926 陆家 / 沈家早期",
         wings=[(0, 0, 15, 8)], bounds=(0, 0, 14, 7), doors=[(7, 7)],
         yard=None, size=(15, 8), player_at=(7, 3),
         rooms=[(3, 3, "主卧"), (8, 3, "次卧"), (11, 3, "灶"),
                (5, 5, "堂屋"), (13, 5, "厕角")],
         note="夫妻+长辈：主卧2×1床+柜、次卧2×1床、灶台、堂屋、如厕角。"),

    dict(name="L 形 · 放大（沈家 1951）", frame="A2 · 1951 沈家",
         wings=[(0, 0, 15, 8), (9, 5, 8, 9)], bounds=(0, 0, 16, 13),
         doors=[(7, 7), (12, 13)], yard=None, size=(17, 14), player_at=(5, 3),
         rooms=[(3, 3, "主卧"), (8, 3, "子女房"),
                (5, 6, "堂屋"), (12, 8, "灶间"), (12, 11, "储物")],
         note="加右翼灶间+储物；主屋面宽加大，子女房出现。"),

    dict(name="凹形 · 放大（沈家 1976）", frame="A3 · 1976 沈家",
         wings=[(0, 0, 19, 7), (0, 4, 6, 11), (13, 4, 6, 11)],
         bounds=(0, 0, 18, 14), doors=[(9, 6), (4, 6), (14, 6)],
         yard=(6, 7, 12, 14), size=(19, 15), player_at=(9, 10),
         rooms=[(9, 3, "北堂"), (2, 8, "西厢"), (16, 8, "东厢"),
                (9, 11, "天井")],
         note="东西两厢围半院，北堂扩到19格宽；天井可停石磨。"),

    dict(name="四合院 · 放大（沈家 2001）", frame="A4 · 2001 沈家",
         wings=[(0, 0, 21, 7), (0, 4, 6, 12), (15, 4, 6, 12), (0, 14, 21, 5)],
         bounds=(0, 0, 20, 18), doors=[(10, 6), (4, 7), (16, 7), (10, 14)],
         gate=[(10, 18), (11, 18)], yard=(6, 7, 14, 13), size=(21, 19),
         player_at=(10, 10),
         rooms=[(10, 3, "北堂"), (2, 9, "西厢"), (18, 9, "东厢"),
                (10, 16, "倒座·账房"), (10, 10, "天井")],
         note="四面围死；倒座设账房，天井摆石磨（跨70年物证）。"),

    dict(name="两进带院（备用）", frame="过渡形态 · 备用",
         wings=[(0, 0, 15, 6), (0, 9, 15, 7), (0, 4, 3, 6), (12, 4, 3, 6)],
         bounds=(0, 0, 14, 15), doors=[(7, 5), (7, 9), (1, 7), (13, 7)],
         yard=(3, 6, 11, 8), size=(15, 16), player_at=(7, 7),
         rooms=[(7, 3, "前厅"), (7, 7, "天井"), (7, 12, "后堂")],
         note="前厅+月台天井+后堂，窄廊连接。备用形态。"),
]


def draw_grid(d, ox, oy, grid, h, yard, player_at, w, rooms):
    yardset = set()
    if yard:
        x0, y0, x1, y1 = yard
        for j in range(y0, y1 + 1):
            for i in range(x0, x1 + 1):
                yardset.add((i, j))

    for row_i, row in enumerate(grid):
        for col_i, ch in enumerate(row):
            px, py = ox + col_i * SCALE, oy + row_i * SCALE
            box = [px, py, px + SCALE - 1, py + SCALE - 1]
            fill = {"#": C["wall"], ".": C["floor"], "D": C["door"],
                    "G": C["gate"]}.get(ch)
            if ch == " " and (col_i, row_i) in yardset:
                fill = C["yard"]
            if fill:
                d.rectangle(box, fill=fill)

    for x in range(w + 1):
        d.line([(ox + x * SCALE, oy), (ox + x * SCALE, oy + h * SCALE)],
               fill=C["grid"], width=1)
    for y in range(h + 1):
        d.line([(ox, oy + y * SCALE), (ox + w * SCALE, oy + y * SCALE)],
               fill=C["grid"], width=1)

    f = font(13)
    for x in range(w):
        d.text((ox + x * SCALE + SCALE / 2, oy - 12), str(x),
               font=f, fill=C["ruler"], anchor="mm")
    for y in range(h):
        d.text((ox - 10, oy + y * SCALE + SCALE / 2), str(y),
               font=f, fill=C["ruler"], anchor="mm")

    # 主角：宽 1 格、视觉高 2 格，脚踩 player_at 那格
    px, py = ox + player_at[0] * SCALE, oy + player_at[1] * SCALE
    pw, ph = SCALE, 2 * SCALE
    top = py - (ph - SCALE)
    d.rectangle([px + 2, top + 2, px + pw - 3, py + SCALE - 3],
                fill=C["player"], outline=C["player_edge"], width=2)
    d.ellipse([px + pw * 0.28, top + ph * 0.12,
               px + pw * 0.72, top + ph * 0.40], fill=C["player_edge"])

    # 房间名
    rf = font(14)
    for (rx, ry, txt) in rooms:
        d.text((ox + (rx + 0.5) * SCALE, oy + (ry + 0.5) * SCALE), txt,
               font=rf, fill="#efe4c8", anchor="mm")


def draw_dim(d, ox, oy, w, h):
    f = font(15)
    col = C["dimline"]
    y = oy + h * SCALE + 12
    d.line([(ox, y), (ox + w * SCALE, y)], fill=col, width=2)
    d.line([(ox, y - 5), (ox, y + 5)], fill=col, width=2)
    d.line([(ox + w * SCALE, y - 5), (ox + w * SCALE, y + 5)], fill=col, width=2)
    d.text((ox + w * SCALE / 2, y + 7), f"{w} 格 = {w*TILE} px",
           font=f, fill=col, anchor="ma")
    x = ox + w * SCALE + 14
    d.line([(x, oy), (x, oy + h * SCALE)], fill=col, width=2)
    d.line([(x - 5, oy), (x + 5, oy)], fill=col, width=2)
    d.line([(x - 5, oy + h * SCALE), (x + 5, oy + h * SCALE)], fill=col, width=2)
    d.text((x + 10, oy + h * SCALE / 2), f"{h} 格 = {h*TILE} px",
           font=f, fill=col, anchor="lm")


def main():
    pad = 36
    col_gap = 50
    cell_w = max(hs["size"][0] for hs in HOUSES) * SCALE + 110
    row_h = 19 * SCALE + 200
    top = 200
    W = pad * 2 + cell_w * 2 + col_gap
    H = top + row_h * 3 + 40
    img = Image.new("RGB", (W, H), C["bg"])
    d = ImageDraw.Draw(img)

    d.text((pad, 20), "建筑方格图 v2 · 按居住尺度放大", font=font(36), fill=C["text"])
    d.text((pad, 72),
           "每格 = 16×16 px（逻辑像素）。红框=主角，宽1格×视觉高2格，占地1格。床=2×1格，灶台/柜=2×1或1×1格。",
           font=font(18), fill=C["dim"])
    d.rectangle([pad, 112, pad + 26, 138], fill=C["player"], outline=C["player_edge"], width=2)
    d.text((pad + 38, 125), "主角 16×32 px = 1×2 格",
           font=font(18), fill=C["key"], anchor="lm")
    d.text((pad, 158),
           "灰格=墙　棕格=室内　绿格=院/天井　深棕=门。陆家放大后才有空间放两张床+灶+厕角。",
           font=font(17), fill=C["dim"])

    for idx, hs in enumerate(HOUSES):
        col, row = idx % 2, idx // 2
        ox = pad + col * (cell_w + col_gap) + 26
        oy = top + row * row_h + 44
        w, h = hs["size"]
        grid = wings_to_grid(hs["wings"], hs["bounds"], hs["doors"], hs.get("gate"))
        d.text((ox, oy - 40), f"{idx+1}. {hs['name']}", font=font(22), fill=C["key"])
        d.text((ox, oy - 14),
               f"{hs['frame']} ｜ 占地 {w}×{h} 格 = {w*TILE}×{h*TILE} px ｜ 翼数 {len(hs['wings'])}",
               font=font(16), fill=C["text"])
        draw_grid(d, ox, oy, grid, h, hs.get("yard"), hs["player_at"], w, hs["rooms"])
        draw_dim(d, ox, oy, w, h)
        d.text((ox, oy + h * SCALE + 54), hs["note"], font=font(15), fill=C["dim"])

    out = os.path.join(OUT, "house_grid_chart.png")
    img.save(out)
    print("saved", out, img.size)

    # 断言
    for hs in HOUSES:
        w, h = hs["size"]
        assert w >= 15 and h >= 8, f"陆家/沈家最小尺寸不能小于 15×8: {hs['name']}"
        assert h * TILE % TILE == 0
    assert img.size == (W, H)
    print("ALL PASS - v2 chart: min footprint 15x8, player 1x2 tiles, canvas", img.size)


if __name__ == "__main__":
    main()
