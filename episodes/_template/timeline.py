"""Narration timing, captions, story beats and scene windows. Copy this file for a new episode and edit
GAPS, CAPS, EV, SCENES, TRANS, MUSIC_PLAN and the renderer settings at the bottom."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))

LINES = json.load(open(os.path.join(HERE, "voice", "lines.json")))
FPS = 30
# pause AFTER each line (seconds). One value per line. Longer pauses after big reveals; last one is the outro hold (1.5-1.8).
GAPS = [0.55, 0.60, 1.75]
LEAD = 0.35
assert len(GAPS) == len(LINES), "GAPS needs one value per script line"

T, E = [], []
t = LEAD
for ln, g in zip(LINES, GAPS):
    T.append(t)
    E.append(t + ln["dur"])
    t = t + ln["dur"] + g
DURATION = round(t * FPS) / FPS
NFRAMES = int(round(DURATION * FPS))

WORDS = [ln["words"] for ln in json.load(open(os.path.join(HERE, "voice", "words.json")))]


def Wd(i, k):
    """absolute start time of word k (0-based) in line i - use these to time every animation beat to the voice"""
    return T[i] + WORDS[i][k]["t0"]


def We(i, k):
    return T[i] + WORDS[i][k]["t1"]


# Caption chunks per line (each chunk shows on screen at once, max ~7 words; "|" = skip marker between sentences).
# The words in each line's chunks must be EXACTLY the line's words in order (punctuation is fine).
CAPS = [
    ["What if Earth had rings like Saturn?"],
    ["Every night, a glowing bridge", "would arc across the sky."],
    ["And it's still there."],
]


def build_captions():
    out = []
    for i, chunks in enumerate(CAPS):
        k = 0
        for ch in chunks:
            if ch == "|":
                continue
            ws = []
            for tok in ch.replace("*", "").split(" "):
                ws.append({"text": tok, "t0": Wd(i, k), "t1": We(i, k)})
                k += 1
            out.append({"words": ws, "t0": ws[0]["t0"] - 0.10, "t1": ws[-1]["t1"] + 0.35, "line": i})
        assert k == len(WORDS[i]), f"caption words for line {i} ({k}) != spoken words ({len(WORDS[i])})"
    for n, c in enumerate(out):
        c["t1"] = min(c["t1"], out[n + 1]["t0"]) if n + 1 < len(out) else min(c["t1"] + 0.8, DURATION - 0.1)
    return out


CAPTIONS = build_captions()

# story beats, each pinned to a spoken word
EV = {
    "rings_appear": Wd(0, 4),
    "bridge": Wd(1, 4),
    "end": Wd(2, 2),
}

# scene windows: (name, start, end). Consecutive scenes overlap by X seconds (the transition).
X = 0.4
SCENES = [
    ("open", 0.0, T[1] - 0.10),
    ("sky", T[1] - 0.10 - X, DURATION + 1),
]
# transition INTO each scene: slide_up | slide_left | zoom_in | zoom_out | fade
TRANS = {"sky": "slide_up"}

# music: moods are wonder / tension / resolve (see engine/audio.py for every key)
MUSIC_PLAN = {
    "sections": [("wonder", 0.0, T[2]), ("resolve", T[2], DURATION)],
    "hush": [],
    "hang": [],
    "pops": [EV["rings_appear"]],
    "drops": [],
    "rises": [EV["end"]],
    "booms": [],
    "ticks": [],
}

# renderer settings
STATIC_SCENES = []            # scenes that run their own camera (no automatic slow drift)
DUSTY_SCENES = ["open"]       # space scenes that get floating foreground dust
ZOOM_FOCUS = {}               # for zoom_in transitions: {"next_scene": (x, y) point to zoom through}
PLANNED_JUMPS = []            # times of deliberate sudden big changes (flashes, pops) the glitch scan should allow

if __name__ == "__main__":
    print("duration", DURATION, "frames", NFRAMES)
    for i, (a, b) in enumerate(zip(T, E)):
        print(i, round(a, 2), round(b, 2), LINES[i]["text"])
    print({k: round(v, 2) for k, v in EV.items()})
    for s in SCENES:
        print(s[0], round(s[1], 2), round(s[2], 2))
