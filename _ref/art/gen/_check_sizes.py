# -*- coding: utf-8 -*-
"""交付总校验：对照 manifest 检查 assets/village/ 下所有交付文件的尺寸与覆盖度。

口径（DECIDE D6）：
  - shell：画布 = cw×32 × ch×32，manifest 的 `cpx` 就是像素尺寸，必须**完全相等**。
  - props：画布 = 占地宽×32 × (占地高×32 + 32)（源图多画一格立面）。
  - scene：画布 = manifest 的 `px`（场景贴图不额外加一格）。
"""
import json
import os
import sys

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
MANIFEST = os.path.join(ROOT, "_ref", "art", "_assets_a1a3", "_a1a3_assets.json")
TILE = 32


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


def check():
    man = json.load(open(MANIFEST, encoding="utf-8"))
    problems = []
    missing = []
    ok = 0

    # ---- shell：23 张，尺寸 = cpx ----
    for s in man["shell"]:
        path = os.path.join(ROOT, s["path"].replace("/", os.sep))
        if not os.path.exists(path):
            missing.append(("shell", s["id"], s["path"]))
            continue
        im = Image.open(path)
        want = tuple(s["cpx"])
        if im.size != want:
            problems.append(("shell", s["id"], s["path"], "want %sx%s" % want, "got %sx%s" % im.size))
        else:
            ok += 1

    # ---- props：84 张，尺寸 = (w*32) × (h*32 + 32) ----
    for p in man["props"]:
        path = os.path.join(ROOT, p["path"].replace("/", os.sep))
        if not os.path.exists(path):
            missing.append(("props", p["id"], p["path"]))
            continue
        im = Image.open(path)
        want = (p["w"] * TILE, p["h"] * TILE + TILE)
        if im.size != want:
            problems.append(("props", p["id"], p["path"], "want %sx%s" % want, "got %sx%s" % im.size))
        else:
            ok += 1

    # ---- scene：24 项（唯一路径 15 个），尺寸 = px ----
    seen = set()
    for s in man["scene"]:
        path = os.path.join(ROOT, s["path"].replace("/", os.sep))
        if path in seen:
            continue
        seen.add(path)
        if not os.path.exists(path):
            missing.append(("scene", s["id"], s["path"]))
            continue
        im = Image.open(path)
        want = tuple(s["px"])
        if im.size != want:
            problems.append(("scene", s["id"], s["path"], "want %sx%s" % want, "got %sx%s" % im.size))
        else:
            ok += 1

    print("=== 交付校验 ===")
    print("尺寸符合: %d" % ok)
    print("缺失: %d" % len(missing))
    for kind, i, p in missing:
        print("  [缺] %s %s -> %s" % (kind, i, p))
    print("尺寸不符: %d" % len(problems))
    for kind, i, p, w, g in problems:
        print("  [错] %s %s -> %s  %s  %s" % (kind, i, p, w, g))

    # ---- 反查：assets/village/ 下有没有 manifest 之外的交付文件 ----
    extra = []
    for base, _dirs, files in os.walk(os.path.join(ROOT, "assets", "village")):
        for f in files:
            if not f.endswith(".png"):
                continue
            rp = rel(os.path.join(base, f))
            if rp.startswith("assets/village/props/_") or rp == "assets/village/scene/tree_old_4x5.png":
                continue
            if rp.startswith("assets/village/houses/"):
                if rp not in {s["path"] for s in man["shell"]}:
                    extra.append(rp)
            elif rp.startswith("assets/village/props/"):
                if rp not in {p["path"] for p in man["props"]}:
                    extra.append(rp)
            elif rp.startswith("assets/village/scene/"):
                if rp not in {s["path"] for s in man["scene"]}:
                    extra.append(rp)
    print("manifest 之外的多余 PNG: %d" % len(extra))
    for e in sorted(extra):
        print("  [多] %s" % e)
    return 1 if (missing or problems) else 0


if __name__ == "__main__":
    sys.exit(check())
