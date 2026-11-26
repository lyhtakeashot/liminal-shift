# L15 · 归档表 + 结局变体 执行提示词

> 这条线把《阈限迁移》最缺的那半块做出来：**「推理—结案」**。
> 现在的游戏只有「探索—观察—归档」：玩家在五帧里走、按 E 看物证、按 I 翻档案。
> 但游戏还没有「把物证填成一份卷宗、然后按你填的东西生成结案记述」——
> `docs/story.md` §10 已经把表格、三个记述变体、两个出口全部写死了，本线负责把它变成能玩的。

---

## §0 开工前

### §0.1 路径与工具

- 仓库根：`D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift`
- Godot：`D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe`（**不在 PATH**）
- 跑回归（**看关键字不看退出码**；沙箱噪声 `Failed to read the root certificate store.` 属正常）：

```
& "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe" --headless --path . -s res://_mdtest/xxx_check.gd 2>&1 | Select-Object -Last 45
```

七套回归：`_mdtest/greybox_check.gd`、`camera_check.gd`、`hud_layout_check.gd`、`asset_draw_check.gd`、`sort_check.gd`、`evidence_archive_check.gd`、`display_check.gd`

### §0.2 HEAD 下限

开工前 `git log --oneline -1` 必须是 **`3f5bc49`** 或更新。
若 HEAD 早于它，**停下报告**。

### §0.3 开工前先跑基线

七套全跑一遍，输出存 `lab/_l15_baseline.txt`。**基线有红项就停下报告。**

### §0.4 脏工作区纪律

- `M _ref/art/A1_1926/*.png` 等 11 张 ＝ 美术线，**一个字都不许碰**
- `D 美术资产/**` ＝ 用户自己删的，**不许恢复**
- **只精确 `git add` 自己那批文件，绝不 `git add -A` / `git add .`**
- **不许 `git checkout -- <file>`**（沙箱拦），要还原用 `git show HEAD:<path>` 按字节写回
- 长文件改不动长行时用 python 按行号改，脚本放 `lab/`

### §0.5 本线要碰的文件（**允许改/新建**）

| 文件 | 说明 |
|---|---|
| **新建** `scripts/ending_form.gd` | 归档表界面（Control，挂在 Main 下，与证物档案同层） |
| **新建** `scripts/ending_report.gd` | 记述生成器（把玩家填的内容变成 §10.3 的三种记述之一） |
| **新建** `scripts/ending_store.gd` | 填格结果与存档（**独立于 `evidence_store.gd`**） |
| **新建** `_mdtest/ending_check.gd` | 本线专属回归 |
| **新建** `docs/FEEDBACK-ending-form-exec.md` | 反馈文档，≤120 行 |
| `scripts/main.gd` | **仅最后一步的接线**（见 §5.2），且必须等 L17 交付 |

### §0.6 本线**不许碰**的文件

- `data/frames.json`（L1 独占）
- `_ref/houses/houses_data.json`
- `scripts/house_shape.gd`（L4 独占）
- `scripts/evidence_store.gd`、`scripts/evidence_archive.gd`（证物域，**不要**把归档表塞进证物档案）
- `scripts/world_view.gd`（L2/L8 独占）
- `scripts/hud.gd`（L17 独占）⇒ **归档表必须是独立 Control，不能往 HUD 里画**
- `scripts/player.gd`、`scripts/timeline.gd`
- `scripts/frame_data.gd`
- `assets/**`、`_ref/art/**`
- `docs/story.md`、`docs/npc.md`（**只读**；本线不写叙事）
- `_mdtest/` 里除新建的 `ending_check.gd` 之外的所有套件 —— **它们的断言一条都不许改**

### §0.7 与 L17（phasing 线）的串行

- L17 独占 `scripts/main.gd`、`scripts/hud.gd`、`scripts/timeline.gd`、`scripts/player.gd`、`scripts/world_view.gd`。
- 本线**除了最后一步接线，其余全部工作都不碰这些文件** ⇒ 主体部分可以与 L17 并行。
- 唯一要碰 `main.gd` 的是 §5.2 的接线（5 行左右）。
  ⇒ **开工前看 `docs/PROMPT-overseer.md` §十一「现在就能开/不能开」表**：
  - 若 L17 **正在跑** ⇒ 本线做到「所有文件都写好、只差 main.gd 接线」就**收工**，把接线补丁写进反馈文档，**等 L17 交付后再补**。
  - 若 L17 **已交付**（`scripts/main.gd` 没有别人的 WIP）⇒ 本线可以自己接完。

---

## §1 独占写入文件

本线**独占**（同一时间不许别的线碰）：

1. `scripts/ending_form.gd`
2. `scripts/ending_report.gd`
3. `scripts/ending_store.gd`
4. `_mdtest/ending_check.gd`
5. `docs/FEEDBACK-ending-form-exec.md`

本线**可小改**（且必须串行）：`scripts/main.gd`（仅接线）。

---

## §2 数据基准（**真相全部在 `docs/story.md` §10，本线不另编内容**）

### §2.1 表格长什么样（`docs/story.md:633-658`）

玩家在 A5，站在超市里，屏幕下方是这张表。表头固定：

| 字段 | 值 |
|---|---|
| 卷宗号 | 7231001 |
| 地点 | ██村 东街 |
| 事件 | 连续非自然死亡 |
| 归档员 | 随当前帧变（见 §2.5） |

表体五行 × 两列下拉：

| | 动机形态 | 故意形态 |
|---|---|---|
| 1926 陆文 19 | 激情 / 蓄谋 / 放任 / 无 | 直接故意 / 间接故意 / 过失 / 无 |
| 1951 陆敬之 24 | 同上 | 同上 |
| 1976 方某 ? | 同上 | 同上 |
| 2001 —— | 同上 | 同上 |
| 2026 沈明远 | 同上 | 同上 |

外加四个单选（`docs/story.md:633-658`）：

| 字段 | 选项 |
|---|---|
| 1951 案的性质 | 杀人灭口 / 债务纠纷 |
| 最早一具 | 1926 / 1951 / 1976 / 无法确定 |
| 埋尸位置 | 补丁下 / 井下 / 地基下 / 无法确定 |
| 埋葬人数 | 一 / 二 / 三 / 无法确定 |

另有两行**自动生成、玩家不能改**：
- 「未寻获死者一（陆文，民国十五年，下游）」
- 「死者二」＝自动生成

**设计约束（不许改）**：
- **没有默认值、没有提示哪个对**（`docs/story.md:653`）
- 玩家填错**不报错**，只让最后的记述降级（`docs/story.md:668`）

### §2.2 正确答案与「允许的错」（`docs/story.md:660-668`）

| 字段 | 事实 | 玩家可能填 |
|---|---|---|
| 最早一具 | **1951** | 1926（事实错） |
| 埋尸位置 | **补丁下** | 井下（**也对** —— 井就在补丁下，但井不是位置的下限） |
| 埋葬人数 | **二** | 三（把失踪的陆文算进来） |

**注意**：不是「填对/填错」二元，而是**每一格都可能合法地不同**。
因此实现上**不要**写成「每格一个正确值 + 判对错」，而要写成**记述生成器按填的内容走分支**。

### §2.3 记述生成器（`docs/story.md:688-742`）

「这一栏自动生成，玩家不能改。它只是把你填的东西念出来。」

**三个变体（按填的内容分流，不是按「对错」分流）**：

**变体甲（`docs/story.md:692-709`）** —— 1951 填「债务纠纷」、最早一具 1951、埋尸位置补丁下、埋葬人数二 ⇒ 全段记述（含「最早一具：一九五一年。埋尸位置：北车道圆形补丁下。埋葬人数：二。未寻获：一（陆文，民国十五年，下游）。」与「五代之中：起意者一，动手者二，算计而未动手者一，不知情者一。第一起无起意。第四起无死者。」与「一九五一年一起，性质：债务纠纷。死者陆敬之，男，二十四岁。本地点自民国十六年起向陆家支付款项三十七笔，至四十年止。没有人被平反。因为没有人是无辜的。」）

**变体乙（`docs/story.md:711-721`）** —— 1951 填「杀人灭口」⇒ 只剩两句：「三十七笔款一个字都不出现。档案上他只是个受害者。」

**变体丙（`docs/story.md:723-742`）** —— 某几格填「无法确定」⇒ 不报错只降级；
**但这两句照样在，因为它们不是玩家填的，是表自己算出来的**：「第一起无起意。第四起无死者。」（`docs/story.md:732-736`）

⇒ **实现要点**：这两句是**表算出来的**（依据 `docs/story.md` §4.6.1 五件事的落表），**不是玩家填的**，所以无论玩家怎么填都会出现。这是全片最硬的地方，**不许简化掉**。

### §2.4 两个出口（`docs/story.md:744-770`）

提交时二选一：

- **出口甲·已归档**（`docs/story.md:748-753`）：「本案已归档。世界刑侦陈列馆 · 第七十二万三千零一卷」
- **出口乙·存疑**（`docs/story.md:755-760`）：「本案存疑。第七十二万三千零一卷 · 暂列待考」

之后（`docs/story.md:762-780`）：
- 「两段之间，世界一模一样。」
- 超市继续营业。收银机在响。沈明远正在小学剪彩。
- 「唯一的区别是：这份卷宗以后会被人怎么读。」
- 然后——什么也没有发生：没有人被捕。没有人被平反。没有人知道。而陈列馆比所有人都活得长。
- ⚠️ `docs/story.md:780`：「**不要写『正义得到伸张』。一句都不要。**」

### §2.5 归档员名字随帧变（`docs/npc.md:33-39`）

| 帧 | 归档员 |
|---|---|
| 1926 | 陈阿福 |
| 1951 | 陈志强 |
| 1976 | 陈卫东 |
| 2001 | 陈小军 |
| 2026 | 陈浩 |

玩家在 A5 填表 ⇒ 归档员＝**陈浩**。
（若将来支持在别的帧填表，就按当前帧取。）

### §2.6 两套分类的出处（`docs/story.md` §4.6）

- 动机形态四档、故意形态四档：§4.6 两套表（`docs/story.md:206-211`）
- 五件事的落表：§4.6.1（`docs/story.md:213-221`）
  - A1 沈万山 放水未告 ＝ 放任 / 间接故意
  - A2 沈守业 灌醉·推井·填井 ＝ 蓄谋 / 直接故意
  - A3 沈德昌 把方师傅封进地基 ＝ 蓄谋 / 直接故意
  - A4 沈建国 改地质报告 ＝ 蓄谋 / 无
  - A5 沈明远 不知道 ＝ 无 / 无
- 玩家怎么推（不许靠猜）的判据：§4.6.2（`docs/story.md:223-246`）

⇒ **这两句「表自己算出来」的依据就在 §4.6.1**，实现时从这份表推导，不要硬编码成字符串拼接。

### §2.7 归档表与证物档案的关系（**必须分清**）

- **证物档案**（`scripts/evidence_archive.gd`，I 键）＝ 玩家**看到过什么**（一件物件一张卡，卡内按年追加观察）
- **归档表**（本线）＝ 玩家**怎么记**（把物证填成一份卷宗）

⇒ 两者是**两个界面、两套数据、两把键**。
**不要**把归档表塞进证物档案，也不要动 `scripts/evidence_store.gd`。

**建议的开放条件（实现方可调，但要在反馈文档里说明）**：
- 归档表在 A5 开放（`docs/story.md:631`「玩家在 A5，站在超市里」）
- **是否要求「证物已收齐」才开放，本线自决**；建议**不强制**（`docs/story.md:668` 明说填错不报错、没提示对错，强制收齐会变成任务清单，反而破坏设计）

---

## §3 必改清单

### §3.1 第一件：`scripts/ending_store.gd`（新建）

保存玩家填的格子。**独立于 `evidence_store.gd`，不要合并。**

最小字段：

```
var motive := {}      # key = "1926"/"1951"/"1976"/"2001"/"2026" → 动机形态
var intent := {}      # 同上 → 故意形态
var case_1951 := ""   # "杀人灭口" / "债务纠纷"
var earliest := ""    # "1926"/"1951"/"1976"/"无法确定"
var burial := ""      # "补丁下"/"井下"/"地基下"/"无法确定"
var count := ""       # "一"/"二"/"三"/"无法确定"
var exit_choice := "" # "已归档"/"存疑"
```

要求：
- 存档路径 **`user://ending_form.json`**（**不要**写 `res://`；Godot 的 `res://` 在导出版本里是只读）
- 要有版本号字段（照 `scripts/evidence_store.gd` 的 `SAVE_VERSION := 2` 的做法，自己定 `1`）
- **容错**：读档时字段缺失/值不合法 ⇒ 归位成空串（不要崩）
- 「未寻获死者一」「死者二」**不要存** ⇒ 它们是自动生成的（§2.1）

### §3.2 第二件：`scripts/ending_report.gd`（新建）

**纯逻辑，输入＝填格结果，输出＝记述文本。** 不碰 UI。

接口建议：

```
static func build(st: Dictionary) -> Dictionary
# 返回：{ "variant": "甲"/"乙"/"丙", "body": "……", "fixed": ["第一起无起意。", "第四起无死者。"], "exit_text": "……" }
```

实现要点：
1. **分流按 §2.3**：1951 案性质＝「杀人灭口」⇒ 变体乙；任一格＝「无法确定」⇒ 变体丙；否则变体甲。
   （变体乙/丙可以叠加：若既填了「杀人灭口」又填了「无法确定」，**以「无法确定」为准**（丙更宽），并在反馈文档里说明这个优先级。）
2. **「第一起无起意。第四起无死者。」两句永远出现**，依据 §4.6.1 的五件事落表推导，**不许写成玩家填的内容**
3. 文本风格照 `docs/story.md` §10.3 原文：**中文数字纪年**（「一九五一年」「北车道圆形补丁下」）、句号收尾、不用感叹号
4. 变体甲要包含「没有人被平反。因为没有人是无辜的。」这种硬句；变体乙**只**两句
5. **不要**出现「正义得到伸张」「真相大白」「凶手被绳之以法」这类词（`docs/story.md:780`）
6. 出口文本照 §2.4 两段原文

### §3.3 第三件：`scripts/ending_form.gd`（新建，界面）

**自定义绘制的 Control，不要用 `OptionButton` 弹出菜单**（Godot 的 PopupMenu 在自绘 overlay 里焦点/层级容易出问题，而且和证物档案的交互风格不一致）。
⇒ 用**循环选择器**：选中某格后按 ←/→ 或点击左右箭头，在选项间循环。

照抄 `scripts/evidence_archive.gd` 的成熟做法（**这是本线的风格模板**）：
- `:1` `extends Control`
- `:28-30` `const UI := 2.0` / `FONT := int(10*UI)` / `FONT_BIG := int(13*UI)`
- `:34` `const PANEL := Rect2(40.0, 16.0, 560.0, 310.0)`（**设计坐标 640×360 时代，乘 UI**）
- `:44` footer 文案常量 `FOOTER_PAUSED`
- `:58-64` `_ready()` 里 **`set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)`**（⚠️ **必须用带 OFFSETS 的版本**，只调 `set_anchors_preset` 的话动态 `add_child` 出来的节点 size 是 (0,0)，全屏压暗矩形坐标全错 —— `scripts/evidence_archive.gd:59-61` 有这个坑的注释）
- `:68` `func is_open() -> bool:` 对外接口
- `_handle_keys()` 自己处理方向键 / Enter / Esc

界面要素：
1. **卷宗抬头**：卷宗号 7231001 / 地点 ██村 东街 / 事件 连续非自然死亡 / 归档员（按当前帧，§2.5）
2. **五行两列**的表格，每格显示当前选项；可编辑格有高亮
3. **四个单选字段**（1951 案性质 / 最早一具 / 埋尸位置 / 埋葬人数）
4. **自动生成行**：「未寻获死者一（陆文，民国十五年，下游）」「死者二」—— 灰字，不可编辑
5. **记述区**：调 `ending_report.build()`，把 `body` 画出来（只读）
6. **两个出口按钮**：「已归档」/「存疑」
7. **footer**：操作提示 + 「世界已暂停 · 按 <键> 关闭归档表」

⚠️ **不要**用 `RichTextLabel` 以外的富文本；记述区是纯文本，直接 `draw_string` 逐行画（中文字体 Godot 默认自带 CJK）。

### §3.4 第四件：接线（**最后一步，且必须等 L17 交付**）

参照 `scripts/main.gd` 里证物档案的现成做法：

- `scripts/main.gd:16-19` preload 区加 `const EndingForm = preload("res://scripts/ending_form.gd")`
- `scripts/main.gd:37-46` 状态区加 `var ending_form: Control = null`
- `scripts/main.gd:76-80` `_make_archive()` 旁边加一个 `_make_ending_form()`，**动态建节点挂在 Main 下**（与证物档案同层）
- `scripts/main.gd:143-147` 那里已经有「档案开着的时候游戏逻辑全停」的处理 ⇒ 归档表开着时**同样要停**：
  - `:144` `player.walking = false`
  - `:145` `_set_hud_hidden(true)`
  - `:146` `return`
  ⇒ 归档表开启条件加进这个 early-return
- `scripts/main.gd:155-156` 附近加一个键触发（**键位自己定**，但不要占用 SHIFT/E/I/WASD）
- 退出出口后要 `_clear_hotspot()` + 恢复 HUD

**键位建议**：`F` 或 `Tab`。⚠️ `project.godot` 的 InputMap 里已有 move_up/down/left/right(WASD/方向键)、shift_axis(Shift)、inspect(E)、toggle_fullscreen(F11)、archive(I)。
⇒ **建议不新增 InputMap action**（改 `project.godot` 要重启编辑器才生效，对「贴任务书去新开会话」不友好），改用**裸键轮询**（照 `scripts/main.gd:106-126` F11 的做法：`Input.is_physical_key_pressed(KEY_…)` ＋ 边沿检测）。

### §3.5 第五件：`_mdtest/ending_check.gd`（新建，本线专属）

**必须断言，不许只在文档里写**。至少覆盖：

| 编号 | 断言 |
|---|---|
| E1 | 全部填对（1951 性质=债务纠纷 / 最早一具=1951 / 埋尸位置=补丁下 / 埋葬人数=二）⇒ 变体甲 |
| E2 | 1951 性质＝杀人灭口 ⇒ 变体乙，且**记述只剩两句** |
| E3 | 任一格＝「无法确定」⇒ 变体丙，**不报错** |
| E4 | 埋尸位置＝「井下」⇒ **不算错**，记述按「井下」念，不降级成错误 |
| E5 | **「第一起无起意。第四起无死者。」在所有变体里都出现** |
| E6 | 记述文本里**不出现**「正义得到伸张」「真相大白」「凶手」「绳之以法」等词 |
| E7 | 出口甲文本＝「本案已归档。世界刑侦陈列馆 · 第七十二万三千零一卷」；出口乙＝「本案存疑。第七十二万三千零一卷 · 暂列待考」 |
| E8 | 归档员名字＝按当前帧取（A5 ⇒ 陈浩） |
| E9 | 存档写盘→读回→字段完全一致；**字段缺失/非法值不崩**（喂一份脏 JSON 试） |
| E10 | 表格默认**全空**（没有默认值、没有提示哪个对） |

### §3.6 第六件：文档

**新建 `docs/FEEDBACK-ending-form-exec.md`**（≤120 行，见 §5.3）。
**不写** `docs/story.md`、`docs/npc.md`（本线不产叙事）。
**不改** `docs/PROMPT-overseer.md`、`docs/待解决事项.md`（总策划回写）。

---

## §4 验收

### §4.1 行为自检

`_mdtest/ending_check.gd` 的 E1–E10 全过。

### §4.2 七套回归

七套全跑全绿，且**输出逐行不变**（本线不该影响任何既有机制）。
若有变化，必须查清原因并在反馈文档里写明。

### §4.3 实机验证（沙箱里做不了窗口，真机做）

1. 进 A5 ⇒ 打开归档表 ⇒ 屏幕下方出现那张表
2. 逐格改选项 ⇒ 高亮跟着走，选项循环正常
3. 全填对 ⇒ 记述区出变体甲全文
4. 把 1951 性质改成「杀人灭口」⇒ 记述缩成两句
5. 把某格改成「无法确定」⇒ 不报错，记述降级，但「第一起无起意。第四起无死者。」仍在
6. 选出口甲/乙 ⇒ 各自文本正确
7. 关掉归档表 ⇒ **HUD 恢复显示**、检视卡正常、走动正常
8. 归档表开着时按 WASD ⇒ **世界不动**（暂停正确）

### §4.4 交付物检查清单

- [ ] `scripts/ending_form.gd` / `ending_report.gd` / `ending_store.gd` 三个新文件都在
- [ ] `_mdtest/ending_check.gd` 存在且 E1–E10 全过
- [ ] 七套回归全绿且输出不变
- [ ] 存档落在 `user://ending_form.json`，**没有**写 `res://`
- [ ] 记述文本里 grep「正义得到伸张|真相大白|绳之以法」**零命中**
- [ ] 归档表**没有**改动 `scripts/evidence_store.gd` / `evidence_archive.gd` / `hud.gd`
- [ ] `docs/FEEDBACK-ending-form-exec.md` ≤120 行

---

## §5 收工

### §5.1 精确 add（**绝不 `git add -A`**）

```
git add scripts/ending_form.gd scripts/ending_report.gd scripts/ending_store.gd
git add _mdtest/ending_check.gd docs/FEEDBACK-ending-form-exec.md
# 只有真的改了 main.gd 才加：
git add scripts/main.gd
```

### §5.2 三段 commit

```
① git commit -m "feat(ending): 归档表填格 + 记述生成器 + 两个出口（story §10）"
   （scripts/ending_*.gd + _mdtest/ending_check.gd）

② git commit -m "feat(ending): 归档表接入主流程（接线，若 L17 已交付）"
   （scripts/main.gd）

③ git commit -m "docs: 归档表执行反馈"
   （docs/FEEDBACK-ending-form-exec.md）
```

**若 L17 未交付**：只做 ①③，把 ② 的接线补丁（完整代码片段）写进反馈文档，等 L17 交付后由总策划或本线补做。

### §5.3 反馈文档 `docs/FEEDBACK-ending-form-exec.md`（≤120 行）必须包含

1. 一句话结论
2. 三个新文件各自的职责与关键行号
3. **变体分流规则**的实际实现（含「无法确定」与「杀人灭口」同时出现时的优先级决定）
4. 「第一起无起意。第四起无死者。」是怎么从 §4.6.1 推导出来的（不要只说「写死的」）
5. `_mdtest/ending_check.gd` 的 E1–E10 逐条结果
6. 七套回归输出对照（应逐行不变）
7. **实机验证结果**（§4.3 八条逐条：做了/没做/为什么做不了）
8. 已知缺口与取舍（尤其：与证物档案的关系、开放条件是否强制收齐、是否支持在非 A5 帧填表）
9. 接线状态（L17 是否已交付；本线是否自己接了 main.gd）

---

## §6 边界提醒

1. **只精确 add 自己的文件**；美术线 11 张 `_ref/art/*.png` 与用户删的 `美术资产/**` 一个都不许碰
2. **不许改** `data/frames.json`、`_ref/houses/houses_data.json`、`scripts/house_shape.gd`、`scripts/evidence_store.gd`、`scripts/evidence_archive.gd`、`scripts/hud.gd`、`scripts/world_view.gd`、`scripts/player.gd`、`scripts/timeline.gd`、`scripts/frame_data.gd`
3. **不许改** `_mdtest/` 里除新建 `ending_check.gd` 外的任何套件的断言
4. **不许**把归档表塞进证物档案（I 键是证物档案的）
5. **不许**给表格加默认值、加「正确答案」提示、加进度条式的完成度显示
6. **不许**在记述里写「正义得到伸张」类结论（`docs/story.md:780`）
7. 本线**不写**叙事文本（`docs/story.md`、`docs/npc.md` 只读）
8. 本线**不改** `docs/PROMPT-overseer.md`、`docs/待解决事项.md`
9. 落盘后扫一遍 `'\ufffd'`（中文乱码检查）
10. 存档写 `user://`，不写 `res://`
11. 改 `project.godot` 需重启编辑器才生效 ⇒ **默认别改**，用裸键轮询

---

## §附 依据

| 文件 | 位置 | 作用 |
|---|---|---|
| `docs/story.md` | `:615-782` §10 | **本线的全部真相来源** |
| `docs/story.md` | `:620-627` §10.0 | 归档表的读法（「归档表问的是物，不是痛。」） |
| `docs/story.md` | `:629-658` §10.1 | 表格结构与全部选项 |
| `docs/story.md` | `:660-668` | 正确答案与「允许的错」（填错不报错，只降级） |
| `docs/story.md` | `:670-686` §10.2 | 1951 案性质：两条都对，两条都不干净 |
| `docs/story.md` | `:688-742` §10.3 | 三个记述变体全文 |
| `docs/story.md` | `:732-740` | 「第一起无起意。第四起无死者。」＝表算出来的，永远出现 |
| `docs/story.md` | `:744-770` §10.4 | 两个出口 |
| `docs/story.md` | `:772-780` §10.5 | 然后什么也没有发生；「不要写正义得到伸张」 |
| `docs/story.md` | `:206-211` §4.6 | 动机/故意两套分类表 |
| `docs/story.md` | `:213-221` §4.6.1 | 五件事的落表（两句硬句的依据） |
| `docs/story.md` | `:223-246` §4.6.2 | 玩家怎么推（不许靠猜） |
| `docs/npc.md` | `:33-39` | 归档员名字随帧变 |
| `scripts/evidence_archive.gd` | `:1-70` | **风格模板**：自绘 Control、`set_anchors_and_offsets_preset`、`is_open()`、`_handle_keys` |
| `scripts/evidence_archive.gd` | `:59-61` | 动态节点的坑（必须带 OFFSETS） |
| `scripts/main.gd` | `:74-94` | `_make_archive()` / `_set_hud_hidden()` 的现成做法 |
| `scripts/main.gd` | `:106-126` | 裸键轮询＋边沿检测的做法（本线抄它做触发键） |
| `scripts/main.gd` | `:143-147` | 「档案开着时游戏逻辑全停」的位置（归档表接入点） |
| `scripts/evidence_store.gd` | `SAVE_VERSION`/`save`/`load` | 存档写盘的现成范式 |
| `docs/PROMPT-overseer.md` | `:237-252` | 任务书骨架 |
| `docs/PROMPT-overseer.md` §四 | `:147-158` | 写者锁（main.gd/hud.gd 的归属） |
| `docs/PROMPT-overseer.md` §十一 | — | 「现在就能开/不能开」表（判断 L17 是否在跑） |
