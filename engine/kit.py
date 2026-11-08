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


def pine(c, x, y, s, col, rim, rim_a):
    for k in range(3):
        w = s * (0.9 - k * 0.22)
        yy = y - k * s * 0.55
        pth = path_from([(x - w / 2, yy), (x, yy - s * 0.8), (x + w / 2, yy)], True)
        c.drawPath(pth, P(hx(col)))
        if rim_a > 0:
            c.drawLine(x, yy - s * 0.8, x + w / 2, yy, P(hx(rim, rim_a * 0.8), stroke=3))
    c.drawRect(skia.Rect.MakeXYWH(x - s * 0.06, y, s * 0.12, s * 0.18), P(hx(col)))


def house(c, x, y, t, m, win=1.0, sc=0.92):
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
        sx = x + (69 + ph * 60 + math.sin(ph * 6 + k) * 10) * sc
        sy = y + (-186 - ph * 170) * sc
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


def landscape(c, t, moon_s=1.0, m=1.0, ghost=0.0, flash=None, cam_y=0.0, cam_z=1.0, sparkle_p=None, shoot=None):
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
    # flat clouds drifting (lit from the moon)
    for k, (cx0, cy0, sc, sp) in enumerate([(160, 300, 1.0, 9), (980, 785, 1.1, 6), (420, 170, 0.75, 11)]):
        x = (cx0 + t * sp) % (W + 500) - 250
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
    for k in range(4):
        yy = lake_top + 40 + k * 38
        c.drawLine(120 + k * 60, yy, 260 + k * 60, yy, P(hx("#7d73d6", 0.25 * m), stroke=3))
    # little rowboat with a fisherman and a lantern
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
    house(c, hx_, 1472, t, m)
    for (px, s_) in [(90, 130), (190, 95), (290, 75), (380, 60), (1010, 105)]:
        pine(c, px, near_y(px) + 10, s_, mixhex("#0c0a2c", "#151249", m), rim, 0.6 * m)
    # foreground
    hill(c, 1700, [(40, 0.005, 1.0), (12, 0.03, 0.5)], mixhex("#080720", "#0f0d33", m))
    for (px, s) in [(60, 200), (1070, 230)]:
        pine(c, px, 1720, s, mixhex("#05041a", "#0a0928", m), rim, 0.35 * m)
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


def branch(c, x, y, ang, L, w, depth, col, sway, tips):
    x2 = x + math.cos(math.radians(ang)) * L
    y2 = y + math.sin(math.radians(ang)) * L
    c.drawLine(x, y, x2, y2, P(hx(col), stroke=w))
    if depth == 0:
        c.drawCircle(x2, y2, w * 0.62, P(hx("#ffd0e6", 0.9)))
        tips.append((x2, y2))
        return
    for da in (-26, 24):
        branch(c, x2, y2, ang + da + sway, L * 0.72, w * 0.78, depth - 1, col, sway, tips)


def fish(c, x, y, s, col, flip, t, k):
    c.save(); c.translate(x, y); c.scale(-s if flip else s, s)
    wag = 8 * math.sin(t * 9 + k)
    c.drawPath(path_from([(-30, 0), (-52, -16 + wag * 0.4), (-52, 16 + wag * 0.4)], True), P(hx(col)))
    c.drawOval(skia.Rect.MakeXYWH(-36, -20, 66, 40), P(hx(col)))
    c.drawOval(skia.Rect.MakeXYWH(-6, -20, 20, 40), P(hx("#ffffff", 0.85)))
    c.drawCircle(16, -5, 5, P(hx("#140f38")))
    c.restore()


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


def hand(c, x, y, a):
    """Simple flat mitten hand pointing down, fingertip at (x, y)."""
    c.save(); c.translate(x, y)
    skin = hx("#f2b48c", a)
    rrect(c, -40, -150, 80, 120, 34, P(skin))          # palm
    rrect(c, -14, -60, 28, 66, 14, P(skin))            # index finger down
    rrect(c, -52, -132, 30, 70, 15, P(hx("#e9a37b", a)))  # thumb
    rrect(c, -44, -230, 88, 90, 20, P(hx("#4a7bff", a)))  # sleeve
    rrect(c, -50, -150, 100, 20, 10, P(hx("#3a63d8", a)))
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
