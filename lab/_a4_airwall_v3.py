# -*- coding: utf-8 -*-
"""A4 重排 v3：按用户口径（实体空气墙一致）评估 A4 候选，并给出「相位触发率」。

用户 2026-11-26 口径：
  S = 房屋 lot 外框 ∪ 山体多边形（房屋还是山都算）
  要求各帧 S 大致一致 ⇒ 玩家推时间不会凭空被实体挡住（触发虚化），也不会虚化穿出地图。

本脚本只用 numpy 加速（沙箱有 numpy）。用 cell 网格 32px（与 TILE 一致）。
指标：
  cover5in4 = |S5∩S4| / |S5|     A5 的实体在 A4 也被实体覆盖
  cover4in5 = |S4∩S5| / |S4|     A4 的实体在 A5 也被实体覆盖
  trigger_5 = A5 的自由格中在 A4 变实体的比例（推 A4→A5 会触发虚化的面积比）
  trigger_4 = A4 的自由格中在 A5 变实体的比例
"""
import io, json, math
import numpy as np

TILE = 32
W, H = 4800, 3600
GW, GH = W // TILE, H // TILE

frames = json.load(io.open("data/frames.json", encoding="utf-8"))
houses = json.load(io.open("_ref/houses/houses_data.json", encoding="utf-8"))
LOT = {h["id"]: h["lot"] for h in houses}
FR = {f["id"]: f for f in frames["frames"]}


def house_rect(pos, lot):
    return (pos[0] + lot[0] * TILE, pos[1] + lot[1] * TILE,
            pos[0] + (lot[2] - lot[0] + 1) * TILE, pos[1] + (lot[3] - lot[1] + 1) * TILE)


def rect_mask(r):
    m = np.zeros((GH, GW), dtype=bool)
    x0 = max(0, r[0] // TILE); x1 = min(GW, (r[2] + TILE - 1) // TILE)
    y0 = max(0, r[1] // TILE); y1 = min(GH, (r[3] + TILE - 1) // TILE)
    if x1 > x0 and y1 > y0:
        m[y0:y1, x0:x1] = True
    return m


def poly_mask(pts):
    m = np.zeros((GH, GW), dtype=bool)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    n = len(pts)
    for gy in range(max(0, int(min(ys)) // TILE), min(GH, int(max(ys)) // TILE + 2)):
        yc = (gy + 0.5) * TILE
        cross = []
        for i in range(n):
            x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % n]
            if (y1 <= yc < y2) or (y2 <= yc < y1):
                cross.append(x1 + (yc - y1) / (y2 - y1) * (x2 - x1))
        cross.sort()
        for i in range(0, len(cross) - 1, 2):
            gx0 = max(0, int(round(cross[i] / TILE)))
            gx1 = min(GW, int(round(cross[i + 1] / TILE)) + 1)
            if gx1 > gx0:
                m[gy, gx0:gx1] = True
    return m


def frame_masks(fr):
    """返回 (S 实体掩码, 房子列表, 山列表)"""
    m = np.zeros((GH, GW), dtype=bool)
    hs = []; hills = []
    for s in fr["shapes"]:
        if s.get("type") == "house" and s.get("id") in LOT:
            r = house_rect(s.get("pos", [0, 0]), LOT[s["id"]])
            hs.append((s["id"], r))
            m |= rect_mask(r)
        elif s.get("type") == "polygon" and s.get("label", "") == "山":
            hills.append(s.get("points", []))
            m |= poly_mask(s.get("points", []))
    return m, hs, hills


S5, A5_HOUSES, A5_HILLS = frame_masks(FR["a5_2026"])
print("A5 实体 %d 格 (%.2f%%)  房子 %s" % (S5.sum(), S5.sum() * 100.0 / (GW * GH),
                                            [h[0] for h in A5_HOUSES]))
for pid, r in A5_HOUSES:
    print("   %-9s rect=%s" % (pid, r))
for pts in A5_HILLS:
    print("   山 bbox=(%d,%d)-(%d,%d)" % (min(p[0] for p in pts), min(p[1] for p in pts),
                                        max(p[0] for p in pts), max(p[1] for p in pts)))


def combine(houses_rc, hills_pts):
    m = np.zeros((GH, GW), dtype=bool)
    for r in houses_rc:
        m |= rect_mask(r)
    for pts in hills_pts:
        m |= poly_mask(pts)
    return m


def score(S4):
    inter = int((S4 & S5).sum()); n4 = int(S4.sum()); n5 = int(S5.sum())
    free5 = int((~S5).sum()); free4 = int((~S4).sum())
    trig5 = int((~S5 & S4).sum())   # A5 自由 → A4 实体（推 A4→A5 的虚化触发区）
    trig4 = int((~S4 & S5).sum())
    return dict(inter=inter, n4=n4, n5=n5,
                cover5in4=inter / float(n5), cover4in5=inter / float(n4),
                trig5=trig5, trig5p=trig5 * 100.0 / max(1, free5),
                trig4=trig4, trig4p=trig4 * 100.0 / max(1, free4),
                sym=int((S4 ^ S5).sum()))


def report(tag, houses_rc, extra_hills=()):
    S4 = combine(houses_rc, list(A5_HILLS) + list(extra_hills))
    s = score(S4)
    print("%-28s cover5in4=%5.1f%% cover4in5=%5.1f%%  trig(A4->A5)=%6.2f%%  trig(A5->A4)=%6.2f%%  sym=%d格"
          % (tag, s["cover5in4"] * 100, s["cover4in5"] * 100, s["trig5p"], s["trig4p"], s["sym"]))
    return s, S4


# ---- 候选配置 ----
SHEN = house_rect((64, 416), LOT["shen_a4"])       # 与 A5 shen_a5 同位
MARKET = house_rect((2144, 320), LOT["market"])    # 与 A5 market 同位
LOT_Z, LOT_G = LOT["zhou_a4"], LOT["zheng_a4"]
WZ = (LOT_Z[2] - LOT_Z[0] + 1) * TILE, (LOT_Z[3] - LOT_Z[1] + 1) * TILE
WG = (LOT_G[2] - LOT_G[0] + 1) * TILE, (LOT_G[3] - LOT_G[1] + 1) * TILE
print("zhou_a4 尺寸", WZ, " zheng_a4 尺寸", WG)

# A5 南部两栋（学校/玩具店）所在格区
SCHOOL = house_rect((576, 1920), LOT["school"])
TOY = house_rect((2176, 1984), LOT["toyshop"])
print("A5 school rect", SCHOOL, " A5 toyshop rect", TOY)

CANDS = {
    "旧案 v2 (2272,1984)/(2304,2400)": [(2272, 1984), (2304, 2400)],
    "对齐学校区 (640,1984)/(1600,1984)": [(640, 1984), (1600, 1984)],
    "对齐学校区 (576,1920)/(1408,1920)": [(576, 1920), (1408, 1920)],
    "一栋进学校区一栋贴玩具店 (640,1984)/(2304,1984)": [(640, 1984), (2304, 1984)],
    "一栋进学校区一栋贴玩具店 (1216,1920)/(2304,1984)": [(1216, 1920), (2304, 1984)],
}

print("\n== 只用 A5 同款三座山，不加补山 ==")
best = None
for tag, (pz, pg) in CANDS.items():
    rects = [SHEN, MARKET, house_rect(pz, LOT_Z), house_rect(pg, LOT_G)]
    s, S4 = report(tag, rects)
    if best is None or s["sym"] < best[0]:
        best = (s["sym"], tag, pz, pg, s, S4)

print("\n== 加补山：把 A5 有实体、A4 没有的缺口用山补上 ==")
sym, tag, pz, pg, s0, S4 = best
gap = S5 & ~S4
ys, xs = np.nonzero(gap)
print("最优候选 %s 的缺口 %d 格" % (tag, gap.sum()))
if gap.sum():
    print("  缺口 bbox: x %d..%d 格 (px %d..%d)  y %d..%d 格 (px %d..%d)"
          % (xs.min(), xs.max(), xs.min() * TILE, xs.max() * TILE,
             ys.min(), ys.max(), ys.min() * TILE, ys.max() * TILE))
    # 把缺口按列切成几个大块，每块用一座三角山覆盖（沿用 A5 山的三点形状，缩放到块 bbox）
    cols = np.array(sorted(set(xs.tolist())))
    blocks = []
    start = prev = cols[0]
    for c in cols[1:]:
        if c - prev > 4:
            blocks.append((start, prev)); start = c
        prev = c
    blocks.append((start, prev))
    print("  缺口列块:", blocks)
    extra = []
    for (c0, c1) in blocks:
        sel = gap[:, c0:c1 + 1]
        rys, rxs = np.nonzero(sel)
        x0 = c0 * TILE; x1 = (c1 + 1) * TILE
        y0 = rys.min() * TILE; y1 = (rys.max() + 1) * TILE
        # 三点三角（与 A5 山同形：底边两点 + 顶点）
        pts = [[x0, y1], [x1, y1], [(x0 + x1) // 2, y0]]
        extra.append(pts)
        print("    补山 bbox=(%d,%d)-(%d,%d)" % (x0, y0, x1, y1))
    rects = [SHEN, MARKET, house_rect(pz, LOT_Z), house_rect(pg, LOT_G)]
    s1, S4b = report(tag + " + 补山%d" % len(extra), rects, extra)
    print("  → 补山后 cover5in4=%.1f%%  仍缺的 A5 实体 %d 格" % (s1["cover5in4"] * 100, s1["n5"] - s1["inter"]))
