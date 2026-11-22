# -*- coding: utf-8 -*-
"""B 档：把图集候选物体渲染成带标签的接触表，供目视识别。

每个候选：(图集名, 序号) → 一格，下面写 「序号 / 尺寸WxH / 网格位置」。
输出 lab/_sheet_<图集名>_<页>.png
"""
import json
import os
import sys

from PIL import Image, ImageDraw

ROOT = r"D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift"
SRC = os.path.join(ROOT, "美术资产", "家具")
LAB = os.path.join(ROOT, "lab")

PER_SHEET = 30
COLS = 6
CELL = 150
ZOOM = 3


def build(name, cands, src_im):
    pages = (len(cands) + PER_SHEET - 1) // PER_SHEET or 1
    for pg in range(pages):
        chunk = cands[pg * PER_SHEET:(pg + 1) * PER_SHEET]
        if not chunk:
            continue
        rows = (len(chunk) + COLS - 1) // COLS
        sheet = Image.new("RGB", (COLS * CELL, rows * CELL), (30, 30, 38))
        d = ImageDraw.Draw(sheet)
        for i, c in enumerate(chunk):
            idx = pg * PER_SHEET + i
            crop = src_im.crop((c["x0"], c["y0"], c["x1"], c["y1"]))
            bbox = crop.getbbox()
            if bbox:
                crop = crop.crop(bbox)
            S = max(1, min(ZOOM, int((CELL - 46) / max(crop.size))))
            im2 = crop.resize((crop.width * S, crop.height * S), Image.NEAREST)
            bg = Image.new("RGBA", im2.size, (92, 92, 108, 255))
            bg.alpha_composite(im2)
            gx = (i % COLS) * CELL
            gy = (i // COLS) * CELL
            x = gx + (CELL - bg.width) // 2
            y = gy + 34 + (CELL - 34 - bg.height) // 2
            sheet.paste(bg.convert("RGB"), (x, y))
            d.rectangle([gx + 2, gy + 2, gx + CELL - 3, gy + CELL - 3], outline=(70, 70, 86))
            d.text((gx + 5, gy + 5), "#%d %dx%d @%d,%d" % (idx, c["gw"], c["gh"], c["gx"], c["gy"]),
                   fill=(255, 225, 140))
        out = os.path.join(LAB, "_sheet_%s_%d.png" % (name.replace(".png", "").replace(" ", "_"), pg))
        sheet.save(out)
        print(out, sheet.size, "cands %d..%d" % (pg * PER_SHEET, pg * PER_SHEET + len(chunk) - 1))


def main():
    names = sys.argv[1:]
    cands_all = json.load(open(os.path.join(LAB, "_cls_atlas_cands.json"), encoding="utf-8"))
    for name in names:
        p = os.path.join(SRC, name)
        im = Image.open(p).convert("RGBA")
        lst = [c for c in cands_all.get(name, []) if c["gw"] <= 2 and c["gh"] <= 2]
        if not lst:
            print("skip (no small cands):", name)
            continue
        build(name, lst, im)


if __name__ == "__main__":
    main()
