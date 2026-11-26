# -*- coding: utf-8 -*-
"""只回写 `docs/待解决事项.md`（overseer 已单独写好）。

纪律：
- 列数按实际表头核对：§1.6 表 4 列（# / 问题 / 我的建议 / 影响面）、§4 表 4 列（线 / 状态 / 产出 / 文件域）。
- 用「内容定位」找锚点行，插在其后的第一个空行之前 ⇒ 不会因前面插入而漂移。
- 落盘后必须扫 U+FFFD。
"""
import io

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


pd = read_lines(PD)
log = []

# ---------------------------------------------------------------- 状态行
old_status = None
for l in pd:
    if l.startswith("> **当前状态**"):
        old_status = l
        break
assert old_status is not None, "status line not found"

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
pd = replace_text(pd, old_status, new_status)
log.append("状态行改写")

# ---------------------------------------------------------------- §1.6 新增三条裁定
q6 = None
for l in pd:
    if l.strip().startswith("| **Q6**"):
        q6 = l
        break
assert q6 is not None, "Q6 anchor not found"

q7 = (
    "| **Q7**<br>✅已拍板 | **已拍板（2026-11-26）：界碑删掉**（用户原话：「界碑删掉吧，本来也没留有多少和它相关的有用剧情」）"
    "（原问题：界碑这条线还要不要留？） | **界碑删除线**（任务书 `docs/PROMPT-stele-removal-exec.md`）："
    "五帧数据（界碑 rect shape ＋ hotspot）＋ 引擎贴图入口（`asset_draw.gd` SHARED_SCENE 的 stele、`world_view.gd` 的碑分支）＋ 三个测试断言 ＋ "
    "`docs/story.md` 叙事收口（§7.2 五条变四条、§7.4 界碑整节删、物证表删一行）＋ 四个资产清单文件（`stele_a1..a5` 五张作废，**要通知美术同学**） | "
    "🔴 **证物基线 25 卡/56 观察 → 24 卡/51 观察**（界碑＝1 卡 5 观察）；"
    "🔴 「周家曾拥有这块地」只剩**登记表前手栏**（`docs/story.md:494`）一条证据 ⇒ `story.md:500-504`/`:612` 两处措辞须拟稿待确认 |")
assert cells(q7) == 4, cells(q7)
q8 = (
    "| **Q8**<br>✅已拍板 | **已拍板（2026-11-26）：不做楼层**（用户原话：「不做楼层了，时间不够了」）"
    "（原问题：phasing 要不要跟楼层方案 C 一起做？） | **只做 phasing**，方案 C（表面高度快照）延后；"
    "L17 任务书 §3.8 已写明「用户已明确不做楼层，不许顺手做一点楼层、也不许把 phasing 做成依赖 surface 高度」 | "
    "`docs/house-spec.md` §8.1 方案 C 保留在文档里不删，标为「暂不实现」 |")
assert cells(q8) == 4, cells(q8)
q9 = (
    "| **Q9**<br>✅已拍板 | **已拍板（2026-11-26）：空气墙一致＝地图线的硬口径**（用户原话："
    "「我们只需要保证包围可探索建筑的房屋、山体的位置大致是不变的，指的是占地，房屋还是山都可以，只要包围的空气墙（实体房屋、山）的范围是一致的，"
    "这就不会有卡到山里，从而通过虚化卡到地图之外的现象」） | **空气墙 ＝ 房屋 lot 外框 ∪ 山体多边形**；"
    "**帧与帧互比**（不是以 A1 为基准）；⇒ **A4 重排线**：A4 空气墙与 A5 逐格对齐（实测目标 cover=100%／双向触发 0 格）；"
    "⇒ **A1–A3 重排线**：等 A4 搭完后按同一套约束重排（用户明说「A1-A3 的地图要等 A4 搭完才能搭建」） | "
    "**phasing 因此只是兜底**（L17 任务书 §2.3「正常不该触发」是第一验收项）；"
    "⚠️ 我先前用「以 A1 为基准」的探针口径**是错的**（A1–A4 还没在 4800×3600 上摆过），已纠正 |")
assert cells(q9) == 4, cells(q9)
pd = insert_after_row(pd, q6, [q7, q8, q9])
log.append("§1.6 Q7/Q8/Q9 插入")

# ---------------------------------------------------------------- §4 表
old_a4 = None
for l in pd:
    if l.strip().startswith("| **A4 重排线**（P0）"):
        old_a4 = l
        break
assert old_a4 is not None, "§4 A4 row not found"

new_a4 = (
    "| **A4 重排线**（P0） | ✅ **任务书已按新口径改写，可派**（`docs/PROMPT-a4-rebuild-exec.md`，464 行）—— "
    "A4 超市/井/槐与 A5 同址、**周郑两家对齐 A5 的小学/玩具店地块**、**补山×4 填平空气墙**、补竖车道/环道/内岛/路标；"
    "🔴 **五帧实体空气墙一致**（cover=100%／IoU=100%／双向触发 0 格）；⚠️ 界碑由界碑删除线撤掉 | "
    "交付物＝`data/frames.json` 的 a4_2001 帧（只改这一帧）＋ `_mdtest/a4_rebuild_check.gd` ＋ `docs/FEEDBACK-a4-rebuild-exec.md` | "
    "`data/frames.json`（与 A1–A3 重排线**串行**；与界碑删除线**错开落盘**） |")
assert cells(new_a4) == 4, cells(new_a4)
pd = replace_text(pd, old_a4, new_a4, expected_cells=4)
log.append("§4 A4 行改写")

stele = (
    "| **界碑删除线**（新） | ✅ **任务书已写，可派**（`docs/PROMPT-stele-removal-exec.md`）—— 五帧数据＋引擎贴图入口＋三个测试＋"
    "`docs/story.md` 叙事收口＋四个资产清单文件（`stele_a1..a5` 作废，**要通知美术同学**） | "
    "证物基线 25 卡/56 观察 → **24 卡/51 观察**；🔴 与 L17 串行（都碰 `world_view.gd`） | "
    "`data/frames.json`（只删界碑条目，与 A4 重排线错开落盘）＋ `scripts/asset_draw.gd` ＋ `scripts/world_view.gd` ＋ `scripts/house_shape.gd` ＋ "
    "三个 `_mdtest/` ＋ `docs/story.md` ＋ 四个资产清单文件 |")
assert cells(stele) == 4, cells(stele)
pd = insert_after_row(pd, new_a4, [stele])
log.append("§4 界碑删除线行插入")

write_lines(PD, pd)

s = io.open(PD, encoding="utf-8").read()
assert s.count("\ufffd") == 0, "U+FFFD found"
for x in log:
    print("ok ", x)
print("pending lines", len(read_lines(PD)), "no U+FFFD")
