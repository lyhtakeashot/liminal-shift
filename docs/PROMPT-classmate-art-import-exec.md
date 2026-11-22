# 新会话提示词：美术同学资产导入适配线（真实手绘图 → 游戏可用资产）

> 整段复制给新会话作为第一条消息。本线把美术同学的新图**盘点、映射、切图、适配**到游戏资产规格，先出对照预览，**不擅自覆盖已交付的 AI 程序化图**。

你是《shift》Godot 4.7 像素游戏的**美术资产导入适配人**。

美术同学带来了一批新图，放在 `D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift\美术资产\`（**项目内、中文目录**）。用户明确：「同学的图都是按照最小量化单位 32px 画的」「新的文件更完整一些，需要重新绑定」。

## 0. 开工前（必做）

```
项目：D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift
Godot：D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe
```

- 所有 pwsh 调用带 `sandbox_permissions: "danger-full-access"`。中文路径一律用 `-LiteralPath` 或 `git -c core.quotePath=false`；**不要用 PowerShell 的 `>` 重定向导出二进制**（会把 PNG 写坏），需要导出二进制用 `cmd /c "... > file"`。
- `git log --oneline -3` 确认 HEAD ≥ `98a9242`。
- `git status --short` 核对其他线正在写的文件（见 §2 边界），**一律只读、绝不写、绝不 add**。
- 先读 `docs/DECIDE-stardew-visual.md` 的 **D6**（美术规格冻结）、`docs/HANDOFF-ART-A1A3.md`、`_ref/art/_assets_a1a3/_a1a3_assets.json`（manifest）。

## 1. 两条资产的区别（别搞混）

- **`assets/village/`**：AI 程序化出图，已交付并 commit `c033c34`（23 shell + 84 props + 20 scene）。这是游戏**当前实际加载**的图。
- **`美术资产/`**：美术同学的新图，74 张 PNG，**尚未被游戏引用**。这是本线要导入的对象。

不要拿同学的图去比对 AI 图的"画得像不像"——风格本来不同。本线目标是**把同学的图变成能加载、尺寸对、命名对的游戏资产**，由用户最后拍板是否替换。

## 2. 硬约束与边界

### 2.1 你独占的写入范围（只有这些）

- 新建文档 `docs/ART-MAPPING-classmate.md`（映射表，本线核心产出）。
- `assets/village/_classmate/` 下的分档暂存目录（见 §4）——**新建子目录，绝不改动现有文件**。
- `lab/` 下的对照预览图与临时脚本（不纳入提交）。

### 2.2 绝对只读（其他线在写 / 已交付）

- `scripts/*.gd`（视觉机制线独占：`world_view.gd` / `player.gd` / `house_shape.gd` / `main.gd`）。
- `_ref/houses/houses_data.json`、`_ref/houses/_redo_*.py`、`_ref/art/A5_2026/`（场景设计4 独占）。
- `data/frames.json`（场景搭建2 独占，正在填 `a4_2001` 帧）。
- `assets/village/houses/<族>/`、`assets/village/props/<id>.png`、`assets/village/scene/*.png`（AI 图，**已交付，不覆盖**）。
- `美术资产/` 源目录（同学的原图，只读，不改名不删除）。

### 2.3 引擎现状（影响你对"看效果"的承诺）

- `world_view.gd:366` 只真实绘制 **roof**；`:239` 的 base 只当"有没有图"的开关，图本身不贴。
- `scripts/` 全目录对 props / scene（河/路/田/井/树）**零消费点**。
- `player.gd` 是纯代码画圆（`draw_self()`），主角贴图也没有消费点。
- ⇒ 即使你完美导入，游戏里也**只能看到 roof 变化**；家具/场景/主角要看到，必须等视觉机制线补消费点。**不要把"导入完成"说成"进游戏能看到"**。

## 3. 同学资产实测清单（74 张，按 32px 单位画）

| 目录 | 数量 | 代表文件 | 尺寸特征 |
|---|---|---|---|
| `家具/` | 55 | `Interiors 0..17_768x768_TILESETS_*.png`、`1_Generic_32x32.png`(512×1760)、`Sprite-长桌1.png`(64×32)、`Sprite-床1.png`(32×64)、`家具.png`(256×256) | 图集 + 单件混合，单件都是 32 的整数倍 |
| `房屋/` | 13 | `GK_B_CC_1.png`/`GK_D_CC_1.png`(768×768)、`tileB_farmA/B`(512×512)、`TopDownHouse_FurnitureState2.png`(208×288)、`地板.png`/`墙面.png`/`屋檐1~3.png`/`地毯.png` | tileset + 组件，需拼装 |
| `地皮/` | 3 | `GK_A2_CCautotile_1.png`(768×576)、`GK_A5_CCfloors_1.png`(384×768)、`GK_C_CC_1.png`(511×511) | tileset |
| `树/` | 2 | `tree.png`(96×128)、`Redtree8.png`(64×64) | 单件 |
| `主角/` | 1 | `Sprite-主角-Sheet.png`(1152×32 = 36 帧横排) | 序列帧 |

## 4. 分档策略（本线的方法）

### A 档：单件家具（约 22 张）——优先做，直接映射

`家具/` 下 `Sprite-*.png` 单件，尺寸是 32 的倍数。建立到 manifest `props` 的映射，例：

| 同学文件 | 尺寸 | manifest id（候选，需你逐项核实） |
|---|---|---|
| `Sprite-水缸1.png` | 32×32 | `shuigang_1x1` |
| `Sprite-柴火灶.png` | 32×32 | `chaihuozao_1x1` |
| `Sprite-柴堆.png` | 32×32 | `chaidui_1x1` |
| `Sprite-茅坑.png` | 32×32 | `maokeng_1x1` |
| `Sprite-床1/2/3.png` | 32×64 | `danrenchuang_1x2` |
| `Sprite-大床1/2.png` | 64×64 | `shuangrenchuang_2x2` |
| `Sprite-长桌1.png` | 64×32 | `changdeng_2x1` / `shuzhuo_2x1` 类 |
| `Sprite-书桌1.png` | 32×32 | `shuzhuo_1x1` |
| `Sprite-箱子1/2/3.png` | 32×32 | `muxiang_1x1` / `jiu_muxiang_1x1` |
| `Sprite-柜子1.png` | 32×64 | `yigui_1x2` / `gui_1x2` |
| `Sprite-短椅1/2.png`、`Sprite-短桌1~4.png` | 32×32 | `yi_1x1` / `deng_1x1` 类 |

**适配规则**：manifest `props[].px` 是**占地**尺寸（如 `deng_1x1` = 32×32），按 D6 交付画布 = 占地 + 32（多出的一格在**顶部**做立面，底部对齐）。即 1×1 家具交付 **32×64**、1×2 交付 **32×96**、2×1 交付 **64×64**。用透明像素补顶部一格，把原图贴底部。

### B 档：图集/家具表（约 30 张）——切图后映射

`Interiors 0..17`（768×768 = 24×24 格）、`1_Generic_32x32.png` 等大表是**切图源**。按 32px 网格切片，靠目视/位置表识别每个 32×32 单元是什么家具，再按 A 档规则映射。**识别不出来的单元宁可留空并列入"未映射清单"，不要猜。**

### C 档：房屋/地皮/树/主角（约 22 张）——只出方案，不落盘

同学素材是 tileset/组件（如 `屋檐1.png` 320×144、`墙面.png` 192×192），要拼成 D6 规格的 `base`/`roof` 整栋图（如 640×448）工作量很大，且风格要跟游戏对齐。**本档只做**：在映射文档里写清"哪张图能提供屋顶/墙面/地面材质、如何拼、缺什么"，出一张对照草图，**不写入 `assets/village/`**。主角序列帧同理（游戏端还没有贴图消费点），只登记不导入。

## 5. 执行步骤

1. **盘点**：逐张量尺寸（PNG 头读宽高即可，别用会坏图的重定向），按 §4 三档归类，写进 `docs/ART-MAPPING-classmate.md`。
2. **映射表**：每行 = `源文件 | 像素尺寸 | 档位 | 目标 manifest id | 目标路径 | 置信度(高/中/低) | 备注`。低置信度单独列出。
3. **A 档落地**：对高置信度的单件，用 Python（`python` 在 `D:\Hermes\hermes-agent\venv\Scripts\python.exe`，Pillow 可用）生成 A 档适配图，落到 `assets/village/_classmate/props/<id>.png`。**不覆盖** `assets/village/props/<id>.png`。
4. **B 档落地**：切图后同样落到 `_classmate/props/`，并保留一张"切片编号 → 内容"对照表。
5. **Godot 导入**：`godot --headless --import --path <project>`，确认 exit=0、无 ERROR、新 PNG 都有 `.import`。
6. **对照预览**：用 Pillow 把同学图与对应 AI 图并排拼成 `lab/_classmate_compare_a.png` / `_b.png`，A/B 档各一张，标上 id 和尺寸。
7. **present** 两张对照图给本人，并给出明确的"替换建议清单"（哪些建议替换、哪些建议保留 AI 图）。**替换动作等本人拍板，本线不自行覆盖。**

## 6. 验收标准（自检）

- 映射表覆盖 74 张图，一张不漏；未映射的进"未映射清单"并给理由。
- A/B 档每张交付图尺寸 = manifest 的 `px` 宽 × (`px` 高 + 32)，透明补在顶部，底边对齐。
- Godot 导入无报错；`_classmate/` 下每张 PNG 都有 `.import`。
- 对照图能一眼看出哪个是同学图、哪个是 AI 图、id 是什么。
- `git status` 确认：本线只新增了 §2.1 范围内的文件，其他线文件未被触碰。

## 7. 输出要求

结束时给本人一份短报告：① 三档各多少张、映射成功多少、未映射多少；② 建议替换清单与理由；③ 引擎消费点缺口提醒（家具/场景/主角现在看不到，需视觉线补）；④ 最多 3 个需要本人拍板的问题（例如：房屋图要不要按 C 档拼装、主角序列帧要不要接、是否同意用同学图整体替换 AI 图）。

## 8. 纪律

- 本线只做资产适配，**不写 GDScript、不改 manifest、不改 houses_data.json / frames.json、不回写既有文档**。
- 不 commit（由项目总策划统一提交）；只把产出文件留在磁盘上并报告路径。
- 遇到"这张图对不上任何 manifest id"时，**列入清单并继续**，不要停下来反复问。
