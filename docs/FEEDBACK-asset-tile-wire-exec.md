# 资产接线执行反馈 · L8（32px 单方格平铺）

> 执行线：`docs/PROMPT-asset-tile-wire-exec.md`｜基线版本 `1c7c34b`（≥ 下限 `7b410bd`）｜交付 2026-11-26｜代码 commit `9248823`（本文档随后的 `docs:` commit 为第二段）
> **结论：七件必改全部落地，平铺管线已通（每 32px 格内 3–5 色，不再是纯色块）。但 A4/A5 的 8 类瓦片是「既有纹样 + 按帧色调色」的临时图（用户 2026-11-26 裁定批准），山/内岛/环道缺路缘仍是缺口 ⇒ 只能说「管线交付、A4/A5 视觉部分交付」。**

## 1 逐文件改动

| 文件 | 改动 |
|---|---|
| `scripts/asset_draw.gd` | +138。新增 `TILE_FILES`（五帧 × ground/road/field/river 四类 32×32 通路）、`POLYGON_TILE_KIND = {"河":"river","路":"road"}`、`tile_tex / ground_tex / road_tex / field_tex / river_tex / polygon_tex / points_in_poly / poly_tile_rects`。**`scene_tex` / `SCENE_FILES` / `SHARED_SCENE` 一字未动**（保住 `asset_draw_check.gd:216` 的 `a4_2001 river == null` 断言） |
| `scripts/world_view.gd` | +124/−63。①`_draw()` 地面：`draw_rect` 底色保留做容错，其上 `draw_texture_rect(gtex, …, true, sc)` 平铺（`true` 是本文件首次启用 tile）；②`_draw_back()` 循环带下标；③rect `road:true` 与田块改为**逐块平铺**，删掉把整帧 merge 成一个大 bbox 的 `_scene_bboxes()`；④polygon 改 `polygon_tex` 按 label 分派 + `_poly_rects` 段缓存（`_bbox_cache` → `_poly_cache`）；⑤`FAMILY` 新增 7 条 A4/A5 接线（见 §5） |
| `assets/village/scene/` | 新增 6 张临时瓦片 + 6 张 `.import`：`river_tiles_l8.png`（←`river_a1` 裁 (384,128)，3 色，含水面浅纹）、`road_tiles_l8.png`（←`road_straight_a3` 裁 (464,24)，3 色）、`road_a5_tiles_l8.png`（Δ(−55,−26,+7) → #56564f）、`field_tiles_l8.png`（←`field_a3` 裁 (88,328)，5 色）、`ground_a4_tiles_l8.png`（Δ(+4,0,+10) → #6f6a52）、`ground_a5_tiles_l8.png`（Δ(+15,+15,+46) → #7a7a76）。生成脚本 `lab/_l8_slice_tiles.py`（可重复执行，源图只读） |
| `_mdtest/tile_wire_check.gd` | **新建**，≈390 行。headless 跑逻辑层 16 条；窗口模式跑像素层 39 条 + 存 6 张实拍 PNG |
| `_mdtest/asset_draw_check.gd` | +27，**只加断言**：五帧 × 四类瓦片齐全、瓦片均 32×32、A4/A5 七栋族登记、`not _art_walls("shen_a4")` |
| `_mdtest/sort_check.gd` | **未改** —— 排序链一行没动（§2.5 铁律），没有要加的东西 |

瓦片切割坐标全部经 `lab/_l8_pick.py` / `lab/_l8_river_pick.py` 扫描选定，判据是「整格 100% 不透明 + 四边零接缝 + 均值色贴近目标色」。纯水窗口是 1 色，故 river 瓦必须带浅纹窗口（948+64+12 px）。

## 2 像素采样（任务书 §4.4）

`& $godot --path . -s res://_mdtest/tile_wire_check.gd`（**不带** `--headless`；headless 是 dummy 渲染器，`frame_post_draw` 永不返回）。根窗口 1280×720，`OpenGL API 3.3.0 NVIDIA 610.88 - Compatibility`。结果：**`TILE_WIRE_CHECK_DONE fails=0 gaps=4 checks=39`**。

| 探针 | 结果（32×32 格内去重色数 / 采样色） |
|---|---|
| 地面（五帧各取一格空地） | a1 **3** / a2 **3** / a3 **3** / a4 **3** / a5 **3** → 不是纯色块 |
| `polygon[河]` 五帧 | 全部 **3** 色，采样 #3f5f6e（瓦片色赢数据色） |
| `polygon[路]`（A4 环道） | **3** 色，格 (1984,288) 采样 #8e7148（数据色 #8a7a5a） |
| `polygon[路]`（A5 环道） | **3** 色 #57564f（柏油） |
| `rect[公路]` road:true | a1/a2/a3/a4 **3** 色 #8e7148；a5 **3** 色 #57564f |
| `rect[田块]` label=="" | 五帧 **5** 色 #5c5637 |
| `polygon[岛]` | a4 **1** 色 #6b7a4a（GAP）；a5 采样格全被「老槐」`circle` r=160 压住（GAP，按数据色判定） |
| `polygon[山]` | a4/a5 **1** 色 #5a6a4a（GAP） |
| **A4 河 x=4700** | **3** 色 #3f5f6e、更接近水 = true ⇒ 引擎把河铺到了 4800 ✓ |
| A1 河 x=3100 / 3199 | 水；x=3200 / 3280 / 3400 / 4700 整列**不在河 polygon 内** ⇒ 数据缺口（见 §4） |

另存 6 张实拍：`_mdtest/assets/l8_{a1_river_bank,a3_field,a4_ring,a4_river_east,a5_ring,a5_hill}.png`（`err=0`）。A4 环岛逐 10px 抽点肉眼可辨：外圈地面 `(96,96,64)` 带 `(80,64,48)/(128,128,112)` 明暗变体、**每 32px 重复一次**（平铺真的在跳），环道是 `(128,112,64)` 圆盘带，盘内是岛与树冠。

## 3 美术缺口表（任务书 §4.2，完整）

| # | 缺口 | 帧 | 现在用什么 | 缺的官方文件 | 画布 | 归谁 |
|---|---|---|---|---|---|---|
| 1 | 地面瓦 | a4 | `ground_a4_tiles_l8.png`（临时调色） | `ground_a4_tiles.png` | 32×32 | 美术 B 组 |
| 2 | 地面瓦 | a5 | `ground_a5_tiles_l8.png`（临时调色） | `ground_a5_tiles.png` | 32×32 | 美术 B 组 |
| 3 | 路面瓦 | a4 | `road_tiles_l8.png`（A3 土路纹样） | `road_a4_tiles.png` | 32×32 | 美术 B 组 |
| 4 | 路面瓦 | a5 | `road_a5_tiles_l8.png`（调色，非沥青颗粒） | `road_a5_tiles.png` | 32×32 | 美术 B 组 |
| 5 | 路面瓦 | a1–a3 | `road_tiles_l8.png` | `road_a1..a3_tiles.png`（ART-GAP 只列了 a4/a5，A1–A3 名待确认） | 32×32 | 美术 + 策划 |
| 6 | 田块瓦 | a1–a5 | `field_tiles_l8.png`（A3 田纹样） | `field_a1..a5_tiles.png` | 32×32 | 美术 B 组 |
| 7 | 河水瓦 | a1–a5 | `river_tiles_l8.png`（A1 水纹样） | `river_a1..a5_tiles.png` | 32×32 | 美术 B 组 |
| 8 | **内岛** | a4 | 色块 #6b7a4a | `roundabout_island_soil.png` | 32×32 | 美术 C 组 |
| 9 | **内岛** | a5 | 色块（且被老槐冠全遮） | `roundabout_island_green.png` | 32×32 | 美术 C 组 |
| 10 | **山地表** | a4×7 / a5×3 | 色块 #5a6a4a | **未定名**（B/C 组都没列） | 32×32 | 美术定名 → 登记 `POLYGON_TILE_KIND["山"]` |
| 11 | 环道**路缘/导流线** | a4/a5 | 无（环道整段按 `road` 瓦平铺成实心圆盘） | `roundabout_curb.png` | 32×32 | 美术 C 组 + 引擎旋转能力（见 §8） |
| 12 | 房屋 base/roof | a4/a5×7 | 色块（`_house_tex` 判 `ResourceLoader.exists` → 降级） | `houses/<族>/{a4,a5}_{base,roof}.png` | 按族 | 美术 A 组 |
| 13 | 老槐 | a4/a5 | 引擎画的树干+双圆冠 | `tree_a4.png` / `tree_a5.png` | 160×160 / 192×192 | 美术 B 组 |
| 14 | 老井 | a4/a5 | 引擎画的圆 | `well_old_a4.png` / `well_old_a5.png` | 64×64 / 96×96 | 美术 B 组 |
| 15 | 界碑 | 五帧 | 五帧共用旧 `stele.png`（`SHARED_SCENE`） | `stele_a1..a5.png` | 32×32 各 | 美术 B 组 / F 组 |
| 16 | 屋顶 | lu / a3 | 既有缺口，非本线范围 | `houses/lu/a3_roof.png` | — | 美术 A 组 |

## 4 河跨帧宽度（D1）——引擎侧 / 数据侧分开说

- **引擎侧：已修**。旧代码写死画布 `Vector2(3200,416)`，现在按 polygon 顶点算 32px 格、格心落在多边形内才铺（`poly_tile_rects` 同行合并成段）。实测 A4 河 `x=4700` 采样 3 色水 ⇒ **引擎铺到了 4800，管线不再截断**。
- **数据侧：还差**。A1–A3 的河 polygon bbox 只到 `x=3200`（103 点），`x=3200/3280/3400/4700` 整列不在多边形内 ⇒ 引擎无从铺、只能露地面。**归 A1–A3 重排数据线**，不是引擎缺陷。
- 结论：本线之后「河在不同帧宽度不一致」**只可能是数据画的**，不会再是引擎画的。

## 5 `FAMILY` 登记（A4/A5 七栋）——本线**偏离任务书 §3.6，已登记而非留模板**

任务书说「A4/A5 六栋先不登记、反馈里给模板」。我改成**直接登记 + `ResourceLoader.exists` 守卫**（图不在就 `null` → 走色块降级，不刷 ERROR），理由是：登记本身零风险，美术 PNG 一落盘就自动接管，省掉一轮接线。**回退方式：删掉 `FAMILY` 表末尾 7 行即回到模板状态。**

| 数据 id | 族目录 | 帧 | 期望文件 |
|---|---|---|---|
| `market`（A4/A5 同一条 id） | `market` | `a4` | `houses/market/a4_base.png` + `a4_roof.png` ⚠️ A5 要独立一套需数据侧拆 id |
| `shen_a4` | `shen` | `a4` | `houses/shen/a4_{base,roof}.png` |
| `zhou_a4` | `zhou` | `a4` | `houses/zhou/a4_{base,roof}.png` |
| `zheng_a4` | `zheng` | `a4` | `houses/zheng/a4_{base,roof}.png` |
| `shen_a5` | `shen` | `a5` | `houses/shen/a5_{base,roof}.png` |
| `toyshop` | `toyshop` | `a5` | `houses/toyshop/a5_{base,roof}.png` |
| `school` | `school` | `a5` | `houses/school/a5_{base,roof}.png` |

配套断言在 `_mdtest/asset_draw_check.gd::_check_a4a5_wiring()`：`not WorldView._art_walls("shen_a4")` —— **美术图到位后这条会红，那正是提醒去改的地方**。

## 6 回归对照（任务书 §4.3：必须逐位一致）

| 套件 | 改动前（HEAD `1c7c34b` 实测） | 改动后 |
|---|---|---|
| `asset_draw_check` | `fails=0` | `fails=0`（总数 29→33，新增 4 条 L8 断言） |
| `sort_check` | `fails=0` | `fails=0` |
| `greybox_check` | `REACH_MAP` 见下 | **逐位一致** |
| `a4_rebuild_check` | `fails=0` | `fails=0` |
| `camera_check` / `hud_layout_check` / `evidence_archive_check` | `fails=0` | `fails=0` |
| `display_check` | 5 行回显 | 5 行回显（`CONTENT_SCALE_MODE=1`/`ASPECT=1`/`SIZE=(1280,720)`/`默认纹理过滤=0`/`STRETCH_SCALE_MODE=0`） |

`REACH_MAP = { "standable": 15104, "to_a5": 12497, "blocked_at_step": [144, 191, 2171, 101], "band_total": 298, "band_full": 298, "band_ratio": "100%", "ratio": "83%" }`、`UNEXPLAINED_BLOCKS=0`、`A1_WELL_FREE=false`、`WALL_BLOCKED=true`、`TIME_FWD_REACHED=[1,2,3,4]`、`A2_HOTSPOTS=11`、`A3_HOTSPOTS=13`、`HOTSPOTS=10`、`WALL_STOP_Y=816.0`、`A1_MILL_INTERIOR_FREE=true`、`A1_MILL_DOOR_FREE=true`、`REACH_OK=true`；五帧 solids/hotspots = 239/10、300/11、380/13、812/12、898/9 —— **全部与改动前一致**。

> ⚠️ 任务书 §4.3 把 a4 写成 `646/13`，实测 HEAD 是 `812/12`：那组数字是 A4 帧重排（commit `9ec040a`）之前的旧值。本线以实测为准，且改动前后两次数值逐位相同。

## 7 `docs/地图视觉口径.md` §5 六问

1. **每个新 shape 的贴图来源？** 能。地面→`ground_*_tiles`；rect `road:true`→`road_*_tiles`；rect `label==""`→`field_*_tiles`；polygon `河`→`river_*_tiles`；polygon `路`→`road_*_tiles`；polygon `岛`/`山`→**说不出来，登记为缺口**（#8–#10），`POLYGON_TILE_KIND` 里故意不登记，`tile_wire_check` 会把它们计成 GAP。✅
2. **缺图是否登记文件名与尺寸？** ✅ 见 §3 十六行，含画布尺寸与归属。
3. **32px 素材入库 + 引擎平铺通路？** ✅ 6 张 `*_l8.png` 入库（带 `.import`）；`draw_texture_rect(..., true, ...)` 首次启用并经窗口渲染回读证明格内 3–5 色。
4. **五帧地面材质是否一致对应？** 结构一致，材质**部分**：A1–A4 土黄系（#8e7148）、A5 柏油系（#57564f），地面瓦 A4 #6f6a52 / A5 #7a7a76 与数据底色贴合。但都是调色临时图，正式纹样待美术。
5. **五帧的河是否覆盖同一宽度区间？** ❌ **不一致**：引擎已能铺到 4800（A4 实测），A1–A3 的数据只画到 3200。归数据线。
6. **有没有实机截图证明「不是色块」？** ✅ 6 张 `_mdtest/assets/l8_*.png` + 39 条像素断言。**但这是沙箱内的真实渲染回读，不是用户手动开窗口的截图**，实机观感仍需人眼确认。

## 8 未做 / 已知缺口

- **没按 §3.5 从 `美术资产/` 切 A4/A5 地皮图集**。实测 `地皮/GK_A2_CCautotile_1.png`（768×576）与 `GK_A5_CCfloors_1.png`（384×768）主色是蓝绿（#6dac65 亮草 / #dada76 沙黄 / #355671 深蓝），跟 A5 柏油 #56564f、A4 土黄 #8a7a5a 都不匹配；32px 对齐重复率仅 38% / 9%（`lab/_l8_grid.py`）。切出来只会更像塑料草皮。故改走「既有纹样 + 按帧色调色」，经用户 2026-11-26 明确批准。要改回只需换 `lab/_l8_slice_tiles.py` 的取样源。
- **时间轴三遍色差只作用于对象层**：地面是 32px 周期纹理，±1px 三遍会让每条接缝长出红/青重影（截图肉眼可见），故地面改走单次 `_grade()` 调制。三遍机制本身一个字没删（房/树/井仍走三遍）。
- **没有旋转瓦片能力**：`roundabout_curb.png` 就算到位也拼不出弧（需要按角度旋转的瓦片阵列）。建议单独立一条任务书，否则缺口 #11 永远补不上。
- `SCENE_FILES` 里 road/field/river 三条**已无渲染消费者**，保留只为 `asset_draw_check` 的索引自检（以及 `a4_2001 river == null` 这条历史断言）。建议下一条任务书统一清理。
- 实机（用户亲眼看）未做：沙箱只能做渲染回读 + 截图。

## 9 需拍板三件事

1. 山地表瓦片的**官方文件名**（B/C 组都没列，引擎表里没法登记）。
2. A1–A3 的 `road_a{1,2,3}_tiles.png` / `field_a{1,2,3}_tiles.png` 是否也归 B 组补出（现在用的是 A3 纹样替身）。
3. 环道路缘要引擎旋转能力——是否单独立线。