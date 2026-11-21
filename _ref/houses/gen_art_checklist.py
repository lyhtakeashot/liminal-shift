# -*- coding: utf-8 -*-
"""由 _a1a3_assets.csv + _a1a3_assets.json 生成 art-handoff/02_交付登记表.csv。

和 01_总需求清单.csv 的区别：那份是「要什么」，这份是「做到哪了」——
多出 批次 / 状态 / 负责人 / 完成日期 / 备注 五列，按 P0→P4 排好序，可以直接当进度表用。

批次口径与 00_总需求清单.md §7 一致，且不重复计数：
  P0 外观 23 / P1 线索家具 12 / P2 高频前 20 中扣掉已进 P1 的 1 件 = 19
  P3 其余家具 48 / P4 场景 24          合计 126
"""
import csv
import json
import os
import shutil
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ART = os.path.join(ROOT, "_ref", "art", "_assets_a1a3")
HANDOFF = os.path.join(ROOT, "art-handoff")
OUT = os.path.join(HANDOFF, "02_交付登记表.csv")

# 交付包里的 12 张单栋图 + 1 张场景图，都是 _ref 下生成产物的改名副本。
# 以前靠手工 Copy-Item，改完生成器忘了同步 → 包里留着旧尺寸的图。这里一并做掉。
FRAME_DIR = {"A1": "A1_1926", "A2": "A2_1951", "A3": "A3_1976"}
ORDER = [("A1", "lu_house"), ("A1", "mill_a1"), ("A1", "shen_a1"), ("A1", "zhou_house"),
         ("A2", "mill_a2"), ("A2", "shen_a2"), ("A2", "lu_a2"), ("A2", "zhou_a2"),
         ("A3", "mill_a3"), ("A3", "shen_a3"), ("A3", "zhou_a3"), ("A3", "lu_a3")]

rows = list(csv.DictReader(open(os.path.join(ART, "_a1a3_assets.csv"), encoding="utf-8-sig")))
d = json.load(open(os.path.join(ART, "_a1a3_assets.json"), encoding="utf-8"))
# 高频前 20 的口径：按实际摆放次数降序（同次数按编号），和文档 §5.2 一致
top20 = {p["code"] for p in sorted(d["props"], key=lambda r: (-r["uses"], r["code"]))[:20]}
# 外观行的 CSV 尺寸已是**画布**（含顶部 +16）；占地尺寸从 JSON 补，便于塌陷核对
lot_of = {s["id"]: (s["w"], s["h"], s["px"]) for s in d["shell"]}


def batch(r):
    cat = r["类别"]
    if cat.startswith("外观"):
        return ("P0", "外观")
    if cat.startswith("场景"):
        return ("P4", "场景")
    if r["线索"]:
        return ("P1", "线索家具")
    if r["编号"] in top20:
        return ("P2", "高频家具")
    return ("P3", "其余家具")


out = []
for r in rows:
    b, grp = batch(r)
    is_shell = r["类别"].startswith("外观")
    if is_shell:
        lot = lot_of.get(r["文件 id"], (0, 0, (0, 0)))
        sizetxt = "%sx%s（画布）｜占地 %dx%d" % (r["像素宽"], r["像素高"], lot[0], lot[1])
        note = "画布比占地高 16px（顶部一格是墙与屋顶立面）；" + r["说明"]
    else:
        sizetxt = "%sx%s" % (r["像素宽"], r["像素高"])
        note = r["说明"]
    out.append({
        "批次": b,
        "类别": grp,
        "编号": r["编号"],
        "文件 id": r["文件 id"],
        "资产名": r["资产名"],
        "格宽": r["格宽"],
        "格高": r["格高"],
        "像素": sizetxt,
        "交付路径": r["交付路径"],
        "线索": r["线索"],
        "说明": note,
        "状态": "待开工",
        "负责人": "",
        "完成日期": "",
        "备注": "",
    })
out.sort(key=lambda x: (x["批次"], x["类别"], x["编号"]))

with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    wr.writeheader()
    wr.writerows(out)

# 顺手把「要什么」那份总表也同步进交付包（它是 _a1a3_assets.csv 的原样副本，
# 之前靠手工复制，改完生成器忘了同步就会留着旧尺寸）。
shutil.copyfile(os.path.join(ART, "_a1a3_assets.csv"),
                os.path.join(HANDOFF, "01_总需求清单.csv"))

# 12 张单栋拆解图 + 1 张场景对比图（改名为 <id>_拆解图.png 方便美术一眼认）
for fr, hid in ORDER:
    os.makedirs(os.path.join(HANDOFF, FRAME_DIR[fr]), exist_ok=True)
    shutil.copyfile(os.path.join(ART, FRAME_DIR[fr], "%s_assets.png" % hid),
                    os.path.join(HANDOFF, FRAME_DIR[fr], "%s_拆解图.png" % hid))
shutil.copyfile(os.path.join(ART, "_scene_a1a3_assets.png"),
                os.path.join(HANDOFF, "00_场景元素_三帧对比.png"))

# 规范快照：docs/house-spec.md 是唯一的权威来源，包里那份只是只读副本
shutil.copyfile(os.path.join(ROOT, "docs", "house-spec.md"),
                os.path.join(HANDOFF, "90_参考规范", "house-spec.md"))

print("synced 01_总需求清单.csv + 12 张拆解图 + 场景图 + house-spec.md")

print("wrote", OUT, len(out), "rows", dict(sorted(Counter(o["批次"] for o in out).items())))
