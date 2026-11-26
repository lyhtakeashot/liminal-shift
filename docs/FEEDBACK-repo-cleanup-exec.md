# FEEDBACK · 仓库整理执行（`docs/PROMPT-repo-cleanup-exec.md`）

执行日期：2026-11-26
分支：`main`　HEAD：`f1804f4`　未 push（任务书 §0-3）

---

## §1 结论先给（C1–C5 判定）

| 项 | 要求 | 实测 | 判定 |
|---|---|---|---|
| **C1** | 未跟踪文件 < 30 | **269**（写完本反馈后 270） | ❌ **不可达**（见 §4-D1，任务书自相矛盾） |
| **C2** | `status --short` < 30 行且只剩 12 个 `M` | **57 行**（12 `M` + 45 `??`；写完本反馈后 58 行） | ⚠️ **部分达成**：`M` 正好 12 个且全是 §3-6 点名的那 12 个；45 行 `??` 全落在任务书**没授权动**的目录里 |
| **C3** | `_archive/` 文件数 = 搬走前未跟踪数（±5）且 `git ls-files lab` 仍 117 | `_archive` **1101**（对账见 §2.6，一分不差）；`git ls-files lab` = **117** | ⚠️ 前半字面差 198（差额 100% 可对账，不是丢文件）；后半 **✅ 逐位相同** |
| **C4** | `git ls-files _archive` 为空 | **0 行**，`git check-ignore -v` → `.gitignore:67:_archive/` | ✅ |
| **C5** | 九套回归全绿、数字与基线逐位相同 | 九套全绿，`solids=238/299/379/812/897`、`hotspots=10/11/13/12/8` 逐位相同 | ✅ |

一句话：**能做的都做完了、没有丢文件、没有搬到运行时要用的东西**；C1/C2 的字面目标在任务书自己的约束下数学上不可达，请 lead 裁定（§4-D1）。

---

## §2 搬了什么（逐条对账）

### 2.1 `_archive/` 结构（实际落盘）

```
_archive/
  lab-2026-11-26/     914 个   # lab/ 的未跟踪文件 904 + __pycache__ 10
  docs-2026-11-26/      1 个   # FEEDBACK-evidence-archive-exec.md
  mdtest-assets/      140 个   # _mdtest 的未跟踪截图/预览
  美术资产-2026-11-26/  34 个   # 不是搬来的，是从 HEAD blob 还原的（见 2.4）
  scratch/             12 个   # move_untracked.py / salvage_deleted.py / reg/ 十个回归日志
合计 1101 个文件（全部未跟踪，`git ls-files _archive` = 0）
```

### 2.2 `lab/` 未跟踪文件 → `_archive/lab-2026-11-26/`

- 搬走 **904** 个（`git ls-files --others` 里 lab 的全部）。
- 另搬 **10** 个 `lab/__pycache__/*.pyc`（已被 `.gitignore` 忽略，不进 `--others`，但留着就是垃圾）。
- `lab/` 下 **48 个空目录**搬后被清掉；`lab/` 目录本身保留（里面有 117 个已跟踪溯源脚本，一个没动 —— C3 后半）。
- 逐条 os.replace，**一个文件都没删**；搬完 `git status` 里 lab 的 `D` 记录 **0 条**（证明没搬错已跟踪文件）。

### 2.3 `_mdtest/` 未跟踪文件 → `_archive/mdtest-assets/`

| 来源 | 数量 | 说明 |
|---|---|---|
| `_mdtest/assets/` | 68 | `asset_shot.gd` / `tile_wire_check.gd` / `scene_bake_check.gd` 的实拍 PNG + `.import` |
| `_mdtest/roofshoot/` | 30 | 屋顶实拍 |
| `_mdtest/house_art_preview/` | 20 | `house_art_check.gd` 的 C5 预览 |
| `_mdtest/greybox/` | 22 | 被 `.gitignore` 忽略，实测存在 → 一并归档 |

**搬完补回两个空目录** `_mdtest/greybox/`、`_mdtest/roofshoot/`（`_shot_final.gd:40` / `_shot_road.gd:31` / `_shot_p3d.gd:38` 直接 `save_png` 到这两个目录，**自己不 make_dir**，目录没了会静默写不出来）。空目录不影响 git status（git 不跟踪空目录）。

`_mdtest` 里剩下 9 个未跟踪（7 个 `*_check.gd.uid` + `_evidence_test.json` 等）**没动** —— 它们是 Godot 4.4+ 的 UID sidecar / 测试账本，属 §3 未点名目录。

### 2.4 根目录 7 个散落 txt（任务书 §3-3 授权直接删）

`lab_out_hud.txt`、`lab_out_ad.txt`、`lab_out_cam.txt`、`lab_out_disp.txt`、`lab_out_greybox.txt`、`lab_frames_diff.txt`、`_tmp_version.txt` —— 逐个 `git ls-files <path>` 确认**未跟踪**后才 `Remove-Item`。

### 2.5 `docs/` 未跟踪 16 个：搬 1 留 15

| 文件 | 处置 | 理由 |
|---|---|---|
| `FEEDBACK-evidence-archive-exec.md` | **搬** `_archive/docs-2026-11-26/` | `git grep "FEEDBACK-evidence-archive-exec"` → **exit=1 零引用** ⇒ 线已收（注意：只 grep `evidence-archive-exec` 会命中 **`docs/PROMPT-evidence-archive-exec.md`** 这个**别的文件**，别被骗） |
| `FEEDBACK-a4-map-build-blockers.md` | 留 | 被 `docs/FEEDBACK-a4-houses-status.md` 引用 |
| `FEEDBACK-a4-map-build-exec.md` | 留 | 被 `docs/待解决事项.md` 引用 |
| `FEEDBACK-a5-map-build-exec.md` | 留 | 被 `docs/FEEDBACK-a5-layout-v5.md` 引用 |
| `FEEDBACK-world-rebuild-exec.md` | 留 | 被 `docs/PROMPT-l11-world-rebuild-exec.md`、`docs/RESUME-2026-11-25.md` 引用 |
| `HANDOFF-ART-A1A3.md` | 留 | 美术交接文档，无收线标记 |
| `HANDOVER-evidence-model-planner.md` | 留 | 证据模型交接文档，无收线标记 |
| `ART-GAP-A4A5.csv.import` | 留 | 对应 `ART-GAP-A4A5.csv` **已跟踪**，删 sidecar 会让 Godot 重新生成 |
| `docs/_mapfix_shots/*.png.import`（8） | 留 | 同理：对应 PNG 全部已跟踪 |

已完成「线已收」判定所需的交叉引用实测（`git grep` 逐个查文件名）—— 这是唯一一个没有引用的，其余 15 个都有在办的活指着。

### 2.6 `美术资产/` 34 个已删文件（§3-5 通过后提交删除）

1. **先查是谁删的**：34 个 `D` 文件的 `Test-Path` **全为 False** —— 它们在盘上早就没了（不是本次删的），本次只是把这个事实提交进库。
2. **§3-5 四道校验全过**：
   - `git grep "老槐树|茅坑|小桌|灶台柴|灶缸柴|Sprite-*" -- scripts scenes tools data *.tres *.tscn *.gd *.json` → 命中**全是道具名/节点名**（`scenes/world/world_a1_1926.tscn:781 [node name="Furn_茅坑_99"...]`、`data/frames.json` 的老槐文案、`_ref/houses/houses_data.json` 的 `"name":"茅坑"`），**没有任何路径引用**；
   - `git grep "美术资产" -- _ref/art/_assets_a1a3/` → 无命中（manifest 没有指回原图）；
   - `git grep "res://美术资产|美术资产/"` → 只有 `scripts/player.gd:39 const HERO_SHEET := "res://美术资产/主角/Sprite-主角-Sheet.png"` 及其 `.import`；
   - 对 34 个文件名逐个 grep `.import` / asset 引用 → **exit=1 零命中**。
3. **顺手救了一把底**：提交删除前，用 `git show HEAD:<path>` 把 34 个文件的字节还原进 `_archive/美术资产-2026-11-26/`（`_archive/scratch/salvage_deleted.py`）。理由：`lab/_cls_gen_a.py:20 SRC = os.path.join(ROOT, "美术资产", "家具")` 这类溯源脚本要重跑时得有源图 —— 它现在本来就跑不了（源图早被人删了），但归档里有就能救回来。

### 2.7 两个提交（未 push）

```
f1804f4 chore: 删除已被 _ref/art manifest 取代的家具原图（主角贴图保留）   34 项
27dc543 chore: 归档区 _archive/ 不进版本库                                 1 项（.gitignore）
8b90040 docs: repo-cleanup task book corrected ...（任务书，不是你写的那版）
```

`git show --name-status f1804f4` 恰好 34 行，**名单里没有「主角」**。

### 2.8 `.gitignore` 追加

只追加两行（`# 归档区：不进版本库` + `_archive/`），**没碰 `lab/`**。

⚠️ 实测：`.gitignore` 大部分是 UTF-8，但第 62 行 `build/` 上方那段注释是 **GBK**。所以用的是
`[System.IO.File]::AppendAllText($p, "`n# 归档区：不进版本库`n_archive/`n", (New-Object System.Text.UTF8Encoding($false)))`，
逐行校验旧规则未被破坏：`.gitignore:61:.evidence_archive.json`、`.gitignore:64:build/` 都还在。

---

## §3 证据

### 3.1 每一步的 status 前后数字（任务书 §0-4 要求）

| 步骤 | `git status --short` 行数 |
|---|---|
| 搬运前 | **1008**（12 `M` / 34 `D` / 962 `??`） |
| 建 `_archive/` + `.gitignore` | 1008 |
| 搬 lab + _mdtest（1054 个文件） | **100** |
| 删根目录 7 个 txt | **93** |
| 搬 docs 1 个 | **92** |
| 提交 `.gitignore` | 92 |
| 提交 34 个 `D` | **57**（当前） |

### 3.2 C1–C5 原始输出

```
== C1 ==
269                      # (git ls-files --others --exclude-standard | Measure-Object -Line).Lines

== C2 ==
57                       # (git status --short | Measure-Object -Line).Lines
Count Name
   12 M
   45 ??

== C3a ==
117                      # (git ls-files lab | Measure-Object -Line).Lines

== C3b ==
1101                     # (Get-ChildItem _archive -Recurse -File -Force | Measure-Object).Count

== C4 ==
0                        # (git ls-files _archive | Measure-Object -Line).Lines
.gitignore:67:_archive/  _archive/lab-2026-11-26
```

**C3 的对账（1101 vs 1299 差 198，不是丢东西）**

```
搬走前未跟踪 1299 = 归档 1023 + 按 §3-3 删除 7 + 留在原地(未授权目录) 269      ← 严格相等
归档 1101        = 未跟踪 1023 + gitignore 忽略项 32 + HEAD 还原 34 + scratch 12
                    其中 32 = lab/__pycache__ 10 + _mdtest/greybox 22（都不在 --others 里）
```

剩下的 269 个未跟踪文件分布（全部是任务书**没授权我动**的目录）：

```
146 美术资产   （地皮/家具/房屋/树 新素材包，§3 只授权删 34 个已删的旧图）
 93 assets     （audio/voice TTS 成品 + audio_raw/tts + _legacy_16px 的 .import，§3 未点名）
 15 docs       （见 §2.5：4 个被在办文档引用的 FEEDBACK + 2 个交接文档 + 9 个 .import）
  9 _mdtest    （7 个 *_check.gd.uid + _evidence_test.json 等，§3 未点名）
  4 scripts    （.gd.uid sidecar）
  2 tools      （.gd.uid sidecar）
```

### 3.3 九套回归原文（`_archive/scratch/reg/*.log`）

```
greybox   FRAME[0] a1_1926 solids=238 hotspots=10
          FRAME[1] a2_1951 solids=299 hotspots=11
          FRAME[2] a3_1976 solids=379 hotspots=13
          FRAME[3] a4_2001 solids=812 hotspots=12
          FRAME[4] a5_2026 solids=897 hotspots=8
          REACH_MAP={ "standable": 15101, "to_a5": 12536, "blocked_at_step": [145, 155, 2159, 106],
                      "band_total": 298, "band_full": 298, "band_ratio": "100%", "ratio": "83%" }
          UNEXPLAINED_BLOCKS=0
          REACH_OK=true　　WALL_STOP_Y=880.0　WALL_BLOCKED=true　TIME_FWD_REACHED=[1,2,3,4]
camera           CAMERA_CHECK_DONE fails=0
hud_layout       HUD_SIZE=(1280.0, 720.0) / HUD_CHECK_DONE fails=0
sort             SORT_CHECK_DONE fails=0
asset_draw       ASSET_DRAW_CHECK_DONE fails=0
evidence_archive EVIDENCE_CHECK_DONE fails=0
display          CONTENT_SCALE_MODE=1 (期望 1) / _ASPECT=1 (期望 1) / _SIZE=(1280,720) (期望 (1280,720))
                 默认纹理过滤=0 (期望 0=Nearest) / STRETCH_SCALE_MODE=0 (期望 0=fractional)
tile_wire        TILE_WIRE_CHECK_DONE fails=0 gaps=0 checks=16          # headless 下像素段跳过，正常
phasing          PHASING_CHECK_DONE fails=0 warns=0
```

- `solids=238/299/379/812/897`、`hotspots=10/11/13/12/8` 与 `docs/PROMPT-overseer.md` 基线**逐位相同**。
- `display_check.gd` **本身不打印 `fails=`**（脚本只 print 5 个值后 quit），所以它的「绿」= 5 个值逐条与脚本内「期望」一致 —— 已逐条核对相符，不是漏跑。
- `tile_wire` 的 `gaps=0 checks=16` 正是任务书 §4 说的 headless 正常态。

**关于 `REACH_MAP` 的 `to_a5` / `blocked_at_step`**：任务书只钉了 solids 与 hotspots（均逐位一致）。`to_a5=12536`、`blocked_at_step=[145,155,2159,106]` 与我 2026-11-26 16:25 记的记忆基线（12554 / [145,155,2150,97]）不同 —— 但本次只搬了 `lab/`、`_mdtest/` 产物、`docs/` 与根目录 txt，**九个检查脚本对这三处的引用全部是「写」不是「读」**（已逐个 grep 确认：`_evidence_shot.gd:19` / `greybox_shot.gd:14` / `ending_outro_check.gd:135` 都自己 `make_dir_recursive`；`ending_outro_check.gd:24-26` 的 `SHOT_*` 常量是 `_shot()` 的**输出**路径，读不到也不影响断言）。差异来自这期间别人合并的提交（音频/A5 美术），不是本次改动造成 —— 若要，请 lead 用 `git stash` 前的 HEAD 交叉复跑确认。

### 3.4 没搬到运行时要用的东西 —— 反向验证

- `git ls-files lab` = **117**（一个溯源脚本都没搬走）。
- 搬运脚本逐条 `os.replace`，搬后 `git status` 里 `lab/` 的 `D` 记录 = **0**。
- 九个检查脚本引用的 `res://lab/...` / `res://_mdtest/...` 逐条查过，**全是输出目录**，且写之前自己 `make_dir_recursive`（或已把空目录补回，见 §2.3）。

---

## §4 拿不准的（不自己决定）

### D1 · C1 与 §3 处置表互相矛盾（**需要 lead 裁定**）

- C1 要「未跟踪 < 30」，但 §3 的处置表只授权动 `lab/`、根目录 7 个 txt、`美术资产/` 的 34 个已删文件、`docs/` 里「线已收」的那几个。
- 剩下 269 个未跟踪文件全在**没授权的目录**（`美术资产/` 146、`assets/` 93、`docs/` 15、`_mdtest/` 9、`scripts+tools` 6）。
- ⇒ **C1 字面不可达**，除非 lead 补授权。我的建议（只报不动）：
  - `美术资产/` 146（地皮/家具/房屋/树 新素材包）→ 这些**看起来是该进库的新素材**，不是垃圾，请美术线确认后 `git add`；
  - `assets/audio/voice/*.wav` + `.import` 是 TTS 成品、`tools/process_voice.py` 在用 → 同样像该进库；
  - `scripts/*.gd.uid`、`tools/*.gd.uid`、`_mdtest/*_check.gd.uid` 共 13 个 → Godot 4.4+ 的 UID sidecar，**要么全进库要么全 ignore**，不能半进半不进（不然每次开编辑器都脏）；
  - `docs/*.import` 9 个 → 对应 PNG 已跟踪，sidecar 该一起进库。

### D2 · C2「只剩 12 个 `M`」与 C1 是同一件事

`status` 的 45 行 `??` 就是 D1 里那 269 个文件的目录级折叠（146+93+15+9+4+2 个目录行 → 45 行）。要它降到 0，必须先决定 D1 那四类进不进库。

### D3 · `docs/` < 90 也不可达

`docs/` 现 **162** 个文件（已跟踪 **139**，未跟踪 15+8 个 sidecar）。§0-1 明文「已跟踪文件一个都不许移动或删除」，而任务书给的理由是「过期任务书/反馈进 `_archive/`」—— 但**过期的任务书/反馈绝大多数是已跟踪的**（`PROMPT-*` 全部已跟踪）。⇒ 按现有约束，`docs/` 最低只能到 147（162 − 15 未跟踪），到不了 90。请 lead 明确：**是否授权我搬走已跟踪的过期 `PROMPT-*` / `FEEDBACK-*`**（那需要 `git mv` + 提交，与 §0-1 冲突，必须你点头）。

### D4 · `美术资产/` 34 个删除已提交，但「该不该删」我只能验到「无引用」

四道 grep 零路径引用 = 「删了不会坏」。但 34 张图是 `_ref/art/_assets_a1a3/` 那批 manifest 的**源素材**，删掉后 `lab/_cls_gen_a.py` 这类生成器再也跑不了（除非用我归档的副本）。若将来还要重出素材，`_archive/美术资产-2026-11-26/` 里是完整 34 个字节。要不要把「素材源图」改成入库、只删中间产物 —— 这是内容决策，我不定。

### D5 · 新规矩已按任务书 §2-2 执行，但要不要写进守则由你定

任务书要求把「一次性草稿/截图/备份一律放 `_archive/scratch/`，不再往 `lab/` 里丢；`lab/` 只放与 `data/` 一起提交的溯源脚本」写进反馈、由 lead 同步到守则。**已在 §5 原样登记**。我的执行体感：这条规矩很值 —— 本次 904 个 `lab/` 垃圾里，绝大多数就是「跑一次的调参脚本 + 截图」，一条 `_archive/scratch/` 规则能挡住 90% 的未来脏乱。

### D6 · 两个「我顺手做的事」请复核

1. 把 34 个已删文件的 HEAD blob 还原进归档（§2.6-3）—— 任务书没要求，我判断「移动不删除」的精神适用于这里。
2. 把 `_mdtest/greybox/`、`_mdtest/roofshoot/` 两个空目录补回（§2.3）—— 任务书要求「搬空」，但 `_shot_*.gd` 靠目录存在才能写图。

两件都不影响 `git status`（归档区已 ignore、空目录 git 不跟踪），但确实超出字面授权，登记备查。

---

## §5 新规矩（任务书 §2-2 要求写进反馈）

> 一次性草稿、截图、备份一律放 `_archive/scratch/`，**不再往 `lab/` 里丢**；`lab/` 只放「和 `data/` 一起提交的溯源脚本」。

---

## §6 现在的仓库长什么样

```
git status --short         58 行（12 M + 45 ?? + 本文件）
git ls-files --others      270（269 全在未授权目录，见 §4-D1；+1 = 本文件）
git ls-files lab           117（一个没动）
git ls-files _archive      0  （归档区确实在库外）
_archive/                  1101 个文件，随时可取回
分支 main，HEAD f1804f4，未 push，无 git add -A，无 git restore
```

> 本文件**没有提交**：任务书 §5「提交」只授权 `.gitignore` 与 `美术资产/` 的删除两项，我按字面执行。请你 `git add docs/FEEDBACK-repo-cleanup-exec.md` 后自行提交（本仓惯例是反馈文档入库）。