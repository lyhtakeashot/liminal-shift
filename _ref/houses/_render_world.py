# -*- coding: utf-8 -*-
"""A1/A2/A3 世界布局对照图生成器。

直接从 data/frames.json + _ref/houses/houses_data.json 读坐标，
用与游戏（scripts/world_view.gd + house_shape.gd）一致的规则渲染，
保证图和游戏里看到的是同一套坐标。

输出：_ref/art/_overview/world_a1.png / world_a2.png / world_a3.png
"""
import json, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(os.path.dirname(HERE), "art", "_overview")
TILE = 16
SCALE = 1          # 1600x900 原尺寸输出，像素与游戏 1:1

FONT_PATHS = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]

def font(sz):
    for p in FONT_PATHS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()

# ---- 与 house_shape.gd 一致的配色 ----
WALL_COLOR = "#8c6b4a"
WALL_TOP = "#c9a878"
DOOR_COLOR = "#e0b25a"
GATE_COLOR = "#9a6a3a"
LOT_OUTLINE = "#a8905a"
YARD_COLOR = "#3b3a2e"
FURN_COLOR = "#c8b48f"
FURN_EDGE = "#e8d7b2"
CLUE_COLOR = "#d98b45"
ROOM_COLORS = {
    "bed": "#9c8468", "hall": "#cbb997", "store": "#8d9a6f",
    "kitchen": "#bdd0b0", "account": "#a8c0d0", "yard": "#3b3a2e",
    "shop": "#b99aa6", "class": "#9dbacd", "mill": "#b5a878",
    "toilet": "#9aa8a8",
}

frames_doc = json.load(open(os.path.join(ROOT, "data", "frames.json"), encoding="utf-8"))
houses = json.load(open(os.path.join(HERE, "houses_data.json"), encoding="utf-8"))
by_id = {h["id"]: h for h in houses}


def build_grid(hs):
    X0, Y0, X1, Y1 = hs["lot"]
    interior = set()
    for (x, y, w, h) in hs["wings"]:
        for j in range(y + 1, y + h - 1):
            for i in range(x + 1, x + w - 1):
                interior.add((i, j))

    def is_wall(i, j):
        if (i, j) in interior:
            return False
        return any((i + di, j + dj) in interior
                   for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)))

    part = set()
    for (x1, y1, x2, y2) in hs.get("partitions", []):
        if x1 == x2:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                part.add((x1, y))
        else:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                part.add((x, y1))

    dset = set(tuple(d) for d in hs["doors"])
    gset = set(tuple(g) for g in hs.get("gate", []))
    rows = []
    for j in range(Y0, Y1 + 1):
        row = ""
        for i in range(X0, X1 + 1):
            c = (i, j)
            if c in gset:
                row += "G"
            elif c in dset:
                row += "D"
            elif c in part or is_wall(i, j):
                row += "#"
            elif c in interior:
                row += "."
            else:
                row += " "
        rows.append(row)
    return rows


def room_of(hs, gx, gy):
    for room in hs["rooms"]:
        x0, y0, x1, y1, name, ck = room[:6]
        if x0 <= gx <= x1 and y0 <= gy <= y1:
            return name, ck
    return None, None


def render(frame):
    W = frames_doc["world"]["width"]
    H = frames_doc["world"]["height"]
    img = Image.new("RGB", (W, H), frame.get("ground", "#6e7a4c"))
    d = ImageDraw.Draw(img, "RGBA")

    # ---------- 1. 非房子形状：河/坝/田/路 ----------
    for s in frame["shapes"]:
        t = s.get("type")
        col = s.get("color", "#888888")
        if t == "rect":
            x, y, w, h = s["rect"]
            d.rectangle([x, y, x + w, y + h], fill=col)
            lbl = s.get("label", "")
            if lbl:
                d.text((x + 4, y + 3), lbl, font=font(13), fill=(250, 250, 245))
        elif t == "circle":
            cx, cy = s["center"]
            r = s.get("radius", 4)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col,
                      outline="#c8c0b0", width=1)
            lbl = s.get("label", "")
            if lbl:
                d.text((cx + r + 3, cy - 8), lbl, font=font(12), fill=(248, 244, 232))
        elif t == "path":
            pts = [tuple(p) for p in s["points"]]
            d.line(pts, fill=col, width=s.get("width", 20), joint="curve")
            lbl = s.get("label", "")
            if lbl and len(pts) > 1:
                mx = sum(p[0] for p in pts) / len(pts)
                my = sum(p[1] for p in pts) / len(pts)
                d.text((mx - 8, my - 7), lbl, font=font(12), fill=(250, 240, 220))

    # ---------- 2. 房子：lot 底 / 房间 / 墙 / 门 / 家具 ----------
    for s in frame["shapes"]:
        if s.get("type") != "house":
            continue
        hid = s["id"]
        hs = by_id.get(hid)
        if hs is None:
            continue
        px, py = s["pos"]
        lot = hs["lot"]
        gw, gh = lot[2] - lot[0] + 1, lot[3] - lot[1] + 1
        lw, lh = gw * TILE, gh * TILE

        # lot 底色（院子）
        d.rectangle([px, py, px + lw, py + lh], fill=YARD_COLOR,
                    outline=LOT_OUTLINE, width=2)

        # 房间色块
        for room in hs["rooms"]:
            x0, y0, x1, y1, name, ck = room[:6]
            rc = ROOM_COLORS.get(ck, "#6b5842")
            d.rectangle([px + x0 * TILE, py + y0 * TILE,
                         px + (x1 + 1) * TILE, py + (y1 + 1) * TILE], fill=rc)

        # 墙 / 门
        grid = build_grid(hs)
        for j, row in enumerate(grid):
            for i, ch in enumerate(row):
                bx = px + (lot[0] + i - lot[0]) * TILE
                by = py + j * TILE
                box = [bx, by, bx + TILE - 1, by + TILE - 1]
                if ch == "#":
                    d.rectangle(box, fill=WALL_COLOR)
                    d.line([(bx, by), (bx + TILE - 1, by)], fill=WALL_TOP, width=2)
                elif ch == "D":
                    d.rectangle(box, fill=DOOR_COLOR)
                elif ch == "G":
                    d.rectangle(box, fill=GATE_COLOR)

        # 家具
        for f in hs["furniture"]:
            fx, fy, fw, fh = f["rect"]
            # 只画落在 lot 内的
            if fx < lot[0] or fy < lot[1] or fx + fw - 1 > lot[2] or fy + fh - 1 > lot[3]:
                continue
            bx = px + (fx - lot[0]) * TILE
            by = py + (fy - lot[1]) * TILE
            bw, bh = fw * TILE, fh * TILE
            fill = CLUE_COLOR if f.get("clue") else FURN_COLOR
            edge = CLUE_COLOR if f.get("clue") else FURN_EDGE
            d.rectangle([bx + 2, by + 2, bx + bw - 3, by + bh - 3],
                        fill=fill, outline=edge, width=1)
            if bw >= 24 and bh >= 14:
                d.text((bx + 4, by + 3), f.get("short", f["name"])[:4],
                       font=font(10), fill=(42, 30, 16))

        # 房子名
        d.text((px + 5, py + 4), hid, font=font(13), fill=(250, 240, 214))

    # ---------- 3. 检视点（手写地标）----------
    for h in frame.get("hotspots", []):
        x, y = h["pos"]
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 226, 120), outline=(60, 40, 10))

    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    names = [("a1_1926", "A1_1926"), ("a2_1951", "A2_1951"), ("a3_1976", "A3_1976")]
    for fid, tag in names:
        fr = next((f for f in frames_doc["frames"] if f["id"] == fid), None)
        if fr is None:
            print("missing frame", fid)
            continue
        img = render(fr)
        p = os.path.join(OUT, "world_%s.png" % tag.lower())
        img.save(p)
        print("saved", p, img.size)


if __name__ == "__main__":
    main()
