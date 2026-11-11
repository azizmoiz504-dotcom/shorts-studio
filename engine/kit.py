"""Reusable drawing kit: backgrounds, landscapes, planets helpers, reef life, characters, props.
Nothing in here depends on an episode timeline."""
import math, random
from lib import *


"""Every scene of the Short. Each scene function draws a full frame for time t."""


STARS = Stars(300, seed=7)


MILKY = Stars(700, seed=31)


STARS_SPACE = Stars(340, seed=11)


MOON_X, MOON_Y, MOON_R = 720, 520, 150


BAND = Stars(520, seed=21, region=(-200, 0, W + 200, H))


NEB = [(180, 380, 560, "#6b3fd6", 0.20), (900, 620, 480, "#c2409e", 0.12), (760, 1500, 700, "#1f8fd0", 0.16),
       (120, 1250, 520, "#3d2fb0", 0.16), (560, 900, 900, "#2a1f7a", 0.18)]


def space_bg(c, t, top="#090c2b", bot="#1c1f5e", star_a=1.0, dx=0, dy=0, hue=None):
    c.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, [hx(top), hx(bot)])))
    for (x, y, r, col, a) in NEB:
        col = hue.get(col, col) if hue else col
        xx, yy = x + dx * 0.15 + 20 * math.sin(t * 0.15 + x), y + dy * 0.15
        c.drawCircle(xx, yy, r, P(shader=rad(xx, yy, r, [hx(col, a), hx(col, a * 0.45), hx(col, 0)], [0, 0.5, 1])))
    # milky band: soft gradient strip (no hard edges) + stars that thin out away from its centre line
    c.save()
    c.translate(W / 2, H / 2); c.rotate(-48)
    c.drawRect(skia.Rect.MakeXYWH(-1600, -260, 3200, 520), P(shader=lin(0, -260, 0, 260, [hx("#9d8cff", 0), hx("#9d8cff", 0.07), hx("#c7b8ff", 0.09), hx("#9d8cff", 0.07), hx("#9d8cff", 0)], [0, 0.3, 0.5, 0.7, 1])))
    c.restore()
    ang = math.radians(-48)
    nx_, ny_ = -math.sin(ang), math.cos(ang)
    for (x, y, sz, ph, f, col, big) in BAND.s:
        d = abs((x - W / 2) * nx_ + (y - H / 2) * ny_)
        if d > 260:
            continue
        fa = (1 - d / 260) ** 1.5
        tw = 0.65 + 0.35 * math.sin(t * f * 2.4 + ph)
        c.drawCircle(x + dx * 0.25, y + dy * 0.25, sz * 0.4, P(hx(col, 0.5 * star_a * fa * tw)))
    STARS_SPACE.draw(c, t, star_a, dx, dy)


def dust(c, t, a=1.0, seed=2, col="#c9c2ff"):
    """large soft out-of-focus motes drifting in front - gives depth"""
    rnd = random.Random(seed)
    for k in range(9):
        x0, y0 = rnd.uniform(0, W), rnd.uniform(0, H)
        sp = rnd.uniform(8, 22)
        x = (x0 + t * sp) % (W + 200) - 100
        y = y0 + 30 * math.sin(t * 0.3 + k)
        r = rnd.uniform(6, 16)
        c.drawCircle(x, y, r, P(hx(col, 0.10 * a), blur=r * 0.8))


def burst(c, x, y, r, p, col="#ffffff", n=10, seed=1):
    """Sparkle burst; p in 0..1."""
    if p <= 0 or p >= 1:
        return
    rnd = random.Random(seed)
    # ring
    rr = r * (1 + 1.8 * ease_out(p))
    c.drawCircle(x, y, rr, P(hx(col, 0.9 * (1 - p)), stroke=r * 0.08 * (1 - p) + 1))
    glow(c, x, y, r * 1.2, col, 1.4 * (1 - p) ** 2, 2.4)
    for i in range(n):
        ang = i / n * 2 * math.pi + rnd.uniform(-0.2, 0.2)
        d = r * (0.6 + rnd.uniform(1.4, 2.3) * ease_out(p))
        s = r * rnd.uniform(0.06, 0.11) * (1 - p) * (1 + 0.6 * math.sin(p * 9))
        px, py = x + math.cos(ang) * d, y + math.sin(ang) * d
        sparkle(c, px, py, s, col, 1 - p, p * 90)


def sparkle(c, x, y, s, col, a, rot=0):
    if s <= 0 or a <= 0:
        return
    c.save(); c.translate(x, y); c.rotate(rot)
    pth = path_from([(0, -s * 2), (s * 0.4, -s * 0.4), (s * 2, 0), (s * 0.4, s * 0.4), (0, s * 2), (-s * 0.4, s * 0.4), (-s * 2, 0), (-s * 0.4, -s * 0.4)], True)
    c.drawPath(pth, P(hx(col, a)))
    c.restore()


def mountain_range(c, peaks, valley_y, lit, shade, snow, m, snow_h=50):
    """peaks: list of (x, y) tops. Valleys sit between peaks at valley_y (slightly varied)."""
    pts = [(peaks[0][0] - 260, valley_y + 140)]
    vals = []
    for i, (px, py) in enumerate(peaks):
        pts.append((px, py))
        if i + 1 < len(peaks):
            nx, ny = peaks[i + 1]
            vx = px + (nx - px) * (0.5 + 0.08 * math.sin(i * 2.3))
            vy = valley_y + 18 * math.sin(i * 1.7)
            pts.append((vx, vy))
            vals.append((vx, vy))
    pts.append((peaks[-1][0] + 260, valley_y + 140))
    pts += [(peaks[-1][0] + 260, 1500), (peaks[0][0] - 260, 1500)]
    sil = path_from(pts, True)
    c.drawPath(sil, P(hx(lit)))
    c.save()
    c.clipPath(sil, doAntiAlias=True)
    for i, (px, py) in enumerate(peaks):
        # right-hand (away from the moon on the right? light comes from upper right) -> shade the left face
        left_v = vals[i - 1] if i > 0 else (px - 260, valley_y + 140)
        face = path_from([(px, py), left_v, (lerp(left_v[0], px, 0.55), valley_y + 230), (px + (px - left_v[0]) * 0.08, valley_y + 230)], True)
        c.drawPath(face, P(hx(shade)))
        # snow cap: band from the peak down to a jagged snowline
        sl = py + snow_h
        jag = []
        for k in range(9):
            x = px - 130 + k * 32.5
            jag.append((x, sl + (14 if k % 2 else -6) + 6 * math.sin(i * 3 + k)))
        cap = path_from([(px - 140, py - 20), (px + 140, py - 20)] + list(reversed(jag)), True)
        c.drawPath(cap, P(hx(snow)))
        c.save()
        c.clipPath(face, doAntiAlias=True)
        c.drawPath(cap, P(hx(shade, 0.35)))
        c.restore()
    c.restore()
    c.drawPath(path_from(pts[1:-3], False), P(hx("#b9afff", 0.28 * m), stroke=2.5))


def hill(c, base, amps, col, rim=None, rim_a=0.0, xs=(-100, W + 100)):
    pts = []
    for i in range(0, 61):
        x = xs[0] + (xs[1] - xs[0]) * i / 60
        y = base + sum(a * math.sin(x * f + ph) for a, f, ph in amps)
        pts.append((x, y))
    top = list(pts)
    pts += [(xs[1], H + 400), (xs[0], H + 400)]
    c.drawPath(path_from(pts, True), P(hx(col) if isinstance(col, str) else col))
    if rim and rim_a > 0:
        c.drawPath(path_from(top, False), P(hx(rim, rim_a), stroke=5))
    return top


def pine(c, x, y, s, col, rim, rim_a, bend=0.0):
    """bend > 0 leans the tree to the right (wind from the left): higher tiers lean further, the trunk stays planted"""
    for k in range(3):
        w = s * (0.9 - k * 0.22)
        yy = y - k * s * 0.55
        bx = x + bend * s * 0.30 * k * k * 0.5 + bend * s * 0.12 * k     # tier base centre drifts with height
        tx = x + bend * s * (0.35 + 0.42 * k)                             # tier tip leans furthest
        pth = path_from([(bx - w / 2, yy), (tx, yy - s * 0.8), (bx + w / 2, yy)], True)
        c.drawPath(pth, P(hx(col)))
        if rim_a > 0:
            c.drawLine(tx, yy - s * 0.8, bx + w / 2, yy, P(hx(rim, rim_a * 0.8), stroke=3))
    c.drawRect(skia.Rect.MakeXYWH(x - s * 0.06, y, s * 0.12, s * 0.18), P(hx(col)))


def house(c, x, y, t, m, win=1.0, sc=0.92, wind=0.0):
    """cozy log cabin in 3/4 view; (x, y) = ground point under the front-right corner"""
    c.save(); c.translate(x, y); c.scale(sc, sc)
    lit = mixhex("#2a2570", "#3a3290", m)
    side = mixhex("#1c1852", "#262066", m)
    roof_c = mixhex("#2e2878", "#463aa6", m)
    roof_s = mixhex("#221d5c", "#30297c", m)
    rim = hx("#c2b6ff", 0.75 * m)
    # warm light spilling on the ground
    c.drawOval(skia.Rect.MakeXYWH(-120, -8, 170, 40), P(hx("#ffbf5a", 0.20 * win), blur=14))
    # stone foundation (reaches into the slope so the cabin never floats)
    c.drawPath(path_from([(-88, -6), (24, -6), (102, -14), (102, 6), (-88, 8)], True), P(hx(mixhex("#17143f", "#221d55", m))))
    for (sx, sy) in [(-70, 1), (-42, 2), (-14, 1), (40, -3), (74, -6)]:
        c.drawOval(skia.Rect.MakeXYWH(sx - 12, sy - 4, 24, 9), P(hx(mixhex("#221e55", "#2e2870", m))))
    # side wall (receding)
    side_p = path_from([(20, -4), (98, -14), (98, -96), (20, -92)], True)
    c.drawPath(side_p, P(hx(side)))
    # front gable wall
    front_p = path_from([(-82, -4), (20, -4), (20, -92), (-31, -138), (-82, -92)], True)
    c.drawPath(front_p, P(hx(lit)))
    c.save(); c.clipPath(front_p, doAntiAlias=True)
    for k in range(1, 8):  # log lines
        c.drawLine(-90, -4 - k * 13, 30, -4 - k * 13, P(hx("#140f40", 0.35), stroke=2.5))
    c.restore()
    c.save(); c.clipPath(side_p, doAntiAlias=True)
    for k in range(1, 8):
        c.drawLine(18, -4 - k * 13, 100, -14 - k * 12, P(hx("#0e0b33", 0.35), stroke=2.5))
    c.restore()
    # chimney (behind roof edge)
    c.drawRect(skia.Rect.MakeXYWH(58, -176, 22, 56), P(hx(mixhex("#1e1a55", "#2b2472", m))))
    c.drawRect(skia.Rect.MakeXYWH(54, -182, 30, 9), P(hx(mixhex("#262068", "#3a3290", m))))
    # roof: side plane + front fascia
    roof_p = path_from([(-31, -148), (50, -158), (112, -88), (30, -80)], True)
    c.drawPath(roof_p, P(hx(roof_c)))
    c.save(); c.clipPath(roof_p, doAntiAlias=True)
    for k in range(1, 6):
        u = k / 6
        c.drawLine(lerp(-31, 30, u), lerp(-148, -80, u), lerp(50, 112, u), lerp(-158, -88, u), P(hx(roof_s, 0.8), stroke=3))
    c.restore()
    c.drawPath(path_from([(-96, -84), (-31, -150), (32, -80)], False), P(hx(mixhex("#3a3290", "#5b4fc8", m)), stroke=11))
    c.drawPath(path_from([(-96, -84), (-31, -150)], False), P(rim, stroke=3))
    # door with a little lamp
    rrect(c, -72, -64, 30, 60, 8, P(hx("#120e36")))
    c.drawCircle(-47, -34, 2.5, P(hx("#ffcf6b", win)))
    glow(c, -36, -76, 6, "#ffcf6b", 0.9 * win, 3.0)
    c.drawCircle(-36, -76, 4, P(hx("#ffe6a8", win)))
    # front window
    glow(c, -8, -54, 30, "#ffc861", 0.6 * win, 2.2)
    rrect(c, -27, -72, 38, 36, 5, P(hx("#ffd47a", win)))
    c.drawLine(-8, -72, -8, -36, P(hx("#c9852e", win), stroke=3.5))
    c.drawLine(-27, -54, 11, -54, P(hx("#c9852e", win), stroke=3.5))
    rrect(c, -31, -38, 46, 6, 3, P(hx(mixhex("#3a3290", "#5b4fc8", m))))
    # attic window
    glow(c, -31, -110, 10, "#ffc861", 0.6 * win, 2.2)
    c.drawCircle(-31, -110, 9, P(hx("#ffd47a", win)))
    # side window (in perspective)
    c.drawPath(path_from([(48, -70), (76, -73), (76, -45), (48, -42)], True), P(hx("#e8a94f", 0.95 * win)))
    c.restore()
    # smoke
    for k in range(5):
        ph = (t * 0.2 + k / 5) % 1
        sx = x + (69 + ph * 60 + math.sin(ph * 6 + k) * 10 + wind * ph * 260) * sc
        sy = y + (-186 - ph * 170 * (1 - 0.75 * wind)) * sc
        c.drawCircle(sx, sy, (9 + ph * 18) * sc, P(hx("#7d73c8", 0.30 * (1 - ph))))


def boat(c, x, y, t, m):
    """rowboat with a tiny fisherman and a lantern"""
    c.save(); c.translate(x, y + 2.5 * math.sin(t * 1.3)); c.rotate(1.5 * math.sin(t * 1.1))
    dark = hx(mixhex("#0d0b2c", "#15123d", m))
    rim = hx("#b6aaff", 0.6 * m)
    # lantern reflection + ripples on water
    for k in range(6):
        yy = 10 + k * 9
        w_ = 26 - k * 3 + 6 * math.sin(t * 3 + k)
        c.drawRoundRect(skia.Rect.MakeXYWH(-62 - w_ / 2, yy, w_, 4), 2, 2, P(hx("#ffcf6b", 0.45 * (1 - k / 6))))
    for k in range(2):
        ph = (t * 0.35 + k * 0.5) % 1
        c.drawOval(skia.Rect.MakeXYWH(-90 - 60 * ph, 2 - 3 * ph, 190 + 120 * ph, 16 + 6 * ph), P(hx("#c9c0ff", 0.25 * (1 - ph) * (0.4 + 0.6 * m)), stroke=2))
    # fishing line + bobber
    c.drawLine(78, -104, 92, 4, P(hx("#d8d0ff", 0.55), stroke=1.4))
    c.drawCircle(92, 4, 4, P(hx("#ff6b6b")))
    # fisherman
    c.drawPath(path_from([(-24, -14), (-20, -50), (-4, -56), (8, -48), (10, -14)], True, 0.6), P(dark))
    c.drawCircle(-8, -66, 11, P(dark))
    c.drawPath(path_from([(-24, -70), (8, -70), (2, -82), (-16, -82)], True), P(dark))   # hat
    c.drawLine(-28, -70, 12, -70, P(dark, stroke=5))
    c.drawLine(4, -46, 22, -34, P(dark, stroke=7))                                   # arm
    rod = skia.Path(); rod.moveTo(18, -32); rod.quadTo(52, -80, 78, -104)
    c.drawPath(rod, P(dark, stroke=3.5))
    c.drawLine(-19, -52, -4, -57, P(rim, stroke=2))
    # lantern on a pole at the stern
    c.drawLine(-62, -14, -62, -66, P(dark, stroke=4))
    c.drawLine(-62, -66, -48, -66, P(dark, stroke=3))
    glow(c, -48, -54, 12, "#ffcf6b", 1.0, 2.8)
    rrect(c, -55, -62, 14, 17, 4, P(hx("#ffe39a")))
    # hull
    hull = skia.Path()
    hull.moveTo(-74, -18); hull.lineTo(78, -24)
    hull.cubicTo(70, 0, 40, 12, 0, 12)
    hull.cubicTo(-40, 12, -66, 4, -74, -18)
    hull.close()
    c.drawPath(hull, P(dark))
    c.drawLine(-74, -18, 78, -24, P(rim, stroke=3))
    c.drawPath(path_from([(-60, -6), (64, -11)], False), P(hx("#2a2470", 0.8 * m), stroke=2))
    c.restore()


WHEEL = Stars(900, seed=41, region=(-700, -900, W + 700, 1500))
POLE = (500, 360)


def star_wheel(c, t, rot, trail, a=1.0, pole=POLE):
    """night sky turning around the pole star: rot = sky angle (deg), trail = arc length behind each star (deg)"""
    px, py = pole
    for (x, y, sz, ph, f, col, big) in WHEEL.s:
        dx, dy = x - px, y - py
        rr = math.hypot(dx, dy)
        if rr < 8:
            continue
        a0 = math.degrees(math.atan2(dy, dx)) + rot
        tw = 0.7 + 0.3 * math.sin(t * f * 2.4 + ph)
        if trail > 0.3:
            rect = skia.Rect.MakeXYWH(px - rr, py - rr, 2 * rr, 2 * rr)
            n = 5
            for k in range(n):  # tail fades out behind the star
                arc = skia.Path()
                arc.addArc(rect, a0 + trail * (1 - (k + 1) / n), trail / n + 0.15)
                c.drawPath(arc, P(hx(col, a * 0.55 * ((k + 1) / n) ** 1.6), stroke=sz * 0.75))
        ang = math.radians(a0)
        sx, sy = px + rr * math.cos(ang), py + rr * math.sin(ang)
        if big:
            c.drawCircle(sx, sy, sz * 3.0, P(hx(col, 0.16 * a * tw), blur=sz * 2))
        c.drawCircle(sx, sy, sz * 0.55 * (0.85 + 0.25 * tw), P(hx(col, a * tw)))
    # the pole star itself barely moves
    glow(c, px, py, 10, "#fff6d8", 0.8 * a, 2.4)
    c.drawCircle(px, py, 4.2, P(hx("#ffffff", a)))


def landscape(c, t, moon_s=1.0, m=1.0, ghost=0.0, flash=None, cam_y=0.0, cam_z=1.0, sparkle_p=None, shoot=None,
              sky_rot=None, trail=0.0, tree_bend=0.0, cloud_dx=0.0, show_boat=True, win=1.0, sky_fn=None, lake_fn=None):
    """sky_rot (deg) switches the sky to a wheeling star field around POLE with trails of `trail` degrees.
    sky_fn(c): extra sky layer drawn after stars/moon, before clouds and terrain (e.g. a ring arch).
    lake_fn(c, lake_top): extra reflections drawn on the lake (terrain coordinates)."""
    sky_top = mixhex("#0a0c2c", "#0e1446", m)
    sky_mid = mixhex("#151a58", "#25307e", m)
    sky_hor = mixhex("#2f2870", "#5a47a9", m)
    c.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, [hx(sky_top), hx(sky_mid), hx(sky_hor), hx(sky_hor)], [0, 0.42, 0.66, 1])))
    c.save()
    c.translate(W / 2, H * 0.45)
    c.scale(cam_z, cam_z)
    c.translate(-W / 2, -H * 0.45 + cam_y)
    # the Milky Way shows up once the moonlight is gone
    mw = (1 - m) * (1 - (moon_s if moon_s < 1 else 1) * 0.0)
    if sky_rot is not None:
        c.save(); c.rotate(sky_rot, POLE[0], POLE[1])
    if mw > 0.01:
        rnd_mw = random.Random(17)
        x0, y0, x1, y1 = -120, 1180, 1200, 120
        for k in range(18):
            u = k / 17 + rnd_mw.uniform(-0.03, 0.03)
            bx = lerp(x0, x1, u) + rnd_mw.uniform(-60, 60)
            by = lerp(y0, y1, u) + rnd_mw.uniform(-60, 60)
            rr = rnd_mw.uniform(130, 260)
            col = rnd_mw.choice(["#7a5cff", "#9b6bff", "#ff7ac8", "#ffd6b0", "#5a7cff"])
            c.drawCircle(bx, by, rr, P(shader=rad(bx, by, rr, [hx(col, 0.22 * mw), hx(col, 0.08 * mw), hx(col, 0)], [0, 0.5, 1])))
        for k in range(9):  # dark dust clouds
            u = rnd_mw.uniform(0.05, 0.95)
            bx = lerp(x0, x1, u) + rnd_mw.uniform(-40, 40)
            by = lerp(y0, y1, u) + rnd_mw.uniform(-40, 40)
            c.drawCircle(bx, by, rnd_mw.uniform(40, 90), P(hx("#0b0b32", 0.28 * mw), blur=30))
        c.save()
        band = skia.Path()
        band.moveTo(-200, 1000); band.lineTo(W + 200, -60); band.lineTo(W + 200, 380); band.lineTo(-200, 1440); band.close()
        c.clipPath(band, doAntiAlias=True)
        MILKY.draw(c, t, 0.85 * mw, 0, -cam_y * 0.4, 0.5)
        c.restore()
    if sky_rot is not None:
        c.restore()
        star_wheel(c, t, sky_rot, trail, 0.75 + 0.25 * (1 - m))
    else:
        STARS.draw(c, t, 0.75 + 0.25 * (1 - m), 0, -cam_y * 0.4)
    # moon halo lighting the sky
    if m > 0:
        c.drawCircle(MOON_X, MOON_Y, 760, P(shader=rad(MOON_X, MOON_Y, 760, [hx("#8f7dff", 0.30 * m), hx("#8f7dff", 0.08 * m), hx("#8f7dff", 0)], [0, 0.4, 1])))
    ghost_circle(c, MOON_X, MOON_Y, MOON_R, ghost, phase=t * 30)
    if moon_s > 0:
        moon(c, MOON_X, MOON_Y, MOON_R * moon_s, 1.0, glow_a=min(1, moon_s))
    if flash is not None:
        burst(c, MOON_X, MOON_Y, MOON_R, flash, "#ffffff", 12, 4)
    # shooting star
    if shoot is not None and 0 < shoot < 1:
        e = ease_out(shoot)
        x0, y0, x1, y1 = 120, 160, 560, 430
        hx_, hy_ = lerp(x0, x1, e), lerp(y0, y1, e)
        tl = 0.22
        tx, ty = lerp(x0, x1, max(0, e - tl)), lerp(y0, y1, max(0, e - tl))
        fa = math.sin(shoot * math.pi)
        c.drawLine(tx, ty, hx_, hy_, P(shader=lin(tx, ty, hx_, hy_, [hx("#ffffff", 0), hx("#ffffff", 0.9 * fa)]), stroke=4))
        glow(c, hx_, hy_, 8, "#ffffff", fa, 2.5)
    if sky_fn is not None:
        sky_fn(c)
    # flat clouds drifting (lit from the moon)
    for k, (cx0, cy0, sc, sp) in enumerate([(160, 300, 1.0, 9), (980, 785, 1.1, 6), (420, 170, 0.75, 11)]):
        x = (cx0 + t * sp + cloud_dx * (0.7 + 0.3 * k)) % (W + 500) - 250
        col = mixhex("#15144a", "#2f2b86", m)
        c.save(); c.translate(x, cy0); c.scale(sc, sc)
        cl = skia.Path()
        cl.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-150, -18, 300, 40), 20, 20))
        for (qx, qy, qr) in [(-50, -24, 42), (30, -34, 54), (95, -10, 30)]:
            cl = skia.Op(cl, circ_path(qx, qy, qr), skia.PathOp.kUnion_PathOp)
        c.drawPath(cl, P(hx(col, 0.92)))
        c.save(); c.clipPath(cl, doAntiAlias=True)
        c.drawPath(cl, P(hx("#b8adff", 0.5 * m), stroke=6))
        c.drawRect(skia.Rect.MakeXYWH(-200, 2, 400, 60), P(hx("#0d0c35", 0.4)))
        c.restore()
        c.restore()
    # hills, far to near (terrain group raised so the lake + cabin sit above the captions)
    c.save()
    c.translate(0, -170)
    rim = "#a596ff"
    m_rim = m
    m = max(m, 0.18)  # starlight keeps the world faintly readable
    # mountain ranges: snow and shadow faces are clipped to the silhouette, so they always follow the slopes
    mountain_range(c, [(-40, 1010), (150, 930), (330, 1000), (520, 900), (720, 985), (900, 915), (1110, 990)], 1090,
                   mixhex("#262266", "#4a40a8", m), mixhex("#1c1a55", "#332d86", m), mixhex("#4a4590", "#e3dcff", m), m, snow_h=58)
    mountain_range(c, [(-80, 1110), (90, 1020), (250, 1095), (420, 1035), (610, 1110), (800, 1030), (980, 1090), (1160, 1040)], 1150,
                   mixhex("#1e1b58", "#3a3290", m), mixhex("#16144a", "#28237a", m), mixhex("#3b3780", "#c9c0ff", m), m, snow_h=40)
    hill(c, 1190, [(46, 0.006, 0.4), (22, 0.017, 1.9)], mixhex("#1c1a52", "#2d2878", m), rim, 0.45 * m)
    hill(c, 1300, [(40, 0.0045, 2.2), (18, 0.013, 0.3)], mixhex("#16144a", "#241f68", m), rim, 0.5 * m)
    # lake with moon reflection
    lake_top = 1365
    c.drawRect(skia.Rect.MakeXYWH(0, lake_top, W, 260), P(shader=lin(0, lake_top, 0, lake_top + 200, [hx(mixhex("#151a52", "#2c3592", m)), hx(mixhex("#0e1240", "#1c2266", m))])))
    if m > 0 and moon_s > 0:
        for k in range(9):
            yy = lake_top + 14 + k * 17
            wv = 70 - k * 4 + 16 * math.sin(t * 2.2 + k * 1.3)
            ox = 10 * math.sin(t * 1.4 + k)
            c.drawRoundRect(skia.Rect.MakeXYWH(MOON_X - wv / 2 + ox, yy, wv, 6), 3, 3, P(hx("#e6deff", 0.55 * m * (1 - k / 10) * min(1, moon_s))))
    if lake_fn is not None:
        lake_fn(c, lake_top)
    for k in range(4):
        yy = lake_top + 40 + k * 38
        c.drawLine(120 + k * 60, yy, 260 + k * 60, yy, P(hx("#7d73d6", 0.25 * m), stroke=3))
    # little rowboat with a fisherman and a lantern
    if show_boat:
        boat(c, 545 + 10 * math.sin(t * 0.35), 1405, t, m)
    # drifting mist over the water
    for k in range(4):
        mx_ = (k * 330 + t * (14 + k * 4)) % (W + 600) - 300
        c.drawRoundRect(skia.Rect.MakeXYWH(mx_, 1328 + k * 22, 420, 26), 13, 13, P(hx("#c9c0ff", 0.07 + 0.04 * m), blur=14))
    # near hills with house + trees (one layer, dipping to reveal the lake under the moon)
    def near_y0(x):
        return 1440 + 150 * math.exp(-((x - 700) / 210) ** 2) + 22 * math.sin(x * 0.011 + 0.4) - 30 * math.exp(-((x - 120) / 260) ** 2)

    def near_y(x):  # with a flat shelf for the cabin
        w_ = smooth(seg(x, 705, 815)) * (1 - smooth(seg(x, 1015, 1085)))
        return lerp(near_y0(x), 1468, w_)
    pts = [(x, near_y(x)) for x in range(-100, W + 120, 20)]
    near_col = mixhex("#100e38", "#1d1958", m)
    c.drawPath(path_from(pts + [(W + 100, H + 400), (-100, H + 400)], True), P(shader=lin(0, 1400, 0, 1800, [hx(near_col), hx(mixhex("#09082a", "#120f3e", m))])))
    c.drawPath(path_from(pts, False), P(hx(rim, 0.55 * m), stroke=5))
    # grass tufts on the near hill
    for k in range(26):
        gx = 30 + k * 41
        if 330 < gx < 1075:
            continue
        gy = near_y(gx) + 4
        for j in (-1, 0, 1):
            c.drawLine(gx + j * 6, gy, gx + j * 11, gy - 16 - 6 * (j == 0), P(hx(mixhex("#1a1650", "#2c2678", m)), stroke=4))
    hx_ = 905
    house(c, hx_, 1472, t, m, win=win, wind=min(1.0, tree_bend * 2.5))
    for (px, s_) in [(90, 130), (190, 95), (290, 75), (380, 60), (1010, 105)]:
        pine(c, px, near_y(px) + 10, s_, mixhex("#0c0a2c", "#151249", m), rim, 0.6 * m, tree_bend * (1 + 0.15 * math.sin(t * 7 + px)))
    # foreground
    hill(c, 1700, [(40, 0.005, 1.0), (12, 0.03, 0.5)], mixhex("#080720", "#0f0d33", m))
    for (px, s) in [(60, 200), (1070, 230)]:
        pine(c, px, 1720, s, mixhex("#05041a", "#0a0928", m), rim, 0.35 * m, tree_bend * 0.8 * (1 + 0.15 * math.sin(t * 6 + px)))
    # fireflies (more visible in the dark)
    ff = 0.35 + 0.65 * (1 - m)
    rnd = random.Random(9)
    for k in range(14):
        bx, by = rnd.uniform(80, 1000), rnd.uniform(1480, 1760)
        x = bx + 30 * math.sin(t * 0.7 + k)
        y = by + 20 * math.sin(t * 0.9 + k * 2.1)
        tw = 0.5 + 0.5 * math.sin(t * 3 + k * 1.7)
        glow(c, x, y, 7, "#ffe27a", 0.7 * ff * tw, 2.5)
        c.drawCircle(x, y, 3, P(hx("#fff3b0", ff * tw)))
    c.restore()
    c.restore()


REEF_TIPS = []






def moon_phase(c, x, y, r, k, a):
    if a <= 0:
        return
    dark, lit = hx("#2b3374", a), hx("#efeaff", a)
    ang = 2 * math.pi * k / 8
    f = (1 - math.cos(ang)) / 2
    ew = r * abs(math.cos(ang))
    c.save()
    c.clipPath(circ_path(x, y, r), doAntiAlias=True)
    c.drawCircle(x, y, r, P(dark))
    if k == 4:
        c.drawCircle(x, y, r, P(lit))
    elif k != 0:
        waxing = k < 4
        c.drawRect(skia.Rect.MakeXYWH(x if waxing else x - r, y - r, r, 2 * r), P(lit))
        c.drawOval(skia.Rect.MakeXYWH(x - ew, y - r, 2 * ew, 2 * r), P(dark if f < 0.5 else lit))
    c.restore()


def crab(c, x, y, t, look, worry):
    """little original crab; look = 0 (at moon, up-right) .. 1 (looking around), worry adds a sweat drop"""
    c.save(); c.translate(x, y)
    bob = 3 * math.sin(t * 3)
    # legs
    for side in (-1, 1):
        for k in range(3):
            lx = side * (34 + k * 12)
            c.drawLine(side * 20, 6, lx, 30 + k * 2, P(hx("#d8452f"), stroke=7))
    # claws
    for side in (-1, 1):
        wav = (8 * math.sin(t * 5 + side) if worry > 0.5 else 3 * math.sin(t * 2 + side))
        c.save(); c.translate(side * 52, -14 + bob); c.rotate(side * (-20 + wav))
        c.drawLine(-side * 10, 12, 0, 0, P(hx("#e8553a"), stroke=9))
        c.drawCircle(0, -10, 17, P(hx("#ff6a4a")))
        c.drawCircle(side * 9, -24, 9, P(hx("#ff7a5a")))
        c.drawLine(side * 2, -12, side * 14, -20, P(hx("#b8331f"), stroke=3))
        c.restore()
    # body
    c.drawOval(skia.Rect.MakeXYWH(-46, -26 + bob, 92, 54), P(hx("#ff6a4a")))
    c.drawOval(skia.Rect.MakeXYWH(-40, -24 + bob, 70, 22), P(hx("#ff9a7a", 0.6)))
    # eye stalks + eyes
    lx = lerp(0.35, -0.6 * math.sin(t * 4.5), look)
    ly = lerp(-0.8, 0.0, look)
    for side in (-1, 1):
        ex, ey = side * 16, -52 + bob
        c.drawLine(side * 12, -20 + bob, ex, ey, P(hx("#e8553a"), stroke=6))
        c.drawCircle(ex, ey, 13, P(hx("#ffffff")))
        c.drawCircle(ex + lx * 5, ey + ly * 5, 6.5, P(hx("#140f38")))
        c.drawCircle(ex + lx * 5 - 2, ey + ly * 5 - 2.5, 2, P(hx("#ffffff")))
    # mouth
    mp = skia.Path(); mp.moveTo(-8, 4 + bob)
    if worry > 0.5:
        mp.quadTo(0, -2 + bob, 8, 4 + bob)
    else:
        mp.quadTo(0, 10 + bob, 8, 4 + bob)
    c.drawPath(mp, P(hx("#7a1f14"), stroke=3.5))
    if worry > 0:
        c.drawPath(path_from([(36, -48), (31, -36), (36, -32), (41, -36)], True, 0.8), P(hx("#9fe0ff", worry)))
    c.restore()


def stag(c, x, y, ang, L, w, depth, col, sway, tips, rnd, shadow=False, tip=None):
    x2 = x + math.cos(math.radians(ang)) * L
    y2 = y + math.sin(math.radians(ang)) * L
    if depth == 0 and tip and not shadow:
        c.drawLine(x, y, x2, y2, P(shader=lin(x, y, x2, y2, [hx(col), hx(tip)]), stroke=w))
    else:
        c.drawLine(x, y, x2, y2, P(hx(col), stroke=w))
    if depth == 0:
        if not shadow:
            tips.append((x2, y2))
        return
    n = 2 if rnd.random() < 0.7 else 3
    spread = 44
    for j in range(n):
        da = -spread / 2 + spread * j / (n - 1) + rnd.uniform(-8, 8)
        stag(c, x2, y2, ang + da + sway, L * rnd.uniform(0.66, 0.8), w * 0.8, depth - 1, col, sway, tips, rnd, shadow, tip)


def staghorn(c, x, y, s, col, shade, tip, sway, tips, seed):
    c.save(); c.translate(x, y); c.scale(s, s)
    for pass_ in range(2):
        rnd = random.Random(seed)
        c.save()
        if pass_ == 0:
            c.translate(7, 5)
        local = []
        for base_ang in (-118, -90, -64):
            stag(c, 0, 0, base_ang + rnd.uniform(-6, 6), 70, 24, 3, shade if pass_ == 0 else col, sway, local, rnd, pass_ == 0, tip)
        c.restore()
        if pass_ == 1:
            m_ = c.getTotalMatrix()
            for (tx, ty) in local:
                p = m_.mapXY(tx, ty)
                tips.append((p.x(), p.y()))
    c.restore()


def table_coral(c, x, y, w, col, shade, lit):
    c.drawRect(skia.Rect.MakeXYWH(x - 14, y - 70, 28, 72), P(hx(shade)))
    c.drawRect(skia.Rect.MakeXYWH(x - 14, y - 70, 10, 72), P(hx(col)))
    plate = skia.Path()
    plate.addOval(skia.Rect.MakeXYWH(x - w / 2, y - 100, w, 46))
    c.drawPath(plate, P(hx(shade)))
    top = skia.Path(); top.addOval(skia.Rect.MakeXYWH(x - w / 2, y - 110, w, 40))
    c.drawPath(top, P(hx(col)))
    c.save(); c.clipPath(top, doAntiAlias=True)
    for k in range(9):
        xx = x - w / 2 + 20 + k * (w - 40) / 8
        c.drawCircle(xx, y - 92 + 4 * math.sin(k), 7, P(hx(lit, 0.8)))
    c.restore()


def brain(c, x, y, r, col, shade, groove, seed):
    dome = skia.Path()
    dome.addArc(skia.Rect.MakeXYWH(x - r, y - r * 0.92, 2 * r, 1.84 * r), 180, 180)
    dome.lineTo(x - r, y)
    dome.close()
    c.drawPath(dome, P(hx(col)))
    c.save(); c.clipPath(dome, doAntiAlias=True)
    c.drawCircle(x + r * 0.5, y + r * 0.1, r * 0.95, P(hx(shade, 0.55)))
    rnd = random.Random(seed)
    for k in range(7):
        yy = y - r * 0.85 + k * r * 0.14
        pts = []
        for j in range(14):
            xx = x - r + j * 2 * r / 13
            pts.append((xx, yy + r * 0.05 * math.sin(j * 1.3 + rnd.uniform(0, 3))))
        c.drawPath(path_from(pts, False, 1.0), P(hx(groove, 0.75), stroke=4))
    c.restore()


def tubes(c, x, y, col, shade, inner, s=1.0):
    for (dx, h, w) in [(-34, 150, 40), (6, 205, 46), (46, 120, 36)]:
        bx = x + dx * s
        hh, ww = h * s, w * s
        rrect(c, bx - ww / 2, y - hh, ww, hh, ww / 2.4, P(hx(col)))
        c.drawRect(skia.Rect.MakeXYWH(bx + ww * 0.15, y - hh + ww * 0.3, ww * 0.35, hh - ww * 0.3), P(hx(shade, 0.6)))
        c.drawOval(skia.Rect.MakeXYWH(bx - ww / 2, y - hh - ww * 0.18, ww, ww * 0.36), P(hx(col)))
        c.drawOval(skia.Rect.MakeXYWH(bx - ww * 0.36, y - hh - ww * 0.12, ww * 0.72, ww * 0.24), P(hx(inner)))


def sea_fan(c, x, y, r, col, shade, sway):
    c.save(); c.translate(x, y); c.rotate(sway * 1.5)
    fan = skia.Path()
    fan.moveTo(0, 0)
    fan.cubicTo(-r * 1.05, -r * 0.25, -r * 1.0, -r * 1.1, -r * 0.15, -r * 1.12)
    fan.cubicTo(r * 0.75, -r * 1.12, r * 1.05, -r * 0.35, 0, 0)
    fan.close()
    c.drawPath(fan, P(hx(col, 0.38)))
    c.save(); c.clipPath(fan, doAntiAlias=True)
    rnd = random.Random(11)
    def vein(x0, y0, ang, L, w, d):
        x1 = x0 + math.cos(math.radians(ang)) * L
        y1 = y0 + math.sin(math.radians(ang)) * L
        pth = skia.Path(); pth.moveTo(x0, y0)
        mx_ = (x0 + x1) / 2 + rnd.uniform(-8, 8); my_ = (y0 + y1) / 2 + rnd.uniform(-8, 8)
        pth.quadTo(mx_, my_, x1, y1)
        c.drawPath(pth, P(hx(col), stroke=w))
        if d > 0:
            for da in (-20, 18):
                vein(x1, y1, ang + da + rnd.uniform(-6, 6), L * 0.72, w * 0.7, d - 1)
    for k in range(5):
        vein(0, 0, -150 + k * 30 + rnd.uniform(-5, 5), r * 0.42, 7, 3)
    c.restore()
    c.drawPath(fan, P(hx(shade), stroke=5))
    c.drawLine(0, -4, 0, 26, P(hx(shade), stroke=12))
    c.restore()


def kelp(c, x, y, h, t, k, col, leaf):
    pts = [(x + 26 * math.sin(t * 1.1 + k + j * 0.45) * (j / 10) ** 1.2, y - j * h / 10) for j in range(11)]
    c.drawPath(path_from(pts, False, 1.0), P(hx(col), stroke=10))
    for j in range(2, 10, 2):
        px, py = pts[j]
        side = 1 if j % 4 else -1
        c.save(); c.translate(px, py); c.rotate(side * (35 + 8 * math.sin(t * 1.3 + j)))
        c.drawOval(skia.Rect.MakeXYWH(0 if side > 0 else -46, -11, 46, 22), P(hx(leaf)))
        c.restore()


def reef_fish(c, x, y, s, body, stripe, flip, t, k, belly="#ffe7c2"):
    c.save(); c.translate(x, y); c.scale(-s if flip else s, s)
    wag = 6 * math.sin(t * 8 + k)
    tail = skia.Path()
    tail.moveTo(-30, 0)
    tail.quadTo(-44, -10, -58, -22 + wag)
    tail.quadTo(-50, 0, -58, 22 + wag)
    tail.quadTo(-44, 10, -30, 0)
    c.drawPath(tail, P(hx(mixhex(body, "#000000", 0.12))))
    fin = skia.Path(); fin.moveTo(-16, -14); fin.quadTo(-4, -40, 20, -16); fin.close()
    c.drawPath(fin, P(hx(mixhex(body, "#000000", 0.12))))
    bp = skia.Path()
    bp.moveTo(42, 2)
    bp.cubicTo(36, -26, -8, -30, -32, -3)
    bp.lineTo(-32, 3)
    bp.cubicTo(-8, 28, 34, 26, 42, 2)
    bp.close()
    c.drawPath(bp, P(shader=lin(0, -28, 0, 26, [hx(mixhex(body, "#000000", 0.08)), hx(body), hx(mixhex(body, belly, 0.55))], [0, 0.45, 1])))
    c.save(); c.clipPath(bp, doAntiAlias=True)
    for sx in (6, -16):
        st = skia.Path(); st.moveTo(sx, -32); st.quadTo(sx + 9, 0, sx, 32)
        c.drawPath(st, P(hx(stripe), stroke=9))
        c.drawPath(st, P(hx("#1a1440", 0.5), stroke=1.5))
    c.restore()
    pf = skia.Path(); pf.moveTo(12, 6); pf.quadTo(-2, 12 + wag * 0.3, 0, 20); pf.quadTo(10, 14, 12, 6)
    c.drawPath(pf, P(hx(mixhex(body, "#ffffff", 0.3), 0.9)))
    c.drawCircle(26, -5, 6.8, P(hx("#ffffff")))
    c.drawCircle(27.5, -5, 4, P(hx("#140f38")))
    c.drawCircle(26, -7, 1.6, P(hx("#ffffff")))
    mo = skia.Path(); mo.moveTo(41, 4); mo.quadTo(37, 7, 34, 6)
    c.drawPath(mo, P(hx("#7a2a3a"), stroke=2))
    c.restore()


def season_icon(c, kind, x, y, s, a):
    if a <= 0:
        return
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawCircle(0, 0, 58, P(hx("#1a2060", 0.9 * a)))
    c.drawCircle(0, 0, 58, P(hx("#ffffff", 0.12 * a), stroke=3))
    if kind == "snow":
        for k in range(6):
            c.save(); c.rotate(k * 60)
            pp = P(hx("#bfe8ff", a), stroke=7)
            c.drawLine(0, 0, 0, -34, pp)
            c.drawLine(0, -22, -10, -32, pp); c.drawLine(0, -22, 10, -32, pp)
            c.restore()
    elif kind == "flower":
        for k in range(5):
            ang = k * 72
            c.drawCircle(18 * math.cos(math.radians(ang)), 18 * math.sin(math.radians(ang)), 15, P(hx("#ff7ab8", a)))
        c.drawCircle(0, 0, 12, P(hx("#ffd84d", a)))
    elif kind == "sun":
        for k in range(8):
            c.save(); c.rotate(k * 45)
            c.drawLine(0, -26, 0, -38, P(hx("#ffd84d", a), stroke=7))
            c.restore()
        c.drawCircle(0, 0, 18, P(hx("#ffd84d", a)))
    elif kind == "leaf":
        c.rotate(-30)
        pth = skia.Path(); pth.moveTo(0, -36); pth.cubicTo(30, -20, 26, 20, 0, 36); pth.cubicTo(-26, 20, -30, -20, 0, -36)
        c.drawPath(pth, P(hx("#ff8a3d", a)))
        c.drawLine(0, -30, 0, 40, P(hx("#c25a1c", a), stroke=4))
    c.restore()


def spinning_top(c, x, y, t, a, steady=1.0):
    c.save(); c.translate(x, y)
    # shadow
    c.drawOval(skia.Rect.MakeXYWH(-60, 92, 120, 22), P(hx("#000010", 0.35 * a)))
    lean = 14 * math.sin(t * 5) * (1 - steady)
    c.rotate(lean)
    body = skia.Path()
    body.moveTo(-78, 0); body.cubicTo(-78, 40, -20, 70, 0, 100); body.cubicTo(20, 70, 78, 40, 78, 0)
    body.cubicTo(78, -22, -78, -22, -78, 0); body.close()
    c.save(); c.clipPath(body, doAntiAlias=True)
    c.drawPath(body, P(hx("#ff5d7a", a)))
    for k in range(-4, 5):
        xx = ((k * 40 + t * 260) % 360) - 180
        c.drawRect(skia.Rect.MakeXYWH(xx, -40, 18, 160), P(hx("#ffd84d", 0.9 * a)))
    c.drawRect(skia.Rect.MakeXYWH(-90, -6, 180, 12), P(hx("#ffffff", 0.35 * a)))
    c.restore()
    c.drawOval(skia.Rect.MakeXYWH(-78, -16, 156, 32), P(hx("#ff8aa0", a)))
    rrect(c, -9, -70, 18, 62, 8, P(hx("#c9c2ff", a)))
    c.restore()




def hand2(c, x, y, a):
    """relaxed hand gripping the top's knob from above (all four fingers curled down around it).
    (x, y) = top of the knob."""
    if a <= 0:
        return
    c.saveLayerAlpha(None, int(255 * clamp(a)))
    c.translate(x, y)
    skin = hx("#f6b994")
    skin_d = hx("#de9a74")
    skin_dd = hx("#c98262")
    nail = hx("#ffe3d2")
    sleeve, sleeve_d, cuff = hx("#4a6cff"), hx("#3a58e0"), hx("#2f47c4")
    # forearm + sleeve, entering from the upper right, off-screen
    c.save(); c.translate(46, -96); c.rotate(38)
    rrect(c, -44, -900, 88, 880, 34, P(sleeve))
    c.drawRect(skia.Rect.MakeXYWH(14, -900, 30, 860), P(sleeve_d))
    c.restore()
    # back of the hand: a soft rounded dome above the knob
    back = skia.Path()
    back.moveTo(-58, -46)
    back.cubicTo(-62, -96, -18, -124, 26, -120)
    back.cubicTo(62, -116, 84, -92, 74, -54)
    back.cubicTo(66, -30, -50, -24, -58, -46)
    back.close()
    c.drawPath(back, P(skin))
    c.save(); c.clipPath(back, doAntiAlias=True)
    c.drawOval(skia.Rect.MakeXYWH(10, -130, 90, 110), P(skin_d))           # shaded far side
    c.drawPath(path_from([(-36, -58), (-8, -64), (22, -64), (50, -58)], False, 1.0), P(skin_d, stroke=3))  # knuckle line
    c.restore()
    # thumb wrapping round the near side
    th = skia.Path()
    th.moveTo(-52, -78); th.cubicTo(-80, -60, -74, -20, -42, -8)
    th.cubicTo(-30, -4, -24, -14, -30, -22)
    th.cubicTo(-48, -34, -50, -56, -36, -70); th.close()
    c.drawPath(th, P(skin))
    th_edge = skia.Path(); th_edge.moveTo(-60, -70); th_edge.cubicTo(-76, -50, -70, -18, -42, -8); th_edge.cubicTo(-30, -4, -24, -14, -30, -22)
    c.drawPath(th_edge, P(hx("#b9765a", 0.55), stroke=2.5))
    c.drawPath(path_from([(-44, -40), (-36, -30)], False), P(skin_d, stroke=2))
    c.drawOval(skia.Rect.MakeXYWH(-44, -20, 14, 11), P(nail))
    c.drawOval(skia.Rect.MakeXYWH(-30, 4, 64, 16), P(hx("#0a0a30", 0.25), blur=5))
    # four fingers curling down around the knob (back to front, each slightly lower and lighter)
    fingers = [  # (knuckle x, knuckle y, tip x, tip y, width, colour)
        (52, -60, 26, -2, 21, skin_dd),
        (30, -62, 12, 6, 22, skin_d),
        (6, -62, -4, 8, 23, skin),
        (-18, -58, -18, 4, 22, skin),
    ]
    for (kx, ky, tx, ty, w_, col) in fingers:
        f = skia.Path()
        f.moveTo(kx, ky)
        f.cubicTo(kx + 4, ky + 26, tx + 10, ty - 22, tx, ty)
        c.drawPath(f, P(col, stroke=w_))
        c.drawPath(f, P(hx("#b9765a", 0.55), stroke=w_ + 3))  # outline under-pass
        c.drawPath(f, P(col, stroke=w_ - 1))
    for (kx, ky, tx, ty, w_, col) in fingers[2:]:
        c.drawOval(skia.Rect.MakeXYWH(tx - 6, ty - 12, 12, 10), P(nail))
    # cuff over the wrist
    c.save(); c.translate(46, -96); c.rotate(38)
    rrect(c, -50, -36, 100, 34, 16, P(cuff))
    c.restore()
    c.restore()


def axis_and_arc(c, cx, cy, r, tilt, a, col="#ffffff", label=True, ref=True):
    if a <= 0:
        return
    L = r * 1.42
    tr = math.radians(tilt)
    dx, dy = math.sin(tr) * L, -math.cos(tr) * L
    if ref:
        dashed(c, path_from([(cx, cy - L), (cx, cy - r * 1.02)], False), P(hx("#ffffff", 0.45 * a), stroke=4), 12, 10)
    c.drawLine(cx - dx, cy - dy, cx + dx, cy + dy, P(hx(col, 0.0), stroke=1))
    # axis segments outside the planet
    k0 = r * 1.02 / L
    c.drawLine(cx + dx * k0, cy + dy * k0, cx + dx, cy + dy, P(hx(col, a), stroke=7))
    c.drawLine(cx - dx * k0, cy - dy * k0, cx - dx, cy - dy, P(hx(col, a), stroke=7))
    c.drawCircle(cx + dx, cy + dy, 9, P(hx(col, a)))
    if label:
        rr = r * 1.25
        start = -90
        sweep = tilt
        arc = skia.Path(); arc.addArc(skia.Rect.MakeXYWH(cx - rr, cy - rr, 2 * rr, 2 * rr), start, sweep)
        c.drawPath(arc, P(hx("#ffd84d", a), stroke=6))
        mid = math.radians(start + sweep / 2)
        lx, ly = cx + math.cos(mid) * (rr + 70) + 20, cy + math.sin(mid) * (rr + 70)
        text(c, f"{tilt:.1f}°" if abs(tilt - 23.4) < 0.05 else f"{round(tilt)}°", lx, ly + 18, 52, "#ffd84d", a, shadow=1)


def orbit_ring(c, cx, cy, rx, ry, rot, a, front):
    if a <= 0:
        return
    c.save(); c.translate(cx, cy); c.rotate(rot)
    pth = skia.Path()
    pth.addArc(skia.Rect.MakeXYWH(-rx, -ry, 2 * rx, 2 * ry), 0 if front else 180, 180)
    dashed(c, pth, P(hx("#cfc6ff", 0.6 * a), stroke=4), 14, 12)
    c.restore()


def phobos(c, x, y, s, col="#9a7f6c"):
    c.save(); c.translate(x, y)
    c.drawPath(path_from([(-s, -s * 0.5), (-s * 0.2, -s * 0.8), (s * 0.9, -s * 0.4), (s, s * 0.3), (s * 0.1, s * 0.75), (-s * 0.85, s * 0.45)], True, 1.0), P(hx(col)))
    c.drawCircle(s * 0.25, -s * 0.1, s * 0.22, P(hx("#7d6656")))
    c.restore()


def thermometer(c, x, y, h, v, a):
    """v in -1 (cold) .. 1 (hot)."""
    col = mixhex("#5cc8ff", "#ff5a3d", (v + 1) / 2)
    rrect(c, x - 26, y, 52, h, 26, P(hx("#1a1f55", 0.95 * a)))
    rrect(c, x - 26, y, 52, h, 26, P(hx("#ffffff", 0.18 * a), stroke=4))
    c.drawCircle(x, y + h + 26, 48, P(hx("#1a1f55", 0.95 * a)))
    c.drawCircle(x, y + h + 26, 36, P(hx(col, a)))
    lvl = lerp(0.15, 0.92, (v + 1) / 2)
    top = y + h - (h - 20) * lvl
    rrect(c, x - 13, top, 26, y + h + 20 - top, 13, P(hx(col, a)))
    for k in range(5):
        yy = y + 30 + k * (h - 50) / 4
        c.drawLine(x + 30, yy, x + 46, yy, P(hx("#ffffff", 0.4 * a), stroke=4))


# ---------------------------------------------------------------- episode 002 additions (spin, winds, new world)
def spin_arrow(c, cx, cy, rx, ry, a, col, t, front, rot=0.0, flow=1.0):
    """elliptical arrow around a planet's equator showing eastward spin (front half moves left -> right).
    Draw with front=False BEFORE the planet and front=True AFTER it."""
    if a <= 0:
        return
    c.save(); c.translate(cx, cy); c.rotate(rot)
    rect = skia.Rect.MakeXYWH(-rx, -ry, 2 * rx, 2 * ry)
    if not front:
        arc = skia.Path(); arc.addArc(rect, 180, 180)
        dashed(c, arc, P(hx(col, 0.35 * a), stroke=5), 16, 14, -t * 60 * flow)
    else:
        arc = skia.Path(); arc.addArc(rect, 160, -138)
        c.drawPath(arc, P(hx(col, 0.25 * a), stroke=16, blur=6))
        dashed(c, arc, P(hx(col, 0.95 * a), stroke=7), 26, 14, t * 90 * flow)
        ang = math.radians(22)
        x, y = rx * math.cos(ang), ry * math.sin(ang)
        tx_, ty_ = rx * math.sin(ang), -ry * math.cos(ang)
        d = math.hypot(tx_, ty_)
        tx_, ty_ = tx_ / d, ty_ / d
        nx_, ny_ = -ty_, tx_
        s = 30
        head = path_from([(x + tx_ * s, y + ty_ * s), (x - tx_ * s * 0.6 + nx_ * s * 0.75, y - ty_ * s * 0.6 + ny_ * s * 0.75),
                          (x - tx_ * s * 0.6 - nx_ * s * 0.75, y - ty_ * s * 0.6 - ny_ * s * 0.75)], True)
        c.drawPath(head, P(hx(col, a)))
    c.restore()


def wind_streaks(c, t, a, speed=1.0, seed=4, n=24, y0=150, y1=1320, col="#e8f2ff"):
    """fast air lines racing to the right (east): soft wide gusts + crisp tapered streaks"""
    if a <= 0:
        return
    rnd = random.Random(seed)
    for k in range(6):  # broad soft gusts
        y = rnd.uniform(y0, y1)
        sp = rnd.uniform(700, 1000) * speed
        L = rnd.uniform(500, 800)
        x = (rnd.uniform(0, W + 1400) + t * sp) % (W + 1400) - 700
        pts = [(x - L + u * L / 12, y + 18 * math.sin(u / 12 * 4 + t * 2 + k)) for u in range(13)]
        c.drawPath(path_from(pts, False, 0.6), P(shader=lin(x - L, y, x, y, [hx(col, 0), hx(col, 0.10 * a), hx(col, 0)]), stroke=34, blur=12, mode=skia.BlendMode.kPlus))
    for k in range(n):
        y = rnd.uniform(y0, y1)
        L = rnd.uniform(240, 520)
        sp = rnd.uniform(1100, 1700) * speed
        x = (rnd.uniform(0, W + 1000) + t * sp) % (W + 1000) - 500
        th = rnd.uniform(3.0, 6.0)
        pts = [(x - L + u * L / 15, y + 9 * math.sin(u / 15 * 3.5 + t * 5 + k)) for u in range(16)]
        pth = path_from(pts, False, 0.6)
        c.drawPath(pth, P(shader=lin(x - L, y, x, y, [hx(col, 0), hx(col, 0.75 * a)]), stroke=th, mode=skia.BlendMode.kPlus))


def flying_leaves(c, t, a, seed=6, n=18):
    if a <= 0:
        return
    rnd = random.Random(seed)
    for k in range(n):
        y = rnd.uniform(500, 1300)
        sp = rnd.uniform(500, 900)
        x = (rnd.uniform(0, W + 400) + t * sp) % (W + 400) - 200
        yy = y + 40 * math.sin(t * 3 + k) - (x * 0.08)
        s = rnd.uniform(14, 22)
        col = rnd.choice(["#5fcf8e", "#9be38a", "#ffcf6b"])
        c.save(); c.translate(x, yy); c.rotate(t * rnd.uniform(200, 500) + k * 40)
        leaf = path_from([(-s, 0), (0, -s * 0.55), (s, 0), (0, s * 0.55)], True, 0.8)
        c.drawPath(leaf, P(hx(col, 0.9 * a)))
        c.drawLine(-s * 0.8, 0, s * 0.8, 0, P(hx("#1a3a2a", 0.5 * a), stroke=1.5))
        c.restore()


def planet_shade(c, cx, cy, r, light=(-0.75, -0.45)):
    """re-apply the planet's flat shading + rim (for overlays painted on top of planet())"""
    llx, lly = light
    c.save(); c.translate(cx, cy)
    c.clipPath(circ_path(0, 0, r), doAntiAlias=True)
    sh = skia.Op(circ_path(0, 0, r * 1.01), circ_path(llx * r * 0.42, lly * r * 0.42, r * 1.08), skia.PathOp.kDifference_PathOp)
    if sh:
        c.drawPath(sh, P(hx("#0a0f3a", 0.36), blur=r * 0.006))
    sh2 = skia.Op(circ_path(0, 0, r * 1.01), circ_path(llx * r * 0.9, lly * r * 0.9, r * 1.25), skia.PathOp.kDifference_PathOp)
    if sh2:
        c.drawPath(sh2, P(hx("#050826", 0.28), blur=r * 0.03))
    hl = skia.Op(circ_path(0, 0, r), circ_path(-llx * r * 0.12, -lly * r * 0.12, r * 0.98), skia.PathOp.kDifference_PathOp)
    if hl:
        c.drawPath(hl, P(hx("#ffffff", 0.22), blur=r * 0.01))
    c.restore()


def _shore(r, lat, top, lon0, wob=0.035, ph=0.0):
    """wavy coastline at latitude lat (deg) across the visible disc, as a list of points left -> right"""
    yb = -r * math.sin(math.radians(lat))
    pts = []
    for i in range(73):
        x = -r * 1.05 + 2.1 * r * i / 72
        u = x / r
        w_ = math.sin(u * 5.0 + ph) * 0.5 + math.sin(u * 11.0 + 1.7 + ph) * 0.3 + math.sin(u * 23.0 + 0.4) * 0.12
        pts.append((x, yb + r * wob * w_ * (1 if top else -1)))
    return pts


def new_world(c, cx, cy, r, lon0, n_lat, s_lat, land_a, hero=0.0, t=0.0, drain=1.0):
    """Overlay for a planet() Earth that has stopped spinning: oceans pooled at the poles above n_lat / below s_lat,
    and the drained equatorial sea floor (fading in with land_a) joining every continent into one belt."""
    c.save(); c.translate(cx, cy)
    c.clipPath(circ_path(0, 0, r), doAntiAlias=True)
    north = _shore(r, n_lat, True, lon0, ph=0.4)
    south = _shore(r, s_lat, False, lon0, ph=2.1)
    belt = path_from(north + list(reversed(south)), True)
    if land_a > 0 and drain > 0:
        c.save(); c.clipPath(belt, doAntiAlias=True)
        hb = r * 1.05 * drain   # the sea floor dries out from the equator toward both shores
        wet = path_from([(x, -hb + 10 * math.sin(x * 0.03 + 1)) for x in range(int(-r) - 10, int(r) + 20, 20)] +
                        [(x, hb + 10 * math.sin(x * 0.025 + 2)) for x in range(int(r) + 10, int(-r) - 20, -20)], True, 0.6)
        c.clipPath(wet, doAntiAlias=True)
        c.drawRect(skia.Rect.MakeXYWH(-r, -r, 2 * r, 2 * r), P(shader=lin(-r * 0.6, -r * 0.6, r * 0.7, r * 0.7, [hx("#ecc46e", land_a), hx("#d49a4c", land_a)])))
        # new grassland spreading over the old sea floor, and a few dry basins
        rnd = random.Random(3)
        for k in range(16):
            x, y = rnd.uniform(-r, r), rnd.uniform(north[36][1] + 30, south[36][1] - 30)
            w_, h_ = rnd.uniform(90, 200), rnd.uniform(30, 60)
            c.drawPath(path_from([(x - w_ / 2, y), (x - w_ * 0.2, y - h_ / 2), (x + w_ * 0.3, y - h_ * 0.4), (x + w_ / 2, y + h_ * 0.1), (x, y + h_ / 2)], True, 1.0),
                       P(hx("#8fc66a" if k % 3 else "#b98d50", 0.6 * land_a)))
        # the old continents stay green on top
        for name, poly in CONT_D.items():
            pts, vis = project(poly, r, lon0)
            if vis:
                c.drawPath(path_from(pts, True, 0.6), P(hx("#3ec27a", land_a)))
        for name, poly in FOR_D.items():
            pts, vis = project(poly, r, lon0)
            if vis:
                c.drawPath(path_from(pts, True, 0.8), P(hx("#2ea866", 0.9 * land_a)))
        for name, poly in DES_D.items():
            pts, vis = project(poly, r, lon0)
            if vis:
                c.drawPath(path_from(pts, True, 0.8), P(hx("#e6be62", 0.92 * land_a)))
        c.restore()
    # polar oceans
    for pts, top in ((north, True), (south, False)):
        edge = -r * 1.1 if top else r * 1.1
        poly = pts + [(r * 1.1, edge), (-r * 1.1, edge)]
        sea = path_from(poly, True)
        yb = pts[36][1]
        c.drawPath(sea, P(shader=lin(0, yb, 0, edge, [hx("#2a8fe6", 0.96), hx("#1450b4", 0.98)])))
        c.drawPath(path_from(pts, False, 0.5), P(hx("#9ae6ff", 0.55), stroke=r * 0.03))
        c.drawPath(path_from(pts, False, 0.5), P(hx("#e6f8ff", 0.85), stroke=r * 0.009))
    c.restore()
    planet_shade(c, cx, cy, r)
    if hero > 0:  # glowing outline of the new continent
        c.save(); c.translate(cx, cy); c.clipPath(circ_path(0, 0, r * 1.0), doAntiAlias=True)
        for pts in (north, south):
            c.drawPath(path_from(pts, False, 0.5), P(hx("#ffd84d", 0.55 * hero), stroke=14, blur=8, mode=skia.BlendMode.kPlus))
            c.drawPath(path_from(pts, False, 0.5), P(hx("#fff2b0", 0.9 * hero), stroke=4))
        c.restore()


def cabin_icon(c, x, y, s, ang, lit, a=1.0):
    """tiny cabin standing on a surface at (x, y), 'up' pointing along ang (degrees); lit = window glow 0..1"""
    c.save(); c.translate(x, y); c.rotate(ang + 90); c.scale(s, s)
    c.drawRect(skia.Rect.MakeXYWH(-10, -16, 20, 16), P(hx("#6b4fd8", a)))
    c.drawRect(skia.Rect.MakeXYWH(0, -16, 10, 16), P(hx("#5440b8", a)))
    c.drawPath(path_from([(-13, -15), (0, -27), (13, -15)], True), P(hx("#ff7a59", a)))
    c.drawRect(skia.Rect.MakeXYWH(-6, -11, 6, 6), P(hx(mixhex("#2b2370", "#ffd84d", lit), a)))
    if lit > 0:
        glow(c, -3, -8, 6, "#ffd84d", 0.8 * lit * a, 2.2)
    c.restore()


def arc_arrow(c, cx, cy, rr, a0, a1, p, col, a=1.0, w=8):
    """curved arrow along a circle of radius rr from angle a0 to a1 (deg, screen); p = draw-on progress 0..1"""
    if a <= 0 or p <= 0:
        return
    a1p = a0 + (a1 - a0) * p
    arc = skia.Path(); arc.addArc(skia.Rect.MakeXYWH(cx - rr, cy - rr, 2 * rr, 2 * rr), a0, a1p - a0)
    c.drawPath(arc, P(hx(col, 0.3 * a), stroke=w * 2.6, blur=6))
    c.drawPath(arc, P(hx(col, a), stroke=w))
    an = math.radians(a1p)
    x, y = cx + rr * math.cos(an), cy + rr * math.sin(an)
    sg = 1 if a1 > a0 else -1
    tx_, ty_ = -math.sin(an) * sg, math.cos(an) * sg
    nx_, ny_ = -ty_, tx_
    s = w * 3.2
    head = path_from([(x + tx_ * s, y + ty_ * s), (x - tx_ * s * 0.5 + nx_ * s * 0.8, y - ty_ * s * 0.5 + ny_ * s * 0.8),
                      (x - tx_ * s * 0.5 - nx_ * s * 0.8, y - ty_ * s * 0.5 - ny_ * s * 0.8)], True)
    c.drawPath(head, P(hx(col, a)))


# ---------------------------------------------------------------- episode 003 additions (the brain, an eye, a dolphin)
_BR_OUT = [(-0.93, 0.20), (-1.01, -0.06), (-0.95, -0.38), (-0.74, -0.64), (-0.42, -0.82), (-0.04, -0.89), (0.34, -0.84),
           (0.66, -0.68), (0.90, -0.42), (1.00, -0.10), (0.96, 0.18), (0.80, 0.36), (0.56, 0.42), (0.30, 0.47),
           (0.04, 0.57), (-0.26, 0.59), (-0.50, 0.50), (-0.63, 0.32), (-0.74, 0.26)]
# grooves (sulci), unit coords, side view facing LEFT; the first two are the big landmark fissures
_BR_GROOVES = [
    [(-0.64, 0.24), (-0.40, 0.12), (-0.10, 0.08), (0.18, -0.04), (0.38, -0.16)],                 # lateral fissure
    [(0.08, -0.89), (0.02, -0.64), (0.08, -0.40), (-0.02, -0.18), (0.02, 0.04)],                   # central groove
    [(-0.22, -0.86), (-0.28, -0.66), (-0.20, -0.48), (-0.28, -0.30), (-0.20, -0.16)],
    [(-0.52, -0.74), (-0.44, -0.58), (-0.54, -0.42), (-0.46, -0.26)],
    [(-0.80, -0.50), (-0.70, -0.38), (-0.78, -0.22), (-0.68, -0.08)],
    [(-0.97, -0.16), (-0.86, -0.06), (-0.90, 0.10)],
    [(-0.62, -0.12), (-0.48, -0.06), (-0.38, -0.14), (-0.30, -0.02)],
    [(0.26, -0.84), (0.22, -0.62), (0.30, -0.46), (0.24, -0.30)],
    [(0.52, -0.72), (0.46, -0.54), (0.56, -0.36), (0.50, -0.18)],
    [(0.78, -0.54), (0.70, -0.38), (0.80, -0.20)],
    [(0.97, -0.20), (0.86, -0.06), (0.92, 0.12)],
    [(0.30, -0.12), (0.46, 0.0), (0.62, 0.02), (0.76, 0.16)],
    [(-0.48, 0.38), (-0.24, 0.28), (0.0, 0.32), (0.22, 0.22), (0.40, 0.26)],
    [(-0.20, 0.52), (0.04, 0.46), (0.26, 0.42)],
]
BRAIN_LIT, BRAIN_SHADE, BRAIN_GROOVE, BRAIN_RIM = "#ff9fd0", "#d8679f", "#b94a87", "#ffd9ec"


def _dense_pts(pts, step):
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        out += [(lerp(x0, x1, i / n), lerp(y0, y1, i / n)) for i in range(n)]
    return out + [pts[-1]]


def _wiggle(pts, amp, freq, ph):
    d = _dense_pts(pts, 0.012)
    out, acc = [], 0.0
    for i, (x, y) in enumerate(d):
        if i:
            acc += math.hypot(x - d[i - 1][0], y - d[i - 1][1])
        a, b = d[max(0, i - 1)], d[min(len(d) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1
        env = max(0.0, math.sin(math.pi * i / max(1, len(d) - 1))) ** 0.5
        off = amp * env * math.sin(acc * freq + ph)
        out.append((x - ty / L * off, y + tx / L * off))
    return out


def _br_outline():
    # Catmull-Rom outline sampled densely, then scalloped: one soft bump per fold so the edge reads as gyri
    pth = path_from(_BR_OUT, True, 1.0)
    meas = skia.PathMeasure(pth, True)
    L = meas.getLength()
    n = 260
    pts = []
    for i in range(n):
        (px, py), (tx, ty) = meas.getPosTan(L * i / n)
        bump = 0.0
        pts.append((px - ty * bump, py + tx * bump))
    return pts


_BR_EDGE = None
_BR_GW = None


def brain_paths(x, y, s):
    """(cerebrum, cerebellum, stem) skia paths for a side-view brain centred at (x, y), half-width s"""
    global _BR_EDGE
    if _BR_EDGE is None:
        _BR_EDGE = _br_outline()
    cer = path_from([(x + s * u, y + s * v) for u, v in _BR_EDGE], True, 0.5)
    cb = skia.Path(); cb.addOval(skia.Rect.MakeXYWH(x + s * 0.30, y + s * 0.30, s * 0.62, s * 0.40))
    stem = path_from([(x + s * 0.14, y + s * 0.40), (x + s * 0.40, y + s * 0.40), (x + s * 0.36, y + s * 0.70),
                      (x + s * 0.34, y + s * 0.98), (x + s * 0.18, y + s * 0.98), (x + s * 0.16, y + s * 0.66)], True, 0.6)
    return cer, cb, stem


def brain_side(c, x, y, s, a=1.0, lit=BRAIN_LIT, shade=BRAIN_SHADE, groove=BRAIN_GROOVE, rim=BRAIN_RIM, inner=None,
               stem_a=1.0, over=None, tint=0.0, tint_col="#4b45a8"):
    """friendly side-view brain (facing left, light from upper left). `inner(c)` draws extra layers clipped inside
    the cerebrum (fluid, sparks...) after the base colours and before the grooves; `over(c)` draws clipped after them."""
    global _BR_GW
    if a <= 0:
        return
    if tint > 0:
        lit, shade, groove, rim = (mixhex(q, tint_col, tint) for q in (lit, shade, groove, rim))
    if _BR_GW is None:
        _BR_GW = [_wiggle(g, 0.012 if k < 2 else 0.042, 13, k * 1.7) for k, g in enumerate(_BR_GROOVES)]
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    cer, cb, stem = brain_paths(x, y, s)
    # brainstem + cerebellum sit behind the cerebrum
    if stem_a > 0:
        c.drawPath(stem, P(hx(mixhex(shade, "#7a3a8a", 0.25), stem_a)))
        c.save(); c.clipPath(stem, doAntiAlias=True)
        c.drawRect(skia.Rect.MakeXYWH(x + s * 0.12, y + s * 0.4, s * 0.09, s * 0.6), P(hx(mixhex(lit, shade, 0.5), stem_a)))
        c.restore()
    c.drawPath(cb, P(hx(shade)))
    c.save(); c.clipPath(cb, doAntiAlias=True)
    c.drawOval(skia.Rect.MakeXYWH(x + s * 0.27, y + s * 0.26, s * 0.62, s * 0.38), P(hx(mixhex(lit, shade, 0.35))))
    for k in range(5):
        yy = y + s * (0.40 + k * 0.065)
        c.drawPath(path_from([(x + s * 0.28, yy - s * 0.02), (x + s * 0.60, yy + s * 0.03), (x + s * 0.95, yy - s * 0.03)], False, 1.0),
                   P(hx(groove, 0.8), stroke=max(2, s * 0.022)))
    c.restore()
    # cerebrum: shadow colour, then the lit face offset towards the light (two-tone flat shading)
    c.drawPath(cer, P(hx(shade)))
    c.save(); c.clipPath(cer, doAntiAlias=True)
    c.save(); c.translate(x - s * 0.045, y - s * 0.06); c.scale(0.975, 0.975); c.translate(-x, -y)
    c.drawPath(cer, P(shader=lin(x - s, y - s, x + s, y + s * 0.5, [hx(mixhex(lit, "#ffffff", 0.14)), hx(lit)])))
    c.restore()
    if inner is not None:
        inner(c)
    for k, g in enumerate(_BR_GW):
        pts = [(x + s * u, y + s * v) for u, v in g]
        w = s * (0.036 if k < 2 else 0.03)
        pth = path_from(pts, False, 0.8)
        c.drawPath(pth, P(hx(groove), stroke=w))
        # a thin highlight just above each groove sells the soft folds
        c.save(); c.translate(-s * 0.010, -s * 0.020)
        c.drawPath(pth, P(hx(rim, 0.30), stroke=w * 0.4))
        c.restore()
    if over is not None:
        over(c)
    c.restore()
    # rim light on the upper-left edge, fading out smoothly
    c.drawPath(cer, P(shader=lin(x - s * 0.8, y - s * 0.8, x + s * 0.1, y + s * 0.1, [hx(rim, 0.9), hx(rim, 0)]), stroke=max(2, s * 0.018)))
    if a < 1:
        c.restore()


def brain_top(c, x, y, s, left=1.0, right=1.0, a=1.0):
    """top-view brain icon (front at the top): two hemispheres. left/right = how awake each half is (0 = dark, asleep)"""
    if a <= 0:
        return
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    for side, k in ((-1, left), (1, right)):
        lit = mixhex("#4a3f8f", BRAIN_LIT, k)
        sh = mixhex("#2f2868", BRAIN_SHADE, k)
        gr = mixhex("#241d55", BRAIN_GROOVE, k)
        pts = [(x + side * s * u, y + s * v) for u, v in
               [(0.04, -0.98), (0.40, -0.92), (0.70, -0.70), (0.84, -0.30), (0.86, 0.12), (0.76, 0.56), (0.50, 0.90),
                (0.20, 1.00), (0.04, 0.96)]]
        pth = path_from(pts, True, 1.0)
        c.drawPath(pth, P(hx(sh)))
        c.save(); c.clipPath(pth, doAntiAlias=True)
        c.save(); c.translate(-s * 0.05, -s * 0.06)
        c.drawPath(pth, P(hx(lit)))
        c.restore()
        for g in ([(0.14, -0.74), (0.42, -0.58), (0.72, -0.62)], [(0.16, -0.30), (0.46, -0.16), (0.78, -0.26)],
                  [(0.14, 0.16), (0.44, 0.28), (0.76, 0.16)], [(0.20, 0.60), (0.48, 0.70), (0.64, 0.58)]):
            gw = _wiggle(g, 0.05, 15, g[0][1] * 7)
            c.drawPath(path_from([(x + side * s * u, y + s * v) for u, v in gw], False, 0.8), P(hx(gr), stroke=s * 0.055))
        c.restore()
    if a < 1:
        c.restore()


def eye_open(c, x, y, s, a=1.0, look=0.0, lid=0.0):
    """big friendly open eye (almond, white, blue iris, pupil, highlight). lid 0 = wide open, 1 = closed"""
    if a <= 0:
        return
    c.saveLayerAlpha(None, int(255 * a))
    top = lerp(-0.62, 0.0, lid)
    al = path_from([(-1.0, 0.0), (-0.5, top * 0.92), (0.0, top), (0.5, top * 0.92), (1.0, 0.0), (0.5, 0.5), (0.0, 0.62),
                    (-0.5, 0.5)], True, 1.0)
    m = skia.Matrix(); m.setScale(s, s); m.postTranslate(x, y)
    al.transform(m)
    c.drawPath(al, P(hx("#fbf8ff")))
    c.save(); c.clipPath(al, doAntiAlias=True)
    ix = x + look * s * 0.25
    c.drawCircle(ix, y, s * 0.46, P(shader=rad(ix - s * 0.1, y - s * 0.12, s * 0.5, [hx("#7fd0ff"), hx("#2a78d8")])))
    c.drawCircle(ix, y, s * 0.46, P(hx("#1a4fa8"), stroke=s * 0.05))
    c.drawCircle(ix, y, s * 0.22, P(hx("#0e1236")))
    c.drawCircle(ix - s * 0.13, y - s * 0.15, s * 0.1, P(hx("#ffffff")))
    c.drawCircle(ix + s * 0.12, y + s * 0.1, s * 0.045, P(hx("#ffffff", 0.8)))
    # soft lid shadow at the top of the white
    c.drawPath(al, P(hx("#8a7fd6", 0.35), stroke=s * 0.16, blur=s * 0.05))
    c.restore()
    c.drawPath(al, P(hx("#1a1440"), stroke=s * 0.07))
    c.restore()


def dolphin(c, x, y, s, t, eye=0.0, a=1.0):
    """friendly bottlenose-style dolphin seen from the side, facing LEFT. (x, y) = body centre, s = half length.
    eye: 0 = closed (resting), 1 = open"""
    if a <= 0:
        return
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    c.save(); c.translate(x, y); c.scale(s, s)
    back, back_sh, belly = "#5f86e0", "#3d5cb8", "#d6e6ff"
    sw = 0.05 * math.sin(t * 2.2)
    body_pts = [(-1.00, 0.06), (-0.90, 0.02), (-0.80, -0.06), (-0.74, -0.16), (-0.60, -0.24), (-0.30, -0.29), (0.00, -0.27),
                (0.30, -0.20), (0.56, -0.12), (0.78, -0.05 + sw * 0.4), (0.90, 0.00 + sw), (0.80, 0.07 + sw * 0.6),
                (0.56, 0.12), (0.26, 0.20), (-0.10, 0.23), (-0.46, 0.20), (-0.72, 0.13), (-0.86, 0.10), (-0.98, 0.09)]
    body = path_from(body_pts, True, 1.0)
    # far-side flipper (behind the body)
    c.drawPath(path_from([(-0.40, 0.14), (-0.30, 0.34), (-0.24, 0.30), (-0.26, 0.14)], True, 0.8), P(hx(back_sh)))
    # tail flukes (behind the body)
    fy = sw
    fl = path_from([(0.84, 0.02 + fy), (0.98, -0.16 + fy * 1.4), (1.10, -0.20 + fy * 1.6), (1.04, -0.06 + fy * 1.3),
                    (0.98, 0.03 + fy), (1.06, 0.14 + fy * 1.3), (1.12, 0.26 + fy * 1.6), (0.98, 0.20 + fy * 1.4)], True, 0.7)
    c.drawPath(fl, P(hx(back_sh)))
    # dorsal fin
    fin = path_from([(-0.08, -0.26), (0.06, -0.46), (0.18, -0.58), (0.16, -0.44), (0.26, -0.20)], True, 0.8)
    c.drawPath(fin, P(hx(back_sh)))
    c.save(); c.clipPath(fin, doAntiAlias=True); c.translate(-0.03, -0.01)
    c.drawPath(path_from([(-0.08, -0.26), (0.06, -0.46), (0.16, -0.56), (0.10, -0.30)], True, 0.8), P(hx(back)))
    c.restore()
    # body: dark back, light belly (countershading), lit from the upper left
    c.drawPath(body, P(hx(back_sh)))
    c.save(); c.clipPath(body, doAntiAlias=True)
    c.save(); c.translate(-0.02, -0.035); c.drawPath(body, P(hx(back))); c.restore()
    bel = path_from([(-1.1, 0.07), (-0.80, 0.02), (-0.50, 0.06), (-0.10, 0.10), (0.30, 0.08), (0.60, 0.06), (0.95, 0.06),
                     (0.95, 0.4), (-1.1, 0.4)], True, 0.8)
    c.drawPath(bel, P(hx(belly)))
    c.drawPath(path_from([(-0.80, 0.02), (-0.50, 0.06), (-0.10, 0.10), (0.30, 0.08), (0.60, 0.06)], False, 0.8),
               P(hx("#a9c4f5"), stroke=0.018))
    # soft highlight along the back
    c.drawPath(path_from([(-0.62, -0.19), (-0.30, -0.24), (0.02, -0.22), (0.30, -0.16)], False, 0.8),
               P(hx("#9fbcff", 0.6), stroke=0.035))
    c.restore()
    # rim light on the upper edge
    c.drawPath(body, P(shader=lin(-0.8, -0.5, 0.3, 0.2, [hx("#cfe0ff", 0.8), hx("#cfe0ff", 0)]), stroke=0.016))
    # near-side flipper
    fp = path_from([(-0.46, 0.13), (-0.38, 0.30), (-0.30, 0.40), (-0.27, 0.33), (-0.30, 0.20), (-0.30, 0.13)], True, 0.8)
    c.drawPath(fp, P(hx(back_sh)))
    c.drawPath(fp, P(hx("#8fb0f5", 0.5), stroke=0.012))
    # mouth line (gentle smile)
    c.drawPath(path_from([(-0.97, 0.075), (-0.86, 0.075), (-0.78, 0.055)], False, 0.8), P(hx("#2c4590"), stroke=0.016))
    # eye
    ex, ey = -0.66, -0.06
    if eye > 0.5:
        c.drawCircle(ex, ey, 0.042, P(hx("#101436")))
        c.drawCircle(ex - 0.012, ey - 0.014, 0.014, P(hx("#ffffff")))
    else:
        c.drawPath(path_from([(ex - 0.045, ey - 0.005), (ex, ey + 0.025), (ex + 0.045, ey - 0.005)], False, 0.8),
                   P(hx("#101436"), stroke=0.018))
    # blowhole
    c.drawPath(path_from([(-0.44, -0.265), (-0.40, -0.275)], False), P(hx("#2c4590"), stroke=0.012))
    c.restore()
    if a < 1:
        c.restore()


# ---------------------------------------------------------------- episode 004 additions (planetary rings)
# ring bands from the outer edge inward: (u0, u1, colour, alpha) as fractions of the ring width
RING_BANDS = [(0.00, 0.06, "#b9a9d6", 0.45), (0.06, 0.26, "#dcc9a6", 0.80), (0.26, 0.31, None, 0.0),
              (0.31, 0.50, "#f2dfb8", 0.92), (0.50, 0.74, "#e2c48f", 0.85), (0.74, 1.00, "#a693c9", 0.40)]


def _arc(rect, a0, sweep):
    p = skia.Path()
    p.addArc(rect, a0, sweep)
    return p


def ring_arch(c, t, cx, cy, rx, ry, w, a=1.0, grow=1.0, shine=0.0, sparkles=1.0, glow_k=1.0):
    """A planetary ring seen from the ground: an elliptical arch (upper half of an ellipse centred on (cx, cy),
    normally just below the horizon). w = band width in px. grow 0..1 sweeps it in from the left horizon.
    Works from a thin vertical line (rx ~ w) to a wide rainbow arch."""
    if a <= 0 or grow <= 0:
        return
    sweep = 180 * grow
    for (u0, u1, col, al) in RING_BANDS:
        if col is None:
            continue
        um = (u0 + u1) / 2
        d = um * w
        rr = skia.Rect.MakeLTRB(cx - rx + d, cy - ry + d, cx + rx - d, cy + ry - d)
        bw = max(1.0, (u1 - u0) * w)
        c.drawPath(_arc(rr, 180, sweep), P(hx(col, al * a * (0.85 + 0.15 * shine)), stroke=bw, cap=False))
    # fine ringlet lines for texture (darker grooves inside the bright bands)
    for k in range(9):
        u = 0.08 + k * 0.075
        if 0.25 < u < 0.33:
            continue
        d = u * w
        rr = skia.Rect.MakeLTRB(cx - rx + d, cy - ry + d, cx + rx - d, cy + ry - d)
        c.drawPath(_arc(rr, 180, sweep), P(hx("#8a74b8", 0.22 * a), stroke=max(1.0, w * 0.012), cap=False))
    # soft additive ringshine around the band
    d = 0.45 * w
    rr = skia.Rect.MakeLTRB(cx - rx + d, cy - ry + d, cx + rx - d, cy + ry - d)
    c.drawPath(_arc(rr, 180, sweep), P(hx("#ffd99a", (0.06 + 0.07 * shine) * a * glow_k), stroke=w * 1.8, blur=w * 0.5, cap=False,
                                       mode=skia.BlendMode.kPlus))
    # glints of sunlight travelling along the ring (particles orbiting)
    if sparkles > 0:
        rnd = random.Random(5)
        for k in range(10):
            ph = (rnd.uniform(0, 1) + t * rnd.uniform(0.025, 0.05)) % 1
            ang = math.radians(180 + 180 * ph)
            if 180 * ph > sweep:
                continue
            u = rnd.uniform(0.1, 0.7)
            x = cx + (rx - u * w) * math.cos(ang)
            y = cy + (ry - u * w) * math.sin(ang)
            tw = 0.5 + 0.5 * math.sin(t * rnd.uniform(2, 4) + k)
            sparkle(c, x, y, max(2.0, w * 0.045) * (0.7 + 0.5 * tw), "#fff6dc", 0.85 * a * sparkles * tw, t * 20 + k * 30)
    # growing tip
    if grow < 1:
        ang = math.radians(180 + sweep)
        x = cx + (rx - 0.45 * w) * math.cos(ang)
        y = cy + (ry - 0.45 * w) * math.sin(ang)
        glow(c, x, y, w * 0.55, "#fff1c8", 0.9 * a, 2.4)
        sparkle(c, x, y, w * 0.12, "#ffffff", a, t * 90)


def _ring_rects(r, rin, rout, ry_k):
    out = []
    for (u0, u1, col, al) in RING_BANDS:
        if col is None:
            continue
        um = (u0 + u1) / 2
        rr = lerp(rout, rin, um) * r
        out.append((rr, (u1 - u0) * (rout - rin) * r, col, al))
    return out


def _arc_pieces(a0, a1, h0, h1):
    """intersection of the angle interval [a0, a1] (any range, may exceed 360) with the half [h0, h1] (0..360)"""
    res = []
    for off in (-720, -360, 0, 360, 720):
        lo, hi = max(a0, h0 + off), min(a1, h1 + off)
        if hi > lo:
            res.append((lo, hi - lo))
    return res


def planet_ring(c, cx, cy, r, tilt, front, a=1.0, t=0.0, rin=1.35, rout=2.2, ry_k=0.2, span=(0, 360), shadow=True,
                light=(-0.75, -0.45), thin=1.0):
    """Saturn-style ring around a planet in its equatorial plane. Draw front=False BEFORE planet(), front=True after.
    span = (a0, a1) degrees of ring that exists (for a ring forming from debris). thin 0..1 fades the bands."""
    if a <= 0:
        return
    c.save(); c.translate(cx, cy); c.rotate(tilt)
    h0, h1 = (0, 180) if front else (179.7, 360.3)   # back half overlaps a hair so the tips show no seam
    full = span[1] - span[0] >= 359.9
    if span[1] - span[0] > 360:
        m_ = (span[0] + span[1]) / 2
        span = (m_ - 180, m_ + 180)
    pieces = _arc_pieces(span[0], span[1], h0, h1)
    if not pieces:
        c.restore(); return
    band = skia.Path()
    for (rr, bw, col, al) in _ring_rects(r, rin, rout, ry_k):
        rect = skia.Rect.MakeXYWH(-rr, -rr * ry_k, 2 * rr, 2 * rr * ry_k)
        for (s0, sw) in pieces:
            if full:
                c.drawPath(_arc(rect, s0, sw), P(hx(col, al * a * thin), stroke=bw, cap=False))
                continue
            # fade toward the open ends of a forming ring: alpha follows the angle via a sweep gradient
            cols, pos = [], []
            for j in range(73):
                ang = j * 5.0
                f = 0.0
                for off in (-360, 0, 360):
                    aa = ang + off
                    if span[0] <= aa <= span[1]:
                        f = max(f, smooth(clamp(min(aa - span[0], span[1] - aa) / 50.0)))
                cols.append(hx(col, al * a * thin * f))
                pos.append(j / 72)
            sh = skia.GradientShader.MakeSweep(0, 0, cols, pos, localMatrix=skia.Matrix.Scale(1, ry_k))
            c.drawPath(_arc(rect, s0, sw), P(shader=sh, stroke=bw, cap=False))
    # ringlet grooves
    for k in range(8):
        u = 0.1 + k * 0.1
        if 0.24 < u < 0.33:
            continue
        rr = lerp(rout, rin, u) * r
        rect = skia.Rect.MakeXYWH(-rr, -rr * ry_k, 2 * rr, 2 * rr * ry_k)
        if not full:
            continue
        for (s0, sw) in pieces:
            c.drawPath(_arc(rect, s0, sw), P(hx("#7d68ae", 0.25 * a * thin), stroke=max(1.0, r * 0.006), cap=False))
    # the planet's shadow falls across the far side of the ring, away from the sun
    if shadow and not front:
        ring_area = skia.Path()
        ring_area.addOval(skia.Rect.MakeXYWH(-rout * r * 1.02, -rout * r * ry_k * 1.02, 2 * rout * r * 1.02, 2 * rout * r * ry_k * 1.02))
        hole = skia.Path()
        hole.addOval(skia.Rect.MakeXYWH(-rin * r * 0.98, -rin * r * ry_k * 0.98, 2 * rin * r * 0.98, 2 * rin * r * ry_k * 0.98))
        ring_area = skia.Op(ring_area, hole, skia.PathOp.kDifference_PathOp)
        top = skia.Path(); top.addRect(skia.Rect.MakeLTRB(-rout * r * 1.1, -rout * r, rout * r * 1.1, 0))
        ring_area = skia.Op(ring_area, top, skia.PathOp.kIntersect_PathOp)
        c.save(); c.clipPath(ring_area, doAntiAlias=True)
        tr = math.radians(-tilt)
        lx, ly = light
        llx = lx * math.cos(tr) - ly * math.sin(tr)
        sx = 1 if llx < 0 else -1  # shadow points away from the sun along the ring plane
        x0, x1 = sx * r * 0.7, sx * r * 1.75
        c.drawRect(skia.Rect.MakeLTRB(min(0, x1), -r * 0.62, max(0, x1), r * 0.62),
                   P(shader=lin(x0, 0, x1, 0, [hx("#0a0b30", 0.62 * a), hx("#0a0b30", 0)])))
        c.restore()
    c.restore()


def chunk_path(s, seed, n=8):
    rnd = random.Random(seed)
    pts = []
    for k in range(n):
        ang = 2 * math.pi * k / n + rnd.uniform(-0.25, 0.25)
        rr = s * rnd.uniform(0.72, 1.0)
        pts.append((rr * math.cos(ang), rr * math.sin(ang) * rnd.uniform(0.8, 1.0)))
    return path_from(pts, True, 0.22)


def ring_chunk(c, x, y, s, rot, seed, ice=1.0, a=1.0, shine=0.0, light=(-0.75, -0.55)):
    """one ring particle: ice (pale blue, glinting) when ice=1, sunlit rock (warm grey-tan, pitted) when ice=0.
    Two-tone flat shading lit from the upper left + a thin rim light."""
    if a <= 0 or s < 1:
        return
    lit = mixhex("#c9a98a", "#e6f4ff", ice)
    shade = mixhex("#5e4a63", "#6f8fd6", ice)
    mid = mixhex("#957a78", "#a9c8f2", ice)
    rim = mixhex("#ffe2b0", "#ffffff", ice)
    c.save(); c.translate(x, y)
    pth = chunk_path(s, seed)
    c.rotate(rot)
    c.saveLayerAlpha(None, int(255 * clamp(a)))
    c.drawPath(pth, P(hx(shade)))
    c.save(); c.clipPath(pth, doAntiAlias=True)
    tr = math.radians(-rot)
    lx, ly = light
    llx, lly = lx * math.cos(tr) - ly * math.sin(tr), lx * math.sin(tr) + ly * math.cos(tr)
    c.save(); c.translate(llx * s * 0.42, lly * s * 0.42); c.drawPath(pth, P(hx(mid))); c.restore()
    c.save(); c.translate(llx * s * 0.75, lly * s * 0.75); c.drawPath(pth, P(hx(lit))); c.restore()
    rnd = random.Random(seed * 7 + 1)
    # rock: a few soft pits; ice: a couple of bright facets
    for k in range(2):
        px, py, pr = rnd.uniform(-0.4, 0.4) * s, rnd.uniform(-0.4, 0.4) * s, rnd.uniform(0.07, 0.13) * s
        c.drawOval(skia.Rect.MakeXYWH(px - pr * 1.2, py - pr, pr * 2.4, pr * 2), P(hx(mixhex("#7a6068", "#9fc0ee", ice), 0.40 * (1 - ice))))
    # a darker facet on the shadow side makes it read as a solid rock, not a disc
    fct = path_from([(0.05 * s, -0.15 * s), (0.9 * s, 0.1 * s), (0.5 * s, 0.9 * s), (-0.3 * s, 0.6 * s)], True)
    c.drawPath(fct, P(hx(mixhex("#4a3a52", "#5f7fc8", ice), 0.35)))
    if ice > 0:
        f = path_from([(-0.1 * s, -0.5 * s), (0.25 * s, -0.2 * s), (0.0, 0.1 * s), (-0.35 * s, -0.15 * s)], True)
        c.drawPath(f, P(hx("#ffffff", 0.35 * ice)))
    # rim light on the sunlit edge
    sh_p = skia.Path(pth); sh_p.offset(-llx * s * 0.10, -lly * s * 0.10)
    rim_reg = skia.Op(pth, sh_p, skia.PathOp.kDifference_PathOp)
    if rim_reg:
        c.drawPath(rim_reg, P(hx(rim, 0.75 + 0.25 * shine)))
    c.restore()
    c.restore()
    c.restore()
    if ice > 0.3:
        tw = 0.5 + 0.5 * math.sin(seed * 3.1 + rot * 0.05)
        sparkle(c, x + light[0] * s * 0.45, y + light[1] * s * 0.45, s * 0.09 * ice, "#ffffff", 0.9 * ice * tw, 15)


ANCIENT_LAND = {
    "laurentia": [(-66, 8), (-58, 22), (-44, 26), (-30, 20), (-16, 22), (-12, 8), (-18, -6), (-26, -16), (-42, -19), (-50, -10), (-62, -6)],
    "baltica": [(-10, -20), (4, -17), (18, -22), (24, -34), (14, -44), (0, -48), (-12, -40), (-8, -30)],
    "siberia": [(26, 6), (32, 20), (44, 28), (58, 22), (62, 10), (54, -2), (40, -6), (30, -2)],
    "gondwana": [(-100, -60), (-80, -44), (-60, -50), (-40, -46), (-24, -56), (-4, -60), (16, -54), (30, -40), (38, -26),
                 (50, -14), (62, -6), (74, 4), (88, 6), (100, 0), (110, -14), (104, -30), (112, -44), (90, -58), (60, -72),
                 (0, -84), (-60, -82), (-110, -74)],
}
# 21 craters, all within 30 degrees of the ancient equator (Tomkins et al. 2024), placed on land
ANCIENT_CRATERS = [(-48, 4), (-38, 14), (-30, -4), (-44, -8), (-26, 6), (-50, -2),
                   (-6, -26), (6, -25), (12, -29),
                   (36, 4), (44, 16), (48, 6), (40, -1),
                   (64, -12), (74, -4), (86, -2), (94, -10), (82, -18), (58, -22), (70, -26), (50, -28)]


def _dense_ll(poly, step=4.0):
    out = []
    for i in range(len(poly)):
        (a0, b0), (a1, b1) = poly[i], poly[(i + 1) % len(poly)]
        n = max(1, int(math.hypot(a1 - a0, b1 - b0) / step))
        for k in range(n):
            out.append((lerp(a0, a1, k / n), lerp(b0, b1, k / n)))
    return out


def _coast(poly, seed):
    """densify and roughen a lon/lat outline into a natural coastline (bays, capes)"""
    pts = _dense_ll(poly, 2.0)
    n = len(pts)
    out = []
    for i, (lo, la) in enumerate(pts):
        (a0, b0), (a1, b1) = pts[i - 1], pts[(i + 1) % n]
        tx, ty = a1 - a0, b1 - b0
        d = math.hypot(tx, ty) or 1
        nx_, ny_ = ty / d, -tx / d
        u = i / n * 2 * math.pi
        k = 3.2 * math.sin(u * 5 + seed) + 1.8 * math.sin(u * 11 + seed * 2.3) + 0.9 * math.sin(u * 23 + seed * 0.7)
        out.append((lo + nx_ * k, la + ny_ * k))
    return out


ANCIENT_D = {k: _coast(v, 1.3 + i * 2.1) for i, (k, v) in enumerate(ANCIENT_LAND.items())}


def ll_xy(r, lon, lat, lon0, elev=0.0):
    """orthographic globe point for (lon, lat) seen from `elev` degrees above the equator plane -> (x, y, z), z>0 = visible"""
    lam = math.radians(lon - lon0)
    ph = math.radians(lat)
    e = math.radians(elev)
    x0 = math.cos(ph) * math.sin(lam)
    y0 = -math.sin(ph)
    z0 = math.cos(ph) * math.cos(lam)
    y = y0 * math.cos(e) + z0 * math.sin(e)
    z = -y0 * math.sin(e) + z0 * math.cos(e)
    return r * x0, r * y, z


def proj_e(poly, r, lon0, elev):
    out, vis = [], False
    for lon, lat in poly:
        x, y, z = ll_xy(r, lon, lat, lon0, elev)
        if z < 0:
            d = math.hypot(x, y) or 1
            x, y = x / d * r * 1.02, y / d * r * 1.02
        else:
            vis = True
        out.append((x, y))
    return out, vis


def lat_arc(r, lat, lon0, elev, n=72):
    """visible (front) arc of a latitude circle, left limb -> right limb, as points; [] if hidden"""
    e = math.radians(elev)
    ph = math.radians(lat)
    k = -math.tan(ph) * math.tan(e) if abs(math.cos(ph)) > 1e-6 else 2
    if k >= 1:
        return []
    lam_max = math.pi if k <= -1 else math.acos(k)
    pts = []
    for i in range(n + 1):
        lam = -lam_max + 2 * lam_max * i / n
        x, y, z = ll_xy(r, lon0 + math.degrees(lam), lat, lon0, elev)
        pts.append((x, y))
    return pts


def lat_cap_path(r, lat, lon0, elev, north=True):
    """region of the visible disc poleward of `lat` (north=True: lat..90, else -90..lat)"""
    full = []
    for i in range(145):
        lon = lon0 - 180 + 360 * i / 144
        x, y, z = ll_xy(r, lon, lat, lon0, elev)
        full.append((x, y, z))
    pole = ll_xy(r, 0, 90 if north else -90, lon0, elev)
    if all(p[2] >= 0 for p in full):  # whole circle visible: a filled ellipse
        return path_from([(p[0], p[1]) for p in full[:-1]], True)
    arc = lat_arc(r, lat, lon0, elev)
    if not arc:
        return None
    # close along the limb on the pole's side
    (xa, ya), (xb, yb) = arc[0], arc[-1]
    a0 = math.atan2(yb, xb)
    a1 = math.atan2(ya, xa)
    side = -1 if north else 1  # north cap closes over the top (negative y)
    pts = list(arc)
    # walk the limb from the right end back to the left end through the pole's side
    if side < 0:
        if a1 < a0:
            a1 += 2 * math.pi
        sweep = a1 - a0
        if sweep > 0 and math.sin(a0 + sweep / 2) > 0:
            sweep -= 2 * math.pi
    else:
        if a1 > a0:
            a1 -= 2 * math.pi
        sweep = a1 - a0
        if math.sin(a0 + sweep / 2) < 0:
            sweep += 2 * math.pi
    for i in range(1, 40):
        an = a0 + sweep * i / 40
        pts.append((r * 1.02 * math.cos(an), r * 1.02 * math.sin(an)))
    return path_from(pts, True)


def ancient_earth(c, cx, cy, r, lon0, t, elev=14.0, ice=0.0, light=(-0.75, -0.45), atmo=1.0):
    """Earth about 466 million years ago: one big southern supercontinent and small land masses near the equator,
    seen from `elev` degrees above the equator plane (so a ring with ry_k = sin(elev) lines up with it).
    ice 0..1 grows the polar ice caps toward the mid latitudes."""
    lx, ly = light
    atmo_c = "#5fd0ff"
    if atmo > 0:
        c.drawCircle(cx, cy, r * 1.22, P(shader=rad(cx, cy, r * 1.22, [hx(atmo_c, 0.0), hx(atmo_c, 0.0), hx(atmo_c, 0.35 * atmo), hx(atmo_c, 0)], [0, 0.78, 0.84, 1])))
    c.save(); c.translate(cx, cy)
    c.clipPath(circ_path(0, 0, r), doAntiAlias=True)
    c.drawCircle(0, 0, r, P(shader=rad(lx * r * 0.45, ly * r * 0.45, r * 1.5, [hx("#2a8fe6"), hx("#1450b4")], [0, 1])))
    c.drawCircle(lx * r * 0.35, ly * r * 0.35, r * 0.55, P(hx("#59b8ff", 0.10), blur=r * 0.15))
    paths = []
    for name, poly in ANCIENT_D.items():
        pts, vis = proj_e(poly, r, lon0, elev)
        if vis:
            paths.append(path_from(pts, True, 0.3))
    for pth in paths:
        c.drawPath(pth, P(hx("#6cd3ff", 0.35), stroke=r * 0.05))
        c.drawPath(pth, P(hx("#9ae6ff", 0.35), stroke=r * 0.022))
    for pth in paths:  # bare land (plants had barely reached land yet): ochre with olive patches
        c.drawPath(pth, P(hx("#c99a5b")))
    for pth in paths:
        c.save(); c.clipPath(pth, doAntiAlias=True)
        c.drawCircle(-lx * r * 0.2, -ly * r * 0.2, r * 0.9, P(hx("#8fa35a", 0.45), blur=r * 0.25))
        c.restore()
    # polar ice caps
    L = lerp(74, 40, ice)
    for north in (True, False):
        cp = None
        if north and elev > 0 and L > elev + 6:
            ring_pts = [(lon0 - 180 + 360 * i / 120, L + (1.5 + 3.0 * ice) * math.sin(math.radians(360 * i / 120) * 7 + 1.0)
                         + (0.8 + 1.5 * ice) * math.sin(math.radians(360 * i / 120) * 13)) for i in range(120)]
            ring_pts = [(lo - (lon0 - 180) + lon0 - 180, la) for lo, la in ring_pts]
            pp, vis = proj_e(ring_pts, r, lon0, elev)
            cp = path_from(pp, True, 0.4)
        if cp is None:
            cp = lat_cap_path(r, L if north else -L, lon0, elev, north)
        if cp is not None:
            c.drawPath(cp, P(hx("#eef8ff")))
            if ice > 0:
                arc = lat_arc(r, L if north else -L, lon0, elev)
                if arc:
                    c.drawPath(path_from(arc, False), P(hx("#bfe6ff", 0.8 * ice), stroke=r * 0.012))
    # clouds
    for (lo, la, s) in [(-60, 35, 1.0), (15, 48, 1.2), (80, 25, 0.9), (150, 40, 1.1), (-130, -20, 1.0), (30, -12, 0.9),
                        (-10, 30, 0.8), (110, -45, 1.0), (-100, 50, 0.9), (-35, -38, 0.8)]:
        lo2 = lo + t * 5
        x, y, z = ll_xy(r, lo2, la, lon0, elev)
        if z <= 0.08:
            continue
        sq = max(0.15, math.cos(math.radians(lo2 - lon0)))
        c.save(); c.translate(x, y); c.scale(sq, 1)
        w, h = r * 0.30 * s, r * 0.066 * s
        for paint, ox, oy in ((P(hx("#0b2f7a", 0.18)), r * 0.02, r * 0.03), (P(hx("#ffffff", 0.9)), 0, 0)):
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2 + ox, -h / 2 + oy, w, h), h / 2, h / 2), paint)
            c.drawCircle(-w * 0.12 + ox, -h * 0.45 + oy, h * 0.75, paint)
            c.drawCircle(w * 0.14 + ox, -h * 0.35 + oy, h * 0.55, paint)
        c.restore()
    c.restore()
    planet_shade(c, cx, cy, r, light)
    c.save(); c.translate(cx, cy)
    ang = math.degrees(math.atan2(ly, lx))
    c.drawPath(_arc(skia.Rect.MakeXYWH(-r, -r, 2 * r, 2 * r), ang - 55, 110), P(hx(atmo_c, 0.55 * atmo), stroke=r * 0.025, blur=r * 0.01))
    c.restore()


def lat_band_path(r, lat0, lat1, lon0, elev):
    """visible region between two latitudes (lat0 < lat1) as a path in globe-centred coordinates"""
    top = lat_arc(r, lat1, lon0, elev)
    bot = lat_arc(r, lat0, lon0, elev)
    if not top or not bot:
        return None
    return path_from(top + list(reversed(bot)), True)


def crater_mark(c, x, y, s, sq, a, marker=0.0):
    """small impact crater seen on a globe (squashed by sq toward the limb); marker draws a locator ring"""
    if a <= 0:
        return
    c.save(); c.translate(x, y); c.scale(sq, 1)
    c.drawCircle(0, 0, s * 1.3, P(hx("#f6e2b8", 0.95 * a)))
    c.drawCircle(0, 0, s, P(hx("#6b4a3a", a)))
    c.drawCircle(s * 0.22, s * 0.22, s * 0.7, P(hx("#8a6248", a)))
    if marker > 0:
        c.drawCircle(0, 0, s * 2.3, P(hx("#ffd84d", 0.9 * a * marker), stroke=max(2.0, s * 0.28)))
    c.restore()


def snowflake(c, x, y, s, col="#bfe8ff", a=1.0, rot=0.0):
    if a <= 0:
        return
    c.save(); c.translate(x, y); c.rotate(rot)
    for k in range(6):
        c.save(); c.rotate(k * 60)
        pp = P(hx(col, a), stroke=s * 0.2)
        c.drawLine(0, 0, 0, -s, pp)
        c.drawLine(0, -s * 0.62, -s * 0.3, -s * 0.92, pp); c.drawLine(0, -s * 0.62, s * 0.3, -s * 0.92, pp)
        c.restore()
    c.restore()


def pill(c, x, y, label, a=1.0, size=40, col="#1a1f55", txt="#ffffff", icon=None, icon_w=0):
    """rounded label badge centred at (x, y); icon(c, cx, cy) draws a small icon at the left"""
    if a <= 0:
        return
    w = measure(label, size, TF_POP_XB) + 64 + icon_w
    h = size * 1.75
    x0 = x - w / 2
    rrect(c, x0, y - h / 2 + 8, w, h, h / 2, P(hx("#03051a", 0.35 * a), blur=14))
    rrect(c, x0, y - h / 2, w, h, h / 2, P(hx(col, 0.95 * a)))
    rrect(c, x0, y - h / 2, w, h, h / 2, P(hx("#ffffff", 0.14 * a), stroke=3))
    if icon:
        icon(c, x0 + 32 + icon_w / 2 - 6, y)
    text(c, label, x0 + 32 + icon_w, y + size * 0.36, size, txt, a, TF_POP_XB, align="left")
