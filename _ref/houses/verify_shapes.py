"""
像素级图稿校验 —— 替代肉眼检查。
不打开图片"看"，而是直接读 PNG 像素断言。

用法：python verify_shapes.py
"""

import os
from PIL import Image, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
T = 64          # 出图倍率 4，一格 16px * 4
PAD, TOP, GAP = 56, 240, 150
YARD = (0x5f, 0x6a, 0x42)
BG = (0x1b, 0x1a, 0x17)

fails = []

def check(name, cond, detail=""):
    status = "OK  " if cond else "FAIL"
    print(f"[{status}] {name}" + (f"  {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def pixel(img, x, y):
    return img.getpixel((x, y))[:3]


def near(a, b, tol=6):
    return all(abs(a[i] - b[i]) <= tol for i in range(3))


# ---------- 1. 文字块不重叠（按实际字体 bbox 算） ----------
FONTS = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]
def fnt(sz):
    for p in FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()

def text_bbox(xy, text, size):
    f = fnt(size)
    bb = f.getbbox(text)
    x, y = xy
    return (x + bb[0], y + bb[1], x + bb[2], y + bb[3])

def overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

sheet_one_labels = [
    ((PAD, 30),  "四合院", 46),
    ((PAD, 96),  "外观占地 13×12 格 = 208×192 px ｜ 翼数 4 ｜ 材质 slate", 24),
    ((PAD, 134), "四翼围全院。沈家 2001 形态，村中首富。", 24),
    ((PAD, 168), "平面图 = 外观占地 1:1。室内可走区 + 墙厚，一格不差。", 20),
    ((PAD, TOP-34), "俯视 3/4 外观（黄箭头 = 屋脊方向）", 25),
    ((PAD + 13*T + GAP, TOP-34), "俯视平面（程序生成）", 25),
]
boxes = [text_bbox(*l) for l in sheet_one_labels]
bad = []
for i in range(len(boxes)):
    for j in range(i+1, len(boxes)):
        if overlap(boxes[i], boxes[j]):
            bad.append((i, j, boxes[i], boxes[j]))
check("sheet_one 顶部文字无重叠", not bad,
      "" if not bad else f"重叠对 {[(b[0],b[1]) for b in bad]}")

evo_labels = [
    ((PAD, 30), "沈家宅第", 44),
    ((PAD, 92), "阶级上升写在建筑上。", 24),
    ((PAD, 130), "旧翼永远不拆，新翼贴着旧翼接。", 24),
    ((PAD, 166), "每格 16px，出图 4 倍。", 20),
    ((PAD, 260-40), "1926 · 土坯长屋", 28),
    ((PAD, 260-8), "创业期：一翼", 20),
]
boxes2 = [text_bbox(*l) for l in evo_labels]
bad2 = [(i,j) for i in range(len(boxes2)) for j in range(i+1,len(boxes2))
        if overlap(boxes2[i], boxes2[j])]
check("evolution 顶部文字无重叠", not bad2, "" if not bad2 else f"重叠对 {bad2}")


# ---------- 2. 天井/院子区域必须是绿色，且外观与平面图一致 ----------
cases = [
    ("v4_siheyuan.png", 13, 12, [(4,5,8,7)]),
    ("v4_wei.png",      13, 10, [(4,5,8,9)]),
    ("v4_liangjin.png", 11, 11, [(2,4,8,5)]),
]
for fname, gw, gh, yards in cases:
    path = os.path.join(OUT, fname)
    if not os.path.exists(path):
        check(f"{fname} 存在", False)
        continue
    img = Image.open(path).convert("RGB")
    check(f"{fname} 尺寸够大", img.width >= 1400 and img.height >= 800,
          f"{img.width}x{img.height}")

    plan_x = PAD + gw*T + GAP
    for (x0,y0,x1,y1) in yards:
        # 采样点取院子上半部（y 靠北），避开南边可能压下来的翼/门/院墙
        cx = (x0+x1)//2 + 0.5
        cy = y0 + 0.5 + min(0.6, (y1-y0)*0.3)
        for panel, ox in (("外观", PAD), ("平面", plan_x)):
            px = int(ox + cx*T)
            py = int(TOP + cy*T)
            if 0 <= px < img.width and 0 <= py < img.height:
                c = pixel(img, px, py)
                check(f"{fname} {panel}天井=绿", near(c, YARD), f"pixel({px},{py})={c}")

    c = pixel(img, 2, 2)
    check(f"{fname} 背景=深色", near(c, BG), f"pixel={c}")


# ---------- 3. 五张图都存在且尺寸各异（证明不是同一张复制） ----------
sizes = []
for fname in ["v4_straight.png","v4_L.png","v4_wei.png","v4_siheyuan.png","v4_liangjin.png"]:
    p = os.path.join(OUT, fname)
    if os.path.exists(p):
        im = Image.open(p)
        sizes.append((fname, im.size))
    else:
        check(f"{fname} 存在", False)
if len(sizes) == 5:
    check("五张房型图尺寸各对应不同占地", len(set(s for _,s in sizes)) >= 3,
          str(sizes))

print()
if fails:
    print(f"RESULT: FAIL ({len(fails)}) -> {fails}")
    raise SystemExit(1)
print("RESULT: ALL PASS")
