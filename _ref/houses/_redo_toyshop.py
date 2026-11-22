"""A5 2026 玩具店（周家曾孙 · 租沈家的楼）：整栋精调重写 · v4（加门前庭院 + 货架列间距 2 格）。

v4 口径（用户 2026-11-22 拍板，四条）：
  - **滑梯不肯出现** → 删掉「滑梯」。
  - **货架还可以再多一点，两列货架之间留两个比较合适** → 店面改成「货架列」布局：
    竖向货架列（1 格宽 × 2 格高）成排排布，**相邻两列之间留 2 格通道**；
    货架数从 v3 的 9 组增加到 12 组。
  - **这个玩具店也需要庭院，庭院放在门口的位置比较合适** → 屋本体不变（21×16），
    整个占地北侧留出 **4 格深的门前庭院**（院子在店门正前方），占地从 21×16 变成 **21×20**。
    前门（大门）从屋本体北墙移到 **y=4**（屋本体北墙那一行），门内是店面、门外是庭院。
  - **摇摇车可以安排两个** → 摇摇马放两只（x4 / x6）。

v3 口径（保留）：玩具不落地 —— 小件货品全部并进货架/柜台的 note（「架上摆着…」），
  落地只留大件（童车 / 摇摇马 / 儿童自行车）；美术那边只要多出几版不重样的货架贴图。

v2/v1 口径（保留）：尺寸 21×16 格（336×256 px）；街面朝北（证物链要求招牌小字在店面北墙）；
  前门在北墙街面、后门在南墙通后巷进货；四间：店面 / 里屋（沈家雇来看店的人的铺）/ 账房 / 仓库；
  账柜落账房北墙；周有田往来账**仍写「位置待定」，不写成定论**。

v4 最终坐标（屋本体整体下移 4 格，让出北侧庭院）：
  占地 lot [0,0,20,19] = 21×20 格（336×320 px）
  屋本体 wings [[0,4,21,16]] → 屋本体 x0..20 / y4..19
  庭院 = y0..3（北侧门前院子，21×4 格）
  北墙 y=4：前门 gate [[9,4],[10,4]]（门内店面、门外庭院）
  店面 y5..11（x1..19）｜隔墙 y=12（门 (9,12)）｜后排 y13..18
  里屋 x1..5 ｜ 账房 x7..12 ｜ 仓库 x14..19（竖墙 x=6 / x=13，门 (6,15) / (13,15)）
  南墙 y=19：后门 gate [[16,19],[17,19]]（通后巷进货，进的是仓库）

幂等：存在则替换，否则追加。
预览：MCS_PREVIEW=1 只出预览图到 lab/，不写 houses_data.json。
"""
import json
import os
from gen_all_houses import build_grid, render

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")
PREVIEW = os.environ.get("MCS_PREVIEW") == "1"

# v4 尺寸口径（唯一真值，脚本自检会卡住）
LOT = [0, 0, 20, 19]          # 21×20 格（含北侧 4 格庭院）
WING = [0, 4, 21, 16]         # 屋本体 21×16，落在 y4..19
YARD_DEPTH = 4                # 门前庭院深度（格）
FRONT_GATE = [[9, 4], [10, 4]]    # 前门在屋本体北墙，正对门前庭院
BACK_GATE = [[16, 19], [17, 19]]  # 后门在屋本体南墙，通后巷进货

# 小件货品：只能出现在货架/柜台的 note 里，不许单独占一格当家具
SMALL_GOODS = ("拨浪鼓", "铁皮青蛙", "纸风车", "陀螺", "弹弓", "竹蜻蜓",
               "积木", "拼图", "布娃娃", "气球", "遥控车", "电子小汽车",
               "塑料小家电", "文具盒", "泡泡机", "蜡笔", "滑板车", "小推车",
               "学步车", "玩具样车")
# 落地大件：本来就该摆地上给人试
FLOOR_DISPLAY = ("童车展示", "摇摇马", "儿童自行车")
# 货架类家具（note 必须写清架上摆什么）
SHELF_NAMES = ("货架", "老货柜", "中岛货架", "柜台")
# 禁出现的家具（用户 m00939：「滑梯不肯出现」）
BANNED = ("滑梯",)


def F(name, x, y, w, h, note="", clue=False, short=None, zone="house",
      yard_building=False, wall_mounted=False):
    return dict(name=name, short=short or name, rect=[x, y, w, h], note=note,
                clue=clue, zone=zone, yard_building=yard_building,
                wall_mounted=wall_mounted)


toyshop = {
    "id": "toyshop",
    "name": "玩具店 · A5 2026 · 周家曾孙（租沈家的楼）",
    "lot": LOT,
    "wings": [WING],
    # 隔墙：
    #   y=12 整条横墙（店面 | 后排），门在 (9,12)
    #   x=6  竖墙（里屋 | 账房），门在 (6,15)
    #   x=13 竖墙（账房 | 仓库），门在 (13,15)
    "partitions": [
        [1, 12, 19, 12],
        [6, 13, 6, 18],
        [13, 13, 13, 18],
    ],
    # 房门：(9,12) 店面↔账房 | (6,15) 里屋↔账房 | (13,15) 账房↔仓库
    "doors": [[9, 12], [6, 15], [13, 15]],
    # 大门：前门在屋本体北墙（门外就是门前庭院）｜后门在屋本体南墙（通后巷进货）
    "gate": FRONT_GATE + BACK_GATE,
    "rooms": [
        [1, 5, 19, 11, "店面", "shop"],
        [1, 13, 5, 18, "里屋", "bed"],
        [7, 13, 12, 18, "账房", "account"],
        [14, 13, 19, 18, "仓库", "store"],
    ],
    "furniture": [
        # ══ 门前庭院 y0..3（x0..20，门在 (9,4)(10,4) 正前方的院子）══
        F("旧招牌架", 2, 1, 2, 1, "门口 · 挂着的旧幌子，三代没换过", zone="yard"),
        F("板车", 11, 1, 2, 1, "门口 · 卸货用的板车", zone="yard"),
        F("水缸", 18, 1, 1, 1, "门口 · 接雨水", zone="yard"),
        F("二八大杠", 6, 2, 2, 1, "门口 · 靠墙停着的旧自行车", zone="yard"),
        F("扫帚", 1, 3, 1, 1, "门口靠墙的扫帚", zone="yard"),
        F("货箱堆", 15, 3, 2, 1, "门口 · 等着搬进仓库的箱子", zone="yard"),
        # ══ 店面 x1..19, y5..11（北墙 y=4 前门，x9..10 是入店通道）══
        # 证物：招牌小字钉在店面北墙最西端（屋本体北墙那一行 y=4）
        F("招牌小字", 1, 4, 2, 1, "「本店由沈氏物业出租」· 店面北墙西端 · A5 铁证链一环",
          clue=True, short="招牌", wall_mounted=True),
        # ── 第一排（贴北墙）：老货角 + 收银台 + 货架列 ──
        F("老货柜", 1, 5, 3, 1, "玻璃柜台 · 架上摆着镇店的旧货：拨浪鼓、铁皮青蛙、纸风车、木陀螺"),
        F("货架", 1, 6, 3, 1, "老货架 · 架上摆着旧货：陀螺、竹蜻蜓、弹弓"),
        F("收银台", 5, 5, 3, 1, "前门旁 · 算盘与找零抽屉"),
        F("货架", 11, 5, 1, 2, "货架列 · 架上摆着新货：遥控车、电子小汽车"),
        F("货架", 14, 5, 1, 2, "货架列 · 架上摆着新货：塑料小家电、风扇"),
        F("货架", 17, 5, 3, 1, "货架列 · 架上摆着新货：文具盒、作业本、蜡笔"),
        # ── 第二排：货架列（与第一排之间是 2 格宽的横向通道 y7..8）──
        F("货架", 1, 9, 1, 2, "货架列 · 架上摆着旧货：铁皮青蛙盒、纸风车架"),
        F("货架", 4, 9, 1, 2, "货架列 · 架上摆着新货：积木、拼图"),
        F("货架", 7, 9, 1, 2, "货架列 · 架上摆着新货：蜡笔盒、拼图盒"),
        F("货架", 11, 9, 1, 2, "货架列 · 架上摆着新货：积木桶、拼图大盒"),
        F("货架", 14, 9, 1, 2, "货架列 · 架上摆着新货：学步车、布娃娃、气球桶"),
        F("货架", 17, 9, 3, 1, "货架列 · 架上摆着新货：气泡机、泡泡机"),
        F("货架", 17, 10, 3, 1, "货架列 · 架上摆着新货：滑板车、小推车"),
        # ── 沿南墙一线：落地大件 + 一排货架 ──
        F("童车展示", 1, 11, 2, 1, "落地陈列的大件 · 折叠童车，摆在店里给人看"),
        F("摇摇马", 4, 11, 1, 1, "落地陈列的大件 · 摇摇马，孩子试骑"),
        F("摇摇马", 6, 11, 1, 1, "落地陈列的大件 · 摇摇马，孩子试骑"),
        F("儿童自行车", 13, 11, 2, 1, "落地陈列的大件 · 儿童自行车"),
        F("货架", 16, 11, 2, 1, "货架列 · 架上摆着新货：遥控车配件、气球"),
        # ══ 里屋 x1..5, y13..18（沈家雇来看店的人的铺位）══
        F("单人床", 1, 13, 2, 1, "看店人的铺 · 沈家雇的人住这儿"),
        F("被褥", 1, 14, 2, 1, "叠在床尾的旧被褥"),
        F("小桌", 4, 13, 2, 1, "看店人吃饭看账的地方"),
        F("马扎", 4, 14, 1, 1, "小桌旁的马扎"),
        F("旧衣柜", 5, 16, 1, 2, "贴东墙"),
        F("脸盆架", 1, 17, 1, 1, "里屋西南角"),
        F("木箱", 1, 18, 2, 1, "装旧物的木箱"),
        F("煤油灯", 3, 18, 1, 1, "看店人自己留的灯"),
        F("小板凳", 5, 18, 1, 1, "门口的小板凳"),
        # ══ 账房 x7..12, y13..18 ══
        # 证物：账柜贴账房北墙（y=12 的隔墙上）
        F("账柜", 11, 12, 2, 1, "贴账房北墙 · 周有田往来账可能在此（位置待定，未定论）",
          clue=True, short="账柜", wall_mounted=True),
        F("档案柜", 7, 13, 1, 1, "贴西墙 · 旧账本"),
        F("办公桌", 7, 14, 2, 1, "账房办公 · 桌上算盘与流水"),
        F("椅", 9, 14, 1, 1, "办公桌旁"),
        F("算盘", 10, 14, 1, 1, "沈家做账用同一款式"),
        F("账本堆", 11, 14, 1, 1, "一摞流水账"),
        F("铁皮柜", 7, 16, 1, 2, "贴西墙 · 上锁的柜子"),
        F("废纸篓", 10, 16, 1, 1, "账房角落"),
        F("暖水瓶", 12, 16, 1, 1, "账房角落"),
        F("旧台灯", 12, 17, 1, 1, "桌上的旧台灯"),
        F("算盘盒", 12, 18, 1, 1, "装旧算盘的盒子"),
        # ══ 仓库 x14..19, y13..18 ══
        F("货架", 14, 13, 1, 2, "西墙货架 · 架上摆着还没拆箱的存货"),
        F("货架", 19, 13, 1, 2, "东墙货架 · 架上摆着还没拆箱的存货"),
        F("货箱", 16, 13, 2, 1, "新到的玩具箱"),
        F("纸箱堆", 16, 14, 2, 1, "纸箱堆"),
        F("货箱", 15, 15, 2, 1, "存货 · 让开账房通仓库的门 (13,15)"),
        F("旧招牌板", 17, 16, 2, 1, "三代没换过的旧门板 · 靠在墙边"),
        F("拆封样品", 14, 17, 2, 1, "拆了包装的样品箱"),
        F("扫帚", 17, 17, 1, 1, "扫仓库的扫帚"),
        F("纸箱", 18, 18, 1, 1, "角落的纸箱"),
        F("水桶", 19, 18, 1, 1, "水桶"),
    ],
    "clue": [
        "店面北墙招牌小字「本店由沈氏物业出租」（A5 铁证链一环）",
        "账房账柜：周有田往来账可能在此（位置待定，未定论）",
    ],
    "story": "租的是沈家的楼，雇的是沈家的人；周家三代不知道替谁看店。",
    "note": ("屋本体 21×16 格 = 336×256 px；占地 21×20 格 = 336×320 px（v4 加北侧 4 格门前庭院）。"
             "旧 note 的「15×9」「15×11」均作废。v4：门前有庭院（前门开在屋本体北墙 y=4，"
             "门外正对院子），院内停着板车与旧自行车、挂着三代没换过的旧幌子；"
             "店内改成货架列布局——竖向货架列成排排布，相邻两列之间留 2 格通道，"
             "货架 12 组；店里的玩具不落地，小件货品全部写进货架的 note（架上摆着…），"
             "落地只留大件（童车 / 摇摇马两只 / 儿童自行车），美术那边只要多出几版不重样的"
             "货架贴图即可。x9..10 是入店通道。后排 y13..18 = 里屋 x1..5 / 账房 x7..12 / "
             "仓库 x14..19。后门 (16,19)(17,19) 通后巷进货，进的是仓库。"
             "招牌小字钉在店面北墙最西端 [1,4,2,1]；账柜贴账房北墙 [11,12,2,1]——"
             "周有田往来账位置待定，未定论。货品新旧混搭：老货进老货柜与西侧货架列，"
             "新货撑门面货架列。"),
}

# ── 自检 1：家具不重叠、门/大门四邻禁放家具 ──
occupied = set()
for f in toyshop["furniture"]:
    x, y, w, h = f["rect"]
    for i in range(x, x + w):
        for j in range(y, y + h):
            assert (i, j) not in occupied, f"家具重叠 ({i},{j}) · {f['name']}"
            occupied.add((i, j))
for d in [tuple(d) for d in toyshop["doors"]] + [tuple(g) for g in toyshop["gate"]]:
    x, y = d
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        assert (x + dx, y + dy) not in occupied, f"堵门：家具占门 {d} 邻格 ({x+dx},{y+dy})"

# ── 自检 2：家具不压墙/门/院门（wall_mounted 的证物除外）──
grid = build_grid(toyshop)
for f in toyshop["furniture"]:
    if f.get("wall_mounted"):
        continue
    x, y, w, h = f["rect"]
    for i in range(x, x + w):
        for j in range(y, y + h):
            assert grid[j][i] in (".", " "), f"家具压墙/门：{f['name']} ({i},{j}) = {grid[j][i]}"

# ── 自检 3：室内每个地板格都有房间归属（不露默认棕）──
room_cells = {(i, j) for (x0, y0, x1, y1, *_rest) in toyshop["rooms"]
              for j in range(y0, y1 + 1) for i in range(x0, x1 + 1)}
floor_cells = {(i, j) for j, row in enumerate(grid) for i, ch in enumerate(row) if ch == "."}
for c in sorted(floor_cells - room_cells):
    raise AssertionError(f"室内无主格（露默认色）: {c}")

# ── 自检 4：尺寸与屋本体口径 ──
assert toyshop["lot"] == LOT, f"lot 必须是 {LOT}"
assert toyshop["wings"] == [WING], f"wings 必须是 {[WING]}"
assert (LOT[2] - LOT[0] + 1) == 21 and (LOT[3] - LOT[1] + 1) == 20, "占地不是 21×20"
# wings 是 (x0, y0, w, h)：屋本体 21×16，落在 y4..19
assert (WING[2], WING[3]) == (21, 16), "屋本体不是 21×16"
assert WING[0] == LOT[0] and WING[1] == LOT[1] + YARD_DEPTH, "屋本体没贴在庭院南边"

# ── 自检 5：四间房，坐标固定 ──
rm = {r[4]: r for r in toyshop["rooms"]}
assert set(rm) == {"店面", "里屋", "账房", "仓库"}, f"房间不对：{sorted(rm)}"
assert rm["店面"][:4] == [1, 5, 19, 11], "店面应是 x1..19,y5..11"
assert rm["里屋"][:4] == [1, 13, 5, 18], "里屋应是 x1..5,y13..18"
assert rm["账房"][:4] == [7, 13, 12, 18], "账房应是 x7..12,y13..18"
assert rm["仓库"][:4] == [14, 13, 19, 18], "仓库应是 x14..19,y13..18"

# ── 自检 6：证物链两条落点（不许挪位置，也不许写成定论）──
sign = [f for f in toyshop["furniture"] if f["name"] == "招牌小字"]
assert len(sign) == 1, "招牌小字必须只有一处"
assert sign[0]["clue"], "招牌小字必须是 clue"
assert sign[0]["rect"] == [1, 4, 2, 1], f"招牌小字必须钉在店面北墙西端 [1,4,2,1]，现在 {sign[0]['rect']}"
assert sign[0].get("wall_mounted"), "招牌小字是钉在墙上的"
assert "沈氏物业出租" in sign[0]["note"], "招牌小字必须写明「本店由沈氏物业出租」"
cab = [f for f in toyshop["furniture"] if f["name"] == "账柜"]
assert len(cab) == 1, "账柜必须只有一处"
assert cab[0]["clue"], "账柜必须是 clue"
assert cab[0]["rect"] == [11, 12, 2, 1], f"账柜必须贴账房北墙 [11,12,2,1]，现在 {cab[0]['rect']}"
assert "位置待定" in cab[0]["note"], "往来账必须仍写「位置待定」"
assert "未定论" in cab[0]["note"], "往来账必须仍写「未定论」"

# ── 自检 7：前门在屋本体北墙（门外是庭院）、后门在屋本体南墙，各 2 格宽 ──
# wings 是 (x0, y0, w, h)：屋本体北墙 = WING[1]，南墙 = WING[1]+WING[3]-1
WALL_N = WING[1]
WALL_S = WING[1] + WING[3] - 1
gset = {tuple(g) for g in toyshop["gate"]}
front = {g for g in gset if g[1] == WALL_N}
back = {g for g in gset if g[1] == WALL_S}
assert len(front) == 2, f"前门必须 2 格宽，现在 {len(front)}"
assert len(back) == 2, f"后门必须 2 格宽，现在 {len(back)}"
assert {g[0] for g in front} == {9, 10}, f"前门位置不对：{front}"
assert {g[0] for g in back} == {16, 17}, f"后门位置不对：{back}"
# 门内侧归属：前门内是店面、后门内是仓库
for g, room in ((list(front)[0], "店面"), (list(back)[0], "仓库")):
    inner = (g[0], g[1] + 1) if g[1] == WALL_N else (g[0], g[1] - 1)
    owner = None
    for r in toyshop["rooms"]:
        if r[0] <= inner[0] <= r[2] and r[1] <= inner[1] <= r[3]:
            owner = r[4]
            break
    assert owner == room, f"门 {g} 内侧是「{owner}」，应该是「{room}」"

# ── 自检 8：门前庭院（院子在门口，北侧 ≥3 格深）──
assert WING[1] - LOT[1] >= 3, "门前庭院深度不足 3 格"
assert YARD_DEPTH == WING[1] - LOT[1], "庭院深度常量与坐标不符"
# 庭院格必须是空地（' '）且不属于任何房间
yard_cells = {(i, j) for j in range(LOT[1], WING[1]) for i in range(LOT[0], LOT[2] + 1)}
for c in sorted(yard_cells):
    ch = grid[c[1] - LOT[1]][c[0] - LOT[0]]
    assert ch == " ", f"庭院格 ({c[0]},{c[1]}) 不是空地，而是 {ch}"
    assert c not in room_cells, f"庭院格 ({c[0]},{c[1]}) 不该属于任何房间"
# 门前要有院子家具（不能是空院子）
assert any(f["zone"] == "yard" for f in toyshop["furniture"]), "门前庭院里要有东西"
yard_f = [f for f in toyshop["furniture"] if f["zone"] == "yard"]
for f in yard_f:
    x, y, w, h = f["rect"]
    for i in range(x, x + w):
        for j in range(y, y + h):
            assert (i, j) in yard_cells, f"院子家具「{f['name']}」不在庭院里"

# ── 自检 9：货架列间距 —— 同一排（y 区间有重叠）的两列货架之间留 ≥2 格通道 ──
shop = rm["店面"]
shop_shelves = []
for f in toyshop["furniture"]:
    if f["name"] not in SHELF_NAMES:
        continue
    x, y, w, h = f["rect"]
    if shop[0] <= x and x + w - 1 <= shop[2] and shop[1] <= y and y + h - 1 <= shop[3]:
        shop_shelves.append(f)
assert len(shop_shelves) >= 12, f"店面货架太少（{len(shop_shelves)} 组），用户要求再多一点"
for i in range(len(shop_shelves)):
    for j in range(i + 1, len(shop_shelves)):
        a, b = shop_shelves[i], shop_shelves[j]
        ax, ay, aw, ah = a["rect"]
        bx, by, bw, bh = b["rect"]
        a_y, b_y = set(range(ay, ay + ah)), set(range(by, by + bh))
        if not (a_y & b_y):
            continue                      # 不同排，不算列间距
        a_x, b_x = (ax, ax + aw - 1), (bx, bx + bw - 1)
        if b_x[0] > a_x[1]:
            gap = b_x[0] - a_x[1] - 1
        elif a_x[0] > b_x[1]:
            gap = a_x[0] - b_x[1] - 1
        else:
            gap = -1
        assert gap >= 2, (f"两列货架之间只隔 {gap} 格（用户要留 2 格）："
                          f"{a['name']}{a['rect']} 与 {b['name']}{b['rect']}")

# ── 自检 10：玩具不落地 —— 小件货品只许出现在货架/柜台的 note 里 ──
for f in toyshop["furniture"]:
    if f["name"] in FLOOR_DISPLAY:
        continue
    for k in SMALL_GOODS:
        assert k not in f["name"], f"小件货品「{k}」不该单独占格当家具（应并进货架的 note）"
for f in toyshop["furniture"]:
    if f["name"] in SHELF_NAMES:
        assert "架上摆着" in f["note"], f"货架「{f['name']}」的 note 必须写清架上摆着什么东西"
for f in shop_shelves:
    assert any(k in f["note"] for k in SMALL_GOODS), \
        f"店面货架「{f['name']}」({f['rect']}) 的 note 要点明架上摆的货品"

# ── 自检 11：新旧混搭（老货当镇店之宝，新货撑门面）──
notes = " ".join(f["note"] for f in toyshop["furniture"])
for k in ("拨浪鼓", "铁皮青蛙", "纸风车", "陀螺", "弹弓", "竹蜻蜓"):
    assert k in notes, f"少了老货「{k}」"
for k in ("积木", "拼图", "布娃娃", "气球", "遥控车", "文具盒"):
    assert k in notes, f"少了新货「{k}」"
assert any("老货" in f["note"] for f in toyshop["furniture"]), "老货的 note 里要写明是老货"
assert any("新货" in f["note"] for f in toyshop["furniture"]), "新货的 note 里要写明是新货"

# ── 自检 12：落地大件 —— 两只摇摇马，无滑梯 ──
rockers = [f for f in toyshop["furniture"] if f["name"] == "摇摇马"]
assert len(rockers) == 2, f"摇摇马要两只，现在 {len(rockers)} 只"
for f in toyshop["furniture"]:
    for k in BANNED:
        assert k not in f["name"], f"不该出现「{f['name']}」"

# ── 自检 13：年代红线（2026 年的村里小玩具店不该有的东西）──
forbidden = ("电视", "电脑", "手机", "自动售货机", "抓娃娃机", "奶茶机",
             "空调", "冰箱", "微波炉")
for f in toyshop["furniture"]:
    assert not any(k in f["name"] for k in forbidden), f"不该有「{f['name']}」"

if PREVIEW:
    out = os.path.join(HERE, "..", "..", "lab", "toyshop_plan_preview.png")
    render(toyshop).save(out)
    print("PREVIEW only (JSON untouched):", os.path.abspath(out))
    print("rooms", len(toyshop["rooms"]), "furniture", len(toyshop["furniture"]))
else:
    with open(DATA, encoding="utf-8") as f:
        houses = json.load(f)
    for i, h in enumerate(houses):
        if h["id"] == "toyshop":
            houses[i] = toyshop
            break
    else:
        houses.append(toyshop)
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(houses, f, ensure_ascii=False, indent=2)
    print(f"toyshop written: houses {len(houses)} lot {toyshop['lot']} "
          f"rooms {len(toyshop['rooms'])} furniture {len(toyshop['furniture'])}")
