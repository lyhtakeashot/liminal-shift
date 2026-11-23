# 新会话提示词：渲染修正执行人 —— 老槐遮井（A4/A5 井被树冠盖住）

> 本线代号 **L2**。上一版 `docs/PROMPT-stardew-engine-exec.md` 是历史线，不适用。
> 你只改**一个文件**：`scripts/world_view.gd`。

---

## §0 开工前（照做，别跳）

| 项 | 值 |
|---|---|
| 仓库根 | `D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift` |
| Godot | `D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe` |
| HEAD 要求 | ≥ `7c93898`（`git log -1` 确认）；若更低先 `git status` 看现场再决定要不要 pull |
| 你能改的文件 | **只有 `scripts/world_view.gd`** |
| 你不能碰 | `data/frames.json`、`_ref/houses/houses_data.json`、`scripts/house_shape.gd`、`scripts/main.gd`、`scripts/evidence_*.gd`、`assets/**`、`_ref/art/**`、`_mdtest/**`（测试文件也不要改，理由见 §5） |
| pwsh | 本机 `pwsh` 调用要带 `sandbox_permissions: "danger-full-access"`（工作区缺 ACL「更改权限」，不带会报 `windows-acl workspace grant failed: Win32Error 5`） |

### §0.1 跑回归的正确姿势（照抄，别自己发明）

```powershell
& "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe" --headless --path . -s res://_mdtest/sort_check.gd 2>&1 | Select-Object -Last 45
```

- ❌ `cmd /c "D:\steam\...\godot..."` → 路径含空格会被截断，报 `'D:\steam\steamapps\common\Godot' is not recognized`。
- ❌ `> out.txt` 重定向 → 产出 0 字节文件。
- ✅ 上面那种**内联管道**写法。
- **看关键字，不看退出码**。沙箱固有噪声：`ERROR: Failed to open 'user://logs/...'`、`Failed to read the root certificate store.`、`[exit code: 1]`。

七套脚本：`greybox_check` / `camera_check` / `display_check` / `hud_layout_check` / `asset_draw_check` / `sort_check` / `evidence_archive_check`。

### §0.2 四个必踩的坑

1. **circle 的半径字段叫 `radius`，不叫 `r`**（`data/frames.json`）。
2. **树冠上抬 0.7r 只发生在「没有贴图」的色块分支**：`scripts/world_view.gd:568-575` 的 circle 分支先试 `_prop_tex(frame.id,label,rad)`，**有贴图就直接 `draw_texture_rect` 然后 `return`（不上抬）**；只有没贴图时才走 `:590-600` 的色块分支，那里 `:596 var lifted := center + offset + Vector2(0, -rad * 0.7)` 把树冠圆心上抬。A1–A3 有树/井贴图（`assets/village/scene/tree_a1..a3.png`、`well_old_a1..a3.png`），A4/A5 **没有场景贴图** ⇒ A4/A5 的老槐是「抬高一截的色块」，比 A1–A3 明显更高、也更靠前 —— 这就是它把井盖住的原因。
3. **`sort_y` 是排序键，升序绘制** ⇒ 键小的先画（在下层）。现状：墙行 `hpos.y+(ry+1)*TILE`、门洞同行深度、屋顶 wings 南沿、家具 `fr.end.y`、**circle `center.y + rad*0.7`**、standing rect `rect.end.y`、玩家 `player_pos.y + 14*0.7`（`world_view.gd:366-444`）。
4. **`_mdtest/sort_check.gd` 断言「排序结果按 sort_y 递增」的单调性**，且只覆盖 A1–A3 的十二栋（`:17-21` 注释「A4/A5 冻结」）。你的改动不能把同层物件的前后关系搞反。

---

## §1 问题定义（为什么必须修）

老槐的树冠盖住老井。**几何遮挡率**（树冠上抬后的圆 ∩ 井圆 ÷ 井圆面积，实测）：

| 帧 | 树 r | 井 r | 几何遮挡 | 实际看不看得见 |
|---|---|---|---|---|
| A1 | 32 | 32 | 0% | 看得见（贴图不抬） |
| A2 | 64 | 32 | 0% | 看得见（贴图不抬） |
| A3 | 96 | 32 | **61.8%** | 贴图路径，实际大多看得见 |
| A4 | 96 | 32 | **61.8%** | **看不见**（色块路径，树冠实心盖住） |
| A5 | 160 | 48 | **100%** | **完全看不见** |

**为什么这是 P0**：老井是故事里的钥匙级物证 ——
- `docs/story.md` §7.2①：「十字路口中央一块圆形沥青补丁」（A5）；
- `docs/story.md` §4.4：「老井就在工地西墙外……他们没敢动它，只是绕着它打了桩」（A4）；
- 玩家在 2001/2026 两帧**必须能看见并 E 检视**这口井，否则整条「地下有个洞，而且那个洞一直在」的线索链断在第一环。

井的世界坐标五帧固定 `(1360,848)`；老槐心固定 `(1296,976)`；两者相距 85px，而 A5 树冠半径 160 ⇒ **A5 纯靠调层解决不了几何重叠**（这是下面 §2.3 要处理的）。

---

## §2 必改清单（3 件事，全在 `scripts/world_view.gd`）

### 2.1 色块树冠不再上抬

`_draw_prop` 的色块分支里，树冠上抬量 `rad*0.7` 去掉（树冠直接画在 `center`），树干照旧画。
**理由**：贴图分支（也就是 A1–A3 的真实观感）本来就不上抬，色块分支上抬是历史补偿，结果 A4/A5 的树比 A1–A3 高一截且更靠前。统一后 A4/A5 的树高度与 A1–A3 一致。

### 2.2 井的深度键改成「贴地底缘」

circle 的 sort_y 现在一律 `center.y + rad*0.7`。对**平贴地**的圆（井、地面圆盘），正确深度是它的**底缘** `center.y + rad`（半径 32 的井 → 880，而不是 870.4）。树属于「立着的」，它的正确深度是树冠底缘 ≈ `center.y + 0.3r`（上抬 0.7r 后的圆底缘 ＝ center+0.3r）。
**要求**：把 circle 的深度键按「立着 / 贴地」区分开，别再用一刀切的 `rad*0.7`。

### 2.3 让井**永远可见**，且井**永不遮挡玩家**

目标两条，缺一不可：
1. 井在所有帧都画在**树冠之上**（玩家能看见井）；
2. 井是地面物件，**玩家站在它旁边/上面时玩家在上层**（井不盖玩家）。

⚠️ 只靠「给井加一个提层常数」做不到第二条（玩家 sort_y ≈ 井中心+10，若井提层 200+，井就会盖住站在井边的玩家）。所以需要**分段绘制**：把「井/碑这类贴地小地标」从 circle 链里单独抽出来，排在**树冠之后、玩家之前**绘制（树冠层 → 地标层 → 玩家层）。

实现方式自选（`_collect_front` 标记 + `_draw_front` 分段，或等价做法），但必须同时满足：

- ① 井（`label` 含「井」）在五帧都画在树冠之上；
- ② 玩家永远画在井之上（无论玩家站哪）；
- ③ 不破坏现有的墙/屋顶/家具/门洞/standing rect 的前后关系；
- ④ 排序结果仍然满足 `sort_check.gd` 的单调性断言（若该断言因分段而需要改写，**不要改测试文件** —— 见 §5，把需要改哪一行写进报告，由总策划裁决）。

### 2.4 兜底方案（只在 2.3 代价过大时用）

如果分段绘制实现代价过大（改得太深、影响面看不清），**只做 2.1 + 2.2**，并在报告里明确写：
- 剩余遮挡的**实测数字**（A3/A4/A5 各多少）；
- **建议的数据层动作**：`a5_2026` 的老槐 `radius` 160 → 128（`data/frames.json` 是 **L1 的独占文件，你不能动**），并说明「改完 A5 井是否就露出来」的推算。
由总策划决定要不要把这刀切给 L1。

---

## §3 验收口径（自己先跑一遍再交）

### 3.1 几何自检（自己写个一次性脚本，`lab/` 下临时文件，**不要提交**）

算出五帧的「井被树冠遮住的比例」：
- 树冠圆＝`center + (0, -0.7r)`、半径 r（**贴图分支不上抬**，所以两种分支各算一遍：贴图分支=树冠不抬、色块分支=树冠上抬；A4/A5 走色块分支）；
- 井圆＝`(1360,848)`、半径按帧 32/32/32/32/48；
- 交步进采样（步长 ≤ 4px）算被覆盖的像素比例。

**目标**：A4/A5 的「色块分支」遮挡率 = 0%（井完全露出来）；A1–A3 不许变差。

### 3.2 实机截图

用 `_mdtest/` 里的 shot 脚本（参考 `_evidence_shot.gd` 的写法）截 A4/A5 两帧的井附近画面，自己看图确认井可见、树没盖住、玩家没被井挡住。截图存 `lab/` 下（临时，**不要提交**），报告里描述你看到了什么。

### 3.3 七套回归全跑

七套脚本都要跑，逐套贴判绿关键字。特别注意：
- `sort_check.gd` → `SORT_CHECK_DONE fails=0`；
- `greybox_check.gd` → `WALL_BLOCKED`、`DOOR_PASSABLE`、`UNEXPLAINED_BLOCKS=0`、`REACH_OK=true`、`A3_OLD_WELL_UNDER_MILL=true`、`A2_MILL_SAME_SPOT=true`、`TIME_FWD_REACHED=[1,2,3,4]`、`A1_WELL_FREE`（A1 井是敞开的、能挡路 —— **你的改动不许让 A1 井变成不挡路**）；
- `asset_draw_check.gd` → `ASSET_DRAW_CHECK_DONE fails=0`（注意 `:216` 有断言 `AssetDraw.scene_tex("a4_2001","river") == null`，**你不要去补图，也不要改这条断言**）。

---

## §4 不要越界（这些是别的线）

| 事 | 归谁 |
|---|---|
| `data/frames.json`（A4/A5 地图帧、界碑、老槐半径） | **L1 地图修正线**（`docs/PROMPT-map-fix-exec.md`） |
| `_ref/houses/houses_data.json`（房子数据） | **L3 房屋数据线** |
| `scripts/house_shape.gd`（`CLUE_TEXTS` 证物文案） | **L4 证物文案线** |
| `scripts/main.gd` + `scripts/evidence_*.gd`（证物档案） | **L5 证物档案线** |
| `scripts/asset_draw.gd` 的 `scene_tex` 优先级、每帧界碑贴图接线 | **L8 资产接线线**（等美术同学的图） |
| `_mdtest/**` 里的测试文件 | **不改**。若某条断言因为你的改动而必须改，把「文件 + 行号 + 期望改成什么」写进报告，总策划裁决 |

---

## §5 收工

1. `git status --short` 确认**只有** `scripts/world_view.gd` 被你改（外加你新建的临时 `lab/` 文件，**不要 add 它们**）。
2. `git add scripts/world_view.gd`（**精确 add，绝不 `git add -A`** —— 工作区里有别的线的产物：`_ref/art/**/*.png` 12 张 M、`美术资产/` 一批 D、大批未跟踪文件）。
3. commit 信息：
   ```
   fix(render): 老槐不再盖住老井（色块树冠不上抬 + 井按贴地底缘分层 + 井恒可见且不挡玩家）
   ```
4. **另写** `docs/FEEDBACK-render-fix-exec.md`（≤120 行，中文）：做了什么 / 几何遮挡率改前改后 / 七套回归结果 / 截图观察 / **兜底方案是否触发 + 数据层建议** / 遗留问题 / 你碰到的坑。**这个文件用 `git add docs/FEEDBACK-render-fix-exec.md` 单独加进同一个 commit**。
5. 报告（给我的最终回复）必须包含：
   - 3 条改动逐条：改在哪一行、改前改后；
   - 几何遮挡率改前改后表（A1–A5）；
   - 七套回归结果逐套关键字；
   - 你碰到的坑与解法；
   - **兜底方案有没有触发**（触发了就给出「A5 老槐 radius 160→128」的数据层建议）。

---

## 依据文档

`docs/DECIDE-a4-a5-layout.md` §6（老槐遮井的根因与最小改法）、§9 R2/R3/R4（遗留风险）、`docs/story.md` §4.4 / §7.2①（为什么井必须可见）、`docs/HANDOFF-VILLAGE.md`（y-sort 机制）、`scripts/world_view.gd`（`world_view.gd:366-444` `_collect_front`、`:568-616` `_draw_prop`、`:618-636` `_prop_tex`/`_prop_box`）。
