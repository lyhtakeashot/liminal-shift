# 新会话提示词：场景搭建2 —— 搭建 A4（2001）地图帧

> 🔴 **本文件已作废（2026-11-23），保留仅作历史留档。**
> 后续修正线用 **`docs/PROMPT-map-fix-exec.md`**（A4+A5 合并一条线写，含已定案的摆位坐标、界碑挪位、井文案对齐）。
> 本文件的坐标表（market [1216,448] / shen_a4 [128,288] / zhou_a4 [1792,1280] / zheng_a4 [2304,768]）与「超市压井」结论**均已被推翻**，不可再引用。

> 整段复制给新会话作为第一条消息。本线**只写 `data/frames.json` 的 `a4_2001` 一帧**，别的什么都不碰。

你是《shift》Godot 4.7 像素游戏的 **A4 地图搭建执行人**。

用户已明确解除「绝不落地 `frames.json`」的禁令（2026-11-22），授权本线**只填 `a4_2001` 帧**。`a5_2026` 帧**不碰**。

## 0. 开工前（必做）

```
项目：D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift
Godot：D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe
```

- 所有 pwsh 调用带 `sandbox_permissions: "danger-full-access"`。
- `git log --oneline -3` 确认 HEAD ≥ `29a5e2f`（世界重构线已落地：世界 3200×2400、主路 y=1664）。低于它就是基准没定，停下来问总策划。
- `git status --short` 会看到一大堆未提交改动（A4 精调线、视觉机制线、美术资产线在跑）。**这些文件全部只读、绝不写入、绝不 `git add`**。本线唯一的写入文件是 `data/frames.json`。
- ⚠️ **先等「场景设计3」把它对 `_ref/houses/houses_data.json` 的改动 commit 掉**（`git status` 里那几条 M 状态消失）再动手读 JSON 定坐标。否则读到半成品。
- 权威源＝`_ref/houses/houses_data.json`（18 栋），一律以 JSON 的 `lot` / `wings` 为准，**不看 note**（note 与 lot 常年不符）。

## 1. 你的独占写入文件

**只有 `data/frames.json` 里的 `a4_2001` 那一个对象**（`{"id": "a4_2001", "year": 2001, "ground": ..., "shapes": [], "hotspots": []}`）。

- `a5_2026` 帧保持原样（仍是 `shapes=[] / hotspots=[]`）。
- `world` / `safe_top` / `safe_bottom` / `start_pos` / a1_1926 / a2_1951 / a3_1976 全部**不许改**。
- 提交时**只 `git add data/frames.json`**，别的会话的文件一个都不要 add。

🔴 **与「A5 地图线」共写 `frames.json` 的防撞约定（必守，和 `PROMPT-a5-map-build-exec.md` §0 对称）**：
- 两条线写的是**同一个文件**、不同的帧对象。写入方式必须是「**读当前文件 → 只替换 `a4_2001` 这一个对象 → 原样写回 a1/a2/a3/a5 和 world/safe/start**」，绝不整文件重排、绝不碰 a5 对象。
- **落盘有先后**：开工先看 `a5_2026` 帧状态。若它已被 A5 线填好，必须基于**这份已含 a5 改动的最新文件**做替换，把 a5 的每一个字节原样保住；反之若你先落盘，A5 线也会保住你的 a4。
- 提交前 `git diff -- data/frames.json` 自检：**只能看到 `a4_2001` 一个对象从空变有**；若同时看到 a5 或其它字段变化，说明你基于旧文件覆盖了别人，立刻回退重来。
- 设计草案（算坐标、排 shapes）可以两边同时做，**但真正落盘和 commit 请与 A5 线错开先后**，别卡在同一秒写同一个文件。

## 2. 地图坐标基准（世界重构线 `29a5e2f` 已定稿，照抄，别自己重算）

世界 **`3200×2400`**（TILE=32px，全图 100×75 格），主路已南移到 **`ROAD_Y = 1664` px（52 格）**，起点 `start_pos=[1024,1680]`，`safe_top=36` / `safe_bottom=2240`。这些都在 `frames.json` 里已就位，**一个都不许改**。`a4_2001` 当前 `ground="#6f6a52"` 保持。

> 🔴 旧基准（世界 3200×1800、主路 y≈1152）已作废。之前「沈家压路无解、必须走世界重构线」的结论就是冲着旧路来的；现在路南移到 1664，河下缘到路北缘的带宽已恢复到 1184px > 沈家 1152px，**摆位冲突自动消解**——不用再为沈家压路纠结。

**A1–A3 房屋锚点（三帧完全同址，房子只在原址长大，A4 继续沿用）：**

| 位置 | A1 | A2 | A3 | A4（本线填） |
|---|---|---|---|---|
| 磨坊/粮站/超市 | `mill_a1 [1216,448]` | `mill_a2 [1216,448]` | `mill_a3 [1216,448]` | `market [1216,448]`（粮站拆→在建超市） |
| 沈家 | `shen_a1 [128,640]` | `shen_a2 [128,512]` | `shen_a3 [128,288]` | `shen_a4 [128,288]`（A3 废墟原址起新房） |
| 周家 | `zhou_house [1792,1280]` | `zhou_a2 [1792,1280]` | `zhou_a3 [1792,1280]` | `zhou_a4 [1792,1280]`（会计家） |
| 陆家→郑家 | `lu_house [2304,768]` | `lu_a2 [2304,768]` | `lu_a3 [2304,768]` | `zheng_a4 [2304,768]`（1976 废墟→2001 外来户新房） |

⚠️ 郑家坐标依据：`houses_data.json` 的 `zheng_a4.note` 明写「与 A1/A2/A3 陆家同址——1976 还是废墟(lu_a3)，2001 已起新房」，实测 `lu_a3 pos=[2304,768]`，故 A4 郑家也落这里。旧文档里「郑家 pos [1120,340]」是旧 1600×900 口径、已作废，**不可引用**。

**摆放前必做碰撞自检**：用 `houses_data.json` 的 `lot` 算占地（`(lot[2]-lot[0]+1)*32` × `(lot[3]-lot[1]+1)*32`），确认四栋互不重叠、不压主路（新路 **y=1664~1728**）、不压河 polygon。A4 沈家 36×36 格＝1152×1152px，从 `[128,288]` 铺到 `[1280,1440]`：x 方向 128+1152=1280 < 1792（周家）✓；y 方向 1440 < 1664（主路北缘）✓ —— **新基准下按 A3 老锚点摆放即可，不再压路**。但仍需自己逐栋验算并把结果写进报告。

**界碑/超市冲突**：旧基准下超市必须压井+老槐、界碑(1856,960)必被覆盖的死结，随主路南移与摆位空间变大已消解。万一仍撞上，按总策划已拍板的「**热点移到可达处**」处理——界碑可以被圈进超市地块，但它的 hotspot 必须放到玩家能站的位置，**绝不删热点**。

## 3. 场景内容（照 A1–A3 的结构写，别照作废文档）

`data/frames.json` 的每个 frame 结构：`{"id", "year", "ground", "shapes": [], "hotspots": []}`。

### shapes 可用的 type（与 `scripts/world_view.gd:126-173` 的 match 完全一致，写别的会被静默忽略）

- `rect`: `{"type":"rect","rect":[x,y,w,h],"color":"#RRGGBB","label":"...","solid":true/false,"road":true}`（rect 单位是 px；`road:true` 只作标记，碰撞仍看 `solid`）
- `circle`: `{"type":"circle","center":[x,y],"radius":n,"color":"#...","label":"...","solid":...}`（label 含「槐」且 radius≥12 会画树干+树冠抬升）
- `polygon`: `{"type":"polygon","points":[[x,y],...],"color":"#...","label":"河","solid":true}`（河）
- `house`: `{"type":"house","id":"<houses_data.json 里的 ID>","pos":[x,y],"solid":true}` ← 四栋就写这四条

### 本帧应画的地形（以 A3 帧为底，按 2001 年剧情变化）

参考实现（**别抄坐标，抄结构**）：`data/frames.json` 的 `a3_1976` 帧——河 polygon + 坝 rect + 主路 rect 若干 + 田块 rect + 老井 circle + 老槐 circle + 界碑 rect + 4 个 house。

A4 的剧情变化点（从 `houses_data.json` 的 note / clue 和 `docs/house-spec.md` 提取，不确定的标问号问用户）：

1. **老井**：A3 是水泥井 `{"center":[1360,848],"radius":32,"label":"老井·水泥"}`；A4 note 说「路口圆形沥青补丁＝井口」（粮站拆、超市建、井被盖住）——把 label 改成沥青补丁口径，`solid:false`。
2. **老槐**：A3 `[1296,976]` radius96；A4 是否还在，按 house-spec 时间线判断（`docs/BUILD-A1.md:96` 直径 3→5→7→9→13 格），拿不准就保留 A3 的。
3. **界碑**：A3 `[1856,960,16,32]` label「碑」；A5 `school` 围墙有「周」界碑 `[1,10,2,1]`——A4 保留。
4. **河/坝/路/田**：沿用 A1–A3 的形状与坐标（时间轴上的地标不该漂，`docs/BUILD-A1.md:115-117` 是硬口径：地标与路在不同时代完全相同，房子只在原址长大）。**主路必须照 A3 的新基准填**（世界重构后 A3 是 `[0,1664,3200,64]` 一条横贯直路，取直口径），别用旧的 y≈1152 坐标。河 polygon、坝 `[384,96,256,128]`、田块坐标 A1–A3 三帧一致，直接抄 A3。
5. **超市工地**：`market` 在建态，可在其 lot 范围内加围挡/建材堆的 rect 示意（可选，不影响碰撞）。

### hotspots（A4 至少要有这几个）

- 老井沥青补丁：`{"pos":[1360,848],"title":"...","reach":88,"text":"..."}`
- 老槐 / 界碑 / 坝 / 田：沿用 A3 的，文字按 2001 年状态改。
- **家具级线索点由 `frame_data.gd:66` 自动从 `houses_data.json` 的 `furniture[].clue:true` 生成**（四栋共 6+3+4+2 条 clue），**不要手写进 `hotspots`**（会重复）。
- 郑家刻意「不知情」：`zheng_a4` 没有任何 clue 家具，别给它编线索。

## 4. 验收（本线自己必跑）

- `python -c "import json; d=json.load(open('data/frames.json',encoding='utf-8')); print([(f['id'],len(f['shapes']),len(f['hotspots'])) for f in d['frames']])"` → a4_2001 应有 shapes > 0、hotspots > 0，a5_2026 仍 0/0。
- 四套回归：`_mdtest/{greybox,camera,display,hud_layout}_check.gd`，跑法 `Godot --headless --path . -s res://_mdtest/<脚本>.gd`。**沙箱噪声 `Failed to read the root certificate store.` / `[exit code:1]` 是基线固有，判绿看关键字不看退出码**：`WORLD_OK` / `START_OK` / `WALL_BLOCKED` / `REACH_OK` / `UNEXPLAINED_BLOCKS=0` / `HOTSPOTS_OK`。
- 实机打开 A4 帧走一圈：四栋房子可见、玩家不穿墙、井/碑可检视、`E` 能读到家具线索。

## 5. 收工

- 只 `git add data/frames.json`，commit 信息 `feat: 搭建 A4 2001 地图帧（四栋房屋 + 地标 + 热点）`。
- 报告写清：四栋 pos 的选定与验算、shapes/hotspots 数量、四套回归关键字结果、a5_2026 确认未动、有没有遗留问题。

## 6. 边界提醒（别的线在跑，别管它们）

- 世界重构线已 commit `29a5e2f`（世界 3200×2400、主路 y=1664、A1–A3 已重画），**这是你的基准来源，别改它**。
- `greybox_check.gd` 的解释集已由世界重构线改成 `for fi in range(1, tl.frames.size())`，A4 房屋不会再被误判 UNEXPLAINED；**你不要碰这个测试文件**。
- 视觉机制线已 commit（`world_view.gd` 的 y-sort + 南墙半高），美术线在画 `assets/village/houses/`，都与你无关。
- 场景设计4 在改 `houses_data.json` 的 `toyshop` / `school` 两栋（A5），与你读的 A4 四栋字段不冲突，但**你绝不写这个文件**。
- 文档回写线不开；旧文档 `BUILD-A4.md` 已作废，里面的坐标是旧 1600×900 口径，**不可引用**。
- A5 帧由另一条线单独搭（`PROMPT-a5-map-build-exec.md`），同样遵守「一帧一写者」：**你只写 a4_2001，绝不碰 a5_2026**。
