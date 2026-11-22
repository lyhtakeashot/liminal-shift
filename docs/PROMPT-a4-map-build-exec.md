# 新会话提示词：场景搭建2 —— 搭建 A4（2001）地图帧

> 整段复制给新会话作为第一条消息。本线**只写 `data/frames.json` 的 `a4_2001` 一帧**，别的什么都不碰。

你是《shift》Godot 4.7 像素游戏的 **A4 地图搭建执行人**。

用户已明确解除「绝不落地 `frames.json`」的禁令（2026-11-22），授权本线**只填 `a4_2001` 帧**。`a5_2026` 帧**不碰**。

## 0. 开工前（必做）

```
项目：D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift
Godot：D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe
```

- 所有 pwsh 调用带 `sandbox_permissions: "danger-full-access"`。
- `git log --oneline -3` 确认 HEAD ≥ `eb6c7fa`。
- `git status --short` 会看到一大堆未提交改动（A4 精调线、视觉机制线、美术资产线在跑）。**这些文件全部只读、绝不写入、绝不 `git add`**。本线唯一的写入文件是 `data/frames.json`。
- ⚠️ **先等「场景设计3」把它对 `_ref/houses/houses_data.json` 的改动 commit 掉**（`git status` 里那几条 M 状态消失）再动手读 JSON 定坐标。否则读到半成品。
- 权威源＝`_ref/houses/houses_data.json`（18 栋），一律以 JSON 的 `lot` / `wings` 为准，**不看 note**（note 与 lot 常年不符）。

## 1. 你的独占写入文件

**只有 `data/frames.json` 里的 `a4_2001` 那一个对象**（`{"id": "a4_2001", "year": 2001, "ground": ..., "shapes": [], "hotspots": []}`）。

- `a5_2026` 帧保持原样（仍是 `shapes=[] / hotspots=[]`）。
- `world` / `safe_top` / `safe_bottom` / `start_pos` / a1_1926 / a2_1951 / a3_1976 全部**不许改**。
- 提交时**只 `git add data/frames.json`**，别的会话的文件一个都不要 add。

## 2. 地图坐标基准（已实测，照这个填，别自己重算）

世界 3200×1800，TILE=32px，全图 100×56.25 格。`a4_2001` 当前 `ground="#6f6a52"` 保持。

**A1–A3 房屋锚点（三帧完全同址，房子只在原址长大，A4 继续沿用）：**

| 位置 | A1 | A2 | A3 | A4（本线填） |
|---|---|---|---|---|
| 磨坊/粮站/超市 | `mill_a1 [1216,448]` | `mill_a2 [1216,448]` | `mill_a3 [1216,448]` | `market [1216,448]`（粮站拆→在建超市） |
| 沈家 | `shen_a1 [128,640]` | `shen_a2 [128,512]` | `shen_a3 [128,288]` | `shen_a4 [128,288]`（A3 废墟原址起新房） |
| 周家 | `zhou_house [1792,1280]` | `zhou_a2 [1792,1280]` | `zhou_a3 [1792,1280]` | `zhou_a4 [1792,1280]`（会计家） |
| 陆家→郑家 | `lu_house [2304,768]` | `lu_a2 [2304,768]` | `lu_a3 [2304,768]` | `zheng_a4 [2304,768]`（1976 废墟→2001 外来户新房） |

⚠️ 郑家坐标依据：`houses_data.json` 的 `zheng_a4.note` 明写「与 A1/A2/A3 陆家同址——1976 还是废墟(lu_a3)，2001 已起新房」，实测 `lu_a3 pos=[2304,768]`，故 A4 郑家也落这里。旧文档里「郑家 pos [1120,340]」是旧 1600×900 口径、已作废，**不可引用**。

**摆放前必做碰撞自检**：用 `houses_data.json` 的 `lot` 算占地（`(lot[2]-lot[0]+1)*32` × `(lot[3]-lot[1]+1)*32`），确认四栋互不重叠、不压主路。A4 沈家 36×36 格＝1152×1152px，从 `[128,288]` 铺到 `[1280,1440]`，会**压到主路（y≈1152）和周家（x=1792 起）吗？自己验算**：x 方向 128+1152=1280 < 1792 ✓；y 方向 288+1152=1440 与主路 y=1152~1248 **重叠** ← 这是真实冲突，按下面规则处理。

**冲突处理规则（重要）**：沈家 A4 占地 36×36 格是四合院，面积远大于 A3 的 28×24 格；若按 A3 锚点 `[128,288]` 会压主路。允许把 `shen_a4` 的 `pos` 在 A3 沈家位置上**向下或向右微调**，但必须满足：①不压主路 rect；②不压其他三栋；③`pos` 是 32 的整数倍；④仍在沈家历史地块（地图西北片区 x<1400、y<1500）内。把最终选点和验算过程写进报告。**别改 A1–A3 任何锚点。**

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
4. **河/坝/路/田**：沿用 A3 的形状与坐标（时间轴上的地标不该漂，`docs/BUILD-A1.md:115-117` 是硬口径：地标与路 A1/A2/A3 完全相同，房子只在原址长大）。A4 主路取直（A3 口径）。
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

- 视觉机制线在改 `scripts/*.gd`（y-sort、南墙半高），美术线在画 `assets/village/houses/`，都与你无关。
- 场景设计4 在改 `houses_data.json` 的 `toyshop` / `school` 两栋（A5），与你读的 A4 四栋字段不冲突，但**你绝不写这个文件**。
- 文档回写线不开；旧文档 `BUILD-A4.md` 已作废，里面的坐标是旧 1600×900 口径，**不可引用**。
