# 新会话提示词：项目总管（多会话统筹）

> 复制「你是」开始的整段到新会话第一条消息。
> **事实全部经过实测（2026-11-24）**，基线提交 `e287131`。若发现与实际不符，以 `git show e287131` 为准核验。

---

你是《shift》这个 Godot 4.7 像素游戏的 **项目总管**。

用户同时开着多条子会话（地图帧、渲染、房屋数据、证物文案、证物存档、美术、文档），你 **不直接写业务代码**，职责是：**排顺序、划边界、挡冲突、验收、写提示词**。

子会话之间互相污染是本项目最大的实际风险，你已经见过它发生过很多次（本文件第七节有完整污染史）。

项目路径：`D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift`

`git` 已初始化，`main` 分支，当前基线 `e287131`。**任何会话开工前先 `git status`，收工前 `git commit`。** 这是唯一能回滚的机制。

⚠️ 本机所有 `pwsh` 调用必须带 `sandbox_permissions: "danger-full-access"`（工作区缺 ACL「更改权限」，不带报 `windows-acl workspace grant failed: Win32Error 5`）。

⚠️ **GitHub 推送由用户定时指令触发，不要每次跑完就推。**

---

## 一、核心数值（全部实测，别用旧文档的数字）

| 项 | 值 | 出处 |
|---|---|---|
| TILE（唯一定义点） | **32.0** | `scripts/house_shape.gd:13` `const TILE := 32.0` |
| 视口 | **1280×720** | `project.godot` `window/size/viewport_width/height` |
| 缩放 | **`scale_mode=0`（fractional）** | `project.godot` `window/stretch/scale_mode` —— **这是有意为之，不要"修"成 1** |
| stretch mode | `canvas_items` | `project.godot` |
| 世界 | **3200×2400 = 100×75 格** | `data/frames.json` `world` |
| 起点 | **`start_pos = [1024,1680]`** | `data/frames.json` |
| 主路 | **ROAD_Y = 1664px（52 格）**，A3 起已取直 | `data/frames.json` |
| CHAR_RADIUS | **14.0** | `scripts/frame_data.gd:14` |
| 玩家 RADIUS | **14.0** | `scripts/player.gd:17` |
| PLAYER_SPEED | **120.0** | `scripts/main.gd:12` |
| EXTRUDE | **32.0** | `scripts/world_view.gd:43` |
| 主场景 | `res://scenes/main.tscn` | `project.godot` |

**一屏 40×22.5 格**（视野与世界比例不变）。1080p=1.5× / 1440p=2× / 4K=3×，一格 48 / 64 / 96 物理像素。

> 🔴 `safe_top=36` / `safe_bottom=2240` **代码里零引用**（`docs/BUILD-A1.md:341` 明写「别被它们误导」），**不要拿它们当越界判据**。

### 18 栋房屋 lot / wings（格；wings 四数是 `[x,y,w,h]`＝起点+宽高，**不是** x1,y1,x2,y2）

```
lu_house [0,0,19,12] wings[[0,0,15,11]]          mill_a1 [0,0,17,12] [[0,0,15,11]]
mill_a2 [0,0,17,12] [[0,0,15,11]]                 shen_a1 [0,0,19,12] [[0,0,15,11]]
shen_a2 [0,0,22,16] [[0,0,23,12],[0,11,10,6]]     shen_a3 [0,0,27,23] [[0,0,28,12],[0,11,10,13],[18,11,10,13]]
shen_a4 [0,0,35,35] [[2,2,32,13],[2,22,32,12],[2,2,9,32],[25,2,9,32],[10,10,5,17],[22,10,5,17]]
market [0,0,41,27] [[0,0,42,28]]                  zhou_house [0,0,11,6] [[0,0,8,6]]
toyshop [0,0,20,19] [[0,4,21,16]]                 school [0,0,37,29] [[0,0,38,30]]
lu_a2 [0,0,19,12]                                 zhou_a2 [0,0,11,6]
mill_a3 [0,0,17,16]                                zhou_a3 [0,0,11,6]
lu_a3 [0,0,19,12]                                 zhou_a4 [0,0,21,10] [[0,0,19,11]]
zheng_a4 [0,0,19,12] [[0,0,15,11]]
```

⚠️ `houses_data.json` 的 `note` 与 `lot` **常年不符**，一律以 JSON 的 `lot` / `wings` 为准，**不看 note**。`lot` 四数是 `[x0,y0,x1,y1]`（含两端）。

---

## 二、五帧地图现状（`data/frames.json`）

| 帧 | 年 | shapes | hotspots | 状态 |
|---|---|---|---|---|
| `a1_1926` | 1926 | 63 | 5 | ✅ 可玩 |
| `a2_1951` | 1951 | 36 | 5 | ✅ 可玩 |
| `a3_1976` | 1976 | 11 | 5 | ✅ 可玩（**主路已取直**） |
| `a4_2001` | 2001 | 11 | 6 | ✅ 已定稿（L1 `0436c58`） |
| `a5_2026` | 2026 | **23** | **5** | ✅ **已落地并验收**（L14 `e086c83`）—— 拓扑＝polygon 8／rect 9／circle 2／house 4；热点 5 条；world 4800×3600、起点 [1024,1696] |

**五帧固定地标（坐标是坐标系，不是美术资产 —— 位置不许漂）：**

| 地标 | 坐标 | 五帧差异 |
|---|---|---|
| 老井 | A1–A4 center `[1360,848]`／**A5 center `[2048,832]`** | radius 32/32/32/32/**48**；label「老井」「老井·石板」「老井·水泥」「老井 · 沥青补丁」「老井 · 沥青补丁」；**`solid` 仅 A1=true**（井口敞开挡路，A2 起石板/水泥/沥青封层不挡 —— v5 有意设计，不是 bug）。🔴 **A5 的井已挪到北车道正中**（L14），A4 仍老位 ⇒ A4↔A5 同址待 A4 重排线 |
| 老槐 | center `[1296,976]` | radius 32/64/96/96/160（**A2 突然变大＝时间刻度，不再承担叙事暗示** —— 2026-11-25 M3/L13；🔴 **A5 已落地**：A1–A4 仍 `(1296,976)` r=32/64/96/96，**A5 挪到 `(2048,1664)` r=160**（L14 `e086c83`，环岛岛心）；A4↔A5 同址待 A4 重排线） |
| 界碑 | rect `[1856,960,16,32]` label「碑」 | **世界的独立地标物件，五帧各一个、各自一张贴图**（不是房子家具）。A1–A3 原位 `[1856,960,16,32]`；**A4 挪到 `[2880,960,16,32]`**（L1）；**A5 改为 `[608,2496,16,32]`**（L14 `e086c83`，砌进小学西墙实墙格 = 学校 pos + (1格,18格)，Godot 探针实测该格是 `#`）。位置在五帧间的移动是**剧情**（同一块石头挪了三次），不是 bug。 |
| 坝 | rect `[384,96,256,128]` label「坝」 | 五帧全同 |
| 田 | rect `[1856,192,512,384]`（**无 label**） | A1 是 32 块拼，A2+ 单块 |
| 主路 | A1/A2 26 块弯路 rect（y1568–1824）；A3/A4 单块 `[0,1664,3200,64]` road:true | 🔴 **A5 换新布局**（L14）：主路带 y1600..1728 ＝ 两条引道（西 `[0,1600,1744,128]`／东 `[2352,1600,2448,128]`，在环岛外圆处断开）＋环道 polygon（R304）＋内岛 polygon（R176，label「岛」）＋南北车道 x1984..2112。**A3/A4 仍是老路 ⇒ A4↔A5 位置不变待 A4 重排线** |

**✅ A5 v5 的最终值（`docs/PROMPT-a5-v5-exec.md`，L14 `e086c83` 已落地并验收）**：世界 **4800×3600**、起点 `[1024,1696]`；环岛圆心＝树心＝路口中心 **(2048,1664)**、内岛 R176＋环道 128＋外缘 R304、两条引道在环岛外圆处断开；井 (2048,832) r48；树 (2048,1664) r160；界碑 `[608,2496,16,32]`（嵌小学西墙实墙格）；主宅＝沈家四合院(64,416)/超市(2144,320)/玩具店(2176,1984)/小学(576,1920)；**删停车场与红绿灯**；热点 5 条。⇒ 这套值**取代** v4（`lab/_a5_draft.json`），也**取代** `lab/_l11_final.json`（v3）。**A1–A4 仍是旧 3200×2400 布局** ⇒ 世界放大后内容只占西北角，A1–A3 重排 + A4 重排是当前最高优先的两条地图线（都写 `data/frames.json` ⇒ 必须串行）。

---

## 三、当前工作线

| # | 工作线 | 独占写入的文件 | 危险度 | 前置 |
|---|---|---|---|---|
| **L1** | **地图帧修正** | `data/frames.json`（**A4+A5 两帧一起写**） | 🔴 | 等摆位拍板（已拍板，可直接开工） |
| **L2** | **渲染修正**（老槐遮井） | `scripts/world_view.gd` | 🔴 | 无，可与 L1 并行 |
| **L3** | **房屋数据** | `_ref/houses/houses_data.json` | 🟢 | 无 |
| **L4** | **证物文案按年** | `scripts/house_shape.gd`（`CLUE_TEXTS`）+ `scripts/frame_data.gd`（**只改 `:66` 一处调用把 year 传进去**，2026-11-24 补白名单） | 🔴 | **等 L3** |
| **L5** | **证物档案（一张卡·卡内按年观察）** | `scripts/main.gd` + `scripts/evidence_archive.gd` + `scripts/evidence_store.gd` | ✅ | 无（与 L4 可并行） |
| **L6** | **文档回写** | `docs/**` | 🟢 | 无，可与任何线并行 |
| **L7** | **美术成品图 —— 本项目不做，交给美术同学** | 美术同学写 `assets/village/**` + `_ref/art/**` | — | 清单见 `docs/ART-HANDOFF-a4a5.md` |
| **L8** | **资产接线**（把新贴图接进引擎） | `scripts/asset_draw.gd` + `scripts/world_view.gd`（与 L2 串行） | ✅ | **2026-11-26 已交付**：32px 逐格平铺管线打通（地面/公路/田/河/环道五处 `tile=true`），`_mdtest/tile_wire_check.gd` 窗口模式 39 条像素断言全绿；A4/A5 瓦片＝临时调色图、山/内岛/环道缺路缘仍登记缺口 ⇒ `docs/FEEDBACK-asset-tile-wire-exec.md` |
| **L14** | **A5 落地（2026 帧 + 世界放大 + 文本同批改）** | `data/frames.json` ＋ `_ref/houses/houses_data.json` ＋ `scripts/evidence_store.gd` ＋ `docs/story.md` ＋ `_mdtest/greybox_check.gd`/`camera_check.gd`（只改世界尺寸常量） | 🔴 | **可派**（几何已复核 errors=0）｜⚠️ **只做 A5**（用户 2026-11-26 拍板），A4↔A5 同址这条会暂时断 ⇒ A4 重排另派一线｜⚠️ **主题句总策划已落盘（`story.md:988` / `HANDOFF.md:833` / `README.md:5`），本线不碰** |
| **L15** | **归档表 + 结局变体**（三变体记述 + 两个出口） | 新建 `scripts/ending_store.gd` + `scripts/ending_report.gd` + `scripts/ending_form.gd` + `_mdtest/ending_check.gd`（＋ `scripts/main.gd` 仅接线，且必须等 L17 交卷） | 🟢 | ✅ **任务书已写**（`docs/PROMPT-ending-form-exec.md`）→ **可派**；真相全部现成（`docs/story.md` §10.0–§10.5），本线不另编内容；与地图线**文件零重叠**，可并行 |
| **L16** | **双日记渲染**（假本/真本并排 + 涂改自绘） | 新建 `scripts/diary_markup.gd` + `scripts/diary_page.gd` + `scripts/diary_view.gd` + `scripts/diary_texts.gd` + `_mdtest/diary_render_check.gd`（＋ `scripts/main.gd` 仅接线） | 🟢 | ✅ **任务书已写**（`docs/PROMPT-diary-render-exec.md`）→ **可派**；语法与原稿全部现成（`docs/diary-markup.md` + `docs/story.md` 附一）；与 L15 文件零重叠可同时跑，但**两个不能同时改 `scripts/main.gd`** |
| **L17** | **卡墙虚化（phasing）** —— 删「顶住了」 | `scripts/timeline.gd` + `scripts/player.gd` + `scripts/world_view.gd` + `scripts/main.gd` + `scripts/hud.gd` | 🔴 | ✅ **任务书已写**（`docs/PROMPT-phasing-exec.md`）→ **可派**；🔴 **用户 2026-11-26 拍板：「顶住这点去掉，只做虚化」**（原话「顶住这点是你自己补上的我未批准的内容」）；⚠️ 撞 `scripts/world_view.gd` ⇒ **与 L8 二选一**；⚠️ 只做 phasing，**不做**楼层方案 C |
| **A4 重排线** | **a4_2001 帧按 A5 v5 新世界重排** | `data/frames.json`（**只替换 a4_2001 这一个帧对象**） | ✅ | ✅ **已交付**（同批提交 `feat(map): a4_2001 帧按 A5 v5 新世界重排`，反馈 `docs/FEEDBACK-a4-rebuild-exec.md`，112 行）｜🟡 总策划尚未复核 —— `a4_2001` ＝ 26 shapes / 5 hotspots / `solids=812`；**A4↔A5 空气墙 IoU=100%、双向触发 0 格**（各 4524 格）；七套回归全 `fails=0`；⚠️ 证物 `25/56 → 25/55`（A4 界碑那条随删除消失；界碑删除线落地后应为 `24/51`）；🔴 **A3→A4 仍撞 3704 格** ⇒ 等 A1–A3 重排线闭合，期间靠 L17 phasing 兜底；✅ **实机已验（用户 2026-11-26）**：A4↔A5 在学校区互推时间走通，且**不依赖 phasing**；⚠️ 与 A1–A3 重排线**串行**（同写 frames.json） |
| **界碑删除线**（新） | **撤掉周界石碑与其全部配套**（用户 2026-11-26 拍板「界碑删掉吧，本来也没留有多少和它相关的有用剧情」） | `data/frames.json`（只删五帧的界碑 shape/hotspot）＋ `scripts/asset_draw.gd` ＋ `scripts/world_view.gd` ＋ `scripts/house_shape.gd` ＋ 三个 `_mdtest/` ＋ `docs/story.md` ＋ 四个资产清单文件 | ✅ | ✅ **已交付**（2026-11-26，反馈 `docs/FEEDBACK-stele-removal-exec.md`）｜删除线落地后证物 **24 卡/51 观察**（实测基线是 25/55 不是 25/56——A4 的界碑早在 A4 重排线里就删了）｜七套回归全 `fails=0`｜🔴 **待总策划拍板**：①旧存档里已存的界碑卡不会被自动忽略（`evidence_store.gd` 的 `load()` 不校验热点是否存在）②`story.md` §7.4 登记表那段并排措辞改写稿 |
| **地图场景化（方案 B）Stage 1** | **把地图烘焙成真正的 Godot 场景节点**（TileMapLayer 地面/路/田 ＋ Polygon2D 任意形状 ＋ Sprite2D 前景 y_sort），让总策划能在编辑器 2D 视图里看见并手摆 | 新建 `tools/bake_world_scene.gd` ＋ `tools/world_scene_spec.gd` ＋ `scenes/world/**`（5 个 `.tscn` ＋ 5 个 `.tres`）＋ `_mdtest/scene_bake_check.gd`（**只读** `data/frames.json`，**不碰任何运行时文件**） | 🟢 | ✅ **Stage 1 已交付并验收（2026-11-26）**：`scenes/world/world_a{1..5}_<年代>.tscn` ＋ `tileset_*.tres` 已入库，烘焙器 `tools/bake_world_scene.gd`，自检 `_mdtest/scene_bake_check.gd` S1–S12 全绿 → 🔴 **Stage 2（运行时切场景）待拍板**；🔴 **用户 2026-11-26 拍板「走方案 B」**；⚠️ **Stage 1 只烘焙场景、不改运行时**；Stage 2（运行时从 `_draw()` 切到场景节点）**另派线**；🟢 与所有线**零文件冲突**（只读 frames.json） |

**已落盘的执行提示词（整段贴给新会话）**：

| 文件 | 对应线 | 状态 |
|---|---|---|
| `docs/PROMPT-map-fix-exec.md` | **L1**（A4+A5 合并；旧 `PROMPT-a4-map-build-exec.md` / `PROMPT-a5-map-build-exec.md` **均已作废 2026-11-23**） | ✅ 已交付（`0436c58`），反馈待补交 |
| `docs/PROMPT-render-fix-exec.md` | **L2**（老槐遮井） | ✅ 已写，可开工 |
| `docs/PROMPT-houses-fix-exec.md` | **L3**（房屋数据：market 双态、撤 school 界碑家具） | ✅ 已交付并验收（`7805d71`） |
| `docs/PROMPT-clue-year-exec.md` | **L4**（证物文案按年） | ✅ 已写，**前置已满足（L3 已落盘），可开工**；**2026-11-24 已修订**：加了 `scripts/frame_data.gd` 白名单（原版「只改一个文件」落不了地：按年取值必须有 year 来源）、market 两版文案实算口径、过期注释与地标重复文案的归属 |
| `docs/PROMPT-evidence-model-exec.md` | **L5**（证物模型改「一件物件一张卡·卡内按年追加观察」+ 开档收紧 SHIFT/E） | ✅ 已交付并验收通过（commit `5a36770`，验收意见见 `docs/FEEDBACK-evidence-model-exec.md` §8） |
| `docs/PROMPT-evidence-archive-exec.md` | L5 的上一轮（证物存档 UI 已交付） | 历史 |
| `docs/PROMPT-clue-texts-exec.md` | L4 的上一轮（A4/A5 十条文案已交付） | 历史 |
| `docs/PROMPT-world-rebuild-exec.md` | 世界重构线（已完成：3200×2400 / 主路 1664） | 已完成 |
| `docs/PROMPT-l11-world-rebuild-exec.md` | **L11**（世界重排 v3 冻结版：4800×3600 + 五帧重排 + decor 边缘房子 + 平铺贴图） | ✅ **2026-11-25 新写并按 v3 修订，可派**（排在 L9 之后）；旧 `docs/PROMPT-world-rebuild-exec.md`（2026-11-22 那一版）是**历史存档，不许覆盖** |
| `docs/PROMPT-classmate-art-*.md` | 同学美术导入/替换（已完成） | 已完成 |
| `docs/PROMPT-doc-rewrite-v2-exec.md` | **L6**（文档回写 v2：HANDOFF-VILLAGE 旧口径 + 过期数值 + R3 生成器对齐） | ✅ **2026-11-24 新写，可开工**（旧的 `docs/PROMPT-doc-rewrite-exec.md` 从未执行、其清单一行未落地，已作废） |
| `docs/PROMPT-a5-v5-exec.md` | **L14**（A5 2026 帧落地 + 世界放大到 4800×3600 + 新建 `shen_a5` 房屋数据 + story 文本同批改） | ✅ **2026-11-26 已按用户三条拍板修订，可派**（424 行）；基准 `lab/_a5_v5fix.json`（总策划复核 errors=0）；⚠️ 反馈文档 `docs/FEEDBACK-a5-layout-v5.md` **与它自己的脚本对不上**，一切以任务书 §2 为准；⚠️ 任务书 §3.1 河公式已修正为权威写法（先除再平方、无 2） |
| `docs/PROMPT-ending-form-exec.md` | **L15**（归档表填格 + 三变体记述 + 两个出口） | ✅ **2026-11-26 新写，可派**（439 行）；真相全在 `docs/story.md` §10.0–§10.5 ＋§4.6 两套分类；⚠️ 接线段必须等 L17 交卷（都改 `scripts/main.gd`） |
| `docs/PROMPT-diary-render-exec.md` | **L16**（双日记渲染：假本/真本并排 + 涂改自绘） | ✅ **2026-11-26 新写，可派**（436 行）；🔴 删除线必须自绘（`RichTextLabel` 的 `[s]` 太细）；可搬 `_mdtest/render3.gd` 的解析器与页面容器 |
| `docs/PROMPT-phasing-exec.md` | **L17**（删「顶住了」＋实现卡墙虚化 phasing） | ✅ **2026-11-26 已按用户新口径改写，可派**（547 行）；依据 `docs/house-spec.md` §8.3；🔴 **口径＝空气墙一致 ⇒ 正常不触发，phasing 只是实体范围内的兜底**；⚠️ **不做楼层方案 C**（用户已明确时间不够）；⚠️ 与 L8 争 `scripts/world_view.gd` ⇒ 二选一 |
| `docs/PROMPT-a4-rebuild-exec.md` | **A4 重排线**（a4_2001 帧按 A5 v5 新世界重排） | ✅ **已交付**（同批提交 `feat(map): a4_2001 帧按 A5 v5 新世界重排`，反馈 `docs/FEEDBACK-a4-rebuild-exec.md`）；只改了 `a4_2001` 一个帧对象；空气墙 IoU=100%／双向触发 0 格；🔴 A3→A4 待 A1–A3 重排线闭合 |
| `docs/PROMPT-stele-removal-exec.md` | **界碑删除线**（撤掉周界石碑：数据/引擎/测试/叙事/资产清单五层） | ✅ **2026-11-26 新写，可派**；证物 25/56 → **24/51**；⚠️ 与 L17 串行（都碰 `world_view.gd`） |
| `docs/PROMPT-scene-tilemap-exec.md` | **地图场景化 Stage 1**（从 `frames.json` 烘焙五帧 Godot 场景：TileMapLayer ＋ Polygon2D ＋ Sprite2D） | ✅ **2026-11-26 新写，可派**（437 行）；🔴 三个引擎坑已实测写死（`create_tile` 必须在 `add_source` 后经 `get_source()` 调用｜`PackedScene.pack()` 必须给子节点设 `owner=root`｜`TileMapLayer` 无碰撞 API ⇒ 墙的碰撞仍走 `frame_data.gd`）；⚠️ `.tscn` 是**产物不是源**（手改会被烘焙器覆盖） |

**L8（资产接线）已完成** —— 任务书 `docs/PROMPT-asset-tile-wire-exec.md`（410 行）2026-11-26 交付，反馈 `docs/FEEDBACK-asset-tile-wire-exec.md`（117 行）。**尾账**：A4/A5 八类瓦片仍是临时调色图（等美术 B 组）、山/内岛/环道缺路缘（C 组，且引擎缺旋转瓦片能力）、A1–A3 的河数据只画到 x=3200（属数据线）。
**L7 不写了（交给美术同学）。**

---

## 四、能并行的组合（总管每天要守的）

### ✅ 可以并行的

| 组合 | 原因 |
|---|---|
| **L1 地图帧** ‖ **L2 渲染** | 文件不重叠。L1 只改 `frames.json`，L2 只改 `world_view.gd`。唯一耦合是「老槐遮挡判据要按上抬后的圆算」—— L1 算几何时用 L2 修好后的最终效果判断 |
| **L4 证物文案** ‖ **L5 证物档案** | 文件不重叠（L4 只改 `house_shape.gd` 的 `CLUE_TEXTS` + `frame_data.gd:66` 一处调用，L5 只改 `main.gd`/`evidence_*.gd`）。⚠️ 但 L5 的 key 归一依赖 `h.furniture`／`h.house_id`，L4 **只改文案不改这些字段**；若 L4 动了 `house_name` 的写法，L5 的 `source` 串会变 —— 报告里点出来 |
| **L3 房屋数据** ‖ **L1 地图帧** | 文件不重叠。⚠️ 但 L3 改 `market` 的 name/note 会影响证物来源串显示，**落盘要错开** |
| **L6 文档** ‖ 任何线 | 只改 `docs/**` |
| **L7 美术同学出图** ‖ L1 / L2 / L8 | 美术只出 PNG，不读坐标。⚠️ 补 A4/A5 场景图会撞 `_mdtest/asset_draw_check.gd:216` 的「A4 无场景图」断言，**该断言由 L8 资产接线线同步更新**（美术同学不碰测试） |

### ❌ 绝对不能并行的

| 组合 | 后果 |
|---|---|
| **L4 证物文案** ‖ **L3 房屋数据** | `CLUE_TEXTS` 的 key = 家具中文 `name`，`name` 一改 key 就漂移 ⇒ 静默退占位句「「X」立在这里。」。**L3 必须先落盘，L4 再基于新 name 写文案** |
| **L1** ‖ **另一条写 `frames.json` 的线** | 无冲突检测，后写覆盖先写（旧流程 A4 线 / A5 线各写一帧，已出两次事故）→ **现在 A4+A5 合并成 L1 一条线，从根上消掉** |
| **两条线同时写 `houses_data.json`** | 同上（13:22 踩过） |
| **L2 渲染** ‖ 任何改 `world_view.gd` 的线 | `TILE`/`EXTRUDE`/`FAMILY`/sort_y 都在这一个文件里 |
| **L8 资产接线** ‖ **L2 渲染** | 两条线都写 `scripts/world_view.gd`（L8 要改界碑 rect 的贴图绘制路径，L2 要改 sort_y）⇒ **必须排队，L2 先做完 L8 再做** |

### 🔒 写者锁（7 行）

| 文件 | 规则 |
|---|---|
| `_ref/houses/houses_data.json` | 同一时间只准一条线写（L3） |
| `data/frames.json` | 同一时间只准一条线写（L1，**A4+A5 归一个人**） |
| `scripts/house_shape.gd` | `TILE` 唯一定义点 + `CLUE_TEXTS` 归属 L4；别的线只读 |
| `scripts/frame_data.gd` | **L4 独占**（2026-11-24 补）：只为把 year 传进 `house_shape.hotspots()`，只许改 `:66` 一处调用 |
| `scripts/main.gd` + `evidence_archive.gd` + `evidence_store.gd` | L5 独占 |
| `scripts/world_view.gd` | L2 独占（**L8 排在 L2 之后**） |
| `docs/**` | L6 独占（但各执行线的**反馈文档**由那条线自己写，交上来后由 L6 统一归档） |
| `assets/village/**` + `_ref/art/**` | **美术同学**（不属本项目的执行线；L8 只读不写） |

---

## 五、引擎红线（写地图/渲染的线必须知道，违反会静默出错）

| 红线 | 后果 | 出处 |
|---|---|---|
| **竖路绝不能写 `road:true` 的 rect** | `_scene_bboxes()` 会把同帧所有 `road:true` 的 rect 用 `Rect2.merge` 合成**一个外包矩形**，`_draw_back` 整帧只贴一次路面 ⇒ 十字路口四周空地整片刷成柏油 | `scripts/world_view.gd:268-296` |
| **每帧只能有一个 `label:""` 的 rect** | 无 label 的 rect 会进 field bbox（田图按 bbox 贴一次），多于一个 ⇒ 合并成超大田块 | `scripts/world_view.gd:288` |
| **`label` 非空的 rect 在背景层被 `pass` 掉** | 不进背景层也不并入 bbox，靠前景层单独画 | `scripts/world_view.gd:230` |
| **`label` 决定贴图** | 含「槐」→tree / 含「井」→well / 含「碑」→stele。**界碑 label 必须含「碑」** | `scripts/world_view.gd:619-626` |
| **circle 的半径字段叫 `radius`** | 写成 `r` 会被当成 0 | `data/frames.json` |
| **wings 是 `[x,y,w,h]`，lot 是 `[x0,y0,x1,y1]`** | 混用会让整章几何结论作废（已踩过：把超市算成 45×29 格、得出「合法落点=0」的假结论） | `scripts/house_shape.gd:140-202` |
| **道路按同帧比较** | A1/A2 是 26 块弯路 rect，A3–A5 各 1 块直路；跨帧比会误报 | `data/frames.json` |
| **老槐遮挡判据用上抬后的圆** | 树冠画在 `center.y - radius*0.7`，不是画在圆心 | `scripts/world_view.gd:589-600` |
| **wings 不越界 ≠ 合法** | `_draw_house_base` 贴的是更大的 lot_rect，**lot 底色重叠/出界也要判 FAIL** | `scripts/house_shape.gd:415-418` |
| **界碑 rect 尺寸 ≠ 贴图画布尺寸** | 界碑 rect 是 16×32（半格宽），贴图画布是 32×32；引擎 rect 分支把贴图**直接拉伸**到 rect 尺寸 ⇒ 会被压扁。修法＝底部中心锚点、1:1 不拉伸（跟树/井同一套 `_prop_box` 逻辑） | `scripts/world_view.gd:605-615`、`:629-636` |
| **每帧贴图必须能覆盖共用贴图** | `scene_tex()` 现在**先查 `SHARED_SCENE` 再查每帧**，stele 三帧共用一张 ⇒ 要做每帧独立贴图必须先改这个优先级 | `scripts/asset_draw.gd:164-171` |

---

## 六、已定的设计口径（不要推翻，要落地）

- **「空间冻结、时间可动、位置不变」是核心玩法** ⇒ 跨时代同一栋楼不许移动。A4 超市必须与 A5 同址 —— 🔴 **L14 落地后 A5 超市已挪到 `[2144,320]`**，A4 重排线同步对齐（任务书 `docs/PROMPT-a4-rebuild-exec.md`，几何已实测 errors=0）。
- **地标是坐标系不是美术资产** ⇒ 五帧位置不许漂；🔴 **界碑已作废（2026-11-26 用户拍板「界碑删掉吧」）** ⇒ 五帧各一个的「周界」石碑与它的三次挪位剧情**全部撤销**（界碑删除线 `docs/PROMPT-stele-removal-exec.md` 负责）；地标口径只剩：老井 `(2048,832)`、老槐 `(2048,1664)`、坝、田、超市工地。
- **「超市压住老井」已被几何堵死**（压井必压槐，井与槐相距 128px）⇒ `docs/story.md` 已改文本，井口改为「就在超市西墙外，只隔一道墙」。**不要复活压井方案。**
- **证物模型 = 「一件物件一张卡，卡内按年追加观察记录」**（2026-11-23 用户拍板，原「日期化观察记录·一对象一年一张卡」作废）：key ＝ 物件身份（家具＝`<房屋族>::<家具名>`，地标＝ title 第一个「·」前的主体名），卡内 `observations` 按年代追加。L5 线 `5a36770` 交付时实测 27 卡 / 58 观察；🔴 **L14 落地后全局变成 25 卡 / 56 观察**（删掉 A5 的「停车场」「路口·红绿灯基座」两张地标卡，各只有 a5 一年）—— **总策划已于 2026-11-26 用 `lab/_audit_evidence_count.py` 独立复算确认 25/56 并回写此口径**（L14 反馈 §9 R-L14-3 已闭环）。⚠️ 早先写的「39 条观察」是**按唯一 title 去重的旧口径**（漏算老槐/界碑/坝/田四张地标卡的跨年代观察），**已作废**。理由：档案是主角唯一的跨时代记录板（`story.md:19-26` 他是归档员，卷宗是唯一能穿过 Shift 的东西），一张卡五个年龄才是卷宗，一对象一年一张卡是数据库。
- **`market` 单 id 两形态，不拆 `market_a5`**（拆 id 牵动 frames/houses_data/CLUE_TEXTS/证物 key 四处）。
- **`zheng_a4` 不补线索**（story §7.4「玩家永远确认不了」依赖这条）。
- **A5 老槐 r=160 暂不改**（等 L2 渲染修好后看实机）。
- **A4/A5 六栋暂无美术成品图**（`world_view.gd:458-463` 的 `FAMILY` 只含 A1–A3 十二栋），走色块降级 —— **美术成品图由美术同学出**（清单 `docs/ART-HANDOFF-a4a5.md`），本项目只负责「资产接线」（把图接进引擎，L8 线）。
- 🔴 **「顶住了」机制作废，只做 phasing（卡墙虚化）**（2026-11-26 用户拍板，原话「顶住这点去掉，只做虚化。顶住这点是你自己补上的我未批准的内容」）：`scripts/timeline.gd:78-92` 的 bump 分支与 `main.gd:_on_bump`／`world_view.gd` 震屏／`player.bump_kick`／`hud.bump_flash` 全部删除，改为实现 `docs/house-spec.md` §8.3 的 phasing（alpha≈0.4 半透明＋色差、phasing 期间**绕过 `is_free()`** 独立位移、每步结束用 `if frames[index].is_free(char_pos)` 退出 phasing、仅 phasing 时用 A/D 做内/外位移）。⚠️ `house-spec.md:770` 原本要求 phasing 与楼层方案 C 同期 ⇒ 本次**只做 phasing，不做楼层方案 C**（取舍见 `docs/PROMPT-phasing-exec.md`）。
- **地标跨帧同址口径（重排后）**：老井与老槐在 A4/A5 **必须同心**（井 `(2048,832)`、槐 `(2048,1664)`），只有**界碑**例外（它的三次挪位是剧情）。
- 🟡 **「五帧实体空气墙一致」原为地图线硬口径（2026-11-26 拍板），同日已降级为待办**（见 `docs/地图视觉口径.md` C6：不再为对齐而补山 / 补实体房，等后续几张地图定稿后统一补）—— 以下是降级前的原始口径：**空气墙 ＝ 房屋 lot 外框 ∪ 山体多边形**（路/田/井/树/内岛/环道都 `solid:false`，不算）；判据是**帧与帧互比**（不是以 A1 为基准）——玩家推时间时，同一坐标在前后两帧必须**都还是可站**，否则就是「空地突变实体」。⇒ **A4 重排线**：A4 的空气墙必须与 A5 **逐格对齐**（实测目标 cover=100%／双向触发 0 格）；⇒ **A1–A3 重排线**：等 A4 搭完后按同一套约束重排（用户 2026-11-26 明说「A1-A3 的地图要等 A4 搭完才能搭建」）。
- 🔴 **phasing（卡墙虚化）只是兜底，不是解法**：用户口径「只要包围的空气墙（实体房屋、山）的范围是一致的，就不会有卡到山里，从而通过虚化卡到地图之外的现象」⇒ **正常游玩不该触发 phasing**（L17 任务书 §2.3「正常不该触发」是它的第一验收项）；⇒ **不做楼层方案 C**（用户 2026-11-26：「不做楼层了，时间不够了」）。

---

## 七、已知污染史（别再踩）

| 时间 | 事件 |
|---|---|
| 13:22 | `houses_data.json` 被改，**所有 lot 加高**（`market` 21×14 → 42×28 翻倍） |
| 13:47 | `_path_to_tiles.py` 把路从折线改成格块，`frames.json` 全量重写 |
| 13:58 | Godot 编辑器把 `art-handoff/*.csv` 当翻译表导入，生成 33 个 `*.translation` 幽灵文件 |
| 14:01 | `world_view.gd` 实现伪 3D（`EXTRUDE=16`），与美术的「画布 +16」耦合 |
| 14:11 | `git init`，基线 `444faa2` |
| 11-23 | A4 线与 A5 线各写 `frames.json` 一帧 → 一次误提交吞掉对方成果（`git commit -- <path>` 提交的是**工作区内容**而非历史版本） |
| 11-23 | 求解脚本误把 wings 当 x1,y1,x2,y2 → 「market 合法落点=0」「压井与同址互斥」两条假结论 |

**教训**：`art-handoff/` 不该放在 Godot 项目根目录（已进 `.gitignore`）；改含非 UTF-8 字节的文件（如 `.gitignore` 的 GBK 注释）**必须用 Python 按 bytes 读写**，`Get-Content | Set-Content` 会改字节。

---

## 八、你必须守住的硬约束（破了就是重做）

1. **内外严格 1:1**（`house-spec.md` §0.1）：外观占地 = 内部可行走区 + 墙厚，差一格切时间就卡墙里。
2. **碰撞是纯数据 AABB**：不建 `CollisionShape2D`。`CHAR_RADIUS` 与 TILE 同比（16→7，32→14）。
3. **`scale_mode=0` 是有意为之**（fractional 缩放，1080p/1440p/4K 都整数倍命中），别改回 1。
4. **时间轴三倍重绘**：`world_view.gd` 整个场景重复画三遍做色差，是核心观感，**不许优化掉**。
5. **缺图不崩**：`load()` 返回 null 必须回落色块，美术可以分批进图。
6. **精确 `git add` 自己那批文件，绝不 `git add -A`**。工作区长期有别的线的产物（`_ref/art/**/*.png` 的 M、用户自己删的 `美术资产/` 旧图 D、大批未跟踪 `.import` 与 `lab/_*`）——**全部保持未暂存**。

---

## 九、你的工作方式

### 每次子会话开工前，你要给的

1. **它只准改哪些文件**（第三节的表 + 写者锁）
2. **它依赖谁的产物先完成**（第三节的「前置」列）
3. **它的验收标准**（能自动跑的，不要靠肉眼）
4. **它必须知道的引擎红线**（第五节相关条目）

### 每次子会话交工后，你要做的

1. `git status` 看它有没有越界改文件
2. 跑对应校验（`greybox_check.gd` 全绿、`CHECK ALL PASS - 18 houses`）
3. `git commit`，提交信息带上「哪条线 + 改了什么」
4. 更新第三节的 owner 表
5. **把它写进 `docs/FEEDBACK-<线名>-exec.md` 留档**（若它自己没写，你代写）

### 写执行提示词的格式（你派新线时用这个骨架）

```
# 新会话提示词：<线名> —— <一句话职责>

> 整段复制给新会话作为第一条消息。本线**只写 <文件清单>**。

## 0. 开工前（必做）      项目路径 / Godot 路径 / HEAD 下限 / git status 警告 / 权威源 / 必踩的坑
## 1. 你的独占写入文件    文件 + 精确替换写法 + git add 白名单 + 落盘错开约定
## 2. 坐标/数据基准       照抄，别自己重算
## 3. 必改清单            逐条「改前 → 改后」+ 为什么
## 4. 验收               几何自检 + 回归关键字 + 实机
## 5. 收工                git add 白名单 + commit 信息 + 报告要写什么
## 6. 边界提醒            别的线在跑，别碰
## 附                     依据文档
```

### 跑回归的正确姿势（沙箱里）

```
& "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe" --headless --path . -s res://_mdtest/<name>_check.gd 2>&1 | Select-Object -Last 45
```

- ❌ `cmd /c "D:\steam\...\godot.exe ..."` 会被空格截断（报 `'D:\steam\steamapps\common\Godot' is not recognized`）。
- ❌ `> file` 重定向产出 0 字节文件。
- ✅ 沙箱噪声固定：`Failed to read the root certificate store.` / `ERROR: Failed to open 'user://logs/...'` / `[exit code: 1]` —— **判绿看关键字不看退出码**。
- Python 脚本遇到 `⇒` 等非 ASCII 字符会崩在 GBK 编码上 ⇒ 先设 `$env:PYTHONIOENCODING='utf-8'`。

### 汇报给用户时

- **先给结论**（能不能开工 / 卡在哪 / 下一步谁做什么）
- 数字要实测，**不要引用旧文档的数字**
- 遇到子会话之间互相冲突，**先停，问用户，不要自己裁决**

---

## 十、当前待办（2026-11-24 状态）

| 线 | 状态 | 备注 |
|---|---|---|
| L1 地图帧修正 | ✅ **已交付**（commit `0436c58`），反馈已补交（`e5d9941` → `docs/FEEDBACK-map-fix-exec.md` 390 行 + 4 张实机截图） | A4 超市[1440,768] 与 A5 同址、shen_a4[96,320]、周郑留路南、界碑 A4[2880,960]／A5 新增[32,1024]、井文案对齐、工地热点挪到 [2112,1632]、`_note` 已加。**尾账**：A4 热点标题仍是「超市工地 · 南大门」（D4，已降级为可选）；`REACH_MAP` 变化已由总策划判为「空间冻结正常表现」，待实机走 A1→A5 主路 |
| L2 渲染修正（老槐遮井） | ✅ **已交付并验收通过**（commit `cc19b4c`） | 改 `scripts/world_view.gd`（+188/−41）：色块树冠不再上抬（删 `lifted = center + offset + Vector2(0, -rad*0.7)`）、圆深度键按「立着/贴地」分开（`_circle_sort_y()` 两支都返回 `center_y + rad`、理由分开写）、井恒可见且不挡玩家（**就地补画 overlay**：补画 A 树→井、补画 B 井→玩家，**排序链一个字未动**）。几何：A4 61.9%→0.0%、A5 100.0%→69.2%→0.0%。总策划已独立复核：七套回归全绿、**实机截图亲眼看过**（井口完整可见、树冠只盖左上沿一小圈）、`_mdtest/**` 零改动。验收意见见 `docs/FEEDBACK-render-fix-exec.md` §8。**尾账**：R1 界碑贴图拉伸 + A4/A5 场景贴图接线 → **L8**；R2 A5 老槐 r=160→128 属 L1 文件域（且 `tree_a5.png` 要同步 320×320→256×256）｜R3 market 两态实机 E 检视验收 |
| L3 房屋数据 | ✅ **已交付并验收通过**（commit `7805d71`） | market 双态说明 + 撤 school 界碑家具（clue 家具 29→28、school 家具 155→154、18 栋几何零改动）。**尾账 R1：两处 px 旧 16px 口径待回退（market 672×448→**1344×896**、school 608×480→**1216×960**）**—— 这两个数是「屋本体 px」（= 占地格数×32），不是画布 px（画布多一格高：1344×928 / 1216×992），L6 反馈已指出并由总策划改正**；**R3 生成器对齐 ✅ 已由 L6 完成**（`3361589` 删掉 `gen_all_houses.py`/`_redo_school.py` 里的界碑家具代码；未运行生成器验证 ⇒ 尾巴 R2） |
| L4 证物文案按年 | ✅ **已交付并验收通过**（commit `63f47eb`） | 改 `scripts/house_shape.gd`（+66/−12）+ `scripts/frame_data.gd`（`:66` 传 year）：`CLUE_TEXTS` value 支持 String 或 `{年: 文案}` 字典，`_clue_text()` 取值链＝该年→`"default"`→占位句；`market` 的 `文件柜`/`上磨盘` 拆 2001/2026 两态；删 `school` 界碑条目；订正 §2.5 过期注释（只改文字不动过滤逻辑）。**实测 28 件全覆盖 / 0 占位句 / 文案 30 条（26 字符串 + 2 字典×2 年）/ 卡数 27 卡 58 观察零变化**（🔴 **L14 落地后全局变 25 卡 / 56 观察**；此处 27/58 是 L4 交付当时的数）。总策划已独立复核：七套回归全绿、`school`/`zheng_a4` 段确实不存在、year 不进 hotspot 输出字段。验收意见见 `docs/FEEDBACK-clue-texts-year-exec.md` §8。**尾账**：R1 market 两态实机 E 检视（与 L2 的 R3 同一次做）｜R2 界碑/坝/田 跨年代重复文案 → **L1 小线**｜R3 L8 改标题标签时别动 key |
| L5 证物档案 | ✅ **已交付并验收通过**（commit `5a36770`） | 模型＝**一件物件一张卡，卡内按年追加观察**：key 归一（家具＝`<房屋族>::<家具名>`，地标＝title 第一个「·」前主体名），卡内 `observations` 按年代追加；**实测 27 张卡 / 58 条观察**（⚠️ 任务书原写「39 条」是按唯一 title 去重的旧口径，已作废）。开档时收紧 SHIFT/E 已实现（`main.gd` 档案暂停判断在前，`shift_axis`/`inspect` 在后）；`evidence_archive_check.gd` 已按新模型重写（PASS 111 / FAIL 0）。总策划已独立复核：八套回归全绿、主场景零 SCRIPT ERROR、`58` 用独立 python 仿真复现；验收意见见 `docs/FEEDBACK-evidence-model-exec.md` §8 |
| L6 文档 | ✅ **已交付并验收通过**（4 个 commit：`def62dd` 主战场 / `cd4b9d4` 第二档 8 份 docs / `585a004` 补正 / `3361589` R3 生成器对齐） | 主战场 `docs/HANDOFF-VILLAGE.md`（+41/−37）：@16px 全表重算成 32px、界碑三处改「A5 世界地标」、`:377`/`:512` 过期句订正、头部日期更新；第二档：`house-spec.md`/`HANDOFF.md`/`REPORT-house-height.md`/`display_manager.gd` 注释/`PROMPT-art-canvas-h16`/`house-size`/`pseudo3d`/`tile-32px` 全部加 SUPERSEDED 或改陈述（**历史记录不改写**）。**六条验收 grep 我亲自复跑全部通过**（`一格 = 16×16 px` 0 命中、旧 px 串仅 `:328` 历史表、`market_a5` 仅 `:132` 正确声明、`155(1)` 0 命中、`[1,18,2,1]` 3 处全在历史语境、`1600×900\|640×360` 0 命中）。验收意见见 `docs/FEEDBACK-doc-rewrite-v2-exec.md` §6。**尾账**：R1 `houses_data.json` 三处 note px 旧值（玩家不可见，等房屋数据线收口）｜R2 生成器未运行验证（跑它会重画 18 张 `_ref/art/*.png`，用 `git checkout-index -f` 还原）｜R3 历史节 `:328` 旧值保留 |
| L7 美术成品图 | **本项目不做，交美术同学** | 清单在 `docs/ART-HANDOFF-a4a5.md`；美术同学不碰代码/测试 |
| **L8 资产接线**（🔴 **升级为 P0 独立线**） | ✅ **2026-11-26 已交付并自检全绿**（反馈 `docs/FEEDBACK-asset-tile-wire-exec.md`）—— 这是 2026-11-26 地图事故的真正补救线 | 把「整帧大图」管线换成 **32px 单方格逐格平铺**：地面铺装＋polygon 按 label 分派（河/路/岛/山）＋rect 逐类贴图；权威＝docs/地图视觉口径.md C1–C5；⚠️ 与 L17／界碑删除线争 scripts/world_view.gd ⇒ 三选一 |
| L9 渲染缺陷调查（人站在墙上 / 门可穿 / A4 门口色块乱） | ✅ **已交卷**（commit `014a18c`，只改 `scripts/world_view.gd` +69/−4，反馈 `docs/FEEDBACK-render-bug-exec.md` 117 行）| **实测推翻任务书 §2.1 的定位**：A4/A5 色块路径排序无错位（python 逐格复刻全 0 例），真因在 A1–A3 美术路径（base 图整张画在背景层、前景 walls 分支有图就 `return`）⇒ 新增 `_draw_art_wall_strips()` 把墙行横条按同落点公式贴回前景层（补贴带固定 64px 高，只在 `alpha_mul==1.0` 主通道贴）＋门 `sort_y` 改行北沿（58/58 门格中心被盖→0）。碰撞未动 ⇒ DOOR_PASSABLE／WALL_STOP_Y(816)／A1_WELL_FREE 不变。**⇒ L11 的 `world_view.gd` 阻塞解除。**🟡 **总策划尚未独立复核**（待办）。
| **L10 缺美术资产清单**（新） | ✅ **已交付并验收**（commit `b0798da`，12 个文件）→ **清单已由用户转交美术同学** | 交付物＝`docs/ART-GAP-A4A5.md`（486 行，用户会原样转发）＋ `docs/ART-GAP-A4A5.csv`（utf-8-sig 进度表）＋ A4/A5 六张拆解图重出成 32px 口径（`_ref/houses/gen_all_houses.py` 的 `TILE = 16` 已改 32）。总策划独立复核：改动只碰 `docs/**` ＋ `_ref/art/A4_2001|A5_2026/**` ＋ `_ref/houses/gen_all_houses.py`；A1–A3 那 11 张美术线未提交 PNG 与备份 sha256 **逐一相同**（没被覆盖）；旧错数 159/194/线索10 已订正为 **158/193/9**。🟢 **2026-11-25 已按「单方格复用」修订**：B 组 20→19（河/路/田六张整帧大图 → 32×32 可平铺瓦，删 `road_a5_vertical.png`）、C 组 4→3（环岛改成「路缘弧段 + 中心岛土色瓦 + 中心岛绿化瓦」三件可复用零件）、D 组 26 张备注加「地图侧只用 rect 圈区域」、树图备注加「冠幅待定」、**总计 224→222**；假裁定「世界不再整体放大」已改成「按甲方案放大到约 4800×3600 ⇒ 全部铺地素材做成 32×32 瓦，地图放大不用重画」 |
| **L11 世界重排（数据 + 地图引擎）** | ✅ **任务书已写并按 v3 冻结布局修订**（`docs/PROMPT-l11-world-rebuild-exec.md`）→ **可派，但排在 L9 之后** | 八条裁定（`docs/待解决事项.md` §1.3 M7–M16）逐条落到任务书：**世界放大到 4800×3600**（TILE 仍 32，150×112 格）→ **先放大再重排**（五帧布局**以 `lab/_l11_final.json` 为准**，执行者不自行设计）→ **树的数据这轮不动**（老槐 radius 32/64/96/96/160 保持）→ **新元素只用 rect 圈方格**（不新增 shape 类型；引擎加 `surface`/`prop` 可选字段）→ **陆家/周家路南、沈家四代同位且逐代变大、界碑跟学校、起点重设 [1024,1680]**（边缘 **12 栋** decor 空白房子，用 v3 的 `edge_houses`，其中第 3 栋须从 `[1984,3328]` 挪到 `[2080,3328]` 避开 A5 竖路南段）→ **美术单方格复用**（河/路/田改平铺，不再拉伸整帧大图）。还要做：**decor 空白房子机制**（改 `frame_data.gd` 不生成热点、整栋 lot 挡路；`world_view.gd` 只画底色不画墙/门/家具/屋顶）、**河/路/田改平铺**（`world_view.gd:263` 写死 `Vector2(3200,416)`、`_scene_bboxes()` `:276-304` 合并 road rect 成外包矩形）、**`data/frames.json` 老槐四帧 text 改口**（老井五帧一字不动）。⚠️ **五处测试断言必红**（`greybox_check.gd:57-58/291/372`、`camera_check.gd:44/51-52`）→ **已授权改期望值**（不删断言）；⚠️ 与 **L9 争 `scripts/world_view.gd`** ⇒ 串行（先 L9 后 L11）；⚠️ **L9 尚未交卷**（`docs/FEEDBACK-render-bug-exec.md` 不存在）⇒ 要催；⚠️ **A1/A2 弯路 29 块 32px rect 在 4 邻接下是 29 个互不连通的连通块** ⇒ 任务书要求「先原样落地 → 加断言实测 → 走不通再补 32×32 road rect」 |
| **L12 界面与手感（小地图 + 提速 + 走路动画）** | ✅ **已交付并验收通过**（代码 `b5ecbd9`，反馈 `d29047f`） | 总策划亲跑七套回归全绿（`hud_layout_check` 21 条 PASS / `greybox_check` `REACH_MAP` 与 L11 前**逐位一致** ⇒ 提速没改可达性 / `camera_check` / `sort_check` / `asset_draw_check` / `evidence_archive_check` / `display_check` 全 `fails=0`）。实现与任务书逐条对齐：`main.gd:12` `PLAYER_SPEED := 180.0`、`player.gd:22` 抽 `const WALK_FREQ := 6.0`（bob 与帧索引**两处同源**，`:103` 站立呼吸未误改）、`hud.gd:46` `minimap_rect()` 作几何唯一出处（绘制与断言共用）＋`:52` `minimap_point()` ＋`:63` `sync_player()`（**`sync()` 签名未动**）、`:129` `_draw_minimap()`；`main.gd:166` 每帧喂坐标（档案开着时 `_process` 已 return ⇒ 开档停更）。🟢 **尾巴**：R-L12-1 精确 add 纪律（`d29047f` 顺带带了 L13 的反馈文档 `docs/FEEDBACK-l11c-text-exec.md`，纯排版改动、语义未变 ⇒ 从宽通过）｜R-L12-2 `MINIMAP_MARGIN` 设计值 8 / 实际 16px 的单位注释（不阻塞）｜R-L12-3 小地图补地标点（**挂 L11 之后**，HUD 不读 frames.json 是 L11 单写者域）。验收意见见 `docs/FEEDBACK-l11b-ui-exec.md` §6 |
| **L14 A5 落地** | ✅ **已交付并验收通过**（`0989e87`／`5621db0`／`e086c83`，反馈 `docs/FEEDBACK-a5-v5-exec.md` 120 行＋总策划验收 §9） | 交付＝`data/frames.json` 的 a5_2026 帧（23 shapes / 5 hotspots）＋顶层 world 4800×3600 / 起点 [1024,1696] ＋ 新建 `_ref/houses/houses_data.json` 的 `shen_a5`（克隆 shen_a4·doors+gate 清空·clue 全 false）＋ `scripts/evidence_store.gd` 的 HOUSE_FAMILY 补 `"shen_a5":"shen"` ＋ `docs/story.md` 的 `:50`/`:433`/`:436`/`:437`/`:444`/`:700`/`:962` 文本同批改 ＋ 两个测试文件的世界尺寸常量。**总策划已独立复核 v5 反馈**：①河 polygon 必须用权威公式（`_ref/houses/_design_v5.py` 的 `river_depth`，实测 100% 复现现行河；v5 脚本自造的河逐点相同 0/103，会让 market/shen_a5 压河）②`shen_a5` 数据不存在必须新建（不建 ⇒ `world_view.gd:475-501` 整栋静默消失）③反馈文档与它自己的脚本对不上（脚本实得 38/6/decor14，文档写 23/5/0）④老槐五帧文案整组重写（M11 树井分家）⑤OY 从 1600 改 1664（1600/1632 下四合院合法落点 0 个）⑥**任务书自查又抓出河公式笔误**（原写 `exp(-((x-46.5)**2)/(2*16**2))`，权威是 `exp(-((x-46.5)/16.0)**2)`，150 列里 65 列不同、对现行河 mismatches=65）⇒ 已改。**用户 2026-11-26 拍板**：只做 A5（A4 之后再排、另派一线）／沈家先定 A5 落 `(64,416)`（实测唯一「不压河＋离主路 ≥1 格」的落点，`[64,352]` 压河 3040 px² 已作废）／英文主题句选 A ⇒ 主题句（中英）总策划已落盘，本线不碰。**尾账**：R-L14-1 A4↔A5 同址暂时断（超市/井/槐）｜R-L14-2 M15 沈家 A1–A5 同位只满足 A5（且 A5 用 (64,416) 而非锚点表的 [64,352]）｜R-L14-3 证物 27/58 → 25/56（回写 §六 口径，不改历史反馈文档）｜R-L14-4 A1–A3 重排未做｜R-L14-5 河贴图画布写死 3200×416（属 L8） |
| **L15 归档表 + 结局变体** | ✅ **代码层已交付并验收**（`6141ff8`＋`45c5f72`，`ENDING_CHECK_DONE fails=0`）｜接线待 L17 | 真相全部现成（`docs/story.md` §10.0–§10.5 ＋§4.6 两套分类）；新建 `scripts/ending_{store,report,form}.gd` ＋ `_mdtest/ending_check.gd`；⚠️ 接线（改 `scripts/main.gd`）必须等 L17 交卷 |
| **L16 双日记渲染** | ✅ **已交付并验收**（`082f0c5`→`8a9f0d2`→`01c3921`，`DIARY_RENDER_CHECK_DONE fails=0`，删除线自绘达标）｜🔴 `J` 临时调试键待删、书热点数据未落地 | 语法 `docs/diary-markup.md` 四标记 ＋ 原稿 `docs/story.md` 附一.1–附一.4；新建 `scripts/diary_{markup,page,view,texts}.gd` ＋ `_mdtest/diary_render_check.gd`；与 L15 文件零重叠可同时跑（但**不能同时改 `scripts/main.gd`**） |
| **L17 phasing/虚化**（用户 2026-11-26 拍板） | ✅ **任务书已按新口径改写，可派**（`docs/PROMPT-phasing-exec.md`，547 行） | **删掉「顶住了」全部代码**（`timeline.gd`／`main.gd`／`world_view.gd`／`player.gd`／`hud.gd` ＋ 两个测试文件）＋ 实现 phasing（alpha≈0.4 半透明、phasing 期间**绕过 `is_free()`** 独立位移、每步结束检查是否回到自由点）；🔴 **口径＝空气墙一致 ⇒ 正常不触发，phasing 只是兜底**；⚠️ **不做楼层方案 C**（用户明说时间不够）；⚠️ 与 L8 争 `scripts/world_view.gd` ⇒ 二选一 |
| **A4 重排线**（P0） | ✅ **已交付并验收**（`9ec040a`，反馈 `docs/FEEDBACK-a4-rebuild-exec.md`＋总策划验收）—— **几何通过 / 视觉未交付**（画面是色块，根因在引擎与缺 L8） | 只替换 `data/frames.json` 的 a4_2001 帧：超市/井/槐与 A5 同址、**周郑两家对齐 A5 的小学/玩具店地块**、**补山×4 填平空气墙**、补竖车道＋环道＋内岛＋路标；🔴 **五帧实体空气墙一致**（cover=100%／双向触发 0 格）；⚠️ 与 A1–A3 重排线**串行**（同写 frames.json）；⚠️ 界碑由界碑删除线撤掉 |
| **L13 树井文案改口 + 倾斜叙事删除** | ✅ **已交付并验收通过**（`67bd62c` 正文三文件 ＋ `docs/FEEDBACK-l11c-text-exec.md`，另有 `1bc0494` 把反馈文档压到 113 行） | 纯文档线，只碰 `docs/story.md`／`docs/npc.md`／`docs/HANDOFF.md`。**总策划亲跑六条 grep 全过**：`story.md`「倾斜」0 命中、「私生子」1 命中（只在 `:964` 右列禁止项「第二个『私生子』」—— 必须保留）、`npc.md`「老槐」0、「这树」0、三份文件「拱裂」0、`HANDOFF.md`「树倾斜」0；**实测 §7.3 整节无「井」字**（全文「树/槐」只剩 `:447`/`:449`/`:451` 三处）⇒ 井树同源在文案层彻底断开。落地：`story.md:447-455` §7.3 整节重写（三段）、`:964`（原 `:965`）左列换「磨盘上凿的那一行字」**右列保留**、`npc.md:230` 删老槐树行并插入老井五行、`:211` 改「旁听 · 主线（老井，五帧）」、`:298`/`:329`/`:335-336`/`:340`/`:341`/`:357`/`:381` 逐处改、`HANDOFF.md:378` 删「、树倾斜」三字；**`npc.md:167`（A1 · 井边 · 两名农妇）与 `HANDOFF.md:453` 保留不改**。文件域零越界。🔴 **本线不闭环，两条挂 L11**：R-L13-1 `data/frames.json` 老槐四帧 `text`（A17，只改 text、`title`/`label`/`reach`/`pos`/`radius` 一律不动）｜R-L13-2 §7.3「2001 年十字路口修起环岛」那句（L11 落地后 a4_2001 才首次有环岛 ⇒ 中间态，我自己的任务书疏漏，不追责）。🔴 **新登记悬案 P1-8**：`story.md:988`「一百年里唯一没移动过的是那块地砖」vs 树被搬进环岛 **5 格**（v3 实测 A1 (2048,1536)→A4 (2048,1696)）⇒ 交用户拍板（甲改措辞／乙给移植解释／丙回退树位违反 M3），我倾向甲。🟢 R-L13-4 老井 A1 旁听句与 A1 老井 hotspot 高度重复（不阻塞）。验收意见见 `docs/FEEDBACK-l11c-text-exec.md` §8 |
**验收尾巴**：① **R2 界碑/坝/田 跨年代重复文案**（我实测 `lab/_v_landmark_dup.py`：界碑 5 年只有 3 种文案、**1926/1951/1976 逐字相同**；坝 5 年 2 种、**1926/1951/1976/2026 四帧同句**；田 1951/1976 同句；老井 5 种全不同、老槐 5 种全不同）—— 文案在 `data/frames.json`，**归 L1 文件域**，L4 不并入 ⇒ 派 **L1 小线**；② **R3 实机验收**（market 两态证物）：实机走 A4（超市工地）与 A5（营业超市），E 检视「文件柜」「上磨盘」，确认两次入档落在**同一张卡**（`market::文件柜`）的**两条观察**（2001/2026）⇒ 与 A5 老槐 radius 决策一起做；③ **A5 老槐 r=160 是否收 128**（实测 128 仍挡井 27.1%、96 才 0.2%；实机 160 观感可接受 ⇒ **我倾向不动**，但属 `data/frames.json`＝L1 独占，且收 128 要把 `tree_a5.png` 从 320×320 改 256×256）；④ **R5 证物测试未钉住 27/58 数字**（`_mdtest/evidence_archive_check.gd` 唯一数字断言是读回前后卡数相等）—— 可并入 L8 或另派小线；⑤ **R6 `evidence_archive.gd` 的 `new_count` 是只写不读的死变量**（旧版用于算 `first_new`）—— 可清理；⑥ **L2 几何遮挡率没有常驻断言**（只在反馈文档与临时脚本里）—— 建议 L8 或收尾阶段补一条「遍历五帧算井被树冠覆盖率、超阈值即 FAIL」；⑦ **R1 `houses_data.json` 三处 note px 旧值**（market/school/toyshop，玩家不可见，等房屋数据线收口）；⑧ **文档过期数值扫描**建议纳入 `_mdtest/` 常驻回归（现在只有一次性 grep）。
| **界碑删除线**（新） | ✅ **任务书已写，可派**（`docs/PROMPT-stele-removal-exec.md`）｜🔴 与 L8／L17 争 `world_view.gd` ⇒ 三选一 | 五帧数据（删界碑 shape/hotspot）＋ 引擎贴图入口（`asset_draw.gd` SHARED_SCENE、`world_view.gd` 碑分支）＋ 三个测试 ＋ `docs/story.md` 叙事收口（§7.2 五条变四条、§7.4 界碑整节删、物证表删一行）＋ 四个资产清单文件（`stele_a1..a5` 五张作废）；🔴 **证物基线 25 卡/56 观察 → 24 卡/51 观察**；⚠️ 与 L17 串行（都碰 `world_view.gd`） |
| **地图场景化（方案 B）Stage 1**（用户 2026-11-26 拍板「走方案 B」） | ✅ **任务书已写，可派**（`docs/PROMPT-scene-tilemap-exec.md`，437 行） | 目标＝**地图从「数据＋画笔」变成「Godot 场景里的节点」**，总策划能在编辑器 2D 视图里看见并手摆。Stage 1＝写烘焙器 `tools/bake_world_scene.gd`，从 `data/frames.json` ＋ `asset_draw.gd` 的贴图表生成 `scenes/world/world_*.tscn` ＋ `tileset_*.tres`（五帧各一），**运行时完全不动**；🟢 **只读 frames.json、不碰 `scripts/**` ⇒ 与所有线零冲突**；⚠️ **Stage 2（运行时切场景）不属本线**，等总策划在编辑器里确认后再派 |

---

## 十一、并行排线（2026-11-24 19:00 更新后的结论）

**现在的局面**：L2 / L4 / L6 三条线**全部交付并验收通过**（`cc19b4c` / `63f47eb` / `def62dd`+`cd4b9d4`+`585a004`+`3361589`），工作区无在途代码改动 ⇒ **下一批可以开三条互不重叠的线**。
**2026-11-24 20:20 更新**：玩家实机体验后新报三条渲染缺陷 → **L9 已写好任务书（`docs/PROMPT-render-bug-exec.md`，commit `d2607a1`）**。L9 与 L8 **同写 `scripts/world_view.gd` ⇒ 两条不能同时开**，L8 要等 L9 落地（或反过来，二选一）。
**2026-11-25 09:19 更新**：玩家逐条拍板八条（详见 `docs/待解决事项.md` §1.3 M7–M16）——**按甲方案放大** → **先放大再重排** → 树数据不动 → 树井文案改口 → **倾斜叙事整组删** → 路宽延后 → **新元素只用 rect 圈方格区域** → 陆家周家路南/沈家同位变大/界碑跟学校/起点重设，追加「**美术做单方格素材复用**」。⇒ **L10 清单已按此口径改好并交美术同学**（B/C 组改成 32×32 可平铺件，总数 224→222）；**L11 世界重排线任务书待写**（要改 `data/frames.json` ＋叙事文本 ＋ HUD/速度 ＋ 河路平铺，**必须同一批改**，且**与 L9 争 `scripts/world_view.gd`** ⇒ 排在 L9 之后）；**放大倍率/环岛规格/空白房子表示法/965 线索表/测试授权五个数已在 L11 任务书里给了默认值**（见上一段 10:30 更新）。

**2026-11-25 10:30 更新**：**L11 任务书已写完**（`docs/PROMPT-l11-world-rebuild-exec.md`，含白名单/禁改表、五个待点头数的默认值、布局基准文件、跑 Godot 姿势与六个坑、数据与叙事同批改的顺序、六条测试改造清单、验收清单与禁改清单）。五个等用户点头的数，任务书里都给了**默认值**（放大倍率 1.5 倍 4800×3600、环岛 R192＋环道 64、decor 标记、`:965` 换「磨盘上凿的那一行字」、测试改期望值已授权）⇒ **执行线可以直接开工，不必再等**。但 **L11 与 L9 争 `scripts/world_view.gd` ⇒ 仍须串行（先 L9）**。
**2026-11-25 10:55 更新（子代理已交卷，任务书拆成三条）**：两个子代理都已交卷 —— `l11-layout` 交 **v3 冻结版**（`lab/_l11_final.json` ＋ `lab/_l11_final_report.txt`，自检红灯 0 项），`l11-text` 交终稿（`lab/_l11_text_final.md` ＝ A1–A17 逐字替换方案 ＋ 树的新来历 2 候选 ＋「第二个私生子」替代物证 3 候选 ＋ 影响清单）。总策划已对 v3 做**独立复核**（脚本 `lab/_l11_verify_road.py`／`lab/_l11_edge_vs_v3.py`／`lab/_l11_edge_move_check.py`）：四段叙事硬约束全成立（A3 磨坊盖井 / A4 井在超市西墙外 32px 一道墙 / A5 井在车道下 / A5 界碑在小学围墙内）、环岛外缘距各屋最近点余量 +2～+40px 全不压、地标可达性最近可站 ≤25px 全通；**两处取舍已写进任务书**：① A1/A2 弯路 29 块 32px rect **4 邻接下互不连通**（8 邻接才连成一片）⇒ 先原样落地、加断言实测、走不通再补 32×32 road rect；② v3 的 12 栋 decor 里第 3 栋 `[1984,3328]` 压在 A5 竖路南段 ⇒ 挪到 `[2080,3328]`（已实测五帧全 OK）。**任务书由一条拆成三条（文件域零重叠）**：L11＝`data/frames.json` ＋ 地图引擎（`world_view.gd`/`frame_data.gd`）｜L12＝HUD ＋ 速度 ＋ 动画（`hud.gd`/`main.gd`/`player.gd`/`hud_layout_check.gd`）｜L13＝叙事文本（`story.md`/`npc.md`/`HANDOFF.md`）。⚠️ 另有一次事故已修：我曾误覆盖了**仓库里早已存在的** `docs/PROMPT-world-rebuild-exec.md`（2026-11-22 旧「世界重构线」任务书）⇒ 已按字节还原，新任务书改名 `docs/PROMPT-l11-world-rebuild-exec.md`；**以后写新任务书前必须先 grep 文件名是否被占用**。

**2026-11-25 11:10 更新（重启后复查 + L9 任务书校准）**：玩家电脑重启后复查仓库 —— HEAD `92078cb`，三份任务书（`docs/PROMPT-l11-world-rebuild-exec.md` / `docs/PROMPT-l11b-ui-exec.md` / `docs/PROMPT-l11c-text-exec.md`）＋ 三份子代理基准文件（`lab/_l11_final.json` 94,609 B / `lab/_l11_final_report.txt` 15,863 B / `lab/_l11_text_final.md` 45,153 B）**全部已入库、无丢失**；三个子代理（`l11-layout` / `l11-text` / `layout-audit`）**均已 inactive 且已交卷，不需要再跑**。玩家拍板：**执行方式＝他自己开新会话跑**，**这一批＝L9 + L12 + L13 全上**（文件域零重叠）。本轮做的事：①总策划逐条复核 `docs/PROMPT-render-bug-exec.md` 里的行号引用（脚本 `lab/_l9_verify_refs.py`），确认 **全部仍准确**；②🔴 **发现并修正 §1.3 断言表的行号写法错误**（真值在 `greybox_check.gd` 里，原表只给断言行号，容易被误读）→ 已在 L9 任务书新增 **§0.0.5** 整段（现状 ＋ 逐条复核结果 ＋ 勘误表）；③四份任务书的 HEAD 基线统一从 `df0c241` / `696caac` 同步到 **`92078cb`**（commit `72494ea`）。⚠️ **L9 是这批里唯一阻塞项**：它与 L8 / L11 争 `scripts/world_view.gd`，**L11 必须等 L9 交卷后再开**。

**2026-11-25 13:45 更新（L12 交卷并验收通过）**：**L12 已交付并验收通过** —— 代码 commit `b5ecbd9`（4 files +89/−3：`scripts/hud.gd` +49／`scripts/main.gd` +5−1／`scripts/player.gd` +8−2／`_mdtest/hud_layout_check.gd` +30−0，**全在白名单内、代码零越界**），反馈 commit `d29047f`。总策划亲自复跑**七套回归全绿**：`hud_layout_check` 21 条 PASS（既有 11 + 新增 10）；`greybox_check` 的 `REACH_MAP={standable:6127, to_a5:4848, blocked_at_step:[144,191,722,222], band_total:196, band_full:159, band_ratio:"81%", ratio:"79%"}` 与 L11 之前**逐位一致** ⇒ **提速没有偷偷改变可达性**（这是本线最该验的一点）；`camera_check` / `sort_check` / `asset_draw_check` / `evidence_archive_check` / `display_check` 全部 `fails=0`。🟡 唯一实质问题＝**程序性越界**：`d29047f` 顺带把 L13 的反馈文档 `docs/FEEDBACK-l11c-text-exec.md` 一起提交了（纯 Markdown 表格化重排、语义未变）⇒ 判**从宽通过**，登记尾巴 R-L12-1（精确 add 要逐个列文件路径，提交前看 `git diff --cached --stat`）。🟢 L12 遗留三条尾巴：R-L12-1 精确 add 纪律｜R-L12-2 `MINIMAP_MARGIN` 设计值 8 / 实际 16px 的单位注释（不阻塞）｜**R-L12-3 小地图补地标点（挂 L11 之后**——HUD 不读 `data/frames.json` 是 L11 的单写者域，现在补就是跨线写）。验收意见已落 `docs/FEEDBACK-l11b-ui-exec.md` §6（独立复核 20 条 ＋ D1–D5 裁决 ＋ R-L12-1/2/3 ＋ 4 条观察 ＋ 签字「通过」）。📌 **L13 也已交卷**（`67bd62c`＋`1bc0494`），**待总策划单独验收**；**L9 仍未交卷**（`docs/FEEDBACK-render-bug-exec.md` 不存在）⇒ **L11 仍被堵**。

**2026-11-25 13:50 更新（L13 交卷并验收通过）**：**L13 已交付并验收通过** —— 文档 commit `67bd62c`（3 files：`docs/story.md` +9−／`docs/npc.md` +18／`docs/HANDOFF.md` +2−）＋ 反馈文档，另有 `1bc0494` 压行。总策划**亲自复跑六条 grep 全过**（`story.md` 倾斜 0／私生子 1＝`:964` 右列禁止项、`npc.md` 老槐 0／这树 0、三份文件拱裂 0、`HANDOFF.md` 树倾斜 0）；**实测 §7.3 整节无「井」字**（全文「树/槐」只剩三处）⇒ M11「树井不再保留同源关系」在文案层彻底落地；**文件域零越界**，且执行者**没有越界去做 A17**（`data/frames.json` 是 L11 单写者域）。🟢 验收意见已落 `docs/FEEDBACK-l11c-text-exec.md` §8（独立复核 16 条 ＋ D1–D7 裁决 ＋ R-L13-1…5 ＋ 4 条观察 ＋ 签字「通过」）。🔴 **两条闭环项挂 L11**：R-L13-1（A17 老槐四帧 `text`，只改 text、`title`/`label`/`reach`/`pos`/`radius` 一律不动 —— `title`「老槐」与 `label` 含「槐」是引擎硬依赖 `scripts/world_view.gd:579`，改了树就不画）／R-L13-2（§7.3「2001 年十字路口修起环岛」那句：当前 `data/frames.json` 的 a4_2001 里 label「路」polygon ＝ **0**，环岛要到 a5 才出现；L11 的 v3 布局里 a4 才首次有环岛 ⇒ 这句**只有 L11 落地后才成立**，属我任务书的疏漏，不追责）。🔴 **新登记悬案 P1-8**：`docs/story.md:988`「一百年里唯一没有移动过的东西，是那块地砖」vs 新 §7.3「2001 年…修起环岛，把它围在当中」⇒ 树被搬进环岛（v3 实测 A1 (2048,1536) → A4 (2048,1696)，位移 **5 格**）⇒ 主题句字面上不再成立；该句**不在 L13 白名单**（L13 没动它是对的）⇒ 交用户拍板：甲改 `:988` 措辞／乙给「移植」解释／丙回退树位（违反 M3）—— **我倾向甲**。🟢 R-L13-4（老井 A1 旁听句与 A1 老井 hotspot 几乎同句，轻微磨损「旁听只给方向、物证才给结论」纪律，不阻塞）。✅ 总策划已回写活文档：`docs/BUILD-A1.md:42/:80/:81/:87/:100`、`docs/art-assets-a1a3.md:350`、`docs/PROMPT-overseer.md:79`、`docs/ART-GAP-A4A5.md:492`、`docs/待解决事项.md`（§1 落地记录／M11/M12／§2 P1-1/P1-2 已定＋**新增 P1-8**／§3.6 出处表 T/N/D 组换现状／F1/F2/F3 换现状）—— **旧任务书按历史不改写、只登记**。📌 **L9 仍未交卷** ⇒ **L11 仍被堵**（L11 开工前要回查 R-L13-1/R-L13-2 两条）。

**2026-11-25 17:20 更新（A5 v4 定稿 + 转接文档）**：**A5 帧布局已定稿为 v4**（`lab/_a5_draft.py` 自检 errors=0 → `lab/_a5_draft.json` ＋预览 `lab/_a5_preview.png`，已 commit `bdfbdf2` 入库）。🔴 **它推翻 `lab/_l11_final.json`（子代理 v3）**：v4 的环心/树心/路口中心统一在 (2048,1456)、内圈 R176＋环道 128＋外缘 R304、两条引道在环岛外圆处断开（v3 是主路直穿环岛内岛 ⇒ 路口根本不在环岛里）；井 (2048,832) r48、界碑 (480,864) 嵌小学西墙实墙格、红绿灯 (2112,816)、四角＝小学(448,288)/超市(2128,225)/玩具店(2128,1856)/停车场(1440,1792)。⇒ **L11 任务书基准必须换**，且 **A1–A4 的新布局尚未定**（用户 2026-11-25 m07696 提过「从 A4/A5 反推 A1–A3」，还没做）。🔴 **本轮新挖两个装饰房引擎穿帮**：①`world_view.gd:668` `FAMILY["lu_house"]=["lu","a1"]` ⇒ A5「空白房子」会贴 A1 陆家底图；②`frame_data.gd:66` 对每栋 house 都调 `HouseShape.hotspots()` ⇒ 14 栋装饰房各带「旧木箱」/「小桌」热点 ⇒ A5 冒出 14 份 A1 线索（`lu::旧木箱`/`zhou::小桌` 键被灌）；且门洞不碰撞 ⇒ 玩家能走进装饰房，「不可探索」没实现。**建议方案乙＝引擎加 decor 分支**（`world_view.gd` 画纯色块墙+屋顶不贴图、`frame_data.gd` 对 decor 房跳过 hotspots、整栋 lot 进碰撞；改动面正好在 L11 白名单里）。🔴 **主题句从项目第一天就写偏**（`story.md:988` 与 `HANDOFF.md:833` 同句「唯一没移动过的东西，是那块地砖」；`git log -S "那块地砖"` 只有初始化提交）⇒ 用户已给中文新句「时过境迁，沧海桑田，我仍在此处看云卷云舒。」（不加老槐、不用全称断言），英文版适配 itch 介绍页待写；**两处必须同步改**。🔴 **`story.md:433`/`:700`「十字路口中央」与新几何冲突**（井在车道正中、距路口中心 624px）⇒ 建议改「车道正中」（A5 热点文案已是「铺在车道正中」）。📌 **转接快照＝`docs/RESUME-2026-11-25-1720.md`**（旧 `docs/RESUME-2026-11-25.md` 已标过期）。

**2026-11-25 23:30 更新（A5 v5 复核完毕 → L14 任务书已写）**：总策划独立复核了 `docs/FEEDBACK-a5-layout-v5.md`（247 行，A5 排版策划线产出，**未入库**），结论＝**用户拍板的部分全部成立、可开工；但反馈文档里的数字有一半不能照抄**。四处硬伤已写进 L14 任务书：①**河 polygon 必须用权威公式**（`_ref/houses/_design_v5.py` 的 `river_depth(x)`，实测能 100% 复现现行 `data/frames.json` 的河；v5 脚本自造的那条河与真河逐点相同 **0/103**，照抄会让超市与四合院压进河里）②**`shen_a5` 房屋数据根本不存在**（grep 0 命中 ⇒ 不建的话 `world_view.gd:475-501` 让整栋**静默消失**；已定：克隆 `shen_a4`、doors+gate 清空、3 件 clue 家具置 false ⇒ 实测网格 D=0/G=0/墙格 298/外墙闭合，**数据侧就封死，不需要引擎 decor 分支**）③**反馈文档与它自己的脚本对不上**（`python lab/_a5_v5.py` 实得 shapes 38 / hotspots 6 / decor 14 / 起点 [1024,1600]，文档写 23/5/0/(1024,1696)）④**老槐五帧文案整组重写**（a1–a5 全都写「朝井那侧歪」，撞 M11「树井分家」；a5 那条还有 L13 已删的「拱裂地砖」）。另：**OY 必须从 1600 改 1664**（实测四合院 1152 高＋不压河＋离主路≥1 格三条在 1600/1632 下合法落点 **0 个**）。总策划已产出**修正版几何** `lab/_a5_v5fix.py`→`lab/_a5_v5fix.json`（自检 **errors=0**：23 shapes / 5 hotspots / 井东缘→超市西墙 48px / 环岛 R304＋内岛 R176 / 树冠 160 ≤ R_IN−16）⇒ **L14 任务书 `docs/PROMPT-a5-v5-exec.md` 已写好，可派**（只写 frames.json / houses_data.json / evidence_store.gd / story.md / HANDOFF.md ＋ 两个测试文件的世界尺寸常量）。🔴 **L14 只做 A5** ⇒ **A4↔A5 的「位置不变」会暂时断**（超市/井/槐不同址）⇒ **A4 重排要另派一线**；🔴 M15「沈家 A1–A5 全帧同位 `[64,352]`」本轮只满足 A5 一半；🔴 L11 任务书基准（`lab/_l11_final.json` v3）**已被 A5 v5 彻底作废**，要换。

**2026-11-26 09:10 更新（用户三条拍板 + 任务书自查修正）**：用户就 v5 复核的待裁定点拍板三条——**Q1 只做 A5**（「先把A5排出来，A4之后再排，要不然又排得乱七八糟」）→ L14 只写 a5_2026 帧，A4 重排**另派一线**且与 L14 串行（都写 `data/frames.json`）；**Q2 沈家先定 A5**（「先做A5的沈家，定下位置后在改A1-A4」）→ A5 沈家落 **`(64,416)`**，A1–A4 之后用这个位置反推（本线一个字都不动）；**Q5 英文主题句选 A** → 中文「时过境迁，沧海桑田，我仍在此处看云卷云舒。」＋英文「The world turns over. He stays where he is, watching the clouds pass.」**已由总策划落盘**（`docs/story.md:988`、`docs/HANDOFF.md:833`、`README.md:5`）⇒ L14 任务书已把这两处从白名单里删掉。另：**总策划复核任务书本身时又抓出一处笔误**——§3.1 的河公式原写 `exp(-((x-46.5)**2) / (2*16**2))`（多了个 2），权威写法是 `exp(-((x-46.5) / 16.0) ** 2)`（先除再平方）⇒ 两种写法在 150 列里有 **65 列不同**，对现行河逐点比对时错的那种 mismatches=65，且会把沈家区间河下沿从 384 算成 416、把车道北段河沿从 288 算成 352 ⇒ 任务书已改成权威写法 + 两道自检（101 列版比现行河 mismatches=0，再生成 150 列落盘版），并把沈家候选位做成对比表（352 压河 3040 px²／416 合法／448 压路）。任务书现 424 行，**可派**。


**2026-11-26 09:40 更新（L14 交卷并验收通过 + 机制盘点 +  phasing 取舍）**：

1. **L14（A5 落地）已交付并验收通过** —— 三 commit `0989e87`／`5621db0`／`e086c83`；反馈 `docs/FEEDBACK-a5-v5-exec.md`（120 行）＋总策划验收意见 §9。**独立复核全部通过**：A1–A4 几何逐位未变、world 4800×3600／起点 [1024,1696]、a5_2026＝23 shapes／5 hotspots、河用权威公式（对现行 103 点 mismatches=0）、`houses_data.json` 19 条且 `shen_a5` 封门无 clue、`evidence_store.gd` 纯插一行、**七套回归总策划亲跑全绿**、**证物 25 卡/56 观察独立复算确认**、`story.md` 七处文本改动 grep 零残留、测试只改世界尺寸常量（`HOUSE_MAP` 未动）。
2. 🔴 **当前最高优先＝两条地图线，且必须串行**（都写 `data/frames.json`）：**A1–A3 重排线**（A1–A4 内容仍只占西北角，世界放大后大片空地）→ **A4 重排线**（A4 超市/井/槐必须与 A5 同址，否则核心玩法「位置不变」当场破）。
3. 🔴 **「顶住了」vs「虚化」的取舍已量化**（用户 m09128 提问）：现行代码只实现「顶住了」（`scripts/timeline.gd:84-88` 目标帧该坐标有 solid 就 bump 不前进）；**「卡墙虚化」是 `docs/house-spec.md` §8.3 的未实现设计**（用户 2026-11-19 拍板，零代码，需楼层方案 C 的高度数据）。**实测现行机制不会困住玩家**：起点连推四时代全部通过、主路带仅 1.0% 的可站点被 A5 挡、主路往东连续可推 118 格；被挡处 91% 是 A5 新建四栋房子的占地（有意设计）。
4. ✅ **可与地图线并行的两条叙事机制线**（文件零重叠）：**L15 归档表 + 结局变体**（`docs/story.md` §10.1 表格已写死，约 2 天）、**L16 双日记渲染**（`docs/diary-markup.md` 四标记 + `_mdtest/` 三个实验脚本可搬，约 1–2 天）。**L17 phasing/虚化**与楼层方案 C 同批，且会碰 `scripts/timeline.gd`／`player.gd`／`world_view.gd`／`main.gd` ⇒ 与 L8（也写 `world_view.gd`）二选一。
**2026-11-26 14:10 更新（方案 B 拍板 ＋ 地图场景化任务书已写）**：用户 m10231 拍板「**1.走方案 B　2.（小地图）这点应该要往后放，因为地图的原因**」⇒ 两条决定：① **地图要落成真正的 Godot 2D 场景节点**（TileMapLayer ＋ Polygon2D ＋ Sprite2D），让总策划能在编辑器 2D 视图里看见并手摆；② **小地图改造往后放**（理由＝小地图要画的内容取决于地图最终形态）。🔴 **为什么编辑器里现在是空的**（实测）：`scenes/main.tscn` 只有 5 个节点、**没有任何 TileMap/Sprite2D**（grep 零命中），地图是 `scripts/world_view.gd` 在 `_draw()` 里按 shape 逐个画的（`:3` 原话「没有图片资源、没有场景继承 —— 全是数据」），且**全仓没有一个 `@tool`** ⇒ 脚本不在编辑器里执行 ⇒ 编辑器 2D 视图里**什么都看不到**。✅ **新任务书 `docs/PROMPT-scene-tilemap-exec.md`（437 行）已写**：Stage 1＝写烘焙器，从 `frames.json` ＋ `asset_draw.gd` 的贴图表生成五帧 `.tscn`/`.tres` 入库，**运行时完全不动**（游戏画面仍是 L8 的平铺管线）；🟢 因只读 frames.json ⇒ **零文件冲突、可与任何线并行**；🔴 **Stage 2（运行时从 `_draw()` 切到场景节点）不属本线**，等总策划在编辑器里确认后再派。📌 **三个引擎坑已用探针实测并写进任务书**（`lab/_probe_tilemap*.gd` 六支，未入库）：`create_tile()` 必须在 `add_source()` 之后**经 `get_source()` 取回引用**再调（用原引用调会得 0 tiles）｜`PackedScene.pack()` **必须给每个子节点设 `owner = root`**（不设则读回 children=0，设了 children=2）｜`TileMapLayer` **没有物理碰撞 API**（`add_collision_polygon()` 不存在）⇒ 墙的碰撞仍走 `scripts/frame_data.gd` 的 `solid_rects`。📌 **沙箱限制备注**：实机截图抓不到游戏画面（桌面处于锁屏态，`CopyFromScreen` 只拿到壁纸＋锁屏时钟）⇒ 实机观感验证只能靠总策划那边看，或用 headless/窗口模式渲染＋像素采样替代。


### ✅ 现在就能开

**2026-11-26 11:20 更新（用户三条新指示 ＋ 五份任务书就绪）**：

1. 🔴 **用户三条新指示（2026-11-26）**：①「**界碑删掉吧**，本来也没留有多少和它相关的有用剧情」⇒ 新开**界碑删除线**（任务书 `docs/PROMPT-stele-removal-exec.md`）；②「**不做楼层了**，时间不够了」⇒ L17 只做 phasing、方案 C 延后；③ **纠正 phasing 口径**：判据不是「以 A1 为基准」，而是「**包围可探索建筑的房屋、山体的占地范围在五帧之间保持一致（空气墙一致）**⇒ 正常游玩不会卡到山里、不会虚化穿出地图」。
2. ✅ **L17 任务书已改写（547 行）**：§2.1 主线改为「空气墙一致性是地图线的活，不是 phasing 的活」；§2.3 新增「🔴 **正常不该触发是本线第一验收项**」；§2.4 加「不许虚化出地图／不许虚化进虚空」；§3.8 补「不做楼层」；§4 新增 §4.5「空气墙一致性核对」（逐对报告触发格数，A4→A5 必须接近 0）。
3. ✅ **A4 重排线任务书已改写（464 行）**：删掉全部界碑内容；新锚点＝**zhou_a4(576,1920)**＋**zheng_a4(1152,2272)**＋**补山×4**；新增 §2.6「五帧实体空气墙一致」——实测 **cover(A5⊆A4)=100%／IoU=100%／A4↔A5 双向触发 0 格**（旧布局 IoU 只有 26.2%）；⚠️ **A1–A3 重排线等 A4 搭完后再派**（用户明说）。
4. 🔴 **实测的两个坑（已写进任务书）**：①压环岛**不能用 bbox**（环道 bbox 比真实环形大）——必须用**点包含测试**；②「实体」的判定照 `scripts/frame_data.gd:38`（`solid:false` 不进碰撞）——**路/田/井/树/内岛/环道都不算实体**，只有房屋 lot 与 `solid:true` 的世界物件算。
**2026-11-26 13:20 更新（三份反馈验收 ＋ 地图事故定性 ＋ L8 补救任务书已写）**：

1. 🔴 **三份反馈验收完毕**：**A4 重排线**（`9ec040a`）＝ **几何通过 / 视觉未交付**；**L15 归档表**（`6141ff8`＋`45c5f72`）＝ **代码层通过，接线待 L17**；**L16 双日记**（`082f0c5`→`8a9f0d2`→`01c3921`）＝ **代码层通过**（`J` 临时键待删、书热点数据未落地、举证系统需单独立项）。
2. 🔴 **用户 2026-11-26 指出地图事故**：「产出提示词后交给会话构造的地图连游戏地图的核心都丢失了……为什么环岛、公路、树都退化成了几何图形？」⇒ **根因在我，不在执行线**，四层：①任务书层（A5 v5／A4 重排两份任务书里「贴图/平铺/32×32/美术」**零命中**，验收项只验几何）②引擎层（`world_view.gd` polygon 分支**只认河**，无平铺通路）③资产层（美术 autotile 已交付未入库未接线）④**纪律层**（M16/M14 早在 2026-11-25 就写进 `待解决事项.md`，**从未转成任务书** —— 规则不落任务书＝不存在）。
3. ✅ **新立 `docs/地图视觉口径.md`**（硬约束 C1–C5 ＋ shape→贴图对应表 ＋ 引擎缺口表 ＋ 交付必查清单）＋ **新立 L8 任务书 `docs/PROMPT-asset-tile-wire-exec.md`**（410 行）：**从现在起「几何就绪」≠「视觉交付」**。
4. 🔴 **另挖到两个现存缺陷**：**D1 河跨帧宽度不一致**（a1–a3 河 103 点 x 只到 3200，a4/a5 152 点铺到 4800 ⇒ **A1–A3 的河在 x=3200 断掉**；`world_view.gd:264` 画布写死 `3200×416`）；**D2 起始帧反了**（`scripts/timeline.gd:58` 至今 `index = 0` ⇒ 进游戏站 1926，而 `docs/house-spec.md:461-464`（2026-11-19 用户拍板）要求「起始帧 = A5 往过去挖」、`:500` 坑表第一条）⇒ 两条都需另派小线。

**2026-11-26 10:10 更新（用户拍板「顶住了作废、只做虚化」＋四份新任务书已写）**：

1. 🔴 **用户拍板：「顶住这点去掉，只做虚化。顶住这点是你自己补上的我未批准的内容」** —— 「顶住了」机制**作废**（`scripts/timeline.gd:78-92` 的 bump 分支、`main.gd:_on_bump`、`world_view.gd` 震屏、`player.bump_kick`、`hud.bump_flash`），改为实现 `docs/house-spec.md` §8.3 的 **phasing（卡墙虚化）**。⚠️ `house-spec.md:770` 原本要求 phasing 与楼层方案 C 同期 ⇒ 本次**只做 phasing，不做楼层方案 C**（取舍写在 L17 任务书 §2/§3.8）。
2. ✅ **四份新任务书已写（2026-11-26）**：**L17 phasing**（`docs/PROMPT-phasing-exec.md`）、**L15 归档表+结局**（`docs/PROMPT-ending-form-exec.md`）、**L16 双日记渲染**（`docs/PROMPT-diary-render-exec.md`）、**A4 重排线**（`docs/PROMPT-a4-rebuild-exec.md`）。
3. 🔴 **并行排线（同一时刻最多三条）**：**A4 重排线**（写 `data/frames.json`）／**L15**（新建 `scripts/ending_*.gd`）／**L16**（新建 `scripts/diary_*.gd`）—— L15 与 L16 与地图线**文件零重叠**。⚠️ **接线顺序**：L15／L16 都要在最后改 `scripts/main.gd`，L17 也要改 ⇒ **L17 先交卷，L15／L16 再各自交接线段**；L15 与 L16 不能同时做接线。
4. 🔴 **两组二选一**：L17 vs L8（都改 `scripts/world_view.gd`）；A4 重排线 vs A1–A3 重排线（都改 `data/frames.json`）。


| 线 | 写哪些文件 | 为什么能开 |
|---|---|---|
| **L9 渲染缺陷调查** | ✅ **已交卷**（`014a18c`，只改 `scripts/world_view.gd` +69/−4，反馈 `docs/FEEDBACK-render-bug-exec.md` 117 行）→ **不要再开重复的**；🟡 总策划尚未独立复核（待办）。**L11 的 `world_view.gd` 阻塞已解除。**
| **L10 缺美术资产清单** | ✅ **已交付并验收**（`b0798da`）→ **不要再开重复的** | 清单 `docs/ART-GAP-A4A5.md` + `docs/ART-GAP-A4A5.csv` 已由用户转交美术同学；2026-11-25 已按「单方格复用」修订（B/C 组改成 32×32 可平铺件、总数 222） |
| **L8 资产接线**（🔴 P0） | scripts/world_view.gd + scripts/asset_draw.gd + ssets/village/scene/ 新切片 + _mdtest/tile_wire_check.gd | ✅ **已交付 2026-11-26**（两段 commit：`feat(asset)` + `docs`）；`world_view.gd` 已释放 ⇒ L17／界碑删除线可以开；不改 data/frames.json ⇒ 与 A4 重排线不冲突 |
| **L1 小尾巴（界碑/坝/田 跨年代文案）** | 只改 `data/frames.json`（三处 `hotspots[].text`） | L4 已交付，不再与文案线并行；`data/frames.json` 是 L1 独占文件、单写者 |
| **L12 界面与手感** | `scripts/hud.gd` + `scripts/main.gd` + `scripts/player.gd` + `_mdtest/hud_layout_check.gd` | ✅ **已交付并验收通过**（`b5ecbd9` ＋ `d29047f`）→ **不要再开重复的**；尾巴 R-L12-3（补地标点）挂 L11 之后 |
| **L13 树井文案与倾斜叙事删除** | `docs/story.md` + `docs/npc.md` + `docs/HANDOFF.md` | ✅ **已交付并验收通过**（`67bd62c` ＋ `1bc0494`）→ **不要再开重复的**；🔴 两条闭环项挂 L11（R-L13-1 老槐四帧 text ＝ A17、R-L13-2「2001 年修起环岛」）；🔴 新悬案 P1-8（`story.md:988` vs 树被搬 5 格）交用户拍板 |
| **L11 世界重排（数据 + 地图引擎）** | `data/frames.json` + `scripts/world_view.gd` + `scripts/frame_data.gd` | 任务书已就绪并按 v3 修订（`docs/PROMPT-l11-world-rebuild-exec.md`）；⚠️ **与 L9 争 `world_view.gd` ⇒ 必须等 L9 交卷后再开** |
| **L14 A5 落地** | `data/frames.json` ＋ `_ref/houses/houses_data.json` ＋ `scripts/evidence_store.gd` ＋ `docs/story.md` ＋ 两个测试文件的世界尺寸常量 | ✅ **已交付并验收**（`e086c83`）→ **不要再开重复的**。🔴 尾账：R-L14-1 A4↔A5 同址（超市/井/槐）**已升 P0**、R-L14-2 M15 沈家同位只满足 A5、R-L14-4 A1–A3 仍是旧布局、R-L14-5 河贴图画布写死 3200×416（属 L8）、R-L14-6 实机肉眼验证未做 |
| **A4 重排线** | `data/frames.json`（**只改 a4_2001 一帧**） | ✅ **任务书已写，可派**（`docs/PROMPT-a4-rebuild-exec.md`）；⚠️ 与 A1–A3 重排线**串行**（同写 frames.json） |
| **L15 归档表 + 结局变体** | 新建 `scripts/ending_store.gd`／`ending_report.gd`／`ending_form.gd` ＋ `_mdtest/ending_check.gd` | ✅ **任务书已写，可派**；文件零重叠，**可与地图线并行**；⚠️ 接线段要等 L17 |
| **L16 双日记渲染** | 新建 `scripts/diary_markup.gd`／`diary_page.gd`／`diary_view.gd`／`diary_texts.gd` ＋ `_mdtest/diary_render_check.gd` | ✅ **任务书已写，可派**；与 L15 文件零重叠可同时跑；⚠️ 不能与 L15 同时改 `scripts/main.gd` |
| **L17 phasing/虚化** | `scripts/timeline.gd` ＋ `scripts/player.gd` ＋ `scripts/world_view.gd` ＋ `scripts/main.gd` ＋ `scripts/hud.gd` | ✅ **任务书已按新口径改写，可派**（547 行）；🔴 与 L8 二选一（争 `world_view.gd`）；⚠️ 界碑删除线也碰 `world_view.gd` ⇒ **这三条里同一时刻只能有一条在跑** |
| **美术清单整理线** | ⚠️ **已被 L10 取代** —— L10 就是这条线的正式任务书（`docs/PROMPT-art-asset-gap-exec.md`），**不要另开一条重复的** | 用户 m05980 的「帮我理一份现在还缺少的美术资产」＝ L10 的交付物 |
| **界碑删除线** | `data/frames.json`（只删界碑条目）＋ `scripts/asset_draw.gd` ＋ `scripts/world_view.gd` ＋ `scripts/house_shape.gd` ＋ 三个 `_mdtest/` ＋ `docs/story.md` ＋ 四个资产清单 | ✅ **任务书已写，可派**；🔴 与 L17 串行（都碰 `world_view.gd`）；⚠️ 与 A4 重排线错开落盘（同写 frames.json） |
| **地图场景化（方案 B）Stage 1** | 新建 `tools/bake_world_scene.gd` ＋ `tools/world_scene_spec.gd` ＋ `scenes/world/**` ＋ `_mdtest/scene_bake_check.gd` | ✅ **Stage 1 已交付并验收（2026-11-26）**：五帧 `scenes/world/world_*.tscn` ＋ `tileset_*.tres`；🟢 **只读 `data/frames.json`、不碰 `scripts/**` ⇒ 可与任何线同时跑**（含 L17／界碑删除线／A1–A3 重排线）；⚠️ Stage 2 另派 |

### ❌ 不能开

- **L5 证物档案** —— 已交付并验收（`5a36770`），不再重开。
- **L3 房屋数据** —— 已交付并验收（`7805d71`）；R1（三处 note px 旧值）若要改，只改 note 文本、不动几何，且属该文件单写者。
- **新的 `_mdtest/` 改动线** —— 测试文件是所有线的公共依赖，改测试必须与写代码的线同一批次、同一会话，避免断言与实现错位。
- **任何同时改两份以上同一文件的线** —— 单写者锁在 §四。
- **L11 世界重排** —— 任务书已就绪，但与 **L9 争 `scripts/world_view.gd`** ⇒ **必须等 L9 交卷**（`docs/FEEDBACK-render-bug-exec.md` 至今不存在 ⇒ 要催）。**L12 / L13 不受影响，现在就能开。**


### 📌 下一批的顺序建议

0. 🔴 **先催 L9 交卷**（L9 / L8 / L11 三条都写 `scripts/world_view.gd` ⇒ 三选一）：**L9 最急**（玩家实机已踩到「人站在墙上 / 人可穿门 / A4 门口色块乱」三条，是体验级缺陷）。L9 落地后按 **L11（数据+引擎）→ L8（资产接线）** 跑，后两条的 `world_view.gd` 改动要合并跑一次七套回归。
1. ~~**L12 界面与手感**~~ ✅ **已交付并验收通过**（`b5ecbd9`）—— 小地图 + 速度 ×1.5 + 走路动画频率降档，全部到位。
2. ~~**L13 树井文案与倾斜叙事删除**~~ ✅ **已交付并验收通过**（`67bd62c` ＋ `1bc0494`）—— 六条 grep 总策划亲跑全过、§7.3 整节无「井」字、文件域零越界。🔴 仍**必须和 L11 的 `data/frames.json` 老槐四帧 text 挨着交付**（R-L13-1 ＝ A17），L11 验收时一并闭环。🔴 新悬案 P1-8（`story.md:988`「唯一没移动过的是那块地砖」vs 树被搬 5 格）**待用户拍板**。
3. **L1 小尾巴**（界碑 1951 / 坝 / 田 跨年代文案，可与 L12 / L13 同时）：只改 `data/frames.json` 的三处 `hotspots[].text` —— ⚠️ 与 **L11 同文件** ⇒ 若 L11 已开工就并进 L11，别另起一条。
4. **实机验收**（L11 + L12 + L1 小尾巴落地后一次做完）：market 两态证物 E 检视、A5 老槐 radius 决策、A1→A5 主路走一遍、小地图位置对不对。

---

*本提示词基于 2026-11-24 的实测数据，基线提交 `e287131`（之后的提交见 `git log`）。2026-11-24 20:20 增补 L9 渲染缺陷调查线。2026-11-24 22:55 增补 L10 缺美术资产清单线（任务书已写）与 L11 世界重排线（方向已裁定、任务书待写），并把玩家对地图骨架的六条裁定落进 `docs/待解决事项.md` §1.2。2026-11-25 09:19 增补：玩家八条逐条裁定落进 `docs/待解决事项.md` §1.3（M7–M16）＋ §1.4 五个待定点；L10 已交卷并按「单方格复用」修订清单；L11 任务书待写。*

*2026-11-25 10:30 增补：L11 任务书已写完（`docs/PROMPT-l11-world-rebuild-exec.md`），五个待点头数都给了默认值。*

*2026-11-25 10:55 增补：子代理交卷（`lab/_l11_final.json` v3 冻结布局 ＋ `lab/_l11_text_final.md` 逐字替换稿）；L11 任务书按 v3 修订并拆成三条并行线 —— **L11**（`docs/PROMPT-l11-world-rebuild-exec.md`，数据+地图引擎，排 L9 之后）／**L12**（`docs/PROMPT-l11b-ui-exec.md`，HUD+速度+动画，现在就能开）／**L13**（`docs/PROMPT-l11c-text-exec.md`，叙事文本，现在就能开）。*

*2026-11-25 11:10 增补：重启后复查 —— 三份任务书与三份子代理基准文件全部已入库无丢失，子代理均已交卷不再需要跑；玩家拍板「自己开新会话跑」＋ **L9 + L12 + L13 全上**。L9 任务书补 **§0.0.5**（现状 ＋ 行号逐条复核 ＋ `greybox_check.gd` 断言位置勘误表），四份任务书 HEAD 基线统一到 `92078cb`（commit `72494ea`）。*

*2026-11-25 13:50 增补：**L13 交卷并验收通过（`67bd62c` ＋ `1bc0494`），六条 grep 由总策划亲跑全过、§7.3 整节无「井」字、文件域零越界；尾巴 R-L13-1（A17 老槐四帧 text，挂 L11）／R-L13-2（§7.3「2001 年修起环岛」等 L11）／**新悬案 P1-8**（`story.md:988`「唯一没移动过的是那块地砖」vs 树被搬 5 格，交用户拍板，我倾向改措辞）／R-L13-4（老井 A1 旁听与物证重复，不阻塞）／R-L13-5（活文档已由总策划回写）。L9 仍未交卷 ⇒ L11 仍被堵。*
*2026-11-25 13:45 增补：**L12 交卷并验收通过（`b5ecbd9` 代码 ＋ `d29047f` 反馈），七套回归由总策划亲跑全绿，`REACH_MAP` 与 L11 前逐位一致；尾巴 R-L12-1（反馈提交带进 L13 的反馈文档，从宽通过）／R-L12-2（`MINIMAP_MARGIN` 单位注释）／R-L12-3（小地图补地标点，挂 L11 之后）。L13 已交卷（`67bd62c`）待验收；L9 仍未交卷 ⇒ L11 仍被堵。*

*2026-11-25 23:30 增补：**A5 v5 反馈（`docs/FEEDBACK-a5-layout-v5.md`）已由总策划独立复核完毕** —— 四处硬伤（河公式、`shen_a5` 数据不存在、反馈与自家脚本不一致、老槐五帧文案）＋ OY 1600→1664 已写进 L14 任务书 `docs/PROMPT-a5-v5-exec.md`（几何基准 `lab/_a5_v5fix.json`，errors=0）。§二 五帧表的 a5 行已更新为「v5 待落地」；§三 已加 L14 行；L11 任务书基准（`lab/_l11_final.json`）已被 A5 v5 作废待换。*
*2026-11-26 09:10 增补：**用户拍板 Q1 只做 A5 / Q2 沈家先定 A5 (64,416) / Q5 英文主题句选 A** ⇒ L14 任务书已修订（新增 §0.1 拍板表、§3.8 沈家排线顺序，§3.7 改成「只做 A5」，白名单去掉 `docs/HANDOFF.md`），并修掉 §3.1 河公式笔误（权威写法＝`exp(-((x-46.5)/16.0)**2)`，先除再平方、无 2）；主题句（中英）已落盘 `docs/story.md:988` / `docs/HANDOFF.md:833` / `README.md:5`。*
