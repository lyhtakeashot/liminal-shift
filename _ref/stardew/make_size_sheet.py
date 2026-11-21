"""Generate a 3x3 furniture size reference sheet from downloaded Stardew sprites.

Each sprite from teemo.dev is rendered at 48 px/tile (3x the 16 px in-game tile).
Sheet keeps that scale so sprites sit exactly on the 48 px grid overlay.

IMPORTANT (learned while building this): a furniture sprite's IMAGE height is
usually 1 tile taller than its FOOTPRINT, because Stardew draws the south-facing
elevation of the object. Image size != footprint. The green box = real footprint.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

base = Path(__file__).resolve().parent
size_dir = base / 'sizes'
out = base / 'stardew_9sizes.png'

# (label, sprite filename, footprint w,h, real name)
items = [
    ('1x1', 'glyph',              1, 1, 'Glyph 墙饰'),
    ('1x2', 'binary',             1, 2, 'Binary 挂画'),
    ('1x3', 'clouds-banner',      1, 3, 'Clouds Banner 竖幅'),
    ('2x1', 'elixir-shelf',       2, 1, 'Elixir Shelf 药架'),
    ('2x2', '1000-years-from-now',2, 2, '1000 Years 挂画'),
    ('2x3', 'decorative-door',    2, 3, 'Decorative Door 门'),
    ('3x1', 'doghouse',           3, 1, 'Doghouse 狗窝'),
    ('3x2', 'groovy',             3, 2, 'Groovy 挂画'),
    ('3x3', 'exotic-palace',      3, 3, 'Exotic Palace 地毯'),
]

TILE = 48
PAD = 16
CELL_W = 3 * TILE + PAD * 2
GRID_H = 3 * TILE
LABEL_H = 46
CELL_H = PAD + GRID_H + LABEL_H
font_path = Path(r'C:\Windows\Fonts\msyh.ttc')
try:
    font = ImageFont.truetype(str(font_path), 15)
    font_small = ImageFont.truetype(str(font_path), 12)
except OSError:
    font = ImageFont.load_default()
    font_small = font

sheet = Image.new('RGB', (CELL_W * 3, CELL_H * 3), (245, 243, 236))
draw = ImageDraw.Draw(sheet)

for idx, (label, fname, w, h, desc) in enumerate(items):
    col, row = idx % 3, idx // 3
    ox, oy = col * CELL_W, row * CELL_H
    draw.rectangle([ox + 2, oy + 2, ox + CELL_W - 3, oy + CELL_H - 3],
                   outline=(190, 182, 160), width=2)

    gx, gy = ox + PAD, oy + PAD
    for ty in range(3):
        for tx in range(3):
            fill = (222, 232, 210) if tx < w and ty < h else (235, 232, 224)
            draw.rectangle([gx + tx * TILE, gy + ty * TILE,
                            gx + (tx + 1) * TILE - 1, gy + (ty + 1) * TILE - 1],
                           fill=fill, outline=(205, 200, 188))
    draw.rectangle([gx, gy, gx + w * TILE - 1, gy + h * TILE - 1],
                   outline=(105, 145, 85), width=3)

    sprite = Image.open(size_dir / f'{fname}.png').convert('RGBA')
    sheet.paste(sprite, (gx, gy), sprite)

    ly = oy + PAD + GRID_H + 4
    draw.text((ox + PAD, ly), f'{label}  ({w*16}x{h*16}px)  {desc}',
              font=font, fill=(55, 48, 38))
    sw, sh = sprite.size
    note = f'源图 {sw//48}x{sh//48} 格 (含立面)'
    if sh > h * TILE:
        note += ' ≠ 占地'
    draw.text((ox + PAD, ly + 20), note, font=font_small, fill=(150, 90, 60))

# Legend strip at the very bottom
ly = CELL_H * 3 + 6
sheet2 = Image.new('RGB', (CELL_W * 3, CELL_H * 3 + 34), (245, 243, 236))
sheet2.paste(sheet, (0, 0))
d2 = ImageDraw.Draw(sheet2)
d2.text((10, ly), '绿框 = 占地格数(footprint)  |  1 格 = 16px 游戏内  |  米色格 = 家具图多画的立面，不算占地',
        font=font_small, fill=(80, 72, 58))
sheet2.save(out)
print(f'SAVED {out}  {sheet2.size[0]}x{sheet2.size[1]}')
