# 反馈：地图场景化 Stage 1（frames.json → 五帧 Godot 场景）

> 任务书 `docs/PROMPT-scene-tilemap-exec.md`｜执行 2026-11-26｜提交时 HEAD `0ceb026`
> **结论：Stage 1 已交付。** 五帧地图已烘成真正的 Godot 场景节点（`scenes/world/world_a{1..5}_<年代>.tscn` ＋ 五个 `tileset_*.tres`），编辑器 2D 视图打开即见、能手摆；**运行时一个字没动**（游戏画面仍是 L8 的 `_draw()` 平铺管线）。自检 S1–S12 全绿（headless 1868 条 / 窗口 1873 条），八套回归 `fails=0`。

## 1. 交付文件（16 个；任务书写「15 个」，按其自身清单逐项数是 16）

| 类 | 文件 |
|---|---|
| 映射表（可执行版） | `tools/world_scene_spec.gd` |
| 烘焙器 | `tools/bake_world_scene.gd` |
| 产物·场景 | `scenes/world/world_a1_1926.tscn`／`world_a2_1951.tscn`／`world_a3_1976.tscn`／`world_a4_2001.tscn`／`world_a5_2026.tscn` |
| 产物·瓦表 | `scenes/world/tileset_a1_1926.tres` … `tileset_a5_2026.tres` |
| 自检 | `_mdtest/scene_bake_check.gd`（S1–S12） |
| 文档 | 本文件 ＋ `docs/PROMPT-overseer.md`／`docs/待解决事项.md` 状态行 |

重建命令（改了 `frames.json` 或美术图后）：`godot --headless --path . -s res://tools/bake_world_scene.gd`；单帧加 `-- --frame a5_2026`。

## 2. 场景结构（每帧一棵，照任务书 §3.2）

```
World_<帧号> (Node2D)
├ Ground  (TileMapLayer, z=-100)  整个世界铺满 ground 瓦（16950 格）
├ Field   (TileMapLayer, z=-95)   rect label=="" 的田块
├ Road    (TileMapLayer, z=-90)   rect road:true 的公路
├ Water   (Polygon2D,    z=-88)   河：polygon/uv=世界坐标，texture_repeat=ENABLED
├ Overlay (Node2D,       z=-84)   环道 -86／内岛 -85／山 -84／路标 -81／坝 -80
├ Houses  (Node2D,       z=-70)   -house 底色（base 图，缺图=lot 底色+房间色块）
└ Props   (Node2D, y_sort=true)   墙/门/屋顶/家具/树/井/碑 —— 底边即排序键
```

`Props` 是唯一 `y_sort_enabled=true` 的层，其余全 false；**玩家不在场景里**。排序键与运行时 `world_view.gd::_collect_front()` 逐条同源：墙=该行南沿、门=该门格北沿、屋顶=wings 南沿、家具=`rect.end.y`、树井=`center.y+radius`。

## 3. 五帧烘焙数量

| 帧 | ground | field | road | 背景多边形 | sprite | 节点数 | 缺图 |
|---|---|---|---|---|---|---|---|
| a1_1926 | 16950 | 165 | 224 | 1 | 164 | 184 | 无 |
| a2_1951 | 16950 | 192 | 224 | 1 | 194 | 218 | 无 |
| a3_1976 | 16950 | 192 | 200 | 1 | 280 | 317 | `lu_a3` 屋顶 |
| a4_2001 | 16950 | 324 | 524 | 12 | 63 | 1290 | 见 §6 |
| a5_2026 | 16950 | 324 | 524 | 8 | 55 | 1576 | 见 §6 |

产物大小：`.tres` 各 ≈1.3KB；`.tscn` = 326／335／360／593／660 KB。缺图一律按 C4 **纯色降级**（取 shape 自带 `color`）并在烘焙日志里登记，不静默丢。

## 4. 自检 `_mdtest/scene_bake_check.gd`

`SCENE_BAKE_CHECK_DONE fails=0 checks=1868`（headless）／`fails=0 checks=1873`（窗口多 5 条像素采样）。
S1 文件存在且 `ResourceLoader.load` 成功｜S2 根名=`World_<帧号>`｜S3 七层齐且类型对｜S4 只 Props y_sort｜S5 Ground/Field/Road `get_used_cells()` 与 `Spec` 复算 ±0｜S6 每个 TileMapLayer 的 tile_set 非空、每 source `get_tiles_count()≥1`｜S7 Polygon2D 有顶点、有贴图的 `texture_repeat==ENABLED`｜S8 前景 `Sprite2D.centered==false` 且 `position.y` 落在帧内｜S9 前景层无 TileMapLayer｜S10 无玩家节点｜S11/S12 窗口渲染 a5/a1，地面 32×32 格颜色数 ≥3（实拍 `_mdtest/assets/scene_bake_*.png`）。

## 5. 与运行时的像素对照（scratch `lab/_scene_diff.gd`，未入库）

| 取样点 | 一致率 |
|---|---|
| a1_1926 (1360,900) 房屋区 | **100.0%** |
| a3_1976 (1296,1100) | 99.8% |
| a5_2026 (2048,900) | 99.8% |
| a4_2001 (2048,1664) 环岛中心 | 97.8% |

**已知差异**：环道圆圈边缘一圈不同。运行时用 32px 格近似多边形（`poly_tile_rects`：格心在内部才铺），烘焙用真 `Polygon2D` 填充 ⇒ 边缘更完整，方向是「烘焙更准」不是错位。

## 6. 美术缺口（16 行，照抄 L8 反馈 §8；**烘焙后仍缺**）

| 组 | 缺口 | 烘焙后状态 |
|---|---|---|
| 1 | ground a4（`ground_a4_tiles.png`） | 仍缺，用 l8 临时瓦 |
| 2 | ground a5 | 仍缺，用 l8 临时瓦 |
| 3 | road a4 | 仍缺 |
| 4 | road a5 正式瓦 | 仍缺，用 l8 临时瓦 |
| 5 | road a1–a3 正式瓦 | 仍缺，用 l8 临时瓦 |
| 6 | field a1–a5 分帧瓦 | 仍缺，五帧共用一张 |
| 7 | river a1–a5 分帧瓦 | 仍缺，五帧共用一张 |
| 8 | 内岛 a4 `roundabout_island_soil` | **仍缺 → 纯色降级** |
| 9 | 内岛 a5 `roundabout_island_green` | **仍缺 → 纯色降级** |
| 10 | 山地表 a4×7／a5×3 | **仍缺 → 纯色降级** |
| 11 | 环道路缘（需旋转） | 仍缺，环道走 road 瓦 |
| 12 | 房屋 base/roof a4/a5 ×7 栋 | **仍缺 → 每栋只剩 lot 底色+房间色块** |
| 13 | 老槐 a4/a5（160/192px） | **仍缺 → 树干+双圆降级** |
| 14 | 老井 a4/a5（64/96px） | **仍缺 → 单圆降级** |
| 15 | 界碑 a1–a5 | 五帧仍缺整张贴（A1 的碑数据已被界碑删除线移除） |
| 16 | 屋顶 lu/a3 | **仍缺 → a3 唯一缺图项，屋顶回落 wings 色块** |

⇒ **a4/a5 的房屋现在是「院子＋房间色块＋墙＋屋顶色块」，没有屋檐贴图**；树/井/山/岛是纯色几何。这是美术缺口，不是烘焙器丢东西。

## 7. 只登记不修的两项

- **D1 河跨帧宽度不一致**：a1–a3 的河数据 x 只到 3200，a4/a5 到 4800 ⇒ 河在 x=3200 处视觉断开。烘焙如实照做（数据即真相），修在 frames.json，本线不碰。
- 运行时用格心近似多边形、烘焙用真多边形 ⇒ 环道边缘 2.2% 像素差（见 §5）。

## 8. 怎么验收（看什么）

1. Godot 编辑器打开 `scenes/world/world_a5_2026.tscn`：地面瓦片铺满、左右两条公路、南侧河、环岛、四栋房屋外框、树与井 —— **这就是「编辑器里终于有东西了」**。
2. 想看得最全的房屋贴图，开 `world_a1_1926.tscn`（A1–A3 有 base/roof 全套，A4/A5 没有）。
3. 选中 `Ground` 节点 → 底部 TileMap 面板可见格子；`tileset_a5_2026.tres` 里四个 AtlasSource（ground/field/road/river）。
4. **`.tscn` 是产物不是源**：手改会被下次烘焙覆盖；要改地图请改 `data/frames.json`（或美术图）再重跑烘焙器。

## 9. 没做 / 等拍板

- 🔴 **Stage 2**（运行时从 `_draw()` 切到场景节点）**未做**，等总策划在编辑器里确认形态后另派。
- 未改：`scripts/**`（含 `world_view.gd`）、`assets/**`、`data/frames.json`、碰撞（墙碰撞仍走 `frame_data.solid_rects`，`TileMapLayer` 无物理 API）。
- 未做：EditorPlugin、小地图、造图/切图集。

## 10. 回归（含一处必须知道的基线漂移）

八套 `fails=0`；`tile_wire`：`fails=0 gaps=4 checks=39`（与基线逐位相同）。
**基线数字变了的全部原因不是我，是 `fe2b28b feat(story): 删除界碑` 在我烘焙期间落地**（同时带了 `085d6d7` phasing）：solid 239/300/380/812/898→238/299/379/812/897、hotspots 10/11/13/12/9→9/10/12/12/8、`standable 15104→15105`、`to_a5 12497→12498`、`HOTSPOTS 门槛 >=10→>=9`、`EVIDENCE_CHECK fails 1→0`。这些数字与 `docs/FEEDBACK-stele-removal-exec.md` 自报的**逐位相同**。
`REACH_MAP` 其余项、`UNEXPLAINED_BLOCKS=0`、`WALL_BLOCKED=true`、`WALL_STOP_Y=816.0`、`TIME_FWD_REACHED=[1,2,3,4]`、`A1_WELL_FREE=false`、`A1_MILL_*_FREE=true` 全部未变。