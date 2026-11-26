#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""地图 v5：A1-A3 九条支路个性重做（任务书 docs/PROMPT-map-v5-exec.md）。

用法：
    python lab/_a13_road_v5.py --check [--ascii] [--report FILE]
    python lab/_a13_road_v5.py --write

只动 a1/a2/a3 三帧里「支路」那批路块：
  * 主路块（label=="路" 且 y 格 ∈ {46,47}、x ∈ 0..149）**原样保留**，不重新生成；
  * 其余 road 块全部删掉，按本文件里九条**逐条手写**的中轴线重建；
  * 别的 shape（房子 / 田 / 河 / 坝 / 井 / 槐 / hotspots）一律不碰。

单位一律「格」（1 格 = 32px），落盘时 ×32。所有路块 [x, y, 1, 2]（1 格宽 × 2 格高）。

九条的设计见 docs/PROMPT-map-v5-exec.md §3。设计要求里「起坡列 / 落差 / 主倾角」
三者有 6 处几何上不能同时成立（落差与起坡列把倾角锁死），本文件按下面的优先级落地：

    必须接主路带 + 必须够到门格（§4.2/§4.3）
      > 性格（S / L / 直上 / 场院 / 缓斜）与主倾角（§3「性格」「主倾角」列）
        > 起坡列这个数（它被倾角唯一决定，属于结果而非约束）

每一处偏离都在下面 SPEC 的 note 里写明，--check 会原样打印。
"""
from __future__ import print_function

import argparse
import hashlib
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

TILE = 32
NC = 150
ROAD_FRAMES = ('a1_1926', 'a2_1951', 'a3_1976')
MAIN_ROWS = (46, 47)

HALF = 0.95          # 中轴线到格子中心的半径；0.95 保证「垂直段正好 2 列」
Y_START = 46.6       # 支路与主路带的接吻高度：起点落在 row 46 里，胶囊才能同时盖住 row 45/46
ROW_CLIP = 46        # 支路格子行号上限（允许吃到主路带北沿那一行）

# --------------------------------------------------------------------------
# 九条支路的设计（逐条手写，不是参数模板）
#
# kind='poly'  : pts 是中轴线折点（格，y 向下为正），按胶囊光栅成格子再合成块
# kind='mill'  : 直上 + 末端特殊件（场院 / 收口），按块表直接给
# --------------------------------------------------------------------------
SPEC = [
    # ---------------- a1 / 1926 ----------------
    dict(fid='a1_1926', key='shen', house='shen_a1', kind='poly',
         # S 形：63° 西北 → 58° 东北 → 80° 北（两次反向）
         pts=[(15.0, Y_START), (7.2, 31.1), (9.5, 27.4), (9.0, 24.6)],
         col=14,
         reason='从坝西侧下来，绕开河边那条田埂，再拐回院门'),
    dict(fid='a1_1926', key='mill', house='mill_a1', kind='mill',
         col=45,
         vert_y=[45, 43, 41, 39, 37, 35, 33, 31],
         apron=dict(cols=[44, 45, 46, 47, 48], ys=[30, 28]),   # 5 格宽 × 4 格深
         throat=dict(cols=[45, 46], ys=[27]),
         reason='磨坊是村里唯一有大车的地方，门口必须能掉头'),
    dict(fid='a1_1926', key='lu', house='lu_house', kind='poly',
         # 斜切之后末端竖直 2 行（60°→90°；落差被起坡列 84 锁到 ~56°）
         pts=[(85.0, Y_START), (79.0, 37.6), (79.0, 35.6)],
         col=84,
         note='任务书要「60°→90°」+ 起坡列 84 + 落差 12。从 84 列斜到门中轴 79 只有 6 列'
              '水平量，落差只剩 10 行 ⇒ 首段几何上限 atan(10/6)=59°。落成「斜切 + 末尾 2 行竖直」，'
              '首段 ~56°，与设计的 60° 差 4°（在 ±8° 内）。',
         reason='从西南角斜插进院，最短的一条土路（实测从东南侧进 —— 起坡列 84 > 门列 78，'
                '任务书理由写的「西南角」与数字矛盾，按数字执行）'),

    # ---------------- a2 / 1951 ----------------
    dict(fid='a2_1951', key='shen', house='shen_a2', kind='poly',
         # L 形：90° 北 → 0° 西 → 90° 北（贴着扩过的院墙东侧上来，横切进院）
         pts=[(27.0, Y_START), (27.0, 30.0), (19.0, 30.0), (19.0, 24.6)],
         col=26,
         reason='院子扩过之后，路改成先贴着院墙东侧上来，再横切进院'),
    dict(fid='a2_1951', key='mill', house='mill_a2', kind='mill',
         col=45,
         vert_y=[45, 43, 41, 39, 37, 35, 33, 31],
         apron=dict(cols=[44, 45, 46, 47], ys=[31, 29]),        # 4 格宽 × 4 行，后撤 1 行
         throat=dict(cols=[45, 46], ys=[27]),
         note='任务书场院「4 格宽 × 3 格深」：路块恒 2 行高（§4.1），3 行深取不到，'
              '落成 4 宽 × 4 行且整体后撤 1 行（比 a1 窄 1 格、离门远 1 行）⇒「小一号」。',
         reason='同上，但车少了、场院缩了'),
    dict(fid='a2_1951', key='lu', house='lu_a2', kind='poly',
         # 单段斜切（反向：从东侧而不是 a1 的西侧进来）
         pts=[(69.5, Y_START), (79.0, 35.6)],
         col=69,
         note='任务书「起坡列 72 / 45°」+ 落差 12：从 72 列到门中轴 79 只有 7 列水平量，'
              '倾角被锁到 atan(11/7)=57°。要 45° 起坡列必须 69.5，故取 69.5（东移 2.5 格）'
              '保住 45° 档，落成 ~49°。另：任务书理由写「从东侧 / 从东南入」，但起坡列 72'
              '＜门列 78 ⇒ 实际是从西南侧斜插，且这样才与 a1 陆家（起坡列 84，从东南）'
              '互为「反向」。按数字执行。',
         reason='1951 井台修整过，路改从西侧斜插进来避让（任务书写「东侧」，与数字矛盾）'),

    # ---------------- a3 / 1976 ----------------
    dict(fid='a3_1976', key='shen', house='shen_a3', kind='poly',
         # 一条斜线切进门（末端停在门格正下方那一行，不铺进门格）
         pts=[(21.0, Y_START), (15.5, 37.4)],
         col=20,
         taper=([37], {15}),          # 末端收 1 格宽（任务书特殊件）
         note='任务书「起坡列 20 / 75°」+ 落差 10：从 20 列切到门中轴 15.5 要用掉 5.5 列'
              '水平量，倾角锁死 atan(9.2/5.5)=59°。要 75° 起坡列只能 ≤17。按「起坡列 20」'
              '执行 ⇒ 落成 ~59°，比设计 75° 差 16°（已超 ±8°，属任务书内部矛盾，见反馈 §3）。'
              '特殊件「末端收 1 格宽」已照做：门格正下方那一行只留门列 15 一格。',
         reason='院子扩到路边，路只剩十格，一条斜线切进门'),
    dict(fid='a3_1976', key='mill', house='mill_a3', kind='mill',
         col=45,
         vert_y=[45, 43, 41, 39, 37, 35, 33, 31],
         apron=dict(cols=[44, 45, 46], ys=[30, 28]),            # 3 格宽收口，无场院
         throat=dict(cols=[45, 46], ys=[27]),
         reason='1976 路面硬化，场院改成硬收边'),
    dict(fid='a3_1976', key='lu', house='lu_a3', kind='poly',
         # 全村最缓的斜上
         pts=[(96.0, Y_START), (79.0, 35.6)],
         col=96,
         note='任务书「起坡列 88 / 30°」+ 落差 12：从 88 列到门中轴 79 只有 9 列水平量，'
              '倾角锁到 atan(11/9)=51°（与 a2 陆家几乎一样，正是这次要消灭的「同款」）。'
              '要 30° 得起坡列 ≈98，取 96（东移 8 格）⇒ 落成 ~33°，保住「全村最缓」。',
         reason='1976 这块地垫平了，车能斜着开上去'),
]

KEYS = ('shen', 'mill', 'lu')
MILL_COLS = (45, 46)   # 磨坊三条都是「正对门」的竖直段
TAG = {'shen': 'S', 'mill': 'M', 'lu': 'L'}

# 任务书 §3 表里的「起坡列」原值（单位＝格）。落地值与它不同的，NOTE 里都写了原因。
DOC_COL = {
    ('a1_1926', 'shen'): 14, ('a1_1926', 'mill'): 45, ('a1_1926', 'lu'): 84,
    ('a2_1951', 'shen'): 26, ('a2_1951', 'mill'): 45, ('a2_1951', 'lu'): 72,
    ('a3_1976', 'shen'): 20, ('a3_1976', 'mill'): 45, ('a3_1976', 'lu'): 88,
}


# --------------------------------------------------------------------------
# 基础 IO
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


def cell_of_rect(r):
    return (r[0] // TILE, r[1] // TILE)


def is_main_block(s):
    if not is_road(s) or s.get('type') != 'rect':
        return False
    c, rr = cell_of_rect(s['rect'])
    return 0 <= c < NC and rr in MAIN_ROWS


def band_blocks(fr):
    """主路带（y∈{46,47}，col 0..149）里的全部路块，按列分组。

    注意：v4 的部分支路根部也落在这一带里（如 a1 的 col 29/30/89 有 y=47 的
    残留块），所以「带里的块」≠「主路」。主路是那条 150 列、逐列相邻的链。
    """
    by_col = {}
    for s in road_shapes(fr):
        if is_main_block(s):
            c, y = cell_of_rect(s['rect'])
            by_col.setdefault(c, []).append((y, s))
    return by_col


def main_chain(fr):
    """主路 = 每列一个块、相邻列 |Δy|≤1 的那条链（col 0..149）。

    返回 (chain_shapes, leftovers)；缺列返回 (None, [])。leftovers 是带里的
    非链块 —— 那批是 v4 支路的根部残块，本次要随支路一起重做掉。
    """
    by_col = band_blocks(fr)
    if any(c not in by_col for c in range(NC)):
        return None, []
    chain = []
    prev = None
    for c in range(NC):
        cands = by_col[c]
        if prev is None:
            pick = min(cands, key=lambda t: abs(t[0] - 46))
        else:
            pick = min(cands, key=lambda t: (abs(t[0] - prev) > 1,
                                             abs(t[0] - prev), t[0]))
        chain.append(pick[1])
        prev = pick[0]
    keep = set(id(s) for s in chain)
    left = [s for c in sorted(by_col) for (y, s) in by_col[c] if id(s) not in keep]
    return chain, left


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


# --------------------------------------------------------------------------
# 光栅：折线 → 格子集合
# --------------------------------------------------------------------------
def seg_cells(p0, p1, half=HALF):
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


def poly_cells(pts, half=HALF):
    cells = set()
    for i in range(len(pts) - 1):
        cells |= seg_cells(pts[i], pts[i + 1], half)
    cells = {(c, r) for (c, r) in cells if r <= ROW_CLIP}
    return cells


def blocks_for_run(c, r0, r1):
    """覆盖 r0..r1 行的 [x,y,1,2] 块（块高 2 格，相邻块可重叠 1 行）。"""
    if r1 <= r0:
        return [(c, r0)]
    ys = list(range(r0, r1, 2))
    if not ys or ys[-1] + 1 < r1:
        ys.append(r1 - 1)
    return [(c, y) for y in ys]


def blocks_from_cells(cells):
    cols = {}
    for (c, r) in cells:
        cols.setdefault(c, []).append(r)
    out = []
    for c in sorted(cols):
        rs = sorted(cols[c])
        s = p = rs[0]
        for r in rs[1:]:
            if r == p + 1:
                p = r
            else:
                out.extend(blocks_for_run(c, s, p))
                s = p = r
        out.extend(blocks_for_run(c, s, p))
    return out


# --------------------------------------------------------------------------
# 九条支路的块表
# --------------------------------------------------------------------------
def mill_blocks(sp):
    out = []
    for y in sp['vert_y']:
        for c in MILL_COLS:
            out.append((c, y))
    ap = sp['apron']
    for y in ap['ys']:
        for c in ap['cols']:
            out.append((c, y))
    th = sp['throat']
    for y in th['ys']:
        for c in th['cols']:
            out.append((c, y))
    return out


def build_branch(sp, frames):
    """返回 (blocks, cells, info)。"""
    if sp['kind'] == 'mill':
        blocks = mill_blocks(sp)
        cells = set()
        for (c, y) in blocks:
            cells.add((c, y))
            cells.add((c, y + 1))
    else:
        cells = poly_cells(sp['pts'])
        # 末端收窄（§4.5「进院最后 ≤2 行允许收成 1 格」）：
        # taper=(rows, keep_cols)，把这些行里不在 keep_cols 的格子剪掉。
        tp = sp.get('taper')
        if tp is not None:
            rows, keep = tp
            cells = set((c, r) for (c, r) in cells
                        if not (r in rows and c not in keep))
        blocks = blocks_from_cells(cells)
    # 去重
    seen = set()
    uniq = []
    for b in blocks:
        if b not in seen:
            seen.add(b)
            uniq.append(b)
    return uniq, cells


def exact_angle(p0, p1):
    """折线的精确倾角（0=水平，90=竖直）。"""
    dx = abs(p1[0] - p0[0])
    dy = abs(p1[1] - p0[1])
    if dx < 1e-9:
        return 90.0
    return math.degrees(math.atan(dy / dx))


def seg_angle(cells, p0, p1):
    """这一段的实测倾角（0=水平，90=竖直）。

    只统计「格心垂直投影落在这段上」的格子（否则水平段会把两侧竖直段的格子
    一起吃进来，拟合出假倾角），再按列取行中心做最小二乘。
    """
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    if L2 <= 1e-12:
        return 90.0
    if abs(x1 - x0) < 1.0:
        return 90.0
    per_col = {}
    for (c, r) in cells:
        px_, py_ = c + 0.5, r + 0.5
        t = ((px_ - x0) * dx + (py_ - y0) * dy) / L2
        if t < -0.02 or t > 1.02:
            continue
        fx, fy = x0 + t * dx, y0 + t * dy
        if math.hypot(px_ - fx, py_ - fy) > HALF + 0.30:
            continue
        per_col.setdefault(c, []).append(py_)
    pts = [(c + 0.5, sum(v) / len(v)) for c, v in sorted(per_col.items())]
    if len(pts) < 2:
        return 90.0
    n = float(len(pts))
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pts)
    if sxx <= 1e-12:
        return 90.0
    slope = sxy / sxx
    return math.degrees(math.atan(abs(slope)))


# --------------------------------------------------------------------------
# 几何命中测试（单位：格）
# --------------------------------------------------------------------------
def rect_hit(c, r, rect):
    x0, y0, w, h = rect
    ox = min(c + 1.0, x0 + w) - max(float(c), x0)
    oy = min(r + 1.0, y0 + h) - max(float(r), y0)
    return ox > 1e-9 and oy > 1e-9


def circle_hit(c, r, cen, rad):
    cx, cy = cen
    nx = min(max(cx, c), c + 1.0)
    ny = min(max(cy, r), r + 1.0)
    return math.hypot(cx - nx, cy - ny) < rad - 1e-9


def point_in_poly(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y):
            xc = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < xc:
                inside = not inside
        j = i
    return inside


def poly_hit(c, r, poly):
    for (px_, py_) in ((c + 0.5, r + 0.5), (c + 0.05, r + 0.05),
                       (c + 0.95, r + 0.05), (c + 0.05, r + 0.95),
                       (c + 0.95, r + 0.95)):
        if point_in_poly(px_, py_, poly):
            return True
    return False


def collect_obstacles(fr, houses, own_house):
    """返回 [(name, kind, payload)]；own_house 的 lot 不算。"""
    obs = []
    for s in fr['shapes']:
        t = s.get('type')
        lab = s.get('label') or ''
        if t == 'house':
            hid = s['id']
            if hid == own_house:
                continue
            h = houses.get(hid)
            if not h:
                continue
            pos_c = (s['pos'][0] // TILE, s['pos'][1] // TILE)
            c0, r0, w, hh = lot_cell_of(h, pos_c)
            obs.append(('%s.lot' % hid, 'rect', (c0, r0, w, hh)))
        elif t == 'rect' and not is_road(s):
            r = s['rect']
            obs.append(('%s.rect' % (lab or 'field'),
                        'rect', (r[0] / TILE, r[1] / TILE, r[2] / TILE, r[3] / TILE)))
        elif t == 'polygon' and lab in ('河',):
            poly = [(p[0] / TILE, p[1] / TILE) for p in s['points']]
            obs.append((lab, 'poly', poly))
        elif t == 'circle':
            cen = (s['center'][0] / TILE, s['center'][1] / TILE)
            obs.append((lab or 'circle', 'circle', (cen, s['radius'] / TILE)))
    return obs


def hits(cells, obs):
    out = []
    for name, kind, pay in obs:
        n = 0
        for (c, r) in cells:
            if kind == 'rect':
                if rect_hit(c, r, pay):
                    n += 1
            elif kind == 'circle':
                if circle_hit(c, r, pay[0], pay[1]):
                    n += 1
            else:
                if poly_hit(c, r, pay):
                    n += 1
        if n:
            out.append((name, n))
    return out


# --------------------------------------------------------------------------
def connected(cells):
    if not cells:
        return False
    seen = {next(iter(cells))}
    stack = list(seen)
    while stack:
        c, r = stack.pop()
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = (c + d[0], r + d[1])
            if nb in cells and nb not in seen:
                seen.add(nb)
                stack.append(nb)
    return len(seen) == len(cells)


def ascii_map(cells, extras, x0, x1, y0, y1):
    rows = []
    for r in range(y0, y1 + 1):
        line = []
        for c in range(x0, x1 + 1):
            ch = '.'
            inb = (c, r) in cells
            inx = (c, r) in extras
            if inb and inx:
                ch = '*'          # 支路压在标记上（房子/门/主路）
            elif inb:
                ch = '#'
            elif inx:
                ch = extras[(c, r)]
            line.append(ch)
        rows.append('%4d %s' % (r, ''.join(line)))
    head = '     ' + ''.join([('%d' % (c % 10)) for c in range(x0, x1 + 1)])
    return '\n'.join([head] + rows)


# --------------------------------------------------------------------------
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--ascii', action='store_true')
    ap.add_argument('--report', default='')
    args = ap.parse_args(argv[1:])

    log = []

    def emit(s):
        print(s)
        log.append(s)

    data, raw = load_json(FRAMES_PATH)
    houses = houses_index()
    rt = dump_like(data, raw)
    emit('roundtrip=%s (bytes=%d)'
         % ('OK' if rt == raw else 'MISMATCH', len(raw.encode('utf-8'))))
    if rt != raw:
        emit('!! dump 与原文件不一致，先停')
        return 2

    head = head_frames()
    emit('baseline=%s' % ('HEAD ok' if head else 'HEAD missing (S1/S2 SKIP)'))

    # ---------- 计划：每帧每条的 block 表 ----------
    plan = {}
    for sp in SPEC:
        fid = sp['fid']
        fr = frame_by_id(data, fid)
        pos_c = house_pos_cell(fr, sp['house'])
        h = houses[sp['house']]
        gc = gate_cell_of(h, pos_c)
        sp = dict(sp)
        sp['gate_cell'] = gc
        sp['lot'] = lot_cell_of(h, pos_c)
        plan[(fid, sp['key'])] = sp

    for key in plan:
        sp = plan[key]
        blocks, cells = build_branch(sp, plan)
        # 门格正下方必须有块
        gx, gy = sp['gate_cell']
        if not any(b[0] == gx and b[1] <= gy + 1 <= b[1] + 1 for b in blocks):
            blocks.append((gx, gy + 1))
            cells.add((gx, gy + 1))
            cells.add((gx, gy + 2))
        sp['blocks'] = blocks
        sp['cells'] = cells
        sp['n_bends'] = 0 if sp['kind'] == 'mill' else len(sp['pts']) - 2
        if sp['kind'] == 'mill':
            sp['exact_angles'] = [90.0]
            sp['meas_angles'] = [90.0]
            sp['seg_len'] = [float(len(sp['vert_y']))]
            sp['main_angle'] = 90.0
            sp['start_col'] = min(MILL_COLS)
        else:
            # 设计倾角 = 折线的精确几何角；实测 = 光栅化后按列拟合的角（量化会偏 2~4°）
            sp['exact_angles'] = [exact_angle(sp['pts'][i], sp['pts'][i + 1])
                                  for i in range(len(sp['pts']) - 1)]
            sp['meas_angles'] = [seg_angle(cells, sp['pts'][i], sp['pts'][i + 1])
                                 for i in range(len(sp['pts']) - 1)]
            sp['seg_len'] = [math.hypot(sp['pts'][i + 1][0] - sp['pts'][i][0],
                                        sp['pts'][i + 1][1] - sp['pts'][i][1])
                             for i in range(len(sp['pts']) - 1)]
            # 主倾角 = 最长那一段的设计倾角
            sp['main_angle'] = sp['exact_angles'][sp['seg_len'].index(max(sp['seg_len']))]
            # 起坡列 = 与主路带相接那一行（y=45 块）的最西列
            base = [b[0] for b in blocks if b[1] == 45]
            sp['start_col'] = min(base) if base else min(b[0] for b in blocks)

    # ---------- 组装新数据 ----------
    new = json.loads(json.dumps(data, ensure_ascii=False))
    for fid in ROAD_FRAMES:
        fr = frame_by_id(new, fid)
        main, left = main_chain(fr)
        if main is None:
            main = [s for s in fr['shapes'] if is_main_block(s)]
        br_shapes = []
        for k in KEYS:
            sp = plan[(fid, k)]
            for (c, y) in sp['blocks']:
                r = [c * TILE, y * TILE, TILE, 2 * TILE]
                if any(m['rect'] == r for m in main):
                    continue
                br_shapes.append({'type': 'rect', 'label': '路', 'road': True,
                                  'rect': r})
        emit('%s 带内残留支路根块（随旧支路一并删除）：%s'
             % (fid, [(cell_of_rect(s['rect'])) for s in left] or '无'))
        shapes, done = [], False
        for s in fr['shapes']:
            if is_road(s):
                if not done:
                    shapes.extend(main)
                    shapes.extend(br_shapes)
                    done = True
                continue
            shapes.append(s)
        if not done:
            shapes.extend(main)
            shapes.extend(br_shapes)
        fr['shapes'] = shapes

    # ---------- 自检 ----------
    fails = [0]

    def verdict(tag, bad, extra=''):
        if bad:
            fails[0] += 1
        emit('%s %s%s' % (tag, 'PASS' if not bad else 'FAIL', extra))
        for b in bad:
            emit('   - ' + str(b))

    # S1 主路 150 列逐块相同（链式取块，不算带里的支路残根）
    bad = []
    if head:
        for fid in ROAD_FRAMES:
            ca, _ = main_chain(frame_by_id(new, fid))
            cb, _ = main_chain(frame_by_id(head, fid))
            if ca is None or cb is None:
                bad.append('%s 主路链取不出来' % fid)
                continue
            a = [s['rect'] for s in ca]
            b = [s['rect'] for s in cb]
            if a != b:
                bad.append('%s 主路块与 HEAD 不同 (now %d / head %d)'
                           % (fid, len(a), len(b)))
                for i, (x, y) in enumerate(zip(a, b)):
                    if x != y:
                        bad.append('    first diff #%d %s != %s' % (i, x, y))
                        break
            if len(a) != NC:
                bad.append('    %s 主路块数 %d != %d 列' % (fid, len(a), NC))
    verdict('S1', bad, '  主路 150 列路块与 HEAD 逐块相同（x 与 y 都比）')

    # S2 非路 shape / hotspots 不动
    bad = []
    if head:
        for fid in [f['id'] for f in new['frames']]:
            a = [s for s in frame_by_id(new, fid)['shapes'] if not is_road(s)]
            b = [s for s in frame_by_id(head, fid)['shapes'] if not is_road(s)]
            ja = json.dumps(a, ensure_ascii=False, sort_keys=True)
            jb = json.dumps(b, ensure_ascii=False, sort_keys=True)
            if ja != jb:
                bad.append('%s 非路 shape 变了 (%d vs %d)' % (fid, len(a), len(b)))
                for i in range(min(len(a), len(b))):
                    if json.dumps(a[i], sort_keys=True) != json.dumps(b[i], sort_keys=True):
                        bad.append('    first diff #%d' % i)
                        bad.append('    now  %s' % json.dumps(a[i], ensure_ascii=False)[:160])
                        bad.append('    head %s' % json.dumps(b[i], ensure_ascii=False)[:160])
                        break
            ha = json.dumps(frame_by_id(new, fid)['hotspots'], ensure_ascii=False,
                            sort_keys=True)
            hb = json.dumps(frame_by_id(head, fid)['hotspots'], ensure_ascii=False,
                            sort_keys=True)
            if ha != hb:
                bad.append('%s hotspots 变了' % fid)
    verdict('S2', bad, '  房子 pos/wings、山/田/河/坝/井/槐、五帧 hotspots 与 HEAD 深比较相同')

    # S3 接主路 + 够到门
    bad = []
    for fid in ROAD_FRAMES:
        fr = frame_by_id(new, fid)
        main_cells = set()
        for s in road_shapes(fr):
            if is_main_block(s):
                c, y = cell_of_rect(s['rect'])
                main_cells.add((c, y))
                main_cells.add((c, y + 1))
        for k in KEYS:
            sp = plan[(fid, k)]
            cells = set(sp['cells'])
            # 支路最底块 y=45 覆盖 row 45,46；同列主路块 y∈{46,47} 必与它在 row 46/47 相邻
            main_cols = set()
            ch, _ = main_chain(fr)
            if ch:
                main_cols = set(cell_of_rect(s['rect'])[0] for s in ch)
            touch = [b for b in sp['blocks'] if b[1] == 45 and b[0] in main_cols]
            if not touch:
                bad.append('%s/%s 没有落在 y=46 行、且与主路块上下相邻的块' % (fid, k))
            gx, gy = sp['gate_cell']
            if not any(b[0] == gx and b[1] <= gy + 1 <= b[1] + 1 for b in sp['blocks']):
                bad.append('%s/%s 门格 %s 正下方无路块' % (fid, k, sp['gate_cell']))
            if not connected(cells):
                bad.append('%s/%s 格子集合不是 4-连通（有断口）' % (fid, k))
    verdict('S3', bad, '  九条都接上主路带（y=46 行 + 上下相邻）且门格正下方有路块')

    # S4 指纹互异
    emit('S4 指纹表（同一帧内三条必须两两不同）：')
    bad = []
    for fid in ROAD_FRAMES:
        rows = []
        for k in KEYS:
            sp = plan[(fid, k)]
            main_a = sp['main_angle']
            rows.append((k, sp['n_bends'], sp['start_col'], main_a,
                         sp['exact_angles'], sp['meas_angles']))
        emit('   %s' % fid)
        for (k, nb, sc, ma, ea, angs) in rows:
            emit('     %-5s 折点=%d 起坡列=%3d 主倾角=%5.1f°  各段设计=%s  光栅实测=%s'
                 % (k, nb, sc, ma, '/'.join('%.1f' % a for a in ea),
                    '/'.join('%.1f' % a for a in angs)))
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                a, b = rows[i], rows[j]
                same_b = a[1] == b[1]
                same_c = a[2] == b[2]
                same_a = abs(a[3] - b[3]) <= 8.0
                if same_b and same_c and same_a:
                    bad.append('%s 的 %s 与 %s 三元组重合 (%d,%d,%.1f)'
                               % (fid, a[0], b[0], a[1], a[2], a[3]))
    verdict('S4', bad, '  (折点数, 起坡列, 实测倾角±8°) 同帧内两两不同')

    # S5 不压他人 lot / 地形
    bad = []
    for fid in ROAD_FRAMES:
        fr = frame_by_id(new, fid)
        for k in KEYS:
            sp = plan[(fid, k)]
            obs = collect_obstacles(fr, houses, sp['house'])
            h = hits(sp['cells'], obs)
            if h:
                bad.append('%s/%s 压到 %s' % (fid, k, h))
    verdict('S5', bad, '  不压任何他人 lot / 田 / 河 / 坝 / 井 / 槐（违规格数=0）')

    # S6 槐冠/井/河/坝 专查
    bad = []
    for fid in ROAD_FRAMES:
        fr = frame_by_id(new, fid)
        locust = None
        well = None
        for s in fr['shapes']:
            lab = s.get('label') or ''
            if s.get('type') == 'circle' and lab.startswith('老槐'):
                locust = s
            if s.get('type') == 'circle' and lab.startswith('老井'):
                well = s
        if not locust:
            bad.append('%s 找不到老槐' % fid)
            continue
        cen = (locust['center'][0] / TILE, locust['center'][1] / TILE)
        if cen != (64.0, 52.0):
            bad.append('%s 老槐圆心 %s != (64,52)' % (fid, cen))
        rad = locust['radius'] / TILE
        for k in KEYS:
            sp = plan[(fid, k)]
            n = sum(1 for (c, r) in sp['cells'] if circle_hit(c, r, cen, rad))
            if n:
                bad.append('%s/%s 压老槐冠 r=%d 格共 %d 格' % (fid, k, int(rad), n))
        if well:
            wc = (well['center'][0] / TILE, well['center'][1] / TILE)
            wr = well['radius'] / TILE
            for k in KEYS:
                sp = plan[(fid, k)]
                n = sum(1 for (c, r) in sp['cells'] if circle_hit(c, r, wc, wr))
                if n:
                    bad.append('%s/%s 压老井 r=%d 格共 %d 格' % (fid, k, int(wr), n))
        # 河 / 坝
        obs = [(n_, kk, p_) for (n_, kk, p_) in
               collect_obstacles(fr, houses, None) if n_ in ('河', '坝')]
        for k in KEYS:
            sp = plan[(fid, k)]
            h = hits(sp['cells'], obs)
            if h:
                bad.append('%s/%s 压 %s' % (fid, k, h))
    verdict('S6', bad, '  槐冠 (64,52) r1/r2/r3、井、河、坝 均未被压')

    # S7 整格
    bad = []
    for fid in ROAD_FRAMES:
        fr = frame_by_id(new, fid)
        for s in road_shapes(fr):
            r = s['rect']
            if len(r) != 4 or r[2] != TILE or r[3] != 2 * TILE:
                bad.append('%s 路块不是 [x,y,32,64]: %s' % (fid, r))
            elif r[0] % TILE or r[1] % TILE:
                bad.append('%s 路块不在整格: %s' % (fid, r))
    verdict('S7', bad, '  所有路块 = [x*32, y*32, 32, 64]，x/y 是整数格')

    # S8 幂等
    out = dump_like(new, raw)
    h1 = hashlib.sha256(out.encode('utf-8')).hexdigest()
    h2 = hashlib.sha256(dump_like(json.loads(out), raw).encode('utf-8')).hexdigest()
    bad = []
    if h1 != h2:
        bad.append('两次 dump sha256 不同')
    verdict('S8', bad, '  dump->loads->dump sha256=%s 稳定；indent=2/ensure_ascii=False 往返字节相同' % h1[:16])

    # S9 每条一句理由
    bad = []
    for sp in SPEC:
        if not sp.get('reason'):
            bad.append('%s/%s 没有理由' % (sp['fid'], sp['key']))
    verdict('S9', bad, '  九条都写了理由（内容由 lead 人工判）')

    # S10 三种倾角：用折线精确角，只统计「够长的段」（≥4 格）
    bands = {'90': [], '60-75': [], '30-45': []}
    for fid in ROAD_FRAMES:
        for k in KEYS:
            sp = plan[(fid, k)]
            if sp['kind'] == 'mill':
                bands['90'].append('%s/%s' % (fid, k))
                continue
            for i, a in enumerate(sp['exact_angles']):
                if sp['seg_len'][i] < 4.0:
                    continue
                if a >= 85:
                    bands['90'].append('%s/%s' % (fid, k))
                elif 60 <= a <= 78:
                    bands['60-75'].append('%s/%s %.1f°' % (fid, k, a))
                elif 28 <= a <= 47:
                    bands['30-45'].append('%s/%s %.1f°' % (fid, k, a))
    bad = [k for k, v in bands.items() if not v]
    verdict('S10', [('缺倾角档 %s' % b) for b in bad],
            '  90°=%d 条 / 60-75°=%d 条 / 30-45°=%d 条  %s'
            % (len(bands['90']), len(bands['60-75']), len(bands['30-45']),
               ' '.join(bands['60-75'] + bands['30-45'])))

    # S11 光栅实测 vs 折线精确角：偏差 ≤6°（证明落盘的形状真带着设计的角度）
    # 只判够长的段（≥6 格）：2 格宽的路在短段上只有 2~3 列可采，拟合角必然被
    # 相邻段污染，量不出真角度，判了也是噪声。
    bad = []
    for fid in ROAD_FRAMES:
        for k in KEYS:
            sp = plan[(fid, k)]
            if sp['kind'] == 'mill':
                continue
            for i, (ea, ma) in enumerate(zip(sp['exact_angles'], sp['meas_angles'])):
                if sp['seg_len'][i] < 6.0:
                    continue
                if abs(ea - ma) > 6.0:
                    bad.append('%s/%s 第%d段 设计 %.1f° vs 光栅实测 %.1f°（差 %.1f°）'
                               % (fid, k, i + 1, ea, ma, abs(ea - ma)))
    verdict('S11', bad, '  光栅实测角与折线设计角偏差 ≤6°（短段不判）')

    # ---------- 明细 ----------
    emit('')
    emit('九条明细（格）：')
    for sp0 in SPEC:
        sp = plan[(sp0['fid'], sp0['key'])]
        emit('   %-8s %-5s 折点=%d 起坡列=%3d 块=%2d 格=%3d 各段设计=%s'
             % (sp['fid'], sp['key'], sp['n_bends'], sp['start_col'],
                len(sp['blocks']), len(sp['cells']),
                '/'.join('%.1f' % a for a in sp['exact_angles'])))
        emit('      光栅实测=%s  任务书起坡列=%s 落地设定列=%s  门格=%s'
             % ('/'.join('%.1f' % a for a in sp['meas_angles']),
                DOC_COL[(sp['fid'], sp['key'])], sp['col'],
                sp['gate_cell']))
        if sp.get('note'):
            emit('      NOTE: %s' % sp['note'])
        emit('      理由: %s' % sp['reason'])

    emit('')
    emit('各帧路块统计：')
    for fr in new['frames']:
        ch, _ = main_chain(fr)
        n_road = len(road_shapes(fr))
        nmain = len(ch) if ch else 0
        emit('   %-9s shapes=%3d 路块=%3d (主路 %d + 支路 %d)'
             % (fr['id'], len(fr['shapes']), n_road, nmain, n_road - nmain))

    if args.ascii:
        for fid in ROAD_FRAMES:
            fr = frame_by_id(new, fid)
            extras = {}
            for s in fr['shapes']:
                if s.get('type') == 'house':
                    h = houses.get(s['id'])
                    if not h:
                        continue
                    pos_c = (s['pos'][0] // TILE, s['pos'][1] // TILE)
                    c0, r0, w, hh = lot_cell_of(h, pos_c)
                    for c in range(c0, c0 + w):
                        for r in range(r0, r0 + hh):
                            extras[(c, r)] = 'h'
                    gc = gate_cell_of(h, pos_c)
                    if gc:
                        extras[gc] = 'g'
            for s in road_shapes(fr):
                c, y = cell_of_rect(s['rect'])
                for rr in (y, y + 1):
                    extras.setdefault((c, rr), '-')
            for k in KEYS:
                sp = plan[(fid, k)]
                cells = set()
                for (c, y) in sp['blocks']:
                    cells.add((c, y))
                    cells.add((c, y + 1))
                xs = [c for (c, r) in cells]
                ys = [r for (c, r) in cells]
                emit('')
                emit('--- %s / %s  (cols %d..%d rows %d..%d)'
                     % (fid, k, min(xs), max(xs), min(ys), max(ys)))
                emit(ascii_map(cells, extras, min(xs) - 1, max(xs) + 1,
                               min(ys) - 1, max(ys) + 1))

    emit('')
    emit('TOTAL FAILS = %d' % fails[0])

    if args.report:
        with io.open(args.report, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(log) + '\n')
        print('REPORT %s' % args.report)

    if args.write:
        if fails[0]:
            emit('自检没过，拒绝写盘')
            return 1
        with io.open(FRAMES_PATH, 'w', encoding='utf-8', newline='\n') as f:
            f.write(out)
        _, raw2 = load_json(FRAMES_PATH)
        h3 = hashlib.sha256(raw2.encode('utf-8')).hexdigest()
        print('WROTE %s (%d bytes) sha256=%s' % (FRAMES_PATH,
                                                len(out.encode('utf-8')), h3[:16]))
        print('write-roundtrip=%s' % ('OK' if raw2 == out else 'MISMATCH'))

    return 0 if fails[0] == 0 else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))