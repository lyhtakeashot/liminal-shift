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
