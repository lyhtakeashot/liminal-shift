# -*- coding: utf-8 -*-
"""shen_a4 沈家四合院 2001 —— 推倒重建（2026-11-21）。

【为什么重建】用户 m02594 指出旧稿两大硬伤，审核确认：
  1) 尺寸倒退：旧 A4 21×19=399格 < A3 28×21=588格（沈家应越建越大）；
  2) 结构丢项：没继承 A3 三翼，10 道门只剩 4 道，(3,7)/(17,7) 还是落在
     地板上的假门，24 格室内无房间覆盖、渲染成暗块。
  house-spec.md:180「全村最大的房子」那句话本身写错（旧稿被它带偏），不采信。

【重建口径】
  - 完整继承 shen_a3：三翼(28×21)/7 道 partitions/10 道 doors/16 格 demolished
    原样不动，51 件家具原位继承——「每代加一翼，旧翼不拆」(house-spec.md:196)。
  - 南边只加第四翼倒座 [0,21,28,7]（7 排），total 28×28=448×448px。
  - 院门从 A3 的 [13,20] 移到倒座南墙正中 [13,27]，朝大马路；
    倒座北墙开 3 门通内院：[7,21] 通西廊 / [13,21] 通天井 / [20,21] 通东廊。
  - 房间 = A3 14 间全留 + 倒座 3 间（门房/账房/客房）= 17 间。
  - 家具 = A3 51 件原位 + 倒座 16 件 = 67 件；5 条 clue 全保留。
  - 沈建国罪证落倒座账房：账桌◆改地质报告、保险柜◆锁改稿底本。

【自检（补 check_all 盲区）】家具不压墙/门/院门、不重叠、门四邻禁家具、
  房间不压墙、每道门原始格必须是墙（防假门）、A3 继承完整性。
"""
import copy
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")
data = json.load(open(DATA, encoding="utf-8"))
by_id = {h["id"]: h for h in data}
a3 = by_id["shen_a3"]
a4 = by_id["shen_a4"]

# ── 继承来源校验：A3 必须是完整的 28×21 三翼 + 10 门 ──
assert a3["lot"] == [0, 0, 27, 20], f"A3 lot 变了: {a3['lot']}"
assert len(a3["wings"]) == 3 and len(a3["doors"]) == 10, "A3 三翼/10门 不完整"
assert len(a3["furniture"]) == 51, "A3 家具不是 51 件，继承基线变了"


def F(name, rect, note, clue=False, zone="house", short=None):
    return {"name": name, "short": short or name, "rect": rect, "note": note,
            "clue": clue, "zone": zone, "yard_building": False}


# ── 结构：A3 原样继承 + 南加倒座 ──
a4["lot"] = [0, 0, 27, 27]                       # 28×28 格 = 448×448 px
a4["wings"] = copy.deepcopy(a3["wings"]) + [[0, 21, 28, 7]]   # 倒座 interior x1..26 y22..26
a4["partitions"] = copy.deepcopy(a3["partitions"]) + [
    [9, 22, 9, 26], [18, 22, 18, 26],            # 倒座三间：门房 x1..8 / 账房 x10..17 / 客房 x19..26
]
a4["doors"] = copy.deepcopy(a3["doors"]) + [
    [7, 21], [13, 21], [20, 21],                 # 倒座北墙三门通内院
]
a4["gate"] = [[13, 27]]                          # 院门移到倒座南墙正中，朝大马路
a4["demolished"] = copy.deepcopy(a3["demolished"])

# ── 房间：A3 14 间原样 + 倒座 3 间 ──
a4["rooms"] = copy.deepcopy(a3["rooms"]) + [
    [1, 22, 8, 26, "倒座·门房", "hall"],
    [10, 22, 17, 26, "倒座·账房", "account"],
    [19, 22, 26, 26, "倒座·客房", "bed"],
]

# ── 家具：A3 51 件原位 + 倒座 16 件 = 67 ──
a4["furniture"] = copy.deepcopy(a3["furniture"]) + [
    # 倒座·门房（x1..8 y22..26）· 外人进门先登记
    F("门房桌", [1, 22, 2, 1], "门房 · 来客登记桌"),
    F("椅",     [3, 22, 1, 1], "门房 · 门房椅"),
    F("储物柜", [1, 24, 1, 2], "门房 · 贴西墙，信件杂物"),
    F("衣帽架", [8, 22, 1, 2], "门房 · 贴东墙，来客挂衣"),
    F("鞋架",   [7, 26, 2, 1], "门房 · 进门换鞋"),
    # 倒座·账房（x10..17 y22..26）· 沈建国改地质报告处（罪证）
    F("算盘",   [11, 22, 1, 1], "账房 · 祖传算盘（记账成癖的延续）"),
    F("账桌",   [12, 23, 3, 1], "账房 · 沈建国在此改地质勘察报告，写『地下有暗河，不宜大开挖』，桩位绕开老井", clue=True),
    F("老板椅", [13, 24, 1, 1], "账房 · 真皮转椅"),
    F("电脑",   [15, 22, 1, 1], "账房 · 2001 台式电脑"),
    F("打印机", [15, 23, 1, 1], "账房 · 打印改好的报告"),
    F("保险柜", [10, 25, 1, 2], "账房 · 贴西墙，改稿底本锁在里面", clue=True),
    F("文件柜", [16, 22, 1, 2], "账房 · 贴东墙，土地登记表第二联（A4 拿到的那张）"),
    F("饮水机", [16, 25, 1, 1], "账房 · 2001 办公室标配"),
    # 倒座·客房（x19..26 y22..26）
    F("单人床", [19, 22, 1, 3], "客房 · 贴西墙"),
    F("衣柜",   [25, 22, 1, 3], "客房 · 贴东墙"),
    F("茶几",   [22, 24, 2, 1], "客房 · 会客茶几"),
]

a4["name"] = "沈家宅 · A4 2001（四合院 · 首富）"
a4["clue"] = [
    "四面围死：完整继承 A3 三翼（28 格正房 + 东西两厢 + 抄手游廊 + 10 道门），南边只加第四翼倒座——28×28 格，院从『半』变『全』，沈家越建越大。",
    "院门从 A3 的南墙正中移到倒座南墙正中 [13,27]，朝大马路；倒座西头添门房，外人进门先过门房登记——首富家的体面壳。",
    "倒座账房的账桌与保险柜（◆）：沈建国在这里改了地质勘察报告，写下『地下有暗河，不宜大开挖』，桩位绕开老井那片地——一具尸体都没碰。",
    "北堂里祖宗牌位与红木八仙桌仍在，大屏彩电和组合音响同屋摆着——旧规矩与新排场挤在一间，沈建国体面斯文的来路。",
    "天井里是石桌、石榴树、鱼缸、葡萄架、松桩盆景——大户人家的排场，2001 年不摆农具；A3 的家具一件没挪。",
]
a4["story"] = ("沈建国一代（36 岁，体面、斯文、手上干净，真心觉得自己是个好人）。"
               "他没杀人：找关系改地质勘察报告，写『地下有暗河，不宜大开挖』，桩基绕开老井那片地。")
a4["note"] = ("四合院 28×28（448×448px）：完整继承 A3 三翼（正房 28×12 + 西厢 10×10 + 东厢 10×10，"
              "7 道隔墙/10 道门/16 格拆墙原样），南加第四翼倒座 28×7。院门从 [13,20] 移倒座正中 [13,27] 朝大马路；"
              "倒座北墙开三门（[7,21] 通西廊/[13,21] 通天井/[20,21] 通东廊），分门房/账房/客房。"
              "67 件家具＝A3 的 51 件原位 + 倒座新增 16 件；罪证（账桌◆/保险柜◆）落账房。")


# ── 自检（补 check_all 盲区）──
def build_grid():
    spec = importlib.util.spec_from_file_location("gah", os.path.join(HERE, "gen_all_houses.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build_grid


grid = build_grid()(a4)
X0, Y0, X1, Y1 = a4["lot"]

# 1) 家具越界/压墙/压门/重叠
occupied = {}
for f in a4["furniture"]:
    x, y, w, h = f["rect"]
    assert X0 <= x and x + w <= X1 + 1 and Y0 <= y and y + h <= Y1 + 1, \
        f"越界: {f['name']} {f['rect']}"
    for j in range(y, y + h):
        for i in range(x, x + w):
            c = grid[j - Y0][i - X0]
            assert c not in ("#", "D", "G"), \
                f"压墙/压门: {f['name']} 占 ({i},{j}) 网格='{c}'"
            assert (i, j) not in occupied, \
                f"重叠: {f['name']} 与 {occupied[(i,j)]} 在 ({i},{j})"
            occupied[(i, j)] = f["name"]

# 2) 门四邻禁家具
for (dx, dy) in a4["doors"] + a4["gate"]:
    for nx, ny in ((dx-1, dy), (dx+1, dy), (dx, dy-1), (dx, dy+1)):
        assert (nx, ny) not in occupied, \
            f"堵门: 门({dx},{dy}) 邻格({nx},{ny}) 被「{occupied[(nx,ny)]}」占据"

# 3) 房间不压墙
for room in a4["rooms"]:
    rx0, ry0, rx1, ry1, rname = room[:5]
    for j in range(ry0, ry1 + 1):
        for i in range(rx0, rx1 + 1):
            if X0 <= i <= X1 and Y0 <= j <= Y1:
                assert grid[j - Y0][i - X0] != "#", \
                    f"房间「{rname}」压墙 ({i},{j})"

# 4) 门落墙（防假门）：清空 doors/gate 后看原始格必须是墙
bare = dict(a4)
bare["doors"] = []
bare["gate"] = []
raw_grid = build_grid()(bare)
for (dx, dy) in a4["doors"] + a4["gate"]:
    raw = raw_grid[dy - Y0][dx - X0]
    assert raw == "#", f"假门: 门({dx},{dy}) 原始格='{raw}' 不是墙"

# 5) A3 继承完整性
assert a4["wings"][:3] == a3["wings"], "A3 三翼没原样继承"
assert a4["doors"][:10] == a3["doors"], "A3 10 门没原样继承"
assert a4["demolished"] == a3["demolished"], "A3 拆墙格没原样继承"
assert a4["furniture"][:51] == a3["furniture"], "A3 51 家具没原位继承"
assert len(a4["clue"]) == 5, "clue 不是 5 条"

json.dump(data, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("shen_a4 REBUILT: houses", len(data), "lot", a4["lot"],
      "wings", len(a4["wings"]), "doors", len(a4["doors"]),
      "rooms", len(a4["rooms"]), "furniture", len(a4["furniture"]),
      "clue", len(a4["clue"]), "— A3 三翼/10门/51家具 原样继承 + 倒座")
