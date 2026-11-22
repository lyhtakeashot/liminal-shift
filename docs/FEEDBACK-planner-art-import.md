# 反馈文档 · 美术同学资产导入适配线（致「项目总策划」会话）

> 提交方：美术同学资产导入适配线（本线，2026-11-22 15:57 交付）
> 接收方：项目总策划会话（负责统筹并行、划边界、验收、提交）
> 目的：汇报本线已交付内容 + **三条阻塞项 + 一条被本线实测暴露的上游数据缺口**，供总策划排期。
> 本线**未 commit**，未覆盖任何既有资产，全部产物在隔离目录内，等总策划统一提交。

---

## 0. 一句话现状

同学手绘资产已**全部盘点映射并适配成游戏规格**（84 张 PNG 就位），但**游戏里一张都看不到** —— 因为引擎侧对 props/scene 零消费点；
且 manifest 的家具 id 与 `houses_data.json` 的运行时摆放**没有硬绑定**（实测 551 条家具里 298 条按名匹配不到 manifest id），
这两件事不解决，本线的产物无法变成画面。

---

## 1. 本线已交付（已实测通过，可直接验收）

| 产物 | 位置 | 规模 | 校验 |
|---|---|---|---|
| 映射表文档 | `docs/ART-MAPPING-classmate.md` | 400 行 | 74 张源图逐张登记，无遗漏 |
| 游戏规格资产 | `assets/village/_classmate/props/` | **39 主图 + 45 变体 = 84 张 PNG** | `lab/_cls_check.py`：**通过 168 项 / 问题 0** |
| manifest 扩容 | `_ref/art/_assets_a1a3/_a1a3_assets.{json,csv}` | props **84 → 91** | `git diff` 纯新增 **168 行 / 0 删除** |
| 对照预览 | `lab/_classmate_compare_a.png` / `_a2.png` / `_b.png` | 19 + 4 + 60 格 | 每格左=同学手绘、右=AI 程序化图 |
| C 档接触表 | `lab/_cls_c_sheet.png` | 19 格 | 房屋/地皮/树/主角 目视核对 |
| 脚本 | `lab/_cls_gen_a.py` / `_cls_atlas_scan.py` / `_cls_atlas_pick.py` / `_cls_check.py` / `_cls_compare.py` / `_cls_doc.py` | 可重跑 | 幂等 |

**规格口径（DECIDE D6）**：交付画布 = 占地宽×32 × (占地高×32 + 32)，透明补在顶部，内容贴底，源像素 1:1 不重采样。
**Godot 导入**：`godot --headless --import --path .` → **EXIT=0**，84 张全部生成 `.import`
（仅 3 条无关告警：编辑器证书 / `editor_settings-4.7.tres` 不可写，非项目问题）。

### 三档分治结果

| 档位 | 源文件 | 已映射 | 落盘 |
|---|---|---|---|
| A 单件家具 | 23 张 | 23 | 19 主图 + 4 变体 |
| B 图集切片 | 32 张图集 | 13 张图集 / 60 切片 / 27 个 id | 20 主图 + 41 变体 |
| C 房屋·地皮·树·主角 | 19 张 | 19（**只出方案**） | 0（按纪律不落盘） |

### manifest 新增 7 个 id（用户已拍板「加新 id」）

`xiaozhuo_1x1`(P85) / `hongzhuo_1x1`(P86) / `baizhuo_1x1`(P87) / `shuzhuo_1x1_top`(P88) /
`gui_1x1`(P89) / `changzhuo_2x1`(P90) / `cantang_3x1`(P91)

其中 `shuzhuo_1x1_top` 是为拆开语义冲突新增的：同学的「短桌3」（俯视摊纸笔）与「书桌1」（侧视带抽屉）
原本都指向 `shuzhuo_1x1`，拆成两个视角 id 后不再互串。

---

## 2. 三条阻塞项（都需要总策划拍板或派工）

### 阻塞 ①（最要紧）props/scene/主角在引擎里零消费点 → 84 张图进游戏看不见

实测 `scripts/world_view.gd` 全文件只有 **1 处** `draw_texture_rect`（第 583 行，roof），
`assets/village/props/`（84 张 AI 图）与本线新交付的 84 张同学图**完全没有引用点**。
`assets/village/scene/`（20 张：河/路/田/井/树/地面）同样零引用，现在靠 `frames.json` 的 polygon/rect 画色块。
`player.gd` 主角是纯代码 `draw_self()` 画圆。

这正是 `docs/PROMPT-asset-consumption-exec.md`（消费点接入线，commit `5e353e4`）要解决的事，但**该线尚未开工**：
`scripts/asset_draw.gd` 与 `_mdtest/asset_draw_check.gd` 目前**都不存在**。

> **请总策划**：确认消费点接入线是否立刻开工。注意它与视觉机制线**同写 `scripts/*.gd`**，是最严重的撞车点，
> 而视觉机制线**当前仍在进行中**（`scripts/world_view.gd` / `house_shape.gd` / `player.gd` / `main.gd` 均有未提交改动）。
> 两者必须**串行**，或由总策划指定文件级写入顺序。

### 阻塞 ② manifest id 与运行时摆放没有硬绑定（**本线实测新发现，建议单开一条线**）

`_ref/houses/houses_data.json`（18 栋）的家具条目**没有 `id` 字段**，只有 `name` / `short` / `rect` / `clue` / `zone` 等。
本线用 `short` → manifest `short` 做了一次全量匹配（脚本产出 `lab/_cls_bind_report.txt`）：

```
total furniture entries: 551
matched by short->manifest id: 253
unmatched: 298
distinct manifest ids reachable via short: 85 / 91
```

未匹配的 298 条集中在**学校/施工类**场景词上（`跑道`×56、`课桌`×30、`未拆封货架`×18、`货架`×5、`茶几`×5 …），
**这些 id 在 manifest 里根本不存在** —— manifest 91 条是「A1–A3 的 12 栋房」的资产清单，
而 `houses_data.json` 已扩到 A4/A5（学校 `school` 21×16 楼等），**资产清单没跟上数据**。

**这条不是本线的猜测，是消费点接入线自己的前提对不上**：
`docs/PROMPT-asset-consumption-exec.md` §3.2 写的是「把每个家具的色块替换成 `assets/village/props/<id>.png`（**从 `f["id"]` 取**）」——
但 `houses_data.json` 的家具条目里**没有 `id` 键**。也就是说照该提示词实现会取到空值。
`85 / 91` 说明按 `short` 近似能覆盖到 91 个 manifest id 中的 85 个，够画但不够准。

> **请总策划**：这意味着「把 props 贴到家具位置上」这一步现在**做不到精确对齐**，只能按名近似。
> 需要决定：① 给 `houses_data.json` 家具补 `id` 字段（改数据，影响面大）；② 扩 manifest 覆盖 A4/A5 家具；
> ③ 先用近似名匹配做过渡。三选一，且**这必须排在消费点接入之前**，否则贴图会贴错位置。

### 阻塞 ③ 替换动作本身待拍板（本线**未执行任何替换**）

替换可行性已算清（文档 §6）：

| 判定 | 数量 | 说明 |
|---|---|---|
| **尺寸一致** | **31** | AI 图与同学图画布完全相同 → 换文件即可 |
| 尺寸不同 | 0 | — |
| **AI 无此图** | **7** | manifest 有 id 但 AI 侧没出图 → 属**纯补位**，不是替换 |

（共 38 个唯一 id；另有 45 张同学变体可作备选。）

**风格差距是硬伤**：同学图是**带描边、有高光/阴影的精细像素画**，多为**正面/等距 3/4 视角**；
AI 图是**平涂色块**、**俯视视角**。同屏混用会明显不协调 ⇒ 建议**一次性全换**而不是挑几张换。

⚠️ **强烈建议不要现在就换**：在阻塞 ① 未解决前替换，等于做一次**看不见的替换**（改了文件，屏幕上什么都没变），
还会让后续对比排查变复杂。

---

## 3. C 档（19 张）只出方案，等排期

本线按纪律**未落盘**任何 C 档产物，方案已登记在 `docs/ART-MAPPING-classmate.md` §3：

- **房屋 13 张** → 拼装方案：`屋檐1/2/3.png` 作 roof 层、`墙面.png`（6×6 墙砖）作墙层、`地板.png`（4×4 地砖）作地层，
  合成 D6 规格整栋（例 `lu_house` 20×13 → 640×448）。`GK_B/D_CC_1.png` 是 24×24 格自成体系，与游戏 20×13/18×13 不匹配。
- **地皮 3 张** → 需重切成单格 32×32 才能对上 `scene/ground_*_tiles.png`；`GK_C_CC_1.png` 是 511×511 非 32 倍数。
- **树 2 张** → `tree.png` 96×128（3×4），对应 scene 的 tree_a1/a2/a3 三态，但游戏侧树占位比源图大。
- **主角 1 张** → `Sprite-主角-Sheet.png` = **1152×32 = 36 帧等距 32px 步进**，但**无方向分组标记**，需同学补一张帧序表；
  且 `player.gd` 纯代码画圆，**无贴图消费点**（与阻塞 ① 同源）。

> **请总策划**：C 档要不要立项？（工作量与风格对齐成本都高，且同样卡在阻塞 ①）
> 建议顺序：**先解 ①（消费点）→ 再解 ②（id 绑定）→ 然后才谈 C 档拼装与主角序列帧**。

---

## 4. 风格统一的一个额外建议

同学图与 AI 图的视角差异（3/4 vs 俯视）意味着**混用必然不协调**。
若决定走「整体换」，建议一次性把 manifest 里 91 个 id 的图全部换成同学风格（或反过来把同学图统一成 AI 风格），
而不是分批换。若只换一部分，需要先定一个过渡方案（例如先统一描边 / 先统一视角）。

---

## 5. 本线的写入边界（已自查，未越界）

**本线只动过**：
- 新增 `docs/ART-MAPPING-classmate.md`
- 新增 `assets/village/_classmate/`（84 PNG + 84 .import）
- 新增 `lab/_cls_*.py` / `lab/_cls_*.json` / `lab/_cls_*.png` / `lab/_cls_*.txt`
- manifest **仅新增** 7 条 props（P85–P91），未删改任何既有条目

**本线没碰**：`scripts/*.gd`、`_ref/houses/houses_data.json`、`data/frames.json`、
`assets/village/props|houses|scene/`、`美术资产/` 源目录、其它任何既有文档。
**未 commit**（等总策划统一提交）。

工作区里 `scripts/*.gd` 的未提交改动、`_mdtest/` 的新文件、`assets/village/props/_legacy_16px/*.import` 等
**来自其它并发线**，不是本线产出。总策划 `git add` 时请按路径精确挑选，
建议提交信息：`feat(art): 美术同学资产导入适配线（84 张 PNG + manifest 7 个新 id + 映射表文档）`

---

## 6. 请总策划回复的三件事

1. **消费点接入线何时开工？** 它与视觉机制线同写 `scripts/*.gd`，请给出串行顺序或文件级写入边界。
2. **manifest ↔ houses_data 的 id 绑定怎么解？**（补 id 字段 / 扩 manifest / 近似匹配过渡，三选一）
3. **替换动作排在哪一步？** 我的建议是：**①、② 都完成、且游戏里能看见家具贴图之后，再一次性全换**。

---

*本反馈的事实全部经过实测（2026-11-22 15:57）。数值可复算：
`lab/_cls_check.py`（168/0）、`lab/_cls_bind_report.txt`（551/253/298）、`git diff --stat`（manifest +168/-0）、
`godot --headless --import`（EXIT=0）。*
