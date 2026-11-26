#!/usr/bin/env python
"""评估一个具体的 A4 实体带方案（人工设计的干净版）。
口径：S = 房屋 lot 外框 ∪ 山体多边形（32px 网格）。只读分析，不写仓库数据。
"""
import numpy as np

TILE = 32
W, H = 4800, 3600
GW, GH = W // TILE, H // TILE

def rect_mask(x0, y0, w, h):
    m = np.zeros((GH, GW), dtype=bool)
    m[y0 // TILE:(y0 + h) // TILE, x0 // TILE:(x0 + w) // TILE] = True
    return m

A5_HOUSES = [
    ("shen_a5", 64, 416, 1152, 1152),
    ("market", 2144, 320, 1344, 896),
    ("toyshop", 2176, 1984, 672, 640),
    ("school", 576, 1920, 1216, 960),
]
A5_HILLS = [(4288, 2624, 512, 384), (64, 2624, 512, 384), (4288, 3040, 384, 288)]

# 方案甲：zhou_a4 贴 A5 小学地块西北角，zheng_a4 贴 A5 玩具店地块西北角
#        剩余 school/toyshop 地块由 4 座补山覆盖
PLAN_A_HOUSES = [
    ("shen_a4", 64, 416, 1152, 1152),
    ("market", 2144, 320, 1344, 896),
    ("zhou_a4", 576, 1920, 704, 352),
    ("zheng_a4", 2176, 1984, 640, 416),
]
PLAN_A_HILLS = A5_HILLS + [
    (1280, 1920, 512, 960),     # school 地块东半
    (576, 2272, 1216, 608),     # school 地块南半
    (2176, 2400, 672, 224),     # toyshop 地块南半
    (2816, 1984, 32, 416),      # toyshop 地块东窄条
]

def build(plan_houses, plan_hills):
    m = np.zeros((GH, GW), dtype=bool)
    for _, x, y, w, h in plan_houses:
        m |= rect_mask(x, y, w, h)
    for x, y, w, h in plan_hills:
        m |= rect_mask(x, y, w, h)
    return m

def river_mask():
    r = np.zeros((GH, GW), dtype=bool)
    for x in range(GW):
        depth = 5.5 + 1.5 * np.sin(x / 13.0 + 0.6) + 0.8 * np.sin(x / 5.3 + 2.1)
        bay = np.exp(-((x - 46.5) / 16.0) ** 2)
        d = int(round(max(4, min(15, depth + bay * 8.0))))
        r[0:d + 1, x] = True
    return r

RIVER = river_mask()
ROAD = rect_mask(0, 1600, 4800, 128)
DAM = rect_mask(384, 96, 256, 128)
FIELD = rect_mask(3600, 320, 880, 384)
RING = rect_mask(2048 - 304, 1664 - 304, 608, 608)
LANE_N = rect_mask(1984, 288, 128, 1360 - 288)
LANE_S = rect_mask(1984, 1968, 128, 3600 - 1968)

def report(tag, plan_houses, plan_hills):
    a5 = build(A5_HOUSES, A5_HILLS)
    a4 = build(plan_houses, plan_hills)
    inter = (a4 & a5).sum()
    print("== %s ==" % tag)
    print("  A5 cells=%d  A4 cells=%d" % (a5.sum(), a4.sum()))
    print("  cover(A5⊆A4)=%.1f%%  cover(A4⊆A5)=%.1f%%  IoU=%.1f%%" % (
        100.0 * inter / a5.sum(), 100.0 * inter / a4.sum(),
        100.0 * inter / (a5 | a4).sum()))
    print("  A4有A5无=%d 格   A5有A4无=%d 格" % ((a4 & ~a5).sum(), (a5 & ~a4).sum()))
    # 相邻时代虚化触发率（以 A4 为源帧推 A5 / 以 A5 为源帧推 A4）
    print("  相邻双向差: A4空地->A5实体 %d 格 ; A5空地->A4实体 %d 格" % (
        (a5 & ~a4).sum(), (a4 & ~a5).sum()))
    # 补山合法性
    for x, y, w, h in plan_hills:
        if (x, y, w, h) in A5_HILLS:
            continue
        m = rect_mask(x, y, w, h)
        house_overlap = False
        for _, hx, hy, hw, hh in plan_houses:
            if (m & rect_mask(hx, hy, hw, hh)).any():
                house_overlap = True
        print("  补山 [%d,%d,%d,%d] 压房=%s 主路=%s 河=%s 坝=%s 田=%s 环岛=%s 车道=%s" % (
            x, y, w, h, house_overlap, (m & ROAD).any(), (m & RIVER).any(),
            (m & DAM).any(), (m & FIELD).any(), (m & RING).any(),
            (m & (LANE_N | LANE_S)).any()))

report("方案甲（zhou 贴小学西北、zheng 贴玩具店西北 + 4 补山）", PLAN_A_HOUSES, PLAN_A_HILLS)

# 方案乙：zhou_a4 直接放在小学地块正中偏北，zheng_a4 放在玩具店地块正中
PLAN_B_HOUSES = [
    ("shen_a4", 64, 416, 1152, 1152),
    ("market", 2144, 320, 1344, 896),
    ("zhou_a4", 832, 1920, 704, 352),
    ("zheng_a4", 2176, 2176, 640, 416),
]
PLAN_B_HILLS = A5_HILLS + [
    (576, 1920, 256, 960),
    (1536, 1920, 256, 960),
    (576, 2272, 1216, 608),
    (2176, 1984, 640, 192),
    (2816, 1984, 32, 416),
]
report("方案乙（两房都在地块正中 + 5 补山）", PLAN_B_HOUSES, PLAN_B_HILLS)
