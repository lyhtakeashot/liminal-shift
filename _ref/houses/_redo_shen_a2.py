# -*- coding: utf-8 -*-
"""shen_a2 重做（v5，按用户 m03053）：

用户: 「这个房子还不够大，而且这样的富豪（应该已经算富豪了）屋子里有厕所了吧」

改动：
  1) 放大：19×15 → 23×17 格（304×240 → 368×272 px）
  2) 加室内净房（厕所）：正房东端的独立小间，放恭桶 + 屏风 + 洗手水盆，
     不再用院子里的茅房。1951 年富户室内便溺用恭桶，隔小间，有屏风挡。

形状仍是 L 向右旋转 90°（横在顶、竖在左，空位在右下）。
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")
data = json.load(open(DATA, encoding="utf-8"))
by_id = {h["id"]: h for h in data}
a2 = by_id["shen_a2"]

a2["lot"] = [0, 0, 22, 16]          # 23×17 格 = 368×272 px
a2["wings"] = [
    [0, 0, 23, 12],   # 正房：横贯北边，x 0..22, y 0..11
    [0, 11, 10, 6],   # 西厢：从左侧向南伸，x 0..9, y 11..16
]
a2["partitions"] = [
    [6, 1, 6, 5],       # 长辈房 | 主卧
    [12, 1, 12, 5],     # 主卧 | 子女房
    [18, 1, 18, 5],     # 子女房 | 净房
    [1, 6, 21, 6],      # 卧室排 | 堂屋
    [1, 11, 9, 11],     # 堂屋 | 西厢
    [5, 12, 5, 15],     # 灶间 | 仓房
]
a2["doors"] = [[3, 6], [9, 6], [16, 6], [20, 6], [3, 11], [9, 13]]
a2["gate"] = [[16, 11]]
a2["rooms"] = [
    [1, 1, 5, 5, "长辈房", "bed"],
    [7, 1, 11, 5, "主卧", "bed"],
    [13, 1, 17, 5, "子女房", "bed"],
    [19, 1, 21, 5, "净房", "toilet"],
    [1, 7, 21, 10, "堂屋", "hall", "top"],
    [1, 12, 4, 15, "灶间", "kitchen"],
    [6, 12, 8, 15, "仓房", "store"],
    [10, 12, 22, 16, "院子", "yard"],
]
a2["furniture"] = [
    # 长辈房（沈万山夫妇 · 真《水簿》在他身上，不在这间屋里）
    {"name": "双人床", "short": "双人床", "rect": [1, 1, 3, 3], "note": "长辈房 · 沈万山夫妇｜3×3 富家床", "clue": False, "zone": "house", "yard_building": False},
    {"name": "柜", "short": "柜", "rect": [5, 1, 1, 2], "note": "长辈房 · 贴东墙", "clue": False, "zone": "house", "yard_building": False},
    {"name": "书桌", "short": "书桌", "rect": [5, 4, 1, 1], "note": "长辈房 · 贴东墙 · 沈万山记账那张；真本他随身带着", "clue": True, "zone": "house", "yard_building": False},
    # 主卧（沈守业夫妇）
    {"name": "双人床", "short": "双人床", "rect": [7, 1, 3, 3], "note": "主卧 · 沈守业夫妇｜3×3", "clue": False, "zone": "house", "yard_building": False},
    {"name": "衣柜", "short": "衣柜", "rect": [11, 1, 1, 2], "note": "主卧 · 贴东墙", "clue": False, "zone": "house", "yard_building": False},
    {"name": "凳", "short": "凳", "rect": [11, 4, 1, 1], "note": "主卧 · 窗下", "clue": False, "zone": "house", "yard_building": False},
    # 子女房（沈德昌 11 岁）
    {"name": "单人床", "short": "单人床", "rect": [13, 1, 2, 1], "note": "子女房 · 沈德昌 11 岁｜横向贴北墙", "clue": False, "zone": "house", "yard_building": False},
    {"name": "书桌", "short": "书桌", "rect": [17, 1, 1, 2], "note": "子女房 · 贴东墙", "clue": False, "zone": "house", "yard_building": False},
    {"name": "柜", "short": "柜", "rect": [13, 5, 2, 1], "note": "子女房 · 贴南墙", "clue": False, "zone": "house", "yard_building": False},
    # 净房（室内厕所 · 富户才有的待遇）
    {"name": "屏风", "short": "屏风", "rect": [19, 1, 1, 2], "note": "净房 · 挡视线", "clue": False, "zone": "house", "yard_building": False},
    {"name": "恭桶", "short": "恭桶", "rect": [20, 1, 1, 1], "note": "净房 · 木桶内衬灰，每日倒", "clue": False, "zone": "house", "yard_building": False},
    {"name": "凳", "short": "凳", "rect": [19, 4, 1, 1], "note": "净房 · 更衣", "clue": False, "zone": "house", "yard_building": False},
    {"name": "水盆", "short": "水盆", "rect": [21, 4, 1, 1], "note": "净房 · 洗手", "clue": False, "zone": "house", "yard_building": False},
    # 堂屋西墙祭祖角：牌位在北端，条案（供桌）接在南边，一字贴西山墙
    {"name": "牌位", "short": "牌位", "rect": [1, 7, 1, 1], "note": "堂屋西山墙北端 · 木牌，面向东", "clue": False, "zone": "house", "yard_building": False},
    {"name": "条案", "short": "条案", "rect": [1, 8, 1, 3], "note": "堂屋西山墙 · 竖向长条桌，摆瓶、座钟、镜", "clue": False, "zone": "house", "yard_building": False},
    # 八仙桌 + 四条长凳 = 4×4 组合，左上角 (11,7)；桌子居中 (12,8)-(13,9)，四角留走道
    {"name": "八仙桌", "short": "八仙桌", "rect": [12, 8, 2, 2], "note": "堂屋 · 待客 · 组合中心", "clue": False, "zone": "house", "yard_building": False},
    {"name": "长凳", "short": "长凳", "rect": [12, 7, 2, 1], "note": "八仙桌 · 北", "clue": False, "zone": "house", "yard_building": False},
    {"name": "长凳", "short": "长凳", "rect": [12, 10, 2, 1], "note": "八仙桌 · 南", "clue": False, "zone": "house", "yard_building": False},
    {"name": "长凳", "short": "长凳", "rect": [11, 8, 1, 2], "note": "八仙桌 · 西", "clue": False, "zone": "house", "yard_building": False},
    {"name": "长凳", "short": "长凳", "rect": [14, 8, 1, 2], "note": "八仙桌 · 东", "clue": False, "zone": "house", "yard_building": False},
    # 灶间（西厢 · 从堂屋进）
    {"name": "置物台", "short": "置物台", "rect": [1, 12, 1, 1], "note": "灶间 · 菜板菜刀", "clue": False, "zone": "house", "yard_building": False},
    {"name": "灶台", "short": "灶台", "rect": [4, 12, 1, 2], "note": "灶间 · 竖向贴东墙", "clue": False, "zone": "house", "yard_building": False},
    {"name": "水缸", "short": "水缸", "rect": [1, 15, 1, 1], "note": "灶间 · 蓄水", "clue": False, "zone": "house", "yard_building": False},
    # 仓房（西厢 · 从院子进）
    {"name": "粮囤", "short": "粮囤", "rect": [6, 12, 2, 2], "note": "仓房 · 谷", "clue": False, "zone": "house", "yard_building": False},
    {"name": "粮囤", "short": "粮囤", "rect": [8, 15, 1, 1], "note": "仓房 · 麦", "clue": False, "zone": "house", "yard_building": False},
    # 院子（右下）
    {"name": "鸡笼", "short": "鸡笼", "rect": [11, 12, 2, 1], "note": "院子 · 养鸡", "clue": False, "zone": "yard", "yard_building": False},
    {"name": "水缸", "short": "水缸", "rect": [11, 16, 1, 1], "note": "院子 · 蓄水", "clue": False, "zone": "yard", "yard_building": False},
    {"name": "柴堆", "short": "柴堆", "rect": [13, 16, 1, 1], "note": "院子 · 柴", "clue": False, "zone": "yard", "yard_building": False},
    {"name": "农具架", "short": "农具架", "rect": [19, 16, 2, 1], "note": "院子 · 锄镰", "clue": False, "zone": "yard", "yard_building": False},
]
a2["name"] = "沈家宅 · A2 1951（L 形 · 正房+西厢）· 青瓦"
a2["note"] = ("占地 23×17 格 = 368×272 px。L 向右旋转 90°：正房 23×12（四间卧室 + 横贯全宽的堂屋）"
              "横在北，西厢 10×6（灶间/仓房）从左侧向南伸，右下 13×5 是院子。"
              "正房东端设室内净房（恭桶+屏风），1951 年村里只有这一家有。")
a2["clue"] = [
    "比 A1 大一圈：加西厢（灶间+仓房）一翼，青瓦取代土坯。",
    "正房东端有室内净房——村里只有这一家有厕所。",
    "沈万山仍住长辈房——真《水簿》在他身上，不在屋里。",
]
a2["story"] = "沈守业一代（36 岁）当家；1951 填井就在这一年。沈万山（父）仍活着，此后不再记事。"

json.dump(data, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("shen_a2 v5 written: lot", a2["lot"], "wings", a2["wings"], "rooms", len(a2["rooms"]))
