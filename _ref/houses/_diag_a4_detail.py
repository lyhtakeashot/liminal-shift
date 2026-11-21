# -*- coding: utf-8 -*-
"""只读导出 A4 三栋（market/zhou_a4/zheng_a4）当前完整数据。"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "houses_data.json"), encoding="utf-8"))
for h in d:
    if h["id"] in ("market", "zhou_a4", "zheng_a4"):
        print("=" * 60)
        for k in ("id", "name", "lot", "wings", "partitions", "doors", "gate",
                  "rooms", "furniture", "clue", "story", "note"):
            if k in h:
                print(k, "=", json.dumps(h[k], ensure_ascii=False))
