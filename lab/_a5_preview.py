# -*- coding: utf-8 -*-
"""把 lab/_a5_draft.json 画成俯视预览图（只读脚本）。
尺寸从 _ref/houses/houses_data.json 读真实 lot，装饰房按各自 lot。"""
import json, io
from PIL import Image, ImageDraw

S = 0.28
W, H = 4800, 3600
TILE = 32
d = json.load(io.open("lab/_a5_draft.json", encoding="utf-8"))
hd = json.load(io.open("_ref/houses/houses_data.json", encoding="utf-8"))
LOTS = {h["id"]: h["lot"] for h in hd}

def lot_size(pid):
    l = LOTS[pid]
    return (l[2] - l[0] + 1) * TILE, (l[3] - l[1] + 1) * TILE

fr = d["frames"][0]
img = Image.new("RGB", (int(W * S), int(H * S)), (110, 122, 76))
dr = ImageDraw.Draw(img, "RGBA")

def px(v):
    return v * S

def col(c, a=255):
    c = c.lstrip("#")
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), a)

for s in fr["shapes"]:
    t = s.get("type")
    if t == "polygon":
        dr.polygon([(px(p[0]), px(p[1])) for p in s["points"]], fill=col(s.get("color", "#888888"), 220))
    elif t == "rect":
        r = s["rect"]
        dr.rectangle([px(r[0]), px(r[1]), px(r[0] + r[2] - 1), px(r[1] + r[3] - 1)],
                     fill=col(s.get("color", "#888888"), 235))
    elif t == "circle":
        c = s["center"]; rr = s["radius"]
        dr.ellipse([px(c[0] - rr), px(c[1] - rr), px(c[0] + rr), px(c[1] + rr)],
                   fill=col(s.get("color", "#888888"), 245))
    elif t == "house":
        p = s["pos"]
        if s.get("decor"):
            lw, lh = lot_size(s["id"])
            dr.rectangle([px(p[0]), px(p[1]), px(p[0] + lw - 1), px(p[1] + lh - 1)],
                         fill=(90, 84, 70, 170), outline=(120, 112, 96, 255))
        else:
            lw, lh = lot_size(s["id"])
            dr.rectangle([px(p[0]), px(p[1]), px(p[0] + lw - 1), px(p[1] + lh - 1)],
                         fill=(150, 130, 105, 240), outline=(60, 52, 44, 255))

def tag(pos, text, colr=(255, 255, 255)):
    dr.text((px(pos[0]), px(pos[1])), text, fill=colr)

for h in fr["hotspots"]:
    dr.ellipse([px(h["pos"][0]) - 4, px(h["pos"][1]) - 4, px(h["pos"][0]) + 4, px(h["pos"][1]) + 4],
               fill=(255, 220, 90, 255))
    tag((h["pos"][0] + 12, h["pos"][1] - 6), h["title"], (255, 240, 200))

a = d["anchors"]
tag((a["tree_center"][0] - 46, a["tree_center"][1] - 34), "TREE/RING", (255, 255, 255))
for r, c in ((a["ring_outer_r"], (255, 255, 255, 150)), (a["ring_inner_r"], (255, 255, 255, 110))):
    dr.ellipse([px(a["tree_center"][0] - r), px(a["tree_center"][1] - r),
                px(a["tree_center"][0] + r), px(a["tree_center"][1] + r)], outline=c, width=2)
sp = d["start_pos"]
dr.ellipse([px(sp[0]) - 6, px(sp[1]) - 6, px(sp[0]) + 6, px(sp[1]) + 6], outline=(120, 200, 255, 255), width=3)
tag((sp[0] + 12, sp[1] - 6), "START", (150, 220, 255))

img.save("lab/_a5_preview.png")
print("saved lab/_a5_preview.png", img.size)
