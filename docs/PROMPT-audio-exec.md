# 任务书 L18：音效层（从零到一）

> 立项 2026-11-26，lead 签发。**这是项目第一条音频线，之前一个音频文件都没有。**
> 比赛截止：北京时间 2026-12-02 05:37（GitHub Game Off）。今天 11-26。

---

## §0 你是谁、要做什么

你是本项目（《阈限迁移 SHIFT》，Godot 4 像素叙事）的**音频执行线**。

一句话目标：**让游戏有声音** —— 13 个自研合成的音效文件 + 1 个 autoload 播放器 + 1 套无头断言。
**不接线**（不改主逻辑，见 §2）。接线是下一步，等 lead 放行。

先读这三个文件再动手：

1. `docs/PROMPT-overseer.md` §四（写者锁 + 绝对不能并行的组合）
2. `docs/RESUME-2026-11-26-1415.md` §8（引擎红线）、§9（命令与沙箱姿势）
3. `scripts/main.gd` 前 60 行（看懂现有代码风格：全轮询、不用 `_unhandled_input`）

---

## §1 现状（已实测，别重复调研）

- 全仓库 `*.wav / *.ogg / *.mp3` 数量 = **0**。`project.godot` 里**没有 `[autoload]` 段**，也没有任何 audio 相关键。
- `project.godot` 的 `[display]` 段：窗口 1280×720，`stretch mode = canvas_items`，`CONTENT_SCALE_MODE=1`。
- 目标平台是 **Web 导出**（gl_compatibility），音频必须走 **WAV（PCM）**，不要 OGG/MP3（Web 上解码不稳、体积也压不下来多少）。
- 本机 python：`C:\Users\lyh\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe`（3.12.14，**numpy 2.3.5 已装**）。系统 python 不在 PATH。
- Godot：`D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe`

---

## §2 硬约束（违反即返工）

### 2.1 素材必须自研合成，零第三方音频

- **不许**下载任何音效素材（CC0 也不行）。理由有二：①赛事要查素材可用性，自研的版权链最干净；②本机目前的 A4/A5 参考美术就是「拿不到可用的第三方资产」才转成自研的（`_ref/art/A4_2001/*` 全不透明无 alpha，切图走不通）。
- 全部音频由 `tools/gen_audio.py` **程序化合成**并落盘成 WAV。生成器入库，**同一个命令必须能逐字节重现已有的 13 个文件**（固定 seed、固定顺序、无随机源、不读时间）。
- 格式统一：**22050 Hz / 单声道 / 16-bit PCM / 峰值 ≤ 0.9（不削波）**。复古感靠采样率和音色，不靠位数。

### 2.2 文件白名单（只能写这些）

```
tools/gen_audio.py               新建
assets/audio/*.wav               新建（13 个，见 §3）
assets/audio/*.wav.import        新建（Godot 导入必须，**必须一起提交**）
scripts/audio.gd                 新建（autoload 单例）
_mdtest/audio_check.gd           新建（无头断言）
project.godot                    只允许**新增**一段 [autoload]（1 行）
docs/FEEDBACK-audio-exec.md      新建（你的交付说明）
```

### 2.3 绝对不许碰（这条是死线）

```
scripts/main.gd          ← 主循环，写者锁在 lead 手里（另有结局演出线在排队）
scripts/world_view.gd    ← lead 刚改完房檐透视，未发布
scripts/player.gd
scripts/hud.gd
scripts/ending_form.gd / ending_report.gd / ending_store.gd
data/**                  ← data/frames.json 是单写者
scenes/**
assets/village/**
docs/**  除你自己的反馈文件
```

**为什么**：`main.gd` 目前有两条线在排队（结局演出、音效接线）。你先做「素材 + 单例 + 断言」，这三样零冲突、可并行；接线由 lead 排在最后统一做。**不要擅自加一行 "顺手接一下" —— 这是本项目历史上出过双写事故的地方。**

---

## §3 要交付的 13 个音效

按「玩家一局会听到的顺序」排，**做不出来就砍，别硬凑**。每行给了合成配方，照着做即可，不需要你有音频设计经验。

| # | 文件名 | 时长 | 用途 | 合成配方 |
|---|---|---|---|---|
| 1 | `amb_a1.wav` | 4.0s loop | 1926 环境底噪 | 低频风声（带通噪声 200–800Hz）+ 蝉鸣（4kHz 窄带脉冲串，约 6 次/秒，密度随机但 seed 固定） |
| 2 | `amb_a2.wav` | 4.0s loop | 1951 | 风声更宽（200–1200Hz）+ 远处人声嗡（200Hz 方波 + 强低通，几乎听不见但压住氛围） |
| 3 | `amb_a3.wav` | 4.0s loop | 1976 | 广播底噪（1kHz 窄带 + 慢速调幅）+ 电流杂音 |
| 4 | `amb_a4.wav` | 4.0s loop | 2001 | 车流（低频隆隆 60–120Hz）+ 稀疏电视声（1.5kHz 短脉冲） |
| 5 | `amb_a5.wav` | 4.0s loop | 2026 | 空场风声（更干、更空，高频少）+ 50Hz 电流嗡及二次谐波 |
| 6 | `step_1.wav` | 0.08s | 脚步变体 1 | 40ms 带通白噪声（800–2500Hz）+ 20ms 指数衰减尾 |
| 7 | `step_2.wav` | 0.08s | 脚步变体 2 | 同上，中心频率 ×1.25，起音延迟 5ms（轻重脚的区别） |
| 8 | `shift_fwd.wav` | 0.30s | 时间轴前进一帧 | 220→110Hz 正弦下滑 + 噪声扫频（模拟石磨/胶片前进） |
| 9 | `shift_back.wav` | 0.30s | 时间轴后退一帧 | 第 8 条**时间反转**（波形倒放，不要重新合成） |
| 10 | `axis.wav` | 0.20s | 切换空间轴/时间轴 | 60Hz 正弦 + 快衰减 + 一层 200Hz 短脉冲 |
| 11 | `collect.wav` | 0.25s | 证物入档 | 523/659/784Hz 三音琶音，每音 60ms，正弦 + 轻微失谐（+3Hz） |
| 12 | `ui_toggle.wav` | 0.10s | 档案/日记/归档表开或关 | 1ms 冲击 + 8ms 指数衰减的宽带 click（只做一条，开和关共用） |
| 13 | `ending.wav` | 2.50s | 归档表落定出口 | 低频 drone（55Hz + 82.5Hz 五度）+ 缓慢上行，尾部 0.5s 淡出 |

**循环音（1–5）额外要求**：首尾各 50ms 做交叉淡化，保证 `|首采样 − 尾采样| < 0.02`（循环接缝不爆音）。写进断言。

**不做的**：BGM/配乐、语音、3D 定位音。赛前时间不够，氛围靠环境底噪 + 交互音效就够。

---

## §4 `scripts/audio.gd` 的接口（照这个签，别自创）

autoload 名 **`Aud`**（不是 `Audio` —— Godot 有 `AudioServer`/`AudioStream`，用 `Audio` 当单例名容易在自动补全里撞）。

```gdscript
extends Node
## 音频单例。autoload 名 = Aud。
## 设计口径：所有音频一次性 preload 进内存（13 个 WAV 合计 < 2MB，Web 导出反而更快）。

const BUS_MASTER := "Master"
const BUS_AMBIENT := "Ambient"
const BUS_SFX := "SFX"

func play(sfx: String) -> void          # 播一条 SFX（同名可重叠，不打断上一条）
func ambient(frame_id: String) -> void  # 切环境底噪（"a1_1926" … "a5_2026"），同名重复调用是 no-op
func stop_ambient() -> void
func set_volume_db(bus: String, db: float) -> void
func ready_check() -> Dictionary        # 返回 {"streams": 13, "buses": [...], "ambient": "..."} 给断言用
```

- **总线在 `_ready()` 里运行时建**（`AudioServer.add_bus()`），不要手改 `default_bus_layout.tres` —— 那是二进制资源，改坏了没人会改回来。
- `play()` 用一个池子（8 个 `AudioStreamPlayer` 循环复用），不要每次 `new()`。
- 音效表用 `const` 字典写死路径，**路径错了要在 `ready_check()` 里报出来**，不要静默 `null`。
- 不读 `user://`、不存任何设置（音量是赛前不做的事）。

---

## §5 `tools/gen_audio.py` 的要求

- 纯 python + numpy + 标准库 `wave`，**不引入任何新依赖**（本机没网，装不了）。
- `python tools/gen_audio.py`（无参数）→ 重写 `assets/audio/` 下全部 13 个文件。
- `python tools/gen_audio.py --check` → 只校验已有文件是否与重新合成的结果**逐字节相同**，不同就非零退出并列出差异文件名。这条是「素材可复现」的机器证明。
- 顶部必须写清采样率/声道/位深/峰值上限，以及每个音色的配方注释（对应 §3 表格行号）。
- 中文注释，和 `_ref/art/gen/_gen_shells.py` 的风格一致（那文件是同类生成器，可以抄它的 `main(argv)` 结构）。

---

## §6 验收表（逐条做，做完在反馈里逐条报）

| 编号 | 断言 | 怎么验 |
|---|---|---|
| **G1** | 13 个 wav 全部存在且能被 Godot `load()` 成 `AudioStreamWAV` | `_mdtest/audio_check.gd` |
| **G2** | 每个文件采样率 22050、16-bit、单声道、时长 > 0 | 同上 |
| **G3** | 每个文件峰值 ≤ 0.9（不削波） | 同上（读出 PCM 采样算峰值） |
| **G4** | 5 条循环音首尾采样差 < 0.02 | 同上 |
| **G5** | 生成器可复现：`--check` 返回 0 | 命令行 |
| **G6** | autoload 生效：`godot --headless --path . --quit-after 60` 输出里**没有** `SCRIPT ERROR`/`Parse Error`，且 `ready_check()` 报 13 个 stream、3 条 bus | 命令行 |
| **G7** | `Aud.play("collect")` / `Aud.ambient("a3_1976")` 调用不报错、不 return null | `_mdtest/audio_check.gd` |
| **G8** | `.wav.import` sidecar 全部提交（缺了 Web 导出会静音） | `git status` 自查 |

**报告格式照 `docs/FEEDBACK-house-art-a4a5-exec.md`**：§1 产出表 → §2 每个音色的实测参数（时长/峰值/首尾差）→ §3 验收表逐条 → §4 剩余问题 → §5 提交范围。

---

## §7 环境与命令

```powershell
# 合成本地（在仓库根）
& "C:\Users\lyh\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe" tools\gen_audio.py
& "C:\Users\lyh\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe" tools\gen_audio.py --check

# 导入（生成 wav 后必须跑一次，否则 ResourceLoader.exists() 是 false）
& "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe" --headless --path . --import

# 断言 / 冒烟
& "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe" --headless --path . -s res://_mdtest/audio_check.gd
& "D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe" --headless --path . --quit-after 60
```

- **看关键字，不看退出码**（本项目 `greybox_check.gd` 退出码不可信，`$LASTEXITCODE` 常读空）。
- 不要 `cmd /c`，不要 `> out.txt` 重定向（沙箱下会 EPERM）。
- `--headless` 下音频驱动可能是 dummy：**断言不许依赖「真的出声」**，只断言资源与时长。出声由人在真机上听，写进反馈的「未做」栏。
- 提交：`git add` 只加 §2.2 白名单里你自己的文件，**绝不 `git add -A`**，**不要 push**。

---

## §8 交付后必须告诉我（写进反馈最后一段）

1. 哪个音色听起来最不像（你自己判断，可以写「我听不出好坏」——不需要装懂）。
2. `project.godot` 的 `[autoload]` 具体加了哪一行。
3. 13 个文件合计字节数（要给 Web 导出算预算）。
4. 你认为 §3 里哪几条应该砍掉（如果某条做出来很难听，说出来，我拍板砍）。

---

## §9 下一阶段（**不要现在做**）

接线（脚步/切帧/收证物/开关界面/落定出口 → `Aud.play(...)`）要动 `scripts/main.gd`，
而 `main.gd` 正在排「结局演出」线。等 lead 说「音效线可以接 main.gd 了」再开第二阶段，
第二阶段另发任务书（L18b），内容：在 `main.gd` 的 6 个既有分支里各插一行 `Aud.play(...)`，
**不新增任何 InputMap action、不改任何既有分支的判断条件**。