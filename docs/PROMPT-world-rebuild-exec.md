# 新会话提示词：世界重构线 —— 主路南移 + 世界放大 + A1–A3 重画（地基级）

> 整段复制给新会话作为第一条消息。这是**地基级重构**：必须先于「场景搭建2 落地 A4 帧」完成。
> 用户已在 2026-11-22 拍板选「世界重构线」，硬约束是「绝对不能压路」。

你是《shift》Godot 4.7 像素游戏的 **世界重构执行人**。

## 0. 开工前（必做，别跳过）

```
项目：D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift
Godot：D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe
```

- 所有 pwsh 调用带 `sandbox_permissions: "danger-full-access"`。
- `git log --oneline -5` 确认 HEAD ≥ `2382ceb`；`git status --short` 会看到一大堆未提交文件（用户删的 17 张旧图 D 状态、lab/ 一堆未跟踪产物、场景设计4 在写 toyshop/school）。**这些全部只读、绝不写、绝不 add**。
- 🔴 **先确认 `data/frames.json` 的 `a4_2001` 帧仍是空**（`shapes=[] / hotspots=[]`）。若场景搭建2 已抢先落盘 A4，你要**基于它的版本**改，保留 a4 帧对象一个字节不动。A4 摆位依赖本线的新路基准，所以它本应等你——发现它已动就停下来告诉总策划，不要覆盖。
- 权威源＝`_ref/houses/houses_data.json`（18 栋，lot 是闭区间 `[x0,y0,x1,y1]`，`lot_rect()` 才 +1）。**房屋尺寸一律以 JSON 的 lot/wings 为准，不看 note**（note 与 lot 常年不符）。

## 1. 为什么要重构（读懂目的，别机械照做）

A4 四栋房屋里 `shen_a4` 的 lot 是 `[0,0,35,35]` = **36×36 格 = 1152×1152 px**（TILE=32）。当前主路在 y=1152、河最深下缘 y≈416，「河以南 + 路以北」的带最窄只有 **904 px**（实测 x=0~200 处 1152−248=904），**塞不下 1152 px 的沈家**。已穷举 1365 个摆位：压路前提下最小仍新增 unexplained=27。用户明确否决「压路」和「压扁沈家」，选择**把路南移 + 世界放大**。

目标：主路南移后，「河下缘→路北缘」带宽 > 1152 px，沈家 36×36 原尺寸完整放进 A4，四栋房互不重叠、不压路、不压河。

## 2. 硬约束（违反任何一条即返工）

1. 🔴 **绝对不能压路**——这是现实逻辑红线（这个时代不会出现房子压在路上的现象），也是用户原话「压路这点是一定不能动的」。
2. **沈家 36×36 完全不动**，不许靠缩小格数/压扁房屋换空间。
3. **A1→A2→A3 的「弯→弯→直」叙事顺序保持**：A1/A2 是弯路（22 段 `rect road:true`），A3 是 1976 年取直（`rect road:true` 的一字路）。只整体南移，不改弯/直性质与先后。
4. **内外 1:1、碰撞纯 AABB、高度不进逐帧数据**——沿用既有引擎约定，不推翻已验收的 y-sort / 不画屋顶成果。
5. **A4/A5 帧保持空**（`a4_2001` / `a5_2026` 不碰，留给场景搭建2 / 后续）。
6. 不碰 `scripts/*.gd` 的绘制逻辑（`world_view.gd` 等视觉/消费线成果只读）——本线只改**测试断言**与数据/生成器/scene 美术。
7. `house_shape.gd:353-381` 的 `CLUE_TEXTS` 只到 A3、A4 七件证物文案退化的问题，**另派装饰线**，本线不碰。

## 3. 新基准参数（建议值，开工先按此验算，不成立再按规则微调）

| 参数 | 旧值 | 建议新值 | 出处 |
|---|---|---|---|
| 世界 `world.height` | 1800 | **2400**（宽 3200 不变） | `data/frames.json:2-4`、`_design_v5.py:36` |
| 主路中线 `ROAD_Y` | 1152 px（36 格） | **1600 px（50 格）** | `_design_v5.py:259`、`greybox_check.gd:283` |
| `start_pos` | `[1024,1168]` | **`[1024,1616]`**（新路中央） | `frames.json:8-11`、`_land_v5.py:252` |
| `safe_bottom` | 668 | 随世界放大重设（格数 37→约 70） | `frames.json:7`、`_land_v5.py:249` |

**验算规则（必须实测，不要盲信建议值）**：
- 沈家顶边贴河下缘（y≈448）时底边 = 448+1152 = 1600；路北缘必须 > 底边并留 ≥2 格（64px）间隔。若 1600 的路紧贴沈家，就把 `ROAD_Y` 再南移到 **52 格（1664 px）**，相应世界 H 可保持 2400。
- 路南空间 = H − ROAD_Y。取 H=2400、ROAD_Y=1600 → 路南 800 px，足以放周家（原 [1792,1280] 需同步南移到路南，如 y≈1696）且留出可站起点。
- 用真实 greybox 的 `standable` / `BFS` / `UNEXPLAINED_BLOCKS` 判定，不要只靠算术。场景搭建2 的 Python 复刻（`C:\Users\lyh\AppData\Local\Temp\a4_write.py`）可作交叉验证。

## 4. 独占写入 vs 只读（严格隔离）

**本线可写**：
- `data/frames.json`（`world` / `safe_top` / `safe_bottom` / `start_pos` + `a1_1926`/`a2_1951`/`a3_1976` 三帧；**a4/a5 两帧只读**）
- `_ref/houses/_design_v5.py`、`_ref/houses/_land_v5.py`
- `_mdtest/greybox_check.gd`、`_mdtest/camera_check.gd`
- `assets/village/scene/road_curved_tiles.png`、`road_straight_a3.png`（及对应 `.import`）
- 若确需改生成器：`_ref/art/gen/_gen_scene.py`

**只读禁写**：`scripts/*.gd`（视觉/消费线成果）、`_ref/houses/houses_data.json`（场景设计4 在写 toyshop/school）、`docs/house-spec.md`、`assets/village/houses/*`、`美术资产/*`、`houses_data.json` 的 A4/A5 栋。

## 5. 分步执行

### 步骤 1 — 数据源改基准，重跑 frames.json
- `_design_v5.py:36` `W, H = 3200, 1800` → `3200, 2400`；`:259` `ROAD_Y = 36` → `50`（格）；`:261-262` `sway()` 保持不变（A1/A2 弯曲形状不换）。
- 注意 `_design_v5.py` 三个 16/格单位语义：`sigma`/`TREE_DIAMETER`/`MILL_X0,X1` 是格单位，**不随 TILE 变**；`W,H` 与 `ROAD_Y` 才改。
- `_land_v5.py:248-252` `safe_bottom` / `start_pos` 按新路重设（`:252` 现在是 `px(36)+TILE//2`，36 是 ROAD_Y 格，改为新 ROAD_Y 格）。`:127-134` 路走 `cells_to_rects(ROAD_SETS[fid])` 逐格 `rect + road:true`，自动跟随 ROADS。
- 重跑生成器出 `data/frames.json`，确认 a1/a2/a3 三帧的路面 rect 整体南移、弯/直性质不变，a4/a5 仍空。

### 步骤 2 — A1–A3 三帧路重画（scene 美术）
- 主路图只有两张：`road_curved_tiles.png`（A1/A2 弯，3200×256）、`road_straight_a3.png`（A3 直，3200×96）。**只重画这两张**。
- `_gen_scene.py:198-238 gen_road()` 从 frames.json 的 `road:true` rect 动态算 bbox（`:202-207`），直接重跑即自动按新路位置/尺寸出图，**不要手画**。
- 详见 §6（scene 美术正确范围，别全重画）。

### 步骤 3 — 引擎断言同步（只改测试，不改渲染）
- `greybox_check.gd:57` `WORLD_OK` 期望 `3200x1800` → `3200x2400`（`:55-56` 打印串同步）。
- `:283` `const ROAD_Y := 1152` → `1600`。
- `:290-291` / `:371-372` 扫描 `range(240,1760,32)` / `range(40,3160,32)`：`y` 上界 1760 要覆盖新路（1600）+ 路南房（周家约 1696~2016），改为 `range(240, 2400, 32)`；x 上界 3160 不变。
- `camera_check.gd:44-46` 写死 `Vector2(3200,1800)` 与 clamp `(1920,1080)` → 宽不变、高 2400，clamp 上限 = `(3200−1280, 2400−720)` = `(1920, 1680)`。`:51` 断言同步。
- ⚠️ `scripts/timeline.gd`（`:23/:44/:56-57`）、`scripts/camera_rig.gd`（`:19/:27/:57`）、`scripts/main.gd`（`:54-60/:110-115/:230`）、`world_view.gd:255` 河贴图 `Vector2(3200,416)` —— **都从 frames.json / 固定河图读，河与视口没变就不用改**。不要顺手改渲染代码。

### 步骤 4 — 收编「解释集」修复（原方案 A，本线统一做，场景搭建2 不再单独改）
`greybox_check.gd:326` 与 `:337` 的解释集硬编码 `for fi in [1, 2]`（只 A2/A3），但 `:297` / `:377` 扫描 `range(1, tl.frames.size())` 含 A4 → A4 四栋房不管放哪都会被判 `UNEXPLAINED`。文件自己的注释 `:320` 已写明「历史帧的空地变成建筑，顶住是设计」。
- 改成 `for fi in range(1, tl.frames.size())`（一行）。当下帧 A4/A5 空，零副作用；将来 A4 落地不再误判。
- 🔴 这一条此前口头授权给场景搭建2 单独改，**现由本线统一执行，避免两条线同写 `greybox_check.gd`**。请总策划转告场景搭建2 撤销单独改动。

### 步骤 5 — 六套回归（看关键字，不看退出码）
依次跑（沙箱里 Godot 会报 `Failed to read the root certificate store.` + `[exit code:1]`，这是基线噪声，不代表失败）：
- `_mdtest/greybox_check.gd`：看 `WORLD_OK=true` / `START_OK=true` / `HOTSPOTS_OK=true` / `WALL_BLOCKED=true` / `REACH_OK=true` / `UNEXPLAINED_BLOCKS=0`。
- `_mdtest/camera_check.gd`、`_mdtest/display_check.gd`、`_mdtest/hud_layout_check.gd`、`_mdtest/asset_draw_check.gd`、`_mdtest/sort_check.gd`：`fails=0` / 参数正确。
- 运行方式：headless 不能管道捕获 stdout，用 `cmd /c "godot --headless --path . --script ... > out.txt 2>&1"` 再读文件。
- 🔴 注意 `asset_draw_check.gd` 的 A1–A3 家具/截图断言里若写死了世界坐标 bbox，需按新 frames.json 重锚（贴图消费点本身不改）。

## 6. scene 美术正确范围（重要纠正，别全重画）

实测 `assets/village/scene/` 有 23 张 PNG，但**几何随 frames.json 变化的只有主路**：
- **要重画**：`road_curved_tiles.png`、`road_straight_a3.png`（`gen_road()` 动态 bbox，重跑即可）。
- **不用动**：`river_a1/a2/a3.png`（河 polygon 坐标不变，贴图按 `world_view.gd:255` 的 `Vector2(3200,416)` 贴）、`dam.png`、`stele.png`、`field_*`（田 rect 坐标不变）、`well_old_*`、`tree_a1/a2/a3`、`ground_*_tiles`、`tree_old_4x5`。这些的 bbox 也从 frames.json 动态算（`world_view.gd:268-295 _scene_bboxes()`），只要几何没变就自动对齐。
- 重跑 `_gen_scene.py` 时它会重出全部 15 个唯一文件；用 `git diff` 核对，**只有两张路图内容变化**才对，其余若变化说明几何被误改，停下来查。

## 7. 界碑/超市冲突自动消解（不用单独处理）

原反馈里「超市压井(1360,848)+老槐(1296,976) → 必压界碑(1856,960)」是**在旧路 y=1152 的拥挤带里**才无解。路南移后带变宽、超市有更多摆位空间，界碑可保住。若最终摆位仍与界碑重叠，按用户拍板：**界碑可被圈进超市范围，但把它的 hotspot 移到玩家可达处**（叙事上「碑在院内、玩家在门口可见」说得通）；**绝不删除界碑热点**。

## 8. A4 帧冻结与串行门

- 你**不写** `a4_2001` / `a5_2026` 两帧。世界重构完成并 commit 后，由总策划通知场景搭建2 基于新基准（路 y、带宽、起点）重新优化四栋摆位并落盘 A4。
- 提交前再次确认 a4/a5 两帧对象是空且未被你改动（`git diff -- data/frames.json` 只看 world/safe/start + 三帧）。

## 9. 提交纪律

- 只 `git add` 本线白名单文件（§4），**绝对不要 `git add -A`**——工作区里另有用户删的 17 张旧图 D 状态、lab/ 未跟踪产物、场景设计4 的 toyshop/school 改动。
- commit 信息写清「feat(world): 主路南移+世界放大+A1-A3重画（地基级重构）」。

## 10. 交付前输出（按此格式回总策划）

1. **新基准实测表**：世界尺寸 / ROAD_Y / 带宽（河下缘→路北缘）/ 沈家摆放 y / 起点 / 路南剩余空间，每项给出实测值（不是建议值）。
2. **弯→直叙事核对**：A1/A2 弯路 rect 段数、A3 直路 rect，确认南移后性质不变。
3. **改动文件清单**：精确到路径，标注哪些是 git diff 确认有变化的。
4. **六套回归结果**：每套的关键字行。
5. **scene 美术核对**：确认只有两张路图变化。
6. **解锁的依赖**：明确告知「A4 帧可由场景搭建2 基于新基准落地了」。
7. 结尾最多提 **3 个**真正需要本人拍板的问题（若参数验算后必须偏离建议值，在这里说清）。
