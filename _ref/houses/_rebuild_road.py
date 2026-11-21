# -*- coding: utf-8 -*-
"""重设 A1/A2/A3 的路 —— 直接用矩形段描述，不走路径推导。

为什么：路径推导 + 各种加宽/补齐策略反复出问题（1 格细条、凹口断口、
x 负坐标、矩形被切碎）。用户要的其实很简单：

  A1/A2：一条 3 格宽的路，中段缓缓起伏（抬高 1 格），**不能有凹口断口**
  A3   ：一条 3 格宽的直路

所以直接写矩形段。每段都是 3 格高，段与段之间用「过渡段」错开 1 格，
视觉上是缓坡，且**绝不出现 1 格高的细条**。

坐标（格）：
  主路基准带 y=36..38（3 格高）
  起伏段抬 1 格 → y=35..37
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TILE = 16
ROAD_W = 3

BASE_Y = 36          # 主路带顶部格（覆盖 36,37,38）

# 每项 (x0, x1, y_top)，闭区间；高固定 ROAD_W 格
# A1/A2：西段平 → 中段抬 1 格（缓坡）→ 东段回平
# 过渡段（宽度 2 格）用来填平台阶处的豁口，避免出现「少一格」的缺口。
A12_SEGMENTS = [
    (0,  21, BASE_Y),        # 西段：y 36..38
    (22, 23, BASE_Y - 1),    # 上坡过渡：y 35..37（与西段在上方连）
    (24, 51, BASE_Y - 1),    # 起伏段：y 35..37
    (52, 53, BASE_Y - 1),    # 下坡过渡：y 35..37
    (54, 99, BASE_Y),        # 东段：y 36..38
]
# A3：一路平
A3_SEGMENTS = [
    (0, 99, BASE_Y),
]


def segs_to_tiles(segs, width=ROAD_W):
    s = set()
    for (x0, x1, ytop) in segs:
        for y in range(ytop, ytop + width):
            for x in range(x0, x1 + 1):
                s.add((x, y))
    return s


def tiles_to_rects(tiles):
    """格集合 → 矩形（同行合并段，再上下合并等宽段）。段都是规整矩形，结果会很少。"""
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


def preview(tiles, x_max=70):
    ys = [t[1] for t in tiles]
    out = []
    for gy in range(min(ys), max(ys) + 1):
        out.append("y=%2d %s" % (gy, "".join("#" if (gx, gy) in tiles else "."
                                              for gx in range(0, x_max))))
    return "\n".join(out)


def main():
    p = os.path.join(ROOT, "data", "frames.json")
    doc = json.load(open(p, encoding="utf-8"))

    for f in doc["frames"]:
        fid = f["id"]
        if fid in ("a1_1926", "a2_1951"):
            segs = A12_SEGMENTS
        elif fid == "a3_1976":
            segs = A3_SEGMENTS
        else:
            continue
        tiles = segs_to_tiles(segs)
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
        print("== %s  路面 %d 矩形" % (fid, len(new_road)))
        for (rx, ry, rw, rh) in rects:
            print("    (%3d,%3d) %2d格 x %d格" % (rx, ry, rw, rh))
        if fid == "a1_1926":
            print(preview(tiles))
        print()

    json.dump(doc, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("written")


if __name__ == "__main__":
    main()
