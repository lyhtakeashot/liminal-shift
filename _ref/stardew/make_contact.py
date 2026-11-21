"""
把 B 站教程抽帧拼成带时间标注的联系表。
当前模型看不到图片，交给用户自己看：哪一段是星露谷建筑素材。
"""
import os, glob, re
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))

FONTS = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]
def fnt(sz):
    for p in FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()

files = sorted(glob.glob(os.path.join(OUT, "scan_*.jpg")),
               key=lambda p: int(re.search(r"scan_(\d+)", p).group(1)))
COLS = 4
CW, CH = 480, 270 + 30
rows = (len(files) + COLS - 1) // COLS

sheet = Image.new("RGB", (COLS*CW, rows*CH + 70), (24, 23, 20))
d = ImageDraw.Draw(sheet)
d.text((16, 12), "星露谷像素画尺寸教程 · 抽帧联系表（每 15 秒一帧，BV1CW4y1s7fC）",
       font=fnt(26), fill=(226, 218, 200))
d.text((16, 44), "原始视频已下载到 _ref/stardew/tutorial.mp4；找到感兴趣的秒数可用 ffmpeg 抽高清帧",
       font=fnt(17), fill=(150, 142, 128))

for i, p in enumerate(files):
    im = Image.open(p).convert("RGB")
    im.thumbnail((CW - 8, CH - 34))
    x = (i % COLS) * CW + 4
    y = (i // COLS) * CH + 70
    sec = (int(re.search(r"scan_(\d+)", p).group(1)) - 1) * 15
    sheet.paste(im, (x, y + 28))
    d.text((x + 4, y + 4), f"{sec//60:02d}:{sec%60:02d}", font=fnt(18), fill=(255, 220, 140))
    d.rectangle([x, y+28, x+im.width, y+28+im.height], outline=(70, 66, 58))

out = os.path.join(OUT, "contact_sheet.jpg")
sheet.save(out, quality=90)
print("saved", out, sheet.size, "frames", len(files))
