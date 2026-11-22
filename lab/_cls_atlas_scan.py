# -*- coding: utf-8 -*-
"""B 档：图集切图 —— 候选物体检测。

同学图集里一件家具往往占 2×2 / 3×2 等多格，不能按 32px 硬切。
做法：对 alpha 做 8 连通域分析 → 求每块内容的包围盒 → 吸附到 32px 网格
→ 得到「候选物体 (x, y, w, h)」列表（单位：格）。

输出：
  lab/_cls_atlas_cands.json   所有图集的候选物体
  lab/_atlas_<name>_cand.png 带编号的候选对照图
"""
import json
import os
import sys

from PIL import Image, ImageDraw

ROOT = r"D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift"
SRC = os.path.join(ROOT, "美术资产", "家具")
LAB = os.path.join(ROOT, "lab")
TILE = 32


def components(alpha):
    """8 连通域。alpha 为 PIL 'L' 模式。返回 [(x0,y0,x1,y1), ...]（像素坐标，右开）。"""
    w, h = alpha.size
    px = alpha.load()
    seen = bytearray(w * h)
    out = []
    for y in range(h):
        for x in range(w):
            i = y * w + x
            if seen[i] or px[x, y] == 0:
                continue
            stack = [(x, y)]
            seen[i] = 1
            x0 = x1 = x
            y0 = y1 = y
            while stack:
                cx, cy = stack.pop()
                if cx < x0: x0 = cx
                if cx > x1: x1 = cx
                if cy < y0: y0 = cy
                if cy > y1: y1 = cy
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < w and 0 <= ny < h:
                            j = ny * w + nx
                            if not seen[j] and px[nx, ny] > 0:
                                seen[j] = 1
                                stack.append((nx, ny))
            out.append((x0, y0, x1 + 1, y1 + 1))
    return out


def snap(box, w, h):
    """包围盒吸附到 32 网格：向外取整。"""
    x0, y0, x1, y1 = box
    gx0 = (x0 // TILE) * TILE
    gy0 = (y0 // TILE) * TILE
    gx1 = -(-x1 // TILE) * TILE
    gy1 = -(-y1 // TILE) * TILE
    gx1 = min(gx1, (w // TILE) * TILE)
    gy1 = min(gy1, (h // TILE) * TILE)
    return gx0, gy0, gx1, gy1


def scan(name, save_png=True, zoom=3):
    p = os.path.join(SRC, name)
    im = Image.open(p).convert("RGBA")
    w, h = im.size
    a = im.split()[3]
    comps = components(a)
    # 合并重叠/相邻的吸附框（同一件家具常由几块拼成）
    boxes = [snap(c, w, h) for c in comps]
    boxes = [b for b in boxes if b[2] > b[0] and b[3] > b[1]]
    boxes.sort(key=lambda b: (b[1], b[0]))

    # 贪心合并：两个框若像素区间相交，合并后再吸附
    merged = True
    while merged:
        merged = False
        out = []
        for b in boxes:
            hit = None
            for i, o in enumerate(out):
                if not (b[2] <= o[0] or o[2] <= b[0] or b[3] <= o[1] or o[3] <= b[1]):
                    hit = i
                    break
            if hit is None:
                out.append(b)
            else:
                o = out[hit]
                out[hit] = (min(o[0], b[0]), min(o[1], b[1]), max(o[2], b[2]), max(o[3], b[3]))
                merged = True
        boxes = out
    boxes.sort(key=lambda b: (b[1], b[0]))

    cands = []
    for (gx0, gy0, gx1, gy1) in boxes:
        gw = (gx1 - gx0) // TILE
        gh = (gy1 - gy0) // TILE
        if gw > 3 or gh > 3 or gw < 1 or gh < 1:
            continue
        cands.append({"gx": gx0 // TILE, "gy": gy0 // TILE, "gw": gw, "gh": gh,
                      "x0": gx0, "y0": gy0, "x1": gx1, "y1": gy1})

    if save_png:
        bg = Image.new("RGBA", (w, h), (72, 72, 86, 255))
        bg.alpha_composite(im)
        base = bg.convert("RGB")
        d = ImageDraw.Draw(base)
        for i, c in enumerate(cands):
            col = (255, 90, 90) if (c["gw"], c["gh"]) != (1, 1) else (110, 220, 255)
            d.rectangle([c["x0"], c["y0"], c["x1"] - 1, c["y1"] - 1], outline=col, width=1)
        base = base.resize((w * zoom, h * zoom), Image.LANCZOS)
        d2 = ImageDraw.Draw(base)
        for i, c in enumerate(cands):
            d2.text((c["x0"] * zoom + 2, c["y0"] * zoom + 2), str(i), fill=(255, 240, 120))
        base.save(os.path.join(LAB, "_atlas_%s_cand.png" % name.replace(".png", "")))
    return cands


def main():
    names = sorted(n for n in os.listdir(SRC) if n.lower().endswith(".png"))
    all_c = {}
    for n in names:
        p = os.path.join(SRC, n)
        if Image.open(p).size[0] <= 128 and Image.open(p).size[1] <= 128:
            continue
        c = scan(n)
        all_c[n] = c
        sizes = {}
        for x in c:
            sizes["%dx%d" % (x["gw"], x["gh"])] = sizes.get("%dx%d" % (x["gw"], x["gh"]), 0) + 1
        print("%-42s 候选 %4d  %s" % (n, len(c), sorted(sizes.items(), key=lambda kv: -kv[1])[:8]))
    with open(os.path.join(LAB, "_cls_atlas_cands.json"), "w", encoding="utf-8") as f:
        json.dump(all_c, f, ensure_ascii=False, indent=1)
    print("\n总计候选:", sum(len(v) for v in all_c.values()))


if __name__ == "__main__":
    main()
