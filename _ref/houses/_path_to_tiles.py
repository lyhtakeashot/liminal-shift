# -*- coding: utf-8 -*-
"""把 frames.json 里的 path（折线）改成 tiles（格子集合），实现像素格路。

为什么改：
  现在 `draw_polyline` 画任意角度斜线，像素画里会出现锯齿边，
  美术每遇到一个新弯度就得画一套斜角图块 —— 不可维护。
  改成「逐格填方块」后，路只有三种图块：
    水平段 / 垂直段 / 直角转弯（4 个朝向），加上 T 字和十字即可拼出任何路。
  这也是星露谷的做法（path 是 tile 网格）。

算法：把折线经过的每个格标记为路面，宽 2 格（与原来 width=32 一致）。
"""
import json, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TILE = 16
ROAD_TILES = 3          # 路宽 3 格（48px，比原 32px 宽；村道通常更宽）


def bresenham(x0, y0, x1, y1):
    """格坐标直线上所有格。"""
    pts = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        pts.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy
    return pts


def orthogonalize(cells):
    """把斜线段拆成"先横后竖"的直角折线（L 形连接）。
    这样路径只含水平和垂直段，膨胀后得到规整的 3 格宽道路，
    而不是斜着走的楼梯。

    cells: [(x, y), ...] 折线格坐标
    返回：直角化后的格列表（每段直线的所有格）。"""
    out = []
    for i in range(len(cells) - 1):
        x0, y0 = cells[i]
        x1, y1 = cells[i + 1]
        if x0 == x1 or y0 == y1:
            # 已经是直的
            for c in bresenham(x0, y0, x1, y1):
                out.append(c)
        else:
            # 斜段 → L 形：先水平到 x1，再垂直到 y1
            # 这样转角是明确的直角，美术只需"直段 + 转角"两种图块
            mid = (x1, y0)
            for c in bresenham(x0, y0, mid[0], mid[1]):
                out.append(c)
            for c in bresenham(mid[0], mid[1], x1, y1):
                out.append(c)
    return out


def path_to_tiles(points, width=ROAD_TILES, blocked=None):
    """折线（像素坐标）→ 路面格集合。

    三步：
      1. 像素点 → 格坐标
      2. **直角化**：斜段拆成"先横后竖"，路径只含水平/垂直段
         （这样美术只需要"直段 + 转角"两种图块，不用画斜角图块）
      3. **形态学膨胀**到 width 格宽（等宽，转角自然圆润）

    blocked = 房子占用格（加宽时跳过）。"""
    cells = [(int(round(p[0] / TILE)), int(round(p[1] / TILE))) for p in points]
    center_list = orthogonalize(cells)
    center = set(center_list)

    radius = (width - 1) / 2.0
    tiles = set()
    blk = blocked or set()
    r_i = int(math.ceil(radius))
    for (cx, cy) in center:
        for dy in range(-r_i, r_i + 1):
            for dx in range(-r_i, r_i + 1):
                if dx * dx + dy * dy <= radius * radius + 0.3:
                    tiles.add((cx + dx, cy + dy))
    # 被房子占的格剔除（中心线本身保留，保证连通）
    tiles = {t for t in tiles if t not in blk or t in center}
    return tiles


def tiles_to_rects(tiles):
    """格集合 → 矩形列表。
    先按行合并连续段；再对「上下相邻且水平重叠」的段做贪婪合并（不要求同起点同宽），
    这样 3 格宽的路会合成少数几个高矩形，而不是每行一条。"""
    if not tiles:
        return []
    rows = {}
    for (x, y) in tiles:
        rows.setdefault(y, []).append(x)

    # 每行切成连续段
    segs = []          # [(x0, x1, y)]
    for y in sorted(rows):
        xs = sorted(rows[y])
        start = xs[0]
        prev = xs[0]
        for x in xs[1:]:
            if x == prev + 1:
                prev = x
                continue
            segs.append((start, prev, y))
            start = x
            prev = x
        segs.append((start, prev, y))

    # 贪婪合并：同 x 范围（或可扩展）且 y 相邻的段
    segs.sort(key=lambda s: (s[2], s[0]))
    consumed = [False] * len(segs)
    rects = []
    for i, (x0, x1, y) in enumerate(segs):
        if consumed[i]:
            continue
        consumed[i] = True
        cx0, cx1, cy0 = x0, x1, y
        cy1 = y
        # 往下找能接上的段
        while True:
            found = None
            for j, (nx0, nx1, ny) in enumerate(segs):
                if consumed[j] or ny != cy1 + 1:
                    continue
                # 要求水平范围完全一致，或新段被当前范围完全包含
                if nx0 == cx0 and nx1 == cx1:
                    found = j
                    break
                if nx0 >= cx0 and nx1 <= cx1:
                    found = j
                    break
            if found is None:
                break
            nx0, nx1, ny = segs[found]
            consumed[found] = True
            cy1 = ny
            # 范围只会收缩
            cx0 = max(cx0, nx0)
            cx1 = min(cx1, nx1)
        rects.append((cx0, cy0, cx1 - cx0 + 1, cy1 - cy0 + 1))
    return rects


def main():
    p = os.path.join(ROOT, "data", "frames.json")
    doc = json.load(open(p, encoding="utf-8"))
    houses_path = os.path.join(HERE, "houses_data.json")
    by_id = {}
    if os.path.exists(houses_path):
        for h in json.load(open(houses_path, encoding="utf-8")):
            by_id[h["id"]] = h

    def blocked_cells(frame):
        """该帧所有房子的 lot 占用格（含院子，路不该压院子）。"""
        s = set()
        for sh in frame["shapes"]:
            if sh.get("type") != "house":
                continue
            hd = by_id.get(sh.get("id", ""))
            if not hd:
                continue
            lot = hd["lot"]
            gw = lot[2] - lot[0] + 1
            gh = lot[3] - lot[1] + 1
            px, py = sh["pos"]
            x0, y0 = px // TILE, py // TILE
            for yy in range(y0, y0 + gh):
                for xx in range(x0, x0 + gw):
                    s.add((xx, yy))
        return s

    total_old = 0
    total_new = 0
    for f in doc["frames"]:
        blk = blocked_cells(f)
        new_shapes = []
        for s in f["shapes"]:
            if s.get("type") == "path":
                total_old += 1
                tiles = path_to_tiles(s["points"], blocked=blk)
                rects = tiles_to_rects(tiles)
                col = s.get("color", "#8a7a5a")
                lbl = s.get("label", "")
                for idx, (rx, ry, rw, rh) in enumerate(rects):
                    new_shapes.append({
                        "type": "rect",
                        "rect": [rx * TILE, ry * TILE, rw * TILE, rh * TILE],
                        "color": col,
                        "label": lbl if idx == 0 else "",
                        "road": True,
                    })
                    total_new += 1
            else:
                new_shapes.append(s)
        f["shapes"] = new_shapes
    json.dump(doc, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("path shapes: %d → %d 个格对齐矩形" % (total_old, total_new))
    for f in doc["frames"][:3]:
        road = [s for s in f["shapes"] if s.get("road")]
        ys = [(x["rect"][1], x["rect"][1] + x["rect"][3]) for x in road]
        print("  %-10s 路面 %2d 个矩形  y %d..%d" % (
            f["id"], len(road), min(y[0] for y in ys), max(y[1] for y in ys)))


if __name__ == "__main__":
    main()
