"""Episode 004 - What if Earth had rings like Saturn? One function per scene window in timeline.SCENES."""
import math, random
from lib import *
from kit import *
from timeline import T, E, EV, LINES, Wd, DURATION, SCENES

SEND = {n: b for n, a, b in SCENES}


def leave(t, name):
    """cards and badges leave before the transition out of their scene"""
    b = SEND[name]
    return 1 - smooth(seg(t, b - 0.85, b - 0.5))


# the ring arch as seen from the lake landscape (sky coordinates, before the terrain's own offset)
ARCH = dict(cx=540, cy=1040, rx=720, ry=800, w=150)
ELEV = 14.0                         # viewing elevation for the ancient globe; ring ry_k must match
RYK = math.sin(math.radians(ELEV))


def arch_layer(t, a, grow=1.0, shine=0.0, day=0.0, sun_ph=None, glow_k=1.0):
    def fn(c):
        if day > 0:  # daytime sky: blue gradient over the night sky, the stars vanish
            c.drawRect(skia.Rect.MakeXYWH(0, -400, W, H + 400), P(shader=lin(0, -200, 0, 1100, [hx("#2c63c9", day), hx("#5a9de8", day), hx("#a9d4ff", day)], [0, 0.6, 1])))
        if sun_ph is not None and 0 < sun_ph < 1:
            sx = lerp(-120, W + 120, sun_ph)
            sy = 980 - 430 * math.sin(math.pi * sun_ph)
            sun(c, sx, sy, 70, t, 1.0, 0.6)
        ring_arch(c, t, ARCH["cx"], ARCH["cy"], ARCH["rx"], ARCH["ry"], ARCH["w"], a, grow, shine, glow_k=glow_k)
    return fn


def lake_glints(a):
    def fn(c, lake_top):
        if a <= 0:
            return
        for k in range(7):
            yy = lake_top + 12 + k * 20
            for x0 in (110, 960):
                wv = 90 - k * 8
                c.drawRoundRect(skia.Rect.MakeXYWH(x0 - wv / 2 + 8 * math.sin(k * 1.7), yy, wv, 5), 2.5, 2.5,
                                P(hx("#ffe9c0", 0.32 * a * (1 - k / 8))))
    return fn


# ------------------------------------------------------------------------------------------------ 1 open
def scene_open(c, t):
    g = ease_io(seg(t, EV["rings"] - 0.15, EV["rings"] + 0.85))
    shine = smooth(seg(t, EV["glowing"] - 0.1, EV["glowing"] + 0.6))
    cam = 130 * ease_io(seg(t, EV["bridge"], EV["across"] + 0.9))
    landscape(c, t, moon_s=0.0, m=0.7, cam_y=cam, sky_fn=arch_layer(t, 1.0, g, shine),
              lake_fn=lake_glints(g * (0.6 + 0.4 * shine)))


# ------------------------------------------------------------------------------------------------ 2 rocks
ROCKS = []
_r = random.Random(12)
for layer, (n, s0, s1, sp, al) in enumerate([(16, 16, 26, 40, 0.6), (12, 36, 62, 75, 0.88), (6, 105, 160, 120, 1.0)]):
    for k in range(n):
        # stratified so every part of the frame gets some rocks and big ones never clump
        y = lerp(300, 1270, (k + _r.uniform(0.2, 0.8)) / n)
        x = (k * 0.618 % 1) * (W + 400) - 200 + (k % 2) * 90
        ROCKS.append(dict(x=x, y=y, s=_r.uniform(s0, s1), sp=sp * _r.uniform(0.85, 1.15),
                          rot=_r.uniform(0, 360), vr=_r.uniform(-14, 14), seed=_r.randint(1, 9999), a=al, layer=layer))


def saturn_icon(c, x, y, s, a=1.0, earth=False):
    planet_ring(c, x, y, s, -18, False, a, rin=1.35, rout=2.0, ry_k=0.28, shadow=False)
    if earth:
        planet(c, x, y, s, 20, tilt=-18, atmo=0.0, clouds=False)
    else:
        c.drawCircle(x, y, s, P(shader=lin(x, y - s, x, y + s, [hx("#f3d79a"), hx("#d9a65c")])))
        c.save(); c.clipPath(circ_path(x, y, s), doAntiAlias=True); c.rotate(-18, x, y)
        for k in (-0.45, 0.1, 0.5):
            c.drawRect(skia.Rect.MakeXYWH(x - s, y + k * s, 2 * s, s * 0.16), P(hx("#c98f4a", 0.6)))
        c.drawCircle(x + s * 0.4, y + s * 0.35, s * 1.0, P(hx("#7a4a2a", 0.25)))
        c.restore()
    planet_ring(c, x, y, s, -18, True, a, rin=1.35, rout=2.0, ry_k=0.28, shadow=False)


def scene_rocks(c, t):
    space_bg(c, t, "#070923", "#191c58")
    sun(c, -40, 140, 170, t, 1.0, 0.7)
    # the ring plane: a faint band of tiny particles running across the frame
    c.save(); c.translate(540, 780); c.rotate(-8)
    c.drawRect(skia.Rect.MakeXYWH(-900, -380, 1800, 760), P(shader=lin(0, -380, 0, 380, [hx("#e8d9b8", 0), hx("#e8d9b8", 0.07), hx("#e8d9b8", 0)])))
    c.restore()
    ice = 1 - smooth(seg(t, EV["rock"] - 0.3, EV["rock"] + 0.35))
    shine = smooth(seg(t, EV["shining"] - 0.1, EV["shining"] + 0.5))
    for R in ROCKS:
        x = (R["x"] + t * R["sp"]) % (W + 400) - 200
        y = R["y"] + 14 * math.sin(t * 0.5 + R["seed"])
        haze = R["a"] * (0.9 if R["layer"] < 2 else 1.0)
        ring_chunk(c, x, y, R["s"], R["rot"] + t * R["vr"], R["seed"], ice, haze, shine)
        if R["layer"] == 0:  # distant ones melt into the dark a little
            c.drawCircle(x, y, R["s"] * 1.05, P(hx("#191c58", 0.35)))
    # label pill: SATURN: ICE  ->  EARTH: ROCK
    p1 = pop(t, EV["saturn2"] + 0.05, 0.4) * (1 - smooth(seg(t, EV["ours"] - 0.15, EV["ours"] + 0.1)))
    p2 = pop(t, EV["ours"] + 0.1, 0.4) * leave(t, "rocks")
    for p, label, earth in ((p1, "SATURN: ICE", False), (p2, "EARTH: ROCK", True)):
        if p <= 0.01:
            continue
        c.save(); c.translate(540, 210); c.scale(p, p); c.translate(-540, -210)
        pill(c, 540, 210, label, min(1, p), 46, icon=lambda cc, ix, iy, e=earth: saturn_icon(cc, ix, iy, 20, 1.0, e), icon_w=70)
        c.restore()


# ------------------------------------------------------------------------------------------------ 3 day & night
def scene_daynight(c, t):
    c1 = seg(t, EV["never"] - 0.15, EV["set"] + 0.55)
    c2 = seg(t, EV["day"] - 0.45, EV["night"] + 0.35)
    day = max(math.sin(math.pi * c1) ** 0.7 if 0 < c1 < 1 else 0, math.sin(math.pi * c2) ** 0.7 if 0 < c2 < 1 else 0)
    sun_ph = c1 if 0 < c1 < 1 else (c2 if 0 < c2 < 1 else None)
    pulse = 0.5 * math.sin(math.pi * seg(t, EV["there"] - 0.1, EV["there"] + 0.6))
    landscape(c, t, moon_s=0.0, m=lerp(0.7, 1.0, day), cam_y=130, sky_fn=arch_layer(t, 1.0, 1.0, 1.0 + pulse - day, day * 0.92, sun_ph, 1.0 - day),
              lake_fn=lake_glints(1.0))
    if day > 0:  # daylight wash over the land
        c.drawRect(skia.Rect.MakeWH(W, H), P(hx("#3a5ea8", 0.22 * day), mode=skia.BlendMode.kPlus))


# ------------------------------------------------------------------------------------------------ 4 views from the ground
VSTARS = Stars(260, seed=19)


def location_pin(c, x, y, s, a=1.0):
    if a <= 0:
        return
    c.save(); c.translate(x, y)
    c.drawOval(skia.Rect.MakeXYWH(-s * 0.5, -s * 0.15, s, s * 0.3), P(hx("#000018", 0.35 * a)))
    pth = skia.Path()
    pth.moveTo(0, 0)
    pth.cubicTo(-s * 0.35, -s * 0.8, -s * 0.75, -s * 1.15, -s * 0.75, -s * 1.6)
    pth.cubicTo(-s * 0.75, -s * 2.05, -s * 0.4, -s * 2.38, 0, -s * 2.38)
    pth.cubicTo(s * 0.4, -s * 2.38, s * 0.75, -s * 2.05, s * 0.75, -s * 1.6)
    pth.cubicTo(s * 0.75, -s * 1.15, s * 0.35, -s * 0.8, 0, 0)
    c.drawPath(pth, P(hx("#ff6b5a", a)))
    c.save(); c.clipPath(pth, doAntiAlias=True)
    c.drawCircle(s * 0.5, -s * 1.5, s * 0.9, P(hx("#d9473a", a)))
    c.restore()
    c.drawCircle(0, -s * 1.6, s * 0.3, P(hx("#ffffff", a)))
    c.restore()


def scene_views(c, t):
    c.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, 1300, [hx("#0a0c2c"), hx("#1c2366"), hx("#3d3590")], [0, 0.55, 1])))
    VSTARS.draw(c, t, 0.9)
    k = ease_io(seg(t, EV["north"] - 0.05, EV["arch"] + 0.15))
    line_on = smooth(seg(t, EV["equator"] - 0.1, EV["equator"] + 0.5))
    shine = smooth(seg(t, EV["overhead"] - 0.1, EV["overhead"] + 0.5)) * (1 - k) + smooth(seg(t, EV["rainbow"] - 0.1, EV["rainbow"] + 0.5))
    hor = 1150
    lcx = lerp(780, 540, ease_io(k))
    rx = lerp(9, 490, k ** 1.3)
    ry = lerp(2300, 790, k)
    w = lerp(14, 100, k ** 1.1)
    if line_on > 0:
        if k < 0.35:  # edge-on: soft glow so the thin line reads as light
            gl = (1 - k / 0.35) * line_on
            c.drawRect(skia.Rect.MakeXYWH(lcx - 40, -50, 80, hor + 50), P(shader=lin(lcx - 40, 0, lcx + 40, 0, [hx("#ffe2a8", 0), hx("#ffe2a8", 0.30 * gl * (1 + shine)), hx("#ffe2a8", 0)]), mode=skia.BlendMode.kPlus))
        grow = ease_out(seg(t, EV["equator"] - 0.1, EV["equator"] + 0.7))
        ring_arch(c, t, lcx, hor, rx, ry, w, line_on, 1.0 if k > 0 else 0.5 + 0.5 * grow, shine * 0.8, sparkles=0.4 + 0.6 * k)
    # ground: hills + pines with rim light
    rim = "#a596ff"
    hill(c, hor - 40, [(50, 0.006, 0.4), (24, 0.016, 1.9)], "#272366", rim, 0.4)
    hill(c, hor + 70, [(40, 0.0045, 2.2), (18, 0.013, 0.3)], "#1d1a55", rim, 0.45)
    for (px, s_) in [(120, 120), (210, 90), (860, 100), (950, 140)]:
        pine(c, px, hor + 92 + 18 * math.sin(px * 0.0045 + 2.2), s_, "#141148", rim, 0.5)
    hill(c, hor + 230, [(30, 0.005, 1.0), (12, 0.03, 0.5)], "#0f0d35", rim, 0.35)
    c.drawRect(skia.Rect.MakeXYWH(0, hor + 300, W, H), P(hx("#0b0a2a")))
    # globe: big in the middle at first, then it shrinks into a corner card
    gk = ease_io(seg(t, EV["equator"] - 0.45, EV["equator"] + 0.15))
    gx, gy, gr = lerp(540, 205, gk), lerp(700, 345, gk), lerp(210, 82, gk)
    ga = smooth(seg(t, T[4] - 0.5, T[4] - 0.1))
    if gk > 0.01:
        cw, ch = 2 * 1.95 * 0.9 * gr + 44, 2 * gr + 104
        card(c, gx - cw / 2, gy - gr - 72, cw, ch, gk)
    ring_s = lerp(1.0, 0.9, gk)
    planet_ring(c, gx, gy, gr, 0, False, ga, rin=1.3 * ring_s, rout=1.95 * ring_s, ry_k=0.22, shadow=False)
    planet(c, gx, gy, gr, -60 + t * 4, 0.0, t=t, atmo=ga)
    planet_ring(c, gx, gy, gr, 0, True, ga, rin=1.3 * ring_s, rout=1.95 * ring_s, ry_k=0.22, shadow=False)
    lat = lerp(28, 0, ease_io(seg(t, EV["equator"] - 0.2, EV["equator"] + 0.4)))
    lat = lerp(lat, 48, ease_io(seg(t, EV["north"] - 0.1, EV["north"] + 0.5)))
    py = gy - gr * math.sin(math.radians(lat))
    bounce = 10 * abs(math.sin(math.pi * seg(t, EV["live"] - 0.05, EV["live"] + 0.45)))
    ps = lerp(30, 17, gk) * pop(t, EV["where"] + 0.1, 0.45)
    location_pin(c, gx, py - bounce, ps, ga)
    # labels
    p1 = pop(t, EV["equator"], 0.4) * (1 - smooth(seg(t, EV["north"] - 0.25, EV["north"] - 0.05)))
    p2 = pop(t, EV["north"] + 0.05, 0.4) * leave(t, "views")
    for p, lab in ((p1, "AT THE EQUATOR"), (p2, "FARTHER NORTH")):
        if p > 0.01:
            c.save(); c.translate(540, 680); c.scale(p, p); c.translate(-540, -680)
            pill(c, 540 - 70 * (lab == "AT THE EQUATOR"), 680, lab, min(1, p), 38)
            c.restore()


# ------------------------------------------------------------------------------------------------ 5 shadow
SCENES_END_SHADOW = T[10] - 0.10
SH = dict(cx=560, cy=790, r=235, tilt=23.0, rin=1.32, rout=1.95, ryk=0.2)


def scene_shadow(c, t):
    space_bg(c, t, "#070923", "#1a1d5a")
    cx, cy, r, tl = SH["cx"], SH["cy"], SH["r"], SH["tilt"]
    sun(c, -70, 640, 175, t, 1.0, 0.8)
    st = math.sin(math.radians(tl))
    ytop, ybot = cy - SH["rout"] * r * st - 28, cy - SH["rin"] * r * st + 28
    planet_ring(c, cx, cy, r, tl, False, 1.0, t, SH["rin"], SH["rout"], SH["ryk"])
    planet(c, cx, cy, r, 30 + t * 6, tilt=tl, t=t, light=(-1.0, -0.05))
    # the ring's shadow on the winter hemisphere (sweeps in from the sunward side)
    sp = ease_io(seg(t, EV["shadows"] - 0.1, EV["fall"] + 0.3))
    deep = smooth(seg(t, EV["darker"] - 0.1, EV["darker"] + 0.6))
    if sp > 0:
        c.save(); c.clipPath(circ_path(cx, cy, r), doAntiAlias=True)
        c.clipRect(skia.Rect.MakeLTRB(cx - r - 10, 0, cx - r - 10 + (2 * r + 20) * sp, H))
        c.drawRect(skia.Rect.MakeLTRB(cx - r - 20, ytop, cx + r + 20, ybot), P(hx("#050720", 0.62 + 0.18 * deep), blur=7))
        hgt = ybot - ytop
        c.drawRect(skia.Rect.MakeLTRB(cx - r - 20, ytop + 0.26 * hgt, cx + r + 20, ytop + 0.32 * hgt), P(hx("#2a3a8a", 0.35), blur=3))
        c.restore()
        la = sp * (1 - smooth(seg(t, SCENES_END_SHADOW - 0.5, SCENES_END_SHADOW - 0.2)))
        ly_ = (ytop + ybot) / 2
        la *= smooth(seg(t, EV["fall"], EV["fall"] + 0.4))
        text(c, "RING SHADOW", cx + 20, ly_ + 12, 34, "#ffd84d", la, TF_POP_XB, shadow=1, track=2)
    planet_ring(c, cx, cy, r, tl, True, 1.0, t, SH["rin"], SH["rout"], SH["ryk"])
    # labels
    pw = pop(t, EV["winter"] + 0.05, 0.45) * leave(t, "shadow")
    if pw > 0.01:
        c.save(); c.translate(560, 300); c.scale(pw, pw); c.translate(-560, -300)
        pill(c, 560, 300, "NORTHERN WINTER", min(1, pw), 40, icon=lambda cc, ix, iy: snowflake(cc, ix, iy, 22, "#bfe8ff", 1.0, t * 20), icon_w=56)
        c.restore()
    tp = pop(t, EV["colder"] - 0.25, 0.4) * leave(t, "shadow")
    if tp > 0.01:
        v = lerp(0.3, -0.85, ease_io(seg(t, EV["colder"], EV["darker"] + 0.4)))
        c.save(); c.translate(170, 1100); c.scale(tp, tp); c.translate(-170, -1100)
        thermometer(c, 170, 990, 170, v, min(1, tp))
        c.restore()


# ------------------------------------------------------------------------------------------------ 6 ancient (hero)
AN = dict(cx=540, cy=840, r=245, rin=1.38, rout=2.08)
THETA_B = -32.0   # where the asteroid breaks up, as an angle on the ring ellipse


def ring_point(cx, cy, rr, ang, ryk):
    a = math.radians(ang)
    return cx + rr * math.cos(a), cy + rr * ryk * math.sin(a)


def asteroid_path(u):
    """asteroid position along its incoming curve, u 0..1 (1 = break-up point on the ring)"""
    bx, by = ring_point(AN["cx"], AN["cy"], AN["r"] * 1.75, THETA_B, RYK)
    sx, sy = 1010, 170
    cx_, cy_ = 1000, 520
    x = (1 - u) ** 2 * sx + 2 * (1 - u) * u * cx_ + u * u * bx
    y = (1 - u) ** 2 * sy + 2 * (1 - u) * u * cy_ + u * u * by
    return x, y


def debris(c, t, cx, cy, r, g, a, seed=4):
    """chunks scattered along the freshly formed ring, flying apart from the break-up point"""
    rnd = random.Random(seed)
    for k in range(30):
        side = 1 if k % 2 else -1
        d = rnd.uniform(0.15, 1.0)
        ang = THETA_B + side * 210 * g * d
        rr = r * rnd.uniform(AN["rin"], AN["rout"])
        x, y = ring_point(cx, cy, rr, ang, RYK)
        front = math.sin(math.radians(ang)) > 0
        yield (x, y, rnd.uniform(4, 11) * (1 - 0.4 * g), rnd.randint(1, 999), front, a * (1 - 0.6 * g * d))


def scene_ancient(c, t):
    space_bg(c, t, "#060820", "#15174d")
    cx, cy, r = AN["cx"], AN["cy"], AN["r"]
    lon0 = 22 + (t - 32.0) * 3
    g = ease_out(seg(t, EV["ring"] - 0.05, EV["ring"] + 1.7))
    span = (THETA_B - 180 * g, THETA_B + 180 * g) if g < 0.999 else (0, 360)
    ra = smooth(seg(t, EV["ring"] - 0.1, EV["ring"] + 0.4))
    parts = list(debris(c, t, cx, cy, r, g, ra * (1 - smooth(seg(t, EV["ring"] + 1.3, EV["ring"] + 2.2)))))
    for (x, y, s, sd, front, al) in parts:
        if not front:
            ring_chunk(c, x, y, s, sd + t * 40, sd, 0.0, al)
    planet_ring(c, cx, cy, r, 0, False, ra, t, AN["rin"], AN["rout"], RYK, span=span, thin=0.35 + 0.65 * g)
    ancient_earth(c, cx, cy, r, lon0, t, ELEV)
    planet_ring(c, cx, cy, r, 0, True, ra, t, AN["rin"], AN["rout"], RYK, span=span, thin=0.35 + 0.65 * g)
    for (x, y, s, sd, front, al) in parts:
        if front:
            ring_chunk(c, x, y, s, sd + t * 40, sd, 0.0, al)
    # the incoming asteroid: streaks in on "wild", cracks on "really", shatters on "ring"
    u = ease_in(seg(t, EV["wild"] - 0.3, EV["ring"])) * 0.85 + 0.15 * seg(t, EV["wild"] - 0.3, EV["ring"])
    ap = smooth(seg(t, EV["wild"] - 0.3, EV["wild"] + 0.1))
    if 0 < u and t < EV["ring"] + 0.05:
        x, y = asteroid_path(u)
        tx, ty = asteroid_path(max(0, u - 0.12))
        c.drawLine(tx, ty, x, y, P(shader=lin(tx, ty, x, y, [hx("#cfc6ff", 0), hx("#cfc6ff", 0.35)]), stroke=26, blur=8))
        crack = seg(t, EV["really"], EV["ring"])
        if crack <= 0:
            ring_chunk(c, x, y, 52 * (0.4 + 0.6 * ap), t * 60, 77, 0.0, ap, 1.0)
        else:  # breaking into pieces that drift apart
            for j, (dx, dy) in enumerate([(-1, -0.6), (1, -0.3), (0.2, 1), (-0.8, 0.7)]):
                ring_chunk(c, x + dx * 34 * crack, y + dy * 30 * crack, 27, t * 80 + j * 50, 80 + j, 0.0, 1.0, 1.0)
            glow(c, x, y, 30, "#ffd59a", 0.6 * crack, 2.2)
    bx, by = asteroid_path(1.0)
    burst(c, bx, by, 60, seg(t, EV["ring"], EV["ring"] + 0.8), "#ffe7b8", 12, 3)
    # age card
    p = pop(t, EV["four"], 0.45) * leave(t, "ancient")
    if p > 0.01:
        c.save(); c.translate(540, 290); c.scale(p, p); c.translate(-540, -290)
        card(c, 230, 190, 620, 200, min(1, p))
        text(c, "466 MILLION", 540, 290, 72, "#ffd84d", min(1, p), TF_POP_XB, shadow=1)
        text(c, "YEARS AGO", 540, 350, 42, "#ffffff", min(1, p), TF_POP_SB, shadow=1, track=3)
        c.restore()


# ------------------------------------------------------------------------------------------------ 7 craters
def ghost_ring(c, t, cx, cy, r, front, a):
    """the long-gone ring, drawn as a soft dashed outline (imagined, not there today)"""
    if a <= 0:
        return
    for k, rr in enumerate((CR["rin"], CR["rout"])):
        R = rr * r
        rect = skia.Rect.MakeXYWH(cx - R, cy - R * RYK, 2 * R, 2 * R * RYK)
        arc = skia.Path(); arc.addArc(rect, 0 if front else 180, 180)
        c.drawPath(arc, P(hx("#ffe2a8", 0.18 * a), stroke=18, blur=8, mode=skia.BlendMode.kPlus))
        dashed(c, arc, P(hx("#ffe9c4", 0.85 * a), stroke=5), 22, 14, t * 30 * (1 if k else -1))



CR = dict(cx=540, cy=820, r=300, rin=1.3, rout=1.72)


def scene_craters(c, t):
    space_bg(c, t, "#060820", "#15174d")
    cx, cy, r = CR["cx"], CR["cy"], CR["r"]
    lon0 = 26 + (t - 40.0) * 1.0
    ring_a = smooth(seg(t, EV["rocks"] - 0.4, EV["rocks"] + 0.3)) * (1 - 0.6 * smooth(seg(t, EV["millions"] - 0.1, EV["millions"] + 1.2)))
    ghost_ring(c, t, cx, cy, r, False, ring_a)
    ancient_earth(c, cx, cy, r, lon0, t, ELEV, light=(-0.45, -0.55))
    # the band within 30 degrees of the ancient equator
    bp = smooth(seg(t, EV["near"] - 0.2, EV["near"] + 0.4))
    glow_b = smooth(seg(t, EV["ancient"], EV["ancient"] + 0.4)) * (1 - 0.5 * smooth(seg(t, EV["rocks"], EV["rocks"] + 1)))
    if bp > 0:
        c.save(); c.translate(cx, cy); c.clipPath(circ_path(0, 0, r), doAntiAlias=True)
        band = lat_band_path(r, -30, 30, lon0, ELEV)
        if band is not None:
            c.drawPath(band, P(hx("#ffd84d", (0.10 + 0.10 * glow_b) * bp), mode=skia.BlendMode.kPlus))
        for la in (-30, 30):
            arc = lat_arc(r, la, lon0, ELEV)
            if arc:
                dashed(c, path_from(arc, False), P(hx("#ffd84d", 0.9 * bp), stroke=5), 18, 12, t * 20)
        eq = lat_arc(r, 0, lon0, ELEV)
        if eq:
            c.drawPath(path_from(eq, False), P(hx("#fff2b0", 0.45 * bp), stroke=3))
        c.restore()
    # craters pop one by one from "twenty" to just after "craters"
    t0, t1 = EV["twenty"] + 0.1, EV["craters"] + 0.9
    order = sorted(range(len(ANCIENT_CRATERS)), key=lambda i: ANCIENT_CRATERS[i][0])
    shown = 0
    for n, i in enumerate(order):
        lo, la = ANCIENT_CRATERS[i]
        x, y, z = ll_xy(r, lo, la, lon0, ELEV)
        tp = lerp(t0, t1, n / (len(order) - 1))
        p = pop(t, tp, 0.3)
        if t >= tp:
            shown += 1
        if z > 0.05 and p > 0:
            crater_mark(c, cx + x, cy + y, r * 0.03 * p, max(0.3, z), min(1, p), 1.0 - 0.5 * smooth(seg(t, EV["rocks"], EV["rocks"] + 1)))
            burst(c, cx + x, cy + y, 16, seg(t, tp, tp + 0.5), "#ffe2a8", 6, i)
    ghost_ring(c, t, cx, cy, r, True, ring_a)
    # rocks raining down from the ring into the band
    rp = seg(t, EV["rocks"] - 0.1, E[14] + 0.3)
    if 0 < rp < 1:
        rnd = random.Random(8)
        for k in range(16):
            st = rnd.uniform(0, 0.75)
            u = seg(rp, st, st + 0.22)
            if u <= 0 or u >= 1:
                continue
            lo, la = rnd.uniform(lon0 - 60, lon0 + 60), rnd.uniform(-26, 26)
            ex, ey, ez = ll_xy(r, lo, la, lon0, ELEV)
            ang = rnd.uniform(-160, -20)
            rr = r * rnd.uniform(1.45, 1.8)
            sx, sy = ring_point(cx, cy, rr, ang, RYK)
            e = ease_in(u)
            x, y = lerp(sx, cx + ex, e), lerp(sy, cy + ey, e)
            tx, ty = lerp(sx, cx + ex, max(0, e - 0.25)), lerp(sy, cy + ey, max(0, e - 0.25))
            c.drawLine(tx, ty, x, y, P(shader=lin(tx, ty, x, y, [hx("#ffb46b", 0), hx("#ffcf8a", 0.9)]), stroke=5, mode=skia.BlendMode.kPlus))
            glow(c, x, y, 9, "#ffd59a", 0.9, 2.2)
            if u > 0.92:
                burst(c, x, y, 12, (u - 0.92) / 0.08, "#ffe2a8", 6, k)
    # counter
    pc = pop(t, EV["twenty"], 0.4) * leave(t, "craters")
    if pc > 0.01:
        c.save(); c.translate(540, 250); c.scale(pc, pc); c.translate(-540, -250)
        pill(c, 540, 250, f"{max(1, shown)} CRATERS", min(1, pc), 46)
        c.restore()
    pa = pop(t, EV["ancient"] - 0.1, 0.4)
    if pa > 0.01 and bp > 0:
        lab_y = cy - r - 34
        text(c, "ANCIENT EQUATOR", 540, lab_y, 34, "#ffd84d", min(1, pa) * (1 - smooth(seg(t, EV["rocks"] - 0.3, EV["rocks"]))), TF_POP_XB, shadow=1, track=2)


# ------------------------------------------------------------------------------------------------ 8 ice age
IC = dict(cx=560, cy=780, r=255, rin=1.34, rout=1.95)


def scene_iceage(c, t):
    space_bg(c, t, "#060820", "#15174d")
    cx, cy, r = IC["cx"], IC["cy"], IC["r"]
    sun(c, -90, 520, 160, t, 1.0, 0.7)
    lon0 = 30 + (t - 48.0) * 3
    ice = ease_io(seg(t, EV["ice"] - 0.3, EV["ice"] + 1.4))
    planet_ring(c, cx, cy, r, 0, False, 1.0, t, IC["rin"], IC["rout"], RYK, thin=0.5)
    ancient_earth(c, cx, cy, r, lon0, t, ELEV, ice, light=(-0.9, -0.3))
    sp = ease_io(seg(t, EV["shadow2"] - 0.1, EV["shadow2"] + 0.8))
    if sp > 0:  # ring shadow band across the low latitudes of one hemisphere
        c.save(); c.translate(cx, cy); c.clipPath(circ_path(0, 0, r), doAntiAlias=True)
        c.clipRect(skia.Rect.MakeLTRB(-r - 10, -r - 10, -r - 10 + (2 * r + 20) * sp, r + 10))
        b = lat_band_path(r, 8, 30, lon0, ELEV)
        if b is not None:
            c.drawPath(b, P(hx("#060824", 0.5), blur=10))
        c.restore()
    planet_ring(c, cx, cy, r, 0, True, 1.0, t, IC["rin"], IC["rout"], RYK, thin=0.5)
    pi_ = pop(t, EV["ice"] - 0.05, 0.45) * leave(t, "iceage")
    if pi_ > 0.01:
        c.save(); c.translate(540, 280); c.scale(pi_, pi_); c.translate(-540, -280)
        pill(c, 540, 280, "ICE AGE", min(1, pi_), 52, icon=lambda cc, ix, iy: snowflake(cc, ix, iy, 26, "#bfe8ff", 1.0, t * 20), icon_w=62)
        c.restore()
    # gentle snowfall in front once the ice age begins
    if ice > 0:
        rnd = random.Random(3)
        for k in range(26):
            x0, sp_ = rnd.uniform(0, W), rnd.uniform(40, 90)
            y = (rnd.uniform(0, 1400) + t * sp_) % 1400 + 120
            x = x0 + 20 * math.sin(t + k)
            snowflake(c, x, y, rnd.uniform(5, 9), "#e6f6ff", 0.55 * ice, t * 30 + k * 20)


# ------------------------------------------------------------------------------------------------ 9 end
def scene_end(c, t):
    look = ease_io(seg(t, EV["look"] - 0.1, EV["look"] + 0.9))
    back = ease_io(seg(t, E[16] + 0.15, DURATION - 0.35))
    cam = 130 * look * (1 - back)
    shine = smooth(seg(t, EV["picture"] - 0.1, EV["picture"] + 0.5)) * (1 - back)
    fade = 1 - back
    landscape(c, t, moon_s=0.0, m=0.7, cam_y=cam, sky_fn=arch_layer(t, fade, 1.0, shine), lake_fn=lake_glints(fade))


SCENE_FN = {"open": scene_open, "rocks": scene_rocks, "daynight": scene_daynight, "views": scene_views,
            "shadow": scene_shadow, "ancient": scene_ancient, "craters": scene_craters, "iceage": scene_iceage,
            "end": scene_end}
