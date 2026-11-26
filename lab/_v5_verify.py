# -*- coding: utf-8 -*-
"""lead 独立验收 v5（34a9dd8）：范围 + 热点 + a4 郑家距离。不依赖 Godot。"""
import json, subprocess, io, sys

def load(path=None):
    if path is None:
        return json.load(io.open("data/frames.json", encoding="utf-8"))
    r = subprocess.run(["git", "show", path], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print("GIT_FAIL", r.stderr[:200]); sys.exit(1)
    return json.loads(r.stdout)

cur = load()
prev = load("34a9dd8^:data/frames.json")
FC = {f["id"]: f for f in cur["frames"]}
FP = {f["id"]: f for f in prev["frames"]}
ids = [f["id"] for f in cur["frames"]]
print("frames ids:", ids)

print("=== 1. a4/a5 / world 是否未动 ===")
for k in ids:
    if k in ("a4_2001", "a5_2026"):
        print("  %-9s deep_equal=%s" % (k, FC[k] == FP[k]))
print("  world deep_equal=%s" % (cur["world"] == prev["world"]))
print("  start_frame=%r start_pos=%r" % (cur.get("start_frame"), cur.get("start_pos")))

print("=== 2. hotspots 五帧 ===")
for k in ids:
    a = FP[k].get("hotspots", []); b = FC[k].get("hotspots", [])
    print("  %-9s n=%d/%d equal=%s" % (k, len(a), len(b), a == b))

print("=== 3. a1-a3 shapes / 路块 ===")
for k in ("a1_1926", "a2_1951", "a3_1976"):
    sa, sb = FP[k]["shapes"], FC[k]["shapes"]
    ra = [s for s in sa if s.get("label") == "路"]
    rb = [s for s in sb if s.get("label") == "路"]
    print("  %-9s shapes %d->%d  路 %d->%d" % (k, len(sa), len(sb), len(ra), len(rb)))

print("=== 4. a4 房子与路带的距离（格，1格=32px）===")
TILE = 32.0
a4 = FC["a4_2001"]
bands = []
for s in a4["shapes"]:
    if s.get("type") == "rect" and (s.get("label") == "路" or s.get("road")):
        x, y, w, h = [v / TILE for v in s["rect"]]
        bands.append((x, y, w, h))
print("  路 rect 带（格）:", [(round(a,1), round(b,1), round(c,1), round(d,1)) for a,b,c,d in bands])
for s in a4["shapes"]:
    if s.get("type") != "house":
        continue
    sid = s.get("id") or s.get("title")
    px, py = [v / TILE for v in s["pos"]]
    print("  %-10s pos=(%g,%g)格" % (sid, px, py))
    for (bx, by, bw, bh) in bands:
        if bx - 30 <= px <= bx + bw:   # 水平大致交叠
            gap = py - (by + bh)
            if gap >= 0:
                print("      路带 y=%g..%g → 房顶距路底 %g 格" % (by, by + bh, gap))