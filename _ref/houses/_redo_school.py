"""A5 2026 小学（沈明远捐建 · 村小）：整栋精调重写 · v4（跑道像素格 + 上下对调）。

v4 口径（用户 2026-11-22 四改）：
  1. 「椭圆形的操场只是打个比方，实际应该是两个半圆中间是矩形」
     → 跑道改成**体育场形**：左右两段半圆 + 中间一段直道。
  2. 「你需要用像素格的方式制作，不能是调用函数完成」
     → 跑道**逐格判定、逐格入数据**（每格一条 1×1 家具，seamless=True），
       出图器只负责把每格铺满（无内缩、无描边、无标签），**不调任何形状绘制函数**。
  3. 「上下两半需要调换绘制（上半：办公室、门厅、教师宿舍；下半：教室一、走廊、教室二）」
     → **教室排提到上面**（北排），办公室 + 门厅落到下面（南排），紧贴操场。
  4. 「操场正对应该是门厅而不是走廊」
     → 大门开在**南侧围墙**，进门即到操场；操场正北对着门厅，
       门厅↔操场的门开在操场中轴上；走廊不再正对操场。
  5. 「教室宿舍没有必要」→ **教师宿舍整间删掉**（用户已确认）。
  6. 「单杠、球门也删掉」→ 操场只剩：升旗台+旗杆、主席台+剪彩台+红绸+花篮、
     像素格跑道、南墙标语牌。

结构（三排 + 操场，整块围墙内，38×30 格）：
  北排 y=1..8   ：教室一 x1..15 │ 走廊 x17..19 │ 教室二 x21..36（竖墙 x16 / x20）
  墙 y=9        ：教室排 | 办公室门厅排（门 (18,9) 走廊↔门厅）
  南排 y=10..17 ：办公室 x1..11 │ 门厅 x13..36（竖墙 x12，门 (12,14)）
  墙 y=18       ：教学楼 | 操场（门 (18,18) 门厅↔操场，正对操场中轴；「周」界碑嵌在西端）
  操场 y=19..28 ：升旗台(西北) / 主席台+剪彩(北侧偏东) / 像素格跑道(中) / 南墙标语
  墙 y=29       ：南围墙，大门 (18,29)(19,29) → 进门就是操场，正对门厅

证物链：
  - 「周」界碑 → 操场北围墙（教学楼南墙）西端 **[1,18,2,1]**（相对落点不变，随墙体整体下移一格）。
  - 剪彩 → 操场主席台（沈明远捐建；他什么都不知道）。

幂等：存在则替换，否则追加。
预览：MCS_PREVIEW=1 只出预览图到 lab/，不写 houses_data.json。
"""
import json
import math
import os
from gen_all_houses import build_grid, render

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")
PREVIEW = os.environ.get("MCS_PREVIEW") == "1"


def F(name, x, y, w, h, note="", clue=False, short=None, zone="house",
      yard_building=False, wall_mounted=False, seamless=False, color=None):
    d = dict(name=name, short=short or name, rect=[x, y, w, h], note=note,
             clue=clue, zone=zone, yard_building=yard_building,
             wall_mounted=wall_mounted)
    if seamless:
        d["seamless"] = True
    if color:
        d["color"] = color
    return d


# ── 跑道：体育场形（两段半圆 + 中间直段），逐格判定、逐格入数据 ──
# 不用任何形状绘制函数：这里只用纯数学算出「哪些格属于跑道」。
TRACK_X0, TRACK_X1 = 6, 29        # 跑道包围盒（列）
TRACK_Y0, TRACK_Y1 = 21, 26       # 跑道包围盒（行）
CAP_R = 3                          # 半圆半径（格）
CAP_LX, CAP_RX = 9, 26            # 左/右半圆圆心的列
TRACK_CY = (TRACK_Y0 + TRACK_Y1) / 2.0   # = 23.5，纵向中线在两行之间
R_IN, R_OUT = 2.5, 3.5             # 跑道环的内/外半径（格）

# 场地配色（数据层给色，出图器按色填；游戏端 house_shape.gd 同样认这两个 key）
FIELD_COLOR = "#6f7d4c"           # 操场草地（整块铺满）
TRACK_COLOR = "#b08050"           # 跑道红土


def track_cells():
    """返回跑道占用的格子集合 {(x, y)}：中段是两条直道，两端是半圆环。"""
    cells = set()
    for x in range(TRACK_X0, TRACK_X1 + 1):
        for y in range(TRACK_Y0, TRACK_Y1 + 1):
            if x < CAP_LX:
                s = math.hypot(x - CAP_LX, y - TRACK_CY)
            elif x > CAP_RX:
                s = math.hypot(x - CAP_RX, y - TRACK_CY)
            else:
                s = abs(y - TRACK_CY)
            if R_IN <= s <= R_OUT:
                cells.add((x, y))
    return cells


TRACK = track_cells()
TRACK_FURN = [
    F("跑道", x, y, 1, 1, "像素格逐格拼出的体育场形跑道（两段半圆＋中间直段）",
      zone="yard", seamless=True, color=TRACK_COLOR)
    for (x, y) in sorted(TRACK, key=lambda c: (c[1], c[0]))
]

school = {
    "id": "school",
    "name": "小学 · A5 2026 · 沈明远捐建（村小）",
    # 38×30 格（608×480 px @16px/格）
    "lot": [0, 0, 37, 29],
    "wings": [[0, 0, 38, 30]],
    # 隔墙：
    #   y=8 整条横墙？——不，教室排在北（y=1..8），故北排与南排之间的横墙是 y=9
    #   y=17 整条横墙？——不，南排 y=10..17，操场北墙是 y=18
    #   x=16 / x=20 北排两条竖墙（教室一 / 走廊 / 教室二）
    #   x=12 南排竖墙（教室三 / 门厅）
    #   x=24 南排竖墙（门厅 / 教室四）
    "partitions": [
        [1, 9, 36, 9],
        [1, 18, 36, 18],
        [16, 1, 16, 8],
        [20, 1, 20, 8],
        [12, 10, 12, 17],
        [24, 10, 24, 17],
    ],
    # 房门：(16,4) 走廊↔教室一 | (20,4) 走廊↔教室二 | (18,9) 走廊↔门厅
    #       (12,14) 教室三↔门厅 | (24,13) 门厅↔教室四
    #       (18,18) 门厅↔操场（正对操场中轴）
    "doors": [[16, 4], [20, 4], [18, 9], [12, 14], [24, 13], [18, 18]],
    # 大门：南围墙 (18,29)(19,29)，进门即是操场，操场正对门厅
    "gate": [[18, 29], [19, 29]],
    "rooms": [
        [1, 1, 15, 8, "教室一", "class"],
        [17, 1, 19, 8, "走廊", "hall"],
        [21, 1, 36, 8, "教室二", "class"],
        [1, 10, 11, 17, "教室三", "class"],
        [13, 10, 23, 17, "门厅", "hall"],
        [25, 10, 36, 17, "教室四", "class"],
        [1, 19, 36, 28, "操场", "field"],
    ],
    "furniture": [
        # ── 教室一 x1..15,y1..8（讲台正对黑板，课桌横竖都留一格空当）──
        F("黑板", 6, 0, 4, 1, "钉在教室北墙", wall_mounted=True),
        F("讲台", 6, 1, 4, 1, "讲台正对黑板"),
        F("教鞭盒", 11, 1, 1, 1, "讲台上的教鞭盒"),
        F("课程表", 1, 0, 2, 1, "钉在教室北墙的课程表", wall_mounted=True),
        F("图书角", 15, 1, 1, 2, "教室东墙的书架"),
        F("书包架", 15, 3, 1, 1, "挂书包的地方"),
        F("课桌", 1, 3, 2, 1, "教室一"),
        F("课桌", 4, 3, 2, 1, "教室一"),
        F("课桌", 7, 3, 2, 1, "教室一"),
        F("课桌", 10, 3, 2, 1, "教室一"),
        F("课桌", 13, 3, 2, 1, "教室一"),
        F("课桌", 1, 5, 2, 1, "教室一"),
        F("课桌", 4, 5, 2, 1, "教室一"),
        F("课桌", 7, 5, 2, 1, "教室一"),
        F("课桌", 10, 5, 2, 1, "教室一"),
        F("课桌", 13, 5, 2, 1, "教室一"),
        F("课桌", 1, 7, 2, 1, "教室一"),
        F("课桌", 4, 7, 2, 1, "教室一"),
        F("课桌", 7, 7, 2, 1, "教室一"),
        F("课桌", 10, 7, 2, 1, "教室一"),
        F("课桌", 13, 7, 2, 1, "教室一"),
        F("讲义筐", 15, 7, 1, 1, "讲义筐"),
        # ── 走廊 x17..19,y1..8 ──
        F("荣誉榜", 16, 1, 1, 3, "钉在走廊西墙", wall_mounted=True),
        F("宣传栏", 20, 1, 1, 3, "钉在走廊东墙 · 贴通知", wall_mounted=True),
        F("扫把", 17, 1, 1, 1, "走廊靠墙"),
        F("拖把", 19, 8, 1, 1, "走廊东南角"),
        # ── 教室二 x21..36,y1..8 ──
        F("黑板", 27, 0, 4, 1, "钉在教室北墙", wall_mounted=True),
        F("讲台", 27, 1, 4, 1, "讲台正对黑板"),
        F("教鞭盒", 32, 1, 1, 1, "讲台上的教鞭盒"),
        F("课程表", 22, 0, 2, 1, "钉在教室北墙的课程表", wall_mounted=True),
        F("书包架", 21, 1, 1, 2, "挂书包的地方"),
        F("图书角", 35, 1, 2, 2, "教室东墙的书架"),
        F("课桌", 21, 3, 2, 1, "教室二"),
        F("课桌", 24, 3, 2, 1, "教室二"),
        F("课桌", 27, 3, 2, 1, "教室二"),
        F("课桌", 30, 3, 2, 1, "教室二"),
        F("课桌", 33, 3, 2, 1, "教室二"),
        F("课桌", 21, 5, 2, 1, "教室二"),
        F("课桌", 24, 5, 2, 1, "教室二"),
        F("课桌", 27, 5, 2, 1, "教室二"),
        F("课桌", 30, 5, 2, 1, "教室二"),
        F("课桌", 33, 5, 2, 1, "教室二"),
        F("课桌", 21, 7, 2, 1, "教室二"),
        F("课桌", 24, 7, 2, 1, "教室二"),
        F("课桌", 27, 7, 2, 1, "教室二"),
        F("课桌", 30, 7, 2, 1, "教室二"),
        F("课桌", 33, 7, 2, 1, "教室二"),
        F("讲义筐", 35, 7, 1, 1, "讲义筐"),
        # ── 教室三 x1..11,y10..17（南排西侧；原办公室改成教室）──
        F("黑板", 3, 9, 4, 1, "钉在教室三北墙", wall_mounted=True),
        F("课程表", 1, 9, 2, 1, "钉在教室三北墙的课程表", wall_mounted=True),
        F("讲台", 3, 10, 4, 1, "讲台正对黑板"),
        F("教鞭盒", 8, 10, 1, 1, "讲台上的教鞭盒"),
        F("书包架", 11, 10, 1, 2, "挂书包的地方"),
        F("图书角", 10, 12, 1, 2, "教室东墙的书架"),
        F("课桌", 1, 12, 2, 1, "教室三"),
        F("课桌", 4, 12, 2, 1, "教室三"),
        F("课桌", 7, 12, 2, 1, "教室三"),
        F("课桌", 1, 14, 2, 1, "教室三"),
        F("课桌", 4, 14, 2, 1, "教室三"),
        F("课桌", 7, 14, 2, 1, "教室三"),
        F("课桌", 1, 16, 2, 1, "教室三"),
        F("课桌", 4, 16, 2, 1, "教室三"),
        F("课桌", 7, 16, 2, 1, "教室三"),
        F("讲义筐", 10, 16, 1, 1, "讲义筐"),
        # ── 门厅 x13..23,y10..17（正对操场；剪彩在操场，这里只办签到和候场）──
        F("签到处", 14, 10, 2, 1, "来宾签到的小桌"),
        F("伞架", 13, 10, 1, 1, "门边的伞架"),
        F("捐款箱", 16, 10, 1, 1, "村民捐建的心意箱"),
        F("饮水机", 22, 10, 1, 1, "门厅角落"),
        F("指示牌", 22, 16, 1, 1, "立着的指路牌 · 操场往南"),
        F("荣誉榜", 12, 11, 1, 3, "钉在门厅西墙", wall_mounted=True),
        F("旧挂钟", 12, 10, 1, 1, "钉在门厅西墙", wall_mounted=True),
        F("公告板", 12, 15, 1, 2, "钉在门厅西墙", wall_mounted=True),
        F("宣传栏", 22, 9, 3, 1, "钉在门厅与走廊之间的墙上 · 贴通知", wall_mounted=True),
        F("捐建牌匾", 14, 18, 4, 1, "「沈氏捐建」牌匾钉在门厅外墙 · 他什么都不知道",
          wall_mounted=True),
        F("长凳", 14, 13, 3, 1, "家长候场席"),
        F("长凳", 18, 13, 3, 1, "家长候场席"),
        F("长凳", 14, 16, 3, 1, "家长候场席"),
        F("长凳", 18, 16, 3, 1, "家长候场席"),
        # ── 教室四 x25..36,y10..17（南排东侧；原会议室改成教室）──
        F("黑板", 29, 9, 4, 1, "钉在教室四北墙", wall_mounted=True),
        F("课程表", 25, 9, 2, 1, "钉在教室四北墙的课程表", wall_mounted=True),
        F("讲台", 29, 10, 4, 1, "讲台正对黑板"),
        F("教鞭盒", 34, 10, 1, 1, "讲台上的教鞭盒"),
        F("书包架", 25, 10, 1, 2, "挂书包的地方"),
        F("图书角", 35, 12, 1, 2, "教室东墙的书架"),
        F("课桌", 26, 12, 2, 1, "教室四"),
        F("课桌", 29, 12, 2, 1, "教室四"),
        F("课桌", 32, 12, 2, 1, "教室四"),
        F("课桌", 26, 14, 2, 1, "教室四"),
        F("课桌", 29, 14, 2, 1, "教室四"),
        F("课桌", 32, 14, 2, 1, "教室四"),
        F("课桌", 26, 16, 2, 1, "教室四"),
        F("课桌", 29, 16, 2, 1, "教室四"),
        F("课桌", 32, 16, 2, 1, "教室四"),
        F("讲义筐", 35, 16, 1, 1, "讲义筐"),
        # ── 操场 x1..36,y19..28（剪彩在这里；设施只留年代上真有的那几样）──
        F("「周」界碑", 1, 18, 2, 1, "嵌在操场北围墙（教学楼南墙）西端 · 字磨掉一半",
          clue=True, short="界碑", wall_mounted=True),
        # 升旗台 + 旗杆：放在跑道西北边的边上
        F("升旗台", 3, 19, 2, 2, "跑道西北边 · 每周一升旗"),
        F("旗杆", 5, 19, 1, 1, "升旗台边上的旗杆（美术画成竖杆）"),
        # 主席台 + 剪彩：贴着跑道北侧（教学楼南墙下），红绸钉在背后的墙上
        F("主席台", 21, 19, 8, 2, "跑道北侧边上的高台 · 沈明远在这儿剪彩"),
        F("剪彩台", 29, 19, 2, 1, "剪彩用的条桌，紧挨主席台东端"),
        F("红绸横幅", 21, 18, 8, 1, "红绸挂在主席台背后的墙上 · 题「沈氏捐建 村小落成」",
          wall_mounted=True),
        F("花篮", 20, 19, 1, 1, "剪彩摆的花篮"),
        F("花篮", 31, 20, 1, 1, "剪彩摆的花篮"),
        # 像素格跑道：体育场形（两段半圆 + 中间直段），每格一条数据
        *TRACK_FURN,
        F("标语牌", 12, 29, 6, 1, "「好好学习 天天向上」钉在操场南围墙", wall_mounted=True),
    ],
    "clue": [
        "操场北围墙里嵌着半块旧界碑，只认得出一个「周」字（身份反转佐证）。",
        "操场主席台上的剪彩台与红绸：2026 沈明远捐建 · 他什么都不知道。",
    ],
    "story": "沈明远剪彩的地方（操场主席台）；他什么都不知道。",
    "note": ("屋本体 38×30 格 = 608×480 px（lot/wings 一致；旧 note 的「21×12」「21×16」「42×32」均作废）。"
             "v5：办公室与会议室**全部改成教室**——南排现在是 教室三(x1..11)/门厅(x13..23)/教室四(x25..36)，"
             "四间教室都配黑板+讲台+课桌（2×1，横竖都留 1 格空当），全校再无办公室与会议室。"
             "操场**整块上色**（room 色键 field=草地 #6f7d4c，整块铺满，不是只描边），"
             "跑道用 seamless 像素格逐格拼成体育场形并单独指定红土色 #b08050。"
             "大门开在南围墙 (18,29)(19,29)，进门即到操场；操场正北对着门厅，"
             "门厅↔操场的门开在 (18,18)（操场中轴），走廊不再正对操场。"
             "操场不堆长椅沙坑花坛粉笔筐乒乓球台爬杆旧车胎水缸篮球架，单杠球门也删了，"
             "只剩升旗台+旗杆、主席台+剪彩台+红绸+花篮、跑道、南墙标语牌。"
             "「周」界碑 [1,18,2,1]（操场北围墙最西端）。"),
}

# ── 自检 1：家具不重叠（院子建筑内嵌家具豁免）──
yard_buildings = [f for f in school["furniture"] if f.get("yard_building")]


def nested_in_building(x, y, w, h):
    for yb in yard_buildings:
        bx, by, bw, bh = yb["rect"]
        if bx <= x and x + w <= bx + bw and by <= y and y + h <= by + bh:
            return True
    return False


occupied = set()
for f in school["furniture"]:
    x, y, w, h = f["rect"]
    for i in range(x, x + w):
        for j in range(y, y + h):
            if nested_in_building(x, y, w, h):
                continue
            assert (i, j) not in occupied, f"家具重叠 ({i},{j}) · {f['name']}"
            occupied.add((i, j))

# ── 自检 2：家具不压墙/门/院门（钉在墙上的黑板/横幅/界碑除外）──
grid = build_grid(school)
for f in school["furniture"]:
    if f.get("wall_mounted"):
        continue
    x, y, w, h = f["rect"]
    for i in range(x, x + w):
        for j in range(y, y + h):
            assert grid[j][i] in (".", " "), f"家具压墙/门：{f['name']} ({i},{j}) = {grid[j][i]}"

# ── 自检 3：门/大门两侧（临地格的邻格）必须空出来，走得进去 ──
for d in [tuple(d) for d in school["doors"]] + [tuple(g) for g in school["gate"]]:
    x, y = d
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if not (0 <= nx < len(grid[0]) and 0 <= ny < len(grid)):
            continue
        if grid[ny][nx] not in (".", " "):   # 墙格上的钉墙物不挡路，豁免
            continue
        assert (nx, ny) not in occupied, \
            f"堵门：家具占门 {d} 的邻格 ({nx},{ny})"

# ── 自检 4：课桌之间必须留 1 格空当（用户 11/22 硬要求），横向纵向都不许贴死 ──
desks = [f for f in school["furniture"] if f["name"] == "课桌"]


def gap(a0, a1, b0, b1):
    """两个闭区间之间隔着的空格子数；重叠返回 -1。"""
    if a1 < b0:
        return b0 - a1 - 1
    if b1 < a0:
        return a0 - b1 - 1
    return -1


for i, a in enumerate(desks):
    ax, ay, aw, ah = a["rect"]
    for b in desks[i + 1:]:
        bx, by, bw, bh = b["rect"]
        gx = gap(ax, ax + aw - 1, bx, bx + bw - 1)
        gy = gap(ay, ay + ah - 1, by, by + bh - 1)
        if gx < 0:            # 列区间重叠 → 前后排，纵向必须留空
            assert gy >= 1, f"课桌前后贴死没空当：{a['rect']} 与 {b['rect']}"
        if gy < 0:            # 行区间重叠 → 并排，横向必须留空
            assert gx >= 1, f"课桌并排贴死没空当：{a['rect']} 与 {b['rect']}"

# ── 自检 5：室内每个地板格都有房间归属（不露默认棕）──
room_cells = {(i, j) for (x0, y0, x1, y1, *_rest) in school["rooms"]
              for j in range(y0, y1 + 1) for i in range(x0, x1 + 1)}
floor_cells = {(i, j) for j, row in enumerate(grid) for i, ch in enumerate(row) if ch == "."}
for c in sorted(floor_cells - room_cells):
    raise AssertionError(f"室内无主格（露默认色）: {c}")

# ── 自检 6：年代红线（用户点名不许有的东西，一个都不许出现）──
forbidden = ("茅坑", "旱厕", "茅房", "教师宿舍", "宿舍")
for f in school["furniture"]:
    assert not any(k in f["name"] for k in forbidden), f"年代/口径不对：不该有「{f['name']}」"
for r in school["rooms"]:
    assert not any(k in r[4] for k in forbidden), f"不该有这个房间：「{r[4]}」"

banned = ("长椅", "沙坑", "花坛", "粉笔框", "粉笔筐", "乒乓球台",
          "爬杆", "旧车胎", "水缸", "篮球架", "单杠", "球门")
for f in school["furniture"]:
    if f.get("zone") != "yard":
        continue
    assert not any(k in f["name"] for k in banned), f"操场上不该有「{f['name']}」"

# ── 自检 7：跑道必须是「像素格拼出的体育场形」，不许用形状绘制函数糊弄 ──
track_furn = [f for f in school["furniture"] if f["name"] == "跑道"]
assert track_furn, "没有跑道"
for f in track_furn:
    x, y, w, h = f["rect"]
    assert w == 1 and h == 1, f"跑道必须是 1×1 像素格，found {w}×{h}"
    assert f.get("seamless"), "跑道格必须标 seamless（无内缩无描边）"
cells = {(f["rect"][0], f["rect"][1]) for f in track_furn}
assert cells == TRACK, "跑道格集合与逐格判定结果不一致"
# 7a. 左右对称（体育场形的必要条件）
for (x, y) in cells:
    assert (TRACK_X0 + TRACK_X1 - x, y) in cells, f"跑道左右不对称：({x},{y})"
# 7b. 中间必须是空的（跑道是环，不是实心块）：中间直段的内场不许有跑道格
inner = {(x, y) for x in range(CAP_LX + 1, CAP_RX) for y in range(TRACK_Y0 + 1, TRACK_Y1)}
assert not (inner & cells), "跑道中间被填实了（应该是环，不是实心）"
# 7c. 上下两条直道必须连续（中间直段）
for ry in (TRACK_Y0, TRACK_Y1):
    run = [x for x in range(CAP_LX, CAP_RX + 1) if (x, ry) in cells]
    assert len(run) == CAP_RX - CAP_LX + 1, f"跑道上/下直道不连续（行 {ry}）"
# 7d. 两端必须有半圆（最外侧两列都得有格子）
for ex in (TRACK_X0, TRACK_X1):
    assert any((ex, y) in cells for y in range(TRACK_Y0, TRACK_Y1 + 1)), \
        f"跑道端头缺半圆（列 {ex}）"

# ── 自检 8：操场必须正对门厅（不许正对走廊）──
rooms = {r[4]: r for r in school["rooms"]}
hall = rooms["门厅"]
yard = rooms["操场"]
yard_cx = (yard[0] + yard[2]) / 2.0
assert hall[0] <= yard_cx <= hall[2], \
    f"操场中轴 {yard_cx} 不在门厅范围内（{hall[0]}..{hall[2]}）"
# 门厅↔操场的门必须存在，且落在门厅与操场之间的墙上
yx = [d for d in school["doors"] if d[1] == hall[3] + 1]
assert yx, "门厅与操场之间没有门"
assert any(abs(d[0] - yard_cx) <= 1 for d in yx), \
    f"门厅↔操场的门不在操场中轴上：{yx}"
# 操场北墙外、轴线上的那一格属于哪个房间？必须是门厅，不许是走廊
axis_x = int(round(yard_cx))
axis_y = yard[1] - 2          # 墙外一格再往里一格 = 紧贴操场北墙的室内格
assert axis_y >= hall[1] and axis_y <= hall[3], "操场正对的室内格不在门厅行范围内"
owner = None
for r in school["rooms"]:
    if r[0] <= axis_x <= r[2] and r[1] <= axis_y <= r[3]:
        owner = r[4]
        break
assert owner == "门厅", f"操场正对的不是门厅而是「{owner}」"

# ── 自检 9：上下两排对调（教室排在北、门厅在南）──
classrooms = [r for r in school["rooms"] if r[4] in ("教室一", "教室二")]
for r in classrooms:
    assert r[1] < r[3], f"教室排没在北边：{r[4]}"
assert hall[1] > classrooms[0][3], "门厅没落到南排"

# ── 自检 10：办公室与会议室都改成教室；全校四间教室 ──
for gone in ("办公室", "会议室", "教师宿舍"):
    assert gone not in rooms, f"不该还有「{gone}」"
for r in school["rooms"]:
    assert not any(k in r[4] for k in ("办公室", "会议室", "宿舍")), \
        f"房间名不该含「{r[4]}」"
for f in school["furniture"]:
    assert not any(k in f["name"] for k in ("办公桌", "会议长桌", "长会议桌",
                                            "打印机", "茶桶", "旧沙发", "奖状",
                                            "成绩档案柜", "批文匣")), \
        f"不该还有办公/会议家具「{f['name']}」"
for cn in ("教室一", "教室二", "教室三", "教室四"):
    assert cn in rooms, f"缺 {cn}"
    cx0, cy0, cx1, cy1 = rooms[cn][0], rooms[cn][1], rooms[cn][2], rooms[cn][3]
    # 黑板钉在北墙（比房间上沿高一格），讲台/课桌在房内
    names = {f["name"] for f in school["furniture"]
             if f["rect"][0] >= cx0 and f["rect"][0] + f["rect"][2] <= cx1 + 1
             and f["rect"][1] >= cy0 - 1 and f["rect"][1] + f["rect"][3] <= cy1}
    assert "黑板" in names, f"{cn} 没黑板"
    assert "讲台" in names, f"{cn} 没讲台"
    assert "课桌" in names, f"{cn} 没课桌"

# ── 自检 11：操场必须整块上色（room 色键 field = 草地），不能只描边 ──
assert yard[5] == "field", f"操场色键应是 field（整块铺满），现在是 {yard[5]}"
assert FIELD_COLOR.startswith("#") and len(FIELD_COLOR) == 7, "草地色必须是 #rrggbb"
# 操场范围内不得有其它 room 抢色，也不得有裸露的院子色块（' ' 格）
assert yard[0] == 1 and yard[2] == 36 and yard[1] == 19 and yard[3] == 28, \
    f"操场矩形变了：{yard[:4]}"
# 跑道必须单独指定红土色（跟草地区分开）
for f in track_furn:
    assert f.get("color") == TRACK_COLOR, "跑道格必须指定红土色"
assert TRACK_COLOR != FIELD_COLOR, "跑道色不能跟草地色一样"

if PREVIEW:
    out = os.path.join(HERE, "..", "..", "lab", "school_plan_preview.png")
    render(school).save(out)
    print("PREVIEW only (JSON untouched):", os.path.abspath(out))
    print("rooms", len(school["rooms"]), "furniture", len(school["furniture"]),
          "desks", len(desks), "track cells", len(cells))
else:
    with open(DATA, encoding="utf-8") as f:
        houses = json.load(f)
    for i, h in enumerate(houses):
        if h["id"] == "school":
            houses[i] = school
            break
    else:
        houses.append(school)
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(houses, f, ensure_ascii=False, indent=2)
    print(f"school written: houses {len(houses)} lot {school['lot']} "
          f"rooms {len(school['rooms'])} furniture {len(school['furniture'])}")
