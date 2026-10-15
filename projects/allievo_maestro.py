#!/usr/bin/env python3
"""Reel giocoso "l'allievo supera il maestro": Manuel fa trazioni con 15 kg, arriva l'atleta e si scalda
con 15 kg di muscle up. Audio originale (ambiente) + effetti sonori; la musica la aggiunge Manuel su Instagram."""
import os, subprocess, wave
import numpy as np

SRC = "/home/user/Video-maker/src_mu/IMG_8132.MOV"
OUT = "/home/user/Video-maker/out/allievo_maestro"
SFXD = "/home/user/Video-maker/sfx"
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30

# pezzi: (inizio sorgente, durata sorgente, velocità, crop (cx, cy, zoom), fermo immagine finale in s)
CUTS = [
    (72.6, 2.2, 1.0, (420, 820, 1.45), 0.0),   # io: trazione con 15 kg
    (141.4, 1.6, 1.0, (540, 980, 1.25), 0.0),  # arriva lui e si mette la zavorra (io guardo)
    (145.2, 0.9, 1.0, (480, 760, 1.4), 0.0),   # prende la sbarra "per scaldarsi"
    (151.0, 3.9, 1.15, (480, 640, 1.45), 0.5),  # muscle up con 15 kg, fermo in cima
    (159.6, 1.4, 1.0, (540, 1100, 1.15), 0.0),  # la mia faccia
]


def run(cmd):
    subprocess.run(cmd, check=True)


lst, starts, t = [], [], 0.0
for i, (ss, d, sp, (cx, cy, z), fz) in enumerate(CUTS):
    cw, ch = int(W / z) // 2 * 2, int(H / z) // 2 * 2
    x0 = int(min(max(cx - cw / 2, 0), W - cw))
    y0 = int(min(max(cy - ch / 2, 0), H - ch))
    out_d = d / sp + fz
    nfr = round(out_d * FPS)
    vf = (f"setpts=PTS/{sp},fps={FPS},crop={cw}:{ch}:{x0}:{y0},scale={W}:{H}:flags=lanczos,setsar=1"
          + (f",tpad=stop_mode=clone:stop_duration={fz}" if fz else ""))
    af = f"atempo={sp},afade=t=in:d=0.03,afade=t=out:st={d / sp - 0.05:.3f}:d=0.05" + (f",apad=pad_dur={fz}" if fz else "")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss}", "-t", f"{d}", "-i", SRC, "-vf", vf, "-af", af,
         "-frames:v", str(nfr), "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
         "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", f"{OUT}/c{i}.mov"])
    lst.append(f"file '{OUT}/c{i}.mov'")
    starts.append(t)
    t += nfr / FPS
TOTAL = t
open(f"{OUT}/cuts.txt", "w").write("\n".join(lst) + "\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/cuts.txt", "-af",
     "loudnorm=I=-20:TP=-2:LRA=9", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
     f"{OUT}/base.mp4"])


def ass_t(x):
    x = max(x, 0)
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


ORANGE, BLACK, WHITE = "&H002C66E8&", "&H00000000&", "&H00FFFFFF&"
ev, SFX = [], []


def label(t0, t1, txt, y, box=BLACK, size=96, rot=0, sfx=None):
    ev.append(f"Dialogue: 4,{ass_t(t0)},{ass_t(t1)},Lab,,0,0,0,,{{\\an8\\pos(540,{y})\\frz{rot}\\3c{box}\\fs{size}"
              f"\\fscx0\\fscy0\\t(0,90,\\fscx114\\fscy114)\\t(90,170,\\fscx100\\fscy100)}}{txt}")
    if sfx:
        SFX.append((t0, sfx[0], sfx[1]))


s1, s2, s3, s4, s5 = starts
top = s4 + CUTS[3][1] / CUTS[3][2]  # inizio del fermo in cima al muscle up
# 1) io
label(0.05, s2, "IO:", 1150, size=110, sfx=("pop", 0.3))
label(0.35, s2, "TRAZIONI CON 15 KG", 1280, box=ORANGE, size=84, sfx=("pop", 0.25))
label(1.2, s2, "TUTTO FIERO", 1400, size=64, rot=-3)
# 2) arriva lui
label(s2, s4, "POI ARRIVA LUI...", 1340, size=92, sfx=("swoosh", 0.3))
label(s3 + 0.05, s4, "E SI SCALDA CON 15 KG", 1470, box=ORANGE, size=76, sfx=("pop", 0.25))
# 3) muscle up
label(s4 + 0.1, s5, "DI MUSCLE UP", 1150, box=ORANGE, size=110, sfx=("whoosh", 0.3))
SFX.append((top, "hit", 0.5))
label(top, s5, "BUONGIORNO", 1300, size=92, rot=-4)
# 4) io dopo
label(s5, TOTAL, "L'ALLIEVO", 300, size=104, sfx=("ding", 0.25))
label(s5 + 0.35, TOTAL, "HA SUPERATO IL MAESTRO", 420, box=ORANGE, size=74, sfx=("pop", 0.25))

ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Lab,Inter Black,90,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,1,0,0,100,100,0,0,3,16,0,8,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n"
open(f"{OUT}/subs.ass", "w").write(ass)

sr = 48000
mix = np.zeros((int((TOTAL + 1) * sr), 2), np.float32)
for t0, nm, vol in SFX:
    with wave.open(f"{SFXD}/{nm}.wav") as wv:
        x = np.frombuffer(wv.readframes(wv.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32767
    i0 = max(int(t0 * sr), 0)
    i1 = min(i0 + len(x), len(mix))
    mix[i0:i1] += x[:i1 - i0] * vol
with wave.open(f"{OUT}/sfx.wav", "wb") as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(sr)
    wv.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())

run(["ffmpeg", "-v", "error", "-y", "-i", f"{OUT}/base.mp4", "-i", f"{OUT}/sfx.wav", "-filter_complex",
     f"[0:v]ass={OUT}/subs.ass,format=yuv420p[v];[0:a][1:a]amix=inputs=2:normalize=0:duration=first,"
     f"alimiter=limit=0.95[a]", "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "slow",
     "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{TOTAL:.3f}",
     f"{OUT}/reel_allievo_maestro.mp4"])
print("TOTAL", round(TOTAL, 2), [round(x, 2) for x in starts])
