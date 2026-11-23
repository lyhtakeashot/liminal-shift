#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lab/_solver_a4_layout.py -- A4/A5 地图帧摆位与跨帧一致性 求解器

用法
----
    python lab/_solver_a4_layout.py            # 全量跑（实测 < 60 秒）
    python lab/_solver_a4_layout.py --quick    # 只跑一致性表 + 界碑候选 + 遮挡率 + 热点重算
    python lab/_solver_a4_layout.py --solve    # 只跑摆位求解

坐标约定
--------
    * 所有坐标单位是像素(px)，与 data/frames.json 完全一致。
    * TILE = 32.0 px（唯一定义点 scripts/house_shape.gd:13）。
    * 世界 3200 x 2400 px = 100 x 75 格。
    * 主路 ROAD_Y = 1664 px、高 64 px，即路带 y ∈ [1664,1728]。
    * 房子 shape 的 pos 是屋体原点(px)；houses_data.json 里 wings 的四个数是
      [x, y, w, h]（格起点 + 宽高），**不是** x1,y1,x2,y2 ——
      见 scripts/house_shape.gd:148-152 grid_of()：wx=w[0], wy=w[1], ww=w[2], wh=w[3]，
      interior 是内缩一圈的矩形，墙 = interior 的四邻格（house_shape.gd:158-164）。
    * 碰撞用半开区间：只共边不算重叠（与引擎 Rect2.has_point/intersects 语义一致）。
    * 位掩码：世界切成 16px 一格（200 x 150 = 30000 bit），Python int 承载。

约束定义
--------
    C1 同一栋房子在 A4 / A5 必须同址（核心玩法「空间冻结、位置不变」）。
       frames.json 里只有 market 这个 id 同时出现在 A4 与 A5，故 C1 对 market 生效；
       其余三栋是 A4 独有（shen_a4 的 A5 化身是 school，见 C8）。
    C2 地标五帧不动：老井 (1360,848) 老槐 (1296,976) 坝 (384,96) 田 (1856,192) 界碑。
    C3 不同房子的 wings 两两不重叠。
    C4 不压河（河 polygon：顶点入矩形 / 矩形角入多边形 / 边相交，三者任一即重叠）。
    C5 不跨主路带 y ∈ [1664,1728]。
    C6 A4 四栋原则上都在路北（bbox 底边 <= 1664）。
    C7 老井不能被任何房子盖住（story §7.1/§7.2①：井是现代物证，必须看得见）。
       老槐树干点 (1296,976) 不能落在任何房子足迹里（story §7.3：1926 栽的苗要活到 2026）。
    C8 shen_a4 ↔ A5 school 允许重叠（同宗：沈家宅 → 沈明远捐建的村小），
       但默认给两种口径分别求解。

输出
----
    每一节都打印成可直接抄进 docs/DECIDE-a4-a5-layout.md 的表格。
"""

import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TILE = 32.0
WORLD_W, WORLD_H = 3200, 2400
ROAD_Y, ROAD_H = 1664, 64
ROAD_BAND = (ROAD_Y, ROAD_Y + ROAD_H)
CELL = 16
CW, CH = WORLD_W // CELL, WORLD_H // CELL

QUICK = "--quick" in sys.argv
ONLY_SOLVE = "--solve" in sys.argv

A4_IDS = ("market", "shen_a4", "zhou_a4", "zheng_a4")
# A4 现状 pos（data/frames.json 实测）
CUR_POS = {"market": (1440, 576), "shen_a4": (128, 320),
            "zhou_a4": (1792, 1728), "zheng_a4": (2560, 1728)}
# A1–A3 同宗房子原址（docs/BUILD-A1.md:103-110「原点固定，只在自己原址上长大」）
LINEAGE_X = {"shen_a4": 128, "zhou_a4": 1792, "mill": 1216, "lu": 2304}


# --------------------------------------------------------------------------
# 0. 几何
# --------------------------------------------------------------------------

def load_data():
    with open(os.path.join(ROOT, "data", "frames.json"), encoding="utf-8") as f:
        frames = json.load(f)
    with open(os.path.join(ROOT, "_ref", "houses", "houses_data.json"), encoding="utf-8") as f:
        houses = json.load(f)
    return frames, {h["id"]: h for h in houses}


def wings_rects(hdata, pos):
    """wings -> 像素矩形列表 [(x, y, w, h), ...]（半开）。"""
    return [(pos[0] + w[0] * TILE, pos[1] + w[1] * TILE, w[2] * TILE, w[3] * TILE)
            for w in hdata.get("wings", [])]


def rects_bbox(rects):
    return (min(r[0] for r in rects), min(r[1] for r in rects),
            max(r[0] + r[2] for r in rects) - min(r[0] for r in rects),
            max(r[1] + r[3] for r in rects) - min(r[1] for r in rects))


def rect_overlap(a, b):
    return not (a[0] + a[2] <= b[0] or b[0] + b[2] <= a[0] or
                a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1])


def circle_rect_overlap(cx, cy, r, rect):
    nx = min(max(cx, rect[0]), rect[0] + rect[2])
    ny = min(max(cy, rect[1]), rect[1] + rect[3])
    dx, dy = cx - nx, cy - ny
    return dx * dx + dy * dy < r * r


def point_in_poly(x, y, pts):
    inside = False
    n = len(pts)
    j = n - 1
    for i in range(n):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > y) != (yj > y):
            xint = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < xint:
                inside = not inside
        j = i
    return inside


def _orient(a, b, c):
    v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return 0 if abs(v) < 1e-9 else (1 if v > 0 else 2)


def _seg_seg_intersect(p1, p2, p3, p4):
    o1, o2 = _orient(p1, p2, p3), _orient(p1, p2, p4)
    o3, o4 = _orient(p3, p4, p1), _orient(p3, p4, p2)
    return o1 != o2 and o3 != o4


def poly_overlaps_rect(pts, rect):
    x, y, w, h = rect
    for (px, py) in pts:
        if x <= px < x + w and y <= py < y + h:
            return True
    for (cx, cy) in ((x, y), (x + w, y), (x, y + h), (x + w, y + h)):
        if point_in_poly(cx, cy, pts):
            return True
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        if _seg_seg_intersect(a, b, (x, y), (x + w, y)):
            return True
        if _seg_seg_intersect(a, b, (x + w, y), (x + w, y + h)):
            return True
        if _seg_seg_intersect(a, b, (x + w, y + h), (x, y + h)):
            return True
        if _seg_seg_intersect(a, b, (x, y + h), (x, y)):
            return True
    return False


def rects_mask(rects):
    m = 0
    for (x, y, w, h) in rects:
        if w <= 0 or h <= 0:
            continue
        x0 = max(0, int(math.floor(x / CELL)))
        x1 = min(CW - 1, int(math.ceil((x + w) / CELL)) - 1)
        y0 = max(0, int(math.floor(y / CELL)))
        y1 = min(CH - 1, int(math.ceil((y + h) / CELL)) - 1)
        if x1 < x0 or y1 < y0:
            continue
        row = ((1 << (x1 - x0 + 1)) - 1) << x0
        for cy in range(y0, y1 + 1):
            m |= row << (cy * CW)
    return m


# --------------------------------------------------------------------------
# 1. 帧视图
# --------------------------------------------------------------------------

class FrameView:
    def __init__(self, fdict, houses):
        self.id = fdict["id"]
        self.year = fdict["year"]
        self.shapes = fdict["shapes"]
        self.hotspots = fdict.get("hotspots", [])
        self.house_shapes = [s for s in self.shapes if s.get("type") == "house"]
        self.circles = [s for s in self.shapes if s.get("type") == "circle"]
        self.rects = [s for s in self.shapes if s.get("type") == "rect"]
        self.polys = [s for s in self.shapes if s.get("type") == "polygon"]
        self.road_rects = [s for s in self.rects if s.get("road")]
        self.field_rects = [s for s in self.rects
                            if not s.get("road") and not s.get("label")]
        self.river = None
        for p in self.polys:
            if p.get("label") == "河":
                self.river = p["points"]
        self.solid_rects = []
        for s in self.shapes:
            if not bool(s.get("solid", False)):
                continue
            if s.get("type") == "rect":
                r = s["rect"]
                self.solid_rects.append((r[0], r[1], r[2], r[3]))
            elif s.get("type") == "circle":
                c, rad = s["center"], s["radius"]
                self.solid_rects.append((c[0] - rad, c[1] - rad, 2 * rad, 2 * rad))
        self.house_footprints = {}
        for hs in self.house_shapes:
            hd = houses.get(hs["id"])
            if hd:
                self.house_footprints[hs["id"]] = wings_rects(hd, hs["pos"])

    def house_pos(self, hid):
        for hs in self.house_shapes:
            if hs["id"] == hid:
                return tuple(hs["pos"])
        return None

    def circle_by(self, key):
        for c in self.circles:
            if key in str(c.get("label", "")):
                return c
        return None

    def rect_by(self, label):
        for r in self.rects:
            if r.get("label") == label:
                return r["rect"]
        return None


# --------------------------------------------------------------------------
# 2. 一致性表
# --------------------------------------------------------------------------

def section_consistency(fv, order):
    print("=" * 96)
    print("[1] 跨帧一致性核查表")
    print("=" * 96)
    print(f"{'帧':<11}{'年':<6}{'老井':<24}{'老槐':<24}{'界碑/红绿灯':<26}"
          f"{'坝':<22}{'田':<26}{'主路':<24}")
    for fid in order:
        v = fv[fid]
        w = v.circle_by("井")
        t = v.circle_by("槐")
        ws = "circle%s r=%d" % (tuple(w["center"]), w["radius"]) if w else "-"
        ts = "circle%s r=%d" % (tuple(t["center"]), t["radius"]) if t else "-"
        st = v.rect_by("碑")
        tl = v.rect_by("红绿灯")
        stxt = ("rect%s" % (tuple(st),)) if st else \
               (("红绿灯%s" % (tuple(tl),)) if tl else "-")
        dm = v.rect_by("坝")
        dmt = ("rect%s" % (tuple(dm),)) if dm else "-"
        fd = v.field_rects
        fdt = ("rect%s x%d" % (tuple(fd[0]["rect"]), len(fd))) if fd else "-"
        rd = ("直路 rect%s" % (tuple(v.road_rects[0]["rect"]),)) if len(v.road_rects) == 1 \
            else ("弯路 rect x%d" % len(v.road_rects))
        print(f"{fid:<11}{v.year:<6}{ws:<24}{ts:<24}{stxt:<26}{dmt:<22}{fdt:<26}{rd:<24}")

    print("\n-- shape label vs hotspot title 不一致（证物 key 取 hotspot title）--")
    for fid in order:
        v = fv[fid]
        labels = [str(c.get("label", "")) for c in v.circles]
        norm = lambda s: s.replace(" ", "").replace("·", "")
        for h in v.hotspots:
            t = h["title"]
            if t.startswith(("老井", "老槐")):
                if not any(norm(t) == norm(l) for l in labels):
                    print(f"  {fid}: hotspot title='{t}'  但 shape label={labels}")

    print("\n-- 房子 pos 对照 --")
    hids = []
    for fid in order:
        for hs in fv[fid].house_shapes:
            if hs["id"] not in hids:
                hids.append(hs["id"])
    print(f"{'house_id':<12}" + "".join(f"{fid:<14}" for fid in order))
    for hid in hids:
        row = f"{hid:<12}"
        for fid in order:
            p = fv[fid].house_pos(hid)
            row += f"{str(p) if p else '-':<14}"
        print(row)

    print("\n-- 井的 solid 标志（frame_data.gd:35 只把 solid=true 的形状当阻挡）--")
    for fid in order:
        w = fv[fid].circle_by("井")
        print(f"  {fid}: solid={w.get('solid')} label={w.get('label')!r}")


# --------------------------------------------------------------------------
# 3. 河道与地块
# --------------------------------------------------------------------------

def river_bottom_profile(river):
    """河 polygon 下沿（每个 x 的最大 y），返回 {x: y}。"""
    prof = {}
    n = len(river)
    for i in range(n):
        ax, ay = river[i]
        bx, by = river[(i + 1) % n]
        if ay == by:
            continue
        lo, hi = (ax, bx) if ax < bx else (bx, ax)
        step = 32 if bx > ax else -32
        x = lo
        while True:
            t = (x - ax) / (bx - ax) if bx != ax else 0.0
            y = ay + (by - ay) * t
            prof[x] = max(prof.get(x, -1e9), y)
            if x == hi:
                break
            x += step
    return prof


def section_land(fv, houses, order):
    print()
    print("=" * 96)
    print("[2] 河道下沿与各地块占位")
    print("=" * 96)
    a4 = fv["a4_2001"]
    prof = river_bottom_profile(a4.river)
    xs = sorted(prof)
    print(f"  河 polygon 共 {len(a4.river)} 点，x 覆盖 {xs[0]}..{xs[-1]}，"
          f"下沿 y ∈ [{min(prof.values()):.0f},{max(prof.values()):.0f}]")
    for x in (0, 128, 192, 320, 640, 960, 1216, 1440, 1792, 2048, 2560, 3000, 3200):
        near = min(prof.keys(), key=lambda k: abs(k - x))
        print(f"    x={x:<6} 下沿 y ≈ {prof[near]:.0f}")
    print("\n  各房子足迹 vs 河 / 地标：")
    for fid in order:
        v = fv[fid]
        for hid, rects in v.house_footprints.items():
            bb = rects_bbox(rects)
            inriver = poly_overlaps_rect(v.river, bb)
            w = v.circle_by("井")
            t = v.circle_by("槐")
            cw = circle_rect_overlap(w["center"][0], w["center"][1], w["radius"], bb)
            ct = circle_rect_overlap(t["center"][0], t["center"][1], t["radius"], bb)
            print(f"    {fid:<11} {hid:<10} bbox={tuple(round(v) for v in bb)}  "
                  f"压河={'是' if inriver else '否':<3} 压井={'是' if cw else '否':<3} "
                  f"压槐={'是' if ct else '否'}")


# --------------------------------------------------------------------------
# 4. 摆位求解
# --------------------------------------------------------------------------

class Cand:
    __slots__ = ("pos", "rects", "mask", "disp", "bbox")

    def __init__(self, pos, rects, mask, disp, bbox):
        self.pos, self.rects, self.mask, self.disp, self.bbox = pos, rects, mask, disp, bbox


def gen_candidates(hid, hdata, cur_pos, *, pinned=None, north_only=True,
                   river=None, well=None, tree=None, obstacles=(), allow_overlap=(),
                   lineage_x=None, max_disp=None):
    protect_circles = []
    if well:
        protect_circles.append(well)
    if tree:
        protect_circles.append(tree)
    out = []
    bb0 = rects_bbox(wings_rects(hdata, (0, 0)))
    w, h = bb0[2], bb0[3]
    gx_max = int((WORLD_W - w) // 32)
    gy_max = int((WORLD_H - h) // 32)
    for gx in range(0, gx_max + 1):
        for gy in range(0, gy_max + 1):
            pos = (gx * 32, gy * 32)
            if pinned is not None and pos != pinned:
                continue
            rects = wings_rects(hdata, pos)
            bb = rects_bbox(rects)
            if bb[0] + bb[2] > WORLD_W or bb[1] + bb[3] > WORLD_H:
                continue
            if north_only:
                if bb[1] + bb[3] > ROAD_BAND[0]:
                    continue
            else:
                if bb[1] < ROAD_BAND[1] and bb[1] + bb[3] > ROAD_BAND[0]:
                    continue
            if lineage_x is not None and pos[0] != lineage_x:
                continue
            disp = math.hypot(pos[0] - cur_pos[0], pos[1] - cur_pos[1])
            if max_disp is not None and disp > max_disp:
                continue
            if river is not None and poly_overlaps_rect(river, bb):
                continue
            bad = False
            for (cx, cy, r) in protect_circles:
                for rr in rects:
                    if circle_rect_overlap(cx, cy, r, rr):
                        bad = True
                        break
                if bad:
                    break
            if bad:
                continue
            for (lbl, orect) in obstacles:
                if lbl in allow_overlap:
                    continue
                for rr in rects:
                    if rect_overlap(rr, orect):
                        bad = True
                        break
                if bad:
                    break
            if bad:
                continue
            out.append(Cand(pos, rects, rects_mask(rects), disp, bb))
    out.sort(key=lambda c: (c.disp, c.pos))
    return out


def enumerate_solutions(cand_lists, threshold, limit=4000):
    """位掩码 + 分层剪枝穷举。cand_lists 每项已按 disp 升序。"""
    n = len(cand_lists)
    order = sorted(range(n), key=lambda i: len(cand_lists[i]))
    min_rest = [0.0] * (n + 1)
    for i in range(n - 1, -1, -1):
        hh = order[i]
        min_rest[i] = min_rest[i + 1] + (cand_lists[hh][0].disp if cand_lists[hh] else 0.0)
    sols = []
    combo = []

    def dfs(i, used, acc):
        if len(sols) >= limit:
            return
        if acc + min_rest[i] > threshold + 1e-9:
            return
        if i == n:
            sols.append((acc, list(combo)))
            return
        hh = order[i]
        for c in cand_lists[hh]:
            if acc + c.disp + min_rest[i + 1] > threshold + 1e-9:
                break
            if used & c.mask:
                continue
            combo.append(c)
            dfs(i + 1, used | c.mask, acc + c.disp)
            combo.pop()

    dfs(0, 0, 0.0)
    return sols


def solution_report(sol, fv, houses, landmarks, tag, allow_pairs=()):
    total, cands = sol
    ids = [c for c in A4_IDS]
    print(f"  --- {tag} 总位移 {total:.0f} px ---")
    for hid, c in zip(ids, cands):
        print(f"      {hid:<9} pos={list(c.pos)}  Δ={c.disp:.0f}px  "
              f"footprint=({c.bbox[0]:.0f},{c.bbox[1]:.0f},"
              f"{c.bbox[0]+c.bbox[2]:.0f},{c.bbox[1]+c.bbox[3]:.0f})")
    flags = []
    for key in ("老井", "老槐"):
        cx, cy, r = landmarks[key]
        cov = any(circle_rect_overlap(cx, cy, r, rr) for c in cands for rr in c.rects)
        flags.append(f"压{key}={'是' if cov else '否'}")
    for key in ("坝", "田"):
        if key in landmarks:
            rect = landmarks[key]
            cov = any(rect_overlap(rr, rect) for c in cands for rr in c.rects)
            flags.append(f"压{key}={'是' if cov else '否'}")
    print("      " + "  ".join(flags))
    a5 = fv["a5_2026"]
    for hid in ("school", "market", "toyshop"):
        p = a5.house_pos(hid)
        hd = houses.get(hid)
        if not p or not hd:
            continue
        rects = wings_rects(hd, p)
        ov = any(rect_overlap(rr, o) for c in cands for rr in c.rects for o in rects)
        allowed = (hid, "market") in allow_pairs or \
                  any((hid, "market") == pair for pair in allow_pairs)
        print(f"      与 A5 {hid:<9} {'重叠(允许)' if ov and allowed else ('重叠' if ov else '不重叠')}")


def section_solve(fv, houses, order):
    print()
    print("=" * 96)
    print("[3] A4 四栋摆位求解（位掩码 + 分层剪枝）")
    print("=" * 96)
    a4, a5 = fv["a4_2001"], fv["a5_2026"]
    river = a4.river
    w = a4.circle_by("井")
    t = a4.circle_by("槐")
    well = (w["center"][0], w["center"][1], w["radius"])
    tree = (t["center"][0], t["center"][1], t["radius"])
    dam = a4.rect_by("坝")
    field = a4.field_rects[0]["rect"] if a4.field_rects else None
    landmarks = {"老井": well, "老槐": tree, "坝": dam, "田": field}

    a5_obstacles = []
    for hid in ("school", "market", "toyshop"):
        p = a5.house_pos(hid)
        hd = houses.get(hid)
        if p and hd:
            for r in wings_rects(hd, p):
                a5_obstacles.append((hid, r))

    def build(pinned_market=None, north_only=True, protect=True,
              allow_shen_school=True, lineage=False, pin_others=None,
              north_map=None):
        lists = []
        for hid in A4_IDS:
            hd = houses[hid]
            pinned = pinned_market if hid == "market" else \
                     (pin_others or {}).get(hid)
            no = north_only if north_map is None else north_map.get(hid, north_only)
            obst = list(a5_obstacles)
            allow = set()
            if hid == "market":
                obst = [(l, r) for (l, r) in obst if l != "market"]
            if hid == "shen_a4" and allow_shen_school:
                allow.add("school")
            lists.append(gen_candidates(
                hid, hd, CUR_POS[hid], pinned=pinned, north_only=no,
                river=river, well=well if protect else None,
                tree=tree if protect else None,
                obstacles=obst, allow_overlap=allow,
                lineage_x=LINEAGE_X.get(hid) if lineage else None))
        return lists

    def show(tag, lists, top=5, allow_pairs=()):
        print(f"\n### {tag}")
        for i, l in enumerate(lists):
            print(f"      候选数 {A4_IDS[i]:<9} = {len(l)}")
        if any(len(l) == 0 for l in lists):
            for i, l in enumerate(lists):
                if not l:
                    print(f"      => 候选集为空：{A4_IDS[i]}（该口径下无解）")
            return []
        base = sum(l[0].disp for l in lists)
        cap = base + 768.0
        found = []
        t = base
        seen = set()
        while t <= cap and len(found) < top:
            sols = enumerate_solutions(lists, t + 1e-6)
            for s in sorted(sols, key=lambda s: s[0]):
                key = tuple(c.pos for c in s[1])
                if key in seen:
                    continue
                seen.add(key)
                found.append(s)
            t += 32.0
        if not found:
            print(f"      => 阈值 ≤ {cap:.0f} px 内无解")
            return []
        found.sort(key=lambda s: s[0])
        print(f"      找到 {len(found)} 组解（总位移升序，前 {min(top,len(found))} 组）")
        for s in found[:top]:
            solution_report(s, fv, houses, landmarks,
                            "解", allow_pairs=allow_pairs)
        return found

    # --- P1：推荐口径 ---------------------------------------------------
    print("\n[P1] 口径：market 钉在 A5 同址 (1440,768) + 地标不动/不埋 + 三栋可自由（可跨路）")
    lists = build(pinned_market=(1440, 768), north_only=False, protect=True,
                  allow_shen_school=True, lineage=False)
    show("P1 market(1440,768) 同址 + 三栋自由（允许在路南）", lists, top=5,
         allow_pairs=(("school", "market"),))

    # --- P1b：market 钉在 A5 同址，但 market 需避让 A5 老槐树冠 ---------
    print("\n[P1b] 同上，但 market 也必须避让 A5 老槐 r=160 的上抬树冠（口径 B）")
    lists_1b = build(pinned_market=None, north_only=False, protect=True,
                     allow_shen_school=True)
    mkt = [c for c in lists_1b[0]
           if c.pos[0] >= 1472 and 576 <= c.pos[1] <= 768]
    print(f"      market 候选（口径B：避五帧树冠）x>=1472 且 576<=y<=768 = {len(mkt)} 个")

    # --- P2：严格不许压 A5 任何房子 --------------------------------------
    lists2 = build(pinned_market=(1440, 768), north_only=True, protect=True,
                   allow_shen_school=False)
    show("P2 同上，但 shen_a4 也不许压 A5 school（严格不重叠 A5 任何房子）", lists2, top=3)

    # --- P3：钉住现状 zhou_a4 / zheng_a4（保持南侧） ---------------------
    lists3 = build(pinned_market=(1440, 768), north_only=True, protect=True,
                   allow_shen_school=True,
                   pin_others={"zhou_a4": (1792, 1728), "zheng_a4": (2560, 1728)})
    show("P3 zhou_a4/zheng_a4 钉在现状(南侧)，market 同址 → 「四栋全路北」不可行", lists3, top=3)

    # --- P4：超市压住老井 ------------------------------------------------
    print("\n[P4] 口径：超市必须压住老井 (1360,848) —— market 自由摆")
    cov_list = []
    for gx in range(0, int((WORLD_W - 1344) // 32) + 1):
        for gy in range(0, int((WORLD_H - 896) // 32) + 1):
            pos = (gx * 32, gy * 32)
            rects = wings_rects(houses["market"], pos)
            bb = rects_bbox(rects)
            if bb[1] + bb[3] > ROAD_BAND[0]:
                continue
            if not circle_rect_overlap(well[0], well[1], well[2], bb):
                continue
            if poly_overlaps_rect(river, bb):
                continue
            # A5 同址时不能压 A5 school / toyshop
            clash = []
            for hid in ("school", "market", "toyshop"):
                p = a5.house_pos(hid)
                hd = houses.get(hid)
                if not p or not hd:
                    continue
                if hid == "market":
                    continue
                for r in wings_rects(hd, p):
                    if rect_overlap(bb, r):
                        clash.append(hid)
            cov_list.append((pos, sorted(set(clash))))
    print(f"      路北、能压住老井的 market 位置共 {len(cov_list)} 个")
    if cov_list:
        xs = sorted(set(p[0] for p, _ in cov_list))
        ys = sorted(set(p[1] for p, _ in cov_list))
        print(f"      x 取值 {xs}")
        print(f"      y 取值 {ys}")
        tree_cov = []
        for pos, _ in cov_list:
            bb = rects_bbox(wings_rects(houses["market"], pos))
            if circle_rect_overlap(tree[0], tree[1], tree[2], bb):
                tree_cov.append(pos)
        print(f"      其中同时压住老槐的 = {len(tree_cov)} / {len(cov_list)} "
              f"（老槐在井西 64px，超市 ≥1344px 宽 → 压井必压槐）")
        no_school = [(p, c) for p, c in cov_list if "school" not in c]
        print(f"      其中不压 A5 school 的 = {len(no_school)} 个"
              f"{'（例：%s）' % (no_school[0][0],) if no_school else ''}")
        if no_school:
            p0 = no_school[0][0]
            bb = rects_bbox(wings_rects(houses["market"], p0))
            print(f"      取 {p0} 时 A5 的 market 也必须同址 → A5 老井 (1360,848) "
                  f"落在超市足迹 x∈[{bb[0]:.0f},{bb[0]+bb[2]:.0f}] 内 = 井被埋")
    print("      结论：压井 ⇒ 压槐 ⇒ 与 story §7.3（2026 树根把超市地砖拱裂）冲突；")
    print("            且 A4/A5 同址 ⇒ A5 井被超市埋掉 ⇒ story §7.2① 沥青补丁（钥匙物证）不可见。")

    # --- P5：老井/老槐 都不埋的超市可行域 -------------------------------
    print("\n[P5] market「既不压老井也不压老槐」的可行域（路北 + 世界内 + 不压河）")
    ok = []
    for gx in range(0, int((WORLD_W - 1344) // 32) + 1):
        for gy in range(0, int((WORLD_H - 896) // 32) + 1):
            pos = (gx * 32, gy * 32)
            bb = rects_bbox(wings_rects(houses["market"], pos))
            if bb[1] + bb[3] > ROAD_BAND[0]:
                continue
            if poly_overlaps_rect(river, bb):
                continue
            if circle_rect_overlap(well[0], well[1], well[2], bb):
                continue
            if circle_rect_overlap(tree[0], tree[1], tree[2], bb):
                continue
            ok.append(pos)
    if ok:
        print(f"      可行位置 {len(ok)} 个；x ∈ [{min(p[0] for p in ok)},"
              f"{max(p[0] for p in ok)}]，y ∈ [{min(p[1] for p in ok)},"
              f"{max(p[1] for p in ok)}]")
        print(f"      其中 x ≥ 1392（超市整体在井/槐以东）的 = "
              f"{len([p for p in ok if p[0] >= 1392])}")
    print("      A5 同址位 (1440,768) 是否可行：",
          "是" if (1440, 768) in ok else "否")
    return landmarks


# --------------------------------------------------------------------------
# 8. 最终拍板方案复核（2026-11-23 lead/总策划口径）
# --------------------------------------------------------------------------

# 总策划拍板：A4 四栋最终摆位
FINAL_A4 = {
    "market":  (1440, 768),   # 与 A5 同址
    "shen_a4": (96, 320),
    "zhou_a4": (1792, 1728),
    "zheng_a4": (2560, 1728),
}
# 总策划拍板：界碑归位 [2880,960]
FINAL_STELE = (2880, 960, 16, 32)
# A5 竖路两段（solid=false，但视觉上是路）
A5_VERT_ROADS = ((1328, 416, 64, 1248), (1328, 1728, 64, 672))
# A5 停车场 + 三个车位
A5_PARKING = ((960, 1728, 320, 256), (976, 1752, 88, 160),
              (1080, 1752, 88, 160), (1184, 1752, 88, 160))


def section_final(fv, houses, order):
    print()
    print("=" * 96)
    print("[9] 总策划拍板方案独立复核（FINAL_A4 + FINAL_STELE）")
    print("=" * 96)
    a4, a5 = fv["a4_2001"], fv["a5_2026"]
    river = a4.river
    well = a4.circle_by("井")
    tree = a4.circle_by("槐")
    a5_tree = a5.circle_by("槐")
    dam = a4.rect_by("坝")
    field = a4.field_rects[0]["rect"] if a4.field_rects else None
    landmarks = {"老井": (well["center"][0], well["center"][1], well["radius"]),
                 "老槐": (tree["center"][0], tree["center"][1], tree["radius"]),
                 "A5老槐(上抬树冠)": (a5_tree["center"][0],
                                     a5_tree["center"][1] - a5_tree["radius"] * 0.7,
                                     a5_tree["radius"]),
                 "坝": dam, "田": field}

    rects_of = {hid: wings_rects(houses[hid], FINAL_A4[hid]) for hid in FINAL_A4}
    bbs = {hid: rects_bbox(rects_of[hid]) for hid in FINAL_A4}

    print("\n-- 9.1 A4 四栋逐项校验 --")
    hdr = f"{'house':<10}{'pos':<16}{'bbox':<30}{'出界':<6}{'压河':<6}{'跨路':<6}"
    hdr += "".join(f"{k:<10}" for k in ("压老井", "压老槐", "压A5槐冠", "压坝", "压田"))
    print(hdr)
    for hid in A4_IDS:
        bb = bbs[hid]
        out = bb[0] < 0 or bb[1] < 0 or bb[0] + bb[2] > WORLD_W or bb[1] + bb[3] > WORLD_H
        inr = poly_overlaps_rect(river, bb)
        cross = bb[1] < ROAD_BAND[1] and bb[1] + bb[3] > ROAD_BAND[0]
        flags = []
        for k, v in landmarks.items():
            if k in ("坝", "田"):
                cov = any(rect_overlap(r, v) for r in rects_of[hid])
            else:
                cov = any(circle_rect_overlap(v[0], v[1], v[2], r) for r in rects_of[hid])
            flags.append("是" if cov else "否")
        print(f"{hid:<10}{str(list(FINAL_A4[hid])):<16}"
              f"{str(tuple(round(v) for v in bb)):<30}"
              f"{('是' if out else '否'):<6}{('是' if inr else '否'):<6}"
              f"{('是' if cross else '否'):<6}" + "".join(f"{f:<10}" for f in flags))

    print("\n-- 9.2 A4 四栋两两重叠 --")
    bad = False
    for i in range(len(A4_IDS)):
        for j in range(i + 1, len(A4_IDS)):
            a, b = A4_IDS[i], A4_IDS[j]
            ov = any(rect_overlap(r, s) for r in rects_of[a] for s in rects_of[b])
            if ov:
                bad = True
            print(f"  {a:<10} vs {b:<10} {'重叠 !!' if ov else '不重叠'}")
    print("  =>", "存在重叠" if bad else "四栋互不重叠 ✔")

    print("\n-- 9.3 与 A5 三栋 + 竖路 + 停车场 --")
    a5_fp = {}
    for hid in ("school", "market", "toyshop"):
        p = a5.house_pos(hid)
        a5_fp[hid] = wings_rects(houses[hid], p)
    for hid in A4_IDS:
        for ahid in ("school", "market", "toyshop"):
            ov = any(rect_overlap(r, s) for r in rects_of[hid] for s in a5_fp[ahid])
            if ov:
                bb0, bb1 = bbs[hid], rects_bbox(a5_fp[ahid])
                ox = (max(bb0[0], bb1[0]), min(bb0[0] + bb0[2], bb1[0] + bb1[2]))
                oy = (max(bb0[1], bb1[1]), min(bb0[1] + bb0[3], bb1[1] + bb1[3]))
                area = max(0, ox[1] - ox[0]) * max(0, oy[1] - oy[0])
                print(f"  {hid:<10} vs A5 {ahid:<9} 重叠 x{ox} y{oy} = {area} px²")
        for nm, vr in [("A5竖路", A5_VERT_ROADS[0]), ("A5竖路南段", A5_VERT_ROADS[1]),
                       ("A5停车场", A5_PARKING[0])]:
            ov = any(rect_overlap(r, vr) for r in rects_of[hid])
            if ov:
                print(f"  {hid:<10} vs {nm:<12} 重叠 !!")
    print("  （未列出者 = 不重叠）")

    print("\n-- 9.4 界碑 FINAL_STELE =", FINAL_STELE, "--")
    srect = FINAL_STELE
    sc = (srect[0] + srect[2] / 2.0, srect[1] + srect[3] / 2.0)
    checks = []
    checks.append(("出界", not (srect[0] >= 0 and srect[1] >= 0 and
                                srect[0] + srect[2] <= WORLD_W and
                                srect[1] + srect[3] <= WORLD_H)))
    checks.append(("压河", any(poly_overlaps_rect(fv[f].river, srect) for f in order)))
    checks.append(("压A1/A2弯路(26块)",
                   any(rect_overlap(srect, r["rect"]) for f in ("a1_1926", "a2_1951")
                       for r in fv[f].road_rects)))
    checks.append(("压A3-5直路", rect_overlap(srect, (0, 1664, 3200, 64))))
    checks.append(("压A5竖路", any(rect_overlap(srect, v) for v in A5_VERT_ROADS)))
    checks.append(("压A5停车场", any(rect_overlap(srect, v) for v in A5_PARKING)))
    for k, v in landmarks.items():
        if k in ("坝", "田"):
            checks.append((f"压{k}", rect_overlap(srect, v)))
        else:
            checks.append((f"压{k}", circle_rect_overlap(v[0], v[1], v[2], srect)))
    hits = []
    for fid in order:
        for hid, rects in fv[fid].house_footprints.items():
            if any(rect_overlap(srect, r) for r in rects):
                hits.append(f"{fid}:{hid}")
    checks.append(("压房子", bool(hits)))
    for nm, v in checks:
        print(f"  {nm:<20} {'冲突 !!' if v else 'OK'}")
    if hits:
        print("  压到的房子：", ", ".join(hits))
    old = (1856, 960)
    print(f"  距 A1 原位 {old} = {abs(srect[0] - old[0]) + abs(srect[1] - old[1])} px"
          f"（纯横移，y 保持 960）")
    # 保持 y=960 时最近合法位
    xs = []
    for x in range(0, WORLD_W - 16, 16):
        r = (x, 960, 16, 32)
        ok = True
        for fid in order:
            if any(rect_overlap(r, h["rect"]) for h in fv[fid].road_rects):
                ok = False
            if poly_overlaps_rect(fv[fid].river, r):
                ok = False
            for hid, rects in fv[fid].house_footprints.items():
                if any(rect_overlap(r, x2) for x2 in rects):
                    ok = False
        for k, v in landmarks.items():
            if k in ("坝", "田"):
                if rect_overlap(r, v):
                    ok = False
            elif circle_rect_overlap(v[0], v[1], v[2], r):
                ok = False
        if ok:
            xs.append(x)
    print(f"  保持 y=960 横移时全部合法 x：{xs}（最近 {min(xs, key=lambda v: abs(v-1856))}）")

    print("\n-- 9.5 界碑可达性（热点中心 = 碑心，reach 68）--")
    for fid in order:
        v = fv[fid]
        spots = []
        for dy in range(-68, 69, 4):
            for dx in range(-68, 69, 4):
                if dx * dx + dy * dy > 68 * 68:
                    continue
                px, py = sc[0] + dx, sc[1] + dy
                if not (0 <= px < WORLD_W and 0 <= py < WORLD_H):
                    continue
                if any(rect_overlap((px - 14, py - 14, 28, 28), s) for s in v.solid_rects):
                    continue
                spots.append((px, py))
        if spots:
            near = min(spots, key=lambda p: math.hypot(p[0] - sc[0], p[1] - sc[1]))
            d = math.hypot(near[0] - sc[0], near[1] - sc[1])
            print(f"  {fid:<11} 可站邻位 {len(spots):>3} 个，最近 {near} 距碑心 {d:.0f}px "
                  f"{'✔ 可检视' if d <= 68 else '✘ 超 reach'}")
        else:
            print(f"  {fid:<11} 周边无可站位 ✘")

    print("\n-- 9.6 A4/A5 同址核对 --")
    for hid in ("market",):
        p4 = fv["a4_2001"].house_pos(hid)
        p5 = fv["a5_2026"].house_pos(hid)
        print(f"  {hid}: A4 {p4} → A5 {p5} "
              f"{'同址 ✔（位置不变）' if p4 == p5 else '不同址'}")
    for hid, ah in (("shen_a4", "school"), ("zhou_a4", "toyshop")):
        b4 = bbs[hid]
        b5 = rects_bbox(a5_fp[ah])
        ox = max(0, min(b4[0] + b4[2], b5[0] + b5[2]) - max(b4[0], b5[0]))
        oy = max(0, min(b4[1] + b4[3], b5[1] + b5[3]) - max(b4[1], b5[1]))
        print(f"  {hid} ↔ A5 {ah}: 重叠 {ox}×{oy} px（{ox*oy} px²）"
              f"{' ＝ 同一栋楼转用途 ✔' if ox > 0 and oy > 0 else ''}")
    print(f"  A5 老槐 r={a5_tree['radius']} 上抬树冠圆心 "
          f"({a5_tree['center'][0]}, {a5_tree['center'][1] - a5_tree['radius']*0.7:.1f}) "
          f"右缘 x={a5_tree['center'][0] + a5_tree['radius']}；"
          f"market x 起点 {FINAL_A4['market'][0]} → "
          f"{'重叠 %dpx' % (a5_tree['center'][0] + a5_tree['radius'] - FINAL_A4['market'][0]) if a5_tree['center'][0] + a5_tree['radius'] > FINAL_A4['market'][0] else '不重叠'}")


# --------------------------------------------------------------------------
# 5. 界碑候选
# --------------------------------------------------------------------------

def reachable(view, center, reach):
    r = int(reach)
    for dy in range(-r, r + 1, 8):
        for dx in range(-r, r + 1, 8):
            if dx * dx + dy * dy > reach * reach:
                continue
            px, py = center[0] + dx, center[1] + dy
            if not (0 <= px < WORLD_W and 0 <= py < WORLD_H):
                continue
            if not any(rect_overlap((px - 14, py - 14, 28, 28), s) for s in view.solid_rects):
                return True
    return False


def section_stele(fv, houses, order):
    print()
    print("=" * 96)
    print("[4] 界碑归位候选评估（界碑必须五帧同位）")
    print("=" * 96)
    cands = [
        (1856, 960, "A1–A3 原位"),
        (1416, 1600, "A4 现状位（与 A5 红绿灯同点）"),
        (1400, 1600, "主路北侧、红绿灯西 16px"),
        (1424, 1632, "主路北沿"),
        (1296, 1536, "旧脚本候选"),
        (1312, 1536, "旧脚本候选"),
        (1296, 1504, "旧脚本候选"),
        (1360, 1504, "旧脚本候选"),
        (1856, 992, "旧脚本候选"),
        (1216, 992, "旧脚本候选"),
        (56, 1024, "school 家具「周」界碑热点位(64,1040)"),
    ]
    print(f"{'候选 rect':<24}{'A1/A2弯路':<11}{'A3-5直路':<11}{'A5竖路':<10}{'河':<6}"
          f"{'压井/槐':<11}{'压房':<7}{'A5可达':<9}{'距路':<7}备注")
    for (x, y, note) in cands:
        rect = (x, y, 16, 32)
        a12 = any(rect_overlap(rect, r["rect"]) for fid in ("a1_1926", "a2_1951")
                  for r in fv[fid].road_rects)
        a345 = rect_overlap(rect, (0, 1664, 3200, 64))
        a5v = rect_overlap(rect, (1328, 416, 64, 1248)) or \
              rect_overlap(rect, (1328, 1728, 64, 672))
        river = any(poly_overlaps_rect(fv[fid].river, rect) for fid in order)
        w = fv["a4_2001"].circle_by("井")
        t = fv["a4_2001"].circle_by("槐")
        hit_lt = (circle_rect_overlap(w["center"][0], w["center"][1], w["radius"], rect) or
                  circle_rect_overlap(t["center"][0], t["center"][1], t["radius"], rect))
        hit_house = []
        for fid in order:
            for hid, rects in fv[fid].house_footprints.items():
                if any(rect_overlap(rect, r) for r in rects):
                    hit_house.append(f"{fid}:{hid}")
        reach = reachable(fv["a5_2026"], (x + 8, y + 16), 68.0)
        d_road = min(abs(y + 32 - 1664), abs(y - 1728))
        print(f"{str((x,y,16,32)):<24}{'冲突' if a12 else 'OK':<11}"
              f"{'冲突' if a345 else 'OK':<11}{'冲突' if a5v else 'OK':<10}"
              f"{'是' if river else '否':<6}{'是' if hit_lt else '否':<11}"
              f"{('是 ' + ','.join(hit_house)) if hit_house else '否':<7}"
              f"{'是' if reach else '否':<9}{d_road:<7}# {note}")


# --------------------------------------------------------------------------
# 6. 遮挡率
# --------------------------------------------------------------------------

def circle_circle_area(r1, r2, d):
    if d >= r1 + r2:
        return 0.0
    if d <= abs(r1 - r2):
        return math.pi * min(r1, r2) ** 2
    a1 = math.acos(max(-1.0, min(1.0, (d * d + r1 * r1 - r2 * r2) / (2 * d * r1))))
    a2 = math.acos(max(-1.0, min(1.0, (d * d + r2 * r2 - r1 * r1) / (2 * d * r2))))
    return r1 * r1 * (a1 - math.sin(2 * a1) / 2) + r2 * r2 * (a2 - math.sin(2 * a2) / 2)


def section_occlusion(fv, order):
    print()
    print("=" * 96)
    print("[5] 老槐遮井遮挡率（复现 world_view.gd:568-615 的画法）")
    print("=" * 96)
    print(f"{'帧':<11}{'井 r':<7}{'槐 r':<7}{'树冠圆心':<20}{'井被盖面积':<13}{'遮挡率':<10}")
    for fid in order:
        v = fv[fid]
        w = v.circle_by("井")
        t = v.circle_by("槐")
        rj, rt = w["radius"], t["radius"]
        lifted = (t["center"][0], t["center"][1] - rt * 0.7)   # world_view.gd:598
        d = math.hypot(lifted[0] - w["center"][0], lifted[1] - w["center"][1])
        covered = circle_circle_area(rj, rt, d)
        print(f"{fid:<11}{rj:<7}{rt:<7}{str(tuple(round(x,1) for x in lifted)):<20}"
              f"{covered:<13.1f}{covered / (math.pi*rj*rj) * 100:<9.1f}%")
    print("  A4/A5 无场景贴图 → 井=平画圆、槐=色块树，走 world_view.gd:589-600 分支；")
    print("  A1–A3 有 well_old/tree 贴图 → 走 _prop_box 分支（贴图底边对齐圆底边，不上抬）。")


# --------------------------------------------------------------------------
# 7. 热点重算
# --------------------------------------------------------------------------

def house_hotspots(hdata, pos):
    """复刻 scripts/house_shape.gd:378-411 hotspots()。"""
    lot = hdata.get("lot", [0, 0, 0, 0])
    out = []
    for fd in hdata.get("furniture", []):
        if not fd.get("clue", False):
            continue
        r = fd.get("rect", [0, 0, 1, 1])
        if int(r[0]) < int(lot[0]) or int(r[1]) < int(lot[1]) or \
           int(r[0]) + int(r[2]) - 1 > int(lot[2]) or \
           int(r[1]) + int(r[3]) - 1 > int(lot[3]):
            continue
        name = str(fd.get("name", "家具"))
        title = name
        if name == "老井":
            title = "%s · 院里" % str(hdata.get("name", "")).split("·")[0].strip()
        cx = pos[0] + (float(r[0]) + float(r[2]) * 0.5) * TILE
        cy = pos[1] + (float(r[1]) + float(r[3]) * 0.5) * TILE
        out.append((title, round(cx, 1), round(cy, 1), name, str(fd.get("note", ""))))
    return out


def section_hotspots(fv, houses, order):
    print()
    print("=" * 96)
    print("[6] 房子 clue 家具热点重算（house_shape.gd:378-411 规则）+ 证物 key 清单")
    print("=" * 96)
    keys = []
    for fid in order:
        v = fv[fid]
        rows = []
        for hs in v.house_shapes:
            hd = houses.get(hs["id"])
            if not hd:
                continue
            for (title, cx, cy, name, note) in house_hotspots(hd, hs["pos"]):
                rows.append((title, cx, cy, hs["id"], name))
                keys.append(("%s::%s" % (hs["id"], name), title, fid))
        print(f"  {fid}:")
        for (title, cx, cy, hid, name) in rows:
            print(f"      {title:<18} pos=({cx},{cy})  key={hid}::{name}")
    print("\n  世界地标热点（key = title，跨时代同名算同一件）：")
    for fid in order:
        v = fv[fid]
        for h in v.hotspots:
            if not h.get("house_id", ""):
                print(f"      {fid:<11} '{h['title']}' pos={h['pos']} reach={h.get('reach')}")
    print("\n  证物 key 汇总（家具 key = house_id::家具名；地标 key = title）：")
    seen = {}
    for (k, title, fid) in keys:
        seen.setdefault(k, []).append(fid)
    for k in sorted(seen):
        print(f"      {k:<28} 出现在 {','.join(seen[k])}")
    print("      井相关：", [k for k in sorted(seen) if "井" in k])
    print("      界碑相关：", [k for k in sorted(seen) if "界碑" in k])


# --------------------------------------------------------------------------
# 4b. 超市合法落点枚举 / 界碑候选位优化（lead 追加问题）
# --------------------------------------------------------------------------

def tree_protect_circles(fv, order):
    """老槐的「遮挡圆」= 原始圆 ∪ 上抬 0.7r 的树冠圆（world_view.gd:589-600）。
    井同理取各帧最大半径。"""
    out = []
    for fid in order:
        v = fv[fid]
        t = v.circle_by("槐")
        if t:
            c, r = t["center"], t["radius"]
            out.append((c[0], c[1], r))
            out.append((c[0], c[1] - r * 0.7, r))
        w = v.circle_by("井")
        if w:
            out.append((w["center"][0], w["center"][1], w["radius"]))
    return out


def market_positions(fv, houses, order, *, protect_a5=True, y_min=None,
                     market_a5_pos=(1440, 768)):
    """超市(market)作为 A4=A5 同址房子时，路北的所有合法落点。"""
    a4, a5 = fv["a4_2001"], fv["a5_2026"]
    river = a4.river
    prot = tree_protect_circles(fv, order)
    if not protect_a5:
        prot = [p for p in prot
                if not (p[2] >= 160 and abs(p[1] - (976 - 160 * 0.7)) < 1
                        or (p[2] == 160))]
    obst = []
    for hid in ("school", "toyshop"):
        p = a5.house_pos(hid)
        hd = houses.get(hid)
        if p and hd:
            for r in wings_rects(hd, p):
                obst.append(r)
    out = []
    for gx in range(0, int((WORLD_W - 1344) // 32) + 1):
        for gy in range(0, int((WORLD_H - 896) // 32) + 1):
            pos = (gx * 32, gy * 32)
            if y_min is not None and pos[1] < y_min:
                continue
            bb = (pos[0], pos[1], 1344, 896)
            if bb[1] + bb[3] > ROAD_BAND[0]:
                continue
            if poly_overlaps_rect(river, bb):
                continue
            bad = False
            for (cx, cy, r) in prot:
                if circle_rect_overlap(cx, cy, r, bb):
                    bad = True
                    break
            if bad:
                continue
            for o in obst:
                if rect_overlap(bb, o):
                    bad = True
                    break
            if bad:
                continue
            out.append(pos)
    return out


def section_market_positions(fv, houses, order):
    print()
    print("=" * 96)
    print("[7] 超市(market)作为 A4=A5 同址房子的合法落点枚举")
    print("=" * 96)
    for label, kw in (
            ("口径 A：只避让 A4 帧的老槐(r=96)+老井(r=32)",
             dict(protect_a5=False)),
            ("口径 B：避让全部五帧的老槐/老槐树冠/老井（含 A5 老槐 r=160）",
             dict(protect_a5=True)),
            ("口径 B + y>=576（与 lead 的 91 个口径对齐）",
             dict(protect_a5=True, y_min=576))):
        ps = market_positions(fv, houses, order, **kw)
        xs = sorted(set(p[0] for p in ps))
        ys = sorted(set(p[1] for p in ps))
        print(f"  {label}")
        print(f"      合法落点 = {len(ps)} 个；x 取值 {xs}")
        print(f"      y 取值 {ys}")
        print(f"      (1440,768) 是否合法：{'是' if (1440,768) in ps else '否'}")
    # 解释 x=1440 为什么在口径 B 下非法
    v = fv["a5_2026"]
    t = v.circle_by("槐")
    lift = (t["center"][0], t["center"][1] - t["radius"] * 0.7)
    print(f"  口径 B 下 x=1440 非法的原因：A5 老槐 r={t['radius']}，"
          f"上抬 0.7r 后树冠圆心 {lift}，树冠右缘 x={lift[0]+t['radius']} > 1440"
          f" → 与超市足迹重叠 {lift[0]+t['radius']-1440}px")


def stele_candidates(fv, houses, order, frames=("a1_1926", "a2_1951", "a3_1976",
                                                 "a4_2001"),
                     market_pos=(1440, 768), origin=(1864, 976),
                     include_a5=False, top=12):
    """界碑候选位：必须在其余各帧都合法（不压井/槐/田/坝/路/房、不进河、可站立检视）。"""
    frames = list(frames) + (["a5_2026"] if include_a5 else [])
    market_bb = (market_pos[0], market_pos[1], 1344, 896)
    out = []
    for gx in range(0, (WORLD_W - 16) // 32 + 1):
        for gy in range(0, (WORLD_H - 32) // 32 + 1):
            x, y = gx * 32, gy * 32
            rect = (x, y, 16, 32)
            ok = True
            notes = []
            for fid in frames:
                v = fv[fid]
                if any(rect_overlap(rect, r["rect"]) for r in v.road_rects):
                    ok = False
                    notes.append(f"{fid}:压路")
                    break
                if poly_overlaps_rect(v.river, rect):
                    ok = False
                    notes.append(f"{fid}:压河")
                    break
                hit = None
                for hid, rects in v.house_footprints.items():
                    if any(rect_overlap(rect, r) for r in rects):
                        hit = hid
                        break
                if hit is None and fid == "a4_2001" and rect_overlap(rect, market_bb):
                    hit = "market(A4 同址)"
                if hit:
                    ok = False
                    notes.append(f"{fid}:压房{hid}")
                    break
                w = v.circle_by("井")
                t = v.circle_by("槐")
                if circle_rect_overlap(w["center"][0], w["center"][1], w["radius"], rect):
                    ok = False
                    notes.append(f"{fid}:压井")
                    break
                if circle_rect_overlap(t["center"][0], t["center"][1], t["radius"], rect) or \
                   circle_rect_overlap(t["center"][0], t["center"][1] - t["radius"] * 0.7,
                                       t["radius"], rect):
                    ok = False
                    notes.append(f"{fid}:压槐")
                    break
                if v.rect_by("田") and rect_overlap(rect, v.rect_by("田")):
                    ok = False
                    notes.append(f"{fid}:压田")
                    break
                if v.rect_by("坝") and rect_overlap(rect, v.rect_by("坝")):
                    ok = False
                    notes.append(f"{fid}:压坝")
                    break
            if not ok:
                continue
            if not reachable(fv["a4_2001"], (x + 8, y + 16), 68.0):
                continue
            if not reachable(fv["a1_1926"], (x + 8, y + 16), 68.0):
                continue
            d = math.hypot((x + 8) - origin[0], (y + 16) - origin[1])
            out.append((d, (x, y), notes))
    out.sort(key=lambda t: (t[0], t[1]))
    return out[:top]


def section_stele_search(fv, houses, order):
    print()
    print("=" * 96)
    print("[8] 界碑候选位优化（按「离原位(1864,976)近」排序）")
    print("=" * 96)
    for label, kw in (
            ("A1–A4 全部合法（A5 界碑进学校围墙，故 A5 不放世界碑）",
             dict(frames=("a1_1926", "a2_1951", "a3_1976", "a4_2001"),
                  market_pos=(1440, 768), include_a5=False)),
            ("A1–A5 全部合法（世界碑五帧都在）",
             dict(frames=("a1_1926", "a2_1951", "a3_1976", "a4_2001"),
                  market_pos=(1440, 768), include_a5=True)),
            ("A1–A4 合法，超市改钉在 (1472,768)",
             dict(frames=("a1_1926", "a2_1951", "a3_1976", "a4_2001"),
                  market_pos=(1472, 768), include_a5=False))):
        print(f"  {label}")
        cands = stele_candidates(fv, houses, order, **kw)
        print(f"      合法候选共（取前 {len(cands)}）：")
        for (d, (x, y), notes) in cands[:8]:
            print(f"        ({x},{y}) rect=({x},{y},16,32) 距原位={d:.0f}px"
                  f"  距主路={min(abs(y+32-1664), abs(y-1728))}px")
        if not cands:
            print("        （无解）")
    # 单独核对 lead 建议的两个点
    print("\n  lead 建议点单独核对：")
    for p in ((1296, 1472), (2816, 960)):
        x, y = p
        rect = (x, y, 16, 32)
        bad = []
        for fid in order:
            v = fv[fid]
            if any(rect_overlap(rect, r["rect"]) for r in v.road_rects):
                bad.append(f"{fid}:压路")
            if poly_overlaps_rect(v.river, rect):
                bad.append(f"{fid}:压河")
            for hid, rects in v.house_footprints.items():
                if any(rect_overlap(rect, r) for r in rects):
                    bad.append(f"{fid}:压房{hid}")
            t = v.circle_by("槐")
            w = v.circle_by("井")
            if circle_rect_overlap(t["center"][0], t["center"][1], t["radius"], rect):
                bad.append(f"{fid}:压槐")
            if circle_rect_overlap(w["center"][0], w["center"][1], w["radius"], rect):
                bad.append(f"{fid}:压井")
        r5 = reachable(fv["a5_2026"], (x + 8, y + 16), 68.0)
        r1 = reachable(fv["a1_1926"], (x + 8, y + 16), 68.0)
        d = math.hypot((x + 8) - 1864, (y + 16) - 976)
        print(f"        ({x},{y}): 距原位 {d:.0f}px  A1可达={r1} A5可达={r5} "
              f"冲突={bad if bad else '无'}")


# --------------------------------------------------------------------------

def main():
    frames, houses = load_data()
    order = [f["id"] for f in frames["frames"]]
    fv = build = {f["id"]: FrameView(f, houses) for f in frames["frames"]}
    if not ONLY_SOLVE:
        section_consistency(fv, order)
        section_land(fv, houses, order)
    section_solve(fv, houses, order)
    section_market_positions(fv, houses, order)
    section_stele_search(fv, houses, order)
    section_stele(fv, houses, order)
    section_occlusion(fv, order)
    section_hotspots(fv, houses, order)
    section_final(fv, houses, order)
    print()
    print("SOLVER_DONE")


if __name__ == "__main__":
    main()
