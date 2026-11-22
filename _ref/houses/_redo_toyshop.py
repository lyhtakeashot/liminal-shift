"""A5 2026 玩具店（周家曾孙 · 租沈家的楼）：整栋精调重写 · v3（全上架 · 可探索点收敛）。

v3 口径（用户 2026-11-22 拍板）：
  - 尺寸：v2 起 **21×16 格**（336×256 px @16px/格），lot [0,0,20,15]、wings [[0,0,21,16]]。
  - **玩具不直接摆在地上**：v2 把每件玩具（拨浪鼓/积木/布娃娃/遥控车…）都做成独立家具，
    等于给店里造了几十个可探索点，还像杂货摊。用户口径：
    **「只需要有货架就行了，货架让美术同学多出几版放上玩具的不重样就行」**。
    → v3 把小件货品**全部撤掉**，改成「货架/柜台 + 架上摆什么（写在 note 里）」，
      美术那边只要多出几版不重样的货架贴图（架上带玩具）即可。
  - **落地只留大件**：童车 / 摇摇马 / 儿童自行车 / 滑梯 —— 这几样本来就得摆地上给人试。
  - 货品**新旧混搭**：老货（拨浪鼓/铁皮青蛙/纸风车/陀螺/弹弓/竹蜻蜓）进「老货柜」，
    新货（学步车/积木/拼图/布娃娃/气球/遥控车/塑料小家电/文具盒）进普通货架。
  - 街面仍朝北：证物链要求「玩具店招牌小字『本店由沈氏物业出租』」在**店面北墙**，
    故前门（大门）开在北墙，招牌小字钉在店面北墙最西端；南墙留后门通仓库（后巷进货）。
  - 四间：店面 / 里屋（沈家雇来看店的人的铺）/ 账房 / 仓库。
    账柜落账房北墙；周有田往来账**仍写「位置待定」，不写成定论**。
  - 家具硬规矩：不压门、不越界、不重叠、不堵门（四邻全空），室内每格有房间归属。

v2 已作废的部分：83 件家具里约 45 件是「地上摆着的一件玩具」，v3 全部并进货架的 note。

幂等：存在则替换，否则追加。
预览：MCS_PREVIEW=1 只出预览图到 lab/，不写 houses_data.json。
"""
import json
import os
from gen_all_houses import build_grid, render

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")
PREVIEW = os.environ.get("MCS_PREVIEW") == "1"

# v2/v3 尺寸口径（唯一真值，脚本自检会卡住）
LOT = [0, 0, 20, 15]          # 21×16 格
WING = [0, 0, 21, 16]
FRONT_GATE = [[9, 0], [10, 0]]
BACK_GATE = [[16, 15], [17, 15]]

# 小件货品：只能出现在货架/柜台的 note 里，不许单独占一格当家具
SMALL_GOODS = ("拨浪鼓", "铁皮青蛙", "纸风车", "陀螺", "弹弓", "竹蜻蜓",
               "积木", "拼图", "布娃娃", "气球", "遥控车", "电子小汽车",
               "塑料小家电", "文具盒", "泡泡机", "蜡笔", "滑板车", "小推车",
               "学步车", "玩具样车")
# 落地大件：本来就该摆地上给人试
FLOOR_DISPLAY = ("童车展示", "摇摇马", "儿童自行车", "滑梯")
# 货架类家具（note 必须写清架上摆什么）
SHELF_NAMES = ("货架", "老货柜", "中岛货架", "柜台")


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
        # 北墙一线：老货柜在西门边（镇店之宝），货架撑门面
        F("老货柜", 1, 1, 3, 1, "玻璃柜台 · 架上摆着镇店的旧货：拨浪鼓、铁皮青蛙、纸风车、木陀螺"),
        F("货架", 5, 1, 1, 2, "北墙货架 · 架上摆着新货：积木、拼图"),
        F("收银台", 6, 1, 3, 1, "前门旁 · 算盘与找零抽屉"),
        F("货架", 11, 1, 1, 2, "北墙货架 · 架上摆着新货：遥控车、电子小汽车"),
        F("货架", 13, 1, 2, 1, "北墙货架 · 架上摆着新货：塑料小家电、风扇"),
        F("货架", 16, 1, 2, 1, "北墙货架 · 架上摆着新货：文具盒、作业本、蜡笔"),
        F("货架", 18, 1, 2, 1, "北墙货架 · 架上摆着新货：气球、泡泡机"),
        # 东西墙
        F("货架", 1, 2, 1, 2, "西墙货架 · 架上摆着老货：陀螺、竹蜻蜓、弹弓"),
        F("货架", 19, 2, 1, 2, "东墙货架 · 架上摆着新货：滑板车、小推车"),
        # 中岛
        F("中岛货架", 7, 3, 1, 3, "店面中间的岛架 · 架上摆着新货：积木桶、拼图大盒"),
        F("货架", 1, 4, 1, 2, "西墙货架 · 架上摆着老货：纸风车、铁皮青蛙盒"),
        F("货架", 19, 4, 1, 2, "东墙货架 · 架上摆着新货：布娃娃、学步车"),
        # 落地大件（本来就该摆地上给人试骑）
        F("童车展示", 3, 6, 2, 1, "落地陈列的大件 · 折叠童车，摆在店里给人看"),
        F("摇摇马", 6, 6, 1, 1, "落地陈列的大件 · 摇摇马，孩子试骑"),
        F("儿童自行车", 13, 6, 2, 1, "落地陈列的大件 · 儿童自行车"),
        F("滑梯", 16, 6, 2, 1, "落地陈列的大件 · 小滑梯"),
        # 南墙一线（留出 (9,7)(10,7) 通账房那道门）
        F("货架", 1, 7, 2, 1, "南墙货架 · 架上摆着老货：拨浪鼓、竹蜻蜓"),
        F("货架", 4, 7, 2, 1, "南墙货架 · 架上摆着新货：蜡笔盒、拼图盒"),
        F("货架", 11, 7, 2, 1, "南墙货架 · 架上摆着新货：文具、泡泡机"),
        F("货架", 17, 7, 2, 1, "南墙货架 · 架上摆着新货：遥控车配件、气球"),
        # ── 里屋 x1..5,y9..14（沈家雇来看店的人的铺位）──
        F("单人床", 1, 9, 2, 1, "看店人的铺 · 沈家雇的人住这儿"),
        F("小桌", 4, 9, 2, 1, "看店人吃饭看账的地方"),
        F("被褥", 1, 10, 2, 1, "叠在床尾的旧被褥"),
        F("马扎", 4, 10, 1, 1, "小桌旁的马扎"),
        F("旧衣柜", 5, 12, 1, 2, "贴东墙"),
        F("脸盆架", 1, 13, 1, 1, "里屋西南角"),
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
        F("旧台灯", 12, 13, 1, 1, "桌上的旧台灯"),
        F("算盘盒", 12, 14, 1, 1, "装旧算盘的盒子"),
        # ── 仓库 x14..19,y9..14 ──
        F("货架", 14, 9, 1, 2, "西墙货架 · 架上摆着还没拆箱的存货"),
        F("货架", 19, 9, 1, 2, "东墙货架 · 架上摆着还没拆箱的存货"),
        F("货箱", 16, 9, 2, 1, "新到的玩具箱"),
        F("纸箱堆", 16, 10, 2, 1, "纸箱堆"),
        F("货箱", 15, 11, 2, 1, "存货 · 让开账房通仓库的门 (13,11)"),
        F("旧招牌板", 17, 12, 2, 1, "三代没换过的旧门板 · 靠在墙边"),
        F("拆封样品", 14, 13, 2, 1, "拆了包装的样品箱"),
        F("扫帚", 17, 13, 1, 1, "扫仓库的扫帚"),
        F("纸箱", 18, 14, 1, 1, "角落的纸箱"),
        F("水桶", 19, 14, 1, 1, "水桶"),
    ],
    "clue": [
        "店面北墙招牌小字「本店由沈氏物业出租」（A5 铁证链一环）",
        "账房账柜：周有田往来账可能在此（位置待定，未定论）",
    ],
    "story": "租的是沈家的楼，雇的是沈家的人；周家三代不知道替谁看店。",
    "note": ("屋本体 21×16 格 = 336×256 px（lot/wings 一致；旧 note 的「15×9」「15×11」均作废）。"
             "v3 全上架：店里的玩具不落地，小件货品全部并进货架/柜台的 note（架上摆着…），"
             "落地只留大件（童车/摇摇马/儿童自行车/滑梯）；美术那边只要多出几版不重样的"
             "货架贴图（架上带玩具）即可，可探索点从 83 收敛到 50 出头。"
             "店面整间 x1..19、y1..7（19×7），x9..10 留出入店通道；"
             "后排 y=9..14 = 里屋 x1..5 / 账房 x7..12 / 仓库 x14..19。"
             "街面朝北：前门（大门）开在北墙 (9,0)(10,0) 两格宽，"
             "招牌小字钉在店面北墙最西端 [1,0,2,1]；"
             "南墙 (16,15)(17,15) 后门通后巷进货，进的是仓库。"
             "账柜贴账房北墙 [11,8,2,1]——周有田往来账位置待定，未定论。"
             "货品新旧混搭：老货（拨浪鼓/铁皮青蛙/纸风车/陀螺/弹弓/竹蜻蜓）进老货柜与西墙货架，"
             "新货（积木/拼图/布娃娃/气球/遥控车/塑料小家电/文具盒）撑门面货架。"),
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

# ── 自检 4：尺寸必须是 21×16 ──
assert toyshop["lot"] == LOT, f"lot 必须是 {LOT}"
assert toyshop["wings"] == [WING], f"wings 必须是 {[WING]}"
assert (LOT[2] - LOT[0] + 1) == 21 and (LOT[3] - LOT[1] + 1) == 16, "尺寸不是 21×16"

# ── 自检 5：四间房（店面/里屋/账房/仓库），坐标固定 ──
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
for g, room in ((list(front)[0], "店面"), (list(back)[0], "仓库")):
    inner = (g[0], g[1] + 1) if g[1] == 0 else (g[0], g[1] - 1)
    owner = None
    for r in toyshop["rooms"]:
        if r[0] <= inner[0] <= r[2] and r[1] <= inner[1] <= r[3]:
            owner = r[4]
            break
    assert owner == room, f"门 {g} 内侧是「{owner}」，应该是「{room}」"

# ── 自检 8：玩具不落地 —— 小件货品只许出现在货架/柜台的 note 里 ──
for f in toyshop["furniture"]:
    if f["name"] in FLOOR_DISPLAY:
        continue
    for k in SMALL_GOODS:
        assert k not in f["name"], f"小件货品「{k}」不该单独占格当家具（应并进货架的 note）"
for f in toyshop["furniture"]:
    if f["name"] in SHELF_NAMES:
        assert "架上摆着" in f["note"], f"货架「{f['name']}」的 note 必须写清架上摆着什么东西"
# 店面里的货架要点明架上摆的具体货品（仓库的货架摆的是没拆箱的存货，不列具体玩具）
shop_rect = rm["店面"]
for f in toyshop["furniture"]:
    if f["name"] in SHELF_NAMES:
        x, y, w, h = f["rect"]
        in_shop = shop_rect[0] <= x and y >= shop_rect[1] and y + h - 1 <= shop_rect[3]
        if in_shop:
            assert any(k in f["note"] for k in SMALL_GOODS), \
                f"店面货架「{f['name']}」({f['rect']}) 的 note 要点明架上摆的货品"

# ── 自检 9：新旧混搭（老货当镇店之宝，新货撑门面）──
notes = " ".join(f["note"] for f in toyshop["furniture"])
for k in ("拨浪鼓", "铁皮青蛙", "纸风车", "陀螺", "弹弓", "竹蜻蜓"):
    assert k in notes, f"少了老货「{k}」"
for k in ("积木", "拼图", "布娃娃", "气球", "遥控车", "文具盒"):
    assert k in notes, f"少了新货「{k}」"
assert any("老货" in f["note"] for f in toyshop["furniture"]), "老货的 note 里要写明是老货"
assert any("新货" in f["note"] for f in toyshop["furniture"]), "新货的 note 里要写明是新货"

# ── 自检 10：年代红线（2026 年的村里小玩具店不该有的东西）──
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
