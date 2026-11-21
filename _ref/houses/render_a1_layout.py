# -*- coding: utf-8 -*-
"""A1 1926 世界布局预览图。与 _layout_check.py 的坐标必须一致。"""
import json, os
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 900
TILE = 16
OUT = os.path.join(os.path.dirname(__file__), "..", "art", "_overview")

def font(sz):
    for p in (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()

F12, F14, F16, F22 = font(12), font(14), font(16), font(22)

img = Image.new("RGB", (W, H), (78, 96, 58))
d = ImageDraw.Draw(img, "RGBA")

# 栅格
for x in range(0, W, 80):
    d.line([(x, 0), (x, H)], fill=(255, 255, 255, 10))
for y in range(0, H, 80):
    d.line([(0, y), (W, y)], fill=(255, 255, 255, 10))

# 河
d.rectangle([0, 0, W, 112], fill=(58, 96, 120))
d.rectangle([0, 100, W, 112], fill=(70, 112, 136))
d.text((16, 84), "河（上游 ← 坝 → 下游）", font=F14, fill=(220, 236, 245))
# 坝
d.rectangle([196, 34, 196 + 120, 34 + 62], fill=(104, 84, 62), outline=(150, 124, 92), width=2)
d.text((204, 44), "坝", font=F16, fill=(240, 228, 208))

# 路
ROAD_W = 36
ROADS = [
    [(0, 560), (840, 560), (900, 624), (960, 560), (1600, 560)],
    [(464, 240), (560, 240), (560, 560)],
]
for road in ROADS:
    pts = [(x, y) for x, y in road]
    d.line(pts, fill=(122, 106, 84), width=ROAD_W, joint="curve")

# 田
for name, x, y in (("田·东", 1000, 130), ("田·西", 1272, 130)):
    d.rectangle([x, y, x + 240, y + 176], fill=(124, 138, 60), outline=(96, 110, 44), width=2)
    for i in range(6):
        yy = y + 20 + i * 28
        d.line([(x + 12, yy), (x + 228, yy)], fill=(104, 118, 48), width=2)
    d.text((x + 8, y + 6), name, font=F14, fill=(30, 38, 16))

# 房子
data = json.load(open(os.path.join(os.path.dirname(__file__), "houses_data.json"), encoding="utf-8"))
by_id = {h["id"]: h for h in data}
PLACE = {
    "mill_a1":    (160, 112),
    "shen_a1":    (160, 340),
    "zhou_house": (600, 400),
    "lu_house":   (1120, 340),
}
TINT = {
    "mill_a1":    ((120, 92, 64), "磨坊 · 沈家产业"),
    "shen_a1":    ((132, 96, 76), "沈家宅 · 磨坊主"),
    "zhou_house": ((104, 90, 70), "长工房 · 周家"),
    "lu_house":   ((110, 104, 78), "陆家 · 佃农"),
}
for hid, (px, py) in PLACE.items():
    lot = by_id[hid]["lot"]
    gw, gh = lot[2] - lot[0] + 1, lot[3] - lot[1] + 1
    w, h = gw * TILE, gh * TILE
    col, label = TINT[hid]
    d.rectangle([px, py, px + w, py + h], fill=col, outline=(226, 208, 176), width=3)
    # 占地格线
    for gx in range(0, gw + 1):
        d.line([(px + gx * TILE, py), (px + gx * TILE, py + h)], fill=(255, 255, 255, 22))
    for gy in range(0, gh + 1):
        d.line([(px, py + gy * TILE), (px + w, py + gy * TILE)], fill=(255, 255, 255, 22))
    d.text((px + 8, py + 8), label, font=F16, fill=(255, 246, 232))
    d.text((px + 8, py + 30), f"{hid}  {gw}×{gh}格 = {w}×{h}px", font=F12, fill=(226, 212, 190))

# 老井 / 老槐
d.ellipse([884 - 16, 529 - 16, 884 + 16, 529 + 16], fill=(26, 30, 30), outline=(150, 150, 140), width=2)
d.text((884 + 22, 529 - 8), "老井", font=F14, fill=(240, 236, 224))
d.ellipse([843 - 12, 496 - 12, 843 + 12, 496 + 12], fill=(52, 106, 58), outline=(120, 160, 110), width=2)
d.text((843 + 18, 496 - 8), "老槐", font=F14, fill=(228, 244, 226))

# 起点
sx, sy = 700, 560
d.ellipse([sx - 9, sy - 9, sx + 9, sy + 9], fill=(226, 210, 130), outline=(120, 96, 40), width=2)
d.text((sx - 22, sy + 14), "起点", font=F12, fill=(250, 240, 200))

# 标题条
d.rectangle([0, 0, W, 30], fill=(18, 18, 16, 210))
d.text((14, 6), "A1 · 1926 · 世界布局（1600×900 = 100×56.25 格）  占位块版，非美术成稿",
       font=F16, fill=(236, 228, 210))

# 图例
lx, ly = 16, H - 120
d.rectangle([lx, ly, lx + 430, ly + 104], fill=(18, 18, 16, 190), outline=(120, 116, 100))
d.text((lx + 10, ly + 8), "图例", font=F14, fill=(236, 228, 210))
d.rectangle([lx + 10, ly + 30, lx + 30, ly + 44], fill=(132, 96, 76), outline=(226, 208, 176), width=1)
d.text((lx + 38, ly + 28), "房屋占地（白框=lot，格线=16px）", font=F12, fill=(220, 212, 196))
d.rectangle([lx + 10, ly + 52, lx + 30, ly + 66], fill=(124, 138, 60))
d.text((lx + 38, ly + 50), "农田（可穿行）", font=F12, fill=(220, 212, 196))
d.line([(lx + 10, ly + 84), (lx + 30, ly + 84)], fill=(122, 106, 84), width=8)
d.text((lx + 38, ly + 76), "路（宽 36px ≈ 2.25 格，可穿行）", font=F12, fill=(220, 212, 196))

os.makedirs(OUT, exist_ok=True)
p = os.path.abspath(os.path.join(OUT, "a1_world_layout.png"))
img.save(p)
print("saved", p, img.size)
