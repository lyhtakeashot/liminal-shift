# -*- coding: utf-8 -*-
"""场景层资产生成器（A1-A3）：15 个唯一文件。

真相源：data/frames.json（场景几何） + _ref/art/_assets_a1a3/_a1a3_assets.json（尺寸）。
口径：1 格 = 32×32 px（TILE=32，scripts/house_shape.gd:13）。

产出（唯一路径 15 个）：
  river_a1/a2/a3.png   3200x416   河（河岸 + 水面），几何同、颜色随帧变
  dam.png              256x128    石坝（三帧共用）
  stele.png            32x32      界碑（图上 8px 宽）
  road_curved_tiles.png 3200x256  主路 A1/A2（弯道）；A3 直路另存 road_straight_a3.png 3200x96
  field_patch_tiles.png 672x384   碎田 A1（28 块）
  field_a2/a3.png      512x384    整块大田
  well_old_a1/a2/a3.png 64x64     老井三态（木架 / 石板 / 水泥封）
  tree_a1/a2/a3.png    64/128/192 老槐三态（树苗 / 中 / 大）
  ground_a1/a2/a3_tiles.png 32x32 地面底瓦（帧底色）
"""
import json
import os
import random
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from pixel_lib import Canvas, PAL, mix, hexc  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
SCENE = os.path.join(ROOT, "assets", "village", "scene")
FRAMES_PATH = os.path.join(ROOT, "data", "frames.json")
TILE = 32

FRAMES = {}
for _fr in json.load(open(FRAMES_PATH, encoding="utf-8"))["frames"]:
    FRAMES[_fr["id"]] = _fr


def out(name):
    p = os.path.join(SCENE, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


# ------------------------------------------------------------------ 通用小工具
def band(cv, xs, y0f, y1f, color):
    """在折线 xs 上画一条带（上边界 y0f(x)，下边界 y1f(x)）。"""
    pts = [(x, y0f(x)) for x in xs] + [(x, y1f(x)) for x in reversed(xs)]
    cv.poly(pts, color)


def tuft(cv, x, y, color, h=3):
    """一根草 / 一撮苗。"""
    cv.line(x, y, x, y - h, color, 1)


# ------------------------------------------------------------------ 河
def gen_river(fid, name):
    fr = FRAMES[fid]
    poly = next(s for s in fr["shapes"] if s["type"] == "polygon")
    pts = [(int(p[0]), int(p[1])) for p in poly["points"]]
    base = poly["color"]
    W, H = 3200, 416
    cv = Canvas(W, H)

    water = hexc(base)
    w_light = mix(base, "#ffffff", 0.26)
    w_dark = mix(base, "#000000", 0.30)
    w_deep = mix(base, "#000000", 0.45)

    # 河岸线（多边形在 y>0 的那条边）
    bank = {}
    for (x, y) in pts:
        if y > 0:
            bank[x] = max(bank.get(x, 0), y)
    xs = sorted(bank.keys())
    if not xs or xs[-1] != 3200:
        xs.append(3200)

    # 水面
    cv.poly(pts, base)
    # 近岸深水
    band(cv, xs, lambda x: bank[x] - 48, lambda x: bank[x], w_deep)
    band(cv, xs, lambda x: bank[x] - 24, lambda x: bank[x] - 2, w_dark)

    # 水纹（横向短划）
    rnd = random.Random(7)
    for _ in range(2600):
        x = rnd.randrange(0, W - 80)
        y = rnd.randrange(2, max(6, bank.get(x, 300) - 12))
        ln = rnd.choice((14, 22, 30, 38, 50))
        cv.line(x, y, min(W - 1, x + ln), y, w_light, 1)
    # 零星高光点
    for _ in range(500):
        x = rnd.randrange(0, W)
        y = rnd.randrange(2, max(6, bank.get(x, 300) - 20))
        cv.px(x, y, mix(base, "#ffffff", 0.45))

    # 河岸：湿泥 + 干沙
    wet = mix(PAL["sand"][1], base, 0.42)
    wet_dark = mix(wet, "#000000", 0.28)
    dry = PAL["sand"][1]
    band(cv, xs, lambda x: bank[x], lambda x: min(H - 1, bank[x] + 16), wet)
    band(cv, xs, lambda x: min(H - 1, bank[x] + 14), lambda x: min(H - 1, bank[x] + 18), wet_dark)
    band(cv, xs, lambda x: min(H - 1, bank[x] + 18), lambda x: min(H - 1, bank[x] + 34), dry)
    # 岸边草
    rnd2 = random.Random(11)
    for x in range(0, W, 3):
        if bank.get(x, 300) + 34 >= H:
            continue
        if rnd2.random() < 0.34:
            tuft(cv, x, bank.get(x, 300) + 33, PAL["grass"][1], rnd2.choice((2, 3, 4)))
    cv.save(out(name))
    return name


# ------------------------------------------------------------------ 石坝
def gen_dam(name="dam.png"):
    W, H = 256, 128
    cv = Canvas(W, H)
    water = mix("#3f5f6e", "#000000", 0.25)
    stone_l, stone, stone_d, stone_dd = PAL["stone"]
    # 上游水面
    cv.rect(0, 0, W, 40, water)
    rnd = random.Random(3)
    for _ in range(120):
        x = rnd.randrange(0, W - 30)
        y = rnd.randrange(2, 36)
        cv.line(x, y, x + rnd.choice((10, 16, 22)), y, mix("#3f5f6e", "#ffffff", 0.28), 1)
    # 坝体石块（两排错缝）
    for row, y0 in enumerate((40, 72)):
        x = 0
        while x < W:
            bw = 32 if row == 0 else 32
            off = 16 if row == 1 else 0
            x0 = x - off
            cv.rect(x0, y0, x0 + bw - 2, y0 + 30, stone)
            cv.rect(x0, y0, x0 + bw - 2, y0 + 2, stone_l)
            cv.rect(x0, y0 + 27, x0 + bw - 2, y0 + 30, stone_d)
            cv.box(x0, y0, x0 + bw - 2, y0 + 30, stone_dd, 1)
            x += bw
    # 坝顶受光
    cv.rect(0, 38, W, 42, stone_l)
    # 苔痕
    for _ in range(90):
        x = rnd.randrange(0, W)
        y = rnd.randrange(44, 100)
        cv.px(x, y, PAL["leaf_d"][2])
    # 下游白沫
    cv.rect(0, 104, W, H, mix(water, "#ffffff", 0.30))
    for _ in range(160):
        x = rnd.randrange(0, W)
        y = rnd.randrange(104, H)
        cv.px(x, y, mix(water, "#ffffff", 0.55))
    cv.save(out(name))
    return name


# ------------------------------------------------------------------ 界碑
def gen_stele(name="stele.png"):
    W, H = 32, 32
    cv = Canvas(W, H)
    sl, st, sd, sdd = PAL["stone"]
    # 半截石碑：图上 8px 宽
    cv.rect(12, 3, 19, 29, st)
    cv.rect(12, 3, 14, 29, sl)
    cv.rect(17, 3, 19, 29, sd)
    # 断口
    cv.rect(11, 3, 12, 6, sd)
    cv.rect(19, 3, 20, 7, sd)
    cv.rect(13, 3, 18, 4, sdd)
    # 刻痕
    cv.rect(14, 11, 17, 12, sdd)
    cv.rect(14, 15, 16, 16, sdd)
    cv.rect(14, 19, 17, 20, sdd)
    # 土坡
    cv.rect(8, 27, 24, 31, PAL["dirt"][2])
    cv.rect(9, 26, 23, 28, PAL["dirt"][1])
    for x in range(7, 26, 3):
        tuft(cv, x, 27, PAL["grass"][1], 2)
    cv.save(out(name))
    return name


# ------------------------------------------------------------------ 主路
def road_cells(fid):
    """返回世界坐标下的路面格集合 {(cx, cy)}。"""
    fr = FRAMES[fid]
    cells = set()
    for s in fr["shapes"]:
        if s["type"] == "rect" and s.get("road"):
            x, y, w, h = s["rect"]
            for cy in range(y // TILE, (y + h) // TILE):
                for cx in range(x // TILE, (x + w) // TILE):
                    cells.add((cx, cy))
    return cells


def gen_road(fid, name):
    cells = road_cells(fid)
    if not cells:
        return None
    x0 = min(c[0] for c in cells)
    x1 = max(c[0] for c in cells)
    y0 = min(c[1] for c in cells)
    y1 = max(c[1] for c in cells)
    W = (x1 - x0 + 1) * TILE
    H = (y1 - y0 + 1) * TILE
    cv = Canvas(W, H)
    road = PAL["dirt"][1]
    road_l = PAL["dirt"][0]
    road_d = PAL["dirt"][2]
    road_dd = PAL["dirt"][3]
    dirt = PAL["earth"][1]
    rnd = random.Random(23)
    for (cx, cy) in cells:
        px = (cx - x0) * TILE
        py = (cy - y0) * TILE
        cv.rect(px, py, px + TILE, py + TILE, road)
        # 边缘：邻格不是路面就压边（路缘）
        if (cx, cy - 1) not in cells:
            cv.rect(px, py, px + TILE, py + 3, road_l)
        if (cx, cy + 1) not in cells:
            cv.rect(px, py + TILE - 3, px + TILE, py + TILE, road_d)
        if (cx - 1, cy) not in cells:
            cv.rect(px, py, px + 3, py + TILE, road_l)
        if (cx + 1, cy) not in cells:
            cv.rect(px + TILE - 3, py, px + TILE, py + TILE, road_d)
        # 车辙与碎石
        for _ in range(9):
            dx = rnd.randrange(2, TILE - 2)
            dy = rnd.randrange(2, TILE - 2)
            cv.px(px + dx, py + dy, dirt)
        for _ in range(3):
            dx = rnd.randrange(2, TILE - 3)
            dy = rnd.randrange(3, TILE - 3)
            cv.rect(px + dx, py + dy, px + dx + 2, py + dy + 1, road_dd)
    cv.save(out(name))
    return name


# ------------------------------------------------------------------ 田
def field_rects(fid, color=None):
    fr = FRAMES[fid]
    out_rects = []
    for s in fr["shapes"]:
        if s["type"] != "rect":
            continue
        if s.get("label"):
            continue
        if color and s.get("color") != color:
            continue
        if not color and s.get("road"):
            continue
        out_rects.append(s)
    return out_rects


def draw_patch(cv, px, py, pw, ph, green, seed):
    """一块田：土底 + 作物行 + 田埂。"""
    rnd = random.Random(seed)
    cv.rect(px, py, px + pw, py + ph, green)
    # 垄（横条纹）
    row_h = 16
    y = py + 4
    k = 0
    while y < py + ph - 2:
        shade = mix(green, "#000000", 0.14) if k % 2 else mix(green, "#ffffff", 0.10)
        cv.rect(px + 3, y, px + pw - 3, y + row_h - 4, shade)
        # 苗
        for _ in range(max(1, (pw // 26))):
            mx = px + rnd.randrange(5, max(6, pw - 6))
            tuft(cv, mx, y + row_h - 5, mix(green, "#ffffff", 0.34), rnd.choice((3, 4)))
            tuft(cv, mx + 1, y + row_h - 5, mix(green, "#000000", 0.18), 3)
        y += row_h
        k += 1
    # 田埂
    cv.rect(px, py, px + pw, py + 3, PAL["earth"][0])
    cv.rect(px, py + ph - 3, px + pw, py + ph, PAL["earth"][2])
    cv.rect(px, py, px + 3, py + ph, PAL["earth"][1])
    cv.rect(px + pw - 3, py, px + pw, py + ph, PAL["earth"][2])
    # 零星土块
    for _ in range(max(4, pw * ph // 900)):
        dx = rnd.randrange(4, max(5, pw - 4))
        dy = rnd.randrange(4, max(5, ph - 4))
        cv.rect(px + dx, py + dy, px + dx + 2, py + dy + 1, PAL["earth"][3])


def gen_field_patches(name="field_patch_tiles.png"):
    fid = "a1_1926"
    rects = field_rects(fid, color="#7d8a3e")
    x0 = min(r["rect"][0] for r in rects)
    y0 = min(r["rect"][1] for r in rects)
    x1 = max(r["rect"][0] + r["rect"][2] for r in rects)
    y1 = max(r["rect"][1] + r["rect"][3] for r in rects)
    W, H = x1 - x0, y1 - y0
    cv = Canvas(W, H)
    for i, r in enumerate(rects):
        x, y, w, h = r["rect"]
        draw_patch(cv, x - x0, y - y0, w, h, r["color"], seed=100 + i)
    cv.save(out(name))
    return name


def gen_field_solid(fid, name, color):
    rects = field_rects(fid, color=color)
    if not rects:
        return None
    x, y, w, h = rects[0]["rect"]
    cv = Canvas(w, h)
    # 2026-11-22 世界重构线：Python 字符串 hash 每进程随机（PYTHONHASHSEED），
    # 会让田图每次重跑都变、制造无意义 diff。改用稳定种子 crc32。
    draw_patch(cv, 0, 0, w, h, color, seed=zlib.crc32(fid.encode("utf-8")) & 0xFFFF)
    cv.save(out(name))
    return name


# ------------------------------------------------------------------ 老井
def well_rim(cv, x0, y0, x1, y1, stone_pal="stone"):
    sl, st, sd, sdd = PAL[stone_pal]
    cv.rect(x0, y0, x1, y1, st)
    cv.rect(x0, y0, x1, y0 + 4, sl)
    cv.rect(x0, y1 - 4, x1, y1, sd)
    cv.rect(x0, y0, x0 + 4, y1, sl)
    cv.rect(x1 - 4, y0, x1, y1, sd)
    # 砖缝
    for yy in range(y0 + 8, y1 - 4, 10):
        cv.rect(x0 + 4, yy, x1 - 4, yy + 1, sdd)
    for xx in range(x0 + 10, x1 - 4, 14):
        cv.rect(xx, y0 + 4, xx + 1, y1 - 4, sdd)


def gen_well(fid, name):
    W = H = 64
    cv = Canvas(W, H)
    if fid == "a1_1926":
        # 木架：开挖 + 支架 + 吊桶
        well_rim(cv, 10, 12, 54, 52)
        cv.ellipse(14, 16, 50, 46, PAL["ink"][1])
        cv.ellipse(17, 19, 47, 42, PAL["ink"][0])
        wl, wd, wdd = PAL["wood_d"][0], PAL["wood_d"][1], PAL["wood_d"][2]
        cv.rect(12, 4, 15, 26, wl)
        cv.rect(49, 4, 52, 26, wl)
        cv.rect(12, 4, 52, 8, wd)
        cv.rect(12, 6, 52, 7, PAL["wood_d"][0])
        cv.rect(30, 8, 31, 22, PAL["ink"][2])
        cv.rect(26, 22, 35, 30, PAL["wood"][1])
        cv.rect(26, 22, 35, 24, PAL["wood"][0])
        cv.rect(26, 28, 35, 30, PAL["wood"][3])
        cv.rect(29, 30, 32, 31, PAL["wood"][2])
    elif fid == "a2_1951":
        # 石板封盖
        well_rim(cv, 8, 10, 56, 54)
        sl, st, sd, sdd = PAL["stone"]
        cv.rect(11, 13, 53, 33, st)
        cv.rect(11, 13, 53, 16, sl)
        cv.rect(11, 30, 53, 33, sd)
        cv.box(11, 13, 53, 33, sdd, 1)
        cv.rect(11, 22, 53, 23, sdd)
        cv.rect(30, 13, 31, 33, sdd)
        cv.rect(14, 34, 50, 50, PAL["ink"][2])
        cv.rect(16, 36, 48, 48, PAL["ink"][1])
        cv.rect(16, 36, 48, 38, PAL["ink"][0])
    else:
        # 水泥封
        well_rim(cv, 8, 10, 56, 54, stone_pal="stone")
        cm_l, cm, cm_d, cm_dd = PAL["stone"]
        cv.rect(10, 12, 54, 34, mix(cm, "#ffffff", 0.22))
        cv.rect(10, 12, 54, 15, mix(cm, "#ffffff", 0.40))
        cv.rect(10, 31, 54, 34, cm_d)
        cv.box(10, 12, 54, 34, cm_dd, 1)
        # 裂纹
        cv.line(30, 13, 34, 20, cm_dd, 1)
        cv.line(34, 20, 31, 26, cm_dd, 1)
        cv.line(31, 26, 36, 33, cm_dd, 1)
        # 水泥台
        cv.rect(10, 34, 54, 52, mix(cm, "#000000", 0.12))
        cv.rect(10, 34, 54, 36, mix(cm, "#ffffff", 0.30))
        for x in range(12, 54, 8):
            cv.rect(x, 36, x + 1, 52, cm_dd)
    cv.save(out(name))
    return name


# ------------------------------------------------------------------ 老槐
def canopy(cv, cx, cy, r, seed):
    rnd = random.Random(seed)
    cv.ellipse(cx - r, cy - r, cx + r, cy + r, PAL["leaf_d"][3])
    steps = [(0.86, PAL["leaf_d"][1]), (0.68, PAL["leaf_d"][0]),
             (0.48, PAL["leaf"][2]), (0.30, PAL["leaf"][0])]
    for frac, col in steps:
        rr = max(2, int(r * frac))
        cv.ellipse(cx - rr, cy - int(rr * 0.92), cx + rr, cy + int(rr * 0.92), col)
    # 叶簇颗粒（只在树冠内）
    for _ in range(int(r * 2.6)):
        x = rnd.randint(cx - r + 3, cx + r - 3)
        y = rnd.randint(cy - r + 3, cy + r - 3)
        if ((x - cx) / float(r)) ** 2 + ((y - cy) / float(r)) ** 2 > 1.0:
            continue
        cv.px(x, y, PAL["leaf"][1] if rnd.random() < 0.5 else PAL["leaf_d"][3])


def gen_tree(fid, name):
    W, H = {"a1_1926": (64, 64), "a2_1951": (128, 128), "a3_1976": (192, 192)}[fid]
    cv = Canvas(W, H)
    wl, wd, wdd = PAL["wood_d"][0], PAL["wood_d"][1], PAL["wood_d"][2]
    cx = W // 2
    if fid == "a1_1926":
        # 树苗
        cv.rect(cx - 2, H - 22, cx + 2, H - 6, wd)
        cv.rect(cx - 2, H - 22, cx - 1, H - 6, wl)
        cv.rect(cx + 1, H - 22, cx + 2, H - 6, wdd)
        canopy(cv, cx, H - 30, 15, seed=5)
        cv.shadow_ellipse(cx, H - 7, 12, 4)
    elif fid == "a2_1951":
        cv.rect(cx - 4, H - 46, cx + 4, H - 8, wd)
        cv.rect(cx - 4, H - 46, cx - 2, H - 8, wl)
        cv.rect(cx + 2, H - 46, cx + 4, H - 8, wdd)
        cv.line(cx, H - 40, cx - 12, H - 52, wd, 2)
        cv.line(cx, H - 36, cx + 13, H - 50, wd, 2)
        canopy(cv, cx, H - 62, 34, seed=9)
        cv.shadow_ellipse(cx, H - 8, 30, 9)
    else:
        cv.rect(cx - 7, H - 74, cx + 7, H - 10, wd)
        cv.rect(cx - 7, H - 74, cx - 3, H - 10, wl)
        cv.rect(cx + 4, H - 74, cx + 7, H - 10, wdd)
        cv.line(cx, H - 62, cx - 26, H - 84, wd, 3)
        cv.line(cx, H - 56, cx + 27, H - 80, wd, 3)
        cv.line(cx - 26, H - 84, cx - 40, H - 96, wd, 2)
        cv.line(cx + 27, H - 80, cx + 42, H - 94, wd, 2)
        canopy(cv, cx, H - 92, 62, seed=13)
        canopy(cv, cx - 40, H - 88, 26, seed=17)
        canopy(cv, cx + 42, H - 84, 26, seed=19)
        cv.shadow_ellipse(cx, H - 10, 52, 13)
    cv.save(out(name))
    return name


# ------------------------------------------------------------------ 地面底瓦
def gen_ground(fid, name):
    W = H = 32
    fr = FRAMES[fid]
    g = fr["ground"]
    cv = Canvas(W, H, bg=g)
    rnd = random.Random(len(fid) * 31)
    gl, gd = mix(g, "#ffffff", 0.22), mix(g, "#000000", 0.24)
    for _ in range(46):
        x = rnd.randrange(1, W - 1)
        y = rnd.randrange(2, H - 1)
        tuft(cv, x, y, gl, rnd.choice((2, 3)))
    for _ in range(34):
        x = rnd.randrange(1, W - 2)
        y = rnd.randrange(1, H - 2)
        cv.px(x, y, gd)
    cv.save(out(name))
    return name


def main():
    made = []
    made.append(gen_river("a1_1926", "river_a1.png"))
    made.append(gen_river("a2_1951", "river_a2.png"))
    made.append(gen_river("a3_1976", "river_a3.png"))
    made.append(gen_dam())
    made.append(gen_stele())
    r1 = gen_road("a1_1926", "road_curved_tiles.png")
    made.append(r1)
    r3 = gen_road("a3_1976", "road_straight_a3.png")
    if r3:
        made.append(r3)
    made.append(gen_field_patches())
    made.append(gen_field_solid("a2_1951", "field_a2.png", "#78863c"))
    made.append(gen_field_solid("a3_1976", "field_a3.png", "#6b6440"))
    made.append(gen_well("a1_1926", "well_old_a1.png"))
    made.append(gen_well("a2_1951", "well_old_a2.png"))
    made.append(gen_well("a3_1976", "well_old_a3.png"))
    made.append(gen_tree("a1_1926", "tree_a1.png"))
    made.append(gen_tree("a2_1951", "tree_a2.png"))
    made.append(gen_tree("a3_1976", "tree_a3.png"))
    made.append(gen_ground("a1_1926", "ground_a1_tiles.png"))
    made.append(gen_ground("a2_1951", "ground_a2_tiles.png"))
    made.append(gen_ground("a3_1976", "ground_a3_tiles.png"))
    print("scene generated:", len(made))
    for m in made:
        print("  ", m)


if __name__ == "__main__":
    main()
