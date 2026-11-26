# -*- coding: utf-8 -*-
"""修 docs/待解决事项.md §4 表里 L15/L16/L17 三行：补回缺失的「文件域（独占）」列（表头 4 列）。"""
import io

P = "docs/待解决事项.md"
ls = io.open(P, encoding="utf-8").read().split("\n")

FIX = {
 "| **L15 归档表 + 结局变体** |":
   "| **L15 归档表 + 结局变体** | ✅ **任务书已写，可派**（`docs/PROMPT-ending-form-exec.md`）—— 真相全在 `docs/story.md` §10.0–§10.5；⚠️ 接线段要等 L17 | 新建 `scripts/ending_{store,report,form}.gd` + `_mdtest/ending_check.gd`（＋ `scripts/main.gd` 仅接线） | `scripts/ending_*.gd`、`_mdtest/ending_check.gd`（＋ `scripts/main.gd` 仅接线） |",
 "| **L16 双日记渲染** |":
   "| **L16 双日记渲染** | ✅ **任务书已写，可派**（`docs/PROMPT-diary-render-exec.md`）—— 语法 `docs/diary-markup.md` ＋ 原稿 `docs/story.md` 附一；🔴 删除线必须自绘 | 新建 `scripts/diary_{markup,page,view,texts}.gd` + `_mdtest/diary_render_check.gd`（＋ `scripts/main.gd` 仅接线） | `scripts/diary_*.gd`、`_mdtest/diary_render_check.gd`（＋ `scripts/main.gd` 仅接线） |",
 "| **L17 phasing/虚化** |":
   "| **L17 phasing/虚化** | ✅ **任务书已写，可派**（`docs/PROMPT-phasing-exec.md`）—— 用户 2026-11-26 拍板删「顶住了」只做虚化；⚠️ 与 L8 争 `scripts/world_view.gd` ⇒ 二选一；⚠️ 只做 phasing，楼层方案 C 不做 | `scripts/timeline.gd`、`scripts/player.gd`、`scripts/world_view.gd`、`scripts/main.gd`、`scripts/hud.gd` | `scripts/timeline.gd`、`scripts/player.gd`、`scripts/world_view.gd`、`scripts/main.gd`、`scripts/hud.gd`（🔴 与 L8 争 `world_view.gd`） |",
}

n = 0
for i, l in enumerate(ls):
    for k, v in FIX.items():
        if l.startswith(k):
            assert l.count("|") == 4, (k, l.count("|"))
            ls[i] = v
            n += 1
assert n == 3, n

io.open(P, "w", encoding="utf-8", newline="\n").write("\n".join(ls))
s = io.open(P, encoding="utf-8").read()
assert s.count("\ufffd") == 0
print("fixed rows:", n)
for i, l in enumerate(ls, 1):
    if l.startswith("| **L15") or l.startswith("| **L16") or l.startswith("| **L17") or l.startswith("| **A4 重排线**"):
        print(i, l.count("|"), l[:70])
