#!/usr/bin/env python3
"""Base phonk/trap originale (sintesi numpy, nessuna licenza) per i reel "hype" stile edit di gara.
130 BPM, Fa# minore: intro scura (pad, campanaccio filtrato, battito, riser), drop con kick distorto,
808 con glide, clap, hat con rulli e campanaccio "phonk"; stop secco, sospensione e colpo finale.

make_phonk(out, bpm=130, intro_bars=2, main_bars=7, tail=3.7)
  t_drop = intro_bars * bar, t_stop = t_drop + main_bars * bar, colpo finale = t_stop + 1 bar.
Uso: python3 sfx/make_phonk.py out.wav"""
import sys, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(11)


def note(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc):
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    h = 1 / np.sqrt(1 + (f / fc) ** 4)
    return np.fft.irfft(X * (h[:, None] if x.ndim == 2 else h), n=len(x), axis=0)


def hp(x, fc):
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    h = 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(X * (h[:, None] if x.ndim == 2 else h), n=len(x), axis=0)


def bp(x, f0, q=1.5):
    return hp(lp(x, f0 * (1 + 1 / q)), f0 / (1 + 1 / q))


def add(buf, x, t0, g=1.0, pan=0.5):
    i0 = int(round(t0 * SR))
    if i0 >= len(buf) or i0 + len(x) <= 0:
        return
    if i0 < 0:
        x, i0 = x[-i0:], 0
    x = x[:len(buf) - i0]
    if x.ndim == 1:
        buf[i0:i0 + len(x), 0] += x * g * (1 - pan) * 2 ** 0.5
        buf[i0:i0 + len(x), 1] += x * g * pan * 2 ** 0.5
    else:
        buf[i0:i0 + len(x)] += x * g


def tt(d):
    return np.arange(int(d * SR)) / SR


def kick(d=0.45, drive=2.5):
    t = tt(d)
    f = 42 + 140 * np.exp(-t * 35)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5)
    x += 0.25 * hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 300)
    return np.tanh(x * drive) / np.tanh(drive)


def b808(m, d, glide_to=None, drive=3.0):
    t = tt(d)
    f0 = note(m)
    if glide_to is not None:
        k = np.clip((t - d * 0.55) / (d * 0.3), 0, 1)
        f = f0 * (note(glide_to) / f0) ** k
    else:
        f = np.full(len(t), f0)
    f = f * (1 + 0.6 * np.exp(-t * 60))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    e = np.minimum(1, t / 0.004) * np.exp(-t * 1.1)
    e[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
    return np.tanh(x * e * drive) / np.tanh(drive)


def clap(d=0.4):
    t = tt(d)
    n = rng.standard_normal(len(t))
    e = np.zeros(len(t))
    for o in (0, 0.011, 0.022):
        i = int(o * SR)
        e[i:] += np.exp(-(t[i:] - o) * (90 if o < 0.02 else 16))
    x = bp(n * e, 1400, 1.2) * 1.6
    x += 0.35 * np.sin(2 * np.pi * 185 * t) * np.exp(-t * 35)
    return np.tanh(x * 1.5)


def hat(d=0.06, open_=False):
    t = tt(0.25 if open_ else d)
    return hp(rng.standard_normal(len(t)), 8000) * np.exp(-t * (14 if open_ else 70))


def cowbell(m, d=0.22, bright=1.0):
    """campanaccio 808 intonato: due quadre (rapporto ~1.48) in passa-banda, decadimento corto."""
    t = tt(d)
    f = note(m)
    x = np.sign(np.sin(2 * np.pi * f * t)) + 0.8 * np.sign(np.sin(2 * np.pi * f * 1.48 * t))
    x = bp(x, f * 1.25, 1.0)
    e = np.exp(-t * 9) * (0.6 + 0.4 * np.exp(-t * 40))
    x = x * e
    if bright < 1:
        x = lp(x, 900 + 3000 * bright)
    return np.tanh(x * 1.8) * 0.7


def pad(notes, d):
    t = tt(d)
    out = np.zeros((len(t), 2))
    for m in notes:
        for det, pan in ((-0.1, 0.2), (0.0, 0.5), (0.1, 0.8)):
            v = 2 * ((note(m + det) * t + rng.random()) % 1) - 1
            out[:, 0] += v * (1 - pan)
            out[:, 1] += v * pan
    e = np.minimum(1, t / 0.5) * np.minimum(1, (d - t) / 0.4)
    return lp(out, 700) * e[:, None] / (len(notes) * 3)


def crash(d=2.0):
    t = tt(d)
    x = hp(rng.standard_normal((len(t), 2)), 6000) * np.exp(-t * 3.2)[:, None]
    return x


def riser(d):
    t = tt(d)
    n = rng.standard_normal((len(t), 2))
    k = t / d
    out = np.zeros_like(n)
    # passa-banda che sale: a blocchi
    nb = 24
    L = len(t) // nb
    for b in range(nb):
        seg = n[b * L:(b + 1) * L + 2000]
        fc = 400 * (12000 / 400) ** (b / nb)
        y = bp(seg, fc, 2.0)
        w = np.hanning(len(y))[:, None]
        add(out, y * w, b * L / SR)
    return out * (k ** 2)[:, None] * 0.9


def boom(d=3.0):
    t = tt(d)
    f = 28 + 70 * np.exp(-t * 5)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.2)
    return np.tanh(x * 1.6)


def reverse_swell(d):
    t = tt(d)
    x = hp(rng.standard_normal((len(t), 2)), 3000) * np.exp(-(d - t) * 2.5)[:, None]
    return x * 0.6


# Fa# minore: F#m - D - E - C#m (pad), campanaccio su 2 battute
PROG = [[54, 57, 61], [50, 54, 57], [52, 56, 59], [49, 52, 56]]
BASS = [30, 26, 28, 25]
MEL = [[(0, 78), (3, 78), (6, 81), (8, 80), (10, 78), (12, 76), (14, 73)],
       [(0, 78), (3, 78), (6, 81), (8, 83), (10, 81), (12, 80), (13, 78), (14, 76)]]


def make_phonk(out, bpm=130, intro_bars=2, main_bars=7, tail=3.7, intro_beats=None):
    """intro_beats: intro corta (es. 2 beat) al posto delle battute di intro: solo riser + battito, poi drop."""
    beat = 60 / bpm
    bar = beat * 4
    s16 = beat / 4
    t_drop = intro_bars * bar if intro_beats is None else intro_beats * beat
    t_stop = t_drop + main_bars * bar
    t_hit = t_stop + bar
    dur = t_stop + tail
    buf = np.zeros((int((dur + 0.5) * SR), 2))

    if intro_beats is not None:
        # intro corta: battito sui sedicesimi che accelera + riser + campanaccio ovattato
        n16 = int(round(t_drop / s16))
        for st in range(0, n16, 2 if n16 > 6 else 1):
            add(buf, kick(0.3, 1.5), st * s16, 0.3 + 0.05 * st)
        add(buf, riser(t_drop + 0.4)[int(0.4 * SR):], 0, 0.45)
        for st, m in MEL[0][:3]:
            if st * s16 < t_drop:
                add(buf, cowbell(m, 0.3, bright=0.3), st * s16, 0.3)
    else:
        # ---- intro: pad, campanaccio ovattato, battito che accelera, riser
        for b in range(intro_bars):
            t0 = b * bar
            add(buf, pad(PROG[b % 4], bar + 0.5), t0, 0.5)
            for st, m in MEL[b % 2]:
                add(buf, cowbell(m, 0.3, bright=0.15 + 0.25 * b), t0 + st * s16, 0.35, pan=0.45)
            t = tt(bar)
            add(buf, np.sin(2 * np.pi * note(BASS[b % 4]) * t) * np.minimum(1, t / 0.1) * np.exp(-t * 0.6), t0, 0.35)
        hb = [0, 2, 4, 6, 8, 10, 12, 13, 14, 15]
        for i, st in enumerate(hb):
            add(buf, kick(0.3, 1.5), (intro_bars - 1) * bar + st * s16, 0.25 + 0.04 * i)
        add(buf, riser(bar * 1.5), t_drop - bar * 1.5, 0.35)
    # piccolo vuoto prima del drop: si silenzia l'ultima sedicesima
    i0, i1 = int((t_drop - s16) * SR), int(t_drop * SR)
    buf[i0:i1] *= np.linspace(1, 0.05, i1 - i0)[:, None]

    # ---- parte piena
    for b in range(main_bars):
        t0 = t_drop + b * bar
        k = b % 4
        add(buf, pad(PROG[k], bar + 0.5), t0, 0.22)
        # kick + 808 (pattern phonk: 1, 1e&, 3, 3a, rullo ultimo bar)
        ks = [0, 3, 8, 11] if b != main_bars - 1 else [0, 4, 8, 12]
        for j, st in enumerate(ks):
            add(buf, kick(), t0 + st * s16, 0.9)
            nxt = ks[j + 1] if j + 1 < len(ks) else 16
            d = (nxt - st) * s16
            gl = BASS[(k + 1) % 4] + 12 if (j == len(ks) - 1 and b % 2 == 1) else None
            add(buf, b808(BASS[k] + 12, d, glide_to=gl), t0 + st * s16, 0.55)
        for st in (4, 12):
            add(buf, clap(), t0 + st * s16, 0.42)
        # hat: ottavi, rulli a 32esimi a fine battuta
        for st in range(0, 16, 2):
            add(buf, hat(), t0 + st * s16, 0.16, pan=0.62)
        if b % 2 == 1 or b == main_bars - 1:
            for r in range(8):
                add(buf, hat(0.03), t0 + 12 * s16 + r * s16 / 2, 0.08 + 0.015 * r, pan=0.4)
        for st, m in MEL[b % 2]:
            add(buf, cowbell(m), t0 + st * s16, 0.42, pan=0.5)
            add(buf, cowbell(m) * 0.5, t0 + st * s16 + s16 * 1.5, 0.12, pan=0.25)  # eco
        if b in (0, 2, 3, 4, 6):
            add(buf, crash(), t0, 0.12)
    add(buf, boom(2.0), t_drop, 0.7)

    # ---- stop: frenata del nastro sugli ultimi 0.15 s, poi sospensione
    i0, i1 = int((t_stop - 0.15) * SR), int(t_stop * SR)
    buf[i0:i1] *= np.linspace(1, 0, i1 - i0)[:, None] ** 2
    buf[i1:] = 0
    add(buf, b808(BASS[0], bar * 0.9) * 0.6, t_stop, 0.35)
    add(buf, reverse_swell(bar), t_stop, 0.6)
    for st, m in ((8, 78), (11, 78), (14, 81)):
        add(buf, cowbell(m, 0.4, bright=0.25), t_stop + st * s16, 0.3)
    # colpo finale
    add(buf, boom(3.2), t_hit, 0.95)
    add(buf, kick(0.6, 3.0), t_hit, 0.9)
    add(buf, clap(), t_hit, 0.5)
    add(buf, crash(3.0), t_hit, 0.35)
    for m in (78, 85):
        add(buf, cowbell(m, 1.2), t_hit, 0.35)
    add(buf, b808(BASS[0] + 12, tail - 0.2), t_hit, 0.5)

    buf = buf[:int(dur * SR)]
    e = np.ones(len(buf))
    nf = int(0.3 * SR)
    e[-nf:] = np.linspace(1, 0, nf)
    buf *= e[:, None]
    buf /= np.max(np.abs(buf)) + 1e-9
    buf *= 0.9
    if out:
        with wave.open(out, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((buf * 32767).astype(np.int16).tobytes())
    return buf, dict(beat=beat, bar=bar, drop=t_drop, stop=t_stop, hit=t_hit, dur=dur)


if __name__ == "__main__":
    _, info = make_phonk(sys.argv[1] if len(sys.argv) > 1 else "phonk.wav")
    print(info)
