#!/usr/bin/env python3
"""Effetti sonori brevi generati via codice (niente licenze): whoosh, pop, click, ding, hit, tick."""
import numpy as np, wave, os
SR = 48000
D = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)


def save(name, x):
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.9
    st = np.stack([x, x], 1)
    with wave.open(f"{D}/{name}.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def env(n, a, r):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-np.maximum(t - a, 0) / r)


def bandnoise(n, f0, f1, q=6):
    """rumore filtrato con centro che scorre da f0 a f1 (filtro risonante semplice)."""
    x = rng.standard_normal(n)
    y = np.zeros(n); b1 = b2 = 0.0
    fc = np.geomspace(f0, f1, n)
    for i in range(n):
        w = 2 * np.pi * fc[i] / SR
        r = 1 - w / q
        b0 = x[i] - 2 * r * np.cos(w) * -b1 - r * r * b2  # risonatore
        y[i] = x[i] + 2 * r * np.cos(w) * b1 - r * r * b2
        b2, b1 = b1, y[i]
    return y


# whoosh: rumore che sale e scende, inviluppo a campana
n = int(0.45 * SR); t = np.linspace(0, 1, n)
w = bandnoise(n, 300, 2500) * np.sin(np.pi * t) ** 2
save("whoosh", w)
# swoosh corto per i tagli
n = int(0.25 * SR); t = np.linspace(0, 1, n)
save("swoosh", bandnoise(n, 1500, 5000) * np.sin(np.pi * t) ** 3)
# pop: sinusoide che scende di tono, velocissima
n = int(0.12 * SR); tt = np.arange(n) / SR
f = 900 * np.exp(-tt * 30) + 250
save("pop", np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.03))
# click (mouse/UI)
n = int(0.05 * SR); tt = np.arange(n) / SR
save("click", (np.sin(2 * np.pi * 2800 * tt) * 0.6 + rng.standard_normal(n) * 0.4) * env(n, 0.0005, 0.006))
# ding: campanella con armoniche
n = int(0.9 * SR); tt = np.arange(n) / SR
d = sum(a * np.sin(2 * np.pi * 1320 * m * tt) * np.exp(-tt * (4 + 3 * m)) for m, a in ((1, 1), (2.76, .4), (5.4, .2)))
save("ding", d * env(n, 0.002, 10))
# hit: colpo basso per le parole che "esplodono"
n = int(0.4 * SR); tt = np.arange(n) / SR
f = 120 * np.exp(-tt * 8) + 45
hit = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.003, 0.12) + bandnoise(n, 3000, 800) * env(n, 0.001, 0.015) * 0.15
save("hit", hit)
# tick (contatore)
n = int(0.03 * SR); tt = np.arange(n) / SR
save("tick", np.sin(2 * np.pi * 4200 * tt) * env(n, 0.0003, 0.004))
print("ok")
