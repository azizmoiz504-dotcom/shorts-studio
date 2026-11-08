"""Final checks + encode. Run after render.py render and mix.py.

  python3 engine/finish.py EPISODE_DIR

1. Checks out/video.mp4 has exactly NFRAMES frames.
2. Glitch scan: finds single-frame pops (something appearing/disappearing in one frame) and big jumps that are
   not at a planned scene transition. Writes qa/glitch_report.txt.
3. Muxes video + out/mix_norm.wav into out/final.mp4 (H.264 CRF 20, AAC 256k, faststart) and verifies it.
Exits with code 1 on any problem. Big jumps at moments listed in timeline.PLANNED_JUMPS are allowed.
"""
import os, sys, subprocess, json

EP = os.path.abspath(sys.argv[1])
sys.path.insert(0, EP)
import numpy as np
import timeline as TL

OUT = os.path.join(EP, "out"); QA = os.path.join(EP, "qa")
os.makedirs(QA, exist_ok=True)
vid = os.path.join(OUT, "video.mp4")
problems, rep = [], []

n = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries",
                        "stream=nb_read_frames", "-of", "csv=p=0", vid], capture_output=True, text=True).stdout.strip())
rep.append(f"frames {n} (expected {TL.NFRAMES})")
if n != TL.NFRAMES:
    problems.append("frame count mismatch - render incomplete")

raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", vid, "-vf", "scale=216:384,format=gray",
                      "-f", "rawvideo", "-"], capture_output=True).stdout
f = np.frombuffer(raw, np.uint8).reshape(-1, 384, 216).astype(np.float32)
f[:, 250:310, :] = 0  # ignore the caption band
d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
trans = [s[1] for s in TL.SCENES[1:]] + [s[2] for s in TL.SCENES[:-1]]
planned = list(getattr(TL, "PLANNED_JUMPS", []))
for i in range(3, len(d) - 3):
    t = (i + 1) / TL.FPS
    ctx = max(np.median(d[i - 3:i]), np.median(d[i + 1:i + 4]))
    if d[i] > 2.2 and d[i] > 3.0 * ctx:
        problems.append(f"single-frame pop at {t:.2f}s (diff {d[i]:.1f}) - something appears/disappears without animating")
thr = np.percentile(d, 99.5)
for i in np.argsort(d)[::-1][:30]:
    t = (i + 1) / TL.FPS
    if d[i] < max(6.0, thr):
        break
    near_t = min(abs(t - x) for x in trans)
    near_p = min([abs(t - x) for x in planned] or [99])
    if near_t > 0.6 and near_p > 0.6:
        problems.append(f"unplanned big jump at {t:.2f}s (diff {d[i]:.1f}) - inspect frames around it")
rep.append(f"median frame change {np.median(d):.2f}, 99.5th pct {thr:.2f}")

final = os.path.join(OUT, "final.mp4")
tmp = os.path.join(OUT, "final.part.mp4")
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", vid, "-i", os.path.join(OUT, "mix_norm.wav"),
                "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                "-profile:v", "high", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", "-shortest", tmp], check=True)
os.replace(tmp, final)
pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_type,width,height",
                                "-of", "json", final], capture_output=True, text=True).stdout)
dur = float(pr["format"]["duration"]); size = int(pr["format"]["size"]) / 1e6
kinds = sorted(s["codec_type"] for s in pr["streams"])
vs = [s for s in pr["streams"] if s["codec_type"] == "video"][0]
rep.append(f"final.mp4 {dur:.2f}s {size:.1f} MB {vs['width']}x{vs['height']} streams {kinds}")
if kinds != ["audio", "video"] or (vs["width"], vs["height"]) != (1080, 1920):
    problems.append("final file streams/size wrong")
if not (15 <= dur <= 59.9):
    problems.append(f"duration {dur:.1f}s outside 15-59.9s")
if size > 95:
    problems.append(f"file {size:.0f} MB is too big for the GitHub hand-off (max 95 MB)")
rep += ["PROBLEMS:"] + problems if problems else ["FINISH OK"]
open(os.path.join(QA, "glitch_report.txt"), "w").write("\n".join(rep) + "\n")
print("\n".join(rep))
sys.exit(1 if problems else 0)
