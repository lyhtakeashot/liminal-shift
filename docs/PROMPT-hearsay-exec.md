# 任务书 L20：旁听（走近就听见，按键不做）

> 立项 2026-11-26，lead 签发。用户拍板：**对话不做，只做旁听**。
> 比赛截止：北京时间 2026-12-02 05:37。

---

## §0 一句话目标

玩家走到村里的某个地方，**自动听见**两个人在说话（字幕，3–4 行，逐字出）。
主角不开口、不用按键、**听完不进行李档表**。7 条，散布在五帧。

## §1 为什么是这个形态（别自己改）

- `docs/npc.md` §2.1 写着「主角不说话，只是听见」⇒ **不做按键交互**，靠近就听。
- §2.1 还写着「旁听内容**永远不进归档表**」⇒ **绝对不能复用 `EvidenceArchive` 的卡片**，
  必须是一条独立字幕。这也是为什么它不能走 `hotspots`（现有 hotspot 带 `text` 的都会进归档表）。
- §2.1 又写「只在空间轴可听；时间轴听不见」⇒ `tl.axis != SPACE` 时必须压掉。
- §2.3「人嘴给方向，物证给结论」⇒ 旁听台词**不许**给出可填进归档表的事实。

## §2 台词已经写好了，逐字抄，一个字不许改

权威版本：**`docs/npc.md` §5.5**（7 条，每条的 `zone at` / `r` / 甲乙台词都在里面）。
你的活是**搬运 + 呈现**，不是写台词。抄错一个字就是改剧情。

台词是为「五帧读下来 = 赔偿→天灾→遗忘→迷信→邪门」这个反差设计的，
两条激情案是「几号、谁先动手、判几年，人人记得」的标尺。**别合并、别删行、别润色。**

## §3 数据：`data/frames.json` 每帧加一个**新的**顶层键

**只加 `"hearsay"` 键，`shapes` 与 `hotspots` 一个字节都不许动。**

这是本线最大的安全阀：不碰 `shapes`/`hotspots` ⇒ `greybox_check` 的
`solids`（238/299/379/812/897）与 `hotspots`（10/11/13/12/8）**必须一位不变**。
数字一变就说明你动了不该动的地方。

形状（照抄这个结构，`at` 是圆心世界坐标）：

```json
"hearsay": [
  {"who": "坝上", "at": [512, 224], "radius": 72,
   "lines": ["甲：沈家赔了三十块洋钿。", "乙：三十块？不少了。",
             "甲：仁至义尽。陆家也认了。", "乙：认了就好。这年头，肯赔钱的主儿不多。"]}
]
```

七条分别落在（`who` 照抄 §5.5 的小节标题里那个地名）：

| 帧 | who | at | radius |
|---|---|---|---|
| `a1_1926` | 坝上 | `[512, 224]` | 72 |
| `a2_1951` | 老井边 | `[1360, 912]` | 72 |
| `a2_1951` | 田边 | `[2112, 384]` | 72 |
| `a3_1976` | 田边 | `[2112, 384]` | 72 |
| `a4_2001` | 超市工地外 | `[2816, 1248]` | 72 |
| `a4_2001` | 田边 | `[4040, 576]` | 72 |
| `a5_2026` | 路口 | `[2048, 1864]` | 96 |

（A1 只有 1 条、A2 有 2 条、A3 有 1 条、A4 有 2 条、A5 有 1 条 = 7 条。
`a5` 的 `[2048,1864]` 就是玩家起始点，五帧实测可站；半径 96 是因为环岛路面宽。）

## §4 呈现：`scripts/hearsay.gd`（新建）

- 底部居中字幕块，宽约 520px，最多 4 行，每行 ≤ 24 字。
- **逐字出**（参考 `scripts/diary_page.gd` 的逐字做法，别自己发明一套），每行约 0.28s 出完；
  一行出完再出下一行。全部出完后**保持显示**（不自动消失）。
- `甲：` / `乙：` 前缀用两种颜色区分（甲方用 HUD 现有的正文色，乙方用略暗一档）。
- 走出半径 → 0.25s 淡出。
- 冷却 1.5s：走出再走进才重播；站在里面不会循环重播。
- 字体沿用 `scripts/hud.gd` 取字体的方式，**不许 new 一个 FontFile**。
- 接口（照签）：

```gdscript
extends Control
func update(tl) -> void        # 每帧调一次；内部读 tl.char_pos / tl.axis / tl.current()
func is_showing() -> bool
func hide_now() -> void
```

`update()` 里自己判：`tl.axis != Timeline.Axis.SPACE` → 立刻隐藏并 return。

## §5 `main.gd` 的改动（**先确认锁**）

`main.gd` 目前被 L19（结局收束）占着。**开工前先跑**：

```powershell
git status --short scripts/main.gd ; git log --oneline -3
```

- 若 `git status` 有输出、或最近 3 条提交里有 `feat(ending)`/`outro` 字样而 main.gd 还在改 ⇒ **停下问 lead**。
- 若已干净 ⇒ 只许加这 4 行（`grep -n` 定位，别按行号硬改）：
  1. preload 区：`const Hearsay = preload("res://scripts/hearsay.gd")`
  2. 状态区：`var hearsay: Control = null`
  3. `_make_diary()` / `_make_outro()` 之后：`hearsay = Hearsay.new()` + `add_child(hearsay)`
  4. `_process` **最前面**：`if hearsay != null: hearsay.update(tl)`
- **不要**把旁听加进「世界停」那个 early-return —— 旁听不打断行走，你是边走边听见的。

## §6 验收表

| 编号 | 断言 | 怎么验 |
|---|---|---|
| **H1** | 7 条全部就位：A1×1 / A2×2 / A3×1 / A4×2 / A5×1，每帧 `hearsay` 是数组 | `_mdtest/hearsay_check.gd` |
| **H2** | 每条 `lines.size()` 在 3–4 之间、每行 ≤ 24 字 | 同上 |
| **H3** | **逐字锚点**：每条的**首行**与 `docs/npc.md` §5.5 完全一致（把 7 个首行写成 `const` 锚点） | 同上（字符串相等，不是肉眼） |
| **H4** | 走近触发：把玩家摆到 zone 中心 → `is_showing() == true` | 同上 |
| **H5** | 时间轴不触发：`tl.axis = TIME` 时 `is_showing() == false`（**5 帧都验**） | 同上 |
| **H6** | 不进归档表：触发前后 `EvidenceArchive` 的条目数不变 | 同上 |
| **H7** | 灰盒零位移：`solids` **238/299/379/812/897**、`hotspots` **10/11/13/12/8** 一位不变 | `_mdtest/greybox_check.gd` |
| **H8** | 冒烟：`--quit-after 240` 窗口模式无 `SCRIPT ERROR`；一张字幕截图（窗口模式，不能带 `--headless`） | 命令行 |

**H7 是本线的守门员**：只要数字动了，说明你改了 `shapes`/`hotspots`，立刻回滚重做。

## §7 文件白名单

```
data/frames.json              只加 "hearsay" 键（每帧）
scripts/hearsay.gd            新建
scripts/main.gd               只加 §5 那 4 行
_mdtest/hearsay_check.gd      新建
docs/FEEDBACK-hearsay-exec.md 新建
_mdtest/hearsay_shot/*.png    字幕截图
```

**不许碰**：`scripts/world_view.gd`、`player.gd`、`hud.gd`、`frame_data.gd`、`timeline.gd`、
`evidence_archive.gd`、`ending_*.gd`、`scenes/**`、`assets/**`、`project.godot`、`docs/**`（除反馈）。

## §8 与音效线（L18）的接口

L18 交付后这里会加两处，**本线先留注释不接线**（音效单例还没入库，import 不存在的单例＝起不来）：

```gdscript
# TODO(audio): L18 交付后 → Aud.play("text_blip")（逐字时每 3 字一次）
# TODO(audio): L18 交付后 → 旁听期间环境底噪 -6dB
```

## §9 环境

```powershell
$g = "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe"
& $g --headless --path . -s res://_mdtest/hearsay_check.gd
& $g --headless --path . -s res://_mdtest/greybox_check.gd
& $g --path . --quit-after 240
```

看关键字不看退出码；不要 `cmd /c`；不要 `> out.txt`；`git add` 只加白名单，**不 push**。

## §10 交付

`docs/FEEDBACK-hearsay-exec.md`，格式照 `docs/FEEDBACK-house-art-a4a5-exec.md`。
额外回答一句：**你在游戏里从「走到井边」到「听见」之间等了多久**（秒）。
设计上应该是「踏进半径就开始出声」，如果实测要等一秒以上，那是做错了。