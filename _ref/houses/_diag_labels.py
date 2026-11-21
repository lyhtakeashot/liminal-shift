# -*- coding: utf-8 -*-
"""诊断 shen_a3 房间名最终落点（复刻 gen_all_houses.py 新逻辑）：是否拿到标签、是否压家具。"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_all_houses as g
from PIL import Image, ImageDraw

data = json.load(open(g.DATA_PATH, encoding="utf-8"))
hs = [h for h in data if h["id"] == "shen_a3"][0]
ox, oy, S = 70, 210, g.SCALE
d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
f = g.font(14)
grid = g.build_grid(hs)
X0, Y0, X1, Y1 = hs["lot"]

print("房间名最终落点（复刻新逻辑）：")
for room in hs["rooms"]:
    x0, y0, x1, y1, name, ck = room[:6]
    force_top = len(room) > 6 and room[6] == "top"
    tw = d.textlength(name, font=f)
    if force_top:
        print(f"  {name:<8} TOP 固定位置（带底衬）")
        continue
    best = None
    for ry in range(y1, y0 - 1, -1):
        for rx in range(x0, x1 + 1):
            if not (X0 <= rx <= X1 and Y0 <= ry <= Y1):
                continue
            if grid[ry - Y0][rx - X0] not in (".", " ") or g.occupied(hs, rx, ry):
                continue
            if tw > (x1 - x0 + 1) * S - 8:
                continue
            dist = (rx - (x0 + x1) / 2) ** 2 + (ry - (y0 + y1) / 2) ** 2
            if best is None or dist < best[0]:
                best = (dist, rx, ry)
    if best:
        _, rx, ry = best
        # 标签框近似：宽 tw+8、高 18，中心在格心
        cx, cy = ox + (rx + .5) * S, oy + (ry + .5) * S
        hits = []
        for furn in hs["furniture"]:
            fx, fy, fw, fh = furn["rect"]
            fb = (ox + fx * S + 3, oy + fy * S + 3, ox + (fx + fw) * S - 4, oy + (fy + fh) * S - 4)
            if cx - tw/2 - 4 < fb[2] and fb[0] < cx + tw/2 + 4 and cy - 9 < fb[3] and fb[1] < cy + 9:
                hits.append(f"{furn['name']}@{fx},{fy}")
        print(f"  {name:<8} 落格({rx},{ry}) 压家具={','.join(hits) or '无'}  底衬遮挡可读")
    else:
        print(f"  {name:<8} 房间内无空位/太窄 → 退到 TOP（带底衬）")
