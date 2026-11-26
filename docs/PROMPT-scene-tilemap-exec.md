# 地图场景化（方案 B）· 执行任务书

> **这份任务书把「地图」从「一份数据 + 一支画笔」变成「Godot 场景里的节点」**，
> 让总策划能直接在 Godot 编辑器的 2D 视图里**看见**这个村庄。
> 用户 2026-11-26 拍板：走方案 B（真 TileMap 路线）。

---

## §0 开工前

### §0.1 路径与工具

| 用途 | 值 |
|---|---|
| 仓库根 | `D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift` |
| Godot | `D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe`（**不在 PATH**） |
| 场景文件 | `scenes/main.tscn`（运行时主场景） |
| 数据源 | `data/frames.json`（**唯一真相源**） |

跑回归的姿势（**照抄，不要自己发挥**）：

```powershell
& "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe" --headless --path . -s res://_mdtest/<name>_check.gd 2>&1 | Select-Object -Last 45
```

- **看关键字不看退出码**。沙箱固有噪声：`Failed to open 'user://logs/godot...log'`、`Failed to read the root certificate store.`、`[exit code:1]`。这些**不是**失败。
- **不要用 `cmd /c`**（路径里有空格会被截断）；**不要用 `> out.txt`**（沙箱下会产出 0 字节）。
- 窗口模式（要抓像素）必须**不带 `--headless`**：headless 是 dummy 渲染器，读不到帧缓冲。

### §0.2 HEAD 下限与版本自检

- 开工 HEAD 必须 **≥ `b928b4c`**（L8 资产接线已交付的那个提交）。
- **版本自检**：开工第一件事是读 `docs/地图视觉口径.md`。
  - **读不到这个文件，或读不到 §1 里的 C1–C5 五条** ⇒ 说明拿到的是旧任务书或缺前置文档，**停下报告，不要自己发挥**。
  - `docs/地图视觉口径.md` 是本线的**唯一视觉口径来源**，本线不许另立一套。

### §0.3 基线（开工前先跑一遍，存进 `lab/_scene_bake_baseline.txt`）

七套回归全部跑，逐字记下输出：

| 套 | 文件 |
|---|---|
| greybox | `_mdtest/greybox_check.gd` |
| camera | `_mdtest/camera_check.gd` |
| hud_layout | `_mdtest/hud_layout_check.gd` |
| sort | `_mdtest/sort_check.gd` |
| asset_draw | `_mdtest/asset_draw_check.gd` |
| evidence_archive | `_mdtest/evidence_archive_check.gd` |
| display | `_mdtest/display_check.gd` |
| **tile_wire（L8）** | `_mdtest/tile_wire_check.gd`（**必须全绿，不许退化**） |

**下面这些数字必须原样记住，收工时要逐位对上**：

```
REACH_MAP = { standable:15104, to_a5:12497, blocked_at_step:[144,191,2171,101],
              band_total:298, band_full:298, band_ratio:"100%", ratio:"83%" }
UNEXPLAINED_BLOCKS = 0
A1_WELL_FREE = false
WALL_BLOCKED = true
TIME_FWD_REACHED = [1, 2, 3, 4]
WALL_STOP_Y = 816.0
五帧 solids/hotspots = a1 239/10, a2 300/11, a3 380/13, a4 812/12, a5 898/9
证物 = 25 卡 / 55 观察
```

> ⚠️ a4 是 **812/12**，不是任务书 L8 里写的 646/13（那是 L8 之前的旧值，L8 已在反馈里标注）。

### §0.4 脏工作区纪律（**违反就是事故**）

- **只精确 `git add` 自己那批文件。绝不 `git add -A`。**
- 工作区长期有别人的东西：11 张 `_ref/art/A1..A3/*.png`（美术线 M）、`美术资产/**` 一批 D（用户自己删的）、几百个未跟踪 `lab/_*`、`docs/FEEDBACK-*`、`.import`。**这些一律不许 add、不许恢复、不许删。**
- **`git checkout -- <file>` 会被沙箱拦**（Safety Net 规则 `git.checkout-double-dash`）。要还原文件用 `git show HEAD:<path>` 按字节写回。
- 不要用 pwsh 的 `-replace` 批量改 python/gd 源文件——它会破坏缩进。**改源码一律写独立 .py/.gd 文件执行**。
- 落盘后必扫 `s.count('\ufffd')`（python 写中文长串进补丁脚本会出 U+FFFD 乱码）。

### §0.5 允许改动的文件（**白名单，越界即事故**）

| 文件 | 动作 |
|---|---|
| `tools/bake_world_scene.gd` | **新建**：烘焙器（Shape → 场景节点） |
| `tools/world_scene_spec.gd` | **新建**：shape → 节点/贴图 的映射表（与烘焙器分离，便于美术口径变更时只改表） |
| `scenes/world/world_a1_1926.tscn` … `world_a5_2026.tscn` | **新建**（5 个产物） |
| `scenes/world/tileset_a1_1926.tres` … `tileset_a5_2026.tres` | **新建**（5 个产物） |
| `_mdtest/scene_bake_check.gd` | **新建**：烘焙产物断言 |
| `docs/FEEDBACK-scene-tilemap-exec.md` | **新建**（≤120 行） |
| `docs/PROMPT-overseer.md` | 只改状态行 / 本线那一行 |
| `docs/待解决事项.md` | 只改状态行 / 本线那一行 |

### §0.6 不许碰的文件（**一个字节都不许动**）

| 文件 | 为什么 |
|---|---|
| `data/frames.json` | 地图数据归地图线（L1 / A4 重排线）。**本线只读。** |
| `_ref/houses/houses_data.json` | 房屋数据归 L3 线 |
| `scripts/world_view.gd` | L8 刚改完（+124/−63）。**本线不碰**，避免把刚交付的平铺管线搅乱 |
| `scripts/frame_data.gd` / `scripts/house_shape.gd` / `scripts/timeline.gd` / `scripts/main.gd` / `scripts/hud.gd` / `scripts/player.gd` / `scripts/asset_draw.gd` | 运行时全部不动（本线只做「场景产物」，见 §2.1 分步） |
| `assets/**` | 美术资产由美术同学管；缺图就缺图，走缺口登记 |
| `_mdtest/` 现有 8 个测试文件 | 只许**新建** `scene_bake_check.gd`，不许改既有测试的断言 |
| `docs/story.md` / `docs/npc.md` / `docs/HANDOFF.md` / `docs/DECIDE-*.md` | 文本线专属 |
| `docs/FEEDBACK-*.md`（既有） | 历史留档，只读 |

### §0.7 串行提醒

- 本线**不改运行时**，因此**与 L8 / L17 / 界碑删除线 / A4 重排线全部零文件冲突**，可以同时跑。
- 本线**只读** `data/frames.json` ⇒ 地图线改数据后，本线**重跑烘焙器**即可同步，不需要重新协商。
- **`.tscn` 是产物不是源**：任何人手改了 `.tscn`，重跑烘焙器会被覆盖。这是设计如此，不是 bug。

---

## §1 独占写入文件

本线**独占**（别人不要同时写）：

1. `tools/bake_world_scene.gd`
2. `tools/world_scene_spec.gd`
3. `scenes/world/**`（5 个 `.tscn` + 5 个 `.tres`）
4. `_mdtest/scene_bake_check.gd`
5. `docs/FEEDBACK-scene-tilemap-exec.md`

---

## §2 数据基准

### §2.1 🔴 先分清两件事（本线做第一件，第二件另派线）

用户要的是「**在 Godot 2D 场景里直接看这个村庄**」。这件事分两步：

| 步骤 | 内容 | 风险 | 本线 |
|---|---|---|---|
| **第一步（Stage 1）** | 写**烘焙器**：从 `data/frames.json` + `asset_draw.gd` 的贴图表出发，生成真正的 Godot 场景文件（`.tscn` + `.tres`），**入库**。运行时**完全不动**（游戏画面还是 L8 的平铺管线）。 | **低**：不碰任何运行时文件 | ✅ **本线** |
| **第二步（Stage 2）** | 把运行时从 `world_view.gd` 的 `_draw()` 切到「实例化烘焙好的场景」：碰撞、y-sort、遮挡全部改由节点承担。 | **高**：动 `world_view.gd`/`main.gd`，可能打破 `sort_check.gd`/`asset_draw_check.gd` 的断言 | ❌ **另派线** |

**Stage 2 的触发条件（写清楚，别提前做）**：
1. 总策划在 Godot 编辑器里打开烘焙场景、确认「这就是我要看的地图」；
2. L8 的临时瓦片被美术的正式 32px 瓦片替换完；
3. 总策划明确点头。

**本线交完 Stage 1 后必须停下来汇报，不要自己接着做 Stage 2。**

### §2.2 为什么编辑器里现在是空的（先把事实讲清楚）

- `scenes/main.tscn` 只有 5 个节点：`Main(Control)` → `CameraRig(Node2D)` → `WorldView(Control)` / `Player(Node2D)`；`Main` 下 `HUD(Control)` / `DisplayManager(Node)`。
- **整个场景里没有任何 `TileMap` / `Sprite2D` 节点**（grep 零命中）⇒ 地图不是场景对象。
- 地图是 `scripts/world_view.gd` 在 `_draw()` 里**按 shape 逐个画**的（文件第 3 行原话：「没有图片资源、没有场景继承 —— 全是数据」）。
- **没有任何脚本带 `@tool`** ⇒ 脚本不在编辑器里执行 ⇒ 编辑器 2D 视图里**看不到任何东西**。

⇒ Stage 1 交付后，`scenes/world/world_a5_2026.tscn` 打开就是**看得见摸得着的格子**。

### §2.3 视觉口径（`docs/地图视觉口径.md` §1，五条，逐条适用）

- **C1** 最小单位是 **32×32 单方格可平铺**；河/路/田/地面/环岛一律 32px 瓦片。
- **C2** 数据只圈方格区域，**不写造型**。
- **C3** 贴图与地图尺寸解耦 ⇒ 放大 1.5 倍不得重画贴图。
- **C4** **缺图降级是容错，不是验收通过**。
- **C5** **每个 shape 都要能说出铺什么贴图**。

### §2.4 节点映射表（本线的核心产物）

| frames.json 的 shape | 场景节点 | 贴图来源 | 层 / z |
|---|---|---|---|
| `rect` 无 label（地面） | `TileMapLayer` cell | `asset_draw.ground_tex(frame_id)` → `ground_*_tiles.png` | `Ground` z=−100 |
| `rect` 无 label（田块） | `TileMapLayer` cell | `asset_draw.field_tex(frame_id)` | `Field` z=−95 |
| `rect` `road:true` | `TileMapLayer` cell | `asset_draw.road_tex(frame_id)` | `Road` z=−90 |
| `polygon` label「河」 | `Polygon2D`（uv + texture_repeat） | `asset_draw.river_tex(frame_id)` | `Water` z=−88 |
| `polygon` label「路」（环道） | `Polygon2D` | `asset_draw.polygon_tex(frame_id,"路")` | `Overlay` z=−86 |
| `polygon` label「岛」 | `Polygon2D` | **目前缺**（`roundabout_island_soil/green` 未交）⇒ 纯色降级 + 登记缺口 | `Overlay` z=−85 |
| `polygon` label「山」 | `Polygon2D` | **目前缺**（山地表瓦未交）⇒ 纯色降级 + 登记缺口 | `Overlay` z=−84 |
| `house`（lot 底色） | `Polygon2D`（lot 外框） | 无（底色）或 `houses/<族>/<帧>_base.png` | `Houses` z=−70 |
| `house` 墙（按行） | `Sprite2D`（一格高/半高） | base 图的墙条 或色块 | `Props`（y_sort） |
| `house` 门洞 | `Sprite2D` | base 图 或色块 | `Props`（y_sort） |
| `house` 屋顶 | `Sprite2D`（wings 外框） | `houses/<族>/<帧>_roof.png` 或色块 | `Props`（y_sort） |
| `house` 家具 | `Sprite2D` | 家具贴图 或色块 | `Props`（y_sort） |
| `circle` 树（label 含「槐」） | `Sprite2D`（底边对齐冠底） | `assets/village/scene/tree_a*.png` | `Props`（y_sort） |
| `circle` 井（label 含「井」） | `Sprite2D` | `well_old_a*.png` | `Props`（y_sort） |
| `rect` label「碑」 | `Sprite2D` | `stele.png`（界碑删除线落地后作废） | `Props`（y_sort） |
| `rect` label「坝」 | `Sprite2D` | `dam.png` | `Overlay` z=−80 |
| `rect` label「路标」 | `Sprite2D` | 缺 ⇒ 色块 | `Props`（y_sort） |
| 玩家 | **不放进烘焙场景** | — | 运行时仍是 `CameraRig/Player` |

**贴图解析必须复用 `scripts/asset_draw.gd`，不许另写一套查表**（§0.6 已把 asset_draw.gd 列为只读——**调用**它的函数是允许的，**修改**它不允许）。

### §2.5 🔴 三个引擎坑（探针已实测，**照抄，别自己试错**）

1. **`create_tile()` 必须在 `add_source()` 之后、经 `get_source(id)` 取回引用再调。**
   - 「add_source 之前 create」⇒ tiles=0；「add_source 之后用**原引用** create」⇒ **也**是 0。
   - 正确顺序：`ts.add_source(src, id)` → `ts.get_source(id).create_tile(Vector2i(x,y))` → `get_tiles_count()` 变 1。
2. **`PackedScene.pack()` 默认不打包子节点 ⇒ 必须给每个子节点设 `owner = root`。**
   - 不设 owner ⇒ 读回 `children=0`；设了 ⇒ `children=2`（实测）。
3. **`TileMapLayer` 没有物理碰撞 API**（`add_collision_polygon()` 不存在、`enabled_physics` 属性不存在）。
   ⇒ **墙的碰撞仍然走 `scripts/frame_data.gd` 的 `solid_rects`**，本线不碰它。

其它已实测可用能力（直接用，不用再探）：

- `TileMapLayer.set_cell(coords, source_id:int, atlas_coords, alternative)` —— **第二参是 int**，不是 Vector2i。
- 一个 `TileSet` 可挂多个 `TileSetAtlasSource`（`add_source(src, id)`），`set_cell` 按 source_id 分派。
- `Polygon2D` 有 `texture` / `uv` / `texture_repeat`（`CanvasItem.TEXTURE_REPEAT_ENABLED`=2）⇒ **任意形状都能 uv 平铺**。
- `Sprite2D.centered=false` + `offset` ⇒ 可做**底边对齐**。
- `Node2D.y_sort_enabled` ⇒ 前景层遮挡可交给节点排序。
- `.gitignore` **不忽略** `scenes/`、`assets/`、`*.tscn`、`*.tres` ⇒ 产物可以入库。

### §2.6 y-sort 口径必须与现有 sort_y 逐位一致

现有运行时排序键（`scripts/world_view.gd:24-31` 注释，`sort_check.gd`/`asset_draw_check.gd` 钉着）：

| 对象 | 排序键 |
|---|---|
| 玩家 | `position.y + RADIUS*0.7` |
| 树 | 冠底缘 `center.y + radius` |
| 井 | 盘底缘 `center.y + radius` |
| 家具 | 占地 `rect.end.y` |
| 墙 | 该行墙格**南沿** |
| 门 | 该门格**北沿**（L9 改） |
| 屋顶 | wings 南沿 |

**烘焙时的做法**：所有前景节点的 `position.y` **就设成上表的排序键**，`Sprite2D.centered=false` ⇒ 精灵底边 = `position.y` ⇒ Godot 的 y_sort 结果与现有 sort_y **天然一致**。这样 Stage 2 才切得干净。

### §2.7 已知数据缺口（照实登记，**不许自己造图**）

- **D1**：A1–A3 的河只铺到 x=3200（103 点），A4/A5 铺到 4800（152 点）⇒ **A1–A3 的河在 x=3200 处断掉**。本线只读数据，**不修**；登记给 A1–A3 重排线。
- **美术缺口 16 行**（照抄 `docs/FEEDBACK-asset-tile-wire-exec.md` §8 的表）：ground_a4/a5、road_a1..a5、field_a1..a5、river_a1..a5、**roundabout_island_soil/green**、**山地表瓦**、**roundabout_curb（还需引擎旋转能力）**、houses/{market,shen,zhou,zheng,toyshop,school}/{a4,a5}_{base,roof}、tree_a4/a5、well_old_a4/a5、stele_a1..a5、lu/a3_roof。
  ⇒ 烘焙时缺图**一律纯色降级**（C4），并在反馈文档的缺口表里**逐项标注「烘焙后仍缺」**。

---

## §3 必改清单

### §3.1 写 `tools/world_scene_spec.gd`（映射表，单独成文件）

内容：
- §2.4 那张映射表的**可执行版**（shape 类型 + label → 节点类型 + 贴图 kind + 层名 + z）。
- 每个 kind 对应 `asset_draw.gd` 的**哪个函数**（`ground_tex` / `road_tex` / `field_tex` / `river_tex` / `polygon_tex` / `house_tex` / `prop_tex`）。
- 缺 kind 的降级策略（纯色 + 登记）。

**不许**在这里写死贴图文件名——一律走 `asset_draw.gd`，否则 L8 换图会失效。

### §3.2 写 `tools/bake_world_scene.gd`（烘焙器）

流程：

1. 读 `data/frames.json`（**只读**）→ 逐帧 `a1_1926` … `a5_2026`。
2. **建 TileSet**：每帧一个 `TileSet`，`tile_size = (32,32)`；对每个用到的贴图建一个 `TileSetAtlasSource`（`texture_region_size = (32,32)`），`add_source(src, id)`，**再经 `get_source(id).create_tile()` 建 tile**（§2.5 坑 1）。
   - 贴图不是 32px 整数倍（美术图集常见）⇒ **只取整数个 32px 区域，余量丢弃**，并在反馈里登记。
3. **建场景树**（每帧一个根节点 `World<帧号>`）：

   ```
   World_a5_2026 (Node2D)
   ├── Ground   (TileMapLayer, z_index=-100)
   ├── Field    (TileMapLayer, z_index=-95)
   ├── Road     (TileMapLayer, z_index=-90)
   ├── Water    (Polygon2D,   z_index=-88)
   ├── Overlay  (Node2D,      z_index=-84)   # 环道/内岛/山/坝
   ├── Houses   (Node2D,      z_index=-70)   # 房屋底色
   └── Props    (Node2D, y_sort_enabled=true) # 墙/门/屋顶/家具/树/井/碑/路标
   ```

   - **前景排序节点 `Props` 必须 `y_sort_enabled = true`**；其余层 `y_sort_enabled = false`（背景层固定顺序，见 `world_view.gd:12-15`）。
   - **玩家不放进场景**（运行时节点）。
4. **按 shape 填节点**：
   - rect（地面/田/路）→ 对应 `TileMapLayer.set_cell()`，cell 坐标 = `round(pos/32)`。
   - polygon → `Polygon2D`，`polygon` = 原始 points（**世界坐标，不平移**），`uv` = 同样的 points（⇒ 1:1 平铺），`texture_repeat = TEXTURE_REPEAT_ENABLED`。
   - circle（树/井）→ `Sprite2D`，`centered=false`，`position = (center.x, center.y + radius)`（**底边对齐**）。
   - house → 底色 `Polygon2D`（lot 外框）＋ 墙/门/屋顶/家具 `Sprite2D`（墙按行拆，排序键照 §2.6）。
     - 家具与墙的格子数据来自 `HouseShape.furniture_rects()` / `house_shape.gd` 的既有函数（**只读调用**）。
     - **`house_shape.gd` 一个字都不许改**。
5. **打包并保存**：
   - `TileSet` → `scenes/world/tileset_<帧号>.tres`（`ResourceSaver.save`）。
   - 场景 → `PackedScene.pack(root)`，**每个子节点 `owner = root`**（§2.5 坑 2）→ `scenes/world/world_<帧号>.tscn`。
6. **自检**：每帧打印 `cells 总量 / polygon 数 / sprite 数 / 缺图 kind 列表`，写进 stdout 供人工核对。

**烘焙器必须支持 `--frame <id>` 只烘一帧**（调试用），默认烘五帧。

### §3.3 场景命名与路径规范

| 帧 | 场景文件 | TileSet |
|---|---|---|
| a1_1926 | `scenes/world/world_a1_1926.tscn` | `scenes/world/tileset_a1_1926.tres` |
| a2_1951 | `scenes/world/world_a2_1951.tscn` | `scenes/world/tileset_a2_1951.tres` |
| a3_1976 | `scenes/world/world_a3_1976.tscn` | `scenes/world/tileset_a3_1976.tres` |
| a4_2001 | `scenes/world/world_a4_2001.tscn` | `scenes/world/tileset_a4_2001.tres` |
| a5_2026 | `scenes/world/world_a5_2026.tscn` | `scenes/world/tileset_a5_2026.tres` |

`scenes/world/` 目录**新建**。`.tscn` 里的贴图路径必须是 `res://assets/...`（相对 res 的绝对路径），**不许用绝对磁盘路径**。

### §3.4 新建 `_mdtest/scene_bake_check.gd`（断言）

**逻辑断言（headless 可跑）**：

| # | 断言 |
|---|---|
| S1 | 五个 `.tscn` 与五个 `.tres` **都存在**且能被 `ResourceLoader.load()` 读回（不报错） |
| S2 | 每个 `.tscn` 的根是 `Node2D`，名字 = `World_<帧号>` |
| S3 | 每个场景的子节点**结构**符合 §3.2 的七层（名字与数量） |
| S4 | `Props` 节点的 `y_sort_enabled == true`，其余层 == false |
| S5 | `Ground`/`Field`/`Road` 的 `used_cells()` 数量 **> 0**，且与「该帧对应 kind 的 shape 覆盖格数」一致（用同一套换算代码复算，允许 ±0） |
| S6 | 每个 `TileMapLayer` 的 `tile_set != null`，且其 source 数量 ≥ 1、每个 source 的 `get_tiles_count() ≥ 1` |
| S7 | 每个 `Polygon2D`（河/环道/岛/山）的 `polygon.size() > 0`；`texture != null` 的那些 `texture_repeat == 2` |
| S8 | 所有前景 `Sprite2D`：`centered == false`；且 `position.y` 落在该帧 y 范围内 |
| S9 | **无 `TileMapLayer` 出现在前景层**（前景必须是 Sprite2D/Polygon2D，碰撞仍走代码） |
| S10 | 场景里**没有玩家节点** |

**像素断言（窗口模式跑，headless 读不到帧缓冲）**：

| # | 断言 |
|---|---|
| S11 | 渲染 `world_a5_2026.tscn` 到 PNG，**地面区域的颜色数 ≥ 3**（不是纯色块） |
| S12 | 渲染 `world_a1_1926.tscn` 到 PNG，颜色数 ≥ 3 |

> 窗口模式跑法见 §0.1 的提示：**不带 `--headless`**。参考 L8 的 `_mdtest/tile_wire_check.gd` 怎么写窗口模式那套。

### §3.5 文档回写

- `docs/PROMPT-overseer.md`：本线那一行改成「✅ Stage 1 已交付并验收（附场景文件路径）」＋「Stage 2 待拍板」。
- `docs/待解决事项.md`：状态行加「地图场景化 Stage 1 交付」。
- **新建** `docs/FEEDBACK-scene-tilemap-exec.md`（≤120 行），必含：
  1. 五帧的 cells/polygon/sprite 数量表；
  2. 美术缺口表（照抄 L8 的 16 行，标注「烘焙后仍缺」）；
  3. D1 河断点登记；
  4. 「打开哪个文件能在编辑器里看到什么」的说明；
  5. 明确写「**`.tscn` 是产物不是源，手改会被烘焙器覆盖**」；
  6. 明确写「**Stage 2（运行时切场景）未做，等总策划拍板**」。

### §3.6 明确不做的事

1. **不改运行时**（`world_view.gd` / `main.gd` / `frame_data.gd` 一个字都不动）。
2. **不删、不改** L8 的 `_draw()` 平铺管线。
3. **不修 D1 河宽**（数据归地图线）。
4. **不造图、不切美术图集**（缺图就降级）。
5. **不碰 `data/frames.json`**。
6. **不做碰撞改造**（碰撞仍在代码里）。
7. **不做 Stage 2**（运行时切场景）。
8. **不写编辑器插件**（`EditorPlugin` 那条路留到以后真有需要再说）。
9. **不碰小地图**（用户 2026-11-26 拍板往后放）。

---

## §4 验收

### §4.1 烘焙产物自检

- `python`/`godot --headless` 跑烘焙器 → 五帧全部成功、退出无错。
- `_mdtest/scene_bake_check.gd` 逻辑断言 S1–S10 **全绿**。
- 窗口模式像素断言 S11–S12 **全绿**。

### §4.2 七套回归 + L8 全绿，且**逐位不变**

- `greybox` / `camera` / `hud_layout` / `sort` / `asset_draw` / `evidence_archive` / `display` **全部 fails=0**。
- **`tile_wire_check` 必须仍然 fails=0**（L8 的成果不许退化）。
- §0.3 那张基线数字表**逐位相同**（本线不改运行时，理论上必然相同；变了就是有副作用，必须查清）。

### §4.3 人工验收（**必须由总策划看，不能自己签字**）

1. 在 Godot 编辑器里打开 `scenes/world/world_a5_2026.tscn` ⇒ 2D 视图里**能看见地面瓦片、路、河、环岛、房屋块、树**（不是空场景）。
2. 打开 `world_a1_1926.tscn` ⇒ 能看见 1926 年的村子（弯路、四栋房、碎田）。
3. 打开 `world_a4_2001.tscn` ⇒ 能看见 2001 年的工地版超市。
4. 报告：「编辑器里看到的和游戏里运行的**哪里一样、哪里不一样」。

> 本线**不要求**编辑器画面与游戏画面像素一致（两套渲染路径并存是 Stage 1 的已知状态）。但**必须**说明差异清单。

### §4.4 交付物清单

- 5 个 `.tscn` + 5 个 `.tres`（入库）。
- `tools/bake_world_scene.gd` + `tools/world_scene_spec.gd`（入库）。
- `_mdtest/scene_bake_check.gd`（入库）。
- `docs/FEEDBACK-scene-tilemap-exec.md`（≤120 行，入库）。
- 美术缺口表（16 行，随反馈文档给出，可直接转发美术同学）。

---

## §5 收工

### §5.1 提交（**精确 add，绝不 `-A`**）

```powershell
git add tools/bake_world_scene.gd tools/world_scene_spec.gd `
        scenes/world/world_a1_1926.tscn scenes/world/world_a2_1951.tscn `
        scenes/world/world_a3_1976.tscn scenes/world/world_a4_2001.tscn `
        scenes/world/world_a5_2026.tscn `
        scenes/world/tileset_a1_1926.tres scenes/world/tileset_a2_1951.tres `
        scenes/world/tileset_a3_1976.tres scenes/world/tileset_a4_2001.tres `
        scenes/world/tileset_a5_2026.tres `
        _mdtest/scene_bake_check.gd docs/FEEDBACK-scene-tilemap-exec.md `
        docs/PROMPT-overseer.md docs/待解决事项.md
```

提交信息建议：

```
feat(scene): 地图场景化 Stage 1 —— 从 frames.json 烘焙五帧 Godot 场景（TileMapLayer 地面/路/田 + Polygon2D 任意形状 + Sprite2D 前景 y_sort），编辑器 2D 视图可见
```

### §5.2 提交前自查

```
git status --short          # 确认 add 列表里没有别人的文件
git diff --cached --stat    # 确认只有上面那些
grep -c $'\ufffd' <每个新文件>   # 确认没有乱码（PowerShell 下用 python 扫）
```

### §5.3 反馈文档必含项

见 §3.5。

---

## §6 边界提醒

1. **`.tscn` 是产物不是源** —— 手改会被覆盖。要改地图，改 `data/frames.json` 再重跑烘焙器。
2. **`data/frames.json` 只读** —— 本线一个字都不许动；地图线改完你重跑烘焙器就行。
3. **`scripts/world_view.gd` 一个字都不许动** —— L8 刚交付，动它就可能把平铺管线搅坏。
4. **`TileMapLayer` 没有碰撞** —— 墙的碰撞仍走 `frame_data.gd` 的 `solid_rects`，别以为做了场景就有碰撞了。
5. **缺图就降级**（C4）—— 纯色不是验收通过，缺口必须登记。
6. **Stage 2 未做** —— 运行时还是 `_draw()`。交完停下汇报，等总策划拍板。
7. **只精确 `git add`** —— 绝不 `git add -A`。
8. **不要用 `git checkout --`** —— 被沙箱拦；用 `git show HEAD:<path>` 写回。
9. **不要用 pwsh `-replace` 改源码** —— 会破坏缩进；写独立脚本改。
10. **落盘必扫 U+FFFD**。
11. **本机没有 pwsh** —— 跑 `.ps1` 要用 `powershell -NoProfile -ExecutionPolicy Bypass -File`；直接 `& .\x.ps1` 会被执行策略拦。
12. **不要跑 `export_seed()` / 任何生成器** —— 会覆盖房屋数据。

---

## §附 依据

| 依据 | 位置 |
|---|---|
| 视觉口径 C1–C5 | `docs/地图视觉口径.md` §1–§3 |
| shape → 贴图对应表（权威） | `docs/地图视觉口径.md` §2 |
| 贴图解析函数（只读调用） | `scripts/asset_draw.gd`：`TILE_FILES`(:58)、`POLYGON_TILE_KIND`(:94)、`ground_tex`/`road_tex`/`field_tex`/`river_tex`/`polygon_tex`/`tile_tex` |
| 现有渲染模型（两层 + 排序键） | `scripts/world_view.gd:12-42`（头部注释） |
| 排序键逐项对照 | `scripts/world_view.gd:24-31`；`scripts/player.gd`、`scripts/house_shape.gd` |
| L8 交付现状 | `docs/FEEDBACK-asset-tile-wire-exec.md`（117 行）＋ `docs/PROMPT-asset-tile-wire-exec.md`（410 行） |
| 美术缺口 16 行 | `docs/FEEDBACK-asset-tile-wire-exec.md` §8 |
| D1 河断点 | `data/frames.json`（a1–a3 河 103 点 x≤3200；a4/a5 152 点 x≤4800）＋ `scripts/world_view.gd:264` 画布写死 3200×416 |
| Godot 能力实测探针 | `lab/_probe_tilemap.gd`、`_probe_tilemap2.gd`、`_probe_tilemap3.gd`、`_probe_tilemap4.gd`、`_probe_tilemap5.gd`、`_probe_tilemap6.gd`（未入库，可参考可重跑） |
| 用户拍板 | 2026-11-26「1.走方案B　2.（小地图）这点应该要往后放，因为地图的原因」 |
| 场景现状（为何编辑器里是空的） | `scenes/main.tscn`（5 节点）＋ `scripts/world_view.gd:3` ＋ 全仓无 `@tool` |
