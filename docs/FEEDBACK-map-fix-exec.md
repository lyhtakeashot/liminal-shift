# 反馈文档 · 地图帧修正执行线（L1）**验收单**：A4 重摆位 + A5 新增世界界碑

> 提交方：地图帧修正执行线（本线，2026-11-23）｜接收方：**项目总策划会话（验收人）**
> 上游任务书：`docs/PROMPT-map-fix-exec.md`（287 行）｜开工 HEAD `d8e2220`
> 交付 commit：**`0436c58`**（`fix(map): A4 重摆位（超市与 A5 同址/界碑挪至工地东侧/井文案对齐新叙事）+ A5 新增世界界碑与井命名对齐`），父提交 `72d75a0`
> 改动范围：**只改 `data/frames.json`**（+32 −10，单文件）＋ 本反馈文档 ＋ 本线实机截图 `docs/_mapfix_shots/`（8 张）。**未碰** `_ref/houses/houses_data.json`、`scripts/**`、`assets/**`、`_mdtest/**`、`docs/**`（除本文件与本线截图目录）；工作区其余 438 项改动全是并发线产物，**一个都没 add**。
> 一句话：**9 项必改全部完成，几何自检 44 PASS / 0 FAIL，七套回归全绿，实机逻辑 57 项全 PASS + 8 张截图，A1→A5 主路实机走通（15 项 0 FAIL）；§3.6 的跨线冲突已由房屋数据线闭合。**

---

## 0. 请总策划拍板的 3 项

| 编号 | 待裁决 | 本线建议 | 影响面 |
|---|---|---|---|
| E1 | A4 手写热点标题仍是「超市工地 · 南大门」（与 L3 给 `market` 换的新名「超市 · 粮站原址 · 两态…」不同调） | **保持不动**（沿用总策划 D4 裁决「改了反而弱化工地信息」）。本线已把该热点**位置**挪到真门口格 `[2112,1632]`，标题保留工地口径是刻意的 | 无（若改就是一行字） |
| E2 | A5 帧同位置**没有**「超市 · 南大门」手写热点（实测按 E 无热点） | 认可为预期：A5 是营业中的超市，「工地」叙事只属 A4。若要加一条 A5 门口热点请另开线 | 无 |
| E3 | A5 老槐 `radius=160`（树冠直径 10 格）仍偏大，遮住 A5 车道正中那口井 | 等 **L2 渲染修正线**落地后再定（见 §6 遗留问题 1）。本线**未改**任何 radius | L2 |

---

## 1. 9 项必改逐条（改前 → 改后）

> 逐字节依据：`git show 0436c58 -- data/frames.json`（全文见 §4）。

### 1.1 §3.1 A4 四栋房屋重摆位 ✅

| house | 改前 pos | 改后 pos | 说明 |
|---|---|---|---|
| `market` | `[1440, 576]` | **`[1440, 768]`** | 与 A5 帧同址（超市两态同一栋楼）；南沿恰好贴主路北缘 y=1664 |
| `shen_a4` | `[128, 320]` | **`[96, 320]`** | 左移 32px，让开 A4 老槐上抬后的树冠（树冠圆心 (1296,908.8) r96，冠矩形 x∈[1200,1392]；改后 wings 最大 x=1184 < 1200） |
| `zhou_a4` | `[1792, 1728]` | `[1792, 1728]` **未动** | 周家留在主路南侧（market 足迹 x1440–2784 吃掉北侧） |
| `zheng_a4` | `[2560, 1728]` | `[2560, 1728]` **未动** | 同上 |

### 1.2 §3.2 周家 / 郑家留主路南侧 ✅（未动，属定案口径）

几何唯一解：market wings 足迹 x∈[1440,2784]，占掉周家（x1792）与郑家（x2304）的北侧原址；两栋落主路南侧 y=1728 是唯一不打架的摆法。

### 1.3 §3.3 A4 界碑挪到工地东侧 ✅

| 项 | 改前 | 改后 |
|---|---|---|
| shape rect | `[1416, 1600, 16, 32]` | **`[2880, 960, 16, 32]`** |
| shape label / solid / color | 「碑」 / true / `#8a8278` | **原样未动** |
| hotspot pos | `[1424, 1616]` | **`[2888, 976]`** |
| hotspot reach | 68 | **68 未动** |

离 A1 原位 `[1856,960]` 位移 **1024px**；最近可站位 (2864,976) 距碑心 **24.0 ≤ reach 68** ⇒ 走近按 E 读得到。

### 1.4 §3.4 A4 老井文案对齐新叙事 ✅

- shape `label`：**「老井 · 沥青补丁」未动**（与 A5 帧对齐）。
- hotspot `title`：「老井 · **圆形**沥青补丁」→ **「老井 · 沥青补丁」**。
- hotspot `text` 改前：「一圈圆形的沥青，比周围的地面新，颜色也深一层。边上留了圈没压实的裂缝，踩上去能听见底下是空的。」
- hotspot `text` 改后：「一小圈沥青补丁，紧贴着超市的西墙外面，位置比路面高出一点点。补丁边上留着新土，颜色和二十多年前填井时倒上去的水泥一样灰。踩上去能听见底下是空的。」

**只写看到什么、不点破「超市在躲它」，保留「脚下是空的」伏笔**；并把井与超市西墙的关系写进文案（井右缘 1392，西墙 x=1440，**相距 80px，只隔一道墙**）。

### 1.5 §3.5 A4「超市工地 · 南大门」热点挪到真门口 ✅

- hotspot pos：`[2112, 1456]` → **`[2112, 1632]`**。
- `reach` 88 与 `text`（「桩位绕着走」伏笔）**一字未动**。
- 落点核对：market 南院门格 `x∈[2048,2208]`、`y=1632` ⇒ 热点正落在门格上。

### 1.6 §3.6 A5 新增世界界碑 + 井命名对齐 ✅

- **新增 shape**（放 `shapes` 数组**最后一项**，红绿灯之后）：
  `{"type":"rect","rect":[32,1024,16,32],"color":"#8a8278","label":"碑","solid":true}`
- **新增 hotspot**（放 `hotspots` 数组**最后一项**）：
  `{"pos":[40,1040],"title":"界碑","reach":68,"text":"围墙里嵌着半截石碑，碑面和砖面抹成了一个平，缝里塞着旧水泥。字磨得只剩一个「周」，旁边那个字只留着一道竖笔。石头底下的土比四周高出一小截。"}`
- **A5 井 shape label**：「老井**·**沥青补丁」（无空格）→ **「老井 · 沥青补丁」**（与 hotspot title 对齐）。
- A5 老槐 `radius=160`、A5 老井 `radius=48`、A5 井 `solid=false`、A5 井文案 —— **全部未动**。

### 1.7 §3.7 家具级热点自动跟随 house pos ✅（**没有手写**）

`scripts/frame_data.gd` 处理 `house` 型 shape 时自动调 `HouseShape.solid_rects(hdata, hpos)` 与 `HouseShape.hotspots(hdata, hpos)`，家具热点中心 = `pos + (r[0]+r[2]*0.5)*32, pos + (r[1]+r[3]*0.5)*32`，reach 固定 68。改位后 A4 家具热点自动落在：

| 家具 | 世界坐标 |
|---|---|
| market 文件柜 | (2672, 1120) |
| market 上磨盘 | (1952, 1488) |
| shen_a4 蜂窝煤炉 | (208, 960) |
| shen_a4 账桌 | (1008, 944) |
| shen_a4 保险柜 | (1136, 960) |
| zhou_a4 保险柜 | (1840, 2000) |
| zhou_a4 账桌 | (1984, 1776) |
| zheng_a4 | 无（该栋无 clue 家具） |

### 1.8 §3.8 给 `a4_2001` 加 `_note` ✅（可选项，已做）

`"_note": "老井 solid 仅 A1=true（井口敞开挡路）、A2-A5=false（石板/水泥/沥青封层不挡）——这是 v5 设计口径，不是 bug，别改。"`

`scripts/timeline.gd` 只读 `id/year/ground/shapes/hotspots`，`frame_data.gd` 的 `setup()` 同理 ⇒ **未知键安全**（实机跑通已证）。

### 1.9 跨帧不许动的部分 ✅（见 §4 完整证据）

`world` / `safe_top` / `safe_bottom` / `start_pos` / `a1_1926` / `a2_1951` / `a3_1976` —— **一个字节都没动**，A1–A3 的界碑 shape `[1856,960,16,32]` 与热点 `[1864,976]` 一字未改。

---

## 2. 几何自检（`mapfix_geom.py` → `mapfix_geom.txt`：**44 checks, 0 FAIL → GEOMETRY SELF-CHECK: ALL PASS**）

自检脚本用 Python 复刻引擎语义（`HouseShape.grid_of` 的 **interior 优先**、`_polygon_scanlines` 的 16px 切片、`is_free` 的 14px 方形探针、`world_view.gd` 的树冠上抬 `center.y - r*0.7`）后逐项判。

### 2.1 A4（2001）—— 23 项全 PASS

| 断言 | 结果 |
|---|---|
| 四栋 house 齐备（market/shen_a4/zhou_a4/zheng_a4） | PASS |
| 四栋 pos = market[1440,768] / shen_a4[96,320] / zhou_a4[1792,1728] / zheng_a4[2560,1728] | PASS |
| wings 两两不重叠 | PASS |
| lot 底色两两不重叠 | PASS |
| wings 不压主路 / 坝 / 田 / 老井 / 老槐上抬树冠 | PASS |
| wings 不进河 polygon（16px 扫描线 + 点包含双判） | PASS |
| lot 底色不压主路 rect[0,1664,3200,64] | PASS |
| 四栋在世界界内 (3200×2400) | PASS |
| 老井[1360,848] 与 market 西墙 x=1440 相距 80px（只隔一道墙） | PASS |
| 「超市工地 · 南大门」热点落在 market 南院门格 (x∈[2048,2208], y=1632) | PASS |
| 界碑 rect = [2880,960,16,32] | PASS |
| 界碑 hotspot = [2888,976]，reach=68（x+8, y+16 中心写法） | PASS |
| 界碑 label 含「碑」+ solid=true + color #8a8278 | PASS |
| 界碑离 A1 原位 [1856,960] 位移 1024px | PASS |
| 界碑[2880,960] 不压主路/坝/田/老井/老槐树冠/A4 四栋/A5 三栋 | PASS |
| 界碑不进河 polygon | PASS |
| 界碑可 E 检视（最近站位距碑心 24.0 ≤ reach 68） | PASS |
| 老井 shape label == hotspot title == 「老井 · 沥青补丁」 | PASS |
| market pos == A5 market pos == [1440,768]（超市同址） | PASS |
| shen_a4[96,320] wings 不压老槐上抬树冠 (1296,908.8) r96（wings_max_x=1184 < canopy_min_x=1200） | PASS |
| 只有一个 label 空 rect（field bbox 单例） | PASS |
| `road:true` rect 只有一个（`_scene_bboxes` merge 前提） | PASS |
| 界碑 solid 且 w≤32,h≤64 ⇒ 参与 y-sort（立着） | PASS |

### 2.2 A5（2026）—— 16 项全 PASS

| 断言 | 结果 |
|---|---|
| 世界界碑 rect = [32,1024,16,32] | PASS |
| 界碑 label 含「碑」+ solid=true + color #8a8278 | PASS |
| 界碑 hotspot pos=[40,1040] reach=68 + 文案完整 | PASS |
| 界碑是 shapes 数组最后一项 | PASS |
| 界碑是 hotspots 数组最后一项 | PASS |
| 界碑[32,1024] 不压主路/田/坝/老井/老槐树冠/非 school 房屋 | PASS |
| 界碑不进河 polygon | PASS |
| 界碑落在 school 的**墙格**内（格(1,18) 字符 `#` ⇒ 石头砌进围墙） | PASS |
| 界碑位于 school lot 内部（**故意**：围墙里的一块石头；任务书 §4 明写不要按「压 lot」判 FAIL） | PASS |
| 界碑可 E 检视（最近站位 (48,1008) 距碑心 33.0 ≤ reach 68） | PASS |
| 老井 shape label == hotspot title == 「老井 · 沥青补丁」 | PASS |
| 老槐 radius 160 未改动 | PASS |
| 老井 radius 48 未改动 | PASS |
| 老槐 solid=false（树不挡路） | PASS |
| 只有一个 label 空 rect（field bbox 单例） | PASS |
| `road:true` rect 只有一个（竖路用 polygon，非 road:true） | PASS |

### 2.3 跨帧（不许动的东西）—— 5 项全 PASS

| 断言 | 结果 |
|---|---|
| a1_1926 界碑保持 [1856,960,16,32] / 热点 [1864,976]（一字未改） | PASS |
| a2_1951 界碑保持 [1856,960,16,32] / 热点 [1864,976]（一字未改） | PASS |
| a3_1976 界碑保持 [1856,960,16,32] / 热点 [1864,976]（一字未改） | PASS |
| world / safe_top / safe_bottom / start_pos 未被改动（3200×2400 / 36 / 2240 / [1024,1680]） | PASS |
| 帧序不变 [a1_1926, a2_1951, a3_1976, a4_2001, a5_2026] | PASS |

### 2.4 自检脚本自身的两个坑（记录给下一任）

1. **`is_wall` 是 interior 优先**（`scripts/house_shape.gd:158-165` 首行 `if interior.has(...): return false`）—— 把整个室内当墙会把整栋房变成实心块，会误判「进河」和「不可站」。
2. **遮挡判据按 wings（碰撞体）计，不按 lot 底色** —— 任务书 §3.1 自己的定案（shen_a4 左移 32px）就是按 wings 算的；按 lot 底色算则任务书的定案也会 FAIL。

---

## 3. 七套回归（改后实跑，**判绿看关键字**；原始输出存 `C:\Users\lyh\AppData\Local\Temp\mapfix_reg\*.txt`）

| 套件 | 关键字 | 结论 |
|---|---|---|
| `greybox_check` | `WORLD_OK=true` `START_OK=true` `DOOR_PASSABLE=true` `WALL_BLOCKED=true` `HOTSPOTS_OK=true` `REACH_OK=true` `UNEXPLAINED_BLOCKS=0` `TIME_FWD_REACHED=[1, 2, 3, 4]` `A2_MILL_SAME_SPOT=true` `A3_OLD_WELL_UNDER_MILL=true` `A2_OLD_WELL_NO_WELL_SOLID=true` `A3_OLD_WELL_FREE=true` | ✅ 全绿 |
| `camera_check` | `CAMERA_CHECK_DONE fails=0` | ✅ |
| `display_check` | `CONTENT_SCALE_MODE=1` `CONTENT_SCALE_ASPECT=1` `CONTENT_SCALE_SIZE=(1280, 720)` `默认纹理过滤=0` `STRETCH_SCALE_MODE=0` | ✅ |
| `hud_layout_check` | `HUD_CHECK_DONE fails=0` | ✅ |
| `asset_draw_check` | `ASSET_DRAW_CHECK_DONE fails=0`（含 `PASS a4_2001 无场景图 → null`） | ✅ |
| `sort_check` | `SORT_CHECK_DONE fails=0` | ✅ |
| `evidence_archive_check` | `EVIDENCE_CHECK_DONE fails=0` `COLLECTED 收集入档已验证` `NO_DUP 去重已验证` `EVIDENCE_OK` | ✅ 全绿 |

**五帧 solids / hotspots**：`a1 239/10`、`a2 300/11`、`a3 380/13`、`a4 646/13`、`a5 534/11`。
⇒ A4 solids 646 → **646**（不变）、hotspots 13 → **13**（不变）；A5 solids 533 → **534**（+1＝新增界碑矩形）、hotspots 11 → **11**（新增界碑热点 + 撤掉 school 家具热点 = 抵消，**总策划 D1 已闭合**）。

### 3.1 `REACH_MAP` 改前 / 改后对比与解释（任务书 §4 要求）

| 指标 | 改前 | 改后 | Δ |
|---|---|---|---|
| `standable`（A1 可站点数） | 6127 | 6127 | 0 |
| `to_a5`（五帧全可站） | 4746 | **4848** | **+102** |
| `blocked_at_step` | `[144, 191, 704, 342]` | `[144, 191, 722, 222]` | A4 +18 / A5 −120 |
| `band_total` / `band_full` / `band_ratio` | 196 / 159 / **81%** | 196 / 159 / **81%** | 不变 |
| `ratio` | 77% | **79%** | +2% |

**归因（脚本 `mapfix_reach.py` → `mapfix_reach.txt`，逐点差集，完全闭合）**：

- 两版都五帧全可站：4663（不变）。
- 改前被顶住 → 改后通了：**185** 点（其中 **107** 点改前被 A4 的 `market` 挡住、78 点其它）。
- 改前通 → 改后被顶住：**83** 点（**全部落在改后 `shen_a4` 的 wings 里**：57 + 18 + 7 + 1 非房屋）。
- **校验：185 − 83 = +102 ＝ `to_a5` 的 Δ，完全闭合。**
- 顶住时刻提前 143 点（old=4→new=3，即从 A5 提前到 A4 挡）、推迟 23 点（old=3→new=4）。

**`blocked_at_step` 的 A4 +18 / A5 −120 是「首次被顶住」的记账效应**，不是净变化：同一批点从 A5 提前到 A4 挡 ⇒ A5 列少 143、A4 列多 143；净 A4 = +143 −23 +83 −185 = **+18**、A5 = −143 +23 = **−120**，与实测完全一致。

**逐帧独立挡点数（不看「首次」）才是净变化**：

| 帧 | 改前 | 改后 | Δ |
|---|---|---|---|
| A2 | 144 | 144 | +0 |
| A3 | 261 | 261 | +0 |
| A4 | 808 | **812** | **+4** |
| A5 | 600 | **600** | **+0** |

⇒ **真正变松的只有 A4 帧的 4 个站位**（`market` 从 y576 挪到 y768，让出 y576–768 那条带）；A5 帧既没变松也没变紧。

**A5 新增世界界碑 `[32,1024,16,32]` 的碰撞贡献 = 0**：A1 站位中与该 rect 探针相交的只有 **1** 点，且该点改前改后都已被 A5 挡（被 school 墙挡住）⇒ 新碑**不改变可行走图**。

**关键几何对照**：

```
market     A4 [1440, 576] -> [1440, 768]      （wings 足迹 y∈[576,1472] -> y∈[768,1664]）
shen_a4    A4 [128, 320]  -> [96, 320]        （wings 足迹 x∈[192,1216] -> x∈[160,1184]）
zhou_a4    A4 [1792,1728] -> 未动
zheng_a4   A4 [2560,1728] -> 未动
market     A5 [1440,768]  -> 未动
```

### 3.2 结论：**这是「空间冻结」的正常表现，不是回归**

A4 的超市扩建到 x1440–2784 / y768–1664（南沿恰好贴主路北缘），A1 站在它将来 footprint 上的点推帧到 A4 会被顶住；而 A4→A5 因为两帧同址，卡点反而少了。**总策划 §8.4 观察1 要求的「实机走一遍 A1→A5 主路」已补做，见 §4.2，结论：走通，玩家不会被卡在超市工地里。**

---

## 4. 实机验收（总策划验收尾巴 ② + R2 要求）

### 4.1 实机逻辑验收：`mapfix_live.gd` → **LIVE_CHECK_DONE checks=57 fails=0，EXITCODE=0**

走引擎真代码路径（`Timeline` → `FrameData` → `HouseShape`），覆盖：

- A4 `market[1440,768]` **== A5 `market[1440,768]`**（超市同址不搬家）；`shen_a4[96,320]`；`zhou_a4[1792,1728]`/`zheng_a4[2560,1728]` 未动。
- 四栋墙体可生成：market rects=183 / shen_a4=285 / zhou_a4=77 / zheng_a4=65。
- A4 界碑 rect+热点+reach 68+solid+label「碑」+**可站位 (2911.9,978.5)、`hotspot_at` 命中「界碑」d=24.0**。
- A4 老井 center[1360,848] r32 label「老井 · 沥青补丁」+**井右缘 1392 距超市西墙 1440 尚有 48px**（不压墙）+新文案含「沥青补丁」「底下是空的」。
- A4 南大门热点 [2112,1632] 落在 market 南院门格 x∈[2048,2176] + 可 E 命中。
- A5 界碑 rect+热点+reach 68+为 shapes/hotspots 末项+**落在 school lot 内部（故意）+可站位 (46.7,1008.7)、命中 d=32.0**。
- A5 老井 label 与 title 对齐、cx=1360 在竖路车道正中 x∈[1328,1392]。
- A4/A5 出生点 (1024,1680) 可站；**BFS 证明 A4/A5 出生点都能走到界碑/老井/南门/超市门口**。
- 家具级热点自动跟随（文件柜 (2672,1120)、shen_a4 账桌 (1008,944)）。

### 4.2 实机走 A1→A5 主路（总策划 §8.4 观察1）：`mapfix_route3.gd` → **ROUTE_CHECK_V3_DONE checks=15 fails=0，EXITCODE=0**

| 检查 | 结果 |
|---|---|
| 主路带（y1664..1728）每一列至少有一行五帧都可真站 | PASS `no_standable_column=[]` |
| A4 主路主体（y≥1680）可站 | PASS（北缘 y=1672 不可站是 **14px 探针蹭超市南墙 6px**，不是路被堵） |
| A5 界碑周围有可站位且在 reach 68 内 | PASS（最近 (56,1008) d=36） |
| A5 界碑按 E 命中热点 | PASS `title=界碑` |
| A5 界碑周围一圈有可站位（不把自己封死） | PASS（5×5 邻域可站 9 格，其中 **6 格与出生点连通**） |
| A5 老井：出生点能走到检视范围 + 按 E 命中 | PASS（d=11 / `老井 · 沥青补丁`） |
| A4 界碑：出生点能走到检视范围 + 按 E 命中 | PASS（d=33 / `界碑`） |
| A4 老井：出生点能走到检视范围 + 按 E 命中 | PASS（d=11 / `老井 · 沥青补丁`） |
| A4 超市工地 · 南大门：出生点能走到检视范围 + 按 E 命中 | PASS（d=11 / `超市工地 · 南大门`） |
| **没有玩家站进去就被四面围死的格子（不会卡死在超市工地里）** | PASS `surrounded=0` |
| A1 可达且 A4 变实心的格 = 1026，占 A1 可达总数 22953 的 **4.47%** | 已记录（量化补充 §3.1） |

**附带信息**：A5 帧南门位置 (2104,1640) 按 E 无热点 —— 这是**预期**的，「超市工地 · 南大门」是 A4 专属手写热点。

**结论：玩家从 A1 出生点一路走到 A5，主路全程有路、不会被超市工地围死。**（本线未改任何碰撞数据，走通是改位本身的结果。）

### 4.3 实机截图（8 张，1280×720，存在 `docs/_mapfix_shots/`）

> 截图脚本 `mapfix_shot.gd` 走 `res://scenes/main.tscn` 真场景（开窗跑，`OpenGL API 3.3.0 NVIDIA RTX 5060 Laptop GPU`），逐帧切 `tl.index` + 定位 `tl.char_pos` + `_refresh_all()` + 相机 `set_target/_clamp/_apply` + `await RenderingServer.frame_post_draw` + `save_png`。

| 截图 | 内容 | 验收点 |
|---|---|---|
| `a4_market_gate.png` | A4 超市工地南大门（大片红褐工地色、道具标签「磨石车/洗灰机/收银箱/搅灰桶/水缸」可见） | §3.5 热点落在真门口 |
| `a4_stele_east.png` | A4 界碑在工地东侧空地（竖条形小碑） | §3.3 挪位生效 |
| `a4_well_west_wall.png` | A4 老井在超市西墙外 | §3.4 —— **树冠压着井（遗留问题，见 §6）** |
| `a4_shen_house.png` | 沈家四合院（家具齐全，账桌/保险柜可见） | §3.1 shen_a4 位置 + §3.7 家具热点 |
| `a4_zhou_zheng_south.png` | 周家/郑家落在主路南侧 | §3.2 定案口径 |
| `a5_market_same.png` | A5 超市与 A4 同址不搬家 | §3.1 超市同址 |
| `a5_stele_school_wall.png` | A5 小学围墙西端（**左上角可见界碑**） | §3.6 世界界碑落地 |
| `a5_well_lane.png` | A5 老井在车道正中 | §3.6 井命名对齐（label 与 title 同为「老井 · 沥青补丁」） |

### 4.4 `git diff` 边界证据（a1/a2/a3/world/safe_top/safe_bottom/start_pos 一字未动）

```
$ git show --stat 0436c58
 data/frames.json | 42 +++++---
 1 file changed, 32 insertions(+), 10 deletions(-)
```

`git show 0436c58 -- data/frames.json` 的**全部 hunk**（共 8 处，逐条列出）：

| # | hunk 位置 | 内容 |
|---|---|---|
| 1 | `@@ -2615,6 +2615,7 @@` | A4 加 `_note`（新增 1 行） |
| 2 | `@@ -3075,7 +3076,7 @@` | A4 `market` pos `576` → `768` |
| 3 | `@@ -3083,7 +3084,7 @@` | A4 `shen_a4` pos `128` → `96` |
| 4 | `@@ -3130,8 +3131,8 @@` | A4 界碑 rect `1416,1600` → `2880,960` |
| 5 | `@@ -3146,9 +3147,9 @@` | A4 老井 hotspot `title` 与 `text` |
| 6 | `@@ -3161,8 +3162,8 @@` | A4 界碑 hotspot pos `1424,1616` → `2888,976` |
| 7 | `@@ -3189,7 +3190,7 @@` | A4 南大门 hotspot pos `2112,1456` → `2112,1632` |
| 8 | `@@ -3835,7 +3836,7 @@` / `@@ -3860,6 +3861,18 @@` / `@@ -3916,6 +3929,15 @@` | A5 井 label 加空格；A5 新增界碑 shape + 新增界碑 hotspot |

**该 diff 里没有任何 hunk 落在 `world` / `safe_top` / `safe_bottom` / `start_pos` / `a1_1926` / `a2_1951` / `a3_1976` 段上** ⇒ 这四组数据与前三帧**一个字节都没动**（几何自检 §2.3 亦已逐项复核通过）。

另：`git log 0436c58..HEAD -- data/frames.json` 为空 ⇒ 后续提交（L3 房屋数据线 `7805d71`、文档线）**没有再动过 frames.json**，本线提交仍是最终版本。

**行尾说明**：`.gitattributes` 是 `* text=auto eol=lf`，工作区文件保持 **CRLF**（与改前一致），入库归一化成 LF ⇒ diff 只有本线 32 + / 10 −，**不会整文件翻行尾**（已实测 `git diff --stat`）。写入方式：读 JSON → 只改 a4/a5 两个对象 → `json.dumps(ensure_ascii=False, indent=2).replace('\n','\r\n')` 整份写回（往返**字节级完全一致**已验证，文件末尾无换行符，未追加）。

---

## 5. §3.6 的跨线冲突（`school` 家具界碑）—— **已由房屋数据线闭合，本线不越界处理**

### 5.1 冲突原貌（任务书 §3.6 原文）

同一块石头（操场北围墙西端那格墙）会有**两份证物**：

- `school` 家具「「周」界碑」rect `[1,18,2,1]` ⇒ 世界坐标 (64, 1040)；
- 本线新增的 A5 世界界碑 rect `[32,1024,16,32]`、热点 (40,1040)。

两者只差 24px ⇒ **玩家在同一处能检视到两块碑，证物档案多出一条重复记录**。

### 5.2 现状复核（实测 `_ref/houses/houses_data.json`，HEAD `65bf061`）

| 项 | 实测 |
|---|---|
| `school` 家具数 | 155 → **154** |
| `school` 家具里含「碑」字的 | **0** |
| `school.clue` 列表 | 2 → **1** 条（只留剪彩台） |
| `school.note` 尾句 | 已改写为指向 **A5 世界地标界碑**（rect `[32,1024,16,32]`、热点 (40,1040)，「由地图线 frames.json 落地」），并注明「本数据不再挂「界碑」家具，免得玩家在同一处检视到两块碑、证物档案多出一条重复记录」 |

⇒ **冲突已闭合**：那块石头现在**只有一份证物**（`data/frames.json` 的 A5 世界界碑），归地图帧数据。**本线没有碰 `_ref/houses/houses_data.json` 一个字节**，这是房屋数据线 commit `7805d71` 做的。

### 5.3 建议改法（交房屋数据线 / 已由其执行，本线只登记）

1. **家具 `furniture[]` 整条删除**（「「周」界碑」含 name/short/rect/note/clue/zone/yard_building/wall_mounted）—— **已执行**。
2. **`clue` 列表删该条**，只保留剪彩台 —— **已执行**。
3. **`note` 尾句改指向世界界碑**（叙事不抹掉，但明确归属）—— **已执行**。
4. **`lot`/`wings`/`partitions`/`doors`/`gate`/`rooms` 一个字未动**（那格墙还在，形状由本线的 frames.json 放）—— **已执行**。
5. **不许在 `scripts/house_shape.gd` 的 `CLUE_TEXTS` 里补 school 界碑条目** —— A5 那块碑的文案在 `data/frames.json`，补了就是两个来源。**⇒ 总策划 D5 已派给 L4 删除 `scripts/house_shape.gd:107` 的 `CLUE_TEXTS["school"]["「周」界碑"]`；L4 若尚未删，请按 D5 执行。**
6. ⚠️ **复发风险（D3 / R3，另一条线）**：`_ref/houses/gen_all_houses.py:294`/`:300` 与 `_ref/houses/_redo_school.py:22/27/226/256` 仍带界碑家具代码。**任何人重跑生成器都会把界碑加回来**，届时 A5 会出现两块碑 + 档案多一条重复记录。**本线不碰 py 文件**（那是「生成器对齐」小线的活）。

---

## 6. 遗留问题 / 需知会

1. **「老槐遮井」是渲染线（L2）的活，本线一律没碰 `scripts/world_view.gd`。**
   实测机理：`scripts/world_view.gd:596` `var lifted := center + offset + Vector2(0, -rad * 0.7)` ⇒ 树冠画在 `center.y - r*0.7`（A4 老槐 r96 ⇒ 圆心 (1296,908.8)；A5 老槐 r160 ⇒ 圆心 (1296,864)）。而 A4/A5 的老槐**没有 tree 贴图** ⇒ 走色块分支 ⇒ 树冠直接盖住井。**截图 `a4_well_west_wall.png` 可见此现象。**
   ⇒ **L2 落地后**再看实机定 A5 老槐 r=160 是否收成 128（总策划验收尾巴 ③）。
   ※ 本线在 A4 已把 `shen_a4` 左移 32px 让开**上抬后的树冠**（wings_max_x=1184 < canopy_min_x=1200），但这只解决「建筑压树冠」，**解决不了「树冠压井」** —— 后者是绘制优先级问题。
2. **A5 老槐 r=160 未改动**（任务书明写不改）—— 尺寸偏大待 L2 后定，见上条与 §0 E3。
3. **界碑贴图会被压扁**（16×32 的 rect 配 32×32 的图，`world_view.gd:605-615` 直接把贴图拉伸到 rect 尺寸）—— 归**资产接线线（L8）**，要改成「底部中心锚点、1:1 不拉伸」。**本线只管数据，没碰 `world_view.gd`。**
4. **`asset_draw_check.gd:216` 断言 A4 无场景贴图** ⇒ 本线**没有**给 A4/A5 补任何场景图（补了会撞这条断言）；A4/A5 的 base/roof/界碑/树/井贴图全部由美术同学出（清单在 `docs/ART-HANDOFF-a4a5.md`）。
5. **A4 热点标题「超市工地 · 南大门」保持不动**（见 §0 E1，沿用总策划 D4 裁决）。
6. **A5 帧同位置无手写热点**（见 §0 E2），A5 是营业中的超市。
7. **`docs/HANDOFF-VILLAGE.md` 有 7 处「周」界碑是 school 家具的过期描述**（`:78`/`:147`/`:289`/`:362`/`:397` 是当前状态表要改；`:307`/`:334` 是历史记录不改写）—— 归 **L6 文档线**，本线不改 `docs/**`（除本文件与截图目录）。
8. **房屋数据线 R1（两处 px 旧 16px 口径回退）** 与 **R3（生成器对齐）** 未由本线处理，仍挂在 L3 / 小线名下。

---

## 7. 依据文档

`docs/DECIDE-a4-a5-layout.md`（§11 裁定①「界碑做成每帧独立世界地标」）、`docs/PROMPT-map-fix-exec.md`（§3 全部 9 项）、`docs/story.md` §4.4 / §7.1 / §7.2⑥ / §7.4（井与界碑叙事依据）、`docs/BUILD-A1.md:95-118`（地标与路的跨帧口径）、`docs/PROMPT-overseer.md`（L1 调度与验收尾巴）、`docs/FEEDBACK-houses-fix-exec.md` §8（L3 验收意见 D1–D5 + R1–R3）、`docs/ART-HANDOFF-a4a5.md`（贴图清单，交美术同学）。

---

## 8. 验收栏（请总策划填写）

- [x] **通过** —— 9 项必改全部达标；几何自检 44 PASS / 0 FAIL；七套回归全绿；实机逻辑 57 项 0 FAIL；实机 A1→A5 主路走通；边界（只改一个数据文件）达标。
- [ ] **需返工** —— 请注明条目：____________________
- 其他要求：E1 保持 A4 标题「超市工地 · 南大门」；E2 A5 不补手写热点；E3 A5 老槐 r=160 等 L2 落地后再定；R1/R2/R3 见 §6。
- 验收人：**项目总策划会话（lead）**　日期：**2026-11-23**

---

## 附：本线脚本索引（全部在仓库外，未入库）

| 脚本 | 用途 | 结果 |
|---|---|---|
| `C:\Users\lyh\AppData\Local\Temp\mapfix_apply.py` | 应用 9 项改动（改前备份 `frames_before.json`） | `frames.json` 75438 → 76291 字节 |
| `…\mapfix_geom.py` | 几何自检（复刻引擎语义） | 44 checks / 0 FAIL |
| `…\mapfix_reach.py` | `REACH_MAP` 改前改后差集归因 | 185 − 83 = +102 完全闭合 |
| `…\mapfix_live.gd` | 实机逻辑验收（引擎真路径） | 57 checks / 0 FAIL |
| `…\mapfix_route.gd` / `…\mapfix_route2.gd` / `…\mapfix_route3.gd` | A1→A5 主路实机走查（v1/v2 判据口径纠错，最终 v3） | 15 checks / 0 FAIL |
| `…\mapfix_shot.gd` | 开窗实机截图（8 张 → `docs/_mapfix_shots/`） | EXITCODE=0 |
| `…\mapfix_reg\*.txt` | 七套回归原始输出 | 全绿 |

> 脚本放在仓库外是因为任务书 §6 禁止本线写 `_mdtest/` 与 `lab/`；全部脚本只读仓库文件，不改任何工程代码。
