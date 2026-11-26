# -*- coding: utf-8 -*-
"""把 tools/gen_voice_tts.py 的 28 句台词按【人物】拆成纯文本，供网页 TTS 站粘贴。

2026-11-26 修正：原先按「场景」拆，配音时同一个人的声音会在 7 场之间来回换，
游戏里听不出谁是谁。改为按人拆 —— 一个人一份文件、一段提示词、一次配完。

产出 assets/audio_raw/_split/：
  W1.txt / W2.txt / M1.txt / M2.txt / W3.txt / M3.txt   每行一句
  MAP.csv   人物 ↔ 组内序号 ↔ 输出文件名 ↔ 场景 ↔ 台词
  ALL.txt   28 句一句一行（备用）
"""
import io
import os
import sys

sys.path.insert(0, os.path.abspath("tools"))
sys.stdout.reconfigure(encoding="utf-8")

import gen_voice_tts as G

OUT = os.path.join("assets", "audio_raw", "_split")
os.makedirs(OUT, exist_ok=True)

# 人物表：代号 -> (描述, 该人负责的 (scene, idx))
CAST = [
    ("W1", "农妇甲 · 1926 二十出头 → 1951 四十五六 → 1976 七十（同一个人在变老）",
     [("a1_bang", 0), ("a1_bang", 2), ("a2_well", 0), ("a2_well", 2), ("a3_field", 0), ("a3_field", 2)]),
    ("W2", "农妇乙 · 同上一同变老（另一个农妇，声音比甲低厚）",
     [("a1_bang", 1), ("a1_bang", 3), ("a2_well", 1), ("a2_well", 3), ("a3_field", 1), ("a3_field", 3)]),
    ("M1", "男声甲 · 1951 农民 / 2001 工地工人（三十到四十多岁的农村男声）",
     [("a2_field", 0), ("a2_field", 2), ("a4_site", 0), ("a4_site", 2), ("a4_field", 1), ("a4_field", 3)]),
    ("M2", "男声乙 · 1951 农民 / 2001 工地工人（比甲沉、慢）",
     [("a2_field", 1), ("a2_field", 3), ("a4_site", 1), ("a4_site", 3), ("a4_field", 0), ("a4_field", 2)]),
    ("W3", "2026 本地老太太（六十多岁，与 1926 农妇甲不是同一个人）",
     [("a5_road", 0), ("a5_road", 2)]),
    ("M3", "2026 年轻居民（二十多岁，普通话）",
     [("a5_road", 1), ("a5_road", 3)]),
]

SCENE_NAME = {
    "a1_bang": "1926 坝上·赔偿", "a2_well": "1951 老井边·天灾",
    "a3_field": "1976 田边·遗忘", "a2_field": "1951 田边·激情案一",
    "a4_site": "2001 超市工地外·迷信", "a4_field": "2001 田边·激情案二",
    "a5_road": "2026 路口·邪门",
}

by_key = {}
for scene, idx, voice, rate, pitch, text in G.LINES:
    by_key[(scene, idx)] = (voice, text)

rows = []
for code, desc, keys in CAST:
    lines = []
    for i, (scene, idx) in enumerate(keys, 1):
        voice, text = by_key[(scene, idx)]
        lines.append(text)
        rows.append((code, i, "%s_%d" % (scene, idx), SCENE_NAME[scene], voice, text))
    p = os.path.join(OUT, code + ".txt")
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("  %s.txt  %d 句  %s" % (code, len(lines), desc))

with io.open(os.path.join(OUT, "ALL.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(r[5] for r in rows) + "\n")

with io.open(os.path.join(OUT, "MAP.csv"), "w", encoding="utf-8-sig", newline="\n") as f:
    f.write("人物,序号,输出文件名,场景,原音色,台词\n")
    for code, i, name, scene, voice, text in rows:
        f.write('%s,%d,%s,%s,%s,"%s"\n' % (code, i, name, scene, voice.replace("zh-CN-", ""), text))

print("\n合计 %d 句 / %d 个人 → %s" % (len(rows), len(CAST), OUT))