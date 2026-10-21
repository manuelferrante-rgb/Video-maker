#!/usr/bin/env python3
"""Effetti per il reel del piede: trascinamento del riquadro (attrito che sale + piccolo colpo d'arrivo)
e tre "punti" che si accendono con tono crescente (punto_1/2/3), più il "disegno" del piede."""
import numpy as np, wave, os
SR = 48000
D = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(23)


def save(name, x, peak=0.9):
    x = x / (np.max(np.abs(x)) + 1e-9) * peak
    st = np.stack([x, x], 1)
    with wave.open(f"{D}/{name}.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def band(n, lo, hi):
    X = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    X *= (f > lo) & (f < hi)
    y = np.fft.irfft(X, n)
    return y / (np.std(y) + 1e-9)


# trascinamento: rumore d'attrito granuloso che cresce, poi "tump" quando il video riempie lo schermo
n = int(0.55 * SR); t = np.arange(n) / SR; u = t / t[-1]
grain = 1 + 0.6 * np.sign(np.sin(2 * np.pi * (18 + 30 * u) * t))  # granulosità che accelera
drag = (band(n, 600, 3500) * 0.7 + band(n, 150, 600) * 0.5) * grain * (u ** 1.5) * np.clip((1 - u) / 0.08, 0, 1)
m = int(0.25 * SR); tt = np.arange(m) / SR
thump = np.sin(2 * np.pi * np.cumsum(90 * np.exp(-tt * 10) + 50) / SR) * np.exp(-tt / 0.07)
x = np.zeros(n + m); x[:n] += drag * 0.6; x[n - int(0.02 * SR):n - int(0.02 * SR) + m] += thump
save("trascina", x)

# punti: "blip" morbido con armonica, tono crescente 1 -> 2 -> 3
for k, f0 in ((1, 880), (2, 1108), (3, 1318)):
    m = int(0.32 * SR); tt = np.arange(m) / SR
    s = (np.sin(2 * np.pi * f0 * tt) + 0.35 * np.sin(2 * np.pi * 2 * f0 * tt)) * np.exp(-tt / 0.07)
    s *= np.minimum(tt / 0.003, 1)
    save(f"punto_{k}", s, 0.75)

# disegno del piede: piccolo "sweep" che sale (la linea che si traccia)
n = int(0.6 * SR); t = np.arange(n) / SR; u = t / t[-1]
f = 400 * (1 + 2.5 * u)
s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + band(n, 2000, 6000) * 0.25
save("disegno", s * np.sin(np.pi * u) ** 1.5, 0.6)
print("ok")
