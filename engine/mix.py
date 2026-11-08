"""Build the soundtrack for an episode, normalise it to YouTube loudness, and check the levels.

  python3 engine/mix.py EPISODE_DIR

Uses EPISODE_DIR/score.py (build_music/build_sfx) if it exists, otherwise the automatic score driven by
MUSIC_PLAN in EPISODE_DIR/timeline.py. Writes out/mix.wav, out/mix_norm.wav and qa/audio_report.txt.
Exits with code 1 if the narration is not clearly above the music on every line, or loudness is off.
"""
import os, sys, json, subprocess, importlib.util

EP = os.path.abspath(sys.argv[1])
os.environ["EPISODE_DIR"] = EP
ENGINE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, EP)
sys.path.insert(1, ENGINE)

import numpy as np
import soundfile as sf
import audio as A
import timeline as TL

OUT = os.path.join(EP, "out"); QA = os.path.join(EP, "qa")
os.makedirs(OUT, exist_ok=True); os.makedirs(QA, exist_ok=True)

if os.path.exists(os.path.join(EP, "score.py")):
    import score
    mus, sfx = score.build_music(), score.build_sfx()
    src = "custom score.py"
else:
    plan = TL.MUSIC_PLAN
    mus, sfx = A.auto_music(plan), A.auto_sfx(plan)
    src = "auto score (MUSIC_PLAN)"

voice, _ = A.build_voice()
N, SR = A.N, A.SR
speaking = np.zeros(N)
for a, b in zip(TL.T, TL.E):
    speaking[int(a * SR):int(b * SR)] = 1
duck = np.clip(A.lowpass(speaking, 2.0), 0, 1)
mus_gain = (0.55 - 0.43 * duck)[:, None]
m2 = mus / np.max(np.abs(mus)) * 0.55 * mus_gain
s2 = sfx / max(1e-6, np.max(np.abs(sfx))) * 0.45
mix = voice + m2 + s2
mix = mix / np.max(np.abs(mix)) * 0.89
sf.write(os.path.join(OUT, "mix.wav"), mix.astype(np.float32), SR, subtype="FLOAT")


def db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)


report = [f"score: {src}"]
problems = []
for i in range(len(TL.T)):
    a, b = int(TL.T[i] * SR), int(TL.E[i] * SR)
    gap = db(voice[a:b]) - db(m2[a:b])
    report.append(f"line {i:02d}: voice {db(voice[a:b]):6.1f} dB  music {db(m2[a:b]):6.1f} dB  gap {gap:5.1f} dB")
    if gap < 10:
        problems.append(f"line {i} narration only {gap:.1f} dB above music (need >= 10)")

# two-pass loudness normalisation to -14 LUFS / -1.5 dBTP
inp = os.path.join(OUT, "mix.wav"); outp = os.path.join(OUT, "mix_norm.wav")
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", inp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True)
j = r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1]
d = json.loads(j)
flt = ("loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true,aresample=48000"
       % (d["input_i"], d["input_tp"], d["input_lra"], d["input_thresh"], d["target_offset"]))
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", inp, "-af", flt, "-c:a", "pcm_s16le", outp], check=True)
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", outp, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
tail = r.stderr[r.stderr.rfind("Summary:"):]
I = float(tail.split("I:")[1].split("LUFS")[0])
peak = float(tail.split("Peak:")[1].split("dBFS")[0])
report.append(f"final loudness {I:.1f} LUFS (target -14), true peak {peak:.1f} dBFS (max -1.0)")
if abs(I + 14) > 1.0:
    problems.append(f"loudness {I:.1f} LUFS is off target")
if peak > -1.0:
    problems.append(f"true peak {peak:.1f} dBFS too hot")
report += ["PROBLEMS:"] + problems if problems else ["AUDIO OK"]
open(os.path.join(QA, "audio_report.txt"), "w").write("\n".join(report) + "\n")
print("\n".join(report))
sys.exit(1 if problems else 0)
