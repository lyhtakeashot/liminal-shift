# 反馈：结局线接线（PROMPT-ending-wire-exec）

> 执行时间 2026-11-26 14:46–15:0x｜执行线：结局线（单线）｜**未 push**
> 结论：**归档表已接进主循环，J 调试键已删，三帧书热点可翻《水簿》**。
> 新 check `_mdtest/ending_wire_check.gd` **90 条断言全绿（fails=0）**；`ending_check` / `phasing_check` / `greybox_check` 全绿；
> `evidence_archive_check` **红 1 条，但与本线无关**（原因见 §6.1，另一条线把 `start_frame` 改成了 `a5_2026`）。

---

## 1. 改了哪几个文件、哪几行

白名单三件：`scripts/main.gd`、`data/frames.json`、`_mdtest/ending_wire_check.gd`（新建）。
`ending_form.gd` / `ending_report.gd` / `ending_store.gd` **一字未动**（校验：`git diff --stat` 里没有这三个文件）。

### 1.1 scripts/main.gd（393 → 407 行，+27 / −13）

| 位置（改后行号） | 改动 |
| --- | --- |
| `:22` | 新增 `const EndingForm = preload("res://scripts/ending_form.gd")` |
| `:44-45` | 删 `var _diary_j_down`，换成 `var ending_form: Control = null` + `var _ending_g_down := false` |
| `:81` | `_ready()` 里 `_make_diary()` 之后加 `_make_ending_form()` |
| `:106-112` | 新增 `func _make_ending_form() -> void:`（`EndingForm.new()` / `name = "EndingForm"` / `add_child`），紧跟在 `_make_diary()` 之后 |
| `:96-97` | `_make_diary()` 的注释：删掉「J 是临时调试入口 / frames.json 里还没有书热点 / 加完就删 J」三句，改成「账桌北头柜格那一格在 data/frames.json 里带 `"diary": "mill"`（A1/A2/A3 三帧各一条）」 |
| `:196-202` | J 键整段删除，换成 G 键轮询 + 边沿（`KEY_G`，`ending_form.toggle(tl.current().year)`） |
| `:204-210` | 停世界判断加第三个条件 `or (ending_form != null and ending_form.is_open())`（行尾续行 `\`），注释补一句「归档表自己吃 ↑↓←→ / Tab / Enter / Esc / F」 |

关键顺序（A2/A6 依赖它）：

```
:196  G 键轮询段          ← 必须在停世界 return 之前
:206  if 档案 or 书本 or 归档表 开着 → player.walking=false; HUD 藏; return
```

若把 G 段挪到 return 之后，表一开就再按不掉 G（当时就是这么设计的，写进注释了）。
`_try_open_diary()` 的判定条件**一个字没改**（任务书 §3.3 要求）：仍只看 `h.get("diary") == "mill"`。

### 1.2 data/frames.json（99509 → 102427 字节）

只给三帧的 `hotspots` 数组**各追加一条**（键序 `pos,title,reach,diary,text`，与既有条目一致，追加在数组末尾）：

| 帧 | pos（格中心） | 说明 |
| --- | --- | --- |
| `a1_1926` | `[1328, 496]` | 账房东北角 (3,1) 格，离账桌热点 80px |
| `a2_1951` | `[1392, 496]` | 账房北侧 (5,1) 格，离账桌 / 墙基暗龛 80px |
| `a3_1976` | `[1392, 496]` | 同上 |

三条都是 `{"title": "水簿", "reach": 68, "diary": "mill", "text": "..."}`，文本各按年代口吻写（油纸抄本 / 硬壳账簿 / 一碰掉渣）。

**选点不是拍的**，先用探针（`lab/_ew_probe2.gd`，跑完已删）逐格问 `hotspot_at()` 再定的。依据两条：

1. `frame_data.gd` 的 `hotspot_at()` **取 reach 内最近的一个**（`d <= reach and d < best_d`），而且在 `setup()` 里**家具热点先加入、手写热点后加入** ⇒ 距离相同时家具赢。所以书格必须落在所有 68px 家具盘之外。
2. a2/a3 的「墙基暗龛」在 `[1,1,1,4]`，它那一整列 x=1 被 x=2 的墙封死、玩家站不进去（x=1 只是「看得见摸不着」的暗龛），所以可站的书格只能往东挪到 x=5。

实测（探针输出，三帧一致）：
- `hotspot_at(书格)` → `title=水簿 diary=mill`，`is_free(书格)` = true；
- `hotspot_at(账桌中心)` → 仍是「账桌」（书没抢走家具卡，A7 反向断言就在测这个）；
- 从书格 BFS 能走到屋外（A1 那道门是通的）。

写回姿势：`json.dumps(d, indent=2, ensure_ascii=False)`，**不补末尾换行**（原文件本来没有），写完复查 `dumps(loads(text)) == text` 为 True。

### 1.3 _mdtest/ending_wire_check.gd（新建，569 行，90 条断言）

五组：`_data_checks()`（数据面）、`_source_checks()`（源码面，兜「J 删干净了」）、`_scene_checks()` + `_a2/_a3/_a6`（真场景，G/停世界/J）、`_form_key_checks()`（表内键位）、`_diary_entry_checks()`（三帧翻书）。
收尾打 `ENDING_WIRE_CHECK_DONE fails=%d`，全绿再打 `ENDING_WIRE_OK ...`。

---

## 2. 验收 A1–A9 逐条结果

跑法：`& $g --headless --path . -s res://_mdtest/ending_wire_check.gd`（`$g = D:\steam\...\godot.windows.opt.tools.64.exe`，v4.7.2.stable.steam.ed1daf0bf）。

| 项 | 要求 | 结果 | 证据 |
| --- | --- | --- | --- |
| A1 | 启动无脚本 ERROR | **PASS** | 窗口模式 `--quit-after 120` 起主场景，stderr 只有 `user://logs/...`（2 行，本沙箱 user:// 不可写）+ `Failed to read the root certificate store.` 三条已知无害 ERROR，无 SCRIPT ERROR，退出码 0。另有 4 条断言兜底：`main.ending_form` 非空 / 名字 `EndingForm` / 是 `Control` / 启动时关着（不抢画面） |
| A2 | 按 G 弹表 | **PASS** | 「守卫：裸键注入生效」→「按 G 弹出归档表」→「归档员年份 = 当前帧年代（1926）」→「松手不会误关表（边沿检测，不是按住即切）」→「表开着时再按 G 能关掉」 |
| A3 | 表开着时世界不响应 | **PASS** | 每组前先放**反向对照**：表关着 W 能走 `(64,320)→(64,317.12)`、W 能推帧 `0→1`、SHIFT 能切时代 `1→0`、E 能检视（坝）。再把表打开：W/S/A/D 坐标不变、`player.walking=false`、`tl.index` 不变、`tl.axis` 不变、E 不检视且表不被顶掉 |
| A4 | 表内键位能填格 | **PASS** | ↓ 焦点 0→2、↑ 2→0、→ 把 1926 动机填成「激情」、← 又转回空（不设默认值）、Tab 10→11、Shift+Tab 11→10、Enter 在表格格里 0→1、Esc 关表、F 关表 |
| A5 | 关表后能走 | **PASS** | `(64,320) → (64,317.12)`（在 A3 之前就测了，当 A3 的对照） |
| A6 | 按 J 无反应 | **PASS** | 「按 J 不再翻开双日记 / 不会开归档表 / 不会开证物档案 / 世界不动」，另加源码断言：`main.gd` 里 `KEY_J`、`_diary_j_down` **零命中** |
| A7 | 三帧书旁按 E 翻《水簿》 | **PASS** | 三帧各：站书格注 `inspect` → `diary.is_open()`=true、两页标题 = `假本 · 誊清 / 真本 · 原稿`、HUD 让开、`_try_open_diary()` 返回 true；反向：站账桌中心 `_try_open_diary()` = false |
| A8 | `ending_check` 仍全绿 | **PASS** | `ENDING_CHECK_DONE fails=0` / `ENDING_OK 归档表填格 / 记述三变体 / 两个出口 已验证` |
| A9 | 新 check 覆盖 A2/A3/A6 | **PASS** | 即上表 A2/A3/A6 三行，共 30 条断言；整体 `ENDING_WIRE_CHECK_DONE fails=0`（90 PASS） |

---

## 3. 回归数字

| 套件 | 结果 |
| --- | --- |
| `_mdtest/ending_wire_check.gd`（新） | **fails=0**，90 PASS |
| `_mdtest/ending_check.gd` | **fails=0**（E1–E8 不变） |
| `_mdtest/phasing_check.gd` | **fails=0 warns=0** |
| `_mdtest/greybox_check.gd` | solids **238 / 299 / 379 / 812 / 897**（未变）、`UNEXPLAINED_BLOCKS=0`、`REACH_OK=true`、`HOTSPOTS_OK=true`；各帧 hotspots **10 / 11 / 13 / 12 / 8**（a1/a2/a3 各 +1，就是这次加的书热点） |
| `_mdtest/evidence_archive_check.gd` | **fails=1**，`FAIL A1 磨坊有账桌热点` ⇒ 见 §6.1，**与本线改动无关** |

> ⚠️ greybox 那句断言是 `HOTSPOTS >= 9`（不是 `== 9`），所以 a1 从 9 变 10 不报错，这是**预期**的 +1。
> 顺带印证了上次记下的那条纪律：门槛别写成硬数字，否则加一条热点就红。

---

## 4. 玩家怎么一路打到结局（键位全流程）

1. **走**：WASD。**推时间**：按住 W 到墙边会推帧（时间轴前移，各帧自动换年代色调）。**切时代轴**：SHIFT。
2. **看东西**：走到地标 / 家具 / 院子里按 **E** → 右下出检视文字，同时收进证物档案（`EvidenceStore`，跨启动存 `user://evidence_archive.json`）。**翻证物档案**：**I**（表开着世界停）。
3. **翻书**：《水簿》在磨坊账房「账桌北头柜格」那一格（a1/a2/a3 三帧各一处，**不是**账桌本身那一格 —— 差 80px，别站错）。站上去按 **E** → 双日记对照（假本·誊清 / 真本·原稿）打开，HUD 让开；**E 或 Esc** 合上。这条现在是**正式入口**，J 已经没了。
4. **填归档表**：任意时刻按 **G** → 归档表弹出（表开着世界全停：不能走、不能推帧、不能切时代、不能检视）。
   - **↑ ↓**：同列上下移焦点；**← →**：改当前格的选项（空 → 激情 → 蓄谋 → 放任 → 无 → 空，转圈，不设默认值；故意形态同理）；
   - **Tab / Shift+Tab**：一格一格往后 / 往前平铺；
   - **Enter**：在表格格里 = 递到下一格；在出口格里 = **落定这个出口**（`Exit 0 = 已归档` / `Exit 1 = 存疑`）；
   - **Esc 或 F**：关表。关表会 `EndingStore.save()` 落盘到 `user://ending_form.json`（写不进去退 `res://`）。
5. **记述**：表里填了多少格决定记述变体（`EndingReport`，归档员随帧变：1926 陈阿福 → 1951 陈志强 → 1976 陈卫东 → 2001 陈小军 → 2026 陈浩），两个出口给两段不同文本。
6. 出口一按就落定：**存盘 → 发 `exit_chosen` → 关表**。

---

## 5. 提交范围

只 `git add` 了自己碰的四个文件（`scripts/main.gd`、`data/frames.json`、`_mdtest/ending_wire_check.gd`、本文件），**未 push**。

**`data/frames.json` 是别人的脏文件**（`start_frame` 被改成 `a5_2026`、`start_pos` 被改），所以我没直接 `git add data/frames.json`（那样会把别人的 WIP 一起提交），而是：`git show HEAD:data/frames.json` → 只把我的三条热点加上去 → `git hash-object -w` → `git update-index --cacheinfo`。结果：index 里 = HEAD + 我的三条热点，工作区里别人的 WIP **原样留着**。
验收：`git show <新 commit> -- data/frames.json` 里搜 `a5_2026` / `start_pos` 必须为空。

`_mdtest/ending_wire_check.gd.uid` 是 Godot 自动生成的，仓库里所有 `.gd.uid` 目前都未跟踪，我也没加。

---

## 6. 遗留问题（按要紧程度）

### 6.1 `evidence_archive_check` 现在红的一条，不是本线造成的 ⇒ 需要总策划裁定

```
FAIL A1 磨坊有账桌热点
```

`_mdtest/evidence_archive_check.gd:343` 是 `var f = main.tl.current()` —— **它假设开局在 a1_1926**。基线 `8238eb7` 时这个假设成立（`timeline.gd` 里写死 `index = 0`，`frames.json` 也没有 `start_frame` 键）；现在工作区里另一条线改了 `scripts/timeline.gd`（加 `start_frame` 读取，`d.get("start_frame","")` 找不到就退回最后一帧）并在 `data/frames.json` 里加了 `"start_frame": "a5_2026"`（A5 开局，符合 house-spec 2026-11-19 的拍板）⇒ `tl.current()` 变成 a5，a5 的磨坊早拆了、没有账桌热点 ⇒ 红。**注意：这两处都还没提交**，所以基线本身是绿的，红只出现在当前工作区。

（顺带说明：那条线即使只加 `timeline.gd` 的读取逻辑、不加 `frames.json` 的键，`start_frame` 取空串也会走「退回最后一帧」⇒ 同样落在 a5。所以红是「开局改 A5」这个决定带来的，不是数据写错。）

证据（临时探针，跑完已删）：
```
PROBE 开局 tl.index=4 id=a5_2026 year=2026
PROBE 回 a1 tl.index=0 id=a1_1926 year=1926 hotspots=10
PROBE 找到账桌热点=true title=账桌 pos=(1264.0, 544.0)
PROBE 检视后 cards=1 obs=1 归一键=true
```
即：**回到 a1 后这条路径完全正常**，只是那个 check 少了一句 `tl.index = 0`。它不在本线白名单里，我没动它。建议：给 `evidence_archive_check.gd:343` 前补 `main.tl.index = 0`（和它第 408/455/530 行的写法一致）。

### 6.2 出口信号没人接

`ending_form.gd:243` 发 `exit_chosen(choice)`，全仓库 **零监听者**（`grep -n exit_chosen scripts/*.gd` 只有定义和这一句 emit）。也就是说现在选了出口 = 存盘 + 关表 + 什么演出都不发生。任务书 §1 的白名单不含「出口后干吗」，所以我没接。下一步要么在主循环里连 `exit_chosen`（放结尾演出 / 结算画面），要么明确「存储态为主、演出后补」。

### 6.3 `ending_check` 的一行 `ERROR: Parse JSON failed ... line 0`

这是**它自己的负向用例**（`_mdtest/ending_check.gd:443` 的注释写着「引擎自己会打一行 Parse JSON failed ERROR —— 那是本用例故意喂进去的，不是失败」），不是回归问题，写在这里免得下一位误判。

### 6.4 存档写在 `user://`，本沙箱读不到也写不进

`EndingStore` 的落盘链是 `user://ending_form.json` → `res://ending_form.json`。本机沙箱下 `user://` 写不进去（同一轮里 `user://logs/godot.log` 也报 `Failed to open log file for writing`），所以**本线所有测试的「填表→关表→重开还在吗」都没真验到跨进程持久化**（`ending_check` 自己也是内存态验证）。普通玩家机器上 `user://` 可写，不受影响；真想验就在自己机器上手动开一次表、填两格、关表、重启游戏再按 G 看还在不在。

### 6.5 书热点之后会被家具改造牵连

三条书热点的坐标是**写死在 frames.json 里的绝对像素**，而磨坊的家具热点是 `house_shape.gd` 按 `house.pos + 家具矩形中心` **算出来**的。这次两者间距 80px（> reach 68）所以稳。以后若有人动了磨坊的 `pos`、挪了「账桌」的 rect、或把账房隔墙改了位置，书热点就可能被家具卡抢走，或者干脆悬在墙里。`ending_wire_check` 的 W 组就是拦这个的：它验 `hotspot_at(书格) == 水簿` **且** `is_free(书格)` **且** `hotspot_at(账桌中心) == 账桌`，改坏了会红。**改磨坊布局的人请顺手跑一次这个 check。**

### 6.6 任务书里的行号已经漂了

任务书说 `main.gd` 的 `:21` / `:43` / `:78` / `:185-190` / `:196`，实际改之前是 `:22` 对应位、`:41-42`、`:78`、`:185-190`（这段是对的）、`:196`。改完是 407 行（不是任务书说的 470）。本文件 §1.1 用的是**改后行号**，后续引用请以 `grep -n` 为准。