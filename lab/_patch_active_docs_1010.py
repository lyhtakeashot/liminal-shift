# -*- coding: utf-8 -*-
"""回写两份活文档：docs/PROMPT-overseer.md 与 docs/待解决事项.md
- overseer：新增 L15/L16/L17/A4 重排线四行（§三 工作线表 + 提示词索引表 + §十 待办表 + §十一 现在就能开表）、
  §六 口径订正（A4↔A5 同址新坐标、界碑新址、顶住了作废只做虚化）、§十一 新增更新段。
- 待解决事项：状态行更新、§1.6 加 Q6（顶住了作废）、§4 表五行状态更新。
"""
import io, re, sys

OV = "docs/PROMPT-overseer.md"
PD = "docs/待解决事项.md"

def read(p):
    return io.open(p, encoding="utf-8").read().split("\n")

def write(p, lines):
    io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))

def sub1(lines, old, new):
    hits = [i for i, l in enumerate(lines) if old in l]
    if len(hits) != 1:
        raise SystemExit("NOT-UNIQUE(%d): %s" % (len(hits), old[:60]))
    lines[hits[0]] = lines[hits[0]].replace(old, new)

def insert_after(lines, anchor, new_lines):
    hits = [i for i, l in enumerate(lines) if anchor in l]
    if len(hits) != 1:
        raise SystemExit("ANCHOR-NOT-UNIQUE(%d): %s" % (len(hits), anchor[:60]))
    i = hits[0]
    lines[i + 1:i + 1] = new_lines

def count_lines(p):
    return len(io.open(p, encoding="utf-8").read().split("\n"))

n_ph = count_lines("docs/PROMPT-phasing-exec.md")
n_en = count_lines("docs/PROMPT-ending-form-exec.md")
n_di = count_lines("docs/PROMPT-diary-render-exec.md")
n_a4 = count_lines("docs/PROMPT-a4-rebuild-exec.md")

# ============================ overseer ============================
ov = read(OV)

# --- §三 工作线表：L14 行后插入四行 ---
insert_after(ov, "| **L14** | **A5 落地（2026 帧 + 世界放大 + 文本同批改）**", [
 "| **L15** | **归档表 + 结局变体**（三变体记述 + 两个出口） | 新建 `scripts/ending_store.gd` + `scripts/ending_report.gd` + `scripts/ending_form.gd` + `_mdtest/ending_check.gd`（＋ `scripts/main.gd` 仅接线，且必须等 L17 交卷） | 🟢 | ✅ **任务书已写**（`docs/PROMPT-ending-form-exec.md`）→ **可派**；真相全部现成（`docs/story.md` §10.0–§10.5），本线不另编内容；与地图线**文件零重叠**，可并行 |",
 "| **L16** | **双日记渲染**（假本/真本并排 + 涂改自绘） | 新建 `scripts/diary_markup.gd` + `scripts/diary_page.gd` + `scripts/diary_view.gd` + `scripts/diary_texts.gd` + `_mdtest/diary_render_check.gd`（＋ `scripts/main.gd` 仅接线） | 🟢 | ✅ **任务书已写**（`docs/PROMPT-diary-render-exec.md`）→ **可派**；语法与原稿全部现成（`docs/diary-markup.md` + `docs/story.md` 附一）；与 L15 文件零重叠可同时跑，但**两个不能同时改 `scripts/main.gd`** |",
 "| **L17** | **卡墙虚化（phasing）** —— 删「顶住了」 | `scripts/timeline.gd` + `scripts/player.gd` + `scripts/world_view.gd` + `scripts/main.gd` + `scripts/hud.gd` | 🔴 | ✅ **任务书已写**（`docs/PROMPT-phasing-exec.md`）→ **可派**；🔴 **用户 2026-11-26 拍板：「顶住这点去掉，只做虚化」**（原话「顶住这点是你自己补上的我未批准的内容」）；⚠️ 撞 `scripts/world_view.gd` ⇒ **与 L8 二选一**；⚠️ 只做 phasing，**不做**楼层方案 C |",
 "| **A4 重排线** | **a4_2001 帧按 A5 v5 新世界重排** | `data/frames.json`（**只替换 a4_2001 这一个帧对象**） | 🔴 | ✅ **任务书已写**（`docs/PROMPT-a4-rebuild-exec.md`）→ **可派**；几何已由总策划实测 errors=0（shen_a4(64,416)／market(2144,320) 与 A5 同址／zhou_a4(2272,1984)／zheng_a4(2304,2400)／井(2048,832) r32／槐(2048,1664) r96／界碑(3520,1536)）；⚠️ 与 A1–A3 重排线**串行**（同写 frames.json） |",
])

# --- §三 提示词索引表：L14 索引行后插入四行 ---
insert_after(ov, "| `docs/PROMPT-a5-v5-exec.md` | **L14**", [
 "| `docs/PROMPT-ending-form-exec.md` | **L15**（归档表填格 + 三变体记述 + 两个出口） | ✅ **2026-11-26 新写，可派**（%d 行）；真相全在 `docs/story.md` §10.0–§10.5 ＋§4.6 两套分类；⚠️ 接线段必须等 L17 交卷（都改 `scripts/main.gd`） |" % n_en,
 "| `docs/PROMPT-diary-render-exec.md` | **L16**（双日记渲染：假本/真本并排 + 涂改自绘） | ✅ **2026-11-26 新写，可派**（%d 行）；🔴 删除线必须自绘（`RichTextLabel` 的 `[s]` 太细）；可搬 `_mdtest/render3.gd` 的解析器与页面容器 |" % n_di,
 "| `docs/PROMPT-phasing-exec.md` | **L17**（删「顶住了」＋实现卡墙虚化 phasing） | ✅ **2026-11-26 新写，可派**（%d 行）；依据 `docs/house-spec.md` §8.3；⚠️ 与 L8 争 `scripts/world_view.gd` ⇒ 二选一 |" % n_ph,
 "| `docs/PROMPT-a4-rebuild-exec.md` | **A4 重排线**（a4_2001 帧按 A5 v5 新世界重排） | ✅ **2026-11-26 新写，可派**（%d 行）；几何基准＝总策划实测的 A4 候选（`lab/_a4_rebuild_check.py` errors=0）；⚠️ 只改 a4_2001 一个帧对象 |" % n_a4,
])

# --- §六 口径订正 ---
sub1(ov, "A4 超市必须与 A5 同址 `[1440,768]`。",
        "A4 超市必须与 A5 同址 —— 🔴 **L14 落地后 A5 超市已挪到 `[2144,320]`**，A4 重排线同步对齐（任务书 `docs/PROMPT-a4-rebuild-exec.md`，几何已实测 errors=0）。")
sub1(ov, "1951 埋土 → 2001 被推到工地东边空地 `[2880,960]` → 2026 砌进小学围墙 `[32,1024,16,32]`",
        "1951 埋土 → 2001 被推到工地东边空地（A4 重排线定 `[3520,1536,16,32]`，旧 `[2880,960]` 作废）→ 2026 砌进小学围墙（L14 已落地 `[608,2496,16,32]`，旧 `[32,1024,16,32]` 作废）")
insert_after(ov, "- **A4/A5 六栋暂无美术成品图**", [
 "- 🔴 **「顶住了」机制作废，只做 phasing（卡墙虚化）**（2026-11-26 用户拍板，原话「顶住这点去掉，只做虚化。顶住这点是你自己补上的我未批准的内容」）：`scripts/timeline.gd:78-92` 的 bump 分支与 `main.gd:_on_bump`／`world_view.gd` 震屏／`player.bump_kick`／`hud.bump_flash` 全部删除，改为实现 `docs/house-spec.md` §8.3 的 phasing（alpha≈0.4 半透明＋色差、phasing 期间**绕过 `is_free()`** 独立位移、每步结束用 `if frames[index].is_free(char_pos)` 退出 phasing、仅 phasing 时用 A/D 做内/外位移）。⚠️ `house-spec.md:770` 原本要求 phasing 与楼层方案 C 同期 ⇒ 本次**只做 phasing，不做楼层方案 C**（取舍见 `docs/PROMPT-phasing-exec.md`）。",
 "- **地标跨帧同址口径（重排后）**：老井与老槐在 A4/A5 **必须同心**（井 `(2048,832)`、槐 `(2048,1664)`），只有**界碑**例外（它的三次挪位是剧情）。",
])

# --- §十 待办表：L14 行后插入四行 ---
insert_after(ov, "| **L14 A5 落地** | ✅ **已交付并验收通过**（`0989e87`／`5621db0`／`e086c83`", [
 "| **L15 归档表 + 结局变体** | ✅ **任务书已写，可派**（`docs/PROMPT-ending-form-exec.md`） | 真相全部现成（`docs/story.md` §10.0–§10.5 ＋§4.6 两套分类）；新建 `scripts/ending_{store,report,form}.gd` ＋ `_mdtest/ending_check.gd`；⚠️ 接线（改 `scripts/main.gd`）必须等 L17 交卷 |",
 "| **L16 双日记渲染** | ✅ **任务书已写，可派**（`docs/PROMPT-diary-render-exec.md`） | 语法 `docs/diary-markup.md` 四标记 ＋ 原稿 `docs/story.md` 附一.1–附一.4；新建 `scripts/diary_{markup,page,view,texts}.gd` ＋ `_mdtest/diary_render_check.gd`；与 L15 文件零重叠可同时跑（但**不能同时改 `scripts/main.gd`**） |",
 "| **L17 phasing/虚化**（用户 2026-11-26 拍板） | ✅ **任务书已写，可派**（`docs/PROMPT-phasing-exec.md`） | **删掉「顶住了」全部代码**（`timeline.gd`／`main.gd`／`world_view.gd`／`player.gd`／`hud.gd` ＋ 两个测试文件）＋ 实现 phasing（独立位移绕过 `is_free()`、alpha≈0.4、A/D 内/外位移）；🔴 与 L8 争 `scripts/world_view.gd` ⇒ 二选一；⚠️ 只做 phasing，楼层方案 C 不做 |",
 "| **A4 重排线**（P0） | ✅ **任务书已写，可派**（`docs/PROMPT-a4-rebuild-exec.md`） | 只替换 `data/frames.json` 的 a4_2001 帧：超市/井/槐与 A5 同址、界碑到工地东边 `[3520,1536]`、补竖车道＋环道＋内岛＋山×3＋路标×4；几何已实测 errors=0；⚠️ 与 A1–A3 重排线**串行**（同写 frames.json） |",
])

# --- §十一 更新段 + 现在就能开表 ---
insert_after(ov, "### ✅ 现在就能开", [
 "**2026-11-26 10:10 更新（用户拍板「顶住了作废、只做虚化」＋四份新任务书已写）**：",
 "",
 "1. 🔴 **用户拍板：「顶住这点去掉，只做虚化。顶住这点是你自己补上的我未批准的内容」** —— 「顶住了」机制**作废**（`scripts/timeline.gd:78-92` 的 bump 分支、`main.gd:_on_bump`、`world_view.gd` 震屏、`player.bump_kick`、`hud.bump_flash`），改为实现 `docs/house-spec.md` §8.3 的 **phasing（卡墙虚化）**。⚠️ `house-spec.md:770` 原本要求 phasing 与楼层方案 C 同期 ⇒ 本次**只做 phasing，不做楼层方案 C**（取舍写在 L17 任务书 §2/§3.8）。",
 "2. ✅ **四份新任务书已写（2026-11-26）**：**L17 phasing**（`docs/PROMPT-phasing-exec.md`）、**L15 归档表+结局**（`docs/PROMPT-ending-form-exec.md`）、**L16 双日记渲染**（`docs/PROMPT-diary-render-exec.md`）、**A4 重排线**（`docs/PROMPT-a4-rebuild-exec.md`）。",
 "3. 🔴 **并行排线（同一时刻最多三条）**：**A4 重排线**（写 `data/frames.json`）／**L15**（新建 `scripts/ending_*.gd`）／**L16**（新建 `scripts/diary_*.gd`）—— L15 与 L16 与地图线**文件零重叠**。⚠️ **接线顺序**：L15／L16 都要在最后改 `scripts/main.gd`，L17 也要改 ⇒ **L17 先交卷，L15／L16 再各自交接线段**；L15 与 L16 不能同时做接线。",
 "4. 🔴 **两组二选一**：L17 vs L8（都改 `scripts/world_view.gd`）；A4 重排线 vs A1–A3 重排线（都改 `data/frames.json`）。",
 "",
])
insert_after(ov, "| **L14 A5 落地** | `data/frames.json` ＋ `_ref/houses/houses_data.json` ＋ `scripts/evidence_store.gd` ＋ `docs/story.md` ＋ 两个测试文件的世界尺寸常量 |", [
 "| **A4 重排线** | `data/frames.json`（**只改 a4_2001 一帧**） | ✅ **任务书已写，可派**（`docs/PROMPT-a4-rebuild-exec.md`）；⚠️ 与 A1–A3 重排线**串行**（同写 frames.json） |",
 "| **L15 归档表 + 结局变体** | 新建 `scripts/ending_store.gd`／`ending_report.gd`／`ending_form.gd` ＋ `_mdtest/ending_check.gd` | ✅ **任务书已写，可派**；文件零重叠，**可与地图线并行**；⚠️ 接线段要等 L17 |",
 "| **L16 双日记渲染** | 新建 `scripts/diary_markup.gd`／`diary_page.gd`／`diary_view.gd`／`diary_texts.gd` ＋ `_mdtest/diary_render_check.gd` | ✅ **任务书已写，可派**；与 L15 文件零重叠可同时跑；⚠️ 不能与 L15 同时改 `scripts/main.gd` |",
 "| **L17 phasing/虚化** | `scripts/timeline.gd` ＋ `scripts/player.gd` ＋ `scripts/world_view.gd` ＋ `scripts/main.gd` ＋ `scripts/hud.gd` | ✅ **任务书已写，可派**（用户拍板删「顶住了」只做虚化）；🔴 与 L8 二选一（争 `world_view.gd`） |",
])

write(OV, ov)

# ============================ 待解决事项 ============================
pd = read(PD)

# 状态行
i = [k for k, l in enumerate(pd) if l.startswith("> **当前状态**")][0]
pd[i] = ("> **当前状态**：2026-11-26 10:10 · 仓库 HEAD `3f5bc49`（本地；远端仍 `b0798da`，按用户定时指令推）· "
 "🔴 **最新快照＝`docs/RESUME-2026-11-25-1720.md`**（旧快照 `docs/RESUME-2026-11-25.md` 已标过期）｜"
 "🔴 **用户 2026-11-26 拍板：「顶住这点去掉，只做虚化。顶住这点是你自己补上的我未批准的内容」** ⇒ 「顶住了」机制作废，改为实现 `docs/house-spec.md` §8.3 的 phasing（任务书 `docs/PROMPT-phasing-exec.md` 已写；**只做 phasing，不做楼层方案 C**）｜"
 "✅ **四份新任务书已写（2026-11-26）**：L17 phasing（`docs/PROMPT-phasing-exec.md`）／L15 归档表+结局（`docs/PROMPT-ending-form-exec.md`）／L16 双日记渲染（`docs/PROMPT-diary-render-exec.md`）／**A4 重排线**（`docs/PROMPT-a4-rebuild-exec.md`）｜"
 "🔴 **A4 重排几何已实测 errors=0**：shen_a4(64,416)／market(2144,320)（与 A5 同址）／zhou_a4(2272,1984)／zheng_a4(2304,2400)／井(2048,832) r32／槐(2048,1664) r96／界碑(3520,1536)／竖车道+环道+内岛+山×3+路标×4 与 A5 帧逐点一致｜"
 "🔴 **并行排线**：A4 重排线（写 frames.json）‖L15‖L16 三条可同批；⚠️ L17 vs L8 二选一（争 `world_view.gd`）、A4 重排 vs A1–A3 重排二选一（争 frames.json）、L15/L16 的 `main.gd` 接线要等 L17｜"
 "L14（A5 落地）已交付并验收 ✅（证物口径 25 卡/56 观察已回写）｜L9 已交卷但总策划尚未独立复核｜L8 资产接线任务书未写｜实机 Shift+E 最终验收未做")

# §1.6 加 Q6
insert_after(pd, "| **Q5**<br>✅已拍板 |", [
 "| **Q6**<br>✅已拍板 | **已拍板（2026-11-26）：「顶住了」机制作废，只做 phasing（卡墙虚化）**（原问题：时间轴推动时角色卡进墙，应该虚化还是推不过去？两者都有设计来源——「顶住了」出自 `docs/HANDOFF.md:239-249` §3.4，「卡墙虚化」出自 `docs/house-spec.md:757-771` §8.3＝用户 2026-11-19 m01214 拍板） | **只做 phasing，删掉顶住了**（用户原话：「顶住这点去掉，只做虚化。顶住这点是你自己补上的我未批准的内容」）⇒ 任务书 `docs/PROMPT-phasing-exec.md` 已写 | **代码层**：`scripts/timeline.gd:78-92` bump 分支、`scripts/main.gd:_on_bump`、`scripts/world_view.gd` 震屏/`player.bump_kick`/`hud.bump_flash`、两个测试文件｜**文档层**：`docs/HANDOFF.md:40/:239-249/:760`、`docs/house-spec.md:216/:230/:741/:760`｜⚠️ `house-spec.md:770` 原要求 phasing 与楼层方案 C 同期 ⇒ 本次只做 phasing，方案 C 延后 |",
])

# §4 表五行状态
sub1(pd, "| **A4 重排线**（新，P0） | 🔴 **待写任务书** —— A4 的超市/井/槐必须与 A5 同址，否则「位置不变」破 | — | `data/frames.json`（与 A1–A3 重排线串行） |",
        "| **A4 重排线**（P0） | ✅ **任务书已写，可派**（`docs/PROMPT-a4-rebuild-exec.md`）—— A4 超市/井/槐与 A5 同址、界碑到工地东边、补竖车道/环道/内岛/山/路标；几何已实测 errors=0 | 交付物＝`data/frames.json` 的 a4_2001 帧（只改这一帧）＋ `_mdtest/a4_rebuild_check.gd` ＋ `docs/FEEDBACK-a4-rebuild-exec.md` | `data/frames.json`（与 A1–A3 重排线**串行**） |")
sub1(pd, "| **L15 归档表 + 结局变体**（新） | 🟡 任务书待写（可与地图线并行，文件零重叠） | — | 新建 `scripts/ending_*.gd` + `_mdtest/ending_check.gd` |",
        "| **L15 归档表 + 结局变体** | ✅ **任务书已写，可派**（`docs/PROMPT-ending-form-exec.md`）—— 真相全在 `docs/story.md` §10.0–§10.5；⚠️ 接线段要等 L17 | 新建 `scripts/ending_{store,report,form}.gd` + `_mdtest/ending_check.gd`（＋ `scripts/main.gd` 仅接线） |")
sub1(pd, "| **L16 双日记渲染**（新） | 🟡 任务书待写（可与地图线并行，文件零重叠） | — | 新建 `scripts/diary_*.gd` + `_mdtest/diary_check.gd` |",
        "| **L16 双日记渲染** | ✅ **任务书已写，可派**（`docs/PROMPT-diary-render-exec.md`）—— 语法 `docs/diary-markup.md` ＋ 原稿 `docs/story.md` 附一；🔴 删除线必须自绘 | 新建 `scripts/diary_{markup,page,view,texts}.gd` + `_mdtest/diary_render_check.gd`（＋ `scripts/main.gd` 仅接线） |")
sub1(pd, "| **L17 phasing/虚化**（新） | 🟡 任务书待写 —— 需楼层方案 C 同期，且与 L8 争 `scripts/world_view.gd` | — | `scripts/timeline.gd`、`scripts/player.gd`、`scripts/world_view.gd`、`scripts/main.gd` |",
        "| **L17 phasing/虚化** | ✅ **任务书已写，可派**（`docs/PROMPT-phasing-exec.md`）—— 用户 2026-11-26 拍板删「顶住了」只做虚化；⚠️ 与 L8 争 `scripts/world_view.gd` ⇒ 二选一；⚠️ 只做 phasing，楼层方案 C 不做 | `scripts/timeline.gd`、`scripts/player.gd`、`scripts/world_view.gd`、`scripts/main.gd`、`scripts/hud.gd` |")

write(PD, pd)
print("OK  overseer lines:", len(read(OV)), " pending lines:", len(read(PD)))
for p in (OV, PD):
    s = io.open(p, encoding="utf-8").read()
    assert s.count("\ufffd") == 0, ("FFFD in", p)
print("no U+FFFD")
