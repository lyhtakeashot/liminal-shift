# -*- coding: utf-8 -*-
"""一次性修正脚本（两条用户口径）：
1) 房间矩形不含墙格（含外围墙与内部隔墙）；院子/天井房间不受外围墙约束，但也要去掉墙格
2) shen_a2 的 L 形 = 完整矩形，只在左上角缺一格（与其它房子角落凹角同款，不需要额外机制）
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")
data = json.load(open(DATA, encoding="utf-8"))
by_id = {h["id"]: h for h in data}


# ---------- 与 gen_all_houses.build_grid 完全一致的几何 ----------
def geometry(hs):
    X0, Y0, X1, Y1 = hs["lot"]
    interior = set()
    for (x, y, w, h) in hs["wings"]:
        for j in range(y + 1, y + h - 1):
            for i in range(x + 1, x + w - 1):
                interior.add((i, j))

    def is_wall(i, j):
        if (i, j) in interior:
            return False
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (i + di, j + dj) in interior:
                return True
        return False

    part = set()
    for (x1, y1, x2, y2) in hs.get("partitions", []):
        if x1 == x2:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                part.add((x1, y))
        else:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                part.add((x, y1))
    return interior, is_wall, part


def split_by_partitions(rect, part):
    """把矩形沿穿过它的隔墙切成不含隔墙格的小矩形（递归，先竖后横交替）。"""
    x0, y0, x1, y1 = rect
    vcuts = [x for x in range(x0, x1 + 1) if any((x, y) in part for y in range(y0, y1 + 1))]
    # 只保留整列都是隔墙的竖切
    vcuts = [x for x in vcuts if all((x, y) in part for y in range(y0, y1 + 1))]
    if vcuts:
        out, prev = [], x0
        for x in vcuts:
            if x > prev:
                out.append((prev, y0, x - 1, y1))
            prev = x + 2  # 隔墙两侧各留一格？不：隔墙只占一列，跳过这一列
            prev = x + 1
        if prev <= x1:
            out.append((prev, y0, x1, y1))
        res = []
        for r in out:
            res.extend(split_by_partitions(r, part))
        return res
    hcuts = [y for y in range(y0, y1 + 1) if all((x, y) in part for x in range(x0, x1 + 1))]
    if hcuts:
        out, prev = [], y0
        for y in hcuts:
            if y > prev:
                out.append((x0, prev, x1, y - 1))
            prev = y + 1
        if prev <= y1:
            out.append((x0, prev, x1, y1))
        res = []
        for r in out:
            res.extend(split_by_partitions(r, part))
        return res
    return [rect]


def clip_free(rect, is_wall, part):
    """把矩形收缩到不含墙格/隔墙格：只剥离「整条边全是脏格」的边，反复直到稳定。
    逐列检查会误杀天井这类「顶行是墙、内部是空地」的矩形。"""
    x0, y0, x1, y1 = rect
    dirty = lambda x, y: is_wall(x, y) or (x, y) in part
    for _ in range(200):
        if x0 > x1 or y0 > y1:
            return None
        if all(dirty(x0, y) for y in range(y0, y1 + 1)):
            x0 += 1
            continue
        if all(dirty(x1, y) for y in range(y0, y1 + 1)):
            x1 -= 1
            continue
        if all(dirty(x, y0) for x in range(x0, x1 + 1)):
            y0 += 1
            continue
        if all(dirty(x, y1) for x in range(x0, x1 + 1)):
            y1 -= 1
            continue
        break
    return (x0, y0, x1, y1) if x0 <= x1 and y0 <= y1 else None


# ---------- 1) shen_a2 重做：完整矩形 + 左上角一格凹角 ----------
a2 = by_id["shen_a2"]
a2["lot"] = [0, 0, 16, 13]            # 17×14 格 = 272×224 px
a2["wings"] = [[0, 0, 17, 12]]        # 完整矩形（南侧 y=12,13 两行作院子）
a2["partitions"] = [
    [6, 1, 6, 4],      # 主卧 / 子女房
    [1, 5, 15, 5],     # 北排 / 南排
    [9, 6, 9, 10],     # 堂屋 / 东侧灶间储物
    [10, 8, 15, 8],    # 灶间 / 储物
]
a2["doors"] = [[3, 5], [11, 5], [9, 7], [12, 8]]
a2["gate"] = [[7, 11]]
a2["rooms"] = [
    [1, 1, 5, 4, "主卧", "bed"],
    [7, 1, 15, 4, "子女房", "bed"],
    [1, 6, 8, 10, "堂屋", "hall"],
    [10, 6, 15, 7, "灶间", "kitchen"],
    [10, 9, 15, 10, "储物", "store"],
    [1, 12, 15, 13, "院子", "yard"],
]
a2["furniture"] = [
    {"name": "双人床", "short": "双人床", "rect": [1, 1, 3, 3], "note": "富家 3×3 · 主卧", "clue": False, "zone": "house", "yard_building": False},
    {"name": "衣柜", "short": "衣柜", "rect": [4, 1, 1, 2], "note": "主卧 · 贴隔墙", "clue": False, "zone": "house", "yard_building": False},
    {"name": "子女床", "short": "子女床", "rect": [13, 1, 2, 2], "note": "子女房 · 贴东墙", "clue": False, "zone": "house", "yard_building": False},
    {"name": "八仙桌", "short": "八仙桌", "rect": [3, 7, 2, 2], "note": "堂屋正中", "clue": False, "zone": "house", "yard_building": False},
    {"name": "牌位", "short": "牌位", "rect": [7, 6, 2, 1], "note": "堂屋北墙 · 祭祖", "clue": False, "zone": "house", "yard_building": False},
    {"name": "灶台", "short": "灶台", "rect": [15, 6, 1, 2], "note": "灶间 · 竖向贴东墙", "clue": False, "zone": "house", "yard_building": False},
    {"name": "粮囤", "short": "粮囤", "rect": [13, 9, 2, 2], "note": "储物 · 粮", "clue": False, "zone": "house", "yard_building": False},
    {"name": "水缸", "short": "水缸", "rect": [2, 12, 1, 1], "note": "院子 · 蓄水", "clue": False, "zone": "yard", "yard_building": False},
    {"name": "柴堆", "short": "柴堆", "rect": [4, 12, 1, 1], "note": "院子 · 柴", "clue": False, "zone": "yard", "yard_building": False},
]
a2["note"] = "屋本体 17×12 完整矩形；左上角一格天然凹角（与其他房子角落凹角同款）；南侧两行院子。"
a2["clue"] = ["比 A1 大一圈、进深翻倍；青瓦取代土坯。"]

# ---------- 2) 全库房间去墙 ----------
for hs in data:
    if hs["id"] == "shen_a2":
        continue
    interior, is_wall, part = geometry(hs)
    new_rooms = []
    for room in hs["rooms"]:
        x0, y0, x1, y1, name, ck = room[:6]
        extra = room[6:]
        is_yard = (ck == "yard")
        rects = split_by_partitions((x0, y0, x1, y1), part)
        pieces = []
        for r in rects:
            c = clip_free(r, is_wall, part)
            if c:
                pieces.append(c)
        if not pieces:
            # 整块都没了：保留原样，交给断言报错
            new_rooms.append(room)
            continue
        pieces.sort(key=lambda r: (-(r[2] - r[0] + 1) * (r[3] - r[1] + 1), r[1], r[0]))
        for i, c in enumerate(pieces):
            nm = name if i == 0 else (name + "·副" if not is_yard else name)
            new_rooms.append([c[0], c[1], c[2], c[3], nm, ck] + list(extra))
    hs["rooms"] = sorted(new_rooms, key=lambda r: (r[1], r[0]))

json.dump(data, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ---------- 3) 自检 ----------
bad = 0
for hs in data:
    interior, is_wall, part = geometry(hs)
    for room in hs["rooms"]:
        x0, y0, x1, y1, name, ck = room[:6]
        hits = [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)
                if is_wall(x, y) or (x, y) in part]
        if hits:
            bad += 1
            print("STILL BAD", hs["id"], name, (x0, y0, x1, y1), len(hits), hits[:6])
print("rooms still touching walls:", bad)
print("OK written")
