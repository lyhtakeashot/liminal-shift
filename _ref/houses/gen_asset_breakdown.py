"""
A1–A3 美术资产拆解图 + 总需求清单生成器
====================================================================
产出（给美术同学）：
  _ref/art/_assets_a1a3/A1_1926/<id>_assets.png   每栋一张资产拆解图（12 张）
  _ref/art/_assets_a1a3/A2_1951/...
  _ref/art/_assets_a1a3/A3_1976/...
  _ref/art/_assets_a1a3/_scene_a1a3_assets.png   三帧场景元素对比 + 清单（1 张）
  _ref/art/_assets_a1a3/_a1a3_assets.csv         总需求清单（Excel 可直接开）
  _ref/art/_assets_a1a3/_a1a3_assets.json        同一份数据的机器可读版

口径（2026-11-21 定）：
  1 格 = 16×16 px，所有资产画布尺寸都是 16 的整数倍。
  外观层 = 整栋单图（base / roof 各 1 张，每栋每帧 2 张），不做 16px 瓦片拼接。
  家具层 = 逐件一个文件，全部对齐 16px 网格（1×1 … 3×3 九档），跨栋共享 props/。
  场景层 = 河/坝/路/田/井/树/碑，按 frames.json 的实际几何出尺寸。

真相源：_ref/houses/houses_data.json（房型/家具）、data/frames.json（场景）。
跑法：
  C:\\Users\\lyh\\.dsh\\dsh-runtimes\\dsh-primary-runtime\\dependencies\\python\\python.exe -X utf8 gen_asset_breakdown.py
"""
import os
import json
import csv
import math
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.dirname(HERE)
ROOT = os.path.dirname(REF)
OUT = os.path.join(REF, "art", "_assets_a1a3")

DATA_PATH = os.path.join(HERE, "houses_data.json")
FRAMES_PATH = os.path.join(ROOT, "data", "frames.json")

TILE = 16
W = 1520
MARGIN = 44
ROW = 26

FONTS_R = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]
FONTS_B = ["C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc",
           "C:/Windows/Fonts/simhei.ttf"]


def font(size, bold=False):
    for p in (FONTS_B if bold else FONTS_R):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


C = {
    "bg": "#191814", "panel": "#211f1a", "panel2": "#262319",
    "text": "#e6dfd0", "gray": "#9a9284", "key": "#e0bb74", "dim": "#6f695c",
    "grid": "#333029", "wall": "#8c6b4a", "wall_top": "#c9a878",
    "part": "#6d5238", "part_top": "#9c7c56",
    "door": "#e0b25a", "gate": "#9a6a3a", "measure": "#7fa8c8",
    "player": "#e8543f", "player_edge": "#ffd9c4", "lot": "#a8905a",
    "yard": "#3b3a2e", "furn": "#c8b48f", "furn_edge": "#e8d7b2",
    "clue": "#d98b45", "yard_furn": "#a9b58a", "yard_edge": "#d3dfae",
    "ruin_wall": "#7a6a55", "ruin_base": "#544c3a", "ruin_grass": "#6f7d4c",
    "head": "#2b2620", "head_line": "#4a4234",
    "room": {"bed": "#9c8468", "hall": "#cbb997", "store": "#8d9a6f",
             "kitchen": "#bdd0b0", "account": "#a8c0d0", "yard": "#3b3a2e",
             "shop": "#b99aa6", "class": "#9dbacd", "mill": "#b5a878",
             "toilet": "#9aa8a8"},
}

ORDER = [
    ("A1", "lu_house"), ("A1", "mill_a1"), ("A1", "shen_a1"), ("A1", "zhou_house"),
    ("A2", "mill_a2"), ("A2", "shen_a2"), ("A2", "lu_a2"), ("A2", "zhou_a2"),
    ("A3", "mill_a3"), ("A3", "shen_a3"), ("A3", "zhou_a3"), ("A3", "lu_a3"),
]
FRAME_OF = {hid: fr for fr, hid in ORDER}
FRAME_DIR = {"A1": "A1_1926", "A2": "A2_1951", "A3": "A3_1976"}
FRAME_YEAR = {"A1": "1926", "A2": "1951", "A3": "1976"}

# 每栋 → (族目录, 帧前缀)；交付路径 assets/village/houses/<族>/<帧>_base.png / _roof.png
FAMILY = {
    "lu_house": ("lu", "a1"), "lu_a2": ("lu", "a2"), "lu_a3": ("lu", "a3"),
    "shen_a1": ("shen", "a1"), "shen_a2": ("shen", "a2"), "shen_a3": ("shen", "a3"),
    "mill_a1": ("mill", "a1"), "mill_a2": ("mill", "a2"), "mill_a3": ("mill", "a3"),
    "zhou_house": ("zhou", "a1"), "zhou_a2": ("zhou", "a2"), "zhou_a3": ("zhou", "a3"),
}

# 家具中文名 → 文件名 slug（同名的不同占地尺寸 = 不同贴图，slug 后统一加 _<w>x<h>）
SLUG = {
    "凳": "deng", "水缸": "shuigang", "粮囤": "liangdun", "茅房": "maofang",
    "八仙桌": "baxianzhuo", "柴堆": "chaidui", "茅坑": "maokeng", "书架": "shujia",
    "单人床": "danrenchuang", "双人床": "shuangrenchuang", "木箱": "muxiang",
    "灶台": "zaotai", "衣柜": "yigui", "酒坛": "jiutan", "长凳": "changdeng",
    "柜": "gui", "置物台": "zhiwutai", "老井": "laojing", "藤椅": "tengyi",
    "账桌": "zhangzhuo", "书桌": "shuzhuo", "墙基暗龛": "qiangji_ankan",
    "小桌": "xiaozhuo", "屏风": "pingfeng", "旧木箱": "jiu_muxiang",
    "条案": "tiaoan", "柴火灶": "chaihuozao", "水盆": "shuipen",
    "灯笼": "denglong", "牌位": "paiwei", "盆景": "penjing", "石磨": "shimo",
    "祖宗牌位": "zuzong_paiwei", "花盆": "huapen", "便民服务台": "bianmin_tai",
    "倒塌的灶台残砖": "daota_zaotai", "农具架": "nongjujia",
    "单据柜+算盘": "danjuji_suanpan", "土圆仓": "tuyuancang",
    "土坯灶台": "tupi_zaotai", "堂屋地基痕迹": "tangwu_diji",
    "小衣柜": "xiao_yigui", "庭树": "tingshu", "弃置石磨": "qizhi_shimo",
    "恭桶": "gongtong", "搪瓷盆": "tangcipen", "旧木床": "jiu_muchuang",
    "晒席": "shaixi", "木跳板+记码牌": "mutiaoban_jimapai", "条凳": "tiaodeng",
    "案板": "anban", "椅": "yi", "水冲蹲便器": "dunbianqi", "水池": "shuichi",
    "水泥封层": "shuini_fengceng", "洗手盆": "xishoupen", "溜筛": "liushai",
    "石桌": "shizhuo", "碗柜": "wangui", "磅秤": "bangcheng",
    "箩筐": "luokuang", "蒸笼": "zhenglong", "蜂窝煤炉": "fengwomeilu",
    "铁锅": "tieguo", "风车": "fengche", "验粮台+取样铁管": "yanliangtai",
    "验粮器": "yanliangqi", "鸡笼": "jilong", "麻袋": "madai",
}


# ----------------------------------------------------------------- 数据装载
def load_houses():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        lst = json.load(f)
    return {h["id"]: h for h in lst}


def load_frames():
    with open(FRAMES_PATH, "r", encoding="utf-8") as f:
        d = json.load(f)
    return {v.get("id"): v for v in d["frames"]}, d


def furn_slug(name, w, h):
    s = SLUG.get(name)
    if s is None:
        raise KeyError("家具名没有 slug：" + name)
    return "%s_%dx%d" % (s, w, h)


def lot_size(hs):
    x0, y0, x1, y1 = hs["lot"]
    return x1 - x0 + 1, y1 - y0 + 1


def wing_bbox(hs):
    xs0 = min(w[0] for w in hs["wings"])
    ys0 = min(w[1] for w in hs["wings"])
    xs1 = max(w[0] + w[2] for w in hs["wings"])
    ys1 = max(w[1] + w[3] for w in hs["wings"])
    return xs1 - xs0, ys1 - ys0


# ----------------------------------------------------------------- 网格（沿用
# gen_all_houses.py 的墙体推导，保证拆解图和现有占地图口径完全一致）
def build_grid(hs):
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
            elif c in part:
                row += "p"
            elif is_wall(i, j):
                row += "#"
            elif c in interior:
                row += "."
            else:
                row += " "
        rows.append(row)
    return rows


def room_of(hs, x, y):
    for room in hs["rooms"]:
        x0, y0, x1, y1, name, ck = room[:6]
        if x0 <= x <= x1 and y0 <= y <= y1:
            return name, ck
    return None, None


def occupied(hs, gx, gy):
    for f in hs["furniture"]:
        x, y, w, h = f["rect"]
        if x <= gx < x + w and y <= gy < y + h:
            return f
    return None


def auto_player_at(hs, grid):
    X0, Y0, X1, Y1 = hs["lot"]

    def walkable(i, j):
        if not (X0 <= i <= X1 and Y0 <= j <= Y1):
            return False
        ch = grid[j - Y0][i - X0]
        return ch in (".", " ") and not occupied(hs, i, j)

    for prefer in (" ", "."):
        for j in range(Y1, Y0, -1):
            for i in range(X1, X0, -1):
                if not (X0 <= i <= X1 and Y0 <= j <= Y1):
                    continue
                if grid[j - Y0][i - X0] == prefer and walkable(i, j):
                    return (i, j)
    for j in range(Y1, Y0, -1):
        for i in range(X1, X0, -1):
            if walkable(i, j):
                return (i, j)
    return (X0 + 1, Y0 + 1)


# ----------------------------------------------------------------- 资产登记表
def build_registry(houses):
    """所有 A1–A3 的资产去重成一张登记表。返回 (props列表, 外观列表, 索引)。"""
    props = {}
    for fr, hid in ORDER:
        hs = houses[hid]
        for f in hs["furniture"]:
            x, y, w, h = f["rect"]
            rid = furn_slug(f["name"], w, h)
            rec = props.get(rid)
            if rec is None:
                rec = props[rid] = {
                    "id": rid, "name": f["name"], "short": f.get("short") or f["name"],
                    "w": w, "h": h, "px": [w * TILE, h * TILE],
                    "layer": "props", "zone": f.get("zone", "house"),
                    "yard_building": bool(f.get("yard_building")),
                    "uses": 0, "houses": [], "clue_houses": [],
                    "path": "assets/village/props/%s.png" % rid,
                    "notes": [],
                }
            rec["uses"] += 1
            if hid not in rec["houses"]:
                rec["houses"].append(hid)
            if f.get("clue") and hid not in rec["clue_houses"]:
                rec["clue_houses"].append(hid)
            note = (f.get("note") or "").strip()
            if note and note not in rec["notes"]:
                rec["notes"].append(note)
    plist = sorted(props.values(), key=lambda r: (-r["uses"], r["name"], r["w"], r["h"]))
    for i, rec in enumerate(plist):
        rec["code"] = "P%02d" % (i + 1)
    by_id = {r["id"]: r for r in plist}

    shells = []
    for fr, hid in ORDER:
        hs = houses[hid]
        gw, gh = lot_size(hs)
        bw, bh = wing_bbox(hs)
        fam, ffr = FAMILY[hid]
        # 画布口径（house-spec §4.8.5 / 伪 3D 投影）：高度比占地多一格。
        # w/h/px 继续表示**占地**（[A] 格图和碰撞都要用），画布另用 cw/ch/cpx。
        # 多出的 16px 在**画布顶部**，是墙 + 屋顶立起来的高度；画布底边仍与 lot 底边对齐。
        cw, ch = gw, gh + 1
        cpx = [cw * TILE, ch * TILE]
        shells.append({
            "id": "%s_base" % hid, "code": "B", "house": hid, "frame": fr,
            "layer": "base", "w": gw, "h": gh, "px": [gw * TILE, gh * TILE],
            "cw": cw, "ch": ch, "cpx": cpx,
            "wing": [bw, bh],
            "path": "assets/village/houses/%s/%s_base.png" % (fam, ffr),
            "uses": 1, "houses": [hid], "clue_houses": [],
            "desc": ("废墟态：残墙基 + 夯土地基 + 杂草底；墙缺失处留透明，不画屋顶；"
                     "顶部多出的一格是残墙立起的高度"
                     if hs.get("ruin") else
                     "地板 + 墙内侧 + 南立面 + 墙顶面 + 院子地面（无屋顶）；"
                     "顶部多出的一格是墙立起来的高度"),
        })
        if hs.get("ruin"):
            continue    # 废墟没有屋顶层，不交付 roof
        shells.append({
            "id": "%s_roof" % hid, "code": "R", "house": hid, "frame": fr,
            "layer": "roof", "w": gw, "h": gh, "px": [gw * TILE, gh * TILE],
            "cw": cw, "ch": ch, "cpx": cpx,
            "wing": [bw, bh],
            "path": "assets/village/houses/%s/%s_roof.png" % (fam, ffr),
            "uses": 1, "houses": [hid], "clue_houses": [],
            "desc": "屋面 + 檐口；画布与 base 同宽同高，只有屋本体 %d×%d 有像素，其余透明" % (bw, bh),
        })
    return plist, shells, by_id


# ----------------------------------------------------------------- 场景资产
def scene_assets(frames):
    """按 frames.json 的真实几何算场景元素尺寸（一帧一份，跨帧同形可共用）。"""
    out = []
    for fr in ("A1", "A2", "A3"):
        f = frames.get("a%s_%s" % (fr[1], FRAME_YEAR[fr]))
        if f is None:
            continue
        year = FRAME_YEAR[fr]
        # 河：全宽多边形，深度按列变化
        river = [s for s in f["shapes"] if s.get("label") == "河"]
        if river:
            pts = river[0]["points"]
            depth_px = max(p[1] for p in pts if p[1] > 0)
            out.append(dict(id="river_%s" % fr.lower(), code="S",
                            name="河（含河岸、水面）", frame=fr,
                            w=100, h=int(math.ceil(depth_px / TILE)),
                            px=[1600, int(math.ceil(depth_px / TILE)) * TILE],
                            path="assets/village/scene/river_%s.png" % fr.lower(),
                            note="全宽 100 格；最深 %d 格（%d px）"
                                 % (int(math.ceil(depth_px / TILE)), int(math.ceil(depth_px / TILE)) * TILE)))
        for s in f["shapes"]:
            lab = s.get("label")
            if lab == "坝":
                w_, h_ = s["rect"][2], s["rect"][3]
                out.append(dict(id="dam", code="S", name="石坝", frame=fr,
                                w=w_ // TILE, h=h_ // TILE, px=[w_, h_],
                                path="assets/village/scene/dam.png",
                                note="三帧同形同尺寸，共用 1 张"))
            elif lab == "碑":
                w_, h_ = s["rect"][2], s["rect"][3]
                out.append(dict(id="stele", code="S", name="界碑（周界半截石碑）", frame=fr,
                                w=1, h=1, px=[TILE, TILE],
                                path="assets/village/scene/stele.png",
                                note="原件 %d×%d px，装进 1×1 格画布（图上 8px 宽）" % (w_, h_)))
        # 路：2026-11-21 起 frames.json 改成**逐格 rect + road 标记**（不再是 path 折线），
        # A3 是一条宽 rect 取直。所以这里按 rect 集合算包围盒，弯/直看是否只有一行。
        roads = [s["rect"] for s in f["shapes"] if s.get("road")]
        if roads:
            rx0 = min(r[0] for r in roads)
            ry0 = min(r[1] for r in roads)
            rx1 = max(r[0] + r[2] for r in roads)
            ry1 = max(r[1] + r[3] for r in roads)
            curved = len(set(r[1] for r in roads)) > 1
            rid = "road_curved" if curved else "road_straight"
            # 路宽：按「逐列覆盖格数的众数」实测，不猜常量。
            # 2026-11-21 `_path_to_tiles.py` 把路从 32px 改成 48px（3 格）；
            # 弯道两侧会自然收到 1~2 格，所以取众数而不是最小值/最大值。
            cells = set()
            for rx, ry, rw, rh in roads:
                for cx in range(rx // TILE, (rx + rw) // TILE):
                    for cy in range(ry // TILE, (ry + rh) // TILE):
                        cells.add((cx, cy))
            colcnt = {}
            for cx, cy in cells:
                colcnt[cx] = colcnt.get(cx, 0) + 1
            road_g = max(set(colcnt.values()), key=lambda v: (list(colcnt.values()).count(v), v)) \
                if colcnt else 2
            out.append(dict(id=rid, code="S", name="主路（宽 %d 格）" % road_g, frame=fr,
                            w=int(math.ceil((rx1 - rx0) / TILE)),
                            h=int(math.ceil((ry1 - ry0) / TILE)),
                            px=[rx1 - rx0, ry1 - ry0],
                            path="assets/village/scene/%s_tiles.png" % rid,
                            note="%s；路宽 %d 格 = %dpx（逐列实测众数），共 %d 个路面格；"
                                 "出 16px 瓦片集（直/弯/丁字/十字）"
                                 % ("弯道（A1/A2 同走向，两侧会收边到 1~2 格）" if curved
                                    else "直道（A3 起取直）",
                                    road_g, road_g * TILE, len(cells))))
        # 田：碎田是无 label 的小 rect；整块大田是一条大 rect。用面积区分，不靠写死的颜色。
        plain = [s["rect"] for s in f["shapes"]
                 if s.get("type") == "rect" and not s.get("label") and not s.get("road")]
        if plain:
            if len(plain) > 1:
                sizes = sorted(set((r[2] // TILE, r[3] // TILE) for r in plain))
                sizetxt = "、".join("%d×%d" % s for s in sizes[:3])
                if len(sizes) > 3:
                    sizetxt += " 等 %d 种" % len(sizes)
                x0 = min(r[0] for r in plain)
                y0 = min(r[1] for r in plain)
                x1 = max(r[0] + r[2] for r in plain)
                y1 = max(r[1] + r[3] for r in plain)
                out.append(dict(id="field_a1", code="S", name="碎田（零散小块）", frame=fr,
                                w=int(math.ceil((x1 - x0) / TILE)),
                                h=int(math.ceil((y1 - y0) / TILE)),
                                px=[x1 - x0, y1 - y0],
                                path="assets/village/scene/field_patch_tiles.png",
                                note="%d 块，单块 %s格；出 16px 土/田埂瓦片" % (len(plain), sizetxt)))
            else:
                r = plain[0]
                out.append(dict(id="field_%s" % fr.lower(), code="S", name="整块大田", frame=fr,
                                w=r[2] // TILE, h=r[3] // TILE, px=[r[2], r[3]],
                                path="assets/village/scene/field_%s.png" % fr.lower(),
                                note="%d×%d 格；A2 与 A3 同尺寸、同田埂，只差土色"
                                     % (r[2] // TILE, r[3] // TILE)))
        # 井：4 态（开挖/封盖/锁死/水泥封）
        well = [s for s in f["shapes"] if s.get("label", "").startswith("老井")]
        if well:
            r = well[0].get("radius", 16)
            d_ = int(round(r * 2 / TILE))
            lbl = well[0]["label"]
            suffix = lbl[len("老井"):].lstrip("·").strip() if lbl.startswith("老井") else lbl
            wname = "老井（%s）" % suffix if suffix else "老井"
            out.append(dict(id="well_old_%s" % fr.lower(), code="S", name=wname,
                            frame=fr, w=d_, h=d_, px=[d_ * TILE, d_ * TILE],
                            path="assets/village/scene/well_old_%s.png" % fr.lower(),
                            note="4 态：开挖 / 封盖 / 锁死 / 水泥封；本帧 %d×%d 格用其中一态" % (d_, d_)))
        # 老槐：树径按帧递增
        tree = [s for s in f["shapes"] if s.get("label") == "老槐"]
        if tree:
            r = tree[0].get("radius", 16)
            d_ = int(round(r * 2 / TILE))
            out.append(dict(id="tree_%s" % fr.lower(), code="S", name="老槐", frame=fr,
                            w=d_, h=d_, px=[d_ * TILE, d_ * TILE],
                            path="assets/village/scene/tree_%s.png" % fr.lower(),
                            note="4 态：树苗 / 中 / 大 / 树桩；本帧 %d×%d 格" % (d_, d_)))
        # 地面底瓦
        g = f.get("ground", "#4a5a3a")
        out.append(dict(id="ground_tile_%s" % fr.lower(), code="S", name="地面底瓦", frame=fr,
                        w=1, h=1, px=[TILE, TILE],
                        path="assets/village/scene/ground_%s_tiles.png" % fr.lower(),
                        note="可平铺 16×16 地面（草地/土），帧底色 %s" % g))
    return out


# ----------------------------------------------------------------- 绘制工具
def tlen(d, s, f):
    return d.textlength(s, font=f)


def fit(d, s, f, maxw):
    if tlen(d, s, f) <= maxw:
        return s
    while s and tlen(d, s + "…", f) > maxw:
        s = s[:-1]
    return (s + "…") if s else ""


def wrap_px(d, s, f, maxw):
    """按像素宽硬折行（中文无空格，逐字折）。"""
    out, cur = [], ""
    for ch in s:
        if tlen(d, cur + ch, f) > maxw and cur:
            out.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


def panel(d, box, fill=None, outline=None, width=2):
    d.rectangle(box, fill=fill or C["panel"], outline=outline or C["head_line"], width=width)


def draw_table(d, x, y, width, headers, widths, rows, colors=None, hdr_h=24, row_h=ROW,
               font_hdr=13, font_row=12):
    """表头 + 行；widths 之和应 ≈ width。返回表尾 y。"""
    d.rectangle([x, y, x + width, y + hdr_h], fill=C["head"])
    cx = x
    for i, htxt in enumerate(headers):
        d.text((cx + 6, y + hdr_h / 2), htxt, font=font(font_hdr, True),
               fill=C["key"], anchor="lm")
        cx += widths[i]
    yy = y + hdr_h
    for r, row in enumerate(rows):
        bg = C["panel"] if r % 2 == 0 else C["panel2"]
        d.rectangle([x, yy, x + width, yy + row_h], fill=bg)
        cx = x
        for i, cell in enumerate(row):
            txt = str(cell)
            f = font(font_row)
            txt = fit(d, txt, f, widths[i] - 10)
            col = C["text"]
            if colors and colors[r] and colors[r][i]:
                col = colors[r][i]
            anchor = "lm"
            d.text((cx + 6, yy + row_h / 2), txt, font=f, fill=col, anchor=anchor)
            cx += widths[i]
        yy += row_h
    d.line([(x, yy), (x + width, yy)], fill=C["head_line"], width=1)
    return yy


# ----------------------------------------------------------------- 单栋拆解图
def _shell_note(is_ruin):
    """[B] 外观层表下那句说明。抽出来是因为要先量它折几行才能定 [C] 的位置。"""
    if is_ruin:
        return ("废墟态只交付 1 张：没有屋顶所以不交 roof。缺墙的位置必须透明，"
                "让场景底图的地面透出来。画布仍比占地高一格 —— 残墙也要向上立起来。")
    return ("画布比占地高 16px：屋顶与墙顶面要向上溢出画布一格，画布不带这一格会被裁掉一条"
            "（不报错、验收也看不出来，跑起来才发现要重画）。多出的一格在顶部，"
            "画布底边仍与占地底边对齐，锚点仍是底部中心。base / roof 必须同宽同高同锚点"
            "（高度都是 占地高 + 16），玩家走进占地矩形时 roof 整层淡出、base 留在原地。")


def render_house(hs, by_id, props_of_house):
    hid = hs["id"]
    fr = FRAME_OF[hid]
    year = FRAME_YEAR[fr]
    fam, ffr = FAMILY[hid]
    X0, Y0, X1, Y1 = hs["lot"]
    gw, gh = X1 - X0 + 1, Y1 - Y0 + 1
    bw, bh = wing_bbox(hs)
    grid = build_grid(hs)
    is_ruin = bool(hs.get("ruin"))
    grass = set(tuple(g) for g in hs.get("grass", []))

    # ---------- 顶部信息块 ----------
    clue_lines = hs.get("clue", []) or []
    header_h = 150 + 22 * len(clue_lines)

    # ---------- 网格 ----------
    S = max(22, min(46, int((W - 2 * MARGIN - 170) / gw)))
    grid_top = header_h + 34
    grid_left = MARGIN + 72
    grid_h = gh * S + 60

    # ---------- 清单 ----------
    rows_all = []
    notes_all = []
    groups, seen = [], {}
    for rec in props_of_house:
        room, ck = room_of(hs, rec["rect"][0] + rec["rect"][2] / 2.0 - 0.5,
                           rec["rect"][1] + rec["rect"][3] / 2.0 - 0.5)
        zone = "院" if (rec.get("zone") == "yard" or rec.get("yard_building")) else "屋"
        rn = room or ("院子" if zone == "院" else "—")
        rid = rec["file_id"]
        if rid in seen:
            g = groups[seen[rid]]
            g["n"] += 1
            if rn not in g["rooms"]:
                g["rooms"].append(rn)
            g["clue"] = g["clue"] or bool(rec.get("clue"))
            if not g["note"]:
                g["note"] = (rec.get("note") or "").strip()
            continue
        seen[rid] = len(groups)
        groups.append(dict(rec=rec, n=1, rooms=[rn], zone=zone,
                           clue=bool(rec.get("clue")), note=(rec.get("note") or "").strip()))

    for g in groups:
        rec = g["rec"]
        rn = "/".join(g["rooms"][:2]) + ("等" if len(g["rooms"]) > 2 else "")
        rows_all.append([rec["code"], rec["file_id"], rec["name"],
                         "%d×%d" % (rec["w"], rec["h"]),
                         "%d×%d" % (rec["w"] * TILE, rec["h"] * TILE),
                         g["zone"], rn, "%d" % g["n"],
                         "%d" % rec["global_uses"],
                         "◆" if g["clue"] else ""])
        notes_all.append(g["note"])

    avail = W - 2 * MARGIN
    two_col = len(rows_all) > 20
    ncol = 2 if two_col else 1
    rows_per_col = int(math.ceil(len(rows_all) / float(ncol))) if rows_all else 0
    colw10 = [46, 158, 92, 52, 84, 34, 104, 40, 56, 26]
    hdr = ["编号", "文件 id（禁改）", "资产名", "格数", "像素", "区",
           "所在房间", "本栋", "全项目", "◆"]
    if two_col:
        colw = colw10
    else:
        narrow = [44, 150, 90, 52, 84, 32, 100, 38, 54, 24]
        colw = narrow + [avail - sum(narrow)]
        hdr = hdr + ["说明（摆放要求 / 线索文案）"]
        for r, nt in zip(rows_all, notes_all):
            r.append(nt)

    # 版式：顺序排，高度先算后画（避免板块互相压）
    _mdraw = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    yA = header_h + 12
    grid_top = header_h + 64
    grid_h = gh * S + 58
    yB = grid_top + grid_h + 4
    yB_tbl = yB + 30
    yB_note = yB_tbl + 30 + 2 * 30 + 6
    # [B] 的说明文字是动态折行的（废墟态 2~3 行、正常态 4 行），[C] 必须接在它下面
    shell_note_txt = _shell_note(is_ruin)
    note_b_lines = wrap_px(_mdraw, shell_note_txt, font(13), avail - 12)
    yC = yB_note + 19 * len(note_b_lines) + 14
    yD_title = yC + 50
    yD_tbl = yD_title + 28
    yfoot = yD_tbl + 24 + rows_per_col * ROW + 26
    note_lines = wrap_px(_mdraw, hs.get("note", "") or "", font(14), avail)
    n_shell = 1 if is_ruin else 2
    total_h = yfoot + 44 + 22 * max(1, len(note_lines))
    n_slot = len(groups)

    img = Image.new("RGB", (W, total_h), C["bg"])
    d = ImageDraw.Draw(img)

    # ---------- 标题 ----------
    d.text((MARGIN, 22), "%s · 资产拆解图" % hs["name"], font=font(30, True), fill=C["text"])
    d.text((MARGIN, 70),
           "占地 %d×%d 格 = %d×%d px ｜ 屋本体 %d×%d 格 ｜ 外观画布 %d×%d px（顶部多一格立面）｜ "
           "1 格 = 16×16 px ｜ 640×360 · 3x 整数缩放"
           % (gw, gh, gw * TILE, gh * TILE, bw, bh, gw * TILE, (gh + 1) * TILE),
           font=font(15), fill=C["key"])
    d.text((MARGIN, 96),
           "本栋交付：外观 %d 张 + 家具 %d 种（本栋共摆 %d 件，含跨栋复用）= 共 %d 个文件%s"
           % (n_shell, n_slot, len(props_of_house), n_shell + n_slot,
              "（废墟态：不交付 roof）" if is_ruin else ""),
           font=font(14), fill=C["gray"])
    d.text((MARGIN, 118),
           "灰棕=外墙板  深棕=内部隔墙  棕=室内地面  深绿=院子  黄=房门  深棕块=院门  橙框=可检视线索",
           font=font(13), fill=C["dim"])
    yy = 142
    for ln in clue_lines:
        d.text((MARGIN, yy), "◆ " + ln, font=font(14), fill=C["clue"], anchor="lm")
        yy += 22
    d.line([(MARGIN, header_h + 2), (W - MARGIN, header_h + 2)], fill=C["head_line"], width=2)

    # ---------- 网格 ----------
    ox, oy = grid_left, grid_top
    d.text((MARGIN, yA), "[A] 占地格图（每格 = 16px；编号对应下表「编号」列）",
           font=font(17, True), fill=C["key"])
    d.rectangle([ox, oy, ox + gw * S, oy + gh * S], outline=C["lot"], width=3)

    rf = font(11 if S < 34 else 12)
    for gx in range(gw):
        d.text((ox + gx * S + S / 2, oy - 12), str(gx), font=rf, fill="#c9c0ae", anchor="mm")
    for gy in range(gh):
        d.text((ox - 10, oy + gy * S + S / 2), str(gy), font=rf, fill="#c9c0ae", anchor="mm")

    for ry, row in enumerate(grid):
        for rx, ch in enumerate(row):
            bx, by = ox + rx * S, oy + ry * S
            box = [bx, by, bx + S - 1, by + S - 1]
            if is_ruin:
                if ch in ("#", "p"):
                    d.rectangle(box, fill=C["ruin_wall"])
                    if (rx * 3 + ry * 5) % 4:
                        d.line([(bx + 2, by + 2), (bx + S - 3, by + 2)],
                               fill=C["ruin_base"], width=3)
                elif ch in ("D", "G", "."):
                    d.rectangle(box, fill=C["ruin_base"])
                else:
                    d.rectangle(box, fill=C["yard"])
                if (X0 + rx, Y0 + ry) in grass:
                    d.rectangle([bx + 2, by + 2, bx + S - 3, by + S - 3],
                                outline=C["ruin_grass"], width=2)
                    d.text((bx + S / 2, by + S / 2), "草", font=font(12),
                           fill=C["ruin_grass"], anchor="mm")
                continue
            if ch == "#":
                d.rectangle(box, fill=C["wall"])
                d.line([(bx, by), (bx + S - 1, by)], fill=C["wall_top"], width=3)
            elif ch == "p":
                d.rectangle(box, fill=C["part"])
                d.line([(bx, by), (bx + S - 1, by)], fill=C["part_top"], width=3)
            elif ch == "D":
                d.rectangle(box, fill=C["door"])
            elif ch == "G":
                d.rectangle(box, fill=C["gate"])
            elif ch == ".":
                _, ck = room_of(hs, X0 + rx, Y0 + ry)
                d.rectangle(box, fill=C["room"].get(ck, "#6b5842"))
            else:
                d.rectangle(box, fill=C["yard"])

    # 网格线（浅）
    for gx in range(gw + 1):
        d.line([(ox + gx * S, oy), (ox + gx * S, oy + gh * S)], fill=C["grid"], width=1)
    for gy in range(gh + 1):
        d.line([(ox, oy + gy * S), (ox + gw * S, oy + gy * S)], fill=C["grid"], width=1)

    # 家具块
    for rec in props_of_house:
        fx, fy, fw, fh = rec["rect"]
        bx, by = ox + (fx - X0) * S, oy + (fy - Y0) * S
        bw_, bh_ = fw * S, fh * S
        clue = bool(rec.get("clue"))
        if is_ruin:
            edge = C["clue"] if clue else C["ruin_wall"]
            vx0, vy0, vx1, vy1 = bx + 5, by + 5, bx + bw_ - 6, by + bh_ - 6
            seg = 8
            xx = vx0
            while xx < vx1:
                d.line([(xx, vy0), (min(xx + seg, vx1), vy0)], fill=edge, width=2)
                d.line([(xx, vy1), (min(xx + seg, vx1), vy1)], fill=edge, width=2)
                xx += seg * 2
            yyy = vy0
            while yyy < vy1:
                d.line([(vx0, yyy), (vx0, min(yyy + seg, vy1))], fill=edge, width=2)
                d.line([(vx1, yyy), (vx1, min(yyy + seg, vy1))], fill=edge, width=2)
                yyy += seg * 2
            lab = rec["code"] + " " + rec["short"]
            bb = d.textbbox((bx + bw_ / 2, by + bh_ / 2), lab, font=font(11), anchor="mm")
            d.rectangle([bb[0] - 3, bb[1] - 2, bb[2] + 3, bb[3] + 2], fill="#2b2418")
            d.text((bx + bw_ / 2, by + bh_ / 2), lab, font=font(11),
                   fill=C["clue"] if clue else C["text"], anchor="mm")
            continue
        if rec.get("yard_building"):
            d.rectangle([bx, by, bx + bw_, by + bh_], outline=C["yard_edge"], width=3)
            d.text((bx + 5, by + 5), rec["code"], font=font(12, True),
                   fill=C["yard_furn"], anchor="la")
            d.text((bx + bw_ / 2, by + bh_ / 2), rec["short"], font=font(13),
                   fill=C["yard_furn"], anchor="mm")
            continue
        if rec.get("zone") == "yard":
            fill, edge = C["yard_furn"], C["yard_edge"]
        elif clue:
            fill, edge = C["clue"], "#ffc07a"
        else:
            fill, edge = C["furn"], C["furn_edge"]
        d.rectangle([bx + 2, by + 2, bx + bw_ - 3, by + bh_ - 3],
                    fill=fill, outline=edge, width=2)
        dark = "#3a1c08" if clue else "#3a2c1c"
        d.text((bx + bw_ / 2, by + bh_ / 2 - (7 if bh_ >= 2 * S else 0)),
               rec["code"], font=font(12, True), fill=dark, anchor="mm")
        if bh_ >= 2 * S and bw_ >= 2 * S:
            d.text((bx + bw_ / 2, by + bh_ / 2 + 10), rec["short"],
                   font=font(12), fill=dark, anchor="mm")

    # 房间名（画在家具之上，带深色底衬）
    if not is_ruin:
        lf = font(13, True)
        placed = []
        for room in hs["rooms"]:
            rx0, ry0, rx1, ry1, rname = room[0], room[1], room[2], room[3], room[4]
            force_top = len(room) > 6 and room[6] == "top"
            need_w = d.textlength(rname, font=lf) + 8
            place = None
            if not force_top:
                for ry in range(ry1, ry0 - 1, -1):
                    if need_w > (rx1 - rx0 + 1) * S:
                        continue
                    for rx in range(rx0, rx1 + 1):
                        if not (X0 <= rx <= X1 and Y0 <= ry <= Y1):
                            continue
                        if need_w > (rx1 - rx + 1) * S:
                            continue
                        if grid[ry - Y0][rx - X0] != "." or occupied(hs, rx, ry):
                            continue
                        if any(abs(rx - px) < 3 and ry == py for px, py in placed):
                            continue
                        dist = (rx - (rx0 + rx1) / 2.0) ** 2 + (ry - (ry0 + ry1) / 2.0) ** 2
                        if place is None or dist < place[0]:
                            place = (dist, rx, ry)
            if place:
                px_, py_ = place[1], place[2]
                cx = ox + (px_ + 0.5) * S
                cy = oy + (py_ + 0.5) * S
                placed.append((px_, py_))
            else:
                cx = ox + (rx0 + 1) * S + (rx1 - rx0) * S / 2.0
                cy = oy + ry0 * S - 3
            bb = d.textbbox((cx, cy), rname, font=lf, anchor="mm")
            d.rectangle([bb[0] - 4, bb[1] - 1, bb[2] + 4, bb[3] + 2], fill="#2b2418")
            d.text((cx, cy), rname, font=lf, fill="#f0e6cc", anchor="mm")

    # 主角（尺寸参照）
    px, py = auto_player_at(hs, grid)
    bx, by = ox + (px - X0) * S, oy + (py - Y0) * S
    d.rectangle([bx + 3, by - S + 3, bx + S - 4, by + S - 4],
                fill=C["player"], outline=C["player_edge"], width=2)
    d.ellipse([bx + S * 0.28, by - S * 0.86, bx + S * 0.72, by - S * 0.55],
              fill=C["player_edge"])
    lab = "主角 1×2 格 = 16×32 px"
    lw = tlen(d, lab, font(12))
    tx = min(bx + S + 8 + lw, ox + gw * S)
    d.text((tx, by - S - 6), lab, font=font(12), fill=C["key"], anchor="rs")

    # 尺寸线
    dy = oy + gh * S + 24
    d.line([(ox, dy), (ox + gw * S, dy)], fill=C["measure"], width=2)
    for xx in (ox, ox + gw * S):
        d.line([(xx, dy - 6), (xx, dy + 6)], fill=C["measure"], width=2)
    d.text((ox + gw * S / 2, dy + 10), "占地 %d 格 = %d px" % (gw, gw * TILE),
           font=font(14), fill=C["measure"], anchor="ma")

    # ---------- 外观层 ----------
    cw, ch = gw, gh + 1           # 画布：宽 = 占地宽，高 = 占地高 + 1 格（伪 3D 立面抬升）
    d.text((MARGIN, yB), "[B] 外观层 · 整栋单图（画布 = 占地宽 × (占地高 + 16)px，"
                         "多出的一格在顶部是墙与屋顶；锚点底部中心，四周留 2px 透明边）",
           font=font(17, True), fill=C["key"])
    if is_ruin:
        shell_rows = [
            ["B", "%s_base.png" % ffr, "%d×%d 格" % (cw, ch), "%d×%d px" % (cw * TILE, ch * TILE),
             "废墟态：残墙基 + 夯土地基 + 杂草底；墙已缺失处画成缺口，不画屋顶；"
             "顶部多出的一格是残墙立起的高度",
             "assets/village/houses/%s/" % fam],
        ]
        shell_note = _shell_note(is_ruin)
    else:
        shell_rows = [
            ["B", "%s_base.png" % ffr, "%d×%d 格" % (cw, ch), "%d×%d px" % (cw * TILE, ch * TILE),
             "地板 + 墙内侧 + 南立面 + 墙顶面 + 院子地面（不含屋顶）", "assets/village/houses/%s/" % fam],
            ["R", "%s_roof.png" % ffr, "%d×%d 格" % (cw, ch), "%d×%d px" % (cw * TILE, ch * TILE),
             "屋面 + 檐口；只有屋本体 %d×%d 格有像素，其余透明" % (bw, bh),
             "assets/village/houses/%s/" % fam],
        ]
        shell_note = _shell_note(is_ruin)
    sw = [50, 150, 96, 110, 0, 0]
    sw[4] = avail - 50 - 150 - 96 - 110 - 190
    sw[5] = 190
    draw_table(d, MARGIN, yB_tbl, avail,
               ["编号", "文件名", "画布格数", "画布像素", "本层画什么", "交付目录"],
               sw, shell_rows, row_h=30)
    for i, ln in enumerate(wrap_px(d, shell_note, font(13), avail - 12)):
        d.text((MARGIN + 6, yB_note + i * 19), ln, font=font(13), fill=C["dim"])

    # ---------- 家具层 ----------
    d.text((MARGIN, yC), "[C] 家具层 · 逐件一个文件（16px 网格，九档 1×1 … 3×3）",
           font=font(17, True), fill=C["key"])
    d.text((MARGIN + 6, yC + 26),
           "交付目录 assets/village/props/<文件 id>.png ｜ 全项目共享，同一 id 只画一次 ｜ "
           "文件名禁改（数据按文件名对号入座）｜ 源图可比占地多画一格高（朝向观众的立面）",
           font=font(13), fill=C["dim"])

    # ---------- 清单 ----------
    d.text((MARGIN, yD_title), "[D] 本栋家具清单（编号 = 上面格图里的编号）",
           font=font(17, True), fill=C["key"])
    rows_split = [rows_all[i:i + rows_per_col] for i in range(0, len(rows_all), rows_per_col)] \
        if rows_all else [[]]
    xoff = MARGIN
    for part in rows_split:
        colr = [[C["clue"] if c == "◆" else None for c in r] for r in part]
        draw_table(d, xoff, yD_tbl, sum(colw), hdr, colw, part, colors=colr)
        xoff += sum(colw) + (avail - 2 * sum(colw) if two_col else 0)

    # ---------- 页脚 ----------
    nclue = len([r for r in props_of_house if r.get("clue")])
    tyf = yfoot
    for ln in note_lines:
        d.text((MARGIN, tyf), ln, font=font(14), fill=C["gray"])
        tyf += 22
    d.text((MARGIN, tyf + 8),
           "本栋合计：外观 %d + 家具 %d 种（其中可检视线索 %d 种）= %d 个文件"
           % (n_shell, n_slot, nclue, n_shell + n_slot),
           font=font(15, True), fill=C["text"])
    return img


# ----------------------------------------------------------------- 场景对比图
def render_scene(frames, scene, hsize=None):
    hsize = hsize or {}
    SC = 0.30  # 世界 px → 图上 px
    pad = 28
    cols = 3
    cell_w = int(1600 * SC)
    cell_h = int(900 * SC)
    header_h = 150
    table_top = header_h + cell_h + 90
    rows = [[a["code"], a["id"], a["name"], a["frame"],
             "%d×%d" % (a["w"], a["h"]), "%d×%d" % (a["px"][0], a["px"][1]), a["note"]]
            for a in scene]
    colw = [44, 200, 180, 60, 78, 110, 720]
    H = table_top + 24 + len(rows) * ROW + 120
    img = Image.new("RGB", (W, H), C["bg"])
    d = ImageDraw.Draw(img)
    d.text((MARGIN, 26), "A1–A3 场景元素拆解图（三帧对比）", font=font(30, True), fill=C["text"])
    d.text((MARGIN, 74), "全部尺寸按 data/frames.json 实际几何换算 ｜ 1 格 = 16×16 px ｜ "
                         "世界 1600×900 px = 100×56.25 格",
           font=font(15), fill=C["key"])
    d.text((MARGIN, 100), "河 / 坝 / 路 / 田 / 老井 / 老槐 / 界碑 三帧同区位对比；"
                          "同形不同色的可共用底图 + tint，清单里已注明。",
           font=font(14), fill=C["gray"])
    d.line([(MARGIN, header_h - 14), (W - MARGIN, header_h - 14)], fill=C["head_line"], width=2)

    for i, fr in enumerate(("A1", "A2", "A3")):
        f = frames.get("a%s_%s" % (fr[1], FRAME_YEAR[fr]))
        x0 = MARGIN + i * (cell_w + pad)
        y0 = header_h
        d.rectangle([x0, y0, x0 + cell_w, y0 + cell_h], fill=f.get("ground", "#4a5a3a"),
                    outline=C["head_line"], width=2)
        if f:
            for s in f["shapes"]:
                t = s.get("type")
                col = s.get("color", "#888")
                if t == "polygon":
                    pts = [(x0 + p[0] * SC, y0 + p[1] * SC) for p in s["points"]]
                    d.polygon(pts, fill=col)
                elif t == "rect":
                    r = s["rect"]
                    d.rectangle([x0 + r[0] * SC, y0 + r[1] * SC,
                                 x0 + (r[0] + r[2]) * SC, y0 + (r[1] + r[3]) * SC], fill=col)
                elif t == "path":
                    pts = [(x0 + p[0] * SC, y0 + p[1] * SC) for p in s["points"]]
                    d.line(pts, fill=col, width=max(1, int(s.get("width", 32) * SC)),
                           joint="curve")
                elif t == "circle":
                    c = s["center"]
                    r = s.get("radius", 8) * SC
                    d.ellipse([x0 + c[0] * SC - r, y0 + c[1] * SC - r,
                               x0 + c[0] * SC + r, y0 + c[1] * SC + r], fill=col)
                elif t == "house":
                    hx0 = x0 + s["pos"][0] * SC
                    hy0 = y0 + s["pos"][1] * SC
                    lot = hsize.get(s["id"])
                    hw = (lot[0] if lot else 16) * TILE * SC
                    hh = (lot[1] if lot else 8) * TILE * SC
                    d.rectangle([hx0, hy0, hx0 + hw, hy0 + hh],
                                outline=C["key"], width=2)
                    d.text((hx0 + 3, hy0 + 2), s["id"], font=font(10), fill=C["key"])
        d.text((x0, y0 - 22), "%s · %s" % (fr, FRAME_YEAR[fr]), font=font(16, True), fill=C["text"])

    ty = table_top
    d.text((MARGIN, ty - 30), "[E] 场景元素清单", font=font(17, True), fill=C["key"])
    draw_table(d, MARGIN, ty, sum(colw),
               ["编号", "文件 id（禁改）", "资产名", "帧", "格数", "像素", "说明 / 交付要求"],
               colw, rows)
    fy = ty + 24 + len(rows) * ROW + 16
    d.text((MARGIN, fy),
           "合计 %d 项。河 / 路 / 田三帧同形不同色 → 可共用一套底图靠 tint 换年代；"
           "老井 4 态、老槐 4 态（苗/中/大/桩）是跨帧变化最大的两件，优先级最高。"
           % len(rows), font=font(14), fill=C["gray"])
    return img


# ----------------------------------------------------------------- 主流程
def main():
    houses = load_houses()
    frames, _ = load_frames()
    props, shells, by_id = build_registry(houses)
    scene = scene_assets(frames)

    os.makedirs(OUT, exist_ok=True)
    for dname in FRAME_DIR.values():
        os.makedirs(os.path.join(OUT, dname), exist_ok=True)

    # 每栋的家具（带全局编号 / 全局复用次数）
    for fr, hid in ORDER:
        hs = houses[hid]
        plist = []
        for f in hs["furniture"]:
            x, y, w, h = f["rect"]
            rid = furn_slug(f["name"], w, h)
            rec = dict(by_id[rid])
            rec["rect"] = (x, y, w, h)
            rec["file_id"] = rid
            rec["clue"] = bool(f.get("clue"))
            rec["zone"] = f.get("zone", "house")
            rec["yard_building"] = bool(f.get("yard_building"))
            rec["global_uses"] = by_id[rid]["uses"]
            rec["shared"] = by_id[rid]["uses"] > 1
            rec["note"] = (f.get("note") or "").strip()
            rec["short"] = f.get("short") or f["name"]
            plist.append(rec)
        plist.sort(key=lambda r: (r["zone"] != "house", r["rect"][1], r["rect"][0]))
        img = render_house(hs, by_id, plist)
        p = os.path.join(OUT, FRAME_DIR[fr], "%s_assets.png" % hid)
        img.save(p)
        print("saved", p, img.size)

    hsize = {}
    for hid, hs in houses.items():
        X0, Y0, X1, Y1 = hs["lot"]
        hsize[hid] = (X1 - X0 + 1, Y1 - Y0 + 1)
    img = render_scene(frames, scene, hsize)
    p = os.path.join(OUT, "_scene_a1a3_assets.png")
    img.save(p)
    print("saved", p, img.size)

    # ---- 总需求清单 ----
    # 外观行的「格宽/格高/像素」= **画布**（= 占地面 + 顶部一格），因为美术照着画的是画布；
    # 占地尺寸写进「说明」列开头，需要时还能对回去。家具/场景行含义不变（= 占地）。
    csv_path = os.path.join(OUT, "_a1a3_assets.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["编号", "类别", "文件 id", "资产名", "格宽", "格高",
                    "像素宽", "像素高", "交付路径", "出现在", "实例数", "线索", "说明"])
        for rec in shells:
            w.writerow([rec["code"], "外观·%s" % rec["layer"], rec["id"],
                        "%s 的 %s" % (rec["house"], rec["layer"]),
                        rec["cw"], rec["ch"], rec["cpx"][0], rec["cpx"][1],
                        rec["path"], rec["house"], 1,
                        "◆" if rec["clue_houses"] else "",
                        "画布 = %d×%d px（占地 %d×%d 格 + 顶部一行立面）；%s"
                        % (rec["cpx"][0], rec["cpx"][1], rec["w"], rec["h"], rec["desc"])])
        for rec in props:
            w.writerow([rec["code"], "家具·%s" % ("院子" if rec["zone"] == "yard" else "室内"),
                        rec["id"], rec["name"], rec["w"], rec["h"],
                        rec["px"][0], rec["px"][1], rec["path"],
                        "/".join(rec["houses"]), rec["uses"],
                        "◆" if rec["clue_houses"] else "",
                        " | ".join(rec["notes"][:2])])
        for a in scene:
            w.writerow([a["code"], "场景", a["id"], a["name"], a["w"], a["h"],
                        a["px"][0], a["px"][1], a["path"], a["frame"], 1, "", a["note"]])
    print("saved", csv_path)

    json_path = os.path.join(OUT, "_a1a3_assets.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump({"shell": shells, "props": props, "scene": scene},
                  fh, ensure_ascii=False, indent=1)
    print("saved", json_path)

    print("TOTAL shell=%d props=%d scene=%d  => files=%d"
          % (len(shells), len(props), len(scene), len(shells) + len(props) + len(scene)))


if __name__ == "__main__":
    main()
