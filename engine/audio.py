"""Shared sound kit: synthesised instruments (felt piano, strings, pads, plucks, bells, pulses), sound effects,
reverb, the narration bus, and an automatic score builder for new episodes. All original, no samples.

Import with EPISODE_DIR set (engine/mix.py does this)."""
import math, json, os, sys
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly, fftconvolve, butter, sosfilt

EP = os.path.abspath(os.environ["EPISODE_DIR"])
if EP not in sys.path:
    sys.path.insert(0, EP)
from timeline import T, E, DURATION, LINES, SCENES

SR = 48000
N = int((DURATION + 0.5) * SR)
rng = np.random.default_rng(4)



def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env_adsr(n, a, r, sr=SR):
    e = np.ones(n)
    na, nr = int(a * sr), int(r * sr)
    na = min(na, n); nr = min(nr, n - na)
    e[:na] = np.linspace(0, 1, na) ** 1.5
    if nr > 0:
        e[n - nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def lowpass(x, fc, order=2):
    sos = butter(order, fc / (SR / 2), btype="low", output="sos")
    return sosfilt(sos, x, axis=0)


def highpass(x, fc, order=2):
    sos = butter(order, fc / (SR / 2), btype="high", output="sos")
    return sosfilt(sos, x, axis=0)


def bandpass(x, lo, hi, order=2):
    sos = butter(order, [lo / (SR / 2), hi / (SR / 2)], btype="band", output="sos")
    return sosfilt(sos, x, axis=0)


def reverb_ir(dur=3.2, decay=2.6, seed=1):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    ir = np.zeros((n, 2))
    for ch in range(2):
        noise = r.normal(0, 1, n)
        noise = lowpass(noise, 6000)
        ir[:, ch] = noise * np.exp(-t * decay)
    ir[: int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))[:, None]
    return ir / np.sqrt((ir ** 2).sum(axis=0))


IR = reverb_ir()


def verb(x, wet=0.35):
    """x mono or stereo -> stereo with reverb."""
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    out = np.zeros_like(x)
    for ch in range(2):
        out[:, ch] = fftconvolve(x[:, ch], IR[:, ch])[: len(x)]
    return x * (1 - wet) + out * wet * 3.0


def place(buf, sig, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if sig.ndim == 1 and buf.ndim == 2:
        l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        sig = np.stack([sig * l * 1.414, sig * r * 1.414], 1)
    i1 = min(len(buf), i0 + len(sig))
    if i0 >= len(buf) or i1 <= max(0, i0):
        return
    s0 = max(0, -i0)
    buf[max(0, i0):i1] += sig[s0:s0 + i1 - max(0, i0)] * gain


# ---------------------------------------------------------------- instruments
def pad_note(m, dur, bright=0.5, a=1.2, r=1.8):
    n = int((dur + r) * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    sig = np.zeros(n)
    for det in (-0.12, 0.0, 0.11):
        ff = f * 2 ** (det / 12)
        ph = rng.uniform(0, 6.28)
        for k in range(1, 9):
            if ff * k > 9000:
                break
            sig += np.sin(2 * np.pi * ff * k * t + ph * k) / (k ** (1.9 - bright))
    sig *= env_adsr(n, a, r + 0.3)
    lfo = 1 + 0.08 * np.sin(2 * np.pi * 0.23 * t + rng.uniform(0, 6))
    return sig * lfo / 6


def pluck(m, dur=1.6, bright=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    sig = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 6) * bright
           + 0.12 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 9) * bright)
    e = np.exp(-t * 3.2) * (1 - np.exp(-t * 400))
    return sig * e


def bell(m, dur=2.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    sig = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 4) + 0.2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 7)
    return sig * np.exp(-t * 2.2) * (1 - np.exp(-t * 600))


def sub_pulse(f=46, dur=0.9):
    n = int(dur * SR)
    t = np.arange(n) / SR
    fr = f * (1 + 0.6 * np.exp(-t * 18))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    return np.sin(ph) * np.exp(-t * 4.5) * (1 - np.exp(-t * 300))


def noise_swell(dur, lo, hi, shape="bell"):
    n = int(dur * SR)
    x = rng.normal(0, 1, n)
    t = np.linspace(0, 1, n)
    # sweep bandpass by chunks
    out = np.zeros(n)
    K = 16
    for k in range(K):
        a, b = k * n // K, (k + 1) * n // K
        fc = lo * (hi / lo) ** (k / (K - 1))
        seg_ = bandpass(x[max(0, a - 2000):b], fc * 0.6, min(fc * 1.6, SR / 2 - 100))[-(b - a):]
        out[a:b] = seg_
    if shape == "bell":
        e = np.sin(np.pi * t) ** 2
    elif shape == "rise":
        e = t ** 2.5 * (1 - np.clip((t - 0.92) / 0.08, 0, 1))
    else:
        e = (1 - t) ** 2
    return out * e


def bloop(f0=520, f1=880, dur=0.12):
    n = int(dur * SR)
    t = np.arange(n) / SR
    fr = f0 * (f1 / f0) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    return np.sin(ph) * np.exp(-t * 28) * (1 - np.exp(-t * 2000))


def tick():
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2400 * t) * 0.6 + rng.normal(0, 0.3, n)) * np.exp(-t * 120)


def boom(dur=3.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    fr = 70 * np.exp(-t * 1.2) + 30
    ph = 2 * np.pi * np.cumsum(fr) / SR
    s = np.sin(ph) * np.exp(-t * 1.4)
    s += lowpass(rng.normal(0, 1, n), 180) * np.exp(-t * 1.8) * 0.8
    return s * (1 - np.exp(-t * 200))


def shimmer(dur=1.2, base=84, n_notes=7, up=True, seed=0):
    r = np.random.default_rng(seed)
    out = np.zeros(int((dur + 2.5) * SR))
    scale = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24]
    for k in range(n_notes):
        m = base + scale[k % len(scale)] if up else base + scale[(n_notes - 1 - k) % len(scale)]
        b = bell(m, 2.2) * 0.5
        i = int(k * dur / n_notes * SR)
        out[i:i + len(b)] += b * r.uniform(0.6, 1.0)
    return out


def piano(m, vel=1.0, dur=3.5):
    """felt piano: inharmonic partials, faster decay for upper partials, soft hammer"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    B = 0.00035
    sig = np.zeros(n)
    for k in range(1, 11):
        fk = f * k * math.sqrt(1 + B * k * k)
        if fk > 12000:
            break
        amp = (1.0 / k ** 1.25) * (0.6 + 0.4 * vel) ** (k * 0.4)
        dec = 0.9 + 0.55 * k + f / 900
        sig += amp * np.sin(2 * np.pi * fk * t + rng.uniform(0, 0.3)) * np.exp(-t * dec)
    # two-stage decay (prompt + aftersound)
    sig *= 0.75 * np.exp(-t * 0.9) + 0.25
    ham = lowpass(rng.normal(0, 1, int(0.012 * SR)), 2500) * np.linspace(1, 0, int(0.012 * SR)) * 0.25
    sig[: len(ham)] += ham
    sig *= (1 - np.exp(-t * 900))
    rel = int(0.25 * SR)
    sig[-rel:] *= np.linspace(1, 0, rel)
    return lowpass(sig, 4200 + 2500 * vel) * vel


def strings(m, dur, a=1.6, r=2.2, bright=0.45):
    n = int((dur + r) * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    sig = np.zeros(n)
    for v in range(5):
        det = (v - 2) * 0.07
        vib = 1 + 0.0035 * np.sin(2 * np.pi * (4.6 + v * 0.3) * t + v)
        ff = f * 2 ** (det / 12)
        ph = 2 * np.pi * ff * np.cumsum(vib) / SR
        for k in range(1, 10):
            if ff * k > 7000:
                break
            sig += np.sin(k * ph + v * k) / (k ** (2.0 - bright))
    sig *= env_adsr(n, a, r + 0.4)
    return lowpass(sig, 2600) / 9


def air(dur):
    n = int(dur * SR)
    x = bandpass(rng.normal(0, 1, n), 2500, 9000)
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * np.arange(n) / SR)
    return x * lfo * 0.04

def build_voice():
    """Narration bus: each recorded line placed at its start time, high-passed, gently compressed, a touch of room."""
    v = np.zeros(N)
    for i, ln in enumerate(LINES):
        x, sr = sf.read(os.path.join(EP, "voice", f"line_{i:02d}.wav"))
        x = resample_poly(x, SR, sr)
        place(v, x, T[i])
    v = highpass(v, 70)
    env = np.abs(v)
    env = lowpass(env, 12)
    thr = 0.12
    gain = np.where(env > thr, (thr / np.maximum(env, 1e-6)) ** 0.35, 1.0)
    v = v * gain
    v = v / np.max(np.abs(v)) * 0.7
    vs = np.stack([v, v], 1)
    vs = vs * 0.94 + verb(v * 0.06, 1.0) * 0.5
    return vs, env


# ----------------------------------------------------------------------------------------------------------------
# Automatic score for new episodes. Describe the music in timeline.py as MUSIC_PLAN:
# MUSIC_PLAN = {
#   "sections": [("wonder", 0.0, 21.0), ("tension", 21.0, 49.0), ("resolve", 49.0, DURATION)],
#   "hush": [(1.3, 2.4)],            # music drops out here (e.g. the big "vanish" moment)
#   "hang": [1.5],                   # single high piano note left hanging (pairs well with a hush)
#   "pops": [9.8, 14.1],             # UI pop-ins (cards, badges, icons)
#   "drops": [1.6, 31.4],            # things vanishing (bloop down + falling shimmer)
#   "rises": [54.9],                 # things appearing / returning (swell + bloop up + rising shimmer)
#   "booms": [21.3],                 # deep hit for a dramatic line
#   "ticks": [(32.0, 34.5, 10)],     # (start, end, count) ticking counter
# }
# Scene-change whooshes are added automatically from SCENES.
# ----------------------------------------------------------------------------------------------------------------
MOODS = {
    # chords as MIDI notes (bass first), bar length in seconds
    "wonder": dict(bar=2.4, chords=[[38, 45, 50, 53, 57], [34, 41, 46, 50, 57], [29, 41, 45, 48, 52], [36, 43, 48, 50, 55]],
                   arps=[[50, 57, 62, 57], [46, 53, 58, 53], [41, 48, 53, 48], [48, 55, 60, 55]],
                   mel=[[69, 74, 77], [65, 70, 74], [69, 72, 77], [67, 72, 76]]),
    "tension": dict(bar=3.2, chords=[[26, 38, 45, 50, 53], [26, 38, 46, 50, 53], [31, 43, 46, 50, 55], [33, 45, 49, 52, 55]],
                    ost=[38, 45, 50, 45]),
    "resolve": dict(bar=2.2, chords=[[34, 46, 53, 57, 62], [33, 45, 53, 57, 60], [29, 41, 48, 57, 64, 67, 72]]),
}


def auto_music(plan):
    pno, strg, low, fx = np.zeros(N), np.zeros(N), np.zeros(N), np.zeros(N)
    hum = np.random.default_rng(12)
    hush = plan.get("hush", [])

    def hushed(t):
        return any(a - 0.05 < t < b for a, b in hush)

    def P_(m, t0, vel=0.8):
        if t0 >= 0 and not hushed(t0):
            place(pno, piano(m, vel), t0 + hum.normal(0, 0.008))

    def S_(notes, t0, dur, g=1.0, bright=0.45):
        for m in notes:
            place(strg, strings(m, dur, bright=bright), t0, g)

    secs = plan["sections"]
    for si, (mood, a, b) in enumerate(secs):
        M = MOODS[mood]
        last = si == len(secs) - 1
        if mood == "wonder":
            t, k = a, 0
            while t < b - 0.1:
                ch = M["chords"][k % 4]
                d = min(M["bar"], b - t) + 0.2
                if not hushed(t):
                    S_(ch[1:], t, d, 0.55)
                    P_(ch[0], t, 0.55)
                for j in range(4):
                    tj = t + j * M["bar"] / 4
                    if tj >= b - 0.1:
                        break
                    P_(M["arps"][k % 4][j], tj, 0.38)
                    if k >= 1 and j < 3 and (k % 2 == 1 or j != 2):
                        P_(M["mel"][k % 4][j], tj + 0.02, 0.6 if j == 0 else 0.48)
                t += M["bar"]; k += 1
        elif mood == "tension":
            t, k = a, 0
            while t < b:
                S_(M["chords"][k % 4], t, min(M["bar"], b - t + 0.2), 0.75, 0.3)
                t += M["bar"]; k += 1
            t, i = a + 0.4, 0
            while t < b - 0.2:
                inten = (t - a) / max(1e-6, b - a)
                P_(M["ost"][i % 4] + (12 if inten > 0.6 and i % 8 >= 4 else 0), t, 0.3 + 0.25 * inten)
                t += 0.4 - 0.08 * inten; i += 1
            t = a + 1.0
            while t < b - 0.1:
                inten = (t - a) / max(1e-6, b - a)
                place(low, sub_pulse(44, 0.8), t, 0.7 * (0.4 + 0.6 * inten))
                place(low, sub_pulse(44, 0.6), t + 0.2, 0.35 * (0.4 + 0.6 * inten))
                t += 1.1 - 0.3 * inten
        elif mood == "resolve":
            ch = M["chords"]
            span = b - a
            t1 = a + min(1.9, span * 0.3)
            S_(ch[0], a, t1 - a + 0.2, 0.6)
            P_(ch[0][0] + 12, a, 0.5); P_(62, a + 0.6, 0.45)
            if last:
                t2 = a + span * 0.55
                S_(ch[1], t1, t2 - t1 + 0.2, 0.62)
                P_(45, t1, 0.5); P_(60, t1 + 0.5, 0.42)
                S_(ch[2], t2, b - t2 + 0.3, 0.9, 0.55)
                P_(41, t2, 0.7); P_(53, t2, 0.5)
                for j, m in enumerate([69, 72, 76, 79, 81]):
                    P_(m, t2 + 0.15 + j * 0.16, 0.5 - j * 0.04)
                place(fx, shimmer(1.0, 81, 8, True, 3), t2 - 0.05, 0.4)
            else:
                S_(ch[1], t1, b - t1 + 0.2, 0.62)
    for t in plan.get("hang", []):
        place(pno, piano(86, 0.45), t)
    place(fx, air(DURATION + 0.5), 0, 1.0)
    mus = np.zeros((N, 2))
    mus += verb(pno * 0.55, 0.42)
    mus += verb(strg * 0.5, 0.55)
    mus += verb(fx * 0.6, 0.6)
    mus += np.stack([low, low], 1) * 0.5
    fade = np.ones(N)
    fi = int(0.12 * SR); fade[:fi] = np.linspace(0, 1, fi)
    fo = int(1.4 * SR); fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
    return mus * fade[:, None]


def auto_sfx(plan):
    s = np.zeros((N, 2))
    for name, st, en in SCENES[1:]:
        place(s, verb(noise_swell(0.55, 300, 3500, "bell") * 0.22, 0.3), st - 0.1)
    for t0 in plan.get("pops", []):
        place(s, verb(bloop(520, 860) * 0.6, 0.25), t0)
    for t0 in plan.get("drops", []):
        place(s, noise_swell(0.35, 800, 6000, "rise") * 0.2, t0 - 0.33)
        place(s, bloop(850, 190, 0.17) * 0.8, t0 + 0.22)
        place(s, verb(shimmer(0.45, 87, 6, False, 1) * 0.3, 0.6), t0 + 0.25)
    for t0 in plan.get("rises", []):
        place(s, noise_swell(0.5, 500, 5000, "rise") * 0.2, t0 - 0.48)
        place(s, bloop(300, 900, 0.2) * 0.6, t0)
    for t0 in plan.get("booms", []):
        place(s, verb(boom(3.0) * 0.9, 0.3), t0 - 0.05)
    for (a, b, n) in plan.get("ticks", []):
        for k in range(int(n)):
            place(s, tick() * 0.35, a + (b - a) * k / max(1, n - 1))
    return s
