# 任务书 · 地图 v8：环岛与内岛按「格」重构

> 派单：lead（2026-11-26 23:40） · 执行：新会话 · 前置 HEAD ≥ `fda791d`
> 上一轮遗留：v7 把内岛的**填充**改成贴图，但**形状**仍是 72 点平滑圆弧 —— 本轮修形状。

---

## §0 白名单（只能碰这些）

**可以写：**

1. `data/frames.json` —— 只允许改 `a4_2001` 与 `a5_2026` 两帧里 **`label == "路"` 的环道 polygon** 和 **`label == "岛"` 的内岛 polygon** 的 `points` 数组。这两条之外的任何一个字节都不许变。
2. `scenes/world/world_a4_2001.tscn`、`scenes/world/world_a5_2026.tscn` —— 只允许由 `tools/bake_world_scene.gd` 重新烘培产生。
3. `lab/_map_grid_roundabout.py` —— 你自己写的生成脚本（新建），必须可复现、带 `--check` 与 `--write`。
4. `docs/FEEDBACK-map-v8-exec.md` —— 结项反馈（新建）。

**绝对不许碰：**

- `scripts/**` —— 引擎侧一行都不用改。`poly_tile_rects()` 已经能填任意多边形，阶梯轮廓天然支持。
- `assets/**`、`_ref/**`、`美术资产/**` —— 本轮是纯几何。
- `a1_1926` / `a2_1951` / `a3_1976` 三帧（**它们没有环岛**，是 2001 年才修的）、`world`、`start_frame`、`start_pos`、`safe_*`、所有 `hotspots`。
- `_mdtest/**` 里的检查脚本 —— 不许为了让它们变绿而改断言。数字变了就在反馈里报，由 lead 重定基线。

**独占**：本轮独占 `data/frames.json`。开工前先跑 `git status --short data/frames.json`，**必须为空**；不空就停下问 lead。

---

## §1 单位：一切按「格」，1 格 = 32px

- 环心 = `(64, 52) 格` = `(2048, 1664) px`。五个年代同一坐标，**本轮不动**。
- **外半径 9 格 = 288px**（现状 304px = 9.5 格，缩 0.5 格）。
- **内半径 5 格 = 160px**（现状 176px = 5.5 格，缩 0.5 格）。
- **环宽 = 外 − 内 = 4 格 = 128px**（与现状一致，不许变）。
- 所有输出坐标必须是 32 的整数倍；写进反馈的数字**一律先写格再写 px**。

---

## §2 要改成什么样

把「一个平滑圆」换成「**一个用 32px 方格拼出来的圆**」。

判定一个格属于哪个形状，用**格心**：

- 格 `(gx, gy)` 的格心 = `((gx+0.5)*32, (gy+0.5)*32)`；
- 到环心距离 `d = |格心 − (2048,1664)|`；
- `d ≤ 288` → 内岛（`label:"岛"`）；
- `160 < d ≤ 288` → 环道（`label:"路"`）。

> 注意：内岛是**实心格圆**，环道是**环带**。两者都必须是**闭合多边形**，顶点按格点边界逐个走出来（就是常见的「像素圆」算法：中点圆/Bresenham 变体，或直接沿格边界走一圈），不要用采样圆弧再取整 —— 那样会得到重复点、自交或漏格。

**输出要求：**

- `points` 里每个点都满足 `x % 32 == 0 && y % 32 == 0`；
- 多边形必须**闭合**（首尾同点或隐式闭合都可，与现有数据口径一致）；
- 不许有自交、不许有重复相邻点；
- 环道与内岛**不能互换**，不能把内岛做成环带的洞（引擎按 `格心在多边形内` 填，洞不会被识别）。

---

## §3 施工

1. **备份现状基线**（改前先跑一遍）：
   ```
   cd <项目根>
   git status --short data/frames.json          # 必须为空
   ```
2. 写 `lab/_map_grid_roundabout.py`：
   - `--check`：只算不写，打印每个形状的点数、bbox、是否全在格点上、围出的格数与「格心判定」重算的格数是否一致（**必须完全一致**，否则算法错）。
   - `--write`：改两个文件里的四条 polygon 的 `points`，其余字节不动。
   - **JSON 往返必须逐字节相同**：用 `json.loads` → `json.dumps(indent=2, ensure_ascii=False)` 读回原文件对比。不一致就别写盘（现有 `data/frames.json` 就是这个格式，v5/v6/v7 都验过）。
   - 改前打印「最长公共前后缀行号」，改后打印「只有哪几行变了」（`data/frames.json` 约 5k 行，四条 polygon 各占一行）。
3. 重烘场景：
   ```
   Start-Process -FilePath "<godot>" -ArgumentList '--headless','--path','.', '-s','res://tools/bake_world_scene.gd' -Wait
   ```
   > 本机 `& godot ...` 抓 stdout 会 Access denied，必须用 `Start-Process -RedirectStandardOutput` 或 `-Wait` 后读文件。

---

## §4 自检（S1–S9，逐条打印 PASS/FAIL）

| 编号 | 断言 |
|---|---|
| **S1** | 四条 polygon（a4/a5 × 环道/内岛）的点**全部**落在 32px 格点上 |
| **S2** | 环道 bbox = `(1760,1376)..(2336,1952)` px = `(55,43)..(73,61)` 格（18×18 格） |
| **S3** | 内岛 bbox = `(1888,1504)..(2208,1824)` px = `(59,47)..(69,57)` 格（10×10 格） |
| **S4** | 环道围出的格数 = 内岛外那圈格数；用「格心判定」与「多边形填充」两种算法重算，**结果必须相等** |
| **S5** | 起点 `start_pos = [2048,1864]` 的格心距环心 6.25 格 ⇒ 落在**环道**里（`5 < d ≤ 9`），仍是可走路面 |
| **S6** | `a1_1926`/`a2_1951`/`a3_1976`/`world`/`start_frame`/`start_pos`/`safe_*` 与改前**深比较相同**；五帧 `hotspots` 逐条相同（应为 10/11/13/12/8） |
| **S7** | 重烘后 `world_a4_2001.tscn`/`world_a5_2026.tscn` 里环道与内岛对应 Polygon2D 的点**全部**是 32 的倍数（从 .tscn 抽读，**不要 `Get-Content` 整个文件**，里面几十 MB base64） |
| **S8** | `a4_2001`/`a5_2026` 里 `label == "山"` 仍为 **0** 条 |
| **S9** | JSON 往返字节一致；`git diff --stat data/frames.json` 只有 1 个文件、只应出现 4 行改动 |

---

## §5 回归（必须全跑，贴原始关键字）

```
_mdtest/greybox_check.gd      → REACH_OK=true / UNEXPLAINED_BLOCKS=0 / solids=? / hotspots=10/11/13/12/8
_mdtest/scene_bake_check.gd   → fails=0
_mdtest/phasing_check.gd      → fails=0 warns=0 / PAIR_A4_A5_NEAR0=true
_mdtest/tile_wire_check.gd    → 窗口模式（不带 --headless）：fails=0 gaps=0 checks=40
_mdtest/sort_check.gd         → fails=0
_mdtest/interior_check.gd     → ALL PASS
```

**预警**：环岛缩小 0.5 格后，`blocked_at_step`、`to_a5`、`solids` 里的某些**可能变**，`greybox_check` 的 `SPACE_MOVE_DX` 也可能变。这些数字**变了不等于失败**，但必须在反馈里逐个列出「改前 → 改后」。若 `REACH_OK=false` 或 `UNEXPLAINED_BLOCKS>0`，**立刻停手**报 lead —— 那说明环道和南北车道之间断了。

**不许**为了让检查变绿去改 `_mdtest/**` 的任何断言。

---

## §6 反馈（`docs/FEEDBACK-map-v8-exec.md`）

三段，缺一段算没交：

1. **做了什么**：四条 polygon 的新点数、bbox（格+px）、围出格数；脚本路径；重烘命令。
2. **证据**：S1–S9 逐条结果 + §5 六套回归的原始输出行 + 「改前 → 改后」数字对照表。
3. **没做到的 / 存疑**：任何偏离本任务书的地方，必须写清偏离了什么、为什么、建议怎么处理。**你判断不了的交给 lead，不要自己扩大范围。**

---

## §7 环境（照抄，别自己发明）

- Godot：`D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe`
- Python：`C:\Users\lyh\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe`（含 numpy/Pillow）
- 跑检查：`--headless --path . -s res://_mdtest/<name>.gd`，**看关键字不看退出码**（剧本里有 `quit(1)` 的守卫，退出码不可信）
- `tile_wire_check` 要拿像素必须**去掉 `--headless`**
- `git add` 只加白名单里的文件，**绝不 `git add -A`**；**不许 push**（推送由 lead 定时安排）
- 中文提交信息：先 `write` 成 `lab/_msg_xxx.txt`，再 `git commit -F`