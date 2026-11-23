# 反馈文档 · 房屋数据线（L3）：market 双态说明 + 撤掉 school 界碑家具（致「项目总策划」会话）

> 提交方：房屋数据执行线（本线，2026-11-23）｜接收方：项目总策划会话
> 上游任务书：`docs/PROMPT-houses-fix-exec.md`（117 行）｜开工 HEAD `d8e2220`（`7c93898` 是其祖先 ✅）
> 改动范围：**只改 `_ref/houses/houses_data.json`**（1 文件 +5 −21）；本反馈文档单独 add 进同一个 commit。

## 0. 一句话现状

**4 项必改全部完成，数据自检 76 条 PASS / 0 FAIL，七套回归全绿。**

**一个偏差要报**：任务书 §3.2 预期的「`evidence_archive_check` 有一处预期内的红」**没有出现**——实测该套没有 school 界碑 / 全校条数断言，撤家具对它零影响；真正体现的差异在 `greybox_check` 的 **A5 帧热点数 11 → 10**（正是撤掉的那一条）。

---

## 1. 4 项改动逐条（改前 → 改后）

### 1.1 `market` 名字去掉单一年份 + note 写清两态 ✅

- **name**：「超市工地 · A4 2001 · 在建（粮站拆）」→「**超市 · 粮站原址 · 两态：A4 在建工地 / A5 营业超市**」。
- **note**（重写，任务书 §1.1 要求的 5 项全含）：①面积口径「**屋本体 42×28 格 = 672×448 px**」（用户 m02311「长宽各扩一倍」：原 21×14 → 42×28）；②明确「同一栋楼两个年代共用同一份数据（a4_2001 与 a5_2026 同写 id=market 且同址）」；③**A4 2001 在建态**（粮站拆了→在建工地：工地围挡/脚手架/建材堆/未拆封货架×18/工地办公室/工棚，大面积开挖而桩基绕开老井那片地）；④**A5 2026 营业态**（超市照常营业）；⑤两条线索家具各自两态位置（见 1.2）；⑥「**路口圆形沥青补丁 = 井口**」口径保留；⑦共 58 件家具 + 结构说明保留。

### 1.2 `market` 两条线索家具 note 写双态 ✅（`name` 未动、刻字原文保留）

| 家具 | rect(格) | 改后 note（A4 ／ A5） |
|---|---|---|
| `文件柜` | `[38,10,1,2]` | A4 2001 在工地办公室 · 土地登记表第二联 + 改过的地质报告（写「地下有暗河，不宜大开挖」）／A5 2026 搬进超市办公室 —— 同一件家具，跨时代不变 |
| `上磨盘` | `[15,22,2,1]` | A4 2001 粮站拆出、暂放工地围挡角落，刻「沈氏丰源·一九五七」／A5 2026 摆进超市门厅（story §7.2⑥ 的现代物证）—— 同一件家具，跨时代不变 |

改前分别是「办公室 · 土地登记表第二联 + 改过的地质报告…」／「粮站拆出、暂放工地角落，刻「沈氏丰源·一九五七」——A5 营业才摆进门厅」。**「沈氏丰源·一九五七」刻字原文一字未改写**（物证原文）；两条家具的 `rect` 未动。

### 1.3 撤掉 `school` 的「「周」界碑」家具 ✅

- **`furniture[]` 整条删除**（含 name/short/rect/note/clue/zone/yard_building/wall_mounted）：`school` 家具 **155 → 154 件**。
- **`clue` 列表 2 → 1 条**：删「操场北围墙里嵌着半块旧界碑，只认得出一个「周」字（身份反转佐证）。」，保留剪彩台那条。
- **`note` 尾句改指向世界界碑**（叙事不抹掉）：原「「周」界碑 [1,18,2,1]（操场北围墙最西端）。」→「操场北围墙西端那格墙里嵌着半截旧石碑，字磨得只剩一个「周」——那是**世界地标**（A5 帧的世界界碑：rect [32,1024,16,32]、热点 (40,1040)，由地图线 frames.json 落地），不属于这间屋子的家具，本数据不再挂「界碑」家具，免得玩家在同一处检视到两块碑、证物档案多出一条重复记录。」
- **`lot`/`wings`/`partitions`/`doors`/`gate`/`rooms` 一个字未动**（自检逐字节比对通过）—— 那格墙还在，形状由 L1 放；`school.story` 未动（原本就没提界碑）。

### 1.4 `zheng_a4` 确认无线索、不新增 ✅

实测 `zheng_a4` 的 `clue: true` 家具数 = **0**，改前改后均为 0（**未新增任何线索家具**）；30 件家具与 `lot`/`wings`/`doors`/`gate`/`partitions`/`rooms` 逐字节未动。

---

## 2. 数据自检（`lab/_l3_selfcheck.py` → `lab/_l3_selfcheck.txt`：**76 PASS / FAILS=0 / SELFCHECK_OK**）

| 断言组 | 结果 |
|---|---|
| `json.load` 成功且为 list；18 条、id 无重复 | PASS |
| 六栋的 `lot`/`wings`/`doors`/`gate`/`partitions`/`rooms` 与改前逐字节一致（×36）；另外 12 栋整体逐字节未动 | PASS |
| 家具条数 market 58→58 / shen_a4 76→76 / zhou_a4 31→31 / zheng_a4 30→30 / **school 155→154（恰好 −1）** / toyshop 58→58 | PASS |
| 全库 `clue:true` 家具 **29 → 28**；`zheng_a4` = 0 且未新增 | PASS |
| `school` 家具里已无「界碑」（连「碑」字都没有）、`school.clue` 无界碑文字；只删掉「「周」界碑」一条 clue 家具名、无新增；任务书点名的 7 个 clue 家具名全部原样保留 | PASS |
| `market.name` 同时点了 A4 与 A5 两态；note 含 42×28 / 在建 / 营业 / 圆形沥青补丁 / 井口 / 文件柜 / 上磨盘 / 沈氏丰源·一九五七；两条家具 rect 未动、note 都写了两态；刻字原文、土地登记表第二联、地下有暗河 都在 | PASS |
| 文件形态：无 BOM + CRLF + `json.dumps(indent=2)` 规范形态 | PASS |

**改后每栋 clue 家具清单（供报告用）**

| 栋 | 数 | 家具 | 栋 | 数 | 家具 | 栋 | 数 | 家具 |
|---|---|---|---|---|---|---|---|---|
| lu_house | 1 | 旧木箱 | mill_a1 | 3 | 账桌·石磨·老井 | mill_a2 | 4 | 墙基暗龛·账桌·石磨·老井 |
| shen_a1 | 0 | — | shen_a2 | 1 | 书桌 | shen_a3 | 1 | 蜂窝煤炉 |
| shen_a4 | 3 | 蜂窝煤炉·账桌·保险柜 | **market** | 2 | 文件柜·上磨盘 | zhou_house | 1 | 小桌 |
| toyshop | 2 | 招牌小字·账柜 | **school** | **0** | （原「「周」界碑」已撤） | lu_a2 | 0 | — |
| zhou_a2 | 1 | 小桌 | mill_a3 | 5 | 墙基暗龛·账桌·弃置石磨·老井·水泥封层 | zhou_a3 | 1 | 账桌 |
| lu_a3 | 1 | 堂屋地基痕迹 | zhou_a4 | 2 | 保险柜·账桌 | **zheng_a4** | **0** | — |

**A5 帧热点差分**（`lab/_l3_hotspot_delta.py`，复刻 `house_shape.gd:378-411` 规则 + TILE=32）：改前 school 1（「周」界碑 (64,1040)）/ market 2 / toyshop 2 ＝ 5；改后 school 0 / market 2 / toyshop 2 ＝ 4。**改前有改后无 `[('school','「周」界碑')]`、改后有改前无 `[]`**；market clue 家具名改前改后一致 `['文件柜','上磨盘']`。⇒ 只少这一条，market / toyshop 坐标一字未动。

---

## 3. 七套回归（改后实跑，**判绿看关键字不看退出码**）

| 套件 | 关键字 | 结论 |
|---|---|---|
| `greybox_check` | `WORLD_OK=true` `A1_IS_FREE_START=true` `START_OK=true` `HOUSES=true` `HOUSE_WALLS>0=true` `HOUSES_A2=true` `HOUSES_A3=true` `DOOR_PASSABLE=true` `HOTSPOTS_OK=true` `UNEXPLAINED_BLOCKS=0` `REACH_OK=true` `A2_HOTSPOTS=11` `A3_HOTSPOTS=13` `HOTSPOTS=10` `WALL_BLOCKED=true` `TIME_FWD_REACHED=[1, 2, 3, 4]` | ✅ 全绿 |
| `camera_check` | `CAMERA_CHECK_DONE fails=0` | ✅ |
| `display_check` | `CONTENT_SCALE_MODE=1` `CONTENT_SCALE_ASPECT=1` `CONTENT_SCALE_SIZE=(1280, 720)` `默认纹理过滤=0` `STRETCH_SCALE_MODE=0` | ✅ |
| `hud_layout_check` | `HUD_CHECK_DONE fails=0`（11 条 PASS） | ✅ |
| `asset_draw_check` | `ASSET_DRAW_CHECK_DONE fails=0`（17 条 PASS） | ✅ |
| `sort_check` | `SORT_CHECK_DONE fails=0`（17 条 PASS） | ✅ |
| `evidence_archive_check` | `EVIDENCE_CHECK_DONE fails=0` `COLLECTED 收集入档已验证` `NO_DUP 去重已验证` `EVIDENCE_OK` | ✅ 全绿 |

**五帧 solids 不变**（239/300/380/646/533）；**hotspots 只有 a5_2026 由 11 变 10**（＝撤掉的那条），a1_1926 10 / a2_1951 11 / a3_1976 13 / a4_2001 13 均不变。

### 3.1 关于任务书 §3.2「预期内的红」—— **没有出现**

实测 `_mdtest/evidence_archive_check.gd`（273 行）**没有任何 school 界碑 / 全校证物条数断言**：它只断言「A1 磨坊账桌入档 1 条 → A2 磨坊账桌第 2 条 → 地标老井第 3 条 → A2「老井 · 石板」第 4 条」与 `_short_house_name()` 裁剪规则。撤掉 `school` 那条家具对它**零影响** ⇒ 该套仍全绿。按任务书纪律**没有改测试文件**。

**真正可见的差异在 `greybox_check` 的 A5 帧热点数 11 → 10**：正是撤掉的那一条（脚本只断言 A1 帧 `HOTSPOTS >= 10`，A5 无下限断言，故不红）。**L1 补上 A5 世界界碑（rect `[32,1024,16,32]`、热点 (40,1040)）后，A5 帧热点会回到 11。**

沙箱固有噪声（非故障）：`Failed to open 'user://logs/godot*.log'`、`Failed to read the root certificate store.`、`[exit code: 1]`。

---

## 4. 给 L4（证物文案线）的交接

1. **本线没有改任何 clue 家具的 `name`** —— `文件柜`/`上磨盘`/`保险柜`/`账桌`/`蜂窝煤炉`/`招牌小字`/`账柜` 全部原样 ⇒ **L4 不需要因改名改任何既有 key**。
2. **L4 需要删一条 key**：`scripts/house_shape.gd:107` 的 `CLUE_TEXTS["school"]["「周」界碑"]` —— 已无对应家具，留着会让下一个人以为界碑还是 `school` 的家具（与 `docs/PROMPT-clue-year-exec.md:77` 一致）。
3. **L4 不要在 `CLUE_TEXTS` 里补 school 界碑条目** —— A5 那块碑的文案在 `data/frames.json`（L1 写），补了会变成两个来源。
4. `market` 两条家具 `name` 保持「文件柜」「上磨盘」，L4 直接在这两个 key 下写 `{2001: …, 2026: …}` 即可。
5. **知会 L5**：`school::「周」界碑` 这条证物 key **在本线之后不再产生**，直到 L1 补上世界界碑（届时走地标分支、key=title，与 1926/2001 的界碑是三条独立观察记录，符合 `docs/DECIDE-a4-a5-layout.md` 裁定②）。

---

## 5. 遗留问题 / 需总策划知会

1. **`data/frames.json:3194` A4 手写热点 title 仍是「超市工地 · 南大门」**（pos `[2112,1456]`）—— 与 `market` 新名不一致；该文件属 L1 独占、本线未碰，建议 L1 改成「超市 · 南大门」并把 pos 挪到南院门格（`x∈[2048,2176] × y=1632`，见 `docs/PROMPT-map-fix-exec.md` §3.5）。
2. **A4 的 `market` pos 仍是 `[1440,576]`**（`frames.json:3075-3078`），L1 会挪到 `[1440,768]` 与 A5 同址；挪完后 A4 两个家具热点世界坐标与 A5 一致（(2672,1120) / (1952,1488)），正是「超市同址」的必然结果。
3. **A4 2001 的界碑仍在 `[1416,1600,16,32]`**（L1 挪到 `[2880,960]`）；A5 帧**尚无**世界界碑 shape —— 这是 A5 热点 10≠11 的另一半原因。
4. **生成脚本里仍有界碑家具代码**：`_ref/houses/_redo_school.py:226`（`F("「周」界碑", 1, 18, 2, 1, …)`）与 `_ref/houses/gen_all_houses.py:294`。二者**不是真相源**（JSON 才是，禁止调 `export_seed()`），本线未碰，但**重跑生成器会把界碑加回来** ⇒ 建议另开「生成器对齐」小线，否则下次重建数据会复发。
5. **`docs/HANDOFF-VILLAGE.md` 有 5 处过期**（「周」界碑 `[1,18,2,1]` 见 :78 / :147 / :289 / :362 / :397）—— 本线不改 `docs/**`（除本反馈文档），需另一条线回写。
6. **`market` 新 name 第一段是「超市」** ⇒ 证物来源标签（`scripts/main.gd:260` → `_short_house_name()`，`scripts/main.gd:276-282`）显示「超市 · 2001」/「超市 · 2026」，语义合理；改名**未破坏**任何既有断言（该套 `_short_house_name` 用例只测 lu_house/mill_a2/zhou_house，全绿）。
7. **`.gitattributes` 是 `* text=auto eol=lf`**，工作区文件保持 CRLF（与改前一致），入库归一化成 LF ⇒ **diff 只有本线 5 + / 21 −，不会整文件翻行尾**（已实测 `git diff --stat`）。

---

## 6. 依据文档

`docs/DECIDE-a4-a5-layout.md` §11 裁定①（界碑做成每帧独立世界地标）、`docs/PROMPT-map-fix-exec.md` §3.6（撤 school 家具）、`docs/story.md` §4.4 / §7.2⑥ / §7.4、`docs/HANDOFF-VILLAGE.md`（房屋数据格式与坑表）、`docs/PROMPT-clue-year-exec.md`（L4 前置与交接）。
