# -*- coding: utf-8 -*-
"""生成对照预览：同学图（左） vs AI 图（右），标 id 与尺寸。

_classmate_compare_a.png —— A 档（单件家具）每个主图 id 一格
_classmate_compare_b.png —— B 档（图集切片）每条切片一格
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = r"D:\Desktop\VibeCoding\godot_project\github_game_off_shift\shift"
LAB = os.path.join(ROOT, "lab")
CL = os.path.join(ROOT, "assets", "village", "_classmate", "props")
AI = os.path.join(ROOT, "assets", "village", "props")
TILE = 32

# 中文字体（默认位图字体画不出中文，会变成方块）
FONT_CANDIDATES = [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf",
                   r"C:\Windows\Fonts\simsun.ttc"]


def font(size):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


F_ID = font(13)
F_SM = font(10)
F_TINY = font(9)


def load(p):
    return Image.open(p).convert("RGBA")


def on_bg(im, bg=(96, 96, 112, 255)):
    b = Image.new("RGBA", im.size, bg)
    b.alpha_composite(im)
    return b.convert("RGB")


def cell(cls_id, cl_path, ai_path, note, cw=170, ch=200):
    """一格：左=同学图，右=AI图。"""
    im = Image.new("RGB", (cw, ch), (26, 26, 34))
    d = ImageDraw.Draw(im)
    half = cw // 2
    d.text((4, 3), cls_id, fill=(255, 224, 138), font=F_ID)
    for i, (path, tag) in enumerate([(cl_path, "同学"), (ai_path, "AI")]):
        x0 = i * half
        if path and os.path.exists(path):
            s = load(path)
            k = max(1, min(5, int((ch - 78) / max(s.size))))
            s2 = s.resize((s.width * k, s.height * k), Image.NEAREST)
            bg = on_bg(s2)
            im.paste(bg, (x0 + (half - bg.width) // 2, 40 + (ch - 40 - bg.height) // 2))
            d.text((x0 + 3, 25), "%s %dx%d" % (tag, s.size[0], s.size[1]),
                   fill=(140, 210, 255), font=F_SM)
        else:
            d.text((x0 + 3, 25), "%s 无" % tag, fill=(190, 120, 120), font=F_SM)
        d.line([(x0, 0), (x0, ch)], fill=(60, 60, 76))
    # 源文件说明（两行）
    for j, seg in enumerate(wrap_cn(note, 17)[:2]):
        d.text((4, ch - 26 + j * 12), seg, fill=(170, 170, 190), font=F_TINY)
    d.rectangle([0, 0, cw - 1, ch - 1], outline=(66, 66, 84))
    return im


def wrap_cn(text, width):
    """按显示宽度折行（中文按 1，ASCII 英文按 0.55 折算）。"""
    out, cur, w = [], "", 0.0
    for ch in text:
        cw = 0.55 if ord(ch) < 128 else 1.0
        if w + cw > width:
            out.append(cur)
            cur, w = "", 0.0
        cur += ch
        w += cw
    if cur:
        out.append(cur)
    return out


def sheet(cells, path, cols=6, title=None):
    cw, ch = cells[0].size
    rows = (len(cells) + cols - 1) // cols
    head = 30 if title else 0
    out = Image.new("RGB", (cols * cw, rows * ch + head), (18, 18, 24))
    if title:
        ImageDraw.Draw(out).text((8, 8), title, fill=(255, 224, 138), font=F_ID)
    for i, c in enumerate(cells):
        out.paste(c, ((i % cols) * cw, head + (i // cols) * ch))
    out.save(path)
    print("saved", path, out.size, len(cells))


def main():
    # ---- A 档：每个主图 id 一格 ----
    a_map = json.load(open(os.path.join(LAB, "_cls_map_a.json"), encoding="utf-8"))
    cells = []
    for r in a_map["rows"]:
        if r["role"] != "主图":
            continue
        cl = os.path.join(CL, "%s.png" % r["id"])
        ai = os.path.join(AI, "%s.png" % r["id"])
        note = "源:%s 置信:%s %s" % (r["src"].replace("美术资产/家具/", ""), r["conf"], r["note"])
        cells.append(cell(r["id"], cl, ai, note))
    sheet(cells, os.path.join(LAB, "_classmate_compare_a.png"),
          title="A 档 · 单件家具主图（19） 左=同学手绘  右=AI 程序化图")

    # ---- A 档变体 ----
    vcells = []
    for r in a_map["rows"]:
        if r["role"] != "变体":
            continue
        cl = os.path.join(ROOT, r["out"].replace("/", os.sep))
        ai = os.path.join(AI, "%s.png" % r["id"])
        note = "源:%s 置信:%s %s" % (r["src"].replace("美术资产/家具/", ""), r["conf"], r["note"])
        vcells.append(cell(r["id"] + " 变体", cl, ai, note))
    if vcells:
        sheet(vcells, os.path.join(LAB, "_classmate_compare_a2.png"), cols=4,
              title="A 档 · 同学图变体（%d）右列=AI 同 id 主图" % len(vcells))

    # ---- B 档：每条切片一格 ----
    b_map = json.load(open(os.path.join(LAB, "_cls_map_b.json"), encoding="utf-8"))
    cells = []
    for r in b_map:
        cl = os.path.join(ROOT, r["out"].replace("/", os.sep))
        ai = os.path.join(AI, "%s.png" % r["id"])
        note = "源:%s #%d 角色:%s" % (r["atlas"].replace("_32x32.png", ""), r["idx"], r["role"])
        cells.append(cell(r["id"], cl, ai, note))
    sheet(cells, os.path.join(LAB, "_classmate_compare_b.png"), cols=5,
          title="B 档 · 图集切片（%d）左=同学切图 右=AI 程序化图" % len(cells))


if __name__ == "__main__":
    main()
