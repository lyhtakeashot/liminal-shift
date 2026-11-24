# 新会话提示词：证物文案执行人 —— CLUE_TEXTS 支持按年覆盖

> 本线代号 **L4**。你只改**两个文件**：`scripts/house_shape.gd`（文案本体）+ `scripts/frame_data.gd`（把年份传进去，**只改一处调用**）。
> **前置**：L3（房屋数据线）必须先完成 —— L3 会撤掉 `school` 的「「周」界碑」家具、并改 `market` 的 name/note。你开工前先 `git log --oneline -5` 看 L3 的 commit 在不在。
>
> ⚠️ **2026-11-24 总策划修订**：原版写「只改一个文件」，但「按年取值」必须有年份来源，而 `house_shape.hotspots()` 原本没有 year 参数 ⇒ 原任务书落不了地。本版已把 `scripts/frame_data.gd` 加进白名单（见 §0/§2.0），其余要求不变。

---

## §0 开工前

| 项 | 值 |
|---|---|
| 仓库根 | `D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift` |
| HEAD 要求 | 含 L3 的提交（先 `git log --oneline -5` 确认；不在就**停下来报告**，不要自己改房屋数据） |
| 你能改 | `scripts/house_shape.gd`（文案本体 + `hotspots()` 取值逻辑）、`scripts/frame_data.gd`（**只改 `:66` 那一处调用**，把 year 传进去；其它一律不动） |
| 你不能碰 | `scripts/main.gd`、`scripts/evidence_*.gd`（L5 独占）、`scripts/world_view.gd`（L2 独占）、`data/frames.json`（L1 独占）、`_ref/houses/houses_data.json`（L3 独占）、`assets/**`、`_mdtest/**`（其它测试不许改） |
| pwsh | 带 `sandbox_permissions: "danger-full-access"` |

> ⚠️ **L2（渲染线）正在跑，`scripts/world_view.gd` 是它的未提交 WIP。**
> `_mdtest/asset_draw_check.gd:13` 和 `_mdtest/sort_check.gd:11` 都 `preload("res://scripts/world_view.gd")` ⇒ 你跑这两套回归时会读到 L2 的在途版本。
> 若 L2 的 WIP 造成 parse 失败：**不要去改 L2 的文件**，按 §0.2 处理。

### §0.1 跑回归的正确姿势

```powershell
& "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe" --headless --path . -s res://_mdtest/greybox_check.gd 2>&1 | Select-Object -Last 45
```

❌ `cmd /c "D:\steam\...\godot..."`（空格截断）／❌ `> out.txt`（0 字节）／✅ 内联管道。看关键字不看退出码。

### §0.2 L2 的 WIP 挡路时怎么办

如果你跑 `asset_draw_check` / `sort_check` 时报 parse 错误，且错误出在 `scripts/world_view.gd`：
1. 先 `git stash list` 确认不是你的问题；
2. 把 `scripts/world_view.gd` 临时换成 HEAD 版本跑回归：
   ```powershell
   Copy-Item scripts/world_view.gd lab/_world_view_wip_backup.gd
   git show HEAD:scripts/world_view.gd | Out-File -Encoding utf8 scripts/world_view.gd
   ```
3. 跑完回归**立刻原样还原**（`Copy-Item lab/_world_view_wip_backup.gd scripts/world_view.gd`），并用 `Get-FileHash scripts/world_view.gd` 对比还原前后的 SHA256 必须一致；
4. **绝不把 `scripts/world_view.gd` 加进你的 commit**。

---

## §1 现状与要改成什么

`scripts/house_shape.gd` 里有一个常量 `CLUE_TEXTS`（约 `:46-109`），结构是：

```
CLUE_TEXTS[house_id][家具中文name] = "一句话文案"
```

`hotspots()`（约 `:378-411`）取文案时：
```
text = CLUE_TEXTS.get(house_id, {}).get(家具name, "")
if text == "": text = "「%s」立在这里。" % 家具name   # 占位句
```

**要改成**：`CLUE_TEXTS[house_id][家具名]` 的值可以是**字符串**（对所有年代通用），也可以是**按年字典** `{年份(int) : 文案}`（该年代专用，优先于通用串）。

示意：
```
CLUE_TEXTS["market"]["文件柜"] = {2001: "…2001 年的文案…", 2026: "…2026 年的文案…"}
```
取值规则（**你来实现，逻辑放 `hotspots()` 里**）：
1. 值为 Dictionary 且含 `f.year` ⇒ 用该年的文案；
2. 值为 Dictionary 但不含该年 ⇒ 回退到该字典里唯一的通用键（如 `"default"`），若没有 ⇒ 退占位句；
3. 值为 String ⇒ 直接用（所有年代通用）。

⚠️ **键是家具的 `name`（中文名），不是 `short`、不是 id**。改名会静默退占位句 —— 这是已知隐患，**本线不要改名**，只在必要处补年份版。

⚠️ **年份从哪来（这是原版任务书漏掉的一环）**：`house_shape.hotspots(data, pos)` **目前没有 year 参数**，而年份在 `scripts/frame_data.gd:28`（`year = int(d.get("year", 0))`）。所以「按年取值」必须先有年份传进来 —— 见 §2.0。

---

## §2 必改清单

### 2.0 【先做这一步】把年份传进 `hotspots()`

**问题**：`scripts/house_shape.gd:378` 的签名是 `static func hotspots(data: Dictionary, pos: Vector2) -> Array` —— **没有 year**，而 §1 要求「按年取值」。年份现在只存在于 `scripts/frame_data.gd:28`（`year = int(d.get("year", 0))`）。

**改法（二选一，推荐 a）**：

a) **加可选参数（改动最小、向后兼容）**
   ```gdscript
   # scripts/house_shape.gd:378
   static func hotspots(data: Dictionary, pos: Vector2, year: int = 0) -> Array:
   ```
   ```gdscript
   # scripts/frame_data.gd:66
   hotspots.append_array(HouseShape.hotspots(hdata, hpos, year))
   ```
   `year` 在 `setup()` 里已经是成员变量（`:28` 赋值），所以 `:66` 这一处可以直接用。

b) 不传参、在 `house_shape.gd` 内部从 `data` 里取年份 —— **不要选这条**：`houses_data.json` 的每栋房子**不带 year 字段**（同一栋 `market` 被 A4/A5 两帧复用），所以家具侧根本取不到年份，**只能由帧数据传入**。

⚠️ `HouseShape.hotspots(` 在全仓**只有一个调用点**（`scripts/frame_data.gd:66`），`_mdtest/` 里没有任何测试直接调用它 ⇒ 改签名不会破坏测试。
⚠️ **不要改 `scripts/frame_data.gd` 的其它部分**（`setup()`、`_rect_from()`、`_polygon_scanlines()`、`is_free()`、`hotspot_at()` 一律不动）。
⚠️ **不要把 year 加进 hotspot 字典的输出字段** —— `scripts/main.gd` 的 `_collect_evidence()` 已经用帧的 `f.year` 取年份（不是从 hotspot 里取），加字段会两边不一致。

### 2.1 `market` 两条线索家具：写 2001 / 2026 两版

`market` 复用了同一个 id，A4 在建、A5 营业，两态位置不同（story §7.2⑥：2026 超市门厅摆着老磨盘）。

| 家具 | 2001 版要点 | 2026 版要点 |
|---|---|---|
| `文件柜` | 工地办公室；柜里是**土地登记表第二联 + 改过的地质报告**（「地下有暗河，不宜大开挖」） | 搬进超市办公室；同一本登记表 |
| `上磨盘` | **粮站拆出、暂放工地围挡角落**，凿着「沈氏丰源·一九五七」 | **摆进超市门厅**（现代物证⑥） |

两条文案都必须**保留「沈氏丰源·一九五七」的刻字原文**（物证原文不能改写）。

**写作纪律（沿用上一版证物文案线的规矩）**：
- **只写看到什么，不写意味着什么**；
- A1 不点破 1957，A4/A5 可以点破；
- 不写「玩家应该想到…」这种出戏的话。

### 2.2 `school` 的界碑文案

L3 已经把 `school` 的「「周」界碑」家具**删掉了** ⇒ `CLUE_TEXTS["school"]["「周」界碑"]` 这条要**删掉**（留着一个没有家具的 key 不会被用到，但会让下次有人以为界碑还是家具）。

⚠️ A5 那块界碑现在由 **L1 放在 `data/frames.json` 的世界界碑**（rect `[32,1024,16,32]`，热点 title「界碑」）承担 ⇒ **它的文案在 `data/frames.json` 里，不在你这个文件**（L1 已经写好了：「围墙里嵌着半截石碑，碑面和砖面抹成了一个平，缝里塞着旧水泥。字磨得只剩一个「周」，旁边那个字只留着一道竖笔。石头底下的土比四周高出一小截。」）。
**你不要在 `CLUE_TEXTS` 里再补 school 界碑条目**（会变成两个来源）。

### 2.3 `zheng_a4` 不补文案

`zheng_a4` 的 clue 家具数 = 0（L3 已确认）⇒ **不要给 `zheng_a4` 加任何 `CLUE_TEXTS` 条目**（story 明确「不设陆家线索格」）。

### 2.4 覆盖度自检（做成常驻断言或一次性脚本）

写一个一次性 python 或 GDScript 脚本（`lab/` 下临时，**不要提交**），逐栋列出 `houses_data.json` 里所有 `clue: true` 的家具，检查 `CLUE_TEXTS[house_id][家具name]` 是否存在且**非占位句**（不含「立在这里」）。
- L3 撤掉 school 界碑后，**期望 28 件**家具全覆盖（A1–A3 的 19 件 + A4/A5 的 9 件）。
- ⚠️ **28 件是「家具数」，不是「文案条数」**：市场那两条家具各有 2001/2026 两版文案 ⇒ 文案条数是 30 条。报告里两个数都写出来，别混。
- 现在的实测量（总策划 2026-11-24 实测，可当对照基准）：
  - 全库 `clue:true` 家具 = **28** 件；`school` clue = 0（界碑家具已撤）、`zheng_a4` clue = 0；
  - 占位句（"立在这里"）条数 = **0**；
  - 归一后的证物卡 = **27 张 / 58 条观察**（L5 线实测值；你的改动**不应该**改变卡数 27 —— 只改文案内容，不新增/删除家具）。
- 把结果贴进报告。

### 2.5 顺手修掉 `scripts/house_shape.gd:374-377` 的过期注释

这段注释是错的（总策划 2026-11-24 实测）：

```
## ⚠️ 只生成**落在房子 lot 内**的家具。lot 外的 clue 家具（如磨坊数据里的「老井」，
## rect [6,10] 已在 lot 下界之外）属于**世界级地标**，由 frames.json 的 hotspots 手写管理，
```

实测：`mill_a1` / `mill_a2` / `mill_a3` 的「老井」家具 rect = `[6,12,1,1]`，而 `mill` 的 lot = `[0,0,17,12]`（`mill_a3` 是 `[0,0,17,16]`）⇒ **它在 lot 内**，不是世界级地标。所以证物档案里真的有一张 `mill::老井` 卡（3 条观察，1926/1951/1976）。

请把注释改成如实描述（例如「只生成落在 lot 内的家具；磨坊院内的『老井』是院内井位，与村中那口老井是同一个东西的两个位置，标题会加『· 院里』后缀，见 :395-399」）。**只改注释文字，不要改过滤逻辑。**

### 2.6 `docs/HANDOFF-VILLAGE.md` 里遗留的旧口径（**不属你的白名单 —— 只核对、只报告，不要改**）

用户 2026-11-24 交代「任务书要包含 HANDOFF-VILLAGE.md 里遗留的旧口径」。总策划已把该文件逐行核实过（实测 568 行），结论是：**这些全是 L6 文档线的活**（`docs/HANDOFF-VILLAGE.md` 不在你 `scripts/` 白名单里），**你只做一件事：在你的报告里把下面这张表抄一遍并逐条标注「已确认 / 已过期 / 与本线无关」**。

⚠️ **绝对不要自己改 `docs/HANDOFF-VILLAGE.md`** —— L6 文档线与你可以同时开，两边都改同一文件会互相覆盖。

**表 A：@16px 旧口径（TILE 已改成 32，全文 px 数都要重算）**

| 位置 | 现在写的 | 正确值（@32px） |
|---|---|---|
| `:86` 全局声明 | 「格坐标，一格 = 16×16 px」 | 一格 = 32×32 px（`scripts/house_shape.gd:13` `const TILE := 32.0`） |
| `:119-134` §3 表的 px 列（18 行全中） | 如 `lu_house`「20×10 = 320×160」 | 按 `houses_data.json` 的 `lot`/`wings` 重算：占地 = lot 格数×32，屋本体 = wings×32。实测 `lu_house` lot 20×13=640×416、wings 15×11；`market` 42×28=1344×896；`school` 38×30=1216×960；`toyshop` 占地 21×20=672×640、屋本体 21×16=672×512 |
| `:239` §6.4 杂草标注 | 「需铺 16px 杂草素材」 | 32px |
| `:273` §6.5 toyshop 现状段 | 「21×20 格（336×320 px）…屋本体 21×16」 | 21×20 格（672×640 px）、屋本体 21×16 格（672×512 px） |
| `:284` §6.5 school 现状段 | 「38×30 格（608×480 px）…155 件家具（1 clue）」 | 38×30 格（1216×960 px）、**154 件家具、0 clue**（界碑家具 L3 已撤） |
| `:340` 尺寸表需回写说明 | 「现行为 38×30 格 = 608×480 px」 | 38×30 格 = 1216×960 px |
| `:550` §8 图像说明 | 「126 个 16px 文件」 | 历史说明，可加「（16px 旧口径）」注 |

**表 B：界碑归属已变（界碑家具 L3 已撤，现在是 frames.json 里的世界地标）**

| 位置 | 现在写的 | 正确口径 |
|---|---|---|
| `:78` `_redo_school.py` 摘要行 | 「「周」界碑 `[1,18,2,1]`」 | 界碑**不再是 school 的家具**；A5 世界界碑＝`data/frames.json` rect `[32,1024,16,32]`、热点 `(40,1040)` |
| `:147` 三条线索落点表 | 界碑 = school 围墙 `[1,18,2,1]` | 同上；`[1,18,2,1]` 这个坐标已作废 |
| `:289` §6.10 school 证物链 | 「界碑现为 `[1,18,2,1]`」 | 同上 |

**表 C：过期陈述（事实已变）**

| 位置 | 现在写的 | 现在的真事实 |
|---|---|---|
| `:377` §6.9 下游注意 | 「`data/frames.json` 的 `a5_2026` 帧仍是空的」 | L1 已落地：a5_2026 = 17 shapes / 7 hotspots |
| `:512` §7.4 地图要放大 | 「`world` 现在是 `640×360`…建议 `1600×900`」 | world = **3200×2400**、start [1024,1680]、主路 y=1664 |
| `:132` market 行 | 「21×14 = 336×224」「⬜ 初版」「A5 营业态要另起 `market_a5`」 | market **单 id 两形态**（A4 在建 / A5 营业，**没有 `market_a5`**）、42×28 格 = 1344×896 px、58 家具 / 2 clue、已定稿 |
| `:136` school 行 | 「38×30 = 608×480」「155(1)」 | 38×30 = 1216×960 px、154 家具 / **0 clue** |
| `:5` 头部 | 「写于 2026-11-20（11-20 更新）」 | 现在是 2026-11-24 |

**表 D：历史记录（按既定纪律「历史记录不改写」，但可加口径注）**

`:300`（§6.7 v2 翻倍，「42×32 格，672×512 px @16px/格」）、`:307`（§6.7 界碑坐标随尺寸翻倍）、`:326`（§6.8 v3 决策表 608×480）、`:334`（§6.8 v3 界碑 `[1,17,2,1]`）、`:362`（§6.9 v4 界碑）、`:397`（§6.10 v5 界碑）—— 这些都在「v2/v3/v4/v5 当时做了什么」的历史节里，**不改内容**，最多加一行「（16px 旧口径 / 界碑已于 L3 撤出 house 数据）」。

> 📌 这份清单已同步进 L6 任务书 `docs/PROMPT-doc-rewrite-v2-exec.md`（L6 会照着改）。你在报告里只需要**确认数字对不对**（比如你实测的 154 件家具 / 0 clue 与表 B/C 一致），**不要自己去改文件**。

---

## §3 验收

1. **七套回归全跑**（`greybox_check` / `camera_check` / `display_check` / `hud_layout_check` / `asset_draw_check` / `sort_check` / `evidence_archive_check`），逐套贴判绿关键字。
   - `evidence_archive_check` 已经有 L5 的新模型（**27 张卡 / 58 条观察**，PASS 111 / FAIL 0）⇒ 你改文案**不应该**让它变红。万一红了，先查是不是自己把卡数或观察数改了（你不该改家具，只该改文案）。
   - `greybox_check` 的 `CLUE_CHECKS_DEFERRED=A2-A5 空帧占位` 那行是旧提示（L1 落地后 A4/A5 帧不空了）—— 不用管，但要在报告里提一句。
   - `asset_draw_check` / `sort_check` 会 preload L2 在途的 `scripts/world_view.gd`，按 §0.2 处理。
2. **实机抽检**（可选但建议）：A4 帧在超市办公室 E 检视「文件柜」、A5 帧在超市门厅 E 检视「上磨盘」，确认取到的是**对应年代**的文案。

### 3.1 顺手核一遍「同一张卡里两条一模一样的观察」

总策划 2026-11-24 实测发现 5 张卡存在跨年代重复文案。**其中 2 张是你的活，3 张不是**：

| 卡 | 现象 | 归谁 |
|---|---|---|
| `market::文件柜` | 2001 与 2026 两条**完全相同**（CLUE_TEXTS 现在是单一 String，两年代共用） | **你（L4）** —— 拆成两版 |
| `market::上磨盘` | 2001 与 2026 两条**完全相同** | **你（L4）** —— 拆成两版 |
| `界碑` | 1926/1951/1976 三条**逐字相同**（「半截石碑，埋在路边的土里。字被凿过，只剩两个：「周界」。」） | **L1**（文案在 `data/frames.json`，不是你的文件）—— 报告里点出来即可，别去改 |
| `坝` | 1926/1951/1976/2026 四条逐字相同 | **L1** —— 同上 |
| `田` | 1951 与 1976 两条逐字相同 | **L1** —— 同上 |

> 📌 界碑那条对应验收尾巴 **R7**（1951 该写「被凿了一半、开始往土里埋」，story §4.4 已有设定），但因为文案在 `frames.json`，**不并入本线**，已登记在 `docs/PROMPT-overseer.md` 的待办里由 L1 处理。你只要在报告里写「界碑 1951 文案与 1926/1976 重复，归 L1」。

---

## §4 不要越界

| 事 | 归谁 |
|---|---|
| `data/frames.json`（A4/A5 帧、界碑/坝/田 的世界地标热点文案） | **L1** |
| `scripts/world_view.gd` | **L2** |
| `_ref/houses/houses_data.json`（market 双态 note、撤 school 界碑家具） | **L3** |
| `scripts/main.gd` / `scripts/evidence_*.gd`（归一键、卡片结构、条数） | **L5**（**已交付并验收通过**，commit `5a36770`） |
| `scripts/frame_data.gd` | **你**（只改 `:66` 一处调用，见 §2.0） |
| `docs/HANDOFF-VILLAGE.md`（旧口径回写，见 §2.6） | **L6 文档线** —— 你只核对、只报告，**不改** |
| 美术图 | 美术同学 |

---

## §5 收工

1. `git status --short` 确认只有 `scripts/house_shape.gd` + `scripts/frame_data.gd` 被改（+ 临时 `lab/`，**不要 add**）。
2. `git add scripts/house_shape.gd scripts/frame_data.gd`（**精确 add，绝不 `git add -A`**）。
3. commit：
   ```
   feat(clue): CLUE_TEXTS 支持按年覆盖 + market 两态文案(2001/2026) + 删 school 界碑条目
   ```
4. 另写 `docs/FEEDBACK-clue-texts-year-exec.md`（≤100 行，中文）：改动逐条／覆盖度自检输出／七套回归结果／遗留问题。**单独 `git add` 加进同一个 commit**。
5. 报告（给我的最终回复）：改动逐条（改在哪一行）／覆盖度自检表（28 件全覆盖、0 条占位；文案 30 条）／七套回归逐套关键字／是否改动了卡数（不应改动）／界碑·坝·田 的重复文案提示（归 L1）／**§2.6 四张表的核对结果（哪些已确认、哪些数字对不上）**。

---

## 依据文档

`docs/story.md` §4.4 / §7.2⑥⑦ / §7.4（界碑三段挪位与「这一行和界碑必须分开放」）、`docs/DECIDE-a4-a5-layout.md` §11 裁定②③、`docs/PROMPT-clue-texts-exec.md`（上一版任务书，本线是它的按年扩展）、`docs/PROMPT-houses-fix-exec.md`（L3，前置）。
