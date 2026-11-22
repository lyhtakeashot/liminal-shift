# -*- coding: utf-8 -*-
"""给 manifest 增加美术同学资产的 7 个新 props id（用户拍板：加新 id）。

只做「追加」，不改动任何既有条目：
  - _ref/art/_assets_a1a3/_a1a3_assets.json  （CRLF，indent=1，无尾换行 —— 原样保真）
  - _ref/art/_assets_a1a3/_a1a3_assets.csv   （UTF-8 BOM，CRLF）

新 id 的 path 指向暂存目录 assets/village/_classmate/props/<id>.png
（尚未经本人拍板替换，故不进 assets/village/props/）。
"""
import json
import os

ROOT = r"D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift"
MAN = os.path.join(ROOT, "_ref", "art", "_assets_a1a3", "_a1a3_assets.json")
CSV = os.path.join(ROOT, "_ref", "art", "_assets_a1a3", "_a1a3_assets.csv")

# id, 资产名, 简称, w, h, zone, 说明
NEW = [
    ("xiaozhuo_1x1",    "小方桌",       "方桌",   1, 1, "house", "素木小方桌，无装饰；美术同学新图（1×1 占地）"),
    ("hongzhuo_1x1",    "红绸桌",       "红桌",   1, 1, "house", "铺红绸的方桌（喜桌/祭桌）；美术同学新图（1×1 占地）"),
    ("baizhuo_1x1",     "白布桌",       "白桌",   1, 1, "house", "铺白桌布的方桌（供桌）；美术同学新图（1×1 占地）"),
    ("shuzhuo_1x1_top", "书桌（俯视）", "书桌",   1, 1, "house", "俯视角度的书桌，桌上摊纸笔；美术同学新图（1×1 占地）"),
    ("gui_1x1",         "矮柜",         "矮柜",   1, 1, "house", "两层抽屉矮柜；美术同学新图（1×1 占地）"),
    ("changzhuo_2x1",   "长桌",         "长桌",   2, 1, "house", "长条木桌；美术同学新图（2×1 占地）"),
    ("cantang_3x1",     "餐桌",         "餐桌",   3, 1, "house", "长桌 + 两侧小凳的整套餐桌；美术同学新图（3×1 占地）"),
]


def main():
    raw = open(MAN, encoding="utf-8", newline="").read()
    man = json.loads(raw)

    have = {p["id"] for p in man["props"]}
    codes = {p["code"] for p in man["props"]}
    nxt = max(int(c[1:]) for c in codes if c.startswith("P")) + 1

    added = []
    for pid, name, short, w, h, zone, desc in NEW:
        if pid in have:
            print("已存在，跳过:", pid)
            continue
        code = "P%02d" % nxt
        nxt += 1
        man["props"].append({
            "id": pid,
            "name": name,
            "short": short,
            "w": w,
            "h": h,
            "px": [w * 32, h * 32],
            "layer": "props",
            "zone": zone,
            "yard_building": False,
            "uses": 0,
            "houses": [],
            "clue_houses": [],
            "path": "assets/village/_classmate/props/%s.png" % pid,
            "notes": [desc, "美术同学资产导入适配线（2026-11-22）；暂存于 _classmate/，待拍板后再进 props/"],
            "code": code,
        })
        added.append((code, pid, name, w, h, zone, desc))

    out = json.dumps(man, ensure_ascii=False, indent=1)
    # 保真：原文件用 CRLF、无尾换行
    out = out.replace("\n", "\r\n")
    open(MAN, "w", encoding="utf-8", newline="").write(out)

    # ---- CSV 追加 ----
    with open(CSV, encoding="utf-8-sig", newline="") as f:
        lines = f.read().split("\r\n")
    lines = [l for l in lines if l != ""]
    header = lines[0]
    for code, pid, name, w, h, zone, desc in added:
        row = ",".join([
            code, "家具·室内", pid, name, str(w), str(h), str(w * 32), str(h * 32),
            "assets/village/_classmate/props/%s.png" % pid, "", "0", "",
            desc + "；美术同学资产导入适配线（2026-11-22），暂存 _classmate/ 待拍板",
        ])
        lines.append(row)
    with open(CSV, "w", encoding="utf-8-sig", newline="") as f:
        f.write("\r\n".join(lines) + "\r\n")

    print("新增 id %d 个:" % len(added))
    for a in added:
        print("  ", a[0], a[1], a[2], "%dx%d" % (a[3], a[4]))

    # ---- 回读校验 ----
    m2 = json.load(open(MAN, encoding="utf-8"))
    print("回读 props 总数:", len(m2["props"]))
    ids = {p["id"] for p in m2["props"]}
    print("7 个新 id 全部在 manifest:", all(a[1] in ids for a in added))
    print("既有 id 未丢失:", len(ids) == len(m2["props"]))


if __name__ == "__main__":
    main()
