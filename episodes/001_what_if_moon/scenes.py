"""Episode 001 - What if the Moon disappeared? Scene functions (one per scene window)."""
import math, random
from lib import *
from kit import *
from timeline import T, E, S2, S8, S13, EV, LINES, Wd


def scene_land_open(c, t):
    v = EV["vanish"]
    # moon: anticipation swell then implode
    if t < v:
        s = 1.0 + 0.10 * ease_out(seg(t, v - 0.25, v))
    else:
        s = 1.10 * (1 - ease_in_back(seg(t, v, v + 0.32), 1.4))
    flash = seg(t, v + 0.26, v + 1.0) if t > v + 0.26 else None
    m = 1.0 - 0.5 * smooth(seg(t, v + 0.2, v + 0.9)) - 0.5 * smooth(seg(t, S2 + 0.1, S2 + 1.2))
    ghost = smooth(seg(t, EV["gone"] - 0.3, EV["gone"] + 0.3)) * (1 - smooth(seg(t, S2, S2 + 1.0))) * 0.9
    glide = ease_io(seg(t, EV["gone"] + 0.2, T[3] - 0.1))
    cam_z = 1.0 + 0.03 * ease_io(seg(t, 0, 3.0)) + 0.10 * glide
    cam_y = -110 * glide
    landscape(c, t, moon_s=max(0, s), m=m, ghost=ghost, flash=flash, cam_z=cam_z, cam_y=cam_y, shoot=seg(t, 0.05, 0.75))


def scene_land_end(c, t):
    b = EV["back"]
    lu = EV["lookup"]
    look = ease_io(seg(t, lu - 0.2, lu + 1.4))
    cam_y = lerp(-230, 0, look)
    cam_z = lerp(1.07, 1.0, ease_io(seg(t, lu - 0.2, b + 0.6)))
    s = ease_out_back(seg(t, b, b + 0.55), 1.8)
    m = smooth(seg(t, b + 0.05, b + 1.1))
    ghost = 0.6 * (1 - smooth(seg(t, b - 0.2, b + 0.2))) * smooth(seg(t, lu, lu + 0.8))
    flash = seg(t, b, b + 0.8) if t >= b else None
    landscape(c, t, moon_s=s, m=m, ghost=ghost, flash=flash, cam_y=cam_y, cam_z=cam_z, shoot=seg(t, lu + 0.35, lu + 1.1))


def scene_tides(c, t):
    t0 = T[3] - 0.5
    space_bg(c, t, "#080b29", "#17195a")
    ex, ey, er = 540, 740, 265
    # sun peeking at left edge
    sun(c, -70, ey, 180, t, 1.0, 0.8)
    tv = EV["tide_vanish"]
    moon_s = 1.0 if t < tv else 1.0 * (1 - ease_in_back(seg(t, tv, tv + 0.3), 1.4))
    mx, my = 850, 255 + 10 * math.sin(t * 0.8)
    th_m = math.atan2(my - ey, mx - ex)
    th_s = math.pi  # sun on the left
    k_ = ease_io(seg(t, tv + 0.1, tv + 1.4))
    amp_b = lerp(0.24, 0.08, k_)
    # bulge axis swings from the Moon to the Sun once the Moon is gone
    dth = (math.pi - th_m)
    dth = (dth + math.pi) % (2 * math.pi) - math.pi
    th_b = th_m + dth * k_
    pts = []
    for i in range(160):
        ph = i / 160 * 2 * math.pi
        rr = er * (0.985 + amp_b * max(0.0, math.cos(2 * (ph - th_b))) ** 1.15 + 0.004 * math.sin(ph * 6 + t * 2))
        pts.append((ex + rr * math.cos(ph), ey + rr * math.sin(ph)))
    wp = path_from(pts, True, 1.0)
    c.drawPath(wp, P(hx("#6fd0ff", 0.85)))
    c.drawPath(wp, P(hx("#e6f8ff", 0.9), stroke=5))
    planet(c, ex, ey, er, lon0=20 - (t - t0) * 9, tilt=0, t=t, atmo=0.0)
    # label the bulge
    la_ = smooth(seg(t, EV["tide_card"] + 0.2, EV["tide_card"] + 0.6)) * (1 - smooth(seg(t, tv, tv + 0.4)))
    if la_ > 0:
        tipx, tipy = ex + math.cos(th_m) * er * 1.2, ey + math.sin(th_m) * er * 1.2
        c.drawLine(tipx + 30, tipy + 30, 855, 650, P(hx("#bfeaff", 0.8 * la_), stroke=3))
        text(c, "ocean bulge", 820, 695, 36, "#bfeaff", la_, tf=TF_POP_SB, align="left", shadow=1)
    # pull chevrons Earth -> Moon
    ca = smooth(seg(t, EV["tide_card"] - 0.3, EV["tide_card"] + 0.3)) * (1 - smooth(seg(t, tv, tv + 0.3)))
    if ca > 0:
        for k in range(3):
            ph = ((t * 0.9) + k / 3) % 1
            d0 = er * 1.25 + ph * (math.hypot(mx - ex, my - ey) - er * 1.25 - 120)
            x, y = ex + math.cos(th_m) * d0, ey + math.sin(th_m) * d0
            arrow_chev(c, x, y, 30, math.degrees(th_m), "#ffd84d", ca * math.sin(ph * math.pi))
    moon(c, mx, my, 92 * max(moon_s, 0), 1.0, 1.0)
    if t >= tv:
        burst(c, mx, my, 92, seg(t, tv + 0.25, tv + 0.95), "#ffffff", 9, 2)
    # tide card
    ap = pop(t, EV["tide_card"], 0.45) * (1 - smooth(seg(t, T[6] - 0.75, T[6] - 0.45)))
    if ap > 0.01:
        cx0, cy0, cw, ch = 130, 1085, 820, 200
        c.save()
        c.translate(540, cy0 + ch / 2); c.scale(ap, ap); c.translate(-540, -(cy0 + ch / 2))
        card(c, cx0, cy0, cw, ch, 1.0)
        text(c, "TIDE HEIGHT", cx0 + 40, cy0 + 52, 28, "#9fb3ff", tf=TF_POP_SB, align="left", track=3)
        amp = lerp(1.0, 0.34, ease_io(seg(t, tv + 0.1, tv + 1.4)))
        mid = cy0 + 118
        A = 46
        # ghost of old range
        if t > tv:
            ga = smooth(seg(t, tv + 0.3, tv + 0.9))
            for yy in (mid - A, mid + A):
                dashed(c, path_from([(cx0 + 40, yy), (cx0 + cw - 40, yy)], False), P(hx("#ffffff", 0.35 * ga), stroke=3), 14, 12)
        wpts = []
        for i in range(90):
            x = cx0 + 40 + (cw - 80) * i / 89
            y = mid - A * amp * math.sin(i / 89 * 2 * math.pi * 2.0 - t * 2.4)
            wpts.append((x, y))
        fill = list(wpts) + [(cx0 + cw - 40, cy0 + ch - 14), (cx0 + 40, cy0 + ch - 14)]
        c.drawPath(path_from(fill, True), P(shader=lin(0, mid - A, 0, cy0 + ch, [hx("#3aa2f2", 0.55), hx("#3aa2f2", 0.0)])))
        c.drawPath(path_from(wpts, False), P(hx("#6fd0ff"), stroke=7))
        c.restore()
        bp = pop(t, EV["third"], 0.4)
        if bp > 0.01:
            bx, by = 830, 1087
            c.save(); c.translate(bx, by); c.scale(bp, bp)
            rrect(c, -95, -42, 190, 84, 42, P(hx("#ffd84d")))
            text(c, "≈ ⅓", 0, 18, 50, "#1a1440", tf=TF_BLACK)
            c.restore()


def scene_reef(c, t):
    lose = EV["reef_lose"]
    m = 1 - smooth(seg(t, lose, lose + 1.0))
    surf = 300
    # sky above the surface
    c.drawRect(skia.Rect.MakeWH(W, surf + 40), P(shader=lin(0, 0, 0, surf, [hx("#0b0f36"), hx(mixhex("#141a55", "#24308a", m))])))
    STARS.draw(c, t, 0.8, 0, 0)
    mx, my = 760, 150
    if m > 0.02:
        moon(c, mx, my, 72 * (0.3 + 0.7 * m), m, 1.0)
    # water body
    c.save()
    pts = [(x, surf + 9 * math.sin(x * 0.011 + t * 1.5) + 4 * math.sin(x * 0.031 - t * 2.1)) for x in range(-20, W + 40, 16)]
    water = path_from(pts + [(W + 40, H + 300), (-20, H + 300)], True)
    c.drawPath(water, P(shader=lin(0, surf, 0, H, [hx(mixhex("#163f8f", "#2167c2", m)), hx(mixhex("#0f2f74", "#174f9f", m)), hx("#0b2560"), hx("#071a45")], [0, 0.3, 0.62, 1])))
    c.clipPath(water, doAntiAlias=True)
    # moonlight pooling just under the surface
    c.drawOval(skia.Rect.MakeXYWH(mx - 220, surf - 20, 440, 90), P(hx("#d6ecff", 0.22 * m), blur=24))
    c.drawPath(path_from(pts, False), P(hx("#cfe8ff", 0.55), stroke=4))
    # soft light shafts
    for k in range(5):
        x0 = mx - 220 + k * 110 + 25 * math.sin(t * 0.4 + k)
        ray = path_from([(x0, surf), (x0 + 70, surf), (x0 + 210 - k * 95, 1250), (x0 - 10 - k * 95, 1250)], True)
        c.drawPath(ray, P(shader=lin(0, surf, 0, 1250, [hx("#bfe3ff", 0.10 * m), hx("#bfe3ff", 0)]), blur=6))
    # far reef silhouettes (two depth layers)
    far = [(-40, 1150), (60, 1080), (170, 1110), (260, 1040), (360, 1090), (470, 1060), (560, 1100), (660, 1030), (770, 1080), (880, 1050), (990, 1090), (1120, 1060)]
    c.drawPath(path_from([(-60, 1400)] + far + [(1140, 1400)], True, 0.9), P(hx(mixhex("#16397f", "#1c4a98", m))))
    for k, (fx, fy) in enumerate(far[1:-1]):
        if k % 2 == 0:
            c.drawLine(fx, fy + 10, fx + 8 * math.sin(t * 0.8 + k), fy - 60 - 20 * (k % 3), P(hx(mixhex("#16397f", "#1c4a98", m)), stroke=12))
    mid = [(-40, 1200), (90, 1150), (230, 1175), (380, 1130), (520, 1165), (690, 1125), (840, 1160), (980, 1135), (1120, 1170)]
    c.drawPath(path_from([(-60, 1400)] + mid + [(1140, 1400)], True, 0.9), P(hx(mixhex("#132f6c", "#183e85", m))))
    # drifting particles
    rnd3 = random.Random(8)
    for k in range(40):
        x = rnd3.uniform(0, W) + 10 * math.sin(t * 0.5 + k)
        y = surf + (rnd3.uniform(0, 1100) + t * 14) % 1100
        c.drawCircle(x, y, rnd3.uniform(1.4, 2.8), P(hx("#cfe6ff", 0.28)))
    # a school of small fish sweeping across mid-water
    sx = ((t - T[6] + 1.5) * 95) % (W + 700) - 350
    for k in range(16):
        ox = (k % 4) * 48 + (k // 4) * 22 + 10 * math.sin(t * 2 + k)
        oy = (k // 4) * 36 + 8 * math.sin(t * 2.6 + k * 1.7)
        fx, fy = sx + ox, 760 + oy + 30 * math.sin(t * 0.7)
        c.save(); c.translate(fx, fy)
        c.drawPath(path_from([(-16, 0), (-26, -7), (-26, 7)], True), P(hx("#9fd8ff", 0.95)))
        c.drawOval(skia.Rect.MakeXYWH(-20, -7, 34, 14), P(hx("#9fd8ff", 0.95)))
        c.drawCircle(8, -2, 2.2, P(hx("#0b1a44")))
        c.restore()
    # bigger reef fish
    for k, (y0, sp, body, stripe, s, ph) in enumerate([(650, 62, "#ff9a2e", "#ffffff", 1.15, 0), (930, -48, "#ff6b8b", "#ffe9a8", 1.0, 400)]):
        span = W + 300
        x = ((ph + sp * (t - T[6])) % span) - 150 if sp > 0 else span - 150 - ((ph - sp * (t - T[6])) % span)
        reef_fish(c, x, y0 + 12 * math.sin(t * 1.3 + k), s, body, stripe, sp < 0, t, k)
    # ---- foreground reef bed
    sway = 2.5 * math.sin(t * 1.1)
    tips = []
    kelp(c, 40, 1330, 330, t, 0, "#1f9e86", "#2cc4a2")
    kelp(c, 1045, 1330, 300, t, 2, "#1f9e86", "#2cc4a2")
    # rock mounds with lit tops
    rocks = [(180, 1275, 175, 80), (520, 1285, 210, 85), (880, 1270, 190, 85)]
    for (rx, ry, rw, rh) in rocks:
        rp = skia.Path(); rp.addOval(skia.Rect.MakeXYWH(rx - rw, ry - rh, 2 * rw, 2 * rh + 120))
        c.drawPath(rp, P(hx("#3a2f8a")))
        c.save(); c.clipPath(rp, doAntiAlias=True)
        c.drawOval(skia.Rect.MakeXYWH(rx - rw * 0.95, ry - rh * 1.05, rw * 1.6, rh * 0.8), P(hx("#5446b3", 0.85)))
        rnd2 = random.Random(int(rx))
        for _ in range(6):
            c.drawCircle(rx + rnd2.uniform(-0.7, 0.7) * rw, ry + rnd2.uniform(-0.2, 0.9) * rh, rnd2.uniform(5, 11), P(hx("#271f66")))
        c.restore()
    staghorn(c, 150, 1215, 1.05, "#ff5c9d", "#c23a78", "#ffc0dc", sway, tips, 3)
    sea_fan(c, 330, 1225, 150, "#ff7a45", "#c9502a", sway)
    brain(c, 520, 1215, 95, "#5fd38a", "#2e9a62", "#2a8c58", 4)
    table_coral(c, 720, 1225, 210, "#3cc9d6", "#1f8fa3", "#a6f2f7")
    staghorn(c, 905, 1205, 0.9, "#b56bff", "#7f3fd0", "#e3c6ff", -sway, tips, 9)
    tubes(c, 985, 1262, "#ffc94a", "#d89a1e", "#7a4a12", 0.8)
    # sand floor
    sand = [(x, 1300 + 16 * math.sin(x * 0.009 + 1) + 6 * math.sin(x * 0.03)) for x in range(-20, W + 40, 20)]
    c.drawPath(path_from(sand + [(W + 40, H + 300), (-20, H + 300)], True), P(shader=lin(0, 1290, 0, 1700, [hx("#2c2a78"), hx("#1a1850"), hx("#0d0c30")])))
    c.drawPath(path_from(sand, False), P(hx("#5b55c4", 0.6), stroke=4))
    for k in range(6):
        y = 1335 + k * 22
        c.drawLine(80 + k * 40, y, 260 + k * 40, y, P(hx("#3d3a96", 0.45), stroke=3))
        c.drawLine(760 - k * 30, y + 6, 930 - k * 30, y + 6, P(hx("#3d3a96", 0.45), stroke=3))
    # dark foreground framing (closer to camera)
    fg = "#0a0a2c"
    c.drawPath(path_from([(-40, 1560), (60, 1500), (170, 1530), (260, 1610), (300, 1700), (300, H + 50), (-40, H + 50)], True, 0.8), P(hx(fg)))
    c.drawPath(path_from([(1120, 1520), (980, 1490), (880, 1560), (820, 1680), (800, H + 50), (1120, H + 50)], True, 0.8), P(hx(fg)))
    for k, (x0, h_) in enumerate([(70, 260), (150, 190), (1000, 280), (930, 200)]):
        pts_k = [(x0 + 18 * math.sin(t * 0.9 + k + j * 0.5) * (j / 8), 1580 - j * h_ / 8) for j in range(9)]
        c.drawPath(path_from(pts_k, False, 1.0), P(hx(fg), stroke=22))
    # spawning: tiny egg bundles rising in soft plumes from the coral heads, starting on "spawn"
    byx = sorted(tips, key=lambda p: p[0])
    heads = [byx[i] for i in range(0, len(byx), max(1, len(byx) // 12))]
    heads += [(520, 1125), (720, 1120), (330, 1080), (985, 1095)]  # brain, table coral, fan, sponges
    rnd = random.Random(5)
    t_sp = Wd(6, 3) - 0.2
    for k in range(70):
        hxp, hyp = heads[k % len(heads)]
        b_ = rnd.uniform(t_sp, lose + 0.4)
        if t < b_:
            continue
        age = t - b_
        sp = rnd.uniform(45, 85)
        x = hxp + rnd.uniform(-6, 6) + age * rnd.uniform(-10, 10) + 10 * math.sin(age * 1.3 + k)
        y = hyp - 8 - age * sp
        if y < surf + 60:
            continue
        a = min(1, age * 3) * clamp((y - surf - 60) / 300) * (1 - 0.6 * (1 - m))
        col = "#ff9cc6" if k % 3 else "#ffc49a"
        c.drawCircle(x, y, 4.6, P(hx(col, a)))
        c.drawCircle(x + 3.8, y + 2.6, 3.4, P(hx(col, a * 0.9)))
    # darken as the light goes
    c.drawRect(skia.Rect.MakeWH(W, H), P(hx("#040822", 0.30 * (1 - m))))
    # the crab, who watches the moon... until it's gone
    look = smooth(seg(t, lose + 0.2, lose + 0.6))
    c.save(); c.translate(640, 1262); c.scale(1.25, 1.25)
    crab(c, 0, 0, t, look, smooth(seg(t, lose + 0.5, lose + 0.8)))
    c.restore()
    qp2 = pop(t, lose + 0.55, 0.4)
    if qp2 > 0.01:
        c.save(); c.translate(722, 1120 + 4 * math.sin(t * 3)); c.scale(qp2, qp2)
        c.drawCircle(0, 0, 38, P(hx("#ffffff")))
        c.drawPath(path_from([(-12, 30), (-26, 52), (4, 36)], True), P(hx("#ffffff")))
        text(c, "?", 0, 17, 50, "#ff5d7a", tf=TF_POP_XB)
        c.restore()
    # calendar card
    ca = pop(t, EV["reef_card"], 0.45)
    if ca > 0.01:
        cx0, cy0, cw, ch = 150, 410, 780, 168
        c.save(); c.translate(540, cy0 + ch / 2); c.scale(ca, ca); c.translate(-540, -(cy0 + ch / 2))
        card(c, cx0, cy0, cw, ch, 0.92, "#14205e")
        text(c, "MOON CALENDAR", 540, cy0 + 42, 24, "#9fb3ff", tf=TF_POP_SB, track=3)
        for k in range(8):
            x = cx0 + 85 + k * 87
            y = cy0 + 95
            r = 26
            dead = smooth(seg(t, lose + 0.1 + k * 0.08, lose + 0.35 + k * 0.08))
            moon_phase(c, x, y, r, k, 1 - dead)
            if dead > 0:
                ghost_circle(c, x, y, r, dead * 0.7, phase=t * 20)
        # spawning night marker (a few nights after full moon)
        mk = (1 - smooth(seg(t, lose + 0.4, lose + 0.8))) * smooth(seg(t, EV["moonlight"] - 0.2, EV["moonlight"] + 0.2))
        if mk > 0:
            x = cx0 + 85 + 5 * 87
            c.drawCircle(x, cy0 + 95, 33, P(hx("#ff8fc0", mk), stroke=4))
            c.drawPath(path_from([(x - 10, cy0 + 146), (x + 10, cy0 + 146), (x, cy0 + 134)], True), P(hx("#ff8fc0", mk)))
        c.restore()
    c.restore()


def scene_space(c, t):
    t0 = T[7] - 0.5
    grow = ease_io(seg(t, t0, T[8]))
    r = lerp(170, 285, grow)
    # make room for the spinning-top comparison
    ana = ease_io(seg(t, EV["top"] - 0.35, EV["top"] + 0.25)) * (1 - ease_io(seg(t, EV["wobble"] + 0.9, EV["wobble"] + 1.6)))
    cx, cy = lerp(540, 330, ana), lerp(750, 560, ana)
    sc_e = lerp(1.0, 0.66, ana)
    r *= sc_e
    dark = smooth(seg(t, T[7], T[7] + 0.8)) * (1 - smooth(seg(t, T[8], T[8] + 1.0)))
    space_bg(c, t, "#070923", "#15184f", 1.0, 0, -grow * 30)
    # ominous red pulse during "the slow, scary part"
    if dark > 0:
        pr = 0.5 + 0.5 * math.sin((t - T[7]) * 4)
        c.drawCircle(cx, cy, r * 2.4, P(shader=rad(cx, cy, r * 2.4, [hx("#ff3b5c", 0.0), hx("#ff3b5c", 0.22 * dark * (0.6 + 0.4 * pr)), hx("#ff3b5c", 0)], [0.35, 0.5, 1])))
    sun(c, -40, 380, 130, t, 0.9, 0.6)
    # tilt
    tilt_in = ease_io(seg(t, EV["tilt"], EV["tilt"] + 0.9))
    base_tilt = 23.4 * tilt_in
    wob_t = t - EV["wobble"]
    amp = 22 * smooth(seg(t, EV["wobble"] + 0.4, E[10]))
    tilt = base_tilt + (amp * math.sin(wob_t * 2.6) if wob_t > 0 else 0)
    # moon orbit
    oa = smooth(seg(t, EV["orbit"], EV["orbit"] + 0.5))
    mv = EV["wobble"]
    moon_s = 1 - ease_in_back(seg(t, mv, mv + 0.3), 1.4) if t > mv else 1.0
    orbit_a = oa * (1 - smooth(seg(t, mv, mv + 0.6)))
    rx, ry, orot = 450 * sc_e, 115 * sc_e, -8
    ang = (t - EV["orbit"]) * 1.1 - 1.2
    mxo, myo = math.cos(ang) * rx, math.sin(ang) * ry
    cr, sr = math.cos(math.radians(orot)), math.sin(math.radians(orot))
    mx, my = cx + mxo * cr - myo * sr, cy + mxo * sr + myo * cr
    behind = math.sin(ang) < 0
    orbit_ring(c, cx, cy, rx, ry, orot, orbit_a, False)
    if behind and oa > 0:
        moon(c, mx, my, 64 * sc_e * oa * max(0, moon_s), 1, 0.8)
    # axis trail while wandering
    if wob_t > 0 and amp > 0.5:
        trail = []
        for k in range(40):
            tt = wob_t - k * 0.03
            if tt < 0:
                break
            a2 = 22 * smooth(seg(t - k * 0.03, EV["wobble"] + 0.4, E[10]))
            tl = 23.4 + a2 * math.sin(tt * 2.6)
            L = r * 1.42
            trail.append((cx + math.sin(math.radians(tl)) * L, cy - math.cos(math.radians(tl)) * L))
        if len(trail) > 2:
            c.drawPath(path_from(trail, False), P(hx("#ff6b8b", 0.6), stroke=6))
    steady = smooth(seg(t, EV["steady"], EV["steady"] + 0.4)) * (1 - smooth(seg(t, mv, mv + 0.4)))
    axis_col = mixhex("#ffffff", "#5cf2c8", steady)
    ax_a = smooth(seg(t, EV["tilt"] - 0.1, EV["tilt"] + 0.4))
    if steady > 0:
        L = r * 1.42
        tr = math.radians(tilt)
        glow(c, cx + math.sin(tr) * L, cy - math.cos(tr) * L, 26, "#5cf2c8", steady, 2.2)
    # back half of axis drawn behind planet would be hidden; draw all, then planet, then front tip
    axis_and_arc(c, cx, cy, r, tilt, ax_a, axis_col, label=ax_a > 0.5 and t > EV["tilt"] + 0.5, ref=True)
    planet(c, cx, cy, r, lon0=-(t - t0) * 12, tilt=tilt, t=t, light=(-0.8, -0.5),
           tint="#ff2a4f", tint_a=0.10 * dark)
    if not behind and oa > 0:
        moon(c, mx, my, 64 * sc_e * oa * max(0, moon_s), 1, 0.8)
    orbit_ring(c, cx, cy, rx, ry, orot, orbit_a, True)
    if t > mv:
        burst(c, mx, my, 56, seg(t, mv + 0.25, mv + 0.95), "#ffffff", 9, 3)
    # season icons
    sa = 1 - smooth(seg(t, T[9] - 0.1, T[9] + 0.3))
    if sa > 0:
        for k, kind in enumerate(["snow", "flower", "sun", "leaf"]):
            p = pop(t, EV["seasons"] + k * 0.16, 0.35)
            season_icon(c, kind, 225 + k * 210, 1235, p * 0.85, sa)
    # spinning top analogy: a hand keeps the top steady... then lets go
    ta = pop(t, EV["top"] - 0.1, 0.5) * (1 - smooth(seg(t, EV["wobble"] + 1.0, EV["wobble"] + 1.5)))
    if ta > 0.01:
        lift = ease_in_back(seg(t, EV["wobble"] - 0.05, EV["wobble"] + 0.5), 1.2)
        wob = smooth(seg(t, EV["wobble"] + 0.1, EV["wobble"] + 0.9))
        c.save(); c.translate(745, 1010); c.scale(1.3 * ta, 1.3 * ta)
        c.drawCircle(0, 30, 190, P(shader=rad(0, 30, 190, [hx("#6b5cff", 0.22), hx("#6b5cff", 0)])))
        spinning_top(c, 0, 0, t, 1.0, 1.0 - wob)
        hp = ease_out(seg(t, EV["hand"] - 0.25, EV["hand"] + 0.25))
        hand2(c, 0, -72 - (1 - hp) * 260 - lift * 320, 1.0 * (1 - lift))
        c.restore()
    # million-year counter
    ka = smooth(seg(t, EV["wobble"] + 0.6, EV["wobble"] + 1.0))
    if ka > 0:
        n = 1 + int(9 * ease_io(seg(t, EV["wobble"] + 0.7, E[10] + 0.3)))
        text(c, f"+{n} MILLION YEARS", 540, 205, 58, "#ffd84d", ka, tf=TF_POP_XB, shadow=1)


def scene_mars(c, t):
    t0 = T[11] - 0.5
    space_bg(c, t, "#0c0920", "#2a1640")
    cx, cy, r = 560, 790, 320
    sun(c, -60, 300, 120, t, 0.85, 0.5)
    ph = (t - T[11])
    amp = 9 + 15 * smooth(seg(t, EV["wildly"] - 0.6, EV["wildly"] + 0.2))
    tilt = 25 + amp * math.sin(ph * 1.8)
    frost = smooth(clamp((tilt - 30) / 14))
    # tiny moons behind/in front
    moons = []
    for (orb, sp, s, off, col) in [(410, 1.6, 26, 0.0, "#a78a74"), (495, 0.9, 17, 2.0, "#8f7a6a")]:
        a = ph * sp + off
        mx, my = cx + math.cos(a) * orb, cy + math.sin(a) * orb * 0.22
        moons.append((math.sin(a) > 0, mx, my, s, col))
    for front, mx, my, s, col in moons:
        if not front:
            phobos(c, mx, my, s, col)
    axis_and_arc(c, cx, cy, r, tilt, 1.0, "#ffffff", label=True, ref=True)
    planet(c, cx, cy, r, lon0=-(t - t0) * 14, tilt=tilt, kind="mars", frost=frost, cap_n=74 + 10 * frost, cap_s=72 + 10 * frost, light=(-0.8, -0.5))
    for front, mx, my, s, col in moons:
        if front:
            phobos(c, mx, my, s, col)
    text(c, "MARS", 540, 230, 66, "#ffb08a", smooth(seg(t, T[11] - 0.2, T[11] + 0.3)), tf=TF_POP_XB, track=12, shadow=1)
    # tiny label for the little moons
    la = smooth(seg(t, T[11] + 0.6, T[11] + 1.0)) * (1 - smooth(seg(t, T[11] + 2.6, T[11] + 3.0)))
    if la > 0:
        text(c, "just 2 tiny moons", 540, 1250, 36, "#e7cfc2", la, tf=TF_POP_SB, shadow=1)


def scene_extreme(c, t):
    t0 = T[12] - 0.5
    space_bg(c, t, "#080a28", "#1b1b58")
    sun(c, -50, 330, 140, t, 0.9, 0.7)
    cx, cy, r = 620, 780, 305
    ph = t - T[12]
    cyc = math.sin(ph * 1.7 - 0.6)
    ice = clamp(0.5 + 0.6 * cyc)
    heat = clamp(-cyc * 1.2)
    tilt = 23.4 + 22 * math.sin(ph * 1.7 - 0.6 + 1.2)
    axis_and_arc(c, cx, cy, r, tilt, 1.0, "#ffffff", label=False, ref=False)
    planet(c, cx, cy, r, lon0=-(t - t0) * 14 + 60, tilt=tilt, t=t, ice=ice, heat=heat, light=(-0.8, -0.6))
    thermometer(c, 120, 590, 380, -cyc, smooth(seg(t, t0 + 0.3, t0 + 0.8)))


def scene_eclipse(c, t):
    t0 = T[13] - 0.5
    space_bg(c, t, "#0a0b2a", "#221a55")
    sx, sy, sr = 540, 760, 235
    sun(c, sx, sy, sr, t, 1.0, 1.0)
    p = ease_io(seg(t, T[13] - 0.2, T[13] + 1.3))
    gx = lerp(-260, W + 260, p)
    ghost_circle(c, gx, sy - 10, sr * 0.98, 0.95, phase=t * 40, col="#ffffff")
    # cross mark appears over the empty spot
    xa = pop(t, T[13] + 0.55, 0.35) * (1 - smooth(seg(t, T[13] + 1.2, T[13] + 1.5)))
    if xa > 0.01:
        c.save(); c.translate(sx + 250, sy - 260); c.scale(xa, xa)
        c.drawCircle(0, 0, 54, P(hx("#ff5d7a")))
        pp = P(hx("#ffffff"), stroke=12)
        c.drawLine(-20, -20, 20, 20, pp); c.drawLine(20, -20, -20, 20, pp)
        c.restore()


SCENE_FN = {
    "land_open": scene_land_open, "tides": scene_tides, "reef": scene_reef, "space": scene_space,
    "mars": scene_mars, "extreme": scene_extreme, "eclipse": scene_eclipse, "land_end": scene_land_end,
}
