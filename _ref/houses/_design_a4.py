# -*- coding: utf-8 -*-
"""A4 2001 世界布局 · 设计稿坐标与校验（不落地 frames.json）。

【坐标基准】docs/BUILD-A1.md §2.2「五帧统一版，2026-11-20 定案，唯一权威版本」：
    河 (0,0,1600,112) | 坝 (196,34,120,62)
    田·东 (1000,130,240,176) | 田·西 (1272,130,240,176)
    老井 圆心 (900,545) r16 | 老槐 圆心 (852,505) | 界碑 (696,594,8,16)
    起点 (700,560)

【⚠️ 历史分裂，落地前必须处理】
    data/frames.json 里 A1–A3 实际落地的坐标是早期 _design_v5 方案：
        井 (680,424) / 槐 (648,488) / 碑 (928,480) / 主路弯 y600 / A3 已拉平
    与 BUILD-A1.md §2.2 不一致。两套坐标不能同时存在于同一条时间轴，
    否则切帧时地标会「漂」。本稿按 §2.2 权威坐标设计；解禁 frames.json
    落地时，须先把 A1–A3 对齐到同一基准。本轮不碰 frames.json。

【A4 的三处改动（用户 2026-11-21 拍板）】
    1. 主路取直：[[0,560],[1600,560]] —— 绕井弯 (900,624) 拉平到 y560，
       井心 (900,545) 落在路面带 (542..578) 正下方 → 接 A5「井在车道下」。
    2. 井埋地下：A3 的「老井·水泥」circle 在 A4 不再出现，地面只留
       圆形沥青补丁（story §7.2 头号物证）。
    3. 农田全荒：田块位置不动，颜色改枯黄 + 荒草点（story §2:49）。
"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
W, H, TILE = 1600, 900, 16
ROAD_W = 36
ROAD_HALF = ROAD_W // 2

# ---- 权威地标（BUILD-A1.md §2.2）----
RIVER = (0, 0, 1600, 112)
DAM = (196, 34, 120, 62)
FIELD_E = (1000, 130, 240, 176)
FIELD_W = (1272, 130, 240, 176)
WELL = (900, 545, 16)          # 圆心 + 半径
TREE = (852, 505)              # 树干位置；树冠朝远离井的方向偏
STELE = (696, 594, 8, 16)
START = (700, 560)

ROAD_MAIN = [(0, 560), (1600, 560)]       # A4 取直（A1–A3 是绕井弯）
ROAD_BRANCH = [(640, 300), (640, 560)]    # 支路沿用，通超市/原磨坊方向

# ---- A4 四栋房子世界坐标（原点固定、南沿对齐路面北侧）----
# shen_a4 四合院 21×19格=336×304，南沿 520（沿用沈家「向北长」原则）
# market  在建超市 21×14格=336×224，南沿 530（粮站拆后原址重建）
# zhou_a4 周家老屋 12×6格=192×96，路南原址（A1–A3 周家一直在）
# zheng_a4 郑家小楼 20×10格=320×160，陆家地块原址（A3 废墟→A4 新房）
PLACE = {
    "shen_a4":  (160, 216),
    "market":   (776, 306),
    "zhou_a4":  (630, 620),
    "zheng_a4": (1120, 340),
}
A4_IDS = list(PLACE)

# 桩基绕开区：井 + 老槐那一片（story §4.4 改地质报告「不宜大开挖」）
# market 屋体矩形盖住这一带，但这一小块不施工 —— 校验时豁免，图上单独标注。
RESERVE = (820, 470, 120, 80)   # x820..940, y470..550，包住井(900,545)与槐(852,505)

data = json.load(open(os.path.join(HERE, "houses_data.json"), encoding="utf-8"))
by_id = {h["id"]: h for h in data}


def size_of(hid):
    lot = by_id[hid]["lot"]
    return ((lot[2] - lot[0] + 1) * TILE, (lot[3] - lot[1] + 1) * TILE)


def lot_rect(hid):
    x, y = PLACE[hid]
    w, h = size_of(hid)
    return (x, y, w, h)


def overlap(a, b):
    return (a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and
            a[1] < b[1] + b[3] and b[1] < a[1] + a[3])


def road_boxes():
    """主路/支路按线段走向生成细带，不用包围盒（斜段会误判）。"""
    out = []
    for road in (ROAD_MAIN, ROAD_BRANCH):
        for (x1, y1), (x2, y2) in zip(road, road[1:]):
            if x1 == x2:
                out.append((x1 - ROAD_HALF, min(y1, y2), ROAD_W, abs(y2 - y1)))
            else:
                out.append((min(x1, x2), y1 - ROAD_HALF, abs(x2 - x1), ROAD_W))
    return out


def check():
    problems = []
    print("A4 2001 世界布局 · 设计稿校验")
    print("=" * 78)

    rbs = road_boxes()
    rects = []
    for hid in A4_IDS:
        r = lot_rect(hid)
        rects.append((hid, r))
        notes = []
        if r[0] < 0 or r[1] < 0 or r[0] + r[2] > W or r[1] + r[3] > H:
            notes.append("OUT")
        if overlap(r, RIVER):
            notes.append("压河")
        if overlap(r, DAM):
            notes.append("压坝")
        if overlap(r, STELE):
            notes.append("压界碑")
        for rb in rbs:
            if overlap(r, rb):
                notes.append("压路")
                break
        for field in (FIELD_E, FIELD_W):
            if overlap(r, field):
                notes.append("压田")
        print("  %-10s x=%4d y=%4d %3dx%-3d 南沿=%3d%s" % (
            hid, r[0], r[1], r[2], r[3], r[1] + r[3],
            ("   [X] " + ",".join(sorted(set(notes)))) if notes else ""))
        if notes:
            problems.append("%s: %s" % (hid, ",".join(sorted(set(notes)))))

    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            if overlap(rects[i][1], rects[j][1]):
                problems.append("%s x %s 重叠" % (rects[i][0], rects[j][0]))
                print("    [X] %s x %s 重叠" % (rects[i][0], rects[j][0]))

    # 取直压井：井心必须落在主路带内（A5「井在车道下」的物证起点）
    wx, wy, wr = WELL
    road_band_y = (ROAD_MAIN[0][1] - ROAD_HALF, ROAD_MAIN[0][1] + ROAD_HALF)
    in_road = road_band_y[0] <= wy <= road_band_y[1]
    print("\n  取直达井：井心 (%d,%d) 路带 y%d..%d → %s" % (
        wx, wy, road_band_y[0], road_band_y[1], "压中" if in_road else "[X] 未压中"))
    if not in_road:
        problems.append("取直段没压过老井")

    # 起点可站：不在任何房子/河/碑里
    sx, sy = START
    if any(overlap((sx - 4, sy - 4, 8, 8), (r[0], r[1], r[2], r[3])) for _, r in rects):
        problems.append("起点压房子")
    if overlap((sx - 4, sy - 4, 8, 8), RIVER) or overlap((sx - 4, sy - 4, 8, 8), STELE):
        problems.append("起点压地标")

    print("\n" + "=" * 78)
    if problems:
        print("有问题：")
        for p in problems:
            print("  !", p)
        return False
    print("A4 LAYOUT OK - 四栋不重叠、不压路/河/田/碑，取直段压中老井，起点可站。")
    print("  注：market 屋体覆盖「桩基绕开区」(820,470,120,80) 是设计意图，非错误。")
    return True


if __name__ == "__main__":
    ok = check()
    sys.exit(0 if ok else 1)
