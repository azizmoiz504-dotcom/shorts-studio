"""Narration timing, captions and scene windows."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))

LINES = json.load(open(os.path.join(HERE, "voice", "lines.json")))
FPS = 30
GAPS = [0.45, 0.70, 0.55, 0.30, 0.35, 0.60, 0.80, 0.70, 0.35, 0.60, 0.60, 0.60, 0.80, 0.90, 0.55, 1.75]
LEAD = 0.35

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
    """absolute start time of word k in line i"""
    return T[i] + WORDS[i][k]["t0"]


def We(i, k):
    return T[i] + WORDS[i][k]["t1"]


S2 = Wd(2, 5)
S8 = Wd(8, 5)
S13 = Wd(13, 3)

# caption chunks per line; "|" separates sentences that have a measured pause; *word* = highlight
CAPS = [
    ["Tonight, the Moon disappears."],
    ["Just... gone."],
    ["At first, you'd barely notice.", "|", "The night gets darker."],
    ["But the oceans would."],
    ["The Moon drives most of Earth's tides."],
    ["Without it, they'd shrink", "to about a third."],
    ["Coral reefs that spawn by moonlight", "would lose their calendar."],
    ["Then comes the slow, scary part."],
    ["Earth spins on a tilt.", "|", "That's what gives us seasons."],
    ["And the Moon holds that tilt steady,", "like a hand on a spinning top."],
    ["Without it, over millions of years,", "the tilt could start to wander."],
    ["Mars has no big moon,", "and its tilt has swung wildly,", "reshaping its climate again and again."],
    ["For Earth, that could mean", "seasons more extreme", "than anything we've ever known."],
    ["No more eclipses.", "|", "No more moonlight."],
    ["So tonight, look up,", "and say thanks."],
    ["It's still there."],
]


def build_captions():
    out = []
    for i, chunks in enumerate(CAPS):
        k = 0
        for ch in chunks:
            if ch == "|":
                continue
            toks = ch.replace("*", "").split(" ")
            ws = []
            for tok in toks:
                ws.append({"text": tok, "t0": Wd(i, k), "t1": We(i, k)})
                k += 1
            out.append({"words": ws, "t0": ws[0]["t0"] - 0.10, "t1": ws[-1]["t1"] + 0.35, "line": i})
        assert k == len(WORDS[i]), (i, k, len(WORDS[i]))
    for n, c in enumerate(out):
        if n + 1 < len(out):
            c["t1"] = min(c["t1"], out[n + 1]["t0"])
        else:
            c["t1"] = min(c["t1"] + 0.8, DURATION - 0.1)
    return out


CAPTIONS = build_captions()

EV = {
    "vanish": Wd(0, 3),
    "gone": Wd(1, 1),
    "darker": Wd(2, 8),
    "tide_card": Wd(4, 0),
    "tide_vanish": Wd(5, 0),
    "third": Wd(5, 7),
    "reef_card": Wd(6, 0) + 0.15,
    "moonlight": Wd(6, 5),
    "reef_lose": Wd(6, 7),
    "scary": Wd(7, 4),
    "tilt": Wd(8, 4),
    "seasons": Wd(8, 9),
    "orbit": Wd(9, 2),
    "steady": Wd(9, 6),
    "top": Wd(9, 7),
    "hand": Wd(9, 9),
    "wobble": Wd(10, 0),
    "millions": Wd(10, 3),
    "wander": Wd(10, 11),
    "mars": Wd(11, 0),
    "wildly": Wd(11, 10),
    "climate": Wd(11, 13),
    "extreme": Wd(12, 7),
    "eclipses": Wd(13, 2),
    "lookup": Wd(14, 2),
    "thanks": Wd(14, 6),
    "back": Wd(15, 1),
}

# scene windows: (name, start, end). Consecutive scenes overlap by the transition length.
X = 0.4
SCENES = [
    ("land_open", 0.0, T[3] - 0.10),
    ("tides", T[3] - 0.10 - X, T[6] - 0.15),
    ("reef", T[6] - 0.15 - X, T[7] - 0.10),
    ("space", T[7] - 0.10 - X, T[11] - 0.12),
    ("mars", T[11] - 0.12 - X, T[12] - 0.12),
    ("extreme", T[12] - 0.12 - X, T[13] - 0.12),
    ("eclipse", T[13] - 0.12 - X, S13 - 0.08),
    ("land_end", S13 - 0.08 - X, DURATION + 1),
]
TRANS = {"tides": "slide_up", "reef": "zoom_in", "space": "zoom_out", "mars": "slide_left",
         "extreme": "slide_left", "eclipse": "fade", "land_end": "fade"}

if __name__ == "__main__":
    print("duration", DURATION, "frames", NFRAMES)
    for i, (a, b) in enumerate(zip(T, E)):
        print(i, round(a, 2), round(b, 2), LINES[i]["text"])
    print({k: round(v, 2) for k, v in EV.items()})
    for s in SCENES:
        print(s[0], round(s[1], 2), round(s[2], 2))

# renderer settings for this episode
STATIC_SCENES = ["land_open", "land_end"]                  # these scenes run their own camera moves
DUSTY_SCENES = ["tides", "space", "mars", "extreme", "eclipse"]
ZOOM_FOCUS = {"reef": (540, 980)}                           # zoom-through point (Earth's ocean) into the reef
PLANNED_JUMPS = [EV["vanish"] + 0.3, EV["top"], EV["back"]]   # deliberate big visual changes (glitch scan ignores these)
