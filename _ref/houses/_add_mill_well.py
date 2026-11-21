# -*- coding: utf-8 -*-
"""幂等：给 A1/A2 磨坊补「老井」线索格，与 A3 粮站的井格时间线连贯（2026-11-20）。

井位统一 (6,10)：三帧都在屋本体南面的露天庭院、离房子远，对应「磨坊院内旧井、
路为它绕弯」。A1 在用 / A2 填埋盖石板 / A3 挖出 + 三层水泥封层（A3 里另有水泥格 (8,10)）。

注意：A1/A2 磨坊此前已定稿，本脚本只加井格与叙事字段，不动结构/隔墙/门/其他家具。
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")
data = json.load(open(DATA, encoding="utf-8"))
by_id = {h["id"]: h for h in data}

WELL_POS = [6, 10, 1, 1]

def well(note):
    return {"name": "老井", "short": "老井", "rect": list(WELL_POS),
            "note": note, "clue": True, "zone": "house", "yard_building": False}

# ---- A1 1926：老井在用（村里的吃水井，路为它绕弯）----
a1 = by_id["mill_a1"]
a1["furniture"] = [f for f in a1["furniture"] if f["name"] != "老井"]
a1["furniture"].append(well("磨坊院内旧井 · 1926 村里的吃水井，路为它绕弯；此时还在用"))
a1["clue"] = [c for c in a1["clue"] if "老井" not in c]
a1["clue"].append("磨坊院内这口老井：1926 年村里的吃水井，路为它绕弯（水磨的动力是上游坝水，不是这口井）。")
if "院内老井" not in a1["note"]:
    a1["note"] += " 院内老井(在用)：村里的吃水井，路为它绕弯。"

# ---- A2 1951：填井盖石板（陆敬之在下面），村里另打新井 ----
a2 = by_id["mill_a2"]
a2["furniture"] = [f for f in a2["furniture"] if f["name"] != "老井"]
a2["furniture"].append(well("磨坊院内旧井 · 1951 沈守业填井盖石板（陆敬之在下面）；村里在路另一头另打新井"))
a2["clue"] = [c for c in a2["clue"] if "老井" not in c and "埋" not in c]
a2["clue"].append("1951 沈守业把陆敬之推下院内老井，填井盖石板；村里在路另一头另打新井。A3 挖地基才把这口井翻出来。")
if "院内老井" not in a2["note"]:
    a2["note"] += " 院内老井已填盖石板(陆敬之在下面)，村里另打新井。"
a2["story"] = "磨坊院内那口老井 1951 年填了盖石板；A3 挖地基翻出，是三次封尸的起点。"

# 自检：井格不压门/院门四邻
def _blocked(h):
    def at(gx, gy):
        for f in h["furniture"]:
            x, y, w, hh = f["rect"]
            if x <= gx < x + w and y <= gy < y + hh:
                return f["name"]
        return None
    for dx, dy in h["doors"] + h.get("gate", []):
        for nx, ny in ((dx-1, dy), (dx+1, dy), (dx, dy-1), (dx, dy+1)):
            hit = at(nx, ny)
            assert hit is None, f"{h['id']} 门({dx},{dy}) 邻格({nx},{ny}) 被「{hit}」占据"
for h in (a1, a2):
    _blocked(h)

json.dump(data, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("mill wells added: houses", len(data),
      "| mill_a1 furniture", len(a1["furniture"]), "clue", len(a1["clue"]),
      "| mill_a2 furniture", len(a2["furniture"]), "clue", len(a2["clue"]))
