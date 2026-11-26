# -*- coding: utf-8 -*-
"""两件事的实测：
A. a4/a5 里到底哪些形状会画成「纯色几何块」（没有瓦片贴图）；
B. zheng_a4 再往环岛中心挪（x 108 -> 78）会不会撞上东西。
"""
import json, io, sys

sys.stdout = io.open("lab/_v7_out.txt", "w", encoding="utf-8")

TILE = 32.0
d = json.load(io.open("data/frames.json", encoding="utf-8"))
F = {f["id"]: f for f in d["frames"]}

# 与 scripts/asset_draw.gd:93 POLYGON_TILE_KIND 一致
POLYGON_TILE_KIND = {"河": "river", "路": "road"}

def classify(s):
    """返回 (是否会画成纯色块, 原因)"""
    t = s.get("type"); label = s.get("label", "")
    if t == "house":
        return False, "house→贴图(FAMILY)或色块降级"
    if t == "circle":
        return False, "circle→前景物件(_draw_prop)"
    if t == "path":
        return False, "path→线"
    if t == "rect":
        if s.get("road"):
            return False, "rect.road→路面瓦片"
        if label == "坝":
            return False, "rect.坝→dam 整图"
        if label != "":
            return False, "rect[%s]→前景小件" % label
        return False, "rect 无label→田瓦片(field)"
    if t == "polygon":
        if label in POLYGON_TILE_KIND:
            return False, "polygon[%s]→%s 瓦片" % (label, POLYGON_TILE_KIND[label])
        return True, "polygon[%s] 不在 POLYGON_TILE_KIND ⇒ 纯色 draw_colored_polygon" % (label or "无label")
    return False, "unknown:%s" % t

print("=== A. 每帧「纯色几何块」清单 ===")
for fid in ["a1_1926", "a2_1951", "a3_1976", "a4_2001", "a5_2026"]:
    flats = []
    for s in F[fid]["shapes"]:
        flat, why = classify(s)
        if flat:
            pts = s.get("points", [])
            flats.append((why, len(pts)))
    print("  %-9s 纯色块 %d 个 %s" % (fid, len(flats), flats if flats else ""))

print("=== A2. 各帧 label 分布 ===")
for fid in ["a4_2001", "a5_2026"]:
    from collections import Counter
    c = Counter((s.get("type"), s.get("label", "")) for s in F[fid]["shapes"])
    print("  %s" % fid)
    for k, v in c.items():
        print("      %-10s %-6s x%d" % (k[0], k[1] or "(空)", v))

print("=== B. zheng_a4 候选位置 ===")
a4 = F["a4_2001"]
def bbox(s):
    t = s.get("type")
    if t == "rect":
        x, y, w, h = s["rect"]; return (x/TILE, y/TILE, (x+w)/TILE, (y+h)/TILE)
    if t == "circle":
        cx, cy = s["center"]; r = s.get("radius", 0)
        return ((cx-r)/TILE, (cy-r)/TILE, (cx+r)/TILE, (cy+r)/TILE)
    if t == "polygon":
        pts = s.get("points", [])
        xs = [p[0]/TILE for p in pts]; ys = [p[1]/TILE for p in pts]
        return (min(xs), min(ys), max(xs), max(ys))
    return None
def overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

LW, LH = 19, 12
for cand in [(108, 58), (96, 58), (88, 58), (80, 58), (78, 58), (76, 58)]:
    lot = (cand[0], cand[1], cand[0]+LW, cand[1]+LH)
    hits = []
    for s in a4["shapes"]:
        sid = s.get("id") or s.get("title") or s.get("label") or s.get("type")
        if sid == "zheng_a4":
            continue
        bb = bbox(s)
        if bb and overlap(lot, bb):
            hits.append(sid)
    cx, cy = cand[0]+LW/2.0, cand[1]+LH/2.0
    dist = ((cx-64)**2 + (cy-52)**2) ** 0.5
    print("  pos=(%d,%d) lot x%d..%d y%d..%d  距环岛心 %5.1f 格  相交=%s"
          % (cand[0], cand[1], lot[0], lot[2], lot[1], lot[3], dist, hits if hits else "0"))