# L16 · 双日记渲染 执行提示词

> 这条线把《阈限迁移》的**第二本账**做出来：假本《水簿》与真本《水簿》。
>
> 设计文档已经把语法、配色、四份原稿全部写死了（`docs/diary-markup.md`、`docs/story.md` 附一），
> `_mdtest/render3.gd` 里还有一个能跑出图的实验实现。
> 本线负责把「实验脚本」变成「游戏里的两页纸」。

---

## §0 开工前

### §0.1 路径与工具

- 仓库根：`D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift`
- Godot：`D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe`（**不在 PATH**）
- 跑回归（**看关键字不看退出码**；沙箱噪声 `Failed to read the root certificate store.` 属正常）：

```
& "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe" --headless --path . -s res://_mdtest/xxx_check.gd 2>&1 | Select-Object -Last 45
```

七套回归：`_mdtest/greybox_check.gd`、`camera_check.gd`、`hud_layout_check.gd`、`asset_draw.gd`…（全名见 `docs/PROMPT-overseer.md` §九）

### §0.2 HEAD 下限

开工前 `git log --oneline -1` 必须是 **`3f5bc49`** 或更新。若早于它，**停下报告**。

### §0.3 开工前先跑基线

七套全跑一遍，输出存 `lab/_l16_baseline.txt`。**基线有红项就停下报告。**

### §0.4 脏工作区纪律

- `M _ref/art/A1_1926/*.png` 等 11 张 ＝ 美术线，**一个字都不许碰**
- `D 美术资产/**` ＝ 用户自己删的，**不许恢复**
- **只精确 `git add` 自己那批文件，绝不 `git add -A` / `git add .`**
- **不许 `git checkout -- <file>`**（沙箱拦），要还原用 `git show HEAD:<path>` 按字节写回
- 长文件改不动长行时用 python 按行号改，脚本放 `lab/`

### §0.5 本线要碰的文件（**允许改/新建**）

| 文件 | 说明 |
|---|---|
| **新建** `scripts/diary_markup.gd` | 标记解析器（纯逻辑） |
| **新建** `scripts/diary_page.gd` | 单页纸的自绘 Control（**删除线自绘**） |
| **新建** `scripts/diary_view.gd` | 双本对照界面（假本 + 真本两页） |
| **新建** `scripts/diary_texts.gd` | 四份原稿的数据（**从 `docs/story.md` 附一抄，不要另编**） |
| **新建** `_mdtest/diary_render_check.gd` | 本线专属回归 |
| **新建** `docs/FEEDBACK-diary-render-exec.md` | 反馈文档，≤120 行 |
| `scripts/main.gd` | **仅最后一步的接线**，且必须等 L17 交付 |

### §0.6 本线**不许碰**的文件

- `data/frames.json`、`_ref/houses/houses_data.json`
- `scripts/house_shape.gd`（L4 独占）
- `scripts/evidence_store.gd`、`scripts/evidence_archive.gd`（证物域）
- `scripts/world_view.gd`（L2/L8 独占）
- `scripts/hud.gd`（L17 独占）⇒ **日记必须是独立 Control，不能往 HUD 里画**
- `scripts/player.gd`、`scripts/timeline.gd`
- `scripts/frame_data.gd`
- `assets/**`、`_ref/art/**`
- `docs/story.md`、`docs/npc.md`、`docs/diary-markup.md`（**只读**；本线不产叙事、不改语法文档）
- `_mdtest/` 里除新建的 `diary_render_check.gd` 之外的所有套件 —— **它们的断言一条都不许改**
  （⚠️ `_mdtest/render3.gd`、`render.gd`、`render2.gd`、`diary_test.gd`、`demo.gd`、`demo4.gd` 是**实验脚本**，可以读、可以参考，**不许删、不许改**）

### §0.7 与 L17（phasing 线）的串行

- L17 独占 `scripts/main.gd`、`scripts/hud.gd`、`scripts/timeline.gd`、`scripts/player.gd`、`scripts/world_view.gd`。
- 本线**除了最后一步接线，其余全部工作都不碰这些文件** ⇒ 主体部分可以与 L17 并行。
- 唯一要碰 `main.gd` 的是 §5.2 的接线。
  ⇒ **开工前看 `docs/PROMPT-overseer.md` §十一「现在就能开/不能开」表**：
  - 若 L17 **正在跑** ⇒ 本线做到「所有文件都写好、只差 main.gd 接线」就**收工**，把接线补丁写进反馈文档，等 L17 交付后再补。
  - 若 L17 **已交付** ⇒ 本线可以自己接完。

### §0.8 与 L15（归档表线）的关系

L15 也在做新界面。**两条线文件零重叠**（L15 用 `ending_*.gd`，本线用 `diary_*.gd`），**可以同时跑**。
但**两个人不能同时改 `scripts/main.gd`** ⇒ 接线段要错开（L17 → L15 → L16，或由总策划指定顺序）。

---

## §1 独占写入文件

本线**独占**（同一时间不许别的线碰）：

1. `scripts/diary_markup.gd`
2. `scripts/diary_page.gd`
3. `scripts/diary_view.gd`
4. `scripts/diary_texts.gd`
5. `_mdtest/diary_render_check.gd`
6. `docs/FEEDBACK-diary-render-exec.md`

本线**可小改**（且必须串行）：`scripts/main.gd`（仅接线）。

---

## §2 数据基准（**语法与原稿全部现成，本线不另编**）

### §2.1 四个标记（`docs/diary-markup.md`）

| 标记 | 含义 | 假本渲染 | 真本渲染 |
|---|---|---|---|
| `{{旧|新}}` | 一处涂改 | **只留「新」** | 旧字划掉变灰 ＋ 新字红色加粗 |
| `{{旧A|旧B|新}}` | 多处涂改 | 只留最后一段 | 旧A划掉 ＋ `…` ＋ 新字红 |
| `---` | 分隔 | 淡色小圆点行 | 同 |
| 行首制表符 | 缩进 | 缩进 | 缩进 |

**必须两套都处理全部四个标记**（`docs/diary-markup.md:118` 第③条陷阱：「假本里 `---` 也要处理，两套渲染都必须处理所有标记」）。

### §2.2 配色与排版参数（`docs/diary-markup.md:36-50`，实测值）

| 项 | 值 |
|---|---|
| 被划掉的字色 | `#8f8474` |
| 改正的字色 | `#8b2f2f` |
| 删除线粗细 | **2px 自绘** |
| 删除线位置 | `y + ascent - font_size * 0.30` |
| 正文字号 | 17 |
| 行高 | 26 |
| 纸张色（假本） | `#e8ddc0` |
| 纸张色（真本） | `#e2d6b4` |
| 墨色 | `#3a2f22` |

⚠️ `_mdtest/render3.gd:30-32` 里的常量是**早期试色**（`OLD_COL := "#9a9080"` / `NEW_COL := "#8b2f2f"` / `INK_COL := "#3a2f22"`）⇒ **以 `docs/diary-markup.md` 的实测值为准**（`#8f8474` 才是定稿值）。

### §2.3 🔴 删除线必须自绘（**本线最大的技术坑**）

`docs/diary-markup.md:52-63`：

> 删除线必须自绘。`RichTextLabel` 的 `[s]` 线宽由字体决定不可调，太细。

`_mdtest/render3.gd:88-95` 用的是 BBCode `[s]` —— **那是实验版，能出图但线太细，不许直接照搬当定稿**。

⇒ **本线要求**：`scripts/diary_page.gd` 用**自绘 Control**（`_draw()` 里 `draw_string` 逐字/逐段画，自己 `draw_line` 画删除线），
删除线位置照公式 `y + font.get_ascent(font_size) - font_size * 0.30`，粗细 2px。

**不要**用 `RichTextLabel` + `[s]` 当最终实现。

### §2.4 多段涂改的折叠（`docs/diary-markup.md:95-118`）

`{{三十|三|二十|三十}}` 四段若全排出来会读成乱码 ⇒ **超过两段折叠成「首 → … → 尾」**。

`_mdtest/render3.gd:80-95` 的 `_emit()` 已有这个逻辑，可参考，但**要按本线的自绘方式重写**（BBCode 字符串在自绘版里不适用）。

### §2.5 BBCode 的坑（`docs/diary-markup.md:75-93`）

- `[s]` ✅ 但太细 ⇒ 不用
- `[color]` 可嵌套，但**必须严格配对，不能跨段落闭合**
- `[opentype]` / `[lb]` / `[rb]` ❌ 不可用
- `_mdtest/diary_test.gd:58-62` 验证过：**未知标签会原样留在文本里**（`RichTextLabel.get_parsed_text()` 可见）⇒ 自绘版本来就没有这个问题，但别因此放松

### §2.6 中文渲染（`docs/diary-markup.md:65-73`）

Godot 默认字体自带 CJK，**不需要额外字体资源**。
⇒ 本线**不许**引入字体文件（避免和美术线的 `assets/` 冲突）。

### §2.7 四份原稿（`docs/story.md` 附一，**逐字抄，不许改一个字**）

| 原稿 | 位置 | 内容要点 |
|---|---|---|
| 附一.1 假本誊清 | `docs/story.md:797-818` | 干净誊清版，**没有涂改标记** |
| 附一.2 真本原稿 | `docs/story.md:827-846` | 带 `{{}}` 标记的原始稿（`收粮 {{三石二斗|三石}}。`／`{{。|在闸下。}}`／`{{三十|三|二十|三十}}`／`{{迁|走了|不再来了}}`） |
| 附一.3 周有田往来账 | `docs/story.md:865-894` | 民国三十五年四笔（叁元/伍元…），含唯一一次笔迹变化「陆婶」→「陆先生」；`:890`「**这一处不许有任何注解。**」 |
| 附一.4 陆敬之残页 | `docs/story.md:900-905` | 「……字迹与村志所载不同，疑非陆万山…… 今夜去老井」＋「到此为止。后面空白。」 |

⇒ **`scripts/diary_texts.gd` 的内容必须从 `docs/story.md` 逐字抄**，不许改写、不许润色。
抄完要能 diff 回原文（用 `git show HEAD:docs/story.md` 抽那几段比对）。

### §2.8 双本的设定差异（`docs/story.md` §5.1，行 288-368）

| | 假《水簿》 | 真《水簿》 |
|---|---|---|
| 位置 | 磨坊柜台随手翻 | 墙基暗龛油布包 |
| 纸张 | 好纸硬壳 | 糙纸线装边角卷 |
| 笔迹 | 极整齐像誊抄 | 有涂改有划掉 |
| 内容 | 全是真话，只删了钱 | 全是数字，偶尔一句 |

`:305`「**假本写得比真本整齐——玩家还没读内容，先感到不对劲。**」
⇒ **假本那页要用「整齐」的排版**（无涂改、字迹规整），**真本那页要有划痕**。两页并排的观感差异本身就是玩法。

### §2.9 跨帧的揭晓节奏（`docs/story.md` §5.3，行 313-331）

| 时代 | 玩家得到什么 |
|---|---|
| A1 | 无暗龛，假本随身带 |
| A2 | 账房新砌暗龛，里面空着；假本续记 |
| A3 | 从暗龛挖出真本 |
| A4 | 土地登记表第二联 |
| A5 | 磨坊不存、真本早已不在现场；周有田往来账 |

⚠️ **本线只做「渲染」**：把这两页纸画出来。
**哪一帧能打开哪一本，是关卡/内容线的事**（本线提供接口，不决定解锁时机）。

### §2.10 三条检视文本（`docs/story.md` §5.6）

- A2 挪动的砖：「东数第三块砖，灰缝是新的。按了一下，砖往里陷了半分。」
- A3 挖出的暗龛：「墙基里凿出一个方龛，油布包着一本线装账，边角都卷了。」
- A3 停工三天

⇒ 这些是**文本**，本线只在反馈文档里记下「它们归哪条线」，**不实现检视逻辑**。

---

## §3 必改清单

### §3.1 第一件：`scripts/diary_markup.gd`（新建，纯逻辑）

**把标记解析成「段结构」，不直接生成 BBCode**（因为要自绘）。

建议数据结构：

```
# 段落数组，每个元素：
{ "kind": "text",  "text": "……" }
{ "kind": "strike", "text": "旧字" }        # 真本：要画删除线
{ "kind": "red",    "text": "新字" }        # 真本：红字
{ "kind": "sep" }                          # ---
{ "kind": "indent", "text": "……" }
```

接口建议：

```
static func parse(raw: String, is_raw_book: bool) -> Array
# is_raw_book = false → 假本：{{A|B|C}} 只保留最后一段，且不产生 strike
# is_raw_book = true  → 真本：两段 → strike(A) + red(B)
#                        三段及以上 → strike(首) + "…" + red(尾)
```

**规则**（照 §2.1 / §2.4）：
- `{{}}` 没闭合（找不到 `}}`）⇒ **原样输出**，不要吞掉后面的内容
- `{{A|B}}` 假本 ⇒ 输出 B（**不加任何标记**）
- `{{A|B|C}}` 真本 ⇒ strike(A) ＋ 红「…」 ＋ red(C)
- `{{A|B|C}}` 假本 ⇒ 输出 C
- `---` ⇒ sep 段
- 行首制表符 ⇒ indent 段（缩进一个固定量，比如 2 个汉字宽）

### §3.2 第二件：`scripts/diary_page.gd`（新建，自绘 Control）

**自绘**，不依赖 `RichTextLabel`。

要点：
- `extends Control`
- `_ready()` 里 `set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)`（⚠️ 见 `scripts/evidence_archive.gd:59-61` 的坑：动态节点必须用带 OFFSETS 的版本）
- `_draw()` 里：
  1. 画纸张底色（假本 `#e8ddc0` / 真本 `#e2d6b4`）
  2. 逐段 `draw_string(font, pos, text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, color)`
  3. **删除线**：在 strike 段下面自己 `draw_line(Vector2(x, y + font.get_ascent(font_size) - font_size*0.30), Vector2(x + w, y + font.get_ascent(font_size) - font_size*0.30), Color("#8f8474"), 2.0)`
     - `w`＝该段文字宽度，用 `font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x`
  4. 字号 17、行高 26、墨色 `#3a2f22`
  5. sep 段画一行淡色小圆点（照 `_mdtest/render3.gd:27` 的 `· · · · · · · ·`，颜色 `#b0a080`）
  6. indent 段按固定缩进量偏移
- **换行**：中文字符按宽度逐字累加，超出可用宽度就换行（行高 26）。**不要**依赖 `draw_string` 的自动换行（它不换行，只裁切）
- 提供 `set_content(segments: Array)` 供外部灌数据

### §3.3 第三件：`scripts/diary_texts.gd`（新建，数据）

把 §2.7 的四份原稿抄进去。

⚠️ **逐字抄**。抄完必须做一次校验：
- 把 `scripts/diary_texts.gd` 里的四段文本与 `docs/story.md` 对应段落做逐字比对（可以写个临时 python 脚本比对，或在 `_mdtest/diary_render_check.gd` 里断言关键行存在）
- 特别核对：附一.2 的四个 `{{}}` 标记、附一.3 的四笔金额与「陆婶」→「陆先生」、附一.4 的「疑非陆万山」「到此为止。后面空白。」

### §3.4 第四件：`scripts/diary_view.gd`（新建，双本界面）

**并排两页**（照 `_mdtest/render3.gd:35-55` 的布局思路，但用正式的自绘控件）：

- 左边＝假本《水簿》（纸色 `#e8ddc0`、整齐）
- 右边＝真本《水簿》（纸色 `#e2d6b4`、有划痕）
- 两页各带一个小标题（假本 · 誊清 / 真本 · 原稿，标题色 `#6a5a48`，字号 13 —— 照 `_mdtest/render3.gd:113-117`）
- 页面之间留 18px 间隔（`_mdtest/render3.gd:44` 的 `separation`）
- 整页有一个压暗底（照 `_mdtest/render3.gd:36-39` 的 ColorRect `#efe6d0`）

**不许**用 `HBoxContainer` + `PanelContainer` 那套（那是实验版）；正式版用自绘，两个 `DiaryPage` 手动摆位置即可（这样删除线的自绘不会和容器布局打架）。

### §3.5 第五件：接线（**最后一步，且必须等 L17 交付**）

参照 `scripts/main.gd` 里证物档案的现成做法：
- preload 区加 `const DiaryView = preload("res://scripts/diary_view.gd")`
- 状态区加 `var diary_view: Control = null`
- 仿 `_make_archive()`（`scripts/main.gd:76-80`）加一个 `_make_diary_view()`，动态挂 Main 下
- `scripts/main.gd:143-147` 的「档案开着时游戏逻辑全停」处 ⇒ **日记开着时同样要停**
- 触发键：**自己定**，不要占用 SHIFT/E/I/WASD；建议用**裸键轮询**（照 `scripts/main.gd:106-126` F11 的做法），**不要改 `project.godot`**（改了要重启编辑器才生效，对「贴任务书去新开会话」不友好）

### §3.6 第六件：`_mdtest/diary_render_check.gd`（新建，本线专属）

**必须断言，不许只在文档里写**：

| 编号 | 断言 |
|---|---|
| D1 | `{{A|B}}` 假本 ⇒ 只有 B，**无 strike 段** |
| D2 | `{{A|B}}` 真本 ⇒ strike(A) + red(B) 两段 |
| D3 | `{{A|B|C|D}}` 真本 ⇒ strike(A) + 「…」 + red(D)（**不出现 B、C**） |
| D4 | `{{A|B|C|D}}` 假本 ⇒ 只有 D |
| D5 | `---` ⇒ sep 段（**假本也要有**） |
| D6 | 行首制表符 ⇒ indent 段 |
| D7 | `{{` 没闭合 ⇒ 原样保留，**不吞内容** |
| D8 | 四份原稿的**关键行**在 `diary_texts.gd` 里存在（逐字断言，例如「疑非陆万山」「到此为止。后面空白。」、「陆婶」「陆先生」） |
| D9 | 真本渲染里**存在** strike 段、假本渲染里**不存在** strike 段 |
| D10 | 解析器**不产生** RichTextLabel 的 `[s]`/`[color]` 之类 BBCode 字符串（自绘版不该输出 BBCode） |

⚠️ headless 下**画不出图**，所以 D9 这类「视觉断言」要用**解析结果**来断言（段类型），不要靠截图。

### §3.7 第七件：文档

**新建 `docs/FEEDBACK-diary-render-exec.md`**（≤120 行，见 §5.3）。
**不写** `docs/story.md`、`docs/npc.md`、`docs/diary-markup.md`（本线不产叙事、不改语法文档）。
**不改** `docs/PROMPT-overseer.md`、`docs/待解决事项.md`（总策划回写）。

---

## §4 验收

### §4.1 行为自检

`_mdtest/diary_render_check.gd` 的 D1–D10 全过。

### §4.2 七套回归

七套全跑全绿，且**输出逐行不变**（本线不该影响任何既有机制）。
有变化必须查清原因并写进反馈文档。

### §4.3 实机验证（沙箱里做不了窗口，真机做）

1. 打开日记界面 ⇒ 左右两页并排
2. **假本那页**：看不到任何删除线、没有红字，版式整齐
3. **真本那页**：能看到**灰色的带删除线的旧字** ＋ 红色的改正字
4. 删除线**粗细看得清**（不是一条几乎看不见的细线）—— 这是本线的验收重点
5. `{{三十|三|二十|三十}}` 那处显示成「三十（划掉）… 三十（红）」，**中间两段不出现**
6. `---` 显示成淡色小圆点行
7. 两页纸的**纸色不同**（假本偏白、真本偏黄）
8. 关掉界面 ⇒ HUD 恢复、走动正常
9. 日记开着时按 WASD ⇒ **世界不动**

### §4.4 交付物检查清单

- [ ] 三个新文件 `scripts/diary_markup.gd`、`diary_page.gd`、`diary_view.gd` ＋ `diary_texts.gd` 都在
- [ ] `_mdtest/diary_render_check.gd` 存在且 D1–D10 全过
- [ ] 七套回归全绿且输出不变
- [ ] `scripts/diary_page.gd` 里 grep `RichTextLabel` **零命中**（必须自绘）
- [ ] `scripts/diary_page.gd` 里 grep `draw_line` **有命中**（删除线自绘）
- [ ] `scripts/diary_markup.gd` 里 grep `\[s\]` **零命中**（不用 BBCode 删除线）
- [ ] 四份原稿与 `docs/story.md` 逐字一致
- [ ] `docs/FEEDBACK-diary-render-exec.md` ≤120 行

---

## §5 收工

### §5.1 精确 add（**绝不 `git add -A`**）

```
git add scripts/diary_markup.gd scripts/diary_page.gd scripts/diary_view.gd scripts/diary_texts.gd
git add _mdtest/diary_render_check.gd docs/FEEDBACK-diary-render-exec.md
# 只有真的改了 main.gd 才加：
git add scripts/main.gd
```

### §5.2 三段 commit

```
① git commit -m "feat(diary): 双日记标记解析 + 自绘纸页（删除线自绘）"
   （scripts/diary_*.gd + _mdtest/diary_render_check.gd）

② git commit -m "feat(diary): 双本对照界面接入主流程（接线，若 L17 已交付）"
   （scripts/main.gd）

③ git commit -m "docs: 双日记渲染执行反馈"
   （docs/FEEDBACK-diary-render-exec.md）
```

**若 L17 未交付**：只做 ①③，把 ② 的接线补丁（完整代码片段）写进反馈文档，等 L17 交付后补做。

### §5.3 反馈文档 `docs/FEEDBACK-diary-render-exec.md`（≤120 行）必须包含

1. 一句话结论
2. 四个新文件各自的职责与关键行号
3. **删除线自绘**的实现细节（位置公式、粗细、宽度怎么算）与实机观感（够不够粗）
4. 多段涂改折叠规则的实际实现
5. 四份原稿的**逐字校验结果**（怎么比对的、差异为零的结论）
6. `_mdtest/diary_render_check.gd` 的 D1–D10 逐条结果
7. 七套回归输出对照（应逐行不变）
8. **实机验证结果**（§4.3 九条逐条：做了/没做/为什么做不了）
9. 已知缺口与取舍（尤其：解锁时机归谁、要不要做滚动、要不要做翻页）
10. 接线状态（L17 是否已交付；本线是否自己接了 main.gd）

---

## §6 边界提醒

1. **只精确 add 自己的文件**；美术线 11 张 `_ref/art/*.png` 与用户删的 `美术资产/**` 一个都不许碰
2. **不许改** `data/frames.json`、`_ref/houses/houses_data.json`、`scripts/house_shape.gd`、证物三件套、`scripts/hud.gd`、`scripts/world_view.gd`、`scripts/player.gd`、`scripts/timeline.gd`、`scripts/frame_data.gd`
3. **不许改** `_mdtest/` 里除新建 `diary_render_check.gd` 外的任何套件的断言；**不许删** `_mdtest/render*.gd`/`demo*.gd`/`diary_test.gd` 这些实验脚本
4. **不许**用 `RichTextLabel` + `[s]` 当最终删除线实现（线太细，`docs/diary-markup.md:52-63` 已定必须自绘）
5. **不许**引入字体文件（Godot 默认字体自带 CJK）
6. **不许**改写/润色 `docs/story.md` 附一的四份原稿
7. **不许**在日记里加任何注解（尤其附一.3 的「陆婶」→「陆先生」处，`docs/story.md:890` 明写「这一处不许有任何注解」）
8. 本线**不写**叙事、不改 `docs/story.md`/`docs/npc.md`/`docs/diary-markup.md`
9. 本线**不改** `docs/PROMPT-overseer.md`、`docs/待解决事项.md`
10. 落盘后扫一遍 `'\ufffd'`（中文乱码检查）
11. 改 `project.godot` 需重启编辑器才生效 ⇒ **默认别改**，用裸键轮询

---

## §附 依据

| 文件 | 位置 | 作用 |
|---|---|---|
| `docs/diary-markup.md` | 全文 145 行 | **语法的权威出处** |
| `docs/diary-markup.md` | `:36-50` | 配色与排版实测参数（定稿值） |
| `docs/diary-markup.md` | `:52-63` | 🔴 删除线必须自绘 |
| `docs/diary-markup.md` | `:65-73` | 中文渲染＝Godot 默认字体自带 CJK |
| `docs/diary-markup.md` | `:75-93` | BBCode 可用性参考与坑 |
| `docs/diary-markup.md` | `:95-118` | 三个陷阱（线太细 / 多段折叠 / 假本也要处理 `---`） |
| `docs/diary-markup.md` | `:122-143` | 原稿示例 |
| `docs/story.md` | `:288-368` §5 | 双日记设定、动机、揭晓节奏、最冷的一刀、最后一笔、暗龛流转 |
| `docs/story.md` | `:305` | 「假本写得比真本整齐」 |
| `docs/story.md` | `:797-818` | 附一.1 假本誊清全文 |
| `docs/story.md` | `:827-859` | 附一.2 真本原稿全文 ＋「这一页里发生了什么」表 |
| `docs/story.md` | `:865-894` | 附一.3 周有田往来账（含「陆婶」→「陆先生」） |
| `docs/story.md` | `:900-905` | 附一.4 陆敬之残页 |
| `docs/story.md` | `:910-936` | 附二 标记语法复述（与 diary-markup.md 对照） |
| `_mdtest/render3.gd` | `:58-77` `_render` | **可搬**：标记扫描解析器 |
| `_mdtest/render3.gd` | `:80-95` `_emit` | **可搬**：多段折叠规则（BBCode 版，需改写成自绘段） |
| `_mdtest/render3.gd` | `:98-129` `_page` | **可搬**：纸色/边框/圆角/标题的视觉参数 |
| `_mdtest/render3.gd` | `:27` / `:30-32` | 分隔符常量与试色（**试色已被 diary-markup.md 取代**） |
| `_mdtest/diary_test.gd` | `:58-62` | 未知 BBCode 标签会留在文本里（自绘版天然规避） |
| `scripts/evidence_archive.gd` | `:1-70` | 风格模板（自绘 Control、`set_anchors_and_offsets_preset`、`is_open()`） |
| `scripts/main.gd` | `:74-94` | `_make_archive()` / `_set_hud_hidden()` 的现成做法 |
| `scripts/main.gd` | `:106-126` | 裸键轮询＋边沿检测（本线抄它做触发键） |
| `scripts/main.gd` | `:143-147` | 「档案开着时游戏逻辑全停」（日记接入点） |
| `docs/PROMPT-overseer.md` | `:237-252` | 任务书骨架 |
| `docs/PROMPT-overseer.md` §四 | `:147-158` | 写者锁 |
| `docs/PROMPT-overseer.md` §十一 | — | 「现在就能开/不能开」表（判断 L17 是否在跑） |
