# 工作区整理执行任务书（2026-11-26）

> 依据：项目总策划 2026-11-26 18:12 第 8 条「工作区文件夹简直是乱的不行，怪不得一直出现调用错和误读的现象，先整理文件，把已经用不上的文件全部归档」。
> 实测现状：`git status --short` 共 **1008 行**（`M` 12 / `D` 34 / `??` 962），其中 `lab/`（草稿脚本 + 截图 + 备份）占 820 个未跟踪文件。
> 本线**只搬文件、不改任何 `.gd` 逻辑、不动 `data/`、不动 `assets/` 里已入库的贴图**。

---

## §0 铁律（违反即作废）

1. **只处理未跟踪文件**。判断依据永远是 `git ls-files --others --exclude-standard`，**已跟踪文件一个都不许移动或删除**（例外只有 §3 第 5 条点名的 `美术资产/`）。
2. **移动，不删除**（例外只有 §3 第 3 条的 7 个散落 txt）。归档区统一是 `_archive/`，**归档区自己不进 git**。
3. **绝不 `git add -A`、绝不 `git restore`（沙箱会拦）、绝不 push**。
4. 每一步搬完都要打印 `git status --short | Measure-Object -Line`，把数字写进反馈。
5. **搬完必须跑九套回归**，全部与 `docs/PROMPT-overseer.md` 的基线一致（`fails=0`，`greybox` 的 `solids=238/299/379/812/897`、`hotspots=10/11/13/12/8`），证明没有搬到运行时要用的东西。

---

## §1 目标

| 指标 | 现状 | 目标 |
|---|---|---|
| `git status --short` 行数 | 1008 | **< 30** |
| 仓库根目录散落文件 | 7 个 `lab_out_*.txt` 等 | 0 |
| `lab/` 里的**未跟踪**文件数 | ~820 | **0**（已跟踪的 117 个溯源脚本**必须原样留着**） |
| `docs/` 文件数 | 161 | < 90（过期任务书/反馈进 `_archive/`） |

---

## §2 新建的两样东西

1. `_archive/` 目录（先建好，里面按下面结构放）：

```
_archive/
  lab-2026-11-26/      # 旧草稿脚本、截图、备份
  docs-2026-11-26/     # 已收线的任务书与反馈
  mdtest-assets/       # _mdtest 下未跟踪的截图与预览图
```

2. `.gitignore` **只追加 `_archive/` 一条**（**不要**把 `lab/` 加进去——`lab/` 里有 117 个已跟踪的溯源脚本，而且以后跑数据线还要往里写可提交的脚本）。

```powershell
Add-Content .gitignore "`n# 归档区：不进版本库`n_archive/"
```

追加后用 `git check-ignore -v _archive/x` 验证生效，并确认 `.evidence_archive.json`（第 61 行）与 `build/`（第 64 行）两条**没有被破坏**。

**新规矩（写进反馈，lead 会同步到守则）**：一次性草稿、截图、备份一律放 `_archive/scratch/`，**不再往 `lab/` 里丢**；`lab/` 只放「和 `data/` 一起提交的溯源脚本」。

---

## §3 处置表

**1. `lab/` 的未跟踪文件 → `_archive/lab-2026-11-26/`**

⚠️ **先读这条**：`lab/` **不是全未跟踪**！实测 `git ls-files lab` 有 **117 个已跟踪文件**（55 个 `.py` 溯源脚本如 `_a13_road_v3.py`、`_a4_build.py`，7 个 `.json` 基线，21 个 `.png` 证据图，17 个 `.import`，6 个 `.gd`，4 个 `.md`，7 个 `.txt`）。**这些是数据产物的溯源，一个都不许移动或删除。**

所以做法是：**只搬 `lab/` 下的未跟踪文件**，已跟踪的原样不动。

```powershell
# 列出 lab/ 下未跟踪的文件（这就是要搬的名单）
git ls-files --others --exclude-standard -- lab/
```

典型要搬的：`_probe_*.py`/`_probe_*.gd`、`_gen_*.py`、`_inspect_*.py`、`_verify_*.py`、`_qa_*.py`、`maps/`、`audio_demo/`、`evidence_shot/`、`render_fix_shot/`、`_backup_16px_a4a5/`、`_backup_artline/`、`_l19_appdata/`、`_push_api_tmp/`、`__pycache__/`、`lab_out_*.txt`。

搬完必须验证：`git ls-files lab | Measure-Object -Line` 仍然是 **117**。

**搬运规则**：`git ls-files --others --exclude-standard -- <目录>` 逐条搬，**不要 `Move-Item lab _archive/` 整个目录**（那样会把 117 个已跟踪文件一起搬走，git 会认为它们被删了）。

**2. `_mdtest/` 下未跟踪的截图与预览 → `_archive/mdtest-assets/`**

只搬未跟踪的。已跟踪的检查脚本（`*_check.gd`、`*_shot.gd`）一个都不许动。
`_mdtest/greybox/*.png` 是运行时截图（可重生成）⇒ 搬。
`_mdtest/qa/`、`_mdtest/house_art_preview/` ⇒ 搬。

**3. 仓库根目录 7 个散落文件 → 直接删**

```
lab_out_hud.txt  lab_out_ad.txt  lab_out_cam.txt  lab_out_disp.txt
lab_out_greybox.txt  lab_frames_diff.txt  _tmp_version.txt
```

删前确认 `git ls-files <名字>` 输出为空（未跟踪才删）。

**4. `docs/` 未跟踪的 16 个 → `_archive/docs-2026-11-26/`**

逐个人工判断，规则：
- **已验收完、线已收的** `PROMPT-*.md` 与对应 `FEEDBACK-*.md` ⇒ 搬。
- **还在跑或即将派的**（至少：`PROMPT-overseer.md`、`PROMPT-lead-discipline.md`、`PROMPT-map-v4-exec.md`、`PROMPT-audio-exec.md`、`PROMPT-hearsay-exec.md`、`PROMPT-ending-outro-exec.md`、`PROMPT-playable-build-exec.md`、`PROMPT-voice-tts-web.md`、`配音台词卡-豆包.md`、`地图元素清单.md`、`待解决事项.md`、`地图视觉口径.md`、`story.md`、`npc.md`、`house-spec.md`、`HANDOFF.md`、`SUBMISSION.md`、`操作手册.md`）⇒ **留在原地**。
- 拿不准的一律**留原地并列进反馈**，由 lead 定。

**已跟踪的 `docs/**` 一个都不许动**（`git ls-files docs` 里有的就别碰）。

**5. `美术资产/` 的 34 个 `D` → 逐个确认后提交删除（**不许删整个目录**）**

⚠️ **这个目录不是垃圾堆**：`scripts/player.gd:39` 写着 `const HERO_SHEET := "res://美术资产/主角/Sprite-主角-Sheet.png"`，**主角贴图正在用**。整目录删掉会直接把玩家立绘干掉。

工作区里已经处于「已删除（`D`）」状态的 **34 个**，实测全是家具道具（`Sprite-老椿树1.png`、`Sprite-茅坑.png`、`小桌/`、`床/`、`椅子/`、`灶台柴/`、`长桌/` 及其 `.import`）。要验证它们确实被 `_ref/art/_assets_a1a3/_a1a3_assets.json` 取代了：

```powershell
# ① 这批文件名是否被任何已跟踪的代码/场景/资源引用（除注释和文档外应该为空）
git grep -n "老椿树1\|茅坑\|小桌\|灶台柴" -- scripts scenes tools data "*.tres" "*.tscn"
# ② manifest 是否指向 assets/ 而不是 美术资产/（实测：不指向）
git grep -n "美术资产" -- _ref/art/_assets_a1a3/
```

- ①**无命中** 且 ②**无命中** ⇒ `git add -u 美术资产` 单独提交，信息：「chore: 删除已被 _ref/art manifest 取代的家具原图（主角贴图保留）」。
- 任何一条**有命中** ⇒ 停手，把命中的行贴进反馈，报 lead。

⚠️ **禁止** `Remove-Item 美术资产 -Recurse`，禁止 `git rm -r 美术资产`。

**6. 12 个 `M` 文件 → 一个字都不许碰**

`_ref/art/A1_1926/*`（4）、`_ref/art/A2_1951/*`（3）、`_ref/art/A3_1976/*`（4）、`docs/HANDOFF.md`。
归属不明（可能是别人的未完成改动），**原样留在工作区**，只在反馈里列出。

---

## §4 自检

- **C1** `git ls-files --others --exclude-standard | Measure-Object -Line` < 30。
- **C2** `git status --short` 行数 < 30，且其中**只剩 §3 第 6 条的 12 个 `M`**（如果 `美术资产` 已提交）。
- **C3** `_archive/` 下文件总数 = 搬走前的未跟踪文件数（误差 ≤ 5，允许合并空目录）；且 **`git ls-files lab | Measure-Object -Line` 仍为 117**（一个溯源脚本都没被搬走）。
- **C4** `git ls-files _archive` 输出为空（归档区确实没进库）。
- **C5** 九套回归全绿，且数字与基线**逐位相同**。

九套：

```powershell
$g="D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe"
foreach ($t in @('greybox','camera','hud_layout','sort','asset_draw','evidence_archive','display','tile_wire','phasing')) {
  & $g --headless --path . -s ("res://_mdtest/{0}_check.gd" -f $t)
}
```

**退出码不可信，只看关键字**（`fails=0` / `REACH_OK=true` / `PHASING_CHECK_DONE fails=0 warns=0`）。`tile_wire` 在 headless 下 `gaps=0 checks=16` 是正常的（像素段自动跳过）。

---

## §5 反馈（`docs/FEEDBACK-repo-cleanup-exec.md`）

三段：

1. **搬了什么**：逐条对账，每个目录搬了多少文件、去了哪。
2. **证据**：每一步的 `git status --short | Measure-Object -Line` 前后数字、C1–C5 输出、九套回归原文、`docs/` 留原地的 16 个的判断理由。
3. **拿不准的**：列出来，不要自己决定。

**提交：** `_archive/` 不进库；只提交 `.gitignore`（追加两行）与（若 §3-5 通过）`美术资产/` 的删除。**绝不 `git add -A`，绝不 push。**

---

## §6 环境

- Godot：`D:\steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe`
- PowerShell 5.1：`&&` 不支持，用 `;`；`(Get-Content f).Count` 数 UTF-8 行数**不准**（用 `git status --short | Measure-Object -Line` 或 python）
- `.gitignore` 不是 UTF-8，`read`/`edit` 工具打不开，只能 `Add-Content`