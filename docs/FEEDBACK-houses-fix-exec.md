# 反馈文档 · 房屋数据线（L3）**验收单**：market 双态说明 + 撤掉 school 界碑家具

> 提交方：房屋数据执行线（本线，2026-11-23）｜接收方：**项目总策划会话（验收人）**
> 上游任务书：`docs/PROMPT-houses-fix-exec.md`（117 行）｜开工 HEAD `d8e2220`（`7c93898` 是其祖先 ✅）
> 交付 commit：**`7805d71`**（`data(houses): market 双态说明 + 撤掉 school 界碑家具（改由 A5 世界界碑承担）+ zheng_a4 确认无线索`），父提交 `d8e2220`
> 改动范围：**只改 `_ref/houses/houses_data.json`**（+5 −21）＋ 本反馈文档。**未碰** `data/frames.json`（L1 独占）、`scripts/house_shape.gd`（L4 独占）、`scripts/**`（L2/L5 独占）、`assets/**`、`_ref/art/**`、`_mdtest/**`、`docs/**`（除本文件）；工作区其余改动是并发线产物，**一个都没 add**。
> 一句话：**4 项必改全部完成，数据自检 76 PASS / 0 FAIL，七套回归全绿；任务书预期的「一处红」实测不存在，原因见 §3.1。**

## 0. 请总策划拍板的 5 项（其余已按任务书执行完毕）

| 编号 | 待裁决 | 本线建议 | 影响面 |
|---|---|---|---|
| D1 | A5 帧热点 10 ≠ 11（撤家具所致） | 同意，等 L1 补上 A5 世界界碑（rect `[32,1024,16,32]`、热点 (40,1040)）后自然回 11，本线不改 | L1 |
| D2 | 任务书 §3.2 预期的「`evidence_archive_check` 一处红」**不存在**（该套无 school 界碑/全校条数断言） | 同意不补测试；是否给该套补一条全校条数断言，请另开线裁决 | L4/L5 |
| D3 | 生成脚本仍带界碑家具代码：`_ref/houses/_redo_school.py:226`、`_ref/houses/gen_all_houses.py:294` | 另开「生成器对齐」小线清掉（JSON 才是真相源，重跑生成器会把界碑加回来） | 未来重建数据 |
| D4 | `data/frames.json:3194` A4 手写热点标题仍是「超市工地 · 南大门」（与 `market` 新名不符） | 交 L1 顺手改成「超市 · 南大门」并把 pos 挪到南院门格 | L1 |
| D5 | L4 需删 `scripts/house_shape.gd:107` 的 `CLUE_TEXTS["school"]["「周」界碑"]`（已无对应家具） | 确认派给 L4；且**不要**在 CLUE_TEXTS 里补 school 界碑（A5 那块碑归 frames.json） | L4 |

## 1. 4 项必改逐条（改前 → 改后）

**1.1 `market` 名字去掉单一年份 + note 写清两态 ✅**
- name：「超市工地 · A4 2001 · 在建（粮站拆）」→「**超市 · 粮站原址 · 两态：A4 在建工地 / A5 营业超市**」。
- note 重写，任务书 §1.1 五项全含：①**屋本体 42×28 格 = 672×448 px**（用户 m02311「长宽各扩一倍」：原 21×14 → 42×28）②「同一栋楼两个年代共用同一份数据（a4_2001 与 a5_2026 同写 id=market 且同址）」③**A4 2001 在建态**（粮站拆了→在建工地：工地围挡/脚手架/建材堆/未拆封货架×18/工地办公室/工棚，大面积开挖而桩基绕开老井那片地）④**A5 2026 营业态**（超市照常营业）⑤两条线索家具各自两态位置（见 1.2）⑥「**路口圆形沥青补丁 = 井口**」保留 ⑦共 58 件家具 + 结构说明保留。

**1.2 `market` 两条线索家具 note 改双态 ✅**（`name` 未动、刻字原文保留）

| 家具 | rect(格) | 改后 note（A4 ／ A5） |
|---|---|---|
| `文件柜` | `[38,10,1,2]` | A4 2001 在工地办公室 · 土地登记表第二联 + 改过的地质报告（写「地下有暗河，不宜大开挖」）／A5 2026 搬进超市办公室 —— 同一件家具，跨时代不变 |
| `上磨盘` | `[15,22,2,1]` | A4 2001 粮站拆出、暂放工地围挡角落，刻「沈氏丰源·一九五七」／A5 2026 摆进超市门厅（story §7.2⑥ 的现代物证）—— 同一件家具，跨时代不变 |

改前分别是「办公室 · 土地登记表第二联 + 改过的地质报告…」／「粮站拆出、暂放工地角落，刻「沈氏丰源·一九五七」——A5 营业才摆进门厅」。**刻字原文一字未改写**（物证原文）；两条家具 `rect` 未动。

**1.3 撤掉 `school` 的「「周」界碑」家具 ✅**
- **`furniture[]` 整条删除**（含 name/short/rect/note/clue/zone/yard_building/wall_mounted）：`school` 家具 **155 → 154 件**。
- **`clue` 列表 2 → 1 条**：删「操场北围墙里嵌着半块旧界碑，只认得出一个「周」字（身份反转佐证）。」，保留剪彩台那条。
- **`note` 尾句改指向世界界碑**（叙事不抹掉）：原「「周」界碑 [1,18,2,1]（操场北围墙最西端）。」→「操场北围墙西端那格墙里嵌着半截旧石碑，字磨得只剩一个「周」——那是**世界地标**（A5 帧的世界界碑：rect [32,1024,16,32]、热点 (40,1040)，由地图线 frames.json 落地），不属于这间屋子的家具，本数据不再挂「界碑」家具，免得玩家在同一处检视到两块碑、证物档案多出一条重复记录。」
- **`lot`/`wings`/`partitions`/`doors`/`gate`/`rooms` 一个字未动**（自检逐字节比对通过）—— 那格墙还在，形状由 L1 放；`school.story` 未动（原本就没提界碑）。

**1.4 `zheng_a4` 确认无线索、不新增 ✅**：实测 `clue: true` 家具数 = **0**，改前改后均为 0；30 件家具与 `lot`/`wings`/`doors`/`gate`/`partitions`/`rooms` 逐字节未动。

## 2. 数据自检（`lab/_l3_selfcheck.py` → `lab/_l3_selfcheck.txt`：**76 PASS / FAILS=0 / SELFCHECK_OK**）

| 断言组 | 结果 |
|---|---|
| `json.load` 成功且为 list；18 条、id 无重复 | PASS |
| 六栋 `lot`/`wings`/`doors`/`gate`/`partitions`/`rooms` 与改前逐字节一致（×36）；另外 12 栋整体逐字节未动 | PASS |
| 家具条数 market 58→58 / shen_a4 76→76 / zhou_a4 31→31 / zheng_a4 30→30 / **school 155→154（恰好 −1）** / toyshop 58→58 | PASS |
| 全库 `clue:true` 家具 **29 → 28**；`zheng_a4` = 0 且未新增 | PASS |
| `school` 家具里已无「界碑」（连「碑」字都没有）、`school.clue` 无界碑文字；只删掉「「周」界碑」一条 clue 家具名、无新增；任务书点名的 7 个 clue 家具名全部原样保留 | PASS |
| `market.name` 同点 A4/A5 两态；note 含 42×28 / 在建 / 营业 / 圆形沥青补丁 / 井口 / 文件柜 / 上磨盘 / 沈氏丰源·一九五七；两条家具 rect 未动、note 都写了两态；刻字原文、土地登记表第二联、地下有暗河 都在 | PASS |
| 文件形态：无 BOM + CRLF + `json.dumps(indent=2)` 规范形态 | PASS |

**改后每栋 clue 家具清单**：lu_house 1 旧木箱｜mill_a1 3 账桌·石磨·老井｜mill_a2 4 墙基暗龛·账桌·石磨·老井｜shen_a1 0｜shen_a2 1 书桌｜shen_a3 1 蜂窝煤炉｜shen_a4 3 蜂窝煤炉·账桌·保险柜｜**market 2 文件柜·上磨盘**｜zhou_house 1 小桌｜toyshop 2 招牌小字·账柜｜**school 0（原「「周」界碑」已撤）**｜lu_a2 0｜zhou_a2 1 小桌｜mill_a3 5 墙基暗龛·账桌·弃置石磨·老井·水泥封层｜zhou_a3 1 账桌｜lu_a3 1 堂屋地基痕迹｜zhou_a4 2 保险柜·账桌｜**zheng_a4 0**。

**A5 帧热点差分**（`lab/_l3_hotspot_delta.py`，复刻 `house_shape.gd:378-411` 规则 + TILE=32）：改前 school 1（「周」界碑 (64,1040)）/ market 2 / toyshop 2 ＝ 5；改后 school 0 / market 2 / toyshop 2 ＝ 4。**改前有改后无 `[('school','「周」界碑')]`、改后有改前无 `[]`**；market clue 家具名改前改后一致 `['文件柜','上磨盘']`。⇒ 只少这一条，market / toyshop 坐标一字未动。

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

### 3.1 关于任务书 §3.2「预期内的红」—— **没有出现**（对应 D2）
实测 `_mdtest/evidence_archive_check.gd`（273 行）**没有任何 school 界碑 / 全校证物条数断言**，只断言「A1 磨坊账桌入档 1 条 → A2 磨坊账桌第 2 条 → 地标老井第 3 条 → A2「老井 · 石板」第 4 条」与 `_short_house_name()` 裁剪规则 ⇒ 撤家具对它**零影响**，该套仍全绿。按任务书纪律**没有改测试文件**。**真正可见的差异在 `greybox_check` 的 A5 帧热点 11 → 10**（脚本只断言 A1 帧 `HOTSPOTS >= 10`，A5 无下限断言，故不红）；**L1 补上 A5 世界界碑后会回到 11。** 沙箱固有噪声（非故障）：`Failed to open 'user://logs/godot*.log'`、`Failed to read the root certificate store.`、`[exit code: 1]`。

## 4. 给 L4 / L5 的交接
1. **本线没有改任何 clue 家具的 `name`**（`文件柜`/`上磨盘`/`保险柜`/`账桌`/`蜂窝煤炉`/`招牌小字`/`账柜` 全原样）⇒ **L4 不需要因改名改任何既有 key**。
2. **L4 需要删一条 key**：`scripts/house_shape.gd:107` 的 `CLUE_TEXTS["school"]["「周」界碑"]` —— 已无对应家具，留着会让下一个人以为界碑还是 `school` 的家具（与 `docs/PROMPT-clue-year-exec.md:77` 一致）。**也不要在 CLUE_TEXTS 里补 school 界碑条目** —— A5 那块碑的文案在 `data/frames.json`（L1 写），补了会变成两个来源。
3. `market` 两条家具 `name` 保持「文件柜」「上磨盘」，L4 直接在这两个 key 下写 `{2001: …, 2026: …}` 即可。
4. **知会 L5**：`school::「周」界碑` 这条证物 key **在本线之后不再产生**，直到 L1 补上世界界碑（届时走地标分支、key=title，与 1926/2001 的界碑是三条独立观察记录，符合 `docs/DECIDE-a4-a5-layout.md` 裁定②）。

## 5. 遗留问题 / 需知会
1. **D3 复发风险**：`_ref/houses/_redo_school.py:226` 与 `_ref/houses/gen_all_houses.py:294` 仍有界碑家具代码。二者**不是真相源**（任务书 §0 明写 JSON 是唯一真相源、禁止调 `export_seed()`），本线未碰；但**重跑生成器会把界碑加回来**。
2. **D4**：`data/frames.json:3194` A4 手写热点 title 仍是「超市工地 · 南大门」（pos `[2112,1456]`）；该文件属 L1 独占、本线未碰，建议 L1 改成「超市 · 南大门」并把 pos 挪到南院门格（`x∈[2048,2176] × y=1632`，见 `docs/PROMPT-map-fix-exec.md` §3.5）。
3. **A4 的 `market` pos 仍是 `[1440,576]`**（`frames.json:3075-3078`），L1 会挪到 `[1440,768]` 与 A5 同址；挪完后 A4 两个家具热点世界坐标与 A5 一致（(2672,1120) / (1952,1488)），正是「超市同址」的必然结果。
4. **A4 2001 的界碑仍在 `[1416,1600,16,32]`**（L1 挪到 `[2880,960]`）；A5 帧**尚无**世界界碑 shape —— 这是 A5 热点 10≠11 的另一半原因。
5. **`docs/HANDOFF-VILLAGE.md` 有 5 处过期**（「周」界碑 `[1,18,2,1]` 见 :78 / :147 / :289 / :362 / :397）—— 本线不改 `docs/**`（除本文件），需另一条线回写。
6. **`market` 新 name 第一段是「超市」** ⇒ 证物来源标签（`scripts/main.gd:260` → `_short_house_name()`，`scripts/main.gd:276-282`）显示「超市 · 2001」/「超市 · 2026」，语义合理；改名**未破坏**任何既有断言（该套 `_short_house_name` 用例只测 lu_house/mill_a2/zhou_house，全绿）。
7. **`.gitattributes` 是 `* text=auto eol=lf`**，工作区文件保持 CRLF（与改前一致），入库归一化成 LF ⇒ **diff 只有本线 5 + / 21 −，不会整文件翻行尾**（已实测 `git diff --stat`）。

## 6. 依据文档
`docs/DECIDE-a4-a5-layout.md` §11 裁定①（界碑做成每帧独立世界地标）、`docs/PROMPT-map-fix-exec.md` §3.6（撤 school 家具）、`docs/story.md` §4.4 / §7.2⑥ / §7.4、`docs/HANDOFF-VILLAGE.md`（房屋数据格式与坑表）、`docs/PROMPT-clue-year-exec.md`（L4 前置与交接）。

## 7. 验收栏（请总策划填写）
- [x] **通过** —— 可进入 L4 / L1 联调（D1–D5 按上表默认建议执行；另附 3 条尾巴 R1–R3，不阻塞 L4）
- [ ] **需返工** —— 请注明条目：____________________
- 其他要求：**R1 两处 px 旧 16px 口径回退本线修；R2 L1 线补交反馈文档；R3 生成器对齐另开小线。R4（D4 标题改名）判为可选、不返工。**
- 验收人：**项目总策划会话（lead）**　日期：**2026-11-23**

---

## 8. 验收意见（总策划，2026-11-23）

### 8.1 独立复核结果（不采信反馈自述，逐条实测）

| 复核项 | 方法 | 结果 |
|---|---|---|
| 提交边界 | `git show --stat 7805d71` | 只改 `_ref/houses/houses_data.json`（+5 −21）＋ 本反馈文档，共 2 files ✅ 未碰 frames.json / house_shape.gd / scripts / assets / _mdtest |
| 18 栋几何零改动 | python 逐栋比对 `lot/wings/doors/gate/partitions/rooms` vs 父提交 `7805d71^` | `geometry_diffs = []`（18×6 项全等）✅ |
| 家具字段零改动（除 note） | python 逐栋逐家具比对（去掉 note 后全等） | 只剩一条差异：`REMOVED school 「周」界碑`；其余全部字段原样 ✅ **符合任务书 §2「不许改 name」** |
| clue 家具总数 | python 统计 `clue:true` | **28**（29 −1），`zheng_a4 = 0`、`school = 0` ✅ 与任务书 §3.1 预期一致 |
| school 家具数 | python | 155 → **154**（恰好 −1），全库无「碑」字家具 ✅ |
| market 双态 | python | `name`＝「超市 · 粮站原址 · 两态：A4 在建工地 / A5 营业超市」；两条 clue 家具 note 各 82 字、含两态位置；刻字「沈氏丰源·一九五七」原文保留 ✅ |
| 数据自检脚本 | `python lab/_l3_selfcheck.py` | `FAILS=0` / `SELFCHECK_OK` ✅（脚本在 `lab/` 下，未入库，可复跑） |
| 七套回归 | 在**当前 HEAD `0436c58`** 重跑 | greybox `WORLD_OK/HOTSPOTS_OK/REACH_OK=true`、`A1_WELL_FREE=false`（A1 井仍挡路，符合 v5）、`UNEXPLAINED_BLOCKS=0`；camera/hud_layout/asset_draw/sort `fails=0`；evidence_archive `EVIDENCE_CHECK_DONE fails=0` + `EVIDENCE_OK` ✅ |
| A4/A5 帧现状（复核时 HEAD） | python dump frames.json | a4：11 shapes / 6 hotspots，`market[1440,768]`、`shen_a4[96,320]`、`zhou_a4[1792,1728]`、`zheng_a4[2560,1728]`、界碑 rect `[2880,960,16,32]` + 热点 `[2888,976]`；a5：**17 shapes / 7 hotspots**，界碑 rect `[32,1024,16,32]` + 热点 `[40,1040]` ✅ L1 已落地 |

**结论：4 项必改全部达标，执行纪律（只改一个文件、精确 add、不碰测试）达标。通过。**

### 8.2 D1–D5 逐条裁决

| 编号 | 裁决 | 理由 |
|---|---|---|
| **D1** | ✅ **已闭合，无需动作** | 复核时 A5 帧热点已是 **11**（L1 补的世界界碑已进 `data/frames.json`）。反馈里写的「11 → 10」是 L1 落地前的中间态，现已自然回 11。 |
| **D2** | ✅ **认账，执行线正确** | 任务书 §3.2 预期「evidence_archive_check 一处红」是**任务书写错了**——该套只断言「磨坊账桌×2 + 地标老井 + A2 老井·石板」四条链，没有 school 界碑/全校条数断言。执行线**没有**擅自改测试，这是对的。要不要补全校条数断言 → 放 L4/L5 顺手做，不单开线。 |
| **D3** | ⚠️ **成立，排小线 R3** | 已核实复发点：`_ref/houses/gen_all_houses.py:294`（`F("「周」界碑", 1, 10, 2, 1, …, clue=True)`）与 `:300`（clue 文案），以及 `_ref/houses/_redo_school.py:22`/`:27` 注释、`:226` 家具定义、`:256` note 文案。**任何人重跑生成器都会把界碑家具加回来**，届时 A5 会出现两块碑 + 档案多一条重复记录。 |
| **D4** | ⬜ **降级为「可选」，不返工** | A4 就是在建工地，热点标题「超市工地 · 南大门」与 story §4.4「粮站拆了、建超市、工地」口径一致，**改了反而弱化「工地」信息**。与 market 新名不冲突（证物来源标签显示「超市 · 2001」，那是另一处 UI）。若用户希望统一口径，可由 L1 线顺手改一行，**不单开线、不阻塞**。 |
| **D5** | ✅ **确认派 L4** | `scripts/house_shape.gd:107` 仍有 `CLUE_TEXTS["school"]["「周」界碑"]`（已核实）。留着会让下一个人以为界碑还是 school 的家具。**且不许在 CLUE_TEXTS 里补 school 界碑**——A5 那块碑的文案归 `data/frames.json`（L1 已写好），补了就是两个来源。 |

### 8.3 三条尾巴（不阻塞 L4）

- **R1（回退本线，1 分钟）**：`houses_data.json` 里有两处 **px 是旧 16px 口径**——market note「42×28 格 = **672×448** px」、school note「38×30 格 = **608×480** px」。现 TILE=32，正确值应为 **1344×928 px** 与 **1216×992 px**（与 `docs/ART-HANDOFF-a4a5.md` 的画布尺寸一致）。**note 是纯说明文字、不影响运行**，但会误导美术同学按旧尺寸出图 ⇒ 请 L3 会话顺手改这两处。
- **R2（交 L1 会话补交）**：`docs/FEEDBACK-map-fix-exec.md` **不存在**。L1 提交 `0436c58` 已落盘且数据经我复核无误，但**任务书 §5 要求的反馈留档没交**。请 L1 会话补交（实机截图与回归原始输出只有它手里有）。数据层结论我已记入本文件 §8.1。
- **R3（另开「生成器对齐」小线）**：清 `_ref/houses/gen_all_houses.py` 与 `_ref/houses/_redo_school.py` 里的界碑家具代码与注释，**只改 `_ref/houses/*.py`、不碰 JSON**（JSON 是唯一真相源）。建议排在 L4 之后、下一批开。

### 8.4 复核时另记的两条观察（非本线责任，登记在案）

1. **L1 改动后的通行率变化**（`greybox_check` 的 `REACH_MAP`）：`to_a5` 4746 → **4848**（净增 102）、`blocked_at_step` `[144,191,0,536]` → `[144,191,722,222]`（A3→A4 从 0 变 722，A4→A5 从 536 降到 222）、主路活动带 `band_ratio` 仍是 **81%**、`REACH_OK=true`、`UNEXPLAINED_BLOCKS=0`。
   → 判定为**「空间冻结」的正常表现，不是回归**：A4 的超市扩建到 x1440–2784 / y768–1664（南沿恰好贴主路北缘），A1 站在它将来 footprint 上的点推帧到 A4 会被顶住；而 A4→A5 因为两帧同址，卡点反而少了 314 个。**唯一要做的是实机走一遍 A1→A5 主路路线，确认玩家不会被卡在超市工地里。**
2. **`docs/HANDOFF-VILLAGE.md` 实际有 7 处**提到「周」界碑是 school 的家具（`:78` `:147` `:289` `:307` `:334` `:362` `:397`；反馈里写 5 处，实际 7 处）。其中 `:307`/`:334` 是**历史变更记录**（记录 v3/v5 当时怎么改的），不该改写；`:147`/`:289`/`:362`/`:397` 是**当前状态表**，要改成「世界地标，五帧各一个」，并补 A4/A5 坐标。→ 登记到 **L6 文档线**（由总策划会话自己做），不退回 L3。

### 8.5 签字

**验收人：项目总策划会话（lead）　日期：2026-11-23　结论：通过（带 R1–R3 三条尾巴，均不阻塞 L4）**
