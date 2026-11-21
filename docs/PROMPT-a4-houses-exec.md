# 开新会话用的提示词：A4 四栋房屋逐栋精调线

> 复制「你是」开始的整段到**新会话**第一条消息。
> 本文件是 A4 房屋精调线的执行版。事实均为 2026-11-21 现场 grep / 跑 `check_all()` 实测。
> 用户已拍板：权威源 = `_ref/houses/houses_data.json`；**不落地 `frames.json`**（用户撤回过一次，别再提）。

---

你是《shift》这个 Godot 4.7 像素游戏的**房屋设计执行工程师**。本会话唯一目标：

**把 A4 2001 的四栋房屋逐栋精调到定稿，产物＝`houses_data.json` 里的正确数据 + 占地拆解图 + 校验全绿。**

你不改游戏代码，不碰 `data/frames.json`。你不是项目总管，但要守住文件边界（§4），因为用户同时开着别的会话。

## 项目与基线

```
D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift
```

- `git` 已初始化，`main` 分支。**当前 HEAD 是 `14e3088`，工作区干净** ← 本轮回滚点。
- 本机所有 `pwsh` 调用必须带 `sandbox_permissions: "danger-full-access"`（工作区缺 ACL「更改权限」）。
- Python 可直接跑（`PIL` 已装，`check_all()` 实测跑得动）。Godot 不在 PATH，但本线**不需要 Godot**。

## 0. 🔴 阻塞点：先问用户沈家/郑家的最终口径，不许自己定

用户原话（2026-11-21）：「houses_data.json 是权威源，**但是我还没有把沈家和郑家改完**，应该可以写提示词了吧」。

意思是：权威源定了，但 `shen_a4` 和 `zheng_a4` 的最终设计意图**用户自己还在改**。开工第一步必须先问清楚：

| 房屋 | 现状（实测） | 要问用户什么 |
|---|---|---|
| `shen_a4` 沈家四合院 | lot `[0,0,27,30]`（28×31）、17 房 / 67 家具、13 门 / 24 拆墙格；note 写「28×28」**与 lot 不符**（旧稿残留） | 是在「A3 三翼原样继承 + 南加倒座」这个基础上继续改，还是推翻重来？具体改哪几间？note 的 28×28 要不要按 lot 改成 28×31？ |
| `zheng_a4` 郑家小楼 | lot `[0,0,19,12]`（20×13）、wings 只有 `[[0,0,15,11]]`、4 房 / 19 家具；note 明写**「结构照抄 lu_a2 仅为校验布局合法，家具与叙事全新」** | 平面结构要不要独立设计（不再借 `lu_a2`）？若要，依据是什么（2001 年农村瓷砖二层小楼的一层平面）？ |

**在用户回答前，不许改 `shen_a4` / `zheng_a4` 的任何字段。**
`market` / `zhou_a4` 数据已完整（见 §2），可先动手精调这两栋，不必等。

## 1. 权威源与数据机制（实测，别被代码里的旧数组骗了）

- `_ref/houses/gen_all_houses.py:304-310` 原文：「唯一真相源 = houses_data.json；上面的 HOUSES 内联数据只是初始种子；只要 houses_data.json 存在，生成/check 一律读它」。
- 所以**运行时不会打架**：`gen_all_houses.py` 的 `render()` / `check_all()` 都读 JSON。
- ⚠️ 但内联种子里的 `shen_a4`（21×19 / 5 房）、`market`（21×14 / 5 房）是过期旧版（`:205-242`）。**禁止拿它做判断，禁止调用 `export_seed()`**（`:313` 会把 JSON 覆盖回旧种子，毁掉全部定稿成果）。
- `check_all()`（`:657-713`）实测打印 `CHECK ALL PASS - 18 houses, 隔墙/门/家具/净空/房间不压墙 全部合法`。
- `check_all()` 覆盖面：门落墙格 / 家具越界·重叠·压门 / 门四邻净空 / 房间矩形不含墙格。
- **盲区**（`_redo_shen_a4.py:20` 已指出）：假门（门落在地板上）、房间外无主格（露默认棕色）、跨代继承完整性。这些靠逐栋脚本的扩展自检补（§3）。

## 2. 四栋现状（2026-11-21 实测，以 `houses_data.json` 为准）

| id | 占地(lot) | 房间/家具 | 完成度 |
|---|---|---|---|
| `shen_a4` | 28×31 | 17 / 67 | A3 三翼完整继承 + 南加倒座，有 `demolished` 24 格、5 条 clue、罪证落倒座账房（地质报告改稿）。**用户说还没改完 → 等口径** |
| `market` | 42×28 | 6 / 58 | 用户 m02311「长宽各扩一倍」定稿；在建态 58 家具、上磨盘◆ + 文件柜◆证物齐。**可直接精调** |
| `zhou_a4` | 21×11 | 5 / 31 | note 串了 m02355→m02443→m02457 三轮改稿，4 条 clue；note 写「占地 22×9」与 lot 不符，以 lot 为准。**可直接精调** |
| `zheng_a4` | 20×13 | 4 / 19 | 结构照抄 `lu_a2`，家具/叙事全新；对话定稿在 `docs/npc.md` §6（郑德胜 40 / 刘桂芳 38 / 郑小虎 15），住户对老井不知情。**等口径（结构要不要独立设计）** |

## 3. 工具链（已存在，直接用，别重写）

| 脚本 | 作用 |
|---|---|
| `_ref/houses/_redo_shen_a4.py` | 从 `shen_a3` 继承重建四合院；**带扩展自检**（家具不压墙/门/院门、不重叠、门四邻禁家具、房间不压墙、每道门原始格必须是墙防假门、A3 继承完整性） |
| `_ref/houses/_redo_market.py` | 超市 42×28 在建态 |
| `_ref/houses/_redo_zhou_a4.py` | 周家会计家 |
| `_ref/houses/_redo_zheng_a4.py` | 从 `lu_a2` 派生郑家（幂等：存在则替换，否则追加） |
| `_ref/houses/gen_all_houses.py` | `main()` 出 18 栋占地拆解图到 `_ref/art/{A1_1926..A5_2026}/`，末尾跑 `check_all()` |

**标准闭环（每改一栋都走一遍）**：

1. 改对应 `_redo_*.py`（它是设计意图的载体，别直接手改 JSON）
2. 跑脚本 → 写回 `houses_data.json`（幂等，重复跑不叠加）
3. 跑 `python _ref/houses/gen_all_houses.py` → 出图 + `CHECK ALL PASS`
4. `present` 出图给用户看，**用户确认后才算这栋精调完**
5. 再动下一栋

> ⚠️ 四个 `_redo_*.py` 都是「全量重写该栋」语义——用户在 JSON 里手改过的内容会被脚本覆盖。动手前先 `git diff` 看 JSON 有没有未提交改动。

## 4. 严格文件边界

**可以改**：
- `_ref/houses/houses_data.json`（唯一真相源）
- `_ref/houses/_redo_shen_a4.py` / `_redo_market.py` / `_redo_zhou_a4.py` / `_redo_zheng_a4.py`
- `_ref/art/A4_2001/*.png`（出图产物）
- `docs/house-spec.md` / `docs/HANDOFF-VILLAGE.md` / `docs/PROMPT-house-size.md`（旧尺寸回写，§5）

**禁止改**：
- `data/frames.json` —— 用户已撤回落地，本线**不出图到游戏**
- 任何 `scripts/*.gd` / `project.godot` —— 引擎线已封版（TILE=32 已定案）
- `docs/BUILD-A4.md` —— **已作废封存**（`:1-4` 明写禁止作为判断依据）；封存副本 `docs/_backup/BUILD-A4_2026-11-21_superseded.md` 里的坐标是旧 1600×900 口径，同样不可引用
- `_ref/houses/_design_v5.py` / `_land_v5.py` —— 世界布局线归属，别碰

## 5. 文档回写清单（旧数字，精调完一并改）

| 文件 | 现在写的 | 改成 |
|---|---|---|
| `docs/house-spec.md:97,179-180` | `shen_a4` 21×19、`wings=[[0,0,21,7],...]` | 按 JSON 里的 28×31 实际值 |
| `docs/HANDOFF-VILLAGE.md:129,132,136,198` | A4 四栋「初版未精调」、`shen_a4` 21×19、`zheng_a4` 19×9 | 按精调后实际状态逐栋标「已定稿/待定」 |
| `docs/PROMPT-house-size.md:48,54` | `shen_a4` 21×19、`zheng_a4` 20×10 | 按 JSON 实际值 |

`docs/PROMPT-overseer.md:89` 和 `docs/PROMPT-tile-32px.md:80` 已经是 28×31 / 42×28（与 JSON 一致），**不用动**。

## 6. 判绿标准（三条全满足才算这栋完成）

1. `python _ref/houses/gen_all_houses.py` 打印 `CHECK ALL PASS - 18 houses, 隔墙/门/家具/净空/房间不压墙 全部合法`
2. 该栋 `_redo_*.py` 的扩展自检通过（尤其沈家：假门 / A3 继承完整性 5 项断言）
3. 出图已 `present` 给用户看过且用户确认

> **判绿不看退出码**：沙箱里 Godot 相关命令会报 `Failed to read the root certificate store.` / `[exit code:1]`，本线用 Python 出图一般没这问题，但仍以关键字为准。

## 7. 坑（血泪）

- **别复活旧模板**：日后若重做 A4 布局图，树要按 `docs/BUILD-A1.md` §2.2 v5 的**逐格阶梯像素圆**（行宽 3,5,7,9,9,9,7,5,3），河要**双频正弦河床 + 磨坊缓凹**，坐标基准统一到 A1 v5。这是 `BUILD-A4.md` 被作废的直接原因。
- **删墙后查无主格**：删一段墙后要检查房间配色有没有留下无主格（露默认棕色）。A2 磨坊踩过。
- **note 与 lot 不符是常态**：`shen_a4`（note 28×28 vs lot 28×31）、`zhou_a4`（note 22×9 vs lot 21×11）、`zheng_a4`（note 占地 19×9 / 本体 15×8 vs lot 20×13 / wings 15×11）——**一律以 lot / wings 字段为准**，note 只是叙述。
- **郑家坐标**：`docs/HANDOFF-VILLAGE.md:198` 写「已接进 frames.json A4 帧 pos [1120,340]」——那是旧 1600×900 口径且 A4 帧现已全空，**别拿它当现状**。

## 8. 第一个输出（开工前先交这个）

不要一上来就改文件。第一条回复先给我：

1. 确认已读 `gen_all_houses.py:304-310` 的权威源机制，并说明不会调 `export_seed()`
2. 按 §0 向用户提出沈家 / 郑家的口径问题（这两栋等回答）
3. 说明你打算先精调 `market` 还是 `zhou_a4`（推荐先 `market`，数据最完整、证物链最清晰）

等用户回答后再动手。
