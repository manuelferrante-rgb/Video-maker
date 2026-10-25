#!/usr/bin/env python3
"""Reel "POV: devi stendere i panni nella giungla indiana" (~9 s, muto: la musica la mette Manuel).
Giungla e arrivo coi panni -> legare la corda al palo (accelerato) -> stendere -> risultato finale fermo.
Scritta unica bianca con bordo nero, centrata e un po' sopra il centro, per tutto il video.
Uso: python3 projects/panni_giungla.py"""
import os, subprocess

R = "/home/user/Video-maker"
S = f"{R}/src_panni"
OUT = f"{R}/out/panni"
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30

# (file, inizio, fine, velocità)
CUTS = [
    ("IMG_8499", 0.70, 2.80, 1.8),   # la giungla dal balcone
    ("IMG_8499", 7.00, 7.85, 1.3),   # arrivo coi panni
    ("IMG_8498", 3.20, 5.00, 2.5),   # corda al palo
    ("IMG_8498", 8.60, 11.00, 3.0),  # la lego
    ("IMG_8498", 13.00, 15.50, 3.0), # il nodo
    ("IMG_8498", 18.50, 20.90, 2.5), # tiro la corda
    ("IMG_8500", 7.60, 11.00, 3.0),  # stendo i pantaloncini (niente corda vuota)
    ("IMG_8500", 13.20, 15.60, 1.4), # risultato finale
]


def run(cmd):
    subprocess.run(cmd, check=True)


lst, t = [], 0.0
for i, (f, a, b, sp) in enumerate(CUTS):
    nfr = round((b - a) / sp * FPS)
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-t", f"{b - a + 0.1}", "-i", f"{S}/{f}.mov",
         "-vf", f"setpts=PTS/{sp},fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1",
         "-an", "-frames:v", str(nfr), "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
         f"{OUT}/c{i}.mp4"])
    lst.append(f"file '{OUT}/c{i}.mp4'")
    t += nfr / FPS
TOTAL = t
open(f"{OUT}/cuts.txt", "w").write("\n".join(lst) + "\n")

ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Txt,Inter ExtraBold,76,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,7,3,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,0:00:00.00,0:00:{TOTAL:05.2f},Txt,,0,0,0,,{{\\an5\\pos(540,760)}}POV: DEVI STENDERE I PANNI\\NNELLA GIUNGLA INDIANA\\NE NON SAI COME FARE
"""
open(f"{OUT}/subs.ass", "w").write(ass)
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/cuts.txt", "-f", "lavfi", "-i",
     "anullsrc=r=48000:cl=stereo", "-vf", f"ass={OUT}/subs.ass,format=yuv420p", "-map", "0:v", "-map", "1:a",
     "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
     "-t", f"{TOTAL:.3f}", f"{OUT}/reel_panni_giungla.mp4"])
print("TOTAL", round(TOTAL, 2))
