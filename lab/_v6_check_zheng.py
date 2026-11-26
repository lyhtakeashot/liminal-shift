# -*- coding: utf-8 -*-
"""检查 zheng_a4 从 (108,72) 格 北移到 (108,60) 格 是否与 a4 任何实体/地形冲突。"""
import json, io
TILE = 32.0
d = json.load(io.open("data/frames.json", encoding="utf-8"))
a4 = [f for f in d["frames"] if f["id"] == "a4_2001"][0]

def bbox(s):
    t = s.get("type")
    if t == "rect":
        x, y, w, h = s["rect"]
        return (x / TILE, y / TILE, (x + w) / TILE, (y + h) / TILE)
    if t == "circle":
        cx, cy = s["center"]; r = s.get("radius", 0)
        return ((cx - r) / TILE, (cy - r) / TILE, (cx + r) / TILE, (cy + r) / TILE)
    if t == "polygon":
        pts = s.get("points", [])
        xs = [p[0] / TILE for p in pts]; ys = [p[1] / TILE for p in pts]
        return (min(xs), min(ys), max(xs), max(ys))
    return None

# 郑家 lot 19x12
NEW = (108.0, 60.0, 108 + 19, 60 + 12)
OLD = (108.0, 72.0, 108 + 19, 72 + 12)
print("new lot 格:", NEW, " px:", [v * TILE for v in NEW])
def overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

print("=== 与 NEW lot 相交的 shape（排除 zheng_a4 自己）===")
hit = 0
for s in a4["shapes"]:
    sid = s.get("id") or s.get("title") or s.get("label") or s.get("type")
    if sid == "zheng_a4":
        continue
    bb = bbox(s)
    if bb and overlap(NEW, bb):
        hit += 1
        print("  !! %-10s type=%-8s bbox=%s solid=%s" % (sid, s.get("type"),
              tuple(round(v, 1) for v in bb), s.get("solid", False)))
print("  相交数 =", hit)

print("=== 参考：OLD lot 相交数 ===")
hit0 = sum(1 for s in a4["shapes"]
           if (s.get("id") or s.get("title") or s.get("label") or s.get("type")) != "zheng_a4"
           and (bbox(s) and overlap(OLD, bbox(s))))
print("  ", hit0)

print("=== a4 全部 shape 一览（格）===")
for s in a4["shapes"]:
    sid = s.get("id") or s.get("title") or s.get("label") or ""
    bb = bbox(s)
    print("  %-12s %-8s %-16s solid=%s" % (sid[:12], s.get("type"), 
          tuple(round(v, 1) for v in bb) if bb else "-", s.get("solid", False)))