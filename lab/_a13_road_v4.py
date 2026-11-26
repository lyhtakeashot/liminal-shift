#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""地图 v4：A1-A3 路网重做 + 删除残留山（任务书 docs/PROMPT-map-v4-exec.md）。

用法：
    python lab/_a13_road_v4.py --check    # 只自检 S1..S9，不落盘
    python lab/_a13_road_v4.py --write    # 自检全绿才写 data/frames.json（幂等）
    python lab/_a13_road_v4.py --png      # 顺带重画 lab/maps/*.png 预览

**一切几何按「格」算（1 格 = 32px），落盘时 x32。** 见任务书 §1.5。

几何
----
主路：Catmull-Rom（向心 alpha=0.5）穿 5 个控制点，按列中心采样 -> 取整格 ->
夹到 [46,47] 格 -> 逐对夹逼使相邻 |Δy| <= 1 格。A3 是单一直线 y=46 格。
（块高 2 格：y=46 占行 46..47，y=47 占行 47..48 ⇒ 带的面 1472..1568px，
 峰谷差 32px <= 任务书 §1.1 的 48px，两个口径都满足。）
支路：两段斜线（先 40 度自路面斜上，再 55 度斜进门口，任务书 §3.5 要求
      「末段与 gate 边成 30~60 度」），用「格心到折线距离 <= 1 格」的胶囊
      光栅化成 32px 格，每列合成 [x,y,32,64] 块。宽 2 格（64px）；进自家院子
      以后收成 1 格（32px）的门口铺装（理由见 feedback §3：S8 要求
      「自家最多压 6 格」，而 mill_a3 的 lot 实际是 17x16 不是任务书的 17x12）。
"""
from __future__ import print_function

import argparse
import io
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FRAMES_PATH = os.path.join(ROOT, 'data', 'frames.json')
HOUSES_PATH = os.path.join(ROOT, '_ref', 'houses', 'houses_data.json')

TILE = 32                      # 1 格 = 32px
NC = 150                       # 世界宽 150 格（4800px）
WORLD_W = NC * TILE
ROAD_H_CELLS = 2
ROAD_H = ROAD_H_CELLS * TILE   # 64px = 2 格

Y_BASE = 46
Y_MIN, Y_MAX = 46, 47
A3_Y = 46

CP_A1 = [(0, 46), (15, 47), (50, 46), (100, 47), (150, 46)]
CP_A2 = [(0, 46), (25, 47), (63, 46), (112, 47), (150, 46)]
CP_X_A1 = [15, 50, 100]
CP_X_A2 = [25, 63, 112]

ROAD_FRAMES = ('a1_1926', 'a2_1951', 'a3_1976')
ZHOU_IDS = ('zhou_house', 'zhou_a2', 'zhou_a3')
ZHOU_NEW_POS_CELL = (18, 49)
ZHOU_NEW_POS = [ZHOU_NEW_POS_CELL[0] * TILE, ZHOU_NEW_POS_CELL[1] * TILE]

LOCUST_CENTER_CELL = (64, 52)
CROWN_R_CELL = {'a1_1926': 1, 'a2_1951': 2, 'a3_1976': 3,
                'a4_2001': 3, 'a5_2026': 3}

SEG1_DEG = 40.0                 # 支路首段与水平面夹角（自主路北沿斜上）
SEG2_DEG = 55.0                 # 支路末段与水平面夹角；= 与 gate 边的夹角，须在 30..60
SEG2_RATIO = 0.45               # 末段承担的竖直落差占比


# --------------------------------------------------------------------------
def load_json(path):
    with io.open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    return json.loads(raw), raw


def dump_like(data, raw):
    out = json.dumps(data, indent=2, ensure_ascii=False)
    if raw.endswith('\n'):
        out += '\n'
    return out


def frame_by_id(data, fid):
    for fr in data['frames']:
        if fr['id'] == fid:
            return fr
    raise KeyError(fid)


def is_road(s):
    return s.get('label') == '路' and bool(s.get('road'))


def road_shapes(fr):
    return [s for s in fr['shapes'] if is_road(s)]


def head_frames():
    try:
        p = subprocess.run(['git', 'show', 'HEAD:data/frames.json'], cwd=ROOT,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            return None
        return json.loads(p.stdout.decode('utf-8'))
    except Exception:
        return None


# --------------------------------------------------------------------------
# 主路
# --------------------------------------------------------------------------
def _cr(p0, p1, p2, p3, u):
    def knot(t, a, b):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        return t + max(d, 1e-6) ** 0.5

    t0 = 0.0
    t1 = knot(t0, p0, p1)
    t2 = knot(t1, p1, p2)
    t3 = knot(t2, p2, p3)
    t = t1 + (t2 - t1) * u

    def blend(a, b, ta, tb):
        if abs(tb - ta) < 1e-12:
            return a
        wa = (tb - t) / (tb - ta)
        wb = (t - ta) / (tb - ta)
        return (a[0] * wa + b[0] * wb, a[1] * wa + b[1] * wb)

    a1 = blend(p0, p1, t0, t1)
    a2 = blend(p1, p2, t1, t2)
    a3 = blend(p2, p3, t2, t3)
    b1 = blend(a1, a2, t0, t2)
    b2 = blend(a2, a3, t1, t3)
    return blend(b1, b2, t1, t2)


def cr_points(cps, density=96):
    pts = [(float(c[0]), float(c[1])) for c in cps]
    ext = [pts[0]] + pts + [pts[-1]]
    dense = []
    for k in range(len(pts) - 1):
        p0, p1, p2, p3 = ext[k], ext[k + 1], ext[k + 2], ext[k + 3]
        for s in range(density):
            dense.append(_cr(p0, p1, p2, p3, s / float(density)))
    dense.append(pts[-1])
    return dense


def sample_cols(dense, n):
    ys = []
    k = 0
    for i in range(n):
        x = i + 0.5
        while k + 2 < len(dense) and dense[k + 1][0] < x:
            k += 1
        x0, y0 = dense[k]
        x1, y1 = dense[min(k + 1, len(dense) - 1)]
        if abs(x1 - x0) < 1e-9:
            ys.append(y0)
        else:
            r = min(max((x - x0) / (x1 - x0), 0.0), 1.0)
            ys.append(y0 + (y1 - y0) * r)
    return ys


def quantize(raw, lo, hi):
    ys = [min(max(int(round(v)), lo), hi) for v in raw]
    n = len(ys)
    for _ in range(60):
        changed = False
        for i in range(1, n):
            if ys[i] > ys[i - 1] + 1:
                ys[i] = ys[i - 1] + 1
                changed = True
            elif ys[i] < ys[i - 1] - 1:
                ys[i] = ys[i - 1] - 1
                changed = True
        for i in range(n - 2, -1, -1):
            if ys[i] > ys[i + 1] + 1:
                ys[i] = ys[i + 1] + 1
                changed = True
            elif ys[i] < ys[i + 1] - 1:
                ys[i] = ys[i + 1] - 1
                changed = True
        if not changed:
            break
    return ys


def build_main(cps):
    return quantize(sample_cols(cr_points(cps), NC), Y_MIN, Y_MAX)


def bends_of(ys):
    """等值段压成 run，再数转向点。位置取平台中点（量化的平台会跨 CP 两侧）。"""
    runs = []
    for i, v in enumerate(ys):
        if runs and runs[-1][0] == v:
            runs[-1][2] = i
        else:
            runs.append([v, i, i])
    out = []
    for j in range(1, len(runs) - 1):
        a, b, c = runs[j - 1][0], runs[j][0], runs[j + 1][0]
        if (b - a) * (c - b) < 0:
            out.append(((runs[j][1] + runs[j][2]) / 2.0, b,
                        'min' if b < a else 'max', (runs[j][1], runs[j][2])))
    return out


def main_rects(ys):
    return [[i * TILE, ys[i] * TILE, TILE, ROAD_H] for i in range(len(ys))]


# --------------------------------------------------------------------------
# 支路
# --------------------------------------------------------------------------
def seg_cells(p0, p1, half=1.0):
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    cells = set()
    for c in range(int(math.floor(min(x0, x1) - half)) - 1,
                   int(math.ceil(max(x0, x1) + half)) + 2):
        for r in range(int(math.floor(min(y0, y1) - half)) - 1,
                       int(math.ceil(max(y0, y1) + half)) + 2):
            px_, py_ = c + 0.5, r + 0.5
            if L2 <= 1e-12:
                t = 0.0
            else:
                t = ((px_ - x0) * dx + (py_ - y0) * dy) / L2
            if t < 0.0 or t > 1.0:
                continue
            if math.hypot(px_ - (x0 + t * dx), py_ - (y0 + t * dy)) <= half + 1e-9:
                cells.add((c, r))
    return cells


def blocks_for_run(c, r0, r1):
    """覆盖 r0..r1 行的 [x,y,1,2] 块（允许 1 格重叠；单行 run 会出头 1 行）。"""
    if r1 <= r0:
        return [[c * TILE, r0 * TILE, TILE, ROAD_H]]
    ys = list(range(r0, r1, ROAD_H_CELLS))
    if not ys or ys[-1] + 1 < r1:
        ys.append(r1 - 1)
    return [[c * TILE, y * TILE, TILE, ROAD_H] for y in ys]


def blocks_from_cells(cells):
    cols = {}
    for (c, r) in cells:
        cols.setdefault(c, []).append(r)
    rects = []
    for c in sorted(cols):
        rs = sorted(cols[c])
        s = p = rs[0]
        for r in rs[1:]:
            if r == p + 1:
                p = r
            else:
                rects.extend(blocks_for_run(c, s, p))
                s = p = r
        rects.extend(blocks_for_run(c, s, p))
    return rects


def plan_branch(g, gate_cell, lot_cell):
    gx, gy = gate_cell
    gate_edge = gy + 1
    lot_c0, lot_r0, lot_w, lot_h = lot_cell
    lot_r1 = lot_r0 + lot_h
    lot_c1 = lot_c0 + lot_w
    stop64 = max(gate_edge, lot_r1)
    # 中轴线终点 x：压在 gate 格与东邻格的界上，胶囊（半径 1 格）正好两列各半
    tx = gx + 1.0

    def road_top(col):
        if g is None:
            return A3_Y
        return g[max(0, min(NC - 1, col))]

    def geom(ys_est):
        rise = max(4.0, float(ys_est - stop64))
        dy2 = max(3, int(round(rise * SEG2_RATIO)))
        dy1 = max(1, int(round(rise)) - dy2)
        dx1 = dy1 / math.tan(math.radians(SEG1_DEG))
        dx2 = dy2 / math.tan(math.radians(SEG2_DEG))
        return dy1, dy2, dx1, dx2

    ys_est = road_top(int(round(tx + 8)))
    for _ in range(10):
        _, _, dx1, dx2 = geom(ys_est)
        new = road_top(int(round(tx + dx1 + dx2)))
        if new == ys_est:
            break
        ys_est = new
    dy1, dy2, dx1, dx2 = geom(ys_est)
    xs = tx + dx1 + dx2
    y_road = road_top(int(round(xs)))
    bend = (tx + dx2, stop64 + dy2)

    cells = set()
    cells |= seg_cells((xs, y_road), bend)
    cells |= seg_cells(bend, (tx, stop64))
    rects = blocks_from_cells(cells)

    door = []
    if stop64 - 1 >= gate_edge:
        door = blocks_for_run(gx, gate_edge, stop64 - 1)
    rects = rects + door

    covered = set()
    for r in rects:
        c = r[0] // TILE
        rr = r[1] // TILE
        covered.add((c, rr))
        covered.add((c, rr + 1))

    gc = (gx + 0.5, gy + 0.5)
    best = None
    for (c, r) in covered:
        for (qx, qy) in ((c, r), (c + 1, r), (c, r + 1), (c + 1, r + 1),
                         (c + 0.5, r), (c + 0.5, r + 1),
                         (c, r + 0.5), (c + 1, r + 0.5)):
            dd = math.hypot(qx - gc[0], qy - gc[1])
            if best is None or dd < best[0]:
                best = (dd, (qx, qy))

    own = len([1 for (c, r) in covered
               if lot_c0 <= c < lot_c1 and lot_r0 <= r < lot_r1])
    return {
        'gate_cell': gate_cell, 'junction': (xs, y_road), 'bend': bend,
        'stop64': stop64, 'axis_end': (tx, stop64),
        'seg1': (dx1, dy1), 'seg2': (dx2, dy2),
        'rects': rects, 'cells': covered,
        'endpoint': best[1], 'endpoint_err_px': best[0] * TILE,
        'own_lot_cells': own, 'door_rows': (stop64 - gate_edge),
    }


# --------------------------------------------------------------------------
# 房子
# --------------------------------------------------------------------------
def houses_index():
    lst, _ = load_json(HOUSES_PATH)
    return {h['id']: h for h in lst}


def house_pos_cell(fr, hid):
    for s in fr['shapes']:
        if s.get('type') == 'house' and s.get('id') == hid:
            return (s['pos'][0] // TILE, s['pos'][1] // TILE)
    raise KeyError(hid)


def gate_of(house):
    """首个门格（相对 lot 左上角的 [列,行]）。没门（如 shen_a5 gate==[]）返回 None。"""
    g = house.get('gate')
    if isinstance(g, list) and g and isinstance(g[0], list):
        g = g[0]
    if not isinstance(g, list) or len(g) < 2:
        return None
    return g


def gate_cell_of(house, pos_cell):
    g = gate_of(house)
    if g is None:
        return None
    return (pos_cell[0] + g[0], pos_cell[1] + g[1])


def lot_cell_of(house, pos_cell):
    lot = house.get('lot') or [0, 0, house.get('w', 16), house.get('h', 12)]
    return (pos_cell[0] + lot[0], pos_cell[1] + lot[1], lot[2], lot[3])


def lot_rect_px(house, pos_cell):
    c0, r0, w, h = lot_cell_of(house, pos_cell)
    return (c0 * TILE, r0 * TILE, w * TILE, h * TILE)


# --------------------------------------------------------------------------
def rect_circle_hit(rect, center_px, radius_px):
    x, y, w, h = rect
    cx, cy = center_px
    nx = min(max(cx, x), x + w)
    ny = min(max(cy, y), y + h)
    return math.hypot(cx - nx, cy - ny) < radius_px - 1e-9


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--png', action='store_true')
    args = ap.parse_args(argv[1:])

    data, raw = load_json(FRAMES_PATH)
    houses = houses_index()

    rt = dump_like(data, raw)
    print('roundtrip=%s (bytes=%d, tail_nl=%s)'
          % ('OK' if rt == raw else 'MISMATCH', len(raw.encode('utf-8')),
             raw.endswith('\n')))
    if rt != raw:
        print('!! 重新 dump 与原文不一致，先别写盘')
        return 2

    head = head_frames()
    print('baseline=%s' % ('HEAD 可用' if head else 'HEAD 不可用（S1/S2/S3 SKIP）'))

    # ---------- 计划 ----------
    plans = {}
    for fid in ROAD_FRAMES:
        fr = frame_by_id(data, fid)
        if fid == 'a1_1926':
            ys = build_main(CP_A1)
        elif fid == 'a2_1951':
            ys = build_main(CP_A2)
        else:
            ys = [A3_Y] * NC
        g = None if len(set(ys)) == 1 else ys
        brs = []
        for s in fr['shapes']:
            if s.get('type') != 'house':
                continue
            hid = s['id']
            if hid not in houses or hid.startswith('zhou'):
                continue
            h = houses[hid]
            pos_c = house_pos_cell(fr, hid)
            brs.append(plan_branch(g, gate_cell_of(h, pos_c), lot_cell_of(h, pos_c)))
        plans[fid] = {'ys': ys, 'brs': brs}

    fails = [0]

    def verdict(tag, bad, extra=''):
        if bad:
            fails[0] += 1
        print('%s %s%s' % (tag, 'PASS' if not bad else 'FAIL', extra))
        for b in bad:
            print('   - ' + str(b))

    # ---------- 落地数据（内存里先拼出来，自检就查它） ----------
    new = json.loads(json.dumps(data, ensure_ascii=False))
    for fid in ROAD_FRAMES:
        fr = frame_by_id(new, fid)
        p = plans[fid]
        new_main = [{'type': 'rect', 'label': '路', 'road': True, 'rect': r}
                    for r in main_rects(p['ys'])]
        new_br = [{'type': 'rect', 'label': '路', 'road': True, 'rect': r}
                  for br in p['brs'] for r in br['rects']]
        shapes, done = [], False
        for s in fr['shapes']:
            if is_road(s):
                if not done:
                    shapes.extend(new_main)
                    shapes.extend(new_br)
                    done = True
                continue
            shapes.append(s)
        if not done:
            shapes.extend(new_main)
            shapes.extend(new_br)
        fr['shapes'] = shapes

    for fr in new['frames']:
        for s in fr['shapes']:
            if s.get('type') == 'house' and s.get('id') in ZHOU_IDS:
                s['pos'] = list(ZHOU_NEW_POS)

    removed = {}
    for fr in new['frames']:
        keep = [s for s in fr['shapes'] if s.get('label') != '山']
        removed[fr['id']] = len(fr['shapes']) - len(keep)
        fr['shapes'] = keep

    # ---------- S1 ----------
    bad = []
    if head:
        for k in ('world', 'safe_top', 'safe_bottom', 'start_frame', 'start_pos'):
            if json.dumps(new.get(k), ensure_ascii=False) != \
               json.dumps(head.get(k), ensure_ascii=False):
                bad.append('%s 变了' % k)
    verdict('S1', bad, '  world/start_pos/start_frame/safe_* 与 HEAD 逐字节相同')

    # ---------- S2 ----------
    bad = []
    if head:
        for fid in ('a4_2001', 'a5_2026'):
            a = [s for s in frame_by_id(new, fid)['shapes'] if s.get('label') != '山']
            b = [s for s in frame_by_id(head, fid)['shapes'] if s.get('label') != '山']
            if json.dumps(a, ensure_ascii=False, sort_keys=True) != \
               json.dumps(b, ensure_ascii=False, sort_keys=True):
                bad.append('%s 除山以外还有变化' % fid)
            if json.dumps(frame_by_id(new, fid)['hotspots'], ensure_ascii=False,
                          sort_keys=True) != \
               json.dumps(frame_by_id(head, fid)['hotspots'], ensure_ascii=False,
                          sort_keys=True):
                bad.append('%s hotspots 变了' % fid)
    verdict('S2', bad, '  a4/a5 除山以外的 shapes + hotspots 未动')

    # ---------- S3 ----------
    bad = []
    if head:
        for fr in new['frames']:
            hfr = frame_by_id(head, fr['id'])
            if json.dumps(fr['hotspots'], ensure_ascii=False, sort_keys=True) != \
               json.dumps(hfr['hotspots'], ensure_ascii=False, sort_keys=True):
                bad.append('%s hotspots 与 HEAD 不同' % fr['id'])
    verdict('S3', bad, '  五帧 hotspots 与 HEAD 深比较相同')

    # ---------- S4 ----------
    bad = []
    for fid, r_cell in CROWN_R_CELL.items():
        fr = frame_by_id(new, fid)
        cen = None
        for s in fr['shapes']:
            if s.get('type') == 'circle' and s.get('label', '').startswith('老槐'):
                cen = s['center']
        if cen is None:
            bad.append('%s 找不到老槐' % fid)
            continue
        if (cen[0] // TILE, cen[1] // TILE) != LOCUST_CENTER_CELL or \
           cen[0] % TILE or cen[1] % TILE:
            bad.append('%s 老槐圆心 %s != (64,52) 格' % (fid, cen))
        for s in fr['shapes']:
            if not is_road(s) or s.get('type') != 'rect':
                continue
            if rect_circle_hit(s['rect'], cen, r_cell * TILE):
                bad.append('%s 有路面块 %s 压到 r=%d 格冠幅' % (fid, s['rect'], r_cell))
    verdict('S4', bad, '  老槐圆心 (64,52) 格不动 + 五帧无路面压冠')

    # ---------- S5 ----------
    bad = []
    for fid in ROAD_FRAMES:
        for s in road_shapes(frame_by_id(new, fid)):
            if s.get('type') != 'rect':
                bad.append('%s 有非 rect 路面 %s' % (fid, s.get('type')))
                continue
            r = s['rect']
            if len(r) != 4 or r[2] != TILE or r[3] != ROAD_H:
                bad.append('%s 路面块不是 [x,y,32,64]: %s' % (fid, r))
            elif r[0] % TILE or r[1] % TILE:
                bad.append('%s 路面块不在整格: %s' % (fid, r))
    verdict('S5', bad, '  a1..a3 全部路面块 = [x,y,1,2] 格（a4/a5 是历史 128 高块，本线禁改）')

    # ---------- S6 ----------
    bad = []
    ys1 = plans['a1_1926']['ys']
    have = set()
    for s in road_shapes(frame_by_id(new, 'a1_1926')):
        have.add(tuple(s['rect']))
    for r in main_rects(ys1):
        if tuple(r) not in have:
            bad.append('A1 路块缺失: %s' % r)
    for i in range(1, NC):
        if abs(ys1[i] - ys1[i - 1]) > 1:
            bad.append('A1 第 %d 列 |Δy|=%d > 1 格' % (i, abs(ys1[i] - ys1[i - 1])))
    bends1 = bends_of(ys1)
    if len(bends1) > 3:
        bad.append('A1 弯折 %d 处 > 3' % len(bends1))
    # 弯位判据：每个内部控制点所在的列必须就是该处极值（1 格振幅量化后平台很宽，
    # 拿平台中点当弯位会被左右坡度不对称带偏 ~9 格，故按「CP 列落在对应极值平台上」判）。
    spans = [(sp, y) for (col, y, kind, sp) in bends1]
    cps1 = CP_A1[1:-1]
    for (cx, cy) in cps1:
        if ys1[cx] != cy:
            bad.append('A1 第 %d 列(CP) ys=%d != %d' % (cx, ys1[cx], cy))
        elif not any(sp[0] <= cx <= sp[1] and y == cy for (sp, y) in spans):
            bad.append('A1 第 %d 列(CP, y=%d) 不在任何极值平台上' % (cx, cy))
    for (sp, y) in spans:
        if not any(sp[0] <= cx <= sp[1] for (cx, cy) in cps1):
            bad.append('A1 极值平台 %d..%d (y=%d) 没有对应 CP' % (sp[0], sp[1], y))
    verdict('S6', bad, '  A1 覆盖 %d 列、弯 %d 处 %s、CP 列 x=%s 取到极值 %s、相邻 |Δy|<=1 格'
            % (NC, len(bends1),
               ['%s y=%d 平台 %d..%d' % (k, y, sp[0], sp[1]) for (c, y, k, sp) in bends1],
               [cx for (cx, cy) in cps1], [cy for (cx, cy) in cps1]))

    # ---------- S7 ----------
    bad = []
    ys3 = plans['a3_1976']['ys']
    have3 = set(tuple(s['rect']) for s in road_shapes(frame_by_id(new, 'a3_1976')))
    if len(set(ys3)) != 1 or ys3[0] != A3_Y:
        bad.append('A3 计划 y 不唯一/不是 46 格: %s' % sorted(set(ys3)))
    for r in main_rects(ys3):
        if tuple(r) not in have3:
            bad.append('A3 主路块缺失: %s' % r)
    verdict('S7', bad, '  A3 主路全程 y = %d 格（%d 列）' % (A3_Y, NC))

    # ---------- S8 ----------
    bad = []
    lines = []
    # 任务书 §3.5：末段与 gate 边（水平）成 30..60 度，且整条支路至少一个弯
    if not (30.0 <= SEG2_DEG <= 60.0):
        bad.append('支路末段与 gate 边夹角 %.0f 度不在 30..60' % SEG2_DEG)
    if abs(SEG1_DEG - SEG2_DEG) < 5.0:
        bad.append('支路两段夹角 %.0f/%.0f 度差 <5，没有可见拐点' % (SEG1_DEG, SEG2_DEG))
    for fid in ROAD_FRAMES:
        fr = frame_by_id(new, fid)
        for br in plans[fid]['brs']:
            gate = br['gate_cell']
            others = []
            for s in fr['shapes']:
                if s.get('type') != 'house':
                    continue
                h = houses.get(s['id'])
                if not h:
                    continue
                pos_c = (s['pos'][0] // TILE, s['pos'][1] // TILE)
                if gate_cell_of(h, pos_c) == gate:
                    continue
                c0, r0, w, hh = lot_cell_of(h, pos_c)
                n = len([1 for (c, r) in br['cells']
                         if c0 <= c < c0 + w and r0 <= r < r0 + hh])
                if n:
                    others.append((s['id'], n))
            lines.append('   %-9s gate%-9s 端点离格心 %5.1fpx  首段 %.0f度v%.1f/h%.1f 格 '
                         '末段 %.0f度v%.1f/h%.1f 格  自家院 %d 格  门口铺装 %d 格  他人院 %s'
                         % (fid, gate, br['endpoint_err_px'],
                            SEG1_DEG, br['seg1'][1], br['seg1'][0],
                            SEG2_DEG, br['seg2'][1], br['seg2'][0],
                            br['own_lot_cells'], br['door_rows'],
                            others if others else '无'))
            if br['endpoint_err_px'] > 24:
                bad.append('%s gate%s 端点 %.1fpx > 24px'
                           % (fid, gate, br['endpoint_err_px']))
            if others:
                bad.append('%s gate%s 压到别的院子 %s' % (fid, gate, others))
            if br['own_lot_cells'] > 6:
                bad.append('%s gate%s 自家院子压 %d 格 > 6'
                           % (fid, gate, br['own_lot_cells']))
    verdict('S8', bad, '  9 条支路（端点 <=24px / 不压他人院 / 自家 <=6 格）')
    for l in lines:
        print(l)

    # ---------- S9 ----------
    bad = []
    for fr in new['frames']:
        n = len([s for s in fr['shapes'] if s.get('label') == '山'])
        if n:
            bad.append('%s 还有 %d 块山' % (fr['id'], n))
    for fr in new['frames']:
        for s in fr['shapes']:
            if s.get('type') == 'house' and s.get('id') in ZHOU_IDS:
                pc = (s['pos'][0] // TILE, s['pos'][1] // TILE)
                if pc != ZHOU_NEW_POS_CELL or s['pos'][0] % TILE or s['pos'][1] % TILE:
                    bad.append('%s/%s pos 格 = %s != (18,49) 或非整格'
                               % (fr['id'], s['id'], pc))
    for fid in ROAD_FRAMES:
        for s in road_shapes(frame_by_id(new, fid)):
            r = s['rect']
            if r[0] % TILE or r[1] % TILE:
                bad.append('%s 路块非整格: %s' % (fid, r))
    verdict('S9', bad, '  山计数 %s 全 0 + 周家三帧 (18,49) 格 + 全部整格' % removed)

    # ---------- 摘要 ----------
    print('\n各帧：')
    for fr in new['frames']:
        print('   %-9s shapes=%3d 路块=%3d 山=%d'
              % (fr['id'], len(fr['shapes']), len(road_shapes(fr)),
                 len([s for s in fr['shapes'] if s.get('label') == '山'])))
    for fid in ROAD_FRAMES:
        p = plans[fid]
        print('   %s 主路 %d 块 + 支路 %d 块（%d 条）'
              % (fid, len(main_rects(p['ys'])),
                 sum(len(b['rects']) for b in p['brs']), len(p['brs'])))
    print('   A1 y 序列(每10列) %s' % [plans['a1_1926']['ys'][i] for i in range(0, NC, 10)])
    print('   A2 y 序列(每10列) %s' % [plans['a2_1951']['ys'][i] for i in range(0, NC, 10)])
    print('   A1 弯 %s' % [(round(c, 1), y) for (c, y, k, sp) in bends_of(plans['a1_1926']['ys'])])
    print('   A2 弯 %s' % [(round(c, 1), y) for (c, y, k, sp) in bends_of(plans['a2_1951']['ys'])])
    print('   周家 lot 格: 18..29 x 49..55；A1/A2 在 18..29 列的路面顶行: %s / %s'
          % (sorted({plans['a1_1926']['ys'][i] for i in range(18, 30)}),
             sorted({plans['a2_1951']['ys'][i] for i in range(18, 30)})))

    print('\nTOTAL FAILS = %d' % fails[0])

    if args.png:
        render_all(new, houses)

    if args.write:
        if fails[0]:
            print('自检没过，拒绝写盘')
        else:
            out = dump_like(new, raw)
            with io.open(FRAMES_PATH, 'w', encoding='utf-8', newline='\n') as f:
                f.write(out)
            print('WROTE %s (%d bytes)' % (FRAMES_PATH, len(out.encode('utf-8'))))
            _, raw2 = load_json(FRAMES_PATH)
            print('写回后 roundtrip=%s'
                  % ('OK' if dump_like(json.loads(raw2), raw2) == raw2 else 'MISMATCH'))

    return 0 if fails[0] == 0 else 1


# --------------------------------------------------------------------------
def render_all(data, houses):
    from PIL import Image, ImageDraw
    outdir = os.path.join(HERE, 'maps')
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    S = 0.25
    for fr in data['frames']:
        W = int(WORLD_W * S)
        H = int(3600 * S)
        img = Image.new('RGB', (W, H), (206, 214, 176))
        d = ImageDraw.Draw(img)

        def sc(p):
            return (p[0] * S, p[1] * S)

        for s in fr['shapes']:
            t = s.get('type')
            lab = s.get('label')
            if t == 'polygon':
                if lab == '河':
                    col = (96, 132, 148)
                elif lab == '山':
                    col = (90, 106, 74)
                elif lab == '岛':
                    col = (150, 170, 130)
                elif lab == '路':
                    col = (138, 122, 90)
                else:
                    col = (170, 170, 150)
                d.polygon([sc(p) for p in s['points']], fill=col)
            elif t == 'rect':
                r = s['rect']
                if is_road(s):
                    col = (138, 122, 90)
                elif lab == '坝':
                    col = (106, 86, 72)
                elif lab == '路标':
                    col = (120, 104, 82)
                else:
                    col = (198, 196, 132)
                d.rectangle([sc((r[0], r[1])), sc((r[0] + r[2], r[1] + r[3]))], fill=col)
            elif t == 'circle':
                c = s['center']
                rr = s['radius']
                d.ellipse([sc((c[0] - rr, c[1] - rr)), sc((c[0] + rr, c[1] + rr))],
                          fill=(63, 107, 58) if (lab or '').startswith('老槐') else (74, 74, 70))
            elif t == 'house':
                h = houses.get(s['id'])
                if not h:
                    continue
                pos_c = (s['pos'][0] // TILE, s['pos'][1] // TILE)
                x0, y0, w, hh = lot_rect_px(h, pos_c)
                d.rectangle([sc((x0, y0)), sc((x0 + w, y0 + hh))],
                            fill=(168, 142, 112), outline=(80, 60, 45))
                gc = gate_cell_of(h, pos_c)
                if gc is None:
                    continue
                d.rectangle([sc((gc[0] * TILE, gc[1] * TILE)),
                             sc(((gc[0] + 1) * TILE, (gc[1] + 1) * TILE))],
                            fill=(190, 60, 60))
        p = os.path.join(outdir, '%s.png' % fr['id'])
        img.save(p)
        print('PNG %s (%dx%d)' % (p, W, H))


if __name__ == '__main__':
    sys.exit(main(sys.argv))