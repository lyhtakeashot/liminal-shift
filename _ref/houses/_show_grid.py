# -*- coding: utf-8 -*-
"""临时诊断：打印指定 house 的 build_grid 字符网格（纯 ASCII，避免控制台编码问题）。
用法: python _show_grid.py market zhou_a4
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gen_all_houses import build_grid

data = json.load(open(os.path.join(HERE, "houses_data.json"), encoding="utf-8"))
ids = sys.argv[1:] or ["market"]
for hid in ids:
    h = next(x for x in data if x["id"] == hid)
    g = build_grid(h)
    w = len(g[0])
    print("=" * 60)
    print("id", hid, "lot", h["lot"], "grid", len(g), "x", w)
    tens = "".join(" " if i < 10 else ("1" if i < 20 else "2") for i in range(w))
    ones = "".join(str(i % 10) for i in range(w))
    print("   " + tens)
    print("   " + ones)
    for y, row in enumerate(g):
        print(f"{y:2d} " + "".join(row))
    print("doors", h.get("doors"), "gate", h.get("gate"))
    print("partitions", h.get("partitions"))
    for r in h.get("rooms", []):
        print("  room", r)
