"""Episode 006 - What if you could see like a bee? One function per scene window in timeline.SCENES."""
import math, random
from lib import *
from kit import *
from timeline import T, E, EV, LINES, Wd, DURATION, SCENES, NFRAMES, FPS

SEND = {n: b for n, a, b in SCENES}
SSTART = {n: a for n, a, b in SCENES}
TEND = (NFRAMES - 1) / FPS
ADD = skia.BlendMode.kPlus
SKY_STARS = Stars(240, seed=5, region=(0, 0, W, 980))


def leave(t, name, lead=0.85):
    """cards and badges leave before the transition out of their scene"""
    b = SEND[name]
    return 1 - smooth(seg(t, b - lead, b - lead + 0.35))


def popped(c, x, y, p, fn):
    if p <= 0.01:
        return
    c.save(); c.translate(x, y); c.scale(p, p); c.translate(-x, -y)
    fn(min(1.0, p))
    c.restore()


# ------------------------------------------------------------------------------------------------ twilight meadow
SUNF = (800, 600, 215)          # sunflower head (x, y, r) in the meadow layout
BEE_HOVER = (470, 700)
SMALL = [  # (x, y head, r, col, shade, centre, stem bottom x, rot)
    (175, 1080, 92, "#b48cff", "#7a52d6", "#ffd84d", 210, -8),
    (395, 1175, 74, "#ff8fb8", "#d9548a", "#ffcf6b", 380, 10),
    (95, 1265, 64, "#f4f0ff", "#b9b0e6", "#ffcf3d", 120, 4),
    (585, 1240, 58, "#7fc8ff", "#3f86d6", "#ffd84d", 600, -12),
]


def meadow_sky(c, t):
    c.drawRect(skia.Rect.MakeXYWH(-80, -80, W + 160, H + 160), P(shader=lin(0, 0, 0, 1120, [hx("#070923"), hx("#141a55"), hx("#25307e"), hx("#5a3d9e"), hx("#c46aa0"), hx("#ffb27a")],
                                                       [0, 0.28, 0.52, 0.74, 0.9, 1.0])))
    # stars fade out toward the warm horizon
    c.save(); c.clipRect(skia.Rect.MakeXYWH(0, 0, W, 980))
    SKY_STARS.draw(c, t, 1.0)
    c.drawRect(skia.Rect.MakeXYWH(0, 520, W, 460), P(shader=lin(0, 520, 0, 980, [hx("#25307e", 0), hx("#4a3a9a", 0.9)])))
    c.restore()


def meadow(c, t, uvp=0.0, sway=1.0):
    """the shared MEADOW layout (open / end). uvp 0..1 = flowers shimmer into their hidden bee colours"""
    meadow_sky(c, t)
    # low setting sun at the left, sinking behind the hills
    sun(c, 150, 1015, 118, t, 1.0, 0.8)
    # far hills (lit rim from the sun)
    hill(c, 1015, [(26, 0.006, 0.4), (14, 0.017, 2.0)], "#4b3c9e", "#ffb27a", 0.55)
    hill(c, 1075, [(30, 0.005, 2.6), (12, 0.02, 0.3)], "#3a2f86", "#c2b6ff", 0.35)
    # meadow ground: green at dusk, darker toward the bottom (texture zone)
    top = hill(c, 1150, [(22, 0.004, 1.0), (8, 0.013, 0.2)], lin(0, 1100, 0, 1920, [hx("#2f8a68"), hx("#236a5c"), hx("#1a3d4c"), hx("#141f3e")], [0, 0.2, 0.55, 1]), "#8fe8b0", 0.45)
    # soft warm light across the top of the meadow from the sun
    c.drawRect(skia.Rect.MakeXYWH(0, 1100, W, 200), P(shader=lin(0, 1100, 0, 1300, [hx("#ffcf6b", 0.10), hx("#ffcf6b", 0)]), mode=ADD))
    rnd = random.Random(3)
    # back grass tufts
    for k in range(70):
        gx = rnd.uniform(-20, W + 20)
        gy = rnd.uniform(1150, 1330) + 20
        hgt = rnd.uniform(26, 60)
        ang = 0.22 * math.sin(t * 1.3 + gx * 0.01) * sway + rnd.uniform(-0.2, 0.2)
        col = mixhex("#3aa878", "#226a58", rnd.random())
        c.drawPath(path_from([(gx - 5, gy), (gx + math.sin(ang) * hgt, gy - hgt), (gx + 5, gy)], True), P(hx(col)))
    # small flowers on stems
    for i, (x, y, r, col, shade, cen, bx, rot) in enumerate(SMALL):
        sw = 7 * math.sin(t * 1.1 + i * 1.7) * sway
        stem(c, bx, 1500, x + sw, y + r * 0.2, 13, t, bend=-18 + i * 8, leaves=[(0.35, 1 if i % 2 else -1, r * 0.75)])
        flower(c, x + sw, y, r, col, shade, cen, rot=rot + sw * 0.6, uv=uvp, guides=uvp)
    # the big sunflower
    fx, fy, fr = SUNF
    sw = 6 * math.sin(t * 0.8) * sway
    stem(c, 900, 1700, fx + sw + 10, fy + fr * 0.3, 30, t, bend=60,
         leaves=[(0.32, -1, 170), (0.55, 1, 150), (0.75, -1, 120)])
    # back of the head (slight 3/4 view)
    c.drawOval(skia.Rect.MakeXYWH(fx + sw - fr * 0.42 + 26, fy - fr * 0.42 + 12, fr * 0.84, fr * 0.84), P(hx("#2f7a4e")))
    sunflower_head(c, fx + sw, fy, fr, t, uv=uvp, rot=-6 + sw * 0.4, sq=0.97)
    # front grass (over stems), stays below the caption band's top area
    for k in range(60):
        gx = rnd.uniform(-20, W + 20)
        gy = rnd.uniform(1330, 1920)
        hgt = rnd.uniform(40, 90)
        ang = 0.25 * math.sin(t * 1.2 + gx * 0.013) * sway + rnd.uniform(-0.25, 0.25)
        col = mixhex("#1f5a50", "#173a46", rnd.random())
        c.drawPath(path_from([(gx - 7, gy), (gx + math.sin(ang) * hgt, gy - hgt), (gx + 7, gy)], True), P(hx(col)))
    c.drawRect(skia.Rect.MakeXYWH(0, 1500, W, 420), P(shader=lin(0, 1500, 0, 1920, [hx("#0d1236", 0), hx("#0d1236", 0.65)])))


def spectrum(c, t, a, uv_on):
    """rainbow bar (red -> violet) with an extra ULTRAVIOLET slot past violet that switches on"""
    if a <= 0:
        return
    x0, y0, sw, sh = 140, 250, 100, 56
    card(c, x0 - 34, y0 - 74, 7 * sw + 68, sh + 150, a, "#141a4a")
    text(c, "COLOURS YOU SEE", x0 + 3 * sw, y0 - 26, 30, "#c2b6ff", a, TF_POP_SB, track=3)
    cols = ["#ff4d5e", "#ff9a3d", "#ffd84d", "#3ec27a", "#2a8fe6", "#6a5cff"]
    bar = skia.Path(); bar.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0, 6 * sw, sh), sh / 2, sh / 2))
    c.save(); c.clipPath(bar, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeXYWH(x0, y0, 6 * sw, sh), P(shader=lin(x0, 0, x0 + 6 * sw, 0, [hx(k, a) for k in cols])))
    c.drawRect(skia.Rect.MakeXYWH(x0, y0, 6 * sw, sh * 0.4), P(hx("#ffffff", 0.18 * a)))
    c.restore()
    # ultraviolet slot
    ux = x0 + 6 * sw + 12
    slot = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(ux, y0, sw - 12, sh), sh / 2, sh / 2)
    p = clamp(uv_on)
    if p < 1:
        pp = P(hx("#c2b6ff", 0.55 * a * (1 - p)), stroke=3)
        pp.setPathEffect(skia.DashPathEffect.Make([10, 8], 0))
        c.drawRRect(slot, pp)
    if p > 0:
        e = ease_out_back(p)
        cx, cy = ux + (sw - 12) / 2, y0 + sh / 2
        c.save(); c.translate(cx, cy); c.scale(e, e); c.translate(-cx, -cy)
        glow(c, cx, cy, sh * 0.9, "#b98cff", 0.9 * a * min(1, p))
        c.drawRRect(slot, P(shader=lin(ux, 0, ux + sw, 0, [hx("#8f6bff", a), hx("#d7b8ff", a)])))
        c.drawRRect(slot, P(hx("#ffffff", 0.7 * a), stroke=3))
        c.restore()
        text(c, "UV", cx, y0 + sh + 52, 40, "#e3d4ff", a * smooth(p), TF_POP_XB, shadow=1)
        burst(c, cx, cy, 40, seg(p, 0.0, 1.0) * 0.999 if p < 1 else 1, "#e3d4ff")
    text(c, "RED", x0 + 40, y0 + sh + 46, 28, "#ffb3bb", a, TF_POP_SB)
    text(c, "VIOLET", x0 + 5 * sw + 40, y0 + sh + 46, 28, "#c9c0ff", a, TF_POP_SB)


def bee_path_in(t, t0):
    """bee zips in from the left on a looping path and settles at BEE_HOVER"""
    p = seg(t, t0 - 0.35, t0 + 0.95)
    e = ease_out(p)
    hx_, hy = BEE_HOVER
    x = lerp(-140, hx_, e) + 70 * math.sin(e * math.pi) * (1 - e)
    y = hy - 160 * math.sin(e * math.pi) * (1 - e * 0.4) + 12 * math.sin(t * 2.2)
    tilt = -18 * (1 - e) + 4 * math.sin(t * 2.2)
    return x, y, tilt, p


def scene_open(c, t):
    meadow(c, t)
    if t > EV["bee"] - 0.4:
        x, y, tilt, p = bee_path_in(t, EV["bee"])
        bee(c, x, y, 80, t, flip=-1, tilt=tilt)
    a = smooth(seg(t, EV["colour"] - 0.1, EV["colour"] + 0.3)) * leave(t, "open", 0.5)
    sp = ease_out_back(seg(t, EV["colour"] - 0.1, EV["colour"] + 0.3))
    popped(c, 540, 300, sp, lambda q: spectrum(c, t, a, seg(t, EV["on"] - 0.05, EV["on"] + 0.4)))


def scene_end(c, t):
    uvp = smooth(seg(t, EV["every"], EV["every"] + 0.8)) * (1 - smooth(seg(t, EV["colour2"], EV["colour2"] + 0.9)))
    meadow(c, t, uvp=uvp * 0.9)
    # bee hovers, then zips away out of frame on "bee"
    hx_, hy = BEE_HOVER
    p = ease_in(seg(t, EV["bee2"] - 0.1, EV["bee2"] + 1.0))
    x = lerp(hx_, -180, p) - 40 * math.sin(p * math.pi)
    y = hy + 12 * math.sin(t * 2.2) - 260 * p * p
    if p < 1:
        bee(c, x, y, 80, t, flip=-1 if p < 0.05 else 1, tilt=4 * math.sin(t * 2.2) + 20 * p)


# ------------------------------------------------------------------------------------------------ eye
EYE = (650, 800, 320)
EYE_SUN = (40, 800, 180)


def ray(c, pts, p, col, w, a=1.0):
    """glowing polyline revealed from its start; p 0..1 of total length"""
    if p <= 0 or a <= 0:
        return
    L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    tot, want = sum(L), sum(L) * p
    out = [pts[0]]
    for i, l in enumerate(L):
        if want >= l:
            out.append(pts[i + 1]); want -= l
        else:
            k = want / l
            out.append((lerp(pts[i][0], pts[i + 1][0], k), lerp(pts[i][1], pts[i + 1][1], k))); break
    pth = path_from(out, False)
    c.drawPath(pth, P(hx(col, 0.45 * a), stroke=w * 2.6, blur=w * 0.9, mode=ADD))
    c.drawPath(pth, P(hx(col, a), stroke=w))
    c.drawPath(pth, P(hx("#ffffff", 0.45 * a), stroke=w * 0.3))
    return out[-1]


def scene_eye(c, t):
    space_bg(c, t, "#080b29", "#1d2160")
    sx, sy, sr = EYE_SUN
    sun(c, sx, sy, sr, t, 1.0, 0.8)
    ex, ey, R = EYE
    rot = math.degrees(math.atan2(sy - ey, sx - ex))
    lhi = smooth(seg(t, EV["lens"] - 0.1, EV["lens"] + 0.35)) * (0.6 + 0.4 * math.sin(t * 5)) if t > EV["lens"] - 0.1 else 0
    to_w = eye_section(c, ex, ey, R, rot, lens_hi=lhi)
    dist = math.dist((sx, sy), (ex, ey)) - sr * 0.6
    focus = (R * 0.84, 0.0)
    cols = [("#ff4d5e", 0.15), ("#ffd84d", 0.09), ("#3ec27a", -0.09), ("#2a8fe6", -0.15)]
    for k, (col, off) in enumerate(cols):
        ly = off * R
        pts = [to_w(-dist, ly), to_w(-R * 1.05, ly), to_w(-R * 0.66, ly), to_w(*focus)]
        p = ease_io(seg(t, EV["sunlight"] + 0.1 * k, EV["sunlight"] + 1.5 + 0.1 * k))
        ray(c, pts, p, col, 9)
    if t > EV["sunlight"] + 1.6:
        fx, fy = to_w(*focus)
        glow(c, fx, fy, 16, "#ffffff", 0.6 + 0.2 * math.sin(t * 6))
    # ultraviolet ray: crawls toward the lens and is stopped at its front face on "blocks"
    stop = to_w(-R * 0.80, -0.0 * R)
    uly = 0.0
    up = ease_out(seg(t, EV["ultra"] - 0.1, EV["blocks"]))
    if up > 0:
        start = to_w(-dist, -0.02 * R)
        mid = to_w(-R * 1.05, -0.02 * R)
        end = to_w(-R * 0.80, -0.02 * R)
        flick = 1.0 - 0.25 * smooth(seg(t, EV["blocks"], EV["blocks"] + 0.4))
        tip = ray(c, [start, mid, end], up, "#b07cff", 16, flick)
        if tip:
            for k in range(6):   # sparkles riding the ultraviolet beam
                fx_ = start[0] + ((t * 260 + k * 90) % max(1, tip[0] - start[0]))
                sparkle(c, fx_, start[1] + 10 * math.sin(t * 6 + k), 6, "#efe4ff", 0.85 * flick, t * 90 + k * 30)
        if tip and up < 1:
            glow(c, tip[0], tip[1], 14, "#d0b0ff", 0.9)
        if t > EV["blocks"] - 0.05:
            q = seg(t, EV["blocks"] - 0.05, EV["blocks"] + 0.6)
            burst(c, end[0], end[1], 40, q, "#e0ccff")
            glow(c, end[0], end[1], 26, "#c9a8ff", 0.8 + 0.2 * math.sin(t * 7))
    # labels
    lx, ly = to_w(-R * 0.66, -R * 0.30)
    la = smooth(seg(t, EV["lens"] - 0.1, EV["lens"] + 0.3)) * leave(t, "eye", 0.55)
    if la > 0:
        c.drawLine(lx, ly - 12, lx, ly - 90, P(hx("#ffffff", 0.85 * la), stroke=4))
        c.drawCircle(lx, ly - 12, 6, P(hx("#ffffff", 0.9 * la)))
        pill(c, lx, ly - 125, "LENS", la, 40, "#1a1f55")
    ya = smooth(seg(t, SSTART["eye"] + 0.3, SSTART["eye"] + 0.8)) * (1 - smooth(seg(t, EV["blocks"] - 0.25, EV["blocks"])))
    pill(c, 600, 1225, "YOUR EYE", ya, 40, "#1a1f55")
    pa = ease_out_back(seg(t, EV["blocks"], EV["blocks"] + 0.35)) * leave(t, "eye", 0.55)
    popped(c, 540, 1230, pa, lambda q: pill(c, 540, 1230, "UV BLOCKED", leave(t, "eye", 0.55), 48, "#5b34b8"))


# ------------------------------------------------------------------------------------------------ bee close-up
BEE_FL = [(150, 1150, 88, "#b48cff", "#7a52d6", "#ffd84d"), (330, 1235, 80, "#ff8fb8", "#d9548a", "#ffcf6b"),
          (540, 1265, 84, "#f4f0ff", "#b9b0e6", "#ffcf3d"), (750, 1235, 80, "#7fc8ff", "#3f86d6", "#ffd84d"),
          (930, 1150, 88, "#ffd84d", "#f0a21c", "#ff9a3d")]


def scene_bee(c, t):
    meadow_sky(c, t)
    hill(c, 1015, [(26, 0.006, 0.4), (14, 0.017, 2.0)], "#4b3c9e", "#ffb27a", 0.45)
    hill(c, 1075, [(30, 0.005, 2.6), (12, 0.02, 0.3)], "#3a2f86", "#c2b6ff", 0.35)
    hill(c, 1150, [(22, 0.004, 1.0), (8, 0.013, 0.2)], lin(0, 1100, 0, 1920, [hx("#2f8a68"), hx("#236a5c"), hx("#1a3d4c"), hx("#141f3e")], [0, 0.2, 0.55, 1]), "#8fe8b0", 0.45)
    uv = smooth(seg(t, EV["painted"] - 0.1, EV["painted"] + 0.7))
    for i, (x, y, r, col, sh, cen) in enumerate(BEE_FL):
        p = ease_out_back(seg(t, EV["flowers"] + 0.08 * i, EV["flowers"] + 0.08 * i + 0.45))
        sw = 5 * math.sin(t * 1.2 + i)
        stem(c, x, 1560, x + sw, y + r * 0.2, 12, t, bend=10, leaves=[(0.45, 1 if i % 2 else -1, 60)])
        flower(c, x + sw, y, r, col, sh, cen, rot=sw + 40 * (1 - p), uv=uv * 0.92, guides=uv, open_=lerp(0.35, 1.0, p))
    c.drawRect(skia.Rect.MakeXYWH(0, 1500, W, 420), P(shader=lin(0, 1500, 0, 1920, [hx("#0d1236", 0), hx("#0d1236", 0.65)])))
    eg = smooth(seg(t, EV["see"] - 0.05, EV["see"] + 0.35)) * (0.75 + 0.25 * math.sin(t * 5))
    bee(c, 560, 700 + 16 * math.sin(t * 2.0), 210, t, flip=-1, tilt=3 * math.sin(t * 2.0), eye_glow=eg)
    pa = ease_out_back(seg(t, EV["see"], EV["see"] + 0.35)) * leave(t, "bee", 0.55)
    popped(c, 540, 300, pa, lambda q: pill(c, 540, 300, "BEES SEE UV", leave(t, "bee", 0.55), 50, "#5b34b8"))


# ------------------------------------------------------------------------------------------------ sunflower (HERO)
SFX, SFY, SFR = 540, 760, 425


def scene_sunflower(c, t):
    meadow_sky(c, t)
    hill(c, 1120, [(26, 0.006, 0.4), (14, 0.017, 2.0)], "#4b3c9e", "#ffb27a", 0.45)
    hill(c, 1210, [(22, 0.004, 1.0), (8, 0.013, 0.2)], lin(0, 1180, 0, 1920, [hx("#2f8a68"), hx("#236a5c"), hx("#1a3d4c"), hx("#141f3e")], [0, 0.2, 0.55, 1]), "#8fe8b0", 0.45)
    stem(c, 560, 1920, SFX + 10, SFY + 200, 46, t, bend=-30, leaves=[(0.45, -1, 230), (0.62, 1, 200)])
    rot = 3 * math.sin(t * 0.7) + 6 * seg(t, EV["sunflower"], EV["sunflower"] + 2.0)
    sc = 0.92 + 0.08 * ease_out(seg(t, SSTART["sunflower"], EV["sunflower"] + 0.6))
    r = SFR * sc
    # back of the head peeks out (3/4 view hint)
    c.drawCircle(SFX + 18, SFY + 16, r * 0.43, P(hx("#2a6e48")))
    sunflower_head(c, SFX, SFY, r, t, uv=0.0, rot=rot)
    # ultraviolet scan: everything above the line is shown in bee colours
    sp = ease_io(seg(t, EV["uv"], EV["bullseye"]))
    if sp > 0:
        y = lerp(SFY - r - 40, SFY + r + 40, sp)
        rings = seg(t, EV["bullseye"], EV["bullseye"] + 1.6) if t > EV["bullseye"] else 0
        c.save(); c.clipRect(skia.Rect.MakeLTRB(0, 0, W, y))
        sunflower_head(c, SFX, SFY, r, t, uv=1.0, rot=rot, rings=rings)
        c.restore()
        if sp < 1:
            la = smooth(seg(t, EV["uv"], EV["uv"] + 0.3)) * (1 - smooth(seg(sp, 0.9, 1.0)))
            c.drawRect(skia.Rect.MakeXYWH(0, y - 18, W, 36), P(shader=lin(0, y - 18, 0, y + 18, [hx("#b98cff", 0), hx("#d9c2ff", 0.9 * la), hx("#b98cff", 0)]), mode=ADD))
            c.drawLine(0, y, W, y, P(hx("#ffffff", 0.9 * la), stroke=3))
            for k in range(7):
                sparkle(c, (k * 157 + t * 400) % W, y, 7, "#f2eaff", 0.9 * la, t * 120 + k * 40)
    # bee lands in the middle of the bullseye
    lp = seg(t, EV["appears"] - 0.2, EV["appears"] + 0.9)
    if lp > 0:
        e = ease_out(lp)
        bx = lerp(W + 160, SFX + 30, e)
        by = lerp(SFY - 380, SFY - 40, e) - 90 * math.sin(e * math.pi)
        bee(c, bx, by + 4 * math.sin(t * 3) * e, 105, t, flip=1, tilt=-14 * (1 - e), flap=1 - 0.7 * smooth(seg(lp, 0.85, 1.0)), eye_glow=0.6)
    # badge: YOUR EYES -> BEE EYES
    a1 = ease_out_back(seg(t, EV["plain"], EV["plain"] + 0.35)) * (1 - smooth(seg(t, EV["bullseye"] - 0.25, EV["bullseye"])))
    popped(c, 540, 235, a1, lambda q: pill(c, 540, 235, "YOUR EYES", 1, 46, "#1a1f55"))
    a2 = ease_out_back(seg(t, EV["bullseye"], EV["bullseye"] + 0.35)) * leave(t, "sunflower", 0.55)
    popped(c, 540, 235, a2, lambda q: pill(c, 540, 235, "BEE EYES", leave(t, "sunflower", 0.55), 46, "#5b34b8"))


# ------------------------------------------------------------------------------------------------ nectar guides
GF = [(540, 710, 300, 8, "#b48cff", "#7a52d6"), (165, 1130, 200, -14, "#ff8fb8", "#d9548a"), (925, 290, 190, 20, "#7fc8ff", "#3f86d6"),
      (950, 1120, 150, 34, "#f4f0ff", "#b9b0e6"), (110, 300, 130, -6, "#ffd84d", "#f0a21c"),
      (400, 1760, 190, 12, "#b48cff", "#7a52d6"), (880, 1700, 170, -25, "#ff8fb8", "#d9548a")]
LEAVES = [(80, 380, 260, 30), (980, 820, 300, -140), (420, 1300, 240, 100), (760, 1180, 260, 160), (300, 140, 220, -60),
          (1000, 1350, 220, -20), (40, 820, 240, 70)]


def scene_guides(c, t):
    c.drawRect(skia.Rect.MakeXYWH(-80, -80, W + 160, H + 160), P(shader=lin(0, 0, 0, H, [hx("#130f3e"), hx("#1d1756"), hx("#120e38")])))
    # leaves below the flowers (bee colours: leaves are dark)
    LV = []
    for k, (x, y, r, rot, col, sh) in enumerate(GF):
        for j in range(4):
            LV.append((x, y, r * 1.45, rot + 35 + j * 90 + 17 * math.sin(j * 2.1 + k)))
    for k, (x, y, sz, ang) in enumerate(LV):
        c.save(); c.translate(x, y); c.rotate(ang + 3 * math.sin(t * 0.8 + k))
        lf = path_from([(0, 0), (sz * 0.32, -sz * 0.3), (sz * 0.22, -sz * 0.85), (0, -sz), (-sz * 0.24, -sz * 0.75), (-sz * 0.3, -sz * 0.28)], True, 1.0)
        c.drawPath(lf, P(shader=lin(-sz * 0.3, 0, sz * 0.3, 0, [hx("#3a3290"), hx("#2c2676"), hx("#211c5e")])))
        c.drawLine(0, -sz * 0.05, 0, -sz * 0.85, P(hx("#4a42a6", 0.8), stroke=4))
        c.restore()
    gp = seg(t, EV["marks"] - 0.1, EV["marks"] + 0.9)
    for k, (x, y, r, rot, col, sh) in enumerate(GF):
        rr = rot + 4 * math.sin(t * 0.6 + k)
        flower(c, x, y, r, col, sh, "#ffd84d", rot=rr, uv=0.82, guides=gp)
        # runway lights running inward along each petal's centre stripe
        la = smooth(seg(t, EV["strips"] - 0.1, EV["strips"] + 0.3)) * leave(t, "guides", 0.6) * (1 if k < 5 else 0)
        if la > 0:
            for i in range(6):
                an = math.radians(rr + 60 * i)
                dx, dy = math.sin(an), -math.cos(an)
                for j in range(4):
                    f = ((t * 0.9 + j / 4) % 1.0)
                    d = lerp(r * 0.88, r * 0.3, f)
                    al = la * math.sin(f * math.pi)
                    px, py = x + dx * d, y + dy * d
                    c.drawCircle(px, py, r * 0.035, P(hx("#fff3b0", 0.9 * al)))
                    glow(c, px, py, r * 0.03, "#ffe9a0", 0.9 * al)
    # arrows pulse inward on the big flower
    x, y, r = GF[0][0], GF[0][1], GF[0][2]
    ap = seg(t, EV["point"] - 0.05, EV["point"] + 1.2)
    if 0 < ap < 1:
        for i in range(6):
            an = math.radians(GF[0][3] + 30 + 60 * i)
            d = lerp(r * 1.15, r * 0.95, ease_out(ap))
            arrow_chev(c, x + math.sin(an) * d, y - math.cos(an) * d, 34, math.degrees(an) + 90, "#ffe9a0", math.sin(ap * math.pi))
    # nectar sparkle + bee arrives on "food"
    fp = seg(t, EV["food"] - 0.6, EV["food"] + 0.4)
    if fp > 0:
        e = ease_out(fp)
        bx, by = lerp(-180, x + 40, e), lerp(260, y - 70, e) - 120 * math.sin(e * math.pi)
        bee(c, bx, by + 5 * math.sin(t * 3), 120, t, flip=-1, tilt=10 * (1 - e), flap=1 - 0.6 * smooth(seg(fp, 0.8, 1)))
    if t > EV["food"]:
        burst(c, x, y, 70, seg(t, EV["food"], EV["food"] + 0.8), "#fff3b0")
    ba = smooth(seg(t, SSTART["guides"] + 0.2, SSTART["guides"] + 0.6)) * leave(t, "guides", 0.6)
    pill(c, 540, 235, "BEE EYES", ba, 46, "#5b34b8")


# ------------------------------------------------------------------------------------------------ north
NE = (540, 880, 370)


def pin_pos():
    x, y, r = NE
    return x, y - r * math.sin(math.radians(72))


def scene_north(c, t):
    space_bg(c, t, "#080b29", "#1d2160")
    x, y, r = NE
    planet(c, x, y, r, lon0=-85 + (t - SSTART["north"]) * 6, tilt=0, t=t)
    # "head north": a dashed arrow climbs from the middle of the globe to the top
    ap = ease_io(seg(t, EV["north"] - 0.15, EV["north"] + 0.6))
    px, py = pin_pos()
    if ap > 0:
        y1 = lerp(y, py + 70, ap)
        pp = P(hx("#ffffff", 0.9), stroke=8)
        pp.setPathEffect(skia.DashPathEffect.Make([22, 16], -t * 60))
        c.drawLine(x, y, x, y1, pp)
        arrow_chev(c, x, y1 - 4, 28, -90, "#ffffff", 1)
    # pin + badge on "Arctic"
    pp_ = ease_out_back(seg(t, EV["arctic"] - 0.05, EV["arctic"] + 0.35))
    if pp_ > 0:
        c.save(); c.translate(px, py); c.scale(pp_, pp_)
        glow(c, 0, 0, 24, "#ffffff", 0.7)
        pin = path_from([(0, 0), (-30, -58), (-30, -86), (0, -110), (30, -86), (30, -58)], True, 1.0)
        c.drawPath(pin, P(shader=lin(-30, -110, 30, 0, [hx("#ff8fb8"), hx("#e8467a")])))
        c.drawCircle(0, -78, 13, P(hx("#ffffff")))
        c.drawPath(pin, P(hx("#ffffff", 0.6), stroke=3))
        c.restore()
        pill(c, px, py - 175, "ARCTIC", min(1, pp_) * leave(t, "north", 0.45), 48, "#1a1f55")


# ------------------------------------------------------------------------------------------------ arctic
from kit import _uvc
ARC_STARS = Stars(220, seed=12, region=(0, 0, W, 860))
RD = (235, 0.95)              # reindeer x, scale
WF_X, WF_S = 885, 0.82        # wolf stand x, scale
LICHEN = [(140, 1170, 1.0), (470, 1100, 0.8), (620, 1220, 1.1), (330, 1250, 0.9), (930, 1200, 0.8), (700, 1080, 0.7)]


def snow_y(x):
    """main snowfield surface (the ridge the animals stand on)"""
    return 1000 + 38 * math.sin(x * 0.0042 + 0.6) + 14 * math.sin(x * 0.011 + 2.0)


def arctic_uv(t):
    on1 = smooth(seg(t, EV["snow"], EV["snow"] + 0.9))
    off = smooth(seg(t, T[13] - 0.05, T[13] + 0.35))
    on2 = smooth(seg(t, EV["dark2"] - 0.1, EV["dark2"] + 0.5))
    return on1 * (1 - off) + on2


def scene_arctic(c, t):
    u = arctic_uv(t)
    c.drawRect(skia.Rect.MakeXYWH(-80, -80, W + 160, H + 160), P(shader=lin(0, 0, 0, 900, [hx(_uvc("#070923", "#0c0626", u)), hx(_uvc("#1a2266", "#22125e", u)), hx(_uvc("#3b4aa8", "#4a2a9e", u))])))
    ARC_STARS.draw(c, t, 1.0)
    # aurora ribbons (a real light source -> additive)
    for k, (yy, col, amp) in enumerate([(300, "#3ec27a", 60), (380, "#2ad6c0", 45), (250, "#7a6cff", 40)]):
        pts = [(x, yy + amp * math.sin(x * 0.006 + t * 0.4 + k * 1.7) + 20 * math.sin(x * 0.017 - t * 0.6)) for x in range(-120, W + 121, 40)]
        pth = path_from(pts, False, 1.0)
        c.drawPath(pth, P(hx(col, 0.22 * (1 - 0.5 * u)), stroke=90, blur=40, mode=ADD))
        c.drawPath(pth, P(hx(col, 0.18 * (1 - 0.5 * u)), stroke=22, blur=10, mode=ADD))
    # far snowy hills
    snow_lit = _uvc("#dfe3ff", "#f6f1ff", u)
    snow_sh = _uvc("#a9b1e6", "#d9ccff", u)
    hill(c, 860, [(40, 0.004, 1.2), (18, 0.013, 0.3)], _uvc("#8f98d6", "#c9b8ff", u), "#ffffff", 0.5)
    for k, px in enumerate([60, 140, 210, 860, 930, 1010]):
        gy = 860 + 40 * math.sin(px * 0.004 + 1.2) + 18 * math.sin(px * 0.013 + 0.3)
        pine(c, px, gy + 14, 60 + 14 * (k % 2), _uvc("#2a2f6e", "#160c3a", u), "#c2b6ff", 0.3)
    # main snowfield
    pts = [(x, snow_y(x)) for x in range(-100, W + 101, 20)]
    sf = path_from(pts + [(W + 100, H + 100), (-100, H + 100)], True)
    c.drawPath(sf, P(shader=lin(0, 960, 0, 1920, [hx(snow_lit), hx(snow_sh), hx(_uvc("#5a62b0", "#7656c8", u)), hx(_uvc("#2c3170", "#3a2878", u)), hx(_uvc("#1a1d4e", "#21164e", u))], [0, 0.24, 0.4, 0.56, 1])))
    c.drawPath(path_from(pts, False), P(hx("#ffffff", 0.8), stroke=4))
    # snow glows in ultraviolet (it reflects most of it)
    if u > 0:
        c.drawRect(skia.Rect.MakeXYWH(-80, 880, W + 160, 420), P(shader=lin(0, 880, 0, 1300, [hx("#b98cff", 0.0), hx("#c9a8ff", 0.26 * u), hx("#b98cff", 0.10 * u), hx("#b98cff", 0)], [0, 0.35, 0.7, 1]), mode=ADD))
        sh_ = smooth(seg(t, EV["shines"] - 0.3, EV["shines"] + 0.4)) * u
        rnd = random.Random(4)
        for k in range(26):
            sx_, sy_ = rnd.uniform(20, W - 20), rnd.uniform(1010, 1260)
            if sy_ < snow_y(sx_) + 10:
                continue
            tw = 0.5 + 0.5 * math.sin(t * 3 + k * 1.3)
            sparkle(c, sx_, sy_, 5 + 3 * tw, "#ffffff", sh_ * tw, k * 20)
    # lichen clumps: faint sage on snow, DARK in ultraviolet
    lp = smooth(seg(t, EV["lichen"] - 0.1, EV["lichen"] + 0.4))
    for k, (lx, ly, sc) in enumerate(LICHEN):
        ly = max(ly, snow_y(lx) + 40)
        rnd = random.Random(k + 9)
        col = _uvc("#bccaa8", "#2a1660", u * max(lp, 1.0 if t > EV["lichen"] + 0.4 else lp))
        al = lerp(0.55, 1.0, u)
        hi = _uvc("#e4ecd2", "#4a2c8e", u * max(lp, 1.0 if t > EV["lichen"] + 0.4 else lp))
        c.drawOval(skia.Rect.MakeXYWH(lx - 50 * sc, ly + 2 * sc, 100 * sc, 14 * sc), P(hx("#5c63a8", 0.25), blur=4))
        c.saveLayerAlpha(None, int(255 * al))
        bumps = []
        for j in range(11):
            dx = rnd.uniform(-26, 26) * sc
            br = rnd.uniform(10, 15) * sc * (1 - abs(dx) / (80 * sc))
            dy = -br * 0.6 + rnd.uniform(-3, 3) * sc
            bumps.append((lx + dx, ly + dy, br))
        for (bx_, by_, br) in bumps:
            c.drawCircle(bx_, by_, br, P(hx(col)))
        for (bx_, by_, br) in bumps:
            c.drawCircle(bx_ - br * 0.25, by_ - br * 0.3, br * 0.4, P(hx(hi, 0.5)))
        c.restore()
        if t > EV["lichen"] and u > 0.5:
            q = seg(t, EV["lichen"] + k * 0.08, EV["lichen"] + k * 0.08 + 0.9)
            if 0 < q < 1:
                c.drawOval(skia.Rect.MakeXYWH(lx - 60 * sc - 30 * q, ly - 22 * sc - 12 * q, (120 * sc + 60 * q), (44 * sc + 24 * q)), P(hx("#ffe9a0", 0.8 * (1 - q)), stroke=4))
    # reindeer on the ridge (grazing, lifts its head on "Reindeer")
    rx, rs = RD
    hd = 1 - ease_io(seg(t, EV["reindeer"] - 0.2, EV["reindeer"] + 0.6))
    eg = smooth(seg(t, EV["uv2"] - 0.1, EV["uv2"] + 0.3)) * (1 - 0.5 * smooth(seg(t, EV["snow"], EV["snow"] + 1)))
    c.drawOval(skia.Rect.MakeXYWH(rx - 175 * rs, snow_y(rx) - 10, 350 * rs, 22), P(hx("#5c63a8", 0.35), blur=6))
    reindeer(c, rx, snow_y(rx) + 4, rs, t, head=hd, uv=u * 0.9, eye_glow=eg)
    # white wolf walks in from the right during line 13
    wp = seg(t, T[13] - 0.1, EV["wolf"] + 0.2)
    if wp > 0:
        wx = lerp(W + 260, WF_X, ease_out(wp))
        c.drawOval(skia.Rect.MakeXYWH(wx - 140 * WF_S, snow_y(wx) - 8, 300 * WF_S, 20), P(hx("#5c63a8", 0.3), blur=6))
        wolf(c, wx, snow_y(wx) + 4, WF_S, t, walk=1 - smooth(seg(wp, 0.75, 1.0)), uv=u if t > EV["wolf"] else 0)
    # badges
    la = leave(t, "arctic", 0.6)
    b1 = smooth(seg(t, EV["snow"], EV["snow"] + 0.4)) * (1 - smooth(seg(t, T[13] - 0.1, T[13] + 0.2)))
    b2 = smooth(seg(t, T[13] + 0.1, T[13] + 0.4)) * (1 - smooth(seg(t, EV["dark2"] - 0.25, EV["dark2"])))
    b3 = smooth(seg(t, EV["dark2"], EV["dark2"] + 0.35)) * la
    pill(c, 540, 235, "REINDEER EYES", max(b1, b3), 46, "#5b34b8")
    pill(c, 540, 235, "YOUR EYES", b2, 46, "#1a1f55")
    fa = ease_out_back(seg(t, EV["food2"], EV["food2"] + 0.35)) * (1 - smooth(seg(t, T[13] - 0.4, T[13] - 0.1)))
    popped(c, 720, 1000, fa, lambda q: pill(c, 720, 1000, "FOOD", 1, 38, "#1a1f55"))


def stub(name):
    def f(c, t):
        space_bg(c, t)
        text(c, name.upper(), 540, 700, 80, "#ffffff", 1, TF_POP_XB)
    return f


SCENE_FN = {"open": scene_open, "eye": scene_eye, "bee": scene_bee, "sunflower": scene_sunflower,
            "guides": scene_guides, "north": scene_north, "arctic": scene_arctic, "end": scene_end}
