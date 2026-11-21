# -*- coding: utf-8 -*-
"""shen_a3 重做（2026-11-20，用户纠正「打通连廊没说把空间让给灶间和储物室」）。

用户正确口径：
  - 粮仓/客房设定删掉后，各自空间变成「连廊」并与堂屋打通；
  - **灶间保持原尺寸 x1..4**（不许吞并西边粮仓空间）；
  - **储物间保留原尺寸 x23..26**（酒坛+木箱），不是假连廊；
  - 西连廊 = 原粮仓空间 x5..8，东连廊 = 原客房空间 x19..22，
    都是空旷走廊，廊下只放纳凉陈设（藤椅/盆景/灯笼），不放储物家具。

结构：正房 28×12 + 西厢 10×10 + 东厢 10×10 + 8×9 天井三面凹廊；
       连廊去掉 x=5 / x=22 两道竖墙与堂屋打通。
灶间：大件摆明面（煤炉◆/铁锅/蒸笼/瓷盆/水池），小件（锅铲/淘米盆）收进碗柜，
      唯一明面组合是「案板插菜刀」。
储物间：酒坛+木箱。天井：石榴树+石桌+花盆。
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")
data = json.load(open(DATA, encoding="utf-8"))
by_id = {h["id"]: h for h in data}
a3 = by_id["shen_a3"]

# ── 结构：正房加长 + 两厢加深 + 中间大天井 + 凹廊 + 连廊打通 ──
a3["lot"] = [0, 0, 27, 20]                       # 28×21 格
a3["wings"] = [
    [0, 0, 28, 12],   # 正房：横 28 格（+5），进深 12
    [0, 11, 10, 10],  # 西厢：向南伸 10 格
    [18, 11, 10, 10], # 东厢：向南伸 10 格
]
a3["partitions"] = [
    [6, 1, 6, 5],       # 长辈房 | 主卧
    [12, 1, 12, 5],     # 主卧 | 子女房
    [18, 1, 18, 5],     # 子女房 | 净房
    [22, 1, 22, 5],     # 净房 | 书房
    [1, 6, 26, 6],      # 卧室排 | 堂屋
    [5, 12, 5, 19],     # 灶间 | 西连廊（用户 11/20「之前那两面墙放回来」）
    [22, 12, 22, 19],   # 东连廊 | 储物间（同上，放回来）
]
a3["doors"] = [
    [3, 6], [9, 6], [15, 6], [20, 6], [24, 6],  # 卧室排 → 堂屋
    [3, 11], [19, 11],                           # 堂屋 → 西厢(灶间) / 东厢(储物)
    [13, 11],                                    # 堂屋 → 天井
    [5, 13], [22, 13],                           # 灶间→西连廊 / 东连廊→储物间（墙放回来，门也放回来）
]
a3["gate"] = [[13, 20]]                          # 天井南面正中
# 用户 11/20：「连廊到庭院是没墙的，把此处的两面墙拆掉」
# 西连廊|天井的 x=9 墙、天井|东连廊的 x=18 墙（y12..19）拆掉，成为露天可走庭院格。
# build_grid() 读 demolished 白名单，把这些边界墙渲染成庭院空格（不影响其他房屋）。
a3["demolished"] = (
    [[x, y] for x in (9, 18) for y in range(12, 20)] +          # 连廊↔天井两面墙
    [[x, 20] for x in list(range(5, 9)) + list(range(19, 23))]  # 连廊南端外墙：西 x5..8、东 x19..22
)
a3["rooms"] = [
    [1, 1, 5, 5, "长辈房", "bed"],
    [7, 1, 11, 5, "主卧", "bed"],
    [13, 1, 17, 5, "子女房", "bed"],
    [19, 1, 21, 5, "净房", "toilet"],
    [23, 1, 26, 5, "书房", "account"],
    [1, 7, 26, 10, "堂屋", "hall", "top"],
    [1, 12, 4, 19, "灶间", "kitchen"],            # 保持原尺寸 x1..4（不吞并西连廊）
    [23, 12, 26, 19, "储物间", "store"],          # 保留原尺寸 x23..26（酒坛+木箱）
    [6, 12, 8, 19, "西连廊", "hall"],             # x=5 墙放回来，西连廊从 x6 起（墙不算房间）
    [19, 12, 21, 19, "东连廊", "hall"],           # x=22 墙放回来，东连廊到 x21 止
    [10, 12, 10, 19, "凹廊·西", "hall"],
    [11, 12, 16, 12, "凹廊·北", "hall"],
    [17, 12, 17, 19, "凹廊·东", "hall"],
    [11, 13, 16, 19, "天井", "yard"],
]

# ── 家具：1976 小富豪，卫浴/煤炉/连廊庭院陈设，无农具 ──
a3["furniture"] = [
    # 长辈房
    {"name": "双人床", "short": "大床", "rect": [1, 1, 3, 3],
     "note": "长辈房 · 3×3 富家床", "clue": False, "zone": "house", "yard_building": False},
    {"name": "柜", "short": "柜", "rect": [5, 1, 1, 2],
     "note": "长辈房 · 贴东墙", "clue": False, "zone": "house", "yard_building": False},
    # 主卧
    {"name": "双人床", "short": "大床", "rect": [7, 1, 3, 3],
     "note": "主卧 · 3×3", "clue": False, "zone": "house", "yard_building": False},
    {"name": "衣柜", "short": "衣柜", "rect": [11, 1, 1, 2],
     "note": "主卧 · 贴东墙", "clue": False, "zone": "house", "yard_building": False},
    {"name": "凳", "short": "凳", "rect": [11, 4, 1, 1],
     "note": "主卧 · 窗下", "clue": False, "zone": "house", "yard_building": False},
    # 子女房
    {"name": "单人床", "short": "单人床", "rect": [13, 1, 2, 1],
     "note": "子女房 · 横向贴北墙", "clue": False, "zone": "house", "yard_building": False},
    {"name": "书桌", "short": "书桌", "rect": [17, 1, 1, 2],
     "note": "子女房 · 贴东墙", "clue": False, "zone": "house", "yard_building": False},
    {"name": "柜", "short": "柜", "rect": [13, 5, 2, 1],
     "note": "子女房 · 贴南墙", "clue": False, "zone": "house", "yard_building": False},
    # 净房（独立卫浴）
    {"name": "屏风", "short": "屏风", "rect": [19, 1, 1, 2],
     "note": "净房 · 挡视线", "clue": False, "zone": "house", "yard_building": False},
    {"name": "水冲蹲便器", "short": "蹲便器", "rect": [20, 1, 1, 2],
     "note": "净房 · 高水箱蹲坑，瓷砖贴面（1976 干部宿舍/体面户配置，非旱厕恭桶）", "clue": False, "zone": "house", "yard_building": False},
    {"name": "洗手盆", "short": "洗手盆", "rect": [21, 1, 1, 1],
     "note": "净房 · 搪瓷洗手盆，盆前墙上挂镜（镜子不另占格）", "clue": False, "zone": "house", "yard_building": False},
    {"name": "水盆", "short": "水盆", "rect": [21, 4, 1, 1],
     "note": "净房 · 洗漱", "clue": False, "zone": "house", "yard_building": False},
    # 书房（横向加长多出来的一间）：书架靠左墙(x=22)，书桌在书架右侧
    {"name": "书架", "short": "书架", "rect": [23, 1, 1, 2],
     "note": "书房 · 靠左墙（净房|书房那道墙）", "clue": False, "zone": "house", "yard_building": False},
    {"name": "书桌", "short": "书桌", "rect": [24, 1, 2, 1],
     "note": "书房 · 书架右侧，粮站站长的账/信", "clue": False, "zone": "house", "yard_building": False},
    {"name": "椅", "short": "椅", "rect": [24, 3, 1, 1],
     "note": "书房 · 书桌前", "clue": False, "zone": "house", "yard_building": False},
    {"name": "书架", "short": "书架", "rect": [26, 1, 1, 2],
     "note": "书房 · 靠右墙", "clue": False, "zone": "house", "yard_building": False},
    {"name": "书架", "short": "书架", "rect": [23, 3, 1, 2],
     "note": "书房 · 左侧书架之南", "clue": False, "zone": "house", "yard_building": False},
    {"name": "书架", "short": "书架", "rect": [26, 3, 1, 2],
     "note": "书房 · 右侧书架之南", "clue": False, "zone": "house", "yard_building": False},
    # 堂屋（祭祖角 + 八仙桌会客）
    {"name": "牌位", "short": "牌位", "rect": [1, 7, 1, 1],
     "note": "堂屋西山墙北端", "clue": False, "zone": "house", "yard_building": False},
    {"name": "条案", "short": "条案", "rect": [1, 8, 1, 3],
     "note": "堂屋西山墙 · 竖向长条桌", "clue": False, "zone": "house", "yard_building": False},
    {"name": "八仙桌", "short": "八仙桌", "rect": [11, 8, 2, 2],
     "note": "堂屋 · 会客中心 · 西移 1 格给门(13,11)让净空", "clue": False, "zone": "house", "yard_building": False},
    {"name": "长凳", "short": "长凳", "rect": [11, 7, 2, 1], "note": "八仙桌 · 北", "clue": False, "zone": "house", "yard_building": False},
    {"name": "长凳", "short": "长凳", "rect": [11, 10, 2, 1], "note": "八仙桌 · 南", "clue": False, "zone": "house", "yard_building": False},
    {"name": "长凳", "short": "长凳", "rect": [10, 8, 1, 2], "note": "八仙桌 · 西", "clue": False, "zone": "house", "yard_building": False},
    {"name": "长凳", "short": "长凳", "rect": [13, 8, 1, 2], "note": "八仙桌 · 东", "clue": False, "zone": "house", "yard_building": False},
    # 灶间：大件摆明面（x=1 一列），小件（锅铲/淘米盆）收进碗柜，
    # 唯一明面组合是案板插菜刀。避开门(3,11)下邻(3,12)、门(5,13)左邻(4,13)。
    {"name": "蜂窝煤炉", "short": "煤炉", "rect": [1, 12, 1, 1],
     "note": "灶间 · 1976 镇上家庭烧蜂窝煤（大件明面）", "clue": True, "zone": "house", "yard_building": False},
    {"name": "铁锅", "short": "铁锅", "rect": [1, 13, 1, 1],
     "note": "灶间 · 章丘铁锅，70 年代家用主炊具（大件明面）", "clue": False, "zone": "house", "yard_building": False},
    {"name": "蒸笼", "short": "蒸笼", "rect": [1, 14, 1, 1],
     "note": "灶间 · 竹制蒸笼（大件明面）", "clue": False, "zone": "house", "yard_building": False},
    {"name": "水池", "short": "水池", "rect": [1, 15, 1, 1],
     "note": "灶间 · 自来水池（大件明面）", "clue": False, "zone": "house", "yard_building": False},
    {"name": "搪瓷盆", "short": "瓷盆", "rect": [1, 16, 1, 1],
     "note": "灶间 · 洗菜搪瓷盆（大件明面）", "clue": False, "zone": "house", "yard_building": False},
    {"name": "碗柜", "short": "碗柜", "rect": [1, 17, 1, 2],
     "note": "灶间 · 锅铲/淘米盆等小件统一收进柜", "clue": False, "zone": "house", "yard_building": False},
    {"name": "案板", "short": "案板", "rect": [3, 15, 2, 1],
     "note": "灶间 · 案板上插着菜刀（唯一明面的小件组合）", "clue": False, "zone": "house", "yard_building": False},
    # 储物间（x23..26）：从最南端 y=19 起整齐码放，两排到底，留过道。
    # 避开门(22,13)右邻(23,13)——该格必须留空。
    {"name": "木箱", "short": "木箱", "rect": [23, 19, 1, 1],
     "note": "储物间 · 木箱（南排）", "clue": False, "zone": "house", "yard_building": False},
    {"name": "木箱", "short": "木箱", "rect": [24, 19, 1, 1],
     "note": "储物间 · 木箱（南排）", "clue": False, "zone": "house", "yard_building": False},
    {"name": "酒坛", "short": "酒坛", "rect": [25, 19, 1, 1],
     "note": "储物间 · 陶瓷酒坛（南排，非欧洲橡木桶）", "clue": False, "zone": "house", "yard_building": False},
    {"name": "酒坛", "short": "酒坛", "rect": [26, 19, 1, 1],
     "note": "储物间 · 陶瓷酒坛（南排）", "clue": False, "zone": "house", "yard_building": False},
    {"name": "木箱", "short": "木箱", "rect": [23, 17, 1, 1],
     "note": "储物间 · 木箱（北排）", "clue": False, "zone": "house", "yard_building": False},
    {"name": "木箱", "short": "木箱", "rect": [24, 17, 1, 1],
     "note": "储物间 · 木箱（北排）", "clue": False, "zone": "house", "yard_building": False},
    {"name": "酒坛", "short": "酒坛", "rect": [25, 17, 1, 1],
     "note": "储物间 · 陶瓷酒坛（北排）", "clue": False, "zone": "house", "yard_building": False},
    {"name": "酒坛", "short": "酒坛", "rect": [26, 17, 1, 1],
     "note": "储物间 · 陶瓷酒坛（北排）", "clue": False, "zone": "house", "yard_building": False},
    # 西连廊（原粮仓 x5..8）：空旷走廊，只摆廊下纳凉陈设，不放储物家具
    {"name": "藤椅", "short": "藤椅", "rect": [7, 12, 1, 1],
     "note": "西连廊 · 藤椅纳凉", "clue": False, "zone": "house", "yard_building": False},
    {"name": "盆景", "short": "盆景", "rect": [8, 17, 1, 1],
     "note": "西连廊 · 松桩盆景", "clue": False, "zone": "house", "yard_building": False},
    # 东连廊（原客房 x19..22）：空旷走廊，与堂屋打通，只摆廊下陈设
    {"name": "灯笼", "short": "灯笼", "rect": [20, 12, 1, 1],
     "note": "东连廊 · 廊下挂灯（避开门(19,11)净空）", "clue": False, "zone": "house", "yard_building": False},
    {"name": "藤椅", "short": "藤椅", "rect": [21, 17, 1, 1],
     "note": "东连廊 · 藤椅纳凉（x=22 墙放回来，从 x21 退开）", "clue": False, "zone": "house", "yard_building": False},
    # 凹廊（П 形回廊，开口朝南）：庭院陈设，无农具
    {"name": "藤椅", "short": "藤椅", "rect": [10, 19, 1, 1],
     "note": "凹廊·西 · 纳凉", "clue": False, "zone": "yard", "yard_building": False},
    {"name": "盆景", "short": "盆景", "rect": [14, 12, 1, 1],
     "note": "凹廊·北 · 松桩", "clue": False, "zone": "yard", "yard_building": False},
    {"name": "灯笼", "short": "灯笼", "rect": [17, 19, 1, 1],
     "note": "凹廊·东 · 廊下挂灯", "clue": False, "zone": "yard", "yard_building": False},
    # 天井（中庭）
    {"name": "石桌", "short": "石桌", "rect": [13, 13, 2, 1],
     "note": "天井 · 石凳", "clue": False, "zone": "yard", "yard_building": False},
    {"name": "庭树", "short": "树", "rect": [13, 15, 2, 2],
     "note": "天井 · 一棵石榴树，大户人家庭院的排场", "clue": False, "zone": "yard", "yard_building": False},
    {"name": "花盆", "short": "花盆", "rect": [11, 19, 1, 1],
     "note": "天井 · 石榴", "clue": False, "zone": "yard", "yard_building": False},
    {"name": "花盆", "short": "花盆", "rect": [16, 19, 1, 1],
     "note": "天井 · 月季", "clue": False, "zone": "yard", "yard_building": False},
]

a3["name"] = "沈家宅 · A3 1976（凹形带连廊）· 灰瓦两厢 · 粮站站长家"
a3["clue"] = [
    "在 A2 的 L 形基础上继续加长：正房横 28 格（比 A2 多 5）、两厢各向南伸 10 格——每代加一翼、旧翼只加不减。",
    "天井 8×9，三面围一圈凹廊（西/北/东，开口朝南），种一棵石榴树——大户人家的抄手游廊，不是穷院子的空地。",
    "连廊与堂屋、灶间、储物间之间都留着墙（灶间|西连廊 x=5、东连廊|储物 x=22，各有门）；连廊与天井之间那两面墙已拆，廊下直接通到露天庭院。",
    "灶间大件摆明面（煤炉◆/铁锅/蒸笼/瓷盆/水池），小件锅铲、淘米盆收进碗柜，只有案板插菜刀是明面组合——1976 年的厨房，无柴火灶。",
]
a3["story"] = ("沈德昌一代（36 岁，粮站站长，三个儿子）。真本从粮站地基出土后，"
                "他看到祖父沈万山的手记，当场决定把知情人一起封进地基——真相本身就是凶器。")
a3["note"] = ("屋本体 凹形 28×21：正房 28×12 + 西厢 10×10 + 东厢 10×10，中间 8×9 天井三面围凹廊"
               "（西/北/东，开口朝南），院门开南面，堂屋 (13,11) 开门直通天井。"
               "西厢：灶间 x1..4（大件厨具明面，小件收碗柜）—墙 x=5（门(5,13)）—西连廊 x6..8；"
               "东厢：东连廊 x19..21—墙 x=22（门(22,13)）—储物间 x23..26（酒坛木箱）。"
               "连廊↔天井的 x=9/x=18 墙已拆，廊下直通露天庭院。"
               "1976 小富豪：独立卫浴（瓷砖净房配高水箱水冲蹲便器，非旱厕恭桶）、蜂窝煤炉、石榴树，无农具。")

# ── 自检：门四邻格不许摆家具（用户 11/20 明确要求：堵门现象不能再发生）──
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

json.dump(data, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("shen_a3 written: houses", len(data), "lot", a3["lot"],
      "wings", len(a3["wings"]), "rooms", len(a3["rooms"]), "furniture", len(a3["furniture"]))
