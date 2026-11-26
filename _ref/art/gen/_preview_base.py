# -*- coding: utf-8 -*-
"""base 单图预览（不叠屋顶）—— 玩家进屋时看到的就是这一张。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
OUT = os.path.join(ROOT, "lab")


def sheet(items, out_path, scale=1, bg=(46, 52, 44, 255)):
    imgs = []
    for rel in items:
        im = Image.open(os.path.join(ROOT, rel.replace("/", os.sep))).convert("RGBA")
        bgim = Image.new("RGBA", im.size, bg)
        bgim.alpha_composite(im)
        imgs.append(bgim)
    W = sum(i.width for i in imgs) + 8 * (len(imgs) - 1)
    H = max(i.height for i in imgs)
    s = Image.new("RGBA", (W, H), (30, 34, 30, 255))
    x = 0
    for i in imgs:
        s.alpha_composite(i, (x, 0))
        x += i.width + 8
    if scale != 1:
        s = s.resize((int(W * scale), int(H * scale)), Image.LANCZOS)
    s.save(out_path)
    return out_path


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    which = sys.argv[1] if len(sys.argv) > 1 else "a1"
    fams = {"a1": ["lu", "mill", "shen", "zhou"],
            "a2": ["lu", "mill", "shen", "zhou"],
            "a3": ["lu", "mill", "shen", "zhou"]}[which]
    items = ["assets/village/houses/%s/%s_base.png" % (f, which) for f in fams]
    p = sheet(items, os.path.join(OUT, "_base_%s.png" % which), scale=0.6)
    print(p)
