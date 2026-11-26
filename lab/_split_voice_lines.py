# -*- coding: utf-8 -*-
"""把 tools/gen_voice_tts.py 的 28 句台词拆成按音色分组的纯文本，供网页 TTS 站粘贴。

产出 assets/audio_raw/_split/：
  W1.txt .. M2.txt   每行一句（顺序即下表），粘一次生成一句
  MAP.csv            行号 ↔ 输出文件名 ↔ 台词
  ALL.txt            28 句一句一行（不分音色，备用）
"""
import io
import os
import sys

sys.path.insert(0, os.path.abspath("tools"))
sys.stdout.reconfigure(encoding="utf-8")

# 直接从 gen_voice_tts.py 取表，避免两处台词不一致
import gen_voice_tts as G

OUT = os.path.join("assets", "audio_raw", "_split")
os.makedirs(OUT, exist_ok=True)

# edge 音色 → 网页站上的「同角色」代号（给人看）
VOICE_GROUP = {
    "zh-CN-XiaoxiaoNeural": ("W1", "女声 A（1926 年轻农妇 → 逐帧变老）"),
    "zh-CN-XiaoyiNeural":   ("W2", "女声 B（1926 年轻农妇 → 逐帧变老）"),
    "zh-CN-YunxiNeural":    ("M1", "男声 A（2001 工人 / 1951 村民）"),
    "zh-CN-YunjianNeural":  ("M2", "男声 B（2001 工人 / 1951 村民）"),
}

groups = {}
rows = []
for scene, idx, voice, rate, pitch, text in G.LINES:
    g, desc = VOICE_GROUP[voice]
    n = len(groups.setdefault(g, [])) + 1
    groups[g].append(text)
    rows.append((g, n, "%s_%d" % (scene, idx), text, desc))

for g, lines in groups.items():
    p = os.path.join(OUT, g + ".txt")
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("  %s.txt  %d 句" % (g, len(lines)))

with io.open(os.path.join(OUT, "ALL.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(r[3] for r in rows) + "\n")

with io.open(os.path.join(OUT, "MAP.csv"), "w", encoding="utf-8-sig", newline="\n") as f:
    f.write("组,组内序号,输出文件名,角色,台词\n")
    for g, n, name, text, desc in rows:
        f.write("%s,%d,%s,%s,%s\n" % (g, n, name, desc, text))

print("\n合计 %d 句 → %s" % (len(rows), OUT))