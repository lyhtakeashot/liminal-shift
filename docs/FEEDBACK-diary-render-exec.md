# 双日记渲染（L16）执行反馈

2026-11-26 · 开线基准 `5387822`；重跑回归时 HEAD 已是 `9ec040a`（A4 重排线），交付时 `768f36b`（归档表反馈）—— 两者都是他线提交 · 远端仍 `b0798da`

## 1 结论

四个 `scripts/diary_*.gd` 与 `_mdtest/diary_render_check.gd` 全部落盘，**自检全绿**（`DIARY_RENDER_CHECK_DONE fails=0`：D1–D10 + 排版 L1–L6 + 静态 S1–S4 + 界面 S5/S6）。
删除线按 `docs/diary-markup.md:52-63` **全部自绘**（`draw_line`，2px），三份实现文件里 `RichTextLabel` / `[s]` / `HBoxContainer` **零命中**。`scripts/main.gd` **一行未改**（L17 未交付）—— 本线只差接线，完整补丁见 §10。

## 2 四个新文件的职责与关键行号

| 文件 | 行数 | 职责 | 关键行 |
|---|---|---|---|
| `scripts/diary_markup.gd` | 158 | 标记 → 段结构（纯逻辑，**不产 BBCode**） | `parse()` :41、折叠 `_emit_group()` :100、`_flush()` :122、`has_kind/plain_text/kinds` :131/:140/:152 |
| `scripts/diary_texts.gd` | 88 | 四份原稿逐字数据（三引号常量） | `FAKE_MILL` :22、`RAW_MILL` :44、`ZHOU_LEDGER` :65、`ZHOU_EARLY` :72、`LU_FRAGMENT` :76、`mill_pair()` :87 |
| `scripts/diary_page.gd` | 256 | 单页纸自绘（删除线在这里画） | `compute_layout()` :123、`_end_strike()` :198（线位算式 :202）、`_draw()` :209、`draw_line` :236 |
| `scripts/diary_view.gd` | 184 | 双本并排界面（两张纸手动摆位） | `_build()` :58、`_layout()` :87、`show_pair()` :103、`open/close/toggle` :121/:129/:134、`_input()` :143 |

`diary_page.gd` 刻意把**排版**（`compute_layout()` 产出 ops 数组）与**绘制**（`_draw()` 消费 ops）拆开：headless 下画不出像素，但排版能量高度、量行位、量线位，所以「删除线位置对不对」「制表符缩进有没有收回」都能进回归。

## 3 删除线自绘（本线验收重点）

- 位置：`ly = st.y + font.get_ascent(FS) - FS * STRIKE_DY`（`diary_page.gd:202`），`STRIKE_DY = 0.30`、`FS = 17`。实测 `ascent(17) = 19.00`、`height(17) = 24.00` ⇒ 线落在基线上方 `19 - 5.1 = 13.9px`，压在字身的视觉中线上。
- 粗细：`STRIKE_W = 2.0`，`draw_line(..., STRIKE_W, true)`（开抗锯齿）。2px / 24px 字高 = 1:12，是「看得出是一道划痕」的下限；真机嫌细，**唯一要改的数就是 `STRIKE_W`**（改 2.5 不动排版）。
- 长度：同一段 strike **每行各画一条**（`_end_strike` 每次换行收尾），`x0` = 该行首字起点、`x1` = 该行末字右缘，不跨行连成一条。
- ⚠️ 「够不够粗」**本线没看过像素**（沙箱无窗口），必须真机定，见 §8 第 4 条。

## 4 多段涂改折叠的实际实现

`{{A|B}}` → `strike(A)` + `red(B)`；`{{A|B|C|D}}` → `strike(首)` + `ellipsis("…")` + `red(尾)`，**中间段整段丢弃**（D3 断言 `plain_text` 里不含 B/C）。假本（`is_raw_book = false`）只留 `parts[-1]`，**永不产生** strike / red / ellipsis。
⚠️ 任务书 §3.1 只列了 5 种 kind，本线**加了第 6 种 `ellipsis`**：折叠出的「…」既不是要划掉的旧字（不该带线、不该灰到认不出），也不是改正后的新字（不该变红），塞进前两种都会让纸面读错。颜色沿用 `OLD_COL`，不画线。真本 `RAW_MILL` 共 4 处标记，2 处是 2 段、另 2 处（`{{三十|三|二十|三十}}`、`{{迁|走了|不再来了}}`）走折叠 ⇒ 真本页共 4 条删除线（D9 断言 `strike` 段 = 4）。

## 5 四份原稿的逐字校验（差异为零）

① **生成期**（`lab/_l16_gen_texts.py`）：直接读 `docs/story.md` 的 `## 附一.x` 围栏块生成 `diary_texts.gd`，写完立刻回读比对 —— `GEN_DONE bad=0`；规模 `FAKE_MILL 122 chars (tabs=2, newlines=20)`、`RAW_MILL 161 (2/19)`、`ZHOU_LEDGER 75 (—/5)`、`ZHOU_EARLY 22 (—/2)`、`LU_FRAGMENT 27 (—/3)`。行首缩进是真制表符，不是空格。
② **测试期**（`diary_render_check.gd` 的 S3）：测试里**现场重抽** `docs/story.md`（按 `## 附一.<n>` 认块号）再与常量逐字 `==`，五块全 PASS ⇒ 以后谁改了附一，这套立刻红。

口径：「到此为止。后面空白。」按 `docs/story.md:906` 判定是**旁白不是正文**，**不上纸**，只存成校验锚点 `LU_FRAGMENT_NOTE`；「这一处不许有任何注解」同理存 `ZHOU_NO_NOTE`。两条都不进纸面，也就没给「陆婶 → 陆先生」那一处加任何注解（守 `docs/story.md:890`）。附一.4 的两块残页同存一个常量，中间是空行。

## 6 `_mdtest/diary_render_check.gd` 逐条结果

| 项 | 断言 | 结果 |
|---|---|---|
| D1 | `{{A\|B}}` 假本 ⇒ 只 B，无 strike / red | ✅ `plain_text == "收粮 三石。"` |
| D2 | 真本 ⇒ strike("三石二斗") + red("三石") | ✅ 且 strike 段序号 < red |
| D3 | `{{甲\|乙\|丙\|丁}}` 真本 ⇒ strike + ellipsis + red | ✅ `"甲…丁"`，乙丙不出现 |
| D4 | 同上假本 ⇒ 只「丁」 | ✅ kinds == `[text]` |
| D5 | `---` ⇒ sep，**假本也有** | ✅ 两本各 2 个 sep，`plain_text` 里无 `---` |
| D6 | 行首制表符 ⇒ indent | ✅ 2 个 indent 段，`plain_text == "卯时开闸。\n未告陆家。"` |
| D7 | `{{` 未闭合 ⇒ 原样保留 | ✅ `"前{{未闭合"`，无 strike |
| D8 | 四份原稿关键行逐字存在 | ✅「疑非陆万山」「到此为止。后面空白。」「陆婶」（仅民国十六年首笔）「陆先生」（民国三十五年四笔）；两本各 2 处行首制表符；两本原稿里无残留 `{{`/`}}` |
| D9 | 真本有 strike、假本无 | ✅ 真本 strike 4 段 + red + sep 2，假本只有普通文字 + sep；真本纯文字比假本长（留了旧字） |
| D10 | 解析器不产 BBCode | ✅ 段只有 `kind`/`text` 两个键，值里不含 `[` `]` |

附带（任务书没要求、本线加的守门）：L1 两本正文高度都 > 0 且一页装得下（`fake_h=520.0`、`real_h=494.0`、`room=586.0`）；L2 删除线正压在「基线 − 17×0.30」（±0.01）；L3 制表符行 `x = 18 + 34 = 52`、换行后收回 `x = 18`；L4 分隔行独占一行；L5 行距是 26 的整数倍、整页高度也是；L6 折行后没有字冲出右界（40 个汉字在 434px 里折两行）；S1/S2/S4 三个「不许出现」的静态扫描；S5/S6 界面冒烟（两张纸都建出来、默认收起、toggle/close 正常）。

## 7 七套回归

| 套件 | 结果 |
|---|---|
| `camera_check` / `hud_layout_check` / `asset_draw_check` / `sort_check` / `evidence_archive_check` | 全 `fails=0`，输出与本线开工前一致 |
| `display_check` | 纯打印型（`CONTENT_SCALE_MODE=1`、`SIZE=(1280,720)`、`STRETCH_SCALE_MODE=0`），打印完 `quit(0)`，无变化 |
| `greybox_check` | `UNEXPLAINED_BLOCKS=0`；但 `REACH_MAP` 变了：`to_a5 12863→12497`、`blocked_at_step [144,191,722,1184]→[144,191,2171,101]`、`band_full 261→298`、`band_ratio 88%→100%`、`ratio 85%→83%`，`standable` 仍 15104 |

`greybox` 的差异**不是本线造成的**：本线只新增文件，没有任何既有脚本 import 它们（`main.gd` 未改）。差异来自 A4 重排线在 `9ec040a` 重写 `data/frames.json` 的 `a4_2001` 帧（+166 solids、补山填空气墙）—— 我在 `5387822` 上取的基线，重跑时 HEAD 已是 `9ec040a`。A4 线自己的反馈文档记的也是这组数字。

## 8 实机验证（§4.3 九条）

**九条全部未做**：沙箱 headless 起不了窗口（无渲染、截图路径本机不可用），本线只用解析结果 + 排版数值断言。真机上按下面看（压成五组，对应 §4.3 的 ① ／ ②③⑦ ／ ⑤⑥ ／ ④ ／ ⑧⑨），**第 4 组是本线唯一的开放验收项**：

1. 打开 ⇒ 左右两页并排（`_layout()` 居中：总宽 `470×2 + 18 = 958`、高 `648 + 22 = 670`，1280×720 下左右各留 161、上下各留 25）
2. 假本页看不到删除线、没有红字，纸色偏白（`#e8ddc0`）；真本页能看到灰色带线旧字 + 暗红改正字，纸色偏黄（`#e2d6b4`）
3. `{{三十|三|二十|三十}}` 显示成「三十（划掉）… 三十（红）」，中间两段不出现；`---` 显示成淡色小圆点行（`· · · · · · · ·`）
4. **删除线粗细看得清吗** —— 嫌细就把 `diary_page.gd:30` 的 `STRIKE_W` 从 2.0 调 2.5
5. 关掉界面 ⇒ HUD 恢复、走动正常；日记开着时按 WASD ⇒ 世界不动（都靠 §10 的接线）

## 9 已知缺口与取舍

- **解锁时机归关卡/内容线**：本线只提供 `show_pair()` / `toggle()`，哪一帧能打开哪一本由关卡线定（A1 假本随身 / A2 续记 / A3 挖出真本 / A4 登记表 / A5 磨坊不存、周有田往来账）。
- **翻页做的是滚动**（`set_scroll` + `max_scroll`，↑↓/PgUp/PgDn/滚轮，`SCROLL_STEP = 52`）：两本正文都一页装得下（520 / 494 < 586），滚动只是保险；**没做翻页动画**，需要另派。
- **窗口窄于 958px 会左右溢出**：`diary_view.gd:87` 的 `_layout()` 只居中、不缩放（470×648 是硬尺寸，排版参数按这个宽度定）。1280×720 下没问题；要支持小窗口得另做按 `size.x` 缩放的摆位。
- **三条检视文本归检视/关卡线**，本线不实现：A2 挪动的砖「东数第三块砖，灰缝是新的。按了一下，砖往里陷了半分。」、A3 暗龛「墙基里凿出一个方龛，油布包着一本线装账，边角都卷了。」、A3 停工三天。
- **加粗/字体**：红字没用斜体或描边，是同一字右移 `0.6px` 重画一遍（视觉加重、不改字宽、不破排版）；字体只用 `ThemeDB.fallback_font`（自带 CJK），**没引入字体文件**。
- **`sep` 吞换行**：`---` 后面紧跟的 `\n` 一起吃掉，否则「圆点行」下面会多空一行。纸色/字色的唯一权威是 `docs/diary-markup.md:36-50`；`_mdtest/render3.gd` 的 `OLD_COL = #9a9080` 是早期试色，本线按定稿用 `#8f8474`（S2 断言 `#9a9080` 不出现）。

## 10 接线状态（L17 未交付 ⇒ 本线不接 `main.gd`）

判定证据（交付时实测）：`scripts/timeline.gd:15` 仍有 `signal bump(index: int)`、`:81/:87` 两处 `bump.emit`；`scripts/main.gd:56` `tl.bump.connect(_on_bump)`、`:317-321` `_on_bump` 仍在；`scripts/hud.gd:29/96/108/179` `bump_flash` 仍在；`scripts/player.gd:48/79/167` `bump_kick` 仍在；`scripts/world_view.gd:88/119/124/130` `_p_bump` 仍在 ⇒ L17 的删码还没发生。等 L17 交付后按下面补做：

```gdscript
# ① 常量区（main.gd:19 `EvidenceArchive` 之后）
const DiaryView = preload("res://scripts/diary_view.gd")

# ② 成员变量（main.gd:38-39 archive / _archive_i_down 之后）
var diary: Control = null      # 双日记界面（代码动态建，挂 Main 下，与档案同层）
var _diary_j_down := false     # J 键边沿检测（裸键轮询，和 F11 / I 同一套路）

# ③ _ready() 里 _make_archive() 之后（main.gd:68 之后）
	_make_diary()

func _make_diary() -> void:            # _ready 里 view 自己已默认灌好《水簿》一对
	diary = DiaryView.new()
	diary.name = "DiaryView"
	add_child(diary)                   # 必须在 HUD 之后 add，才盖得住 HUD

# ④ _process() 里 I 键那段之后、停世界判断之前（main.gd:138 与 :143 之间）
	var diary_now := Input.is_key_pressed(KEY_J) or Input.is_physical_key_pressed(KEY_J)
	if diary_now and not _diary_j_down and diary != null:
		diary.toggle()                 # Esc 由 DiaryView._input 自己吃
	_diary_j_down = diary_now

# ⑤ 停世界判断扩成两个界面（main.gd:143-146）
	if (archive != null and archive.is_open()) or (diary != null and diary.is_open()):
		player.walking = false
		_set_hud_hidden(true)
		return
```

⚠️ 键位：任务书要求不占 SHIFT / E / I / WASD，这里用 **J**，且走裸键轮询（不改 `project.godot`，免重启编辑器）。