# -*- coding: utf-8 -*-
"""清理自动拆分产生的「·副」命名：
- mill_a2：x=1 那一列是墙基暗龛所在（藏起来的东西不标注），整个删掉，房间只留账房
- shen_a3 / shen_a4：被隔墙分开的两半给自然名字（西间 / 后间）
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")
data = json.load(open(DATA, encoding="utf-8"))
by_id = {h["id"]: h for h in data}

# mill_a2：去掉暗龛列那个假房间
mill = by_id["mill_a2"]
mill["rooms"] = [r for r in mill["rooms"] if r[4] != "账房·副"]
assert len(mill["rooms"]) == 3, mill["rooms"]

RENAME = {
    "shen_a3": {"北堂·副": "北堂西间", "西厢·副": "西厢后间", "东厢·副": "东厢后间"},
    "shen_a4": {"北堂·副": "北堂西间", "西厢·副": "西厢后间", "东厢·副": "东厢后间"},
}
for hid, mp in RENAME.items():
    for r in by_id[hid]["rooms"]:
        if r[4] in mp:
            r[4] = mp[r[4]]

json.dump(data, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

leftover = [(h["id"], r[4]) for h in data for r in h["rooms"] if "·副" in r[4]]
print("leftover ·副:", leftover)
print("OK")
