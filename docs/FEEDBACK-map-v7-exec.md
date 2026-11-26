# 反馈：地图 v7（任务书 `docs/PROMPT-map-v7-exec.md`）

- **开工 HEAD**：`0412fbe`（满足「≥ `621f026`」），开工前 `git status --short data/frames.json scripts/asset_draw.gd` 为空。
- **前置**：`json.dumps(obj, ensure_ascii=False, indent=2)` 与原文件逐字节相等（`S7_PRECHECK byte_equal=True raw_len=223853 dump_len=223853`），确认可安全改写。
- **结论**：P1（a4 郑家挪到环岛东侧）与 P2（内岛接地面瓦片）均已落地；S1–S7 全过；六条回归全绿或已知红（a4_rebuild_check）；a4 场景已重烘，其余四帧逐字节回退到 HEAD。

---

## 1. 改了什么

### P1：a4 郑家挪到环岛东侧（`data/frames.json`）

只改 `a4_2001.shapes` 中 `zheng_a4.pos` 的 x：**`3456 → 2432` px（108 → 76 格），y 保持 1856 px（58 格）不变**。改后与其余 a4 形状相交数 = 0。

a4 局部位置图（格；1 格 = 32 px）：

```
  环岛圆心 (64,52)  外沿半径 9.5 格  主路带 y 50..54 格

  y\x  52  56  60  64  68  72  76  80  84  88  92  96 100
  48        .............................................
  50  =====[===== 主路带 y50..54 =====]====================
  52        ....(环岛 R9.5)....
  54  =====[===== 主路带 y50..54 =====]====================
  56        .............................................
  58        ............................[郑家 76..95].....
  60        ............................[      ]..........
  64        ............................[ 19x12]..........
  68        ............................[      ]..........
  70        ............................[______]..........
  72        .............................................

  郑家 lot: x 76..95 / y 58..70 格（pos=(76,58)=(2432,1856)px）
  西墙 x=76 格 vs 环道外沿 x≈73.5 格 ⇒ 水平净距 ≈2.5 格
  （y=58 处环道真实边界 x≈71.4 格 ⇒ 净距 ≈4.6 格）
  北墙 y=58 格 vs 主路底 y=54 格 ⇒ 净距 4 格
```

### P2：内岛接上瓦片（`scripts/asset_draw.gd` + `_mdtest/tile_wire_check.gd` + 重烘场景）

- `scripts/asset_draw.gd:93` 的 `POLYGON_TILE_KIND` 加 `岛 → ground`（注释同步更新，去掉原来「岛缺图」的说明）。内岛现在复用各帧地面瓦片。
- `_mdtest/tile_wire_check.gd:31` 的 `KNOWN_GAP` 由 `["岛", "山"]` 改为 `["山"]`；复核 `:177-200` / `:280-295` 两处依赖分支：`:187` 的 dispatch 分支因 `polygon_tex(fid,"岛") != null` 而提前 `continue`，`:294` 的像素分支改走 `int(pc["n"]) >= 3` 的贴图断言，均不会误判为 fail。
- **`岛` 现在的贴图名**：a4 是 `ground_a4_tiles_l8.png`，a5 是 `ground_a5_tiles_l8.png`（a1–a3 无环岛）。S5 探针实测五帧 `polygon_tex(fid,"岛")` 全部返回 32×32 Texture2D。
- 重烘 `scenes/world/world_a4_2001.tscn`：`Poly_island_5` 节点新增 `texture_repeat = 2`、`texture = ExtResource("5_8jv74")`（=`ground_a4_tiles_l8.png`），郑家各 Sprite 的 x 从 3456 变 2432。`unique_id` 噪声如任务书所述存在，**只提交 a4 场景**；其余四帧已用 `git show HEAD:<file>` 逐字节写回（git status 确认仅 a4 场景为 M）。

---

## 2. 自检 S1–S7（原样输出）

```
=== map v7 self-check S1-S4,S6,S7 ===
--- S1 zheng_a4.pos == (76,58) 格; others unchanged ---
before zheng_a4.pos = [3456, 1856] px = (108.0, 58.0) 格
after  zheng_a4.pos = [2432, 1856] px = (76.0, 58.0) 格
S1 zheng_ok=True
S1 market     before=[2144, 320] after=[2144, 320] same=True
S1 shen_a4    before=[64, 416] after=[64, 416] same=True
S1 zhou_a4    before=[576, 1920] after=[576, 1920] same=True
--- S2 a4_2001.hotspots unchanged (5) ---
S2 hotspots n=5 same=True
--- S3 other four frames + world/start_pos deep-equal ---
S3 frame a1_1926  deep_equal=True
S3 frame a2_1951  deep_equal=True
S3 frame a3_1976  deep_equal=True
S3 frame a5_2026  deep_equal=True
S3 world        deep_equal=True
S3 safe_top     deep_equal=True
S3 safe_bottom  deep_equal=True
S3 start_frame  deep_equal=True
S3 start_pos    deep_equal=True
--- S4 shapes counts 237/239/222/19/19 ---
S4 a1_1926  237 -> 237 unchanged=True
S4 a2_1951  239 -> 239 unchanged=True
S4 a3_1976  222 -> 222 unchanged=True
S4 a4_2001  19 -> 19 unchanged=True
S4 a5_2026  19 -> 19 unchanged=True
--- S6 new zheng_a4 lot vs all a4 shapes intersections ---
S6 i=0 polygon[河]                         hit=False
S6 i=1 rect[坝]                            hit=False
S6 i=2 rect[路]                            hit=False
S6 i=3 rect[路]                            hit=False
S6 i=4 polygon[路]                         hit=False
S6 i=5 polygon[路]                         hit=False
S6 i=6 polygon[路]                         hit=False
S6 i=7 polygon[岛]                         hit=False
S6 i=8 circle[老井 · 沥青补丁]                  hit=False
S6 i=9 circle[老槐]                         hit=False
S6 i=10 rect[]                            hit=False
S6 i=11 rect[路标]                          hit=False
S6 i=12 rect[路标]                          hit=False
S6 i=13 rect[路标]                          hit=False
S6 i=14 rect[路标]                          hit=False
S6 i=15 house[market]                     hit=False
S6 i=16 house[shen_a4]                    hit=False
S6 i=17 house[zhou_a4]                    hit=False
S6 polygon/rect/circle hit_count=0
S6 zheng_a4 pos dist to ring center = 13.42 格
S6 west wall x=2432 px; ring center x=2048; gap=2.5 格 (edge, R=304)
--- S7 json.dumps byte equality ---
S7 byte_equal=True raw_len=223853 dump_len=223853
S7 before_len=223853 only_diff_expected=zheng_a4.x
```

> S6 说明：逐形状用 lot 矩形 `x 76..95 / y 58..70 格` 与 a4 其余 18 个形状做几何相交测试（house 用 `houses_data.json` 的 lot 尺寸 × 32），全部 `hit=False`。自算的「距环心 13.42 格」是按圆心 (2048,1664) 到 pos 中心的欧氏距离，任务书里的「24.6 格」是另一参考点的口径；**验收口径是相交数 = 0**，已满足。

S5（Godot 探针原样结果，写入 `lab/_tmp/map_v7_s5_result.txt`）：

```
S5_PROBE_START
S5 POLYGON_TILE_KIND={ "河": "river", "路": "road", "岛": "ground" }
S5 has_island=true kind=ground
S5 a1_1926 polygon_tex(岛)= size=32x32
S5 a2_1951 polygon_tex(岛)= size=32x32
S5 a3_1976 polygon_tex(岛)= size=32x32
S5 a4_2001 polygon_tex(岛)= size=32x32
S5 a5_2026 polygon_tex(岛)= size=32x32
S5_PROBE_DONE
```

S7 前置（改前先验）：

```
S7_PRECHECK byte_equal=True raw_len=223853 dump_len=223853 keys=['world', 'safe_top', 'safe_bottom', 'start_frame', 'start_pos', 'frames']
```

---

## 3. 回归六条（原样）

### 3.1 `_mdtest/greybox_check.gd` —— 全绿，数字一位不变

```
FRAME[0] a1_1926 year=1926 solids=238 hotspots=10
FRAME[1] a2_1951 year=1951 solids=299 hotspots=11
FRAME[2] a3_1976 year=1976 solids=379 hotspots=13
FRAME[3] a4_2001 year=2001 solids=649 hotspots=12
FRAME[4] a5_2026 year=2026 solids=834 hotspots=8
UNEXPLAINED_BLOCKS=0
REACH_OK=true (期望 true：卡点全部可解释)
WALL_STOP_Y=880.0 (磨坊南墙前，期望 864~880)
SPACE_MOVE_DX=40.0 (期望 40)
```

（`blocked_at_step=[145, 155, 793, 395]` 随房子挪动改变，属非回归。）

### 3.2 `_mdtest/tile_wire_check.gd` —— 全绿，gaps 由 2 降为 0

改前（临时把 `KNOWN_GAP` 复原为 `["岛", "山"]`，窗口模式跑）：

```
INFO 已知缺口 shape = 0 个（岛/山，见反馈文档 §2 缺口表）
GAP  a4_2001 polygon[岛] 32×32 格内颜色数 = 3（缺 32×32 瓦片 ⇒ 纯色降级）格(1984,1504) 采样色=6e694f 数据色=#6b7a4a
GAP  a5_2026 polygon[岛] 无 32×32 瓦片 ⇒ 纯色降级（采样格全被 9:circle/老槐 遮住，按数据色 #6b7a4a 判定）
TILE_WIRE_CHECK_DONE fails=0 gaps=2 checks=39
```

改后（`KNOWN_GAP=["山"]`，窗口模式跑）：

```
PASS 每个 polygon/rect 都说得出铺什么贴图（说不出的 0 条：[]）
INFO 已知缺口 shape = 0 个（岛/山，见反馈文档 §2 缺口表）
PASS a4_2001 polygon[岛] 32×32 格内颜色数 = 3（≥3=贴图）格(1984,1504) 采样色=6e694f 数据色=#6b7a4a
TILE_WIRE_CHECK_DONE fails=0 gaps=0 checks=40
```

### 3.3 `_mdtest/phasing_check.gd`

```
PAIR_0_1_BLOCKED=103
PAIR_1_2_BLOCKED=95
PAIR_2_3_BLOCKED=581
PAIR_3_4_BLOCKED=295
PAIR_A4_A5_NEAR0=true（295 格 ≤ 容差 320）
PHASING_CHECK_DONE fails=0 warns=0
```

### 3.4 `_mdtest/scene_bake_check.gd`

```
TABLE | a4_2001 | 16950 | 324 | 524 | 5 | 364 | 528 | S1-S10 OK
TABLE | a5_2026 | 16950 | 324 | 524 | 5 | 409 | 720 | S1-S10 OK
PIXEL 跳过 S11/S12（headless=dummy 渲染器；用不带 --headless 再跑一次）
SCENE_BAKE_CHECK_DONE fails=0 checks=3044
```

### 3.5 `_mdtest/sort_check.gd`

```
PASS 排序结果按 sort_y 递增
PASS player.z_index = 0（不再靠 z_index 叠最上）
SORT_CHECK_DONE fails=0
```

### 3.6 `_mdtest/a4_rebuild_check.gd` —— 已知红，未修，原样贴

```
FAIL a4_2001 shapes=26（实际 19）
FAIL 山 polygon 7 座＝3 抄 A5 ＋ 4 补山（实际 0）
FAIL cover(A5⊆A4)=100%（实际 70.2%）
FAIL cover(A4⊆A5)=100%（实际 95.2%）
FAIL A4↔A5 双向触发格数 = 0（实际 143 / 1201）
FRAME a4_2001 solids=649 hotspots=12
FRAME a5_2026 solids=834 hotspots=8
A4_REBUILD_CHECK_DONE fails=5
```

### 3.7 重烘输出（`tools/bake_world_scene.gd`）

```
FRAME a4_2001 cells ground=16950 field=324 road=524 | poly=5 sprite=364 nodes=517 | missing=well:a4_2001,tree:a4_2001,prop_rect:路标:a4_2001
BAKE_DONE frames=5 out=res://scenes/world
```

---

## 4. 没做到的

- **`a4_rebuild_check.gd` 仍为已知红（5 fails）**：按任务书 §4「已知红，不许修」原样保留。
- **`scene_bake_check` 的 S11/S12 像素断言未跑**：headless 是 dummy 渲染器，脚本自己打印 `PIXEL 跳过`；任务书 §4 要求的只是 `fails=0`，已满足。若要像素证据需另跑窗口模式（本机无视觉模型，我不验图，只看数字）。
- **任务书给的距离数字与本地自算口径不一致**：任务书 §1 称「距环岛心 24.6 格」，我按圆心 (2048,1664) 到新 pos (2432,1856) 算欧氏距离为 13.42 格；不影响验收口径（相交数 = 0，且 west wall 距环道外沿约 2.5 格 / y=58 处真实边界约 4.6 格）。未自行把 pos 调到更小的值，遵守「不要自己试更小的值」。
- **未提交**：`lab/_v7_*.py`、`lab/_v7_*.gd`、`lab/_tmp/*` 为自检/探针产物，按任务书 §7 的 `git add` 清单不入库。
