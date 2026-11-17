"""Narration timing, captions, story beats and scene windows. Copy this file for a new episode and edit
GAPS, CAPS, EV, SCENES, TRANS, MUSIC_PLAN and the renderer settings at the bottom."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))

LINES = json.load(open(os.path.join(HERE, "voice", "lines.json")))
FPS = 30
# pause AFTER each line (seconds). One value per line. Longer pauses after big reveals; last one is the outro hold (1.5-1.8).
GAPS = [0.50, 0.55, 0.35, 0.50, 0.55, 0.45, 0.90, 0.30, 0.55, 0.35, 0.40, 0.40, 0.40, 0.75, 0.30, 1.70]
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
    ["What if you could", "see like a bee?"],
    ["A whole new colour", "would switch on."],
    ["Sunlight carries invisible", "ultraviolet light."],
    ["But the lens in your", "eye blocks it."],
    ["Bees can see it,", "and flowers are", "painted for them."],
    ["Take a sunflower.", "|", "To you, it's plain yellow."],
    ["But in ultraviolet,", "a giant bullseye appears."],
    ["Many flowers hide", "marks like this."],
    ["Secret landing strips", "that point bees to the food."],
    ["Now head north,", "to the Arctic."],
    ["Reindeer can see", "ultraviolet too."],
    ["Snow reflects it,", "so the land shines bright."],
    ["But lichen, their food,", "soaks it up and looks dark."],
    ["And to them, a white wolf", "looks dark against the snow."],
    ["So every flower around you", "hides a message,"],
    ["written in a colour", "only a bee can see."],
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
    "bee": Wd(0, 7),
    "colour": Wd(1, 3), "switch": Wd(1, 5), "on": Wd(1, 6),
    "sunlight": Wd(2, 0), "ultra": Wd(2, 3),
    "lens": Wd(3, 2), "blocks": Wd(3, 6),
    "bees": Wd(4, 0), "see": Wd(4, 2), "flowers": Wd(4, 5), "painted": Wd(4, 7),
    "sunflower": Wd(5, 2), "plain": Wd(5, 6), "yellow": Wd(5, 7),
    "uv": Wd(6, 2), "bullseye": Wd(6, 5), "appears": Wd(6, 6),
    "many": Wd(7, 0), "marks": Wd(7, 3),
    "strips": Wd(8, 2), "point": Wd(8, 4), "food": Wd(8, 8),
    "north": Wd(9, 2), "arctic": Wd(9, 5),
    "reindeer": Wd(10, 0), "uv2": Wd(10, 3),
    "snow": Wd(11, 0), "shines": Wd(11, 6),
    "lichen": Wd(12, 1), "food2": Wd(12, 3), "soaks": Wd(12, 4), "dark": Wd(12, 9),
    "wolf": Wd(13, 5), "dark2": Wd(13, 7), "snow2": Wd(13, 10),
    "every": Wd(14, 1), "message": Wd(14, 7),
    "colour2": Wd(15, 3), "bee2": Wd(15, 6), "seeend": Wd(15, 8),
}

X = 0.4
SCENES = [
    ("open", 0.0, T[2] - 0.10),
    ("eye", T[2] - 0.10 - X, T[4] - 0.10),
    ("bee", T[4] - 0.10 - X, T[5] - 0.10),
    ("sunflower", T[5] - 0.10 - X, T[7] - 0.10),
    ("guides", T[7] - 0.10 - X, T[9] - 0.10),
    ("north", T[9] - 0.10 - X, T[10] - 0.10),
    ("arctic", T[10] - 0.10 - X, T[14] - 0.10),
    ("end", T[14] - 0.10 - X, DURATION + 1),
]
TRANS = {"eye": "slide_up", "bee": "zoom_out", "sunflower": "slide_left", "guides": "fade", "north": "slide_up",
         "arctic": "zoom_in", "end": "fade"}

MUSIC_PLAN = {
    "sections": [("wonder", 0.0, T[2] - 0.2), ("tension", T[2] - 0.2, T[4] - 0.2), ("wonder", T[4] - 0.2, T[9] - 0.2),
                 ("tension", T[9] - 0.2, T[14] - 0.3), ("resolve", T[14] - 0.3, DURATION)],
    "hush": [(EV["uv"] - 0.3, EV["bullseye"])],
    "hang": [EV["bullseye"]],
    "pops": [EV["on"], EV["blocks"], EV["see"], EV["plain"], EV["strips"], EV["arctic"], EV["food2"]],
    "drops": [EV["dark2"]],
    "rises": [EV["uv"] - 0.2, EV["snow"] - 0.2, E[15] + 0.15],
    "booms": [EV["bullseye"]],
    "ticks": [],
}

# renderer settings
STATIC_SCENES = ["open", "end"]            # scenes that run their own camera (no automatic slow drift)
DUSTY_SCENES = ["eye", "north"]       # space scenes that get floating foreground dust
ZOOM_FOCUS = {"arctic": (540, 528)}               # for zoom_in transitions: {"next_scene": (x, y) point to zoom through}
PLANNED_JUMPS = []            # times of deliberate sudden big changes (flashes, pops) the glitch scan should allow

if __name__ == "__main__":
    print("duration", DURATION, "frames", NFRAMES)
    for i, (a, b) in enumerate(zip(T, E)):
        print(i, round(a, 2), round(b, 2), LINES[i]["text"])
    print({k: round(v, 2) for k, v in EV.items()})
    for s in SCENES:
        print(s[0], round(s[1], 2), round(s[2], 2))
