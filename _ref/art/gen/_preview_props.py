# -*- coding: utf-8 -*-
"""道具预览：把所有 props 按 manifest 顺序铺成一张接触表（grid），输出到 lab/。

用途：目视检查每件家具的形状是否可辨识、有没有画出去 / 画歪。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
OUT = os.path.join(ROOT, "lab")
MANIFEST = os.path.join(ROOT, "_ref", "art", "_assets_a1a3", "_a1a3_assets.json")

CELL = 132          # 单个格子（含标签位）的像素尺寸
PAD = 8


def build(items, out_path, cols=8, scale=1.0):
    cw = CELL
    ch = CELL
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * (cw + PAD) + PAD, rows * (ch + PAD) + PAD),
                      (38, 44, 38, 255))
    for i, (rel, label) in enumerate(items):
        r, c = divmod(i, cols)
        ox = PAD + c * (cw + PAD)
        oy = PAD + r * (ch + PAD)
        cell = Image.new("RGBA", (cw, ch), (58, 64, 54, 255))
        im = Image.open(os.path.join(ROOT, rel.replace("/", os.sep))).convert("RGBA")
        if im.width > cw - 8 or im.height > ch - 20:
            k = min((cw - 8) / im.width, (ch - 20) / im.height)
            im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))),
                           Image.LANCZOS)
        cell.alpha_composite(im, ((cw - im.width) // 2, (ch - 20 - im.height)))
        sheet.alpha_composite(cell, (ox, oy))
    if scale != 1.0:
        sheet = sheet.resize((int(sheet.width * scale), int(sheet.height * scale)),
                             Image.LANCZOS)
    sheet.save(out_path)
    return out_path


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    man = json.load(open(MANIFEST, encoding="utf-8"))
    props = [(p["path"], p["id"]) for p in man["props"]]
    half = len(props) // 2
    print(build(props[:half], os.path.join(OUT, "_props_1.png"), cols=7, scale=0.85))
    print(build(props[half:], os.path.join(OUT, "_props_2.png"), cols=7, scale=0.85))
