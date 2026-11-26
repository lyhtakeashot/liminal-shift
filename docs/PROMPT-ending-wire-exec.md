# 执行任务书 · 线 A：结局接线 + 日记正式入口收口

> 总策划下达 2026-11-26。**这是赛前唯一「玩法不闭环」的缺口**：证物能收、日记能看，但**没有结局**。
> 派发前先读整份，特别看 §1 白名单和 §5 不能同时跑的线。

---

## §0 一句话

`scripts/ending_form.gd`（归档表界面，758 行）、`ending_report.gd`（记述生成）、`ending_store.gd`（存档）**全部已交付并通过自测**（`_mdtest/ending_check.gd` 的 E1–E8 全绿），
但 `scripts/main.gd` 里 **`EndingForm` 零引用** ⇒ 归档表永远弹不出来。
本线就干一件事：**把它接进主循环，让玩家能走到结局**；顺带把日记的临时调试键（J）收掉、换成正式入口。

---

## §1 文件白名单（**只许动这三个**）

| 文件 | 允许的改动 |
|---|---|
| `scripts/main.gd` | 接线（约 10 行）＋ 删 J 调试键 |
| `data/frames.json` | **只允许**给 `a1_1926`/`a2_1951`/`a3_1976` 三帧的 `hotspots` 各加**一条**书热点 |
| `_mdtest/ending_wire_check.gd`（新建） | 接线自检 |

🔴 **别碰**：`scripts/ending_form.gd`、`ending_report.gd`、`ending_store.gd`（已交付，改它们＝重开一条线）、`scripts/world_view.gd`、`scripts/house_shape.gd`、`scripts/evidence_store.gd`、`docs/**`（活文档只有总策划写）、`assets/**`。

⚠️ 工作区现在有别人未提交的改动（`data/frames.json` 的 `start_frame`/`start_pos`、`scripts/timeline.gd`、`scripts/frame_data.gd`、三份 docs）。
**提交时只 `git add` 你自己碰的文件，绝不 `git add -A`，绝不 push。**

---

## §2 现状（2026-11-26 总策划实测，行号按当时 HEAD）

`scripts/main.gd`（470 行）：

| 锚点 | 内容 |
|---|---|
| `:16-21` | preload 区：`Timeline` / `FrameData` / `EvidenceStore` / `EvidenceArchive` / `DiaryView` / `DiaryTexts` |
| `:40-43` | 状态区：`archive` / `_archive_i_down` / `diary` / `_diary_j_down` |
| `:77-78` | `_ready()` 里 `_make_archive()` / `_make_diary()` 相邻两行 |
| `:86-89` | `_make_archive()`：`EvidenceArchive.new()` → `add_child()` |
| `:96-101` | `_make_diary()`：`DiaryView.new()` → `add_child()` → `set("archive_hook", archive)` |
| `:105-124` | `_try_open_diary()`：**契约**＝脚下热点字典里带 `"diary": "mill"` 才翻开《水簿》 |
| `:173-183` | **I 键**开关证物档案（`InputMap` 动作 + 裸键兜底 + 边沿检测）—— 照它抄 |
| `:185-190` | **J 键**开关日记（临时调试入口，本线要删） |
| `:192-200` | 「档案 / 书本开着 ⇒ 世界全停」的 early-return（`player.walking=false` → `_set_hud_hidden(true)` → `return`） |
| `:210-214` | E 键：先 `_try_open_diary()`，翻不开才 `_do_inspect()` |

`scripts/ending_form.gd` 对外接口（**只许用这些**）：`is_open()`、`open_form(year:int=2026)`、`close_form()`、`toggle(year:int=2026)`、`report_now()`。
内部 `_handle_keys()` 自己吃 **↑↓←→ / Tab / Enter / Esc / F**（F 和 Esc 都是关表）。

---

## §3 要做的事

### 3.1 接线归档表（照 `_make_archive()` 抄）

1. `:21` 之后加 `const EndingForm = preload("res://scripts/ending_form.gd")`。
2. `:43` 之后加两行：`var ending_form: Control = null`、`var _ending_g_down := false`。
3. `:78` 之后加 `_make_ending_form()`；在 `_make_diary()`（`:101`）后面加实现：
   ```gdscript
   ## 建结案归档表：动态挂 Main 下（与证物档案同层，建在最后 → 画在最上面）。
   func _make_ending_form() -> void:
       ending_form = EndingForm.new()
       ending_form.name = "EndingForm"
       add_child(ending_form)
   ```
4. `:196` 的 early-return 条件里加上归档表：
   ```gdscript
   if (archive != null and archive.is_open()) \
           or (diary != null and diary.is_open()) \
           or (ending_form != null and ending_form.is_open()):
   ```
5. 触发键：**`G`**（`KEY_G`）。照 `:173-183` I 键的写法：裸键轮询 + 边沿检测，`ending_form.toggle(tl.current().year)`。
   🔴 **不许用** E / F / Esc / Tab / Enter / 方向键 / WASD / Shift / I / F11 —— 有的被 `ending_form._handle_keys()` 自己吃了，有的是移动/检视/切时代键。
   🔴 **不新增 InputMap action**（改 `project.godot` 要重启编辑器才生效）。裸键段要放在 `:192` 那条 early-return **之前**（和 J 键同位置），否则表开着的时候按 G 关不掉它。

### 3.2 删掉 J 调试键

删 `:185-190` 整段 + `:43` 的 `_diary_j_down` 声明 + `_make_diary()` 注释里关于「J 是临时入口」的两句（`:93-95`）。
日记从此只能从世界里的书翻开（E）。

### 3.3 给日记一个正式入口（**唯一允许改 `data/frames.json` 的地方**）

磨坊只在 `a1_1926` / `a2_1951` / `a3_1976` 三帧存在（`mill_a1`/`mill_a2`/`mill_a3`）。给这三帧各加**一条**书热点：

```json
{"title": "水簿", "pos": [x, y], "reach": 68, "diary": "mill", "text": "……"}
```

`(x, y)` 取磨坊**室内柜台 / 暗龛那一格**的世界坐标＝`house.pos + 格坐标 × 32`（格坐标看 `_ref/houses/houses_data.json` 里 `mill_a1/a2/a3` 的 `furniture` / `clue`）。

⚠️ **必须实测确认一件事**：`hotspot_at()` 的取用顺序。房子的家具热点是在 `scripts/frame_data.gd` 的 shapes 循环里先加的，`frames.json` 的 `hotspots` 是循环后补加的 —— **同一格可能被家具热点先吃掉**，那样按 E 只会弹检视卡、翻不开书。
⇒ 站到那格、按 E、看翻开的是不是《水簿》。翻不开就那条热点换个位置（挪到旁边一格）或换实现路径，**但不许去改 `_try_open_diary()` 的判断条件**（那是契约）。

---

## §4 验收（一条一条过，报告里逐条写结果）

| # | 断言 | 怎么验 |
|---|---|---|
| A1 | 启动无脚本 ERROR | 窗口模式 `--quit-after 120`，日志里除 `user://logs` / root certificate 两条已知无害 ERROR 外为空 |
| A2 | 按 **G** 弹出归档表 | 截图或打印 `ending_form.is_open()` |
| A3 | 表开着时世界真停 | 按 G 后再按 WASD / Shift / E，`tl.char_pos` 与 `tl.index` 不变 |
| A4 | 表内能填格 | ↑↓←→ / Tab / Enter 能改值填格；Esc 或 F 能关表 |
| A5 | 关表后能正常走 | 按 G 关掉后再按 W，坐标变化 |
| A6 | **J 不再有反应** | 按 J，日记不弹 |
| A7 | **书旁按 E 能翻开《水簿》**（三帧都验） | 站到热点格按 E，`diary.is_open()` 为真、标题正确 |
| A8 | `_mdtest/ending_check.gd` 仍 `fails=0` | 关键词判定 |
| A9 | `_mdtest/ending_wire_check.gd`（新建）覆盖 A2/A3/A6 | 关键词判定 |

再跑这三套确认没碰坏别人的东西：`phasing_check`（`fails=0 warns=0`）、`greybox_check`（`solids` 仍是 **238/299/379/812/897**、`HOTSPOTS=9`、`UNEXPLAINED_BLOCKS=0`、`REACH_OK=true`）、`evidence_archive_check`（`fails=0`）。

---

## §5 环境 / 命令 / 纪律

- Godot：`D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe`
- python（带 Pillow）：`C:\Users\lyh\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe`
- 跑测试：`& $g --headless --path . -s res://_mdtest/<name>_check.gd`；**看关键字，不看退出码**（`greybox_check.gd:49` 有个提前 `quit(1)` 的守卫，`$LASTEXITCODE` 也读不出值）
- 要像素/截图：**不能带 `--headless`**
- 读 `data/frames.json`：`[IO.File]::ReadAllText($p,[Text.Encoding]::UTF8) | ConvertFrom-Json`（`Get-Content | ConvertFrom-Json` 会因编码炸）
- 写 `data/frames.json`：先验证 `json.dumps(indent=2, ensure_ascii=False)` 与原文件**逐字节相同**再动手（防止整文件格式漂移）
- 比赛截止 2026-12-02 05:37（北京）。**不 push**，提交时机由用户定。

## §6 交付物

1. `scripts/main.gd`（接线 + 删 J）、`data/frames.json`（三帧各一条书热点）、`_mdtest/ending_wire_check.gd`
2. `docs/FEEDBACK-ending-wire-exec.md`：改了哪几行、A1–A9 逐条结果、回归数字、**玩家怎么触发结局（完整键位流程）**、遗留问题