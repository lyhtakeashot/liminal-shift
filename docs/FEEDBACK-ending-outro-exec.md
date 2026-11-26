# 反馈 · L19 结局收束（落定出口后的黑幕）

> 执行线交付于 2026-11-26，任务书 `docs/PROMPT-ending-outro-exec.md`。
> **结论：O1–O8 全部通过。** `_mdtest/ending_outro_check.gd` 窗口模式 `checks=71 fails=0`、headless `checks=57 fails=0`；黑幕铺满实机 781 ms（设计 800 ms）、淡出实测 1000 ms（设计 1000 ms）；三行字逐像素验过（黑幕中心亮度 0.456 → 0.126，降 72%）。
> 需转达 3 项（§3 第 2 行的取法与丙变体那句的读感 / §7 请求为「黑幕落定」补一条音效 / §7 沙箱 `user://` 只读会让旧套件假红），需人眼复核 1 项（§5 截图）。

---

## §1 交付清单与守约

| 文件 | 状态 | 行数 | 说明 |
|---|---|---|---|
| `scripts/ending_outro.gd` | 新建 | 298 | 收束层（黑幕 + 三行字 + 任意键 + 暂停兜底） |
| `scripts/main.gd` | 改 5 处 | 499（`+16 / −1`） | 只动任务书 §5 点的五处，见下表 |
| `_mdtest/ending_outro_check.gd` | 新建 | 483 | O0–O8 全覆盖 + 窗口像素采样 + 三变体断言 |
| `docs/FEEDBACK-ending-outro-exec.md` | 新建 | — | 本文件 |

`git diff --stat scripts/main.gd` = `17 ++++++++++++++++-`，**恰好 5 个位置**：

| # | 位置 | 改动 |
|---|---|---|
| 1 | preload 区（紧邻 `const EndingForm`） | `const EndingOutro = preload("res://scripts/ending_outro.gd")` |
| 2 | 状态区（`var _ending_g_down` 之后） | `var outro: Control = null` |
| 3 | `_ready()` | `_make_ending_form()` 之后加一行 `_make_outro()` |
| 4 | `_make_ending_form()` 之后 | 新增 `func _make_outro()`：`new()` → `name = "EndingOutro"` → `add_child` → `ending_form.exit_chosen.connect(Callable(outro, "play"))` |
| 5 | 停世界那条 early-return | 条件加第三行 `or (outro != null and bool(outro.call("is_playing")))` |

**没有碰**：`ending_form.gd` / `ending_report.gd` / `ending_store.gd` / `world_view.gd` / `player.gd` / `hud.gd` / `frame_data.gd` / `timeline.gd` / `data/**` / `scenes/**` / `assets/**` / `project.godot` / 其它 docs。**没有新增任何 InputMap action**（「任意键」走 `_input` 的裸事件）。

两处与任务书字面不同的实现（都是 GDScript 静态类型逼出来的，行为一致）：

1. 任务书 §5.4 写 `ending_form.exit_chosen.connect(...)`，信号参数名实际是 **`choice: String`**（不是 `exit_key`），`play()` 的签名按 `choice` 走。
2. 任务书 §5.5 写 `outro.is_playing()`；但 `outro` 声明为 `Control`，静态类型上没有该方法，直接写会编译不过。改成 `bool(outro.call("is_playing"))`（同一语义，运行时派发）。`_make_outro()` 里的 connect 同理用 `Callable(outro, "play")`。

---

## §2 O1–O8 验收结果

| # | 断言 | 实测 | 判定 |
|---|---|---|---|
| O1 | 落定后 1s 内黑幕出现（中心像素亮度降 ≥50%） | 铺满 `alpha=0.82`；中心亮度 **0.456 → 0.126（降 72%）**；截图 `lab/_l19_outro_o1_black.png` | ✅ |
| O2 | 收束文字 == `ending_report` 对应变体正文的一段 | 甲乙丙三变体各 8 条断言全过（第 2 行逐字 `body.contains`，见 §3） | ✅ |
| O3 | 收束期间 `walking == false` 且 WASD 不改 `char_pos` | `walking=false`；按 W 前后坐标 `(64.0, 317.12)` 不动（前置对照：`(64.0, 320.0) → (64.0, 317.12)`）；`tree.paused=true`、`main.can_process=false` | ✅ |
| O4 | 按键后黑幕消失（中心像素回 ±10%） | 按 Esc → 淡出 → 中心亮度回到 **0.456**（基准 0.456，偏差 0%）；截图 `lab/_l19_outro_o4_clear.png` | ✅ |
| O5 | 收束后 `open_form()` 仍可调、`is_open()` 正确翻转 | 开 / 关 / `toggle` / 二次落定全部正常，第二次收束也干净收场 | ✅ |
| O6 | 存档收束前后都存在且内容不同 | `user://ending_form.json` 308 → 311 字节，内容差异里带着刚落的「已归档」 | ✅ |
| O7 | `--quit-after 120` 无 SCRIPT ERROR | 无 SCRIPT ERROR（只有沙箱本机的 `user://logs` / 根证书两条环境 ERROR） | ✅ |
| O8 | `ending_check` / `ending_wire_check` / `greybox_check` | `fails=0` / `fails=0` / solids·hotspots·standable·REACH_OK·UNEXPLAINED 全与基线一致；`WALL_BLOCKED` 有一处**既有**偏差（非本线引入，见 §6） | ✅ |

额外补了任务书没要求的四类断言（都在同一个测试文件里）：

- **O0 接线**：收束层是 `Main` 的最后一个孩子（画在表 / HUD 之上）、启动时是空的、`exit_chosen → play()` 真连上了、**认不出的出口字不放黑幕**（`play()` 返回 false 且状态不变）。
- **O1b 实机时长**：让引擎按真实帧率自己跑（不手动驱动），黑幕 **781 ms**、淡出 **1000 ms**、铺满时 `alpha=0.82`。
- **暂停的正当性**：`O3 收束期间整棵树被暂停（G / I / F11 的轮询段全在停世界 return 之前，只能靠暂停挡）`——这条是我加的，见 §4.3。
- **一次落定只收一次**：收束中再 `play()` 被拒，且不打断正在放的那次；收束结束后重开表再落定可以照常再来一遍（任务书 §3.6 允许）。

---

## §3 第 2 行到底取了哪一段（任务书 §7 的问题）

**取法：`EndingReport.build()` 返回的 `prose` 数组里最后一条非空行。** 只做 `strip_edges()` 与超长截断（60 字，见 §8.2），**一个字都没有改写**。

| 变体 | 第 2 行实际字符串 | 字数 | 在 `ending_report.gd` 里的位置 |
|---|---|---|---|
| 甲（1951 = 债务纠纷，四单选都填了确定值） | `没有人被平反。因为没有人是无辜的。` | 17 | `_build_jia` 最后一行（`out.append("没有人被平反。因为没有人是无辜的。")`） |
| 乙（1951 = 杀人灭口） | `死者陆敬之，男，二十四岁。` | 13 | `_build_yi` 最后一行 |
| 丙（有格「无法确定」/ 没填，降级） | `埋葬人数：无法确定。` | 10 | `_build_bing` 最后一栏（`埋葬人数：%s。`） |

**为什么取末行，而不是前三行或整段：**

1. **三个变体的末行本来就是各自「把话说完」的位置。** 甲的那句是全书唯一的收官句（`story.md` 里 `9ec040a` 之前就没改过），放在黑幕正中收尾，收束层不用替它再说一次「完了」。乙的设计是「同一批证据只换一处、后面整段消失」，那么末行自然停在死者那一条——档案上他只被记成受害者，这就是乙的落点。丙整段被降级，末行是最后一个还能念的事实栏，等于「档案到此为止」。
2. **取末行不会重样。** 如果取前三行，黑幕上写的正是玩家刚刚在归档表记述区里读完的那几句的事实栏（`最早一具` / `埋尸位置`），黑幕就只是一次重复播报；末行是记述区最后一行，读到这里玩家视线也刚走到那里。
3. **不拼、不改写所以可测。** 测试直接 `report["prose"][-1] == outro.lines()[1]`，再回溯断言它在 `report["body"]` 里（`body.contains`），将来改文案不会静默失效。

⚠️ **丙变体这句要请总策划定**：甲、乙的末行读起来像「结局的最后一句」，丙的末行是档案的一栏（`埋葬人数：无法确定。`），读起来像**日志**不像结局。这是任务书 §2.1「不许新写剧情文案」下的必然结果——`_build_bing` 里没有比它更像收官句的现成句子（它的收官句 `没有人被平反…` 在降级时被整段丢掉了）。若要丙也有一个「结局感」的落点，唯一的办法是在 `ending_report.gd` 的 `_build_bing` 里补一句（或让降级保留固定句之外的一句），**那个文件本线不许动**，所以留在这里待拍板。

---

## §4 怎么实现的

### 4.1 状态机

`IDLE → IN(0.8s 渐黑 + 字后到) → WAIT(等键) → OUT(1.0s 渐明) → IDLE`。

- 渐黑 `_black = BLACK_MAX(0.82) * clampf(t/0.8)`；字比黑幕晚 35% 起浮（`_text_a` 从 `t=0.28s` 才开始涨），避免「黑幕还薄的时候字已经清楚了」。
- 渐明时字退得更快（`1 - k*1.8`）：黑幕还剩一半时字已经干净，不会糊在半黑上。
- `_advance(delta)` 单独抽出来，测试可以 `set_process(false)` 后按固定步长手动推，不受真实帧率影响；O1b 则反过来让引擎真跑，两条路都验。

### 4.2 三行字

`_draw()` 自己画，不引入任何美术资源：黑幕是 `draw_rect`，字是 `draw_string`，字体沿用 `ThemeDB.fallback_font`（与 `hud.gd` / `ending_form.gd` 同一条路）。

- 第 1 行：玩家选的出口字（`已归档` / `存疑`），32 px 暖白。
- 第 2 行：见 §3，20 px。
- 第 3 行：`—— 按任意键 ——`，18 px 灰。
- 竖排三行，水平居中，`y0 = size.y * 0.40`（正中偏上），行距 52 / 124 px（按 640×360 设计值 × 2）。

### 4.3 世界全停是两层（这一条超出了任务书 §5.5 的字面）

任务书只要求改 `main.gd` 那条 early-return。但 `_process()` 里 **G / I / F11 的轮询段在那条 return 之前**（鼠标段、切帧段也在），只加 `or outro.is_playing()` 的话，收束期间按 G 仍会弹出归档表、按 F11 仍会切全屏。所以收束层**自己把 `SceneTree.paused` 置 true**：

- `process_mode = PROCESS_MODE_ALWAYS`，黑幕照常渐变、`_input` 照常收键；
- 只解除「本层暂停的」（`_paused_tree` 标记），别人暂停的场景不会被顺手放开；
- `_exit_tree()` 兜底解除，不会把游戏永久卡在暂停态（有断言：`O3 收束结束后暂停被解开`）。

### 4.4「任意键」只认按下边沿

`_input` 里只认 `pressed and not echo`（键 / 鼠标左键 / 手柄键），不轮询按键**状态**。这样「按下出口那颗 Enter / 空格还按着」不会把刚起的收束直接收掉——这是纯轮询写法最容易踩的坑。命中后 `set_input_as_handled()`，不让同一次按键再被下游消费。

---

## §5 截图取证（结构验证 + 数值，**无人眼复核**）

窗口模式（`& $g --path . -s res://_mdtest/ending_outro_check.gd`，不带 `--headless`），`root.get_texture().get_image()` 取帧：

| 文件 | 用途 |
|---|---|
| `lab/_l19_outro_o0_base.png` | 落定前的自由探索基准帧 |
| `lab/_l19_outro_o1_black.png` | 黑幕铺满帧（含三行字） |
| `lab/_l19_outro_o4_clear.png` | 按键淡回后的帧 |

用 `lab/_l19_verify_shots.py`（Pillow）独立验像素，输出 `lab/_l19_verify_report.txt`，结果 `OUTRO_SHOT_VERIFY OK`：

- 黑幕帧颜色数 **1234**（不是纯色块：有渐隐的字）；
- 三行字各自的「近白像素」计数 **1370 / 1094 / 443**，第 1 行 `x_width=92`（3 个字 × ~31 px，与 `已归档` 三字吻合）；
- **行间空隙 0 个亮像素** ⇒ 三行是分开的三行，没有叠在一起；
- `BASE_VS_CLEAR 0/14400 differ (0.0%)` ⇒ 淡回之后画面与落定前**逐像素一致**（世界确实恢复了，没有残留蒙层）。

⚠️ 本机没有视觉模型（`read_image` 报 model 不支持图像输入），所以上面全是数值判定。**排版观感（字号大小、行距疏密、`y0=0.40` 是否偏上）需要一次人眼确认**，改起来只是三个常数（`FONT_BIG` / `FONT` / `y0`）。

---

## §6 回归

O8 指定的三套（headless，`APPDATA` 指向仓库内可写目录，见 §7）：

| 套件 | 结果 |
|---|---|
| `_mdtest/ending_check.gd` | `ENDING_CHECK_DONE fails=0` |
| `_mdtest/ending_wire_check.gd` | `ENDING_WIRE_CHECK_DONE fails=0` |
| `_mdtest/greybox_check.gd` | `solids 238/299/379/812/897`（五帧与基线逐帧一致）、`standable=15105`、`to_a5=12498`、`HOTSPOTS_OK=true`、`REACH_OK=true`、`UNEXPLAINED_BLOCKS=0` |

全仓 17 套一轮扫（13 套用 `PASS` 计数，合计 **954 PASS / 0 FAIL**；另 4 套自带输出格式，同样全绿）：

| 套件 | 结果 | 套件 | 结果 |
|---|---|---|---|
| `a4_rebuild_check` | PASS=34 FAIL=0 | `house_art_check` | PASS=99 FAIL=0 |
| `asset_draw_check` | PASS=62 FAIL=0 | `hud_layout_check` | PASS=21 FAIL=0 |
| `audio_check` | PASS=123 FAIL=0 | `sort_check` | PASS=90 FAIL=0 |
| `camera_check` | PASS=8 FAIL=0 | `tile_wire_check` | PASS=16 FAIL=0 |
| `diary_render_check` | PASS=104 FAIL=0 | `phasing_check` | `fails=0 warns=0` |
| `ending_check` | PASS=139 FAIL=0 | `scene_bake_check` | `checks=1868 fails=0` |
| `ending_wire_check` | PASS=90 FAIL=0 | `display_check` | 五项参数逐条符合（无 PASS 行，直接打值） |
| `evidence_archive_check` | PASS=111 FAIL=0 | `interior_check` | `RESULT: ALL PASS` |
| `ending_outro_check` | PASS=57 FAIL=0（headless）/ 71（窗口） | | |

⚠️ `greybox_check` 里有一条**本线之前就存在的偏差**，不是我引入的：`WALL_STOP_Y=424.0`（脚本自带注释期望 800~816）、`WALL_BLOCKED=false`。该脚本不加载 `main.tscn`、文件未被本线改动（`git status` 干净），三维指标（solids / hotspots / standable / REACH_OK / UNEXPLAINED）全部与基线一致，所以是 A3 世界重构线留下的墙体坐标问题，需要那条线自己对齐。

---

## §7 环境坑（会影响别人的测试，建议同步）

**1. 本沙箱的 `user://` 是只读的，会把旧套件坑成假红。** `user://` = `C:\Users\<user>\AppData\Roaming\Godot\app_userdata\shift`，沙箱里 `Set-Content` / `Remove-Item` 全被拒。后果有两层：

- `EndingStore.save()` 静默回退写 `res://.ending_form.json`（符合设计）；
- 但 `load()` 先读 `user://ending_form.json` —— 那里躺着一份**上一轮遗留的脏存档**（166 字节，`exit_choice:"已归档"`、`motive:{1926:激情,1951:无}`），于是读回来的不是刚存的那份。

实测：直接用默认 `APPDATA` 跑 `ending_check` 会 **`fails=5`**（E9 往返 / E9 覆盖写 / E14 空表 0-14 / E14 空表比例 0 / E13 关表存盘），全部是存档往返类断言——**不是代码问题，是那 5 条读到脏存档**。

**解法（本线全程使用，建议后续测试线统一）**：跑 Godot 前把 `APPDATA` 指到仓库内一个可写目录，`user://` 就落到那里、干净且可写：

```powershell
$env:APPDATA = Join-Path (Get-Location) "lab\_l19_appdata"
& $g --headless --path . -s res://_mdtest/ending_check.gd
```

这样一来 `ending_check` 立刻 `fails=0`，且存档真落在 `user://ending_form.json`（`PASS E9 存档落盘（实际落在 user://ending_form.json）`）——比默认环境更接近玩家机器。本线所有回归数据都在这个环境下取得。

**2. 用 `Get-Content` 数中文文件行数会数错。** PowerShell 默认按系统代码页读 UTF-8，`scripts/ending_outro.gd` 会被数成 254 行（真实 298 行），`main.gd` 被数成 419（真实 499）。要行数请用 `[System.IO.File]::ReadAllLines($p).Count` 或 `Select-String -Pattern "^"`，与本文件里引用的行号一致。

---

## §8 留待后面的事

1. **丙变体的收束文字读起来不像结局**（§3 末），需要 `ending_report.gd` 里补一句，本线不许动。
2. **60 字截断没有被真实文案检验**：三变体现有的末行最长 17 字，截断分支永远走不到。它防的是「将来文案写长了」，逻辑已单测（`_truncate`），但真实排版没验过——真要有 60 字的第 2 行，`draw_string` 会按 `size.x` 居中、单行显示。
3. **「黑幕落定」没有音效**：L18 刚落地 13 条合成 WAV + `Aud` 播放器（尚未接线），本线不许碰音频。这条落定是全游戏情绪最重的一下，建议后续给它挂一条（或复用已有总线里最安静的那条）。
4. **收束期间整棵树 `paused=true`**：HUD 动画、音频淡出、任何靠 `_process` 的节点都会一起停。竞品普遍这么做，但以后若要「黑幕期间 HUD 继续呼吸」，得改成只冻世界（`Timeline`/`Player`）而不是整棵树。
5. **收束层是 `Main` 的最上层孩子**：以后若有比它更晚 `add_child` 的全屏层（比如设置菜单），要确保它画在收束层之下，否则黑幕会被盖住。