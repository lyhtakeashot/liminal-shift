# -*- coding: utf-8 -*-
"""由 _a1a3_assets.json + houses_data.json 生成给美术的总需求清单。

两种模式：
  python gen_art_doc.py               -> docs/art-assets-a1a3.md（仓库内版，引用 _ref 路径）
  python gen_art_doc.py --handoff     -> art-handoff/00_总需求清单.md（外发版，引用交付文件夹内路径）
"""
import json
import os
import sys

HANDOFF = "--handoff" in sys.argv

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ART = os.path.join(ROOT, "_ref", "art", "_assets_a1a3")
DOC = (os.path.join(ROOT, "art-handoff", "00_总需求清单.md") if HANDOFF
       else os.path.join(ROOT, "docs", "art-assets-a1a3.md"))
HOUSES = os.path.join(ROOT, "_ref", "houses", "houses_data.json")

# 一格多少像素（2026-11-21 TILE 16→32）。与技术线 house_shape.gd:13 保持一致。
TILE = 32

# 外发版把图/表的引用指向 art-handoff/ 里的实际文件名
IMG_DIR = "本文件夹" if HANDOFF else "`_ref/art/_assets_a1a3/`"
IMG_SUF = "_拆解图.png" if HANDOFF else "_assets.png"
SCENE_FILE = "00_场景元素_三帧对比.png" if HANDOFF else "_scene_a1a3_assets.png"
CSV_FILE = "01_总需求清单.csv" if HANDOFF else "_a1a3_assets.csv"

ORDER = [("A1", "lu_house"), ("A1", "mill_a1"), ("A1", "shen_a1"), ("A1", "zhou_house"),
         ("A2", "mill_a2"), ("A2", "shen_a2"), ("A2", "lu_a2"), ("A2", "zhou_a2"),
         ("A3", "mill_a3"), ("A3", "shen_a3"), ("A3", "zhou_a3"), ("A3", "lu_a3")]
YEAR = {"A1": 1926, "A2": 1951, "A3": 1976}
FRAME_DIR = {"A1": "A1_1926", "A2": "A2_1951", "A3": "A3_1976"}
FAMILY = {"lu_house": "lu", "lu_a2": "lu", "lu_a3": "lu",
          "shen_a1": "shen", "shen_a2": "shen", "shen_a3": "shen",
          "mill_a1": "mill", "mill_a2": "mill", "mill_a3": "mill",
          "zhou_house": "zhou", "zhou_a2": "zhou", "zhou_a3": "zhou"}

d = json.load(open(os.path.join(ART, "_a1a3_assets.json"), encoding="utf-8"))
houses = {h["id"]: h for h in json.load(open(HOUSES, encoding="utf-8"))}
shells, props, scene = d["shell"], d["props"], d["scene"]
by_id = {r["id"]: r for r in props}

shell_of = {}
for s in shells:
    shell_of.setdefault(s["house"], []).append(s)

TOTAL = len(shells) + len(props) + len(scene)


def house_rows():
    out = []
    for fr, hid in ORDER:
        hs = houses[hid]
        X0, Y0, X1, Y1 = hs["lot"]
        gw, gh = X1 - X0 + 1, Y1 - Y0 + 1
        wings = hs["wings"]
        bw = max(w[0] + w[2] for w in wings) - min(w[0] for w in wings)
        bh = max(w[1] + w[3] for w in wings) - min(w[1] for w in wings)
        nroom = len(hs["rooms"])
        ninst = len(hs["furniture"])
        ids = set()
        for f in hs["furniture"]:
            ids.add("%s_%dx%d" % (None, f["rect"][2], f["rect"][3]))
        nslot = len(shell_of.get(hid, []))
        out.append((fr, hid, hs, gw, gh, bw, bh, nroom, ninst, nslot))
    return out


def slug_of(hid, f):
    # 家具的唯一 id 由 gen_asset_breakdown.furn_slug 决定，这里从 props 里反查
    for r in props:
        if r["name"] == f["name"] and r["w"] == f["rect"][2] and r["h"] == f["rect"][3]:
            return r
    return None


L = []
w = L.append

w("# A1–A3 美术资产总需求清单")
w("")
w("> 对象：`shift` 三个时期的房屋与村落场景（A1 1926 / A2 1951 / A3 1976）。")
w("> 数据来源：`_ref/houses/houses_data.json`（18 栋里 A1–A3 的 12 栋）+ `data/frames.json`（场景几何）。")
w("> 全部尺寸按 **1 格 = 32×32 px** 换算，和代码里的占地格数一一对应。")
w("> 本文由 `_ref/houses/gen_art_doc.py` 生成；改数据后重跑即可，不要手改数字。")
w("")
w("## 0. 一页结论")
w("")
w("这三年一共 **%d 个文件**，分三层：" % TOTAL)
w("")
w("| 层 | 数量 | 是什么 | 画布怎么定 |")
w("|---|---|---|---|")
w("| 外观层 `base` / `roof` | **%d** | 每栋每帧整栋单图，不是 32px 瓦片拼 | **占地宽 × (占地高 + 32)px**，锚点底部中心 |" % len(shells))
w("| 家具层 `props` | **%d** | 每件家具一个文件，全项目共享 | 九档 1×1…3×3 格，锚点底部中心 |" % len(props))
w("| 场景层 | **%d** | 河 / 坝 / 路 / 田 / 老井 / 老槐 / 界碑 / 地面底瓦 | 按 `frames.json` 实测几何 |" % len(scene))
w("")
w("先做这四批，收益最高（详细见 §7）：")
w("")
w("1. **12 张外观**（§4）—— 没有它游戏里现在只有色块。")
w("2. **12 件线索家具**（§5.3）—— 剧情全靠这 12 件，缺一个就断线索。")
w("3. **20 件高频复用家具**（§5.2）—— 一件顶 4~12 处，摆满全场。")
w("4. **8 件场景核心**（§6）—— 河 / 路 / 田 / 老井 / 老槐 / 界碑 / 坝 / 地面底瓦。")
w("")
w("## 1. 这套东西怎么看")
w("")
w("配套 13 张拆解图，都在%s：" % IMG_DIR)
w("")
w("- `A1_1926/<栋 id>%s`、`A2_1951/…`、`A3_1976/…` —— 每栋一张，共 12 张。" % IMG_SUF)
w("- `%s` —— 三个时期的场景同区位对比 + 场景元素清单。" % SCENE_FILE)
w("- `%s` —— 全部 %d 项的可筛选总表（Excel 直接打开）。" % (CSV_FILE, TOTAL))
if not HANDOFF:
    w("- `_a1a3_assets.json` —— 同上，机器可读。")
w("")
w("单栋拆解图分四块：")
w("")
w("| 区块 | 内容 | 用途 |")
w("|---|---|---|")
w("| `[A] 占地格图` | 每格代表 32×32 px，格子里的 `Pxx` 编号 = 家具编号 | 看清每件东西摆在哪、占几格 |")
w("| `[B] 外观层` | 这栋要交几张 `base` / `roof`、画布多大、画什么 | 外观单图照着画 |")
w("| `[C] 家具层` | 交付目录与命名规则 | 统一规范 |")
w("| `[D] 本栋家具清单` | 编号 / 文件名 / 尺寸 / 位置 / 全局复用次数 / 摆放要求 | 一行一件，照着做 |")
w("")
w("色图例：灰棕 = 外墙板，深棕 = 内部隔墙，棕 = 室内地面，深绿 = 院子，"
  "黄 = 房门，深棕块 = 院门，橙框 + ◆ = 可检视线索，绿框「草」= 需铺 32px 杂草（废墟）。")
w("")
w("## 2. 交付规范（硬要求，不满足会掉图或错位）")
w("")
w("| 项 | 要求 |")
w("|---|---|")
w("| 网格 | 1 格 = **32×32 px**；家具只用九档：1×1、1×2、1×3、2×1、2×2、2×3、3×1、3×2、3×3 |")
w("| 画布 | **外观 = 占地宽 × (占地高 + 32)px**（高度比占地多一格，多出的一格在顶部，是墙与屋顶立起来的高度）；"
  "家具 = 占地格数 × 32px（**允许高度多画一格**做朝向立面，但占地按数据算，不看 PNG 像素） |")
w("| 锚点 | 一律**底部中心**（外观的画布底边仍与占地底边对齐，只是往上多一格） |")
w("| 透明边 | 每张图四周留 **2px** 透明，别让像素贴边 |")
w("| base / roof | **同宽同高同锚点**，高度都是 `占地高 + 32`；玩家走进占地矩形时 `roof` 整层淡出、`base` 留在原地 |")
w("| 文件名 | **禁改**。数据按文件名对号入座，改名等于丢图 |")
w("| 缺图兜底 | 代码对缺图有回落：返回 null → 画纯色块 + id 名，游戏不崩。所以可以分批进图 |")
w("")
w("为什么外观不做 32px 瓦片拼：檐口厚度、屋顶坡度、烟囱、门窗凹陷、墙脚水渍这些"
  "在 32px 瓦片里要么拼不出来、要么网格重复一眼露怯；而且 A1–A3 每帧房型本来就不一样"
  "（一字 → L 形 → 凹形 → 废墟），外观无论如何都要重画，「瓦片换色省工」在这里不成立。"
  "星露谷也是这么分的：建筑外观整栋单图，室内家具按格吸附。")
w("")
w("## 3. 三个时期总览（12 栋）")
w("")
w("| 帧 | 栋 id | 名称 | 占地（格） | 占地（px） | 屋本体（格） | 房间 | 家具件数 | 外观张数 | 外观画布（px） |")
w("|---|---|---|---|---|---|---|---|---|---|")
for fr, hid, hs, gw, gh, bw, bh, nroom, ninst, nslot in house_rows():
    short = hs["name"].split("·")[0].strip()
    roomtxt = "废墟（无可进入房间）" if hs.get("ruin") else str(nroom)
    w("| %s %d | `%s` | %s | %d×%d | %d×%d | %d×%d | %s | %d | %d | **%d×%d** |"
      % (fr, YEAR[fr], hid, short, gw, gh, gw * TILE, gh * TILE, bw, bh,
         roomtxt, ninst, nslot, gw * TILE, (gh + 1) * TILE))
w("")
w("> 注意区分两列：**「占地（px）」是格图与碰撞用的**，"
  "**「外观画布（px）」是美术要交的图的实际尺寸**（比占地高 32px）。")
w("")
w("三年变化一句话：")
w("")
w("- **A1 1926**：全村最朴素的一年。陆家、沈家都是一字房，磨坊是作坊，周家是长工房。")
w("- **A2 1951**：磨坊改粮站（新砖、暗龛成了空的）；沈家扩成 L 形（正房 + 西厢，两代同住）；"
  "陆家、周家的占地与开间跟 A1 一模一样，只换材料与陈设（陆家已空屋）。")
w("- **A3 1976**：沈家继续长成凹形带连廊的 14 间大院；磨坊 → 粮站加南侧晒谷场和土圆仓；周家翻新灶间；"
  "**陆家只剩地基废墟**（房已塌，不交付 roof）。")
w("")
w("## 4. 外观层：23 张整栋单图")
w("")
w("一共 %d 张（12 栋 × 2 层 − 陆家 A3 废墟没有 `roof`）。" % len(shells))
w("")
w("**画布 = 占地宽 × (占地高 + 32)px**：多出的一格在**顶部**，是墙与屋顶立起来的高度；"
  "画布底边仍与占地底边对齐，锚点仍是底部中心。"
  "屋顶与墙顶面天然要向上溢出画布一格，画布不带这 32px 就会被**裁掉一条**——"
  "不报错、验收也看不出来，跑起来才发现 23 张全要重画。")
w("")
for fam, fname in (("lu", "陆家"), ("shen", "沈家"), ("mill", "磨坊 / 粮站"), ("zhou", "周家")):
    rows = [s for s in shells if FAMILY.get(s["house"]) == fam]
    if not rows:
        continue
    w("### %s（`assets/village/houses/%s/`）" % (fname, fam))
    w("")
    w("| 编号 | 文件名 | 画布（格） | 画布（px） | 其中占地（px） | 说明 |")
    w("|---|---|---|---|---|---|")
    for s in rows:
        w("| %s | `%s.png` | %d×%d | **%d×%d** | %d×%d | %s |"
          % (s["code"], s["path"].split("/")[-1][:-4], s["cw"], s["ch"],
             s["cpx"][0], s["cpx"][1], s["px"][0], s["px"][1], s["desc"]))
    w("")

w("## 5. 家具层：79 件共享素材")
w("")
w("A1–A3 里家具一共摆了 **%d 件**，去重后是 **%d 个文件**。" %
  (sum(len(houses[hid]["furniture"]) for _, hid in ORDER), len(props)))
w("逐件一个文件、全项目共享：同一件东西在最多 8 栋里都出现，只画一次。")
w("")
w("### 5.1 尺寸分布（只用到 9 档里的 7 档）")
w("")
sizes = {}
for r in props:
    sizes["%d×%d" % (r["w"], r["h"])] = sizes.get("%d×%d" % (r["w"], r["h"]), 0) + 1
w("| 格数 | px | 件数 | 备注 |")
w("|---|---|---|---|")
note_size = {"1×1": "最多，覆盖小物件：凳 / 水缸 / 茅坑 / 木箱 等",
             "1×2": "竖贴墙：衣柜 / 书架 / 灶台 / 账桌 / 屏风",
             "1×3": "只 1 件：条案（堂屋）",
             "2×1": "横贴墙：单人床 / 长凳 / 小桌 / 便民服务台",
             "2×2": "八仙桌 / 石磨 / 粮囤 / 地基痕迹",
             "3×2": "只 1 件：茅房（院子独立建筑）",
             "3×3": "双人床 / 土圆仓",
             "2×3": "本期未使用", "3×1": "本期未使用"}
for k in ("1×1", "1×2", "1×3", "2×1", "2×2", "2×3", "3×1", "3×2", "3×3"):
    n = sizes.get(k, 0)
    gw_, gh_ = k.split("×")
    w("| %s | %s×%s | %d | %s |" % (k, int(gw_) * TILE, int(gh_) * TILE, n, note_size.get(k, "")))
w("")
w("### 5.2 高频复用前 20（一件顶多处，先做）")
w("")
w("| 编号 | 文件 id | 资产名 | 格数 | 全项目出现 | 出现在 |")
w("|---|---|---|---|---|---|")
for r in props[:20]:
    w("| %s | `%s` | %s | %d×%d | %d 处 | %s |"
      % (r["code"], r["id"], r["name"], r["w"], r["h"], r["uses"],
         " / ".join(r["houses"])))
w("")
w("### 5.3 线索家具 12 件（剧情硬依赖，最优先）")
w("")
w("这 12 件是玩家的「可检视点」，橙框标在格图上。缺一件就断一条线索链。")
w("")
w("| 编号 | 文件 id | 资产名 | 格数 | 出现（线索落点） |")
w("|---|---|---|---|---|")
for r in props:
    if r["clue_houses"]:
        w("| %s | `%s` | %s | %d×%d | %s |"
          % (r["code"], r["id"], r["name"], r["w"], r["h"], " / ".join(r["clue_houses"])))
w("")
w("线索链（文案侧已写死，美术只管画够区分度）：")
w("")
w("- 假《水簿》→ 账桌（`zhangzhuo_1x2` / `zhangzhuo_2x1`）")
w("- 真本 → 墙基暗龛（`qiangji_ankan_1x2`）：A1 无、A2 空龛、A3 已出土")
w("- 上磨盘刻字 → 石磨（`shimo_2x2`）；A3 那块弃置在晒谷场（`qizhi_shimo_2x2`）")
w("- 周有田往来账 → 小桌（`xiaozhuo_2x1`）抽屉")
w("- 陆家十六两秤的秤砣 → 旧木箱（`jiu_muxiang_1x1`）")
w("- 周家书桌（`shuzhuo_1x1`）、沈家蜂窝煤炉（`fengwomeilu_1x1`）、"
  "陆家地基痕迹（`tangwu_diji_2x2`）、老井（`laojing_1x1`）、水泥封层（`shuini_fengceng_1x1`）")
w("")
w("### 5.4 全量清单（79 件，按编号）")
w("")
w("`院` = 院子里的；`◆` = 可检视线索；「全项目」= 三年里一共摆在几处（复用价值）。")
w("")
w("| 编号 | 文件 id | 资产名 | 格数 | px | 区 | 全项目 | 出现在 |")
w("|---|---|---|---|---|---|---|---|")
for r in props:
    w("| %s | `%s` | %s | %d×%d | %d×%d | %s | %d | %s |"
      % (r["code"], r["id"], r["name"], r["w"], r["h"], r["px"][0], r["px"][1],
         "院" if r["zone"] == "yard" else "屋", r["uses"], " / ".join(r["houses"])))
w("")
w("### 5.5 画家具的五个坑")
w("")
w("1. **高度可以多画一格**：星露谷那套画法会画出朝向观众的立面，所以 1×1 的凳子源图常常是 32×64。"
  "**占地按数据算，不看 PNG 像素**。—— 这条和外观层的「+32px」是同一个道理："
  "所有立体物都按 `(x, y − 高度)` 绘制，立面一律往上长。")
w("2. **锚点底部中心**：多出来的那一格往**上**长，不要往左右偏。")
w("3. **不要画地板 / 墙体**：家具图只含物件本身，底下的地板墙由 `base` 层出，否则叠两层会脏。")
w("4. **院子建筑（茅房 3×2）里还嵌了茅坑**：两件是分开的两个文件，茅房只画外壳和门，坑单独一层。")
w("5. **立面不要画细节**：2× 整数缩放下**一格只有星露谷 1/4 的像素**，砖缝 / 木纹 / 窗框会糊成噪点。"
  "只靠色阶分层：墙顶亮带 + 墙身 + 墙基暗带。外观层同理。")
w("")
w("## 6. 场景层：24 项")
w("")
w("尺寸全部按 `data/frames.json` 的实测几何换算，不是估算。")
w("")
w("| 编号 | 文件 id | 资产名 | 帧 | 格数 | px | 交付要求 |")
w("|---|---|---|---|---|---|---|")
for a in scene:
    w("| %s | `%s` | %s | %s %d | %d×%d | %d×%d | %s |"
      % (a["code"], a["id"], a["name"], a["frame"], YEAR[a["frame"]],
         a["w"], a["h"], a["px"][0], a["px"][1], a["note"]))
w("")
w("**省工建议**：河 / 坝 / 路 / 田在三帧里**几何完全相同，只有颜色不同**"
  "（河 `#3f5f6e`→`#3f5f6e`→`#4a6a60`，田 `#7d8a3e`→`#78863c`→`#6b6440`）。"
  "所以底图只要画一套，另外两帧用 tint 染色即可 —— 但**路要先做一套 32px 瓦片**"
  "（直 / 弯 / 丁字），因为 A1/A2 是弯的、A3 是直的，整张图对不上。")
w("")
w("跨帧变化最大的两件，优先级最高：")
w("")
w("- **老井 4 态**：开挖 → 封盖 → 锁死 → 水泥封（A1 木架 / A2 石板 / A3 三层水泥，是剧情主线）")
w("- **老槐 4 态**：树苗 / 中 / 大 / 树桩；三帧直径 2×2 → 4×4 → 6×6 格，跨帧差别最明显")
w("")
w("## 7. 建议排期（按依赖排，不按栋排）")
w("")
w("| 批次 | 内容 | 数量 | 累计 | 为什么排这里 |")
w("|---|---|---|---|---|")
w("| **P0** | 外观 `base` 12 张 + `roof` 11 张 | 23 | 23 | 现在游戏里房子全是色块；外观不落地，场地截图没法看 |")
w("| **P1** | 12 件线索家具（§5.3） | 12 | 35 | 剧情卡在这里；缺一件就断线索链 |")
w("| **P2** | 高频复用前 20 件（§5.2） | 19 | 54 | 一件顶 4~12 处，摆满全场最快见效；前 20 里有 1 件（P20 老井）已在 P1，本批只算新增 19 |")
w("| **P3** | 剩下 48 件家具 | 48 | 102 | 补齐细节；缺图有兜底，可以按栋分批进图 |")
w("| **P4** | 场景 24 项（§6），先出老井 4 态 + 老槐 4 态 | 24 | 126 | 底图可以先用具象色块顶着；老井 / 老槐是主线道具 |")
w("")
w("23 + 12 + 19 + 48 + 24 = **126**，和 §0 的总数对得上，没有重复计数。")
w("")
if HANDOFF:
    w("## 8. 关于这份清单")
    w("")
    w("本文由项目数据自动生成，和图片一起是**同一版数据的快照**。")
    w("房型 / 家具位置 / 线索若有调整，会重新生成整包发过来 —— 所以")
    w("**不要手改这份 md，也不要改图**，有疑问按 `README.md` 里留的方式反馈。")
else:
    w("## 8. 改数据后怎么重跑")
    w("")
    w("```powershell")
    w("$py = \"C:\\Users\\lyh\\.dsh\\dsh-runtimes\\dsh-primary-runtime\\dependencies\\python\\python.exe\"")
    w("$env:PYTHONIOENCODING = \"utf-8\"")
    w("& $py -X utf8 _ref\\houses\\gen_asset_breakdown.py   # 重出 13 张图 + csv + json")
    w("& $py -X utf8 _ref\\houses\\gen_art_doc.py           # 重出本文")
    w("& $py -X utf8 _ref\\houses\\gen_art_doc.py --handoff # 重出外发文件夹里的 00_总需求清单.md")
    w("& $py -X utf8 _ref\\houses\\gen_art_checklist.py     # 重出外发文件夹里的 02_交付登记表.csv")
    w("```")
    w("")
    w("真相源只有一个：`_ref/houses/houses_data.json`（房型 / 占地 / 家具 / 线索）"
      "+ `data/frames.json`（场景几何）。**本文和图片都是它的投影，不要手改。**")
w("")
w("## 9. 与既有规范的差异（需要同步给美术）")
w("")
w("1. `docs/house-spec.md` §5 原写「每族一份 `props/`」，本清单改成"
  "**全项目共享 `assets/village/props/<文件 id>.png`**。理由：79 个素材跨最多 8 栋复用，"
  "按族拆会膨胀成 178 个重复文件。")
w("2. 外观只交 `base` + `roof` 两层（`props` 由家具层承担），与 §4.5 三层表一致；"
  "但交付目录用 `assets/village/houses/<族>/<a1|a2|a3>_base.png`（**帧前缀在文件名里**，"
  "因为同族三个时期要同时存在）。")
w("3. 陆家 A3 是唯一的废墟态（`ruin:true`）：只交 1 张，墙缺失处留透明让场景地面透出来，"
  "另有 70 格需要铺 32px 杂草素材（格图上绿框「草」标注）。")
w("")

open(DOC, "w", encoding="utf-8", newline="\n").write("\n".join(L))
print("wrote", DOC, len(L), "lines")
