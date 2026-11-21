"""
房型方案 v4b —— 高分辨率版：一个房型一张图，平面图与外观 1:1 等大

改动（针对"太模糊"）：
  1. 出图倍率 3x → 4x（一格 = 64px）
  2. 不再一张大图挤五个房型 —— 每个房型单独一张，100% 放大能看清每格
  3. 平面图从半缩改为全尺寸，与外观严格 1:1 对照
  4. 房间直接标名（堂屋/厢房/天井/倒座）

翼组合法则（与星露谷同款）：
  房屋 = 若干矩形翼。屋脊沿翼长轴。南翼压北翼檐。
  翼交接处墙体自动消解成连通，跨翼房间不用开门洞。
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))

C = {
    "bg": "#1b1a17", "text": "#d8d2c4", "text_dim": "#8c8578",
    "grid": "#332f2a", "key": "#d8b878", "room": "#e8dcc0",
}

FONTS = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]

def font(size):
    for p in FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

TILE = 16
SCALE = 4
T = TILE * SCALE          # 64 px / 格

MAT = {
    "mud":    dict(roof="#9c8c5a", roof_d="#7c6e44", roof_l="#b8a878",
                   wall="#a89070", wall_d="#877255"),
    "thatch": dict(roof="#a89058", roof_d="#8a7444", roof_l="#c8ac74",
                   wall="#c0a480", wall_d="#9c8462"),
    "tile":   dict(roof="#7a5a52", roof_d="#5c4038", roof_l="#9a7268",
                   wall="#b89a72", wall_d="#8a7355"),
    "slate":  dict(roof="#5e6068", roof_d="#43454c", roof_l="#7e828c",
                   wall="#a89c88", wall_d="#827868"),
}


# ============================================================
# 翼 → 平面图
# ============================================================

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

    doorset = set(doors)
    gateset = set(gate or ())
    rows = []
    for j in range(Y0, Y1 + 1):
        row = ""
        for i in range(X0, X1 + 1):
            if (i, j) in gateset:
                row += "G"
            elif (i, j) in doorset:
                row += "D"
            elif (i, j) in interior:
                row += "."
            elif is_wall(i, j):
                row += "#"
            else:
                row += " "
        rows.append(row)
    return rows


def ridge_of(wing):
    x, y, w, h = wing
    return "h" if w >= h else "v"


# ============================================================
# 房型定义（wings, bounds, doors, gate, name, size, yards, rooms）
# ============================================================

def plan_straight():
    wings = [(0, 0, 11, 5)]
    doors = [(5, 4)]
    return wings, (0, 0, 10, 5), doors, None, "一字形", (11, 6), [], \
        [(5, 2, "堂屋 · 卧室")]


def plan_L():
    wings = [(0, 0, 11, 5), (6, 3, 5, 6)]
    doors = [(5, 4), (8, 8)]
    return wings, (0, 0, 10, 8), doors, None, "L 形", (11, 9), [], \
        [(4, 2, "堂屋"), (8, 6, "灶间 · 储物")]


def plan_wei():
    wings = [(0, 0, 13, 5), (0, 3, 4, 7), (9, 3, 4, 7)]
    doors = [(6, 4), (3, 4), (9, 4)]
    return wings, (0, 0, 12, 9), doors, None, "凹形", (13, 10), \
        [(4, 5, 8, 9)], \
        [(6, 2, "北堂"), (1, 6, "西厢"), (11, 6, "东厢"), (6, 7, "天井")]


def plan_siheyuan():
    wings = [(0, 0, 13, 5), (0, 3, 4, 7), (9, 3, 4, 7), (0, 8, 13, 4)]
    doors = [(6, 4), (3, 5), (9, 5), (6, 8)]
    gate = [(6, 11), (7, 11)]
    return wings, (0, 0, 12, 11), doors, gate, "四合院", (13, 12), \
        [(4, 5, 8, 7)], \
        [(6, 2, "北房"), (1, 6, "西厢"), (11, 6, "东厢"),
         (6, 9, "倒座"), (6, 6, "天井")]


def plan_liangjin():
    wings = [(0, 0, 11, 4), (0, 6, 11, 5), (0, 3, 2, 4), (9, 3, 2, 4)]
    doors = [(5, 3), (5, 6), (1, 5), (9, 5)]
    return wings, (0, 0, 10, 10), doors, None, "两进带院", (11, 11), \
        [(2, 4, 8, 5)], \
        [(5, 1, "前厅"), (5, 4, "天井"), (5, 8, "后堂")]


SHAPES = [
    (plan_straight, "thatch", "最简：一翼。陆家 / 周家的原型。"),
    (plan_L, "tile", "两翼相接。转角处墙体自动消解，两翼互通，不用开门洞。"),
    (plan_wei, "slate", "三翼围半院：北堂 + 东西厢，院墙就是两厢本身。"),
    (plan_siheyuan, "slate", "四翼围全院。沈家 2001 形态，村中首富。"),
    (plan_liangjin, "tile", "前后两进 + 窄廊。介于 L 与凹之间，带月台天井。"),
]


# ============================================================
# 绘制
# ============================================================

def roof_h(d, ox, oy, w, h, m, t):
    ins = max(2, int(w * 0.05))
    ridge = oy + int(h * 0.42)
    d.polygon([(ox + ins, oy), (ox + w - ins, oy), (ox + w, ridge), (ox, ridge)],
              fill=m["roof_d"])
    d.polygon([(ox, ridge), (ox + w, ridge), (ox + w, oy + h), (ox, oy + h)],
              fill=m["roof"])
    d.line([(ox + ins, oy), (ox + w - ins, oy)], fill=m["roof_l"], width=max(2, t // 9))
    rows = max(3, (oy + h - ridge) // max(1, t // 3))
    for i in range(1, rows):
        yy = ridge + (oy + h - ridge) * i / rows
        d.line([(ox, yy), (ox + w, yy)],
               fill=m["roof_d"] if i % 2 else m["roof"], width=max(1, t // 15))


def roof_v(d, ox, oy, w, h, m, t):
    mid = ox + w // 2
    ins = max(2, int(h * 0.05))
    d.polygon([(ox, oy + ins), (mid, oy), (mid, oy + h), (ox, oy + h - ins)],
              fill=m["roof_l"])
    d.polygon([(mid, oy), (ox + w, oy + ins), (ox + w, oy + h - ins), (mid, oy + h)],
              fill=m["roof_d"])
    d.line([(mid, oy + 1), (mid, oy + h - 1)], fill=m["wall"], width=max(1, t // 16))
    cols = max(2, w // max(1, t // 2))
    for i in range(1, cols):
        xx = ox + w * i / cols
        col = m["roof_d"] if xx > mid else m["roof"]
        d.line([(xx, oy + ins), (xx, oy + h - ins)], fill=col, width=max(1, t // 15))


def draw_house(d, ox, oy, wings, m, t=T, yards=()):
    # 先铺院子底色（俯视时天井露出地面），再画翼（后画的压住前画的檐）
    for (yx0, jy0, yx1, jy1) in yards:
        d.rectangle([ox + yx0 * t, oy + jy0 * t,
                     ox + (yx1 + 1) * t, oy + (jy1 + 1) * t], fill="#5f6a42")
    for wing in sorted(wings, key=lambda w: (w[1], w[0])):
        x, y, w, h = wing
        px, py = ox + x * t, oy + y * t
        W, H = w * t, h * t
        roof_h(d, px, py, W, H, m, t) if ridge_of(wing) == "h" \
            else roof_v(d, px, py, W, H, m, t)


def draw_ridge_arrows(d, ox, oy, wings, t=T):
    for (x, y, w, h) in wings:
        cx = ox + (x + w / 2) * t
        cy = oy + (y + h / 2) * t
        if ridge_of((x, y, w, h)) == "h":
            a, b = (cx - w * t * 0.28, cy), (cx + w * t * 0.28, cy)
        else:
            a, b = (cx, cy - h * t * 0.28), (cx, cy + h * t * 0.28)
        d.line([a, b], fill="#ffe9a0", width=max(3, t // 14))
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        for end, aa in ((b, ang), (a, ang + math.pi)):
            s = t * 0.45
            d.polygon([end,
                       (end[0] - s * math.cos(aa - 0.5), end[1] - s * math.sin(aa - 0.5)),
                       (end[0] - s * math.cos(aa + 0.5), end[1] - s * math.sin(aa + 0.5))],
                      fill="#ffe9a0")


def draw_plan(d, ox, oy, grid, yards=(), rooms=(), t=T):
    wall, floor, door, gatec = "#b89a72", "#6b5842", "#3a2a1c", "#5a4030"
    yardc = "#5f6a42"
    h = len(grid)
    w = max(len(r) for r in grid)

    yardset = set()
    for (yx0, jy0, yx1, jy1) in yards:
        for j in range(jy0, jy1 + 1):
            for i in range(yx0, yx1 + 1):
                yardset.add((i, j))

    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            px, py = ox + x * t, oy + y * t
            box = [px, py, px + t - 1, py + t - 1]
            if ch == " ":
                if (x, y) in yardset:
                    d.rectangle(box, fill=yardc)
                continue
            if ch == "#":
                d.rectangle(box, fill=wall)
                d.line([(px, py), (px + t - 1, py)], fill="#cfb08a", width=max(1, t // 24))
                d.line([(px, py), (px, py + t - 1)], fill="#cfb08a", width=max(1, t // 24))
            elif ch == ".":
                d.rectangle(box, fill=floor)
            elif ch == "D":
                d.rectangle(box, fill=door)
                d.line([(px, py + t - 2), (px + t - 1, py + t - 2)],
                       fill="#c9a05a", width=max(1, t // 20))
            elif ch == "G":
                d.rectangle(box, fill=gatec)
                d.line([(px, py), (px + t - 1, py)], fill="#8a6a4a", width=max(1, t // 20))

    for x in range(w + 1):
        d.line([(ox + x * t, oy), (ox + x * t, oy + h * t)], fill=C["grid"])
    for y in range(h + 1):
        d.line([(ox, oy + y * t), (ox + w * t, oy + y * t)], fill=C["grid"])

    f = font(max(16, t // 3))
    for (rx, ry, txt) in rooms:
        d.text((ox + (rx + 0.5) * t, oy + (ry + 0.5) * t), txt,
               font=f, fill=C["room"], anchor="mm")

    return w * t, h * t


def label(d, xy, text, size=22, color=None, anchor=None):
    d.text(xy, text, font=font(size), fill=color or C["text"], anchor=anchor)


def legend(d, x, y):
    items = [("#b89a72", "墙"), ("#6b5842", "室内"), ("#5f6a42", "院子"),
             ("#3a2a1c", "门"), ("#5a4030", "大门")]
    for col, name in items:
        d.rectangle([x, y - 14, x + 22, y + 6], fill=col)
        label(d, (x + 30, y - 10), name, 20, C["text_dim"])
        x += 30 + font(20).getlength(name) + 34
    return x


# ============================================================
# 每个房型一张图
# ============================================================

def sheet_one(fn, mat, blurb, fname):
    wings, bounds, doors, gate, name, size, yards, rooms = fn()
    grid = wings_to_grid(wings, bounds, doors, gate)

    pad, top, gap = 56, 240, 150
    ext_w, ext_h = size[0] * T, size[1] * T
    plan_w = max(len(r) for r in grid) * T
    plan_h = len(grid) * T

    W = pad * 2 + ext_w + gap + plan_w
    H = top + max(ext_h, plan_h) + 130

    img = Image.new("RGB", (W, H), C["bg"])
    d = ImageDraw.Draw(img)

    label(d, (pad, 30), name, 46)
    label(d, (pad, 96),
          f"外观占地 {size[0]}×{size[1]} 格 = {size[0]*16}×{size[1]*16} px ｜ "
          f"翼数 {len(wings)} ｜ 材质 {mat}", 24, C["text_dim"])
    label(d, (pad, 134), blurb, 24, C["key"])
    label(d, (pad, 168),
          "平面图 = 外观占地 1:1。室内可走区 + 墙厚，一格不差（Shift 进屋的前提）。",
          20, C["text_dim"])

    label(d, (pad, top - 34), "俯视 3/4 外观（黄箭头 = 屋脊方向）", 25)
    draw_house(d, pad, top, wings, MAT[mat], yards=yards)
    draw_ridge_arrows(d, pad, top, wings)

    px = pad + ext_w + gap
    label(d, (px, top - 34), "俯视平面（程序生成）", 25)
    draw_plan(d, px, top, grid, yards=yards, rooms=rooms)

    legend(d, pad, H - 46)

    out = os.path.join(OUT, fname)
    img.save(out)
    print("saved", out, img.size)


def sheet_evolution():
    """沈家宅第五帧演变：每代加一翼，旧翼不拆。"""
    stages = [
        ("1926 · 土坯长屋", plan_straight, "mud", "创业期：一翼"),
        ("1951 · L 形青瓦", plan_L, "tile", "加右翼：灶间独立"),
        ("1976 · 凹形两厢", plan_wei, "slate", "加东西两厢，围半院"),
        ("2001 · 四合院", plan_siheyuan, "slate", "加南倒座，围全院"),
    ]
    pad, top, gap = 56, 260, 60
    cw = 13 * T + pad
    chh = 12 * T + 120
    W = pad * 2 + cw * 2 + gap
    H = top + chh * 2 + 120

    img = Image.new("RGB", (W, H), C["bg"])
    d = ImageDraw.Draw(img)

    label(d, (pad, 30), "沈家宅第 · 五帧演变 = 逐级加翼", 44)
    label(d, (pad, 92), "阶级上升写在建筑上。玩家在时间轴连按 W，看到同一块地「长出来」——这就是搜证。",
          24, C["text_dim"])
    label(d, (pad, 130), "旧翼永远不拆，新翼贴着旧翼接。2026 年：四合院全拆，超市压在原址上。",
          24, C["key"])
    label(d, (pad, 166), "每格 16px，出图 4 倍。黄箭头 = 各翼屋脊方向。", 20, C["text_dim"])

    for i, (name, fn, mat, note) in enumerate(stages):
        wings, bounds, doors, gate, _, size, yards, rooms = fn()
        col, row = i % 2, i // 2
        ox = pad + col * (cw + gap)
        oy = top + row * chh
        label(d, (ox, oy - 40), name, 28)
        label(d, (ox, oy - 8), note, 20, C["text_dim"])
        draw_house(d, ox, oy + 26, wings, MAT[mat], yards=yards)
        draw_ridge_arrows(d, ox, oy + 26, wings)

    out = os.path.join(OUT, "evolution_v4.png")
    img.save(out)
    print("saved", out, img.size)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    names = ["v4_straight.png", "v4_L.png", "v4_wei.png",
             "v4_siheyuan.png", "v4_liangjin.png"]
    for (fn, mat, blurb), fname in zip(SHAPES, names):
        sheet_one(fn, mat, blurb, fname)
    sheet_evolution()
