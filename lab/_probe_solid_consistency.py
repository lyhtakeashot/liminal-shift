# -*- coding: utf-8 -*-
"""量化：五帧「实体占地」是否一致（房屋 lot 外框 + 山多边形 + solid 小物件）
用户 2026-11-26 口径：只需要保证包围可探索建筑的房屋、山体的占地范围一致，
这样玩家推时间时不会突然「卡到山里」或「虚化穿出地图」。
输出：
  1. 每帧实体覆盖格数/占比
  2. 两两 IoU（grid_area = 房屋 lot + 山）
  3. 玩家体验判据：A1 空地格推到其它帧落进实体的比例；A1 实体格推到其它帧仍是实体的比例
  4. 差异最大的区域 bbox
"""
import io, json, math

TILE = 32
W, H = 4800, 3600
GW, GH = W // TILE, H // TILE

frames = json.load(io.open("data/frames.json", encoding="utf-8"))
houses = json.load(io.open("_ref/houses/houses_data.json", encoding="utf-8"))
LOT = {h["id"]: h["lot"] for h in houses}

def poly_fill(pts, grid):
    ys = [p[1] for p in pts]
    for gy in range(max(0, int(min(ys)) // TILE), min(GH, int(max(ys)) // TILE + 2)):
        yc = (gy + 0.5) * TILE
        xs = []
        n = len(pts)
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            if (y1 <= yc < y2) or (y2 <= yc < y1):
                xs.append(x1 + (yc - y1) / (y2 - y1) * (x2 - x1))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            gx0 = int(round(xs[i] / TILE))
            gx1 = int(round(xs[i + 1] / TILE))
            for gx in range(max(0, gx0), min(GW, gx1 + 1)):
                grid[gy * GW + gx] = True

def build(fr, with_small):
    area = bytearray(GW * GH)
    solid = bytearray(GW * GH)
    for s in fr["shapes"]:
        t = s.get("type")
        if t == "house":
            pos = s.get("pos", [0, 0])
            lot = LOT.get(s.get("id"))
            if not lot:
                continue
            x0 = pos[0] + lot[0] * TILE
            y0 = pos[1] + lot[1] * TILE
            w = (lot[2] - lot[0] + 1) * TILE
            h = (lot[3] - lot[1] + 1) * TILE
            for gy in range(max(0, y0 // TILE), min(GH, (y0 + h) // TILE)):
                for gx in range(max(0, x0 // TILE), min(GW, (x0 + w) // TILE)):
                    area[gy * GW + gx] = 1
                    solid[gy * GW + gx] = 1
        elif t == "polygon":
            lbl = s.get("label", "")
            pts = s.get("points", [])
            if lbl == "山":
                poly_fill(pts, area)
                poly_fill(pts, solid)
            elif s.get("solid", False):
                poly_fill(pts, solid)
        elif t == "rect":
            r = s.get("rect", [0, 0, 0, 0])
            lbl = s.get("label", "")
            if lbl == "":
                continue  # 田块：地面铺装，不是实体
            if s.get("solid", False):
                for gy in range(max(0, r[1] // TILE), min(GH, (r[1] + r[3]) // TILE)):
                    for gx in range(max(0, r[0] // TILE), min(GW, (r[0] + r[2]) // TILE)):
                        solid[gy * GW + gx] = 1
                        if with_small:
                            area[gy * GW + gx] = 1
    return area, solid

info = {}
for fr in frames["frames"]:
    a, s = build(fr, True)
    info[fr["id"]] = (a, s)

print("=== 每帧实体占地（房屋 lot 外框 + 山 + solid 小物件）===")
for fid, (a, s) in info.items():
    ca = sum(a)
    print("  %-10s 格 %5d / %d  占比 %5.1f%%   其中solid小物件 %d 格"
          % (fid, ca, GW * GH, ca * 100.0 / (GW * GH), sum(s) - ca))

ids = [f["id"] for f in frames["frames"]]
print("\n=== 两两 IoU（实体占地）===")
for i in range(len(ids)):
    for j in range(i + 1, len(ids)):
        a, _ = info[ids[i]]
        b, _ = info[ids[j]]
        inter = sum(1 for k in range(GW * GH) if a[k] and b[k])
        uni = sum(1 for k in range(GW * GH) if a[k] or b[k])
        print("  %s vs %s : IoU %.1f%%   各自独有 A=%d B=%d 格"
              % (ids[i], ids[j], inter * 100.0 / uni if uni else 0,
                 sum(1 for k in range(GW*GH) if a[k] and not b[k]),
                 sum(1 for k in range(GW*GH) if b[k] and not a[k])))

print("\n=== 玩家体验判据（以 solid 为准：实体=房屋墙区+山+solid小物件）===")
base = "a1_1926"
a0, s0 = info[base]
for fid in ids:
    if fid == base:
        continue
    _, s1 = info[fid]
    free0 = [k for k in range(GW * GH) if not s0[k]]
    in0 = [k for k in range(GW * GH) if s0[k]]
    free_to_solid = sum(1 for k in free0 if s1[k])
    in_to_free = sum(1 for k in in0 if not s1[k])
    print("  A1 %s → %s : A1 空地 %d 格中 %d 格变成实体(%.1f%%) ; A1 实体 %d 格中 %d 格变空地(%.1f%%)"
          % (base, fid, len(free0), free_to_solid, free_to_solid * 100.0 / len(free0),
             len(in0), in_to_free, in_to_free * 100.0 / len(in0)))

print("\n=== 各帧实体分布 bbox（看是否挤在西北角）===")
for fid in ids:
    a, _ = info[fid]
    xs = [k % GW for k in range(GW * GH) if a[k]]
    ys = [k // GW for k in range(GW * GH) if a[k]]
    if not xs:
        print("  %s 无实体" % fid)
        continue
    print("  %-10s x %3d..%3d 格 (世界 %4d..%4d px)   y %3d..%3d 格 (世界 %4d..%4d px)"
          % (fid, min(xs), max(xs), min(xs)*TILE, max(xs)*TILE,
             min(ys), max(ys), min(ys)*TILE, max(ys)*TILE))
