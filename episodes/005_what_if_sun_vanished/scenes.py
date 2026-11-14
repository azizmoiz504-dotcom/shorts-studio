"""Episode 005 - What if the Sun vanished right now? One function per scene window in timeline.SCENES."""
import math, random
from lib import *
from kit import *
from timeline import T, E, EV, LINES, Wd, DURATION, SCENES, NFRAMES, FPS

SEND = {n: b for n, a, b in SCENES}
TEND = (NFRAMES - 1) / FPS
ADD = skia.BlendMode.kPlus

# shared SPACE layout (open / race / back)
SX, SY, SR = 300, 650, 200           # the Sun
ORB = 640                            # Earth's orbit radius around the Sun
ER = 104                              # Earth radius


def leave(t, name, lead=0.85):
    """cards and badges leave before the transition out of their scene"""
    b = SEND[name]
    return 1 - smooth(seg(t, b - lead, b - lead + 0.35))


def earth_pos(th):
    a = math.radians(th)
    return SX + ORB * math.cos(a), SY + ORB * math.sin(a)


def light_dir(x, y):
    dx, dy = SX - x, SY - y
    d = math.hypot(dx, dy)
    return (dx / d * 0.88, dy / d * 0.88)


def orbit_line(c, a=1.0, cx=SX, cy=SY, rr=ORB, phase=0.0):
    if a <= 0:
        return
    dashed(c, circ_path(cx, cy, rr), P(hx("#c2b6ff", 0.38 * a), stroke=4), 22, 18, phase)


def clock_icon(c, x, y, s, t, spin=0.0):
    c.drawCircle(x, y, s, P(hx("#ffd84d")))
    c.drawCircle(x, y, s * 0.78, P(hx("#1a1f55")))
    for k in range(4):
        an = k * math.pi / 2
        c.drawLine(x + math.cos(an) * s * 0.6, y + math.sin(an) * s * 0.6, x + math.cos(an) * s * 0.7, y + math.sin(an) * s * 0.7, P(hx("#ffd84d"), stroke=3))
    a1 = -math.pi / 2 + spin
    c.drawLine(x, y, x + math.cos(a1) * s * 0.55, y + math.sin(a1) * s * 0.55, P(hx("#ffffff"), stroke=4))
    c.drawLine(x, y, x + s * 0.30 * 0.71, y - s * 0.30 * 0.71, P(hx("#ffd84d"), stroke=5))
    c.drawCircle(x, y, s * 0.12, P(hx("#ffffff")))


def popped(c, x, y, p, fn):
    """scale-pop a drawing around (x, y)"""
    if p <= 0.01:
        return
    c.save(); c.translate(x, y); c.scale(p, p); c.translate(-x, -y)
    fn(min(1.0, p))
    c.restore()


def dark_earth(c, x, y, r, lon0, t, dark, light):
    """Earth, fading to an unlit ball lit only by a faint starlight rim"""
    planet(c, x, y, r, lon0=lon0, tilt=23.4, t=t, light=light, atmo=1.0 - 0.85 * dark)
    if dark > 0:
        c.drawCircle(x, y, r + 0.5, P(hx("#0a0d33", 0.72 * dark)))
        c.drawCircle(x, y, r + 0.5, P(hx("#2a2f7a", 0.25 * dark), mode=skia.BlendMode.kColor))
        arc = skia.Path(); arc.addArc(skia.Rect.MakeXYWH(x - r + 2, y - r + 2, 2 * r - 4, 2 * r - 4), 180, 110)
        c.drawPath(arc, P(hx("#a596ff", 0.55 * dark), stroke=3))


def space_layout(c, t, sun_s, ghost, th, lon0, earth_dark=0.0, zoom=1.0):
    space_bg(c, t, "#070923", "#191c58")
    ex, ey = earth_pos(th)
    if zoom != 1.0:
        c.save(); c.translate(ex, ey); c.scale(zoom, zoom); c.translate(-ex, -ey)
    orbit_line(c, 1.0, phase=-t * 6)
    ghost_circle(c, SX, SY, SR, ghost, phase=t * 30)
    if sun_s > 0.005:
        sun(c, SX, SY, SR * sun_s, t, min(1.0, sun_s * 1.5), 0.9)
    dark_earth(c, ex, ey, ER, lon0, t, earth_dark, light_dir(ex, ey))
    return ex, ey


# ------------------------------------------------------------------------------------------------ 1 open
def th_open(t):
    return 30 + 1.0 * t


def scene_open(c, t):
    v = EV["vanished"]
    if t < v:
        s = 1.0 + 0.08 * ease_out(seg(t, EV["sun"] - 0.25, v))
    else:
        s = 1.08 * (1 - ease_in_back(seg(t, v, v + 0.34), 1.4))
    ghost = smooth(seg(t, v + 0.25, v + 0.7)) * 0.9
    space_layout(c, t, max(0, s), ghost, th_open(t), -t * 12)
    if t > v:
        burst(c, SX, SY, SR, seg(t, v + 0.26, v + 1.05), "#fff3c4", 12, 3)


# ------------------------------------------------------------------------------------------------ 2 + 4 daytime landscape
DAY_SUN = (300, 520, 78)
DMOON = (720, 470, 66)


def day_sky(t, day, sun_a, moon_a, moon_lit):
    def fn(c):
        if day > 0:
            c.drawRect(skia.Rect.MakeXYWH(0, -400, W, H + 400), P(shader=lin(0, -200, 0, 1100, [hx("#2c63c9", day), hx("#5a9de8", day), hx("#a9d4ff", day)], [0, 0.6, 1])))
        sx, sy, sr = DAY_SUN
        if sun_a > 0.005:
            sun(c, sx, sy, sr * (0.9 + 0.1 * sun_a), t, sun_a, 0.7)
        mx, my, mr = DMOON
        if moon_a > 0:
            if moon_lit > 0.01:
                c.saveLayerAlpha(None, int(255 * clamp(moon_a * (0.55 + 0.45 * (1 - day)) * moon_lit)))
                moon(c, mx, my, mr, 1.0, glow_a=(1 - day) * 0.8)
                c.restore()
            if moon_lit < 0.99:  # unlit moon: a dark disc with a faint outline
                d = (1 - moon_lit) * moon_a
                c.drawCircle(mx, my, mr, P(hx("#0d1036", 0.92 * d)))
                ghost_circle(c, mx, my, mr, 0.75 * d, phase=t * 30)
    return fn


def scene_day(c, t):
    c.clipRect(skia.Rect.MakeWH(W, H))  # keep the tall sky layers inside this scene during slides
    pulse = 0.5 * math.sin(math.pi * seg(t, EV["know"] - 0.1, EV["know"] + 0.8))
    landscape(c, t, moon_s=0.0, m=1.0, cam_y=40, sky_fn=day_sky(t, 1.0, 1.0, 1.0, 1.0))
    c.drawRect(skia.Rect.MakeWH(W, H), P(hx("#3a5ea8", 0.22), mode=ADD))
    if pulse > 0:
        sx, sy, sr = DAY_SUN
        glow(c, sx, sy - 40, sr * 1.3, "#ffe7a0", 0.5 * pulse, 2.2)
    p = pop(t, EV["eight"], 0.45) * leave(t, "day", 0.7)
    spin = 2 * math.pi * 3 * ease_io(seg(t, EV["eight"], SEND["day"]))
    popped(c, 540, 230, p, lambda a: pill(c, 540, 230, "8 MIN 20 S", a, 50,
           icon=lambda cc, ix, iy: clock_icon(cc, ix, iy, 30, t, spin), icon_w=72))


def scene_out(c, t):
    c.clipRect(skia.Rect.MakeWH(W, H))  # keep the tall sky layers inside this scene during slides
    o = EV["out"]
    day = 1 - smooth(seg(t, o - 0.02, o + 0.55))
    sun_a = 1 - smooth(seg(t, o - 0.05, o + 0.25))
    moon_lit = 1 - smooth(seg(t, EV["dark"] - 0.05, EV["dark"] + 0.6))
    m = lerp(1.0, 0.35, smooth(seg(t, o, o + 0.6))) * (1 - smooth(seg(t, EV["dark"] - 0.05, EV["dark"] + 0.6)))
    cam_z = 1.0 + 0.04 * ease_io(seg(t, o - 0.2, o + 1.6))
    landscape(c, t, moon_s=0.0, m=m, cam_y=40, cam_z=cam_z,
              sky_fn=day_sky(t, day, sun_a, 1.0, moon_lit))
    if day > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P(hx("#3a5ea8", 0.22 * day), mode=ADD))
    # the sunlight that was still arriving shuts off: a soft darkening sweep
    p = pop(t, EV["borrowed"] - 0.1, 0.45) * leave(t, "out", 0.75)
    popped(c, 540, 230, p, lambda a: pill(c, 540, 230, "MOONLIGHT = SUNLIGHT", a, 42,
           icon=lambda cc, ix, iy: moon(cc, ix, iy, 22, 1.0, 0.0), icon_w=56))


# ------------------------------------------------------------------------------------------------ 3 race
def th_race(t):
    return 26 + 2.2 * (t - SEND["day"])


FRONT_T0, FRONT_T1 = EV["light"] - 0.25, SEND["race"] - 0.1


def front_r(t):
    """radius of the trailing edge of the last sunlight (constant speed, like light)"""
    return lerp(SR, ORB, seg(t, FRONT_T0, FRONT_T1))


def scene_race(c, t):
    th = th_race(t)
    ex, ey = earth_pos(th)
    space_bg(c, t, "#070923", "#191c58")
    R = front_r(t)
    on = smooth(seg(t, FRONT_T0 - 0.2, FRONT_T0 + 0.3))
    # sunlight still streaming outward beyond the front (warm haze), darkness inside it
    big = skia.Path(); big.addRect(skia.Rect.MakeXYWH(-200, -200, W + 400, H + 400))
    outside = skia.Op(big, circ_path(SX, SY, R), skia.PathOp.kDifference_PathOp)
    c.save(); c.clipPath(outside, doAntiAlias=True)
    c.drawCircle(SX, SY, 1500, P(shader=rad(SX, SY, 1500, [hx("#ff9a2a", 0.30), hx("#ff8a1a", 0.16), hx("#ff7a10", 0.06), hx("#ff7a10", 0)], [0, 0.35, 0.7, 1]), mode=ADD))
    # photons racing outward
    racing = smooth(seg(t, EV["racing"] - 0.3, EV["racing"] + 0.3))
    if racing > 0:
        rnd = random.Random(4)
        for k in range(46):
            an = rnd.uniform(-1.35, 1.45)
            sp = 260
            d = (rnd.uniform(0, 900) + t * sp) % 900 + R + 10
            L = 46
            x0, y0 = SX + math.cos(an) * d, SY + math.sin(an) * d
            x1, y1 = SX + math.cos(an) * (d + L), SY + math.sin(an) * (d + L)
            c.drawLine(x0, y0, x1, y1, P(shader=lin(x0, y0, x1, y1, [hx("#ffe6a0", 0), hx("#ffe6a0", 0.55 * racing)]), stroke=4, mode=ADD))
    c.restore()
    # the front itself: the very last light
    c.drawCircle(SX, SY, R, P(hx("#ffcf6b", 0.30 * on), stroke=34, blur=16, mode=ADD))
    c.drawCircle(SX, SY, R, P(hx("#ffe9b0", 0.85 * on), stroke=5, mode=ADD))
    # gravity ripple rides with the light
    g = smooth(seg(t, EV["gravity"] - 0.15, EV["gravity"] + 0.4))
    if g > 0:
        for k, off in enumerate((16, 40)):
            pts = []
            for i in range(180):
                an = i / 180 * 2 * math.pi
                rr = R - off + 5 * math.sin(an * 28 - t * 8 + k)
                pts.append((SX + rr * math.cos(an), SY + rr * math.sin(an)))
            c.drawPath(path_from(pts, True), P(hx("#b49cff", (0.75 - 0.3 * k) * g), stroke=4))
    nothing = 0.5 * math.sin(math.pi * seg(t, EV["nothing"] - 0.1, EV["nothing"] + 0.8))
    orbit_line(c, 1.0, phase=-t * 6)
    ghost_circle(c, SX, SY, SR, 0.9 + nothing * 0.2, phase=t * 30)
    if nothing > 0:
        c.drawCircle(SX, SY, SR * (1 + 0.15 * nothing), P(hx("#cfc6ff", 0.6 * nothing), stroke=4))
    # Earth keeps going around... nothing
    ca = smooth(seg(t, EV["circling"] - 0.3, EV["circling"] + 0.2)) * leave(t, "race", 0.6)
    arc_arrow(c, SX, SY, ORB, th + 9, th + 34, ease_out(seg(t, EV["circling"] - 0.3, EV["circling"] + 0.5)), "#ffd84d", ca, 8)
    dark_earth(c, ex, ey, ER, -t * 12 - 40, t, 0.0, light_dir(ex, ey))
    # countdown
    rem = 500 * (1 - seg(t, FRONT_T0, FRONT_T1))
    label = f"{int(rem // 60)}:{int(rem % 60):02d}"
    ka = smooth(seg(t, SEND["day"] + 0.3, SEND["day"] + 0.7)) * leave(t, "race", 0.45)
    if ka > 0:
        pill(c, 760, 230, "  " + label + " ", ka, 54, icon=lambda cc, ix, iy: clock_icon(cc, ix, iy, 30, t, rem / 500 * 2 * math.pi * 4), icon_w=72)
    gp = pop(t, EV["gravity"] + 0.05, 0.45) * leave(t, "race", 0.6)
    popped(c, 300, 1130, gp, lambda a: pill(c, 300, 1130, "GRAVITY TOO", a, 40, col="#2a1f6e"))


# ------------------------------------------------------------------------------------------------ 5 drift
DGX, DGY, DGR, DORB = 360, 1220, 110, 600


def scene_drift(c, t):
    space_bg(c, t, "#060820", "#14174a", 1.0)
    s0 = EV["sails"]
    ghost_circle(c, DGX, DGY, DGR, 0.8, phase=t * 30)
    dashed(c, circ_path(DGX, DGY, DORB), P(hx("#c2b6ff", 0.32), stroke=4), 22, 18, -t * 6)
    th0 = -100.0
    a0 = math.radians(th0)
    px, py = DGX + DORB * math.cos(a0), DGY + DORB * math.sin(a0)
    ux, uy = -math.sin(a0), math.cos(a0)
    v = DORB * math.radians(26)          # same speed on the curve and on the line
    if t < s0:
        th = th0 - 26 * (s0 - t)
        a = math.radians(th)
        ex, ey = DGX + DORB * math.cos(a), DGY + DORB * math.sin(a)
    else:
        d = v * (t - s0)
        ex, ey = px + ux * d, py + uy * d
    # the straight path ahead
    la = smooth(seg(t, s0 - 0.3, s0 + 0.3))
    st = smooth(seg(t, EV["straight"] - 0.1, EV["straight"] + 0.4))
    if la > 0:
        L = 1100
        qx, qy = px + ux * L, py + uy * L
        if st > 0:
            c.drawLine(px, py, qx, qy, P(hx("#ffd84d", 0.22 * st), stroke=24, blur=10))
        dashed(c, path_from([(px, py), (qx, qy)], False), P(hx(mixhex("#ffffff", "#ffd84d", st), 0.85 * la), stroke=6), 26, 18, -t * 40)
        for k in range(3):
            ph = ((t * 0.6) + k / 3) % 1
            dd = 200 + ph * 760
            arrow_chev(c, px + ux * dd, py + uy * dd, 28, math.degrees(math.atan2(uy, ux)), "#ffd84d", la * math.sin(ph * math.pi) * (0.5 + 0.5 * st))
    # faint trail behind Earth
    if t > s0:
        c.drawLine(px, py, ex, ey, P(shader=lin(px, py, ex, ey, [hx("#c2b6ff", 0), hx("#c2b6ff", 0.35)]), stroke=26, blur=6))
    dark_earth(c, ex, ey, 140, -t * 12, t, 1.0, (-0.8, -0.4))


# ------------------------------------------------------------------------------------------------ 6 freeze
SNOW = [(random.Random(k).uniform(0, W), random.Random(k + 99).uniform(0, H), random.Random(k + 7).uniform(9, 17)) for k in range(34)]


def ice_lake(ice):
    def fn(c, top):
        if ice <= 0:
            return
        c.drawRect(skia.Rect.MakeXYWH(0, top, W, 260), P(shader=lin(0, top, 0, top + 200, [hx("#cde8ff", 0.85 * ice), hx("#8fb8e8", 0.75 * ice)])))
        c.drawRect(skia.Rect.MakeXYWH(0, top, W, 6), P(hx("#ffffff", 0.6 * ice)))
        rnd = random.Random(3)
        for k in range(7):
            x = rnd.uniform(60, 1020); y = top + rnd.uniform(30, 190)
            pts = [(x, y)]
            for j in range(4):
                x += rnd.uniform(25, 60) * (1 if k % 2 else -1); y += rnd.uniform(-14, 14)
                pts.append((x, y))
            c.drawPath(path_from(pts, False), P(hx("#ffffff", 0.55 * ice), stroke=2.5))
    return fn


def scene_freeze(c, t):
    c.clipRect(skia.Rect.MakeWH(W, H))  # keep the tall sky layers inside this scene during slides
    wk = smooth(seg(t, EV["week"] - 0.1, EV["week"] + 1.2))
    yr = smooth(seg(t, EV["year"] - 0.1, EV["year"] + 1.4))
    ice = 0.75 * wk + 0.25 * yr
    landscape(c, t, moon_s=0.0, m=0.0, cam_y=20, lake_fn=ice_lake(ice), show_boat=True)
    # frost wash over the land and frost creeping in from the edges
    c.drawRect(skia.Rect.MakeWH(W, H), P(hx("#9ec9ff", 0.05 + 0.07 * ice), mode=ADD))
    fr = 0.5 * wk + 0.5 * yr
    for (fx, fy) in ((0, 0), (W, 0), (0, H), (W, H)):
        c.drawCircle(fx, fy, 520, P(shader=rad(fx, fy, 520, [hx("#dff0ff", 0.38 * fr), hx("#dff0ff", 0.10 * fr), hx("#dff0ff", 0)], [0, 0.45, 1])))
    # snow
    sa = smooth(seg(t, EV["week"], EV["week"] + 0.8)) * (0.6 + 0.4 * yr)
    if sa > 0:
        for k, (x0, y0, s) in enumerate(SNOW[: int(18 + 16 * yr)]):
            y = (y0 + t * (60 + s * 4)) % (H + 60) - 30
            x = x0 + 26 * math.sin(t * 0.8 + k)
            snowflake(c, x, y, s * 0.55, "#e8f4ff", 0.75 * sa, t * 30 + k * 20)
    # thermometer: comfortable -> below freezing -> deep cold
    v = lerp(0.25, -0.45, wk)
    v = lerp(v, -1.0, yr)
    ta = smooth(seg(t, SEND["drift"] - 0.1, SEND["drift"] + 0.4)) * leave(t, "freeze", 0.6)
    if ta > 0:
        thermometer(c, 120, 400, 360, v, ta)
    p1 = pop(t, EV["week"] + 0.05, 0.45) * (1 - smooth(seg(t, EV["year"] - 0.25, EV["year"] - 0.05)))
    p2 = pop(t, EV["year"] + 0.05, 0.45) * leave(t, "freeze", 0.6)
    popped(c, 580, 230, p1, lambda a: pill(c, 580, 230, "1 WEEK: BELOW 0°C", a, 44, col="#173a7a",
           icon=lambda cc, ix, iy: snowflake(cc, ix, iy, 20, "#bfe8ff"), icon_w=58))
    popped(c, 580, 230, p2, lambda a: pill(c, 580, 230, "1 YEAR: BELOW −70°C", a, 44, col="#173a7a",
           icon=lambda cc, ix, iy: snowflake(cc, ix, iy, 20, "#bfe8ff"), icon_w=58))


# ------------------------------------------------------------------------------------------------ 7 ocean
SURF = 440
OSTARS = Stars(160, seed=23, region=(0, 0, W, SURF - 30))


def scene_ocean(c, t):
    fz = ease_io(seg(t, EV["freeze"] - 0.1, EV["top"] + 0.3))
    thick = 26 + 64 * fz + 18 * smooth(seg(t, EV["top"], EV["lid"] + 0.4))
    # night sky
    c.drawRect(skia.Rect.MakeWH(W, SURF + 20), P(shader=lin(0, 0, 0, SURF, [hx("#070923"), hx("#1a1f5e")])))
    OSTARS.draw(c, t, 0.9)
    # water
    wpts = [(x, SURF + 6 * math.sin(x * 0.012 + t * 1.4) * (1 - fz)) for x in range(-20, W + 40, 16)]
    water = path_from(wpts + [(W + 40, H + 300), (-20, H + 300)], True)
    c.drawPath(water, P(shader=lin(0, SURF, 0, 1320, [hx("#164a9c"), hx("#0f3478"), hx("#0a2254"), hx("#071538")], [0, 0.3, 0.7, 1])))
    # currents: liquid water keeps flowing below the ice
    cur = 0.4 * smooth(seg(t, SEND["freeze"] - 0.4, SEND["freeze"] + 0.4)) + 0.6 * smooth(seg(t, EV["deep"] - 0.5, EV["deep"] + 0.4))
    if cur > 0:
        for k in range(5):
            y0 = SURF + 230 + k * 110
            dirn = 1 if k % 2 == 0 else -1
            pts = [(x, y0 + 22 * math.sin(x * 0.007 + k * 1.3)) for x in range(-40, W + 60, 20)]
            pth = path_from(pts, False, 1.0)
            c.drawPath(pth, P(hx("#4fa8ff", 0.10 * cur), stroke=26, blur=10))
            dashed(c, pth, P(hx("#8fd0ff", 0.42 * cur), stroke=6), 150, 110, -t * 120 * dirn)
            for j in range(3):
                ph = (t * 0.25 * dirn + j / 3 + k * 0.17) % 1
                x = ph * (W + 100) - 50
                y = y0 + 22 * math.sin(x * 0.007 + k * 1.3)
                slope = math.degrees(math.atan(22 * 0.007 * math.cos(x * 0.007 + k * 1.3)))
                arrow_chev(c, x, y, 20, slope + (0 if dirn > 0 else 180), "#bfe6ff", 0.7 * cur * math.sin(ph * math.pi))
    # gentle drifting specks for depth (small, matte)
    rnd = random.Random(8)
    for k in range(26):
        x = (rnd.uniform(0, W) + t * rnd.uniform(-12, 12)) % W
        y = rnd.uniform(SURF + thick + 40, 1240) + 8 * math.sin(t + k)
        c.drawCircle(x, y, rnd.uniform(1.5, 2.6), P(hx("#9cc8ff", 0.22)))
    # seabed
    bed = [(x, 1240 + 22 * math.sin(x * 0.008 + 0.7) + 10 * math.sin(x * 0.027)) for x in range(-20, W + 40, 20)]
    c.drawPath(path_from(bed + [(W + 40, H + 300), (-20, H + 300)], True), P(shader=lin(0, 1220, 0, 1700, [hx("#2a2470"), hx("#16134a"), hx("#0b0a2c")])))
    c.drawPath(path_from(bed, False), P(hx("#5b55c4", 0.5), stroke=4))
    for (rx, rw, rh) in [(150, 120, 46), (420, 80, 30), (820, 140, 52), (990, 70, 28)]:
        ry = 1240 + 22 * math.sin(rx * 0.008 + 0.7) + 10 * math.sin(rx * 0.027) + 8
        rp = skia.Path(); rp.addOval(skia.Rect.MakeXYWH(rx - rw, ry - rh, 2 * rw, 2 * rh))
        c.drawPath(rp, P(hx("#352d86")))
        c.save(); c.clipPath(rp, doAntiAlias=True)
        c.drawOval(skia.Rect.MakeXYWH(rx - rw * 1.1, ry - rh * 1.2, rw * 1.5, rh * 1.1), P(hx("#4a40a8", 0.8)))
        c.restore()
    # a warm glow in a seabed crack hints at what is below
    hint = smooth(seg(t, EV["centuries"] - 0.3, EV["centuries"] + 0.6))
    if hint > 0:
        glow(c, 540, 1258, 26, "#ff8a3a", 0.8 * hint, 2.8)
        c.drawPath(path_from([(500, 1250), (525, 1262), (548, 1252), (575, 1264)], False), P(hx("#ffb36b", hint), stroke=5))
    # ice lid: a thin film that thickens everywhere at once
    if fz > 0:
        top = SURF - 8
        th_ = 8 + (thick - 8) * fz
        bot = [(x, SURF + th_ * (0.88 + 0.08 * math.sin(x * 0.013 + 0.6) + 0.05 * math.sin(x * 0.041))) for x in range(-40, W + 60, 20)]
        ip = path_from([(-40, top)] + bot + [(W + 60, top)], True, 0.8)
        c.drawPath(ip, P(shader=lin(0, top, 0, SURF + th_, [hx("#eef8ff"), hx("#b4dcf7"), hx("#78b2e2")], [0, 0.4, 1])))
        c.drawLine(-20, top + 2, W + 20, top + 2, P(hx("#ffffff", 0.9), stroke=5))
        c.save(); c.clipPath(ip, doAntiAlias=True)
        rnd2 = random.Random(5)
        for k in range(8):
            x = rnd2.uniform(40, 1040)
            c.drawPath(path_from([(x, top + 6), (x + rnd2.uniform(-18, 18), top + th_ * 0.5), (x + rnd2.uniform(-22, 22), top + th_ * 0.9)], False), P(hx("#ffffff", 0.4), stroke=2.5))
        gl = seg(t, EV["lid"] - 0.1, EV["lid"] + 1.0)
        if 0 < gl < 1:
            gx = lerp(-200, W + 200, ease_io(gl))
            band = path_from([(gx - 40, top), (gx + 30, top), (gx - 20, top + 140), (gx - 90, top + 140)], True)
            c.drawPath(band, P(hx("#ffffff", 0.55 * math.sin(gl * math.pi)), blur=10, mode=ADD))
        c.restore()
    pi_ = pop(t, EV["top"] - 0.05, 0.45) * leave(t, "ocean", 0.75)
    popped(c, 840, SURF - 80, pi_, lambda a: pill(c, 840, SURF - 80, "ICE", a, 42, col="#173a7a"))
    pl = pop(t, EV["liquid"], 0.45) * leave(t, "ocean", 0.75)
    popped(c, 540, 900, pl, lambda a: pill(c, 540, 900, "STILL LIQUID", a, 46, col="#123a8a"))
    pc = pop(t, EV["centuries"], 0.45) * leave(t, "ocean", 0.75)
    popped(c, 540, 1020, pc, lambda a: pill(c, 540, 1020, "FOR CENTURIES", a, 40, col="#1a1f55", txt="#ffd84d"))


# ------------------------------------------------------------------------------------------------ 8 under
def microbe(c, x, y, s, kind, col, shade, t, k):
    c.save(); c.translate(x, y); c.rotate(25 * math.sin(t * 1.6 + k) + k * 40)
    wob = 1 + 0.05 * math.sin(t * 4 + k)
    if kind == "rod":
        body = skia.Path(); body.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-s * wob, -s * 0.38, 2 * s * wob, s * 0.76), s * 0.38, s * 0.38))
        # little tail (flagellum)
        tail = [(s * wob + j * s * 0.22, s * 0.12 * math.sin(j * 1.4 - t * 9 + k)) for j in range(7)]
        c.drawPath(path_from(tail, False, 1.0), P(hx(shade), stroke=max(2, s * 0.09)))
    else:
        body = circ_path(0, 0, s * 0.62 * wob)
    c.drawPath(body, P(hx(col)))
    c.save(); c.clipPath(body, doAntiAlias=True)
    c.drawCircle(s * 0.35, s * 0.45, s * 0.9, P(hx(shade)))
    c.restore()
    c.drawPath(body, P(hx("#ffffff", 0.35), stroke=2))
    for j in range(3):
        c.drawCircle(-s * 0.35 + j * s * 0.32, -s * 0.06 + (j % 2) * s * 0.12, s * 0.09, P(hx(shade)))
    c.restore()


ROCK_LAYERS = [(-120, "#3d3488"), (180, "#382e7a"), (420, "#32296c"), (640, "#2c235e"), (850, "#3a2450"), (1040, "#4a2a48")]
MICROBES = [(-130, -70, "rod", "#5fd38a", "#2e9a62"), (70, -125, "ball", "#ff8fc0", "#c95a8a"), (140, 40, "rod", "#ffc94a", "#d89a1e"),
            (-60, 95, "ball", "#7fd6ff", "#3a8fc2"), (-165, 45, "ball", "#ffc94a", "#d89a1e"), (35, 160, "rod", "#ff8fc0", "#c95a8a"),
            (170, -50, "ball", "#5fd38a", "#2e9a62"), (-20, -20, "rod", "#7fd6ff", "#3a8fc2")]
PORES = [(300, 1010, 46), (820, 900, 34), (160, 760, 30), (930, 1120, 30), (620, 1160, 26)]


def magma_y(x, t):
    return 1225 + 20 * math.sin(x * 0.006 + 0.8) + 6 * math.sin(x * 0.02 - t * 0.8)


def scene_under(c, t):
    sink = ease_io(seg(t, SEND["ocean"] - 0.4, SEND["under"])) * 70
    heat = 0.75 + 0.25 * smooth(seg(t, EV["heat"] - 0.3, EV["heat"] + 0.5))
    c.save(); c.translate(0, -sink)
    for k, (y, col) in enumerate(ROCK_LAYERS):
        pts = [(x, y + 18 * math.sin(x * 0.006 + k * 1.9) + 8 * math.sin(x * 0.02 + k)) for x in range(-20, W + 40, 20)]
        lay = path_from(pts + [(W + 40, H + 400), (-20, H + 400)], True)
        c.drawPath(lay, P(hx(col)))
        c.drawPath(path_from(pts, False), P(hx("#7a6ad8", 0.30), stroke=3))
        rnd = random.Random(k + 3)
        for j in range(8):  # embedded pebbles: lit top, shaded bottom
            px_, py_ = rnd.uniform(30, 1050), y + rnd.uniform(50, 170)
            w_, h_ = rnd.uniform(26, 54), rnd.uniform(16, 26)
            c.drawOval(skia.Rect.MakeXYWH(px_, py_, w_, h_), P(hx("#000018", 0.20)))
            c.drawOval(skia.Rect.MakeXYWH(px_ + 2, py_ + 1, w_ - 6, h_ * 0.55), P(hx("#8f80e0", 0.12)))
    # hot rock glowing at the bottom: Earth's own heat (a real light source)
    mpts = [(x, magma_y(x, t)) for x in range(-20, W + 40, 20)]
    mag = path_from(mpts + [(W + 40, H + 400), (-20, H + 400)], True)
    c.drawPath(mag, P(shader=lin(0, 1200, 0, 1500, [hx("#ff8a2a"), hx("#e8541a"), hx("#9a2a1a")])))
    c.drawPath(path_from(mpts, False), P(hx("#ffd08a", 0.9), stroke=5))
    c.restore()
    c.drawRect(skia.Rect.MakeXYWH(0, 700, W, 1220), P(shader=lin(0, 700, 0, 1250, [hx("#ff6a1a", 0), hx("#ff7a2a", 0.30 * heat)]), mode=ADD))
    for k in range(8):  # heat shimmer rising
        ph = (t * 0.4 + k / 8) % 1
        x0 = 70 + k * 135
        y0 = 1180 - sink - ph * 460
        pts = [(x0 + 12 * math.sin(j * 0.9 + t * 3 + k), y0 - j * 16) for j in range(8)]
        c.drawPath(path_from(pts, False, 1.0), P(hx("#ffb36b", 0.45 * heat * math.sin(ph * math.pi)), stroke=5, mode=ADD))
    # little water-filled cracks where microbes live
    for (px, py, pr) in PORES:
        py -= sink
        c.drawOval(skia.Rect.MakeXYWH(px - pr, py - pr * 0.55, 2 * pr, 1.1 * pr), P(hx("#140c30")))
        c.drawOval(skia.Rect.MakeXYWH(px - pr * 0.8, py - pr * 0.1, 1.6 * pr, 0.6 * pr), P(hx("#ff7a2a", 0.18 * heat)))
    lp = pop(t, EV["microbes"] - 0.15, 0.5) * leave(t, "under", 0.7)
    if lp > 0.01:
        px, py = PORES[0][0], PORES[0][1] - sink
        lx, ly, lr = 600, 640, 290
        a = min(1, lp)
        c.drawLine(px + 36, py - 30, lx - lr * 0.72, ly + lr * 0.69, P(hx("#c2b6ff", 0.8 * a), stroke=5))
        c.drawCircle(px, py, 58, P(hx("#c2b6ff", 0.8 * a), stroke=5))
        c.save(); c.translate(lx, ly); c.scale(lp, lp)
        lens = circ_path(0, 0, lr)
        c.drawCircle(0, 12, lr + 8, P(hx("#03051a", 0.45), blur=18))
        c.save(); c.clipPath(lens, doAntiAlias=True)
        c.drawCircle(0, 0, lr, P(shader=rad(0, lr * 0.9, lr * 1.7, [hx("#4a2440"), hx("#2a1840"), hx("#1a1236")])))
        rnd = random.Random(2)
        for j in range(14):  # rock grains framing the water pocket (flat two-tone)
            an = j / 14 * 2 * math.pi + rnd.uniform(-0.15, 0.15); d = lr * rnd.uniform(0.95, 1.08)
            gx_, gy_, gr = math.cos(an) * d, math.sin(an) * d, rnd.uniform(55, 80)
            col = rnd.choice(["#4a3a7a", "#3e3170", "#55448a"])
            gp = circ_path(gx_, gy_, gr)
            c.drawPath(gp, P(hx(col)))
            c.save(); c.clipPath(gp, doAntiAlias=True)
            c.drawCircle(gx_ + gr * 0.35, gy_ + gr * 0.4, gr, P(hx("#000018", 0.25)))
            c.restore()
        c.drawRect(skia.Rect.MakeXYWH(-lr, lr * 0.1, 2 * lr, lr), P(shader=lin(0, lr * 0.1, 0, lr, [hx("#ff7a2a", 0), hx("#ff7a2a", 0.22 * heat)]), mode=ADD))
        for k, (mx, my, kind, col, shade) in enumerate(MICROBES):
            mp = pop(t, EV["microbes"] + 0.05 + k * 0.07, 0.4)
            if mp > 0.01:
                c.save(); c.translate(mx + 8 * math.sin(t * 0.9 + k), my + 6 * math.cos(t * 1.1 + k)); c.scale(mp, mp)
                microbe(c, 0, 0, 52 if kind == "rod" else 54, kind, col, shade, t, k)
                c.restore()
        c.restore()
        c.drawCircle(0, 0, lr, P(hx("#c2b6ff", a), stroke=10))
        c.drawCircle(0, 0, lr - 9, P(hx("#ffffff", 0.18 * a), stroke=3))
        c.restore()
    sp = pop(t, EV["survive"], 0.45) * leave(t, "under", 0.7)
    popped(c, 600, 1065, sp, lambda a: pill(c, 600, 1065, "STILL ALIVE", a, 44, col="#1d5a3a"))


# ------------------------------------------------------------------------------------------------ 9 back
def night_side(c, ex, ey, r, a, dawn):
    """shadow over the half of Earth facing away from the Sun, with a warm dawn line on its edge"""
    if a <= 0:
        return
    ld = light_dir(ex, ey)
    ang = math.degrees(math.atan2(ld[1], ld[0]))
    disc = circ_path(ex, ey, r)
    c.save(); c.clipPath(disc, doAntiAlias=True)
    c.translate(ex, ey); c.rotate(ang)
    c.drawRect(skia.Rect.MakeXYWH(-r * 1.3, -r * 1.2, r * 1.32, r * 2.4), P(hx("#0a0d33", 0.76 * a), blur=r * 0.06))
    c.drawRect(skia.Rect.MakeXYWH(-r * 0.05, -r * 1.2, r * 0.14, r * 2.4), P(hx("#ffb04a", 0.6 * a * dawn), blur=r * 0.09))
    c.restore()


def scene_back(c, t):
    g = EV["good"]
    s = ease_out_back(seg(t, g - 0.05, g + 0.55), 1.6)
    ghost = 0.9 * (1 - smooth(seg(t, g - 0.1, g + 0.3)))
    th = 30 + 1.0 * (t - TEND)
    ex, ey = earth_pos(th)
    # look closer at Earth for the sunrise, then back out to the exact starting view
    zin = ease_io(seg(t, EV["tomorrow"] - 0.4, EV["sunrise"] + 0.1))
    zout = ease_io(seg(t, EV["light2"] - 0.6, EV["light2"] + 0.4))
    k = zin * (1 - zout)
    z = 1.0 + 0.75 * k
    spin = 90 * ease_io(seg(t, EV["tomorrow"] - 0.2, EV["sunrise"] + 0.8))
    space_bg(c, t, "#070923", "#191c58")
    c.save()
    c.translate(lerp(ex, 640, k), lerp(ey, 860, k)); c.scale(z, z); c.translate(-ex, -ey)
    orbit_line(c, 1.0, phase=-t * 6)
    ghost_circle(c, SX, SY, SR, ghost, phase=t * 30)
    if s > 0.005:
        sun(c, SX, SY, SR * s, t, min(1.0, s * 1.5), 0.9)
    dark_earth(c, ex, ey, ER, -t * 12 + spin, t, 0.0, light_dir(ex, ey))
    night_side(c, ex, ey, ER, k, smooth(seg(t, EV["sunrise"] - 0.6, EV["sunrise"] + 0.2)))
    c.restore()
    if t > g + 0.1:  # fade the burst in over a few frames so it never pops in a single frame
        c.saveLayerAlpha(None, int(255 * smooth(seg(t, g + 0.1, g + 0.3))))
        burst(c, SX, SY, SR, seg(t, g + 0.1, g + 0.95), "#fff3c4", 12, 5)
        c.restore()
    # one pulse of light leaves the Sun and reaches Earth
    lp = seg(t, EV["light2"] + 0.3, EV["old"] + 0.7)
    if 0 < lp < 1:
        R = lerp(SR * 1.05, ORB - ER * 0.95, ease_io(lp))
        fa = math.sin(math.pi * lp) ** 0.5
        ang = math.degrees(math.atan2(ey - SY, ex - SX))
        for k2, (dr, al) in enumerate([(0, 1.0), (-30, 0.45), (-60, 0.2)]):
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeXYWH(SX - R - dr, SY - R - dr, 2 * (R + dr), 2 * (R + dr)), ang - 13, 26)
            c.drawPath(arc, P(hx("#ffcf6b", 0.40 * fa * al), stroke=44, blur=14, mode=ADD))
            c.drawPath(arc, P(hx("#fff2c2", 0.95 * fa * al), stroke=9 - 3 * k2, mode=ADD))
    la = smooth(seg(t, EV["eight2"] - 0.3, EV["eight2"] + 0.1)) * (1 - smooth(seg(t, EV["old"] + 0.5, EV["old"] + 0.9)))
    if la > 0:
        pill(c, 800, 500, "8 MIN 20 S", la, 40, icon=lambda cc, ix, iy: clock_icon(cc, ix, iy, 24, t, 0), icon_w=58)
    bp = pop(t, EV["five"], 0.45) * (1 - smooth(seg(t, EV["tomorrow"] - 0.5, EV["tomorrow"] - 0.2)))
    popped(c, 540, 230, bp, lambda a: pill(c, 540, 230, "5 BILLION YEARS LEFT", a, 44, txt="#ffd84d"))


SCENE_FN = {"open": scene_open, "day": scene_day, "race": scene_race, "out": scene_out, "drift": scene_drift,
            "freeze": scene_freeze, "ocean": scene_ocean, "under": scene_under, "back": scene_back}
