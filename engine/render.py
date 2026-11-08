"""Generic renderer: composes an episode's scenes, transitions, captions, glow and grain; encodes.

Usage (from the repo root):
  python3 engine/render.py EPISODE_DIR render [NPROC]          -> EPISODE_DIR/out/video.mp4 (silent)
  python3 engine/render.py EPISODE_DIR strip NAME t1 t2 ...     -> EPISODE_DIR/qa/NAME.jpg (half-size frames side by side)
  python3 engine/render.py EPISODE_DIR full NAME t              -> EPISODE_DIR/qa/NAME.jpg (one full-size frame)
  python3 engine/render.py EPISODE_DIR crops NAME t x y w h [t x y w h ...]  -> 100% crops scaled to 600px tall
  python3 engine/render.py EPISODE_DIR sheet NAME t1 t2 ...     -> small contact sheet (8 per row)

The episode folder must contain timeline.py (SCENES, TRANS, CAPTIONS, FPS, NFRAMES, DURATION and optionally
STATIC_SCENES, DUSTY_SCENES, ZOOM_FOCUS) and scenes.py (SCENE_FN).
"""
import sys, os, subprocess, math

ENGINE = os.path.dirname(os.path.abspath(__file__))
if __name__ == "__main__":
    EP = os.path.abspath(sys.argv[1])
else:
    EP = os.path.abspath(os.environ["EPISODE_DIR"])
sys.path.insert(0, EP)
sys.path.insert(1, ENGINE)

import numpy as np
from multiprocessing import Process
from PIL import Image, ImageFilter
from lib import *
import timeline as TL
from timeline import SCENES, TRANS, CAPTIONS, FPS, NFRAMES, DURATION
from scenes import SCENE_FN
from kit import dust

OUT = os.path.join(EP, "out")
QA = os.path.join(EP, "qa")
os.makedirs(OUT, exist_ok=True)
os.makedirs(QA, exist_ok=True)
INFO = skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)
STATIC = set(getattr(TL, "STATIC_SCENES", []))          # scenes that manage their own camera (no drift)
DUSTY = set(getattr(TL, "DUSTY_SCENES", []))            # scenes that get floating foreground dust
FOCUS = dict(getattr(TL, "ZOOM_FOCUS", {}))             # zoom_in focus point per incoming scene

rng = np.random.default_rng(1)
GRAIN = [np.clip(rng.normal(0, 3.0, (H, W, 1)), -9, 9).astype(np.int16) for _ in range(6)]
SPAN = {n: (a, b) for n, a, b in SCENES}


def draw_scene(c, name, t):
    c.save()
    if name not in STATIC:
        a, b = SPAN[name]
        p = seg(t, a, b)
        s = 1.0 + 0.055 * p
        c.translate(W / 2 + 14 * math.sin(t * 0.35), H * 0.45 + 10 * math.sin(t * 0.27 + 1))
        c.scale(s, s)
        c.translate(-W / 2, -H * 0.45)
    SCENE_FN[name](c, t)
    if name in DUSTY:
        dust(c, t, 1.0)
    c.restore()


def compose(c, t):
    act = [s for s in SCENES if s[1] <= t < s[2]]
    if not act:
        act = [SCENES[-1]]
    if len(act) == 1:
        draw_scene(c, act[0][0], t)
    else:
        A, B = act[0], act[1]
        p = seg(t, B[1], A[2])
        e = ease_io(p)
        st = TRANS.get(B[0], "fade")
        if st in ("slide_up", "slide_left"):
            dx, dy = (0, -H) if st == "slide_up" else (-W, 0)
            c.save(); c.translate(dx * e, dy * e); draw_scene(c, A[0], t); c.restore()
            c.save(); c.translate(-dx * (1 - e), -dy * (1 - e)); draw_scene(c, B[0], t); c.restore()
            c.drawRect(skia.Rect.MakeWH(W, H), P(hx("#ffffff", 0.06 * math.sin(p * math.pi))))
        elif st == "zoom_in":
            fx, fy = FOCUS.get(B[0], (W / 2, H / 2))
            s = 1 + 3.5 * ease_in(p)
            c.save(); c.translate(fx, fy); c.scale(s, s); c.translate(-fx, -fy); draw_scene(c, A[0], t); c.restore()
            c.saveLayerAlpha(None, int(255 * smooth(seg(p, 0.35, 1.0))))
            s2 = lerp(0.6, 1.0, ease_out(p))
            c.translate(W / 2, H / 2); c.scale(s2, s2); c.translate(-W / 2, -H / 2)
            draw_scene(c, B[0], t)
            c.restore()
        elif st == "zoom_out":
            s = lerp(1.0, 1.3, ease_in(p))
            c.save(); c.translate(W / 2, H * 0.62); c.scale(s, s); c.translate(-W / 2, -H * 0.62); draw_scene(c, A[0], t); c.restore()
            c.saveLayerAlpha(None, int(255 * smooth(seg(p, 0.1, 0.9))))
            s2 = lerp(1.25, 1.0, ease_out(p))
            c.translate(W / 2, H / 2); c.scale(s2, s2); c.translate(-W / 2, -H / 2)
            draw_scene(c, B[0], t)
            c.restore()
        else:  # "fade"
            draw_scene(c, A[0], t)
            c.saveLayerAlpha(None, int(255 * e))
            s2 = lerp(1.04, 1.0, e)
            c.translate(W / 2, H / 2); c.scale(s2, s2); c.translate(-W / 2, -H / 2)
            draw_scene(c, B[0], t)
            c.restore()


# Captions live in the phone-safe zone: centre y=1405 (YouTube's title/channel overlay covers ~y>1540).
CAP_Y = 1405
CAP_SIZE = 68
CAP_MAXW = 860
CAP_FONT = skia.Font(TF_POP_B, CAP_SIZE)
CAP_FONT.setSubpixel(True)
CAP_FONT.setEdging(skia.Font.Edging.kSubpixelAntiAlias)


def caption(c, t):
    cur = None
    for cp in CAPTIONS:
        if cp["t0"] <= t < cp["t1"]:
            cur = cp
    if not cur:
        return
    f = CAP_FONT
    p = seg(t, cur["t0"], cur["t0"] + 0.22)
    a = ease_out(p) * (1 - smooth(seg(t, cur["t1"] - 0.08, cur["t1"])))
    lift = 22 * (1 - ease_out(p))
    words = cur["words"]
    space = f.measureText(" ")
    widths = [f.measureText(w["text"]) for w in words]
    total = sum(widths) + space * (len(words) - 1)
    lines = [list(range(len(words)))]
    if total > CAP_MAXW and len(words) > 1:
        best = None
        for k in range(1, len(words)):
            w1 = sum(widths[:k]) + space * (k - 1)
            w2 = sum(widths[k:]) + space * (len(words) - k - 1)
            sc_ = max(w1, w2) + (0.15 * abs(w1 - w2) if w2 > w1 else 0)
            if best is None or sc_ < best[0]:
                best = (sc_, k)
        lines = [list(range(best[1])), list(range(best[1], len(words)))]
    lh = CAP_SIZE * 1.22
    y0 = CAP_Y - (len(lines) - 1) * lh / 2 + lift
    for li, idxs in enumerate(lines):
        lw = sum(widths[i] for i in idxs) + space * (len(idxs) - 1)
        x = 540 - lw / 2
        y = y0 + li * lh + CAP_SIZE * 0.36
        for i in idxs:
            w = words[i]
            on = smooth(seg(t, w["t0"] - 0.03, w["t0"] + 0.06)) * (1 - smooth(seg(t, w["t1"] + 0.02, w["t1"] + 0.14)))
            said = t >= w["t0"]
            col = mix("#ffffff", "#ffd84d", on, a * (1.0 if said else 0.9))
            c.drawString(w["text"], x, y + 5, f, P(hx("#02021a", 0.55 * a), blur=12))
            c.drawString(w["text"], x, y, f, P(hx("#02021a", 0.35 * a), stroke=5))
            c.drawString(w["text"], x, y, f, P(col))
            x += widths[i] + space


def bloom(arr, thr=200, amt=0.42):
    """Glow only on near-white light (luminance based), never on saturated colours."""
    im = Image.fromarray(arr[:, :, :3])
    sm = im.resize((W // 8, H // 8), Image.BILINEAR)
    a = np.asarray(sm).astype(np.float32)
    lum = (a[:, :, :1] * 0.3 + a[:, :, 1:2] * 0.59 + a[:, :, 2:3] * 0.11)
    b = a * np.clip((lum - thr) / (255 - thr), 0, 1)
    bi = Image.fromarray(b.astype(np.uint8)).filter(ImageFilter.GaussianBlur(5))
    big = np.asarray(bi.resize((W, H), Image.BILINEAR)).astype(np.uint16)
    base = arr[:, :, :3].astype(np.uint16)
    res = base + (big * int(amt * 256) >> 8)
    np.minimum(res, 255, out=res)
    arr[:, :, :3] = res.astype(np.uint8)


def frame(surface, i, out=None):
    t = i / FPS
    c = surface.getCanvas()
    c.clear(hx("#000000"))
    compose(c, t)
    c.drawRect(skia.Rect.MakeXYWH(0, 1250, W, H - 1250), P(shader=lin(0, 1250, 0, H, [hx("#03031a", 0), hx("#03031a", 0.38)])))
    vignette(c, 0.5)
    caption(c, t)
    arr = np.empty((H, W, 4), np.uint8) if out is None else out
    surface.readPixels(INFO, arr, W * 4)
    bloom(arr)
    g = GRAIN[i % len(GRAIN)]
    rgb_ = arr[:, :, :3].astype(np.int16) + g
    np.clip(rgb_, 0, 255, out=rgb_)
    arr[:, :, :3] = rgb_.astype(np.uint8)
    return arr


def frame_image(t, surface=None):
    s = surface or skia.Surface.MakeRaster(INFO)
    return Image.fromarray(frame(s, int(round(t * FPS)))[:, :, :3].copy())


def worker(f0, f1, path):
    s = skia.Surface.MakeRaster(INFO)
    tmp = path[:-4] + ".part.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    buf = np.empty((H, W, 4), np.uint8)
    for i in range(f0, f1):
        pr.stdin.write(frame(s, i, buf).tobytes())
    pr.stdin.close()
    if pr.wait() == 0:
        os.replace(tmp, path)


def cmd_strip(name, times):
    s = skia.Surface.MakeRaster(INFO)
    ims = [frame_image(t, s).resize((540, 960), Image.LANCZOS) for t in times]
    sheet = Image.new("RGB", (540 * len(ims), 960))
    for k, im in enumerate(ims):
        sheet.paste(im, (540 * k, 0))
    out = os.path.join(QA, name + ".jpg")
    sheet.save(out, quality=90)
    print(out)


def cmd_sheet(name, times, cols=8, scale=0.2):
    s = skia.Surface.MakeRaster(INFO)
    tw, th = int(W * scale), int(H * scale)
    rows = math.ceil(len(times) / cols)
    sheet = Image.new("RGB", (tw * cols, th * rows), (20, 20, 20))
    for k, t in enumerate(times):
        sheet.paste(frame_image(t, s).resize((tw, th), Image.LANCZOS), ((k % cols) * tw, (k // cols) * th))
    out = os.path.join(QA, name + ".jpg")
    sheet.save(out, quality=85)
    print(out)


def cmd_crops(name, args):
    s = skia.Surface.MakeRaster(INFO)
    cache, ims = {}, []
    for k in range(0, len(args), 5):
        t, x, y, w, h = float(args[k]), int(args[k + 1]), int(args[k + 2]), int(args[k + 3]), int(args[k + 4])
        if t not in cache:
            cache[t] = frame_image(t, s)
        im = cache[t].crop((x, y, x + w, y + h))
        ims.append(im.resize((int(w * 600 / h), 600), Image.LANCZOS))
    sheet = Image.new("RGB", (sum(i.width for i in ims) + 10 * (len(ims) - 1), 600), (255, 255, 255))
    x = 0
    for im in ims:
        sheet.paste(im, (x, 0)); x += im.width + 10
    out = os.path.join(QA, name + ".jpg")
    sheet.save(out, quality=92)
    print(out)


if __name__ == "__main__":
    cmd = sys.argv[2]
    if cmd == "strip":
        cmd_strip(sys.argv[3], [float(x) for x in sys.argv[4:]])
    elif cmd == "sheet":
        cmd_sheet(sys.argv[3], [float(x) for x in sys.argv[4:]])
    elif cmd == "full":
        out = os.path.join(QA, sys.argv[3] + ".jpg")
        frame_image(float(sys.argv[4])).save(out, quality=92)
        print(out)
    elif cmd == "crops":
        cmd_crops(sys.argv[3], sys.argv[4:])
    elif cmd == "render":
        nproc = int(sys.argv[3]) if len(sys.argv) > 3 else 2
        for f in os.listdir(OUT):
            if f.startswith("part") or f == "video.mp4":
                os.remove(os.path.join(OUT, f))
        bounds = [round(NFRAMES * k / nproc) for k in range(nproc + 1)]
        procs = []
        for k in range(nproc):
            p = Process(target=worker, args=(bounds[k], bounds[k + 1], f"{OUT}/part{k}.mp4"))
            p.start(); procs.append(p)
        for p in procs:
            p.join()
        missing = [k for k in range(nproc) if not os.path.exists(f"{OUT}/part{k}.mp4")]
        if missing:
            sys.exit(f"render FAILED: parts {missing} missing")
        with open(f"{OUT}/list.txt", "w") as fh:
            for k in range(nproc):
                fh.write(f"file 'part{k}.mp4'\n")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{OUT}/list.txt", "-c", "copy", f"{OUT}/video.mp4"], check=True)
        print("RENDER DONE", NFRAMES, "frames ->", f"{OUT}/video.mp4")
    else:
        sys.exit("unknown command " + cmd)
