# -*- coding: utf-8 -*-
"""L14 (A5 v5 落地) 验收落盘：FEEDBACK §9 + overseer + 待解决事项 三份文档同步。
按行号/整串替换；只改精确行。"""
import io, sys

def read(p):
    return io.open(p, encoding='utf-8').read().split('\n')

def write(p, lines):
    io.open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))

def replace_once(lines, idx, old, new, tag):
    if old not in lines[idx]:
        print('MISS %s: line %d does not contain %r' % (tag, idx + 1, old[:60]))
        sys.exit(1)
    lines[idx] = lines[idx].replace(old, new)

# ---------------------------------------------------------------- 1. FEEDBACK §9
FB = 'docs/FEEDBACK-a5-v5-exec.md'
f = read(FB)
sec9 = """
## 9. 总策划验收意见（2026-11-26 · 项目总策划会话 lead）

**结论：通过。** 本线可以收口。以下是总策划的**独立复核**（不是照抄你的报告，每一条都自己重跑过）。

### 9.1 独立复核表

| # | 复核项 | 方法 | 结果 |
|---|---|---|---|
| 1 | 提交链与文件域 | `git log` + 三 commit 的 `git show --stat` | ✅ `0989e87`（houses_data + evidence_store）／`5621db0`（frames.json + 两个测试）／`e086c83`（story.md + 本反馈文档）。**只碰** `data/frames.json`、`_ref/houses/houses_data.json`、`scripts/evidence_store.gd`、`docs/story.md`、`_mdtest/greybox_check.gd`、`_mdtest/camera_check.gd`、本文件 —— 无越界 |
| 2 | A1–A4 几何一字未动 | python 对比 `815368e` 与当前 `data/frames.json` 的五帧 `shapes`／`hotspots` | ✅ a1–a4 `shapes` **逐位全等 True**；hotspots 只有老槐的 `text` 变（`pos`／`reach` 不变）⇒ 写者锁守住了 |
| 3 | 顶层 world / 起点 / 安全区 | python 读 `frames.json` | ✅ world `{4800,3600}`、`start_pos [1024,1696]`、`safe_top 36`／`safe_bottom 3552` |
| 4 | a5_2026 帧内容 | python dump | ✅ **23 shapes**（polygon 8／rect 9／circle 2／house 4）／**5 hotspots**；热点＝老井·沥青补丁[2048,832] r88／老槐[2048,1664] r100／坝[512,160] r140／田[4040,512] r96／界碑[616,2512] r68；主宅＝`shen_a5[64,416]`／`market[2144,320]`／`toyshop[2176,1984]`／`school[576,1920]` |
| 5 | 河 polygon | 用权威公式 `base=5.5+1.5·sin(x/13+0.6)+0.8·sin(x/5.3+2.1)`、`bay=exp(-((x-46.5)/16.0)²)`、`depth=round(clamp(base+bay·8.0, 4, 15))`、`RIVER_Y=(depth+1)·32` 重算 | ✅ 对现行 103 点河 **mismatches=0**；新帧 152 点全部落在公式上；河下沿 shen 384／market 288／toyshop 256／school 416 ⇒ 房-河净距 shen 32、market 32 |
| 6 | `shen_a5` 房屋数据 | python 读 `houses_data.json` + grep | ✅ 共 **19 条**、id 无重复；`shen_a5` 存在，`doors []`／`gate []`、furniture 76 件、**clue:true 为 0**、name「沈家宅 · A5 2026（四合院 · 祖宅 · 封门）」、lot[0,0,35,35]、wings 6 条 |
| 7 | `evidence_store.gd` 的 HOUSE_FAMILY | grep + diff | ✅ 纯插入一行 `"shen_a5": "shen",`（+1/−0），无重排 |
| 8 | 七套回归 | 总策划**亲跑**（headless） | ✅ 全绿：greybox `WORLD_OK/START_OK/WALL_BLOCKED/TIME_FWD_REACHED=[1,2,3,4]/A1_MILL_INTERIOR_FREE/A1_MILL_DOOR_FREE/A1_WELL_FREE=false/HOTSPOT_*/UNEXPLAINED_BLOCKS=0/REACH_OK` 全 true；`REACH_MAP={standable:15104,to_a5:12863,blocked_at_step:[144,191,722,1184],band_total:298,band_full:261,band_ratio:"88%",ratio:"85%"}`；camera 8 PASS／hud_layout 21 PASS／asset_draw 60 PASS／sort 90 PASS／evidence_archive 111 PASS／display 配置一致 |
| 9 | 证物口径 25/56 | 跑 `lab/_audit_evidence_count.py`（独立复算） | ✅ **observations total = 56、cards total = 25**，与你在 §6 的结论**一致**（我第一版按唯一 title 去重算成 39 条是旧口径，已作废） |
| 10 | `docs/story.md` 文本改动 | diff 逐行核对 + grep 残留 | ✅ `:50` 删「、停车场」；`:433`「十字路口中央」→「北车道正中」；`:436` 红绿灯条删；`:437` 停车场条删（§7.2 七条→五条，编号前移）；`:444`「第 1 和第 4 条是钥匙」→「第 1 和第 2 条是钥匙」；`:700`「十字路口圆形补丁下」→「北车道圆形补丁下」；`:957-965` 表删「红绿灯基座偏移」行。`story.md`/`npc.md` grep「停车位｜红绿灯｜停车场」**命中 0 条** |
| 11 | 测试文件改动范围 | `git show 5621db0` diff | ✅ 只改世界尺寸常量：`camera_check.gd` setup_viewport 3200×2400→4800×3600、clamp 1920/1680→3520/2880；`greybox_check.gd` WORLD 期望值、扫描范围 `range(240,2400,32)`→`range(240,3600,32)`、`range(40,3160,32)`→`range(40,4800,32)`。**`HOUSE_MAP`/`HOUSE_MAP_A2`/`HOUSE_MAP_A3` 一行未动** ✅ |
| 12 | 实机肉眼验证 | — | ⚠️ **未做**（沙箱 Godot 出不了窗口）。记为尾巴 R-L14-6，不追责 |

### 9.2 裁决

- **D1**｜§4.1 第 9 条的算术表述有误（`1600 = OY − ROAD_W/2`＝1664−64；`OY − R_OUT = 1360` 是竖车道北段终点、1968 是南段起点、1744/2352 是东西引道在环岛外圆处的断点）—— **属表述问题，不改数据，从宽通过**。
- **D2**｜§6 请求把 overseer §六 的「27 卡/58 观察」回写为「25 卡/56 观察」—— **已采纳，本次已回写**（见 `docs/PROMPT-overseer.md` §六）。你的复算与我独立复算同值。
- **D3**｜§7 缺口 1「A4/A5 位置不变暂时断开」—— **这不是普通缺口，是直接违反核心玩法（空间冻结、时间可动、位置不变）**：玩家 Shift 从 2001 切到 2026，超市会跳位置。**已升为 P0**，需另派一条「A4 重排线」（与 L14 串行，两者都写 `data/frames.json`），且**必须与 A5 对齐**（超市同址、井同址、槐同址）。
- **D4**｜§7 缺口 4「美术交接文档过期」—— 登记为文档线待办（`docs/ART-HANDOFF-a4a5.md` `:75/:79/:86/:92/:94/:102-103/:82-85` 逐条作废重写＋`docs/ART-GAP-A4A5.md` 的环岛几何定稿），**排在实机验收之后**，不阻塞本线收口。
- **D5**｜§7 缺口 2「M15 沈家同位只满足 A5 一半」—— 已知并接受：A5 落点 `(64,416)` 是**实测唯一「不压河 + 离主路 ≥1 格」**的位置（`[64,352]` 压河 3040 px²，已作废）；A1–A4 的沈家反向统一挂「A1–A3 重排线」。

### 9.3 尾巴（挂后续线，不阻塞本线）

- **R-L14-1**｜A4↔A5 同址（超市/井/槐）—— **P0**，派 A4 重排线。
- **R-L14-2**｜M15 沈家 A1–A5 同位只满足 A5（且用 `(64,416)` 而非锚点表 `[64,352]`）—— 挂 A1–A3 重排线。
- **R-L14-3**｜证物 27/58 → 25/56 回写 overseer §六 —— ✅ **本次已做**（不改历史反馈文档，这条做对了）。
- **R-L14-4**｜A1–A3 仍是旧 3200×2400 布局（世界放大后内容只占西北角）—— 派 A1–A3 重排线。
- **R-L14-5**｜河贴图画布写死 `Vector2(3200,416)`（`scripts/world_view.gd`）—— 属 L8 资产接线。
- **R-L14-6**｜实机肉眼验证未做 —— 真机按 §4.4 走一遍（切到 A5 看环岛在路口正中、树在岛心、四象限、北车道正中的补丁、小学西墙里的半截界碑；井旁 E 看老井文案、环岛中心 E 看新老槐文案）。

**签字：项目总策划会话（lead）2026-11-26 · 结论：通过，本线闭环；R-L14-1 升 P0 派 A4 重排线。**
"""
if any('## 9. 总策划验收意见' in x for x in f):
    print('SKIP feedback: §9 already there')
else:
    f = f + sec9.split('\n')
    write(FB, f)
    print('OK feedback: +%d lines' % len(sec9.split('\n')))

# ---------------------------------------------------------------- 2. overseer
OV = 'docs/PROMPT-overseer.md'
o = read(OV)

# :72 a5_2026 行
replace_once(o, 71,
  '| `a5_2026` | 2026 | 17 → **23** | 7 → **5** | 🟡 **v5 排版已定稿、待落地**（任务书 `docs/PROMPT-a5-v5-exec.md`，几何已复核 errors=0）。**现行文件里仍是 L1 `0436c58` 的 17/7** |',
  '| `a5_2026` | 2026 | **23** | **5** | ✅ **已落地并验收**（L14 `e086c83`）—— 拓扑＝polygon 8／rect 9／circle 2／house 4；热点 5 条；world 4800×3600、起点 [1024,1696] |',
  'overseer:a5row')

# :78 老井行
replace_once(o, 77,
  '| 老井 | center `[1360,848]` | radius 32/32/32/32/48；label「老井」「老井·石板」「老井·水泥」「老井 · 沥青补丁」「老井·沥青补丁」；**`solid` 仅 A1=true**（井口敞开挡路，A2 起石板/水泥/沥青封层不挡 —— v5 有意设计，不是 bug） |',
  '| 老井 | A1–A4 center `[1360,848]`／**A5 center `[2048,832]`** | radius 32/32/32/32/**48**；label「老井」「老井·石板」「老井·水泥」「老井 · 沥青补丁」「老井 · 沥青补丁」；**`solid` 仅 A1=true**（井口敞开挡路，A2 起石板/水泥/沥青封层不挡 —— v5 有意设计，不是 bug）。🔴 **A5 的井已挪到北车道正中**（L14），A4 仍老位 ⇒ A4↔A5 同址待 A4 重排线 |',
  'overseer:well')

# :79 老槐行
replace_once(o, 78,
  '🔴 坐标与刻度以 L11 的 v3 布局为准：A1–A3 `(2048,1536)` r=32/64/96、A4/A5 `(2048,1696)` r=96/160） |',
  '🔴 **A5 已落地**：A1–A4 仍 `(1296,976)` r=32/64/96/96，**A5 挪到 `(2048,1664)` r=160**（L14 `e086c83`，环岛岛心）；A4↔A5 同址待 A4 重排线） |',
  'overseer:tree')

# :80 界碑行
replace_once(o, 79,
  '**A5 新增 `[32,1024,16,32]`**（L1，砌进小学围墙西端）。位置在五帧间的移动是**剧情**（同一块石头挪了三次），不是 bug。 |',
  '**A5 改为 `[608,2496,16,32]`**（L14 `e086c83`，砌进小学西墙实墙格 = 学校 pos + (1格,18格)，Godot 探针实测该格是 `#`）。位置在五帧间的移动是**剧情**（同一块石头挪了三次），不是 bug。 |',
  'overseer:stele')

# :83 主路行
replace_once(o, 82,
  '| 主路 | A1/A2 26 块弯路 rect；A3/A4/A5 单块 `[0,1664,3200,64]` road:true | A5 另有竖路 polygon x1328–1392 |',
  '| 主路 | A1/A2 26 块弯路 rect（y1568–1824）；A3/A4 单块 `[0,1664,3200,64]` road:true | 🔴 **A5 换新布局**（L14）：主路带 y1600..1728 ＝ 两条引道（西 `[0,1600,1744,128]`／东 `[2352,1600,2448,128]`，在环岛外圆处断开）＋环道 polygon（R304）＋内岛 polygon（R176，label「岛」）＋南北车道 x1984..2112。**A3/A4 仍是老路 ⇒ A4↔A5 位置不变待 A4 重排线** |',
  'overseer:road')

# :85 A5 v5 目标值段
replace_once(o, 84,
  '**🔴 A5 v5 的目标值（`docs/PROMPT-a5-v5-exec.md`，尚未落盘）**：',
  '**✅ A5 v5 的最终值（`docs/PROMPT-a5-v5-exec.md`，L14 `e086c83` 已落地并验收）**：',
  'overseer:a5values')
replace_once(o, 84,
  '⇒ 这套值**取代** v4（`lab/_a5_draft.json`），也**取代** `lab/_l11_final.json`（v3）。',
  '⇒ 这套值**取代** v4（`lab/_a5_draft.json`），也**取代** `lab/_l11_final.json`（v3）。**A1–A4 仍是旧 3200×2400 布局** ⇒ 世界放大后内容只占西北角，A1–A3 重排 + A4 重排是当前最高优先的两条地图线（都写 `data/frames.json` ⇒ 必须串行）。',
  'overseer:a5values2')

# :185 证物口径
replace_once(o, 184,
  '实测 **27 张卡 / 58 条观察**（L5 线 `5a36770` 交付时的真实代码路径实测 `PROBE cards=27 observations=58`；总策划用独立 python 仿真复现同值）。🔴 **L14 落地后全局变成 25 卡 / 56 观察**（删掉 A5 的「停车场」「路口·红绿灯基座」两张地标卡，各只有 a5 一年）⇒ **L14 落地后此处口径要改成 25/56**。',
  'L5 线 `5a36770` 交付时实测 27 卡 / 58 观察；🔴 **L14 落地后全局变成 25 卡 / 56 观察**（删掉 A5 的「停车场」「路口·红绿灯基座」两张地标卡，各只有 a5 一年）—— **总策划已于 2026-11-26 用 `lab/_audit_evidence_count.py` 独立复算确认 25/56 并回写此口径**（L14 反馈 §9 R-L14-3 已闭环）。',
  'overseer:evidence')

# :289 L14 行（§十 待办表）
replace_once(o, 288,
  '| **L14 A5 落地** | ✅ **任务书已写并按用户三条拍板修订**（`docs/PROMPT-a5-v5-exec.md`，424 行）→ **可派** |',
  '| **L14 A5 落地** | ✅ **已交付并验收通过**（`0989e87`／`5621db0`／`e086c83`，反馈 `docs/FEEDBACK-a5-v5-exec.md` 120 行＋总策划验收 §9） |',
  'overseer:l14todo')

# :327 L14 行（§十一 现在就能开）
replace_once(o, 326,
  '| **L14 A5 落地** | `data/frames.json` ＋ `_ref/houses/houses_data.json` ＋ `scripts/evidence_store.gd` ＋ `docs/story.md` ＋ 两个测试文件的世界尺寸常量 |',
  '| **L14 A5 落地** | `data/frames.json` ＋ `_ref/houses/houses_data.json` ＋ `scripts/evidence_store.gd` ＋ `docs/story.md` ＋ 两个测试文件的世界尺寸常量 | ✅ **已交付并验收**（`e086c83`）→ **不要再开重复的**。🔴 尾账：R-L14-1 A4↔A5 同址（超市/井/槐）**已升 P0**、R-L14-2 M15 沈家同位只满足 A5、R-L14-4 A1–A3 仍是旧布局、R-L14-5 河贴图画布写死 3200×416（属 L8）、R-L14-6 实机肉眼验证未做 |',
  'overseer:l14open')

# 在 :314 之后插入新的更新段
idx = 314
newseg = [
 '',
 '**2026-11-26 09:40 更新（L14 交卷并验收通过 + 机制盘点 +  phasing 取舍）**：',
 '',
 '1. **L14（A5 落地）已交付并验收通过** —— 三 commit `0989e87`／`5621db0`／`e086c83`；反馈 `docs/FEEDBACK-a5-v5-exec.md`（120 行）＋总策划验收意见 §9。**独立复核全部通过**：A1–A4 几何逐位未变、world 4800×3600／起点 [1024,1696]、a5_2026＝23 shapes／5 hotspots、河用权威公式（对现行 103 点 mismatches=0）、`houses_data.json` 19 条且 `shen_a5` 封门无 clue、`evidence_store.gd` 纯插一行、**七套回归总策划亲跑全绿**、**证物 25 卡/56 观察独立复算确认**、`story.md` 七处文本改动 grep 零残留、测试只改世界尺寸常量（`HOUSE_MAP` 未动）。',
 '2. 🔴 **当前最高优先＝两条地图线，且必须串行**（都写 `data/frames.json`）：**A1–A3 重排线**（A1–A4 内容仍只占西北角，世界放大后大片空地）→ **A4 重排线**（A4 超市/井/槐必须与 A5 同址，否则核心玩法「位置不变」当场破）。',
 '3. 🔴 **「顶住了」vs「虚化」的取舍已量化**（用户 m09128 提问）：现行代码只实现「顶住了」（`scripts/timeline.gd:84-88` 目标帧该坐标有 solid 就 bump 不前进）；**「卡墙虚化」是 `docs/house-spec.md` §8.3 的未实现设计**（用户 2026-11-19 拍板，零代码，需楼层方案 C 的高度数据）。**实测现行机制不会困住玩家**：起点连推四时代全部通过、主路带仅 1.0% 的可站点被 A5 挡、主路往东连续可推 118 格；被挡处 91% 是 A5 新建四栋房子的占地（有意设计）。',
 '4. ✅ **可与地图线并行的两条叙事机制线**（文件零重叠）：**L15 归档表 + 结局变体**（`docs/story.md` §10.1 表格已写死，约 2 天）、**L16 双日记渲染**（`docs/diary-markup.md` 四标记 + `_mdtest/` 三个实验脚本可搬，约 1–2 天）。**L17 phasing/虚化**与楼层方案 C 同批，且会碰 `scripts/timeline.gd`／`player.gd`／`world_view.gd`／`main.gd` ⇒ 与 L8（也写 `world_view.gd`）二选一。',
]
o[idx+1:idx+1] = newseg
write(OV, o)
print('OK overseer: %d lines (+%d)' % (len(o), len(newseg)))

# ---------------------------------------------------------------- 3. 待解决事项
TS = 'docs/待解决事项.md'
u = read(TS)
# :6 状态行
replace_once(u, 5,
  '> **当前状态**：2026-11-26 09:10 · 仓库 HEAD `34c6848`（本地；远端仍 `b0798da`，按用户定时指令推）',
  '> **当前状态**：2026-11-26 09:40 · 仓库 HEAD `e086c83`（本地；远端仍 `b0798da`，按用户定时指令推）',
  'ts:status')
# :147 Q3
replace_once(u, 146,
  '| **Q3** | **老槐五帧新文案谁写？**',
  '| **Q3**<br>✅已办 | **已办（2026-11-26）：L14 执行线已写完并落地**（老槐五帧新文案全部换掉：统一「朝西北歪」，不再说「朝井那侧」；a5 删掉已作废的「拱裂地砖」；a5 结尾改为「环岛修起来的时候，把它圈在了正当中，树冠正好顶满内圈」）**（原问题：老槐五帧新文案谁写？）** | **L14 执行线写**（它已经是 `data/frames.json` 的唯一写者，顺手闭环；别的线写会撞写者锁） | 低。已写进 L14 任务书 §3.4 |',
  'ts:q3')
# §4 表：L9 行 + 加 L14 行
replace_once(u, 429,
  '| **L9 渲染缺陷调查** | 🔵 已派，等反馈 | `docs/PROMPT-render-bug-exec.md`（208 行）+ overseer 登记 | `scripts/world_view.gd`、`scripts/house_shape.gd`、`scripts/frame_data.gd` |',
  '| **L9 渲染缺陷调查** | ✅ 已交卷（`014a18c`，只改 `scripts/world_view.gd` +69/−4，反馈 `docs/FEEDBACK-render-bug-exec.md` 117 行）｜🟡 总策划尚未独立复核 | `docs/PROMPT-render-bug-exec.md`（208 行） | `scripts/world_view.gd`、`scripts/house_shape.gd`、`scripts/frame_data.gd` |',
  'ts:l9row')
insert_at = 439  # L6 行之后
u[insert_at+1:insert_at+1] = [
 '| **L14 A5 落地** | ✅ 已交付并验收（`0989e87`／`5621db0`／`e086c83`） | `docs/FEEDBACK-a5-v5-exec.md`（120 行＋总策划验收 §9） | `data/frames.json`、`_ref/houses/houses_data.json`、`scripts/evidence_store.gd`、`docs/story.md`、两个测试文件的世界尺寸常量 |',
 '| **A4 重排线**（新，P0） | 🔴 **待写任务书** —— A4 的超市/井/槐必须与 A5 同址，否则「位置不变」破 | — | `data/frames.json`（与 A1–A3 重排线串行） |',
 '| **A1–A3 重排线**（新） | 🔴 **待写任务书** —— A1–A4 内容仍只占西北角 | — | `data/frames.json`（单写者） |',
 '| **L15 归档表 + 结局变体**（新） | 🟡 任务书待写（可与地图线并行，文件零重叠） | — | 新建 `scripts/ending_*.gd` + `_mdtest/ending_check.gd` |',
 '| **L16 双日记渲染**（新） | 🟡 任务书待写（可与地图线并行，文件零重叠） | — | 新建 `scripts/diary_*.gd` + `_mdtest/diary_check.gd` |',
 '| **L17 phasing/虚化**（新） | 🟡 任务书待写 —— 需楼层方案 C 同期，且与 L8 争 `scripts/world_view.gd` | — | `scripts/timeline.gd`、`scripts/player.gd`、`scripts/world_view.gd`、`scripts/main.gd` |',
]
write(TS, u)
print('OK 待解决事项: %d lines' % len(u))

print('DONE')
