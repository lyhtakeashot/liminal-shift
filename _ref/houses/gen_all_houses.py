"""
全部建筑 · 占地拆解图生成器 v2
====================================================================
用户 m01438 反馈：
  1) 墙板呢，怎么全都去掉了  -> 加回内部隔墙(partitions)，墙格画顶部高光(墙板感)
  2) 还有茅房                -> 加回院子 + 院子家具(茅房/水缸/柴堆)
  3) 不要生产完整的大图      -> 不再输出 all_houses.png 总览拼图
  4) 要内容详细的占地拆解图，以 straight_rooms.png 为例
     -> 布局/配色/家具标名/家具清单 完全照搬 straight_rooms.py

输出（用户 m01912）：按时间节点分文件夹，文件名带帧号
  _ref/art/A1_1926/ _ref/art/A2_1951/ _ref/art/A3_1976/ _ref/art/A4_2001/ _ref/art/A5_2026/
跨帧建筑每帧一张（mill_a1/mill_a2、market_a4/market_a5 等）；生成器本体仍留 _ref/houses/。
坐标：lot=(x0,y0,x1,y1) 覆盖整个占地(含院子)，从 0 开始。
字符：# 墙(有墙板高光) / . 室内地面 / D 房门 / G 院门 / 空格 院子
"""
import os
import json
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "art")  # _ref/art/
FRAME_DIR = {"A1": "A1_1926", "A2": "A2_1951", "A3": "A3_1976",
             "A4": "A4_2001", "A5": "A5_2026"}
FRAME_OF_ID = {
    "lu_house": "A1", "mill_a1": "A1", "shen_a1": "A1", "zhou_house": "A1",
    "mill_a2": "A2", "shen_a2": "A2", "lu_a2": "A2", "zhou_a2": "A2", "shen_a3": "A3", "mill_a3": "A3", "zhou_a3": "A3", "lu_a3": "A3",
    "shen_a4": "A4", "market": "A4", "zhou_a4": "A4", "zheng_a4": "A4",
    "toyshop": "A5", "school": "A5",
}
TILE = 16
SCALE = 40
FONTS = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]


def font(size):
    for p in FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


C = {
    "bg": "#191814", "text": "#e6dfd0", "gray": "#9a9284", "key": "#e0bb74",
    "grid": "#333029", "wall": "#8c6b4a", "wall_top": "#c9a878",
    "door": "#e0b25a", "gate": "#9a6a3a", "measure": "#7fa8c8",
    "player": "#e8543f", "player_edge": "#ffd9c4", "lot": "#a8905a",
    "yard": "#3b3a2e", "furn": "#c8b48f", "furn_edge": "#e8d7b2",
    "clue": "#d98b45", "yard_furn": "#a9b58a", "yard_edge": "#d3dfae",
    # 废墟态（ruin:true，如 A3 陆家地基）：断砖残墙基 / 夯土地基 / 荒草
    "ruin_wall": "#7a6a55", "ruin_base": "#544c3a", "ruin_grass": "#6f7d4c",
    "room": {"bed": "#9c8468", "hall": "#cbb997", "store": "#8d9a6f",
             "kitchen": "#bdd0b0", "account": "#a8c0d0", "yard": "#3b3a2e",
             "shop": "#b99aa6", "class": "#9dbacd", "mill": "#b5a878",
             "toilet": "#9aa8a8"},
}

STD = ("家具标准：人 1×2 ｜ 双人床 2×2(穷)/3×3(富) ｜ 单人床 2×1 横向贴墙 ｜ "
       "柜/灶台 1×2 ｜ 一格 16×16 px ｜ 橙框=可检视线索")


def F(name, x, y, w, h, note="", clue=False, short=None, zone="house", yard_building=False):
    return dict(name=name, short=short or name, rect=(x, y, w, h), note=note,
                clue=clue, zone=zone, yard_building=yard_building)


# rooms = (x0,y0,x1,y1, 名称, 配色key)
# partitions = [(x1,y1,x2,y2)] 内部隔墙线段(水平或垂直)，保证房间之间真的有墙板
# doors = [(x,y)] 房门(须落在墙上)；gate=[(x,y)] 院门/大门
HOUSES = [
    dict(id="lu_house", name="陆家（一字形）· A1 1926 · 受害方",
         lot=(0, 0, 19, 9), wings=[(0, 0, 15, 8)],
         partitions=[(5, 1, 5, 6), (10, 1, 10, 6), (11, 4, 13, 4)],
         doors=[(5, 5), (10, 2), (10, 5)], gate=[(6, 7)],
         rooms=[(1, 1, 4, 6, "夫妻房", "bed"), (6, 1, 9, 6, "堂屋", "hall"),
                (11, 1, 13, 3, "长辈房", "bed"), (11, 5, 13, 6, "灶间", "kitchen")],
         furniture=[
             F("双人床", 1, 1, 2, 2, "穷家 2×2"), F("衣柜", 4, 1, 1, 2),
             F("旧木箱", 2, 5, 1, 1, "夫妻房 · 可检视线索", clue=True, short="木箱"),
             F("八仙桌", 7, 2, 2, 2), F("祖宗牌位", 8, 6, 2, 1, "横向贴南墙", short="牌位"),
             F("单人床", 11, 1, 2, 1, "横向靠北墙"), F("柜", 13, 1, 1, 2, "贴东墙"),
             F("灶台", 13, 5, 1, 2, "竖向靠东墙"),
             F("茅房", 16, 1, 3, 2, "屋外独立茅房", zone="yard", yard_building=True),
             F("茅坑", 17, 1, 1, 1, "茅房内", zone="yard"),
             F("水缸", 16, 4, 1, 1, "院子 · 接雨水", zone="yard"),
             F("柴堆", 18, 4, 1, 1, "院子", zone="yard"),
         ],
         clue=["旧木箱（夫妻房）= 可检视线索（文本待定）"],
         story="1926 三口人：老太爷 / 陆文(19岁,这年溺亡) / 儿媳(怀陆敬之,未出生)。屋外独立茅房。",
         note="屋本体 15×8；占地 20×10 含东侧院子(可走可搜证)。"),

    # ===== A1 1926 磨坊：无暗龛 / 无掩饰墙 / 无挪动砖 / 全旧砖 =====
    # 与 A2 同尺寸（lot/wings 原样复用），只改 partitions/furniture/rooms。
    # 真《水簿》此时在沈万山身上随身天天记，账房只摆假《水簿》。
    # 隐藏设计（用户 m02464）：账房外框/门位置与 A2 对齐——竖墙 x=7→x=4、账房门(7,2)→(4,2)、
    # 大厅门(8,3)→(5,3)；账桌挪进 alcove 位(1,1)-(1,2)、凳(2,1)。这样进账房看不出 A2 空龛的改动。
    # 石磨挪到(7,1)（视觉核心是石磨不是墙），大厅平时少人进出，进一步辅助隐藏暗龛。
    # y=3 长横墙保持与 A2 一致：x=1..4 账房段不能留空（用户 m02483 纠正：这条墙从没要求拆）。
    dict(id="mill_a1", name="磨坊 · A1 1926（旧砖、无暗龛）· 加害方根",
         lot=(0, 0, 17, 10), wings=[(0, 0, 15, 9)],
         # A1 结构性隔墙：账房/大厅竖墙 x=4、y=3 整条横墙（账房段(1,3)-(4,3)+大厅段(5,3)-(13,3)）
         # 没有暗龛隔墙(2,1)-(2,2)、没有(1,4)-(2,7)掩饰墙
         partitions=[(4, 1, 4, 2), (1, 3, 4, 3), (5, 3, 13, 3)],
         doors=[(4, 2), (5, 3)], gate=[(7, 8)],
         # 颜色贴合新墙：账房 x=1..3,y=1..2；y=3 是墙不填房间色；大厅 x=5..13,y=1..2
         rooms=[(1, 1, 3, 2, "账房", "account", "top"), (1, 4, 13, 7, "仓场", "store", "top"),
                (5, 1, 13, 2, "磨盘大厅", "mill", "top")],
         furniture=[
             F("账桌", 1, 1, 1, 2, "假《水簿》A1-A2；真本在沈万山身上（占日后暗龛位）", clue=True, short="账桌"),
             F("凳", 2, 1, 1, 1, "账房 · 账桌旁"),
             F("石磨", 7, 1, 2, 2, "挪到大厅西侧当视觉核心；上磨盘后刻「沈氏丰源·一九五七」", clue=True, short="石磨"),
             F("粮囤", 8, 6, 2, 2, "仓储"), F("粮囤", 11, 5, 2, 2, "仓储"),
         ],
         clue=["A1 全旧砖、无暗龛：真《水簿》沈万山随身天天记（1951 停笔）",
               "账桌占日后暗龛位、石磨当视觉核心：进账房看不出 A2 空龛的房型改动"],
         story="1926 陆文溺亡那年，磨坊是沈家的；账房只有一本给别人看的账。",
         note="屋本体 15×9；A1 无暗龛/掩饰墙/挪动砖、全旧砖；账房外框与 A2 对齐辅助隐藏暗龛。"),

    # ===== A2 1951 磨坊：新砌空暗龛 + 掩饰墙 + 挪动砖（当前 mill.png 这版）=====
    dict(id="mill_a2", name="磨坊 → 粮站 · A2 1951（新砖空暗龛）· 加害方根",
         lot=(0, 0, 17, 10), wings=[(0, 0, 15, 9)],
         # 账房一排：暗龛(1,1-2)真本 | 竖墙(2,1-2) | 账桌(3,1-2)假本 | 凳(4,1)
         # 竖隔墙由 (5,1)-(5,3) 挪到 (7,1)-(7,2)，账房向东扩到 x=6，大厅缩到 x=8-13
         # 旧门 (4,3) 补墙封死；账房门挪到竖墙上的 (7,2)；大厅门由 (9,3) 挪到 (8,3)
         # (1,4)-(2,7) 整块填墙掩饰暗龛；x=5 下半段墙已删，上下仓场直接通
         partitions=[(7, 1, 7, 2), (4, 3, 4, 3), (1, 3, 3, 3), (2, 1, 2, 2), (5, 3, 13, 3),
                     (1, 4, 2, 4), (1, 5, 2, 5), (1, 6, 2, 6), (1, 7, 2, 7)],
         doors=[(7, 2), (8, 3)], gate=[(7, 8)],
         # 颜色分区贴合墙：横墙 y=3 分南北，竖墙 x=7 分账房/大厅
         # 仓场+仓储合并为一个大仓场(3,4)-(13,7)，绿=store
         # 三个房间名均带第 7 项 "top" = 画在矩形上边缘之外、层级在家具之后（防被家具盖住）
         rooms=[(1, 1, 6, 2, "账房", "account", "top"), (3, 4, 13, 7, "仓场", "store", "top"),
                (8, 1, 13, 2, "磨盘大厅", "mill", "top")],
         furniture=[
             F("墙基暗龛", 1, 1, 1, 2, "墙后(西) · 真《水簿》油布包 A3 出土", clue=True, short="暗龛"),
             F("账桌", 3, 1, 1, 2, "墙前(东) · 假《水簿》A1-A2", clue=True, short="账桌"),
             F("凳", 4, 1, 1, 1, "账房 · 账桌旁"),
             F("石磨", 11, 1, 2, 2, "上磨盘刻「沈氏丰源·一九五七」", clue=True, short="石磨"),
             F("粮囤", 8, 6, 2, 2, "仓储"), F("粮囤", 11, 5, 2, 2, "仓储"),
         ],
         clue=["账房缩到左上角、加一堵墙：墙后墙基暗龛藏真《水簿》(A3 出土)，墙前账桌摆假《水簿》(A1-A2)",
               "石磨上磨盘后搬去超市门厅；磨坊正下方＝老井(A3 挖到→封水泥)"],
         story="磨坊一直盖在井上面——A3 挖地基挖到井，是三次封尸的起点。",
         note="屋本体 15×9；账房缩左上角、新增隔墙分暗龛/账桌前后；磨坊 A1-A2 → 粮站 A3。"),

    dict(id="shen_a1", name="沈家宅 · A1 1926（一字形）· 土坯发迹",
         lot=(0, 0, 19, 9), wings=[(0, 0, 15, 8)],
         partitions=[(5, 1, 5, 6), (10, 1, 10, 6), (11, 4, 13, 4)],
         doors=[(5, 5), (10, 2), (10, 5)], gate=[(6, 7)],
         rooms=[(1, 1, 4, 6, "正房", "bed"), (6, 1, 9, 6, "堂屋", "hall"),
                (11, 1, 13, 3, "少东房", "bed"), (11, 5, 13, 6, "灶间", "kitchen")],
         furniture=[
             F("双人床", 1, 1, 2, 2, "穷家 2×2"), F("衣柜", 4, 1, 1, 2),
             F("八仙桌", 7, 2, 2, 2), F("祖宗牌位", 8, 6, 2, 1, short="牌位"),
             F("凳", 6, 2, 1, 1, "堂屋 · 八仙桌旁"), F("凳", 9, 2, 1, 1, "堂屋"),
             F("凳", 6, 4, 1, 1, "堂屋"), F("凳", 9, 4, 1, 1, "堂屋"),
             F("单人床", 12, 1, 2, 1, "少东房 · 横向贴北墙"),
             F("书桌", 13, 2, 1, 1, "少东房"), F("书架", 12, 3, 2, 1, "少东房 · 横向"),
             F("小衣柜", 11, 3, 1, 1, "少东房 · 由 1×2 缩为 1×1"),
             F("灶台", 13, 5, 1, 2),
             F("茅房", 16, 1, 3, 2, "屋外独立茅房", zone="yard", yard_building=True),
             F("茅坑", 17, 1, 1, 1, "茅房内", zone="yard"),
             F("水缸", 16, 4, 1, 1, "院子 · 接雨水", zone="yard"),
             F("柴堆", 18, 4, 1, 1, "院子", zone="yard"),
         ],
         clue=["沈家起家形态；比陆家略好，仍是土坯。"],
         story="沈万山此时是磨坊主。此地 A5 全拆建超市。",
         note="屋本体 15×8；占地 20×10 含东侧院子；A5 全拆建超市。"),

    dict(id="shen_a2", name="沈家宅 · A2 1951（L 形）· 青瓦",
         lot=(0, 0, 16, 13), wings=[(0, 0, 15, 8), (9, 5, 8, 9)],
         partitions=[(6, 1, 6, 5), (10, 9, 16, 9)],
         doors=[(6, 3), (12, 9)], gate=[(7, 7)],
         rooms=[(1, 1, 5, 4, "主卧", "bed"), (7, 1, 13, 4, "子女房", "bed"),
                (1, 5, 5, 6, "堂屋", "hall"), (10, 6, 16, 8, "灶间", "kitchen"),
                (10, 10, 16, 12, "储物", "store")],
         furniture=[
             F("双人床", 1, 1, 3, 3, "富家 3×3"), F("衣柜", 4, 1, 1, 2),
             F("八仙桌", 3, 5, 2, 2), F("牌位", 5, 5, 2, 1),
             F("子女床", 10, 1, 2, 2), F("灶台", 15, 6, 1, 2), F("粮囤", 14, 11, 2, 2),
         ],
         clue=["加右翼：灶间+储物；出现 3×3 大床(富家)。"],
         story="沈守业一代；1951 填井就在这一年。",
         note="屋本体 L 形 17×14；每代加一翼、旧翼不拆。"),

    dict(id="shen_a3", name="沈家宅 · A3 1976（凹形）· 灰瓦两厢",
         lot=(0, 0, 18, 14), wings=[(0, 0, 19, 7), (0, 4, 6, 11), (13, 4, 6, 11)],
         partitions=[(9, 1, 9, 4), (1, 9, 4, 9), (14, 9, 17, 9)],
         doors=[(9, 3), (2, 9), (15, 9)], gate=[(9, 0)],
         rooms=[(6, 1, 17, 4, "北堂", "hall"), (1, 5, 4, 13, "西厢", "bed"),
                (14, 5, 17, 13, "东厢", "bed"), (6, 6, 12, 13, "天井", "yard")],
         furniture=[
             F("八仙桌", 7, 1, 3, 2, "北堂"), F("牌位", 11, 1, 2, 1),
             F("大床", 1, 6, 3, 3, "西厢"), F("柜", 4, 6, 1, 2),
             F("大床", 14, 6, 3, 3, "东厢"), F("书案", 14, 12, 2, 1),
             F("水缸", 8, 12, 1, 1, "天井", zone="yard"),
         ],
         clue=["天井＝两厢围出的半院；阶级写在面积上。真《水簿》A3 出土。"],
         story="沈德昌一代；真本出土后他决定把知情人封进地基。",
         note="屋本体 凹形 19×15；两厢围半院。"),

    dict(id="shen_a4", name="沈家宅 · A4 2001（四合院）· 首富",
         lot=(0, 0, 20, 18),
         wings=[(0, 0, 21, 7), (0, 4, 6, 12), (15, 4, 6, 12), (0, 14, 21, 5)],
         partitions=[(9, 1, 9, 5), (1, 9, 4, 9), (17, 9, 20, 9)],
         doors=[(10, 6), (3, 7), (17, 7), (10, 14)], gate=[(10, 18)],
         rooms=[(6, 1, 20, 5, "北堂", "hall"), (1, 5, 4, 13, "西厢", "bed"),
                (17, 5, 20, 13, "东厢", "bed"), (6, 15, 20, 17, "倒座·账房", "account"),
                (6, 7, 14, 13, "天井", "yard")],
         furniture=[
             F("八仙桌", 5, 1, 3, 2), F("牌位", 11, 1, 2, 1),
             F("大床", 1, 9, 3, 3, "西厢"), F("衣柜", 4, 7, 1, 2),
             F("大床", 17, 9, 3, 3, "东厢"), F("书案", 17, 12, 2, 1),
             F("账桌", 10, 15, 3, 1, "倒座账房"), F("保险柜", 16, 15, 1, 2),
             F("水缸", 9, 12, 1, 1, zone="yard"),
         ],
         clue=["倒座设账房；四面围死，院从『半』变『全』。"],
         story="沈建国一代；他改了地质报告，桩基绕开老井。",
         note="屋本体 四合院 21×19；天井居中。"),

    dict(id="market", name="超市 · A4 在建 / A5 营业 · 洗白",
         lot=(0, 0, 20, 13), wings=[(0, 0, 21, 14)],
         partitions=[(1, 4, 19, 4), (14, 5, 14, 12), (6, 9, 6, 12)],
         doors=[(10, 4), (14, 8), (6, 10)], gate=[(9, 13), (10, 13), (11, 13)],
         rooms=[(6, 1, 13, 3, "门厅", "hall"), (1, 5, 13, 8, "营业大厅", "shop"),
                (15, 5, 19, 8, "收银", "account"), (15, 9, 19, 12, "仓库", "store"),
                (1, 9, 5, 12, "办公室", "account")],
         furniture=[
             F("上磨盘", 9, 1, 2, 2, "刻「沈氏丰源·一九五七」", clue=True, short="上磨盘"),
             F("收银台", 15, 6, 3, 1),
             F("货架", 2, 5, 1, 3), F("货架", 5, 5, 1, 3),
             F("货架", 8, 5, 1, 3), F("货架", 11, 5, 1, 3),
             F("文件柜", 2, 10, 1, 2, "土地登记表第二联位置待定", clue=True, short="文件柜"),
             F("货箱", 16, 10, 2, 2),
         ],
         clue=["门厅上磨盘(铁证) / 办公室文件柜=土地登记表第二联(待定)",
               "门外十字路口圆形沥青补丁＝井口(井在车道正下方)"],
         story="压在磨坊/粮站/老井原址上；桩位绕开老井那片地。",
         note="屋本体 21×14；A4 在建、A5 营业。"),

    dict(id="zhou_house", name="周家 · 长工房 · 帮凶方（穷）",
         lot=(0, 0, 11, 5), wings=[(0, 0, 8, 5)],
         partitions=[(4, 1, 4, 3)],
         doors=[(4, 3)], gate=[(2, 4)],
         rooms=[(1, 1, 3, 3, "卧室兼客厅", "bed"),
                (5, 1, 6, 3, "灶间", "kitchen")],
         furniture=[
             F("单人床", 1, 1, 1, 2, "竖向贴西墙 (1,1)-(1,2)"),
             F("小桌", 2, 1, 2, 1, "贴北墙 (2,1)-(3,1) · 抽屉藏周有田往来账(位置待定)", clue=True, short="小桌"),
             F("凳", 3, 2, 1, 1, "卧室兼客厅 · (3,2)"),
             F("衣柜", 1, 3, 1, 1, "卧客一体 · 贴西墙 (1,3)", short="衣柜"),
             F("置物台", 5, 1, 1, 1, "放菜板菜刀 · 贴柴火灶", short="置物台"),
             F("柴火灶", 6, 1, 1, 1, "1×1 一口锅 · 灶间北侧", short="柴火灶"),
             F("茅房", 9, 1, 3, 2, "屋外独立茅房", zone="yard", yard_building=True),
             F("茅坑", 10, 1, 1, 1, "茅房内", zone="yard"),
             F("水缸", 9, 4, 1, 1, "院子 · 接雨水", zone="yard"),
             F("柴堆", 10, 4, 1, 1, "院子", zone="yard"),
         ],
         clue=["小桌抽屉＝周有田往来账(位置待定)；周有田记了 24 年账没说一个字。"],
         story="独居长工；进门就是卧室兼客厅；灶间 2×2 围墙；三家唯一延续到 2026 的旁支。",
         note="屋本体 (0,0)-(8,4) 含墙；卧室兼客厅 3×3、灶间 2×2 围墙；占地 12×6 含东侧院子。"),

    dict(id="toyshop", name="玩具店 · A5 2026 · 周家曾孙",
         lot=(0, 0, 14, 8), wings=[(0, 0, 15, 9)],
         partitions=[(1, 5, 13, 5), (10, 6, 10, 7)],
         doors=[(7, 5), (10, 6)], gate=[(7, 8)],
         rooms=[(1, 1, 13, 4, "店面", "shop"), (1, 6, 9, 7, "柜台", "account"),
                (11, 6, 13, 7, "仓库", "store")],
         furniture=[
             F("招牌小字", 6, 1, 2, 1, "「本店由沈氏物业出租」", clue=True, short="招牌"),
             F("玩具架", 2, 2, 1, 3), F("玩具架", 5, 2, 1, 3),
             F("玩具架", 9, 2, 1, 3), F("玩具架", 12, 2, 1, 3),
             F("柜台", 2, 6, 3, 1),
             F("账柜", 11, 6, 2, 1, "周有田往来账待定", clue=True, short="账柜"),
             F("货箱", 13, 6, 1, 2),
         ],
         clue=["招牌小字「本店由沈氏物业出租」(A5 铁证链一环)",
               "账柜：周有田往来账(待定)"],
         story="租的是沈家的楼，雇的是沈家的人；周家三代不知道替谁看店。",
         note="屋本体 15×9。"),

    dict(id="school", name="小学 · A5 2026 · 沈明远捐建",
         lot=(0, 0, 20, 11), wings=[(0, 0, 21, 12)],
         partitions=[(1, 4, 19, 4), (1, 8, 19, 8)],
         doors=[(10, 4), (5, 4), (15, 4), (10, 8)], gate=[(9, 11), (10, 11)],
         rooms=[(6, 1, 14, 3, "门厅", "hall"), (1, 5, 9, 7, "教室一", "class"),
                (11, 5, 19, 7, "教室二", "class"), (11, 9, 19, 10, "办公室", "account")],
         furniture=[
             F("「周」界碑", 1, 10, 2, 1, "嵌围墙,字磨掉一半", clue=True, short="界碑"),
             F("课桌", 3, 5, 2, 1), F("课桌", 6, 5, 2, 1), F("课桌", 3, 7, 2, 1),
             F("讲台", 5, 2, 3, 1),
             F("课桌", 13, 5, 2, 1), F("课桌", 16, 5, 2, 1), F("讲台", 15, 2, 3, 1),
             F("办公桌", 12, 9, 3, 1),
         ],
         clue=["围墙嵌半块「周」界碑，字磨掉一半(身份反转佐证)。"],
         story="沈明远剪彩的地方；他什么都不知道。",
         note="屋本体 21×12。"),
]


# ===== 唯一真相源 = houses_data.json =====
# 上面的 HOUSES 内联数据只是初始种子；只要 houses_data.json 存在，生成/check 一律读它。
# 编辑器（editor.html + editor_server.py）改的就是这个 JSON 文件。
DATA_PATH = os.path.join(HERE, "houses_data.json")
if os.path.exists(DATA_PATH):
    with open(DATA_PATH, "r", encoding="utf-8") as _f:
        HOUSES = json.load(_f)


def export_seed():
    """把内联种子导出成 JSON（仅在 JSON 不存在/要重置时用）。"""
    with open(DATA_PATH, "w", encoding="utf-8") as _f:
        json.dump(HOUSES, _f, ensure_ascii=False, indent=2)
    print("exported seed", DATA_PATH, len(HOUSES))


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

    # JSON 加载后坐标是 list（不可哈希），转 tuple 才能进 set
    dset = set(tuple(d) for d in hs["doors"])
    gset = set(tuple(g) for g in hs.get("gate", []))
    # 数据驱动的「拆墙」白名单：连廊↔天井之间要拆掉的边界墙格（如 shen_a3 的 x=9/x=18）。
    # 没有 demolished 字段的房屋不受影响。拆墙格底色分两种：
    #   - 两侧都是室内（原内隔墙，如 mill_a3 厅仓打通）→ 恢复室内地板 '.'，别画成深绿院子；
    #   - 一侧临院/天井/外墙（如 shen_a3 连廊↔天井）→ 恢复露天庭院空格 ' '。
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
            elif c in part or is_wall(i, j):
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
            return f["name"]
    return None


def auto_player_at(hs, grid):
    """讲解图主角站位：整个占地右下角的第一个可走格（脚格+头顶格都不是墙/门/院门，且无家具）。
    从底行往上、每行从右往左扫；优先院子空格' '（占地最右下角空地），找不到才退回室内'.'。"""
    X0, Y0, X1, Y1 = hs["lot"]

    def walkable(i, j):
        if not (X0 <= i <= X1 and Y0 <= j <= Y1):
            return False
        ch = grid[j - Y0][i - X0]
        return ch in (".", " ") and not occupied(hs, i, j)

    def ok(i, j):
        # 讲解图主角只作尺寸参照、且设定上能穿墙：脚格 (i,j) 不站墙/门/家具即可，
        # 头顶格 (i,j-1) 即使是屋墙也接受——保证主角能落在占地最右下角（如磨坊 (17,9)-(17,10)）
        return walkable(i, j)

    # 优先院子空格(' ')：主角统一站整个占地最右下角的空地；找不到院子才退回室内('.')
    for prefer in (" ", "."):
        for j in range(Y1, Y0, -1):
            for i in range(X1, X0, -1):
                if not (X0 <= i <= X1 and Y0 <= j <= Y1):
                    continue
                if grid[j - Y0][i - X0] == prefer and ok(i, j):
                    return (i, j)
    # 极端兜底：任一可走格
    for j in range(Y1, Y0, -1):
        for i in range(X1, X0, -1):
            if walkable(i, j):
                return (i, j)
    return (X0 + 1, Y0 + 1)


def draw_label(d, bx, by, bw, bh, short, clue=False):
    if bw >= 2:
        d.text((bx + bw / 2, by + bh / 2), short,
               font=font(14 if bh >= 2 else 12), fill="#3a1c08" if clue else "#3a2c1c",
               anchor="mm")
    elif bh >= 2:
        for i, ch in enumerate(short):
            d.text((bx + bw / 2, by + bh * (i + 1) / (len(short) + 1)), ch,
                   font=font(12), fill="#3a1c08" if clue else "#3a2c1c", anchor="mm")
    else:
        d.text((bx + bw / 2, by + bh / 2), short,
               font=font(11 if len(short) <= 2 else 9),
               fill="#3a1c08" if clue else "#3a2c1c", anchor="mm")


def render(hs):
    X0, Y0, X1, Y1 = hs["lot"]
    gw, gh = X1 - X0 + 1, Y1 - Y0 + 1
    grid = build_grid(hs)
    is_ruin = bool(hs.get("ruin"))
    grass_set = set(tuple(g) for g in hs.get("grass", []))
    pad, bottom = 70, 560
    # 顶部文字块高度随 clue 条数变化：每条线索 22px，末尾还有一行图例。
    # 网格原点 oy 必须落在图例下方，并再给 x 轴列号数字（oy-12）留出高度，
    # 否则上方文字会压住方格图顶部的列号。
    legend_y = 132 + 22 * len(hs["clue"]) + 4
    top = max(210, legend_y + 40)
    W = pad + gw * SCALE + 220
    H = top + gh * SCALE + bottom
    img = Image.new("RGB", (W, H), C["bg"])
    d = ImageDraw.Draw(img)

    d.text((40, 16), hs["name"] + " · 占地拆解图", font=font(28), fill=C["text"])
    d.text((40, 54), f"屋本体见注 ｜ 占地 {gw}×{gh} 格 = {gw*TILE}×{gh*TILE} px ｜ 一格 16×16 px ｜ 主角 1×2 格",
           font=font(15), fill=C["key"])
    d.text((40, 80), STD, font=font(14), fill=C["gray"])
    d.text((40, 104), hs["story"], font=font(14), fill=C["gray"])
    yy = 132
    for ln in hs["clue"]:
        d.text((40, yy), "◆ " + ln, font=font(14), fill=C["clue"], anchor="lm")
        yy += 22
    legend = ("废墟图：残墙基 夯土=地基 绿框[草]=需美术铺 16px 杂草的格 深绿=院/天井 橙虚框=可检视地面痕迹"
              if is_ruin else
              "灰棕=墙板(顶部高光) 棕=室内 深绿=院/天井 黄=门 橙框=可检视线索")
    d.text((40, yy + 4), legend, font=font(13), fill=C["gray"])

    ox, oy = pad, top
    # 占地框
    d.rectangle([ox, oy, ox + gw * SCALE, oy + gh * SCALE],
                outline=C["lot"], width=3)
    d.text((ox + 8, oy + 8), f"占地 {gw}×{gh} 格", font=font(14), fill=C["lot"], anchor="la")

    rf = font(11 if SCALE < 34 else 12)
    for gx in range(gw):
        d.text((ox + gx * SCALE + SCALE / 2, oy - 12), str(X0 + gx),
               font=rf, fill="#c9c0ae", anchor="mm")
    for gy in range(gh):
        d.text((ox - 9, oy + gy * SCALE + SCALE / 2), str(Y0 + gy),
               font=rf, fill="#c9c0ae", anchor="mm")

    for ry, row in enumerate(grid):
        for rx, ch in enumerate(row):
            bx, by = ox + rx * SCALE, oy + ry * SCALE
            box = [bx, by, bx + SCALE - 1, by + SCALE - 1]
            if is_ruin:
                # 废墟态：墙=残墙基，室内=夯土地基，门/院门=缺口。
                # 杂草不在这里画——grass 字段列出需铺 16px 杂草素材的格，图上只画绿框+"草"占位标注，
                # 实际美术素材交给美术复用。
                if ch == "#":
                    d.rectangle(box, fill=C["ruin_wall"])
                    if (rx * 3 + ry * 5) % 4:  # 残顶高低不一，有的墙段只剩半截
                        d.line([(bx + 2, by + 2), (bx + SCALE - 3, by + 2)],
                               fill=C["ruin_base"], width=3)
                elif ch in ("D", "G"):
                    d.rectangle(box, fill=C["ruin_base"])  # 门洞缺口，不画门板色
                elif ch == ".":
                    d.rectangle(box, fill=C["ruin_base"])
                else:
                    d.rectangle(box, fill=C["yard"])
                # 杂草格占位标注：绿色细框 + "草"字，交给美术铺 16px 素材
                if (X0 + rx, Y0 + ry) in grass_set:
                    d.rectangle([bx + 2, by + 2, bx + SCALE - 3, by + SCALE - 3],
                                outline=C["ruin_grass"], width=2)
                    d.text((bx + SCALE / 2, by + SCALE / 2), "草", font=font(13),
                           fill=C["ruin_grass"], anchor="mm")
                continue
            if ch == "#":
                d.rectangle(box, fill=C["wall"])
                d.line([(bx, by), (bx + SCALE - 1, by)], fill=C["wall_top"], width=3)
            elif ch == "D":
                d.rectangle(box, fill=C["door"])
            elif ch == "G":
                d.rectangle(box, fill=C["gate"])
            elif ch == ".":
                name, ck = room_of(hs, X0 + rx, Y0 + ry)
                d.rectangle(box, fill=C["room"].get(ck, "#6b5842"))
            else:
                d.rectangle(box, fill=C["yard"])

    # 房间名：所有房间名统一延后到家具之后绘制，免得被家具矩形盖住；
    # 废墟态房间已无意义（只剩地基），跳过房间名绘制。
    # 标签统一带深色底衬，若在房间内找不到不被家具/墙占用的空格则退到矩形上边缘（top）绘制。
    label_rooms = []
    if not is_ruin:
      for room in hs["rooms"]:
        x0, y0, x1, y1, name, ck = room[:6]
        cx = ox + (x0 + x1 + 1) / 2 * SCALE
        force_top = len(room) > 6 and room[6] == "top"
        if force_top:
            label_rooms.append((cx, oy + y0 * SCALE - 2, name, "mb"))
            continue
        # 在房间里找一个空的可走格：离中心越近越好，脚下及其左右邻格无墙/家具
        # （标签横向有宽度，左右邻格被占时文字会压到家具上）
        tw = d.textlength(name, font=font(14))
        span = max(1, int(tw / SCALE) + 1)  # 标签横跨的格数
        best = None
        for ry in range(y1, y0 - 1, -1):
            for rx in range(x0, x1 + 1):
                if not (X0 <= rx <= X1 and Y0 <= ry <= Y1):
                    continue
                if grid[ry - Y0][rx - X0] not in (".", " ") or occupied(hs, rx, ry):
                    continue
                # 标签宽度不能越出房间左右边界（窄房间/斜向文字会溢出）
                if tw > (x1 - x0 + 1) * SCALE - 8:
                    continue
                # 横向 span 格内不能有墙/家具，否则文字压上去
                left = max(0, rx - span // 2)
                right = min(x1, left + span - 1)
                left = max(x0, right - span + 1)
                blocked = False
                for sx in range(left, right + 1):
                    if grid[ry - Y0][sx - X0] not in (".", " ") or occupied(hs, sx, ry):
                        blocked = True
                        break
                if blocked:
                    continue
                dist = (rx - (x0 + x1) / 2) ** 2 + (ry - (y0 + y1) / 2) ** 2
                if best is None or dist < best[0]:
                    best = (dist, rx, ry, left, right)
        if best:
            _, rx, ry, bl, br = best
            # 标签横向居中到可用空档，而不是格心
            cx = ox + (bl + br + 1) / 2 * SCALE
            label_rooms.append((cx, oy + (ry + 0.5) * SCALE, name, "mm"))
        else:
            label_rooms.append((cx, oy + y0 * SCALE - 2, name, "mb"))

    # 家具
    for f in hs["furniture"]:
        fx, fy, fw, fh = f["rect"]
        bx, by = ox + (fx - X0) * SCALE, oy + (fy - Y0) * SCALE
        bw, bh = fw * SCALE, fh * SCALE
        if is_ruin:
            # 废墟态：◆格不是摆在屋里的物件，而是地基上扒开荒草才看得见的「原物占地痕迹」。
            # 不画实心家具块，只留虚线框圈出范围 + 地面文字（橙=可检视线索）。
            edge = C["clue"] if f["clue"] else C["ruin_wall"]
            vx0, vy0, vx1, vy1 = bx + 5, by + 5, bx + bw - 6, by + bh - 6
            seg = 8
            xx = vx0
            while xx < vx1:
                d.line([(xx, vy0), (min(xx + seg, vx1), vy0)], fill=edge, width=2)
                d.line([(xx, vy1), (min(xx + seg, vx1), vy1)], fill=edge, width=2)
                xx += seg * 2
            yy = vy0
            while yy < vy1:
                d.line([(vx0, yy), (vx0, min(yy + seg, vy1))], fill=edge, width=2)
                d.line([(vx1, yy), (vx1, min(yy + seg, vy1))], fill=edge, width=2)
                yy += seg * 2
            lf = font(12)
            label = ("◆ " if f["clue"] else "") + f["short"]
            bb = d.textbbox((bx + bw / 2, by + bh / 2), label, font=lf, anchor="mm")
            d.rectangle([bb[0] - 3, bb[1] - 2, bb[2] + 3, bb[3] + 2], fill="#2b2418")
            d.text((bx + bw / 2, by + bh / 2), label, font=lf,
                   fill=C["clue"] if f["clue"] else C["text"], anchor="mm")
            continue
        if f["yard_building"]:
            d.rectangle([bx, by, bx + bw, by + bh], outline=C["yard_edge"], width=3)
            d.text((bx + bw / 2, by + bh / 2), "茅房", font=font(15),
                   fill=C["yard_furn"], anchor="mm")
            continue
        if f["zone"] == "yard":
            fill, edge = C["yard_furn"], C["yard_edge"]
        elif f["clue"]:
            fill, edge = C["clue"], C["clue"]
        else:
            fill, edge = C["furn"], C["furn_edge"]
        if f.get("seamless"):
            # 像素格拼块（如跑道）：严格按格铺满，无内缩、无描边、无标签，
            # 相邻格严丝合缝 → 拼出来的形状就是数据里的格子集合本身。
            d.rectangle([bx, by, bx + bw - 1, by + bh - 1], fill=fill)
            continue
        d.rectangle([bx + 3, by + 3, bx + bw - 4, by + bh - 4], fill=fill, outline=edge, width=2)
        draw_label(d, bx + 3, by + 3, bw - 7, bh - 7, f["short"], f["clue"])

    # 所有房间名画在家具之上，带深色底衬，任何底色/家具上都读得清
    for cx, cy, name, anchor in label_rooms:
        lf = font(14)
        bb = d.textbbox((cx, cy), name, font=lf, anchor=anchor)
        d.rectangle([bb[0] - 4, bb[1] - 2, bb[2] + 4, bb[3] + 2], fill="#2b2418")
        d.text((cx, cy), name, font=lf, fill="#f0e6cc", anchor=anchor)

    # 主角（讲解图统一放整个占地右下角可走格，视觉高 2 格；显式 player_at 仍优先）
    px, py = hs.get("player_at") or auto_player_at(hs, grid)
    bx, by = ox + (px - X0) * SCALE, oy + (py - Y0) * SCALE
    d.rectangle([bx + 3, by - SCALE + 3, bx + SCALE - 4, by + SCALE - 4],
                fill=C["player"], outline=C["player_edge"], width=2)
    d.ellipse([bx + SCALE * 0.28, by - SCALE * 0.86, bx + SCALE * 0.72, by - SCALE * 0.55],
              fill=C["player_edge"])
    d.text((bx + SCALE + 8, by - SCALE / 2), "主角 1×2", font=font(12), fill=C["key"], anchor="lm")

    # 尺寸线
    dy = oy + gh * SCALE + 22
    d.line([(ox, dy), (ox + gw * SCALE, dy)], fill=C["measure"], width=2)
    for xx in (ox, ox + gw * SCALE):
        d.line([(xx, dy - 6), (xx, dy + 6)], fill=C["measure"], width=2)
    d.text((ox + gw * SCALE / 2, dy + 8), f"占地 {gw} 格 = {gw*TILE} px",
           font=font(14), fill=C["measure"], anchor="ma")

    # 完整家具清单（分室内/院子）
    ty = oy + gh * SCALE + 62
    d.text((40, ty), "家具清单（单位：格 ｜ ◆=可检视线索）", font=font(18), fill=C["key"])
    ty += 30
    for zone, title in (("house", "— 屋内 —"), ("yard", "— 院子（可走可搜证）—")):
        d.text((40, ty), title, font=font(14), fill=C["gray"])
        ty += 22
        # 像素格拼块（如跑道）按名字合并成一行，免得刷屏
        merged = {}
        for f in [x for x in hs["furniture"] if x["zone"] == zone]:
            fx, fy, fw, fh = f["rect"]
            mark = "◆" if f["clue"] else "·"
            col = C["clue"] if f["clue"] else C["text"]
            if f.get("seamless"):
                key = (f["name"], f["note"])
                merged[key] = merged.get(key, 0) + 1
                continue
            d.text((52, ty),
                   f"{mark} {f['name']}  {fw}×{fh} 格 = {fw*TILE}×{fh*TILE} px   {f['note']}",
                   font=font(13), fill=col, anchor="lm")
            ty += 21
        for (nm, note), cnt in merged.items():
            d.text((52, ty),
                   f"· {nm}  1×1 格 × {cnt}（像素格逐格拼出，共 {cnt} 格 = {cnt*TILE}×{TILE} px）   {note}",
                   font=font(13), fill=C["text"], anchor="lm")
            ty += 21
        ty += 8
    d.text((40, H - 18), hs["note"], font=font(13), fill=C["gray"], anchor="lm")
    return img


def check_all():
    for hs in HOUSES:
        X0, Y0, X1, Y1 = hs["lot"]
        grid = build_grid(hs)
        gh = Y1 - Y0 + 1
        assert len(grid) == gh, f"{hs['name']} 网格行数不符"
        # 隔墙必须存在（用户：墙板不能全去掉）
        assert len(hs.get("partitions", [])) >= 1, f"{hs['name']} 缺内部隔墙"
        # 门必须落在墙/门格
        for (dx, dy) in hs["doors"]:
            assert 0 <= dy - Y0 < gh and 0 <= dx - X0 < len(grid[0]), f"{hs['name']} 门出界"
            assert grid[dy - Y0][dx - X0] == "D", f"{hs['name']} 门({dx},{dy})不在门格"
        # 家具：越界/重叠/压门/堵门
        boxes = []
        for f in hs["furniture"]:
            x, y, w, h = f["rect"]
            assert X0 <= x and x + w <= X1 + 1 and Y0 <= y and y + h <= Y1 + 1, \
                f"{hs['name']} 家具 {f['name']} 越界"
            for (dx, dy) in hs["doors"] + hs.get("gate", []):
                assert not (x <= dx < x + w and y <= dy < y + h), \
                    f"{hs['name']} 家具 {f['name']} 压门({dx},{dy})"
            boxes.append((x, y, w, h, f["name"]))
        # 院子建筑（茅房）可包含其内部家具（茅坑）——刻意的嵌套，豁免
        yard_buildings = [f for f in hs["furniture"] if f.get("yard_building")]
        def nested_outside(x, y, w, h):
            for yb in yard_buildings:
                bx, by, bw, bh = yb["rect"]
                if bx <= x and x + w <= bx + bw and by <= y and y + h <= by + bh:
                    return True
            return False
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                x1, y1, w1, h1, n1 = boxes[i]
                x2, y2, w2, h2, n2 = boxes[j]
                if nested_outside(x1, y1, w1, h1) or nested_outside(x2, y2, w2, h2):
                    continue
                assert not (x1 < x2 + w2 and x2 < x1 + w1 and y1 < y2 + h2 and y2 < y1 + h1), \
                    f"{hs['name']} 家具重叠: {n1} 与 {n2}"
        # 门两侧净空：至少一边可通行（.或空格且无家具）
        for (dx, dy) in hs["doors"]:
            opens = 0
            for nx, ny in ((dx-1, dy), (dx+1, dy), (dx, dy-1), (dx, dy+1)):
                if nx < X0 or nx > X1 or ny < Y0 or ny > Y1:
                    continue
                ch = grid[ny - Y0][nx - X0]
                if ch in (".", " ") and not occupied(hs, nx, ny):
                    opens += 1
            assert opens >= 1, f"{hs['name']} 门({dx},{dy})四面被堵"
        # 房间矩形不含墙格（用户口径：房间不包括墙）
        for room in hs["rooms"]:
            rx0, ry0, rx1, ry1, rname = room[:5]
            for ry in range(ry0, ry1 + 1):
                for rx in range(rx0, rx1 + 1):
                    if X0 <= rx <= X1 and Y0 <= ry <= Y1:
                        assert grid[ry - Y0][rx - X0] != "#", \
                            f"{hs['name']} 房间「{rname}」压到墙格 ({rx},{ry})"
    print(f"CHECK ALL PASS - {len(HOUSES)} houses, 隔墙/门/家具/净空/房间不压墙 全部合法")


def main():
    for frame, dname in FRAME_DIR.items():
        os.makedirs(os.path.join(OUT, dname), exist_ok=True)
    for hs in HOUSES:
        frame = FRAME_OF_ID[hs["id"]]
        sub = FRAME_DIR[frame]
        img = render(hs)
        p = os.path.join(OUT, sub, hs["id"] + ".png")
        img.save(p)
        print("saved", p, img.size)
    check_all()


if __name__ == "__main__":
    main()
