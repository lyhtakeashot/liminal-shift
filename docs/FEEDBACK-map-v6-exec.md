# 任务书 L22 · 地图 v6 执行反馈（a4 郑家北移贴近东侧主路）

## ① 改了什么

`data/frames.json` 中 `a4_2001.shapes` 里 `type=="house" && id=="zheng_a4"` 的那一条，`pos` 由 `[3456, 2304]` 改为 `[3456, 1856]`（x 不动，y 北移 448 px = 14 格）。北墙从 y=72 格移到 y=58 格，距路底（54 格）4 格 = 128 px。除此之外 `frames.json` 一字未动（格式漂移检查 `roundtrip==raw : True`，改后 `git diff` 仅 1 行）。

重烘 `godot --headless --path . -s res://tools/bake_world_scene.gd` 后，四个非 a4 场景只有 `unique_id` 噪声差异，已按任务书要求回退至 HEAD，工作区只留 `scenes/world/world_a4_2001.tscn` 一个场景文件改动。该文件的语义差异核对：去掉 `unique_id` 后共 63 个节点变化，其中 33 个是 zheng_a4 相关节点随房子北移 448 px，其余 30 个是下游 furniture/prop 节点的整体 y 平移 `-448.0`（全部同位移，无其他语义差异）。

a4 局部 ASCII 位置图（x 100..140 格，每字符 2 格；y 44..92 格，每行 2 格；`=` 主路带 y50..54，`#` 郑家 lot 19×12）：

```
=== 改前 zheng_a4 pos=(108,72) 格 ===
      x 100..140 格 (每字符 2 格)  y 44..92 格 (每行 2 格)
  92 |                     |
  84 |    ##########       |
  72 |    ##########       |
  58 |                     |
  54 |=====================|
  52 |=====================|
  50 |=====================|
  44 |                     |
=== 改后 zheng_a4 pos=(108,58) 格 ===
  92 |                     |
  84 |                     |
  72 |                     |
  70 |    ##########       |
  58 |    ##########       |
  54 |=====================|
  52 |=====================|
  50 |=====================|
  44 |                     |
```

（完整逐行图见 `lab/_v6_ascii_out.txt`。本机无视觉模型，未看画面，全部结论以数字为准。）

## ② 自检 S1–S6 原样输出

```
=== S1: shapes count five frames ===
  a1_1926   shapes=237
  a2_1951   shapes=239
  a3_1976   shapes=222
  a4_2001   shapes=19
  a5_2026   shapes=19
  expected: a1 237 / a2 239 / a3 222 / a4 19 / a5 19
=== S2: zheng_a4.pos and other houses ===
  market     before=[2144, 320] after=[2144, 320] same=True
  shen_a4    before=[64, 416] after=[64, 416] same=True
  zheng_a4   before=[3456, 2304] after=[3456, 1856] same=False
  zhou_a4    before=[576, 1920] after=[576, 1920] same=True
  zheng_a4 in 格 = [108.0, 58.0], 格 = [3456, 1856]
=== S3: a4 hotspots identical ===
  n=5/5 equal=True
=== S4: other four frames + world + start_pos deep_equal ===
  a1_1926   deep_equal=True
  a2_1951   deep_equal=True
  a3_1976   deep_equal=True
  a5_2026   deep_equal=True
  world deep_equal=True
  start_pos deep_equal=True
  start_frame='a5_2026' -> 'a5_2026'
=== S5: label==山 in five frames ===
  a1_1926   山 count=0
  a2_1951   山 count=0
  a3_1976   山 count=0
  a4_2001   山 count=0
  a5_2026   山 count=0
=== S6: NEW lot 格 x108..127 / y58..70 vs all a4 shapes ===
  相交数 = 0
```

格式漂移检查（`lab/_v6_exec_log.txt`）：

```
=== STEP A: format drift check ===
len(raw)=219998 len(roundtrip)=219998
raw endswith newline=False
roundtrip==raw : True
roundtrip+'\n'==raw : False
before zheng_a4.pos = [3456, 2304]
=== STEP B: after write ===
after zheng_a4.pos = [3456, 1856]
reread == written : True
reread parse ok   : True
```

## ③ 回归五条原样输出 + 没做到的

### 1. `_mdtest/greybox_check.gd`（exit=0，关键行原样）

```
A2_HOTSPOTS=11 (期望 >=10：手写5 + clue家具)
A3_HOTSPOTS=13 (期望 >=10：手写5 + clue家具)
HOTSPOTS=10 (期望 >=9)
HOTSPOTS_OK=true
SPACE_MOVE_DX=40.0 (期望 40)
WALL_STOP_Y=880.0 (磨坊南墙前，期望 864~880)
FRAME[0] a1_1926 year=1926 solids=238 hotspots=10
FRAME[1] a2_1951 year=1951 solids=299 hotspots=11
FRAME[2] a3_1976 year=1976 solids=379 hotspots=13
FRAME[3] a4_2001 year=2001 solids=649 hotspots=12
FRAME[4] a5_2026 year=2026 solids=834 hotspots=8
REACH_MAP={ "standable": 15101, "to_a5": 13607, "blocked_at_step": [145, 155, 793, 401], "band_total": 288, "band_full": 288, "band_ratio": "100%", "ratio": "90%" }
UNEXPLAINED_BLOCKS=0
REACH_OK=true (期望 true：卡点全部可解释)
```

solids 五数 238/299/379/649/834 一位不变；HOTSPOTS 10/11/13/12/8 与任务书一致；`blocked_at_step` 由改前 `[145, 155, 2150, 97]` 变为 `[145, 155, 793, 401]`（房子挪了，绕行路径变，按 §5 说明属预期位移，非回归）。

### 2. `_mdtest/phasing_check.gd`（exit=0）

```
PHASING_CHECK_DONE fails=0 warns=0
```

### 3. `_mdtest/scene_bake_check.gd`（exit=0）

```
SCENE_BAKE_CHECK_DONE fails=0 checks=3044
```

### 4. `_mdtest/sort_check.gd`（exit=0）

```
SORT_CHECK_DONE fails=0
```

### 5. `_mdtest/a4_rebuild_check.gd`（exit=1，已知红，原样输出；未修）

```
FAIL a4_2001 shapes=26（实际 19）
FAIL 山 polygon 7 座＝3 抄 A5 ＋ 4 补山（实际 0）
FAIL cover(A5⊆A4)=100%（实际 67.3%）
FAIL cover(A4⊆A5)=100%（实际 91.3%）
FAIL A4↔A5 双向触发格数 = 0（实际 260 / 1318）
FRAME a4_2001 solids=649 hotspots=12
FRAME a5_2026 solids=834 hotspots=8
A4_REBUILD_CHECK_DONE fails=5
```

AIRWALL 数字（供 lead 重定基线）：

```
AIRWALL a4=2974 cells  a5=4032 cells  cover(A5⊆A4)=67.3%  cover(A4⊆A5)=91.3%  IoU=63.2%  A4独有=260  A5独有=1318
AIRWALL_A4_vs_a1_1926 = A4独有 2454 格 / a1_1926独有 318 格（a1_1926 共 838 格）
AIRWALL_A4_vs_a2_1951 = A4独有 2323 格 / a2_1951独有 318 格（a2_1951 共 969 格）
AIRWALL_A4_vs_a3_1976 = A4独有 2042 格 / a3_1976独有 390 格（a3_1976 共 1322 格）
AIRWALL_A4_vs_a5_2026 = A4独有 260 格 / a5_2026独有 1318 格（a5_2026 共 4032 格）
```

### 没做到的

- 无。S1–S6 全绿；四条应绿回归全绿；`a4_rebuild_check.gd` 是任务书明示的已知红、不许修，原样贴出交 lead 重定基线。
- 重烘时四个非 a4 场景一度产生 `unique_id` 噪声差异，已按任务书要求逐字节回退到 HEAD，最终工作区只改 a4 场景。
- 本机无视觉模型，未做画面复核，所有判断基于数字与 JSON/场景逐字节核对。
