"""Narration timing, captions, story beats and scene windows. Copy this file for a new episode and edit
GAPS, CAPS, EV, SCENES, TRANS, MUSIC_PLAN and the renderer settings at the bottom."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))

LINES = json.load(open(os.path.join(HERE, "voice", "lines.json")))
FPS = 30
# pause AFTER each line (seconds). One value per line. Longer pauses after big reveals; last one is the outro hold (1.5-1.8).
GAPS = [0.45, 0.60, 0.45, 0.35, 0.30, 0.45, 0.40, 0.30, 0.55, 0.30, 0.30, 0.60, 0.25, 0.30, 0.55, 0.30, 1.75]
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
    ["Tonight, you stop sleeping."],
    ["Not one minute.", "|", "Ever again."],
    ["You'd win back a third of your life."],
    ["But your brain would lose", "its night shift."],
    ["In deep sleep, slow waves", "of fluid wash through it."],
    ["Scientists think they help", "rinse away the day's waste."],
    ["Your brain also replays your day,", "and saves what matters."],
    ["Without sleep,", "all that work piles up."],
    ["The waste stays,", "and new memories struggle to stick."],
    ["Stay awake long enough,", "and something strange happens."],
    ["Tiny parts of your brain", "fall asleep anyway."],
    ["For a few seconds,", "even with your eyes open."],
    ["Dolphins have a clever trick."],
    ["They sleep with one half", "of their brain at a time."],
    ["One half rests,", "while the other half keeps watch."],
    ["So tonight,", "when the lights go out,"],
    ["your brain starts its night shift."],
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
    "stop": Wd(0, 2),
    "minute": Wd(1, 2),
    "ever": Wd(1, 3),
    "win": Wd(2, 1),
    "third": Wd(2, 4),
    "brain": Wd(3, 2),
    "night": Wd(3, 6),
    "deep": Wd(4, 1),
    "waves": Wd(4, 4),
    "wash": Wd(4, 7),
    "rinse": Wd(5, 4),
    "waste": Wd(5, 8),
    "replays": Wd(6, 3),
    "saves": Wd(6, 7),
    "without": Wd(7, 0),
    "piles": Wd(7, 5),
    "waste2": Wd(8, 1),
    "memories": Wd(8, 5),
    "stick": Wd(8, 8),
    "awake": Wd(9, 1),
    "strange": Wd(9, 6),
    "tiny": Wd(10, 0),
    "asleep": Wd(10, 6),
    "seconds": Wd(11, 3),
    "eyes": Wd(11, 7),
    "dolphins": Wd(12, 0),
    "trick": Wd(12, 4),
    "half": Wd(13, 4),
    "time": Wd(13, 10),
    "rests": Wd(14, 2),
    "other": Wd(14, 5),
    "watch": Wd(14, 8),
    "tonight": Wd(15, 1),
    "out": Wd(15, 6),
    "shift": Wd(16, 5),
}

# scene windows: (name, start, end). Consecutive scenes overlap by X seconds (the transition).
X = 0.4
SCENES = [
    ("cabin_open", 0.0, T[2] - 0.10),
    ("life", T[2] - 0.10 - X, T[3] - 0.10),
    ("brain_sleep", T[3] - 0.10 - X, T[7] - 0.10),
    ("pileup", T[7] - 0.10 - X, T[9] - 0.10),
    ("local", T[9] - 0.10 - X, T[12] - 0.10),
    ("dolphin", T[12] - 0.10 - X, T[15] - 0.10),
    ("cabin_end", T[15] - 0.10 - X, DURATION + 1),
]
# transition INTO each scene: slide_up | slide_left | zoom_in | zoom_out | fade
TRANS = {"life": "zoom_out", "brain_sleep": "slide_up", "pileup": "slide_left", "local": "zoom_in",
         "dolphin": "slide_up", "cabin_end": "fade"}

# music: moods are wonder / tension / resolve (see engine/audio.py for every key)
MUSIC_PLAN = {
    "sections": [("wonder", 0.0, T[7] - 0.2), ("tension", T[7] - 0.2, T[12] - 0.2), ("wonder", T[12] - 0.2, T[15] - 0.3),
                 ("resolve", T[15] - 0.3, DURATION)],
    "hush": [(EV["asleep"] - 0.05, EV["asleep"] + 0.6)],
    "hang": [EV["asleep"]],
    "pops": [EV["third"], EV["night"], EV["saves"], EV["eyes"], EV["half"], EV["watch"]],
    "drops": [EV["asleep"], EV["out"]],
    "rises": [EV["brain"], EV["dolphins"], E[16] + 0.15],
    "booms": [EV["stop"]],
    "ticks": [],
}

# renderer settings
STATIC_SCENES = ["cabin_open", "cabin_end"]   # these scenes run their own camera
DUSTY_SCENES = ["life", "brain_sleep", "pileup", "local"]
ZOOM_FOCUS = {"local": (540, 760)}
PLANNED_JUMPS = [EV["stop"]]

if __name__ == "__main__":
    print("duration", DURATION, "frames", NFRAMES)
    for i, (a, b) in enumerate(zip(T, E)):
        print(i, round(a, 2), round(b, 2), LINES[i]["text"])
    print({k: round(v, 2) for k, v in EV.items()})
    for s in SCENES:
        print(s[0], round(s[1], 2), round(s[2], 2))
