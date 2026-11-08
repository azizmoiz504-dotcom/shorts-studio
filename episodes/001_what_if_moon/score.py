"""Episode 001 score: hand-written music + sound effects (custom, not the auto score)."""
from audio import *
from timeline import T, E, S8, S13, EV, DURATION, SCENES, LINES, Wd


def build_music():
    pno = np.zeros(N)
    strg = np.zeros(N)
    low = np.zeros(N)
    fx = np.zeros(N)
    hum = np.random.default_rng(12)

    def P_(m, t0, vel=0.8):
        if t0 < 0:
            return
        place(pno, piano(m, vel), t0 + hum.normal(0, 0.008))

    def S_(notes, t0, dur, g=1.0, bright=0.45):
        for m in notes:
            place(strg, strings(m, dur, bright=bright), t0, g)

    v = EV["vanish"]
    BAR = 2.4
    # ---- A: wonder.  Dm9 | Bbmaj7 | Fmaj7 | Cadd9
    chords = [[38, 45, 50, 53, 57], [34, 41, 46, 50, 57], [29, 41, 45, 48, 52], [36, 43, 48, 50, 55]]
    melody = [[69, 74, 77, 76], [65, 70, 74, 72], [69, 72, 77, 76], [67, 72, 76, 74]]
    lh = [[50, 57, 62, 57], [46, 53, 58, 53], [41, 48, 53, 48], [48, 55, 60, 55]]
    tA_end = T[7] - 0.15
    t = 0.0
    k = 0
    while t < tA_end:
        ch = chords[k % 4]
        if not (v - 0.4 < t < EV["gone"] + 0.2):
            S_(ch[1:], t, min(BAR, tA_end - t) + 0.2, 0.55)
            P_(ch[0], t, 0.55)
        for j in range(4):
            tj = t + j * BAR / 4
            if tj >= tA_end - 0.1:
                break
            silent = v - 0.05 < tj < EV["gone"] + 0.55
            if silent:
                continue
            P_(lh[k % 4][j], tj, 0.38)
            if k >= 1 and j in (0, 1, 2) and (k % 2 == 1 or j != 2):
                P_(melody[k % 4][j], tj + 0.02, 0.62 if j == 0 else 0.5)
        t += BAR
        k += 1
    # the vanish: a single high note left hanging, then a low swell on "gone"
    P_(86, v + 0.25, 0.45)
    S_([26, 38], EV["gone"] - 0.1, 1.6, 0.8, 0.3)
    # ---- B: tension (scary part -> eclipse).  Dm | Bb/D | Gm | A7
    tB0, tB1 = T[7] - 0.05, T[13] + 0.25
    Bc = [[26, 38, 45, 50, 53], [26, 38, 46, 50, 53], [31, 43, 46, 50, 55], [33, 45, 49, 52, 55]]
    t = tB0
    k = 0
    while t < tB1:
        d = min(3.2, tB1 - t + 0.2)
        S_(Bc[k % 4], t, d, 0.75, 0.3)
        t += 3.2
        k += 1
    # ostinato low piano: millions-of-years clock
    t = Wd(8, 0) - 0.05
    pat = [38, 45, 50, 45]
    i = 0
    while t < T[13] - 0.2:
        inten = min(1, max(0, (t - T[10]) / (T[12] + 3 - T[10])))
        P_(pat[i % 4] + (12 if inten > 0.6 and i % 8 >= 4 else 0), t, 0.3 + 0.25 * inten)
        t += 0.4 - 0.08 * inten
        i += 1
    # high tension melody (sparse)
    for j, (tt, m) in enumerate([(Wd(9, 2), 74), (Wd(9, 6), 77), (Wd(9, 11), 76), (Wd(10, 3), 72), (Wd(10, 11), 70),
                                  (Wd(11, 0), 69), (Wd(11, 10), 74), (Wd(11, 13), 73), (Wd(12, 7), 77), (Wd(12, 10), 76)]):
        P_(m, tt, 0.5)
    # pulses that speed up toward the extremes
    t = T[10]
    while t < T[13] - 0.1:
        inten = min(1, max(0, (t - T[10]) / (T[12] + 3 - T[10])))
        place(low, sub_pulse(44, 0.8), t, 0.7 * (0.4 + 0.6 * inten))
        place(low, sub_pulse(44, 0.6), t + 0.2, 0.35 * (0.4 + 0.6 * inten))
        t += 1.1 - 0.3 * inten
    # ---- eclipse: everything drops to a thin high string
    S_([81, 86], T[13] - 0.1, S13 - T[13] + 0.6, 0.35, 0.6)
    # ---- C: resolve.  Bbmaj7 -> F/A ... -> Fmaj9 on "still there"
    tC = S13 + 0.35
    S_([34, 46, 53, 57, 62], tC, 1.9, 0.6)
    P_(46, tC, 0.5); P_(62, tC + 0.6, 0.45); P_(65, tC + 1.2, 0.45)
    tC2 = tC + 1.9
    S_([33, 45, 53, 57, 60], tC2, EV["back"] - tC2 + 0.2, 0.62)
    P_(45, tC2, 0.5); P_(60, tC2 + 0.5, 0.42); P_(64, Wd(14, 2), 0.5); P_(65, Wd(14, 6), 0.55)
    b = EV["back"]
    S_([29, 41, 48, 57, 64, 67, 72], b - 0.05, DURATION - b + 0.3, 0.9, 0.55)
    P_(41, b, 0.7); P_(53, b, 0.5)
    for j, m in enumerate([69, 72, 76, 79, 81]):
        P_(m, b + 0.15 + j * 0.16, 0.5 - j * 0.04)
    place(fx, shimmer(1.0, 81, 8, True, 3), b - 0.05, 0.4)
    place(fx, air(DURATION + 0.5), 0, 1.0)

    mus = np.zeros((N, 2))
    mus += verb(pno * 0.55, 0.42)
    mus += verb(strg * 0.5, 0.55)
    mus += verb(fx * 0.6, 0.6)
    mus += np.stack([low, low], 1) * 0.5
    fade = np.ones(N)
    fi = int(0.12 * SR)
    fade[:fi] = np.linspace(0, 1, fi)
    fo = int(1.4 * SR)
    fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
    return mus * fade[:, None]


def build_sfx():
    s = np.zeros((N, 2))
    v = EV["vanish"]
    place(s, noise_swell(0.35, 800, 6000, "rise") * 0.25, v - 0.33)
    place(s, bloop(900, 180, 0.18) * 0.9, v + 0.25)
    place(s, verb(shimmer(0.5, 88, 6, False, 1) * 0.35, 0.6), v + 0.27)
    # transitions
    for name, st, en in SCENES[1:]:
        mid = st + 0.2
        place(s, verb(noise_swell(0.55, 300, 3500, "bell") * 0.22, 0.3), mid - 0.3)
    # UI pops
    for t0, f0, f1 in [(EV["tide_card"], 500, 820), (EV["third"], 620, 980), (EV["reef_card"], 500, 820),
                       (EV["reef_lose"] + 0.55, 700, 420), (EV["top"], 520, 860), (T[13] + 0.55, 700, 380)]:
        place(s, verb(bloop(f0, f1) * 0.6, 0.25), t0)
    for k in range(4):
        place(s, verb(bloop(560 + 90 * k, 880 + 90 * k) * 0.45, 0.25), EV["seasons"] + k * 0.16, pan=-0.5 + k * 0.33)
    # tide moon vanish + space moon vanish
    for t0 in (EV["tide_vanish"], EV["wobble"]):
        place(s, bloop(800, 200, 0.16) * 0.7, t0 + 0.22)
        place(s, verb(shimmer(0.4, 86, 5, False, 2) * 0.25, 0.6), t0 + 0.24)
    # scary boom
    place(s, verb(boom(3.0) * 0.9, 0.3), EV["scary"] - 0.05)
    # million-year ticks
    last = None
    t = EV["wobble"] + 0.7
    while t < E[10] + 0.3:
        from lib import ease_io, seg
        n = 1 + int(9 * ease_io(seg(t, EV["wobble"] + 0.7, E[10] + 0.3)))
        if n != last:
            place(s, tick() * 0.35, t)
            last = n
        t += 1 / 60
    # moon returns
    b = EV["back"]
    place(s, noise_swell(0.5, 500, 5000, "rise") * 0.2, b - 0.48)
    place(s, bloop(300, 900, 0.2) * 0.6, b)
    return s
