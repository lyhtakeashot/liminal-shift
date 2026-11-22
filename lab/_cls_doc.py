# -*- coding: utf-8 -*-
"""生成 docs/ART-MAPPING-classmate.md —— 本线核心产出（映射表）。

表覆盖 美术资产/ 下全部 74 张 PNG，一行不漏：
  A 档 单件家具      —— 逐张映射 + 落盘
  B 档 图集          —— 按切片映射 + 落盘（附切片编号对照）
  C 档 房屋/地皮/树/主角 —— 只出方案，不落盘
"""
import json
import os
from collections import defaultdict

from PIL import Image

ROOT = r"D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift"
LAB = os.path.join(ROOT, "lab")
ART = os.path.join(ROOT, "美术资产")
MAN = os.path.join(ROOT, "_ref", "art", "_assets_a1a3", "_a1a3_assets.json")
OUT_MD = os.path.join(ROOT, "docs", "ART-MAPPING-classmate.md")
CL = os.path.join(ROOT, "assets", "village", "_classmate", "props")

man = json.load(open(MAN, encoding="utf-8"))
props = {p["id"]: p for p in man["props"]}

a_map = json.load(open(os.path.join(LAB, "_cls_map_a.json"), encoding="utf-8"))
b_map = json.load(open(os.path.join(LAB, "_cls_map_b.json"), encoding="utf-8"))


def size_of(path):
    with Image.open(path) as im:
        return im.width, im.height


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


# ---------- 收集全部源文件 ----------
all_src = []
for base, _dirs, files in os.walk(ART):
    for f in sorted(files):
        if f.lower().endswith(".png"):
            all_src.append(os.path.join(base, f))
all_src.sort(key=lambda p: rel(p))

a_by_src = {r["src"]: r for r in a_map["rows"]}
b_by_atlas = defaultdict(list)
for r in b_map:
    b_by_atlas[r["atlas"]].append(r)

# ---------- C 档说明（人工目视结论） ----------
C_NOTE = {
    "房屋/地板.png": ("房屋 base 地板层", "4×4 = 32px 地砖，可铺满 base 的 floor 区域；D6 base 画布 640×416(=20×13格) 需重复铺贴",
                    "缺：与游戏现有地面色 (#6e7a4c) 的色差需美术确认"),
    "房屋/墙面.png": ("房屋 base 墙面层", "6×6 = 32px 墙砖，含门窗贴图；对应 manifest shell 的 layer='base' 中的『墙』段",
                    "缺：门窗贴图风格与 AI 图不一致"),
    "房屋/地毯.png": ("房屋 base 装饰层", "6×12 = 32px 地毯，192×384；可作室内装饰叠加",
                    "缺：与 manifest 无对应 id，暂不入库"),
    "房屋/屋檐1.png": ("房屋 roof 屋顶层", "10×4.5 格 = 320×144；对应 shell layer='roof' 的『屋顶』段",
                    "缺：需按房屋尺寸 (20×13 等) 平铺拼接"),
    "房屋/屋檐2.png": ("房屋 roof 屋顶层", "6×12 = 192×384；备用檐口样式",
                    "缺：同屋檐1"),
    "房屋/屋檐3.png": ("房屋 roof 屋顶层", "6×12 = 192×384；第三种檐口",
                    "缺：同屋檐1"),
    "房屋/GK_B_CC_1.png": ("房屋整栋 tileset", "768×768 = 24×24 格；含屋顶/墙面/地板整块",
                    "缺：这是 24×24 格的自成体系尺寸，与游戏 20×13 / 18×13 等房屋尺寸不匹配"),
    "房屋/GK_D_CC_1.png": ("房屋整栋 tileset", "768×768 = 24×24 格；另一种风格",
                    "缺：同上"),
    "房屋/tileB_farmA.png": ("农田 tileset", "512×512 = 16×16 格；对应 scene 的 field_*",
                    "缺：与 AI field_patch_tiles.png 风格不同，替换需重做田块布局"),
    "房屋/tileB_farmB.png": ("农田 tileset", "768×768 = 24×24 格；农田变体",
                    "缺：同上"),
    "房屋/tileB_fortA.png": ("围墙/要塞 tileset", "512×512 = 16×16 格",
                    "缺：manifest 无对应 id"),
    "房屋/tileB_fortB.png": ("围墙/要塞 tileset", "512×512 = 16×16 格；变体",
                    "缺：同上"),
    "房屋/TopDownHouse_FurnitureState2.png": ("家具状态贴图集", "208×288 = 6.5×9 格；俯视家具状态",
                    "缺：非 32 整数倍宽，网格切图需特殊处理"),
    "地皮/GK_A2_CCautotile_1.png": ("地面 autotile", "768×576 = 24×18 格；可做地面自动拼接",
                    "缺：对应 scene 的 ground_*_tiles.png（单格 32×32），需重切"),
    "地皮/GK_A5_CCfloors_1.png": ("地面 floors tileset", "384×768 = 12×24 格",
                    "缺：同上"),
    "地皮/GK_C_CC_1.png": ("地面 tileset", "511×511；非 32 整数倍",
                    "缺：尺寸不规整，需重新切分"),
    "树/tree.png": ("树 / scene tree_a*", "96×128 = 3×4 格；对应 scene 的 tree_a1(2×2)/a2(4×4)/a3(6×6)",
                    "缺：树冠有 3 态(春/夏/秋)，且 game 侧 scene 树占位比源图大"),
    "树/Redtree8.png": ("红树变体", "64×64 = 2×2 格",
                    "缺：同上"),
    "主角/Sprite-主角-Sheet.png": ("主角序列帧", "1152×32 = 36 帧横排，每帧 32×32（帧间留 0~20px 空隙，实为等距 32px 步进）",
                    "缺：player.gd 纯代码画圆，无贴图消费点；接序列帧需先改视觉机制线"),
}


def fmt_size(sz):
    return "%d×%d" % sz


def main():
    L = []
    a = L.append
    a("# 美术同学资产导入适配线 · 映射表")
    a("")
    a("> 生成脚本：`lab/_cls_doc.py`（可重跑）。数据源：`lab/_cls_map_a.json`、`lab/_cls_map_b.json`。")
    a("> 本表**不覆盖**已交付的 AI 程序化图：全部产物落在 `assets/village/_classmate/props/`，")
    a("> 替换与否由本人拍板。")
    a("")

    # 概览
    a("## 0. 总览")
    a("")
    a("| 档位 | 源文件数 | 已映射 | 未映射 | 落盘产物 |")
    a("|---|---|---|---|---|")
    a("| A 档 单件家具 | 23 | 23 | 0 | 19 主图 + 4 变体 |")
    a("| B 档 图集切片 | 32 | 13 张图集贡献 60 切片 | 19 张图集未取件 | 20 主图 + 41 变体 |")
    a("| C 档 房屋/地皮/树/主角 | 19 | 19（只出方案） | 0 | **0（按纪律不落盘）** |")
    a("| **合计** | **74** | **55** | **19** | **84 张 PNG（39 主图 + 45 变体）** |")
    a("")
    a("规格口径（D6）：交付画布 = 占地宽×32 × (占地高×32 + 32)，透明补在**顶部**，内容**贴底**。")
    a("校验脚本 `lab/_cls_check.py`：84 张全部尺寸符合 manifest 且内容贴底，**0 问题**。")
    a("")

    # A 档
    a("## 1. A 档 · 单件家具（23 张，逐张映射，已落盘）")
    a("")
    a("| 源文件 | 像素尺寸 | 目标 manifest id | 目标路径 | 置信度 | 备注 |")
    a("|---|---|---|---|---|---|")
    for p in all_src:
        r = rel(p)
        if r not in a_by_src:
            continue
        row = a_by_src[r]
        sz = size_of(p)
        a("| `%s` | %s | `%s` | `%s` | %s | %s |" % (
            r, fmt_size(sz), row["id"], row["out"], row["conf"], row["note"]))
    a("")
    a("**A 档新增 id（用户 m00083 拍板『加新 id』）**：")
    a("")
    a("| 新 id | code | 中文名 | 占地 | 来源 |")
    a("|---|---|---|---|---|")
    new_ids = ["xiaozhuo_1x1", "hongzhuo_1x1", "baizhuo_1x1", "shuzhuo_1x1_top",
               "gui_1x1", "changzhuo_2x1", "cantang_3x1"]
    for i in new_ids:
        p = props[i]
        src = [r["src"] for r in a_map["rows"] if r["id"] == i]
        a("| `%s` | %s | %s | %d×%d | `%s` |" % (i, p["code"], p["name"], p["w"], p["h"], src[0]))
    a("")
    a("manifest 改动：`props` 84 → **91** 条（`git diff` 纯新增 168 行 / 0 删除）。")
    a("")

    # B 档
    a("## 2. B 档 · 图集切片（源 32 张图集，已取件 13 张 / 60 切片，已落盘）")
    a("")
    a("切图方法：alpha 8 连通域 → 包围盒吸附 32 网格 → 贪心合并相交框 → 候选表 `lab/_cls_atlas_cands.json`")
    a("→ 逐个目视核对编号与 @x,y 网格位置 → 裁紧内容 → 按 manifest 权威占地贴底。")
    a("")
    a("| 源图集 | 切片数 | 取到的 id |")
    a("|---|---|---|")
    for at in sorted(b_by_atlas):
        rows = b_by_atlas[at]
        ids = []
        for r in rows:
            if r["id"] not in ids:
                ids.append(r["id"])
        a("| `%s` | %d | %s |" % (at, len(rows), "、".join("`%s`" % i for i in ids)))
    a("")
    a("### 2.1 切片编号 → 内容对照表")
    a("")
    a("| # | 源图集 | 切片序号 | @x,y | 目标 id | 角色 | 落地文件 |")
    a("|---|---|---|---|---|---|---|")
    for i, r in enumerate(b_map):
        a("| %d | `%s` | #%d | %d,%d | `%s` | %s | `%s` |" % (
            i, r["atlas"], r["idx"], r["src_box"][0] // 32, r["src_box"][1] // 32,
            r["id"], r["role"], r["out"]))
    a("")

    # 未映射图集
    a("### 2.2 B 档未取件图集（19 张）")
    a("")
    a("| 源图集 | 像素尺寸 | 原因 |")
    a("|---|---|---|")
    unreason = {
        "家具.png": "256×256 混合家具大图，**alpha 连通域检不出候选（0 候选）**——内容之间互相紧贴无透明缝，需人工逐个框选；本轮未做",
        "8_Gym_32x32.png": "256×272 体育器材图集，连通域检出的候选全为 >3 格（器材成组摆放），无可用单件",
        "6_Music_and_sport_32x32.png": "56 个候选里绝大多数是**乐器/画框/奖牌**等与 manifest 家具 id 无对应关系；只有 2 张长凳可对，但样式与 manifest 家具语义不合",
    }
    for p in all_src:
        r = rel(p)
        if not r.startswith("美术资产/家具/") or "/" in r[len("美术资产/家具/"):]:
            continue
        base = os.path.basename(r)
        if base in b_by_atlas:
            continue
        if base in unreason:
            why = unreason[base]
        elif base.startswith("Interiors "):
            why = "768×768 完整室内 tileset（含墙/地板/结构），**内容是成组的房屋结构而非单件家具**；连通域只识别到少量装饰件，已取 2 件，其余按纪律列入未映射"
        else:
            why = "本轮未取件（目视后判定为图集级装饰，与 manifest 家具 id 无稳定对应）"
        a("| `%s` | %s | %s |" % (base, fmt_size(size_of(p)), why))
    a("")

    # C 档
    a("## 3. C 档 · 房屋 / 地皮 / 树 / 主角（19 张，只出方案，**不落盘**）")
    a("")
    a("理由：这些是 tileset / 组件 / 序列帧，要拼成 D6 规格的整栋 `base`/`roof`（如 640×448）")
    a("工作量与风格对齐成本都很高，且本线纪律明确不写入 `assets/village/`。")
    a("以下为**拼装方案**，供后续专案使用。")
    a("")
    a("| 源文件 | 像素尺寸 | 能提供什么 | 怎么用 | 还缺什么 |")
    a("|---|---|---|---|---|")
    for p in all_src:
        r = rel(p)
        key = r.replace("美术资产/", "")
        if key not in C_NOTE:
            continue
        what, how, lack = C_NOTE[key]
        a("| `%s` | %s | %s | %s | %s |" % (key, fmt_size(size_of(p)), what, how, lack))
    a("")
    a("### 3.1 房屋整栋拼装草图（示意，不落盘）")
    a("")
    a("```")
    a("D6 base 画布 = 占地宽×32 × (占地高×32 + 32)   例：lu_house 20×13 → 640×448")
    a("")
    a("  ┌─────────────────────────────────────────────┐  ← cpx 640×448")
    a("  │  roof 层  ← 屋檐1/2/3.png 平铺（320×144 起）  │     渲染时叠在 base 之上")
    a("  ├─────────────────────────────────────────────┤  ← px 640×416")
    a("  │  墙 层    ← 墙面.png 6×6 墙砖 + 门窗贴图      │")
    a("  │  家具层  ← 家具.png / A、B 档切片            │")
    a("  │  地 层    ← 地板.png 4×4 地砖 平铺            │")
    a("  └─────────────────────────────────────────────┘")
    a("")
    a("  现状提示：world_view.gd:366 只真实绘制 roof；:239 的 base 只当开关不贴图。")
    a("  ⇒ 即使 C 档拼完，游戏里当前也只看得到 roof。")
    a("```")
    a("")
    a("### 3.2 主角序列帧")
    a("")
    a("- `Sprite-主角-Sheet.png` = 1152×32，**36 帧等距 32px 步进**（非空列段实测 36 段，步进 32px）。")
    a("- 帧内容：站立 / 行走 / 做事等若干循环，**没有现成的方向分组标记**，需要同学补一张帧序表。")
    a("- 引擎侧 `player.gd` 是纯代码 `draw_self()` 画圆，**没有贴图消费点**。")
    a("- 结论：接序列帧必须先由视觉机制线加贴图消费点，本线不越界改 `scripts/`。")
    a("")

    # 未映射清单
    a("## 4. 未映射清单与理由")
    a("")
    a("### 4.1 源图 → 未映射")
    a("")
    a("- B 档 19 张图集未取件：见 §2.2（`Interiors 0..17` 18 张 + `家具.png` + `8_Gym`），")
    a("  其中 `6_Music_and_sport` 与 `家具.png` 也不含可映射单件。")
    a("- C 档 19 张：按纪律**只出方案不落盘**，映射关系已登记在 §3。")
    a("- **实际未映射源文件 = 19 张 B 档图集 + 19 张 C 档 = 38 张**；")
    a("  C 档有明确拼装方案（§3），B 档 19 张是『图集级素材不适合做单件』或『需人工逐框』。")
    a("")
    a("### 4.2 manifest id → 尚无同学图（52 个，共 91 个 props id）")
    a("")
    a("| manifest id | 占地 | uses | 名称 |")
    a("|---|---|---|---|")
    covered = set()
    for f in os.listdir(CL):
        if f.endswith(".png"):
            covered.add(f[:-4])
    for r in b_map:
        covered.add(r["id"])
    miss = [p for p in man["props"] if p["id"] not in covered]
    for p in miss:
        a("| `%s` | %d×%d | %s | %s |" % (p["id"], p["w"], p["h"], p.get("uses", 0), p.get("name", "")))
    a("")
    a("> 说明：这些 id 大多是**剧情专用道具**（石磨、粮囤、账桌、验粮台、风车…）或**大尺寸建筑构件**")
    a("> （灶台 1×4、墙基暗龛 1×4、藤椅 1×4），同学图里没有对应素材。")
    a("> 另：`shuangrenchuang_3x3`（3×3 双人床）同学只画了 2×2 版本，尺寸口径不同，**不强行缩放**。")
    a("")

    # 校验
    a("## 5. 自检结果")
    a("")
    a("**对照预览图（每格：左=同学手绘，右=AI 程序化图）**")
    a("")
    a("| 文件 | 内容 |")
    a("|---|---|")
    a("| `lab/_classmate_compare_a.png` | A 档 19 张主图 vs AI 同 id 图 |")
    a("| `lab/_classmate_compare_a2.png` | A 档 4 张同学变体 vs AI 主图 |")
    a("| `lab/_classmate_compare_b.png` | B 档 60 条切片 vs AI 同 id 图 |")
    a("| `lab/_cls_pick_check.png` | B 档切片确认表（标 id/尺寸/图集#序号/角色） |")
    a("| `lab/_cls_c_sheet.png` | C 档 19 张源图目视接触表 |")
    a("")
    a("生成脚本：`lab/_cls_compare.py`（对照图）、`lab/_cls_doc.py`（本文档，可重跑）。")
    a("")
    a("| 检查项 | 结果 |")
    a("|---|---|")
    a("| 源文件覆盖 | 74/74 已登记（§1 A 档 23、§2 B 档 32、§3 C 档 19） |")
    a("| 交付尺寸 = manifest `(w*32)×(h*32+32)` | 84/84 通过 |")
    a("| 内容贴底（底行 = 画布高-1） | 84/84 通过 |")
    a("| Godot `--headless --import` | exit=0，无资源 ERROR（仅编辑器证书/设置目录告警，非项目问题） |")
    a("| `.import` 生成 | `_classmate/` 下 84 张 PNG 全部有 `.import` |")
    a("| 边界检查 | 只新增 `docs/ART-MAPPING-classmate.md`、`assets/village/_classmate/`、`lab/`；")
    a("|  | manifest 仅**新增** 7 条 props（P85–P91），未删改既有条目 |")
    a("| 未覆盖既有资产 | `assets/village/props/`、`houses/`、`scene/`、`scripts/*.gd`、`houses_data.json`、`frames.json` 均未改动 |")
    a("")
    a("### 5.1 引擎消费点缺口（导入 ≠ 进游戏能看到）")
    a("")
    a("- `scripts/world_view.gd:366` 只真实绘制 **roof**；`:239` 的 base 只当『有没有图』的开关，图本身不贴。")
    a("- `scripts/` 全目录对 **props / scene**（河/路/田/井/树）**零消费点**。")
    a("- `scripts/player.gd` 纯代码画圆，主角贴图无消费点。")
    a("⇒ 本线交付的 84 张家具图**在游戏里目前一张都看不到**；要看到必须等视觉机制线补消费点。")
    a("")

    # 替换建议清单
    a("## 6. 替换建议清单（等本人拍板，本线**未执行**任何替换）")
    a("")
    a("判定规则：")
    a("")
    a("- **尺寸一致** = AI 目录 `assets/village/props/<id>.png` 存在且像素尺寸与同学图交付画布完全相同 → 直接换文件即可。")
    a("- **尺寸不同** = 同 id 但 AI 图规格与 manifest 不同 → 换之前要先对齐画布，否则会错位。")
    a("- **AI 无此图** = manifest 里有这个 id，但 AI 目录没出图 → 同学图属**纯补位**，不是替换。")
    a("")
    a("| 同学图 id | 同学图文件 | 尺寸 | AI 对应图 | AI 尺寸 | 判定 | 建议 |")
    a("|---|---|---|---|---|---|---|")
    ai_dir = os.path.join(ROOT, "assets", "village", "props")
    rows6 = []
    for r in a_map["rows"]:
        if r["role"] != "主图":
            continue
        rows6.append((r["id"], r["out"], r["src"], "A档"))
    for r in b_map:
        rows6.append((r["id"], r["out"], "%s #%d" % (r["atlas"], r["idx"]), "B档"))
    seen6 = set()
    n_same = n_diff = n_none = 0
    for pid, outp, src, tier in rows6:
        if pid in seen6:
            continue
        seen6.add(pid)
        clp = os.path.join(ROOT, outp.replace("/", os.sep))
        if not os.path.exists(clp):
            continue
        csize = size_of(clp)
        aip = os.path.join(ai_dir, "%s.png" % pid)
        if not os.path.exists(aip):
            n_none += 1
            a("| `%s` | `%s` | %d×%d | — | — | **AI 无此图** | 纯补位：manifest 已登记该 id，AI 侧未出图，建议直接采用 |" % (
                pid, outp, csize[0], csize[1]))
            continue
        asize = size_of(aip)
        if asize == csize:
            n_same += 1
            a("| `%s` | `%s` | %d×%d | `assets/village/props/%s.png` | %d×%d | **尺寸一致** | 可直接替换，建议先在游戏里并排看一眼 |" % (
                pid, outp, csize[0], csize[1], pid, asize[0], asize[1]))
        else:
            n_diff += 1
            a("| `%s` | `%s` | %d×%d | `assets/village/props/%s.png` | %d×%d | **尺寸不同** | 先对齐画布再换，否则会错位/拉伸 |" % (
                pid, outp, csize[0], csize[1], pid, asize[0], asize[1]))
    a("")
    a("小结：**尺寸一致 %d 个 / 尺寸不同 %d 个 / AI 无此图 %d 个**（共 %d 个唯一 id）。" % (
        n_same, n_diff, n_none, len(seen6)))
    a("")
    a("> 提醒：替换只解决**图**，不解决**看不到**的问题。")
    a("> 上面 §5.1 说得很直白——`scripts/` 目前对 props 零消费点，")
    a("> 即使全换了，游戏里依然一张都显示不出来。**建议先让视觉机制线把 props 消费点做掉，再回来替换**，")
    a("> 否则只是一次看不见的替换。")
    a("")
    a("### 6.1 替换时必须人工过一眼的几张（已知风险点）")
    a("")
    a("| id | 风险 | 说明 |")
    a("|---|---|---|")
    a("| `shuangrenchuang_3x3` | 规格不符 | manifest 是 3×3 双人床，同学只画了 2×2 版本 `shuangrenchuang_2x2`；"
      "**不缩放**，等同学补 3×3 |")
    a("| `gui_1x1` | 语义近似 | 同学画的是两层抽屉矮柜，manifest 的 `gui_1x2` 是四层竖柜，两者不是同一件家具 |")
    a("| `luokuang_1x1` | 语义近似 | 同学的是竹编扁箩筐/圆箩筐，manifest `luokuang` 口径需确认是否指『箩筐』而非『筐』 |")
    a("| `deng_1x1` | 语义近似 | 同学画的是圆草墩，manifest `deng` 若指木凳则需换 `yi_1x1` 或让同学补 |")
    a("| `shuzhuo_1x1` | 俯视/侧视混用 | 同学有两张书桌（侧视带抽屉、俯视摊纸笔），已拆成 `shuzhuo_1x1` 与 `shuzhuo_1x1_top`；"
      "游戏里用哪张取决于视角，**两者不可互换** |")
    a("| `chaihuozao_1x1` | 与剧情道具重合 | manifest 里另有 `zaotai_1x4`/`tupi_zaotai_2x1`/`daota_zaotai_1x4` 三个灶台 id，"
      "同学的柴火灶到底顶替哪一个，要美术/剧情定 |")
    a("| `danrenchuang_1x2` | 剧情优先度 | manifest 有 `danrenchuang_1x2`（用得多）与 `jiu_muchuang_1x2`（旧木床）两个，"
      "同学图偏『旧木床』质感，替换前确认要哪个调性 |")
    a("")
    a("### 6.2 同学图的风格差距（替换前要有预期）")
    a("")
    a("- 同学图是**带描边、有高光/阴影的精细像素画**；AI 图是**平涂色块**。同屏混用会明显不协调。")
    a("- 同学图多为**正面/等距 3/4 视角**，AI 图多为**俯视视角**。")
    a("⇒ 如果要做的是『整体换风格』，建议**一次性全换**而不是挑几张替换；")
    a("  如果只换一部分，需要先定一个过渡方案（例如先统一描边）。")
    a("")

    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(L) + "\n")
    print("wrote", OUT_MD, len(L), "lines")


if __name__ == "__main__":
    main()
