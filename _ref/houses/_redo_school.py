"""A5 2026 小学（沈明远捐建 · 村小）：整栋精调重写。

口径（用户 2026-11-22 拍板「还是一栋一栋来做」）：
  - 尺寸不动：lot [0,0,20,15] = 21×16 格（336×256 px），wings 同尺寸（整块，无外院子），
    与 docs/PROMPT-overseer.md:91、docs/PROMPT-tile-32px.md:84-85 的口径一致。
  - 街面朝北：主大门开在北墙 (9,0)(10,0)，门厅正对大门（沈明远剪彩处）。
  - 三排：北排 办公室 / 门厅 / 教师宿舍；中排 教室一 / 走廊 / 教室二；南排 操场（围墙内露天）。
    走廊是交通枢纽：门厅→走廊→操场，教室一/二各开门向走廊。
  - 证物链：「周」界碑按 docs/HANDOFF-VILLAGE.md §3 记的原坐标 [1,10,2,1] **原位保留**——
    嵌在操场北围墙（教学楼南墙）西端，字磨掉一半。
  - 修掉初版硬伤：初版两个「讲台」都放在门厅里、教室里没有讲台；教室课桌太少；
    东南角 (1..9,11..14) 一大片地面无房间归属（露默认棕）。
  - 家具硬规矩：不压门、不越界、不重叠、不堵门（四邻全空），室内每格有房间归属。

幂等：存在则替换，否则追加。
预览：MCS_PREVIEW=1 只出预览图到 lab/，不写 houses_data.json。
"""
import json
import os
from gen_all_houses import build_grid, render

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "houses_data.json")
PREVIEW = os.environ.get("MCS_PREVIEW") == "1"


def F(name, x, y, w, h, note="", clue=False, short=None, zone="house",
      yard_building=False, wall_mounted=False):
    return dict(name=name, short=short or name, rect=[x, y, w, h], note=note,
                clue=clue, zone=zone, yard_building=yard_building,
                wall_mounted=wall_mounted)


school = {
    "id": "school",
    "name": "小学 · A5 2026 · 沈明远捐建（村小）",
    "lot": [0, 0, 20, 15],
    "wings": [[0, 0, 21, 16]],
    # 隔墙：
    #   y=5  整条横墙（北排 | 中排）
    #   y=10 整条横墙（中排 | 操场）——「周」界碑就嵌在这条墙上
    #   x=5  / x=15 两条竖墙（门厅两侧 + 走廊两侧）
    "partitions": [
        [1, 5, 19, 5],
        [1, 10, 19, 10],
        [5, 1, 5, 4],
        [15, 1, 15, 4],
        [5, 6, 5, 9],
        [15, 6, 15, 9],
    ],
    # 房门：(5,3) 门厅↔办公室 | (15,3) 门厅↔宿舍 | (10,5) 门厅↔走廊
    #       (5,7) 走廊↔教室一 | (15,7) 走廊↔教室二 | (10,10) 走廊↔操场
    "doors": [[5, 3], [15, 3], [10, 5], [5, 7], [15, 7], [10, 10]],
    # 大门：(9,0)(10,0) 北墙正门
    "gate": [[9, 0], [10, 0]],
    "rooms": [
        [1, 1, 4, 4, "办公室", "account"],
        [6, 1, 14, 4, "门厅", "hall"],
        [16, 1, 19, 4, "教师宿舍", "bed"],
        [1, 6, 4, 9, "教室一", "class"],
        [6, 6, 14, 9, "走廊", "hall"],
        [16, 6, 19, 9, "教室二", "class"],
        [1, 11, 19, 14, "操场", "yard"],
    ],
    "furniture": [
        # ── 门厅 x6..14,y1..4（正门进来，剪彩处）──
        F("剪彩台", 11, 1, 3, 1, "沈明远剪彩的地方 · 他什么都不知道"),
        F("红绸横幅", 12, 0, 3, 1, "剪彩用的红绸 · 钉在门厅北墙（让开正门）", wall_mounted=True),
        F("花篮", 7, 1, 1, 1, "剪彩摆的花篮"),
        F("签到处", 6, 1, 1, 1, "来宾签到的小桌"),
        F("长凳", 7, 3, 3, 1, "家长席 · 剪彩那天坐满"),
        F("长凳", 11, 3, 3, 1, "家长席"),
        # ── 办公室 x1..4,y1..4 ──
        F("办公桌", 1, 1, 2, 1, "校长办公 · 捐建批文在抽屉"),
        F("椅", 3, 1, 1, 1, "办公桌旁"),
        F("文件柜", 4, 1, 1, 2, "贴东墙 · 教学档案"),
        F("成绩档案柜", 1, 3, 1, 2, "贴西墙"),
        F("打印机", 3, 3, 1, 1, "打印试卷"),
        F("茶桶", 4, 4, 1, 1, "办公室角落"),
        # ── 教师宿舍 x16..19,y1..4 ──
        F("单人床", 16, 1, 2, 1, "住校老师的床"),
        F("衣柜", 19, 1, 1, 2, "贴东墙"),
        F("书桌", 18, 3, 2, 1, "备课改作业"),
        F("脸盆架", 16, 4, 1, 1, "宿舍西南角"),
        # ── 教室一 x1..4,y6..9 ──
        F("黑板", 2, 5, 2, 1, "钉在教室北墙 · 让开 (10,5) 门", wall_mounted=True),
        F("讲台", 2, 6, 2, 1, "讲台正对黑板"),
        F("书包架", 4, 6, 1, 1, "挂书包的地方"),
        F("课桌", 1, 7, 2, 1, "教室一"),
        F("课桌", 1, 8, 2, 1, "教室一"),
        F("课桌", 3, 8, 2, 1, "教室一"),
        F("课桌", 1, 9, 2, 1, "教室一"),
        F("课桌", 3, 9, 2, 1, "教室一"),
        # ── 走廊 x6..14,y6..9 ──
        F("宣传栏", 6, 5, 3, 1, "贴走廊北墙 · 贴通知", wall_mounted=True),
        F("荣誉榜", 12, 5, 3, 1, "贴走廊北墙", wall_mounted=True),
        F("扫把", 6, 6, 1, 1, "走廊靠墙"),
        F("饮水机", 13, 6, 1, 1, "走廊尽头"),
        F("长凳", 7, 7, 2, 1, "课间学生坐"),
        F("长凳", 12, 7, 2, 1, "课间学生坐"),
        F("拖把", 14, 9, 1, 1, "走廊东南角"),
        # ── 教室二 x16..19,y6..9 ──
        F("黑板", 17, 5, 2, 1, "钉在教室北墙", wall_mounted=True),
        F("讲台", 17, 6, 2, 1, "讲台正对黑板"),
        F("书包架", 16, 6, 1, 1, "挂书包的地方"),
        F("课桌", 18, 7, 2, 1, "教室二"),
        F("课桌", 16, 8, 2, 1, "教室二"),
        F("课桌", 18, 8, 2, 1, "教室二"),
        F("课桌", 16, 9, 2, 1, "教室二"),
        F("课桌", 18, 9, 2, 1, "教室二"),
        # ── 操场 x1..19,y11..14（围墙内露天）──
        F("「周」界碑", 1, 10, 2, 1, "嵌在操场北围墙（教学楼南墙）西端 · 字磨掉一半",
          clue=True, short="界碑", wall_mounted=True),
        F("花坛", 2, 11, 2, 1, "操场西侧"),
        F("篮球架", 5, 11, 2, 1, "水泥篮球架"),
        F("单杠", 8, 11, 2, 1, "一副单杠"),
        F("国旗台", 14, 11, 1, 1, "升旗处 · 每周一升旗"),
        F("旱厕", 17, 11, 3, 2, "操场东南角 · 村小旱厕", zone="yard", yard_building=True),
        F("茅坑", 18, 12, 1, 1, "旱厕内", zone="yard"),
        F("标语牌", 5, 13, 3, 1, "「好好学习 天天向上」"),
        F("乒乓球台", 9, 13, 2, 1, "水泥乒乓球台"),
        F("沙坑", 13, 13, 3, 1, "跳远沙坑"),
    ],
    "clue": [
        "操场北围墙里嵌着半块旧界碑，只认得出一个「周」字（身份反转佐证）。",
        "门厅剪彩台与红绸横幅：2026 沈明远捐建 · 他什么都不知道。",
    ],
    "story": "沈明远剪彩的地方；他什么都不知道。",
    "note": ("屋本体 21×16 格 = 336×256 px（lot/wings 一致，旧 note 的「21×12」作废）。"
             "街面朝北：主大门开在北墙 (9,0)(10,0)，门厅正对大门即剪彩处。"
             "三排：北排 办公室/门厅/教师宿舍，中排 教室一/走廊/教室二，南排 操场（围墙内露天）；"
             "走廊为交通枢纽，门厅→走廊→操场。两间教室各有一块黑板+讲台（初版把讲台错放在门厅、"
             "教室里没有讲台）；教室课桌补到 5 张一张。东南角大片无归属地面已并入操场。"
             "「周」界碑按原坐标 [1,10,2,1] 保留——嵌在操场北围墙（教学楼南墙）西端。"),
}

# ── 自检 1：家具不重叠（院子建筑内嵌家具豁免）、门/大门四邻禁放家具 ──
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
for d in [tuple(d) for d in school["doors"]] + [tuple(g) for g in school["gate"]]:
    x, y = d
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        assert (x + dx, y + dy) not in occupied, f"堵门：家具占门 {d} 邻格 ({x+dx},{y+dy})"

# ── 自检 2：家具不压墙/门/院门（钉在墙上的黑板/横幅/界碑除外）──
grid = build_grid(school)
for f in school["furniture"]:
    if f.get("wall_mounted"):
        continue
    x, y, w, h = f["rect"]
    for i in range(x, x + w):
        for j in range(y, y + h):
            assert grid[j][i] in (".", " "), f"家具压墙/门：{f['name']} ({i},{j}) = {grid[j][i]}"

# ── 自检 3：室内每个地板格都有房间归属（不露默认棕）──
room_cells = {(i, j) for (x0, y0, x1, y1, *_rest) in school["rooms"]
              for j in range(y0, y1 + 1) for i in range(x0, x1 + 1)}
floor_cells = {(i, j) for j, row in enumerate(grid) for i, ch in enumerate(row) if ch == "."}
for c in sorted(floor_cells - room_cells):
    raise AssertionError(f"室内无主格（露默认色）: {c}")

if PREVIEW:
    out = os.path.join(HERE, "..", "..", "lab", "school_plan_preview.png")
    render(school).save(out)
    print("PREVIEW only (JSON untouched):", os.path.abspath(out))
    print("rooms", len(school["rooms"]), "furniture", len(school["furniture"]))
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
