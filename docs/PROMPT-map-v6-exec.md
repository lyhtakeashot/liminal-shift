# 任务书 L22 · 地图 v6：a4 郑家北移贴近道路（单点微任务）

> **一句话**：`a4_2001` 的 `zheng_a4` 目前离东侧主路 **18 格**（全帧最远），北移到 **4 格**。
> 除此之外**一个字都不许改**。这是用户 2026-11-26 验收 v5 后唯一点名的问题。

## §0 边界（先看这段，越界即返工）

| 项 | 内容 |
|---|---|
| **你能写** | `data/frames.json` 里 `a4_2001` 帧的 `zheng_a4` 那一形状的 `pos`；重烘产物（`scenes/world/*.tscn`）；`docs/FEEDBACK-map-v6-exec.md` |
| **你不许写** | 其余四帧任何字段；`a1/a2/a3/a4` 的 `shapes` 里除 `zheng_a4.pos` 外的任何内容；`hotspots`；`world`；`start_pos`/`start_frame`；`scripts/**`；`_mdtest/**`；`tools/**`；`docs/**` 其余文件 |
| **独占** | `data/frames.json`。开工前 `git status --short data/frames.json` 必须是空；HEAD ≥ `34a9dd8` |
| **不许并行** | 任何也写 `data/frames.json` 的线（L20 旁听线若还在跑，等它交回） |

## §1 一切按「格」写（1 格 = 32 px）

- 世界 = **150 × 112.5 格**（4800 × 3600 px）。
- a4 东侧主路带 = `y 50..54 格`（1600..1728 px），横跨 `x 73.5..150 格`。
- `zheng_a4` lot = **19 × 12 格**（608 × 384 px），`gate = [7,10]`（南沿）。
- **现状**：`pos = (108, 72) 格 = (3456, 2304) px` ⇒ 北墙距路底 **18 格（576 px）**。
  对比同帧 `zhou_a4 pos = (18, 60) 格` ⇒ 距路底 **6 格**。郑家是全帧唯一离路很远的。

## §2 要改成什么

**`pos` = `(108, 58) 格` = `(3456, 1856) px`**（只改 y：72 → 58，北移 14 格 = 448 px）

- 北墙 `y=58 格`，距路底（54 格）**4 格 = 128 px** ⇒ 临街但留一条走道。
- `x` **不许动**（108）。房子仍在同一列、同一排院落关系里。
- 已核验：新位置 `x 108..127 / y 58..70 格` 与 a4 现有全部形状（河/坝/路/环道/内岛/井/槐/田/路标）**相交数 = 0**。
- 若你认为 4 格不合适：**不要自己改数字**，照 58 格做，在反馈里说明你的意见。

## §3 施工（就三步，别扩）

1. 读 `data/frames.json` → 在 `a4_2001.shapes` 里找 `type == "house"` 且 `id == "zheng_a4"` 的那一条 → `pos` 改成 `[3456, 1856]`。
2. 读回校验：`json.dumps(..., ensure_ascii=False, indent=2)` 与原文件**逐字节相同**（改之前先验证一次，防止格式漂移；漂移了立刻停手报错，不要硬写）。
3. 重烘：`godot --headless --path . -s res://tools/bake_world_scene.gd`。
   .tscn 每次重烘都会产生大量 `unique_id` 噪声差异，**只提交 `world_a4_2001.tscn`**；如果其余四个也变了，说明你动了不该动的东西 → 回滚重来。

## §4 自检（S1–S6，全部要贴原样输出）

- **S1** 五帧 `shapes` 数量：`a1 237 / a2 239 / a3 222 / a4 19 / a5 19`（与改前逐位相同）。
- **S2** `zheng_a4.pos == (108, 58) 格`，其余三个 house 的 `pos` 与改前逐位相同。
- **S3** `a4_2001.hotspots` 与改前**逐条相同**（5 条）。
- **S4** 其余四帧（`a1/a2/a3/a5`）+ `world` + `start_pos` **JSON 深比较等于改前**（`deep_equal=True`）。
- **S5** `label=="山"` 在五帧仍全为 0（v4 删的，不许长回来）。
- **S6** 新位置与 a4 所有形状相交数 = 0（复算一遍，别抄我这行）。

## §5 回归（五条，看关键字不看退出码）

| 脚本 | 期望 |
|---|---|
| `_mdtest/greybox_check.gd` | `solids=238/299/379/649/834`（**四个数字必须一位不变**）、`HOTSPOTS=10/11/13/12/8`、`UNEXPLAINED_BLOCKS=0`、`REACH_OK=true`、`WALL_STOP_Y=880.0`、`SPACE_MOVE_DX=40.0` |
| `_mdtest/phasing_check.gd` | `fails=0 warns=0` |
| `_mdtest/scene_bake_check.gd` | `fails=0`（项数 3049±5 都可） |
| `_mdtest/sort_check.gd` | `fails=0` |
| `_mdtest/a4_rebuild_check.gd` | **已知红，不许修**：AIRWALL 相关的几条会因 house lot 位移而变化。原样贴出来，由 lead 重定基线 |

⚠️ 灰盒脚本的 `blocked_at_step` 可能位移（房子挪了，绕行路径变），**这不是回归**，照实贴数字。

## §6 反馈文件 `docs/FEEDBACK-map-v6-exec.md`

三段，不许省：①改了什么（含改前/改后各一张 a4 的 ASCII 位置图，见 §7）②自检 S1–S6 原样输出 ③回归五条原样输出 + 「没做到的」。

**没有截图就别声称看过画面**——本机无视觉模型，我看不见图，你交图我也不验。用数字说话。

## §7 附：a4 平面速查（格）

```
y:  0 ┌──────────────────────────── 河（y 0..13）
   10 │                    ▓▓▓田(112.5..140, 10..22)
   50 ├──────────────────── 主路带 y 50..54（x 0..54.5 与 73.5..150 两段）
   54 │         ◎环道(54.5..73.5)  ○老井(64,26) ○老槐(64,52)  ⚑路标 x=106.3
   58 │                                        ┏━━━━━━━━┓ ← 郑家(108..127)  新位置
   72 │                                        ┗━━━━━━━━┛ ← 旧位置（北墙 72）
```
（`market (67,10)`、`shen_a4 (2,13)`、`zhou_a4 (18,60)` 未画，位置不变）

## §8 提交与收尾

- `git add` **只加**：`data/frames.json`、`scenes/world/world_a4_2001.tscn`、`docs/FEEDBACK-map-v6-exec.md`。**绝不 `git add -A`**。
- 提交信息建议：`map v6: a4 郑家北移 14 格贴近东侧主路（18 格 → 4 格）`。
- **不要 push**（网络受限，由 lead 统一推）。
- 环境：Godot = `D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe`；python = `C:\Users\lyh\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe`。
- 沙箱注意：直接 `& godot ...` 抓不到 stdout，要用 `Start-Process -RedirectStandardOutput 文件` 再读文件；系统 Temp 不可写，临时文件落 `lab/_tmp/`。