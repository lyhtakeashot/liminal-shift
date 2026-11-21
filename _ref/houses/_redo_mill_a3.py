# -*- coding: utf-8 -*-
"""mill_a3 新建（2026-11-20）：磨坊→粮站 A3 1976，第 14 栋。

用户口径（11/20 拍板）：
  - 屋本体照抄 A2 磨坊（15×9），不另起新地基；北侧原样；
  - 南扩晒谷场：lot 从 A2 的 18×11 向南扩到 18×15（y0..14），水泥晒场翻晒/排队用，
    场内一座 1970s 土圆仓（安乡 1973 年全县 240 栋的典型形制）；
    老井/水泥封层/弃置石磨留在晒场中央，叙事更顺。
  - 三处案发线索格上图：老井（1951 填埋盖石板）、水泥封层（三层，方石匠在下面）、
    墙基暗龛（状态从 A2 空龛改为真本已出土）。

粮站职能考据（11/20）：粮站只管收购/销售/调运/储存，不加工粮食；厅仓打通（拆 y3 横墙东段
x8..13，含原门(8,3)）：收购厅北排摆验粮台（取样铁管）/风车/磅秤，溜筛/木跳板+记码牌/便民服务台
移到粮仓北口整粮入库；粮仓另摆箩筐、麻袋、验粮器、晒席，账房加算盘/单据柜。
老石磨从收购厅挪到晒场角落废弃（刻字保留，A4 搬去超市门厅）。

story 链（docs/story.md §4.3 / §5.4 / §5.6）：
  磨坊一直盖在老井上 → A3 改建粮站挖地基挖到老井 → 真《水簿》从账房暗龛出土
  → 沈德昌认出是祖父沈万山的手记 → 把看见的外乡石匠方师傅封进地基，倒三层水泥。
  「真相本身就是凶器」。
"""
import json
import os
import sys

HERE_FOR_IMPORT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE_FOR_IMPORT)
from gen_all_houses import build_grid

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")
data = json.load(open(DATA, encoding="utf-8"))
by_id = {h["id"]: h for h in data}
src = by_id["mill_a2"]  # 同址改建：结构照抄 A2 磨坊

a3 = {
    "id": "mill_a3",
    "name": "粮站 · A3 1976（原磨坊同址改建）· 加害方根",
    # 屋本体照抄 A2（wings 不动）；南扩晒谷场：lot 底边 y8→14
    "lot": [src["lot"][0], src["lot"][1], src["lot"][2], 14],
    "wings": [list(w) for w in src["wings"]],
    "partitions": [list(p) for p in src["partitions"]],
    # 厅仓打通后原门(8,3)多余：连门一起拆平，只留账房↔厅的门(7,2)
    "doors": [list(d) for d in src["doors"] if d != [8, 3]],
    "gate": [list(g) for g in src["gate"]],
    # A3 改建：拆 y3 横墙东段 x8..13（含原门格(8,3)），收购厅和粮仓完全打通；x14 外墙不动
    "demolished": [[x, 3] for x in range(8, 14)],
    # 房间照抄 A2 坐标（已验证不压墙），只改用途名
    "rooms": [
        [3, 1, 6, 2, "粮站账房", "account", "top"],
        [8, 1, 13, 2, "收购厅", "mill", "top"],
        [3, 4, 13, 7, "粮仓", "store", "top"],
    ],
    "furniture": [
        {"name": "墙基暗龛", "short": "暗龛", "rect": [1, 1, 1, 2],
         "note": "墙后(西) · A2 空龛，A3 真《水簿》油布包从这里出土，龛已空", "clue": True, "zone": "house", "yard_building": False},
        {"name": "账桌", "short": "账桌", "rect": [3, 1, 1, 2],
         "note": "墙前(东) · 假《水簿》仍摆着 A1-A3", "clue": True, "zone": "house", "yard_building": False},
        {"name": "凳", "short": "凳", "rect": [4, 2, 1, 1],
         "note": "账房 · 账桌前", "clue": False, "zone": "house", "yard_building": False},
        # 收购厅 x8..13,y1..2：北排验粮→过磅，南排 y2 留空当过道（门(7,2) 邻格必须空；(8,3) 原门已拆）。
        # A3 拆 y3 横墙东段 x9..13 后，整粮入库三件（溜筛/跳板/服务台）移到粮仓北排 y4 靠入库口：
        # 厅里验粮过磅、仓口整粮入库，流程顺，收购厅也不再挤。
        {"name": "验粮台+取样铁管", "short": "验粮台", "rect": [8, 1, 2, 1],
         "note": "收购厅北墙 · 检验员用带槽铁管插粮袋取样，牙磕验干湿", "clue": False, "zone": "house", "yard_building": False},
        {"name": "风车", "short": "风车", "rect": [10, 1, 2, 1],
         "note": "收购厅 · 扬谷去杂，不合格的粮食先过风车", "clue": False, "zone": "house", "yard_building": False},
        {"name": "磅秤", "short": "磅秤", "rect": [12, 1, 2, 1],
         "note": "收购厅北墙 · 大磅秤过磅记码（司磅员）", "clue": False, "zone": "house", "yard_building": False},
        {"name": "溜筛", "short": "溜筛", "rect": [9, 4, 1, 1],
         "note": "粮仓北口 · 筛除杂质整粮工具（拆墙后从收购厅南排移来）", "clue": False, "zone": "house", "yard_building": False},
        {"name": "木跳板+记码牌", "short": "跳板", "rect": [10, 4, 2, 1],
         "note": "粮仓北口 · 挑粮上仓的木跳板，旁挂入库记数码单牌（拆墙后移来）", "clue": False, "zone": "house", "yard_building": False},
        {"name": "便民服务台", "short": "服务台", "rect": [12, 4, 2, 1],
         "note": "入库口旁 · 凉茶桶+防暑药，交粮排队农民歇脚处（拆墙后移来）", "clue": False, "zone": "house", "yard_building": False},
        {"name": "粮囤", "short": "粮囤", "rect": [8, 6, 2, 2],
         "note": "粮仓 · 收购来的粮食", "clue": False, "zone": "house", "yard_building": False},
        {"name": "粮囤", "short": "粮囤", "rect": [11, 5, 2, 2],
         "note": "粮仓 · 收购来的粮食", "clue": False, "zone": "house", "yard_building": False},
        {"name": "单据柜+算盘", "short": "单据柜", "rect": [4, 1, 2, 1],
         "note": "账房北墙 · 单据柜横放靠墙，柜面上摆算盘（一体道具，美术可见，不做交互）", "clue": False, "zone": "house", "yard_building": False},
        {"name": "箩筐", "short": "箩筐", "rect": [11, 7, 1, 1],
         "note": "粮仓 · 装粮箩筐", "clue": False, "zone": "house", "yard_building": False},
        {"name": "麻袋", "short": "麻袋", "rect": [12, 7, 1, 1],
         "note": "粮仓 · 装粮麻袋", "clue": False, "zone": "house", "yard_building": False},
        {"name": "验粮器", "short": "验粮器", "rect": [13, 6, 1, 1],
         "note": "粮仓 · 扦样验粮器具", "clue": False, "zone": "house", "yard_building": False},
        {"name": "晒席", "short": "晒席", "rect": [5, 7, 2, 1],
         "note": "粮仓 · 晒谷席，收购的粮食先摊开验晒", "clue": False, "zone": "house", "yard_building": False},
        # 晒谷场（南扩 y9..14，水泥坪）：土圆仓 + 旧物三件套，全部归院子组
        {"name": "土圆仓", "short": "土圆仓", "rect": [2, 11, 3, 3],
         "note": "晒谷场西北 · 草泥结构土圆仓，1970s 粮站标配（安乡 1973 年全县 240 栋），储粮用", "clue": False, "zone": "yard", "yard_building": False},
        # 石磨：粮站不加工粮食，A3 改建时从收购厅挪到晒谷场角落露天废弃；A4 拆粮站时捡走搬去超市门厅（跨帧道具）
        {"name": "弃置石磨", "short": "石磨", "rect": [11, 9, 2, 2],
         "note": "上磨盘刻「沈氏丰源·一九五七」；粮站不磨面，改建时挪到晒谷场角落废弃，A4 拆粮站才搬去超市门厅", "clue": True, "zone": "yard", "yard_building": False},
        # 案发线索格：磨坊院内旧井（村里的吃水井，路为它绕弯）；1951 填埋盖石板，A3 挖地基翻出
        {"name": "老井", "short": "老井", "rect": [6, 10, 1, 1],
         "note": "晒谷场中央旧井 · 1926 路为它绕弯；1951 填井盖石板（陆敬之在下面），A3 挖地基挖到", "clue": True, "zone": "yard", "yard_building": False},
        {"name": "水泥封层", "short": "封层", "rect": [8, 10, 1, 1],
         "note": "晒谷场 · 三层水泥，外乡石匠方师傅看见挖到井，被沈德昌封在这里", "clue": True, "zone": "yard", "yard_building": False},
    ],
    "clue": [
        "磨坊改粮站，屋本体照抄 A2 不另起地基；南侧扩建水泥晒谷场，加一座 1970s 土圆仓。",
        "账房墙基暗龛：A2 还是空龛，A3 真《水簿》从这里出土；沈德昌认出是祖父沈万山的手记。",
        "晒谷场中央旧井：1926 年村里的吃水井，路为它绕弯；1951 沈守业填井盖石板（陆敬之在下面），A3 挖地基挖到。",
        "石匠方师傅看见挖到井，被沈德昌封进地基倒三层水泥——真相本身就是凶器。",
        "粮站只管收购/储存/调运，不加工：验粮台/风车/磅秤是主角具；老石磨挪到晒场角落废弃，上磨盘刻「沈氏丰源·一九五七」。",
        "A3 改建拆掉收购厅与粮仓之间的 y3 横墙东段（x8..13，含原门(8,3)一并拆平），厅仓打通：厅内验粮过磅、仓口整粮入库，不再挤在两排格里。",
    ],
    "story": ("沈德昌一代（36 岁，粮站站长）。磨坊改建粮站、南扩晒谷场挖地基，挖到院内老井；"
              "真《水簿》从账房暗龛出土，他认出是祖父沈万山的手记，"
              "当场决定把看见的外乡石匠方师傅一起封进地基，倒三层水泥。"),
    "note": ("屋本体 15×9（照抄 A2 磨坊）：账房 x3..6 / 收购厅 x8..13 / 粮仓 x3..13；"
             "南侧新扩水泥晒谷场 y9..14（土圆仓+翻晒场地）；"
             "A2 空暗龛 A3 真本出土；晒场旧井（1951 填埋盖石板）+ 三层水泥封尸格；"
             "粮站不加工：收购厅北排验粮台/风车/磅秤，拆 y3 横墙东段 x8..13（含原门(8,3)）厅仓打通，"
             "溜筛/跳板/服务台移到粮仓北口整粮入库，仓内摆箩筐/麻袋/验粮器/晒席；"
             "老石磨挪到晒场角落废弃（A4 搬去超市门厅）。磨坊 A1-A2 → 粮站 A3 → 超市 A4-A5。"),
}

# 幂等：已存在则替换，否则追加（第 14 栋）
if "mill_a3" in by_id:
    idx = next(i for i, h in enumerate(data) if h["id"] == "mill_a3")
    data[idx] = a3
else:
    data.append(a3)

# 自检：门/院门四邻格不许摆家具（沿用 shen_a3 教训：check_all 只保证一侧通行，抓不到堵门正对）
def _furniture_at(gx, gy):
    for f in a3["furniture"]:
        x, y, w, h = f["rect"]
        if x <= gx < x + w and y <= gy < y + h:
            return f["name"]
    return None

for (dx, dy) in a3["doors"] + a3["gate"]:
    for nx, ny in ((dx - 1, dy), (dx + 1, dy), (dx, dy - 1), (dx, dy + 1)):
        hit = _furniture_at(nx, ny)
        assert hit is None, f"堵门！门({dx},{dy}) 邻格({nx},{ny}) 被家具「{hit}」占据"

# 自检 2：家具不许压墙（单据柜 [1,4] 曾整个塞进墙格没被 check_all 抓到）
_grid = build_grid(a3)
for f in a3["furniture"]:
    x, y, w, h = f["rect"]
    for gy in range(y, y + h):
        for gx in range(x, x + w):
            c = _grid[gy][gx]
            assert c not in ("#", "D", "G"), f"家具「{f['name']}」格({gx},{gy})压在墙/门/院门「{c}」上"

json.dump(data, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("mill_a3 written: houses", len(data), "lot", a3["lot"],
      "rooms", len(a3["rooms"]), "furniture", len(a3["furniture"]))
