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
| `lab/` 文件数 | 1031 | < 40（只留本周在用的） |
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

2. `.gitignore` 追加两行（**该文件不是 UTF-8，`read`/`edit` 工具会报 invalid UTF-8，只能用 `Add-Content` 追加**）：

```powershell
Add-Content .gitignore "`n# 归档区：不进版本库`n_archive/`n# 草稿脚本区：本地工作用`nlab/"
```

追加后用 `git check-ignore -v _archive/x lab/x` 验证生效，并确认 `.evidence_archive.json`（第 61 行）与 `build/`（第 64 行）两条**没有被破坏**。

---

## §3 处置表

**1. `lab/` → `_archive/lab-2026-11-26/`**

整目录搬（`lab/` 下 1031 个文件全部是未跟踪的草稿：`_probe_*.py`/`_probe_*.gd`、`maps/`、`audio_demo/`、`evidence_shot/`、`render_fix_shot/`、`_backup_16px_a4a5/`、`_backup_artline/`、`_l19_appdata/`、`_push_api_tmp/`、`__pycache__/`、`lab_out_*.txt`）。

搬完 `lab/` 保留为空目录即可（或删掉空目录）。**注意：`lab/` 里没有已跟踪文件，搬之前用 `git ls-files lab` 确认输出为空。**

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

**5. `美术资产/` 的 34 个 `D` → 提交删除**

先证明它已经用不上：

```powershell
Select-String -Path scripts/*.gd,scenes/**/*.tscn,*.tres -Pattern "美术资产" -ErrorAction SilentlyContinue
```

**输出为空**（说明没有任何代码/场景/资源引用它）⇒ `git add -u 美术资产` 并单独提交，提交信息：「chore: 删除被 assets/ 取代的原始素材目录」。
**输出非空** ⇒ 停手，把命中的行贴进反馈，报 lead。

**6. 12 个 `M` 文件 → 一个字都不许碰**

`_ref/art/A1_1926/*`（4）、`_ref/art/A2_1951/*`（3）、`_ref/art/A3_1976/*`（4）、`docs/HANDOFF.md`。
归属不明（可能是别人的未完成改动），**原样留在工作区**，只在反馈里列出。

---

## §4 自检

- **C1** `git ls-files --others --exclude-standard | Measure-Object -Line` < 30。
- **C2** `git status --short` 行数 < 30，且其中**只剩 §3 第 6 条的 12 个 `M`**（如果 `美术资产` 已提交）。
- **C3** `_archive/` 下文件总数 = 搬走前的未跟踪文件数（误差 ≤ 5，允许合并空目录）。
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