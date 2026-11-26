"""旁听人声 · 第 1 步：用 edge-tts（微软 Edge 在线神经 TTS，免费无 key）生成原始语音。

用法（需要联网 + 一次 pip install）：

    pip install edge-tts
    python tools/gen_voice_tts.py            # 生成缺的
    python tools/gen_voice_tts.py --force    # 全部重生成
    python tools/gen_voice_tts.py --list     # 只列音色，不生成

产出：assets/audio_raw/tts/<scene>_<n>.mp3   （28 条，7 场景 × 4 行）
目录带 .gdignore，Godot 不会导入原始素材。

台词逐字抄自 docs/npc.md §5.5，一个字都不许改（改了就是改剧情）。
提示词里「甲：」「乙：」前缀不念，只念后面的正文。

配音表的设计意图（别改）：
  1926 → 1951 → 1976 三个年代的农妇是「同一批人在变老」，
  所以逐帧降速（rate）与降调（pitch）——这是本作「时间可动、人不可留」的听觉注释。
  2001 / 2026 换成另一组人（不同家族、不同性别构成），音色必须能听出「不是同一拨」。
"""

import argparse
import asyncio
import os
import sys

OUT_DIR = os.path.join("assets", "audio_raw", "tts")

# (scene, idx, voice, rate, pitch, text)
#   scene 与 data/frames.json 的 hearsay 场景 id 一致
#   voice 见 edge-tts 的 zh-CN 音色表；rate/pitch 必须带符号
LINES = [
    # ── A1 · 1926 · 坝上（两个年轻农妇，当场：赔偿）────────────────
    ("a1_bang", 0, "zh-CN-XiaoxiaoNeural", "+0%",  "+2Hz", "沈家赔了三十块洋钿。"),
    ("a1_bang", 1, "zh-CN-XiaoyiNeural",   "-5%",  "-2Hz", "三十块？不少了。"),
    ("a1_bang", 2, "zh-CN-XiaoxiaoNeural", "+0%",  "+2Hz", "仁至义尽。陆家也认了。"),
    ("a1_bang", 3, "zh-CN-XiaoyiNeural",   "-5%",  "-2Hz", "认了就好。这年头，肯赔钱的主儿不多。"),

    # ── A2 · 1951 · 老井边（同一批人，老了 25 年；天灾化）──────────
    ("a2_well", 0, "zh-CN-XiaoxiaoNeural", "-12%", "-10Hz", "民国十五年那场大水，你还记得？"),
    ("a2_well", 1, "zh-CN-XiaoyiNeural",   "-10%", "-8Hz",  "记得。冲走了陆家一个后生。"),
    ("a2_well", 2, "zh-CN-XiaoxiaoNeural", "-12%", "-10Hz", "听说就是那么没的。"),
    ("a2_well", 3, "zh-CN-XiaoyiNeural",   "-10%", "-8Hz",  "可不就是。水嘛，说来就来。"),

    # ── A3 · 1976 · 田边（同一批人，又老 25 年；遗忘化）────────────
    ("a3_field", 0, "zh-CN-XiaoxiaoNeural", "-18%", "-25Hz", "老辈子的事，谁还记得。"),
    ("a3_field", 1, "zh-CN-XiaoyiNeural",   "-16%", "-22Hz", "我阿爸提过一句，说陆家……"),
    ("a3_field", 2, "zh-CN-XiaoxiaoNeural", "-18%", "-25Hz", "提什么提。地里的活还没干完。"),
    ("a3_field", 3, "zh-CN-XiaoyiNeural",   "-16%", "-22Hz", "也是。"),

    # ── A4 · 2001 · 超市工地外（男人们；迷信化）──────────────────
    ("a4_site", 0, "zh-CN-YunxiNeural",    "-5%",  "-5Hz", "这地基底下好像有东西。"),
    ("a4_site", 1, "zh-CN-YunjianNeural",  "-12%", "-6Hz", "什么东西？"),
    ("a4_site", 2, "zh-CN-YunxiNeural",    "-5%",  "-5Hz", "老人都这么说。挖的时候别往西边深了。"),
    ("a4_site", 3, "zh-CN-YunjianNeural",  "-12%", "-6Hz", "那就别挖了呗。"),

    # ── A5 · 2026 · 路口（现代年长者 + 年轻居民；邪门化）──────────
    ("a5_road", 0, "zh-CN-XiaoxiaoNeural", "-6%",  "-5Hz", "这路口老塌。"),
    ("a5_road", 1, "zh-CN-YunxiNeural",    "+2%",  "+2Hz", "年年补，年年塌。"),
    ("a5_road", 2, "zh-CN-XiaoxiaoNeural", "-6%",  "-5Hz", "邪门。"),
    ("a5_road", 3, "zh-CN-YunxiNeural",    "+2%",  "+2Hz", "邪门。"),

    # ── A2 · 1951 · 田边 · 激情案（两个男人，细节全对）────────────
    ("a2_field", 0, "zh-CN-YunxiNeural",   "-4%",  "-4Hz", "西头两户为地界打起来了。"),
    ("a2_field", 1, "zh-CN-YunjianNeural", "-8%",  "-6Hz", "动锄头了？判了几年？"),
    ("a2_field", 2, "zh-CN-YunxiNeural",   "-4%",  "-4Hz", "动了。三号下午，姓王的先抡的。"),
    ("a2_field", 3, "zh-CN-YunjianNeural", "-8%",  "-6Hz", "判了三年，当场就判了，人证物证都在。"),

    # ── A4 · 2001 · 田边 · 激情案（两个男人，细节全对）────────────
    ("a4_field", 0, "zh-CN-YunjianNeural", "-6%",  "-6Hz", "邻村为水渠打人那事，你还记得？"),
    ("a4_field", 1, "zh-CN-YunxiNeural",   "-2%",  "-3Hz", "记得。七号那天，李家老二动的手。"),
    ("a4_field", 2, "zh-CN-YunjianNeural", "-6%",  "-6Hz", "判了七年。"),
    ("a4_field", 3, "zh-CN-YunxiNeural",   "-2%",  "-3Hz", "对，七年。全村都知道。"),
]


async def _gen(edge_tts, scene, idx, voice, rate, pitch, text, force):
    out = os.path.join(OUT_DIR, "%s_%d.mp3" % (scene, idx))
    if os.path.exists(out) and not force:
        return out, os.path.getsize(out), "skip"
    comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await comm.save(out)
    return out, os.path.getsize(out), "new"


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="已有文件也重新生成")
    ap.add_argument("--list", action="store_true", help="只列 zh-CN 音色")
    args = ap.parse_args()

    try:
        import edge_tts
    except ImportError:
        sys.exit("缺 edge-tts。先跑：\n    pip install edge-tts\n"
                 "（需要联网；装完再跑本脚本）")

    if args.list:
        voices = await edge_tts.list_voices()
        for v in voices:
            if v["Locale"].startswith("zh-CN"):
                print("%-32s %s  %s" % (v["ShortName"], v["Gender"], v.get("VoiceTag", {}).get("VoicePersonalities", [])))
        return

    os.makedirs(OUT_DIR, exist_ok=True)
    ok = fail = 0
    for scene, idx, voice, rate, pitch, text in LINES:
        try:
            path, size, state = await _gen(edge_tts, scene, idx, voice, rate, pitch, text, args.force)
            if size < 1000:
                raise RuntimeError("产出的文件只有 %d 字节，像失败了" % size)
            print("  %-12s %-3s %-28s %7d B  %s" % (scene, idx, voice.replace("zh-CN-", "").replace("Neural", ""), size, state))
            ok += 1
        except Exception as e:
            print("  %-12s %-3s FAIL: %s" % (scene, idx, e))
            fail += 1

    print("\n完成：ok=%d fail=%d  输出目录 %s" % (ok, fail, OUT_DIR))
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())