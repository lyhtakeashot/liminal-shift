# 新会话提示词：证物档案执行人 —— 证物模型改成「日期化观察记录」

> 本线代号 **L5**。你改这三个文件：
> `scripts/main.gd`、`scripts/evidence_store.gd`、`scripts/evidence_archive.gd`
> 以及测试 ` _mdtest/evidence_archive_check.gd`（**只有这个测试文件你可以改**，别的测试不许动）。
> **不要碰 `scripts/house_shape.gd`**（L4 独占）、**不要碰 `data/frames.json`**、**不要碰 `_ref/houses/houses_data.json`**。

---

## §0 开工前

| 项 | 值 |
|---|---|
| 仓库根 | `D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift` |
| HEAD 要求 | ≥ `7c93898`；`git log -1` 确认 |
| 你能改 | `scripts/main.gd`、`scripts/evidence_store.gd`、`scripts/evidence_archive.gd`、`_mdtest/evidence_archive_check.gd` |
| 你不能碰 | `scripts/house_shape.gd`、`scripts/world_view.gd`、`data/frames.json`、`_ref/houses/houses_data.json`、`assets/**`、`_mdtest/` 里其它测试 |
| pwsh | 带 `sandbox_permissions: "danger-full-access"` |

### §0.1 跑回归的正确姿势

```powershell
& "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe" --headless --path . -s res://_mdtest/evidence_archive_check.gd 2>&1 | Select-Object -Last 45
```

- ❌ `cmd /c "D:\steam\...\godot..."` → 路径含空格被截断（`'D:\steam\steamapps\common\Godot' is not recognized`）。
- ❌ `> out.txt` → 产出 0 字节文件。
- ✅ 内联管道。看关键字不看退出码（沙箱噪声 `Failed to read the root certificate store.` / `[exit code: 1]`）。

---

## §1 为什么改（现状的问题）

现在的证物模型是「**按对象去重**」：
- 世界地标的 key ＝ hotspot 的 `title`（`scripts/main.gd:249-269`）；家具的 key ＝ `house_id::家具名`。
- 结果：1926 年那棵「今年刚栽下」的老槐和 2026 年「一百岁」的老槐**共用一个 key** ⇒ 玩家在 2026 再看一次老槐，档案里那条**不会更新**，永远停在 1926 的文案。
- 同理 `market::文件柜`、`market::上磨盘` 在 A4/A5 两帧共用一条 ⇒ A5 看到的信息被 A4 那条盖掉。

**这个游戏的全部主题就是「同一个东西在五个年代里的变化」**，而证物档案是玩家唯一的跨时代记录板 —— 按对象去重等于把主线抹掉。
⇒ 改成**日期化观察记录**：同一对象在每个年代各记一条。

---

## §2 必改清单（4 件事）

### 2.1 key 加年份

| 类型 | 现状 | 改成 |
|---|---|---|
| 家具 | `house_id::家具名` | `house_id::家具名::年份` |
| 世界地标 | `title` | `title::年份` |

年份取当前帧的 `f.year`（`scripts/main.gd` 里 `_collect_evidence(h, f)` 的 `f` 就是 `tl.current()`）。

**同对象同年代重复检视仍然只入一条**（去重逻辑不变，只是 key 多了年份这一维）。

### 2.2 显示名加年份

条目 `name` 改成 `名称 · 年份`（例：`老槐 · 1926`、`老槐 · 2026`）。
`source`（来源标签）保持现在的写法不变（`<年份> · 村中` / `<房名> · <年份>`）。

### 2.3 开档时收紧：**档案开着时不响应 SHIFT / E**

现状（`scripts/main.gd:96-165` `_process()`）：
- `:100-101` `if Input.is_action_just_pressed("shift_axis"): tl.toggle_axis()` —— 在档案暂停判断**之前** ⇒ 开着档案还能切时代；
- `:131-132` `if Input.is_action_just_pressed("inspect"): _do_inspect()` —— 也在**之前** ⇒ 开着档案还能 E 检视并继续入档；
- `:146-151` 才是 `if archive != null and archive.is_open(): player.walking = false; _set_hud_hidden(true); return`。

**要求**：把 `shift_axis` 与 `inspect` 两个分支**移到档案暂停判断之后**（即开档时世界是停的）。
配套：`scripts/evidence_archive.gd` 的底部 footer（`_draw_footer`，约 `:291`）加一行提示，例如「**世界已暂停 · 按 I 或 Esc 关闭档案**」。

> 说明：任务书原本写「打开时暂停游戏逻辑（不响应行走/时间轴）」，现状是行走停了但 SHIFT/E 没停 —— 现在按上面收紧，与口径一致。

### 2.4 条数预期（写进测试断言）

实测当前证物总量：**41 条**（家具 29 + 世界地标 12）。改成按年分条后：
- 家具：29 件 × 各自出现的帧数（A1–A3 的家具在三个年代各有一条）⇒ **约 43 条**（29 件里，mill 的三条「老井」各跨 3 帧、market 的 2 条跨 2 帧、其余各 1 帧）；
- 世界地标：12 条 × 各自出现的帧数（老槐 5 帧 ⇒ 5 条、坝 5 ⇒ 5、田 5 ⇒ 5、老井 5 帧但 title 各不同 ⇒ 5 条、界碑 A1–A4 4 条……）⇒ **约 24 条**；
- 合计 **约 56–58 条**（L3 会撤掉 `school` 的「「周」界碑」家具，A5 那条界碑改由 L1 的世界界碑承担，数目会再动一点点 —— **最终数字以你自己实测为准**，把实测值写进报告）。

---

## §3 测试改造（`_mdtest/evidence_archive_check.gd`，你可以改）

现有断言里**这几处一定要改**（它们是按老模型写的）：
- `:234` 注释「地标 key = title，跨时代同名只留一条」→ 改成「同年代同名去重，跨年代分条」；
- `:237-245` 找 `title == "老井"` 的地标热点后断言 `EvidenceStore.count() == 3` → 按新模型重算；
- `:249-258` A2 的「老井 · 石板」是独立证物、`count() == 4` → 按新模型重算；
- 「跨时代同名老槐只入 1 条」那条 ⇒ 改成「**入 5 条**（1926/1951/1976/2001/2026 各一条）」。

**新增断言**（这几条是本线的意义所在，必须有）：
1. 同一对象在两个不同年代检视 ⇒ **两条**记录，顺序按收集顺序；
2. 同一对象在**同一年代**重复检视 ⇒ 仍然只有一条（去重没坏）；
3. 条目 `name` 带年份后缀（`老槐 · 1926` 之类），`source` 保留原有格式；
4. 开档状态下按 SHIFT **不切时代**、按 E **不检视**（可直接调 `_process` 或断言 `tl` 的当前年份未变）；
5. 存档落盘/读回后条数与顺序不变（现有 `:90` 那条已有，重算条数即可）。

---

## §4 不要越界

| 事 | 归谁 |
|---|---|
| `scripts/house_shape.gd` 的 `CLUE_TEXTS`（证物文案按年、market 两版文案、删掉 school 那条界碑文案） | **L4**（前置＝L3） |
| `data/frames.json`（A4/A5 帧、界碑、井文案） | **L1** |
| `scripts/world_view.gd`（渲染） | **L2** |
| `_ref/houses/houses_data.json`（撤 school 界碑家具） | **L3** |

⚠️ **key 的另一段是 `house_id::furniture`**：`h.furniture` 来自 `scripts/house_shape.gd` 的 `hotspots()`（L4 也在改那个文件，但 L4 只改 `CLUE_TEXTS`，**不改 `hotspots()` 的输出字段**）。如果 L4 动了 `house_name` 的写法，`_short_house_name()`（`scripts/main.gd:276-282`）的 `source` 字符串会变 —— **L4 只改文案不改 name**，所以不会冲突；但你若发现 `house_name` 变了，在报告里点出来。

---

## §5 收工

1. `git status --short` 确认只有那 4 个文件被改（外加临时 `lab/`，**不要 add**）。
2. `git add scripts/main.gd scripts/evidence_store.gd scripts/evidence_archive.gd _mdtest/evidence_archive_check.gd`（**精确 add，绝不 `git add -A`**）。
3. commit：
   ```
   feat(evidence): 证物模型改日期化观察记录（key 加年份、显示名带年份）+ 开档时收紧 SHIFT/E
   ```
4. 另写 `docs/FEEDBACK-evidence-model-exec.md`（≤120 行，中文）：4 项改动逐条改前改后／新条数实测／测试改造清单（哪条断言从几改成几、为什么）／七套回归结果／遗留问题。**单独 `git add` 加进同一个 commit**。
5. 报告（给我的最终回复）：4 项改动逐条（改在哪一行）／**最终证物总条数实测**／新测试断言逐条结果／七套回归逐套关键字／旧存档文件的兼容情况（`EvidenceStore.load()` 读旧格式会不会崩，见下）。

### ⚠️ 旧存档兼容（必须处理）
`scripts/evidence_store.gd` 的 `save()` 写的是 `{"version":1,"entries":[...]}`。旧存档里的条目没有年份维度。
**要求**：`load()` 读到**旧格式**（条目里没有年份字段）时**不能崩**，按「年份未知」兼容（例如 source 里的年份兜底，或显示名后缀留空）。在报告里说明你选了哪种兼容方式。

---

## 依据文档

`docs/DECIDE-a4-a5-layout.md` §7（证物档案影响面）、§11 裁定②③、`docs/PROMPT-evidence-archive-exec.md`（上一版任务书，§0.3 的 key 口径已被本次改判推翻）、`docs/story.md` §7.3（老槐五帧变化）、`scripts/main.gd:96-165`/`:235-282`、`scripts/evidence_store.gd` 全文、`scripts/evidence_archive.gd` 全文。
