# -*- coding: utf-8 -*-
"""把 base / roof 叠起来做预览图，方便目视检查（输出到 lab/）。"""
import os
import sys

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
OUT = os.path.join(ROOT, "lab")


def compose(base_rel, roof_rel, out_path, bg=(46, 52, 44, 255)):
    bp = os.path.join(ROOT, base_rel.replace("/", os.sep))
    im = Image.open(bp).convert("RGBA")
    bgim = Image.new("RGBA", im.size, bg)
    bgim.alpha_composite(im)
    rp = os.path.join(ROOT, roof_rel.replace("/", os.sep))
    if os.path.exists(rp):
        r = Image.open(rp).convert("RGBA")
        bgim.alpha_composite(r)
    bgim.save(out_path)
    return out_path


def sheet(items, out_path, scale=1):
    """items = [(base_rel, roof_rel_or_None), ...] 横向拼一张。"""
    imgs = []
    for b, r in items:
        bp = os.path.join(ROOT, b.replace("/", os.sep))
        im = Image.open(bp).convert("RGBA")
        bgim = Image.new("RGBA", im.size, (46, 52, 44, 255))
        bgim.alpha_composite(im)
        if r:
            rp = os.path.join(ROOT, r.replace("/", os.sep))
            if os.path.exists(rp):
                bgim.alpha_composite(Image.open(rp).convert("RGBA"))
        imgs.append(bgim)
    if not imgs:
        return None
    W = sum(i.width for i in imgs) + 8 * (len(imgs) - 1)
    H = max(i.height for i in imgs)
    sheet_img = Image.new("RGBA", (W, H), (30, 34, 30, 255))
    x = 0
    for i in imgs:
        sheet_img.alpha_composite(i, (x, 0))
        x += i.width + 8
    if scale != 1:
        sheet_img = sheet_img.resize((int(W * scale), int(H * scale)), Image.LANCZOS)
    sheet_img.save(out_path)
    return out_path


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    groups = [
        ("a1", [("lu", "a1"), ("mill", "a1"), ("shen", "a1"), ("zhou", "a1")]),
        ("a2", [("lu", "a2"), ("mill", "a2"), ("shen", "a2"), ("zhou", "a2")]),
        ("a3", [("lu", "a3"), ("mill", "a3"), ("shen", "a3"), ("zhou", "a3")]),
    ]
    for name, lst in groups:
        items = []
        for fam, fr in lst:
            items.append((
                "assets/village/houses/%s/%s_base.png" % (fam, fr),
                "assets/village/houses/%s/%s_roof.png" % (fam, fr),
            ))
        p = sheet(items, os.path.join(OUT, "_prev_%s.png" % name), scale=0.6)
        print(p)
