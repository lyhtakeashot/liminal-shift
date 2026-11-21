"""List all furniture rows, including their href, for a chosen footprint."""
import re
from pathlib import Path
h = Path(__file__).with_name('furniture.html').read_text(encoding='utf-8', errors='replace')
# Match the <tr> row: capture name, size, and the sprite filename from the <img src>
pat = re.compile(r'<tr><td><a href="([^"]+/)"[^>]*><img[^>]*src="[^"]*?([^/"]+)\.png"[^>]*>\s*([^<]+?)</a><td><span>(\d+×\d+)</span>')
rows = pat.findall(h)
print('rows', len(rows))
for href, png, name, size in rows:
    if size == '3×1':
        print(f'{png:32} {name.strip()}')
