"""Narration timing, captions, story beats and scene windows. Copy this file for a new episode and edit
GAPS, CAPS, EV, SCENES, TRANS, MUSIC_PLAN and the renderer settings at the bottom."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))

LINES = json.load(open(os.path.join(HERE, "voice", "lines.json")))
FPS = 30
# pause AFTER each line (seconds). One value per line. Longer pauses after big reveals; last one is the outro hold (1.5-1.8).
GAPS = [0.55, 0.45, 0.35, 0.30, 0.60, 0.90, 0.45, 0.50, 0.35, 0.50, 0.30, 0.45, 0.50, 0.35, 0.30, 1.70]
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
    ["What if the Sun vanished right now?"],
    ["For eight minutes,", "you wouldn't even know."],
    ["Its last light would still", "be racing toward us."],
    ["Even its gravity takes", "that long to get here."],
    ["So Earth keeps circling,", "around nothing."],
    ["Then, the lights go out."],
    ["The Moon goes dark too.", "|", "It only shines", "with borrowed sunlight."],
    ["And Earth sails off", "in a straight line."],
    ["Within a week,", "the whole surface", "drops below freezing."],
    ["After a year, colder than", "minus seventy degrees Celsius."],
    ["The oceans freeze over,", "but only on top."],
    ["Under that lid of ice,", "deep water could stay", "liquid for centuries."],
    ["And deep underground,", "tiny microbes could survive,", "warmed by Earth's own heat."],
    ["Good news.", "|", "The Sun has about", "five billion years left."],
    ["So tomorrow, catch the sunrise."],
    ["That light is only", "eight minutes old."],
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
    "sun": Wd(0, 3), "vanished": Wd(0, 4), "now": Wd(0, 6),
    "eight": Wd(1, 1), "know": Wd(1, 6),
    "light": Wd(2, 2), "racing": Wd(2, 6), "us": Wd(2, 8),
    "gravity": Wd(3, 2), "here": Wd(3, 8),
    "circling": Wd(4, 3), "nothing": Wd(4, 5),
    "lights": Wd(5, 2), "out": Wd(5, 4),
    "moon": Wd(6, 1), "dark": Wd(6, 3), "borrowed": Wd(6, 9),
    "sails": Wd(7, 2), "straight": Wd(7, 6),
    "week": Wd(8, 2), "freezing": Wd(8, 8),
    "year": Wd(9, 2), "colder": Wd(9, 3), "seventy": Wd(9, 6),
    "oceans": Wd(10, 1), "freeze": Wd(10, 2), "top": Wd(10, 7),
    "lid": Wd(11, 2), "deep": Wd(11, 5), "liquid": Wd(11, 9), "centuries": Wd(11, 11),
    "underground": Wd(12, 2), "microbes": Wd(12, 4), "survive": Wd(12, 6), "heat": Wd(12, 11),
    "good": Wd(13, 0), "sun2": Wd(13, 3), "five": Wd(13, 6), "left": Wd(13, 9),
    "tomorrow": Wd(14, 1), "sunrise": Wd(14, 4),
    "light2": Wd(15, 1), "eight2": Wd(15, 4), "old": Wd(15, 6),
}

X = 0.4
SCENES = [
    ("open", 0.0, T[1] - 0.10),
    ("day", T[1] - 0.10 - X, T[2] - 0.10),
    ("race", T[2] - 0.10 - X, T[5] - 0.10),
    ("out", T[5] - 0.10 - X, T[7] - 0.10),
    ("drift", T[7] - 0.10 - X, T[8] - 0.10),
    ("freeze", T[8] - 0.10 - X, T[10] - 0.10),
    ("ocean", T[10] - 0.10 - X, T[12] - 0.10),
    ("under", T[12] - 0.10 - X, T[13] - 0.10),
    ("back", T[13] - 0.10 - X, DURATION + 1),
]
TRANS = {"day": "slide_up", "race": "zoom_out", "out": "fade", "drift": "slide_left", "freeze": "slide_up",
         "ocean": "zoom_in", "under": "zoom_in", "back": "fade"}

MUSIC_PLAN = {
    "sections": [("wonder", 0.0, T[2] - 0.2), ("tension", T[2] - 0.2, EV["out"] - 0.05), ("wonder", T[6] - 0.3, T[8] - 0.2),
                 ("tension", T[8] - 0.2, T[12] - 0.3), ("wonder", T[12] - 0.3, T[13] - 0.2), ("resolve", T[13] - 0.2, DURATION)],
    "hush": [(EV["out"] - 0.05, T[6] - 0.3)],
    "hang": [EV["out"]],
    "pops": [EV["eight"], EV["gravity"], EV["borrowed"], EV["week"], EV["year"], EV["liquid"], EV["microbes"], EV["five"], EV["eight2"]],
    "drops": [EV["vanished"], EV["dark"]],
    "rises": [EV["good"], E[15] + 0.15],
    "booms": [EV["out"]],
    "ticks": [(EV["light"], EV["out"] - 0.3, 14)],
}

# renderer settings
STATIC_SCENES = ["open", "back"]            # scenes that run their own camera (no automatic slow drift)
DUSTY_SCENES = ["open", "race", "drift", "back"]       # space scenes that get floating foreground dust
ZOOM_FOCUS = {"ocean": (540, 1000), "under": (540, 1250)}               # for zoom_in transitions: {"next_scene": (x, y) point to zoom through}
PLANNED_JUMPS = [EV["vanished"], EV["out"], EV["good"]]            # times of deliberate sudden big changes (flashes, pops) the glitch scan should allow

if __name__ == "__main__":
    print("duration", DURATION, "frames", NFRAMES)
    for i, (a, b) in enumerate(zip(T, E)):
        print(i, round(a, 2), round(b, 2), LINES[i]["text"])
    print({k: round(v, 2) for k, v in EV.items()})
    for s in SCENES:
        print(s[0], round(s[1], 2), round(s[2], 2))
