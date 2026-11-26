# -*- coding: utf-8 -*-
"""按 gen_asset_breakdown.py:355-387 的同一逻辑，复算各帧「路」条目的 id/px/note。"""
import json
import math
import sys

sys.stdout.reconfigure(encoding="utf-8")

TILE = 32
data = json.load(open("data/frames.json", encoding="utf-8"))
frames = data["frames"] if isinstance(data, dict) else data

for f in frames:
    roads = [s["rect"] for s in f["shapes"] if s.get("road")]
    if not roads:
        continue
    rx0 = min(r[0] for r in roads)
    ry0 = min(r[1] for r in roads)
    rx1 = max(r[0] + r[2] for r in roads)
    ry1 = max(r[1] + r[3] for r in roads)
    curved = len(set(r[1] for r in roads)) > 1
    rid = "road_curved" if curved else "road_straight"
    cells = set()
    for rx, ry, rw, rh in roads:
        for cx in range(rx // TILE, (rx + rw) // TILE):
            for cy in range(ry // TILE, (ry + rh) // TILE):
                cells.add((cx, cy))
    colcnt = {}
    for cx, cy in cells:
        colcnt[cx] = colcnt.get(cx, 0) + 1
    road_g = max(set(colcnt.values()), key=lambda v: (list(colcnt.values()).count(v), v)) if colcnt else 2
    note = ("%s；路宽 %d 格 = %dpx（逐列实测众数），共 %d 个路面格；出 32px 瓦片集（直/弯/丁字/十字）"
            % ("弯道（A1/A2 同走向，两侧会收边到 1~2 格）" if curved else "直道（A3 起取直）",
               road_g, road_g * TILE, len(cells)))
    print("%-24s id=%-14s px=[%d,%d] w=%d h=%d" % (
        f.get("id"), rid, rx1 - rx0, ry1 - ry0,
        math.ceil((rx1 - rx0) / TILE), math.ceil((ry1 - ry0) / TILE)))
    print("    name=主路（宽 %d 格）" % road_g)
    print("    path=assets/village/scene/%s_tiles.png" % rid)
    print("    note=%s" % note)
