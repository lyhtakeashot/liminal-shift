# 新会话提示词：星露谷美术资产执行线（A1–A3）

> 整段复制给新会话作为第一条消息。本线只产出 PNG 资产 + 资产清单，不写 GDScript、不改数据、不回写文档。

你是《shift》Godot 4.7 像素游戏的**美术资产执行人**。

用户原话（2026-11-22）：「A1–A3 是可以参与改造的」；场景设计线正在做 A4/A5 房屋——**本线只做 A1–A3 的 12 栋，A4/A5 一律不碰**。

## 0. 开工前（必做）

```
项目：D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift
Godot：D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe
```

- 所有 pwsh 调用带 `sandbox_permissions: "danger-full-access"`。
- `git log --oneline -3` 确认 HEAD ≥ `eb6c7fa`。
- `git status --short`：**工作区有另一条 A4 精调线的未提交改动**（`_ref/houses/houses_data.json`、`_ref/houses/_redo_*.py`、`_ref/art/A4_2001/*.png`、`docs/HANDOFF-VILLAGE.md`、`docs/PROMPT-house-size.md`、`docs/PROMPT-a4-houses-exec.md`）。这些**只读、绝不写、绝不 add**。
- 先读 `docs/DECIDE-stardew-visual.md` 的 **D6**（美术规格冻结）和 `docs/art-assets-a1a3.md`、`_ref/art/_assets_a1a3/_a1a3_assets.json`。
- 不要参考 `assets/village/props/` 现有 17 张旧图——它们全是 16px 时代的产物，照着画会小一半。不要参考 `PROMPT-art-canvas-h16.md`（已 SUPERSEDED）。

## 1. D6 冻结规格（唯一答案，不许自行发挥）

| 项 | 规格 |
|---|---|
| 一格 | **32×32 px**（`scripts/house_shape.gd:13 TILE := 32.0`） |
| 房屋图 | 每栋 **base + roof 两张**（`lu_a3` 废墟只有 base），同宽同高同锚点 |
| 画布尺寸 | `cw = gw`、`ch = gh + 1`（单位格）→ 像素画布 = `cw×32` × `ch×32`；**多出的那一格在顶部做立面** |
| 锚点 | **底部中心**（贴图对齐到房子占地底边中心） |
| 家具 | `props` 是**独立数据对象**（pos/size/reach 在 `houses_data.json`），贴图只是外观；**占地/碰撞读数据不读 PNG**；源图多画一格（画布高 = 占地高 + 1 格） |
| 缺图降级 | Godot 端 `_house_tex()`（`world_view.gd:188-200`）会自动回色块——**分批交付安全**，不用一次画完 |

## 2. 你的独占写入目录

- `assets/village/houses/<族>/` —— 新建 PNG（族目录：`lu` / `mill` / `shen` / `zhou`）。
- `assets/village/props/` —— 重画 84 项家具中的 P0 外观（可分批）。
- `assets/village/scene/` —— 树等场景图（可选，P1）。

### 2.1 房屋 shell 清单（23 张，路径与 manifest 一致）

来源 `_ref/art/_assets_a1a3/_a1a3_assets.json` 的 `shell` 数组，字段 `path` 就是必须交付的路径（画布 `cpx` 是像素尺寸）：

| 族 | A1 | A2 | A3 |
|---|---|---|---|
| lu | `lu/a1_base.png` `lu/a1_roof.png` (640×448) | `lu/a2_base.png` `lu/a2_roof.png` (640×448) | `lu/a3_base.png` (640×448，仅 base) |
| mill | `mill/a1_base.png` `mill/a1_roof.png` (576×448) | `mill/a2_base.png` `mill/a2_roof.png` (576×448) | `mill/a3_base.png` `mill/a3_roof.png` (576×576) |
| shen | `shen/a1_base.png` `shen/a1_roof.png` (640×448) | `shen/a2_base.png` `shen/a2_roof.png` (736×576) | `shen/a3_base.png` `shen/a3_roof.png` (896×800) |
| zhou | `zhou/a1_base.png` `zhou/a1_roof.png` (384×256) | `zhou/a2_base.png` `zhou/a2_roof.png` (384×256) | `zhou/a3_base.png` `zhou/a3_roof.png` (384×256) |

⚠️ 上面尺寸是 manifest 里的 `cpx`（= `cw×32, ch×32`），直接按这个开画布。

### 2.2 家具 props（84 项）

manifest 的 `props` 数组每项有 `id / w / h / px / path / uses / houses`；`px` 已是 32px 口径（如 `deng_1x1` = [32,32]）。按 `path` 交付，画布高 = `h×32 + 32`（源图多画一格立面）。优先做 `uses` 高的（灯/床/灶/桌/水缸）。

### 2.3 场景 scene（24 项）

manifest 的 `scene` 数组：`river_a1` 等；路径按 `path`。树可按 `assets/village/scene/tree_old_4x5.png` 的思路重画（32px 口径），但 Godot 端树接入逻辑还没写——**本线不写接入代码**，只交资产。

## 3. 生成方式（推荐）

- 可用现成脚本 `_ref/houses/gen_asset_breakdown.py:286` / `:611` 的画布公式复算（`cw,ch=gw,gh+1`、`(gh+1)*TILE`），**别改这个脚本本身**。
- 允许用 `workbuddy_draw_image` 或自己写 Python/Pillow 生成像素图；**一张一张出，别指望一次生成整套**。
- 风格：星露谷式 32px 像素风，暖色调乡村；base 画墙体/门窗/室内地面/院落地面，roof 只画屋顶（进屋时整块消失，所以 roof 单独一张）。

## 4. 验收

- [ ] 每张 PNG 尺寸 = manifest 对应 `cpx`，不多不少。
- [ ] base/roof 同宽同高、底部中心锚点对齐。
- [ ] 12 栋覆盖完整（23 张 shell，`lu_a3` 只有 base）。
- [ ] A4/A5 目录一个字节都没动（`git status` 确认那些 `M` 文件仍是场景线的）。
- [ ] 不写 GDScript、不改 JSON、不回写文档。

## 5. 收工

- 只 `git add assets/village/` 下你自己新建/重画的文件。**不要 add 任何其他文件**。
- commit 信息写 `art: A1-A3 房屋/家具 32px 资产按 DECIDE D6 规格交付`。
- 报告里列出：交付张数、哪些还没画（分批计划）、有没有尺寸不符的。
