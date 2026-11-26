"""旁听人声 · 第 2 步：把 edge-tts 生成的 mp3 加工成游戏用的 WAV。

前置：先跑 tools/gen_voice_tts.py，产出 assets/audio_raw/tts/*.mp3
      （那一步需要联网；本步完全离线，只要本机有 ffmpeg）

用法：
    python tools/process_voice.py            # 处理缺的
    python tools/process_voice.py --force    # 全部重做
    python tools/process_voice.py --selftest # 用合成音自测管线，不读真实素材

产出：assets/audio/voice/<scene>_<n>.wav（22050Hz / mono / 16bit）

为什么要加工，而不是直接把 mp3 丢进游戏（这不是「加个效果更好听」，是**叙事要求**）：
  docs/npc.md §2.1 已把「听不清」写成设定 —— 隔了几十年，声音是糊的。
  所以每条都要过：180Hz 高通 + 4000Hz 低通（旧喇叭/远场）
              + 三个短延迟抽头做房间感（站在空地上听到的那点混响）
              + 一层 -50dB 的空气底噪（不是静音，静音会露馅到「像录音棚」）
  台词仍然能听清，但一听就知道「对面没人，只有剩下的话」。

加工是确定性的（无随机种子、无时间依赖），同输入必得同输出 —— 可以逐字节复现。
"""

import argparse
import os
import shutil
import struct
import subprocess
import sys
import tempfile

import numpy as np

SRC_DIR = os.path.join("assets", "audio_raw", "tts")
DST_DIR = os.path.join("assets", "audio", "voice")
FS = 22050

SCENES = ["a1_bang", "a2_well", "a3_field", "a4_site", "a5_road", "a2_field", "a4_field"]
PER_SCENE = 4


# ── 滤波器（RBJ biquad）──────────────────────────────────────────────

def _bq_lp(fc, fs, q=0.7071):
    w = 2.0 * np.pi * fc / fs
    cw, sw = np.cos(w), np.sin(w)
    al = sw / (2.0 * q)
    b = np.array([(1.0 - cw) / 2.0, 1.0 - cw, (1.0 - cw) / 2.0])
    a = np.array([1.0 + al, -2.0 * cw, 1.0 - al])
    return b / a[0], a / a[0]


def _bq_hp(fc, fs, q=0.7071):
    w = 2.0 * np.pi * fc / fs
    cw, sw = np.cos(w), np.sin(w)
    al = sw / (2.0 * q)
    b = np.array([(1.0 + cw) / 2.0, -(1.0 + cw), (1.0 + cw) / 2.0])
    a = np.array([1.0 + al, -2.0 * cw, 1.0 - al])
    return b / a[0], a / a[0]


def _biquad(x, b, a):
    y = np.empty_like(x)
    x1 = x2 = y1 = y2 = 0.0
    b0, b1, b2 = float(b[0]), float(b[1]), float(b[2])
    a1, a2 = float(a[1]), float(a[2])
    for i in range(x.shape[0]):
        xi = float(x[i])
        yi = b0 * xi + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1 = x1, xi
        y2, y1 = y1, yi
        y[i] = yi
    return y


# ── 加工链 ───────────────────────────────────────────────────────────

def shape_voice(x, fs=FS):
    """远场 + 旧喇叭 + 房间。参数是刻意的，别随手调。"""
    bp_lp = _bq_lp(4000.0, fs)
    bp_hp = _bq_hp(180.0, fs)
    y = _biquad(_biquad(x, *bp_hp), *bp_lp)

    # 房间感：3 个短延迟抽头（空地上的那一点点回声，不是教堂）
    wet = y.copy()
    for delay_s, gain in ((0.023, 0.22), (0.037, 0.14), (0.053, 0.09)):
        n = int(delay_s * fs)
        if n < y.shape[0]:
            wet[n:] += gain * y[:-n]
    y = 0.72 * wet + 0.28 * y

    # 空气底噪：确定性（固定相位噪声），不是「加个随机数意思一下」
    t = np.arange(y.shape[0], dtype=np.float64) / fs
    air = (np.sin(2 * np.pi * 47.0 * t) * 0.6 + np.sin(2 * np.pi * 113.0 * t) * 0.4)
    air = _biquad(air, *_bq_lp(900.0, fs))
    y = y + air * 10.0 ** (-50.0 / 20.0)

    # 淡入淡出，防爆音
    fi, fo = int(0.015 * fs), int(0.060 * fs)
    if y.shape[0] > fi + fo:
        y[:fi] *= np.linspace(0.0, 1.0, fi)
        y[-fo:] *= np.linspace(1.0, 0.0, fo)

    peak = float(np.max(np.abs(y))) or 1.0
    return y * (0.72 / peak)


def write_wav(path, x, fs=FS):
    pcm = np.clip(x, -1.0, 1.0)
    pcm = (pcm * 32767.0).astype("<i2").tobytes()
    with open(path, "wb") as f:
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + len(pcm)))
        f.write(b"WAVEfmt ")
        f.write(struct.pack("<IHHIIHH", 16, 1, 1, fs, fs * 2, 2, 16))
        f.write(b"data")
        f.write(struct.pack("<I", len(pcm)))
        f.write(pcm)


def decode_mp3(path, fs=FS):
    """ffmpeg 解码成 f32 单声道。中间文件落盘而不是抓 stdout（沙箱里抓管道容易 EPERM）。"""
    if not shutil.which("ffmpeg"):
        sys.exit("找不到 ffmpeg。装一个，或把它加进 PATH 再跑。")
    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, "a.raw")
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", path,
               "-ac", "1", "-ar", str(fs), "-f", "f32le", raw]
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode != 0 or not os.path.exists(raw):
            raise RuntimeError("ffmpeg 解码失败：%s\n%s" % (path, r.stderr.decode("utf-8", "replace")[:400]))
        return np.fromfile(raw, dtype="<f4").astype(np.float64)


# ── 主流程 ───────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--selftest", action="store_true", help="用合成音自测管线，不读真实素材")
    args = ap.parse_args()

    os.makedirs(DST_DIR, exist_ok=True)

    if args.selftest:
        # 合成一段「像说话的」占位音（不是配音，只用来证明管线能跑）
        t = np.arange(int(2.2 * FS)) / FS
        f0 = 210.0 + 30.0 * np.sin(2 * np.pi * 2.3 * t)
        ph = 2 * np.pi * np.cumsum(f0) / FS
        src = np.zeros_like(t)
        for k, g in ((1, 0.5), (2, 0.3), (3, 0.16), (4, 0.08)):
            src += g * np.sin(k * ph)
        env = np.clip(np.sin(2 * np.pi * 3.1 * t) ** 2, 0, 1)
        src = src * env
        out = shape_voice(src)
        p = os.path.join(DST_DIR, "_selftest.wav")
        write_wav(p, out)
        tmp = p.replace(".wav", ".import")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write("# selftest placeholder, delete me\n")
        print("SELFTEST_OK %s  %.2fs  peak=%.3f" % (p, out.shape[0] / FS, float(np.max(np.abs(out)))))
        return

    if not os.path.isdir(SRC_DIR):
        sys.exit("没有 %s。先跑 tools/gen_voice_tts.py（需要联网 + pip install edge-tts）" % SRC_DIR)

    ok = skip = fail = 0
    for scene in SCENES:
        for i in range(PER_SCENE):
            src = os.path.join(SRC_DIR, "%s_%d.mp3" % (scene, i))
            dst = os.path.join(DST_DIR, "%s_%d.wav" % (scene, i))
            if not os.path.exists(src):
                print("  %-12s %d  缺源文件" % (scene, i))
                fail += 1
                continue
            if os.path.exists(dst) and not args.force:
                skip += 1
                continue
            try:
                x = decode_mp3(src)
                y = shape_voice(x)
                write_wav(dst, y)
                print("  %-12s %d  %5.2fs -> %.3f 峰" % (scene, i, x.shape[0] / FS, float(np.max(np.abs(y)))))
                ok += 1
            except Exception as e:
                print("  %-12s %d  FAIL: %s" % (scene, i, e))
                fail += 1

    print("\n完成：ok=%d skip=%d fail=%d  输出 %s" % (ok, skip, fail, DST_DIR))
    print("下一步：godot --headless --path . --import   （生成 .import sidecar，别漏）")
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()