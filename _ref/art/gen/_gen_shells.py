# -*- coding: utf-8 -*-
"""生成 A1–A3 12 栋 + A4/A5 7 栋房屋的 base / roof PNG。

A4/A5 批次（PROMPT-house-art-a4a5-exec.md，2026-11-26）：同一套画法，只是帧号多两格；
唯一特例是 lu_a3 的 roof 层 —— 废墟没有屋顶，那张图是**压色块用的遮罩**，
见 paint_ruin_roof_mask() 的注释，不要当美术去欣赏。

规格来源（冻结，不自行发挥）：
- docs/DECIDE-stardew-visual.md D6
- docs/art-assets-a1a3.md §4（外观层 23 张）、§5.5
- docs/house-spec.md §4.8.5（画布比占地高一格，锚点底部中心）

画布：cw = gw（占地宽格）, ch = gh + 1（占地高格 + 1），像素 = cw×32 × ch×32。
锚点：底部中心 —— 画布底边 = 占地底边，多出的那一格在**顶部**（墙/屋顶立起来的高度）。

⚠️ 画布坐标映射（与 scripts/world_view.gd 的伪 3D 严格一致，改动前先读那段）：
  贴图绘制位置 = 世界 (lot_x, lot_y − 32)，尺寸 = lot_w×32 × (lot_h+1)×32
  ⇒ 画布行 0 = 世界行 −1；画布行 j*32 = 世界行 j−1；画布行 j*32+32 = 世界行 j

  格 (i, j)：
     地面 / 地板   → 画布 [i*32,(i+1)*32] × [j*32+32, j*32+64]
     南立面（垂直面）→ 画布 [i*32,(i+1)*32] × [j*32+32, j*32+64]   ← 与地板同一格
     墙顶面（抬高 32）→ 画布 [i*32,(i+1)*32] × [j*32, j*32+32]    ← 盖住北邻那一格
  ⇒ 北墙（j=0）的顶面正好落在画布顶部多出的那一格，这就是多一格的原因。
  ⇒ 墙顶面会盖住北邻格的地面（伪 3D 的正确遮挡：墙立起来挡住它后面那格）。

  屋顶（wing 矩形，引擎 `world_view.gd:345` 同式）：
     世界 x ∈ [wx*32 − 1, wx*32 + ww*32 + 1]
     世界 y ∈ [wy*32 − 33, wy*32 + wh*32 − 31]
     ⇒ 画布 x ∈ [(wx−X0)*32 − 1, (wx−X0+ww)*32 + 1]
     ⇒ 画布 y ∈ [(wy−Y0)*32 − 1, (wy−Y0+wh)*32 + 1]
     ⇒ 翼按 wy 升序画：南翼压北翼（引擎 `_draw_roof` 同序）。

可见性规则（照抄引擎 `_draw_walls_lifted` 的叠放后果）：
  只有**南边是空格的墙格**才画得见南立面 —— 它南邻那一格若也是墙，那格的墙顶面
  会正好盖上来。四面墙都画全高会把室内全挡住（house-spec §7 坑表）。
  门分两种：南北向的门（南邻空）画在立面上；东西向的门（东西邻是室内）画成墙顶
  面上的一道缺口（通道）。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pixel_lib import Canvas, TILE, PAL, shade, mix, hexc  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
DATA = os.path.join(ROOT, "_ref", "houses", "houses_data.json")
MANIFEST = os.path.join(ROOT, "_ref", "art", "_assets_a1a3", "_a1a3_assets.json")

FAMILY = {
    "lu_house": ("lu", "a1"), "lu_a2": ("lu", "a2"), "lu_a3": ("lu", "a3"),
    "shen_a1": ("shen", "a1"), "shen_a2": ("shen", "a2"), "shen_a3": ("shen", "a3"),
    "mill_a1": ("mill", "a1"), "mill_a2": ("mill", "a2"), "mill_a3": ("mill", "a3"),
    "zhou_house": ("zhou", "a1"), "zhou_a2": ("zhou", "a2"), "zhou_a3": ("zhou", "a3"),
}
ORDER = ["lu_house", "mill_a1", "shen_a1", "zhou_house",
         "lu_a2", "mill_a2", "shen_a2", "zhou_a2",
         "lu_a3", "mill_a3", "shen_a3", "zhou_a3"]

# 房屋配色：墙材质 / 屋顶材质 / 院落地
# 演变线：茅草顶 → 红瓦 → 绿瓦（1951 改瓦、1976 换绿瓦），是这一代人的家当变化。
STYLE = {
    ("lu", "a1"):  dict(wall="mud",     roof="thatch", yard="dirt"),
    ("lu", "a2"):  dict(wall="mud",     roof="thatch", yard="dirt"),
    ("lu", "a3"):  dict(wall=None,     roof=None,     yard="grass"),   # 废墟
    ("mill", "a1"): dict(wall="mud",    roof="thatch", yard="dirt"),
    ("mill", "a2"): dict(wall="brick",  roof="thatch", yard="dirt"),
    ("mill", "a3"): dict(wall="brick",  roof="tile_g", yard="dirt"),
    ("shen", "a1"): dict(wall="plaster", roof="tile_r", yard="grass"),
    ("shen", "a2"): dict(wall="plaster", roof="tile_r", yard="grass"),
    ("shen", "a3"): dict(wall="brick",   roof="tile_r", yard="grass"),
    ("zhou", "a1"): dict(wall="mud",     roof="thatch", yard="dirt"),
    ("zhou", "a2"): dict(wall="plaster", roof="thatch", yard="dirt"),
    ("zhou", "a3"): dict(wall="plaster", roof="tile_g", yard="dirt"),
}

# ---------------------------------------------------------------- A4 / A5 七栋
# 帧号 a4 = 2001、a5 = 2026。FAMILY 与 scripts/world_view.gd:641-653 的 const FAMILY 一一对应
# （那边的登记本线一行不动，这里只是生成端给出同样的映射）。
# 配色按各栋在故事里的身份定，不按「好看」定：
#   market a4  在建工地 —— 毛坯砌体（stone 的砖缝感）+ 已上的灰瓦
#   shen_a4    2001 首富的四合院 —— 砖墙 + 红瓦，与 1976 的 shen_a3（砖+红瓦）同系但更整齐
#   shen_a5    2026 同一座祖宅封门空置 —— 抹灰墙皮 + 灰瓦（几何与 a4 逐格相同，是设计
#              决定的「祖宅不变」，所以只靠材质与 seed 区分，不是漏画）
#   zhou_a4    会计家平房 —— 砖 + 灰瓦
#   zheng_a4   外来户二层小楼 —— 抹灰 + 红瓦
#   toyshop a5 临街店面 —— 砖 + 红瓦
#   school a5  村小 —— 砖 + 灰瓦
FAMILY_A45 = {
    "market": ("market", "a4"),
    "shen_a4": ("shen", "a4"),
    "zhou_a4": ("zhou", "a4"),
    "zheng_a4": ("zheng", "a4"),
    "shen_a5": ("shen", "a5"),
    "toyshop": ("toyshop", "a5"),
    "school": ("school", "a5"),
}
ORDER_A45 = ["market", "shen_a4", "zhou_a4", "zheng_a4",
             "shen_a5", "toyshop", "school"]
STYLE_A45 = {
    ("market", "a4"):  dict(wall="stone",   roof="tile_g", yard="dirt"),
    ("shen", "a4"):    dict(wall="brick",   roof="tile_r", yard="grass"),
    ("zhou", "a4"):    dict(wall="brick",   roof="tile_g", yard="dirt"),
    ("zheng", "a4"):   dict(wall="plaster", roof="tile_r", yard="dirt"),
    ("shen", "a5"):    dict(wall="plaster", roof="tile_g", yard="grass"),
    ("toyshop", "a5"): dict(wall="brick",   roof="tile_r", yard="dirt"),
    ("school", "a5"):  dict(wall="brick",   roof="tile_g", yard="dirt"),
}

# 交付 roof 图层的废墟（默认废墟不出 roof：docs/art-assets-a1a3.md:82）。
# lu_a3 例外：引擎 _draw_roof 会无条件先画 wings 色块，缺图＝屋顶压着塌房，
# docs/PROMPT-art-asset-gap-exec.md:91 因此把 lu a3_roof 列为缺口。
RUIN_ROOF_IDS = {"lu_a3"}

# 房间 color_key → 地板基色（取自 scripts/house_shape.gd 的 ROOM_COLORS，引擎占位块同色）
ROOM_TINT = {
    "bed":     "#9c8468", "hall":   "#cbb997", "store":  "#8d9a6f",
    "kitchen": "#bdd0b0", "account": "#a8c0d0", "yard":  "#6f7449",
    "shop":    "#b99aa6", "class":  "#9dbacd", "mill":   "#b5a878",
    "toilet":  "#9aa8a8", "bath":   "#9aa8a8", "field":  "#9a9678",
}
# 地板纹理：plank = 木板条纹，tile = 方砖，earth = 夯土
ROOM_TEX = {
    "bed": "plank", "hall": "plank", "store": "earth", "kitchen": "tile",
    "account": "plank", "shop": "tile", "class": "tile", "mill": "earth",
    "toilet": "tile", "yard": "earth", "bath": "tile", "field": "earth",
}


def tint3(hexstr, light=0.28, dark=0.30):
    """由一个基色推出 (亮, 主, 暗) 三档。"""
    return (mix(hexstr, "#ffffff", light), hexstr, mix(hexstr, "#000000", dark))


# ================================================================ 网格
def build_grid(hs):
    """抄 gen_all_houses.py 的 build_grid()：'#' 墙 / '.' 室内 / 'D' 房门 / 'G' 院门 / ' ' 院子。"""
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
            for j in range(min(y1, y2), max(y1, y2) + 1):
                part.add((x1, j))
        else:
            for i in range(min(x1, x2), max(x1, x2) + 1):
                part.add((i, y1))

    dset = set(tuple(d) for d in hs["doors"])
    gset = set(tuple(g) for g in hs.get("gate", []))
    demolished = set(tuple(p) for p in hs.get("demolished", []))
    rows = []
    for j in range(Y0, Y1 + 1):
        row = ""
        for i in range(X0, X1 + 1):
            c = (i, j)
            if c in demolished:
                ns, ss = (i, j - 1) in interior, (i, j + 1) in interior
                ws, es = (i - 1, j) in interior, (i + 1, j) in interior
                row += "." if (ns and ss) or (ws and es) else " "
            elif c in gset:
                row += "G"
            elif c in dset:
                row += "D"
            elif c in part or is_wall(i, j):
                row += "#"
            elif c in interior:
                row += "."
            else:
                row += " "
        rows.append(row)
    return rows


def interior_cells(hs):
    out = set()
    for (x, y, w, h) in hs["wings"]:
        for j in range(y + 1, y + h - 1):
            for i in range(x + 1, x + w - 1):
                out.add((i, j))
    return out


def perimeter_cells(hs, interior):
    """翼矩形里、但不是室内的格子 —— 外墙环。"""
    out = set()
    for (x, y, w, h) in hs["wings"]:
        for j in range(y, y + h):
            for i in range(x, x + w):
                if (i, j) not in interior:
                    out.add((i, j))
    return out


def room_cell_colors(hs, interior):
    """格 → 房间 color_key（房间矩形压过室内格；没压到的用 hall）。"""
    out = {}
    for room in hs.get("rooms", []):
        rx0, ry0, rx1, ry1 = room[0], room[1], room[2], room[3]
        ck = room[5] if len(room) > 5 else "hall"
        for j in range(ry0, ry1 + 1):
            for i in range(rx0, rx1 + 1):
                if (i, j) in interior:
                    out[(i, j)] = ck
    for c in interior:
        out.setdefault(c, "hall")
    return out


# ================================================================ 地面
def fill_ground(cv, x0, y0, x1, y1, pal, seed):
    """院子地面：踩实的土 / 草皮，稀疏颗粒。"""
    c0, c1, c2, c3 = PAL[pal]
    cv.rect(x0, y0, x1, y1, c1)
    if pal == "grass":
        cv.speckle(x0, y0, x1, y1, c0, seed=seed, density=0.035)
        cv.speckle(x0, y0, x1, y1, c2, seed=seed + 7, density=0.05)
        cv.speckle(x0, y0, x1, y1, c3, seed=seed + 19, density=0.02)
    else:
        cv.speckle(x0, y0, x1, y1, c2, seed=seed, density=0.05)
        cv.speckle(x0, y0, x1, y1, c0, seed=seed + 13, density=0.028)
        cv.speckle(x0, y0, x1, y1, c3, seed=seed + 29, density=0.012)


def fill_room(cv, x0, y0, x1, y1, ck, seed):
    """房间地板：按 color_key 选基色 + 纹理。"""
    base = ROOM_TINT.get(ck, "#cbb997")
    lo, mid, hi = tint3(base)
    tex = ROOM_TEX.get(ck, "plank")
    cv.rect(x0, y0, x1, y1, mid)
    if tex == "plank":
        y = y0
        r = 0
        while y < y1:
            yb = min(y1, y + 12)
            cv.rect(x0, y, x1, yb, mix(mid, lo if r % 2 == 0 else hi, 0.10))
            cv.line(x0, y, x1, y, mix(mid, lo, 0.42))
            cv.line(x0, yb - 1, x1, yb - 1, mix(mid, hi, 0.52))
            seg = 40 + ((r * 23 + seed) % 3) * 14
            jx = x0 + ((r * 31 + seed * 7) % seg)
            while jx < x1:
                cv.line(jx, y + 1, jx, yb - 1, mix(mid, hi, 0.38))
                jx += seg
            y = yb
            r += 1
    elif tex == "tile":
        y = y0
        r = 0
        while y < y1:
            yb = min(y1, y + 16)
            off = 8 if r % 2 else 0
            x = x0 - off
            while x < x1:
                xa, xb = max(x0, x), min(x1, x + 16)
                cv.rect(xa, y, xb, yb, mix(mid, lo, 0.10))
                cv.line(xa, y, xb, y, mix(mid, lo, 0.38))
                cv.line(xa, yb - 1, xb, yb - 1, mix(mid, hi, 0.48))
                x += 16
            y = yb
            r += 1
    else:  # earth
        cv.speckle(x0, y0, x1, y1, mix(mid, hi, 0.4), seed=seed, density=0.055)
        cv.speckle(x0, y0, x1, y1, mix(mid, lo, 0.5), seed=seed + 11, density=0.03)


# ================================================================ 墙体
def draw_cap(cv, x0, y0, x1, y1, pal, kind, seed):
    """墙顶面（抬高 32px 的那一面）：最亮的一档 + 北缘高光 + 南缘接触阴影。"""
    c0, c1, c2, c3 = PAL[pal]
    cv.rect(x0, y0, x1, y1, c0)
    if kind == "brick":
        y = y0 + 6
        while y < y1 - 1:
            cv.line(x0, y, x1, y, c1)
            off = 8 if ((y - y0) // 6) % 2 else 0
            x = x0 + off
            while x < x1:
                cv.line(x, y, x, min(y1 - 1, y + 6), c1)
                x += 16
            y += 6
    elif kind == "stone":
        y = y0 + 8
        while y < y1 - 1:
            cv.line(x0, y, x1, y, c1)
            x = x0 + (8 if ((y - y0) // 8) % 2 else 0)
            while x < x1:
                cv.line(x, y, x, min(y1 - 1, y + 8), c1)
                x += 16
            y += 8
    else:
        cv.speckle(x0, y0, x1, y1, c1, seed=seed + 2, density=0.035)
    cv.rect(x0, y0, x1, y0 + 2, mix(c0, "#ffffff", 0.38))   # 北缘受光
    cv.rect(x0, y1 - 3, x1, y1, c2)                          # 南缘接触阴影


def draw_facade(cv, x0, y0, x1, y1, pal, kind, seed, height=32):
    """南立面（垂直面）：主色 + 顶部受光带 + 底部暗带 + 轻材质颗粒。"""
    c0, c1, c2, c3 = PAL[pal]
    cv.rect(x0, y0, x1, y0 + height, c1)
    if kind == "brick":
        y = y0 + 2
        while y < y0 + height - 3:
            cv.line(x0, y, x1, y, c2)
            off = 8 if ((y - y0) // 4) % 2 == 0 else 0
            x = x0 + off
            while x < x1:
                cv.line(x, y, x, min(y0 + height - 3, y + 4), c2)
                x += 16
            y += 4
        cv.speckle(x0, y0, x1, y0 + height, c0, seed=seed, density=0.008)
    elif kind == "wood":
        x = x0 + 5
        while x < x1:
            cv.line(x, y0 + 3, x, y0 + height - 4, c2)
            x += 10
    elif kind == "plaster":
        cv.speckle(x0, y0, x1, y0 + height, c2, seed=seed, density=0.020)
        cv.speckle(x0, y0, x1, y0 + height, c0, seed=seed + 7, density=0.010)
    elif kind == "stone":
        y = y0 + 3
        while y < y0 + height - 3:
            cv.line(x0, y, x1, y, c2)
            off = 8 if ((y - y0) // 6) % 2 == 0 else 0
            x = x0 + off
            while x < x1:
                cv.line(x, y, x, min(y0 + height - 3, y + 6), c2)
                x += 16
            y += 6
    else:  # mud
        cv.speckle(x0, y0, x1, y0 + height, c2, seed=seed, density=0.030)
        cv.speckle(x0, y0, x1, y0 + height, c0, seed=seed + 13, density=0.016)
    cv.rect(x0, y0, x1, y0 + 2, c0)                    # 顶部受光
    cv.rect(x0, y0 + height - 6, x1, y0 + height, c3)  # 墙脚阴影
    cv.rect(x0, y0 + height - 8, x1, y0 + height - 6, c2)


def draw_window(cv, x0, y0, x1, y1):
    """立面上的窗：深色窗洞 + 木框 + 一点反光。"""
    ix0, iy0 = x0 + 8, y0 + 9
    ix1, iy1 = x1 - 8, y1 - 9
    if ix1 - ix0 < 8 or iy1 - iy0 < 6:
        return
    cv.rect(ix0 - 1, iy0 - 1, ix1 + 1, iy1 + 1, PAL["wood_d"][3])
    cv.rect(ix0, iy0, ix1, iy1, PAL["ink"][2])
    cv.rect(ix0, iy0, ix1, iy0 + 2, PAL["wood_l"][2])
    cv.rect(ix0, iy0, ix0 + 2, iy1, PAL["wood_l"][2])
    cv.rect(ix1 - 2, iy0, ix1, iy1, PAL["wood_l"][2])
    cv.rect(ix0 + 1, iy0 + 1, ix0 + 4, iy0 + 4, PAL["glass"][1])
    cv.line(ix0 + 4, iy0 + 4, ix1 - 2, iy1 - 2, PAL["wood_d"][2])


def draw_door(cv, x0, y0, x1, y1):
    """南立面上的门：门框 + 门板 + 门闩。"""
    cv.rect(x0, y0, x1, y1, PAL["wood_d"][3])
    cv.rect(x0 + 2, y0 + 2, x1 - 2, y1, PAL["wood_d"][2])
    cv.rect(x0 + 5, y0 + 4, x1 - 5, y1 - 3, PAL["wood"][1])
    cv.rect(x0 + 7, y0 + 6, x1 - 7, y1 - 6, PAL["wood"][2])
    cv.line(x0 + 6, y0 + 5, x0 + 6, y1 - 5, PAL["wood"][0])
    cv.px(x1 - 9, (y0 + y1) // 2, PAL["brass"][1])
    cv.px(x1 - 9, (y0 + y1) // 2 + 1, PAL["brass"][2])


def draw_gate(cv, x0, y0, x1, y1):
    """南立面上的院门：两根门柱 + 一道横木栅。"""
    cv.rect(x0, y0, x1, y1, PAL["wood_d"][3])
    cv.rect(x0 + 2, y0 + 3, x1 - 2, y1 - 2, PAL["wood_d"][2])
    cv.rect(x0 + 5, y0 + 9, x1 - 5, y1 - 5, PAL["wood"][2])
    x = x0 + 8
    while x < x1 - 6:
        cv.line(x, y0 + 10, x, y1 - 6, PAL["wood"][0])
        x += 6
    cv.rect(x0 + 3, y0 + 5, x0 + 7, y1 - 3, PAL["wood"][3])
    cv.rect(x1 - 7, y0 + 5, x1 - 3, y1 - 3, PAL["wood"][3])


def draw_passage(cv, x0, y0, x1, y1):
    """东西向的门：在墙顶面上开一道通口（阴影 + 门洞黑）。"""
    cv.rect(x0, y0, x1, y1, PAL["ink"][3])
    cv.rect(x0 + 4, y0 + 6, x1 - 4, y1 - 6, PAL["ink"][1])
    cv.rect(x0 + 4, y0 + 6, x1 - 4, y0 + 10, PAL["wood_d"][2])
    cv.rect(x0 + 6, y0 + 8, x1 - 6, y0 + 10, PAL["wood"][1])


# ================================================================ 屋顶
def draw_roof(cv, hs, st, seed, W, H):
    """每个 wing 一块屋顶（整体抬高 32px 落位，见文件头映射表）。"""
    X0, Y0 = hs["lot"][0], hs["lot"][1]
    pal = st["roof"]
    c0, c1, c2, c3 = PAL[pal]
    for wi, w in enumerate(sorted(hs["wings"], key=lambda w: w[1])):
        wx, wy, ww, wh = w
        x0 = max(0, (wx - X0) * TILE - 1)
        x1 = min(W, (wx - X0 + ww) * TILE)
        y0 = max(0, (wy - Y0) * TILE - 1)
        y1 = min(H, (wy - Y0 + wh) * TILE)
        if x1 <= x0 or y1 <= y0:
            continue
        wide = (x1 - x0) >= (y1 - y0)
        # 屋脊在中间；北坡略暗（背光），南坡略亮（迎光）
        if wide:
            ry = (y0 + y1) // 2
            north = mix(c1, "#000000", 0.10)
            south = mix(c1, "#ffffff", 0.06)
            cv.rect(x0, y0, x1, ry - 4, north)
            cv.rect(x0, ry + 4, x1, y1, south)
        else:
            rx = (x0 + x1) // 2
            west = mix(c1, "#000000", 0.10)
            east = mix(c1, "#ffffff", 0.06)
            cv.rect(x0, y0, rx - 4, y1, west)
            cv.rect(rx + 4, y0, x1, y1, east)
        # 材质纹理
        if pal == "thatch":
            y = y0
            while y < y1:
                cv.line(x0, y, x1, y, mix(c1, "#000000", 0.16))
                cv.line(x0, y + 1, x1, y + 1, mix(c1, "#ffffff", 0.08))
                y += 5
            cv.speckle(x0, y0, x1, y1, c3, seed=seed + wi, density=0.022)
            cv.speckle(x0, y0, x1, y1, c0, seed=seed + wi + 5, density=0.010)
        else:
            x = x0
            while x < x1:                      # 瓦垄
                cv.line(x, y0, x, y1, mix(c1, "#000000", 0.24))
                cv.line(x + 1, y0, x + 1, y1, mix(c1, "#ffffff", 0.12))
                cv.line(x + 2, y0, x + 2, y1, mix(c1, "#000000", 0.10))
                x += 8
            y = y0
            while y < y1:                      # 瓦排横缝
                cv.line(x0, y, x1, y, mix(c1, "#000000", 0.14))
                y += 11
            cv.speckle(x0, y0, x1, y1, c3, seed=seed + wi, density=0.008)
        # 屋脊
        if wide:
            cv.rect(x0, ry - 5, x1, ry + 5, c0)
            cv.rect(x0, ry - 5, x1, ry - 2, mix(c0, "#ffffff", 0.55))
            cv.rect(x0, ry + 2, x1, ry + 5, c2)
        else:
            cv.rect(rx - 5, y0, rx + 5, y1, c0)
            cv.rect(rx - 5, y0, rx - 2, y1, mix(c0, "#ffffff", 0.55))
            cv.rect(rx + 2, y0, rx + 5, y1, c2)
        # 出檐：南边（近观众）压两道暗带，东西两边压一道
        cv.rect(x0, y1 - 6, x1, y1, c3)
        cv.rect(x0, y1 - 10, x1, y1 - 6, c2)
        cv.rect(x0, y0, x0 + 2, y1, c2)
        cv.rect(x1 - 2, y0, x1, y1, c2)
        cv.rect(x0, y0, x1, y0 + 1, mix(c0, "#ffffff", 0.30))
        # 烟囱（只在第一翼，靠近屋脊）
        if st.get("chimney") and wi == 0:
            cx = x0 + (x1 - x0) // 2 + 12
            cy = max(1, y0 + (y1 - y0) // 8)
            cv.rect(cx, cy, cx + 13, cy + 20, PAL["brick"][2])
            cv.rect(cx, cy, cx + 13, cy + 4, PAL["brick"][1])
            cv.rect(cx + 1, cy + 20, cx + 12, cy + 23, PAL["brick"][3])
            cv.rect(cx + 3, cy + 23, cx + 10, cy + 27, PAL["ink"][1])


# ================================================================ base
def paint_base(hs, st, seed, out_path):
    X0, Y0, X1, Y1 = hs["lot"]
    gw, gh = X1 - X0 + 1, Y1 - Y0 + 1
    W, H = gw * TILE, (gh + 1) * TILE
    cv = Canvas(W, H)
    grid = build_grid(hs)
    interior = interior_cells(hs)
    perim = perimeter_cells(hs, interior)
    is_ruin = bool(hs.get("ruin"))

    # ---- 1) 院子地面（画布第 32 行往下；顶部那格是墙顶面，必须留透明）----
    fill_ground(cv, 0, TILE, W, H, st["yard"], seed)

    if is_ruin:
        paint_ruin(cv, hs, st, seed, W, H)
        cv.save(out_path)
        return out_path

    # ---- 2) 房间地板（逐格画，保证铺满室内）----
    cell_ck = room_cell_colors(hs, interior)
    for (gx, gy), ck in sorted(cell_ck.items()):
        i, j = gx - X0, gy - Y0
        x0 = i * TILE
        x1 = x0 + TILE
        y0 = TILE + j * TILE
        y1 = y0 + TILE
        if ck == "yard":
            fill_ground(cv, x0, y0, x1, y1, "grass", seed + gx * 7 + gy)
        else:
            fill_room(cv, x0, y0, x1, y1, ck, seed + gx * 7 + gy)

    # ---- 3) 分类墙格 ----
    wall_cells = []
    door_cells = []
    gate_cells = []
    for j, row in enumerate(grid):
        for i, ch in enumerate(row):
            gx, gy = X0 + i, Y0 + j
            if ch == "#":
                wall_cells.append((gx, gy, i, j))
            elif ch == "D":
                door_cells.append((gx, gy, i, j))
            elif ch == "G":
                gate_cells.append((gx, gy, i, j))
    wall_set = set((c[0], c[1]) for c in wall_cells)

    def is_wall_at(gx, gy):
        return (gx, gy) in wall_set

    # ---- 4) 墙顶面（全部墙格都画；它盖住北邻那一格）----
    for (gx, gy, i, j) in sorted(wall_cells, key=lambda c: (c[3], c[2])):
        x0 = i * TILE
        y0 = TILE + j * TILE
        draw_cap(cv, x0, y0 - TILE, x0 + TILE, y0,
                 st["wall"], st["wall"], seed + gx * 3 + gy)

    # ---- 5) 南立面：只有南邻不是墙的墙格才看得见 ----
    for (gx, gy, i, j) in sorted(wall_cells, key=lambda c: (c[3], c[2])):
        if is_wall_at(gx, gy + 1):
            continue                       # 南邻也是墙 → 立面被它顶面盖住
        x0 = i * TILE
        y0 = TILE + j * TILE
        draw_facade(cv, x0, y0, x0 + TILE, y0 + TILE,
                    st["wall"], st["wall"], seed + gx * 5 + gy)
        if (gx, gy) not in perim:
            continue                       # 内隔墙不开窗
        if (gx, gy + 1) in interior:
            continue                       # 朝北的墙不朝观众
        if (gx, gy - 1) in interior:
            continue                       # 内侧墙不朝观众
        draw_window(cv, x0, y0, x0 + TILE, y0 + TILE)

    # ---- 6) 门 ----
    for (gx, gy, i, j) in door_cells:
        x0 = i * TILE
        y0 = TILE + j * TILE
        ns, ss = (gx, gy - 1) in interior, (gx, gy + 1) in interior
        ew, we = (gx - 1, gy) in interior, (gx + 1, gy) in interior
        if ss or not (ew or we):
            draw_door(cv, x0, y0, x0 + TILE, y0 + TILE)     # 南北向门 → 立面
        else:
            draw_passage(cv, x0, y0 - TILE, x0 + TILE, y0)  # 东西向门 → 顶面通口
    for (gx, gy, i, j) in gate_cells:
        x0 = i * TILE
        y0 = TILE + j * TILE
        draw_gate(cv, x0, y0, x0 + TILE, y0 + TILE)

    cv.save(out_path)
    return out_path


def paint_ruin(cv, hs, st, seed, W, H):
    """废墟态：夯土地基 + 残墙基 + 杂草；缺墙处留透明。"""
    X0, Y0, X1, Y1 = hs["lot"]
    demolished = set(tuple(p) for p in hs.get("demolished", []))
    grass = set(tuple(g) for g in hs.get("grass", []))
    grid = build_grid(hs)

    # 房间轮廓 = 夯土地基
    for ri, room in enumerate(hs.get("rooms", [])):
        rx0, ry0, rx1, ry1 = room[0], room[1], room[2], room[3]
        x0 = (rx0 - X0) * TILE
        x1 = (rx1 - X0 + 1) * TILE
        y0 = TILE + (ry0 - Y0) * TILE
        y1 = TILE + (ry1 - Y0 + 1) * TILE
        cv.rect(x0, y0, x1, y1, PAL["earth"][2])
        cv.speckle(x0, y0, x1, y1, PAL["earth"][1], seed=seed + ri, density=0.045)
        cv.speckle(x0, y0, x1, y1, PAL["earth"][3], seed=seed + ri + 9, density=0.025)
        cv.box(x0, y0, x1 - 1, y1 - 1, PAL["earth"][3], 1)

    # 残墙基：矮墙 8px，cap 面朝上
    for j, row in enumerate(grid):
        for i, ch in enumerate(row):
            if ch != "#":
                continue
            gx, gy = X0 + i, Y0 + j
            if (gx, gy) in demolished:
                continue
            x0 = i * TILE
            y0 = TILE + j * TILE
            cv.rect(x0, y0 + 8, x0 + TILE, y0 + TILE, PAL["stone"][2])
            cv.rect(x0, y0 + 8, x0 + TILE, y0 + 13, PAL["stone"][1])
            cv.rect(x0, y0 + TILE - 5, x0 + TILE, y0 + TILE, PAL["stone"][3])
            cv.speckle(x0, y0 + 8, x0 + TILE, y0 + TILE, PAL["stone"][3],
                       seed=seed + gx, density=0.05)

    # 杂草
    for (gx, gy) in sorted(grass):
        i, j = gx - X0, gy - Y0
        if i < 0 or j < 0 or i > X1 - X0 or j > Y1 - Y0:
            continue
        x0 = i * TILE
        y0 = TILE + j * TILE
        for k in range(5):
            px = x0 + 4 + k * 6
            h = 8 + (k * 5 + gx) % 7
            cv.line(px, y0 + 27, px, y0 + 27 - h, PAL["leaf_d"][1], 2)
            cv.px(px, y0 + 27 - h, PAL["leaf"][0])


# ================================================================ 废墟的 roof 层
def paint_ruin_roof_mask(hs, base_abs, out_abs):
    """废墟的「屋顶层」不是美术，是**遮罩**：把 base 在这块地上的样子原样顶上去。

    为什么不能交透明图（读 scripts/world_view.gd:900-945 就明白）：
      _draw_roof **无条件**先用每个 wing 画一遍色块屋顶（:912-934），
      然后才在 :937-945 按同一锚点、同一尺寸叠 tex_roof。
      ⇒ 缺 roof 图时，玩家看到的是「实心色块屋顶盖在塌掉的房子上」；
        交一张全透明 PNG 也压不掉它（色块在下面，透明图只是让色块露出来）。

    所以这里沿着 draw_roof 同一套 x0/x1/y0/y1 公式算出翼投影区，把 base 在那块的像素
    原样复制进 roof 画布，其余留透明 —— 效果是 roof 层在废墟上「什么都不加」，
    _draw_roof 那块色块被 base 自己的样子盖住。

    根治办法是引擎对 ruin 跳过色块屋顶（本线零代码改动，已写进
    docs/FEEDBACK-house-art-a4a5-exec.md 的已知限制）。动这张图之前先读那段。
    """
    X0, Y0 = hs["lot"][0], hs["lot"][1]
    base = Image.open(base_abs).convert("RGBA")
    W, H = base.size
    cv = Canvas(W, H)                     # 默认全透明
    for w in sorted(hs["wings"], key=lambda w: w[1]):
        wx, wy, ww, wh = w
        x0 = max(0, (wx - X0) * TILE - 1)
        x1 = min(W, (wx - X0 + ww) * TILE)
        y0 = max(0, (wy - Y0) * TILE - 1)
        y1 = min(H, (wy - Y0 + wh) * TILE)
        if x1 <= x0 or y1 <= y0:
            continue
        cv.im.paste(base.crop((x0, y0, x1, y1)), (x0, y0))
    cv.save(out_abs)
    return out_abs


# ================================================================ 主流程
def gen_one(houses, hid, fam, fr, st, want, made):
    """一栋房：base 一定出；roof 按 manifest（A1–A3）或 lot 推导（A4/A5）出。"""
    hs = houses[hid]
    seed = sum(ord(c) for c in hid) * 37 + 11
    base_rel = "assets/village/houses/%s/%s_base.png" % (fam, fr)
    roof_rel = "assets/village/houses/%s/%s_roof.png" % (fam, fr)
    base_abs = os.path.join(ROOT, base_rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(base_abs), exist_ok=True)
    paint_base(hs, st, seed, base_abs)
    made.append(base_rel)

    ruin = bool(hs.get("ruin"))
    if ruin and hid not in RUIN_ROOF_IDS:   # 废墟没有 roof
        return

    if roof_rel in want:
        px = want[roof_rel]["cpx"]
    else:                                # A4/A5 不在 a1a3 manifest 里，按 lot 推
        gw = hs["lot"][2] - hs["lot"][0] + 1
        gh = hs["lot"][3] - hs["lot"][1] + 1
        px = (gw * TILE, (gh + 1) * TILE)
    roof_abs = os.path.join(ROOT, roof_rel.replace("/", os.sep))
    if ruin:
        paint_ruin_roof_mask(hs, base_abs, roof_abs)
    else:
        cv = Canvas(px[0], px[1])
        draw_roof(cv, hs, st, seed, px[0], px[1])
        cv.save(roof_abs)
    made.append(roof_rel)


def main(argv=()):
    with open(DATA, "r", encoding="utf-8") as f:
        houses = {h["id"]: h for h in json.load(f)}
    with open(MANIFEST, "r", encoding="utf-8") as f:
        man = json.load(f)
    want = {s["path"]: s for s in man["shell"]}

    only = set(argv)                     # 传 id 只跑那几栋（不传 = 全跑，含 A4/A5）
    made = []
    for hid in ORDER:
        if only and hid not in only:
            continue
        fam, fr = FAMILY[hid]
        st = dict(STYLE[(fam, fr)])
        if fam == "shen":
            st["chimney"] = True
        gen_one(houses, hid, fam, fr, st, want, made)
    for hid in ORDER_A45:
        if only and hid not in only:
            continue
        fam, fr = FAMILY_A45[hid]
        st = dict(STYLE_A45[(fam, fr)])
        if fam == "shen":
            st["chimney"] = True
        gen_one(houses, hid, fam, fr, st, want, made)
    print("generated %d files" % len(made))
    for m in made:
        print("  " + m)


if __name__ == "__main__":
    main(sys.argv[1:])
