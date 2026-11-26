#!/usr/bin/env python
"""A4 实体带补山求解：把 A5 实体带在 A4 缺失的格用补山覆盖，且补山不压本帧 house 自身占地。
口径：S = 房屋 lot 外框 ∪ 山体多边形（32px 网格）。只读分析，不写仓库数据。
"""
import numpy as np

TILE = 32
W, H = 4800, 3600
GW, GH = W // TILE, H // TILE  # 150 x 112

def rect_mask(x0, y0, w, h):
    m = np.zeros((GH, GW), dtype=bool)
    m[y0 // TILE:(y0 + h) // TILE, x0 // TILE:(x0 + w) // TILE] = True
    return m

def house_mask(x0, y0, w, h):
    return rect_mask(x0, y0, w, h)

def hill_mask(x0, y0, w, h):
    return rect_mask(x0, y0, w, h)

# A5 实体（houses + 3 hills）
A5_HOUSES = [
    ("shen_a5", 64, 416, 1216, 1568 - 416),
    ("market", 2144, 320, 3488 - 2144, 1216 - 320),
    ("toyshop", 2176, 1984, 2848 - 2176, 2624 - 1984),
    ("school", 576, 1920, 1792 - 576, 2880 - 1920),
]
A5_HILLS = [(4288, 2624, 4800 - 4288, 3008 - 2624),
             (64, 2624, 576 - 64, 3008 - 2624),
             (4288, 3040, 4672 - 4288, 3328 - 3040)]

a5 = np.zeros((GH, GW), dtype=bool)
for _, x, y, w, h in A5_HOUSES:
    a5 |= house_mask(x, y, w, h)
for x, y, w, h in A5_HILLS:
    a5 |= hill_mask(x, y, w, h)

# A4 候选：shen_a4 / market 与 A5 同位；zhou_a4 / zheng_a4 一栋进学校区一栋贴玩具店
A4_HOUSES = [
    ("shen_a4", 64, 416, 1216, 1568 - 416),
    ("market", 2144, 320, 3488 - 2144, 1216 - 320),
    ("zhou_a4", 640, 1984, 1344 - 640, 2336 - 1984),
    ("zheng_a4", 2304, 1984, 2944 - 2304, 2400 - 1984),
]
a4 = np.zeros((GH, GW), dtype=bool)
for _, x, y, w, h in A4_HOUSES:
    a4 |= house_mask(x, y, w, h)
for x, y, w, h in A5_HILLS:
    a4 |= hill_mask(x, y, w, h)

house_only = np.zeros((GH, GW), dtype=bool)
for _, x, y, w, h in A4_HOUSES:
    house_only |= house_mask(x, y, w, h)

gap = a5 & ~a4
print("A5 cells=%d  A4 cells=%d  gap=%d" % (a5.sum(), a4.sum(), gap.sum()))

# 贪心最大矩形补山（不压 house）
def best_rect(mask, forbidden):
    best = (0, None)
    GHm, GWm = mask.shape
    # 用前缀和快速算矩形内 gap 数量
    ps = np.zeros((GHm + 1, GWm + 1), dtype=np.int32)
    np.cumsum(np.cumsum(mask.astype(np.int32), axis=0), axis=1, out=ps[1:, 1:])
    fb = np.zeros((GHm + 1, GWm + 1), dtype=np.int32)
    np.cumsum(np.cumsum(forbidden.astype(np.int32), axis=0), axis=1, out=fb[1:, 1:])
    # 候选矩形：只在 gap 的列/行边界上取，粗网格 32px 已够
    rows = sorted(set([i for i in range(GHm) if mask[i].any()] + [0]))
    cols = sorted(set([j for j in range(GWm) if mask[:, j].any()] + [0]))
    for i0 in rows:
        for i1 in rows:
            if i1 <= i0:
                continue
            for j0 in cols:
                for j1 in cols:
                    if j1 <= j0:
                        continue
                    cnt = ps[i1, j1] - ps[i0, j1] - ps[i1, j0] + ps[i0, j0]
                    f = fb[i1, j1] - fb[i0, j1] - fb[i1, j0] + fb[i0, j0]
                    if f > 0:
                        continue
                    area = (i1 - i0) * (j1 - j0)
                    if cnt == area and area > best[0]:
                        best = (area, (i0, i1, j0, j1))
    return best[1]

cur_gap = gap.copy()
hills = []
for _ in range(8):
    r = best_rect(cur_gap, house_only)
    if r is None:
        break
    i0, i1, j0, j1 = r
    hills.append((j0 * TILE, i0 * TILE, (j1 - j0) * TILE, (i1 - i0) * TILE))
    cur_gap[i0:i1, j0:j1] = False

print("补山 %d 块：" % len(hills))
for h in hills:
    print("  rect [%d, %d, %d, %d]" % h)

final = a4.copy()
for x, y, w, h in hills:
    final |= hill_mask(x, y, w, h)

inter = (final & a5).sum()
print("cover5in4 = %.1f%%   cover4in5 = %.1f%%" % (
    100.0 * inter / a5.sum(), 100.0 * inter / final.sum()))
print("仍缺 A5 实体 %d 格" % (a5 & ~final).sum())

# 相邻时代虚化触发率（A4 空地 -> A5 实体 / A5 实体 -> A4 空地）
a4_only_house = a4.copy()
trig_45 = (a4 & ~final).sum()  # A4 实体区里 A5 不是实体 => 反向
gap_45 = (final & ~a4).sum()
print("A4有A5无 = %d 格 ; A5有A4无 = %d 格" % (trig_45, gap_45))

# 补山是否压主路/河/坝/田/环岛/内岛（粗判）
def band(y0, y1, x0, x1):
    m = np.zeros((GH, GW), dtype=bool)
    m[y0 // TILE:y1 // TILE, x0 // TILE:x1 // TILE] = True
    return m

road = band(1600, 1728, 0, 4800)
river = np.zeros((GH, GW), dtype=bool)
for x in range(GW):
    depth = 5.5 + 1.5 * np.sin(x / 13.0 + 0.6) + 0.8 * np.sin(x / 5.3 + 2.1)
    bay = np.exp(-((x - 46.5) / 16.0) ** 2)
    d = int(round(max(4, min(15, depth + bay * 8.0))))
    river[0:d + 1, x] = True
dam = rect_mask(384, 96, 256, 128)
field = rect_mask(3600, 320, 880, 384)
ring = rect_mask(2048 - 304, 1664 - 304, 608, 608)
for h in hills:
    m = hill_mask(*h)
    print("  补山 %s : 压主路%s 压河%s 压坝%s 压田%s 压环岛%s" % (
        h, (m & road).any(), (m & river).any(), (m & dam).any(),
        (m & field).any(), (m & ring).any()))
