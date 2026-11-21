# -*- coding: utf-8 -*-
"""按**最新** houses_data.json 重绘 A1 整帧布局（房子 + 路）。

背景：houses_data.json 在 13:22 被另一条线改过，所有房子 lot 都变高了：
  mill_a1/shen_a1/lu_house 从 10 格高 → 13 格高
  zhou_house 从 6 → 7 格高
frames.json 里的坐标是按旧尺寸算的，全过期了。

本轮目标（用户 2026-11-21）：
  1. 路不能压房子
  2. A1 的路要有 3 格起伏（不能太直）

设计（格）：
  河    y0..7（弯曲下缘，不动）
  坝    x12..19 y3..6
  磨坊   x38..55, 13 格高 → y14..26
  沈家   x4..23,  13 格高 → y20..32
  周家   x56..67,  7 格高 → y46..52
  陆家   x72..91, 13 格高 → y22..34
  老井  (42,26) 老槐 (40,30) 碑 (58,30)

  路的安全带：沈家到 y32、陆家到 y34、周家从 y46
  → 可用 y35..45（11 格），足够做 3 格起伏
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TILE = 16
ROAD_W = 3

# 房子原点（按最新 lot 高度定位；x 保持原设计）
HOUSE_POS = {
    "mill_a1":    (608, 224),     # 格(38,14)
    "shen_a1":    (64, 320),      # 格(4,20)
    "zhou_house": (896, 736),     # 格(56,46)
    "lu_house":   (1152, 352),    # 格(72,22)
}

# 路带：(x0, x1, y_top)，高固定 3 格
# 3 格起伏：基准 y35..37 → 抬到 y32..34（高3格）→ 回落 → 再降到底 y38..40
A1_SEGMENTS = [
    (0,  11, 36),        # 西段：y36..38
    (12, 15, 35),        # 上坡 1
    (16, 19, 34),        # 上坡 2
    (20, 23, 33),        # 上坡 3（到顶）
    (24, 43, 33),        # 顶段平
    (44, 47, 34),        # 下坡 1
    (48, 51, 35),        # 下坡 2
    (52, 63, 36),        # 中段平
    (64, 67, 37),        # 下坡 1
    (68, 71, 38),        # 下坡 2
    (72, 75, 39),        # 下坡 3（到底）
    (76, 99, 39),        # 东段平
]


def segs_to_tiles(segs, width=ROAD_W):
    s = set()
    for (x0, x1, ytop) in segs:
        for y in range(ytop, ytop + width):
            for x in range(x0, x1 + 1):
                s.add((x, y))
    return s


def tiles_to_rects(tiles):
    if not tiles:
        return []
    rows = {}
    for (x, y) in tiles:
        rows.setdefault(y, []).append(x)
    segs = []
    for y in sorted(rows):
        xs = sorted(rows[y])
        start = prev = xs[0]
        for x in xs[1:]:
            if x == prev + 1:
                prev = x
                continue
            segs.append((start, prev, y))
            start = prev = x
        segs.append((start, prev, y))
    segs.sort(key=lambda s: (s[2], s[0]))
    consumed = [False] * len(segs)
    rects = []
    for i, (x0, x1, y) in enumerate(segs):
        if consumed[i]:
            continue
        consumed[i] = True
        cx0, cx1, cy0, cy1 = x0, x1, y, y
        while True:
            found = -1
            for j, (nx0, nx1, ny) in enumerate(segs):
                if consumed[j] or ny != cy1 + 1:
                    continue
                if nx0 == cx0 and nx1 == cx1:
                    found = j
                    break
            if found < 0:
                break
            nx0, nx1, ny = segs[found]
            consumed[found] = True
            cy1 = ny
        rects.append((cx0, cy0, cx1 - cx0 + 1, cy1 - cy0 + 1))
    return rects


def house_cells_from_pos(fix, by_id):
    s = set()
    for hid, (px, py) in fix.items():
        hd = by_id.get(hid)
        if not hd:
            continue
        lot = hd["lot"]
        gw, gh = lot[2] - lot[0] + 1, lot[3] - lot[1] + 1
        for yy in range(py // TILE, py // TILE + gh):
            for xx in range(px // TILE, px // TILE + gw):
                s.add((xx, yy))
    return s


def preview(tiles, houses, x_max=72, y_range=None):
    ys = y_range or ([t[1] for t in tiles] + [h[1] for h in houses])
    lo, hi = min(ys) - 1, max(ys) + 1
    out = []
    for gy in range(lo, hi + 1):
        row = ""
        for gx in range(0, x_max):
            if (gx, gy) in tiles:
                row += "#"
            elif (gx, gy) in houses:
                row += "H"
            else:
                row += "."
        out.append("y=%2d %s" % (gy, row))
    return "\n".join(out)


def main():
    p = os.path.join(ROOT, "data", "frames.json")
    doc = json.load(open(p, encoding="utf-8"))
    hp = os.path.join(HERE, "houses_data.json")
    by_id = {h["id"]: h for h in json.load(open(hp, encoding="utf-8"))}

    for f in doc["frames"]:
        if f["id"] != "a1_1926":
            continue

        # 1) 更新房子位置（按最新 lot 尺寸）
        for sh in f["shapes"]:
            if sh.get("type") == "house" and sh["id"] in HOUSE_POS:
                old = sh["pos"]
                sh["pos"] = list(HOUSE_POS[sh["id"]])
                print("房子 %-12s %s → %s" % (sh["id"], old, sh["pos"]))

        # 2) 生成路 + 检查冲突
        houses = house_cells_from_pos(HOUSE_POS, by_id)
        tiles = segs_to_tiles(A1_SEGMENTS)
        clash = tiles & houses
        print("\n压房格数:", len(clash))
        if clash:
            for c in sorted(clash)[:10]:
                print("   ", c)
            tiles -= houses

        # 3) 写回
        rects = tiles_to_rects(tiles)
        kept = [s for s in f["shapes"] if s.get("type") != "path" and not s.get("road")]
        new_road = []
        for idx, (rx, ry, rw, rh) in enumerate(rects):
            new_road.append({
                "type": "rect",
                "rect": [rx * TILE, ry * TILE, rw * TILE, rh * TILE],
                "color": "#8a7a5a",
                "label": "路" if idx == 0 else "",
                "road": True,
            })
        f["shapes"] = kept + new_road

        print("\nA1 路面 %d 矩形:" % len(new_road))
        for (rx, ry, rw, rh) in rects:
            print("   (%3d,%3d) %2d格 x %d格" % (rx, ry, rw, rh))
        print()
        print(preview(tiles, houses, y_range=[y for y in range(19, 55)]))

    json.dump(doc, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("\nwritten")


if __name__ == "__main__":
    main()
