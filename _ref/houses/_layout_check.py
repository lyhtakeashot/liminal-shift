# -*- coding: utf-8 -*-
"""A1 1926 世界布局体检：BUILD-A1.md 里那张坐标表就是从这里来的。
改坐标时同步改这里，跑一遍，看到 LAYOUT OK 再写进文档。"""
import json, os

W, H = 1600, 900
TILE = 16

R = []
def rect(name, x, y, w, h, solid=True, kind="rect", note=""):
    R.append(dict(name=name, x=x, y=y, w=w, h=h, solid=solid, kind=kind, note=note))

def circle(name, cx, cy, r, solid=True, note=""):
    rect(name, cx - r, cy - r, r * 2, r * 2, solid, "circle", note)

# ---------- 自然 ----------
rect("河", 0, 0, 1600, 112, True, note="水自西向东；坝以上是上游")
rect("坝", 196, 34, 120, 62, True, note="沈家在上游筑坝（在河身里，蓄意重叠，豁免）")

# ---------- 建筑（lot 左上角，尺寸取自 houses_data.json）----------
data = json.load(open(os.path.join(os.path.dirname(__file__), "houses_data.json"), encoding="utf-8"))
by_id = {h["id"]: h for h in data}
PLACE = {
    "mill_a1":    (160, 112),   # 上游，紧贴河与坝
    "shen_a1":    (160, 340),   # 磨坊主家，在磨坊下游
    "zhou_house": (600, 400),   # 长工房，在沈家东边的路边
    "lu_house":   (1120, 340),  # 佃农，在自己田的下游
}
for hid, (px, py) in PLACE.items():
    lot = by_id[hid]["lot"]
    w = (lot[2] - lot[0] + 1) * TILE
    h = (lot[3] - lot[1] + 1) * TILE
    rect(hid, px, py, w, h, True, "house", note=f"lot {lot[2]-lot[0]+1}×{lot[3]-lot[1]+1} 格")

# ---------- 田（下游，不阻挡）----------
rect("田·东", 1000, 130, 240, 176, False, note="陆家田，坝以下")
rect("田·西", 1272, 130, 240, 176, False, note="陆家田，坝以下")

# ---------- 构筑物 ----------
circle("老井", 900, 545, 16, True, note="A5 的圆形补丁就在这儿；路为它绕弯")
circle("老槐", 852, 505, 9, False, note="1926 种在井边")

# ---------- 路（主路绕井 + 一条上磨坊的支路）----------
ROADS = [
    # 主路：横贯全图，到井那儿往南绕一个弯
    [(0, 560), (840, 560), (900, 624), (960, 560), (1600, 560)],
    # 支路：从磨坊东南角下来，绕开沈家，接主路
    [(464, 240), (560, 240), (560, 560)],
]
ROAD_W = 36
road_boxes = []
for road in ROADS:
    for i in range(len(road) - 1):
        (x1, y1), (x2, y2) = road[i], road[i + 1]
        road_boxes.append((min(x1, x2), min(y1, y2) - ROAD_W // 2,
                           abs(x2 - x1) + ROAD_W, abs(y2 - y1) + ROAD_W))

# ---------- 校验 ----------
EXEMPT = {("河", "坝")}
bad = []
solids = [r for r in R if r["solid"]]
for i in range(len(solids)):
    for j in range(i + 1, len(solids)):
        a, b = solids[i], solids[j]
        if a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and \
           a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]:
            if (a["name"], b["name"]) in EXEMPT or (b["name"], a["name"]) in EXEMPT:
                continue
            bad.append(f"重叠: {a['name']} × {b['name']}")

for r in R:
    if r["x"] < 0 or r["y"] < 0 or r["x"] + r["w"] > W or r["y"] + r["h"] > H:
        bad.append(f"出界: {r['name']}")

print(f"世界 {W}×{H} = {W//TILE}×{H/TILE:.2f} 格")
print(f"图元 {len(R)}（solid {len(solids)}），路 {len(road_boxes)} 段\n")
for r in R:
    print(f"  {r['name']:10s} ({r['x']:4d},{r['y']:4d}) {r['w']:4d}×{r['h']:3d}px"
          f"  {r['w']/TILE:5.1f}×{r['h']/TILE:5.2f}格  {'SOLID' if r['solid'] else '     '}  {r['note']}")

def blocked(px, py, rad=7):
    for a in solids:
        if a["x"] - rad < px < a["x"] + a["w"] + rad and a["y"] - rad < py < a["y"] + a["h"] + rad:
            return a["name"]
    return None

def in_road(px, py):
    return any(x <= px <= x + w and y <= py <= y + h for x, y, w, h in road_boxes)

print()
START = (700, 560)
print(f"起点 {START}: 在路={in_road(*START)} 阻挡={blocked(*START)}")
for hid, (px, py) in PLACE.items():
    lot = by_id[hid]["lot"]
    cx = px + (lot[2] - lot[0] + 1) * TILE // 2
    cy = py + (lot[3] - lot[1] + 1) * TILE + 24
    print(f"  {hid:11s} 南门外 ({cx:4d},{cy:4d}) 在路={in_road(cx, cy)} 阻挡={blocked(cx, cy)}"
          f"  到路面距离={min(abs(cy - y) for _, y, _, _ in road_boxes)}")

print()
if bad:
    for m in bad:
        print("BAD", m)
else:
    print("LAYOUT OK - 无重叠（河×坝 豁免）无出界")
