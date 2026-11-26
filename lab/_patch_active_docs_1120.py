# -*- coding: utf-8 -*-
"""回写两份活文档：新增界碑删除线 / L17 口径改写 / 空气墙一致 / A4 新锚点。

纪律（踩过的坑）：
- 只用「整行替换」或「按内容定位后插入」两种操作；**绝不用 replace 拼接**（会把表格列数改错）。
- 新增表格行的列数必须与该表表头一致（工作线表 5 列、索引表 3 列、§十 待办表 3 列、§十一「现在就能开」表 3 列、
  待解决事项 §1.6 表 4 列、§4 表 4 列）。
- 新增表格行必须插在「表格最后一行之后、空行之前」，否则会断开表格。
- **行号一律不写死**：用「内容定位」找锚点行，插在它后面的第一个空行之前 ⇒ 不会因前面插入而漂移。
- 落盘后必须扫 U+FFFD。
"""
import io
import json

OV = "docs/PROMPT-overseer.md"
PD = "docs/待解决事项.md"


def read_lines(path):
    return io.open(path, encoding="utf-8").read().split("\n")


def write_lines(path, lines):
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))


def cells(line):
    s = line.strip()
    if not s.startswith("|"):
        return None
    return len(s.split("|")) - 2


def find(lines, text):
    hits = [i for i, l in enumerate(lines) if l == text]
    assert len(hits) == 1, "anchor not unique (%d hits): %r" % (len(hits), text[:80])
    return hits[0]


def insert_after_row(lines, text, new_rows):
    """在锚点行之后、其后的第一个空行之前插入新行。"""
    i = find(lines, text)
    j = i + 1
    while j < len(lines) and lines[j].strip() != "":
        j += 1
    assert j < len(lines) and lines[j].strip() == "", "no blank line after anchor"
    return lines[:j] + new_rows + lines[j:]


def replace_text(lines, text, new_row, expected_cells=None):
    i = find(lines, text)
    if expected_cells is not None:
        assert cells(lines[i]) == expected_cells, (
            "cells mismatch: %s != %s for %r" % (cells(lines[i]), expected_cells, text[:60]))
    lines[i] = new_row
    return lines


def check_no_fffd(path):
    s = io.open(path, encoding="utf-8").read()
    n = s.count("\ufffd")
    assert n == 0, "%s has %d U+FFFD" % (path, n)


ov_rows = json.load(io.open("lab/_ov_rows.json", encoding="utf-8"))
pd_rows = json.load(io.open("lab/_pd_rows.json", encoding="utf-8"))

log = []

# ================================================================ overseer
ov = read_lines(OV)

# --- §三 工作线表（5 列）：A4 行改写 + 新增界碑删除线行
new_a4_work = (
    "| **A4 重排线** | **a4_2001 帧按 A5 v5 新世界重排** | `data/frames.json`（**只替换 a4_2001 这一个帧对象**） | 🔴 | "
    "✅ **任务书已按新口径改写**（`docs/PROMPT-a4-rebuild-exec.md`，464 行）→ **可派**；"
    "新锚点＝shen_a4(64,416)／market(2144,320)（与 A5 同址）／**zhou_a4(576,1920)**（落在 A5 小学那块地）／**zheng_a4(1152,2272)**＋**补山×4**；"
    "🔴 **五帧实体空气墙一致**（空气墙＝房屋 lot ∪ 山体）⇒ 实测 cover=100%／IoU=100%／**A4↔A5 双向触发 0 格**（旧布局 IoU 只有 26.2%）；"
    "⚠️ **界碑已由界碑删除线撤掉，本线不落界碑**；⚠️ 与 A1–A3 重排线**串行**（同写 frames.json） |")
assert cells(new_a4_work) == 5
ov = replace_text(ov, ov_rows["105"], new_a4_work, expected_cells=5)
log.append("ov §三 工作线表：A4 行改写")

stele_work = (
    "| **界碑删除线**（新） | **撤掉周界石碑与其全部配套**（用户 2026-11-26 拍板「界碑删掉吧，本来也没留有多少和它相关的有用剧情」） | "
    "`data/frames.json`（只删五帧的界碑 shape/hotspot）＋ `scripts/asset_draw.gd` ＋ `scripts/world_view.gd` ＋ `scripts/house_shape.gd` ＋ 三个 `_mdtest/` ＋ "
    "`docs/story.md` ＋ 四个资产清单文件 | 🔴 | ✅ **任务书已写**（`docs/PROMPT-stele-removal-exec.md`）→ **可派**；"
    "证物基线 25 卡/56 观察 → **24 卡/51 观察**（界碑＝1 卡 5 观察）；⚠️ 与 L17 **串行**（都碰 `world_view.gd`）；⚠️ 与 A4 重排线**错开落盘**（同写 frames.json） |")
assert cells(stele_work) == 5
ov = insert_after_row(ov, new_a4_work, [stele_work])
log.append("ov §三 工作线表：界碑删除线行插入")

# --- §三 索引表（3 列）：L17 行改写 + A4 行改写 + 新增界碑删除线行
new_idx_l17 = (
    "| `docs/PROMPT-phasing-exec.md` | **L17**（删「顶住了」＋实现卡墙虚化 phasing） | "
    "✅ **2026-11-26 已按用户新口径改写，可派**（547 行）；依据 `docs/house-spec.md` §8.3；"
    "🔴 **口径＝空气墙一致 ⇒ 正常不触发，phasing 只是实体范围内的兜底**；⚠️ **不做楼层方案 C**（用户已明确时间不够）；"
    "⚠️ 与 L8 争 `scripts/world_view.gd` ⇒ 二选一 |")
assert cells(new_idx_l17) == 3
ov = replace_text(ov, ov_rows["125"], new_idx_l17, expected_cells=3)
log.append("ov §三 索引表：L17 行改写")

new_idx_a4 = (
    "| `docs/PROMPT-a4-rebuild-exec.md` | **A4 重排线**（a4_2001 帧按 A5 v5 新世界重排） | "
    "✅ **2026-11-26 已按新口径改写，可派**（464 行）；新锚点＋**五帧实体空气墙一致**（cover=100%／双向触发 0 格）；"
    "⚠️ 只改 a4_2001 一个帧对象 |")
assert cells(new_idx_a4) == 3
ov = replace_text(ov, ov_rows["126"], new_idx_a4, expected_cells=3)
log.append("ov §三 索引表：A4 行改写")

stele_index = (
    "| `docs/PROMPT-stele-removal-exec.md` | **界碑删除线**（撤掉周界石碑：数据/引擎/测试/叙事/资产清单五层） | "
    "✅ **2026-11-26 新写，可派**；证物 25/56 → **24/51**；⚠️ 与 L17 串行（都碰 `world_view.gd`） |")
assert cells(stele_index) == 3
ov = insert_after_row(ov, new_idx_a4, [stele_index])
log.append("ov §三 索引表：界碑删除线行插入")

# --- §六 口径订正：界碑那条改写 + 新增两条
new_rule_stele = (
    "- **地标是坐标系不是美术资产** ⇒ 五帧位置不许漂；"
    "🔴 **界碑已作废（2026-11-26 用户拍板「界碑删掉吧」）** ⇒ 五帧各一个的「周界」石碑与它的三次挪位剧情**全部撤销**"
    "（界碑删除线 `docs/PROMPT-stele-removal-exec.md` 负责）；地标口径只剩：老井 `(2048,832)`、老槐 `(2048,1664)`、坝、田、超市工地。")
ov = replace_text(ov, ov_rows["191"], new_rule_stele)
log.append("ov §六：界碑口径改写")

new_rules = [
    "- 🔴 **「五帧实体空气墙一致」是地图线的硬口径（2026-11-26 用户拍板）**："
    "**空气墙 ＝ 房屋 lot 外框 ∪ 山体多边形**（路/田/井/树/内岛/环道都 `solid:false`，不算）；"
    "判据是**帧与帧互比**（不是以 A1 为基准）——玩家推时间时，同一坐标在前后两帧必须**都还是可站**，否则就是「空地突变实体」。"
    "⇒ **A4 重排线**：A4 的空气墙必须与 A5 **逐格对齐**（实测目标 cover=100%／双向触发 0 格）；"
    "⇒ **A1–A3 重排线**：等 A4 搭完后按同一套约束重排（用户 2026-11-26 明说「A1-A3 的地图要等 A4 搭完才能搭建」）。",
    "- 🔴 **phasing（卡墙虚化）只是兜底，不是解法**：用户口径「只要包围的空气墙（实体房屋、山）的范围是一致的，"
    "就不会有卡到山里，从而通过虚化卡到地图之外的现象」⇒ **正常游玩不该触发 phasing**"
    "（L17 任务书 §2.3「正常不该触发」是它的第一验收项）；⇒ **不做楼层方案 C**（用户 2026-11-26：「不做楼层了，时间不够了」）。",
]
ov = insert_after_row(ov, new_rule_stele, new_rules)
log.append("ov §六：空气墙/phasing 两条口径插入")

# --- §十 待办表（3 列）：L17 行改写 + A4 行改写 + 新增界碑删除线行
new_todo_l17 = (
    "| **L17 phasing/虚化**（用户 2026-11-26 拍板） | ✅ **任务书已按新口径改写，可派**（`docs/PROMPT-phasing-exec.md`，547 行） | "
    "**删掉「顶住了」全部代码**（`timeline.gd`／`main.gd`／`world_view.gd`／`player.gd`／`hud.gd` ＋ 两个测试文件）＋ 实现 phasing（alpha≈0.4 半透明、"
    "phasing 期间**绕过 `is_free()`** 独立位移、每步结束检查是否回到自由点）；"
    "🔴 **口径＝空气墙一致 ⇒ 正常不触发，phasing 只是兜底**；⚠️ **不做楼层方案 C**（用户明说时间不够）；"
    "⚠️ 与 L8 争 `scripts/world_view.gd` ⇒ 二选一 |")
assert cells(new_todo_l17) == 3
ov = replace_text(ov, ov_rows["302"], new_todo_l17, expected_cells=3)
log.append("ov §十 待办表：L17 行改写")

new_todo_a4 = (
    "| **A4 重排线**（P0） | ✅ **任务书已按新口径改写，可派**（`docs/PROMPT-a4-rebuild-exec.md`，464 行） | "
    "只替换 `data/frames.json` 的 a4_2001 帧：超市/井/槐与 A5 同址、**周郑两家对齐 A5 的小学/玩具店地块**、**补山×4 填平空气墙**、"
    "补竖车道＋环道＋内岛＋路标；🔴 **五帧实体空气墙一致**（cover=100%／双向触发 0 格）；"
    "⚠️ 与 A1–A3 重排线**串行**（同写 frames.json）；⚠️ 界碑由界碑删除线撤掉 |")
assert cells(new_todo_a4) == 3
ov = replace_text(ov, ov_rows["303"], new_todo_a4, expected_cells=3)
log.append("ov §十 待办表：A4 行改写")

stele_todo = (
    "| **界碑删除线**（新） | ✅ **任务书已写，可派**（`docs/PROMPT-stele-removal-exec.md`） | "
    "五帧数据（删界碑 shape/hotspot）＋ 引擎贴图入口（`asset_draw.gd` SHARED_SCENE、`world_view.gd` 碑分支）＋ 三个测试 ＋ "
    "`docs/story.md` 叙事收口（§7.2 五条变四条、§7.4 界碑整节删、物证表删一行）＋ 四个资产清单文件（`stele_a1..a5` 五张作废）；"
    "🔴 **证物基线 25 卡/56 观察 → 24 卡/51 观察**；⚠️ 与 L17 串行（都碰 `world_view.gd`） |")
assert cells(stele_todo) == 3
ov = insert_after_row(ov, new_todo_a4, [stele_todo])
log.append("ov §十 待办表：界碑删除线行插入")

# --- §十一「现在就能开」表（3 列）：L17 行改写 + 新增界碑删除线行
new_open_l17 = (
    "| **L17 phasing/虚化** | `scripts/timeline.gd` ＋ `scripts/player.gd` ＋ `scripts/world_view.gd` ＋ `scripts/main.gd` ＋ `scripts/hud.gd` | "
    "✅ **任务书已按新口径改写，可派**（547 行）；🔴 与 L8 二选一（争 `world_view.gd`）；"
    "⚠️ 界碑删除线也碰 `world_view.gd` ⇒ **这三条里同一时刻只能有一条在跑** |")
assert cells(new_open_l17) == 3
ov = replace_text(ov, ov_rows["359"], new_open_l17, expected_cells=3)
log.append("ov §十一 现在就能开表：L17 行改写")

stele_open = (
    "| **界碑删除线** | `data/frames.json`（只删界碑条目）＋ `scripts/asset_draw.gd` ＋ `scripts/world_view.gd` ＋ `scripts/house_shape.gd` ＋ 三个 `_mdtest/` ＋ "
    "`docs/story.md` ＋ 四个资产清单 | ✅ **任务书已写，可派**；🔴 与 L17 串行（都碰 `world_view.gd`）；"
    "⚠️ 与 A4 重排线错开落盘（同写 frames.json） |")
assert cells(stele_open) == 3
ov = insert_after_row(ov, new_open_l17, [stele_open])
log.append("ov §十一 现在就能开表：界碑删除线行插入")

# --- §十一 更新段：插在「### ✅ 现在就能开」标题之后
anchor = None
for i, l in enumerate(ov):
    if l.strip() == "### ✅ 现在就能开":
        anchor = i
        break
assert anchor is not None
block = [
    "",
    "**2026-11-26 11:20 更新（用户三条新指示 ＋ 五份任务书就绪）**：",
    "",
    "1. 🔴 **用户三条新指示（2026-11-26）**：①「**界碑删掉吧**，本来也没留有多少和它相关的有用剧情」⇒ 新开**界碑删除线**"
    "（任务书 `docs/PROMPT-stele-removal-exec.md`）；②「**不做楼层了**，时间不够了」⇒ L17 只做 phasing、方案 C 延后；"
    "③ **纠正 phasing 口径**：判据不是「以 A1 为基准」，而是「**包围可探索建筑的房屋、山体的占地范围在五帧之间保持一致（空气墙一致）**"
    "⇒ 正常游玩不会卡到山里、不会虚化穿出地图」。",
    "2. ✅ **L17 任务书已改写（547 行）**：§2.1 主线改为「空气墙一致性是地图线的活，不是 phasing 的活」；"
    "§2.3 新增「🔴 **正常不该触发是本线第一验收项**」；§2.4 加「不许虚化出地图／不许虚化进虚空」；§3.8 补「不做楼层」；"
    "§4 新增 §4.5「空气墙一致性核对」（逐对报告触发格数，A4→A5 必须接近 0）。",
    "3. ✅ **A4 重排线任务书已改写（464 行）**：删掉全部界碑内容；新锚点＝**zhou_a4(576,1920)**＋**zheng_a4(1152,2272)**＋**补山×4**；"
    "新增 §2.6「五帧实体空气墙一致」——实测 **cover(A5⊆A4)=100%／IoU=100%／A4↔A5 双向触发 0 格**（旧布局 IoU 只有 26.2%）；"
    "⚠️ **A1–A3 重排线等 A4 搭完后再派**（用户明说）。",
    "4. 🔴 **实测的两个坑（已写进任务书）**：①压环岛**不能用 bbox**（环道 bbox 比真实环形大）——必须用**点包含测试**；"
    "②「实体」的判定照 `scripts/frame_data.gd:38`（`solid:false` 不进碰撞）——**路/田/井/树/内岛/环道都不算实体**，"
    "只有房屋 lot 与 `solid:true` 的世界物件算。",
]
ov = ov[:anchor + 1] + block + ov[anchor + 1:]
log.append("ov §十一：2026-11-26 11:20 更新段插入")

write_lines(OV, ov)
check_no_fffd(OV)

# ================================================================ 待解决事项
pd = read_lines(PD)

new_status = (
    "> **当前状态**：2026-11-26 11:20 · 仓库 HEAD `4e10958`（本地；远端仍 `b0798da`，按用户定时指令推）· "
    "🔴 **用户 2026-11-26 三条新指示**：①「**界碑删掉吧**，本来也没留有多少和它相关的有用剧情」⇒ 新开**界碑删除线**"
    "（任务书 `docs/PROMPT-stele-removal-exec.md`）；②「**不做楼层了**，时间不够了」⇒ L17 只做 phasing、方案 C 延后；"
    "③ **纠正 phasing 口径**＝「包围可探索建筑的房屋、山体的占地范围在五帧之间保持一致（空气墙一致）」⇒ 正常游玩不触发 phasing，phasing 只是兜底。"
    "｜✅ **五份任务书就绪**：L17 phasing（`docs/PROMPT-phasing-exec.md` 547 行，已按新口径改写）／L15 归档表+结局／L16 双日记渲染／"
    "**A4 重排线**（`docs/PROMPT-a4-rebuild-exec.md` 464 行，新锚点＋补山×4）／**界碑删除线**（新）｜"
    "🔴 **A4 空气墙实测**：zhou_a4(576,1920)＋zheng_a4(1152,2272)＋补山×4 ⇒ cover(A5⊆A4)=100%／IoU=100%／**A4↔A5 双向触发 0 格**"
    "（旧布局 IoU 仅 26.2%）｜🔴 **并行排线**：A4 重排线（写 frames.json）‖L15‖L16‖界碑删除线；"
    "⚠️ **L17 与界碑删除线与 L8 三选一**（都碰 `world_view.gd`）；⚠️ A4 重排线 vs A1–A3 重排线二选一（用户明说 A1–A3 等 A4 搭完）；"
    "L15/L16 的 `main.gd` 接线要等 L17｜L14（A5 落地）已交付并验收 ✅（证物口径 25 卡/56 观察；**界碑删除后 → 24 卡/51 观察**）")
pd = replace_text(pd, pd_rows["6"], new_status)
log.append("pd 状态行改写")

q7 = (
    "| **Q7**<br>✅已拍板 | **已拍板（2026-11-26）：界碑删掉**（用户原话：「界碑删掉吧，本来也没留有多少和它相关的有用剧情」）"
    "（原问题：界碑这条线还要不要留？） | **界碑删除线**（任务书 `docs/PROMPT-stele-removal-exec.md`）："
    "五帧数据（界碑 rect shape ＋ hotspot）＋ 引擎贴图入口（`asset_draw.gd` SHARED_SCENE 的 stele、`world_view.gd` 的碑分支）＋ 三个测试断言 ＋ "
    "`docs/story.md` 叙事收口（§7.2 五条变四条、§7.4 界碑整节删、物证表删一行）＋ 四个资产清单文件（`stele_a1..a5` 五张作废，**要通知美术同学**） | "
    "🔴 **证物基线 25 卡/56 观察 → 24 卡/51 观察**（界碑＝1 卡 5 观察）；"
    "🔴 「周家曾拥有这块地」只剩**登记表前手栏**（`docs/story.md:494`）一条证据 ⇒ `story.md:500-504`/`:612` 两处措辞须拟稿待确认 |")
assert cells(q7) == 4
q8 = (
    "| **Q8**<br>✅已拍板 | **已拍板（2026-11-26）：不做楼层**（用户原话：「不做楼层了，时间不够了」）"
    "（原问题：phasing 要不要跟楼层方案 C 一起做？） | **只做 phasing**，方案 C（表面高度快照）延后；"
    "L17 任务书 §3.8 已写明「用户已明确不做楼层，不许顺手做一点楼层、也不许把 phasing 做成依赖 surface 高度」 | "
    "`docs/house-spec.md` §8.1 方案 C 保留在文档里不删，标为「暂不实现」 |")
assert cells(q8) == 4
q9 = (
    "| **Q9**<br>✅已拍板 | **已拍板（2026-11-26）：空气墙一致＝地图线的硬口径**（用户原话："
    "「我们只需要保证包围可探索建筑的房屋、山体的位置大致是不变的，指的是占地，房屋还是山都可以，只要包围的空气墙（实体房屋、山）的范围是一致的，"
    "这就不会有卡到山里，从而通过虚化卡到地图之外的现象」） | **空气墙 ＝ 房屋 lot 外框 ∪ 山体多边形**；"
    "**帧与帧互比**（不是以 A1 为基准）；⇒ **A4 重排线**：A4 空气墙与 A5 逐格对齐（实测目标 cover=100%／双向触发 0 格）；"
    "⇒ **A1–A3 重排线**：等 A4 搭完后按同一套约束重排（用户明说「A1-A3 的地图要等 A4 搭完才能搭建」） | "
    "**phasing 因此只是兜底**（L17 任务书 §2.3「正常不该触发」是第一验收项）；"
    "⚠️ 我先前用「以 A1 为基准」的探针口径**是错的**（A1–A4 还没在 4800×3600 上摆过），已纠正 |")
assert cells(q9) == 4

# Q6 原文在文件里：用「Q6」开头定位
q6_anchor = None
for l in pd:
    if l.strip().startswith("| **Q6**"):
        q6_anchor = l
        break
assert q6_anchor is not None, "Q6 anchor not found"
pd = insert_after_row(pd, q6_anchor, [q7, q8, q9])
log.append("pd §1.6：Q7/Q8/Q9 插入")

new_pending_a4 = (
    "| **A4 重排线**（P0） | ✅ **任务书已按新口径改写，可派**（`docs/PROMPT-a4-rebuild-exec.md`，464 行）—— "
    "A4 超市/井/槐与 A5 同址、**周郑两家对齐 A5 的小学/玩具店地块**、**补山×4 填平空气墙**、补竖车道/环道/内岛/路标；"
    "🔴 **五帧实体空气墙一致**（cover=100%／IoU=100%／双向触发 0 格）；⚠️ 界碑由界碑删除线撤掉 | "
    "交付物＝`data/frames.json` 的 a4_2001 帧（只改这一帧）＋ `_mdtest/a4_rebuild_check.gd` ＋ `docs/FEEDBACK-a4-rebuild-exec.md` | "
    "`data/frames.json`（与 A1–A3 重排线**串行**；与界碑删除线**错开落盘**） |")
assert cells(new_pending_a4) == 5
pd = replace_text(pd, pd_rows["442"], new_pending_a4, expected_cells=5)
log.append("pd §4：A4 行改写")

stele_pending = (
    "| **界碑删除线**（新） | ✅ **任务书已写，可派**（`docs/PROMPT-stele-removal-exec.md`）—— 五帧数据＋引擎贴图入口＋三个测试＋"
    "`docs/story.md` 叙事收口＋四个资产清单文件（`stele_a1..a5` 作废，**要通知美术同学**） | "
    "证物基线 25 卡/56 观察 → **24 卡/51 观察**；🔴 与 L17 串行（都碰 `world_view.gd`） | "
    "`data/frames.json`（只删界碑条目，与 A4 重排线错开落盘）＋ `scripts/asset_draw.gd` ＋ `scripts/world_view.gd` ＋ `scripts/house_shape.gd` ＋ "
    "三个 `_mdtest/` ＋ `docs/story.md` ＋ 四个资产清单文件 |")
assert cells(stele_pending) == 5
pd = insert_after_row(pd, new_pending_a4, [stele_pending])
log.append("pd §4：界碑删除线行插入")

write_lines(PD, pd)
check_no_fffd(PD)

for x in log:
    print("ok ", x)
print("overseer lines", len(read_lines(OV)), "pending lines", len(read_lines(PD)))
print("no U+FFFD in both")
