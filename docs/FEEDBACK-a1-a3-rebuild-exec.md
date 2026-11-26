# 反馈：A1–A3 重排（任务书 `docs/PROMPT-a1-a3-rebuild-exec.md`）

- **开工 HEAD**：`c476ff0`（=任务书提交，满足「≥ `1a4e5d3`」）
- **交付提交**：本提交（父提交 `69825e0`），提交信息 `feat(frames): A1–A3 按 A5 v5 骨架重排（环岛/南北车道/河延伸/房屋落位）`。哈希见 `git log -1`。
  说明：施工期间别的线在 `c476ff0` 上并了两笔音频文档提交（`4a2774c`、`69825e0`），都只动 `assets/audio_raw/_split/*`、`docs/*`、`lab/*`，**没碰 `data/frames.json`**，所以我的重排是在它们之上做的，无需 rebase。
- **结论**：`data/frames.json` 的 a1/a2/a3 三帧已按 A5 v5 骨架重排；a4/a5/world/safe_*/start_frame/start_pos **零变化**；三套回归（`greybox_check` / `a4_rebuild_check` / `phasing_check`）全绿；S4 三组空气墙双向格数全部下降；V1 视觉统计按整窗口口径全过；路面分代材质**做不到**（数据层无此能力，见 §5-V4 与 §7-①）。

---

## 0. 交付物与改动量

| 文件 | 状态 | 说明 |
|---|---|---|
| `data/frames.json` | 修改 | 102427 → 135469 字节；`git diff --numstat` = `3188 1262`，改动全在三帧内部 |
| `lab/_a13_plan.py` | 新增（约 554 行） | 方案脚本：生成三帧 + 34 条自检 + `--write` 才落盘 |
| `docs/FEEDBACK-a1-a3-rebuild-exec.md` | 新增 | 本文件 |
| `_mdtest/greybox_check.gd` | 修改 | 见 §8：硬编码坐标必须跟着改，否则 S6 不成立；**是否随本次提交由你定** |
| `lab/_a13_stats.py` | 新增（未跟踪） | V1/V2 像素统计，PIL |

`git diff` 里其余脏文件（`_ref/art/A1_1926|A2_1951|A3_1976/*.png` 的 M、`docs/HANDOFF.md` 的 M、`美术资产/**` 的 D）**是别人的在途改动，我没碰、也没加进索引**。

---

## 1. 复现命令

```powershell
# 生成（--write 才写盘；写前校验 json round-trip 与原文件逐字节一致，a4/a5/world 零变化）
& $py lab\_a13_plan.py            # 只跑自检
& $py lab\_a13_plan.py --write    # 落盘；二次跑幂等（BYTES old=new=135469, fails=0）

# 三套回归
& $godot --path . --headless --script _mdtest/greybox_check.gd    # S6
& $godot --path . --headless --script _mdtest/a4_rebuild_check.gd # S4 + A4 自检不许变
& $godot --path . --headless --script _mdtest/phasing_check.gd    # S5

# 视觉（窗口模式，非 headless）
& $godot --path . --script _mdtest/greybox_shot.gd                # → _mdtest/greybox/*.png（1280×720）
& $py lab\_a13_stats.py                                           # → lab/_a13_stats.txt（V1/V2）
```

`$godot` = `D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe`
`$py` = `C:\Users\lyh\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe`

基线（HEAD 版数据）复跑法：`cmd /c "git show HEAD:data/frames.json > lab\_a13_head_raw.json"`（**必须用 cmd 重定向**，PowerShell 的 `Out-File` 会加 BOM+CRLF；`lab/_a13_plan.py` 的基线快照 `lab/_a13_head.json` 就是这么来的，读取用 `utf-8-sig`）→ 临时覆盖 `data/frames.json` 跑三套 → 还原。产物：`lab/_a13_base_greybox.txt`、`lab/_a13_base_a4.txt`、`lab/_a13_base_phasing.txt`。

---

## 2. 逐条字段改动清单

### 2.0 三帧共同结构（照抄 A5 v5，几何与 a4/a5 逐点相同）

shapes 顺序：**河(152 点) → 坝 rect → 主路西 rect → 主路东 rect → 北车道 polygon(4 点) → 南车道 polygon(4 点) → 环道 polygon(72 点) → 内岛 polygon(72 点) → 井 circle → 槐 circle → 田 rect(s) → 南片 rect(s) → 4 栋 house**。
热点顺序：**井 → 槐 → 坝 → 田 → 水簿**（`text` 逐字未改，只挪 `pos`）。

| 项 | 旧值（a1/a2/a3） | 新值（三帧一致） |
|---|---|---|
| 河 polygon | 103 点、铺到 x=3200 | **152 点、铺到 x=4800**（与 a4/a5 逐点相同，mismatches=0） |
| 直筒主路 | a1/a2 各 26 个 32px 小 rect（弯曲）；a3 一条 `[0,1664,3200,64]` | **删除**，改为西引道 `[0,1600,1744,128]` + 东引道 `[2352,1600,2448,128]` + 环道 72 点（圆心 (2048,1664)、R304、宽 128） |
| 南北车道 | 无 | 北 polygon `[[1984,288],[2112,288],[2112,1360],[1984,1360]]`、南 polygon `[[1984,1968],[2112,1968],[2112,3600],[1984,3600]]`（label「路」、solid:false） |
| 内岛 | 无 | polygon 72 点、R176、label「岛」、color `#6b7a4a`、solid:false |
| 老井 circle | `[1360,848]` r32 | **`[2048,832]` r32**（a1 label「老井」solid:**true** 沿用旧值；a2「老井·石板」/a3「老井·水泥」solid:false 沿用旧值） |
| 老槐 circle | `[1296,976]` r32/a2 r64/a3 r96 | **`[2048,1664]` r32/r64/r96**（半径逐年递增保留） |
| 田 | a1：28 个小 rect x1856..2560 y160..576（**压在河 polygon 里，田瓦盖住了河**，旧数据 bug）；a2/a3：`[1856,192,512,384]` | 全搬到河以南的 `[3600,320,880,384]` 一带：**a1 六小块**（`(3616,352,192,128)` `(3840,352,192,128)` `(4064,352,256,128)` `(3616,512,160,160)` `(3808,496,256,176)` `(4096,512,224,160)`，体现 1926 零散私田）；**a2/a3 一整块** `[3600,320,880,384]`（集体田） |
| 南片补满 | 无（y>1900 除主路外大半是空地，走一步就露底） | 5 个 `label:""`/`solid:false` 的 rect：`[64,1984,512,1568]` `[960,1984,768,1568]` `[576,2176,384,1376]` `[1792,1984,192,1568]` `[2176,1984,2624,1568]`（末块右到 4800、下到 3552=safe_bottom；y 起 1984 避开主路南沿 1728 与环岛外圈最低 1968） |
| 帧键顺序 | `id, year, ground, shapes, hotspots` | `id, year, ground, _note, shapes, hotspots`（与 a4/a5 对齐），`_note` 写明「A1–A3 重排：几何照抄 A5 v5，材质缺图见反馈」 |

### 2.1 房屋落位（门世界坐标 = `pos + (gate_x*32+16, gate_y*32+16)`）

| 房 | 旧 pos | 新 pos | lot 尺寸 | 门 | 说明 |
|---|---|---|---|---|---|
| `mill_a1`/`mill_a2` | (1216,448) | **(1216,512)** | 576×416 | (1456,848) | 旧 448 会压进延长后的引水湾（cols 44..49 河下沿 y=512）；选 512 不选 576 是因为 **`mill_a3` 高 544，512+544=1056 ⇒ (1400,1120) 三帧仍可站**（`phasing_check` P1 与 `greybox_check` 的 TIME 探针都钉在这个点，它必须一直是空地） |
| `mill_a3` | (1216,448) | **(1216,512)** | 576×544 | (1456,848) | 同上；三帧磨坊同址，与旧数据「三帧同址」一致 |
| `shen_a1` | (128,640) | **(64,416)** | 640×416 | (272,752) | §1 表 |
| `shen_a2` | (128,512) | **(64,416)** | 736×544 | (592,784) | §1 表（三帧沈家同址，S2） |
| `shen_a3` | (128,288) | **(64,416)** | 896×768 | (496,1168) | 同上（三层楼门开在南墙，`gate=[13,23]`） |
| `zhou_house`/`zhou_a2`/`zhou_a3` | (1792,1280) | **(576,1920)** | 384×224 | (656,2096) | 对齐 A5 小学地块，S2 |
| `lu_house`/`lu_a2`/`lu_a3` | (2304,768) | **(2304,768)** 不动 | 640×416 | (2512,1104) | 原址不压河/环道/车道；且 `_mdtest/asset_draw_check.gd:290` 用 (2304,768) 采样，原地不动保它绿 |

### 2.2 热点（`text` 一个字未改，只挪 `pos`；`reach` 沿用旧值）

| 热点 | 旧 pos | 新 pos |
|---|---|---|
| 老井 / 老井·石板 / 老井·三层水泥 | (1360,848) | **(2048,832)** |
| 老槐（三帧同题不同文案） | (1296,976) | **(2048,1664)** |
| 坝 | (512,160) | 不变 |
| 田 | (2112,320) | **(4040,512)**（新田块中心，A1 的六小块特意把它包住） |
| 水簿（diary，磨坊院内） | a1 (1328,496) / a2·a3 (1392,496) | **a1 (1328,560) / a2·a3 (1392,560)**（=旧偏移 + 磨坊下移 64） |

### 2.3 数量对比

| 帧 | 旧 shapes | 新 shapes | 旧/新 手写 solid | 热点 |
|---|---|---|---|---|
| a1_1926 | 62（polygon 1 / rect 55 / circle 2 / house 4） | **25**（polygon 5 / rect 14 / circle 2 / house 4） | 3 → 3 | 5 → 5 |
| a2_1951 | 35（polygon 1 / rect 28 / circle 2 / house 4） | **20**（polygon 5 / rect 9 / circle 2 / house 4） | 2 → 2 | 5 → 5 |
| a3_1976 | 10（polygon 1 / rect 3 / circle 2 / house 4） | **20**（polygon 5 / rect 9 / circle 2 / house 4） | 2 → 2 | 5 → 5 |

rect 变少是因为直线主路 26 段/a3 1 段换成了 2 段引道 + 环道 polygon；polygon 变多是补了车道/环道/内岛。

---

## 3. S1–S8 实测

### S1 只有三帧变化，a4/a5/world 零变化 —— **PASS**
`lab/_a13_plan.py` 断言 `a4_2001 / a5_2026 帧对象相等`、`world / safe_top / safe_bottom / start_frame / start_pos 不变`、`顶层键顺序不变`：全 PASS。整文件由 `json.dumps(parsed, indent=2, ensure_ascii=False)` 重生成，与原文 round-trip 逐字节一致（无末尾换行）⇒ 对象相等即文本相等，a4/a5 段落字节级不变。
`git diff --numstat` 只有 `data/frames.json 3188 1262`。

### S2 井/槐/沈家/周家五帧同址 —— **PASS**
脚本断言：井 `(2048,832)` r32 三帧 == a4/a5；槐 `(2048,1664)` 三帧中心 == a4/a5（半径按年 32/64/96/a4 96/a5 160 递增，属设计）；沈家 `(64,416)`、周家 `(576,1920)` 三帧 == a4/a5。

### S3 三帧河到 x=4800 且与 A5 重叠区逐点相同 —— **PASS**
`river_depth(x)` 只在 `lab/_a13_plan.py` 里实现一份（与 `_ref/houses/_design_v5.py:59` 同式），`RIVER_Y[x] = (river_depth(x)+1)*32`，`RIVER_PTS = [[x*32, RIVER_Y[x]] for x in range(150)] + [[4800,0],[0,0]]` ⇒ 152 点；与 a4/a5 河 polygon 逐点比对 **mismatches=0**。历史坑（`exp(-((x-46.5)**2)/(2*16**2))` 少个平方会让 65 列算错）已在脚本注释里标明。

### S4 三组空气墙双向格数必须比现在小 —— **PASS**（数字取项目自带 `_mdtest/a4_rebuild_check.gd`）

| 对比 | 旧：A4 独有 / 该帧独有 | 新：A4 独有 / 该帧独有 |
|---|---|---|
| A1 ↔ A4 | 4004 / 318 | **3920 / 234** |
| A2 ↔ A4 | 3873 / 318 | **3789 / 234** |
| A3 ↔ A4 | **3704** / 502 | **3508 / 306** |
| A4 ↔ A5 | 0 / 0 | 0 / 0（IoU 100%，未动） |

`lab/_a13_plan.py` 自算的口径（把 a4 的 7 座山 bbox 也计入，a4 基底 4694）给的是 4174/318→4090/234、4043/318→3959/234、3874/502→3678/306，方向一致；**以项目自带 check 的 4524 口径为准**。

### S5 phasing_check 三帧触发格数显著下降 —— **PASS**
`PAIR_0_1=108→103`、`PAIR_1_2=142→95`、`PAIR_2_3=2195→1894`、`PAIR_3_4=80→80`（A4↔A5 未动，容差 100 内 `PAIR_A4_A5_NEAR0=true`）。`fails=0 warns=0`，P1 `(1400,1120)` 五帧可站且 `step_time(+1)` 不虚化。

### S6 greybox_check 三条 —— **PASS**
`REACH_OK=true`、`UNEXPLAINED_BLOCKS=0`、`TIMES_FWD_REACHED=[1,2,3,4]`（`TIME_FWD_PHASING=false`）。
其余：`DOOR_PASSABLE=true`、`WALL_STOP_Y=880.0`、`WALL_BLOCKED=true`、`HOTSPOTS=10`、`A2_HOTSPOTS=11`、`A3_HOTSPOTS=13`、`A1_MILL_INTERIOR_FREE=true`、`A1_MILL_DOOR_FREE=true`、`A1_WELL_FREE=false`(A1 井仍 solid)、`HOTSPOT_A1/A2/A3_WELL=老井 / 老井 · 石板 / 老井 · 三层水泥`、`HOTSPOT_A1_MILL_DESK=账桌`。

### S7 solids / hotspots / START 变化逐帧解释 —— **PASS（变化全部可解释）**

| 指标 | 旧 | 新 | 解释 |
|---|---|---|---|
| `solids` a1..a5 | 238/299/379/812/897 | **238/299/379/812/897（不变）** | 河 polygon 走 `_polygon_scanlines`，每行合并成 1 条 scanline rect ⇒ 河延长到 x=4800 只改 rect 长度不改条数；井仍是 1 个 bbox（r32→64×64）；房墙格数由 `houses_data.json` 决定，本次没动 |
| `standable` 格 | 15105 | **15101（−4）** | 只来自**河的延长**：`_scan_reach` 从 y=240 起扫，x∈[3208,3368] 那 6 列在新数据里水底到 256~288，y≈240/272 的扫描点被水吃掉（按 `river_depth` 推算 7 个点，边界取整与 scanline 宽度抵掉 3 个 ⇒ 净 −4）。房墙格数**没变**（见上一行 solids 不变 ⇒ `mill`/`周家` 只换位置不换墙格数，且新址与网格对齐一致） |
| `to_a5` 格 | 12498 | **12554（+56）** | 三帧几何统一、空气墙从 3~5 米级空洞收窄（S4 数字下降）⇒ 从 A1–A3 可走到 A5 的格数上升 |
| `blocked_at_step` | [144,191,2171,101] | **[145,155,2150,97]** | 逐段空气墙收敛，第 3 段（A3→A4）降得最多，与 S4 的 3704→3508 同向 |
| `hotspots` | a1/a2/a3 = 5/5/5 | 5/5/5（`HOTSPOTS=10` 是「手写热点 + 房屋内 clue 热点」合计） | 位置全挪到新实体上，文案未改 |
| `START` | `start_frame=a5_2026`、`start_pos=[2048,1864]`、`safe_top=36`、`safe_bottom=3552` | **完全不变** | 任务书禁改；`[2048,1864]` 距环岛圆心 200，落在环道（R176–R304）上，A5 现有取值，未触碰 |

### S8 scripts/scenes/_ref/assets 零改动 —— **PASS**
`git status --porcelain` 里这几处只有别人的在途改动（`_ref/art/**` 的 M、`美术资产/**` 的 D），我的改动只有 `data/frames.json`、`lab/_a13_plan.py`、`lab/_a13_stats.py`、本文件、`_mdtest/greybox_check.gd`（见 §8）。

---

## 4. V1–V4 视觉验收

### V1 主色占比 <60%、颜色数 ≥900 —— **PASS（整窗口口径）**

| 帧 | 整窗口 colors | 整窗口主色 | 世界区 colors | 世界区主色 |
|---|---|---|---|---|
| a1_1926 | 1360 | `#8e7148` 22.8% | 171 | `#8e7148` 26.9% |
| a2_1951 | 1354 | `#8e7148` 22.8% | 171 | `#8e7148` 26.9% |
| a3_1976 | 1367 | `#8e7148` 22.8% | 171 | `#8e7148` 26.9% |
| a4_2001（参考） | 1388 | `#8e7148` 22.8% | 256 | 26.9% |
| a5_2026（参考） | 1718 | `#57564f` 22.8% | 485 | 26.9% |

**口径说明（重要）**：`≥900` 只能按**整窗口**判。世界区（裁掉 HUD 与底栏）里**已交付验收的 A4/A5 也只有 256/485 色**——32px 平铺瓦本来就色数少，把 `≥900` 套在世界区会把 A4/A5 一起判死。所以本表两列都列出来，判定用整窗口。
年代地面确实各不相同（主色证据）：a1 `#6e7a4c` 25.2%、a2 `#68744a`、a3 `#6a6a44`、a4 `#5a6a4a`+`#6e694f`、a5 `#57564f`(柏油)+`#797973`。

### V2 地面/路/田/河必须是 32×32 平铺瓦 —— **PASS**
- 代码事实：`scripts/world_view.gd` 的 `_draw_back` 里五处 `draw_texture_rect(tex, rect, true)`（地面全屏平铺、road rect、田 rect、河 polygon 分段、环道 polygon 分段），无整帧大图。
- 像素证据：截图三条水平线上的 32px 周期命中率 a1 90%/95%/87%、a2 84%/95%/87%、a3 84%/95%/87%、a4 85%/95%/90%、a5 87%/91%/79%。未命中的部分是房屋/井/树/HUD/前景小件压在瓦上，不是地瓦本身不周期。
- 数据证据：我从没给任何 shape 填过整帧色块图；a1–a3 的 ground 各自指向 `ground_a1/a2/a3_tiles.png`（前两次改动的 L8 平铺没被破坏）。

### V3 截图交用户看 —— **见最终回复附图，共 10 张（a1..a5 × space/time）+ 1 张 phasing**，路径 `_mdtest/greybox/`。
**声明：我本人看的是像素统计（颜色数/主色占比/32px 周期命中率），不是肉眼看图——本机没有视觉模型（`read_image` / `modlens_read_image` 都报不支持）。** 画面是否「像 1926/1951/1976 的村子」需要你本人裁定。

### V4 缺材质点名 —— **见 §7-①，美术缺口共 4 条**

---

## 5. 没做到 / 做不到 的项，及原因

1. **路面材质分代（§2 的 a1 土路带车辙 / a2 碎石夯土 / a3 水泥）：数据层做不到。**
   `scripts/asset_draw.gd` 的 `TILE_FILES` 里 a1/a2/a3 的 `road` 都指向同一张 `assets/village/scene/road_tiles_l8.png`（`POLYGON_TILE_KIND` 也只认「河」「路」两种 label）。要让三帧路面不同，必须新增 3 张路面瓦并改 `asset_draw.gd` 的帧→瓦映射——两者都在禁改清单（`scripts/**`、`assets/**`）。**故三帧路面仍是同一张土黄瓦（截图里 `#8e7148` 三帧同占 26.9%）**，请美术补 `road_a1/a2/a3_tiles.png`，再开一个小任务改 `TILE_FILES`。
2. **§2 的「A1 环岛位置是空地/树影」做不到。** polygon 分派只有「河」「路」两种瓦，`label` 留空会退化成 `draw_colored_polygon(color)` 纯色块（违反 C4）。所以我保留三帧环道都为「路」polygon——这也正好保住了 S4/S5 要的几何一致性。
3. **story §4.3「粮油站挖地基挖到老井」失去载体。** §1 要求五帧井同址 `(2048,832)`，而磨坊三帧在 `(1216,512)`，井不可能再压在磨坊地基下。`_mdtest/greybox_check.gd` 里原来那条 `A3_OLD_WELL_UNDER_MILL`（磨坊 lot 必须包含井）已按新事实翻面成 `A3_WELL_NOT_UNDER_MILL`。**这条需要总策划裁定**：是改剧情（比如「挖到的是老井的地下水脉/旧管沟」），还是把井挪回去（那就要破 S2）。
4. **`start_pos` 落在环道上**：`[2048,1864]` 距圆心 200，在 R176–R304 的环道内。这是 A5 现有取值、任务书禁改，我只记录不修改。

---

## 6. 待拍板（3 项）

1. **磨坊/陆家的落位是我定的**（§1 表格只给了沈家、周家）。磨坊 `(1216,512)`（旧 448 会压进引水湾；512 让 `(1400,1120)` 保持可站）、陆家留在 `(2304,768)`（原址不压河/环道/车道，且 `asset_draw_check` 用它采样）。
2. **§2 年代语义整体**：我按「几何完全一致、只让材质分代」施工，但材质分代做不到（§5-1、§5-2）。是接受「三帧路面/环道暂时同材质」，还是另开任务补 3 张路面瓦？
3. **story §4.3 井的剧情冲突**（§5-3）。

---

## 7. 我为什么改了 `_mdtest/greybox_check.gd`（不在禁改清单内，但 S6 要求它全绿）

它把 a1–a3 的房屋坐标、井坐标、门位、撞墙探针**硬编码**在脚本里（`HOUSE_MAP`/`HOUSE_MAP_A2`/`HOUSE_MAP_A3`/`OLD_WELL`）。挪房挪井后不跟着改，S6 必然红。改动清单：

- `HOUSE_MAP`/`_A2`/`_A3` 全部换新 pos/size（磨坊 (1216,512)、沈家 (64,416)、周家 (576,1920)、陆家不动）；
- `OLD_WELL (1360,848)` → `WELL_POS (2048,832)`；
- `A2_OLD_WELL_NO_WELL_SOLID`→`A2_WELL_NO_WELL_SOLID`（期望 `is_free(WELL_POS)`）、`A3_OLD_WELL_FREE`→`A3_WELL_FREE`、`A3_OLD_WELL_UNDER_MILL`→`A3_WELL_NOT_UNDER_MILL`（见 §5-3）；
- `DOOR_PASSABLE` 门位 (1456,784)(336,976)(1872,1456)(2512,1104) → (1456,848)(272,752)(656,2096)(2512,1104)；
- `WALL_STOP_Y` 期望 800~816 → **864~880**（磨坊下移 64，南墙下沿从 800 变 864），实测 880；
- `A1_MILL_INTERIOR_FREE` 探针 (1400,520)→(1400,752)、`A1_MILL_DOOR_FREE`→(1456,848)、`HOTSPOT_A1_MILL_DESK` (1264,544)→(1264,608)；
- 新增 `HOTSPOT_A2_WELL`/`HOTSPOT_A3_WELL`（都在 `WELL_POS`，验证三层文案）；
- **顺手修了一个和本次数据无关的测试 bug**：`load_frames()` 把 `index` 落在 `start_frame`（A5），而「空间移动」「撞墙」两段没切 `tl.index = 0`，所以这两段一直在测 A5（旧跑出 `WALL_STOP_Y=424`、`WALL_BLOCKED=false`，与文档值 816 矛盾）。已在这两段前补 `tl.index = 0`。**用 HEAD 版数据 + 这个补丁复跑，得到 `WALL_STOP_Y=816`（=文档旧期望值）**，证明老断言本身是对的，只是被 `start_frame` 改到 A5 后测错了帧。

---

## 8. 顺手发现、未在本任务范围内处理

- `_ref/art/` 下 A1/A2/A3 的 PNG 正被别人并行修改（工作区 M）——如果那批图是给本次重排配的，位置可能已经和我的新坐标对不上，需要他 rebase。
- `scripts/house_shape.gd` 的 `hotspots()` 用 `pos + (r[0] + r[2]*0.5)*32` 算中心（不是 `r[0] + r[2]/2 - 0.5`），即取 span 的右下角一格；本次水簿热点用的是旧偏移 + 64，与它一致，未改引擎。