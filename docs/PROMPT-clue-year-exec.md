# 新会话提示词：证物文案执行人 —— CLUE_TEXTS 支持按年覆盖

> 本线代号 **L4**。你只改**一个文件**：`scripts/house_shape.gd`。
> **前置**：L3（房屋数据线）必须先完成 —— L3 会撤掉 `school` 的「「周」界碑」家具、并改 `market` 的 name/note。你开工前先 `git log --oneline -5` 看 L3 的 commit 在不在。

---

## §0 开工前

| 项 | 值 |
|---|---|
| 仓库根 | `D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift` |
| HEAD 要求 | 含 L3 的提交（先 `git log --oneline -5` 确认；不在就**停下来报告**，不要自己改房屋数据） |
| 你能改 | `scripts/house_shape.gd`（唯一） |
| 你不能碰 | `scripts/main.gd`、`scripts/evidence_*.gd`（L5 独占）、`scripts/world_view.gd`（L2 独占）、`data/frames.json`（L1 独占）、`_ref/houses/houses_data.json`（L3 独占）、`assets/**`、`_mdtest/**`（其它测试不许改） |
| pwsh | 带 `sandbox_permissions: "danger-full-access"` |

### §0.1 跑回归的正确姿势

```powershell
& "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe" --headless --path . -s res://_mdtest/greybox_check.gd 2>&1 | Select-Object -Last 45
```

❌ `cmd /c "D:\steam\...\godot..."`（空格截断）／❌ `> out.txt`（0 字节）／✅ 内联管道。看关键字不看退出码。

---

## §1 现状与要改成什么

`scripts/house_shape.gd` 里有一个常量 `CLUE_TEXTS`（约 `:46-109`），结构是：

```
CLUE_TEXTS[house_id][家具中文name] = "一句话文案"
```

`hotspots()`（约 `:374-411`）取文案时：
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

---

## §2 必改清单

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
- 把结果贴进报告。

---

## §3 验收

1. **七套回归全跑**（`greybox_check` / `camera_check` / `display_check` / `hud_layout_check` / `asset_draw_check` / `sort_check` / `evidence_archive_check`），逐套贴判绿关键字。
   - `evidence_archive_check` 可能有**预期内的红**（L5 正在改证物模型、条数变了）——**不要改那个测试文件**，把红了哪条写进报告。
   - `greybox_check` 的 `CLUE_CHECKS_DEFERRED=A2-A5 空帧占位` 那行是旧提示（L1 落地后 A4/A5 帧不空了）—— 不用管，但要在报告里提一句。
2. **实机抽检**（可选但建议）：A4 帧在超市办公室 E 检视「文件柜」、A5 帧在超市门厅 E 检视「上磨盘」，确认取到的是**对应年代**的文案。

---

## §4 不要越界

| 事 | 归谁 |
|---|---|
| `data/frames.json`（A4/A5 帧、界碑世界热点文案、井文案） | **L1** |
| `scripts/world_view.gd` | **L2** |
| `_ref/houses/houses_data.json`（market 双态 note、撤 school 界碑家具） | **L3** |
| `scripts/main.gd` / `scripts/evidence_*.gd`（key 加年份、显示名、条数） | **L5** |
| 美术图 | 美术同学 |

---

## §5 收工

1. `git status --short` 确认只有 `scripts/house_shape.gd` 被改（+ 临时 `lab/`，**不要 add**）。
2. `git add scripts/house_shape.gd`（**精确 add，绝不 `git add -A`**）。
3. commit：
   ```
   feat(clue): CLUE_TEXTS 支持按年覆盖 + market 两态文案(2001/2026) + 删 school 界碑条目
   ```
4. 另写 `docs/FEEDBACK-clue-texts-year-exec.md`（≤100 行，中文）：改动逐条／覆盖度自检输出／七套回归结果／遗留问题。**单独 `git add` 加进同一个 commit**。
5. 报告（给我的最终回复）：改动逐条（改在哪一行）／覆盖度自检表（28 件全覆盖、0 条占位）／七套回归逐套关键字／是否触发了 L5 的预期红。

---

## 依据文档

`docs/story.md` §4.4 / §7.2⑥⑦ / §7.4（界碑三段挪位与「这一行和界碑必须分开放」）、`docs/DECIDE-a4-a5-layout.md` §11 裁定②③、`docs/PROMPT-clue-texts-exec.md`（上一版任务书，本线是它的按年扩展）、`docs/PROMPT-houses-fix-exec.md`（L3，前置）。
