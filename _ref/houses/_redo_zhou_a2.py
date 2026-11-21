# -*- coding: utf-8 -*-
"""zhou_a2：周家长工房 · A2 1951（新增第 13 栋）。

史实依据 docs/story.md:
  - 周家 A1 长工房仍在（周有田的祖父 1926 看见放水未告，没说）
  - 1951 周有田是沈家长工兼账房，1927-1951 记了 24 年、37 笔账，
    一辈子没说过一个字；这年账上多一行「酒二斤」= 沈守业灌醉陆敬之
  - A5 才出土周有田往来账；A2 只延续「小桌抽屉藏账（位置待定）」的口径，
    不提前放账本、不编新位置

设计口径（用户 2026-11-20 拍板）：
  沿用 A1 长工房结构（屋本体 8×5、占地 12×6），周有田人还在；
  **家具完全照抄 A1（含 note），不做旧化**——用户口径「家具做旧这点不用做，
  美术方的工作量太大了」，这样 A1/A2 周家家具图可直接复用。
  只改 name / clue / story / note（叙事层）。

结构完全照抄 A1 zhou_house（lot/wings/partitions/doors/gate/rooms/furniture）。
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")
data = json.load(open(DATA, encoding="utf-8"))
by_id = {h["id"]: h for h in data}

src = by_id["zhou_house"]  # A1 周家：结构源 + 家具源（完全照抄）

a2 = {
    "id": "zhou_a2",
    "name": "周家 · 长工房 · A2 1951 · 帮凶方（人还在）",
    "lot": list(src["lot"]),
    "wings": [list(w) for w in src["wings"]],
    "partitions": [list(p) for p in src["partitions"]],
    "doors": [list(d) for d in src["doors"]],
    "gate": [list(g) for g in src.get("gate", [])],
    "rooms": [list(r) for r in src["rooms"]],
    # 家具完全复用 A1（连 note 一起），不做旧化，减轻美术工作量
    "furniture": [dict(f) for f in src["furniture"]],
    "clue": [
        "小桌抽屉＝周有田往来账(位置待定)；1927-1951 记了二十四年三十七笔，一个字没说。",
        "1951 这年账上多一行「酒二斤」——沈守业灌醉陆敬之那天买的。",
    ],
    "story": ("周有田此时是沈家长工兼账房，1927-1951 记了二十四年账。"
              "1943 年陆婶死，十七岁的陆敬之接手，账上把「婶」改成了「先生」。"
              "土改这年陆敬之回村查地，账上又多一行「酒二斤」——"
              "他照常记账，那笔账一辈子没给人看过。"),
    "note": ("屋本体 8×5、占地 12×6（含东侧院子），与 A1 周家完全同尺寸同结构——"
             "同一栋长工房，二十五年后。家具完全照抄 A1（不做旧化，美术直接复用）；"
             "往来账位置维持待定，不提前出土。"),
}

if a2["id"] in by_id:
    data[data.index(by_id[a2["id"]])] = a2
else:
    data.append(a2)

json.dump(data, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("zhou_a2 written: houses", len(data), "lot", a2["lot"], "furniture", len(a2["furniture"]))
