#!/usr/bin/env python3
"""Effetti aereo generati via codice: decollo (rombo che sale) e atterraggio (rombo che scende + gomme + tonfo)."""
import numpy as np, wave, os
SR = 48000
D = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(11)


def save(name, x):
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.9
    st = np.stack([x, x], 1)
    with wave.open(f"{D}/{name}.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def band(n, lo, hi):
    """rumore filtrato in frequenza (FFT, senza scipy)."""
    X = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    X *= np.clip((f - lo) / (lo * 0.5 + 1), 0, 1) * np.clip((hi - f) / (hi * 0.5), 0, 1)
    y = np.fft.irfft(X, n)
    return y / (np.std(y) + 1e-9)


def whine(n, f0, f1):
    """fischio di turbina: sinusoide con armoniche che scorre da f0 a f1."""
    f = np.geomspace(f0, f1, n)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) + 0.35 * np.sin(2 * ph + 1) + 0.15 * np.sin(3.1 * ph)


def roar(n, t):
    """rombo del jet: rumore basso + medio, con un leggero tremolio."""
    return (band(n, 40, 400) * 0.9 + band(n, 400, 2500) * 0.35) * (1 + 0.08 * np.sin(2 * np.pi * 7 * t))


# decollo: il rombo cresce, il fischio sale di tono, coda che si allontana
n = int(1.6 * SR); t = np.arange(n) / SR; u = t / t[-1]
envd = np.minimum(u / 0.55, 1) ** 1.6 * np.clip((1 - u) / 0.3, 0, 1) ** 0.8
save("aereo_decollo", roar(n, t) * envd + whine(n, 700, 1900) * 0.10 * envd)

# atterraggio: il rombo arriva e scende di tono, poi stridio delle gomme e tonfo
n = int(1.3 * SR); t = np.arange(n) / SR; u = t / t[-1]
enva = np.minimum(u / 0.15, 1) * np.clip((0.75 - u) / 0.35, 0, 1) ** 1.2
x = roar(n, t) * enva * 0.8 + whine(n, 1600, 600) * 0.10 * enva
for t0 in (0.62, 0.74):  # due "squeak" delle gomme
    i0 = int(t0 * SR); m = int(0.12 * SR); tt = np.arange(m) / SR
    sq = band(m, 1800, 4200) * 0.5 + np.sin(2 * np.pi * 2300 * tt) * 0.6
    x[i0:i0 + m] += sq * np.exp(-tt / 0.05) * 0.9
i0 = int(0.62 * SR); m = int(0.35 * SR); tt = np.arange(m) / SR
x[i0:i0 + m] += np.sin(2 * np.pi * np.cumsum(70 * np.exp(-tt * 6) + 40) / SR) * np.exp(-tt / 0.1) * 1.4
save("aereo_atterraggio", x)
print("ok")
