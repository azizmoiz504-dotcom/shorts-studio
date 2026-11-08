"""Record the narration for an episode and time every word.

  python3 engine/voice.py EPISODE_DIR

Reads EPISODE_DIR/script.json: {"voice": "am_michael", "speed": 0.94, "lines": ["...", ...]}
Writes EPISODE_DIR/voice/line_XX.wav, lines.json (durations) and words.json (word start/end per line).
Rules for script lines: write numbers as words ("twenty three"), no symbols, no abbreviations - the word
aligner needs plain words. Exits with code 1 if any line fails to align word-for-word.
"""
import os, sys, json, re
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

EP = os.path.abspath(sys.argv[1])
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VO = os.path.join(EP, "voice")
os.makedirs(VO, exist_ok=True)
S = json.load(open(os.path.join(EP, "script.json")))

from kokoro_onnx import Kokoro
k = Kokoro(os.path.join(ROOT, "models", "kokoro-v1.0.onnx"), os.path.join(ROOT, "models", "voices-v1.0.bin"))
info = []
for i, line in enumerate(S["lines"]):
    samples, sr = k.create(line, voice=S.get("voice", "am_michael"), speed=float(S.get("speed", 0.94)), lang="en-us")
    samples = np.asarray(samples, dtype=np.float32)
    a = np.abs(samples)
    idx = np.where(a > 0.01 * a.max())[0]
    s0, e0 = max(0, idx[0] - int(0.02 * sr)), min(len(samples), idx[-1] + int(0.06 * sr))
    samples = samples[s0:e0]
    sf.write(os.path.join(VO, f"line_{i:02d}.wav"), samples, sr)
    info.append({"i": i, "text": line, "dur": len(samples) / sr, "sr": sr})
    print(f"line {i:02d} {len(samples) / sr:5.2f}s  {line}")
json.dump(info, open(os.path.join(VO, "lines.json"), "w"), indent=1)
print("total speech", round(sum(x["dur"] for x in info), 1), "s")

# word alignment
from pocketsphinx import Decoder
dec = Decoder(samprate=16000, bestpath=False, loglevel="FATAL")
out, bad = [], []
for ln in info:
    x, sr = sf.read(os.path.join(VO, f"line_{ln['i']:02d}.wav"))
    pad = np.zeros(int(0.15 * sr))
    y = resample_poly(np.concatenate([pad, x, pad]), 16000, sr)
    pcm = (np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()
    words = re.sub(r"[^a-z' ]", " ", ln["text"].lower()).split()
    dec.set_align_text(" ".join(words))
    dec.start_utt(); dec.process_raw(pcm, full_utt=True); dec.end_utt()
    segs = [(s.word, s.start_frame / 100 - 0.15, (s.end_frame + 1) / 100 - 0.15) for s in dec.seg()
            if s.word not in ("<s>", "</s>", "<sil>", "(NULL)")]
    segs = [(re.sub(r"\(\d+\)", "", w), max(0, a), b) for w, a, b in segs]
    ok = [w for w, _, _ in segs] == words
    if not ok:
        bad.append(ln["i"])
    out.append({"i": ln["i"], "words": [{"w": w, "t0": a, "t1": b} for w, a, b in segs], "ok": ok})
json.dump(out, open(os.path.join(VO, "words.json"), "w"), indent=1)
if bad:
    sys.exit(f"ALIGNMENT FAILED on lines {bad}: rewrite those lines in plain words (numbers spelled out) and rerun")
print("VOICE OK - all", len(out), "lines aligned word-for-word")
