"""A5 2026 玩具店（周家曾孙 · 租沈家的楼）：整栋精调重写 · v2（放大到 21×16 + 新旧混搭）。

v2 口径（用户 2026-11-22 拍板）：
  - 尺寸：15×11 → **21×16 格**（336×256 px @16px/格），lot [0,0,20,15]、wings [[0,0,21,16]]。
  - 货品：**新旧混搭**——老货（拨浪鼓/铁皮青蛙/纸风车/陀螺/弹弓/竹蜻蜓）当镇店之宝，
    新货（学步车/积木/拼图/布娃娃/气球/遥控车/文具/塑料小家电）撑门面。
    突出「三代人没换过招牌」的味道。
  - 街面仍朝北：证物链要求「玩具店招牌小字『本店由沈氏物业出租』」在**店面北墙**，
    故前门（大门）开在北墙，招牌小字钉在店面北墙西端；南墙留后门通仓库（后巷进货）。
  - 四间：店面 / 里屋（沈家雇来看店的人的铺）/ 账房 / 仓库。
    账柜落账房北墙；周有田往来账**仍写「位置待定」，不写成定论**。
  - 家具硬规矩：不压门、不越界、不重叠、不堵门（四邻全空），室内每格有房间归属。

结构（21×16 格，街面朝北）：
  北墙 y=0     ：前门 (9,0)(10,0)（2 格宽）
  店面 y=1..7  ：x1..19 整间（19×7），招牌小字钉北墙西端 [1,0,2,1]
  墙 y=8       ：店面 | 后排（门 (9,8) 店面↔账房）
  后排 y=9..14 ：里屋 x1..5 │ 账房 x7..12 │ 仓库 x14..19（竖墙 x=6 / x=13）
  南墙 y=15    ：后门 (16,15)(17,15)（2 格宽，通后巷进货，进仓库）

证物链：
  - 招牌小字「本店由沈氏物业出租」→ 店面北墙西端 **[1,0,2,1]**（A5 铁证链一环）。
  - 账柜 → 账房北墙 **[11,8,2,1]**；周有田往来账**位置待定，未定论**。

幂等：存在则替换，否则追加。
预览：MCS_PREVIEW=1 只出预览图到 lab/，不写 houses_data.json。
"""
import json
import os
from gen_all_houses import build_grid, render

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")
PREVIEW = os.environ.get("MCS_PREVIEW") == "1"

# v2 尺寸口径（唯一真值，脚本自检会卡住）
LOT = [0, 0, 20, 15]          # 21×16 格
WING = [0, 0, 21, 16]
# 前门（北墙）与后门（南墙）
FRONT_GATE = [[9, 0], [10, 0]]
BACK_GATE = [[16, 15], [17, 15]]


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
    #   y=8  整条横墙（店面 | 后排），门在 (9,8)
    #   x=6  竖墙（里屋 | 账房），门在 (6,11)
    #   x=13 竖墙（账房 | 仓库），门在 (13,11)
    "partitions": [
        [1, 8, 19, 8],
        [6, 9, 6, 14],
        [13, 9, 13, 14],
    ],
    # 房门：(9,8) 店面↔账房 | (6,11) 里屋↔账房 | (13,11) 账房↔仓库
    "doors": [[9, 8], [6, 11], [13, 11]],
    # 大门：北墙前门（街面，2 格宽）+ 南墙后门（通后巷进货，2 格宽）
    "gate": FRONT_GATE + BACK_GATE,
    "rooms": [
        [1, 1, 19, 7, "店面", "shop"],
        [1, 9, 5, 14, "里屋", "bed"],
        [7, 9, 12, 14, "账房", "account"],
        [14, 9, 19, 14, "仓库", "store"],
    ],
    "furniture": [
        # ── 店面 x1..19,y1..7（北面开前门，x9..10 留出入店通道）──
        # 证物：招牌小字钉在店面北墙最西端
        F("招牌小字", 1, 0, 2, 1, "「本店由沈氏物业出租」· 店面北墙西端 · A5 铁证链一环",
          clue=True, short="招牌", wall_mounted=True),
        # 北墙一排（老货柜在西门边，收银台靠前门西侧）
        F("老货柜", 1, 1, 3, 1, "玻璃柜台 · 镇店的旧货：拨浪鼓、铁皮青蛙、纸风车"),
        F("玩具架", 5, 1, 1, 2, "前门西侧 · 竖向贴墙"),
        F("收银台", 6, 1, 3, 1, "前门旁 · 算盘与找零抽屉"),
        F("玩具架", 11, 1, 1, 2, "前门东侧 · 竖向贴墙"),
        F("遥控车架", 13, 1, 2, 1, "新货 · 一排遥控车"),
        F("塑料小家电架", 16, 1, 2, 1, "新货 · 塑料小风扇、小收音机"),
        F("文具盒柜", 18, 1, 2, 1, "新货 · 铅笔盒与作业本"),
        # 第二排
        F("铁皮青蛙盒", 1, 2, 1, 1, "老货 · 铁皮青蛙，柜台里搬出来的"),
        F("纸风车架", 2, 2, 1, 1, "老货 · 手扎纸风车"),
        F("陀螺盒", 3, 2, 1, 1, "老货 · 木头陀螺"),
        F("弹弓盒", 4, 2, 1, 1, "老货 · 弹弓（不卖，只是老货堆里的一件）"),
        F("竹蜻蜓盒", 13, 2, 1, 1, "老货 · 竹蜻蜓"),
        F("拼图盒", 14, 2, 1, 1, "新货 · 拼图"),
        F("蜡笔盒", 15, 2, 1, 1, "新货 · 蜡笔"),
        F("积木箱", 16, 2, 2, 1, "新货 · 积木"),
        F("布娃娃", 18, 2, 1, 1, "新货 · 布娃娃"),
        # 第三排
        F("玩具架", 1, 3, 1, 2, "贴西墙"),
        F("拨浪鼓堆", 2, 3, 1, 1, "老货 · 拨浪鼓"),
        F("学步车", 3, 3, 2, 1, "新货 · 学步车"),
        F("儿童自行车", 13, 3, 2, 1, "新货 · 儿童自行车"),
        F("滑板车", 16, 3, 1, 1, "新货 · 滑板车"),
        F("气球桶", 18, 3, 1, 1, "新货 · 一桶气球"),
        # 第四排
        F("布娃娃架", 2, 4, 1, 2, "新货 · 挂着的布娃娃"),
        F("积木箱", 3, 4, 2, 1, "新货 · 积木"),
        F("拼图盒", 5, 4, 1, 1, "新货 · 拼图"),
        F("中岛货架", 7, 3, 1, 3, "店面中间的岛架 · 走道从两边绕"),
        F("电子小汽车", 13, 4, 2, 1, "新货 · 遥控小汽车"),
        F("货箱", 17, 4, 2, 1, "没拆的箱子 · 堆在架子上"),
        # 第五排
        F("泡泡机", 3, 5, 1, 1, "新货 · 泡泡机"),
        F("积木桶", 4, 5, 1, 1, "新货 · 塑料积木桶"),
        F("童车展示", 5, 5, 2, 1, "新货 · 摆在中间给人看的童车"),
        F("纸箱", 16, 5, 1, 1, "拆开的空箱"),
        # 第六排
        F("玩具样车", 1, 6, 2, 1, "孩子试骑的样车"),
        F("拼图大盒", 3, 6, 2, 1, "新货 · 大盒拼图"),
        F("摇摇马", 6, 6, 1, 1, "摇摇马 · 孩子试骑"),
        F("滑梯", 12, 6, 2, 1, "新货 · 小滑梯"),
        F("童车", 16, 6, 2, 1, "新货 · 折叠童车"),
        # 第七排（南墙一线，留出 (9,7)(10,7) 通后门）
        F("货箱", 1, 7, 2, 1, "补货的箱子"),
        F("样品摊", 3, 7, 2, 1, "拆了包装的样品"),
        F("塑料玩具箱", 6, 7, 2, 1, "新货 · 一整箱塑料玩具"),
        F("小推车", 12, 7, 2, 1, "新货 · 儿童小推车"),
        F("纸箱堆", 16, 7, 2, 1, "堆到墙角的空箱"),
        # ── 里屋 x1..5,y9..14（沈家雇来看店的人的铺位）──
        F("单人床", 1, 9, 2, 1, "看店人的铺 · 沈家雇的人住这儿"),
        F("小桌", 4, 9, 2, 1, "看店人吃饭看账的地方"),
        F("被褥", 1, 10, 2, 1, "叠在床尾的旧被褥"),
        F("马扎", 4, 10, 1, 1, "小桌旁的马扎"),
        F("旧衣柜", 5, 12, 1, 2, "贴东墙"),
        F("脸盆架", 1, 13, 1, 1, "里屋西南角"),
        F("泡面箱", 2, 13, 1, 1, "看店人吃的泡面"),
        F("搪瓷盆", 4, 13, 1, 1, "洗脸的搪瓷盆"),
        F("木箱", 1, 14, 2, 1, "装旧物的木箱"),
        F("煤油灯", 3, 14, 1, 1, "看店人自己留的灯"),
        F("小板凳", 5, 14, 1, 1, "门口的小板凳"),
        # ── 账房 x7..12,y9..14 ──
        # 证物：账柜贴账房北墙（y=8 的墙上）
        F("账柜", 11, 8, 2, 1, "贴账房北墙 · 周有田往来账可能在此（位置待定，未定论）",
          clue=True, short="账柜", wall_mounted=True),
        F("档案柜", 7, 9, 1, 1, "贴西墙 · 旧账本"),
        F("办公桌", 7, 10, 2, 1, "账房办公 · 桌上算盘与流水"),
        F("椅", 9, 10, 1, 1, "办公桌旁"),
        F("算盘", 10, 10, 1, 1, "沈家做账用同一款式"),
        F("账本堆", 11, 10, 1, 1, "一摞流水账"),
        F("铁皮柜", 7, 12, 1, 2, "贴西墙 · 上锁的柜子"),
        F("废纸篓", 10, 12, 1, 1, "账房角落"),
        F("暖水瓶", 12, 12, 1, 1, "账房角落"),
        F("茶缸", 10, 13, 1, 1, "看店人的茶缸"),
        F("胶水罐", 11, 13, 1, 1, "算账用的胶水"),
        F("复写纸", 12, 13, 1, 1, "写单据的复写纸"),
        F("旧台灯", 7, 14, 1, 1, "桌上的旧台灯"),
        F("算盘盒", 12, 14, 1, 1, "装旧算盘的盒子"),
        # ── 仓库 x14..19,y9..14 ──
        F("货架", 14, 9, 1, 2, "贴西墙"),
        F("货架", 19, 9, 1, 2, "贴东墙"),
        F("货箱", 16, 9, 2, 1, "新到的玩具箱"),
        F("拆封样品", 18, 9, 1, 1, "拆了包装的样品"),
        F("纸箱堆", 16, 10, 2, 1, "纸箱堆"),
        F("货箱", 15, 11, 2, 1, "存货 · 让开账房通仓库的门 (13,11)"),
        F("梯子", 19, 11, 1, 2, "上架用的旧梯子"),
        F("麻袋", 17, 12, 1, 1, "装碎料的麻袋"),
        F("自行车堆", 14, 13, 2, 1, "拆了包装的童车"),
        F("童车堆", 16, 13, 2, 1, "堆起来的童车"),
        F("旧招牌板", 18, 13, 2, 1, "三代没换过的旧门板 · 靠在墙边"),
        F("纸箱", 14, 14, 1, 1, "角落的纸箱"),
        F("扫帚", 15, 14, 1, 1, "扫仓库的扫帚"),
        F("拖把", 18, 14, 1, 1, "拖把"),
        F("水桶", 19, 14, 1, 1, "水桶"),
    ],
    "clue": [
        "店面北墙招牌小字「本店由沈氏物业出租」（A5 铁证链一环）",
        "账房账柜：周有田往来账可能在此（位置待定，未定论）",
    ],
    "story": "租的是沈家的楼，雇的是沈家的人；周家三代不知道替谁看店。",
    "note": ("屋本体 21×16 格 = 336×256 px（lot/wings 一致；旧 note 的「15×9」「15×11」均作废）。"
             "v2 放大到 21×16，店面整间 x1..19、y1..7（19×7），x9..10 留出入店通道；"
             "后排 y=9..14 = 里屋 x1..5 / 账房 x7..12 / 仓库 x14..19。"
             "街面朝北：前门（大门）开在北墙 (9,0)(10,0) 两格宽，"
             "招牌小字钉在店面北墙最西端 [1,0,2,1]；"
             "南墙 (16,15)(17,15) 后门通后巷进货，进的是仓库。"
             "账柜贴账房北墙 [11,8,2,1]——周有田往来账位置待定，未定论。"
             "货品新旧混搭：老货（拨浪鼓/铁皮青蛙/纸风车/陀螺/弹弓/竹蜻蜓）当镇店之宝，"
             "新货（学步车/积木/拼图/布娃娃/气球/遥控车/文具/塑料小家电）撑门面。"),
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

# ── 自检 4：尺寸必须是 21×16（v2 口径）──
assert toyshop["lot"] == LOT, f"lot 必须是 {LOT}"
assert toyshop["wings"] == [WING], f"wings 必须是 {[WING]}"
assert (LOT[2] - LOT[0] + 1) == 21 and (LOT[3] - LOT[1] + 1) == 16, "尺寸不是 21×16"

# ── 自检 5：四间房（店面/里屋/账房/仓库），且分区不重叠不留缝 ──
rm = {r[4]: r for r in toyshop["rooms"]}
assert set(rm) == {"店面", "里屋", "账房", "仓库"}, f"房间不对：{sorted(rm)}"
assert rm["店面"][:4] == [1, 1, 19, 7], "店面应是 x1..19,y1..7"
assert rm["里屋"][:4] == [1, 9, 5, 14], "里屋应是 x1..5,y9..14"
assert rm["账房"][:4] == [7, 9, 12, 14], "账房应是 x7..12,y9..14"
assert rm["仓库"][:4] == [14, 9, 19, 14], "仓库应是 x14..19,y9..14"

# ── 自检 6：证物链两条落点（不许挪位置，也不许写成定论）──
sign = [f for f in toyshop["furniture"] if f["name"] == "招牌小字"]
assert len(sign) == 1, "招牌小字必须只有一处"
assert sign[0]["clue"], "招牌小字必须是 clue"
assert sign[0]["rect"] == [1, 0, 2, 1], f"招牌小字必须钉在店面北墙西端 [1,0,2,1]，现在 {sign[0]['rect']}"
assert sign[0].get("wall_mounted"), "招牌小字是钉在墙上的"
assert "沈氏物业出租" in sign[0]["note"], "招牌小字必须写明「本店由沈氏物业出租」"
cab = [f for f in toyshop["furniture"] if f["name"] == "账柜"]
assert len(cab) == 1, "账柜必须只有一处"
assert cab[0]["clue"], "账柜必须是 clue"
assert cab[0]["rect"][1] == 8, f"账柜必须贴账房北墙（y=8），现在 {cab[0]['rect']}"
assert "位置待定" in cab[0]["note"], "往来账必须仍写「位置待定」"
assert "未定论" in cab[0]["note"], "往来账必须仍写「未定论」"

# ── 自检 7：前门在北墙、后门在南墙，各 2 格宽 ──
gset = {tuple(g) for g in toyshop["gate"]}
front = {g for g in gset if g[1] == 0}
back = {g for g in gset if g[1] == 15}
assert len(front) == 2, f"前门必须 2 格宽，现在 {len(front)}"
assert len(back) == 2, f"后门必须 2 格宽，现在 {len(back)}"
assert {g[0] for g in front} == {9, 10}, f"前门位置不对：{front}"
assert {g[0] for g in back} == {16, 17}, f"后门位置不对：{back}"
# 前门内侧属于店面、后门内侧属于仓库
for g, room in ((list(front)[0], "店面"), (list(back)[0], "仓库")):
    inner = (g[0], g[1] + 1) if g[1] == 0 else (g[0], g[1] - 1)
    owner = None
    for r in toyshop["rooms"]:
        if r[0] <= inner[0] <= r[2] and r[1] <= inner[1] <= r[3]:
            owner = r[4]
            break
    assert owner == room, f"门 {g} 内侧是「{owner}」，应该是「{room}」"

# ── 自检 8：新旧混搭（老货当镇店之宝，新货撑门面）──
names = [f["name"] for f in toyshop["furniture"]]
old_goods = ("拨浪鼓", "铁皮青蛙", "纸风车", "陀螺", "弹弓", "竹蜻蜓")
new_goods = ("学步车", "积木", "拼图", "布娃娃", "气球", "遥控", "文具", "小家电")
for k in old_goods:
    assert any(k in n for n in names), f"少了老货「{k}」"
for k in new_goods:
    assert any(k in n for n in names), f"少了新货「{k}」"
assert any("老货" in f["note"] for f in toyshop["furniture"]), "老货的 note 里要写明是老货"

# ── 自检 9：年代红线（2026 年的村里小玩具店不该有的东西）──
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
