"""Parse teemo.dev Stardew furniture HTML into size buckets."""
import re
from collections import defaultdict
from pathlib import Path

html = Path(__file__).with_name('furniture.html').read_text(encoding='utf-8', errors='replace')
# Row shape: <a href="glyph/"><img ...> Glyph</a><td><span>1×1</span>
rows = re.findall(r'<a href="[^"]*/"><img[^>]*>\s*([^<]+?)</a><td><span>(\d+×\d+)</span>', html)
buckets = defaultdict(list)
for name, size in rows:
    buckets[size].append(name.strip())
print(f"TOTAL ROWS: {len(rows)}")
for size in sorted(buckets, key=lambda s: (int(s.split('×')[0]), int(s.split('×')[1]))):
    names = buckets[size]
    print(f"{size}: {len(names)}")
    for n in names[:12]:
        print(f"  - {n}")
