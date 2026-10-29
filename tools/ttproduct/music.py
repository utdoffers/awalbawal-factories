# -*- coding: utf-8 -*-
"""🎵 موسيقى مقاطع المنتجات (WP-684) — مولَّدةٌ بالكامل: لا ملفَّ خارجيًّا ولا حقوقَ أحد.
طبلٌ وتصفيقٌ وباص 808 ينزلق ولحنٌ على مقام الحجاز ونَفَسٌ دافئ. والبذرةُ تغيّر اللحنَ والسلّمَ
والسرعة، فلا يتكرّر صوتٌ واحدٌ على كلِّ مقطع (درسُ «المحتوى المكرّر»).
الاستعمال: python3 music.py <المدة_بالثواني> <البذرة> <الملف.wav>"""
import sys, wave
import numpy as np
from scipy.signal import fftconvolve, butter, lfilter

SR = 44100

def make(dur, seed, out):
    rng = np.random.default_rng(seed)
    BPM = float(rng.choice([92, 96, 100, 104]))
    BEAT = 60 / BPM
    N = int(dur * SR)
    L = np.zeros(N); R = np.zeros(N)
    shift = int(rng.choice([-2, 0, 2, 3, 5]))
    def hz(m): return 440 * 2 ** ((m + shift - 69) / 12)
    def add(sig, t0, pan=0.0, gain=1.0):
        s = int(t0 * SR); e = min(N, s + len(sig))
        if e <= s or s < 0: return
        l = np.sqrt(0.5 * (1 - pan)); r = np.sqrt(0.5 * (1 + pan))
        L[s:e] += sig[:e - s] * gain * l; R[s:e] += sig[:e - s] * gain * r
    def lp(x, fc, o=2): b, a = butter(o, fc / (SR / 2)); return lfilter(b, a, x)
    def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), 'high'); return lfilter(b, a, x)
    def kick():
        n = int(.45 * SR); t = np.arange(n) / SR; f = 48 + 120 * np.exp(-t * 30); ph = 2 * np.pi * np.cumsum(f) / SR
        return np.tanh(1.6 * np.sin(ph) * np.exp(-t * 7)) + 0.3 * np.exp(-t * 300) * rng.uniform(-1, 1, n)
    def clap():
        n = int(.3 * SR); t = np.arange(n) / SR; nz = hp(rng.uniform(-1, 1, n), 900)
        e = np.exp(-t * 25) + 0.6 * np.exp(-np.maximum(0, t - .012) * 60) * (t > .012)
        return nz * e * 0.8
    def hat(o=False):
        n = int((.25 if o else .05) * SR); t = np.arange(n) / SR
        return hp(rng.uniform(-1, 1, n), 7000) * np.exp(-t * (12 if o else 90))
    def b808(m, ln, gf=None):
        n = int(ln * SR); t = np.arange(n) / SR; f = np.full(n, hz(m))
        if gf: f = hz(m) + (hz(gf) - hz(m)) * np.exp(-t * 18)
        ph = 2 * np.pi * np.cumsum(f) / SR; e = np.minimum(1, t * 200) * np.exp(-t * 1.6)
        return np.tanh(2.2 * np.sin(ph) * e) * 0.9
    def pluck(m, ln=.45):
        n = int(ln * SR); t = np.arange(n) / SR; f = hz(m)
        x = (np.sin(2 * np.pi * f * t) + .5 * np.sin(4 * np.pi * f * t + .3) + .25 * np.sin(6 * np.pi * f * t)) * np.exp(-t * 7) * np.minimum(1, t * 400)
        return lp(x, 5000)
    def pad(ms, ln):
        n = int(ln * SR); t = np.arange(n) / SR; x = np.zeros(n)
        for m in ms:
            for dt in (-0.12, 0, 0.11):
                f = hz(m) * 2 ** (dt / 12); x += 2 * ((f * t + rng.random()) % 1) - 1
        x = lp(x, 1800, 2) / (len(ms) * 3)
        return x * np.minimum(1, t / 0.4) * np.minimum(1, np.maximum(0, (ln - t)) / 0.4)
    # حجازٌ على ري: ري مي♭ فا# صول لا سي♭ دو
    chords = [[55, 58, 62], [60, 63, 67], [62, 66, 69], [62, 66, 69]]
    roots = [43, 48, 38, 38]
    scale = [62, 63, 66, 67, 69, 70, 72, 74, 75, 78, 79]
    mel = [int(rng.choice(scale)) for _ in range(16)]
    K = kick(); C = clap(); BAR = 4 * BEAT
    nb = int(np.ceil(dur / BAR)) + 1
    for b in range(nb):
        t0 = b * BAR
        if t0 >= dur: break
        add(pad(chords[b % 4], BAR), t0, 0, 0.5)
        for k in range(8):
            if b == 0 and k % 2: continue
            add(pluck(mel[(b * 8 + k) % 16]), t0 + k * BEAT / 2, pan=(-0.3 if k % 2 else 0.3), gain=0.28)
        if b >= 1 or dur < 6:
            add(K, t0, 0, 0.9); add(K, t0 + 2 * BEAT, 0, 0.9); add(K, t0 + 2.5 * BEAT, 0, 0.55)
            add(C, t0 + BEAT, 0.05, 0.5); add(C, t0 + 3 * BEAT, -0.05, 0.5)
            for k in range(8): add(hat(), t0 + k * BEAT / 2, 0.25, 0.12)
            add(b808(roots[b % 4], BEAT * 1.8), t0, 0, 0.75)
            add(b808(roots[b % 4], BEAT * 1.4, gf=roots[b % 4] + 5), t0 + 2.5 * BEAT, 0, 0.6)
    cut = min(N, int(BAR * SR)); L[:cut] = lp(L[:cut], 1200); R[:cut] = lp(R[:cut], 1200)
    d = int(BEAT * 0.75 * SR)
    L2 = L.copy(); R2 = R.copy(); L2[d:] += 0.2 * R[:-d]; R2[d:] += 0.2 * L[:-d]
    ir_n = int(1.0 * SR); t = np.arange(ir_n) / SR; ir = rng.uniform(-1, 1, ir_n) * np.exp(-t * 4)
    L = L2 + 0.08 * fftconvolve(L2, ir)[:N] / 30; R = R2 + 0.08 * fftconvolve(R2, ir)[:N] / 30
    L = lp(L, 11000); R = lp(R, 11000)
    f = int(0.6 * SR); fade = np.linspace(1, 0, f); L[-f:] *= fade; R[-f:] *= fade
    m = np.stack([L, R], 1); m = np.tanh(1.2 * m / max(1e-9, np.max(np.abs(m)))); m *= 0.9 / max(1e-9, np.max(np.abs(m)))
    w = wave.open(out, 'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((m * 32767).astype('<i2').tobytes()); w.close()

if __name__ == "__main__":
    make(float(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
    print("✓ موسيقى", sys.argv[3])
