"""Narration timing, captions, story beats and scene windows. Copy this file for a new episode and edit
GAPS, CAPS, EV, SCENES, TRANS, MUSIC_PLAN and the renderer settings at the bottom."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))

LINES = json.load(open(os.path.join(HERE, "voice", "lines.json")))
FPS = 30
# pause AFTER each line (seconds). One value per line. Longer pauses after big reveals; last one is the outro hold (1.5-1.8).
GAPS = [0.45, 0.75, 0.35, 0.55, 0.35, 0.35, 0.45, 0.30, 0.85, 0.25, 0.35, 0.70, 0.30, 0.60, 1.75]
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
    ["Right now, Earth stops spinning."],
    ["Not slows down.", "|", "Stops."],
    ["At the equator, you were moving east", "at over sixteen hundred", "kilometers an hour."],
    ["The air keeps going,", "in winds stronger than any hurricane."],
    ["But the strangest change is slower."],
    ["Earth's spin makes the planet,", "and its oceans, bulge at the middle."],
    ["Without the spin, that water", "slides toward the poles."],
    ["Two giant oceans would cover", "the top and bottom of the world."],
    ["And around the middle,", "one enormous continent."],
    ["Days change too."],
    ["The Sun would rise and set", "just once a year."],
    ["Six months of daylight.", "|", "Six months of night."],
    ["Don't worry.", "|", "Nothing is about to stop Earth's spin."],
    ["It is slowing, by about", "two thousandths of a second", "per century."],
    ["So right now,", "you're still spinning with it."],
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
    "stop": Wd(0, 3),
    "stops2": Wd(1, 3),
    "equator": Wd(2, 2),
    "you": Wd(2, 3),
    "east": Wd(2, 6),
    "sixteen": Wd(2, 9),
    "hour": Wd(2, 13),
    "air": Wd(3, 1),
    "winds": Wd(3, 5),
    "hurricane": Wd(3, 9),
    "slower": Wd(4, 5),
    "spin": Wd(5, 1),
    "bulge": Wd(5, 8),
    "without": Wd(6, 0),
    "slides": Wd(6, 5),
    "poles": Wd(6, 8),
    "oceans": Wd(7, 2),
    "top": Wd(7, 6),
    "bottom": Wd(7, 8),
    "middle": Wd(8, 3),
    "continent": Wd(8, 6),
    "days": Wd(9, 0),
    "sun": Wd(10, 1),
    "once": Wd(10, 7),
    "daylight": Wd(11, 3),
    "night": Wd(11, 7),
    "worry": Wd(12, 1),
    "slowing": Wd(13, 2),
    "two": Wd(13, 5),
    "century": Wd(13, 11),
    "spinning": Wd(14, 5),
}

# scene windows: (name, start, end). Consecutive scenes overlap by X seconds (the transition).
X = 0.4
SCENES = [
    ("sky_open", 0.0, T[2] - 0.05),
    ("globe_speed", T[2] - 0.05 - X, T[3] - 0.10),
    ("winds", T[3] - 0.10 - X, T[4] - 0.10),
    ("bulge", T[4] - 0.10 - X, T[7] - 0.10),
    ("newworld", T[7] - 0.10 - X, T[9] - 0.15),
    ("dayyear", T[9] - 0.15 - X, T[12] - 0.15),
    ("slowing", T[12] - 0.15 - X, T[14] - 0.15),
    ("sky_end", T[14] - 0.15 - X, DURATION + 1),
]
# transition INTO each scene: slide_up | slide_left | zoom_in | zoom_out | fade
TRANS = {"globe_speed": "zoom_out", "winds": "slide_left", "bulge": "zoom_out", "newworld": "zoom_in",
         "dayyear": "slide_up", "slowing": "slide_left", "sky_end": "fade"}

# music: moods are wonder / tension / resolve (see engine/audio.py for every key)
MUSIC_PLAN = {
    "sections": [("wonder", 0.0, EV["stop"]), ("tension", EV["stop"] + 0.3, T[4] - 0.1), ("wonder", T[4] - 0.1, T[9] - 0.1),
                 ("wonder", T[9] - 0.1, T[14] - 0.3), ("resolve", T[14] - 0.3, DURATION)],
    "hush": [(EV["stop"], EV["stop"] + 0.3)],
    "hang": [EV["stop"] + 0.05],
    "pops": [EV["you"], EV["sixteen"], EV["hurricane"], EV["bulge"], EV["top"], EV["bottom"], EV["once"],
             EV["daylight"], EV["night"], EV["two"]],
    "drops": [],
    "rises": [EV["continent"], E[14] + 0.15],
    "booms": [EV["stop"], EV["stops2"]],
    "ticks": [],
}

# renderer settings
STATIC_SCENES = ["sky_open", "sky_end"]   # these scenes run their own camera
DUSTY_SCENES = ["globe_speed", "bulge", "dayyear", "slowing"]
ZOOM_FOCUS = {"newworld": (540, 780)}
PLANNED_JUMPS = [EV["stop"], EV["stops2"]]

if __name__ == "__main__":
    print("duration", DURATION, "frames", NFRAMES)
    for i, (a, b) in enumerate(zip(T, E)):
        print(i, round(a, 2), round(b, 2), LINES[i]["text"])
    print({k: round(v, 2) for k, v in EV.items()})
    for s in SCENES:
        print(s[0], round(s[1], 2), round(s[2], 2))
