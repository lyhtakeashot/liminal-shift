# -*- coding: utf-8 -*-
"""只读导出 frames.json 前三帧 + A4 的 shapes，供 A4 场景设计核对。"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fr = json.load(open(os.path.join(ROOT, "data", "frames.json"), encoding="utf-8"))
print("WORLD", fr.get("world"), "START", fr.get("start_pos"))
for f in fr["frames"]:
    if f["id"] in ("a1_1926", "a2_1951", "a3_1976", "a4_2001"):
        print("\n==", f["id"], "ground", f.get("ground"))
        for s in f["shapes"]:
            print("  ", json.dumps(s, ensure_ascii=False))
        print("  hotspots:", len(f.get("hotspots", [])))
