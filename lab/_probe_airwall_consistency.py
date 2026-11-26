# -*- coding: utf-8 -*-
"""按用户 2026-11-26 的口径量化：五帧「实体空气墙」（房屋 lot 外框 ∪ 山体多边形）是否一致。

用户口径：
  - 不看某栋房子在某坐标，只看「包围可探索建筑的房屋、山体的占地范围」是否一致。
  - 房屋还是山都可以 —— 同一片区域每帧都是实体即可。
  - 目标：玩家推时间时落点不会从空地突然变成实体（卡住/需虚化），也不会穿出地图。
输出：每帧实体格数与占比、两两 IoU、相邻时代「空地变实体 / 实体变空地」的双向差、差异最大区域 bbox。
"""
import io, json

TILE = 32
W, H = 4800, 3600
GW, GH = W // TILE, H // TILE

frames = json.load(io.open("data/frames.json", encoding="utf-8"))
houses = json.load(io.open("_ref/houses/houses_data.json", encoding="utf-8"))
LOT = {h["id"]: h["lot"] for h in houses}


def poly_fill(pts, grid):
    ys = [p[1] for p in pts]
    n = len(pts)
    for gy in range(max(0, int(min(ys)) // TILE), min(GH, int(max(ys)) // TILE + 2)):
        yc = (gy + 0.5) * TILE
        xs = []
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            if (y1 <= yc < y2) or (y2 <= yc < y1):
                xs.append(x1 + (yc - y1) / (y2 - y1) * (x2 - x1))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for gx in range(max(0, int(round(xs[i] / TILE))), min(GW, int(round(xs[i + 1] / TILE)) + 1)):
                grid[gy * GW + gx] = 1


def airwall(fr):
    """S = 房屋 lot 外框 ∪ 山体多边形（用户口径的「实体空气墙」）"""
    g = bytearray(GW * GH)
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
                    g[gy * GW + gx] = 1
        elif t == "polygon" and s.get("label", "") == "山":
            poly_fill(s.get("points", []), g)
    return g


ids = [f["id"] for f in frames["frames"]]
S = {fid: airwall(f) for fid, f in zip(ids, frames["frames"])}

print("=== 每帧「实体空气墙」（房屋 lot 外框 ∪ 山体）===")
for fid in ids:
    c = sum(S[fid])
    print("  %-10s %5d 格 / %d  占比 %5.2f%%" % (fid, c, GW * GH, c * 100.0 / (GW * GH)))

print("\n=== 两两 IoU ===")
for i in range(len(ids)):
    for j in range(i + 1, len(ids)):
        a, b = S[ids[i]], S[ids[j]]
        inter = sum(1 for k in range(GW * GH) if a[k] and b[k])
        uni = sum(1 for k in range(GW * GH) if a[k] or b[k])
        onlyA = sum(1 for k in range(GW * GH) if a[k] and not b[k])
        onlyB = sum(1 for k in range(GW * GH) if b[k] and not a[k])
        print("  %s vs %s : IoU %5.1f%%   只A有 %4d 格  只B有 %4d 格"
              % (ids[i], ids[j], inter * 100.0 / uni if uni else 0, onlyA, onlyB))

print("\n=== 相邻时代 双向差（玩家体验）===")
for i in range(len(ids) - 1):
    a, b = S[ids[i]], S[ids[i + 1]]
    free = [k for k in range(GW * GH) if not a[k]]
    blk = [k for k in range(GW * GH) if a[k]]
    f2b = sum(1 for k in free if b[k])
    b2f = sum(1 for k in blk if not b[k])
    print("  %s → %s : 空地变实体 %4d 格 (%.1f%% of 空地)   实体变空地 %4d 格 (%.1f%% of 实体)"
          % (ids[i], ids[i + 1], f2b, f2b * 100.0 / len(free), b2f, b2f * 100.0 / len(blk)))

print("\n=== 每帧实体 bbox ===")
for fid in ids:
    xs = [k % GW for k in range(GW * GH) if S[fid][k]]
    ys = [k // GW for k in range(GW * GH) if S[fid][k]]
    print("  %-10s x %3d..%3d 格 (px %4d..%4d)   y %3d..%3d 格 (px %4d..%4d)"
          % (fid, min(xs), max(xs), min(xs) * TILE, max(xs) * TILE,
             min(ys), max(ys), min(ys) * TILE, max(ys) * TILE))

print("\n=== 与 A1 差异最大的格区（按 32 格粗分块）===")
base = S["a1_1926"]
from collections import Counter
c = Counter()
for k in range(GW * GH):
    if base[k] != S["a5_2026"][k]:
        c[(k % GW // 16, k // GW // 16)] += 1
for (bx, by), n in c.most_common(12):
    print("  区块 x %3d..%3d y %3d..%3d 格  差异 %4d 格" % (bx * 16, bx * 16 + 15, by * 16, by * 16 + 15, n))
