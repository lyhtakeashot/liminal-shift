# -*- coding: utf-8 -*-
"""场景资产预览：把 scene/ 下的图拼成一张总览，便于目视检查。"""
import os
import sys

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
SCENE = os.path.join(ROOT, "assets", "village", "scene")
OUT = os.path.join(ROOT, "lab")

BIG = {"river_a1.png": 0.06, "river_a2.png": 0.06, "river_a3.png": 0.06,
       "road_curved_tiles.png": 0.06, "road_straight_a3.png": 0.06,
       "field_patch_tiles.png": 0.25, "field_a2.png": 0.35, "field_a3.png": 0.35}


def main():
    os.makedirs(OUT, exist_ok=True)
    names = ["river_a1.png", "river_a2.png", "river_a3.png",
             "road_curved_tiles.png", "road_straight_a3.png",
             "dam.png", "stele.png",
             "field_patch_tiles.png", "field_a2.png", "field_a3.png",
             "well_old_a1.png", "well_old_a2.png", "well_old_a3.png",
             "tree_a1.png", "tree_a2.png", "tree_a3.png",
             "ground_a1_tiles.png", "ground_a2_tiles.png", "ground_a3_tiles.png"]
    sheet = Image.new("RGBA", (1400, 900), (40, 44, 40, 255))
    x = 20
    y = 20
    row_h = 0
    for n in names:
        p = os.path.join(SCENE, n)
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert("RGBA")
        k = BIG.get(n, 0.6)
        im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
        if x + im.width > 1380:
            x = 20
            y += row_h + 14
            row_h = 0
        sheet.alpha_composite(im, (x, y))
        x += im.width + 14
        row_h = max(row_h, im.height)
    sheet = sheet.crop((0, 0, 1400, min(900, y + row_h + 20)))
    out = os.path.join(OUT, "_scene_all.png")
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    main()
