# 界碑删除线 · 撤掉周界石碑与其全部配套 执行提示词

> 用户 2026-11-26 原话：「**界碑删掉吧，本来也没留有多少和它相关的有用剧情。**」
> 这条线把界碑从**数据、引擎、测试、叙事、美术清单**五个层面彻底撤掉，不留半截。

---

## §0 开工前

### §0.1 路径与工具

- 仓库根：`D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift`
- Godot（**不在 PATH**，必须用全路径）：`D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe`
- 跑回归的正确姿势（**看关键字，不看退出码**）：

```powershell
& "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe" --headless --path . -s res://_mdtest/evidence_archive_check.gd 2>&1 | Select-Object -Last 45
```

- 沙箱固有噪声（**不是错误**）：`Failed to read the root certificate store.`、`Failed to open 'user://logs/godot...log'`。
- 🔴 **不要用 `cmd /c`（路径有空格会被截断）；不要用 `> file` 重定向（会产出 0 字节文件）。**

### §0.2 HEAD 下限与版本自检

- HEAD 必须 **≥ `4e10958`**（＝四份新任务书落盘那笔）。
- 🔴 **版本自检**：确认本文件 §2.3 有「删除后的 §7.2 清单」和 §2.4 有「§7.4 改写方案」。
  拿不到这两节 ⇒ **你拿到的是旧任务书，停下报告**。

### §0.3 开工前必须先跑一遍基线（七套回归）

依次跑 `_mdtest/` 下七套，把输出存进 `lab/_stele_baseline.txt`（未入库，可留）：

```
asset_draw / camera / display / evidence_archive / greybox / hud_layout / sort
```

**基线里必须有这几个数字**：

| 项 | 基线值 | 本线之后 |
|---|---|---|
| 证物卡 / 观察 | `25` 卡 / `56` 观察 | **`24` 卡 / `51` 观察**（界碑＝1 卡 / 5 观察） |
| a1–a5 solids/hotspots | a1 239/10、a2 300/11、a3 380/13、a4 646/13、a5 898/9 | **每帧各减 1 个 hotspot**（a4 若已被 A4 重排线重排过，则按重排后的值减 1） |
| `REACH_MAP.standable` / `to_a5` | `15104` / `12863` | 变了要解释（界碑是 `solid:true` 的小件，删掉后那一格会变可站） |
| `UNEXPLAINED_BLOCKS` | `0` | `0` |
| `A1_WELL_FREE` | `false` | `false` |
| `WALL_BLOCKED` | `true` | `true` |
| `TIME_FWD_REACHED` | `[1,2,3,4]` | `[1,2,3,4]` |

🔴 证物基线 **`24` / `51`** 是本线的核心数字：界碑是**一张卡、五个年代各一条观察**（A1–A5 五帧各有一个界碑热点）。
删掉后就是 25−1＝24 卡、56−5＝51 观察。**实测必须对上**；对不上说明漏删或多删了。

### §0.4 脏工作区纪律（**本条最容易出事**）

工作区长期是脏的，**这些不是你的**：

- `M _ref/art/A1_1926/*.png`、`A2_1926/*.png`、`A3_1976/*.png` —— 美术线的改动。
- `D 美术资产/**` 一批 —— 用户自己删的。
- 大量未跟踪的 `lab/_*`、`.import`、`docs/FEEDBACK-*`。

规矩：

1. **只精确 `git add <你的文件>`，绝不 `git add -A`、绝不 `git add .`。**
2. **不许 `git checkout -- <file>`**（沙箱 CC Safety Net 会拦这条规则）；要还原文件用 `git show HEAD:<path>` 按字节写回。
3. `git status --short` 里出现你以外的脏文件 ⇒ **不要碰、不要提交、不要"顺手清理"**。
4. **不许删 `_ref/art/**` 或 `assets/**` 里的图片文件**（美术同学的东西）。图片只**从清单和引用里移除**，磁盘文件留着。

### §0.5 本线要碰的文件（**允许改**）

| 文件 | 改什么 |
|---|---|
| `data/frames.json` | **只删界碑**：五帧里的 `label`「碑」的 rect shape、`title`「界碑」的 hotspot。**其余一个字不许动**（含 `world`/`start_pos`/`safe_*`/其它 shape 的数值）。若 A4 重排线已落地，`a4_2001` 帧按**重排后的**内容删。 |
| `scripts/asset_draw.gd` | 删 `SHARED_SCENE` 里的 `"stele"` 条目（`:45`），改 `:164` 的 kind 注释 |
| `scripts/world_view.gd` | 删 `:15`、`:240`、`:775`、`:836-837`（`label.find("碑")` 分支）里的界碑相关文字与贴图分支；`:290` 的 `label == "碑"` 跳过条件改成只剩 `label == "坝"` |
| `scripts/house_shape.gd` | 改 `:122-124` 的过期注释（写着「A5 那块碑由 frames.json 的世界地标承担」，现在碑没了） |
| `_mdtest/evidence_archive_check.gd` | 改 `:528-541` 的界碑断言（改成用另一个地标热点做 E 检视入档测试） |
| `_mdtest/asset_draw_check.gd` | `:212` 的 kind 列表去掉 `"stele"` |
| `_mdtest/greybox_check.gd` | `:324` 注释里的「界碑」字样（纯注释） |
| `docs/story.md` | §7.2 清单、§7.4 周家的地、留白、物证表（见 §2.3 / §2.4） |
| `docs/ART-GAP-A4A5.md` | `:127-131` 的 `stele_a1..a5` 五行、`:442-443` 的「五帧共用一张」条目、`:97` 的括号说明 ⇒ 标作废 |
| `docs/ART-HANDOFF-a4a5.md` | `:71-75` 的 `stele_a1..a5` 五行 ⇒ 标作废 |
| `docs/art-assets-a1a3.md` | `:16`、`:23`、`:312`、`:320`、`:328` 的界碑字样 ⇒ 标作废/注明 |
| `_ref/art/_assets_a1a3/_a1a3_assets.json` | 三条 `stele` 条目（`:3050`/`:3162`/`:3274`）⇒ 移除 |
| `docs/FEEDBACK-stele-removal-exec.md` | 新建，≤120 行，见 §5.3 |
| `docs/PROMPT-overseer.md` | 只改「界碑删除线」那一行状态 |
| `docs/待解决事项.md` | 只改 §4 表里界碑删除线那一行 ＋ 新增一条裁定 |

### §0.6 本线**不许碰**的文件

- `_ref/houses/houses_data.json` —— 界碑**从来不是家具**（L3 早已把 school 的「「周」界碑」家具撤掉），本线不改任何房屋数据。
- `scripts/evidence_store.gd` / `scripts/evidence_archive.gd` / `scripts/main.gd` —— **证物系统一行不改**（界碑卡是数据驱动的，删掉热点就没有了）。
- `scripts/timeline.gd` / `scripts/player.gd` / `scripts/hud.gd` / `scripts/frame_data.gd` —— 不动。
- `scripts/main.gd`、`scripts/world_view.gd` 的**非界碑部分** —— 不动。
- `assets/**`、`_ref/art/**` 里的**图片文件** —— 不删（美术线的东西）。
- `docs/HANDOFF.md` / `docs/HANDOFF-VILLAGE.md` / `docs/DECIDE-a4-a5-layout.md` —— **历史留档，不改写**（只在新反馈文档里说明「界碑已作废」）。
- `docs/npc.md` —— 实测零命中界碑，**不用改**（若发现漏网，报告，不要自己改）。

### §0.7 串行提醒（本线会撞人）

- `data/frames.json` 是**全局单写者文件**。
  - 与 **A4 重排线**的关系：两条线都写 frames.json，但**各写各的帧**（本线删五帧里的界碑、A4 重排线整体替换 `a4_2001`）。
    ⇒ **允许并行，但必须落盘错开**：任何时刻只允许一条线在改这个文件；
    改完立刻 `git diff -- data/frames.json` 自检，确认**只有自己那几帧变了**；**不要在对方正在改的时候动同一个文件**。
  - 若 A4 重排线**尚未落地**，本线照现在的 `a4_2001` 内容删界碑即可；A4 重排线随后整体替换该帧，界碑自然不会回来。
- 本线**不碰 `scripts/world_view.gd` 的世界视图逻辑**（只删界碑那一小段）⇒ 与 L17（phasing）撞同一文件，**必须串行**（见 §4.4）。

---

## §1 独占写入文件

**本线独占（其它线不许同时写）：**

1. `data/frames.json` 里**界碑相关的 shape/hotspot 条目**
2. `docs/FEEDBACK-stele-removal-exec.md`
3. `_ref/art/_assets_a1a3/_a1a3_assets.json` 的三条 `stele` 条目

**本线只读不写：**

- `scripts/evidence_store.gd`（确认 `landmark_key` 的「·」切分规则不受影响）
- `docs/story.md` 的其它章节（只按 §2.3/§2.4 指定的位置改）

---

## §2 数据基准

### §2.1 界碑在代码与数据里的全部落点（**已逐处实测，这是完整清单**）

**数据（`data/frames.json`）**：五帧各有一个 rect shape（`label`「碑」，16×32，`solid:true`）＋ 一个 hotspot（`title`「界碑」）。

| 帧 | rect | hotspot pos / reach |
|---|---|---|
| a1_1926 | `[1856,960,16,32]` | `(1864,976)` / 68 |
| a2_1951 | `[1856,960,16,32]` | `(1864,976)` / 68 |
| a3_1976 | `[1856,960,16,32]` | `(1864,976)` / 68 |
| a4_2001 | `[2880,960,16,32]` | `(2888,976)` / 68 |
| a5_2026 | `[608,2496,16,32]`（L14 落地后） | `(616,2512)` / 68 |

⚠️ A1–A4 的旧坐标是 3200×2400 旧世界；**A4 若已被 A4 重排线重排过，坐标会变** ⇒ **以开工时 `data/frames.json` 的实际值为准**，不要照抄本表。

**引擎**：
- `scripts/asset_draw.gd:45` `SHARED_SCENE` 里的 `"stele": "assets/village/scene/stele.png"`（五帧共用一张图）
- `scripts/asset_draw.gd:164` kind 注释：`kind ∈ road/field/river/well/tree/dam/stele`
- `scripts/world_view.gd:836-837` `if label.find("碑") >= 0: return AssetDraw.scene_tex(frame_id, "stele")`
- `scripts/world_view.gd:290` `if label == "坝" or label == "碑":`（`_scene_bboxes()` 里跳过这两类小件，界碑不该占田图/路图 bbox）
- `scripts/world_view.gd:15`、`:240`、`:775` 三处注释提到碑
- `scripts/house_shape.gd:122-124` 过期注释（「A5 那块碑现在由 data/frames.json 的世界地标承担」）

**测试**：
- `_mdtest/evidence_archive_check.gd:528-541`：**用界碑做「移动到热点位置 → E 检视 → 入档 → 观察数 +1」的测试**
- `_mdtest/asset_draw_check.gd:212` kind 列表含 `"stele"`；`:214` 断言每帧每 kind 都有图
- `_mdtest/greybox_check.gd:324` 注释提到界碑

**资产清单**：
- `_ref/art/_assets_a1a3/_a1a3_assets.json:3050/:3162/:3274` 三条 `stele`
- `docs/art-assets-a1a3.md:16/:23/:312/:320/:328`
- `docs/ART-GAP-A4A5.md:127-131`（`stele_a1..a5` 五张交付规格）、`:442-443`、`:97`
- `docs/ART-HANDOFF-a4a5.md:71-75`
- `_ref/art/gen/_gen_scene.py:10/:160/:465`（`gen_stele()`）与 `_ref/houses/gen_asset_breakdown.py:351` —— **生成器代码不跑、不改**（改了会重生成别的资产）；只在清单里标注「stele 已作废」。

**叙事（`docs/story.md`）**：`:438`、`:472`、`:474`、`:478`、`:479`、`:481`、`:484`、`:500`、`:501`、`:502`、`:612`、`:962`。

### §2.2 删掉后的证物账（**核心数字**）

- 界碑＝**1 张卡 / 5 条观察**（`landmark_key` 取 title 第一个「·」前的主体名，五帧 title 都是「界碑」⇒ 归一到同一张卡）。
- 25 卡 / 56 观察 ⇒ **24 卡 / 51 观察**。
- 删除后**仍存在**的地标卡：老井、老槐、坝、田（各 5 年）＋ 超市工地（1 年）＝ 5 张地标卡；家具卡 19 张。
  ⇒ 24 = 19 + 5 ✅。

### §2.3 `docs/story.md` 改写清单（**逐条改，别凭印象**）

| 位置 | 现状 | 改法 |
|---|---|---|
| `:438` | §7.2 第 3 条「一块旧界碑，嵌在小学围墙里，字磨掉一半，只能认出一个「周」。」 | **整条删掉**，后面的条目（磨盘、玩具店招牌）序号依次前移 ⇒ §7.2 从 **5 条变 4 条** |
| `:442-443` | 「**第 1 和第 2 条是钥匙。**」 | **不动**（删的是第 3 条，前两条序号不变 ⇒ 这句仍成立） |
| `:472-487` | §7.4「**① 界碑**」整节（含三次挪位剧情 `:478/:479/:481`、玩家能自己发现 `:484`） | **整节删掉**；下面「**② 土地登记表的前手栏**」的序号要改成「**①**」，「**③ 周有田账本的纸**」→「**②**」，「**④ 名字**」→「**③**」；节内「#### 四条线索（全部来自现有物件）」→「#### 三条线索（全部来自现有物件）」 |
| `:487` | 「**交付成本：一行检视文本。**」 | 随 ① 整节删掉 |
| `:500-504` | 「**关键：这一行和界碑必须分开放。** 单独看界碑……两样放在一起，才知道石头说的地和表上卖的地是同一块。」＋「这正是附三纪律 ③ 的做法：真相靠**两件东西并排**」 | **改写**：删掉「和界碑」这层并排，改成「这一行和**别的证据**必须分开放」式的表述 —— 但**具体措辞由你拟、两处都必须点在反馈文档里请总策划定**。⚠️ 这一段是 §7.4「第四层」的方法论支点，**不许简单删掉整段**（那会把「周家的地」这一层拆散） |
| `:612` | §9 留白「**周家曾经是这块地的主人。** 只有一块界碑（「周界」）、登记表上一行前手栏。」 | 改成只留「登记表上一行前手栏」这一条（**具体措辞拟好待确认**） |
| `:962` | 物证表「| 字磨掉一半的界碑 | 第二次「身份反转」 |」 | **整行删掉**（左列是可用的物理证据清单，界碑没了就不该占位） |
| `:494` | 登记表前手栏「原业主 周氏 光绪二十六年 立契」 | **不动** —— 这是界碑删掉之后「周家曾拥有这块地」的**唯一**物证 |

🔴 **写清「四层」还剩几层**：§7.4 标题是「周家的地（第四层，最深的一层）」。
界碑删掉后这一层**只剩登记表一行 + 账本 + 名字**。标题里的「第四层」是相对 §7.1/§7.2/§7.3 的编号，**不要改**；
但如果执行中发现「第四层」在方法论上站不住，**写进反馈文档请示，不要自己改**。

### §2.4 引擎改法（**最小改动**）

1. `scripts/asset_draw.gd`：删 `SHARED_SCENE` 的 `"stele"` 一行；`:164` 注释里的 kind 列表去掉 `stele`。
   ⚠️ **不许动 `SCENE_FILES`**（a1/a2/a3 的场景图清单与界碑无关）。
2. `scripts/world_view.gd`：
   - 删 `:836-837` 的 `if label.find("碑") >= 0: return ...` 分支（连同它的 `return` 之后那行一起处理干净，**别留下语法残渣**）。
   - `:290` 的 `if label == "坝" or label == "碑":` → 改成 `if label == "坝":`。
   - `:15`、`:240`、`:775` 三处注释里的「碑」字去掉或改写。
   - ⚠️ **不许动 `_collect_front` / `_draw_front` / 排序链 / `set_player_state` / 时间轴三遍色差**（`:167-174`）—— 那是 L17 的地盘。
3. `scripts/house_shape.gd`：`:122-124` 注释改写（说清「界碑已于 2026-11-26 删除，school 不挂界碑家具」）。

### §2.5 测试改法（**不许为了保绿灯去改断言的语义**）

- `_mdtest/evidence_archive_check.gd:528-541`：那段是「找一个**地标**热点 → 把玩家挪过去 → E 检视 → 断言观察数 +1」。
  **改法**：把找的目标从 `title == "界碑"` 换成**另一个仍存在的地标**（推荐 `title` 以「老井」开头的那个，或「坝」）。
  ⇒ 断言的**语义保持不变**（地标热点可检视、可入档、观察数 +1），**只是换了一个测点**。
- `_mdtest/asset_draw_check.gd:212`：kind 列表去掉 `"stele"`；`:214` 的「每帧每 kind 都有图」随之少查一个。
  ⚠️ 注意：`:216` 的 `scene_tex("a4_2001","river") == null` 断言**不许动**。
- `_mdtest/greybox_check.gd:324`：纯注释，去掉「界碑」二字即可。

---

## §3 必改清单

### §3.1 第一件：数据（`data/frames.json`）

1. 五帧里删掉 `label` 为「碑」的 rect shape（**注意 `label` 可能是「碑」或含「碑」的其它写法，以实际数据为准**）。
2. 五帧里删掉 `title` 为「界碑」的 hotspot。
3. **只删这两类**，其余 shape/hotspot（连同 `text`、`reach`）**一字不许动**。
4. 改完立刻自检：

```powershell
git diff -- data/frames.json
```

⇒ diff 里**只应出现**被删掉的行，**不许出现**任何其它数值变化。

### §3.2 第二件：引擎（三个文件）

按 §2.4 做，**最小改动**。

### §3.3 第三件：测试（三个文件）

按 §2.5 做。

### §3.4 第四件：叙事（`docs/story.md`）

按 §2.3 做。**两处措辞（`:500-504`、`:612`）必须把拟用文案写进反馈文档请总策划定。**

### §3.5 第五件：资产清单（四个文件）

- `_ref/art/_assets_a1a3/_a1a3_assets.json`：删三条 `stele` 条目。
  ⚠️ 改这个 JSON **必须用 Python 按字节读写**（它带中文与缩进，PowerShell 重定向会写坏 UTF-8）。
- `docs/art-assets-a1a3.md`：`:16`、`:23` 的清单里去掉界碑；`:312/:320/:328` 三行标作废。
- `docs/ART-GAP-A4A5.md`：`:127-131` 五行标作废（**这五张是已经发给美术同学的清单里的一部分** ⇒ 反馈文档必须提醒「要跟美术同学说一声，这五张不做了」）；`:442-443`、`:97` 同步。
- `docs/ART-HANDOFF-a4a5.md`：`:71-75` 五行标作废。

### §3.6 第六件：文档

- `docs/PROMPT-overseer.md`：只改「界碑删除线」那一行状态。
- `docs/待解决事项.md`：§4 表里界碑删除线那一行 ＋ **新增一条裁定**「界碑已删除（用户 2026-11-26）」。
- **不要改** `docs/HANDOFF.md` / `docs/HANDOFF-VILLAGE.md` / `docs/DECIDE-a4-a5-layout.md`（历史留档）。

---

## §4 验收

### §4.1 数据自检

- `data/frames.json` 里 grep「碑」**零命中**（shape 的 `label` 与 hotspot 的 `title`/`text` 都要查）。
- 五帧 shapes / hotspots 计数各减 1。
- `git diff -- data/frames.json` 只含删除行。

### §4.2 证物基线

- 跑 `_mdtest/evidence_archive_check.gd`：**证物卡 24 / 观察 51**（用 `EvidenceStore.count()` / `observation_count()` 断言或独立复算，**都要做**）。
- 界碑卡在 `user://evidence_archive.json` 旧存档里可能残留 ⇒ **旧存档兼容**：加载时把已不存在的 key 忽略掉（**若 `evidence_store.gd` 现在的加载逻辑不会崩，本线不改它**，只在反馈文档里说明「旧存档里的界碑卡会被忽略」）。

### §4.3 七套回归

七套全跑，贴进反馈文档。必须给出前后对照（对照项见 §0.3）。
`UNEXPLAINED_BLOCKS=0` / `A1_WELL_FREE=false` / `WALL_BLOCKED=true` / `TIME_FWD_REACHED=[1,2,3,4]` **不许变**。

### §4.4 与别的线的串行检查

- 若 L17（phasing）**正在跑** ⇒ 本线对 `scripts/world_view.gd` 的改动**必须等 L17 交付后再动**（两边都碰这个文件）。
- 若 A4 重排线**正在跑** ⇒ 本线改 `data/frames.json` 的 a4 帧要**错开落盘**，且**不许同时改这个文件**。
- 这两条检查的结果**必须写进反馈文档**（开工时 HEAD 是谁、有没有别的线在跑）。

### §4.5 实机验证（沙箱里做不了窗口，**必须真机做**）

1. 五帧各走一遍，E 检视所有热点 ⇒ **没有任何热点提到碑**。
2. 开证物档案（I）⇒ **没有「界碑」那张卡**；其余卡正常。
3. 主路走一圈，**没有任何地方出现半截石碑**（贴图入口已删，磁盘上的 `stele.png` 还在但不该被加载）。
4. 旧存档（`user://evidence_archive.json` 里还有界碑卡）启动 ⇒ **不崩**，界碑卡被忽略。

### §4.6 grep 零命中清单

- `data/frames.json`：grep `碑` ⇒ **0**
- `scripts/`：grep `stele` ⇒ **0**；grep `界碑` ⇒ 只允许出现在**注释**里（本线要清掉，但若某处注释必须提到历史（如 `house_shape.gd` 注明「界碑已删除」），**在反馈文档里列出并说明**）
- `_mdtest/`：grep `界碑` ⇒ 只允许注释
- `docs/story.md`：grep `界碑` / `周界` ⇒ **0**（叙事里界碑彻底没了）
- `_ref/art/_assets_a1a3/_a1a3_assets.json`：grep `stele` ⇒ **0**

---

## §5 收工

### §5.1 精确 add（**绝不 `git add -A`**）

```powershell
git add data/frames.json
git add scripts/asset_draw.gd
git add scripts/world_view.gd
git add scripts/house_shape.gd
git add _mdtest/evidence_archive_check.gd
git add _mdtest/asset_draw_check.gd
git add _mdtest/greybox_check.gd
git add docs/story.md
git add docs/art-assets-a1a3.md
git add docs/ART-GAP-A4A5.md
git add docs/ART-HANDOFF-a4a5.md
git add _ref/art/_assets_a1a3/_a1a3_assets.json
git add docs/FEEDBACK-stele-removal-exec.md
git add docs/PROMPT-overseer.md
git add docs/待解决事项.md
git status --short          # 确认没有别人的脏文件被带进来
```

### §5.2 commit

```powershell
git commit -m "feat(story): 删除界碑（用户 2026-11-26 拍板）——撤掉五帧数据/引擎贴图入口/测试断言/叙事与资产清单"
```

一次提交即可（数据 + 引擎 + 测试 + 文档同批，因为它们是同一件事）。

### §5.3 反馈文档 `docs/FEEDBACK-stele-removal-exec.md`（≤120 行）必须包含

1. HEAD 基线与开工 HEAD；开工时 L17 / A4 重排线在不在跑。
2. 删掉的数据条目清单（五帧 rect + hotspot 的实际坐标）。
3. **证物基线实测**：24 卡 / 51 观察（怎么算的）。
4. 引擎三处改动的 before/after 摘要。
5. 测试两处改动的 before/after 摘要（断言语义没变，只是换了测点）。
6. `docs/story.md` 改写清单（逐条：位置 + 改前 + 改后）＋ **两处待总策划拍板的拟用文案**（`:500-504`、`:612`）。
7. 资产清单四处改动的摘要 ＋ **提醒总策划去跟美术同学说「stele_a1..a5 五张不做了」**。
8. 七套回归输出 + §0.3 的前后对照表 + 每处变化的解释。
9. 实机验证结果（§4.5 五条）。
10. 仍然存在的缺口（磁盘上的 `stele.png` 留着没删；`gen_stele()` 生成器代码没动；历史留档文档里的界碑字样保留）。

---

## §6 边界提醒

1. **只删界碑，别顺手做别的**（删贴图文件、改生成器、重排地图都不许）。
2. **叙事不许大改**：`:500-504`、`:612` 两处只许「拟稿待确认」，不许自己定稿。
3. **不许改证物系统**（`evidence_store.gd` / `evidence_archive.gd` / `main.gd`）—— 界碑卡会自己消失。
4. **不许改 `_ref/houses/houses_data.json`**。
5. **不许删磁盘上的图片**（`assets/village/scene/stele.png` 留着；美术线的东西）。
6. **不许改 `_ref/art/gen/*.py` / `_ref/houses/gen_asset_breakdown.py`**（生成器代码留着，只在清单里标作废；**绝不运行生成器**——它会覆盖别的美术线资产）。
7. **不许改历史留档文档**（`docs/HANDOFF*.md`、`docs/DECIDE-a4-a5-layout.md`、各 `docs/FEEDBACK-*.md`、`docs/RESUME-*.md`）。
8. **不许动 `scripts/world_view.gd` 的排序链 / 时间轴色差 / `set_player_state`**（L17 的地盘）。
9. **只精确 `git add`**，绝不 `git add -A`，绝不 `git checkout --`。
10. **与 L17（phasing）串行**：本线碰 `scripts/world_view.gd`，L17 也碰 ⇒ 同时只允许一条线在改它。
11. **与 A4 重排线错开落盘**：两条线都写 `data/frames.json`，各写各的帧，不许同时动同一个文件。

---

## §附 依据

| 依据 | 位置 |
|---|---|
| 用户拍板「界碑删掉吧，本来也没留有多少和它相关的有用剧情」 | 2026-11-26（见本文件引言） |
| 界碑的全部代码/数据落点（逐处实测清单） | 本文件 §2.1 |
| 证物归一规则（界碑＝1 卡 5 观察） | `scripts/evidence_store.gd`（`landmark_key` 取 title 第一个「·」前的主体名） |
| 证物基线 25 卡 / 56 观察 | `docs/FEEDBACK-clue-texts-year-exec.md:51/:88`（历史留档，不改） |
| 界碑在叙事里的作用（§7.2 / §7.4） | `docs/story.md:431-444`、`:453-504`、`:612`、`:957-965` |
| 美术清单里要作废的五张 | `docs/ART-GAP-A4A5.md:127-131`、`docs/ART-HANDOFF-a4a5.md:71-75` |
| 引擎贴图入口 | `scripts/asset_draw.gd:43-46/:164-171`、`scripts/world_view.gd:290/:836-837` |
| 测试断言 | `_mdtest/evidence_archive_check.gd:528-541`、`_mdtest/asset_draw_check.gd:212-216` |
| 排线与写者锁 | `docs/PROMPT-overseer.md` §四/§十一 |
