#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""a1/a2 村路重做（控制点 + Catmull-Rom，替掉正弦）+ 四宅支路 + a4 zheng_a4 挪位。

任务书：docs/PROMPT-a13-road-rework-exec.md
  §2 主路：≥7 个控制点 + 插值，每 32px 采样成 32x64 的 rect；每道弯必须写得出理由。
         h=64；y 只允许为了瓦片对齐量化到 32；相邻块 |Δy| ≤ 32。
         老槐红线：x∈[1888,2208] 内路面顶边 y ≥ 1728。a3 保持 [0,1728,4800,64] 不动。
  §3 支路：每栋有院子的房子一条 32 宽的支路，从主路到 gate 格中心（留 16px 门槛）。
  §1 a4：只挪 zheng_a4 一栋进右下。

用法：
  python lab/_a13_road_v3.py --snapshot   # 改前把受保护片段的指纹记下来
  python lab/_a13_road_v3.py --check      # 只跑自检，不写盘
  python lab/_a13_road_v3.py --write      # 自检全过才写 data/frames.json

本脚本不碰 scripts/** 与 _ref/**，只读 houses_data.json 拿 lot/gate。
"""
import argparse
import hashlib
import heapq
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAMES_PATH = os.path.join(ROOT, 'data', 'frames.json')
HOUSES_PATH = os.path.join(ROOT, '_ref', 'houses', 'houses_data.json')
BASELINE_PATH = os.path.join(ROOT, 'lab', '_a13_road_v3.baseline.json')

TILE = 32
ROAD_H = 64
BRANCH_W = 32
WORLD_W = 4800
WORLD_H = 3600
NC = WORLD_W // TILE          # 150 列
NR = WORLD_H // TILE          # 112 行

OLD_WELL = (2048, 1664)       # 老槐树心
OLD_WELL_R = 96
RED_LINE = (1888, 2208)       # 老槐红线窗口（x）
RED_LINE_Y = 1728

ZHENG_NEW_POS = (3456, 2304)

# --------------------------------------------------------------------------
# 受保护片段（§4-A1）
# --------------------------------------------------------------------------

def canon(obj):
    blob = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(blob.encode('utf-8')).hexdigest()[:16]


def protected(data):
    """除「a1/a2/a3 的 路 rect」和「zheng_a4 的 pos」以外，全部原样快照。"""
    out = {
        'world': data.get('world'),
        'safe_top': data.get('safe_top'),
        'safe_bottom': data.get('safe_bottom'),
        'start_frame': data.get('start_frame'),
        'start_pos': data.get('start_pos'),
        'frames': {},
    }
    for fr in data['frames']:
        shapes = []
        for s in fr['shapes']:
            if s.get('label') == '路' and s.get('road'):
                continue                                  # 主路 + 新支路都归本次改
            if s.get('type') == 'house' and s.get('id') == 'zheng_a4':
                shapes.append({'type': 'house', 'id': 'zheng_a4', 'solid': s.get('solid')})
                continue
            shapes.append(s)
        rest = {k: v for k, v in fr.items() if k not in ('shapes', 'hotspots')}
        out['frames'][fr['id']] = {
            'meta': rest,
            'shapes': shapes,
            'hotspots': fr.get('hotspots', []),
        }
    return out


# --------------------------------------------------------------------------
# 房屋几何（抄 scripts/house_shape.gd:157-238 的 grid_of / solid_rects）
# --------------------------------------------------------------------------

def grid_of(h):
    lot = h.get('lot', [0, 0, 0, 0])
    x0, y0, x1, y1 = int(lot[0]), int(lot[1]), int(lot[2]), int(lot[3])
    interior = set()
    for w in h.get('wings', []):
        wx, wy, ww, wh = int(w[0]), int(w[1]), int(w[2]), int(w[3])
        for j in range(wy + 1, wy + wh - 1):
            for i in range(wx + 1, wx + ww - 1):
                interior.add((i, j))

    part = set()
    for p in h.get('partitions', []):
        px1, py1, px2, py2 = int(p[0]), int(p[1]), int(p[2]), int(p[3])
        if px1 == px2:
            for j in range(min(py1, py2), max(py1, py2) + 1):
                part.add((px1, j))
        else:
            for i in range(min(px1, px2), max(px1, px2) + 1):
                part.add((i, py1))

    doors = {(int(d[0]), int(d[1])) for d in h.get('doors', [])}
    gates = {(int(g[0]), int(g[1])) for g in h.get('gate', [])}

    rows = []
    for j in range(y0, y1 + 1):
        row = []
        for i in range(x0, x1 + 1):
            c = (i, j)
            if c in gates:
                row.append('G')
            elif c in doors:
                row.append('D')
            elif c in part:
                row.append('#')
            else:
                wall = False
                if c not in interior:
                    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        if (i + di, j + dj) in interior:
                            wall = True
                            break
                row.append('#' if wall else ('.' if c in interior else ' '))
        rows.append(row)
    return rows, x0, y0


def lot_rect(h, pos):
    lot = h.get('lot', [0, 0, 0, 0])
    return (pos[0], pos[1],
            (int(lot[2]) - int(lot[0]) + 1) * TILE,
            (int(lot[3]) - int(lot[1]) + 1) * TILE)


def walls_cells(h, pos):
    rows, x0, y0 = grid_of(h)
    out = set()
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == '#':
                out.add(((pos[0] + (x0 + i) * TILE) // TILE,
                         (pos[1] + (y0 + j) * TILE) // TILE))
    return out


def lot_cells(h, pos):
    x, y, w, hh = lot_rect(h, pos)
    return {(x // TILE + i, y // TILE + j)
            for i in range(w // TILE) for j in range(hh // TILE)}


# --------------------------------------------------------------------------
# 主路：控制点 → Catmull-Rom（向心，alpha=0.5）→ 32px 采样 → 量化 → 夹紧
# --------------------------------------------------------------------------

CP_A1 = [
    (0,    1728, '西端：与 a3_1976 的取直路 [0,1728,4800,64] 同标高，换帧时西端不跳'),
    (320,  1664, '极大（北）：沈家车口。沈家院门 (272,752)，支路从路面北沿直接北上'),
    (576,  1728, '周家绕行口：路面回中线，周家支路从南沿下沉、向西绕院墙进南门'),
    (928,  1824, '极大（南，本帧最南）：周家以东没有宅基，路面下沿压到 1888 与南片田块北沿齐平'),
    (1456, 1664, '极大（北，本帧最北）：磨坊车口，全村唯一货运点，支路正对 (1456,848)'),
    (1888, 1728, '老槐红线西端：x∈[1888,2208] 内路面顶边不许高过 1728（树心 1664）'),
    (2208, 1728, '老槐红线东端'),
    (2528, 1664, '极大（北）：陆家车口，支路正对 (2512,1104)'),
    (3072, 1792, '陆家以东出村段：贴着南片田块北沿走，路面下沿 1856，与田留 32px'),
    (3520, 1728, '出村收平：x>3520 没有宅基也没有田埂，取直'),
    (4800, 1728, '东端：与 a3 同标高，直路出村'),
]

CP_A2 = [
    (0,    1728, '西端：与 a3 同标高'),
    (384,  1696, '极小（北）：沈家车口。1951 年沈家扩成 22×16、院门东移到 (592,784)'),
    (896,  1760, '极大（南）：周家绕行口（1951 年周家仍是 11×6 小院，院门仍在南沿）'),
    (1440, 1696, '极小（北）：磨坊车口（1951 年磨坊仍是 17×12，车口 (1456,848)）'),
    (1888, 1728, '老槐红线西端（1951 年老槐 r=64，树心仍是 1664）'),
    (2208, 1728, '老槐红线东端'),
    (2528, 1696, '极小（北）：陆家车口 (2512,1104)'),
    (3072, 1760, '极大（南）：出村段贴南片田块北沿'),
    (3520, 1728, '出村收平'),
    (4800, 1728, '东端'),
]

_ALPHA = 0.5


def _cr_point(p0, p1, p2, p3, u):
    def knot(t, a, b):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        return t + max(d, 1e-6) ** _ALPHA

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


def catmull_points(cps, density=64):
    pts = [(float(c[0]), float(c[1])) for c in cps]
    ext = [pts[0]] + pts + [pts[-1]]
    dense = []
    for k in range(len(pts) - 1):
        p0, p1, p2, p3 = ext[k], ext[k + 1], ext[k + 2], ext[k + 3]
        for s in range(density):
            dense.append(_cr_point(p0, p1, p2, p3, s / density))
    dense.append(pts[-1])
    return dense


def sample_y(dense, n):
    ys = []
    k = 0
    for i in range(n):
        x = i * TILE
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


def quantize_and_clamp(raw, n, *, red_window=True):
    ys = [int(round(v / TILE)) * TILE for v in raw]
    for _ in range(60):
        changed = False
        for i in range(1, n):
            if ys[i] > ys[i - 1] + TILE:
                ys[i] = ys[i - 1] + TILE
                changed = True
            elif ys[i] < ys[i - 1] - TILE:
                ys[i] = ys[i - 1] - TILE
                changed = True
        for i in range(n - 2, -1, -1):
            if ys[i] > ys[i + 1] + TILE:
                ys[i] = ys[i + 1] + TILE
                changed = True
            elif ys[i] < ys[i + 1] - TILE:
                ys[i] = ys[i + 1] - TILE
                changed = True
        if red_window:
            for i in range(n):
                x = i * TILE
                if RED_LINE[0] <= x <= RED_LINE[1] and ys[i] < RED_LINE_Y:
                    ys[i] = RED_LINE_Y
                    changed = True
        if not changed:
            break
    return ys


def build_main_road(cps):
    n = WORLD_W // TILE
    dense = catmull_points(cps)
    raw = sample_y(dense, n)
    ys = quantize_and_clamp(raw, n)
    rects = [[i * TILE, ys[i], TILE, ROAD_H] for i in range(n)]
    return ys, rects


# --------------------------------------------------------------------------
# 支路：32px 网格 Dijkstra
# --------------------------------------------------------------------------

DEST_LOT_COST = TILE  # 支路只能从院门进出，走自家院子是唯一路；不加惩罚（最短=最贴门）
TURN_COST = 3 * TILE  # 转弯罚分：只为让支路成直角，不影响可达性
DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def sid(i, j, d):
    return (j * NC + i) * 5 + d


def dijkstra(blocked, start):
    """带方向状态的 Dijkstra：转弯比直行贵 TURN_COST，出来就是直角折线。"""
    INF = float('inf')
    dist = [INF] * (NC * NR * 5)
    par = [-1] * (NC * NR * 5)
    s = sid(start[0], start[1], 4)
    dist[s] = 0
    pq = [(0, s)]
    while pq:
        c, u = heapq.heappop(pq)
        if c > dist[u]:
            continue
        k, d = divmod(u, 5)
        i, j = k % NC, k // NC
        for nd, (di, dj) in enumerate(DIRS):
            ni, nj = i + di, j + dj
            if not (0 <= ni < NC and 0 <= nj < NR):
                continue
            if (ni, nj) in blocked:
                continue
            step = TILE + (TURN_COST if d != 4 and nd != d else 0)
            w = dist[u] + step
            v = sid(ni, nj, nd)
            if w < dist[v]:
                dist[v] = w
                par[v] = u
                heapq.heappush(pq, (w, v))
    return dist, par


def trace(par, u):
    out = []
    while u >= 0:
        k, d = divmod(u, 5)
        out.append((k % NC, k // NC))
        u = par[u]
    return out[::-1]


def ytop_at(ys, x):
    if ys is None:                       # a3：整段平路
        return RED_LINE_Y
    return ys[max(0, min(len(ys) - 1, x // TILE))]


def plan_branch(fid, frame_shapes, house_ids, houses, ys, dest_id, dest_pos):
    """返回 dict（rects/endpoint/polyline/junction/length/ratio...）或抛异常。"""
    # 1. 阻塞格：主路带、非本宅的整块 lot、本宅的墙与室内、坝/老井/老槐
    blocked = set()
    for i in range(NC):
        t = ytop_at(ys, i * TILE)
        blocked.add((i, t // TILE))
        blocked.add((i, t // TILE + 1))

    dest_lot = set()
    for hid in house_ids:
        h = houses[hid]
        pos = dest_pos if hid == dest_id else house_pos(frame_shapes, hid)
        if hid == dest_id:
            dest_lot = lot_cells(h, pos)
            rows, x0, y0 = grid_of(h)
            for j, row in enumerate(rows):
                for i, ch in enumerate(row):
                    if ch in '#.D':
                        blocked.add(((pos[0] + (x0 + i) * TILE) // TILE,
                                     (pos[1] + (y0 + j) * TILE) // TILE))
        else:
            blocked |= lot_cells(h, pos)

    for s in frame_shapes:                       # 坝 / 老井 / 老槐 不进支路
        if s.get('label') in ('坝', '老井', '老槐') or s.get('label', '').startswith('老井'):
            if s.get('type') == 'rect':
                x, y, w, hh = s['rect']
                for i in range(x // TILE, (x + w) // TILE):
                    for j in range(y // TILE, (y + hh) // TILE):
                        blocked.add((i, j))
            elif s.get('type') == 'circle':
                cx, cy = s['center']
                r = s['radius']
                for i in range((cx - r) // TILE, (cx + r) // TILE + 1):
                    for j in range((cy - r) // TILE, (cy + r) // TILE + 1):
                        blocked.add((i, j))

    # 2. 起点：gate 格朝向主路的那个邻格
    h = houses[dest_id]
    gate = h['gate'][0]
    gpos = (dest_pos[0] + int(gate[0]) * TILE, dest_pos[1] + int(gate[1]) * TILE)
    gcell = (gpos[0] // TILE, gpos[1] // TILE)
    cands = [(gcell[0], gcell[1] + 1), (gcell[0], gcell[1] - 1),
             (gcell[0] + 1, gcell[1]), (gcell[0] - 1, gcell[1])]
    goal = None
    for c in cands:
        if c in blocked:
            continue
        if not (0 <= c[0] < NC and 0 <= c[1] < NR):
            continue
        goal = c
        break
    if goal is None:
        raise RuntimeError('%s 的 gate %s 四周全被占，做不出支路' % (dest_id, gate))

    dist, par = dijkstra(blocked, goal)

    # 3. 找接口格：贴着主路带的那一格，且第一步必须垂直于路（不许沿着路皮走）
    best = None
    road_cells = {(i, ytop_at(ys, i * TILE) // TILE + k) for i in range(NC) for k in (0, 1)}
    for i in range(NC):
        t = ytop_at(ys, i * TILE)
        for j, side in ((t // TILE - 1, 'north'), (t // TILE + 2, 'south')):
            if not (0 <= j < NR) or (i, j) in blocked:
                continue
            pick = None
            for dd in range(4):
                v = sid(i, j, dd)
                if dist[v] < (pick[0] if pick else float('inf')):
                    pick = (dist[v], dd)
            if pick is None or pick[0] == float('inf'):
                continue
            cells = trace(par, sid(i, j, pick[1]))[::-1]      # 接口格 -> 院门
            if len(cells) < 2 or cells[1][0] != cells[0][0]:
                continue                                  # 第一格就横着走 → 不要
            # 支路不许压主路
            if any(c in road_cells for c in cells):
                continue
            key = (pick[0],
                   abs(cells[-1][0] - cells[0][0]) + abs(cells[-1][1] - cells[0][1]))
            if best is None or key < best[0]:
                best = (key, cells, side, (i, j))
    if best is None:
        raise RuntimeError('%s 找不到贴主路的接口格' % dest_id)

    _, cells, side, jcell = best

    # 4. 格链 → rect 串（竖段拆成 32x32，横段合成一条）
    rects = []
    k = 0
    while k < len(cells):
        i0, j0 = cells[k]
        if k + 1 < len(cells) and cells[k + 1][1] == j0:      # 横段
            m = k
            while m + 1 < len(cells) and cells[m + 1][1] == j0:
                m += 1
            i1, i2 = min(i0, cells[m][0]), max(i0, cells[m][0])
            rects.append([i1 * TILE, j0 * TILE, (i2 - i1 + 1) * TILE, TILE])
            k = m + 1
        else:                                                 # 竖段
            m = k
            while m + 1 < len(cells) and cells[m + 1][0] == i0:
                m += 1
            j1, j2 = min(j0, cells[m][1]), max(j0, cells[m][1])
            step = 1 if cells[m][1] >= j0 else -1
            for jj in range(j0, cells[m][1] + step, step):
                rects.append([i0 * TILE, jj * TILE, TILE, TILE])
            k = m + 1

    # 5. 折线 + 端点：gate 格与世界边界共享边的中点（离 gate 中心 16px）
    t = ytop_at(ys, jcell[0] * TILE)
    start_pt = (jcell[0] * TILE + TILE // 2,
                t if side == 'north' else t + ROAD_H)
    if side == 'north':
        end_pt = (gpos[0] + TILE // 2, gpos[1])
    else:
        end_pt = (gpos[0] + TILE // 2, gpos[1] + TILE)

    # 拐点（方向变化处）
    corners = []
    for n in range(1, len(cells) - 1):
        a = (cells[n][0] - cells[n - 1][0], cells[n][1] - cells[n - 1][1])
        b = (cells[n + 1][0] - cells[n][0], cells[n + 1][1] - cells[n][1])
        if a != b:
            corners.append((cells[n][0] * TILE + TILE // 2,
                            cells[n][1] * TILE + TILE // 2))

    # 长度：整条支路footprint的折线长（各段都单调时 = |Δx|+|Δy|）
    xs = [c[0] for c in cells]
    js = [c[1] for c in cells]
    mono = (xs == sorted(xs) or xs == sorted(xs, reverse=True)) and \
           (js == sorted(js) or js == sorted(js, reverse=True))
    if mono:
        length = abs(end_pt[0] - start_pt[0]) + abs(end_pt[1] - start_pt[1])
    else:
        length = TILE * (len(cells) - 1)
    straight_end = math.hypot(end_pt[0] - start_pt[0], end_pt[1] - start_pt[1])
    gate_pt = (gpos[0] + TILE // 2, gpos[1] + TILE // 2)
    straight_gate = math.hypot(gate_pt[0] - start_pt[0], gate_pt[1] - start_pt[1])

    shapes = [{'type': 'rect', 'label': '路', 'road': True, 'rect': r} for r in rects]
    return {
        'id': dest_id,
        'side': side,
        'junction_cell': jcell,
        'junction_pt': start_pt,
        'endpoint': end_pt,
        'gate_center': gate_pt,
        'gate_err': math.hypot(end_pt[0] - gate_pt[0], end_pt[1] - gate_pt[1]),
        'length': length,
        'mono': mono,
        'corners': corners,
        'ratio_end': length / straight_end if straight_end else float('inf'),
        'ratio_gate': length / straight_gate if straight_gate else float('inf'),
        'rects': rects,
        'shapes': shapes,
        'lot_overlap': sum(1 for c in cells if c in dest_lot),
        'cells': cells,
    }


def house_pos(shapes, hid):
    for s in shapes:
        if s.get('type') == 'house' and s.get('id') == hid:
            return tuple(s['pos'])
    raise KeyError(hid)


# --------------------------------------------------------------------------
# 自检
# --------------------------------------------------------------------------

def road_shapes(fr):
    return [s for s in fr['shapes'] if s.get('label') == '路' and s.get('road')]


def check_road_rects(fr):
    bad = []
    for s in road_shapes(fr):
        x, y, w, h = s['rect']
        if h not in (TILE, ROAD_H):
            bad.append('h=%d 不在 {32,64}: %s' % (h, s['rect']))
        if x % TILE or y % TILE:
            bad.append('未对齐 32: %s' % (s['rect'],))
        if w % TILE:
            bad.append('w 不是 32 的倍数: %s' % (s['rect'],))
    return bad


def check_main_steps(ys):
    bad = []
    for i in range(1, len(ys)):
        if abs(ys[i] - ys[i - 1]) > TILE:
            bad.append('x=%d 与 x=%d 的 y 差 %d > 32' % ((i - 1) * TILE, i * TILE,
                                                        abs(ys[i] - ys[i - 1])))
    return bad


def check_red_line(ys):
    bad = []
    for i in range(len(ys)):
        x = i * TILE
        if RED_LINE[0] <= x <= RED_LINE[1] and ys[i] < RED_LINE_Y:
            bad.append('x=%d 的 y=%d 高过了红线 1728' % (x, ys[i]))
    cx, cy = OLD_WELL
    r = OLD_WELL_R
    for i in range(len(ys)):
        x = i * TILE
        if x < cx - r or x + TILE > cx + r:
            continue
        if ys[i] <= cy <= ys[i] + ROAD_H:
            bad.append('x=%d 的路面 y=%d..%d 盖住了老槐树心 (%d,%d)'
                       % (x, ys[i], ys[i] + ROAD_H, cx, cy))
    return bad


def check_extrema(ys):
    runs = []
    i = 0
    while i < len(ys):
        j = i
        while j + 1 < len(ys) and ys[j + 1] == ys[i]:
            j += 1
        runs.append((i, j, ys[i]))
        i = j + 1
    ext = []
    for k in range(1, len(runs) - 1):
        prev_y = runs[k - 1][2]
        cur = runs[k]
        nxt_y = runs[k + 1][2]
        if cur[2] > prev_y and cur[2] > nxt_y:
            ext.append(('极大', cur[0] * TILE, cur[2]))
        elif cur[2] < prev_y and cur[2] < nxt_y:
            ext.append(('极小', cur[0] * TILE, cur[2]))
    amps = [abs(ext[k + 1][2] - ext[k][2]) for k in range(len(ext) - 1)]
    ok = len(ext) >= 3 and len(set(amps)) >= 2
    return ok, ext, amps


def rects_overlap(a, b):
    return not (a[0] + a[2] <= b[0] or b[0] + b[2] <= a[0]
                or a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1])


def poly_bbox_overlap_rect(points, rect):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    bb = (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
    return rects_overlap(bb, rect)


def point_in_poly(p, poly):
    x, y = p
    inside = False
    n = len(poly)
    for k in range(n):
        x1, y1 = poly[k]
        x2, y2 = poly[(k + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xi:
                inside = not inside
    return inside


def check_house_separation(fr, hid_shapes):
    """a4：四宅互不重叠、离主路/山/田/路标够远。"""
    bad = []
    its = [(hid, tuple(pos)) for hid, pos in hid_shapes]
    return bad, its


def a4_zheng_check(a4, houses):
    bad = []
    h = houses['zheng_a4']
    rect = lot_rect(h, ZHENG_NEW_POS)
    x, y, w, hh = rect

    if x < 3400 or x + w > 4300:
        bad.append('x %d..%d 超出 3400..4300' % (x, x + w))
    if y < 2200 or y + hh > 2900:
        bad.append('y %d..%d 超出 2200..2900' % (y, y + hh))
    if y + hh > 3552:
        bad.append('压过 safe_bottom 3552')

    for s in a4['shapes']:
        if s.get('type') == 'house':
            if s.get('id') == 'zheng_a4':
                continue
            other = houses[s['id']]
            orect = lot_rect(other, tuple(s['pos']))
            if rects_overlap(rect, orect):
                bad.append('与 %s 的 lot 重叠 %s' % (s['id'], orect))
            gap = min(abs(orect[0] - (x + w)), abs(x - (orect[0] + orect[2])),
                      abs(orect[1] - (y + hh)), abs(y - (orect[1] + orect[3])))
            if math.hypot(max(0, max(x, orect[0]) - min(x + w, orect[0] + orect[2])),
                          max(0, max(y, orect[1]) - min(y + hh, orect[1] + orect[3]))) < 96:
                bad.append('与 %s 的间距 < 96px' % s['id'])
        elif s.get('type') == 'polygon' and s.get('label') == '山':
            if poly_bbox_overlap_rect(s['points'], rect):
                for p in ((x, y), (x + w, y), (x, y + hh), (x + w, y + hh),
                          (x + w // 2, y + hh // 2)):
                    if point_in_poly(p, s['points']):
                        bad.append('落在山里 %s' % (p,))
                        break
                else:
                    bad.append('山 bbox 与宅基 bbox 相交（需人工确认）')
        elif s.get('type') == 'rect':
            r = s['rect']
            if rects_overlap(rect, r):
                bad.append('与 %s rect %s 重叠' % (s.get('label') or s.get('type'), r))
                continue
            if s.get('label') == '路':
                gap = r[1] - (y + hh) if r[1] >= y + hh else y - (r[1] + r[3])
                if gap < 0:
                    bad.append('北墙/南墙贴到主路')
    return bad, rect


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

FRAME_HOUSES = {
    'a1_1926': ['mill_a1', 'shen_a1', 'zhou_house', 'lu_house'],
    'a2_1951': ['mill_a2', 'shen_a2', 'zhou_a2', 'lu_a2'],
    'a3_1976': ['mill_a3', 'shen_a3', 'zhou_a3', 'lu_a3'],
}


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    return json.loads(raw), raw


def frame_by_id(data, fid):
    for fr in data['frames']:
        if fr['id'] == fid:
            return fr
    raise KeyError(fid)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', action='store_true')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args(argv[1:])

    data, raw = load_json(FRAMES_PATH)
    houses_list, _ = load_json(HOUSES_PATH)
    houses = {h['id']: h for h in houses_list}

    # 往返自检：重新 dump 必须和原文逐字节一样
    dump = json.dumps(data, indent=2, ensure_ascii=False)
    tail_nl = raw.endswith('\n')
    rt = dump + ('\n' if tail_nl else '')
    print('roundtrip=%s (tail_newline=%s, bytes=%d)'
          % ('OK' if rt == raw else 'MISMATCH', tail_nl, len(raw)))
    if rt != raw:
        print('!! 重新 dump 和原文不一致，先别写盘')
        return 2

    if args.snapshot:
        base = {'protected': canon(protected(data)),
                'raw_sha256': hashlib.sha256(raw.encode('utf-8')).hexdigest()}
        with open(BASELINE_PATH, 'w', encoding='utf-8') as f:
            json.dump(base, f, indent=2, ensure_ascii=False)
        print('baseline protected=%s raw=%s' % (base['protected'], base['raw_sha256'][:16]))
        return 0

    # ---- 算新数据（只在内存里） ----
    plans = {}
    for fid, road_cps in (('a1_1926', CP_A1), ('a2_1951', CP_A2), ('a3_1976', None)):
        fr = frame_by_id(data, fid)
        ids = FRAME_HOUSES[fid]
        if road_cps is None:
            ys = None
            main = None
        else:
            ys, main = build_main_road(road_cps)
        branches = []
        for hid in ids:
            pos = house_pos(fr['shapes'], hid)
            branches.append(plan_branch(fid, fr['shapes'], ids, houses, ys, hid, pos))
        plans[fid] = {'ys': ys, 'main': main, 'branches': branches}

    # ---- 自检 ----
    fails = 0

    print('\n=== 1. 受保护片段 ===')
    if os.path.exists(BASELINE_PATH):
        with open(BASELINE_PATH, 'r', encoding='utf-8') as f:
            base = json.load(f)
        now = canon(protected(data))
        same = (now == base['protected'])
        print('protected %s -> %s   [%s]' % (base['protected'], now,
                                             'OK' if same else 'FAIL'))
        if not same:
            fails += 1
    else:
        print('没有 baseline（先跑 --snapshot），这条按 FAIL 记')
        fails += 1

    # ---- 7. 落盘一致性：文件里的路 rect 必须就是这次算出来的那批 ----
    if not args.write:
        print('\n=== 7. 落盘一致性（文件里的路 == 本次算出的路）===')
        bad7 = []
        for fid in ('a1_1926', 'a2_1951', 'a3_1976'):
            p = plans[fid]
            got = [s['rect'] for s in road_shapes(frame_by_id(data, fid))]
            got_main = [r for r in got if r[3] == ROAD_H]
            got_br = [r for r in got if r[3] != ROAD_H]
            want_main = p['main'] if p['main'] else [[0, RED_LINE_Y, 4800, ROAD_H]]
            want_br = []
            for br in p['branches']:
                want_br += br['rects']
            if sorted(got_main) != sorted(want_main):
                bad7.append('%s 主路 %d 块 != 计划 %d 块'
                            % (fid, len(got_main), len(want_main)))
            elif sorted(got_br) != sorted(want_br):
                bad7.append('%s 支路 %d 块 != 计划 %d 块'
                            % (fid, len(got_br), len(want_br)))
            else:
                print('%s 主路 %d 块 + 支路 %d 块，与计划逐块相同'
                      % (fid, len(got_main), len(got_br)))
        print('7. 落盘一致性: %s' % ('OK' if not bad7 else 'FAIL'))
        for b in bad7:
            print('   - ' + b)
        fails += bool(bad7)

    for fid in ('a1_1926', 'a2_1951', 'a3_1976'):
        p = plans[fid]
        fr = frame_by_id(data, fid)
        print('\n=== %s（主路 %s 块 / 支路 %d 条）==='
              % (fid, ('%d' % len(p['main'])) if p['main'] else '1', len(p['branches'])))

        # 2. rect 规格 + 相邻步长
        bad = check_road_rects(fr)
        if p['ys'] is not None:
            bad += check_main_steps(p['ys'])
        print('2. rect 规格/步长: %s' % ('OK' if not bad else 'FAIL'))
        for b in bad[:8]:
            print('   - ' + b)
        fails += bool(bad)

        # 3. 老槐红线
        if p['ys'] is not None:
            bad = check_red_line(p['ys'])
        else:
            bad = []
        print('3. 老槐红线: %s' % ('OK' if not bad else 'FAIL'))
        for b in bad[:8]:
            print('   - ' + b)
        fails += bool(bad)

        # 4. 支路端点
        bad = []
        for br in p['branches']:
            if br['gate_err'] > 32:
                bad.append('%s 端点离 gate 中心 %.1f > 32' % (br['id'], br['gate_err']))
        print('4. 支路端点 ≤32px: %s' % ('OK' if not bad else 'FAIL'))
        for b in bad:
            print('   - ' + b)
        fails += bool(bad)

        # 5. 支路 vs 房基（自家院子/他人 lot/任何墙）
        bad = []
        for br in p['branches']:
            for hid in FRAME_HOUSES[fid]:
                h = houses[hid]
                pos = house_pos(fr['shapes'], hid)
                wc = walls_cells(h, pos)
                hit = len([c for c in br['cells'] if c in wc])
                if hit:
                    bad.append('%s 的支路压到 %s 的墙 %d 格' % (br['id'], hid, hit))
                if hid != br['id']:
                    lo = len([c for c in br['cells'] if c in lot_cells(h, pos)])
                    if lo:
                        bad.append('%s 的支路进了 %s 的院子 %d 格' % (br['id'], hid, lo))
        print('5. 支路 vs 房基: %s' % ('OK' if not bad else 'FAIL'))
        for b in bad:
            print('   - ' + b)
        fails += bool(bad)

        # 附带：绕行比 §3-2（≤1.4）+ 接口贴合 §3-3
        bad2 = []
        for br in p['branches']:
            if br['ratio_gate'] > 1.4 + 1e-9:
                bad2.append('%s 总长/到格心直线 = %.2f > 1.4' % (br['id'], br['ratio_gate']))
            first = br['rects'][0]
            t = ytop_at(p['ys'], first[0])
            flush = (first[1] + first[3] == t or first[1] == t + ROAD_H)
            if not flush:
                bad2.append('%s 的第一块没贴主路边缘: %s (ytop=%d)' % (br['id'], first, t))
        print('5b. 绕行比 ≤1.4 / 接口贴合: %s' % ('OK' if not bad2 else 'FAIL'))
        for b in bad2:
            print('   - ' + b)
        fails += bool(bad2)

        # 6. 主路极值
        if p['ys'] is not None:
            ok, ext, amps = check_extrema(p['ys'])
            print('6. 主路极值: %s  极值 %d 处 %s' % ('OK' if ok else 'FAIL', len(ext),
                                                    [(e[0], e[1], e[2]) for e in ext]))
            print('   相邻振幅 %s  %s' % (amps, '不全相等' if len(set(amps)) >= 2 else '!!全相等'))
            if not ok:
                fails += 1
        else:
            print('6. 主路极值: SKIP（a3 是一条直路，任务书要求不动）')

        # 附：支路表
        for br in p['branches']:
            print('   支路 %-10s 接口(%d,%d) %s 拐点%s 端点 %s  gate %s err=%.0f 长 %.0f  '
                  '长/格心直线 %.2f (对端点 %.2f) 自家院子 %d 格'
                  % (br['id'], br['junction_pt'][0], br['junction_pt'][1], br['side'],
                     br['corners'] or '无', br['endpoint'], br['gate_center'],
                     br['gate_err'], br['length'], br['ratio_gate'], br['ratio_end'],
                     br['lot_overlap']))

    # a4 zheng_a4
    print('\n=== a4_2001 zheng_a4 ===')
    bad, rect = a4_zheng_check(frame_by_id(data, 'a4_2001'), houses)
    print('新位置 %s -> lot %s  [%s]' % (ZHENG_NEW_POS, rect, 'OK' if not bad else 'FAIL'))
    for b in bad:
        print('   - ' + b)
    fails += bool(bad)

    print('\nTOTAL FAILS = %d' % fails)
    if not (args.check or args.write):
        print('（只校验，不写盘；加 --write 生效）')
        return 0 if fails == 0 else 1

    if args.write:
        if fails:
            print('自检没过，拒绝写盘')
            return 1
        for fid in ('a1_1926', 'a2_1951', 'a3_1976'):
            p = plans[fid]
            fr = frame_by_id(data, fid)
            new_main = ([{'type': 'rect', 'label': '路', 'road': True, 'rect': r}
                         for r in p['main']] if p['main']
                        else [s for s in fr['shapes']
                              if s.get('label') == '路' and s.get('road')])
            new_branch = [s for br in p['branches'] for s in br['shapes']]
            shapes = []
            done = False
            for s in fr['shapes']:
                if s.get('label') == '路' and s.get('road'):
                    if not done:
                        shapes.extend(new_main)
                        shapes.extend(new_branch)
                        done = True
                    continue
                shapes.append(s)
            if not done:
                shapes.extend(new_main)
                shapes.extend(new_branch)
            fr['shapes'] = shapes

        for s in frame_by_id(data, 'a4_2001')['shapes']:
            if s.get('type') == 'house' and s.get('id') == 'zheng_a4':
                s['pos'] = list(ZHENG_NEW_POS)

        out = json.dumps(data, indent=2, ensure_ascii=False) + ('\n' if tail_nl else '')
        with open(FRAMES_PATH, 'w', encoding='utf-8', newline='\n') as f:
            f.write(out)
        print('WROTE %s (%d bytes)' % (FRAMES_PATH, len(out)))
        for fr in data['frames']:
            print('   %-9s shapes=%d road=%d' % (fr['id'], len(fr['shapes']),
                                                 len(road_shapes(fr))))
        print('protected after = %s' % canon(protected(data)))
    return 0 if fails == 0 else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))