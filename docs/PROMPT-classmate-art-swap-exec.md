# 执行提示词 · 同学资产一次性替换线（把 38 张同学图换进游戏）

> 用途：整段复制给**一条新会话**执行。本会话（总策划）不亲自改 PNG。
> 上游依据：`docs/ART-MAPPING-classmate.md` §6 替换建议清单、`docs/FEEDBACK-planner-art-import.md` 阻塞③、`docs/FEEDBACK-asset-consumption-exec.md` 拍板 A。
> 用户已拍板（2026-11-22）：**①id 绑定走近似匹配、②等能看到贴图后一次性全换、③C 档暂缓**。
> 现在①②均已完成（消费线 `aac2115` 已提交、贴图在画面里看得到），**执行时机已到**。

---

## 0. 开工前必读（先核再动，别凭印象）

1. **确认 HEAD ≥ `80bb223`**（消费线提交+反馈文档），且 `scripts/asset_draw.gd` 已在版本库。
   - 若 `scripts/world_view.gd` 里没有 `_art_walls()` / `_draw_furniture()` 的贴图分支 → **停下来问本人**，不要自己补代码。
2. **只读**以下文件，不许改：`docs/ART-MAPPING-classmate.md`（清单权威）、`_ref/art/_assets_a1a3/_a1a3_assets.json`（manifest）、`houses_data.json`、`data/frames.json`、`scripts/*.gd`、`assets/village/houses/**`。
3. 工作区此刻还有其它线在跑（场景搭建2 写 frames.json、场景设计4 写 houses_data.json、本人删的 17 张旧图 D 状态）。**你的写入范围只有 `assets/village/props/` 下的 PNG**，别的一律不碰。

## 1. 目标

把同学那批**精细描边、3/4 视角**的 PNG 一次性替换进 `assets/village/props/`，
让游戏里 A1–A3 的家具从「AI 平涂色块」变成「同学手绘质感」。
**只换文件，不动任何代码、数据、manifest** —— 消费点已经就绪，换完立刻能在画面上看到。

## 2. 替换范围（以 `docs/ART-MAPPING-classmate.md` §6 表格为准，共 38 个唯一 id）

| 类别 | 数量 | 动作 |
|---|---|---|
| **尺寸一致**（AI 图存在且像素尺寸相同） | 31 | 用 `assets/village/_classmate/props/<id>.png` **覆盖** `assets/village/props/<id>.png` |
| **AI 无此图**（manifest 有 id，AI 侧未出图） | 7 | 从 `_classmate/props/` **复制**到 `assets/village/props/<id>.png`（纯补位，不是覆盖） |

- 7 个补位 id（文档 §6 标「AI 无此图」）：`gui_1x1` / `xiaozhuo_1x1` / `hongzhuo_1x1` / `shuzhuo_1x1_top` / `baizhuo_1x1` / `changzhuo_2x1` / `cantang_3x1`。
- **不含 C 档**：房屋、地皮、树、主角一律不换（用户拍板暂缓）。
- **不含 `_variants/` 里的 45 张变体**：只取 `_classmate/props/` 下的 39 张主图。
- 清单表格里没有的 id，**不要自己发挥去换**。

## 3. 风险点：这 7 张先判再做（文档 §6.1）

按下面规则处理，**判不准就跳过并写进报告，绝不硬换**：

| id | 规则 |
|---|---|
| `shuangrenchuang_3x3` | 同学只画了 2×2，**没有 3×3 → 跳过不换** |
| `gui_1x1` | 语义是「矮柜」，与 `gui_1x2` 竖柜不是一件 → 按补位纳入，但在报告里标「语义待确认」 |
| `luokuang_1x1` / `deng_1x1` | 语义近似（箩筐/草墩），按补位纳入，报告标注 |
| `shuzhuo_1x1` vs `shuzhuo_1x1_top` | 侧视/俯视两张，**各自按 id 对位，不可互换** |
| `chaihuozao_1x1` | 与 `zaotai_*` 三个灶台 id 重合 → **跳过，等本人定** |
| `danrenchuang_1x2` | 同学图偏「旧木床」调性，manifest 用的是常用单人床 → **跳过，等本人定** |

⇒ 实际执行数量会少于 38，**跳过的一定要在最终报告里列清楚原因**。

## 4. 执行步骤（严格顺序）

1. **备份**：把将被覆盖的 31 张 AI 图先复制到 `assets/village/props/_legacy_ai/`
   （照之前 `_legacy_16px/` 的做法，保留 `.import` 一并复制），保证可回滚。
   ⚠️ 取 git 历史里的旧图**不要用 PowerShell `>` 重定向**（会损坏 PNG），用 `cmd /c "git show ... > file"`。
2. **替换**：按 §2/§3 判定结果逐个覆盖或复制。用 `Copy-Item`，保持文件名与 manifest id 完全一致。
3. **尺寸校验**：逐张比对替换前后像素尺寸；清单说「尺寸一致」的必须一致，不一致立刻停止并报告。
4. **Godot 导入**：跑一次 `godot --headless --import`，确认 EXIT=0、无导入错误。
5. **截图对照**（关键，证明「看得见的替换」）：
   - 复用现有截图器 `_mdtest/asset_shot.gd`，**但输出目录另建** `_mdtest/assets/swap_before/` 与 `swap_after/`；
   - **绝对不要覆盖** `_mdtest/assets/*.png` 下消费线已提交的 11 张截图。
   - 至少覆盖：`a1_shen_house` / `a1_mill_road` / `a2_zhou_house` / `a3_mill` 四处家具密集视角。
6. **六套回归**：greybox / sort / camera / display / hud / asset_draw_check 全跑。
   判回归**看关键字不看退出码**（沙箱固有噪声 `Failed to read the root certificate store.` + `[exit code:1]`）：
   `WORLD_OK` / `SORT_CHECK_DONE fails=0` / `CAMERA fails=0` / `HUD fails=0` / `ASSET_DRAW_CHECK_DONE fails=0`。
7. **present** 替换前后对照图给本人看，等确认。

## 5. 文件边界

- ✅ **写**：`assets/village/props/<id>.png`（38 个 id 内的文件）、`assets/village/props/_legacy_ai/`（备份）、`_mdtest/assets/swap_{before,after}/`（对照图）、`docs/HANDOFF-classmate-art-swap.md`（交接文档，新建）。
- ❌ **不碰**：`scripts/*.gd`、`houses_data.json`、`data/frames.json`、manifest、`assets/village/houses/**`、`_classmate/**`（只读源）、`美术资产/**`、任何 `.import`（Godot 自动生成的除外）。

## 6. 提交纪律

- **绝对不要 `git add -A`**（工作区里有其他四条线的产物）。
- 只精确 add：`git add -- assets/village/props/ _mdtest/assets/swap_before/ _mdtest/assets/swap_after/ docs/HANDOFF-classmate-art-swap.md`。
- 提交前 `git status --short` 复核：暂存区里**不应出现** `frames.json` / `houses_data.json` / `scripts/*.gd` / `美术资产/` 的删除。
- 提交后把 hash 回给本人。

## 7. 输出要求（结束时）

1. 替换统计：覆盖 31 / 补位 7 / 跳过 N（逐条列 id + 原因）。
2. 尺寸校验结果、Godot 导入结果、六套回归关键字。
3. 替换前后对照图路径（present 给本人）。
4. 交接文档 `docs/HANDOFF-classmate-art-swap.md`。
5. 最多 **3 个**需要本人拍板的问题（例如跳过的几张怎么处理）；不要罗列长串问号。
