# -*- coding: utf-8 -*-
"""把 _design_v5 的格坐标布局落地成 data/frames.json。

格 → 像素：px = 格 * TILE（TILE 由 _design_v5 单点提供）。
河 / 田 / 路 用格子集合压成大矩形或折线；房子用 house 形状（读 houses_data.json）。
"""
import json, os, math, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

spec = importlib.util.spec_from_file_location("d5", os.path.join(HERE, "_design_v5.py"))
dv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dv)

TILE = dv.TILE          # 引用单一真相源，别再写死 16/32

by_id = dv.by_id


def px(v):
    return int(v) * TILE


# ---------- 河：格子 → 折线（下缘轮廓） ----------
def river_path_points():
    """把逐列河深转成一条闭合折线：上边 y=0 → 右边下缘 → 下缘曲线 → 左边。"""
    pts = []
    # 上边从右到左（简化：直接画矩形到最深处，再用下缘折线覆盖背景）
    for x in range(0, dv.GW):
        pts.append([px(x), px(dv.river_depth(x) + 1)])
    for x in range(dv.GW - 1, -1, -1):
        pts.append([px(x), 0])
    return pts


def river_shape():
    """河用 polygon 画（下缘是弯曲的）。返回 points 列表。"""
    pts = []
    for x in range(0, dv.GW):
        pts.append([px(x), px(dv.river_depth(x) + 1)])
    pts.append([px(dv.GW), px(dv.river_depth(dv.GW - 1) + 1)])
    pts.append([px(dv.GW), 0])
    pts.append([0, 0])
    return pts


# ---------- 田：格子集合 → 矩形列表（相邻同色合并成行，减少 JSON 体积） ----------
def cells_to_rects(cells):
    """把格子集合合并成矩形（按行扫描，合并连续段；再合并上下相邻等宽段）。"""
    if not cells:
        return []
    rows = {}
    for (x, y) in cells:
        rows.setdefault(y, []).append(x)
    segs = []
    for y in sorted(rows):
        xs = sorted(rows[y])
        start = xs[0]
        prev = xs[0]
        for x in xs[1:]:
            if x == prev + 1:
                prev = x
                continue
            segs.append((start, y, prev - start + 1))
            start = x
            prev = x
        segs.append((start, y, prev - start + 1))
    # 合并上下同 x 同宽的段
    merged = []
    used = [False] * len(segs)
    segs.sort(key=lambda s: (s[1], s[0]))
    for i, (sx, sy, sw) in enumerate(segs):
        if used[i]:
            continue
        h = 1
        j = i + 1
        while j < len(segs):
            tx, ty, tw = segs[j]
            if tx == sx and tw == sw and ty == sy + h and not used[j]:
                used[j] = True
                h += 1
                j += 1
            else:
                break
        merged.append((sx, sy, sw, h))
    return merged


# ---------- 路：走 cells_to_rects（逐格 rect + road 标记），不再出折线 ----------
# 旧实现 road_points_a123() 已删除：它出的是 path 中心线，边缘不对齐格子且带抗锯齿，
# 美术没法直接铺瓦片。现在路和「田」共用同一个格集合→矩形合并函数。


def build_frames():
    frames = []
    for fid, ids in dv.FRAMES.items():
        meta = dv.META[fid]
        year = int(fid.split("_")[1])
        ground = meta["ground"]
        shapes = []

        # 1. 河（多边形，弯曲下缘）
        shapes.append({
            "type": "polygon",
            "points": river_shape(),
            "color": "#%02x%02x%02x" % meta["river"],
            "label": "河",
            "solid": True,
        })
        # 2. 坝
        dminx = min(c[0] for c in dv.DAM_CELLS)
        dmaxx = max(c[0] for c in dv.DAM_CELLS) + 1
        dminy = min(c[1] for c in dv.DAM_CELLS)
        dmaxy = max(c[1] for c in dv.DAM_CELLS) + 1
        shapes.append({
            "type": "rect",
            "rect": [px(dminx), px(dminy), px(dmaxx - dminx), px(dmaxy - dminy)],
            "color": "#6a5648",
            "label": "坝",
            "solid": True,
        })
        # 3. 路：逐格 rect + road 标记（**不用 path 折线**）。
        # 为什么：path 是「中心线 + 线宽」，边缘落在格子中间、且 draw_polyline 带抗锯齿，
        # 像素风里瓦片永远对不齐；rect 每块正好整格，美术能直接铺 32px 路瓦片。
        # ROAD_SETS 是 _design_v5 里已经膨胀过的格子集合，和「田」共用同一个合并函数。
        road_rects = cells_to_rects(dv.ROAD_SETS[fid])
        for k, (rx, ry, rw, rh) in enumerate(road_rects):
            shapes.append({
                "type": "rect",
                "rect": [px(rx), px(ry), px(rw), px(rh)],
                "color": "#8a7a5a",
                "label": "路" if k == 0 else "",
                "road": True,
            })
        # 4. 田（不规则/规整）
        for (rx, ry, rw, rh) in cells_to_rects(dv.FIELDS[fid]):
            shapes.append({
                "type": "rect",
                "rect": [px(rx), px(ry), px(rw), px(rh)],
                "color": "#%02x%02x%02x" % meta["field"],
            })
        # 5. 房子
        for hid in ids:
            lx, ly = dv.PLACE[hid]
            shapes.append({
                "type": "house", "id": hid,
                "pos": [px(lx), px(ly)], "solid": True,
            })
        # 6. 井 / 槐 / 碑
        wx, wy = dv.WELL_CELL
        shapes.append({
            "type": "circle", "center": [px(wx) + TILE // 2, px(wy) + TILE // 2],
            "radius": TILE,
            "color": "#2e3232" if fid == "a1_1926" else "#4a4a46",
            "label": "老井" if fid == "a1_1926" else ("老井·石板" if fid == "a2_1951" else "老井·水泥"),
            "solid": fid == "a1_1926",
        })
        tx, ty = dv.TREE_CELL
        shapes.append({
            "type": "circle", "center": [px(tx) + TILE // 2, px(ty) + TILE // 2],
            "radius": (dv.TREE_DIAMETER[fid] // 2) * TILE,
            "color": "#3f6b3a",
            "label": "老槐",
        })
        sx, sy = dv.STELE_CELL
        shapes.append({
            "type": "rect",
            "rect": [px(sx), px(sy), TILE // 2, TILE],
            "color": "#8a8278", "label": "碑", "solid": True,
        })

        frames.append({
            "id": fid, "year": year,
            "ground": "#%02x%02x%02x" % ground,
            "shapes": shapes,
            "hotspots": [],      # 检视点下一步单独写
        })
    return frames


# ---------- 检视点 ----------
def build_hotspots(fid):
    hs = []
    # 老井
    wx, wy = dv.WELL_CELL
    well_c = [px(wx) + TILE // 2, px(wy) + TILE // 2]
    if fid == "a1_1926":
        hs.append({"pos": well_c, "title": "老井", "reach": 80,
                   "text": "井口是木架，绳子在井沿上磨出一道沟。水面离地不到一尺。"})
    elif fid == "a2_1951":
        hs.append({"pos": well_c, "title": "老井 · 石板", "reach": 80,
                   "text": "井口盖了一块石板，四边和地面几乎齐平。石板接缝里的土是新的。"})
    elif fid == "a3_1976":
        hs.append({"pos": well_c, "title": "老井 · 三层水泥", "reach": 88,
                   "text": "三层水泥。最上一层和地面几乎一样平，边上留了一道没抹完的缝。"})
    # 老槐
    tx, ty = dv.TREE_CELL
    tree_c = [px(tx) + TILE // 2, px(ty) + TILE // 2]
    if fid == "a1_1926":
        hs.append({"pos": tree_c, "title": "老槐", "reach": 68,
                   "text": "老槐树，今年刚栽下。树干还细，根边堆着新土。"})
    elif fid == "a2_1951":
        hs.append({"pos": tree_c, "title": "老槐", "reach": 80,
                   "text": "老槐树，二十五岁。树干朝远离井的方向歪过去——井那侧的地面，像是塌下去了一点。"})
    elif fid == "a3_1976":
        hs.append({"pos": tree_c, "title": "老槐", "reach": 88,
                   "text": "老槐树，四十九岁。树干朝西北歪出去，井那侧的地面塌下去一块，树根有一半露在土外面。"})
    # 界碑
    sx, sy = dv.STELE_CELL
    hs.append({"pos": [px(sx) + TILE // 4, px(sy) + TILE // 2], "title": "界碑", "reach": 68,
               "text": "半截石碑，埋在路边的土里。字被凿过，只剩两个：「周界」。"})
    # 坝
    hs.append({"pos": [px(16), px(5)], "title": "坝", "reach": 140,
               "text": "一道石坝横在河身里。水面在坝前抬高了几寸，从坝顶漫过去。"})
    # 田
    if fid == "a1_1926":
        hs.append({"pos": [px(66), px(10)], "title": "田", "reach": 96,
                   "text": "几块零散的小田，地界歪歪扭扭。土是干的。田埂上的草被踩出一条路，通向磨坊。"})
    else:
        hs.append({"pos": [px(66), px(10)], "title": "田", "reach": 96,
                   "text": "田已经归并成整块。田埂是直的，一头挨着另一头。土还是干的。"})
    return hs


def main():
    frames = build_frames()
    for f in frames:
        f["hotspots"] = build_hotspots(f["id"])

    # 保留 A4 / A5 的旧数据（本轮设计只覆盖 A1–A3；A4 还没有设计，A5 只有环岛）
    old_path = os.path.join(ROOT, "data", "frames.json")
    old_by_id = {}
    if os.path.exists(old_path):
        try:
            old = json.load(open(old_path, encoding="utf-8"))
            for f in old.get("frames", []):
                old_by_id[f["id"]] = f
        except Exception:
            pass
    for keep in ("a4_2001", "a5_2026"):
        if keep in old_by_id and keep not in [f["id"] for f in frames]:
            frames.append(old_by_id[keep])
    frames.sort(key=lambda f: f["year"])

    doc = {
        "world": {"width": dv.W, "height": dv.H},
        "safe_top": 36,
        "safe_bottom": 668,
        # 起点：老槐西侧约 8 格（原先的 -260px 是裸像素，TILE 翻倍后会缩成 4 格），
        # 纵向落在主路中央（ROAD_Y 是路中线所在格）。
        "start_pos": [px(dv.TREE_CELL[0]) - 8 * TILE, px(36) + TILE // 2],
        "frames": frames,
    }
    out = old_path
    with open(out, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print("written", out)
    for f in frames:
        print("  %-10s year=%d shapes=%2d hotspots=%d" % (
            f["id"], f["year"], len(f["shapes"]), len(f["hotspots"])))


if __name__ == "__main__":
    main()
