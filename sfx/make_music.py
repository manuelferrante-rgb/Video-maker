#!/usr/bin/env python3
"""Musica originale (sintesi numpy, nessuna licenza) per i reel "muti": tappeto scuro in minore, riser e drop
con batteria. make_music(dur, drop, bars_before_drop, out) mette il drop esattamente al secondo `drop`
(il BPM si ricava da drop / bars). Prima del drop: pad + basso morbido + battito leggero; dopo: kick, clap, hat,
basso pieno, arpeggio. Uso diretto: python3 sfx/make_music.py out.wav 23 17.4 7"""
import sys, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def note(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env(n, a, r, sus=1.0):
    e = np.ones(n) * sus
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, sus, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def lp_fast(x, fc):
    """filtro passa-basso FFT (fc fisso) per tracce lunghe."""
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    h = 1 / np.sqrt(1 + (f / fc) ** 4)
    return np.fft.irfft(X * (h[:, None] if x.ndim == 2 else h), n=len(x), axis=0)


def hp_fast(x, fc):
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    h = 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(X * (h[:, None] if x.ndim == 2 else h), n=len(x), axis=0)


def saw(f, t):
    return 2 * ((f * t) % 1) - 1


def pad_chord(notes, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for m in notes:
        for det, pan in ((-0.12, 0.2), (0.0, 0.5), (0.12, 0.8)):
            f = note(m + det)
            v = saw(f, t + rng.random())
            out[:, 0] += v * (1 - pan)
            out[:, 1] += v * pan
    out = lp_fast(out, 900) * env(n, 0.6, 0.6)[:, None]
    return out / (len(notes) * 3)


def kick(n=0.5):
    t = np.arange(int(n * SR)) / SR
    f = 45 + 95 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7) + 0.3 * np.exp(-t * 200) * rng.standard_normal(len(t)) * 0.2


def clap(n=0.35):
    t = np.arange(int(n * SR)) / SR
    x = rng.standard_normal(len(t)) * np.exp(-t * 18)
    x = hp_fast(x, 900)
    return x * 0.6 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.3


def hat(n=0.08):
    t = np.arange(int(n * SR)) / SR
    return hp_fast(rng.standard_normal(len(t)), 7000) * np.exp(-t * 60)


def boom(n=2.5):
    t = np.arange(int(n * SR)) / SR
    f = 30 + 60 * np.exp(-t * 6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)


def pluck(m, n=0.4):
    t = np.arange(int(n * SR)) / SR
    f = note(m)
    x = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t) + 0.15 * np.sin(6 * np.pi * f * t))
    return x * np.exp(-t * (9 if n < 1 else 2.5)) * env(len(t), 0.003, 0.05)


def add(buf, x, t0, g=1.0, pan=0.5):
    i0 = int(t0 * SR)
    if i0 >= len(buf) or i0 < 0:
        return
    x = x[:len(buf) - i0]
    if x.ndim == 1:
        buf[i0:i0 + len(x), 0] += x * g * (1 - pan) * 2 ** 0.5
        buf[i0:i0 + len(x), 1] += x * g * pan * 2 ** 0.5
    else:
        buf[i0:i0 + len(x)] += x * g


# progressione in La minore: Am - F - C - G (pad un'ottava sotto, basso due)
PROG = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
BASS = [33, 29, 36, 31]
ARP = [[69, 72, 76, 72], [65, 69, 72, 69], [64, 67, 72, 67], [67, 71, 74, 71]]


def make_music(dur, drop, bars, out=None):
    bar = drop / bars
    beat = bar / 4
    buf = np.zeros((int((dur + 1) * SR), 2))
    nb = int(np.ceil((dur + 1) / bar))
    for b in range(nb):
        t0 = b * bar
        k = b % 4
        after = t0 >= drop - 1e-6
        add(buf, pad_chord(PROG[k], bar + 0.6), t0, 0.55 if not after else 0.45)
        # basso: prima del drop note lunghe morbide, dopo ottavi pulsanti
        if not after:
            t = np.arange(int(bar * SR)) / SR
            bs = np.sin(2 * np.pi * note(BASS[k]) * t) * env(len(t), 0.2, 0.3)
            add(buf, bs, t0, 0.35)
            # due note di "carillon" per battuta, lente e lontane
            for j, q in enumerate((0, 2)):
                add(buf, pluck(ARP[k][j * 2] + 12, 1.6) * 0.8, t0 + q * beat, 0.07, pan=0.35 + 0.3 * j)
            # battito di cuore leggero sul 1 e sul 3 negli ultimi bar prima del drop
            if b >= bars - 3:
                for q in (0, 2):
                    add(buf, kick(0.35) * 0.5, t0 + q * beat, 0.35)
        else:
            for e in range(8):
                t = np.arange(int(beat / 2 * SR)) / SR
                f = note(BASS[k])
                bs = (np.sin(2 * np.pi * f * t) + 0.3 * saw(f, t)) * env(len(t), 0.005, 0.06)
                add(buf, lp_fast(bs, 400), t0 + e * beat / 2, 0.42)
            for q in range(4):
                add(buf, kick(), t0 + q * beat, 0.9)
                if q in (1, 3):
                    add(buf, clap(), t0 + q * beat, 0.32)
                for h in (0.5,):
                    add(buf, hat(), t0 + (q + h) * beat, 0.16, pan=0.65)
            for j in range(16):
                add(buf, pluck(ARP[k][j % 4] + (12 if j % 8 >= 4 else 0)), t0 + j * beat / 4, 0.09,
                    pan=0.3 + 0.4 * (j % 2))
    # riser nell'ultimo bar prima del drop + impatto sul drop
    rn = int(bar * SR)
    t = np.arange(rn) / SR
    noise = rng.standard_normal((rn, 2))
    riser = np.zeros_like(noise)
    seg = rn // 16
    for s in range(16):  # filtro che si apre a gradini (veloce, niente loop per campione)
        fc = 400 * (12000 / 400) ** (s / 15)
        a, b2 = s * seg, (s + 1) * seg if s < 15 else rn
        riser[a:b2] = lp_fast(noise[a:b2], fc)
    riser *= (t / bar)[:, None] ** 2
    add(buf, riser, drop - bar, 0.22)
    add(buf, boom(), drop, 0.8)
    add(buf, hp_fast(rng.standard_normal(int(1.5 * SR)), 3000) * np.exp(-np.arange(int(1.5 * SR)) / SR * 4), drop,
        0.12)
    buf = buf[:int(dur * SR)]
    # fade finale e normalizzazione dei picchi (la loudness la sistema il montaggio)
    fo = int(1.2 * SR)
    buf[-fo:] *= np.linspace(1, 0, fo)[:, None]
    buf /= np.max(np.abs(buf)) / 0.89
    if out:
        with wave.open(out, "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((buf * 32767).astype(np.int16).tobytes())
    return buf


if __name__ == "__main__":
    make_music(float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), sys.argv[1])
