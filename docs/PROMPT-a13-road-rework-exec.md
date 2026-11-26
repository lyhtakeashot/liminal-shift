# 任务书 · A1–A3 土路重做 + A4 左下房屋挪位

> 用户 2026-11-26 17:27 原话：
> 「1. a4 的左下位置为什么有两栋房子？挪移动到右下位置去
> 2. a1,a2 的土路确定不是直接套正弦模型做的吗，这一点也不可能在现实中出现好吧，重做
> 3. 补充 2 的，土路需要有延伸到房屋的趋势」
>
> 执行者：新会话。**你只改 `data/frames.json` 里写明的那几处，别的一律不动。**
> 上一版（commit `30f9b4d`）的土路确实是直接套正弦做的——那是 lead 的锅，不是你的。

---

## §0 边界（先看这段，违反任何一条就作废）

**可以写：**

| 文件 | 允许改什么 |
|---|---|
| `data/frames.json` | ① `a1_1926` / `a2_1951` / `a3_1976` 三帧里 **`label` 为 `路` 的 `rect`（含新增支路）**；② `a4_2001` 里 **`zheng_a4` 这一个 house 的 `pos`** |
| `scenes/world/world_a{1..5}_*.tscn` | **只允许**用 `godot --headless --path . -s res://tools/bake_world_scene.gd` 重新烘出来（产物，不是源） |
| `_mdtest/greybox_check.gd` | 只有当它的硬编码坐标因这次改动失效时才动，且必须在反馈里逐行说明为什么 |
| `docs/FEEDBACK-a13-road-rework-exec.md` | 新建，你的反馈 |

**绝对不许碰：** `scripts/**`、`assets/**`、`_ref/**`（含 `_ref/houses/houses_data.json`）、`a4_2001` 的其它 shape、`a4_2001` 的其它 house、整个 `a5_2026`、`world`、`start_frame`、`start_pos`、`safe_*`、任何 `hotspots`、任何 `label` 为「河」「坝」「岛」的 shape、任何房子的 `pos`（除 §1 指定的那一个）。

**不许：** `git add -A`、`git commit --amend`、`git push`。只精确 `git add` 你改的文件。

**前置：** HEAD ≥ `30f9b4d`。先 `git log --oneline -3` 和 `git status --short` 各跑一次，把结果写进反馈开头。

---

## §1 A4 左下那两栋房子

**实测事实：** `a4_2001` 的四个 house 是
`market (2144,320)` / `shen_a4 (64,416)` / `zhou_a4 (576,1920)` / `zheng_a4 (1152,2272)`。
左下角重叠在一起的是 **周家 `zhou_a4`（576,1920）** 与 **郑家 `zheng_a4`（1152,2272）**。

**关键约束（必须先看懂再动手）：** 周家这块地在别的帧里也是同一块地——
`a1/a2/a3` 的周家都在 **(576,1920)**，`a5_2026` 的**小学**也在 **(576,1920)**。
只在这四帧里挪周家，玩家切换 1976→2001→2026 会看见房子凭空跳走再回来。

**所以默认只挪郑家：**

- 郑家是 2001 才出现的外来户，其它四帧都没有它 ⇒ **挪它零连续成本**。
- 目标区域：**右下**，x 取 3400..4300、y 取 2200..2900。具体位置你定，但要满足：
  1. 与 `zhou_a4` 的距离 ≥ 3 格（96px）；
  2. 不与任何 house lot / 山 polygon / 南片填充 rect 重叠；
  3. 房子北墙不要压到主路（主路在 a4 是 y=1600..1728）；
  4. 不越过 `safe_bottom`（3552）。
- **不要**顺手改 `_ref/houses/houses_data.json`（那里郑家的 lot 是 19×12 格，pos 变了尺寸不变）。

**如果你（或用户）认为周家也必须挪：** 立刻停手，在反馈里写明「周家与 A1–A3、A5 小学同址，挪它需要五帧一起挪并连带改 A5 小学」，等 lead 拍板。**不要自己决定。**

---

## §2 A1/A2 的土路：不许再用正弦

**现状（要修的就是这个）：** `a1/a2` 的主路是 38 块 `rect`，每块 y 由
`48*(1+sin(2πx/1400))` 量化到 32px 得到 ⇒ 等周期、等振幅、每个弯长得一模一样，一眼假。

**要求：**

1. **用控制点 + 插值，不用任何单一周期函数。** 推荐 Catmull-Rom（或单调三次 Hermite）过控制点，再按 32px 采样成 `rect` 块。控制点**至少 7 个**，且每段的长度/方向不许雷同。
2. **每个弯必须有理由**，在反馈里一条条写出来（例：「x≈800 处向南凸，因为要让开沈家院前的场院」「x≈2048 处贴平，因为老槐在 (2048,1664)」）。写不出理由的弯就删掉。
3. **振幅不要恒定**：有的弯只偏 32–64px，有的偏到 128–192px。**A1 比 A2 更野**（1926 的车辙更深、路更窄更乱），A2 收顺一些。
4. **路面宽 64**（`rect` 的 h=64）。量化到 32px 只允许为了瓦片对齐，量化后**相邻块的 y 差不许超过 32px**（超过就是台阶，玩家会看见锯齿）。
5. **硬红线**：老槐 `(2048,1664)`（r=96，A3 最大）周围 `x∈[1888,2208]` 内，路面 `y` 必须 ≥ 1728，也就是树冠可以压进路面 32px，但**路面绝对不许盖住树心**。这条必须写成自检。

**A3 不动**：`a3_1976` 保持现在那一条 `[0,1728,4800,64]` 直路（`BUILD-A1.md:86`「A3 起路取直」是它的辨识特征）。

---

## §3 土路要延伸到房屋（支路）

**每栋有院的房子，从主路引一条支路到它的院门。**

- 支路宽 **32**，同样用 `rect`（`road: true`，`label: "路"`），同样禁止正弦。
- **终点**＝该房 `gate` 格中心的世界坐标 = `(pos.x + gx*32 + 16, pos.y + gy*32 + 16)`，
  其中 `gate` 取 `_ref/houses/houses_data.json`（读，不许改）。实测值：

| 帧 | 房子 | pos | gate(格) | 支路终点(世界) |
|---|---|---|---|---|
| a1/a2/a3 | 磨坊 `mill_aN` | (1216,512) | `[7,10]` | (1456, 848) |
| a1/a2/a3 | 沈家 `shen_aN` | (64,416) | `[6,10]` | (272, 752) |
| a1/a2/a3 | 周家 `zhou_house` 等 | (576,1920) | `[2,5]` | (656, 2096) |
| a1/a2/a3 | 陆家 `lu_house` 等 | (2304,768) | `[6,10]` | (2512, 1104) |

- **支路允许近直角转弯**（村里的路进院就是直着拐进去的），但要满足：
  1. 全程**不与任何 house lot 重叠**（从院门外走，不穿院子）；
  2. 总长 ≤ 直线距离 × 1.4；
  3. 与主路的接口处要**至少一块 rect 完全贴合主路边缘**（不许留缝，也不许伸进主路面超过 32px）。
- **注意周家**：它的 `gate=[2,5]` 在院子的**南沿**，而主路在它北边的 y=1728..1792 ⇒ 支路要沿着房子东侧或西侧绕到南面。**不许改 `houses_data.json` 把 gate 挪到北面。**
- 陆家 `pos.y=768` 在 a1 的河带（y ≤ 416）以南、主路以北，支路从主路向北接。

---

## §4 验收（逐条交数字，不交「看起来对了」）

**A. 数据自检（写成一个脚本，比如 `lab/_a13_road_v3.py`，带 `--write` 开关）**

1. `a4_2001` / `a5_2026` 的 `shapes`（除 §1 指定的 `zheng_a4` pos）与 `world` / `start_*` **逐字节不变**（脚本里做 dict 比较并打印）。
2. 三帧里所有 `label=="路"` 的 rect：`h ∈ {32,64}`；相邻同宽块的 `y` 差 ≤ 32px。
3. 老槐树心不被路面覆盖（见 §2-5）。
4. 四条支路终点与 §3 表格误差 ≤ 32px。
5. 支路与 house lot 零重叠。
6. 主路的极值点：符号变化的局部极大/极小**≥ 3 处**（证明不是单调正弦），且相邻弯的振幅不全相等。

**B. 回归（一条不改地跑，把输出里的关键行贴进反馈）**

```
godot --headless --path . -s res://_mdtest/greybox_check.gd
godot --headless --path . -s res://_mdtest/a4_rebuild_check.gd
godot --headless --path . -s res://_mdtest/phasing_check.gd
godot --headless --path . -s res://tools/bake_world_scene.gd
godot --headless --path . -s res://_mdtest/scene_bake_check.gd
```

当前基线（你改之前应该是这样，改完把新值也报一遍）：
`solids = 238/299/379/812/897`、`hotspots = 10/11/13/12/8`、`REACH_OK=true`、
`UNEXPLAINED_BLOCKS=0`、`WALL_STOP_Y=880.0`、`TIME_FWD_REACHED=[1,2,3,4]`、
`a4_rebuild fails=0`（A4↔A5 = 0/0）、`phasing fails=0 warns=0`、`scene_bake fails=0 checks=3054`。

**预期会变的两项，必须在反馈里解释清楚：**
- 挪郑家 ⇒ `a4_2001` 的 `solids=812` 会变（房子是实体的），`AIRWALL a4` 与 A4↔A5 的 100% 也**可能**破掉（现在那 100% 有一部分是靠 A4 的山挡住的）。破了就把新数字写成新基线，**不要为了让断言变绿去改山**。
- 土路加弯 + 支路 ⇒ `UNEXPLAINED_BLOCKS` 与 `REACH_OK` 可能变。若 `REACH_OK=false`，把「卡点坐标 + 是哪块 shape 挡的」列出来，**不要删支路了事**。

**C. 视觉（这条不能省）**

- `python lab/_map_overview.py` 生成 `lab/maps/a1_1926.png`、`a2_1951.png`、`all_frames_overview.png`
- 真机窗口截图：`godot --path . -s res://_mdtest/greybox_shot.gd`（**不要加 `--headless`**，加了没有像素）
- 把这几张图的路径写进反馈，让用户看。**你和 lead 都看不见图，所以不许写「画面正常」。**

---

## §5 反馈文件

新建 `docs/FEEDBACK-a13-road-rework-exec.md`，必须有三段：

1. **做了什么**：每个弯的理由（§2-2）、支路端点表、郑家新 pos 与选择理由。
2. **证据**：A 段六条自检的实测输出、B 段五行回归的关键行、C 段图片路径。
3. **没做到的**：任何一条没通过或没执行的，老实写。**禁止写「其余正常」这种话。**

---

## §6 环境

- Godot：`D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe`
- Python：`C:\Users\lyh\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe`（有 numpy / Pillow，**没有** scipy）
- 跑 headless 脚本时看到 `Failed to open 'user://logs/...'`、`Failed to read the root certificate store.` 都是沙箱噪音，忽略。
- 看退出码没用，**只看关键字**（`fails=` / `DONE` / `REACH_OK=`）。
- 改 JSON 前先验 round-trip：`json.dumps(data, indent=2, ensure_ascii=False)` 必须与原文件**逐字节相同**，否则停手报告（说明有人手改过）。
- 读 `.tscn` 千万别 `Get-Content`（内含几十 MB 的 base64 瓦片数据，会灌爆上下文）。
- 写含中文的 python 脚本要先落盘成 `.py` 再跑，别用 `python -`（stdin 会按 GBK 解码崩）。