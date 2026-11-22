# 交接文档 · 同学资产一次性替换线

> 执行依据：`docs/PROMPT-classmate-art-swap-exec.md`（本人 2026-11-22 授权替换，原「不覆盖 AI 图」禁令已 supersede）
> 清单权威：`docs/ART-MAPPING-classmate.md` §6；风险点：同文档 §6.1 / 提示词 §3
> 执行时间：2026-11-22　|　执行前 HEAD：`3f36587`（≥ `80bb223`，消费线 `aac2115` 贴图消费点已就绪）

---

## 1. 替换统计

| 动作 | 数量 | 说明 |
|---|---|---|
| **覆盖**（AI 图存在、尺寸一致 → 同学图覆盖） | **29** | 旧 AI 图（含 `.import`）已备份到 `assets/village/props/_legacy_ai/` |
| **补位**（AI 无此图 → 同学图复制进来） | **7** | `gui_1x1` / `xiaozhuo_1x1` / `hongzhuo_1x1` / `shuzhuo_1x1_top` / `baizhuo_1x1` / `changzhuo_2x1` / `cantang_3x1` |
| **跳过** | **3** | 见下表，逐条列 id + 原因 |

§6 的 38 个唯一 id 中，实际替换 36（29 覆盖 + 7 补位），跳过 2；另 §3 额外点名的 1 个也列入跳过。

### 跳过清单（判不准，绝不硬换）

| id | 原因 |
|---|---|
| `chaihuozao_1x1` | 与 manifest 里 `zaotai_1x4` / `tupi_zaotai_2x1` / `daota_zaotai_1x4` 三个灶台 id 语义重合，同学的柴火灶顶替哪一个需美术/剧情定 → 等本人拍板 |
| `danrenchuang_1x2` | 同学图偏「旧木床」调性，manifest 该 id 是常用单人床，另有 `jiu_muchuang_1x2` 旧木床 id → 调性取舍等本人拍板 |
| `shuangrenchuang_3x3` | 同学只画了 2×2（`shuangrenchuang_2x2`），没有 3×3；不缩放，等同学补图 |

> 注：跳过的 2 个 id（`chaihuozao_1x1` / `danrenchuang_1x2`）目标文件仍是原 AI 图，未改动；已用 md5 对比目标与备份确认。

---

## 2. 校验结果

### 2.1 尺寸校验（替换前预检 + 替换后复核）

- 预检：覆盖组逐张比对同学图与 AI 图像素尺寸，**29 张全部一致**才放行；不一致即整体中止（本次无不一致）。
- 复核（`lab/_swap_verify.py`）：
  - 备份齐全：29 张 PNG + 29 个 `.import` 全在 `_legacy_ai/`；
  - 36 张目标 PNG 与同学源图 **字节一致**（md5 相同）；
  - 跳过的 2 个 id 目标 == 备份（未被同学图覆盖）；
  - 36 张目标尺寸全部符合 manifest 权威口径 `w*32 × (h*32+32)`。
- 结论：**通过检查项全过，问题 0**。

### 2.2 Godot 导入

- `godot --headless --import --path .` → **EXIT=0**，`[ DONE ] reimport`。
- 7 张补位 PNG 的 `.import` 全部生成（Godot 自动）。
- 仅沙箱固有噪声：`Failed to read the root certificate store.` / `Cannot save editor settings to .../editor_settings-4.7.tres`（编辑器目录不可写，非项目问题）。

### 2.3 替换前后截图对照

- 截图器：`lab/_swap_shot.gd`（`_mdtest/asset_shot.gd` 副本，仅输出目录改由环境变量 `SWAP_SHOT_OUT` 指定），**原截图器与 `_mdtest/assets/*.png` 那 11 张一字未动**。
- 输出：`_mdtest/assets/swap_before/`（11 张）、`_mdtest/assets/swap_after/`（11 张）。
- 提示词要求的 4 处家具密集视角 `a1_shen_house` / `a1_mill_road` / `a2_zhou_house` / `a3_mill` **全部覆盖且均有画面变化**；11 个视角共 8 个有差异（其余 3 个 `a3_field_road`/`a1_mill_outside`/`a3_lu_ruin` 视角无被换家具入镜，像素 0% 差异属正常）。
- 拼图对照：`lab/_swap_compare.png`（每视角左 before / 右 after，绿框标有变化者）。

### 2.4 六套回归（看关键字不看退出码）

| 套件 | 关键字 | 结果 |
|---|---|---|
| greybox_check | `WORLD_OK=true` / `START_OK=true` / `HOTSPOTS_OK=true` / `REACH_OK=true` | ✅ |
| sort_check | `SORT_CHECK_DONE fails=0` | ✅ |
| camera_check | `CAMERA_CHECK_DONE fails=0` | ✅ |
| display_check | 无 FAIL；CONTENT_SCALE_* 全部 expected 匹配 | ✅ |
| hud_layout_check | `HUD_CHECK_DONE fails=0` | ✅ |
| asset_draw_check | `ASSET_DRAW_CHECK_DONE fails=0` | ✅ |

---

## 3. 写入边界自检

- ✅ 写入：`assets/village/props/<id>.png`（36 个 id）、`assets/village/props/_legacy_ai/`（备份）、`_mdtest/assets/swap_{before,after}/`、`lab/_swap_*.{py,gd,json,txt}`、`lab/_swap_compare.png`、本文档。
- ❌ 未碰：`scripts/*.gd`、`houses_data.json`、`data/frames.json`、manifest（`_a1a3_assets.json/.csv`）、`assets/village/houses/**`、`_classmate/**`（只读源）、`美术资产/**`、原 `_mdtest/assets/*.png` 11 张。
- 工作区其他并发线产物（17 张旧图 D 状态、lab/ 大量未跟踪脚本、其他文档）**保持原样，未暂存**。
- **未 commit**（本次执行受提示词 §6 约束，需精确 add 后提交——见提交记录）。

---

## 4. 待本人拍板（≤3 个）

1. **跳过的 2 张怎么定**：`chaihuozao_1x1` 顶替哪个灶台 id、`danrenchuang_1x2` 是否改用旧木床调性？（定了我再补换）
2. **`gui_1x1` 语义**：补位的矮柜与 `gui_1x2` 竖柜不是同一件，是否保留该补位 id？
3. **是否回退**：若游戏里观感不如预期，`_legacy_ai/` 留有 29 张原图可一键回滚——是否需要我现在出一份回滚脚本？
