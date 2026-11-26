# 任务书 L23 · 地图 v7：①内岛去掉几何色块 ②a4 郑家再挪到环岛边

> 用户 2026-11-26 验收 v6 后提两件：
> 1. **「a4、a5 为什么还在画纯几何图形而不是网格」** —— 实测只有一处：`polygon(label="岛")`（内岛，72 点）没有 32px 瓦片，`scripts/asset_draw.gd:93` 的 `POLYGON_TILE_KIND` 只登记了 `河`／`路`，所以它落到 `scripts/world_view.gd:266-272` 的纯色 `draw_colored_polygon`。a1–a3 没有环岛（`story.md:448`：2001 年才修），所以只有 a4/a5 露馅。
> 2. **「a4 右下角的房子往环岛中心挪点」** —— v6 只做了北移（y 72→58），x 没动，它离环岛心还有 54.8 格。

两件事**互不相干**（一件在 `assets/` + `scripts/`，一件在 `data/`），可以做在同一条线里先后完成。

## §0 边界

| 项 | 内容 |
|---|---|
| **你能写** | P1：`data/frames.json` 里 `a4_2001.shapes` 中 `zheng_a4` 的 `pos`（**只此一处**）；P2：`scripts/asset_draw.gd` 的 `POLYGON_TILE_KIND`、`_mdtest/tile_wire_check.gd` 的 `KNOWN_GAP`；重烘产物 `scenes/world/world_a4_2001.tscn`；`docs/FEEDBACK-map-v7-exec.md` |
| **你不许写** | 其余四帧任何字段；`a4_2001` 里除 `zheng_a4.pos` 外的一切（尤其 `hotspots`）；`world`／`start_pos`／`start_frame`；`assets/**`（不新建美术）；`scripts/**` 除上述一行；`project.godot`；`docs/**` 其余文件 |
| **前置** | HEAD ≥ `621f026`；`git status --short data/frames.json scripts/asset_draw.gd` 必须为空 |
| **不许并行** | 任何也写 `data/frames.json` 的线 |

## §1 P1：a4 郑家挪到环岛东侧

单位一律**格**（1 格 = 32 px）。

- 环岛圆心 = `(64, 52) 格`；环道外沿半径 9.5 格 ⇒ 东边缘约 `x = 73.5 格`。a4 主路带 `y 50..54 格`。
- 现状（v6 落地）：`zheng_a4 pos = (108, 58) 格`，距环岛心 **54.8 格**。
- **改成 `pos = (76, 58) 格 = (2432, 1856) px`**（只改 x：108 → 76）。
  - lot 19×12 ⇒ 占 `x 76..95 / y 58..70 格`
  - 距环岛心 **24.6 格**；西墙距环道外沿约 **4.6 格**（y=58 处环道实际边界 x≈71.4）；北墙距主路底 **4 格**。
  - 已核验：与 a4 全部形状（河/坝/路/环道/内岛/井/槐/田/4 个路标）**相交数 = 0**。
- 想更贴环也只能到 `x = 74`（再往西就压进环道），**不要自己试更小的值**。

## §2 P2：内岛接上瓦片，从「纯色几何块」变成网格

**做法（零新美术）**：内岛是环岛中间那块草地，与四周地面是同一种草 ⇒ 直接复用地面瓦片。

1. `scripts/asset_draw.gd:93` 的 `POLYGON_TILE_KIND` 加一行：
   ```gdscript
   const POLYGON_TILE_KIND := {
       "河": "river",
       "路": "road",
       "岛": "ground",   # 内岛＝草地，复用地面瓦片（原先无图 ⇒ 纯色圆盘）
   }
   ```
   `ground` 在五帧的 `TILE_FILES` 里都有（a4 是 `ground_a4_tiles_l8.png`、a5 是 `ground_a5_tiles_l8.png`），不需要新增文件。
2. `_mdtest/tile_wire_check.gd:31` 的 `KNOWN_GAP := ["岛", "山"]` 改成 `["山"]`（`山` 保留：v4 已删光，但如果哪天长回来还要报缺口）。
3. 顺手核对 `_mdtest/tile_wire_check.gd` 里所有依赖 `KNOWN_GAP` 的分支（`:177-200`、`:280-295`），确保「岛现在有图」不会把它误判成 fail。

## §3 自检（S1–S7，全部贴原样输出）

- **S1** `zheng_a4.pos == (76, 58) 格`；其余三个 house 的 `pos` 与改前逐位相同。
- **S2** `a4_2001.hotspots` 与改前逐条相同（5 条）。
- **S3** 其余四帧（a1/a2/a3/a5）+ `world` + `start_pos` **JSON 深比较等于改前**。
- **S4** 五帧 `shapes` 数量不变：`237 / 239 / 222 / 19 / 19`。
- **S5** `POLYGON_TILE_KIND` 里 `岛 → ground`，且 `AssetDraw.polygon_tex("a4_2001", "岛") != null`（打印 texture 的宽高）。
- **S6** 新位置与 a4 全部形状相交数 = 0（自己复算）。
- **S7** `json.dumps(..., ensure_ascii=False, indent=2)` 与原文件逐字节相同（改前先验一次，漂移就停手报错）。

## §4 回归（六条，看关键字不看退出码）

| 脚本 | 期望 |
|---|---|
| `_mdtest/greybox_check.gd` | `solids=238/299/379/649/834`（**一位不变**）、`HOTSPOTS=10/11/13/12/8`、`UNEXPLAINED_BLOCKS=0`、`REACH_OK=true`、`WALL_STOP_Y=880.0`、`SPACE_MOVE_DX=40.0` |
| `_mdtest/tile_wire_check.gd` | `fails=0`；**`gaps` 会比改前小（岛不再计入）**，把改前改后的数字都贴出来 |
| `_mdtest/phasing_check.gd` | `fails=0 warns=0` |
| `_mdtest/scene_bake_check.gd` | `fails=0` |
| `_mdtest/sort_check.gd` | `fails=0` |
| `_mdtest/a4_rebuild_check.gd` | 已知红，**不许修**，原样贴 |

⚠️ `blocked_at_step` 位移不是回归（房子又挪了，绕行路径变了）。

## §5 重烘

`godot --headless --path . -s res://tools/bake_world_scene.gd`。
.tscn 每次重烘都有 `unique_id` 噪声 ⇒ **只提交 `world_a4_2001.tscn`**，其余四个若有差异逐字节回退到 HEAD，并在反馈里说明。

## §6 反馈 `docs/FEEDBACK-map-v7-exec.md`

三段：①改了什么（P1/P2 分开写，附 a4 局部 ASCII 位置图 + `岛` 现在的贴图名）②S1–S7 原样 ③回归六条原样 + 「没做到的」。
**没有截图就别声称看过画面**——本机无视觉模型，我不验图，只看数字。

## §7 提交

`git add` **只加**：`data/frames.json`、`scripts/asset_draw.gd`、`_mdtest/tile_wire_check.gd`、`scenes/world/world_a4_2001.tscn`、`docs/FEEDBACK-map-v7-exec.md`。**绝不 `git add -A`**，**不 push**。

建议提交信息：`map v7: a4 郑家挪到环岛东侧（距环心 54.8→24.6 格）+ 内岛接地面瓦片去掉纯色圆盘`

## §8 环境

- Godot = `D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe`
- python = `C:\Users\lyh\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe`
- 沙箱：`& godot ...` 抓不到 stdout，要 `Start-Process -RedirectStandardOutput 文件` 再读文件；系统 Temp 不可写，临时文件落 `lab/_tmp/`。