# L8 · 资产接线执行提示词（32px 平铺管线）

> **本线是 2026-11-26 地图事故的真正补救线。**
> 起因：用户 2026-11-26 指出「产出提示词后交给会话构造的地图连游戏地图的核心都丢失了……为什么环岛、公路、树都退化成了几何图形？」
> 根因分析见 `docs/地图视觉口径.md` §4（任务书层／引擎层／资产层／纪律层四层）。
> **本线是唯一负责「把色块变成画面」的线。** 别的线只管摆几何，本线管贴图。

---

## §0 开工前

### §0.1 环境

| 项 | 值 |
|---|---|
| 仓库根 | `D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift` |
| Godot | `D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe`（**不在 PATH**，必须全路径） |
| 跑回归 | `& $godot --headless --path . -s res://_mdtest/<name>_check.gd 2>&1 \| Select-Object -Last 45` |
| 判定 | **看关键字不看退出码**。沙箱固有噪声：`Failed to open 'user://logs/godot...log'`、`Failed to read the root certificate store.`、`ERROR: Parse JSON failed. Error at line 0: Unexpected character` |
| 禁止 | `cmd /c`（路径有空格会被截断）、`> out.txt`（产出 0 字节） |

### §0.2 HEAD 下限

**≥ `7b410bd`**。

**版本自检（开工第一步，不通过就停下报告）**：

```powershell
git log --oneline -1
Test-Path -LiteralPath 'docs/地图视觉口径.md'
Select-String -LiteralPath 'docs/地图视觉口径.md' -Pattern 'C5'
```

- `docs/地图视觉口径.md` 不存在 ⇒ 拿到的是旧任务书，**停下报告**。
- `docs/地图视觉口径.md` 里搜不到 `C5` ⇒ 同上。

### §0.3 基线（开工前必须自己跑一遍存成 `lab/_l8_baseline.txt`）

七套回归全绿，并记下：

```
_godot --headless --path . -s res://_mdtest/asset_draw_check.gd   # ASSET_DRAW_CHECK_DONE fails=0
_godot --headless --path . -s res://_mdtest/sort_check.gd          # SORT_CHECK_DONE fails=0
_godot --headless --path . -s res://_mdtest/greybox_check.gd       # 记 REACH_MAP
_godot --headless --path . -s res://_mdtest/camera_check.gd        # CAMERA_CHECK_DONE fails=0
_godot --headless --path . -s res://_mdtest/hud_layout_check.gd    # HUD_CHECK_DONE fails=0
_godot --headless --path . -s res://_mdtest/evidence_archive_check.gd
_godot --headless --path . -s res://_mdtest/display_check.gd
```

**必须原样记住的基线数字**（改动前后要对照）：

| 项 | 基线值 |
|---|---|
| `REACH_MAP` | `standable=15104`、`to_a5=12497`、`blocked_at_step=[144,191,2171,101]`、`band_total=298`、`band_full=298`、`band_ratio="100%"`、`ratio="83%"` |
| `UNEXPLAINED_BLOCKS` | `0` |
| `A1_WELL_FREE` | `false` |
| `WALL_BLOCKED` | `true` |
| `TIME_FWD_REACHED` | `[1,2,3,4]` |
| 五帧 solids/hotspots | a1 239/10、a2 300/11、a3 380/13、a4 646/13、a5 898/9 |
| 证物 | 25 卡 / 55 观察（界碑删除线落地后 24 / 51） |

### §0.4 脏工作区纪律（本仓库长期脏，务必守住）

- **只精确 `git add` 自己那批文件。绝不 `git add -A`。**
- **`git checkout -- <file>` 会被沙箱拦（CC Safety Net 规则 `git.checkout-double-dash`）** ⇒ 要还原某个文件，用 `git show HEAD:<path>` 按字节写回。
- 工作区长期存在**不属你**的改动：11 张 `_ref/art/A1..A3/*.png`（美术线 M）、`美术资产/**` 一批 D（用户自己删的）、大批未跟踪 `lab/_*` / `docs/FEEDBACK-*` / `.import`。**一个字都别动。**
- 本线若要新增美术资产入库，**只 add 你自己切片/改名出来的那几个文件**，不许把 `美术资产/` 整目录 add 进去。

### §0.5 允许改的文件（白名单）

| 文件 | 改什么 |
|---|---|
| `scripts/world_view.gd` | **本线主战场**：地面铺装、rect/polygon 按 label 分派贴图、32px 平铺通路 |
| `scripts/asset_draw.gd` | `SCENE_FILES` / `SHARED_SCENE` 扩表、新增 kind、新增平铺辅助函数 |
| `assets/village/scene/**`（新增切片文件） | 你从美术图集切出来的 32px 素材 |
| `_mdtest/asset_draw_check.gd` | 场景图断言扩展（**只许加，不许删既有断言**） |
| `_mdtest/sort_check.gd` | **只许加断言，不许改既有断言** |
| 新建 `_mdtest/tile_wire_check.gd` | 本线专项测试 |
| `docs/FEEDBACK-asset-tile-wire-exec.md` | 本线反馈（≤120 行） |
| `docs/地图视觉口径.md` | **只许补实测数据**（§3 表格里把「现状」改成实测结论），不许改 C1–C5 |
| `docs/PROMPT-overseer.md` / `docs/待解决事项.md` | **只许改状态行** |

### §0.6 不许碰的文件

- `data/frames.json`（**L1/A4 独占**）—— 本线只读；发现 shape 没贴图，**登记进反馈文档的「美术缺口表」，不许自己改数据**。
- `_ref/houses/houses_data.json`（L3 独占）
- `scripts/house_shape.gd`（L4 独占）、`scripts/frame_data.gd`（L4 独占）
- `scripts/timeline.gd`、`scripts/player.gd`、`scripts/main.gd`、`scripts/hud.gd`（L17 独占，见 §0.7）
- `scripts/evidence_store.gd`、`scripts/evidence_archive.gd`
- `docs/story.md`、`docs/npc.md`、`docs/HANDOFF.md`（L6 独占）
- `docs/_backup/**`、`docs/FEEDBACK-*`、`docs/RESUME-*`、`docs/DECIDE-*`（历史留档）
- `_ref/art/**` 的 PNG（美术线在改）
- `美术资产/**` 的原始文件（**只读，只切片，不改名、不移动、不删除**）

### §0.7 串行提醒

- 本线改 `scripts/world_view.gd` ⇒ **与 L17 phasing、界碑删除线、L8 之外的任何 world_view 线三选一**。同一时刻只能有一个人在这文件里。
- 本线**不改** `scripts/main.gd` / `timeline.gd` / `player.gd` / `hud.gd` ⇒ 与 L17 不争这几个文件，**只争 `world_view.gd`**。
- 本线**不改** `data/frames.json` ⇒ 与 A4 重排线、界碑删除线**不冲突**，可同批跑。

---

## §1 独占写入文件

本线独占（同一时刻只有本线能写）：

1. `scripts/world_view.gd`
2. `scripts/asset_draw.gd`
3. `assets/village/scene/` 下**本线新增**的文件（文件名必须带 `_l8` 或明确新名，不许覆盖既有 20 张旧大图）
4. `_mdtest/tile_wire_check.gd`（新建）

本线**不独占**（可与别人同批跑，但要错开落盘）：`_mdtest/asset_draw_check.gd`、`_mdtest/sort_check.gd`、`docs/**`。

---

## §2 数据基准

### §2.1 唯一权威：视觉口径

**`docs/地图视觉口径.md` 是本线的唯一权威文档。** 动手前先把它整篇读完（它不长）。

它的五条硬约束（C1–C5）本线逐条落地：

| 约束 | 含义 | 本线怎么落地 |
|---|---|---|
| **C1** | 最小单位 = 32×32 单方格可平铺 | 所有地面层素材切到 32px；引擎用 `draw_texture_rect(tex, rect, true, ...)` 平铺 |
| **C2** | 数据只圈方格区域，不写造型 | 本线**不改数据**，但要让引擎能吃下任何 shape 的区域声明 |
| **C3** | 贴图与地图尺寸解耦 | 贴图按 32px 切，不按 4800×3600 做整帧图 ⇒ 世界再放大不用重画 |
| **C4** | 缺图降级是容错不是验收通过 | 缺图必须**登记**，不许静默留色块 |
| **C5** | 每个 shape 都要能说出铺什么贴图 | 引擎按 label/类型分派贴图；分派不出来的 shape 要在反馈里点名 |

### §2.2 引擎现状（我已逐行核对，照这个改）

`scripts/world_view.gd:195-271` `_draw_back()` 的现状分派：

```
:211-212  house        → _draw_house_base()
:213-215  circle       → pass（树/井走前景层）
:216-218  rect 立的     → pass（路标等走前景层）
:219-229  rect road:true → 整帧 road bbox 贴一次整张路图（无图则 draw_rect 纯色）
:230-238  rect label=="坝" → 单 rect 贴 dam 图
:239-241  rect label!=""  → pass（前景层 _draw_prop）
:242-252  rect label==""  → 整帧 field bbox 贴一次整张田图
:253-259  path         → draw_polyline
:260-271  polygon      → 只认河！有 river 图则贴（画布写死 3200×416），否则 draw_colored_polygon 纯色
```

⇒ **五处硬缺口**：

1. **地面永远是纯色**。`:165` `draw_rect(Rect2(Vector2.ZERO, size), _grade(frame.ground), true)` —— 全屏一块颜色。磁盘上的 `assets/village/scene/ground_a1_tiles.png` / `ground_a2_tiles.png` / `ground_a3_tiles.png`（**各 32×32，100% 不透明，正好一格**）**零消费点**。
2. **polygon 只认河**。环岛环道、内岛、竖车道、山 —— 全部只会被 `draw_colored_polygon` 画成纯色。这是「环岛退化成了几何图形」的**直接原因**。
3. **路/田是「整帧 bbox 贴一次整张大图」**。`road_curved_tiles.png` 3200×256、`road_straight_a3.png` 3200×64、`field_a2/a3.png` 512×384、`field_patch_tiles.png` 672×384 —— 这些是 A1–A3 旧尺寸（世界当时 3200 宽）的整帧图，**放大到 4800 后必然对不上**（C3 违反）。
4. **河贴图画布写死 `Vector2(3200, 416)`**（`:264`）。⇒ **A1–A3 的河在 x=3200 处视觉断掉**，而 A4/A5 的河数据是 152 点铺到 4800。**五帧的河宽度不一致，是现存视觉缺陷**。
5. **A4/A5 六栋房屋走色块**。`:666-673` `const FAMILY` 只登记 A1–A3 的 12 个 id（`lu_house`/`lu_a2`/`lu_a3`/`shen_a1..a3`/`mill_a1..a3`/`zhou_house`/`zhou_a2`/`zhou_a3`）；`:687-699` `_house_tex()` 查 `assets/village/houses/<族>/<帧>_{base,roof}.png`。A4/A5 的 `market`/`shen_a4`/`zhou_a4`/`zheng_a4`/`shen_a5`/`toyshop`/`school` 都没登记 ⇒ 走色块墙＋色块屋顶。**注：`assets/village/houses/` 现在只有 lu/mill/shen/zhou 四族 a1–a3 共 23 张，其中 `lu/a3_roof.png` 缺失** ⇒ A4/A5 六栋的图**要等美术**，本线只能先接线通路、登记缺口。
   `scripts/asset_draw.gd:18-40` `SCENE_FILES` 只有 `a1_1926`/`a2_1951`/`a3_1976` 三帧 ⇒ A4/A5 的河/路/田/井/槐也走色块。

### §2.3 Godot 已有能力，不用新造

`CanvasItem.draw_texture_rect(texture, rect, tile, modulate, transpose)` 的**第三个参数就是 `tile`**：

```gdscript
draw_texture_rect(tex, Rect2(pos, size), true, sc)   # true = 32×32 贴图平铺填满 rect
```

现有代码 `:225` / `:236` / `:248` / `:264` **全都传 `false`**。改成 `true` 就能平铺 —— **但前提是贴图本身是 32×32 单方格**（现在贴的是 3200×416 大图，平铺无意义）。

⇒ **本线的真正工作量 = 把「整帧大图」管线换成「32px 单方格逐格铺」管线，再把美术的 autotile 图集切进 `assets/village/scene/`。**

### §2.4 美术资产现状（我已实测）

**A. 已入库的旧整帧大图**（`assets/village/scene/`，20 张）：

| 文件 | 尺寸 | 32px 格数 | 本线怎么用 |
|---|---|---|---|
| `ground_a1_tiles.png` / `ground_a2_tiles.png` / `ground_a3_tiles.png` | **32×32** | 1×1 | ✅ **直接拿来平铺地面**，零加工 |
| `road_curved_tiles.png` | 3200×256 | 100×8 | ⚠️ 28.5% 不透明（带透明通道的稀疏图）⇒ 不可直接平铺，需切成 32px 小件 |
| `road_straight_a3.png` | 3200×64 | 100×2 | ✅ 100% 不透明 ⇒ 可切 32px 瓦片 |
| `field_a2.png` / `field_a3.png` | 512×384 | 16×12 | ✅ 100% 不透明 ⇒ 可切 32px 瓦片 |
| `field_patch_tiles.png` | 672×384 | 21×12 | ⚠️ 66% 不透明 ⇒ 需切小件 |
| `river_a1/a2/a3.png` | 3200×416 | 100×13 | ⚠️ 77.6% 不透明、主色蓝水 ⇒ 需切 32px 瓦片 |
| `tree_a1/a2/a3.png` | 64/128/192 | 2/4/6 | ✅ 整张贴（树是独立物件，不平铺） |
| `well_old_a1/a2/a3.png` | 64×64 | 2×2 | ✅ 整张贴 |
| `dam.png` | 256×128 | 8×4 | ✅ 整张贴（坝是一个物件） |
| `stele.png` | 32×32 | 1×1 | ✅ 整张贴（**界碑删除线会删掉它** —— 本线碰它要串行） |

**B. 美术同学已交付但**未入库**的图集**（`美术资产/`，整目录 `git status` 是 `??`）：

| 文件 | 尺寸 | 32px 格数 | 备注 |
|---|---|---|---|
| `美术资产/地皮/GK_A2_CCautotile_1.png` | 768×576 | **24×18** | ✅ 32px 对齐的 autotile 图集 |
| `美术资产/地皮/GK_A5_CCfloors_1.png` | 384×768 | **12×24** | ✅ 32px 对齐 |
| `美术资产/地皮/GK_C_CC_1.png` | 511×511 | 15.97×15.97 | ⚠️ **不是 32 倍数**（511）⇒ 需按 32 网格切、边角 31px 余量处理 |
| `美术资产/树/Redtree8.png` | 64×64 | 2×2 | 整张贴 |
| `美术资产/树/tree.png` | 96×128 | 3×4 | 整张贴（96/128 是 32 倍数 ✅） |
| `美术资产/房屋/GK_B_CC_1.png` / `GK_D_CC_1.png` | 768×768 | **24×24** | ✅ 32px 对齐的房屋图集 |
| `美术资产/房屋/tileB_farmA/farmB/fortA/fortB.png` | — | — | 房屋变体 |
| `美术资产/房屋/地板.png` `墙面.png` `屋檐1-3.png` | — | — | 房屋构件 |

**C. 美术清单里已列但磁盘上没有的**（`docs/ART-GAP-A4A5.md`）：
- B 组 19 张 32×32 瓦片规格（`river_a4/a5_tiles`、`road_a4/a5_tiles`、`field_a4/a5_tiles`、`ground_a4/a5_tiles`、`ditch_tiles_a1..a3`）
- C 组 3 张环岛零件（`roundabout_curb.png` / `roundabout_island_soil.png` / `roundabout_island_green.png`，各 32×32）
⇒ **磁盘上 `roundabout*` 搜索零命中**。本线要**先把环岛零件的美术缺口写清楚**（尺寸已定：各 32×32），**不许拿色块糊过去**（C4）。

### §2.5 引擎侧不变式（改的时候不能破）

1. **排序链只加不减**。`world_view.gd:468-546` `_collect_front()` 收 walls/door/roof/furniture/prop 五类 ＋ player，`sort_y` 升序、`sort_custom`（同值按 seq）。`_mdtest/sort_check.gd:250` 与 `_mdtest/asset_draw_check.gd:287` 断言 sort_y 单调。**贴图只影响背景层 `_draw_back`，不许动 `_collect_front` 与排序键。**
2. **前景层的「井恒可见」就地补画**（`:330-345` 补画 A/B）**不许改成 sort_y 调整** —— 会直接破排序断言。
3. **`world_view.gd:167-174` 时间轴模式的三遍色差绘制**（红偏左/青偏右各 1px、alpha 0.45）是**核心观感，不许优化掉**。
4. **`solid:false` 不进碰撞**（`scripts/frame_data.gd:38` `if not bool(sd.get("solid", false)): continue`）。本线只改绘制，不碰碰撞。
5. **一帧只能一个无 label rect**（`_scene_bboxes()` `:274-305` 把 label=="" 的 rect 全 merge 成 field bbox）。本线若要给 rect 加 label 语义，**不许加第二个无 label rect**。
6. **竖路/环岛绝不能写 `road:true`**（会把整帧路 bbox merge 成一个外包矩形）。本线做 polygon 贴图时按 label 分派，正好绕开这个坑。

---

## §3 必改清单（七件，逐件做完）

### §3.1 新增「地面铺装」通路

- 在 `asset_draw.gd` 加一个地面贴图索引（按帧 id → 32px 地面瓦片路径），优先复用已有的 `ground_a1/a2/a3_tiles.png`（32×32，零加工）。
- `world_view.gd:165` 改成：先按整帧地面色铺底（容错），再按**地面瓦片平铺**覆盖（A1–A3 有图就用图；A4/A5 没图就留纯色 **并在反馈里登记美术缺口**：`ground_a4_tiles.png` / `ground_a5_tiles.png`）。
- 平铺用 `draw_texture_rect(tex, Rect2(offset, size), true, sc)`（**第三参传 `true`**）。
- 底色必须保留：**贴图缺失时不能变成透明**。

### §3.2 新增「polygon 按 label 分派贴图」通路（**事故核心**）

在 `_draw_back()` 的 polygon 分支（`:260-271`）改成按 `label` 分派：

| label | 铺什么 | 贴图来源 | 平铺？ |
|---|---|---|---|
| `河` | 河水 | `river_<帧>_tiles.png`（32×32 瓦片，切自现有 `river_a1..a3.png`） | 是，**按 polygon 内的格铺**（不是整块贴一张大图） |
| `路`（环道） | 环岛车道 | `roundabout_curb.png`（路缘）＋ `road_<帧>_tiles.png` | 是 |
| `岛` | 环岛内岛 | `roundabout_island_soil.png`（2001 工地态）/ `roundabout_island_green.png`（2026） | 是 |
| `山` | 山体 | 山地表 32×32 瓦片 | 是 |
| 其它/空 | 保留现纯色降级 | — | — |

**polygon 内逐格平铺怎么做**：polygon 的 `points` 是世界坐标多边形 ⇒ 必须先算出**哪些 32px 格心落在多边形内**，再逐格 `draw_texture_rect(tex, Rect2(gx*32+offset, gy*32+offset, 32,32), true, sc)`。
- 判定用**格心在多边形内**（射线法或半平面法，自己在 `asset_draw.gd` 写一个纯逻辑函数 `points_in_poly(poly, p) -> bool`）。
- **不许用 polygon 的 bbox 近似**（环岛环道的 bbox 比真实环大一圈，会糊到岛上 —— 这个坑我在 A4 重排线已经踩过一次）。
- 边的格子：格心在多边形内就铺，**不做抗锯齿、不做半格**，保持像素风。

### §3.3 新增「rect 按 label/类型分派」通路

- `rect` + `road:true` ⇒ 改用 `road_<帧>_tiles.png` **32×32 平铺**，**不再整帧 bbox 贴一次大图**（C3）。
- `rect` + `label:""`（田块）⇒ `field_<帧>_tiles.png` 32×32 平铺。**注意：一帧只能一个无 label rect**（`_scene_bboxes()` 合并逻辑），所以田块只有一块时可以直接平铺这个 rect 本身。
- `rect` + `label:"坝"` ⇒ 保持整张贴 `dam.png`（坝是一个物件，不平铺）。
- `rect` + `label` 非空 ⇒ 保持走前景层 `_draw_prop`（路标等立着的小件）。
- **`road:true` 的判定要保留**：`frame_data.gd:38` 用它区分「地面铺装 vs 立着实体」，**不许从数据里删 `road:true` 字段**。

### §3.4 修「河跨帧宽度不一致」（现存视觉缺陷 D1）

- 引擎侧：河贴图**不许再写死 `Vector2(3200, 416)`** ⇒ 改成「按 polygon 的实际 bbox 铺」，或者改成 32px 瓦片按格铺（§3.2 的做法天然解决）。
- 数据侧：**A1–A3 的河 polygon 只有 103 点、x 只到 3200**，而 A4/A5 是 152 点铺到 4800 ⇒ **A1–A3 的河在 x=3200 处断掉**。
  ⇒ **数据修复属 A1–A3 重排线**，本线**不许改 `data/frames.json`**。本线在反馈文档里把这条**明确写出来并点名责任人**。

### §3.5 把美术图集切进 `assets/village/scene/`

- 从 `美术资产/地皮/`、`美术资产/房屋/` 的 32px 对齐图集里，按 32px 网格**切出**本线需要的单方格小件，切完**存到 `assets/village/scene/`**（新文件名，不许覆盖既有 20 张）。
- 切图脚本放 `lab/`（如 `lab/_l8_slice_tiles.py`），用 PIL；**必须是可重复执行的**（读源、切、写出，不改源）。
- 切片结果要报：**切出几张、每张尺寸、从哪个源图哪个格子**。
- `美术资产/` 目录**只读**：不许改名、不许移动、不许删除、不许整目录 `git add`。
- ⚠️ `GK_C_CC_1.png` 511×511 **不是 32 倍数** ⇒ 按 32 网格切时最后一行/列会有 31px 余量，**余量丢弃**，并在反馈里写明。

### §3.6 扩 `SCENE_FILES` / `SHARED_SCENE` / `FAMILY`

- `asset_draw.gd:18-40` `SCENE_FILES`：把新的瓦片按 kind 登记（kind 名自定，但要与 §3.2/§3.3 的分派一致）。**A4/A5 的图还没有 ⇒ 先不登记，缺图走色块降级 + 登记缺口**（C4）。
- `asset_draw.gd:43-46` `SHARED_SCENE`：新增共享小件时登记（`stele` 条目**界碑删除线会删掉它**，本线要与之串行或避开该条目）。
- `world_view.gd:666-673` `FAMILY`：A4/A5 六栋房屋的底图/屋顶图**现在磁盘上没有** ⇒ **本线先不登记**，但要在反馈里给出**登记表模板**（`"market": ["market", "a4"]` 之类），等美术出图后一行就能加。
- ⚠️ `assets/village/houses/` 现有 23 张里 **`lu/a3_roof.png` 缺失** ⇒ 陆家 A3 屋顶走色块，已是现存缺口，本线登记不改。

### §3.7 引擎红线（改的时候别踩）

- **不许新建绘制节点、不设 `z_index`**（`asset_draw.gd:5-6` 的 A 方案：绘制调用必须落在 `world_view.gd` 现有分支里）。
- **不许改 `_collect_front()` 与排序键**（见 §2.5）。
- **不许改 `frame_data.gd` / `house_shape.gd`**（碰撞与线索热点在那边）。
- **不许改 `data/frames.json`**（别的线在写）。
- 贴图**不得**影响碰撞体与排序不变式（`_mdtest/asset_draw_check.gd` 第 5 项就是测这个）。

### §3.8 明确不做

1. **不做**楼层、不做 phasing（那是 L17）。
2. **不做** A4/A5 的房屋底图（等美术出图，本线只留接线通路）。
3. **不做**环岛零件的美术绘制（只登记缺口：`roundabout_curb` / `roundabout_island_soil` / `roundabout_island_green`，各 32×32）。
4. **不改**五帧的几何数据（那是 L1/A4 的活）。
5. **不删** `stele.png`（界碑删除线管）。
6. **不做**真机截图脚本（沙箱无窗口；本线用 headless 渲染测试 + 像素采样代替，见 §4.4）。

---

## §4 验收

### §4.1 引擎层自检（必须全过）

1. **地面贴图有消费点**：grep `ground_a1_tiles` 在 `scripts/` 里**必须命中**（现在是零命中）。
2. **polygon 不再只认河**：grep `world_view.gd` 里 polygon 分支，必须能看出**按 label 分派**（河/路/岛/山各有各的贴图来源）。
3. **平铺参数用对了**：所有 32px 瓦片的 `draw_texture_rect` 第三参**必须是 `true`**（整张贴的地方保持 `false`）。
4. **无 label rect 仍只有一个**：跑 `_mdtest/asset_draw_check.gd` 与 `_mdtest/greybox_check.gd`，断言不许红。
5. **排序不变式没破**：`_mdtest/sort_check.gd` fails=0。
6. **A1–A3 河不再视觉断掉**：写一个 headless 探针，渲染 A1 帧并**采样 x=3100/3199/3200/3280/3400 这几列的像素**，x>3200 的区域**不许是纯地面色**（要么是河、要么是别的地面材质）⇒ 证明「河覆盖到 4800」这条通路是通的（**注意**：A1–A3 的河数据只到 3200 ⇒ 若探针显示 x>3200 无河，**这是数据缺口不是引擎缺口**，要在反馈里分开写清，不许硬改数据）。

### §4.2 美术缺口表（**反馈文档里必须有，不许静默留色块**）

逐条列出**哪些 shape 现在还在走色块降级**、缺哪张图、图的确切尺寸：

| shape 类型 | 帧 | 现在长什么样 | 缺什么 | 尺寸规格 | 归属 |
|---|---|---|---|---|---|
| 地面 | a4_2001 | 纯色 | `ground_a4_tiles.png` | 32×32 | 美术 |
| 地面 | a5_2026 | 纯色 | `ground_a5_tiles.png` | 32×32 | 美术 |
| 环道 | a4/a5 | 纯色 | `roundabout_curb.png` | 32×32 | 美术 |
| 内岛 | a4_2001 | 纯色 | `roundabout_island_soil.png` | 32×32 | 美术 |
| 内岛 | a5_2026 | 纯色 | `roundabout_island_green.png` | 32×32 | 美术 |
| 山 | 五帧 | 纯色三角 | 山地表瓦片 | 32×32 | 美术 |
| 房屋底图/屋顶 | A4/A5 六栋 | 色块墙＋色块屋顶 | `houses/<族>/<帧>_{base,roof}.png` | 画布＝lot宽×32 ×(lot高×32+32) | 美术 |
| 河 | a1–a3 | 3200 宽断掉 | **数据侧**河 polygon 要延伸到 4800 | — | A1–A3 重排线 |

### §4.3 回归（改动前后对照表）

七套回归全绿，且这几项**必须与 §0.3 基线逐位一致**（贴图不该动碰撞与排序）：

| 项 | 基线 | 要求 |
|---|---|---|
| `REACH_MAP` | `standable=15104`、`to_a5=12497`、`blocked_at_step=[144,191,2171,101]`、`band_total=298`、`band_full=298`、`band_ratio="100%"`、`ratio="83%"` | **逐位一致** |
| `UNEXPLAINED_BLOCKS` | 0 | 一致 |
| `A1_WELL_FREE` | false | 一致 |
| `WALL_BLOCKED` | true | 一致 |
| `TIME_FWD_REACHED` | `[1,2,3,4]` | 一致 |
| 五帧 solids/hotspots | 239/10、300/11、380/13、646/13、898/9 | 一致 |
| `A4_REBUILD_CHECK` | fails=0 | 一致 |

### §4.4 「这不是色块」的证据（**几何自检之外必须有**）

沙箱出不了窗口 ⇒ 用 headless 渲染 + 像素采样代替实机截图：

1. 写 `_mdtest/tile_wire_check.gd`：实例化 `world_view`，切到指定帧，**用 `get_viewport().get_texture().get_image()` 抓像素**，断言：
   - 地面区域**存在多种颜色**（纯色地面只有 1 种；贴图地面至少有 3–4 种不同像素值）。
   - 环岛区域**不是单一纯色**。
   - 山体区域**不是纯色**。
   - 同一格重复平铺区里，同一 32px 格的不同位置**颜色不同**（证明是贴图不是色块）。
2. 报告里贴出**采样到的颜色数量**（例如「A5 地面 32×32 格内取到 5 种颜色」）。
3. 若某帧某区域仍是纯色（缺图），**必须在 §4.2 的缺口表里点名**，不许含糊。

### §4.5 交卷前逐条回答 `docs/地图视觉口径.md` §5 的清单

那份文档 §5 有 6 个勾选框，**逐条回答并给出证据**，不许空着。

---

## §5 收工

### §5.1 commit（精确 add，禁 `git add -A`）

**建议两段**：

1. `feat(asset): 32px 平铺管线（地面铺装 + polygon 按 label 分派 + rect 逐类贴图）`
   - `scripts/world_view.gd`
   - `scripts/asset_draw.gd`
   - `assets/village/scene/` 下**本线新增**的文件
   - `_mdtest/tile_wire_check.gd`（新建）
   - `_mdtest/asset_draw_check.gd` / `_mdtest/sort_check.gd`（只加断言）
2. `docs: 资产接线执行反馈（贴图通路 + 美术缺口表 + 视觉口径实测回写）`
   - `docs/FEEDBACK-asset-tile-wire-exec.md`
   - `docs/地图视觉口径.md`（只补实测数据）
   - `docs/PROMPT-overseer.md` / `docs/待解决事项.md`（只改状态行）

### §5.2 反馈文档 `docs/FEEDBACK-asset-tile-wire-exec.md`（≤120 行）必含

1. 本线改了哪些文件、各改了什么（逐文件一行）。
2. §4.4 的**像素采样数字**（各帧各区域取到几种颜色）。
3. §4.2 的**完整美术缺口表**（每条：缺什么图、尺寸、归属）。
4. 「河跨帧宽度不一致」这条**分开写清**：引擎侧做了什么、数据侧还差什么、归谁。
5. A4/A5 六栋房屋的 `FAMILY` 登记表模板（等美术出图后一行加）。
6. §4.3 的**改动前后对照表**（必须逐位一致，若不一致要解释）。
7. `docs/地图视觉口径.md` §5 六问的逐条回答。
8. 未做的事与已知缺口。

---

## §6 边界提醒

1. **只精确 `git add` 自己那批文件，绝不 `git add -A`。**
2. **不许 `git checkout -- <file>`**（被沙箱拦），要还原用 `git show HEAD:<path>` 按字节写回。
3. **不许改 `data/frames.json`** —— 发现 shape 没贴图，登记缺口，不许自己动数据。
4. **不许改 `scripts/timeline.gd` / `player.gd` / `main.gd` / `hud.gd`**（L17 独占）。
5. **不许改 `scripts/house_shape.gd` / `frame_data.gd`**（L4 独占）。
6. **不许改 `docs/story.md` / `npc.md` / `HANDOFF.md`**（L6 独占）。
7. **不许动 `美术资产/` 的原始文件**（只读切片），**不许整目录 add**。
8. **不许改 `_ref/art/**` 的 PNG**（美术线在改）。
9. **不许删 `stele.png`**（界碑删除线管）—— 两线若同批跑要错开落盘。
10. **不许优化掉时间轴三遍色差**（`world_view.gd:167-174`）。
11. **不许改 `_collect_front()` 的排序链**（排序断言会红）。
12. **不许把「缺图走色块」写成「通过」** —— C4，缺图就是没交付。

---

## §附 依据

| 文档 | 用在哪 |
|---|---|
| `docs/地图视觉口径.md` | **唯一权威**：C1–C5 硬约束、shape→贴图对应表、引擎缺口表、事故根因、交付必查清单 |
| `docs/ART-GAP-A4A5.md` | B 组 19 张 32×32 瓦片规格、C 组 3 张环岛零件（美术已认领但未出图） |
| `docs/PROMPT-asset-consumption-exec.md` | 上一版资产消费点任务书（贴图锚点 D6 底部中心、`prop_draw` 契约） |
| `docs/DECIDE-a4-a5-layout.md` §11 | 总策划裁定（界碑是独立地标、A4/A5 贴图交给美术同学、L8 资产接线） |
| `docs/PROMPT-overseer.md` §九 | 执行提示词的标准骨架（本任务书照它写） |
| `scripts/world_view.gd:195-271` | 背景层分派现状（本线主战场） |
| `scripts/asset_draw.gd:18-46 / :165-171` | `SCENE_FILES` / `SHARED_SCENE` / `scene_tex()` 现状 |
| `scripts/frame_data.gd:38` | `solid:false` 不进碰撞（贴图不影响碰撞的依据） |
| `_mdtest/asset_draw_check.gd:28 / :210-216` | 场景图断言现状（`FRAMES` 只含 a1–a3；kind 列表含 `stele`；`:216` 断言 a4_2001 无 river 图 ⇒ **改成 a4 有图后这条要改，但只能由本线改，且改完要在反馈里写明为什么**） |
| `_mdtest/sort_check.gd:250` | sort_y 单调断言（本线不许破） |
| `_mdtest/greybox_check.gd` | 碰撞/可达性基线（本线不许改数字） |
