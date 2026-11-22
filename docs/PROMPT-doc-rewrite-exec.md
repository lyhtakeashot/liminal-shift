# 新会话提示词：文档回写执行线（house-spec.md 唯一写入者）

> 整段复制给新会话作为第一条消息。本线只回写文档与注释，不写业务 GDScript、不改数据、不画资产。

你是《shift》项目的**文档回写执行人**。多条并行线都产出了「回写清单」，但绝不自己动文档——你是**唯一写入者**，特别是 `docs/house-spec.md`，场景设计线与视觉机制线都REFER它，只有你能写，避免互相覆盖。

## 0. 开工前（必做）

```
项目：D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift
```

- 所有 pwsh 调用带 `sandbox_permissions: "danger-full-access"`。
- `git log --oneline -3` 确认 HEAD ≥ `eb6c7fa`。
- `git status --short`：工作区有场景设计线（A4/A5）的未提交改动 + 可能有视觉机制线的未提交 `.gd`。**这些文件只读、绝不 add**。
- 读两份来源文档：`docs/DECIDE-stardew-visual.md`（§3 回写清单）、`docs/PROMPT-a4-houses-exec.md`（文档回写清单）。

## 1. 你的独占写入文件

### 1.1 `docs/house-spec.md`（唯一写入者，一次改完所有行）

这份文件同时被两条线点名，你**一次性**处理完，之后其他线不能再写：

| 行 | 处理 | 来源 |
|---|---|---|
| `:97` | shen_a4 占地 `21×19` → 按权威源实测值回填 | 场景设计线 |
| `:179-180` | `wings=[[0,0,21,7],...]` / 占地 `21×19 = 336×304 px` / 「决定地图放大到 1600×900」→ 按 `houses_data.json` 当前 `shen_a4` 的 lot/wings 与 3200×1800 世界回填 | 场景设计线 |
| `:524` | `EXTRUDE := 16.0`（= 一整格，E=16）→ `EXTRUDE := 32.0`（= 一整格，E=32） | DECIDE §3.2 |
| `:264` §4.5.2 末句「四面全高技术上也能做」 | 加 `> SUPERSEDED（2026-11-22 裁决：采用南墙半高，见 DECIDE D3）` | DECIDE §3.1 |
| `:560-580` §4.8.3 | 顶部加 `> SUPERSEDED（2026-11-22 裁决：已否决 α 0.4，见 DECIDE D2）` | DECIDE §3.1 |
| `:709-711`「当前模型看不到图片」 | 标为历史环境注记（2026-11-19 状态），非项目事实 | DECIDE §3.1 |

⚠️ 回写 `:97`/`:179-180` 前**先实测** `_ref/houses/houses_data.json` 里 `shen_a4` 的 `lot` / `wings`（用 Python 读，别照抄旧提示词）：note 字段与 lot 常年不符（shen_a4 note 写 28×28、lot 却是 28×31），**一律以 lot/wings 为准**。若场景线仍在改、lot 尚未稳定，就先只改 DECIDE 那几行，A4 尺寸行留到场景线 commit 后再补——报告里说明。

### 1.2 其他文档

| 文件 | 处理 | 来源 |
|---|---|---|
| `docs/HANDOFF.md:396-405` §5.1 | 「640×360 不能改」标 SUPERSEDED（保留「定案后不再改」原则、换成 1280×720 + canvas_items + scale_mode=0） | DECIDE D7 |
| `docs/PROMPT-art-canvas-h16.md` | 整份标题下加 `> SUPERSEDED：画布高应为 lot_h + 32（TILE 已 16→32），见 DECIDE D6` | DECIDE §3.1 |
| `docs/PROMPT-pseudo3d.md:34-55` | 现状章节加 `> SUPERSEDED：现状已实现 EXTRUDE=32/墙立面/树抬升/进屋不画屋顶，勿照抄` | DECIDE §3.1 |
| `docs/PROMPT-pseudo3d.md:76` | 「单 _draw() 做不到」加 `> SUPERSEDED：方案 B（:81）成立，见 DECIDE D4/C5` | DECIDE §3.1 |
| `docs/PROMPT-overseer.md:46` | `TILE := 16.0` → `32.0`（`house_shape.gd:13`） | DECIDE §3.2 |
| `docs/PROMPT-overseer.md:47-49` | `640×360 / scale_mode=1` → `1280×720 / canvas_items + scale_mode=0` | DECIDE §3.2 |
| `docs/PROMPT-overseer.md:50` | 世界 `1600×900` → `3200×1800` | DECIDE §3.2 |
| `docs/PROMPT-overseer.md:52-55` | 主角/半径/`EXTRUDE:=16` → 按 32px 口径重填（`EXTRUDE:=32`，`world_view.gd:21`；`frame_data.gd:14 CHAR_RADIUS`、`player.gd:12 RADIUS` 实测当前值） | DECIDE §3.2 |
| `docs/REPORT-house-height.md:37-38,66` | P1③ 标记「已裁决：否决 α 0.4，见 DECIDE D2」 | DECIDE §3.2 |
| `docs/HANDOFF-VILLAGE.md:129,132,136,198` | A4 四栋「初版未精调」/ shen_a4 21×19 / zheng_a4 19×9 → 按场景设计线最终口径回填 | 场景设计线 |
| `docs/PROMPT-house-size.md:48,54` | 同上，按场景设计线最终口径回填 | 场景设计线 |
| `scripts/display_manager.gd:5-8` | 注释旧缩放口径 `scale_mode=1 / 640×360 / 2x` → `scale_mode=0 / 1280×720 / 1.5×~3× fractional`（**只改注释，不改逻辑**；视觉机制线不改这个文件，不冲突） | DECIDE §3.2 |

## 2. 纪律

1. **先实测再写**：所有 file:line 可能已因并行线改动而位移；用 grep 定位内容而不是死守行号。
2. **标 SUPERSEDED 用「加注记」而非删正文**：保留原文，顶部加一行引用 `DECIDE-stardew-visual.md` 的对应条目。
3. 不写业务 GDScript（除 `display_manager.gd` 的注释）、不改 `houses_data.json` / `data/frames.json`、不画资产。
4. 不碰场景设计线正在写的 A4 源数据文件和 `_ref/art/A4_2001/*.png`。

## 3. 收工

- 只 `git add` 上表列出的文档与 `scripts/display_manager.gd`。**不要 add 任何其他文件**。
- commit 信息写 `docs: DECIDE 回写 + A4 尺寸同步，house-spec.md 单一写入者`。
- 报告里写清：哪些行按实测值回填（附你读到的 lot/wings）、哪些因场景线未定稿而暂缓、有没有残留旧值 grep 不到的。
