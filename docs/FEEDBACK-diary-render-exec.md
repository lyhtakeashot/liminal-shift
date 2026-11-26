# 双日记渲染（L16）执行反馈

2026-11-26 · 开线 `5387822` · 渲染交付 `768f36b` · 本轮交互重做时 HEAD `85eb561`（老井文案，他线提交）· 远端仍 `b0798da`

## 1 结论

五个新文件 + `scripts/main.gd` 接线全部落盘，**自检全绿**（`DIARY_RENDER_CHECK_DONE fails=0`，**104 条断言**：D1–D10 解析 / L1–L6 排版 / P1–P6 分页 / S1–S6 静态与界面 / V1–V6 键位）。
删除线按 `docs/diary-markup.md:52-63` **全部自绘**（`draw_line`，2px）；`RichTextLabel` / `[s]` / `HBoxContainer` 在三份实现文件里**零命中**。
交互按 2026-11-26 的定案重做：**翻页改成页脚两个箭头（仿《Minecraft》的书）**，**E 翻开、E 或 Esc 合上**，**翻开即入档一份书类证物**。

## 2 五个文件的职责与关键行号

| 文件 | 行数 | 职责 | 关键行 |
|---|---|---|---|
| `scripts/diary_markup.gd` | 158 | 标记 → 段结构（纯逻辑，不产 BBCode） | `parse()` :41、折叠 `_emit_group()` :100、`has_kind/plain_text/kinds` :131/:140/:152 |
| `scripts/diary_texts.gd` | 108 | 四份原稿逐字数据 + 书类证物卡 | `FAKE_MILL` :22、`RAW_MILL` :44、`ZHOU_LEDGER` :65、`ZHOU_EARLY` :72、`LU_FRAGMENT` :76、`mill_pair()` :87、`mill_evidence()` :100 |
| `scripts/diary_page.gd` | 433 | 单页纸自绘 + 分页 + 页脚箭头 | `per_page_lines()` :127、`_ensure_pages()` :134、`arrow_rect()` :213、`hit_arrow()` :221、`compute_layout()` :245、`_end_strike()` :323（线位 :327）、`draw_line` :375、`_draw_footer()` :388 |
| `scripts/diary_view.gd` | 244 | 双本并排 + 翻页 + 开合 + 入档 | `_layout()` :100、`show_pair()` :116、`just_closed()` :153、`collect_copy()` :167、`turn()` :181、`_input()` :195（`KEY_ESCAPE, KEY_E` :228） |
| `_mdtest/diary_render_check.gd` | 544 | 全部断言（headless 跑） | `_layout_checks()` :262、`_page_checks()` :363、`_view_smoke()` :463、`_view_input_checks()` :497 |

`diary_page.gd` 刻意把**排版**（`compute_layout()` 吐 ops，每条 op 带行号 `l`）与**绘制**（`_draw()` 只消费当前页的 op）拆开：headless 画不出像素，但能量高度、量行位、量线位，所以删除线位置、制表符缩进、分页行数都能进回归。

## 3 删除线自绘（本线验收重点）

- 位置 `ly = st.y + ascent(17) − 17×0.30`（`diary_page.gd:327`）⇒ 落在基线上方 13.9px；实测 `ascent(17)=19.00`、`height(17)=24.00`。
- 粗细 `STRIKE_W = 2.0`（`:34`）；2px / 24px 字高 = 1:12，是「看得出是一道划痕」的下限；真机嫌细**只改这一个数**（2.5 不动排版）。
- 同一段 strike **每行各画一条**（`_end_strike` 收尾），不跨行连成一条。
- ⚠️ 「够不够粗」**本线没看过像素**（沙箱无窗口），必须真机定，见 §8。

## 4 多段涂改折叠

`{{A|B}}` → `strike(A)` + `red(B)`；`{{A|B|C|D}}` → `strike(首)` + `ellipsis("…")` + `red(尾)`，中间段整段丢弃；假本只留 `parts[-1]`，**永不产生** strike/red/ellipsis。
⚠️ 任务书 §3.1 只列 5 种 kind，本线**加了第 6 种 `ellipsis`**：折叠出的「…」既不该划线变灰到认不出，也不该变红，塞进前两种都会让纸面读错。真本 `RAW_MILL` 4 处标记（2 处 2 段 + 2 处折叠）⇒ 4 条删除线（D9 断言）。

## 5 逐字校验（差异为零）

① 生成期：`lab/_l16_gen_texts.py` 直接读 `docs/story.md` 的 `## 附一.x` 围栏块生成常量、写完回读比对（`GEN_DONE bad=0`；`FAKE_MILL 122 chars`、`RAW_MILL 161`、`ZHOU_LEDGER 75`、`ZHOU_EARLY 22`、`LU_FRAGMENT 27`）。行首缩进是**真制表符**，不是空格。
② 测试期：S3 **现场重抽** `docs/story.md` 再与常量逐字 `==`，五块全 PASS ⇒ 以后谁改附一立刻红。
口径：「到此为止。后面空白。」按 `docs/story.md:906` 是**旁白不是正文**，**不上纸**，只存校验锚点 `LU_FRAGMENT_NOTE`；`ZHOU_NO_NOTE` 同理。守 `docs/story.md:890`：账页里不加任何注解。

## 6 自检逐条

| 项 | 断言 | 结果 |
|---|---|---|
| D1–D4 | `{{A\|B}}` 假本只 B / 真本 strike+red；`{{A\|B\|C\|D}}` 真本「甲…丁」、假本「丁」 | ✅ 且 strike 段序号 < red |
| D5–D7 | `---`→sep（**假本也有**）；行首制表符→indent；`{{` 未闭合原样保留 | ✅ 两本各 2 个 sep；未闭合不吞字 |
| D8 | 四份原稿关键行逐字存在 | ✅「疑非陆万山」「陆婶」（仅十六年首笔）「陆先生」（三十五年四笔）；两本各 2 处制表符 |
| D9–D10 | 真本 4 条删除线、假本 0；解析器不产 BBCode | ✅ 段只有 `kind`/`text` 两键 |
| L1–L6 | 一页装得下 / 线位 ±0.01 / 缩进回收 / sep 独占行 / 行距 26 整数倍 / 折行不出界 | ✅ `fake_h=520 real_h=494 room=556` |
| P1–P6 | 默认一页（箭头灰掉、点了没反应）；压到 300 高按行分页；两头停住；箭头命中与禁用；箭头在页脚内；真本同样分页 | ✅ 假本 20 行 → 3 页、真本 19 行 → 3 页 |
| S1–S6 | 无 `RichTextLabel`、有 `draw_line`、无 `[s]`、无容器拼装、定稿色/字号、界面冒烟 | ✅ |
| V1–V6 | Esc 合 / E 合 / 点右箭头两本同翻 / 点正文不翻 / → 到末页停 / 收起时按键不开 | ✅ `just_closed()` 在合上那一帧为真 |

## 7 七套回归

`camera_check` / `hud_layout_check` / `asset_draw_check` / `sort_check` / `evidence_archive_check` 全 `fails=0`；`display_check` 打印型无变化；`greybox_check` `UNEXPLAINED_BLOCKS=0`，`REACH_MAP` 与 A4 重排后一致（`to_a5 12497`、`band_full 298/298`、`ratio 83%`、`standable 15104`）——这组数是 A4 线 `9ec040a` 改 `data/frames.json` 带来的，不是本线。

## 8 实机验证（仍未做，沙箱无窗口）

①两页并排、页脚左右两个三角箭头、中间「1 / 1」；②假本无删线无红字、真本灰字带线 + 暗红改正；③`{{三十|三|二十|三十}}` 读成「三十（划掉）… 三十（红）」；④**删除线粗细**（嫌细改 `STRIKE_W`）；⑤E 翻开 → E / Esc 合上 → HUD 回来、能继续走；⑥纸面压小或文本更长时点箭头能翻页、两本同步。

## 9 已知缺口与取舍

- **翻页按行切、不劈行**：一行绝不跨两页；一页放 `floor((h−18−30−44)/26)` 行。默认 648 高时每本只有一页 ⇒ 箭头灰着（和 Minecraft 一样，按钮留着）。
- **解锁时机归关卡/内容线**：本线只提供 `show_pair()` / `open_view()`；哪一帧能打开哪一本由关卡线定（A1 假本随身 / A3 挖出真本 / A5 磨坊不存、周有田往来账）。
- **入口要数据**：`data/frames.json` 里还没有任何「书」热点，所以现在 E 没有可翻的东西；`J` 是**临时调试入口**，数据落地后删掉（`main.gd:180-184`）。
- **举证（对质时呈上）还没做**：本线只做到「翻开即入档一张书类证物卡」（key `《水簿》`，`diary_texts.gd:100`）；全文仍只在 `RAW_MILL` 里，将来对质按 key 取卡 + 取全文，不存两份正文。
- **窗口窄于 958px 会左右溢出**：`_layout()` 只居中不缩放（470×648 是硬尺寸，排版按这个宽度定）。
- **三条检视文本归检视/关卡线**，本线不实现：A2 挪砖、A3 暗龛、A3 停工三天。
- 字体只用 `ThemeDB.fallback_font`（自带 CJK），**没引字体文件**；红字「加粗」是同字右移 0.6px 重画；`---` 后面紧跟的 `\n` 一起吃掉，否则圆点行下面多一空行。

## 10 接线状态：已接 `main.gd`（6 处，纯增量）

1. 常量 `DiaryView` / `DiaryTexts`（`:20-21`）；2. 成员 `diary` / `_diary_j_down`（`:42-43`）；3. `_ready()` 里 `_make_diary()`（`:73`）；4. `_make_diary()`（`:91`）+ `_try_open_diary()`（`:101`）；5. 停世界判断扩成两个界面（`:191`）；6. E 分支（`:204-209`）。

数据契约：热点字典加一行 `"diary": "mill"` ⇒ 在该格按 E 翻开《水簿》一对，同一次按键顺手 `collect_copy(f.year)` 入档。
⚠️ **L17 冲突面**：`main.gd` 正是 L17（phasing）要删 `bump` 的文件，本线交付时 L17 尚未落地（`timeline.gd:15` 仍有 `signal bump`、`main.gd:56` 仍有 `tl.bump.connect`）。本线这 6 处是纯增量，L17 先合也只是按行号重贴。
⚠️ 键位不占 WASD / SHIFT / I；E 复用检视键（界面内 E = 合上）；界面开着时世界全停，HUD 让开。