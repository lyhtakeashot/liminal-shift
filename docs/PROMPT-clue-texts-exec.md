# 新会话提示词：证物文案线 —— 补齐 A4/A5 六栋检视文本

> 整段复制给新会话作为第一条消息。本线**只写 `scripts/house_shape.gd` 里的 `CLUE_TEXTS` 常量**（加条目），别的什么都不碰。

你是《shift》Godot 4.7 像素叙事游戏的 **证物文案执行人**。

背景：`house_shape.gd` 的 `CLUE_TEXTS`（`:46-87`）目前只写了 A1–A3 十栋的家具检视文本。A4/A5 六栋的证物家具点开后会退化成占位句「「X」立在这里。」（`house_shape.gd:381`），玩家读不到任何线索。本线把这些文案补齐。

## 0. 开工前（必做）

```
项目：D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift
Godot：D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe
```

- 所有 pwsh 调用带 `sandbox_permissions: "danger-full-access"`。
- `git log --oneline -3` 确认 HEAD ≥ `091ac45`。低于它说明基准没就位，停下来问总策划。
- `git status --short` 会看到别的线的改动（美术资产 D 状态、`lab/` 未跟踪产物等）。**全部只读、绝不写、绝不 add**。
- 本线唯一写入文件：`scripts/house_shape.gd`，且**只允许在 `CLUE_TEXTS` 常量里加 A4/A5 条目**。文件其余部分（函数、其它常量、A1–A3 已有文案）一个字都不许改。

## 1. 匹配机制（别踩键名坑）

`house_shape.gd:357` 用 `texts.get(name, ...)` 取文案，**键 = 家具的 `name` 字段（中文名），不是 `short`、不是 id**。先从 `_ref/houses/houses_data.json` 实测每栋 clue 家具的 `name`，照抄成 key；写错一个字就取不到，仍显示占位句。

`hotspots()`（`:352-384`）只为**整个矩形落在房子 lot 内**的 clue 家具生成检视点（`:366-369`）；lot 外的（如磨坊院内「老井」）是世界级地标，由 frames.json 手写，不归本线。所以补文案前先核：`rect` 是否落在 lot 内——不在的家具写了也不会显示，别白写，但仍可补上以备将来。

## 2. 要补的六栋与 story 线索（实测清单）

| 房子 | clue 家具 name（照抄做 key） | story 依据 |
|---|---|---|
| `shen_a4` | 蜂窝煤炉 / 账桌 / 保险柜 | 沈建国改地质报告、桩基绕井；账桌承 A1–A3「沈氏丰源」账簿线 |
| `market` | 文件柜 / 上磨盘 | story.md:436 超市门厅上磨盘刻「沈氏丰源 · 一九五七」；文件柜＝证物 |
| `zhou_a4` | 保险柜 / 账桌 | 周有田往来账线（note 串了三轮改稿）；周家会计家 |
| `zheng_a4` | 无 clue 家具 | **刻意不知情**，什么都别加 |
| `toyshop` | 招牌小字 / 账柜 | story.md:437 玩具店招牌小字「本店由沈氏物业出租」；账柜＝周有田往来账 |
| `school` | 「周」界碑 | story.md:435/470-474 界碑嵌小学围墙，字磨掉一半只剩「周」，划地界＝这块地曾是周家的 |

`docs/story.md:426-440` 是现代物证清单，`:470-490` 是界碑详解，动笔前读这两段。

## 3. 写作纪律（硬约束，违反就是 bug）

- **只写看到什么，不写意味着什么**（`house_shape.gd:43-45`、`docs/BUILD-A1.md` §5）。例：界碑写「一块旧界碑，字磨掉一半，只能认出一个『周』」，**不要**写「这说明周家曾是地主」。
- **不剧透、时间线对齐**：A1 不点破「一九五七」（那是 A5 回读的线）；但 **A4/A5 时间线已到，可以点破**——`market` 上磨盘直接写「沈氏丰源 · 一九五七」是符合时间线的。
- 每条 1–2 句、口语、有具体细节（颜色/位置/缺口/笔迹），别写空泛的「很重要」「值得调查」。
- 沿用已有 A1–A3 文案的语气（`house_shape.gd:47-86` 是范本），保持同一叙事声线。
- 不新增、不删除、不改写 A1–A3 十条已有文案。

## 4. 验收（本线自己必跑）

- `grep -n 'CLUE_TEXTS' scripts/house_shape.gd` 确认只动了常量区；`git diff -- scripts/house_shape.gd` **只能看到 `CLUE_TEXTS` 里新增的六栋条目**，别的一行都没有。
- 实机（去掉 `--headless`）打开游戏，用 Shift 切到 A4/A5，走到对应家具按 E 检视，确认读到你写的文案而不是「「X」立在这里。」。
- 四套回归：`_mdtest/{greybox,camera,display,hud_layout}_check.gd`，跑法 `Godot --headless --path . -s res://_mdtest/<脚本>.gd`。**沙箱噪声 `Failed to read the root certificate store.` / `[exit code:1]` 是基线固有，判绿看关键字不看退出码**：`WORLD_OK` / `START_OK` / `WALL_BLOCKED` / `REACH_OK` / `UNEXPLAINED_BLOCKS=0` / `HOTSPOTS_OK`。文案是纯字符串常量，理论上不影响回归，但必须跑一遍证明没手滑改坏语法。

## 5. 收工

- 只 `git add scripts/house_shape.gd`，commit 信息 `feat: 补齐 A4/A5 六栋证物检视文案（CLUE_TEXTS）`。
- 报告写清：补了哪六栋/几条、哪几条因 rect 在 lot 外没生成检视点、实机 E 检视的验证结果、四套回归关键字结果。

## 6. 边界提醒（别的线在跑，别管它们）

- A4 地图线、A5 地图线都在写 `data/frames.json`（一帧一写者），**与你写的 `.gd` 完全错开**。
- 视觉机制线、消费点接入线此前改过 `house_shape.gd`，但都已提交、当前文件干净；**本线基于最新 HEAD 工作，别用旧副本覆盖**。
- 场景设计线改 `houses_data.json`，你只读它的 clue 家具 name，**绝不写这个文件**。
- 美术成品图线暂缓，与你无关。
- 不要推 GitHub（用户按定时指令推送）。
