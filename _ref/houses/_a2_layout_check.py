# -*- coding: utf-8 -*-
"""A2 1951 世界布局体检（BUILD-A1 §7.3 同款）。
原则：
- 沈家/周家/陆家与 A1 同 lot 原点（时间之门 1:1 铁律）
- 磨坊 A2 东移到老井上方（story §4.3「磨坊一直盖在井上面」，A3 挖地基挖到）→ (800,400)
- 老井封盖（石板铺平、可站，非 solid）留在磨坊院子下方
- 主路南移 y640（沈家 A2 扩建 368×272 南沿 612）
- 新井在路的另一头（西段路南）
- 老槐倾斜（朝远离井的方向 = 西北）"""
import json, os

W, H = 1600, 900
TILE = 16

R = []
def rect(name, x, y, w, h, solid=True, kind="rect", note=""):
    R.append(dict(name=name, x=x, y=y, w=w, h=h, solid=solid, kind=kind, note=note))

def circle(name, cx, cy, r, solid=True, note=""):
    rect(name, cx - r, cy - r, r * 2, r * 2, solid, "circle", note)

data = json.load(open(os.path.join(os.path.dirname(__file__), "houses_data.json"), encoding="utf-8"))
by_id = {h["id"]: h for h in data}

PLACE = {
    "mill_a2":    (800, 400),   # 东移：盖在老井(900,545)上方
    "shen_a2":    (160, 340),   # 同 A1 原点，扩建 368×272
    "zhou_a2":    (600, 400),   # 同 A1
    "lu_a2":      (1120, 340),  # 同 A1
}
for hid, (px, py) in PLACE.items():
    lot = by_id[hid]["lot"]
    w = (lot[2] - lot[0] + 1) * TILE
    h = (lot[3] - lot[1] + 1) * TILE
    rect(hid, px, py, w, h, True, "house", note=f"lot {lot[2]-lot[0]+1}×{lot[3]-lot[1]+1} 格")

# 自然
rect("河", 0, 0, 1600, 112, True, note="水自西向东")
rect("坝", 196, 34, 120, 62, True, note="河身里，豁免")
rect("田·东", 1000, 130, 240, 176, False)
rect("田·西", 1272, 130, 240, 176, False)
# 构筑物
circle("老井·封", 900, 545, 16, False, note="石板铺平、可站（磨坊正下方）")
circle("新井", 300, 700, 11, True, note="路的另一头（西段路南）")
circle("老槐·斜", 840, 495, 12, False, note="朝远离井的方向倾斜（西北）")
rect("碑", 696, 594, 8, 16, True, note="同 A1 原位")

# 路（主路南移 y640，保留绕井弯形状）
ROADS = [
    [(0, 640), (840, 640), (900, 704), (960, 640), (1600, 640)],
    [(464, 240), (560, 240), (560, 640)],
]
ROAD_W = 36
road_boxes = []
for road in ROADS:
    for i in range(len(road) - 1):
        (x1, y1), (x2, y2) = road[i], road[i + 1]
        road_boxes.append((min(x1, x2), min(y1, y2) - ROAD_W // 2,
                           abs(x2 - x1) + ROAD_W, abs(y2 - y1) + ROAD_W))

# 校验
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
          f"  {'SOLID' if r['solid'] else '     '}  {r['note']}")

def blocked(px, py, rad=7):
    for a in solids:
        if a["x"] - rad < px < a["x"] + a["w"] + rad and a["y"] - rad < py < a["y"] + a["h"] + rad:
            return a["name"]
    return None

def in_road(px, py):
    return any(x <= px <= x + w and y <= py <= y + h for x, y, w, h in road_boxes)

print()
START = (700, 640)
print(f"起点 {START}: 在路={in_road(*START)} 阻挡={blocked(*START)}")
for hid, (px, py) in PLACE.items():
    lot = by_id[hid]["lot"]
    cx = px + (lot[2] - lot[0] + 1) * TILE // 2
    cy = py + (lot[3] - lot[1] + 1) * TILE + 6
    print(f"  {hid:11s} 南门外 ({cx:4d},{cy:4d}) 在路={in_road(cx, cy)} 阻挡={blocked(cx, cy)}"
          f"  到路面距离={min(abs(cy - y) for _, y, _, _ in road_boxes) if road_boxes else '?'}")

print()
# 老井必须在磨坊 lot 内（story：磨坊盖在井上面）
mx, my = PLACE["mill_a2"]
lota = by_id["mill_a2"]["lot"]
mw, mh = (lota[2]-lota[0]+1)*TILE, (lota[3]-lota[1]+1)*TILE
in_mill = mx <= 900 <= mx + mw and my <= 545 <= my + mh
print(f"老井(900,545) 在 mill_a2 lot 内: {in_mill}")
if not in_mill:
    bad.append("老井不在磨坊下方")

if bad:
    for m in bad:
        print("BAD", m)
else:
    print("LAYOUT OK - 无重叠（河×坝 豁免）无出界")