"""Episode 002 - What if Earth stopped spinning? One function per scene window."""
import math, random
from lib import *
from kit import *
from timeline import T, E, EV, LINES, Wd, DURATION

SPD = 9.0      # sky rotation (deg/s) in the star-wheel scenes
TRAIL = 30.0   # star-trail length (deg)
R0 = -12.0     # sky angle at t = 0 (and again at the very last frame -> seamless loop)
M_SKY = 0.32   # dim starlight: Milky Way shows


def braked(t, t_stop, speed, dur):
    """angle travelled by something turning at `speed` that brakes to a halt over `dur` seconds from t_stop"""
    if t < t_stop:
        return speed * t
    u = min(1.0, (t - t_stop) / dur)
    return speed * t_stop + speed * dur * (u - u * u / 2)


def jolt(t, t0, amp, f=22.0, decay=6.0):
    if t < t0:
        return 0.0
    return amp * math.sin((t - t0) * f) * math.exp(-(t - t0) * decay)


def scene_sky_open(c, t):
    st = EV["stop"]
    rot = R0 - braked(t, st, SPD, 0.35)
    trail = TRAIL * (1 - ease_out(seg(t, st, st + 0.55)))
    cam_z = 1.0 + 0.03 * smooth(seg(t, 0, 5.2)) + 0.035 * ease_out_back(seg(t, EV["stops2"], EV["stops2"] + 0.45), 2.0)
    cam_y = jolt(t, st, 9) + jolt(t, EV["stops2"], 12)
    bend = 0.12 * max(0.0, jolt(t, st, 1.0, 9, 3.5)) + 0.22 * max(0.0, jolt(t, EV["stops2"], 1.0, 8, 3.0))
    landscape(c, t, moon_s=0.0, m=M_SKY, cam_z=cam_z, cam_y=cam_y, sky_rot=rot, trail=trail, tree_bend=bend)


def scene_sky_end(c, t):
    a = SCENES_END
    rot = R0 - SPD * (t - DURATION)
    trail = TRAIL * ease_io(seg(t, a + 0.2, EV["spinning"] + 0.2))
    cam_z = 1.0 + 0.03 * (1 - smooth(seg(t, a, DURATION)))
    # time runs relative to the end so clouds/fireflies/twinkle land exactly where frame 1 starts (seamless loop)
    landscape(c, t - DURATION, moon_s=0.0, m=M_SKY, cam_z=cam_z, sky_rot=rot, trail=trail)


SCENES_END = T[14] - 0.55


# ------------------------------------------------------------------ 2: you were moving east
def scene_globe_speed(c, t):
    space_bg(c, t, "#080b29", "#17195a")
    sun(c, -70, 420, 170, t, 1.0, 0.7)
    cx, cy, r = 540, 800, 325
    LM = 12.0                      # marker longitude (on the equator, Africa)
    lon0 = LM + 50 - braked(t - 4.7, EV["hour"] - 4.7, 20.0, 0.55)
    planet(c, cx, cy, r, lon0=lon0, tilt=0, t=t)
    # equator line draws on from the left
    ea = smooth(seg(t, EV["equator"] - 0.2, EV["equator"] + 0.5))
    if ea > 0:
        x1 = cx - r + 2 * r * ease_io(seg(t, EV["equator"] - 0.2, EV["equator"] + 0.6))
        c.save(); c.clipPath(circ_path(cx, cy, r), doAntiAlias=True)
        c.drawLine(cx - r, cy, x1, cy, P(hx("#ffd84d", 0.35 * ea), stroke=16, blur=7, mode=skia.BlendMode.kPlus))
        c.drawLine(cx - r, cy, x1, cy, P(hx("#ffe58a", 0.95 * ea), stroke=5))
        c.restore()
        text(c, "EQUATOR", cx - r + 40, cy - 22, 30, "#ffe58a", ea * (1 - smooth(seg(t, EV["you"] - 0.2, EV["you"] + 0.2))), tf=TF_POP_SB, align="left", shadow=1, track=3)
    # east chevrons riding along the equator
    ca = smooth(seg(t, EV["east"] - 0.2, EV["east"] + 0.3)) * (1 - smooth(seg(t, EV["hour"], EV["hour"] + 0.4)))
    if ca > 0:
        for k in range(5):
            ph = (t * 0.9 + k / 5) % 1
            x = cx - r * 0.85 + ph * r * 1.7
            arrow_chev(c, x, cy + 48, 22, 0, "#ffffff", ca * math.sin(ph * math.pi) * 0.9)
    # the "you" marker on the equator
    lam = math.radians(LM - lon0)
    if math.cos(lam) > 0:
        mx, my = cx + r * math.sin(lam), cy
        ma = pop(t, EV["you"], 0.4)
        if ma > 0.01:
            pr = (t * 1.2) % 1
            c.drawCircle(mx, my, 18 + 30 * pr, P(hx("#ffd84d", 0.8 * (1 - pr) * min(1, ma)), stroke=4))
            glow(c, mx, my, 16, "#ffd84d", min(1, ma), 2.4)
            c.drawCircle(mx, my, 13 * ma, P(hx("#fff6c8")))
            c.drawCircle(mx, my, 13 * ma, P(hx("#ff9a2e"), stroke=4))
            # name tag
            c.save(); c.translate(mx, my - 78); c.scale(ma, ma)
            rrect(c, -58, -30, 116, 56, 28, P(hx("#ffffff", 0.95)))
            c.drawPath(path_from([(-12, 24), (12, 24), (0, 40)], True), P(hx("#ffffff", 0.95)))
            text(c, "YOU", 0, 12, 34, "#1a1440", tf=TF_POP_XB)
            c.restore()
    # speed badge
    bp = pop(t, EV["sixteen"], 0.45)
    if bp > 0.01:
        c.save(); c.translate(540, 300); c.scale(bp, bp)
        rrect(c, -270, -62, 540, 124, 62, P(hx("#ffd84d")))
        text(c, "1,600+ km/h", 0, 22, 66, "#1a1440", tf=TF_POP_XB)
        c.restore()
        text(c, "EASTWARD", 540, 410, 32, "#ffe58a", min(1, bp), tf=TF_POP_SB, shadow=1, track=6)


# ------------------------------------------------------------------ 3: the air keeps going
def scene_winds(c, t):
    w = smooth(seg(t, EV["air"] - 0.3, EV["air"] + 0.6))
    hard = smooth(seg(t, EV["winds"] - 0.3, EV["winds"] + 0.5))
    bend = 0.22 * w + 0.33 * hard + 0.05 * math.sin(t * 9) * w
    cdx = 0
    if t > EV["air"] - 0.3:
        u = t - (EV["air"] - 0.3)
        cdx = 260 * u * u if u < 1.0 else 260 + 520 * (u - 1.0)
    rot = R0 - braked(EV["stop"] + 1, EV["stop"], SPD, 0.35)
    landscape(c, t, moon_s=1.0, m=0.75, sky_rot=rot, trail=0.0, tree_bend=bend, cloud_dx=cdx, show_boat=False,
              cam_z=1.02)
    wind_streaks(c, t, w * (0.6 + 0.4 * hard), 1.0 + 0.4 * hard)
    flying_leaves(c, t, hard)
    # card: this wind vs the strongest hurricane ever measured (~345 km/h vs 1,600+ km/h)
    ap = pop(t, EV["hurricane"] - 0.15, 0.45) * (1 - smooth(seg(t, T[4] - 0.55, T[4] - 0.3)))
    if ap > 0.01:
        cx0, cy0, cw, ch = 90, 940, 900, 230
        c.save(); c.translate(540, cy0 + ch / 2); c.scale(ap, ap); c.translate(-540, -(cy0 + ch / 2))
        card(c, cx0, cy0, cw, ch, 0.94)
        g = ease_out(seg(t, EV["hurricane"], EV["hurricane"] + 0.7))
        bx0, full = 450, 490
        text(c, "strongest hurricane", bx0 - 24, cy0 + 82, 32, "#c9d4ff", tf=TF_POP_SB, align="right")
        rrect(c, bx0, cy0 + 56, max(8, full * 0.215 * g), 40, 20, P(hx("#ff6b8b")))
        text(c, "this wind", bx0 - 24, cy0 + 170, 32, "#ffe58a", tf=TF_POP_SB, align="right")
        rrect(c, bx0, cy0 + 144, max(8, full * g), 40, 20, P(hx("#ffd84d")))
        c.restore()


# ------------------------------------------------------------------ 4: the bulge
def scene_bulge(c, t):
    space_bg(c, t, "#070923", "#15184f")
    sun(c, -60, 360, 140, t, 0.9, 0.6)
    cx, cy, r = 540, 810, 315
    z = lerp(0.84, 1.0, ease_io(seg(t, T[4] - 0.4, EV["spin"] + 0.4)))
    c.save(); c.translate(cx, cy); c.scale(z, z); c.translate(-cx, -cy)
    stop_t = EV["without"] + 0.3
    lon0 = 30 - braked(t - 14.0, stop_t - 14.0, 14.0, 0.8)
    sw = smooth(seg(t, EV["spin"] - 0.2, EV["spin"] + 0.4))
    off = smooth(seg(t, EV["without"] + 0.1, EV["without"] + 0.8))
    sa = (0.55 + 0.45 * sw) * (1 - off)
    show = smooth(seg(t, EV["spin"] + 1.4, EV["bulge"] - 0.1))       # the ocean layer appears on "oceans"
    bul = ease_io(seg(t, EV["bulge"] - 0.2, EV["bulge"] + 0.7))
    flow = ease_io(seg(t, EV["slides"] - 0.2, EV["poles"] + 0.6))
    eq = 0.035 * show + 0.15 * bul * (1 - flow)
    po = 0.012 * show + 0.15 * flow
    pts = []
    for i in range(180):
        ph = i / 180 * 2 * math.pi
        cs, sn = abs(math.cos(ph)), abs(math.sin(ph))
        rr = r * (0.99 + eq * cs ** 2.2 + po * sn ** 2.2 + 0.005 * show * math.sin(ph * 9 + t * 3))
        pts.append((cx + rr * math.cos(ph), cy + rr * math.sin(ph)))
    wp = path_from(pts, True, 1.0)
    spin_arrow(c, cx, cy, r * 1.45, r * 0.24, sa, "#a8e6ff", t, False)
    if show > 0:
        c.drawPath(wp, P(shader=rad(cx - r * 0.3, cy - r * 0.3, r * 1.5, [hx("#3aa8f5", 0.95 * show), hx("#1e6fd0", 0.95 * show)])))
        # wave lines inside the water layer
        for k in range(2):
            wl = []
            for i in range(181):
                ph = i / 180 * 2 * math.pi
                cs, sn = abs(math.cos(ph)), abs(math.sin(ph))
                rr = r * (0.99 + (eq * cs ** 2.2 + po * sn ** 2.2) * (0.45 + 0.25 * k) + 0.004 * math.sin(ph * 14 - t * 3 + k * 2))
                wl.append((cx + rr * math.cos(ph), cy + rr * math.sin(ph)))
            dashed(c, path_from(wl, False, 0.8), P(hx("#bfeaff", 0.55 * show), stroke=3), 34, 26, t * 40 * (1 if k else -1))
        c.drawPath(wp, P(hx("#e6f8ff", 0.9 * show), stroke=5))
    planet(c, cx, cy, r, lon0=lon0, tilt=0, t=t, atmo=0.0)
    spin_arrow(c, cx, cy, r * 1.45, r * 0.24, sa, "#a8e6ff", t, True)
    c.restore()
    # bulge arrows + label
    ba = smooth(seg(t, EV["bulge"], EV["bulge"] + 0.4)) * (1 - smooth(seg(t, EV["without"], EV["without"] + 0.4)))
    if ba > 0:
        for sgn in (-1, 1):
            for k in range(2):
                ph = (t * 1.1 + k / 2) % 1
                x = cx + sgn * (r * 1.24 + ph * 60)
                arrow_chev(c, x, cy - 75, 24, 0 if sgn > 0 else 180, "#ffffff", ba * math.sin(ph * math.pi))
        text(c, "ocean bulge", 540, cy - r - 80, 50, "#bfeaff", ba, tf=TF_POP_SB, shadow=1)
    # water sliding toward the poles: four curved arrows, equator -> pole
    fa = smooth(seg(t, EV["slides"] - 0.3, EV["slides"])) * (1 - smooth(seg(t, E[6] + 0.1, E[6] + 0.5)))
    if fa > 0:
        pr = ease_out(seg(t, EV["slides"] - 0.3, EV["slides"] + 0.9))
        rr = r * 1.30
        for a0, a1 in ((-8, -62), (8, 62), (188, 242), (172, 118)):
            arc_arrow(c, cx, cy, rr, a0, a1, pr, "#ffffff", fa, 7)
    sp = smooth(seg(t, EV["without"] + 0.3, EV["without"] + 0.7)) * (1 - smooth(seg(t, T[7] - 0.6, T[7] - 0.3)))
    if sp > 0:
        text(c, "spin stopped", 540, cy - r - 80, 50, "#ffb3c1", sp, tf=TF_POP_SB, shadow=1)


# ------------------------------------------------------------------ 5: the new world (hero)
def scene_newworld(c, t):
    space_bg(c, t, "#080a28", "#1b1b58")
    sun(c, -50, 300, 130, t, 0.85, 0.6)
    hero = smooth(seg(t, EV["continent"] - 0.1, EV["continent"] + 0.5))
    z = 1.0 + 0.05 * ease_io(seg(t, EV["continent"] - 0.2, EV["continent"] + 1.2))
    c.save(); c.translate(540, 780); c.scale(z, z); c.translate(-540, -780)
    cx, cy, r = 540, 780, 340
    lon0 = 15.0
    k_o = ease_io(seg(t, EV["oceans"] - 0.4, EV["bottom"] + 0.9))
    k_l = 1.0 if t > EV["oceans"] - 0.4 else 0.0
    drain = ease_io(seg(t, EV["oceans"] - 0.4, EV["bottom"] + 0.9))
    planet(c, cx, cy, r, lon0=lon0, tilt=0, t=t, clouds=False)
    new_world(c, cx, cy, r, lon0, lerp(92, 40, k_o), lerp(-92, -33, k_o), k_l, hero, t, drain)
    if hero > 0:
        for k in range(10):
            ph = (t * 0.6 + k / 10) % 1
            an = k / 10 * 2 * math.pi
            x = cx + r * 0.9 * math.cos(an + t * 0.2)
            y = cy + r * 0.18 * math.sin(an * 2 + t)
            sparkle(c, x, y, 9 * math.sin(ph * math.pi), "#fff2b0", hero * math.sin(ph * math.pi), t * 60)
    # labels
    na = pop(t, EV["top"] - 0.1, 0.45)
    if na > 0.01:
        c.save(); c.translate(cx, cy - r * 0.84); c.scale(na, na)
        text(c, "NORTH OCEAN", 0, 14, 40, "#ffffff", 1, tf=TF_POP_XB, shadow=1, track=4)
        c.restore()
    sa = pop(t, EV["bottom"] - 0.1, 0.45)
    if sa > 0.01:
        c.save(); c.translate(cx, cy + r * 0.76); c.scale(sa, sa)
        text(c, "SOUTH OCEAN", 0, 14, 40, "#ffffff", 1, tf=TF_POP_XB, shadow=1, track=4)
        c.restore()
    c.restore()
    ha = pop(t, EV["continent"], 0.5) * (1 - smooth(seg(t, T[9] - 0.6, T[9] - 0.3)))
    if ha > 0.01:
        c.save(); c.translate(540, 250); c.scale(ha, ha)
        rrect(c, -300, -58, 600, 116, 58, P(hx("#ffd84d")))
        text(c, "ONE CONTINENT", 0, 20, 58, "#1a1440", tf=TF_POP_XB)
        c.restore()


# ------------------------------------------------------------------ 6: one day = one year
DAY_DIR = 270.0        # direction (deg, screen) the cabin side of the non-spinning Earth always faces


def scene_dayyear(c, t):
    space_bg(c, t, "#090b2c", "#1a1a56")
    cx, cy = 540, 830
    rx, ry = 320, 345
    sun(c, cx, cy, 130, t, 1.0, 0.9)
    # month dots around the orbit
    oa = smooth(seg(t, T[9] - 0.2, T[9] + 0.4))
    pth = skia.Path(); pth.addOval(skia.Rect.MakeXYWH(cx - rx, cy - ry, 2 * rx, 2 * ry))
    dashed(c, pth, P(hx("#cfc6ff", 0.55 * oa), stroke=4), 14, 12)
    for k in range(12):
        an = k / 12 * 2 * math.pi
        c.drawCircle(cx + rx * math.cos(an), cy + ry * math.sin(an), 6, P(hx("#cfc6ff", 0.6 * oa)))
    # Earth: one orbit; sunrise for the cabin around "once", sunset around "night"
    t_rise, t_set = EV["once"] + 0.1, EV["night"] - 0.75
    w = 180.0 / (t_set - t_rise)                       # deg of orbit per second (half an orbit = daylight)
    th = DAY_DIR - 90 - w * (t - t_rise)               # counter-clockwise orbit (seen from the north)
    an = math.radians(th)
    ex, ey = cx + rx * math.cos(an), cy + ry * math.sin(an)
    er = 100
    planet(c, ex, ey, er, lon0=10, tilt=0, t=0, clouds=True, atmo=0.6, light=(-math.cos(an), -math.sin(an)))
    # night side: the half facing away from the Sun
    c.save(); c.translate(ex, ey); c.rotate(math.degrees(an) - 90)
    c.clipPath(circ_path(0, 0, er + 1), doAntiAlias=True)
    c.drawRect(skia.Rect.MakeXYWH(-er - 4, 0, 2 * er + 8, er + 4), P(hx("#05061e", 0.62)))
    c.restore()
    # the cabin on the side that always faces DAY_DIR
    sun_dir = math.degrees(math.atan2(cy - ey, cx - ex))
    lit = math.cos(math.radians(sun_dir - DAY_DIR))
    night_k = smooth(clamp((-lit + 0.1) * 4))
    d = math.radians(DAY_DIR)
    cabin_icon(c, ex + er * 0.97 * math.cos(d), ey + er * 0.97 * math.sin(d), 2.4, DAY_DIR, night_k)
    # DAY / NIGHT tag next to the Earth
    da = smooth(seg(t, EV["daylight"] - 0.3, EV["daylight"])) * (1 - smooth(seg(t, EV["night"] - 0.45, EV["night"] - 0.2)))
    na = smooth(seg(t, EV["night"] - 0.2, EV["night"] + 0.1)) * (1 - smooth(seg(t, T[12] - 0.6, T[12] - 0.35)))
    tx, ty = ex + (200 if ex < 540 else -200), ey
    for a_, label, col in ((da, "DAY", "#ffd84d"), (na, "NIGHT", "#a596ff")):
        if a_ > 0.01:
            c.save(); c.translate(tx, ty); c.scale(0.7 + 0.3 * a_, 0.7 + 0.3 * a_)
            wdt = 80 + 26 * len(label)
            rrect(c, -wdt / 2, -36, wdt, 72, 36, P(hx(col, a_)))
            text(c, label, 0, 15, 40, "#1a1440", a_, tf=TF_POP_XB)
            c.restore()
    # 1 day = 1 year card
    ca = pop(t, EV["once"], 0.45) * (1 - smooth(seg(t, T[12] - 0.6, T[12] - 0.35)))
    if ca > 0.01:
        c.save(); c.translate(540, 235); c.scale(ca, ca)
        rrect(c, -290, -58, 580, 116, 58, P(hx("#ffffff", 0.95)))
        text(c, "1 DAY = 1 YEAR", 0, 20, 56, "#1a1440", tf=TF_POP_XB)
        c.restore()


# ------------------------------------------------------------------ 7: don't worry - it's slowing, a tiny bit
def scene_slowing(c, t):
    space_bg(c, t, "#080b29", "#17195a")
    sun(c, -60, 380, 150, t, 0.95, 0.7)
    cx, cy, r = 540, 700, 280
    lon0 = 60 - 14.0 * (t - 41.0)
    ga = smooth(seg(t, EV["worry"] - 0.2, EV["worry"] + 0.4))
    spin_arrow(c, cx, cy, r * 1.42, r * 0.24, 0.6 + 0.4 * ga, mixhex("#a8e6ff", "#5cf2c8", ga), t, False)
    planet(c, cx, cy, r, lon0=lon0, tilt=0, t=t)
    spin_arrow(c, cx, cy, r * 1.42, r * 0.24, 0.6 + 0.4 * ga, mixhex("#a8e6ff", "#5cf2c8", ga), t, True)
    ap = pop(t, EV["slowing"], 0.45) * (1 - smooth(seg(t, T[14] - 0.6, T[14] - 0.35)))
    if ap > 0.01:
        cx0, cy0, cw, ch = 150, 1060, 780, 230
        c.save(); c.translate(540, cy0 + ch / 2); c.scale(ap, ap); c.translate(-540, -(cy0 + ch / 2))
        card(c, cx0, cy0, cw, ch, 0.94)
        text(c, "EACH DAY GETS LONGER BY", 540, cy0 + 50, 26, "#9fb3ff", tf=TF_POP_SB, track=3)
        na = smooth(seg(t, EV["two"] - 0.1, EV["two"] + 0.3))
        text(c, "+0.002 seconds", 540, cy0 + 132, 62, "#ffd84d", na, tf=TF_POP_XB)
        ca = smooth(seg(t, EV["century"] - 0.2, EV["century"] + 0.2))
        text(c, "every 100 years", 540, cy0 + 196, 36, "#e8ecff", ca, tf=TF_POP_SB)
        c.restore()


SCENE_FN = {
    "sky_open": scene_sky_open, "globe_speed": scene_globe_speed, "winds": scene_winds, "bulge": scene_bulge,
    "newworld": scene_newworld, "dayyear": scene_dayyear, "slowing": scene_slowing, "sky_end": scene_sky_end,
}
