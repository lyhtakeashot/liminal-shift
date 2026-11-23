# 新会话提示词：房屋数据执行人 —— A4/A5 六栋的状态与线索校正

> 本线代号 **L3**。你只改**一个文件**：`_ref/houses/houses_data.json`。
> **不要碰 `data/frames.json`**（L1 独占）、**不要碰 `scripts/house_shape.gd`**（L4 独占）、**不要碰 `scripts/**`**（L2/L5 独占）。

---

## §0 开工前

| 项 | 值 |
|---|---|
| 仓库根 | `D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift` |
| HEAD 要求 | ≥ `7c93898`；`git log -1` 确认 |
| 你能改 | `_ref/houses/houses_data.json`（唯一） |
| 你不能碰 | `data/frames.json`、`scripts/**`、`assets/**`、`_ref/art/**`、`_mdtest/**`、`docs/**`（除你自己的反馈文档） |
| 权威源 | `_ref/houses/houses_data.json` 是**唯一真相源**（`gen_all_houses.py:304-310` 明写）。**禁止调 `export_seed()`**（会把内联种子写回去、覆盖 JSON）。改完只改 JSON 本身。 |
| pwsh | 带 `sandbox_permissions: "danger-full-access"` |

### §0.1 数据结构（照抄，别改格式）

`houses_data.json` 是 **list**（18 条），每条键：
`id / name / lot / wings / partitions / doors / gate / rooms / furniture / clue / story / note`

- `lot` ＝ `[x0,y0,x1,y1]`（**含两端**，格坐标）
- `wings` ＝ `[[x,y,w,h], ...]`（**起点 + 宽高**，格坐标）⚠️ 别当 x1,y1,x2,y2
- `furniture[]` 每项含 `name / short / rect / note / clue / zone / ...`；`rect` ＝ `[x,y,w,h]`（格）
- `clue` ＝ 说明文字列表；家具的 `clue: true` 才生成 E 检视点

---

## §1 必改清单（4 件事）

### 1.1 `market` 一个 id 两种状态 —— 名字与说明要写清两态

现状：`market` 的 `name` 是「超市工地 · A4 2001 · 在建（粮站拆）」。
**A5 用的是同一个 id、同一份数据**（`data/frames.json` 的 a4_2001 与 a5_2026 都写 `"id":"market"`），但 A5 它是营业中的超市。

**要求**：`name` 改成**不带单一年份**的中性写法，同时在 `note` 里把两态说清。参考现有其它 house 的命名风格（`name` ＝「谁的房子 · 什么状态」）。

`note` 必须包含：
- A4 2001：粮站拆了，改在建工地（工地围挡/脚手架/建材堆/未拆封货架×18/工地办公室/工棚）；
- A5 2026：超市照常营业；
- 面积口径：**屋本体 42×28 格**（用户 2026-11-23 前拍板「长宽各扩一倍」：原 21×14 → 42×28）；
- 两条线索家具各自的**两态位置**（见 §1.2）；
- 「**路口圆形沥青补丁 = 井口**」这条既有口径**保留**。

### 1.2 `market` 的两条线索家具：note 写清两态

| 家具 | rect(格) | A4 在建态 | A5 营业态 |
|---|---|---|---|
| `文件柜` | `[38,10,1,2]` | 工地办公室里，柜里是**土地登记表第二联 + 改过的地质报告** | 搬进超市办公室（同一件家具，跨时代不变） |
| `上磨盘` | `[15,22,2,1]` | **粮站拆出、暂放工地围挡角落**，凿着「沈氏丰源·一九五七」 | **摆进超市门厅**（story §7.2⑥ 的现代物证） |

两条 `note` 都要写「A4 在……／A5 在……」双态，**并保留「沈氏丰源·一九五七」的刻字原文**（这是物证原文，不能改写）。

### 1.3 撤掉 `school` 的「「周」界碑」家具 ⭐

**原因**：L1 会在 A5 帧的 `data/frames.json` 里放**一块世界界碑**（rect `[32,1024,16,32]`，热点 `(40,1040)`，位置＝小学操场北围墙西端）。而 `school` 现在有一条 clue 家具「「周」界碑」（rect `[1,18,2,1]`），它的世界热点中心也在 (64,1040) —— **两者只差 24px，是同一块石头**。留着会让玩家在同一处检视到两个「界碑」、证物档案多出一条重复记录。

**要求**：把 `school` 的 `furniture[]` 里那条「「周」界碑」**整条删掉**（含 `furniture` 条目本身）。
- `school` 的 `clue` 列表里如果有对应说明文字，一并删掉。
- `story`/`note` 里如果提到界碑，改成指向**世界界碑**（例如「围墙上嵌着半截石碑——那是世界地标，不属于这间屋子」），**不要把叙事抹掉**。
- `school` 的 `lot`/`wings`/`partitions`/`doors`/`gate`/`rooms` **一个字都不许动**（界碑那块墙格还在，形状照旧由 L1 放）。

### 1.4 `zheng_a4` 不补线索 —— 确认不动

`zheng_a4.note` 已写明「住户对陆家旧事和老井一无所知，**不设陆家线索格**」，其 `furniture[].clue` 数量应为 0。
**要求**：核对一下确实没有 `clue: true` 的家具；**不要新增**任何线索家具。

---

## §2 不要越界（别的线）

| 事 | 归谁 |
|---|---|
| `data/frames.json`（A4/A5 摆位、界碑 rect/热点、老井文案） | **L1** |
| `scripts/house_shape.gd` 的 `CLUE_TEXTS`（证物文案，含 `market` 的 2001/2026 两版、`school` 那条要删） | **L4**（**前置＝本线完成**） |
| `scripts/main.gd` / `scripts/evidence_*.gd`（证物档案按年） | **L5** |
| `scripts/world_view.gd`（渲染） | **L2** |
| 美术图 | 美术同学（清单 `docs/ART-HANDOFF-a4a5.md`） |

⚠️ **你改名会连带影响 `CLUE_TEXTS` 的 key**：`scripts/house_shape.gd` 的 `CLUE_TEXTS[house_id][家具中文名]` 用的是**家具 `name`**，不是 `short`、不是 id。你若改了任何 clue 家具的 `name`，L4 必须同步改 key，否则证物文案会**静默退化成占位句「「X」立在这里。」**。⇒ **本线不要改任何 clue 家具的 `name`**（`文件柜`/`上磨盘`/`保险柜`/`账桌`/`蜂窝煤炉`/`招牌小字`/`账柜` 全部保持原名）。

---

## §3 验收

1. **数据自检**（自己写一次性 python 脚本，`lab/` 下临时文件，**不要提交**）：
   - `json.load` 成功，18 条，id 无重复；
   - 六栋（`market`/`shen_a4`/`zhou_a4`/`zheng_a4`/`school`/`toyshop`）的 `lot`/`wings`/`doors`/`gate` 与改前**逐字节一致**（你只应改了 `market` 的 `name`/`note`、两条家具的 `note`、删了 `school` 一条家具）；
   - 全库 `clue: true` 的家具总数 = 改前 29 − 1（删了 school 那条）＝ **28**；
   - `zheng_a4` 的 `clue: true` 家具数 = **0**；
   - `school` 的家具里已无「界碑」；
   - 打印每栋 clue 家具清单供报告用。
2. **回归**（跑法见 `docs/PROMPT-map-fix-exec.md` §0.1 的「跑回归的正确姿势」，或 `docs/PROMPT-overseer.md` §九）：
   `greybox_check` / `camera_check` / `display_check` / `hud_layout_check` / `asset_draw_check` / `sort_check` / `evidence_archive_check` 七套全跑，**逐套贴判绿关键字**。
   - ⚠️ `evidence_archive_check` 会有一处**预期内的红**：它断言过「老井」「界碑」相关的条数，`school` 那条界碑家具撤掉后条数会少 1。**不要改测试文件** —— 把「哪个断言红了、期望值 vs 实际值」写进报告，由总策划裁决（L5 会顺手把这类断言一起改）。
3. 其它六套必须**全绿**。

---

## §4 收工

1. `git status --short` 确认只有 `_ref/houses/houses_data.json` 被你改（+ 你新建的临时 `lab/` 文件，**不要 add**）。
2. `git add _ref/houses/houses_data.json`（**精确 add，绝不 `git add -A`**）。
3. commit：
   ```
   data(houses): market 双态说明 + 撤掉 school 界碑家具（改由 A5 世界界碑承担）+ zheng_a4 确认无线索
   ```
4. 另写 `docs/FEEDBACK-houses-fix-exec.md`（≤120 行，中文）：4 项改动逐条改前改后／数据自检输出／七套回归结果（含那条预期红的断言）／**你改过哪些 clue 家具的 `name`（如果有，告诉 L4 要改哪个 key）**／遗留问题。**单独 `git add docs/FEEDBACK-houses-fix-exec.md` 加进同一个 commit**。
5. 报告（给我的最终回复）：4 项改动逐条 + 自检输出 + 七套回归逐套关键字 + 你对 L4 的交接说明（哪些 key 要跟着改）。

---

## 依据文档

`docs/DECIDE-a4-a5-layout.md` §11（总策划裁定）、`docs/story.md` §4.4（2001 合法化）/ §7.2⑥（超市门厅的上磨盘）/ §7.4（界碑三段挪位）、`docs/HANDOFF-VILLAGE.md`（房屋数据格式与坑表）、`docs/PROMPT-map-fix-exec.md` §3.6（A5 世界界碑）。
