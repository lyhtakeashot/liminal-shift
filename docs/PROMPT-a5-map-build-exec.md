# 新会话提示词：场景搭建2 —— 搭建 A5（2026）地图帧

> 🔴 **本文件已作废（2026-11-23），保留仅作历史留档。**
> A4+A5 两帧现由 **一条线**统一写：`docs/PROMPT-map-fix-exec.md`（已交付 `0436c58`）。
> 本文件的坐标口径（school 1216×960 / toyshop 672×640 / market 1344×896）与「界碑＝school 的家具 `[1,18,2,1]`」**均已被推翻**：
> ①界碑改为**世界的独立地标物件，五帧各一个、各自一张贴图**，A5 新增世界碑 rect `[32,1024,16,32]`、热点 `[40,1040]`；
> ②`school` 的「「周」界碑」家具已于 L3（`7805d71`）撤掉；
> ③画布尺寸口径已按 TILE=32 重订（school 1216×992、toyshop 672×672、market 1344×928）。
> **不可再按本文件派工。**

> 整段复制给新会话作为第一条消息。本线**只写 `data/frames.json` 的 `a5_2026` 一帧**，别的什么都不碰。
> 数据与世界基准均已定稿（世界重构线 `29a5e2f` 已落地），这是纯落地执行，不是设计。

你是《shift》Godot 4.7 像素游戏的 **A5 地图搭建执行人**。

用户已明确授权写 `frames.json`（2026-11-22），本线只填 `a5_2026` 帧。`a4_2001` 帧**不碰**（那是另一条线/场景搭建2 的 A4 任务）。

## 0. 开工前（必做）

```
项目：D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift
Godot：D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe
```

- 所有 pwsh 调用带 `sandbox_permissions: "danger-full-access"`。
- `git log --oneline -5` 确认 HEAD ≥ `29a5e2f`（世界重构线已落地）。低于它就是基准没定，停下来问总策划。
- `git status --short` 会看到一堆别的线的改动（美术资产 D 状态、`lab/` 未跟踪产物等）。**全部只读、绝不写、绝不 add**。
- 🔴 **`frames.json` 撞车约定**：本线和「场景搭建2（A4 帧）」都可能写 `data/frames.json`。**开工前看 `a4_2001` 帧状态**：
  - 若 A4 帧仍空（`shapes=[]`）：你**可以**先写 a5 帧，但写入方式必须是「读当前文件 → 只替换 `a5_2026` 这一个对象 → 原样写回 a1/a2/a3/a4 和 world/safe/start」，绝不整文件重排、绝不碰 a4 对象。
  - 若 A4 帧已被填：更要按上条精确替换，保住它的每一个字节。
  - 提交前 `git diff -- data/frames.json` 自检：**只能看到 a5_2026 一个对象从空变有**，其它任何字段变化都说明你改错了，回退重来。
- 权威源＝`_ref/houses/houses_data.json`（18 栋），一律以 `lot`/`wings` 为准，**不看 note**（note 与 lot 常年不符，且多为 16px 旧口径）。

## 1. 你的独占写入文件

**只有 `data/frames.json` 里的 `a5_2026` 那一个对象**：`{"id":"a5_2026","year":2026,"ground":"#7a7a76","shapes":[],"hotspots":[]}`（`ground` 保持原值）。

- `world` / `safe_top` / `safe_bottom` / `start_pos` / a1_1926 / a2_1951 / a3_1976 / a4_2001 全部**不许改**。
- 提交时**只 `git add data/frames.json`**，别的会话的文件一个都不要 add，**绝不 `git add -A`**。

## 2. 世界基准（世界重构线 `29a5e2f` 已定稿，照抄，别自己重算）

- 世界 `world = {"width": 3200, "height": 2400}`（TILE=32px）。
- 主路 `ROAD_Y = 1664` px（52 格），**横向主路**，A5 是「笔直十字路口」（story §A5）——横向主路已就位；是否需要一条**竖向路**forming 十字，由你按叙事判断，但**不得改横向主路基准**。拿不准就问总策划，别擅自加竖路。
- `start_pos = [1024, 1680]`（新路中央），`safe_top=36` / `safe_bottom=2240`。
- `a5_2026.ground = "#7a7a76"`（保持）。

## 3. A5 房屋尺寸（⚠️ 用 32px 口径，别信 HANDOFF 旧值）

| id | 房屋 | lot | 现行格数 | **真实像素（×32）** | 状态 |
|---|---|---|---|---|---|
| `school` | 小学（沈明远捐建） | `[0,0,37,29]` | 38×30 格 | **1216×960 px** | ✅ 定稿 v6；界碑嵌围墙 |
| `toyshop` | 玩具店（周家曾孙租沈家的楼） | `[0,0,20,19]` | 21×20 格（屋本体 21×16 + 北侧 4 格庭院） | **672×640 px** | ✅ 定稿 v5 |
| `market` | 超市（继续营业） | `[0,0,41,27]` | 42×28 格 | **1344×896 px** | 沿用 A4 那栋，**直接复用 `market` 这个 id，不要新建 `market_a5`** |

🔴 **最大的坑**：`docs/HANDOFF-VILLAGE.md` 里的 `608×480`（school）、`336×320`（toyshop）、`:312` 的「school 42×32 / 672×512」全是**16px 时代旧口径**，一律作废。真值就是上表 ×32 的数。摆位碰撞一律用 `(lot[2]-lot[0]+1)*32 × (lot[3]-lot[1]+1)*32` 现算。

## 4. A5 摆位（自己验算，别抄旧坐标）

A1–A4 的房屋锚点是「四代同址、房子在原址长大」。A5 三栋建议沿这个传统，但**必须用新基准（路 1664px / 世界 H=2400）重新验算**，不压路、不互相重叠、不压河：

- 参考 A1–A4 同址锚点：磨坊系 `[1216,448]`、沈家 `[128,288]`、周家 `[1792,1280]`、陆家/郑家 `[2304,768]`。
- `school` 38×30 格比 `market` 42×28 略小但仍是巨物（1216×960px），摆不下就往路南大片空地放，别压路。
- `toyshop`「在超市旁、租沈家的楼」——摆位上靠近 `market`，叙事上说得通。
- 摆放前逐栋算占地框，确认：①不压主路 rect（含 `road:true` 段）；②三栋互不重叠；③`pos` 是 32 的整数倍；④都在世界 3200×2400 内。把选点+验算写进报告。
- `house` shape 写法：`{"type":"house","id":"school","pos":[x,y],"solid":true}`（id 必须精确等于 houses_data.json 里的键）。

## 5. shapes 可用的 type（`scripts/world_view.gd` 的 match 白名单，写别的静默忽略）

- `rect`: `{"type":"rect","rect":[x,y,w,h],"color":"#RRGGBB","label":"...","solid":bool,"road":bool}`（px 单位；`road:true` 只是标记，碰撞看 `solid`）
- `circle`: `{"type":"circle","center":[x,y],"radius":n,"color":"#...","label":"...","solid":bool}`（label 含「槐」且 radius≥12 会画树干+树冠抬升）
- `polygon`: `{"type":"polygon","points":[[x,y],...],"color":"#...","label":"河","solid":true}`
- `house`: 见上。

## 6. A5 场景内容（照 A3/A4 结构写 + story 的 A5 变化点）

参考实现（**抄结构不抄坐标**）：`data/frames.json` 的 `a3_1976` 帧——河 polygon + 坝 rect + 主路 rect + 田 rect + 老井 circle + 老槐 circle + 界碑 rect + 4 个 house。地标在 A1–A3 完全同址，A5 继续沿用（河/坝/井/老槐本体位置不漂）。

story（`docs/story.md`）的 A5 关键变化点：
1. **老槐**：1926 种在井边是树苗，2026「把超市门口的地砖拱裂了」——保留老槐 circle（radius 随年代最大，参考 `docs/BUILD-A1.md` 直径口径），可在超市门口加几块裂纹 rect 示意（可选，`solid:false`）。
2. **界碑**：「周界」碑嵌在小学围墙里（story §4.5、§附1）——school 摆位后，把界碑 rect/`label` 放到小学围墙位置；`school` 数据里界碑家具是 `[1,18,2,1]`（相对格），换成帧坐标时按 school 的 pos 换算。
3. **玩具店招牌**：小字「本店由沈氏物业出租」——做成 toyshop 附近的 hotspot 文本，别手写进家具热点。
4. **十字路口 / 停车场**：story §A5 提到「笔直十字路口、停车场」——横向主路已有；停车场可用一块灰 rect 示意（`solid:false`）；竖路见 §2 的判断是否问总策划。
5. **老井**：A3 是水泥井，A4 被盖成沥青补丁；A5 继续是补丁口径（`solid:false`）。

### hotspots（A5 至少要有这几个）

- 老井沥青补丁 / 老槐 / 界碑 / 坝 / 田：沿用 A3/A4 结构，文字按 2026 状态改（井已盖、槐拱裂地砖、碑嵌小学墙）。
- 「周界」碑 hotspot：叙事是「这块地曾经划在周家边界内」，可在文本里点一句。
- **家具级线索点由 `frame_data.gd:66` 自动从 `houses_data.json` 的 `furniture[].clue:true` 生成**（school/toyshop/market 的 clue），**不要手写进 `hotspots`**（会重复）。
- `scripts/house_shape.gd` 的 `CLUE_TEXTS` 只到 A3、A5 证物文案退化的事是**另一条装饰线**的活，本线不管、不碰 `scripts/*.gd`。

## 7. 验收（本线自己必跑）

- `python -X utf8 -c "import json;d=json.load(open('data/frames.json',encoding='utf-8'));print([(f['id'],len(f['shapes']),len(f['hotspots'])) for f in d['frames']])"` → a5_2026 应 shapes>0、hotspots>0；a4_2001 保持你开工时的状态（空就仍空）。
- `git diff -- data/frames.json` → **只有 a5_2026 对象变化**，其它字段零变化（§0 自检）。
- 六套回归：`_mdtest/{greybox,camera,display,hud_layout,asset_draw,sort}_check.gd`，跑法 `Godot --headless --path . --script res://_mdtest/<脚本>.gd`。**沙箱噪声 `Failed to read the root certificate store.` / `[exit code:1]` 是基线固有，判绿看关键字不看退出码**：`WORLD_OK` / `START_OK` / `HOTSPOTS_OK` / `WALL_BLOCKED` / `REACH_OK` / `UNEXPLAINED_BLOCKS=0` / 各 `fails=0`。
- headless 不能管道捕获 stdout，用 `cmd /c "<Godot> --headless --path . --script res://_mdtest/<脚本>.gd > out.txt 2>&1"` 再读文件。
- 实机打开 A5 帧走一圈（去掉 --headless）：三栋房子可见、玩家不穿墙、碑/井可检视、`E` 能读到家具线索。

## 8. 收工

- 只 `git add data/frames.json`，commit 信息 `feat: 搭建 A5 2026 地图帧（小学/玩具店/超市 + 十字路口 + 热点）`。
- 报告写清：三栋 pos 的选定与验算、shapes/hotspots 数量、`git diff` 确认只动 a5 对象、六套回归关键字结果、a4_2001 未动确认、有没有遗留问题。
- 交付前输出最多 **3 个**真正需要本人拍板的问题（例如竖路要不要加、停车场位置），别罗列一堆问号。

## 9. 边界提醒（别的线在跑，别管它们）

- 场景搭建2（A4 帧）可能与您同写 `frames.json`——按 §0 的「一帧一写者 + 精确替换」约定错开，别覆盖它。
- 视觉机制线/消费线的 `scripts/*.gd` 已封版，只读。
- 美术线在画 `assets/village/houses/`，与你无关；A5 两栋的美术成品图是另一条线的活。
- 旧文档 `docs/BUILD-A4.md`、`docs/_backup/` 下封存件里的坐标是旧 1600×900 口径，**不可引用**；`docs/HANDOFF-VILLAGE.md` 里的像素尺寸是 16px 旧口径，**不可引用**（见 §3）。
