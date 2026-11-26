# -*- coding: utf-8 -*-
"""支路审计：把 a1..a3 的路块拆成「主路 / 支路连通块」，每块输出几何指纹（一律按格）。
只读。输出 < 100 行。"""
import json, os
from collections import defaultdict

T = 32
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FJ = os.path.join(ROOT, "data", "frames.json")
HD = os.path.join(ROOT, "_ref", "houses", "houses_data.json")


def main():
    frames = json.load(open(FJ, encoding="utf-8"))
    hd = {h["id"]: h for h in json.load(open(HD, encoding="utf-8"))}
    w = frames["world"]
    print("world = %gx%g 格" % (w["width"] / T, w["height"] / T))
    for fr in frames["frames"]:
        fid = fr["id"]
        blocks = set()
        for s in fr["shapes"]:
            if s.get("road") and s.get("type") == "rect":
                r = s["rect"]
                blocks.add((r[0] // T, r[1] // T))  # (col, row) 单位格，块高 2 格
        # 主路：a1/a2 的 0..149 列 y∈{46,47}；a3 同
        main = {(x, y) for (x, y) in blocks if 0 <= x <= 149 and y in (46, 47)}
        rest = blocks - main
        # 连通块（按块心 1 格间隔 4 邻接，含对角）
        seen, groups = set(), []
        for b in sorted(rest):
            if b in seen:
                continue
            stack, comp = [b], []
            seen.add(b)
            while stack:
                cx, cy = stack.pop()
                comp.append((cx, cy))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        nb = (cx + dx, cy + dy)
                        if nb in rest and nb not in seen:
                            seen.add(nb)
                            stack.append(nb)
            groups.append(sorted(comp))
        # 房子
        hs = []
        for s in fr["shapes"]:
            if s.get("type") == "house":
                hid = s.get("house_id") or s.get("id")
                h = hd.get(hid)
                if not h:
                    continue
                pos = s.get("pos", [0, 0])
                lot, gate = h["lot"], h["gate"]
                if gate and isinstance(gate[0], (list, tuple)):
                    gate = list(gate[0])
                hs.append((hid, pos[0] // T, pos[1] // T, lot, gate,
                           pos[0] // T + gate[0], pos[1] // T + gate[1]))
        print("\n=== %s === main=%d branch_blocks=%d branches=%d" % (fid, len(main), len(rest), len(groups)))
        print("  houses: " + " | ".join("%s pos(%g,%g) lot%dx%d gate(%g,%g)"
                                        % (hid, px, py, lot[2], lot[3], gate[0], gate[1])
                                        for hid, px, py, lot, gate, gx, gy in hs))
        for comp in groups:
            cols = [c[0] for c in comp]
            rows = [c[1] for c in comp]
            bycol = defaultdict(list)
            for c, r in comp:
                bycol[c].append(r)
            xs = sorted(bycol)
            seq = [min(bycol[x]) for x in xs]
            # 指纹：逐列 Δy 序列
            dys = [seq[i + 1] - seq[i] for i in range(len(seq) - 1)]
            # 折点数（Δy 变号或由非零变零）
            turns = 0
            for i in range(1, len(dys)):
                a, b = dys[i - 1], dys[i]
                if (a > 0) != (b > 0) or (a == 0) != (b == 0):
                    turns += 1
            print("  支路 x %g..%g  y %g..%g  块%2d  起(%g,%g) 终(%g,%g)  折点%d  Δy序列=%s"
                  % (min(cols), max(cols), min(rows), max(rows), len(comp),
                     xs[0], seq[0], xs[-1], seq[-1], turns,
                     ",".join("%+d" % d for d in dys)))


main()