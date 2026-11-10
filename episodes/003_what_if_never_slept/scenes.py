"""Episode 003 - What if you never slept? One function per scene window."""
import math, random
from lib import *
from kit import *
from timeline import T, E, EV, LINES, Wd, DURATION

SPD = 9.0      # sky rotation (deg/s) while the nights fly by
TRAIL = 30.0   # star-trail length (deg)
R0 = -12.0     # sky angle on the first and last frame (seamless loop)
M_SKY = 0.32   # dim starlight: the Milky Way shows
WIN_X, WIN_Y = 898, 1252           # the cabin's front window (world coords of landscape())
FOC = (760, 1150)                  # camera focus when close on the cabin
Z_CLOSE = 1.7

BX, BY, BS = 540, 760, 330         # the brain: centre and half-width


def cabin_cam(c, k):
    """k = 0: the full landscape, k = 1: close on the cabin"""
    z = lerp(1.0, Z_CLOSE, k)
    fx, fy = lerp(W / 2, FOC[0], k), lerp(H * 0.45, FOC[1], k)
    c.translate(W / 2, H * 0.45); c.scale(z, z); c.translate(-fx, -fy)


def window_glow(c, win, t):
    if win <= 0.01:
        return
    fl = 1.0 + 0.04 * math.sin(t * 11) * math.sin(t * 3.7)
    c.drawCircle(WIN_X, WIN_Y, 120, P(shader=rad(WIN_X, WIN_Y, 120, [hx("#ffb84d", 0.30 * win * fl), hx("#ffb84d", 0.08 * win), hx("#ffb84d", 0)], [0, 0.45, 1]), mode=skia.BlendMode.kPlus))


def switch(t, t0, up=True):
    """lamp switching: quick ramp with a tiny flicker, never a single-frame jump"""
    u = seg(t, t0 - 0.04, t0 + 0.22)
    v = smooth(u) * (1 - 0.35 * math.sin(u * math.pi * 3) * (1 - u))
    return v if up else 1 - v


# ------------------------------------------------------------------ 1: tonight, you stop sleeping
def scene_cabin_open(c, t):
    win = switch(t, EV["stop"])
    k = 1 - ease_io(seg(t, EV["ever"] - 0.2, EV["ever"] + 1.3))
    rot = R0 - SPD * max(0.0, t - EV["ever"] + 0.1) * smooth(seg(t, EV["ever"] - 0.1, EV["ever"] + 0.6))
    trail = TRAIL * ease_io(seg(t, EV["ever"], EV["ever"] + 1.4))
    c.save()
    cabin_cam(c, k)
    landscape(c, t, moon_s=0.0, m=M_SKY, sky_rot=rot, trail=trail, win=win)
    window_glow(c, win, t)
    c.restore()


def scene_cabin_end(c, t):
    win = switch(t, EV["out"], up=False)
    ts, dur = EV["out"] + 1.4, 1.4
    if t >= ts:
        rem = 0.0
    elif t >= ts - dur:
        rem = SPD * (ts - t) ** 2 / (2 * dur)
    else:
        rem = SPD * dur / 2 + SPD * (ts - dur - t)
    rot = R0 + rem
    trail = TRAIL * (1 - ease_io(seg(t, EV["out"] - 0.2, ts)))
    k = ease_io(seg(t, EV["out"] - 0.5, EV["out"] + 1.6))
    c.save()
    cabin_cam(c, k)
    # time runs relative to the end so clouds/fireflies/twinkle land exactly where frame 1 starts (seamless loop)
    landscape(c, t - DURATION, moon_s=0.0, m=M_SKY, sky_rot=rot, trail=trail, win=win)
    window_glow(c, win, t)
    c.restore()


# ------------------------------------------------------------------ 2: a third of your life back
def sun_icon(c, x, y, r, a=1.0):
    if a <= 0:
        return
    glow(c, x, y, r, "#ffd84d", 0.6 * a, 2.0)
    for k in range(8):
        an = k / 8 * 2 * math.pi
        c.drawLine(x + math.cos(an) * r * 1.25, y + math.sin(an) * r * 1.25, x + math.cos(an) * r * 1.6,
                   y + math.sin(an) * r * 1.6, P(hx("#fff0a8", a), stroke=r * 0.22))
    c.drawCircle(x, y, r, P(hx("#ffe27a", a)))
    c.drawCircle(x - r * 0.2, y - r * 0.2, r * 0.55, P(hx("#fff3c4", 0.6 * a)))


def moon_icon(c, x, y, r, a=1.0, bg="#3b3394"):
    if a <= 0:
        return
    pth = skia.Op(circ_path(x, y, r), circ_path(x + r * 0.55, y - r * 0.35, r * 0.85), skia.PathOp.kDifference_PathOp)
    c.drawPath(pth, P(hx("#e8e2ff", a)))


def scene_life(c, t):
    space_bg(c, t, "#080b29", "#18195a")
    cx, cy, R, w = 540, 790, 290, 96
    rect = skia.Rect.MakeXYWH(cx - R, cy - R, 2 * R, 2 * R)
    ap = ease_out_back(seg(t, T[2] - 0.5, T[2] + 0.1), 1.2)
    c.save(); c.translate(cx, cy); c.scale(0.85 + 0.15 * ap, 0.85 + 0.15 * ap); c.rotate(-30 * (1 - ap)); c.translate(-cx, -cy)
    sw = ease_io(seg(t, EV["win"] - 0.1, EV["win"] + 0.8))      # the sleep third sweeps to gold
    # soft shadow ring
    c.drawCircle(cx, cy, R, P(hx("#05061e", 0.45), stroke=w + 18, blur=12))
    a0 = -90
    awake = skia.Path(); awake.addArc(rect, a0 + 1.5, 237)
    c.drawPath(awake, P(shader=lin(cx - R, cy - R, cx + R, cy + R, [hx("#ffe27a"), hx("#ffb84d")]), stroke=w, cap=False))
    sl = skia.Path(); sl.addArc(rect, a0 + 241.5, 117)
    c.drawPath(sl, P(hx("#3b3394"), stroke=w, cap=False))
    if sw > 0:
        gp = skia.Path(); gp.addArc(rect, a0 + 241.5, 117 * sw)
        c.drawPath(gp, P(shader=lin(cx - R, cy - R, cx + R, cy + R, [hx("#ffe27a"), hx("#ffb84d")]), stroke=w, cap=False))
    # inner rim light + gaps
    c.drawCircle(cx, cy, R - w / 2 - 3, P(hx("#a596ff", 0.35), stroke=3))
    for an in (a0, a0 + 240):
        r_ = math.radians(an)
        c.drawLine(cx + math.cos(r_) * (R - w / 2 - 6), cy + math.sin(r_) * (R - w / 2 - 6), cx + math.cos(r_) * (R + w / 2 + 6),
                   cy + math.sin(r_) * (R + w / 2 + 6), P(hx("#0b0d33"), stroke=8 * (1 - sw) + 0.01))
    # icons on the ring
    sa = math.radians(a0 + 120)
    sun_icon(c, cx + math.cos(sa) * R, cy + math.sin(sa) * R, 26)
    ma = math.radians(a0 + 300)
    mx, my = cx + math.cos(ma) * R, cy + math.sin(ma) * R
    moon_icon(c, mx, my, 28, 1 - smooth(seg(sw, 0.5, 0.9)))
    sun_icon(c, mx, my, 26 * pop(t, EV["win"] + 0.55, 0.4), min(1, pop(t, EV["win"] + 0.55, 0.4)))
    burst(c, mx, my, 40, seg(t, EV["win"] + 0.5, EV["win"] + 1.3), "#fff2b0", 10, 3)
    for k in range(6):
        ph = (t * 0.7 + k / 6) % 1
        an = math.radians(a0 + 241.5 + 117 * (k + 0.5) / 6)
        sparkle(c, cx + math.cos(an) * (R + 70 * ph), cy + math.sin(an) * (R + 70 * ph), 9 * math.sin(ph * math.pi),
                "#fff2b0", sw * math.sin(ph * math.pi), t * 50)
    # centre label
    text(c, "YOUR LIFE", cx, cy + 16, 50, "#e8ecff", ap, tf=TF_POP_XB, track=4)
    c.restore()
    pp = pop(t, EV["third"], 0.45)
    if pp > 0.01:
        c.save(); c.translate(540, 300); c.scale(pp, pp)
        rrect(c, -300, -58, 600, 116, 58, P(hx("#ffd84d")))
        text(c, "+1/3 OF YOUR LIFE", 0, 20, 52, "#1a1440", tf=TF_POP_XB)
        c.restore()


# ------------------------------------------------------------------ 3: the night shift (fluid waves, rinse, memories)
_rnd = random.Random(5)
CRUMBS = [(-0.62, -0.30), (-0.40, -0.52), (-0.10, -0.60), (0.20, -0.66), (0.44, -0.44), (0.70, -0.32), (-0.75, 0.0),
          (-0.30, -0.25), (0.12, -0.30), (0.40, -0.10), (0.66, -0.02), (-0.20, 0.38), (0.10, 0.22), (-0.50, 0.20)]
CRUMB_SZ = [_rnd.uniform(0.85, 1.25) for _ in range(60)]
MORE = [(-0.86, -0.18), (-0.70, -0.46), (-0.52, -0.62), (-0.26, -0.74), (0.02, -0.78), (0.32, -0.74), (0.58, -0.58),
        (0.82, -0.30), (0.86, 0.04), (0.74, 0.20), (0.50, 0.14), (0.28, 0.04), (-0.02, 0.00), (-0.56, -0.12),
        (-0.84, 0.10), (-0.36, 0.48), (0.00, 0.44), (0.24, 0.36), (-0.12, -0.44), (0.56, -0.20), (-0.44, 0.04),
        (0.36, -0.36), (-0.66, -0.24), (0.14, -0.50)]
STARS_AT = [(-0.70, -0.20), (-0.46, -0.56), (-0.08, -0.70), (0.32, -0.62), (0.66, -0.40), (0.78, -0.02), (0.40, 0.18),
            (-0.30, 0.06)]
HIPPO = (0.02, 0.26)


def crumb(c, x, y, r, a=1.0):
    if a <= 0 or r <= 0:
        return
    pth = path_from([(x - r, y + r * 0.35), (x - r * 0.75, y - r * 0.55), (x + r * 0.1, y - r * 0.9), (x + r * 0.9, y - r * 0.35),
                     (x + r * 0.95, y + r * 0.45), (x + r * 0.1, y + r * 0.8)], True, 1.0)
    c.drawPath(pth, P(hx("#c9741f", a)))
    c.save(); c.clipPath(pth, doAntiAlias=True)
    c.drawCircle(x - r * 0.25, y - r * 0.35, r * 0.85, P(hx("#f5a640", a)))
    c.restore()


def sediment(c, t, x, y, s, level, a=1.0):
    """waste settling in the bottom of the brain like golden sand; level = top of the pile in brain units (draw clipped)"""
    if a <= 0 or level > 0.75:
        return
    top = [(x + s * (-1.1 + i * 0.1), y + s * (level + 0.025 * math.sin(i * 1.3 + t * 1.5) + 0.04 * math.sin(i * 0.5)))
           for i in range(23)]
    pth = path_from(top + [(x + s * 1.2, y + s * 1.2), (x - s * 1.2, y + s * 1.2)], True, 0.7)
    c.drawPath(pth, P(shader=lin(0, y + s * level, 0, y + s * (level + 0.5), [hx("#ffbf5e", a), hx("#d9822e", a)])))
    c.save(); c.clipPath(pth, doAntiAlias=True)
    rnd = random.Random(3)
    for k in range(70):
        gx, gy = x + s * rnd.uniform(-1.0, 1.0), y + s * (level + rnd.uniform(0.04, 0.6))
        c.drawCircle(gx, gy, s * rnd.uniform(0.010, 0.018), P(hx("#b8661f", 0.45 * a)))
    c.restore()
    c.drawPath(path_from(top, False, 0.7), P(hx("#ffe0a0", 0.9 * a), stroke=s * 0.014))


def wave_bands(c, t, t0, amp, x, y, s, period=1.6):
    """bands of cleaning fluid sweeping up through the brain (draw inside the brain clip)"""
    if amp <= 0 or t < t0 - 2:
        return
    for k in range(3):
        u = ((t - t0) / period + k / 3) % 1.0
        yc = y + s * lerp(0.75, -1.05, u)
        env = amp * math.sin(u * math.pi) ** 0.7
        top = [(x + s * (-1.1 + i * 0.1), yc - s * 0.10 + s * 0.035 * math.sin(i * 0.9 + t * 3 + k)) for i in range(23)]
        bot = [(x + s * (1.1 - i * 0.1), yc + s * 0.10 + s * 0.035 * math.sin((22 - i) * 0.9 + t * 3 + k + 1)) for i in range(23)]
        pth = path_from(top + bot, True, 0.7)
        c.drawPath(pth, P(hx("#5ec8ff", 0.42 * env), blur=s * 0.03))
        c.drawPath(path_from(top, False, 0.7), P(hx("#d9f3ff", 0.75 * env), stroke=s * 0.016))


def scene_brain_sleep(c, t):
    space_bg(c, t, "#070923", "#15184f")
    moon(c, 180, 270, 62, 1.0, glow_a=0.9)
    x, y, s = BX, BY, BS
    bp = pop(t, EV["brain"] - 0.25, 0.55)
    tint = 0.42 * smooth(seg(t, EV["deep"] - 0.3, EV["deep"] + 0.6))
    wav = smooth(seg(t, EV["waves"] - 0.3, EV["waves"] + 0.3)) * (1 - smooth(seg(t, EV["replays"] - 0.6, EV["replays"])))
    wav = wav * (1 + 0.4 * smooth(seg(t, EV["wash"] - 0.2, EV["wash"] + 0.3)))
    rinse = seg(t, EV["rinse"] - 0.25, EV["waste"] + 0.4)

    def inner(cc):
        wave_bands(cc, t, EV["waves"] - 0.2, wav, x, y, s)

    def over(cc):
        # waste settled at the bottom drains away down the brainstem
        sediment(cc, t, x, y, s, lerp(0.30, 0.80, ease_in(rinse)), 1 - smooth(seg(rinse, 0.7, 1.0)))
        # memories: sparks loop out of the memory centre and settle in the outer folds as stars
        hx0, hy0 = x + s * HIPPO[0], y + s * HIPPO[1]
        for k, (u, v) in enumerate(STARS_AT):
            t0 = EV["replays"] - 0.2 + k * 0.17
            p = seg(t, t0, t0 + 1.1)
            if p <= 0:
                continue
            tx, ty = x + s * u, y + s * v
            mxp, myp = (hx0 + tx) / 2 + s * 0.35 * math.sin(k * 2.1), (hy0 + ty) / 2 - s * 0.25
            if p < 1:
                e = ease_io(p)
                for j in range(7):
                    ee = max(0.0, e - j * 0.03)
                    qx = (1 - ee) ** 2 * hx0 + 2 * (1 - ee) * ee * mxp + ee * ee * tx
                    qy = (1 - ee) ** 2 * hy0 + 2 * (1 - ee) * ee * myp + ee * ee * ty
                    glow(cc, qx, qy, s * 0.035 * (1 - j * 0.12), "#ffe6a0", 0.9 * (1 - j * 0.14), 2.2)
                    cc.drawCircle(qx, qy, s * 0.02 * (1 - j * 0.12), P(hx("#fff6d8", 1 - j * 0.14)))
        # constellation lines between the saved memories
        la = smooth(seg(t, EV["saves"] - 0.1, EV["saves"] + 0.5))
        if la > 0:
            for k in range(len(STARS_AT) - 1):
                (u0, v0), (u1, v1) = STARS_AT[k], STARS_AT[k + 1]
                q = ease_io(seg(t, EV["saves"] + k * 0.08, EV["saves"] + k * 0.08 + 0.35))
                if q > 0:
                    x0, y0 = x + s * u0, y + s * v0
                    cc.drawLine(x0, y0, lerp(x0, x + s * u1, q), lerp(y0, y + s * v1, q), P(hx("#fff2c4", 0.75 * la), stroke=s * 0.010))
        for k, (u, v) in enumerate(STARS_AT):
            t0 = EV["replays"] - 0.2 + k * 0.17 + 1.1
            sa = pop(t, t0, 0.35)
            if sa > 0.01:
                tw = 0.8 + 0.2 * math.sin(t * 5 + k * 1.3)
                glow(cc, x + s * u, y + s * v, s * 0.04, "#ffe27a", min(1, sa) * tw, 2.4)
                sparkle(cc, x + s * u, y + s * v, s * 0.022 * sa * (1.0 + 0.25 * (k % 2)), "#fff6d0", min(1, sa), 0)

    c.save(); c.translate(x, y); c.scale(lerp(0.4, 1.0, bp), lerp(0.4, 1.0, bp)); c.translate(-x, -y)
    brain_side(c, x, y, s, a=min(1, bp * 1.5), inner=inner, over=over, tint=tint)
    c.restore()
    burst(c, x, y - s * 0.15, s * 0.28, seg(t, EV["brain"] - 0.2, EV["brain"] + 0.6), "#ffd9ec", 12, 5)
    # NIGHT SHIFT badge
    na = pop(t, EV["night"], 0.45) * (1 - smooth(seg(t, EV["deep"] + 1.4, EV["deep"] + 1.8)))
    if na > 0.01:
        c.save(); c.translate(540, 300); c.scale(na, na)
        rrect(c, -240, -54, 480, 108, 54, P(hx("#ffd84d")))
        moon_icon(c, -170, 0, 26, 1.0)
        c.drawPath(skia.Op(circ_path(-170, 0, 26), circ_path(-170 + 14, -9, 22), skia.PathOp.kDifference_PathOp), P(hx("#1a1440")))
        text(c, "NIGHT SHIFT", 28, 19, 50, "#1a1440", tf=TF_POP_XB)
        c.restore()
    # small label while the fluid flows
    la = smooth(seg(t, EV["waves"], EV["waves"] + 0.4)) * (1 - smooth(seg(t, EV["replays"] - 0.6, EV["replays"] - 0.2)))
    if la > 0:
        text(c, "brain fluid", 540, 330, 46, "#bfeaff", la, tf=TF_POP_SB, shadow=1, track=2)
    ma = smooth(seg(t, EV["saves"], EV["saves"] + 0.4)) * (1 - smooth(seg(t, T[7] - 0.55, T[7] - 0.3)))
    if ma > 0:
        text(c, "memories saved", 540, 330, 46, "#ffe58a", ma, tf=TF_POP_SB, shadow=1, track=2)


# ------------------------------------------------------------------ 4: without sleep, it piles up
def scene_pileup(c, t):
    space_bg(c, t, "#0a0c2e", "#221d62")
    sy = lerp(560, 330, ease_out(seg(t, EV["without"] - 0.4, EV["without"] + 1.2)))
    sun(c, -40, sy, 150, t, 0.95, 0.7)
    x, y, s = BX, BY, BS
    pile = ease_out(seg(t, EV["piles"] - 0.4, EV["piles"] + 1.0))

    def over(cc):
        lvl = lerp(0.36, 0.02, ease_io(seg(t, EV["piles"] - 0.6, EV["waste2"] + 1.4)))
        sediment(cc, t, x, y, s, lvl)
        # new memories try to land, flicker, and slide off
        for k, (u, v) in enumerate(STARS_AT[:5]):
            t0 = EV["memories"] - 0.5 + k * 0.18
            p = seg(t, t0, t0 + 0.7)
            if p <= 0:
                continue
            tx, ty = x + s * u, y + s * v
            sx_, sy_ = tx + s * 0.9, ty - s * 0.9
            fall = ease_in(seg(t, EV["stick"] - 0.3 + k * 0.08, EV["stick"] + 0.6 + k * 0.08))
            px = lerp(sx_, tx, ease_out(p)) + s * 0.1 * fall
            py = lerp(sy_, ty, ease_out(p)) + s * 0.5 * fall
            fl = 0.55 + 0.45 * math.sin(t * 23 + k * 2) if p >= 1 else 1.0
            a_ = (1 - fall) * fl * min(1, p * 3)
            glow(cc, px, py, s * 0.06, "#ffe27a", a_, 2.2)
            sparkle(cc, px, py, s * 0.032, "#fff6d0", a_, t * 40)

    brain_side(c, x, y, s, over=over)
    ba = pop(t, EV["without"] + 0.1, 0.45) * (1 - smooth(seg(t, T[9] - 0.6, T[9] - 0.35)))
    if ba > 0.01:
        c.save(); c.translate(540, 300); c.scale(ba, ba)
        rrect(c, -190, -54, 380, 108, 54, P(hx("#ffd84d")))
        c.drawCircle(-110, 0, 22, P(hx("#ff9a2e")))
        for k in range(8):
            an = k / 8 * 2 * math.pi
            c.drawLine(-110 + math.cos(an) * 30, math.sin(an) * 30, -110 + math.cos(an) * 39, math.sin(an) * 39, P(hx("#ff9a2e"), stroke=5))
        text(c, "AWAKE", 34, 19, 52, "#1a1440", tf=TF_POP_XB)
        c.restore()
    wa = smooth(seg(t, EV["piles"], EV["piles"] + 0.4)) * (1 - smooth(seg(t, EV["memories"] - 0.4, EV["memories"])))
    if wa > 0:
        text(c, "waste piles up", 540, 428, 44, "#ffc27a", wa, tf=TF_POP_SB, shadow=1, track=2)


# ------------------------------------------------------------------ 5: tiny parts fall asleep (hero)
def _spark_points():
    pts = []
    rnd = random.Random(12)
    cer, _, _ = brain_paths(0, 0, 1.0)
    while len(pts) < 42:
        u, v = rnd.uniform(-0.95, 0.95), rnd.uniform(-0.85, 0.52)
        if cer.contains(u, v) and all((u - a) ** 2 + (v - b) ** 2 > 0.02 for a, b, *_ in pts):
            pts.append((u, v, rnd.uniform(0, 6.28), rnd.uniform(2.0, 4.5)))
    return pts


SPARKS = _spark_points()
PATCHES = [(-0.58, -0.36, 0.30), (0.06, 0.36, 0.27), (0.62, -0.30, 0.27)]   # frontal, temporal, back


def scene_local(c, t):
    space_bg(c, t, "#070923", "#141650")
    x, y, s = BX, BY - 10, 350
    z = 1.0 + 0.06 * ease_io(seg(t, EV["strange"] - 0.3, EV["asleep"] + 0.6))
    c.save(); c.translate(x, y); c.scale(z, z); c.translate(-x, -y)
    dark = [smooth(seg(t, EV["asleep"] - 0.15 + i * 0.28, EV["asleep"] + 0.25 + i * 0.28)) for i in range(3)]
    fast = 1 + 0.8 * smooth(seg(t, EV["awake"] - 0.2, EV["awake"] + 0.5))

    def over(cc):
        for i, (u, v, rr) in enumerate(PATCHES):
            if dark[i] > 0:
                px, py = x + s * u, y + s * v
                cc.drawCircle(px, py, s * rr, P(shader=rad(px, py, s * rr, [hx("#1a1650", 0.92 * dark[i]), hx("#1d1858", 0.88 * dark[i]), hx("#221c62", 0)], [0, 0.84, 1])))
                dashed(cc, circ_path(px, py, s * rr * 0.86), P(hx("#c9c0ff", 0.7 * dark[i]), stroke=s * 0.010), s * 0.05, s * 0.035, t * 30)
                for j in range(4):
                    an = j * 1.7 + i
                    sx_, sy_ = px + s * rr * 0.5 * math.cos(an), py + s * rr * 0.45 * math.sin(an)
                    sparkle(cc, sx_, sy_, s * 0.012 * (0.7 + 0.3 * math.sin(t * 4 + j)), "#e8e2ff", dark[i] * 0.9, 0)
        for (u, v, ph, f) in SPARKS:
            off = 0.0
            for i, (pu, pv, rr) in enumerate(PATCHES):
                if (u - pu) ** 2 + (v - pv) ** 2 < (rr * 0.92) ** 2:
                    off = max(off, dark[i])
            tw = 0.5 + 0.5 * math.sin(t * f * fast + ph)
            a_ = (0.35 + 0.65 * tw ** 3) * (1 - off)
            if a_ > 0.02:
                px, py = x + s * u, y + s * v
                cc.drawCircle(px, py, s * 0.05, P(shader=rad(px, py, s * 0.05, [hx("#ffd84d", 0.55 * a_), hx("#ffd84d", 0)]), mode=skia.BlendMode.kPlus))
                cc.drawCircle(px, py, s * 0.008, P(hx("#fff2b8", a_)))

    brain_side(c, x, y, s, over=over, tint=0.3)
    # little z's floating up from each sleeping patch
    for i, (u, v, rr) in enumerate(PATCHES):
        if dark[i] <= 0:
            continue
        for j in range(2):
            ph = ((t - EV["asleep"] - i * 0.28) * 0.55 + j * 0.5) % 1
            if t - EV["asleep"] - i * 0.28 < j * 0.9:
                continue
            zx = x + s * u + s * 0.12 * math.sin(ph * 4 + i) + s * 0.08 * ph
            zy = y + s * v - s * 0.08 - s * 0.45 * ph
            text(c, "z", zx, zy, 40 + 26 * ph, "#e8e2ff", dark[i] * math.sin(ph * math.pi), tf=TF_POP_XB, shadow=1)
    c.restore()
    # wide open eye card
    ea = pop(t, EV["eyes"] - 0.1, 0.45) * (1 - smooth(seg(t, T[12] - 0.55, T[12] - 0.3)))
    if ea > 0.01:
        c.save(); c.translate(540, 260); c.scale(ea, ea)
        rrect(c, -150, -86, 300, 172, 50, P(hx("#1a1f55", 0.94)))
        rrect(c, -150, -86, 300, 172, 50, P(hx("#a596ff", 0.5), stroke=3))
        eye_open(c, 0, 0, 105, 1.0, look=0.15 * math.sin(t * 1.5))
        c.restore()
    la = smooth(seg(t, EV["asleep"] + 0.3, EV["asleep"] + 0.7)) * (1 - smooth(seg(t, EV["eyes"] - 0.5, EV["eyes"] - 0.2)))
    if la > 0:
        text(c, "parts asleep", 540, 300, 50, "#c9c0ff", la, tf=TF_POP_SB, shadow=1, track=2)


# ------------------------------------------------------------------ 6: dolphins sleep with half a brain
SEA_Y = 1060


def scene_dolphin(c, t):
    # night sky + sea
    c.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, SEA_Y, [hx("#080a28"), hx("#1d2470"), hx("#3a3290")], [0, 0.7, 1])))
    STARS_D.draw(c, t, 0.9)
    mx, my = 200, 330
    c.drawCircle(mx, my, 520, P(shader=rad(mx, my, 520, [hx("#8f7dff", 0.25), hx("#8f7dff", 0.06), hx("#8f7dff", 0)], [0, 0.4, 1])))
    moon(c, mx, my, 80, 1.0, glow_a=1.0)
    c.drawRect(skia.Rect.MakeXYWH(0, SEA_Y, W, H - SEA_Y), P(shader=lin(0, SEA_Y, 0, H, [hx("#1d4fae"), hx("#0f2a78"), hx("#0a1650")])))
    for k in range(10):   # moonlight on the water
        yy = SEA_Y + 16 + k * 22
        wv = 150 - k * 9 + 26 * math.sin(t * 2 + k * 1.3)
        c.drawRoundRect(skia.Rect.MakeXYWH(mx - wv / 2 + 14 * math.sin(t * 1.3 + k), yy, wv, 7), 3.5, 3.5, P(hx("#e6deff", 0.5 * (1 - k / 11))))
    for k in range(6):
        yy = SEA_Y + 60 + k * 70
        xx = (k * 260 + t * 18) % (W + 300) - 150
        c.drawLine(xx, yy, xx + 160, yy, P(hx("#7fb0ff", 0.25), stroke=4))
    # the dolphin glides in from the right and rests at the surface
    gx = lerp(1350, 590, ease_out(seg(t, EV["dolphins"] - 0.6, EV["dolphins"] + 1.6)))
    dy = SEA_Y - 30 + 7 * math.sin(t * 1.3)
    ds = 360
    dolphin(c, gx, dy, ds, t, eye=0.0)
    # the water surface covers the lower body (tinted, semi-transparent)
    surf = [(xx, SEA_Y + 6 * math.sin(xx * 0.02 + t * 2.2)) for xx in range(-20, W + 40, 20)]
    c.drawPath(path_from(surf + [(W + 20, H), (-20, H)], True, 0.6), P(hx("#1a4aa8", 0.55)))
    c.drawPath(path_from(surf, False, 0.6), P(hx("#bcd4ff", 0.6), stroke=4))
    # ripples around the dolphin
    for k in range(3):
        ph = (t * 0.5 + k / 3) % 1
        rw = ds * (1.2 + 0.6 * ph)
        c.drawOval(skia.Rect.MakeXYWH(gx - rw, SEA_Y - 6, 2 * rw, 22), P(hx("#d6e6ff", 0.35 * (1 - ph)), stroke=3))
    # top-view brain icon: the right half rests (the dolphin's visible LEFT eye is shut), the left half keeps watch
    bp = pop(t, EV["half"] - 0.6, 0.5) * (1 - smooth(seg(t, T[15] - 0.6, T[15] - 0.3)))
    if bp > 0.01:
        rest = smooth(seg(t, EV["half"] - 0.1, EV["half"] + 0.5))
        watch = smooth(seg(t, EV["other"] - 0.1, EV["other"] + 0.4))
        bx, by = 540, 500
        c.save(); c.translate(bx, by); c.scale(bp, bp); c.translate(-bx, -by)
        if watch > 0:
            glow(c, bx - 80, by, 110, "#ffd84d", 0.45 * watch, 1.8)
        brain_top(c, bx, by, 160, left=1.0, right=1 - rest)
        for j in range(2):
            ph = ((t - EV["half"]) * 0.5 + j * 0.5) % 1
            if rest > 0.5 and t - EV["half"] > j:
                text(c, "z", bx + 80 + 30 * ph, by - 40 - 140 * ph, 40 + 24 * ph, "#e8e2ff", math.sin(ph * math.pi), tf=TF_POP_XB, shadow=1)
        c.restore()
        ra = pop(t, EV["rests"] - 0.05, 0.4) * (1 - smooth(seg(t, T[15] - 0.6, T[15] - 0.35)))
        if ra > 0.01:
            c.save(); c.translate(bx + 125, by + 225); c.scale(ra, ra)
            rrect(c, -110, -38, 220, 76, 38, P(hx("#a596ff")))
            text(c, "resting", 0, 15, 40, "#1a1440", tf=TF_POP_XB)
            c.restore()
        wa = pop(t, EV["watch"] - 0.05, 0.4) * (1 - smooth(seg(t, T[15] - 0.6, T[15] - 0.35)))
        if wa > 0.01:
            c.save(); c.translate(bx - 125, by + 225); c.scale(wa, wa)
            rrect(c, -120, -38, 240, 76, 38, P(hx("#ffd84d")))
            text(c, "on watch", 0, 15, 40, "#1a1440", tf=TF_POP_XB)
            c.restore()


STARS_D = Stars(220, seed=19, region=(0, 0, W, SEA_Y - 40))

SCENE_FN = {
    "cabin_open": scene_cabin_open, "life": scene_life, "brain_sleep": scene_brain_sleep, "pileup": scene_pileup,
    "local": scene_local, "dolphin": scene_dolphin, "cabin_end": scene_cabin_end,
}
