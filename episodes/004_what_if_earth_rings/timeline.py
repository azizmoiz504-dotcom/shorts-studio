"""Narration timing, captions, story beats and scene windows. Copy this file for a new episode and edit
GAPS, CAPS, EV, SCENES, TRANS, MUSIC_PLAN and the renderer settings at the bottom."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))

LINES = json.load(open(os.path.join(HERE, "voice", "lines.json")))
FPS = 30
# pause AFTER each line (seconds). One value per line. Longer pauses after big reveals; last one is the outro hold (1.5-1.8).
GAPS = [0.45, 0.55, 0.45, 0.55, 0.30, 0.40, 0.60, 0.30, 0.35, 0.70, 0.30, 0.40, 0.55, 0.35, 0.45, 0.70, 1.75]
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
    ["A glowing bridge,", "right across the sky."],
    ["Saturn's rings are icy.", "|", "Ours would be rock,", "shining in sunlight."],
    ["And they'd never rise or set.", "|", "They'd be there day and night."],
    ["Where you live would change everything."],
    ["At the equator,", "a thin line straight overhead."],
    ["Farther north, a giant arch,", "like a rainbow."],
    ["But rings cast shadows."],
    ["In winter, the shadow would fall", "on your half of the world."],
    ["Winters could get colder and darker."],
    ["Now, here's the wild part."],
    ["Earth may have really had a ring."],
    ["About four hundred sixty six", "million years ago."],
    ["Twenty one old craters", "all sit near the ancient equator."],
    ["As if rocks rained down from a ring,", "over millions of years."],
    ["Its shadow might even", "have helped bring an ice age."],
    ["So tonight, look up,", "and picture it there."],
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
    "rings": Wd(0, 4),
    "saturn": Wd(0, 6),
    "glowing": Wd(1, 1),
    "bridge": Wd(1, 2),
    "across": Wd(1, 4),
    "saturn2": Wd(2, 0),
    "icy": Wd(2, 3),
    "ours": Wd(2, 4),
    "rock": Wd(2, 7),
    "shining": Wd(2, 8),
    "never": Wd(3, 2),
    "rise": Wd(3, 3),
    "set": Wd(3, 5),
    "there": Wd(3, 8),
    "day": Wd(3, 9),
    "night": Wd(3, 11),
    "where": Wd(4, 0),
    "live": Wd(4, 2),
    "everything": Wd(4, 5),
    "equator": Wd(5, 2),
    "line": Wd(5, 5),
    "overhead": Wd(5, 7),
    "north": Wd(6, 1),
    "arch": Wd(6, 4),
    "rainbow": Wd(6, 7),
    "cast": Wd(7, 2),
    "shadows": Wd(7, 3),
    "winter": Wd(8, 1),
    "shadow": Wd(8, 3),
    "fall": Wd(8, 5),
    "half": Wd(8, 8),
    "colder": Wd(9, 3),
    "darker": Wd(9, 5),
    "now": Wd(10, 0),
    "wild": Wd(10, 3),
    "earth": Wd(11, 0),
    "really": Wd(11, 3),
    "ring": Wd(11, 6),
    "four": Wd(12, 1),
    "million": Wd(12, 5),
    "twenty": Wd(13, 0),
    "craters": Wd(13, 3),
    "near": Wd(13, 6),
    "ancient": Wd(13, 8),
    "rocks": Wd(14, 2),
    "rained": Wd(14, 3),
    "ring2": Wd(14, 7),
    "millions": Wd(14, 9),
    "shadow2": Wd(15, 1),
    "ice": Wd(15, 8),
    "tonight": Wd(16, 1),
    "look": Wd(16, 2),
    "picture": Wd(16, 5),
    "there2": Wd(16, 7),
}

# scene windows: (name, start, end). Consecutive scenes overlap by X seconds (the transition).
X = 0.4
SCENES = [
    ("open", 0.0, T[2] - 0.10),
    ("rocks", T[2] - 0.10 - X, T[3] - 0.10),
    ("daynight", T[3] - 0.10 - X, T[4] - 0.10),
    ("views", T[4] - 0.10 - X, T[7] - 0.10),
    ("shadow", T[7] - 0.10 - X, T[10] - 0.10),
    ("ancient", T[10] - 0.10 - X, T[13] - 0.10),
    ("craters", T[13] - 0.10 - X, T[15] - 0.10),
    ("iceage", T[15] - 0.10 - X, T[16] - 0.10),
    ("end", T[16] - 0.10 - X, DURATION + 1),
]
# transition INTO each scene: slide_up | slide_left | zoom_in | zoom_out | fade
TRANS = {"rocks": "zoom_in", "daynight": "zoom_out", "views": "slide_up", "shadow": "slide_left",
         "ancient": "fade", "craters": "zoom_in", "iceage": "slide_left", "end": "fade"}

# music: moods are wonder / tension / resolve (see engine/audio.py for every key)
MUSIC_PLAN = {
    "sections": [("wonder", 0.0, T[7] - 0.2), ("tension", T[7] - 0.2, T[10] - 0.2), ("wonder", T[10] - 0.2, T[16] - 0.3),
                 ("resolve", T[16] - 0.3, DURATION)],
    "hush": [(EV["ring"] - 0.05, EV["ring"] + 0.5)],
    "hang": [EV["ring"]],
    "pops": [EV["icy"], EV["rock"], EV["equator"], EV["north"], EV["winter"], EV["four"], EV["twenty"], EV["ice"]],
    "drops": [EV["shadow"], EV["ring"]],
    "rises": [EV["rings"] - 0.3, EV["wild"], E[16] + 0.15],
    "booms": [EV["ring"]],
    "ticks": [],
}

# renderer settings
STATIC_SCENES = ["open", "daynight", "end"]   # these scenes run their own camera
DUSTY_SCENES = ["rocks", "shadow", "ancient", "craters", "iceage"]
ZOOM_FOCUS = {"rocks": (540, 370), "craters": (540, 840)}
PLANNED_JUMPS = [EV["ring"]]

if __name__ == "__main__":
    print("duration", DURATION, "frames", NFRAMES)
    for i, (a, b) in enumerate(zip(T, E)):
        print(i, round(a, 2), round(b, 2), LINES[i]["text"])
    print({k: round(v, 2) for k, v in EV.items()})
    for s in SCENES:
        print(s[0], round(s[1], 2), round(s[2], 2))
