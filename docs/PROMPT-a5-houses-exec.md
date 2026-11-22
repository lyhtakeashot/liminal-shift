# 新会话提示词：场景设计4 —— A5（2026）两栋房屋精调

> 整段复制给新会话作为第一条消息。本线**只改 `_ref/houses/houses_data.json` 里的 `toyshop` / `school` 两栋**，别的什么都不碰。

你是《shift》Godot 4.7 像素游戏的 **A5 房屋精调执行人**。

## 0. 开工前（必做，这是硬门槛）

```
项目：D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift
Godot：D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe
```

- 所有 pwsh 调用带 `sandbox_permissions: "danger-full-access"`。
- `git log --oneline -3` 确认 HEAD ≥ `eb6c7fa`。
- 🔴 **必须等「场景设计3」先把它对 `_ref/houses/houses_data.json` 的未提交改动 commit 掉**（`git status --short` 里该文件的 M 状态消失），你才能开工。否则你和它写同一个文件会互相覆盖。开工前在报告里记下当时的 HEAD 与 `git status` 截图/文本。
- 权威源＝`_ref/houses/houses_data.json`（18 栋）。`gen_all_houses.py:304-310` 在 JSON 存在时以它覆盖内联种子；**禁止调用 `export_seed()`**（`:313`，会把 JSON 覆盖回过期旧种子）。
- 前序转接文档：`docs/HANDOFF-VILLAGE.md` 与 `docs/HANDOFF-A4-REVIEW.md`（读，不写）。

## 1. 你的独占写入文件

| 文件 | 允许做什么 |
|---|---|
| `_ref/houses/houses_data.json` | **只改 `toyshop` 和 `school` 两个对象**。A1–A4 的 16 栋数据只读、绝不改。 |
| `_ref/houses/_redo_toyshop.py` / `_redo_school.py` | 可新建（幂等重写脚本，照 `_redo_zheng_a4.py` 的写法：带 `PREVIEW` 环境变量只出预览不写 JSON、存在则替换否则追加）。 |
| `_ref/art/A5_2026/` | 可新建/覆盖这两栋的预览图（`toyshop.png` / `school.png`），由 `gen_all_houses.py` 出图。 |
| `docs/HANDOFF-VILLAGE.md` | 只有在你改完两栋、且场景设计3 已交棒后，才可回写 A5 两行的状态（`:133-134`）。若场景设计3 仍持有该文件，就不写、留给文档回写线。 |

**绝不写**：`data/frames.json`、`scripts/*.gd`、`docs/house-spec.md`、任何 `assets/village/` 下的图、A4 四栋的数据或图。

## 2. 两栋当前实测数据（以 JSON 为准，note 是旧口径别信）

| ID | 名称 | lot | wings | 房间数 | 家具数 | note 旧口径（作废） |
|---|---|---|---|---|---|---|
| `toyshop` | 玩具店（A5 2026） | `[0,0,14,10]` = **15×11 格**（480×352px） | `[0,0,15,11]` | 3 | 8 | note 写「屋本体 15×9」——旧数字，以 lot/wings 为准 |
| `school` | 小学（A5 2026） | `[0,0,20,15]` = **21×16 格**（672×512px） | `[0,0,21,16]` | 4 | 9 | note 写「屋本体 21×12」——旧数字，以 lot/wings 为准 |

`docs/PROMPT-overseer.md:91` 与 `docs/PROMPT-tile-32px.md:84-85` 已是 15×11 / 21×16（与 JSON 一致）；`docs/PROMPT-house-size.md:52-53` 和 `docs/HANDOFF-VILLAGE.md:133-134` 还是旧数字——**这些文档交文档回写线，你只管数据**。

## 3. 精调口径（用户已定的叙事约束，别推翻）

从权威文档提取（读，不写）：

- `docs/npc.md` §6：郑家/周家人物设定；A5 是 2026 年。
- `docs/HANDOFF-VILLAGE.md:144-148` 的证物链：
  - 「周」界碑 → `school` 的围墙（`[1,10,2,1]`）；
  - 玩具店招牌小字「本店由沈氏物业出租」 → `toyshop` 店面北墙；
  - 周有田往来账 → `toyshop` 账柜（与 `zhou_house` 小桌同案，**同样待定**，别写成定论）；
  - A5 营业态的 `market` 才是正式超市（本线不动 `market`）。
- 玩具店是曾孙租沈家的楼（不算周家自有），小学是村小——保持设定。
- 两栋的 `clue` 家具要能支撑上述证物链；新增/挪动家具时保持「家具不压门、不越界、不重叠」的硬规矩。
- 内外严格 1:1；碰撞恒为整格 AABB（纯数据，`scripts/frame_data.gd:is_free()` 不引物理引擎）。

## 4. 标准闭环（每改一栋都跑一遍）

1. 写一个幂等脚本 `_ref/houses/_redo_<id>.py`（照 `_redo_zheng_a4.py` 的骨架：读 JSON → 替换/追加该 ID → `PREVIEW=1` 只出预览不写 JSON）。
2. 先 `MCS_PREVIEW=1 python _ref/houses/_redo_<id>.py` 出预览图，自己看布局（门/隔墙/家具/净空/房间矩形）。
3. 满意后 `python _ref/houses/_redo_<id>.py` 写回 `houses_data.json`。
4. 跑 `python _ref/houses/gen_all_houses.py` 全库出图 + 自检，必须看到 `CHECK ALL PASS - 18 houses`（18 栋，不增不减）；`check_all()` 在 `gen_all_houses.py:657-713`，校验隔墙/门落墙格/家具越界重叠压门/门净空/房间矩形不含墙格（**不校验连通性**，自己肉眼确认门能通）。
5. present 预览图给用户确认；用户点头才继续下一栋。

⚠️ 老坑：`note` 与 `lot` 常年不符（A4 四栋全中过招），一律以 `lot` / `wings` 为准。改完同步把 note 里过时的「屋本体 15×9 / 21×12」改成与 lot/wings 一致，避免下一条线再踩。

## 5. 收工

- 只 `git add` 你改/新建的上述文件（`houses_data.json`、两个 `_redo_*.py`、`_ref/art/A5_2026/*.png`、场景设计3 交棒后的 `HANDOFF-VILLAGE.md`）。
- commit 信息 `feat: A5 两栋房屋精调（toyshop/school）`。
- 报告写清：两栋最终 lot/房间/家具数、证物链落点、`CHECK ALL PASS - 18 houses` 结果、有没有遗留问题。

## 6. 边界提醒（别的线在跑，别管它们）

- 场景搭建2 在填 `data/frames.json` 的 `a4_2001` 帧，与你写的 A5 两栋数据不冲突（它只读 A4 四栋）。**将来 A5 地图搭建时才会用到你这两栋的 pos**，本线不碰 frames.json。
- 视觉机制线改 `scripts/*.gd`、美术线画 `assets/village/houses/`（A1–A3，且视觉线验收只用 A1–A3）——都与你无关。
- 文档回写线没开；`docs/house-spec.md` 的唯一写入者是文档回写线，你只读。
