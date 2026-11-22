# 反馈文档 · 美术同学资产替换线（致「项目总策划」会话）

> 提交方：美术同学资产替换线（本线，2026-11-22 21:19 交付）
> 接收方：项目总策划会话（负责统筹并行、划边界、验收、提交）
> 目的：汇报**替换线已执行并已提交** + 校验结果 + **三条待拍板问题**，供总策划验收与排期。
> 本线**已 commit**：`33900e9`（当前 HEAD 为并发线 `2382ceb`，我的提交是其父）。
> 授权链：本人 2026-11-22 拍板 supersede 了导入线任务书第 26/99 行「不覆盖 AI 图 / 替换等本人拍板」——
> 因消费点已就绪（`aac2115` 已提交、游戏里看得到家具贴图），**授权执行替换**。执行依据 `docs/PROMPT-classmate-art-swap-exec.md`。

---

## 0. 一句话现状

同学手绘资产已经**真正替换进游戏**并**提交进版本库**：29 张覆盖 + 7 张补位，游戏内四处密集视角截图确认画面变化（8/11 视角有差异）；
原 AI 图 29 张已全量备份到 `assets/village/props/_legacy_ai/`，可随时回滚。
**与导入线反馈文档（`docs/FEEDBACK-planner-art-import.md`）最大的不同**：那条说的「阻塞①消费点零引用」已由 `aac2115` 解决，本线不再是「看不见的替换」。

---

## 1. 本线已交付（已实测通过，可直接验收）

| 产物 | 位置 | 规模 | 校验 |
|---|---|---|---|
| 替换提交 | commit `33900e9` | **135 文件** | 在版本库，`git log` 可见 |
| 覆盖（AI 图 → 同学图） | `assets/village/props/` | **29 个 id** | 尺寸与 manifest 一致，md5 与源图一致 |
| 补位（AI 无图 → 同学图） | `assets/village/props/` | **7 个 id** | `.import` 由 Godot 自动生成 |
| 跳过（保持原 AI 图） | `assets/village/props/` | **3 个 id** | md5 == 备份，证明未动 |
| 原 AI 图备份 | `assets/village/props/_legacy_ai/` | **58 文件**（29 PNG + 29 .import） | 齐全，可回滚 |
| 替换前/后截图 | `_mdtest/assets/swap_before/` / `swap_after/` | 各 11 PNG + .import | **未覆盖**消费线已提交的 11 张 `_mdtest/assets/*.png` |
| 对照拼图 | `lab/_swap_compare.png` | 1250×3130 | 11 视角 before/after 并排 |
| 交接文档 | `docs/HANDOFF-classmate-art-swap.md` | 82 行 | 含统计/校验/边界/待拍板 |
| 执行与校验脚本 | `lab/_swap_execute.py` / `_swap_verify.py` / `_swap_compare.py` / `_swap_shot.gd` | 可重跑 | 独立复核 PASS |

**开工前闸门核对**：HEAD=`3f36587`（≥ 提示词要求的 `80bb223`）✅；
`scripts/world_view.gd` 有 `_art_walls()`（第 470 行）与 `_draw_furniture()`（第 540 行）贴图分支 ✅；
`scripts/asset_draw.gd` 在版本库 ✅ —— 否则按提示词必须停下问本人。

### 替换明细

**覆盖 29**（AI 图存在、尺寸一致，直接换文件）：
`anban_2x1` / `baxianzhuo_2x2` / `chaidui_1x1` / `changdeng_1x2` / `danrenchuang_2x1` / `deng_1x1` / `denglong_1x1` / `dunbianqi_1x2` / `gui_1x2` / `gui_2x1` / `jiutan_1x1` / `luokuang_1x1` / `maokeng_1x1` / `muxiang_1x1` / `paiwei_1x1` / `penjing_1x1` / `shuangrenchuang_2x2` / `shuichi_1x1` / `shuigang_1x1` / `shuipen_1x1` / `shujia_1x2` / `shujia_2x2` / `shuzhuo_1x1` / `shuzhuo_2x1` / `wangui_1x2` / `xiaozhuo_2x1` / `yi_1x1` / `yigui_1x2` / `zhenglong_1x1`

**补位 7**（manifest 有 id 但 AI 侧无图，纯新增）：
`gui_1x1` / `xiaozhuo_1x1` / `hongzhuo_1x1` / `shuzhuo_1x1_top` / `baizhuo_1x1` / `changzhuo_2x1` / `cantang_3x1`

**跳过 3**（判不准按提示词 §3 跳过，不自行决断）：

| id | 跳过原因 | 现状 |
|---|---|---|
| `chaihuozao_1x1` | 与 `zaotai_1x4` / `tupi_zaotai_2x1` / `daota_zaotai_1x4` 三个灶台 id 语义重合，不知该顶替哪个 | 仍是原 AI 图 |
| `danrenchuang_1x2` | 同学图偏旧木床调性，而 manifest 这个是常用单人床，风格/语义不符 | 仍是原 AI 图 |
| `shuangrenchuang_3x3` | 同学只画了 2×2，本线不做缩放拉伸 | 仍是原 AI 图 |

### 校验结果（全部实测通过）

- **尺寸/内容**：`lab/_swap_verify.py` → `[PASS] covered=29 added=7 backup_png=29 skipped=3`；36 个目标文件 md5 == 源图；跳过组未动；尺寸符合 manifest `w*32 × (h*32+32)`。
- **Godot 导入**：`godot --headless --import --path .` → **EXIT=0**（仅 3 条沙箱编辑器目录噪声：`Failed to read the root certificate store.` / `editor_settings-4.7.tres` 不可写，非项目问题）。
- **截图对照**：11 视角中 **8 个有变化**；提示词要求的四处密集视角 `a1_shen_house` / `a1_mill_road` / `a2_zhou_house` / `a3_mill` **全覆盖且均有变化**。
  3 个 0% 差异视角（`a3_field_road` / `a1_mill_outside` / `a3_lu_ruin`）属无被换家具入镜的正常情况，非替换失败。
- **六套回归**（看关键字，不看退出码）：greybox `WORLD_OK=true` / `START_OK=true` / `HOTSPOTS_OK=true` / `REACH_OK=true`；
  sort `fails=0`；camera `fails=0`；display 无 FAIL 且 `CONTENT_SCALE_*` 全匹配；hud `fails=0`；asset_draw `fails=0`。

---

## 2. 与导入线反馈文档的状态差异（供总策划更新全局台账）

| 导入线反馈（2026-11-22 15:57） | 本线交付时（2026-11-22 21:19） |
|---|---|
| 阻塞①：props/scene 零消费点，`asset_draw.gd` 不存在 | **已解除** —— 消费点接入线 `aac2115` 已提交，游戏里能看到家具贴图 |
| 阻塞③：替换待拍板 | **已解除** —— 本人 m00631 授权，本线已执行并提交 `33900e9` |
| 阻塞②：manifest id ↔ `houses_data.json` 运行时摆放无硬绑定 | **本线未触碰、未验证**，仍挂起（属数据线，不在本线边界内） |

> 请总策划据此更新并行台账：①②③ 中 ① 和 ③ 已闭环，② 仍开放。

---

## 3. 本线的写入边界（已自查，按提交白名单精确 add）

**本线只动过**：
- `assets/village/props/` 下 29 覆盖 + 7 补位 PNG（及其 `.import`）
- `assets/village/props/_legacy_ai/`（29 PNG + 29 .import，备份）
- `_mdtest/assets/swap_before/` / `swap_after/`（各 11 PNG + .import）
- 新增 `docs/HANDOFF-classmate-art-swap.md`
- `lab/` 下执行脚本、报告与对照图（`_swap_*`，未入库）

**本线没碰**：`scripts/*.gd`、`_ref/houses/houses_data.json`、`data/frames.json`、
`assets/village/houses|scene/`、`美术资产/` 源目录、导入线映射表文档与其它既有文档。

**提交纪律**：**未用 `git add -A`**。按 `lab/_swap_report.json` 生成精确文件清单 `git add`；
暂存前检查确认无 `frames.json` / `houses_data.json` / `scripts/` / `美术资产/` / `_legacy_16px/` / `lab/` 混入。
工作区里其它并发线的产物（A5 玩具店 v5、美术资产 D 状态 17 张、场景搭建2 的 frames.json 等）**全部保持未暂存/未碰**。

> 本反馈文档 `docs/FEEDBACK-classmate-art-swap.md` **不在提交白名单内，仍是未跟踪文件**，请总策划决定是否纳入版本库。

---

## 4. 请总策划回复的三件事

1. **跳过 2 张怎么定**：`chaihuozao_1x1` 要顶替 `zaotai_1x4` / `tupi_zaotai_2x1` / `daota_zaotai_1x4` 中的哪一个？
   `danrenchuang_1x2` 是否要接受「旧木床」调性（那就换）；若不接受，保留 AI 图。
2. **`gui_1x1` 矮柜与 `gui_1x2` 竖柜语义不同**，补位的 `gui_1x1` 是否符合预期？不符合就撤掉补位。
3. **回滚预案是否要落地**：`_legacy_ai/` 有 29 张原图，要不要现在就出一份一键回滚脚本（含 `.import`）？
   本线未擅自生成，等拍板。

---

*本反馈事实全部经过实测（2026-11-22 21:19）。数值可复算：*
*`git log --oneline`（`33900e9` / HEAD `2382ceb`）、`lab/_swap_verify.py`（`PASS 29/7/29/3`）、*
*`lab/_swap_compare.png`（11 视角 / 8 有变化）、六套回归日志 `lab/_swap_*_check.txt`、*
*`_legacy_ai/` 文件数 58、`lab/_swap_import.txt`（EXIT=0）。*
