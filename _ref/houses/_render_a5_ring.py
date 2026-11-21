# -*- coding: utf-8 -*-
"""A5 2026 环岛预览：树被马路环绕。仅渲染环岛 + 十字路口 + 河，验证视觉效果。"""
import os, math
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "art", "_overview")
TILE = 16
W, H = 1600, 900
GW, GH = W // TILE, H // TILE

FONTS = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]
def font(sz):
    for p in FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()

# 与 _design_v5 一致
RING_CENTER = (40, 30)
RING_INNER = 5
RING_OUTER = 8

def ring_cells():
    cx, cy = RING_CENTER
    s = set()
    for y in range(cy - RING_OUTER, cy + RING_OUTER + 1):
        for x in range(cx - RING_OUTER, cx + RING_OUTER + 1):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if RING_INNER < d <= RING_OUTER:
                s.add((x, y))
    return s

def canopy():
    cx, cy = RING_CENTER
    s = set()
    for y in range(cy - RING_INNER, cy + RING_INNER + 1):
        for x in range(cx - RING_INNER, cx + RING_INNER + 1):
            if ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 <= RING_INNER:
                s.add((x, y))
    return s

RING = ring_cells()
CANOPY = canopy()

img = Image.new("RGB", (W, H), (122, 122, 118))
d = ImageDraw.Draw(img, "RGBA")

for x in range(0, W, TILE):
    d.line([(x,0),(x,H)], fill=(255,255,255,10))
for y in range(0, H, TILE):
    d.line([(0,y),(W,y)], fill=(255,255,255,10))

# 河（A5 病绿）
import importlib.util
spec = importlib.util.spec_from_file_location("d5", os.path.join(HERE, "_design_v5.py"))
dv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dv)
for (x, y) in dv.RIVER_CELLS:
    d.rectangle([x*TILE, y*TILE, x*TILE+TILE-1, y*TILE+TILE-1], fill=(74,106,96))

# 十字路口：东西路 y=30，南北路 x=40
cx, cy = RING_CENTER
# 东西路（沥青）
for x in range(0, GW):
    for oy in (-1, 0):
        if abs(x - cx) <= RING_OUTER:
            continue
        yy = cy + oy
        d.rectangle([x*TILE, yy*TILE, x*TILE+TILE-1, yy*TILE+TILE-1], fill=(88,88,88))
# 南北路
for y in range(0, GH):
    for ox in (-1, 0):
        if abs(y - cy) <= RING_OUTER:
            continue
        xx = cx + ox
        d.rectangle([xx*TILE, y*TILE, xx*TILE+TILE-1, y*TILE+TILE-1], fill=(88,88,88))
# 环岛车道
for (x, y) in RING:
    d.rectangle([x*TILE, y*TILE, x*TILE+TILE-1, y*TILE+TILE-1], fill=(88,88,88))
# 树冠（大树）
for (x, y) in CANOPY:
    d.rectangle([x*TILE, y*TILE, x*TILE+TILE-1, y*TILE+TILE-1], fill=(63,107,58))

# 树心
tx, ty = cx*TILE+8, cy*TILE+8
d.ellipse([tx-6, ty-6, tx+6, ty+6], fill=(42,80,38))

# 标注
d.text((tx+90, ty-40), "老槐（2026：冠幅 10 格 = 160px）", font=font(14), fill=(240,250,235))
d.text((tx+90, ty-20), "环岛直径 16 格 = 256px", font=font(13), fill=(230,240,225))

d.rectangle([0, 0, 520, 26], fill=(18,18,16,225))
d.text((10, 4), "A5 · 2026 · 十字路口 + 环岛（树被马路环绕）", font=font(15), fill=(236,228,210))

os.makedirs(OUT, exist_ok=True)
p = os.path.join(OUT, "world_a5_ring.png")
img.save(p)
print("saved", p, img.size)
