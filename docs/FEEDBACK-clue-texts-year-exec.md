# L4 反馈：证物文案执行人（CLUE_TEXTS 支持按年覆盖）

- 线号 L4　日期 2026-11-24　commit `feat(clue): CLUE_TEXTS 支持按年覆盖 + market 两态文案(2001/2026) + 删 school 界碑条目`
- 白名单：`scripts/house_shape.gd`、`scripts/frame_data.gd`（只改 `:66` 一处调用）。**未碰** `main.gd`/`evidence_*.gd`/`world_view.gd`/`data/frames.json`/`_ref/houses/houses_data.json`/`assets/**`/`_mdtest/**`/`docs/HANDOFF-VILLAGE.md`。
- 前置：L3 `7805d71`、L5 `5a36770` 均在 HEAD。

## 1. 改动逐条

| 文件 | 行号 | 改了什么 |
|---|---|---|
| `house_shape.gd` | :46-53 | `CLUE_TEXTS` 头注释补「value 两种形态」（String 通用 / Dictionary 按年；取不到该年退 `"default"` 再退占位句；键一律中文 name）。 |
| `house_shape.gd` | :101-112 | `market` 两条拆成按年字典：`文件柜`{2001,2026}、`上磨盘`{2001,2026}。2001 版与原单串文案**逐字相同**（保持现状），2026 版新写。 |
| `house_shape.gd` | :122-125 | **删掉** `"school": { "「周」界碑": … }` 整段，换注释：L3 已撤该家具，A5 那块碑归 `data/frames.json`（rect `[32,1024,16,32]`、热点 `(40,1040)`），别在此补；`zheng_a4` 同样无条目。 |
| `house_shape.gd` | :391-399 | `hotspots()` 签名加 `year: int = 0`；同时修 §2.5 过期注释（老注释说「lot 外老井属世界地标」是错的：mill_a1/a2 的「老井」rect `[6,12,1,1]` 在 lot `[0,0,17,12]` 内、mill_a3 在 `[0,0,17,16]` 内，**是真的家具热点**，证物档案里是独立的 `mill::老井` 卡）。**只改注释文字，过滤逻辑一行未动。** |
| `house_shape.gd` | :424 | `"text"` 由 `String(texts.get(name, 占位句))` 改为 `_clue_text(texts, name, year)`。 |
| `house_shape.gd` | :435-456 | 新增 `static func _clue_text(texts, name, year) -> String`：String 直接用；Dictionary 先取该年 → 再取 `"default"` → 再退占位句「「X」立在这里。」。 |
| `frame_data.gd` | :66 | `hotspots.append_array(HouseShape.hotspots(hdata, hpos, year))`（**只改这一行**）。`year` 来自同文件 `:28` 的 `year = int(d.get("year", 0))`。 |

⚠️ **没有**把 year 加进 hotspot 输出字段 —— 入档年份仍由 `scripts/main.gd` 的 `_collect_evidence()` 取帧的 `f.year`。

**2026 版文案要点**（完整文案见脚本）：文件柜搬进超市办公室，玻璃换新、划痕是新的；只剩一个棉线扎过的牛皮纸档案袋（袋口绕线发黑），写着「土地登记表（第二联）」，前手栏还是「原业主 周氏，光绪二十六年立契」；柜底那份地质勘察报告上被圆珠笔圈过两道的地方已褪成很淡的蓝。上磨盘搬进超市门厅，平放砖砌水泥台上压透明板，磨眼干水泥被掏干净、掏过的那一圈比别处浅，盘沿刻字擦得发亮：**沈氏丰源·一九五七**。两版都保留刻字原文；只写看到什么不写意味着什么；无「玩家应该想到…」类出戏话。

## 2. 覆盖度自检（临时脚本 `lab/_l4_coverage_check.gd`，未提交）

```
CLUE_FURNITURE_TOTAL=28   CLUE_COVERED=28   PLACEHOLDER_COUNT=0
TEXT_ENTRIES_TOTAL=30     SCHOOL_CLUE=0     ZHENG_A4_CLUE=0
ISSUES=0                  L4_COVERAGE_OK=true
```

逐栋（年份取自 `data/frames.json` 的 house 形状）：lu_house[1926] 旧木箱｜mill_a1[1926] 账桌/石磨/老井｜mill_a2[1951] 墙基暗龛/账桌/石磨/老井｜shen_a2[1951] 书桌｜zhou_house[1926] 小桌｜zhou_a2[1951] 小桌｜mill_a3[1976] 墙基暗龛/账桌/弃置石磨/老井/水泥封层｜shen_a3[1976] 蜂窝煤炉｜lu_a3[1976] 堂屋地基痕迹｜zhou_a3[1976] 账桌｜shen_a4[2001] 蜂窝煤炉/账桌/保险柜｜zhou_a4[2001] 保险柜/账桌｜**market[2001+2026] 文件柜/上磨盘（各 2 版）**｜toyshop[2026] 招牌小字/账柜。合计 28 件（A1–A3 19 + A4/A5 9）。**school 与 zheng_a4 的 clue 数均为 0**（未新增条目）。

## 3. 七套回归（改动后，与改动前基线逐项一致）

| 套 | 关键字 |
|---|---|
| greybox_check | `HOTSPOT_A1_MILL_DESK=账桌`、`FRAME[0..4] hotspots=10/11/13/13/11`、`UNEXPLAINED_BLOCKS=0`、`REACH_OK=true`、`CLUE_CHECKS_DEFERRED=A2-A5 空帧占位` |
| camera_check | `CAMERA_CHECK_DONE fails=0` |
| display_check | `CONTENT_SCALE_MODE=1`、`CONTENT_SCALE_ASPECT=1`、`CONTENT_SCALE_SIZE=(1280, 720)`、`默认纹理过滤=0`、`STRETCH_SCALE_MODE=0`（无 fails 行） |
| hud_layout_check | `HUD_CHECK_DONE fails=0` |
| asset_draw_check | `ASSET_DRAW_CHECK_DONE fails=0` |
| sort_check | `SORT_CHECK_DONE fails=0` |
| evidence_archive_check | `EVIDENCE_CHECK_DONE fails=0`、`COLLECTED 收集入档已验证`、`NO_DUP 去重已验证`、`EVIDENCE_OK` |

- hotspot 数 10/11/13/13/11 未变。`CLUE_CHECKS_DEFERRED=A2-A5 空帧占位` 是 greybox 的**旧提示**（L1 落地后 A4/A5 帧已不空），不影响判绿，本线未处理。
- `hud_layout_check` 尾部 Godot anchor WARNING 与 `[exit code: 1]` 是沙箱噪声，非失败。
- asset_draw/sort 无需按 §0.2 换 HEAD 版：L2 的 `scripts/world_view.gd` 工作区干净，七套直跑通过。

## 4. 卡数未变

`lab/_audit_evidence_count.py`：**cards total = 27、observations total = 58** —— 与 L5 验收基线完全一致，本线只改文案、不改家具，**未改卡数或观察数**。

## 5. 遗留 / 交接

1. **归 L1**（文案在 `data/frames.json`，本线不碰）：`界碑` 1926/1951/1976 三条逐字相同（story §4.4 已有「1951 被凿一半、开始往土里埋」的设定，对应总调度 R7）；`坝` 1926/1951/1976/2026 四条相同；`田` 1951 与 1976 两条相同。实测 distinct：`界碑` 3、`坝` 2、`田` 4、`老井` 5、`老槐` 5。
2. `docs/HANDOFF-VILLAGE.md` 旧口径核对见 §6 —— **本线一个字未改**（L6 已在 `def62dd` 回写）。
3. 临时脚本 `lab/_l4_coverage_check.gd`、`lab/_l4_dump_houses.py` 不提交。

## 6. `docs/HANDOFF-VILLAGE.md` 四张表核对（只核对、只报告）

⚠️ 核对时该文件已被 **L6 提交 `def62dd` 回写**，**行号整体位移**（实测 572 行，任务书写 568），故任务书表里的行号已过时，判定以内容为准。

- **表 A（@16px 旧口径）—— 全部已被 L6 修掉 ✅**：`:86` 现为「一格 = 32×32 px」（与 `house_shape.gd:13` `const TILE := 32.0` 一致）；`:119-136` 尺寸表已是 640×416 / 1344×896 / 1216×960；`:239` 已写 32px 杂草；`:273` toyshop「21×20 格（672×640 px）…58 件家具（2 clue）」；`:284` school「38×30 格（1216×960 px）…154 件家具（0 clue）」；`:340` 有 2026-11-24 回写注；`:554`「126 个 16px 文件」已加「16px 时代产物，现行 TILE=32px」。
- **表 B（界碑归属）—— 三处全改 ✅**：`:78`（`_redo_school.py` 摘要行）、`:147`（三条线索落点表）、`:289`（§6.10 证物链）均已写「界碑不再是 house 家具，A5 世界地标 rect `[32,1024,16,32]`、热点 `(40,1040)`」。
- **表 C（过期陈述）—— 大部已改，两处仍是旧口径 ⚠️**：`:379`「a5_2026 已落地（17 shapes / 7 hotspots）」✅（实测一致）；`:516`「world 已是 3200×2400、start_pos [1024,1680]、主路 y=1664」✅（实测一致）；`:132` market「单 id 两形态…靠 house_shape.gd 按年覆盖…不另起 market_a5」✅（与本线实现一致，实测 58 家具/2 clue）；`:136` school「154(0)」✅；`:5` 头部已加「2026-11-24 全面回写」✅。
  - ⚠️ **仍需 L6 处理**：`:312`「a5_2026 帧目前还是空的（shapes/hotspots 都空）…要用这栋新的 42×32 尺寸」—— 与 `:379` 自相矛盾，且 42×32 已过期（现 38×30）。
  - ⚠️ **仍需 L6 处理**：`:389`/`:392`「家具数 159 → 155」「155 家具（1 clue）」—— 实测应为 **154 件家具（0 clue）**。
- **表 D（历史记录）—— 保持不改 ✅**：`:300`/`:307`/`:326`/`:334`/`:364`/`:399` 都在 v2–v5 过程节里，`:340` 已加统一口径注。

**结论**：表 A、表 B、表 C 中除 `:312` 与 `:389`/`:392` 外全部已被 L6 回写到位；那两处是 L6 文档线的尾巴，**本线不改**。

## 7. 边界声明

- 本线只提交 `scripts/house_shape.gd`、`scripts/frame_data.gd`、本反馈文档三份；`lab/` 临时脚本不提交。
- 工作区里 `docs/HANDOFF.md`、`docs/house-spec.md`、`scripts/display_manager.gd`、`_ref/art/**`、美术素材目录等改动属别的线，**未 add、未改**。

## 8. 验收意见（总策划，2026-11-24）

### 8.1 独立复核结果（不采信反馈自述，逐条实测）

| 复核项 | 方法 | 结果 |
|---|---|---|
| 提交边界 | `git show --stat 63f47eb` | 3 files：`scripts/house_shape.gd`（+66 −12）＋ `scripts/frame_data.gd`（±2）＋ 本反馈文档（75 行）✅ 白名单守住（没碰 `data/frames.json` / `world_view.gd` / `_mdtest/**` / `_ref/**`） |
| year 来源链路 | `git show 63f47eb -- scripts/frame_data.gd` | 唯一改动＝`scripts/frame_data.gd:66` `HouseShape.hotspots(hdata, hpos)` → `HouseShape.hotspots(hdata, hpos, year)` ✅ 正是任务书 §2.0 要求的写法 |
| 改签名的安全性 | 全仓 grep `HouseShape.hotspots(` | 调用点**只有** `scripts/frame_data.gd:66`；`_mdtest/` 里三个脚本只 `preload` house_shape.gd，**没有任何测试直接调用 hotspots()** ✅ 改签名零风险 |
| 覆盖度 | 我自己的 python 脚本解析 `CLUE_TEXTS`（`lab/_v_l2l4l6.py`，未入库） | `total=28 covered=28 missing=0 year_gap=[]`；`school` 段 **present: False**、`zheng_a4` 段 **present: False** ✅ 与自报一致 |
| **文案条数 30** | 我的展开口径脚本（`lab/_v_clue_count.py`，未入库） | **L4 自报正确**：26 条字符串 ＋ 2 个字典 × 2 个年份（`market` 的 `文件柜`/`上磨盘`，年份键实测 `['2001','2026']`）＝ **30 条**。我先前复核出的「28」用的是 **key 条数**口径（28 个家具 key）⇒ **是我的口径错，L4 无错**，此处更正记录在案 |
| 卡数未变 | `lab/_audit_evidence_count.py` 在 HEAD 复跑 | 地标卡 8 张全 5 年（老井/老槐/界碑/坝/田 各 5 条，停车场 1、超市工地 1、路口 1）；家具多观察卡＝`mill::老井`3 / `mill::账桌`3 / `market::上磨盘`2 / `market::文件柜`2 / `mill::墙基暗龛`2 / `mill::石磨`2 / `shen::蜂窝煤炉`2 / `zhou::小桌`2 / `zhou::账桌`2 ⇒ **27 卡 / 58 观察，与 L5 验收基线完全一致** ✅ |
| 七套回归 | 当前 HEAD `daa8b67` 重跑 | greybox（solids 239/300/380/646/534，hotspots 10/11/13/13/11，`REACH_OK=true`、`UNEXPLAINED_BLOCKS=0`）/ camera / hud_layout / asset_draw / sort / evidence_archive 全绿 ✅ |
| year 不进输出字段 | 读 `scripts/house_shape.gd:421-431` | hotspot 输出字段＝`pos/title/text/reach/house_id/furniture/house_name`，**没有 year** ✅ 入档年份仍由 `scripts/main.gd:276` `try_collect(..., f.year)` 取帧年份，口径单一 |
| §2.5 过期注释 | 读 `scripts/house_shape.gd` 注释段 | 已改为「mill_a1/mill_a2 的 rect [6,12,1,1] 落在 lot [0,0,17,12] 内、mill_a3 在 [0,0,17,16] 内 ⇒ 是真的家具热点，证物档案里是独立的 `mill::老井` 卡；和 frames.json 手写的世界老井是同一口井的两个位置，靠标题「· 院里」后缀区分」✅ **只改注释文字，过滤逻辑一行未动**（我核对 `hotspots()` 的 lot 过滤条件仍是原样） |
| 老井双来源区分 | 读 `house_shape.gd:418-420` | 家具名「老井」时 title 改写为 `"%s · 院里"` ⇒ `main.gd:269` 用 `furniture` 字段（原始名）算 key、`main.gd:273` 用 title 算地标 key ⇒ **`mill::老井` 与 `老井` 永不同卡** ✅ 与任务书 §2.1 规则 C 一致 |

**结论：按年取值链路打通、覆盖度 28/28、卡数零变化、注释订正属实、边界守住。通过。**

### 8.2 D1–D6 逐条裁决

| 编号 | 裁决 | 理由 |
|---|---|---|
| **D1**（CLUE_TEXTS value 支持 String 或按年字典） | ✅ **通过** | 兼容旧写法，26 条字符串不用改；`_clue_text()` 取值顺序＝该年 → `"default"` → 占位句「「X」立在这里。」，回退链清楚。 |
| **D2**（`hotspots()` 加 `year: int = 0` + `frame_data.gd:66` 传参） | ✅ **通过** | 这正是任务书 §2.0 指定的改法 a；**禁止**的改法 b（从 data 取年份）没有踩——`houses_data.json` 的房子本来就不带 year（`market` 被 A4/A5 复用），从 data 取会把同一家超市钉死在一个年份。 |
| **D3**（`market` 的 `文件柜`/`上磨盘` 拆 2001/2026 两态） | ✅ **通过** | 实测 `house_shape.gd:103-110`：两件都是 `{2001: …, 2026: …}` 字典；2001 版与原单串**逐字相同**（保留 2001 既有观感），2026 版是新写的「搬进超市办公室/门厅」——与 A4「在建工地」/A5「营业超市」两态一致。 |
| **D4**（删 `school` 的「「周」界碑」条目） | ✅ **通过，边界正确** | 界碑现在是 **A5 世界地标**（`data/frames.json` rect `[32,1024,16,32]`、热点 `(40,1040)`）。若在这里补 school 界碑，同一块碑会有**两个来源**，证物档案必然多一条重复记录。执行线还写了注释提醒下一个人别补回去 ✅ |
| **D5**（§2.5 过期注释订正） | ✅ **通过** | 原注释「rect [6,10] 已在 lot 下界之外 ⇒ 世界级地标」是错的（实测 `[6,12,1,1]` 在 lot 内）；L3 验收时我判它是「注释过期必须改」，本线改对了，且**没顺手改过滤逻辑**（改了会真的把 `mill::老井` 这条热点删掉、破坏 27 卡/58 观察基线）。 |
| **D6**（§6 的 `docs/HANDOFF-VILLAGE.md` 四张表核对） | ✅ **核对属实，但两条提醒已过时** | 表 A/B/C/D 的判断我逐条复跑，与自报一致（`一格 = 16×16 px` 0 命中、旧 px 串仅 `:328`、`market_a5` 仅 `:132`、`155(1)` 0 命中、`[1,18,2,1]` 3 处全在历史语境、`1600×900|640×360` 0 命中）。**但它说「`:312` 与 `:389`/`:392` 仍需 L6 处理」这两条已经不成立**——L6 的 `585a004` 已在 `:314` 与 `:396` 补了「2026-11-24 现状更正：a5_2026 帧已落地（17 shapes / 7 hotspots）／school 现行 38×30 格 = 1216×960 px」与「界碑已撤出 house 数据，现为 154 家具 / 0 clue」块注。**不必再找 L6 返工。** |

### 8.3 三条尾巴

- **R1（实机验收，阻塞「证物文案线」结项）**：本线给 `market` 拆了 2001/2026 两态，**必须在实机走一遍 A4（A4 超市工地）与 A5（A5 营业超市）**，用 E 检视「文件柜」「上磨盘」，确认两次入档落在**同一张卡**（`market::文件柜`）的**两条观察**（2001 与 2026），而不是两张卡。这是证物模型 B 方案的最终闭环验收。
- **R2（交 L1 小线）：跨年代重复文案**。我实测（`lab/_v_landmark_dup.py`，按 title 主体名归组）地标卡的文案重复情况：**界碑** 5 年只有 3 种文案，**1926/1951/1976 三帧逐字相同**；**坝** 5 年只有 2 种文案，**1926/1951/1976/2026 四帧相同**；**田** 1951/1976 相同；老井 5 种全不同、老槐 5 种全不同。这三条地标文案写在 `data/frames.json`（**L1 独占文件**），不在本线白名单 ⇒ 派 L1 小线改，不要在本线越界。目标：界碑 1951 那条要写出「被凿了一半、开始往土里埋」（story 里这是 1951→2001 的关键动作）；坝与田按年代差写出可见变化。
- **R3（登记 L8）**：`house_shape.gd` 输出的 `title` 里「老井 · 院里」是**给玩家看的标签**，而 `furniture` 字段是给 key 用的原始名——L8 若要改证物来源标签显示（「磨坊 · 院里 · 1926」之类），要同时看这两个字段，别把 key 也改了（会散卡）。

### 8.4 复核时另记的一条观察

**「按年取值」目前只在家具侧生效，地标侧仍是手写文案。** 五帧地标的文案都写在 `data/frames.json` 的 `hotspots[].text` 里，本来就一帧一句、天然按年；所以本线的机制只解决家具侧（同一件家具在 A4/A5 两个时代出现时取不同文案）。**这不是缺口**，但下一个读代码的人容易误以为「按年」覆盖全部热点——建议在 `scripts/house_shape.gd` 的 `_clue_text()` 注释里补一句「地标文案按帧手写，见 `data/frames.json`」。

### 8.5 签字

**验收人：项目总策划会话（lead）　日期：2026-11-24　结论：通过（带 R1–R3 三条尾巴；R2 派 L1 小线，不阻塞 L8）**
