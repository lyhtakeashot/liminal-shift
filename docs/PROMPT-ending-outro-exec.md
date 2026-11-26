# 任务书 L19：结局收束（把最后一个「按了没反应」补上）

> 立项 2026-11-26，lead 签发。用户已拍板「结局要接」。
> 比赛截止：北京时间 2026-12-02 05:37。

---

## §0 一句话目标

玩家在归档表上落定出口（「已归档」或「存疑」）后，**画面收束**：渐黑 + 三行字 + 一句提示，
按任意键回到自由探索。现在按出口等于什么都没发生（只存盘 + 关表），这是全游戏最后一个断点。

## §1 现状（已实测）

- `scripts/ending_form.gd` 第 243 行声明了 `signal exit_chosen(exit_key: String)`，
  全仓库**零监听者** —— 这就是「按了没反应」的全部原因。
- `ending_form.gd` 对外只有 5 个方法：`is_open()` / `open_form(year:int=2026)` / `close_form()` /
  `toggle(year:int=2026)` / `report_now()`；内部 `_handle_keys()` 自己吃 ↑↓←→/Tab/Enter/Esc/F。
- `scripts/ending_report.gd` 已有**三个变体**的记述正文（按玩家填法切换），
  `scripts/ending_store.gd` 存到 `user://ending_form.json`（已验过：存档能留存）。
- `scripts/main.gd` 里 `EndingForm` 的接线在 `82c4a31`（G 键开表）。锚点见 §5。

## §2 硬约束

### 2.1 不许新写剧情文案

收束文字**必须**取自 `ending_report.gd` 已有的变体正文（取每个变体正文的**最后一段/最后一句**即可），
或直接展示该变体正文的前 N 行。理由：文案是 lead 的地盘（`docs/story.md` 口径），
执行线自创剧情会在赛前引入没人复读过的句子。**你要做的是「把它显示出来」，不是「写它」。**

### 2.2 文件白名单

```
scripts/ending_outro.gd          新建（收束层，Control 或 CanvasLayer）
scripts/main.gd                  只允许：1 个 preload + 1 个成员变量 + 1 处 _make_* 调用
                                 + 1 处 connect + 1 处 early-return 条件（见 §5）
_mdtest/ending_outro_check.gd    新建
docs/FEEDBACK-ending-outro-exec.md  新建
```

### 2.3 绝对不许碰

```
scripts/ending_form.gd / ending_report.gd / ending_store.gd   ← 已交付且被 82c4a31 依赖
scripts/world_view.gd / player.gd / hud.gd / frame_data.gd / timeline.gd
data/**    scenes/**    assets/**    project.godot
docs/**  除你自己的反馈
```

**`main.gd` 是独占锁**：这条线跑的期间不许有第二条线改 `main.gd`。
开工前先 `git status --short scripts/main.gd` —— 非空就停下问我。

**不许新增 InputMap action**：改 `project.godot` 的 `[input]` 要重启编辑器才生效，
本项目历史上被这个坑过。一律用裸键轮询（抄 `main.gd` 的 I 键那段：`Input.is_key_pressed(KEY_X)` + 边沿检测）。

## §3 行为规格

1. `exit_chosen` 触发 → 立刻 `close_form()`（表先收，别两样东西叠着），然后播放收束。
2. 收束表现（**纯代码画，不引入任何美术资源**）：
   - 全屏黑幕 `alpha` 从 0 → 0.82，时长 **0.8s**（`create_tween()` 即可）。
   - 黑幕起来后，正中偏上竖排三行：
     - 第 1 行：玩家选的那个出口的字（「已归档」/「存疑」）
     - 第 2 行：`ending_report.gd` 对应变体正文的最后一段（超长就截断到 60 字）
     - 第 3 行：`—— 按任意键 ——`
   - 字体沿用项目现有字体（看 `scripts/hud.gd` 怎么取字体，别自己 new 一个）。
3. 收束期间**世界全停**：直接复用 `main.gd` 里「档案/书本开着 ⇒ 世界停」那个 early-return
   的判断位置，把收束也加进条件（见 §5 第 5 条）。
4. 按任意键（`KEY_ESCAPE` 或任意键都收）→ 黑幕 alpha 1.0s 淡回 0 → 恢复自由探索。
   **不要**跳标题、不要退出游戏（本项目没有标题场景，`run/main_scene` 就是 `main.tscn`）。
5. 收束结束后再按 `G` 必须还能重新打开归档表（不许把 `ending_form` 状态搞坏）。
6. `exit_chosen` 只能触发一次收束；重开表再落定 = 再来一次，允许。

## §4 验收表

| 编号 | 断言 |
|---|---|
| **O1** | 落定出口后 1s 内黑幕出现（截图采样中心像素亮度下降 ≥ 50%） |
| **O2** | 收束文字 == `ending_report.gd` 对应变体正文的一段（**字符串包含断言**，不是肉眼比对） |
| **O3** | 收束期间 `main.player.walking == false`，且 WASD 不改变 `tl.char_pos` |
| **O4** | 按任意键后黑幕消失（中心像素回到收束前的亮度 ±10%） |
| **O5** | 收束结束后 `ending_form.open_form()` 仍可调用，`is_open()` 正确翻转 |
| **O6** | `user://ending_form.json` 在收束前后都存在且内容不同（说明落定确实存了盘） |
| **O7** | `godot --headless --path . --quit-after 120` 无 `SCRIPT ERROR` |
| **O8** | 回归：`_mdtest/ending_check.gd`、`_mdtest/ending_wire_check.gd`、`_mdtest/greybox_check.gd` 全绿 |

**截图要求**：O1/O4 必须出图（窗口模式，**不能带 `--headless`**，headless 取不到像素）。
O2 必须是字符串断言 —— 本项目铁律「验收项决定产出形态」：只写「看起来对」等于没验。

## §5 `main.gd` 的 5 处改动（只许改这 5 处）

以 `82c4a31` 之后的文件为准，先 `grep -n` 定位，不要凭本任务书里的行号硬改：

1. preload 区（`const DiaryTexts = preload(...)` 之后）：`const EndingOutro = preload("res://scripts/ending_outro.gd")`
2. 状态区（`var diary: Control = null` 之后）：`var outro: Control = null`
3. `_make_diary()` 之后新增 `_make_outro()`，并在 `_ready()` 里 `_make_diary()` 之后调用它
4. `_make_outro()` 里：`outro = EndingOutro.new()` → `add_child(outro)` →
   `ending_form.exit_chosen.connect(outro.play)`（**注意 `ending_form` 的成员名以实际为准**，
   可能叫 `form` / `ending`，先 grep）
5. 「档案/书本开着 ⇒ 世界停」那条 `if`：条件里加 `or (outro != null and outro.is_playing())`

**其它一个字都不许动。** 尤其不许碰 `_process_time` / `_process_space` / `_collect_evidence` / 输入分支。

## §6 环境

```powershell
$g = "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe"
& $g --headless --path . -s res://_mdtest/ending_outro_check.gd
& $g --headless --path . -s res://_mdtest/ending_check.gd
& $g --headless --path . -s res://_mdtest/ending_wire_check.gd
& $g --headless --path . -s res://_mdtest/greybox_check.gd
& $g --path . --quit-after 240          # 窗口模式冒烟，看有没有渲染期报错
```

看关键字不看退出码；不要 `cmd /c`；不要 `> out.txt`；`git add` 只加白名单，不 push。

## §7 交付

`docs/FEEDBACK-ending-outro-exec.md`，格式照 `docs/FEEDBACK-house-art-a4a5-exec.md`。
另外在反馈里回答一句：**收束文字你实际取了哪一段、为什么取它**（我要确认它读起来像结局，不像日志）。