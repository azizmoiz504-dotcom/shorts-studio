"""Drawing toolkit for the flat, glowing space-explainer look (original art)."""
import math, random
import numpy as np
import skia

W, H = 1080, 1920
import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
FONT_DIR = _os.path.join(ROOT, "fonts") + "/"
TF_BLACK = skia.Typeface.MakeFromFile(FONT_DIR + "InterDisplay-Black.otf")
TF_BOLD = skia.Typeface.MakeFromFile(FONT_DIR + "InterDisplay-Bold.otf")
TF_SEMI = skia.Typeface.MakeFromFile(FONT_DIR + "InterDisplay-SemiBold.otf")
POP = FONT_DIR
TF_POP_B = skia.Typeface.MakeFromFile(POP + "Poppins-Bold.ttf")
TF_POP_SB = skia.Typeface.MakeFromFile(POP + "Poppins-SemiBold.ttf")
TF_POP_XB = skia.Typeface.MakeFromFile(POP + "Poppins-ExtraBold.ttf")
TF_POP_M = skia.Typeface.MakeFromFile(POP + "Poppins-Medium.ttf")


# ---------------------------------------------------------------- math
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def seg(t, a, b):
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_io(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = clamp(x)
    return x ** 3


def ease_out_back(x, s=1.70158):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def ease_in_back(x, s=1.70158):
    x = clamp(x)
    return (s + 1) * x ** 3 - s * x ** 2


def pop(t, t0, dur=0.35):
    """0 -> 1 with overshoot, for things popping into view."""
    return ease_out_back(seg(t, t0, t0 + dur), 2.2)


def wave(t, f=1.0, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


# ---------------------------------------------------------------- colour
def hx(h, a=1.0):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return skia.ColorSetARGB(int(clamp(a) * 255), r, g, b)


def rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def mix(h1, h2, t, a=1.0):
    c = rgb(h1) * (1 - t) + rgb(h2) * t
    return skia.ColorSetARGB(int(clamp(a) * 255), *[int(round(v)) for v in c])


def mixhex(h1, h2, t):
    c = rgb(h1) * (1 - t) + rgb(h2) * t
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in c)


def P(color=None, shader=None, stroke=0, blur=0, alpha=None, cap=True, mode=None):  # noqa
    p = skia.Paint(AntiAlias=True)
    if color is not None:
        p.setColor(color)
    if shader is not None:
        p.setShader(shader)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        if cap:
            p.setStrokeCap(skia.Paint.kRound_Cap)
            p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if alpha is not None:
        p.setAlphaf(clamp(alpha) * p.getAlphaf())
    if mode is not None:
        p.setBlendMode(mode)
    return p


def lin(x0, y0, x1, y1, cols, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)], cols, pos)


def rad(cx, cy, r, cols, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(cx, cy), max(r, 0.01), cols, pos)


# ---------------------------------------------------------------- primitives
def circle(c, x, y, r, p):
    if r > 0:
        c.drawCircle(x, y, r, p)


def glow(c, x, y, r, col, a=1.0, spread=2.2):
    """Soft additive-looking halo."""
    if r <= 0 or a <= 0:
        return
    c.drawCircle(x, y, r * spread, P(shader=rad(x, y, r * spread, [hx(col, 0.55 * a), hx(col, 0.18 * a), hx(col, 0)], [0, 0.45, 1])))


def path_from(pts, closed=True, smooth_k=0.0):
    p = skia.Path()
    if not pts:
        return p
    if smooth_k <= 0:
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
    else:  # Catmull-Rom through points
        n = len(pts)
        p.moveTo(*pts[0])
        rng = range(n) if closed else range(n - 1)
        for i in rng:
            p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
            p1 = pts[i]
            p2 = pts[(i + 1) % n]
            p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
            k = smooth_k / 6
            c1 = (p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k)
            c2 = (p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k)
            p.cubicTo(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    if closed:
        p.close()
    return p


def circ_path(x, y, r):
    p = skia.Path()
    p.addCircle(x, y, r)
    return p


def dashed(c, path, p, on=18, off=14, phase=0):
    p.setPathEffect(skia.DashPathEffect.Make([on, off], phase))
    c.drawPath(path, p)


def text(c, s, x, y, size, col, a=1.0, tf=None, align="center", shadow=0.0, track=0.0):
    tf = tf or TF_BLACK
    f = skia.Font(tf, size)
    f.setSubpixel(True)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    if track:
        wtot = sum(f.measureText(ch) for ch in s) + track * (len(s) - 1)
    else:
        wtot = f.measureText(s)
    if align == "center":
        x0 = x - wtot / 2
    elif align == "right":
        x0 = x - wtot
    else:
        x0 = x
    def draw(paint, dx=0, dy=0):
        if track:
            xx = x0
            for ch in s:
                c.drawString(ch, xx + dx, y + dy, f, paint)
                xx += f.measureText(ch) + track
        else:
            c.drawString(s, x0 + dx, y + dy, f, paint)
    if shadow > 0:
        draw(P(hx("#05061a", 0.55 * a * shadow), blur=size * 0.12), 0, size * 0.06)
    draw(P(hx(col, a) if isinstance(col, str) else col))
    return wtot


def measure(s, size, tf=None):
    return skia.Font(tf or TF_BLACK, size).measureText(s)


# ---------------------------------------------------------------- stars
class Stars:
    def __init__(self, n=260, seed=3, region=(0, 0, W, H)):
        rnd = random.Random(seed)
        x0, y0, x1, y1 = region
        self.s = []
        for _ in range(n):
            size = rnd.choice([1.4, 1.8, 2.2, 2.6, 3.2, 4.2]) * (1.4 if rnd.random() < 0.06 else 1)
            col = rnd.choice(["#ffffff", "#ffffff", "#fff0c2", "#bfe0ff", "#d9ccff"])
            self.s.append((rnd.uniform(x0, x1), rnd.uniform(y0, y1), size, rnd.uniform(0, 6.28), rnd.uniform(0.3, 1.2), col, rnd.random() < 0.08))

    def draw(self, c, t, a=1.0, dx=0, dy=0, par=1.0):
        if a <= 0:
            return
        for (x, y, sz, ph, f, col, big) in self.s:
            tw = 0.65 + 0.35 * math.sin(t * f * 2.4 + ph)
            xx, yy = x + dx * par * (sz / 3), y + dy * par * (sz / 3)
            if big:
                al = a * tw
                c.drawCircle(xx, yy, sz * 3.2, P(hx(col, 0.18 * al), blur=sz * 2))
                pt = P(hx(col, 0.85 * al), stroke=1.6)
                L = sz * 3.0 * (0.8 + 0.2 * tw)
                c.drawLine(xx - L, yy, xx + L, yy, pt)
                c.drawLine(xx, yy - L, xx, yy + L, pt)
            c.drawCircle(xx, yy, sz * 0.5 * (0.85 + 0.25 * tw), P(hx(col, a * tw)))


# ---------------------------------------------------------------- planets
def chaikin(poly, it=3):
    for _ in range(it):
        out = []
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            out.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            out.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        poly = out
    return poly


def _dense(poly, step=3.0):
    poly = chaikin(poly, 3)
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        d = max(abs(b[0] - a[0]), abs(b[1] - a[1]))
        k = max(1, int(d / step))
        for j in range(k):
            out.append((a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k))
    return out


CONTINENTS = {
    "africa": [(-17, 15), (-10, 30), (10, 36), (32, 31), (43, 12), (51, 11), (40, -5), (40, -15), (33, -26), (20, -35), (12, -18), (9, -2), (-5, 5)],
    "europe": [(-10, 36), (-9, 43), (-2, 48), (5, 51), (10, 55), (20, 58), (30, 62), (40, 65), (45, 55), (40, 45), (28, 41), (20, 40), (12, 44), (5, 43)],
    "asia": [(40, 45), (45, 55), (40, 66), (60, 70), (90, 75), (130, 72), (160, 68), (178, 65), (160, 60), (140, 50), (130, 40), (122, 30), (110, 20), (105, 10), (100, 15), (90, 22), (80, 9), (72, 20), (60, 25), (50, 28), (45, 35)],
    "arabia": [(35, 30), (48, 29), (57, 23), (52, 15), (43, 13), (37, 22)],
    "indon": [(95, 5), (105, -4), (116, -8), (124, -6), (112, 2)],
    "aus": [(114, -22), (122, -17), (131, -12), (137, -12), (142, -11), (146, -19), (153, -27), (150, -37), (140, -38), (132, -32), (115, -34)],
    "namer": [(-168, 65), (-160, 70), (-140, 70), (-120, 72), (-95, 72), (-80, 65), (-60, 55), (-55, 48), (-67, 45), (-75, 38), (-81, 30), (-80, 25), (-90, 30), (-97, 26), (-97, 20), (-90, 15), (-83, 9), (-78, 8), (-87, 13), (-105, 20), (-112, 30), (-117, 33), (-124, 40), (-125, 49), (-135, 58), (-150, 60), (-165, 60)],
    "green": [(-55, 60), (-45, 60), (-20, 70), (-20, 80), (-40, 83), (-60, 80), (-70, 77)],
    "samer": [(-78, 8), (-72, 12), (-62, 10), (-50, 0), (-35, -5), (-38, -15), (-48, -25), (-58, -35), (-65, -42), (-68, -52), (-73, -50), (-75, -40), (-71, -30), (-71, -18), (-77, -10), (-81, -4)],
}
DESERTS = {
    "sahara": [(-12, 18), (-12, 27), (0, 30), (15, 31), (30, 29), (33, 21), (25, 17), (10, 15)],
    "arab": [(38, 28), (47, 27), (54, 21), (50, 16), (44, 15), (39, 21)],
    "ausd": [(119, -23), (130, -20), (139, -24), (137, -30), (125, -31), (119, -28)],
}
FORESTS = {
    "amazon": [(-74, -2), (-60, 2), (-50, -3), (-52, -12), (-64, -14), (-72, -10)],
    "congo": [(10, 3), (22, 4), (30, 0), (27, -7), (15, -6)],
    "taiga": [(55, 58), (90, 62), (125, 62), (130, 55), (95, 52), (60, 52)],
    "canada": [(-125, 55), (-95, 58), (-70, 52), (-80, 48), (-110, 49)],
    "seasia": [(96, 22), (106, 22), (108, 12), (100, 8), (95, 15)],
    "euro": [(10, 50), (25, 54), (35, 56), (30, 48), (15, 46)],
}
FOR_D = {k: _dense(v) for k, v in FORESTS.items()}
CONT_D = {k: _dense(v) for k, v in CONTINENTS.items()}
DES_D = {k: _dense(v) for k, v in DESERTS.items()}

MARS_REG = {
    "a": [(-40, 2), (-5, 10), (25, 3), (40, -12), (10, -22), (-25, -14)],
    "b": [(55, 28), (80, 24), (92, 8), (78, -2), (60, 6)],
    "c": [(110, -18), (150, -10), (170, -26), (135, -36), (105, -30)],
    "d": [(-150, 40), (-115, 50), (-85, 42), (-100, 30), (-140, 28)],
    "e": [(-95, -30), (-60, -26), (-50, -42), (-85, -48)],
    "f": [(150, 50), (175, 44), (178, 30), (155, 32)],
}
MARS_D = {k: _dense(v) for k, v in MARS_REG.items()}


def project(pts, r, lon0):
    out = []
    vis = False
    for lon, lat in pts:
        lam = math.radians(lon - lon0)
        ph = math.radians(lat)
        x = r * math.cos(ph) * math.sin(lam)
        y = -r * math.sin(ph)
        z = math.cos(ph) * math.cos(lam)
        if z < 0:
            d = math.hypot(x, y) or 1
            x, y = x / d * r * 1.02, y / d * r * 1.02
        else:
            vis = True
        out.append((x, y))
    return out, vis


CLOUDS = [(-60, 35, 1.0), (10, 52, 1.2), (80, 10, 0.9), (150, 40, 1.1), (-130, -20, 1.0), (40, -40, 1.3), (-20, -10, 0.8), (110, -45, 1.0), (-100, 50, 0.9), (170, -5, 0.8)]


def planet(c, cx, cy, r, lon0, tilt=0.0, kind="earth", light=(-0.75, -0.45), ice=0.0, heat=0.0, frost=0.0,
           tint=None, tint_a=0.0, clouds=True, t=0.0, atmo=1.0, cap_n=74, cap_s=70):
    """Flat stylised planet. lon0 = longitude at disc centre; tilt in degrees (image plane)."""
    lx, ly = light
    if kind == "earth":
        ocean_lo, ocean_hi, atmo_c = "#1450b4", "#2a8fe6", "#5fd0ff"
        land, land_d = "#3ec27a", "#2a9a5c"
    else:
        ocean_lo, ocean_hi, atmo_c = "#b8432a", "#ef7a45", "#ff9e6b"
        land, land_d = "#b5452c", "#9a3a24"
    # atmosphere halo
    if atmo > 0:
        c.drawCircle(cx, cy, r * 1.22, P(shader=rad(cx, cy, r * 1.22, [hx(atmo_c, 0.0), hx(atmo_c, 0.0), hx(atmo_c, 0.35 * atmo), hx(atmo_c, 0)], [0, 0.78, 0.84, 1])))
    c.save()
    c.translate(cx, cy)
    c.rotate(tilt)
    c.clipPath(circ_path(0, 0, r), doAntiAlias=True)
    # rotate light into planet frame
    tr = math.radians(-tilt)
    llx, lly = lx * math.cos(tr) - ly * math.sin(tr), lx * math.sin(tr) + ly * math.cos(tr)
    c.drawCircle(0, 0, r, P(shader=rad(llx * r * 0.45, lly * r * 0.45, r * 1.5, [hx(ocean_hi), hx(ocean_lo)], [0, 1])))
    # land
    # soft ocean depth patches
    if kind == "earth":
        c.drawCircle(llx * r * 0.35, lly * r * 0.35, r * 0.55, P(hx("#59b8ff", 0.10), blur=r * 0.15))
    regs = CONT_D if kind == "earth" else MARS_D
    paths = []
    for name, poly in regs.items():
        pts, vis = project(poly, r, lon0)
        if vis:
            paths.append(path_from(pts, True, 0.6))
    if kind == "earth":  # shallow-water halo around coasts
        for pth in paths:
            c.drawPath(pth, P(hx("#6cd3ff", 0.35), stroke=r * 0.05))
            c.drawPath(pth, P(hx("#9ae6ff", 0.35), stroke=r * 0.022))
    for pth in paths:
        c.drawPath(pth, P(hx(land)))
    if kind == "earth":
        for name, poly in FOR_D.items():
            pts, vis = project(poly, r, lon0)
            if vis:
                c.drawPath(path_from(pts, True, 0.8), P(hx("#2ea866", 0.9), blur=r * 0.006))
        for name, poly in DES_D.items():
            pts, vis = project(poly, r, lon0)
            if vis:
                c.drawPath(path_from(pts, True, 0.8), P(hx("#e6be62", 0.92), blur=r * 0.008))
        if heat > 0:  # scorched land
            for name, poly in CONT_D.items():
                pts, vis = project(poly, r, lon0)
                if vis:
                    c.drawPath(path_from(pts, True, 0.6), P(hx("#e8a23e", 0.85 * heat)))
            c.drawCircle(0, 0, r, P(hx("#ff7a2e", 0.18 * heat)))
    else:  # mars: volcano, canyon + craters
        pp, vv = project([(-134, 18)], r, lon0)
        lam = math.radians(-134 - lon0)
        if math.cos(math.radians(18)) * math.cos(lam) > 0.1:
            x, y = pp[0]
            sq = max(0.2, math.cos(lam) * math.cos(math.radians(18)))
            c.save(); c.translate(x, y); c.scale(sq, 1)
            c.drawCircle(0, 0, r * 0.13, P(hx("#d9653c")))
            c.drawCircle(0, 0, r * 0.13, P(hx("#f08a5a", 0.6), stroke=r * 0.012))
            c.drawCircle(0, 0, r * 0.04, P(hx("#a53f26")))
            c.restore()
        for (lo, la, s) in [(-62, 18, 0.05), (118, 22, 0.045), (-150, -40, 0.08), (22, -48, 0.06), (170, 8, 0.04), (-20, 38, 0.035), (66, -38, 0.07), (-110, -5, 0.03), (35, 30, 0.03), (-175, 15, 0.05)]:
            pp, vv = project([(lo, la)], r, lon0)
            lam = math.radians(lo - lon0)
            if math.cos(math.radians(la)) * math.cos(lam) > 0.15:
                x, y = pp[0]
                sq = max(0.2, math.cos(lam) * math.cos(math.radians(la)))
                c.save(); c.translate(x, y); c.scale(sq, 1)
                c.drawCircle(0, 0, r * s, P(hx("#c64e2f")))
                c.drawCircle(r * s * 0.15, r * s * 0.15, r * s * 0.8, P(hx("#a83b25")))
                c.restore()
    # polar caps (cap boundary at latitude L is the line y = -r sin L in this frame)
    def cap(L, top, col="#eef8ff", a=1.0, wob=0.02):
        yb = -r * math.sin(math.radians(L)) if top else r * math.sin(math.radians(L))
        pts = []
        N = 64
        for i in range(N + 1):
            x = -r + 2 * r * i / N
            u = x / r
            w_ = math.sin(u * 4.0 + lon0 * 0.06) * 0.55 + math.sin(u * 9.0 - lon0 * 0.04 + 1.3) * 0.3 + math.sin(u * 17.0 + 0.7) * 0.15
            yy = yb + r * wob * w_ * (1 if top else -1)
            pts.append((x, yy))
        if top:
            pts += [(r, -r * 1.1), (-r, -r * 1.1)]
        else:
            pts += [(r, r * 1.1), (-r, r * 1.1)]
        pth = path_from(pts, True, 0.0)
        c.drawPath(pth, P(hx(col, a)))
    capn = cap_n - ice * 42
    caps = cap_s - ice * 38
    cap(capn, True, wob=0.02 + 0.13 * ice)
    cap(caps, False, wob=0.02 + 0.13 * ice)
    if frost > 0:  # mid-latitude frost bands (mars at high tilt)
        cap(lerp(80, 38, frost), True, "#fff4ea", 0.55 * frost, 0.04)
        cap(lerp(80, 40, frost), False, "#fff4ea", 0.55 * frost, 0.04)
    # clouds
    if clouds and kind == "earth":
        for (lo, la, s) in CLOUDS:
            lo2 = lo + t * 6
            lam = math.radians(lo2 - lon0)
            z = math.cos(math.radians(la)) * math.cos(lam)
            if z <= 0.05:
                continue
            x = r * math.cos(math.radians(la)) * math.sin(lam)
            y = -r * math.sin(math.radians(la))
            sq = max(0.15, math.cos(lam))
            c.save(); c.translate(x, y); c.scale(sq, 1)
            w, h = r * 0.34 * s, r * 0.075 * s
            def puff(paint, ox=0.0, oy=0.0):
                rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2 + ox, -h / 2 + oy, w, h), h / 2, h / 2)
                c.drawRRect(rr, paint)
                c.drawCircle(-w * 0.12 + ox, -h * 0.45 + oy, h * 0.75, paint)
                c.drawCircle(w * 0.14 + ox, -h * 0.35 + oy, h * 0.55, paint)
            puff(P(hx("#0b2f7a", 0.18)), r * 0.02, r * 0.03)
            puff(P(hx("#ffffff", 0.92)))
            c.restore()
    # flat shading: lit crescent + shadow crescent
    sh = skia.Op(circ_path(0, 0, r * 1.01), circ_path(llx * r * 0.42, lly * r * 0.42, r * 1.08), skia.PathOp.kDifference_PathOp)
    if sh:
        c.drawPath(sh, P(hx("#0a0f3a", 0.36), blur=r * 0.006))
    sh2 = skia.Op(circ_path(0, 0, r * 1.01), circ_path(llx * r * 0.9, lly * r * 0.9, r * 1.25), skia.PathOp.kDifference_PathOp)
    if sh2:
        c.drawPath(sh2, P(hx("#050826", 0.28), blur=r * 0.03))
    c.save(); c.translate(llx * r * 0.5, lly * r * 0.5); c.rotate(math.degrees(math.atan2(lly, llx)) + 90)
    c.drawOval(skia.Rect.MakeXYWH(-r * 0.22, -r * 0.08, r * 0.44, r * 0.16), P(hx("#ffffff", 0.10), blur=r * 0.05))
    c.restore()
    hl = skia.Op(circ_path(0, 0, r), circ_path(-llx * r * 0.12, -lly * r * 0.12, r * 0.98), skia.PathOp.kDifference_PathOp)
    if hl:
        c.drawPath(hl, P(hx("#ffffff", 0.22), blur=r * 0.01))
    if tint and tint_a > 0:
        c.drawCircle(0, 0, r, P(hx(tint, tint_a)))
    c.restore()
    # rim light on lit side
    c.save()
    c.translate(cx, cy)
    ang = math.degrees(math.atan2(ly, lx))
    rect = skia.Rect.MakeXYWH(-r, -r, 2 * r, 2 * r)
    pth = skia.Path()
    pth.addArc(rect, ang - 55, 110)
    c.drawPath(pth, P(hx(atmo_c, 0.55 * atmo), stroke=r * 0.025, blur=r * 0.01))
    c.restore()


MOON_CRATERS = [(-0.35, -0.3, 0.2), (0.25, -0.45, 0.12), (0.4, 0.15, 0.22), (-0.1, 0.35, 0.15), (-0.5, 0.2, 0.1), (0.05, -0.05, 0.08), (0.6, -0.2, 0.08), (-0.25, 0.65, 0.09)]
MOON_MARIA = [[(-0.55, -0.45), (-0.1, -0.6), (0.1, -0.3), (-0.2, -0.05), (-0.6, -0.1)],
              [(0.05, 0.05), (0.45, -0.05), (0.55, 0.35), (0.2, 0.5), (-0.05, 0.3)]]


def moon(c, x, y, r, a=1.0, glow_a=1.0, light=(-0.6, -0.5), sx=1.0, sy=1.0):
    if r <= 0.5 or a <= 0:
        return
    if glow_a > 0:
        glow(c, x, y, r * 1.1, "#cbbcff", 0.55 * glow_a * a, 3.2)
        glow(c, x, y, r, "#ffffff", 0.35 * glow_a * a, 1.6)
    c.saveLayerAlpha(None, int(255 * clamp(a)))
    c.translate(x, y)
    c.scale(sx, sy)
    c.save()
    c.clipPath(circ_path(0, 0, r), doAntiAlias=True)
    lx, ly = light
    c.drawCircle(0, 0, r, P(shader=rad(lx * r * 0.4, ly * r * 0.4, r * 1.5, [hx("#fbf8ff"), hx("#cfc6ea")], [0, 1])))
    for m in MOON_MARIA:
        c.drawPath(path_from([(px * r, py * r) for px, py in m], True, 0.9), P(hx("#b8aedb", 0.55)))
    for (px, py, pr) in MOON_CRATERS:
        c.drawCircle(px * r, py * r, pr * r, P(hx("#c2b9e2")))
        c.drawCircle(px * r + pr * r * 0.12, py * r + pr * r * 0.14, pr * r * 0.8, P(hx("#ada2d6")))
    sh = skia.Op(circ_path(0, 0, r * 1.01), circ_path(lx * r * 0.35, ly * r * 0.35, r * 1.05), skia.PathOp.kDifference_PathOp)
    if sh:
        c.drawPath(sh, P(hx("#6f5fb0", 0.35), blur=r * 0.03))
    c.restore()
    c.restore()


def ghost_circle(c, x, y, r, a, phase=0.0, col="#cfc6ff"):
    if a <= 0:
        return
    p = P(hx(col, 0.8 * a), stroke=max(3, r * 0.035))
    dashed(c, circ_path(x, y, r), p, r * 0.16, r * 0.12, phase)


def sun(c, x, y, r, t, a=1.0, rays=1.0):
    """layered corona + glowing disc with soft surface granules (no cartoon spikes)"""
    c.drawCircle(x, y, r * 3.2, P(shader=rad(x, y, r * 3.2, [hx("#ff8a1a", 0.35 * a), hx("#ff6a00", 0.10 * a), hx("#ff6a00", 0)], [0.25, 0.55, 1]), mode=skia.BlendMode.kPlus))
    for k, (sc, col, al) in enumerate([(1.62, "#ff5a00", 0.20), (1.38, "#ff7a10", 0.26), (1.18, "#ffa020", 0.36)]):
        pts = []
        N = 96
        for i in range(N):
            an = 2 * math.pi * i / N
            rr = r * sc * (1 + 0.03 * math.sin(an * 7 + t * 1.3 + k * 2) + 0.018 * math.sin(an * 13 - t * 1.9 + k))
            pts.append((x + rr * math.cos(an), y + rr * math.sin(an)))
        c.drawPath(path_from(pts, True, 1.0), P(hx(col, al * a * (0.6 + 0.4 * rays)), blur=r * 0.015, mode=skia.BlendMode.kPlus))
    disc = circ_path(x, y, r)
    c.drawPath(disc, P(shader=rad(x - r * 0.3, y - r * 0.3, r * 1.45, [hx("#fffbe8", a), hx("#ffe58a", a), hx("#ffbb3a", a), hx("#ff941f", a)], [0, 0.35, 0.75, 1])))
    c.save(); c.clipPath(disc, doAntiAlias=True)
    rnd = random.Random(7)
    for _ in range(14):
        an, d = rnd.uniform(0, 6.28), rnd.uniform(0.15, 0.85) * r
        gx, gy = x + math.cos(an + t * 0.05) * d, y + math.sin(an + t * 0.05) * d
        c.drawCircle(gx, gy, rnd.uniform(0.08, 0.16) * r, P(hx("#fff3b8", 0.35 * a), blur=r * 0.04))
    for _ in range(5):
        an, d = rnd.uniform(0, 6.28), rnd.uniform(0.3, 0.8) * r
        c.drawCircle(x + math.cos(an) * d, y + math.sin(an) * d, rnd.uniform(0.05, 0.09) * r, P(hx("#ff9a2a", 0.30 * a), blur=r * 0.03))
    c.drawCircle(x + r * 0.35, y + r * 0.35, r * 0.95, P(hx("#ff7a1a", 0.18 * a), blur=r * 0.2))
    c.restore()
    c.drawCircle(x, y, r * 0.985, P(hx("#fff6d0", 0.35 * a), stroke=r * 0.025))


def rrect(c, x, y, w, h, rad_, p):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), rad_, rad_), p)


def card(c, x, y, w, h, a=1.0, col="#1a1f55"):
    rrect(c, x, y + 10, w, h, 36, P(hx("#03051a", 0.35 * a), blur=18))
    rrect(c, x, y, w, h, 36, P(hx(col, 0.96 * a)))
    rrect(c, x, y, w, h, 36, P(hx("#ffffff", 0.10 * a), stroke=3))


def vignette(c, a=0.55):
    c.drawRect(skia.Rect.MakeWH(W, H), P(shader=rad(W / 2, H * 0.47, H * 0.72, [hx("#000010", 0), hx("#000010", 0), hx("#000010", a)], [0, 0.55, 1])))


def arrow_chev(c, x, y, s, ang, col, a):
    c.save(); c.translate(x, y); c.rotate(ang)
    pth = path_from([(-s, -s * 0.7), (0, 0), (-s, s * 0.7)], False)
    c.drawPath(pth, P(hx(col, a), stroke=s * 0.35))
    c.restore()
