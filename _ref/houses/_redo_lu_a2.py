# -*- coding: utf-8 -*-
"""lu_a2：陆家空屋（1951）。

史实依据 docs/story.md:
  - A1 1926：陆家三口（老太爷 / 陆文 19 岁溺亡 / 儿媳怀遗腹子）
  - 陆文死后，老太爷拿抚恤银、签卖地契，带儿媳搬走
  - 陆婶 1927–1943 去要钱，1943 年春死
  - 陆敬之（遗腹子）1943 年 17 岁接过账本；1951 年 24 岁，县工作队员，回村查地
  - 1951 年他查地查出卖地契字迹见证人不对 → 沈守业灌醉、推井、填井

所以 1951 年的陆家：**空了八年**（1943 陆婶死后再没人住）。

设计口径（用户 m02514 决策）：空屋 = 留大件、搬走小件。
  搬走：衣柜、木箱、牌位（祖宗牌位一定会带走）、老太爷的单人床
  留下：双人床（床架）、八仙桌（搬不动）、灶台（砌死的）、水缸（裂）、茅房（塌半边）

占地与屋本体完全沿用 A1：屋 15×8，占地 19×9（含东侧院子）。
结构不变（同一栋房子，八年后），只改家具与叙事。
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")
data = json.load(open(DATA, encoding="utf-8"))
by_id = {h["id"]: h for h in data}

src = by_id["lu_house"]

a2 = {
    "id": "lu_a2",
    "name": "陆家 · 空屋 · A2 1951 · 受害方（已无人）",
    "lot": list(src["lot"]),
    "wings": [list(w) for w in src["wings"]],
    "partitions": [list(p) for p in src["partitions"]],
    "doors": [list(d) for d in src["doors"]],
    "gate": [list(g) for g in src.get("gate", [])],
    "rooms": [list(r) for r in src["rooms"]],
    "furniture": [
        # 夫妻房：只剩搬不动的床架，草垫烂了
        {"name": "双人床", "short": "双人床", "rect": [1, 1, 2, 2],
         "note": "床架还在，草垫烂成一堆", "clue": False, "zone": "house", "yard_building": False},
        # 堂屋：八仙桌搬不动，留在原处；牌位被走的人带走了
        {"name": "八仙桌", "short": "八仙桌", "rect": [7, 2, 2, 2],
         "note": "没人搬得动，桌面积了一层灰", "clue": False, "zone": "house", "yard_building": False},
        # 灶间：灶台是砌进墙里的，拆不走
        {"name": "灶台", "short": "灶台", "rect": [13, 5, 1, 2],
         "note": "砌死在墙里 · 锅早被拿走了", "clue": False, "zone": "house", "yard_building": False},
        # 院子
        {"name": "水缸", "short": "水缸", "rect": [16, 4, 1, 1],
         "note": "院子 · 缸沿豁了一块口", "clue": False, "zone": "yard", "yard_building": False},
        {"name": "茅房", "short": "茅房", "rect": [16, 1, 3, 2],
         "note": "屋外独立茅房 · 塌了半边", "clue": False, "zone": "yard", "yard_building": True},
        {"name": "茅坑", "short": "茅坑", "rect": [17, 1, 1, 1],
         "note": "茅房内", "clue": False, "zone": "yard", "yard_building": False},
    ],
    "clue": [
        "门板没了，门槛上长草——空了不止一年两年。",
        "堂屋八仙桌还在，牌位不见了：走的人把祖宗带走了。",
        "灶台上积了一层灰。灶膛里还有半截没烧完的柴。",
    ],
    "story": ("陆文 1926 年溺亡后，老太爷拿抚恤银、签卖地契，带儿媳搬走；"
              "陆婶 1943 年春死；房子从此空着。1951 年陆敬之 24 岁，"
              "作为县工作队员回村查地，查到卖地契的字迹和见证人对不上——"
              "这一年他被人灌醉，推进井里。"),
    "note": ("屋本体 15×8，占地 19×9（含东侧院子），与 A1 陆家完全同尺寸同结构——"
             "八年后还是这栋房子，只是没人住了。留大件（床架/八仙桌/灶台/水缸/塌了的茅房），"
             "搬走小件（衣柜/木箱/牌位/老太爷的单人床）。"),
}

# 已在列表里就替换，否则追加
if "lu_a2" in by_id:
    idx = data.index(by_id["lu_a2"])
    data[idx] = a2
else:
    data.append(a2)

json.dump(data, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("lu_a2 written: lot", a2["lot"], "furniture", len(a2["furniture"]))
