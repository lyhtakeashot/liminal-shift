# -*- coding: utf-8 -*-
"""《阈限迁移 SHIFT》音频素材生成器（任务书 L18 音效层）

格式口径（任务书 §2.1，改这里就等于改全部产出）
--------------------------------------------------
  采样率   22050 Hz          （复古感靠采样率，不靠位数；Web 上 WAV 解码最稳）
  声道     单声道 (mono)
  位深     16-bit PCM，小端
  峰值     上限 0.9（不削波）——本文件所有音色统一归一到 0.85，留 0.05 余量
  循环音   首尾各 50ms 交叉淡化，且循环点两侧取「相邻采样差最小」的位置
           ⇒ |首采样 − 尾采样| < 0.02（assert 在 _mdtest/audio_check.gd 的 G4）

可复现（任务书 §2.1 / §5）
--------------------------
  无随机源、不读时间、不读环境。噪声来自 python 标准库 random.Random(固定 seed)
  的 randbytes（Mersenne Twister，跨版本/跨机器稳定），滤波全用 numpy float64。
  同一个命令必须逐字节重现已有文件：

      python tools/gen_audio.py            # 重写 assets/audio/*.wav（13 个）
      python tools/gen_audio.py --check    # 逐字节比对，不同则非零退出

  13 个文件的配方逐条对应 docs/PROMPT-audio-exec.md §3 表格的行号（见各 snd_* 注释）。

仅依赖：python 标准库 + numpy（本机 numpy 2.3.5）。
"""

import io
import math
import os
import random
import sys
import wave

import numpy as np

# ---------------------------------------------------------------- 全局常量

SR = 22050                 # 采样率
CHANNELS = 1               # 声道数
SAMPLE_WIDTH = 2           # 位深 16-bit ⇒ 2 字节
PEAK_LIMIT = 0.9           # 任务书硬上限（不许削波）
PEAK_TARGET = 0.85         # 实际归一目标（比上限低 0.05）
LOOP_SECONDS = 4.0         # 环境底噪循环长度（§3 表 1–5）
LOOP_FADE = 0.050          # 循环音首尾交叉淡化 50ms（§3「循环音额外要求」）
LOOP_SEARCH = 0.30         # 接缝搜索窗（秒）：在这段里找相邻采样差最小的循环点
SEED_BASE = 20261126       # 固定 seed 基底；每条音色用 SEED_BASE+序号
AMBIENT_RMS = 0.13         # 循环音的响度口径：按 RMS 对齐（峰归一会被稀疏瞬态带偏 ⇒ 各帧忽大忽小）

ORDER = [
    "amb_a1.wav", "amb_a2.wav", "amb_a3.wav", "amb_a4.wav", "amb_a5.wav",
    "step_1.wav", "step_2.wav",
    "shift_fwd.wav", "shift_back.wav",
    "axis.wav", "collect.wav", "ui_toggle.wav", "ending.wav",
]

LOOP_NAMES = ["amb_a1.wav", "amb_a2.wav", "amb_a3.wav", "amb_a4.wav", "amb_a5.wav"]

# 一次性音效时长（秒），与 §3 表格一致
DURATIONS = {
    "step_1.wav": 0.08,
    "step_2.wav": 0.08,
    "shift_fwd.wav": 0.30,
    "axis.wav": 0.20,
    "collect.wav": 0.25,
    "ui_toggle.wav": 0.10,
    "ending.wav": 2.50,
}


# ---------------------------------------------------------------- 基础工具

def _n(sec):
    """秒 → 采样数（四舍五入，且确定）。"""
    return int(math.floor(sec * SR + 0.5))


def _t(n):
    """时间轴，单位秒。"""
    return np.arange(n, dtype=np.float64) / float(SR)


def _rng(idx):
    """固定 seed 的随机源；randbytes 走 Mersenne Twister，跨版本稳定。"""
    return random.Random(SEED_BASE + idx)


def _noise(rnd, n):
    """均匀白噪声，幅度 [−1, 1]。"""
    raw = rnd.randbytes(n)
    return np.frombuffer(raw, dtype=np.uint8).astype(np.float64) / 127.5 - 1.0


def _dc(x):
    """去直流（低速风声会积出直流分量，听感是「占掉一半动态」）。"""
    return x - float(np.mean(x))


def _norm(x, peak=1.0):
    """按峰值归一。"""
    m = float(np.max(np.abs(x))) if len(x) else 0.0
    if m <= 1e-12:
        return x
    return x * (peak / m)


def _level(x, rms):
    """按 RMS 定电平：混音时用这个定各层的相对响度（峰归一只管最后一步）。"""
    r = float(np.sqrt(np.mean(x * x))) if len(x) else 0.0
    if r <= 1e-12:
        return x
    return x * (rms / r)


def _swell(n, rate, depth, phase=0.0):
    """缓慢起伏（LFO）：返回 [1−depth, 1] 的乘性包络。"""
    t = _t(n)
    return (1.0 - depth) + depth * (0.5 + 0.5 * np.sin(2.0 * np.pi * rate * t + phase))


def _fade_out(x, secs):
    """末段线性收尾，避免波形被硬截断产生爆音。"""
    k = min(len(x), _n(secs))
    if k <= 0:
        return x
    out = x.copy()
    out[-k:] *= np.linspace(1.0, 0.0, k)
    return out


# ---- 滤波器（RBJ biquad，逐样点迭代；22kHz 下每文件 9 万点，python 循环够快）----

def _iir(x, b, a):
    b0, b1, b2 = b
    a1, a2 = a
    y = np.empty_like(x)
    x1 = x2 = y1 = y2 = 0.0
    for i in range(len(x)):
        xi = x[i]
        yi = b0 * xi + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2 = x1
        x1 = xi
        y2 = y1
        y1 = yi
        y[i] = yi
    return y


def _lp_coeffs(fc, q=0.7071):
    w0 = 2.0 * math.pi * fc / SR
    cosw, sinw = math.cos(w0), math.sin(w0)
    alpha = sinw / (2.0 * q)
    a0 = 1.0 + alpha
    b = ((1.0 - cosw) / 2.0 / a0, (1.0 - cosw) / a0, (1.0 - cosw) / 2.0 / a0)
    a = (-2.0 * cosw / a0, (1.0 - alpha) / a0)
    return b, a


def _hp_coeffs(fc, q=0.7071):
    w0 = 2.0 * math.pi * fc / SR
    cosw, sinw = math.cos(w0), math.sin(w0)
    alpha = sinw / (2.0 * q)
    a0 = 1.0 + alpha
    b = ((1.0 + cosw) / 2.0 / a0, -(1.0 + cosw) / a0, (1.0 + cosw) / 2.0 / a0)
    a = (-2.0 * cosw / a0, (1.0 - alpha) / a0)
    return b, a


def _lowpass(x, fc, q=0.7071):
    b, a = _lp_coeffs(min(fc, SR * 0.45), q)
    return _iir(x, b, a)


def _highpass(x, fc, q=0.7071):
    b, a = _hp_coeffs(max(fc, 10.0), q)
    return _iir(x, b, a)


def _band(x, lo, hi):
    """带通 = 高通(lo) → 低通(hi)。§3 表格里的「200–800Hz」就按这个字面实现。"""
    return _lowpass(_highpass(x, lo), hi)


# ---------------------------------------------------------------- 循环处理

def _make_loop(src, n):
    """把长素材裁成 n 样本的无缝循环。

    两步：
      1. 接缝搜索：在 [0, len−n−fade] 里找使 |src[s+n] − src[s+n−1]| 最小的 s。
         循环点两侧因此是**相邻采样**，接缝天然连续（这是 |首−尾| 断言能过的原因）。
      2. 头部 50ms 与尾料（src[s+n : s+n+fade]）线性交叉淡化：
         out[0] = src[s+n]（正好接上 out[n−1] = src[s+n−1]），
         淡化到 fade 处完全回到原始素材。
    长度严格等于 n ⇒ 时长仍是 4.0s。
    """
    fade = _n(LOOP_FADE)
    hi = len(src) - n - fade
    if hi < 0:
        raise ValueError("素材比循环长度短")
    d = np.abs(src[n:n + hi + 1] - src[n - 1:n + hi])
    s = int(np.argmin(d))
    out = src[s:s + n].copy()
    head = src[s:s + fade]
    tail = src[s + n:s + n + fade]
    w = np.linspace(1.0, 0.0, fade)          # i=0 → 全取尾料，i=fade−1 → 全取原始头
    out[:fade] = head * (1.0 - w) + tail * w
    return out


# ---------------------------------------------------------------- §3 表 1–5：环境底噪

def snd_amb_a1(m):
    """§3 行 1 · amb_a1 · 1926 环境底噪 = 低频风声(200–800Hz) + 蝉鸣(4kHz 脉冲串 ~6 次/秒)。"""
    rnd = _rng(101)
    wind = _band(_noise(rnd, m), 200.0, 800.0)
    wind *= _swell(m, 0.23, 0.45) * _swell(m, 0.07, 0.18, 1.1)
    wind = _level(wind, 0.20)
    cic = _cicada(rnd, m, rate=6.2, freq=4000.0)
    cic = _level(_band(cic, 3400.0, 4700.0), 0.075)
    return _norm(_dc(wind + cic), 1.0)


def _cicada(rnd, m, rate, freq):
    """蝉鸣：4kHz 窄带脉冲串。间隔在 0.6/rate ~ 1.4/rate 之间随机（seed 固定）。"""
    out = np.zeros(m)
    tmax = m / float(SR)
    tt0 = 0.12
    while tt0 < tmax - 0.05:
        a = int(tt0 * SR)
        b = min(m, a + _n(0.028))
        if b > a:
            seg = _t(b - a)
            env = np.minimum(1.0, seg / 0.002) * np.exp(-seg / 0.018)
            tone = np.sin(2.0 * np.pi * freq * seg) * (0.70 + 0.30 * np.sin(2.0 * np.pi * 115.0 * seg))
            out[a:b] += env * tone
        tt0 += rnd.uniform(0.6 / rate, 1.4 / rate)
    return out


def snd_amb_a2(m):
    """§3 行 2 · amb_a2 · 1951 = 更宽的风声(200–1200Hz) + 远处人声嗡(200Hz 方波+强低通)。"""
    rnd = _rng(102)
    wind = _band(_noise(rnd, m), 200.0, 1200.0)
    wind *= _swell(m, 0.17, 0.40) * _swell(m, 0.05, 0.15, 0.7)
    wind = _level(wind, 0.22)
    t = _t(m)
    sq = 0.5 * np.sign(np.sin(2.0 * np.pi * 200.0 * t)) + 0.5 * np.sign(np.sin(2.0 * np.pi * 197.0 * t))
    murmur = _level(_lowpass(_lowpass(sq, 240.0), 240.0) * _swell(m, 0.11, 0.6), 0.10)
    return _norm(_dc(wind + murmur), 1.0)


def snd_amb_a3(m):
    """§3 行 3 · amb_a3 · 1976 = 广播底噪(1kHz 窄带+慢速调幅) + 电流杂音(稀疏脉冲)。"""
    rnd = _rng(103)
    hiss = _band(_noise(rnd, m), 900.0, 1150.0) * _swell(m, 0.40, 0.55)
    hiss = _level(hiss, 0.20)
    crack = np.zeros(m)
    tt0 = 0.05
    tmax = m / float(SR)
    while tt0 < tmax - 0.02:
        a = int(tt0 * SR)
        b = min(m, a + _n(0.004))
        if b > a:
            seg = _t(b - a)
            crack[a:b] += _noise(rnd, b - a) * np.exp(-seg / 0.0015)
        tt0 += rnd.uniform(0.12, 0.34)
    crack = _level(_band(crack, 2000.0, 6000.0), 0.045)
    return _norm(_dc(hiss + crack), 1.0)


def snd_amb_a4(m):
    """§3 行 4 · amb_a4 · 2001 = 车流隆隆(60–120Hz) + 稀疏电视声(1.5kHz 短脉冲)。"""
    rnd = _rng(104)
    rumble = _band(_noise(rnd, m), 60.0, 120.0)
    rumble *= _swell(m, 0.90, 0.50) * _swell(m, 0.31, 0.35, 2.0)
    rumble = _level(rumble, 0.26)
    tv = np.zeros(m)
    tt0 = 0.30
    tmax = m / float(SR)
    while tt0 < tmax - 0.10:
        a = int(tt0 * SR)
        dur = rnd.uniform(0.05, 0.09)
        b = min(m, a + _n(dur))
        if b > a:
            seg = _t(b - a)
            env = np.minimum(1.0, seg / 0.005) * np.exp(-seg / (dur * 0.6))
            tv[a:b] += _noise(rnd, b - a) * env
        tt0 += rnd.uniform(0.50, 1.10)
    tv = _level(_band(tv, 1200.0, 1800.0), 0.09)
    return _norm(_dc(rumble + tv), 1.0)


def snd_amb_a5(m):
    """§3 行 5 · amb_a5 · 2026 = 空场风声(更干更空、高频少) + 50Hz 电流嗡及二次谐波。"""
    rnd = _rng(105)
    wind = _band(_noise(rnd, m), 60.0, 320.0) * _swell(m, 0.13, 0.50)
    wind = _level(wind, 0.16)
    t = _t(m)
    hum = 0.055 * np.sin(2.0 * np.pi * 50.0 * t) + 0.022 * np.sin(2.0 * np.pi * 100.0 * t + 0.7)
    return _norm(_dc(wind + hum), 1.0)


# ---------------------------------------------------------------- §3 表 6–13：一次性音效

def snd_step_1(m):
    """§3 行 6 · step_1 · 40ms 带通白噪声(800–2500Hz) + 20ms 指数衰减尾。"""
    rnd = _rng(106)
    burst = _band(_noise(rnd, m), 800.0, 2500.0)
    tt = _t(m)
    env = np.zeros(m)
    atk = max(1, _n(0.001))
    env[:atk] = np.linspace(0.0, 1.0, atk)
    hold = min(m, _n(0.040))
    env[atk:hold] = 1.0
    if hold < m:
        env[hold:] = np.exp(-(tt[hold:] - 0.040) / 0.010)   # τ=10ms ⇒ 20ms 后约 −18dB
    return _norm(burst * env, 1.0)


def snd_step_2(m):
    """§3 行 7 · step_2 · 同 6，中心频率 ×1.25（1000–3125Hz），起音延迟 5ms。"""
    rnd = _rng(107)
    burst = _band(_noise(rnd, m), 1000.0, 3125.0)
    tt = _t(m)
    d = _n(0.005)
    atk = max(1, _n(0.001))
    env = np.zeros(m)
    if d + atk <= m:
        env[d:d + atk] = np.linspace(0.0, 1.0, atk)
    hold = min(m, d + _n(0.040))
    if d + atk < hold:
        env[d + atk:hold] = 1.0
    if hold < m:
        env[hold:] = np.exp(-(tt[hold:] - (d / float(SR) + 0.040)) / 0.010)
    return _norm(burst * env, 1.0)


def _sweep_noise(rnd, m, f_hi, f_lo, blocks=10):
    """分块带通噪声扫频：中心频率从 f_hi 线性降到 f_lo，块间 8ms 交叉淡化。"""
    x = _noise(rnd, m)
    out = np.zeros(m)
    seg = m // blocks
    edge = _n(0.008)
    for i in range(blocks):
        a = i * seg
        b = m if i == blocks - 1 else (i + 1) * seg
        if b <= a:
            continue
        fc = f_hi + (f_lo - f_hi) * (i / float(max(1, blocks - 1)))
        y = _band(x[a:b], fc * 0.7, fc * 1.4)
        w = np.ones(b - a)
        if i > 0 and edge < (b - a):
            w[:edge] = np.linspace(0.0, 1.0, edge)
        if i < blocks - 1 and edge < (b - a):
            w[-edge:] = np.linspace(1.0, 0.0, edge)
        out[a:b] = y * w
    return out


def snd_shift_fwd(m):
    """§3 行 8 · shift_fwd · 220→110Hz 正弦下滑 + 噪声扫频（石磨/胶片前进）。"""
    rnd = _rng(108)
    dur = m / float(SR)
    tt = _t(m)
    f0, f1 = 220.0, 110.0
    phase = 2.0 * np.pi * (f0 * tt + 0.5 * (f1 - f0) / dur * tt * tt)
    tone = _level(np.sin(phase), 0.20)
    sweep = _level(_sweep_noise(rnd, m, 2500.0, 400.0, 10), 0.14)
    env = np.minimum(1.0, tt / 0.005) * np.exp(-tt / 0.090)
    return _norm(_fade_out((tone + sweep) * env, 0.020), 1.0)


def snd_axis(m):
    """§3 行 10 · axis · 60Hz 正弦 + 快衰减，叠一层 200Hz 短脉冲。"""
    tt = _t(m)
    e1 = np.minimum(1.0, tt / 0.002) * np.exp(-tt / 0.035)
    body = _level(np.sin(2.0 * np.pi * 60.0 * tt) * e1, 0.24)
    pulse = np.zeros(m)
    d = _n(0.020)
    n2 = min(m - d, _n(0.030))
    if n2 > 0:
        ptt = _t(n2)
        penv = np.minimum(1.0, ptt / 0.004) * np.exp(-ptt / 0.020)
        pulse[d:d + n2] = np.sin(2.0 * np.pi * 200.0 * ptt) * penv
    pulse = _level(pulse, 0.16)
    return _norm(_fade_out(body + pulse, 0.010), 1.0)


def snd_collect(m):
    """§3 行 11 · collect · 523/659/784Hz 三音琶音，每音 60ms 起、正弦 + 轻微失谐(+3Hz)。"""
    out = np.zeros(m)
    for i, f in enumerate((523.25, 659.25, 783.99)):
        d = _n(0.060) * i
        if d >= m:
            break
        seg = _t(m - d)
        env = np.minimum(1.0, seg / 0.005) * np.exp(-seg / 0.045)
        out[d:] += (np.sin(2.0 * np.pi * f * seg) + 0.45 * np.sin(2.0 * np.pi * (f + 3.0) * seg)) * env
    return _norm(_fade_out(out, 0.010), 1.0)


def snd_ui_toggle(m):
    """§3 行 12 · ui_toggle · 1ms 冲击 + 8ms 指数衰减的宽带 click（开/关共用一条）。"""
    rnd = _rng(109)
    tt = _t(m)
    click = _noise(rnd, m) * np.exp(-tt / 0.006) * np.minimum(1.0, tt / 0.0004)
    ping = np.sin(2.0 * np.pi * 3000.0 * tt) * np.exp(-tt / 0.004)
    return _norm(_fade_out(click * 0.90 + ping * 0.35, 0.005), 1.0)


def snd_ending(m):
    """§3 行 13 · ending · 55Hz + 82.5Hz 五度 drone，缓慢上行，尾部 0.5s 淡出。"""
    tt = _t(m)
    dur = m / float(SR)
    glide = 55.0 * (1.0 + 0.055 * np.clip(tt / 2.0, 0.0, 1.0))   # 2s 内 55 → 58.0Hz
    phase = 2.0 * np.pi * np.cumsum(glide) / float(SR)
    tone = 0.65 * np.sin(phase) + 0.40 * np.sin(1.5 * phase)
    tone *= 1.0 + 0.12 * np.sin(2.0 * np.pi * 0.7 * tt)
    rise = np.clip(tt / 1.4, 0.0, 1.0)
    rise = rise * rise * (3.0 - 2.0 * rise)
    tail = np.clip((dur - tt) / 0.50, 0.0, 1.0)
    tail = tail * tail * (3.0 - 2.0 * tail)
    return _norm(_dc(tone * rise * tail), 1.0)


# ---------------------------------------------------------------- 落盘

def _to_pcm(sig, loudness="peak"):
    """float → int16 小端字节。

    两种响度口径（为什么不是一律峰归一）：
      · "peak"：一次性音效按峰值归一到 PEAK_TARGET —— 瞬态就是它的全部内容。
      · "rms" ：循环环境音按 RMS 对齐到 AMBIENT_RMS —— 峰归一会被「稀疏的电流杂音/电视脉冲」
                带偏（amb_a3 实测 RMS 只有 0.04，同总线播出来比别的帧小一大截），
                对齐 RMS 后五帧响度一致，峰值再按 PEAK_TARGET 封顶。
    最后四舍五入到 int16（无抖动，保证逐字节可复现）。
    """
    if loudness == "rms":
        r = float(np.sqrt(np.mean(sig * sig)))
        x = sig * (AMBIENT_RMS / r) if r > 1e-12 else sig
        pk = float(np.max(np.abs(x))) if len(x) else 0.0
        if pk > PEAK_TARGET:
            x = x * (PEAK_TARGET / pk)
    else:
        x = _norm(sig, PEAK_TARGET)
    x = np.clip(x, -1.0, 1.0)
    return np.round(x * 32767.0).astype("<i2")


def _wav_bytes(pcm_i16):
    """写标准 44 字节头的 PCM WAV（python wave 模块，头字段确定）。"""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(CHANNELS)
        w.setsampwidth(SAMPLE_WIDTH)
        w.setframerate(SR)
        w.writeframes(pcm_i16.tobytes())
    return buf.getvalue()


def _stats(pcm_i16):
    x = pcm_i16.astype(np.float64) / 32768.0
    return {
        "frames": int(len(x)),
        "dur": len(x) / float(SR),
        "peak": float(np.max(np.abs(x))) if len(x) else 0.0,
        "seam": abs(float(x[0] - x[-1])) if len(x) else 0.0,
    }


def build_all():
    """返回 (文件名 → wav 字节, 文件名 → 实测参数)。顺序固定。"""
    n_loop = _n(LOOP_SECONDS)
    src_len = n_loop + _n(LOOP_FADE) + _n(LOOP_SEARCH) + 1

    sig = {}
    # §3 表 1–5：4.0s 循环环境底噪（长素材 → 裁成无缝循环）
    sig["amb_a1.wav"] = _make_loop(snd_amb_a1(src_len), n_loop)
    sig["amb_a2.wav"] = _make_loop(snd_amb_a2(src_len), n_loop)
    sig["amb_a3.wav"] = _make_loop(snd_amb_a3(src_len), n_loop)
    sig["amb_a4.wav"] = _make_loop(snd_amb_a4(src_len), n_loop)
    sig["amb_a5.wav"] = _make_loop(snd_amb_a5(src_len), n_loop)

    # §3 表 6–8、10–13：一次性音效
    sig["step_1.wav"] = snd_step_1(_n(DURATIONS["step_1.wav"]))
    sig["step_2.wav"] = snd_step_2(_n(DURATIONS["step_2.wav"]))
    sig["shift_fwd.wav"] = snd_shift_fwd(_n(DURATIONS["shift_fwd.wav"]))
    # §3 行 9：shift_back 是第 8 条的**波形倒放**，不重新合成
    sig["shift_back.wav"] = sig["shift_fwd.wav"][::-1].copy()
    sig["axis.wav"] = snd_axis(_n(DURATIONS["axis.wav"]))
    sig["collect.wav"] = snd_collect(_n(DURATIONS["collect.wav"]))
    sig["ui_toggle.wav"] = snd_ui_toggle(_n(DURATIONS["ui_toggle.wav"]))
    sig["ending.wav"] = snd_ending(_n(DURATIONS["ending.wav"]))

    wavs = {}
    stats = {}
    for name in ORDER:
        pcm = _to_pcm(sig[name], "rms" if name in LOOP_NAMES else "peak")
        wavs[name] = _wav_bytes(pcm)
        stats[name] = _stats(pcm)
    return wavs, stats


def main(argv):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outdir = os.path.join(root, "assets", "audio")
    if len(ORDER) != 13:
        print("INTERNAL_ERROR: ORDER must hold 13 files")
        return 2

    print("gen_audio: %d Hz / mono / %d-bit PCM / peak target %.2f (limit %.2f)"
          % (SR, SAMPLE_WIDTH * 8, PEAK_TARGET, PEAK_LIMIT))
    wavs, stats = build_all()

    if "--check" in argv:
        diffs = []
        for name in ORDER:
            path = os.path.join(outdir, name)
            if not os.path.exists(path):
                diffs.append(name + " (missing)")
                continue
            with open(path, "rb") as fh:
                if fh.read() != wavs[name]:
                    diffs.append(name + " (bytes differ)")
        if diffs:
            print("CHECK_FAIL: " + ", ".join(diffs))
            return 1
        print("CHECK_OK: %d files byte-identical to freshly synthesised output" % len(ORDER))
        return 0

    os.makedirs(outdir, exist_ok=True)
    total = 0
    for name in ORDER:
        data = wavs[name]
        with open(os.path.join(outdir, name), "wb") as fh:
            fh.write(data)
        total += len(data)
        st = stats[name]
        print("  %-14s %6.3fs peak=%.3f seam=%.4f %7d B"
              % (name, st["dur"], st["peak"], st["seam"], len(data)))
    print("TOTAL %d bytes in %d files" % (total, len(ORDER)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))