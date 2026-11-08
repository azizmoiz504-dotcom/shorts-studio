"""Scene functions: one per scene window in timeline.SCENES. Each draws a FULL 1080x1920 frame for time t.
Build from engine/kit.py + engine/lib.py pieces first; draw new objects only when the kit has nothing suitable."""
import math, random
from lib import *
from kit import *
from timeline import T, E, EV, LINES, Wd, DURATION


def scene_open(c, t):
    space_bg(c, t, "#080b29", "#17195a")
    sun(c, -60, 420, 150, t, 0.9, 0.6)
    p = pop(t, EV["rings_appear"], 0.5)

    def rings(half):  # half = 180 -> back half (behind the planet), 0 -> front half
        if p <= 0.01:
            return
        c.save(); c.translate(540, 780); c.rotate(18); c.scale(p, p)
        for k, (rr, a) in enumerate([(430, 0.55), (390, 0.75), (350, 0.5)]):
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeXYWH(-rr, -rr * 0.18, 2 * rr, 2 * rr * 0.18), half, 180)
            c.drawPath(arc, P(hx("#e9d7a8", a), stroke=14 - k * 3))
        c.restore()
    rings(180)
    planet(c, 540, 780, 260, lon0=-t * 10, tilt=18, t=t)
    rings(0)


def scene_sky(c, t):
    landscape(c, t, moon_s=1.0, m=1.0)


SCENE_FN = {"open": scene_open, "sky": scene_sky}
