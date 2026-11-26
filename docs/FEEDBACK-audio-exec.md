# 反馈 · L18 音效层（13 个自研合成 WAV + `Aud` 播放器）

> 执行于 2026-11-26，任务书 `docs/PROMPT-audio-exec.md`，基线 HEAD `277f4ea`。
> **结论：13 个 WAV 全部自研合成落地，G1–G8 全绿（`fails=0` / 123 条断言），九套回归无一变动；`Aud` autoload 已挂、接口按 §4 签名齐备，但按任务书 §1「不接线」——`main.gd` 一个字没动。**
> 需转达 4 项（§8）、需人耳复核 1 项（§2.3，本机 headless 是 dummy 音频，我也没有听感）。

---

## §1 产出清单

| 文件 | 类型 | 字节 | 说明 |
|---|---|---|---|
| `tools/gen_audio.py` | 新建 | 546 行 | 合成器；无参数=重写 13 个，`--check`=逐字节比对 |
| `assets/audio/{amb_a1..amb_a5,step_1,step_2,shift_fwd,shift_back,axis,collect,ui_toggle,ending}.wav` | 新建 13 个 | **合计 1050594**（约 1.00 MB） | 22050 Hz / 单声道 / 16-bit PCM |
| `assets/audio/*.wav.import` | 新建 13 个 | — | `compress/mode=0`（**必须是 PCM，见 §7.1**） |
| `scripts/audio.gd` | 新建 | 178 行 | autoload `Aud`：3 条总线 + 8 路 SFX 池 + 1 路底噪 |
| `scripts/audio.gd.uid` | 新建（Godot 自动） | — | 本仓库已跟踪 41 个 `*.gd.uid`，跟随入库 |
| `_mdtest/audio_check.gd` | 新建 | 195 行 | 无头断言 123 条，`AUDIO_OK` |
| `_mdtest/audio_check.gd.uid` | 新建（Godot 自动） | — | 同上 |
| `project.godot` | 修改 +3 行 | — | 只新增 `[autoload]` 段与 `Aud="*res://scripts/audio.gd"` |

**死线（§2.3）逐条确认未碰**：`scripts/main.gd`、`world_view.gd`、`player.gd`、`hud.gd`、`ending_form.gd`、`ending_report.gd`、`ending_store.gd`、`data/**`、`scenes/**`、`assets/village/**`、`docs/**`（仅本文件）。

---

## §2 每音色实测参数

数据来源：`_mdtest/audio_check.gd` 从**已导入的 `AudioStreamWAV.data` 逐样点**解出（不是读我自己的生成器输出），13 个文件约 46 万采样点。

| 文件 | 时长 | 帧数 | 峰值 | RMS | 首尾差 seam | 字节 | 配方（§3 表号） |
|---|---|---|---|---|---|---|---|
| `amb_a1` | 4.000s | 88200 | 0.762 | 0.130 | **0.000000** | 176444 | 风 200–800Hz + 蝉 4kHz 约 6.2 次/秒（表 1） |
| `amb_a2` | 4.000s | 88200 | 0.606 | 0.130 | **0.000000** | 176444 | 风 200–1200Hz + 200Hz 方波强低通人声嗡（表 2） |
| `amb_a3` | 4.000s | 88200 | 0.850 | 0.099 | **0.000000** | 176444 | 1kHz 窄带 + 慢调幅 + 电流杂音（表 3） |
| `amb_a4` | 4.000s | 88200 | 0.833 | 0.130 | **0.000000** | 176444 | 隆隆 60–120Hz + 稀疏 1.5kHz 电视脉冲（表 4） |
| `amb_a5` | 4.000s | 88200 | 0.579 | 0.130 | **0.000000** | 176444 | 干风声 + 50Hz 及二次谐波（表 5） |
| `step_1` | 0.080s | 1764 | 0.850 | 0.206 | 0.0093 | 3572 | 800–2500Hz 中心（表 6） |
| `step_2` | 0.080s | 1764 | 0.850 | 0.174 | 0.0027 | 3572 | 中心 ×1.25 + 5ms 延迟（表 7） |
| `shift_fwd` | 0.300s | 6615 | 0.850 | 0.126 | 0.000000 | 13274 | 220→110Hz + 噪声扫频（表 8） |
| `shift_back` | 0.300s | 6615 | 0.850 | 0.126 | 0.000000 | 13274 | **= 表 8 波形倒放**（表 9，不重新合成） |
| `axis` | 0.200s | 4410 | 0.850 | 0.192 | 0.000000 | 8864 | 60Hz + 200Hz 短脉冲（表 10） |
| `collect` | 0.250s | 5513 | 0.850 | 0.271 | 0.000000 | 11070 | 523/659/784Hz 三音琶音，每音 60ms，+3Hz 失谐（表 11） |
| `ui_toggle` | 0.100s | 2205 | 0.850 | 0.079 | 0.000000 | 4454 | 1ms 冲击 + 8ms 衰减 click（表 12） |
| `ending` | 2.500s | 55125 | 0.850 | 0.301 | 0.000000 | 110294 | 55Hz+82.5Hz 五度 drone 缓慢上行，尾 0.5s 淡出（表 13） |

- 帧数与 §3 时长**逐条精确对齐**（88200 = 4.000×22050 等），断言里写死为 `EXPECT_FRAMES`，多一帧少一帧都红。
- 5 条循环音 `loop_mode == LOOP_FORWARD`、`loop_begin=0`、`loop_end=frames` 也在断言里查了 —— 否则「首尾差 0」也可能只是「播一遍就停」。

### 2.1 配方落地的旁证（频谱抽样，肉眼不可见时用这个代替）

对每条信号做 FFT 取主峰：`amb_a1` 3992/3998Hz（蝉）+ 348Hz（风）· `amb_a2` 197/200Hz（人声嗡）· `amb_a3` 823–1030Hz（底噪）+ 1455Hz（杂音）· `amb_a4` 71/117Hz（隆隆）· `amb_a5` 50Hz · `axis` 60/200Hz · `collect` 660/784Hz · `ending` 57Hz · `step_1` 1438Hz · `step_2` 2525Hz（≈1438×1.25×1.4，中心上移方向正确）· `shift_back` 与 `shift_fwd` 谱完全一致（确认是倒放而不是另合成一条）。

### 2.2 响度口径（一处偏离「按峰值归一」的设计选择，必须报备）

§2.1 只规定「峰值 ≤ 0.9」，没规定各条之间的相对响度。若全部按峰值归一到 0.85，稀疏瞬态会带偏：`amb_a3` 的 RMS 只有 0.040，与其它帧同总线播出时会「一进 1976 年声音就没了」。所以：

- **一次性音效**（step/shift/axis/collect/ui_toggle/ending，9 条）：按 `peak` 归一到 0.85。
- **5 条循环底噪**：先按 `RMS` 对齐到 `AMBIENT_RMS=0.13`，再用 0.85 封顶（`amb_a3` 因此峰封顶后 RMS 落到 0.099，是这一条的特例）。实测 4 条恰好 0.130、a3 0.099 ⇒ 换帧时响度连续。

### 2.3 我听不出好坏（§8 第 1 问的正面回答）

headless 下 Godot 是 dummy 音频驱动，**没有任何一条被真正播出过**；我也没有听觉。能给的只是上面那些数值与频谱证据：配方按表落地、格式合法、不削波、循环无缝。**「像不像 1926 年的蝉声」「2019 年那种电视雪花味对不对」必须人耳复核** —— 这是本线唯一无法自证的验收形式。

---

## §3 验收 G1–G8 逐条

| # | 断言 | 实测 | 判定 |
|---|---|---|---|
| G1 | 13 个 wav 存在且 `load()` 成 `AudioStreamWAV` | 13/13，`ResourceLoader.exists` 全 true，`load()` 类型全对 | ✅ |
| G2 | 22050 / 16-bit / 单声道 / 时长 > 0 | `mix_rate=22050`、`format=1`(FORMAT_16_BITS)、`stereo=false`、帧数=§2 表（全部 > 0） | ✅ |
| G3 | 峰值 ≤ 0.9 | 全部 ≤ 0.850（最高 0.850，最低 0.579） | ✅ |
| G4 | 5 条循环首尾差 < 0.02 | 全部 `0.000000`（判据 0.02） | ✅ |
| G5 | `python tools/gen_audio.py --check` 返 0 | `CHECK_OK: 13 files byte-identical to freshly synthesised output`，exit=0 | ✅ |
| G6 | `--quit-after 60` 无 SCRIPT ERROR / Parse Error，`ready_check` 报 13 streams + 3 bus | 打印 `AUDIO_READY streams=13 buses=Master,Ambient,SFX ambient= missing=`；stderr 只有既有环境噪音 | ✅ |
| G7 | `Aud.play("collect")` / `Aud.ambient("a3_1976")` 不报错 | 不只是「不报错」：断言检查了某个池播放器 `stream != null`、`ready_check().ambient == "a3_1976"`、同名重复无副作用、`stop_ambient()` 清空 | ✅ |
| G8 | 13 个 `.wav.import` 全部提交 | 13 个已精确 `git add`（见 §5） | ✅ |

`_mdtest/audio_check.gd` 输出：`PASS` 123 条 / `FAIL` 0 条 / `AUDIO_CHECK_DONE fails=0` / `AUDIO_OK`。

`Aud` 侧的一次性自检行（每次进游戏都会打，便于现场排错）：

```
AUDIO_READY streams=13 buses=Master,Ambient,SFX ambient= missing=
```

`missing=` 后面会列出任何加载失败的 key —— 路径写错时它不再沉默降级。

---

## §4 剩余问题

1. **未接线**（按 §1 刻意如此）。`main.gd` 里目前没有一行 `Aud.` 调用 ⇒ 进游戏是静的。接线清单建议（L18b 用）：`play("step_1"/"step_2")` 交替踩步、`play("shift_fwd"/"shift_back")` 时间轴前后跳、`play("collect")` 收集证物、`play("axis")` 切轴、`play("ui_toggle")` 表单开关、`play("ending")` 进结局、`ambient("a1_1926" … "a5_2026")` 随帧切换。
2. **底噪 key 用的是帧 id**（`a1_1926`…`a5_2026`），而 SFX 用的是音色名（`collect`…）。这是任务书 §4 `ambient(frame_id)` 的签名决定的，接线时注意别传成 `amb_a1`（传错会在 `ready_check().missing` 里显形、并只打一条 `push_error`）。
3. **时长固定 4.000s**，没有做「每帧不同长度」。若以后要更长的环境循环，改 `LOOP_SECONDS` 会让全部 5 条同时变长（约 44KB/秒/条）。
4. **`.import` 的 `compress/mode` 是踩过坑后手改的**（§7.1）。若将来有人在编辑器里点「重新导入」并接受默认值，会退回 QOA 有损且帧数减半 —— 目前没有自动化守卫拦这个，`audio_check` 的 G2（`format=1` + 精确帧数）能在下次跑时抓住。
5. 退出时多一条 `WARNING: 4 ObjectDB instances were leaked at exit` + `ERROR: 2 resources still in use at exit`（autoload 持有的 `AudioStreamWAV` 在 SceneTree 结束时仍被引用）。**不影响运行、不影响断言**，属 autoload 常驻资源的固有噪声；若以后要求日志绝对干净，得在 `_notification(NOTIFICATION_WM_CLOSE_REQUEST)` 里 `stream = null`。

---

## §5 提交范围（`git add` 只加白名单，未 push）

加进 index 的（精确路径，共 33 个文件）：

1. `tools/gen_audio.py`
2. `assets/audio/` 下 13 个 `.wav` + 13 个 `.wav.import`
3. `scripts/audio.gd`、`scripts/audio.gd.uid`
4. `_mdtest/audio_check.gd`、`_mdtest/audio_check.gd.uid`
5. `project.godot`（+3 行：`[autoload]` / 空行 / `Aud="*res://scripts/audio.gd"`）
6. `docs/FEEDBACK-audio-exec.md`（本文件）

**没加、也没动**的：`scripts/main.gd` 等全部死线文件、`data/**`、`scenes/**`、`assets/village/**`；工作区原有别人的脏文件（`_ref/art/A1..A3/*.png` 的 `M`、`美术资产/**` 的 `D`、`lab/_*` 未跟踪）原样留着，**没有 `git add -A`**。

---

## §6 回归（九套，跑在 HEAD `277f4ea` + 本线改动）

| 脚本 | 结果 |
|---|---|
| `greybox_check` | `solids=238/299/379/812/897`、`hotspots=10/11/13/12/8`、`REACH_MAP.standable=15105`、`to_a5=12498`、`WALL_BLOCKED=false`、`REACH_OK=true`、`HOTSPOTS_OK=true` |
| `camera_check` | `fails=0` |
| `hud_layout_check` | `HUD_CHECK_DONE fails=0` |
| `sort_check` | `fails=0` |
| `asset_draw_check` | `fails=0` |
| `evidence_archive_check` | `fails=0` · `EVIDENCE_OK` |
| `display_check` | 五项不变（`CONTENT_SCALE_MODE=1` / `ASPECT=1` / `SIZE=(1280,720)` / 默认纹理过滤=0 / `STRETCH_SCALE_MODE=0`） |
| `tile_wire_check` | `fails=0 gaps=0 checks=16` |
| `phasing_check` | `fails=0 warns=0` |

与基线的唯一区别：**现在每个 `-s` 跑测试都会额外打印一行 `AUDIO_READY …`**（因为 autoload 在 `SceneTree` 起来时就会 `_ready()`）。无断言依赖它，不构成回归。

---

## §7 三个坑（后来人直接抄结论）

### 7.1 ⚠️ Godot 4.7 的 wav 导入器默认是 QOA 有损（`compress/mode=2`）

第一次导入后 `audio_check` 一次性红了 44 条：`format=3`（QOA 而非 16-bit PCM）、帧数只有应有值的 1/5（17644 而不是 88200）、峰值读到 `1.000`。**这不是生成器的问题，是导入器默认值**，而且：
- QOA 是有损压缩 —— 与「Web 导出的 WAV(PCM)」要求直接冲突；
- 帧数被压缩字节数带偏 ⇒ 所有时长断言全错。

修法：13 个 `.wav.import` 里 `compress/mode=2` → `compress/mode=0`，再跑一次 `--import`。其余参数确认过：`force/max_rate=false`（不重采样）、`edit/trim=false`、`edit/normalize=false`、`edit/loop_mode=0`。**循环不写在 `.import` 里**，而在 `audio.gd` 加载时设 `loop_mode=LOOP_FORWARD`，这样重新导入不会把循环弄丢。

### 7.2 Godot 4.7 的 `PackedByteArray` 没有 `to_int16_array()`

只有 `to_int32_array()` / `to_int64_array()` / `to_float32_array()` / `to_float64_array()`。第一版用它，脚本在 **parse 阶段**就 `Cannot find member "to_int16_array"` 起不来（连 `fails` 都打不出来）。改用 `data.decode_s16(i*2)` 逐样点扫，13 文件 46 万点，1s 内跑完。除法统一 `/32768.0`，与生成器 `_stats()` 同口径。

### 7.3 循环接缝不是「淡入淡出」能解决的，要做接缝搜索

`_make_loop(src, n)` 先在 `src[n : n+hi+1]` 里搜**与 `src[n-1]` 差异最小的起点 s**，再拿 `tail=src[s+n : s+n+fade]` 跟头部交叉淡化 —— 这样 `out[0]` 恰好等于 `out[n-1]` 的下一个采样，首尾差天然为 0（实测 6 位小数全 0）。单纯两端 fade 出来的是「声音凹一下」，且首尾差仍在 0.1 量级。
噪声源用 `random.Random(SEED_BASE+idx).randbytes(n)`（Mersenne Twister，跨 Python 版本稳定），**不用 `np.random`** —— 后者不保证版本间序列一致，会直接打破 `--check` 的逐字节可复现。

---

## §8 任务书 §8 要求的四项报告

1. **哪个音色最不像**：我没法听（§2.3）。若只能按配方推断风险点，我会说 **`amb_a2`（1951 的人声嗡）** —— 它是唯一靠「方波过强低通」模拟人声的，谱上看确实塌在 197/200Hz，但方波低通在听感上容易像「嗡鸣的机器」而不是「远处有人说话」；其次是 **`collect`**（三音琶音每音只有 60ms，短到可能听不出音高，只留下一声「叮」）。
2. **`[autoload]` 加了哪一行**：`project.godot:20`
   ```
   Aud="*res://scripts/audio.gd"
   ```
   连同段头 `[autoload]` 共 3 行（含一个空行），插入在 `[application]` 的 `config/icon` 之后、`[display]` 之前。星号 = 作为单例节点而不是 Resource 加载，`root.get_node_or_null("Aud")` 可直取。
3. **13 个文件合计字节**：**1050594**（约 1.00 MiB）。其中 5 条 4s 底噪占 882220（84%），`ending` 110294，其余 7 条 SFX 合计 58080。Web 导出这 1MB 会进 `.pck`，不算大；若嫌底噪占地方，把 `LOOP_SECONDS` 从 4.0 降到 2.0 能省 44 万字节（但 2 秒的蝉声循环容易被听出周期）。
4. **建议砍哪几条**：如果只留最小集，我会砍 **`step_2`**（`step_1` 变调即可，或干脆只用一条踩步声）和 **`ui_toggle`**（0.10s 的 click 在 UI 里最容易被「不响也行」掉），再考虑 **`axis`**（切轴本身有画面反馈，音效是加强项）。**不建议砍**：`shift_fwd`/`shift_back`（时间跳转是本作的核心动作，且 `shift_back` 是免费的 —— 倒放已有波形、0 成本）、`collect`（收集证物是正反馈锚点）、`ending`（结局唯一的听觉记号）。5 条底噪与 5 个时间帧一一对应，砍任何一条都会让那一帧「静音」，**不建议砍**。