# -*- coding: utf-8 -*-
"""校验 _classmate/ 下所有交付 PNG 的尺寸是否符合 D6（占地宽×32 × (占地高×32+32)）。"""
import json
import os
import sys

from PIL import Image

ROOT = r"D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift"
MAN = os.path.join(ROOT, "_ref", "art", "_assets_a1a3", "_a1a3_assets.json")
OUT = os.path.join(ROOT, "assets", "village", "_classmate", "props")
TILE = 32

man = json.load(open(MAN, encoding="utf-8"))
spec = {}
for p in man["props"]:
    spec[p["id"]] = (p["w"] * TILE, p["h"] * TILE + TILE)

ok = bad = 0
probs = []
for base, _d, files in os.walk(OUT):
    for f in sorted(files):
        if not f.endswith(".png"):
            continue
        p = os.path.join(base, f)
        rp = os.path.relpath(p, ROOT).replace(os.sep, "/")
        pid = os.path.splitext(f)[0].split("__")[0]
        im = Image.open(p)
        want = spec.get(pid)
        if want is None:
            probs.append(("未知 id", rp, str(im.size), "?"))
            bad += 1
            continue
        if im.size != want:
            probs.append(("尺寸不符", rp, str(im.size), "%dx%d" % want))
            bad += 1
        else:
            ok += 1
        # 内容必须贴底（底边不能有透明行）
        a = im.convert("RGBA").split()[3]
        lastrow = None
        for y in range(im.size[1] - 1, -1, -1):
            if a.crop((0, y, im.size[0], y + 1)).getbbox() is not None:
                lastrow = y
                break
        if lastrow is None:
            probs.append(("全透明", rp, str(im.size), "-"))
        elif lastrow != im.size[1] - 1:
            probs.append(("未贴底", rp, "底行=%d" % lastrow, "画布高=%d" % im.size[1]))
            bad += 1
        else:
            ok += 1

print("=== _classmate 交付校验 ===")
print("通过检查项: %d" % ok)
print("问题: %d" % len(probs))
for a, b, c, d in probs:
    print("  [%s] %s | 实 %s | 期望 %s" % (a, b, c, d))
sys.exit(1 if probs else 0)
