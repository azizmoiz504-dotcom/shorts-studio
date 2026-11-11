"""Episode 004 score: the automatic MUSIC_PLAN score with ~3 dB of extra room under every spoken line
(the tension section under line 9 sat too close to the voice)."""
import numpy as np
import audio as A
import timeline as TL


def build_music():
    mus = A.auto_music(TL.MUSIC_PLAN)
    sp = np.zeros(A.N)
    for a, b in zip(TL.T, TL.E):
        sp[int(max(0, a - 0.15) * A.SR):int((b + 0.1) * A.SR)] = 1
    env = np.clip(A.lowpass(sp, 3.0), 0, 1)
    return mus * (1.0 - 0.3 * env)[:, None]


def build_sfx():
    return A.auto_sfx(TL.MUSIC_PLAN)
