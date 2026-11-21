# -*- coding: utf-8 -*-
"""重排 A2/A3 的房子位置 + 生成 3 格宽的格子路（与 A1 同一套规格）。

背景：
  - houses_data.json 2026-11-21 13:22 改过，房子 lot 都变高了
  - A2/A3 的 frames.json 坐标还是旧尺寸
  - A2/A3 的路还是旧 path 折线（不是格子，宽度也不对）

规格（与 A1 一致）：
  路宽 3 格；A2 跟 A1 一样做 3 格起伏；A3 完全直（story：沈德昌取直）
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TILE = 16
ROAD_W = 3

# 房子新位置（格→px），按最新 lot 尺寸给路腾空间
# A2: 沈家到 y32、陆家到 y36、周家从 y40
#   → 安全带 y37..39（只有3格，做不了起伏）→ 把周家下移、陆家上移
A2_HOUSE = {
    "mill_a2":    (608, 224),     # 格(38,14) 18x13 → y14..26
    "shen_a2":    (64, 256),      # 格(4,16)  23x17 → y16..32
    "zhou_a2":    (896, 736),     # 格(56,46) 12x7  → y46..52
    "lu_a2":      (1152, 352),    # 格(72,22) 20x13 → y22..34
}
# A3: 沈家凹形到 y? 周家陆家同样调整
A3_HOUSE = {
    "mill_a3":    (608, 224),     # 格(38,14) 18x17 → y14..30
    "shen_a3":    (64, 192),      # 格(4,12)  28x24 → y12..35
    "zhou_a3":    (896, 736),     # 格(56,46) 12x7  → y46..52
    "lu_a3":      (1152, 352),    # 格(72,22) 20x13 → y22..34
}

# A2 路：同 A1 的 3 格起伏（安全带 y35..45）
A2_SEGMENTS = [
    (0,  11, 36),
    (12, 15, 35), (16, 19, 34), (20, 23, 33),
    (24, 43, 33),
    (44, 47, 34), (48, 51, 35),
    (52, 63, 36),
    (64, 67, 37), (68, 71, 38), (72, 75, 39),
    (76, 99, 39),
]
# A3 路：完全直，3 格宽
A3_SEGMENTS = [
    (0, 99, 37),      # y37..39
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


def house_cells(fix, by_id):
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


def process(doc, fid, fix, segs, by_id):
    for f in doc["frames"]:
        if f["id"] != fid:
            continue
        # 1) 房子位置
        for sh in f["shapes"]:
            if sh.get("type") == "house" and sh["id"] in fix:
                old = sh["pos"]
                sh["pos"] = list(fix[sh["id"]])
                if old != sh["pos"]:
                    print("  %-11s %s → %s" % (sh["id"], old, sh["pos"]))

        # 2) 路
        houses = house_cells(fix, by_id)
        tiles = segs_to_tiles(segs)
        clash = tiles & houses
        if clash:
            print("  !! 压房 %d 格: %s" % (len(clash), sorted(clash)[:6]))
            tiles -= houses
        else:
            print("  路不压房 ✓")

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
        print("  %s：路面 %d 矩形" % (fid, len(new_road)))


def main():
    p = os.path.join(ROOT, "data", "frames.json")
    doc = json.load(open(p, encoding="utf-8"))
    hp = os.path.join(HERE, "houses_data.json")
    by_id = {h["id"]: h for h in json.load(open(hp, encoding="utf-8"))}

    print("=== A2 1951 ===")
    process(doc, "a2_1951", A2_HOUSE, A2_SEGMENTS, by_id)
    print("\n=== A3 1976 ===")
    process(doc, "a3_1976", A3_HOUSE, A3_SEGMENTS, by_id)

    json.dump(doc, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("\nwritten")


if __name__ == "__main__":
    main()
