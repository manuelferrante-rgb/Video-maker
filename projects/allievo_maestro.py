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

# pezzi: (inizio sorgente, durata sorgente, velocità, crop iniziale (cx, cy, zoom), crop finale, fermo finale in s)
# il crop si sposta durante il pezzo per seguire il gesto (zoom leggero)
CUTS = [
    (72.95, 1.2, 1.0, (430, 920, 1.1), (430, 790, 1.16), 0.0),     # 0 io: trazione con 15 kg
    (141.8, 0.5, 1.0, (540, 980, 1.08), (540, 980, 1.08), 0.0),   # 1 arriva lui: cintura (mini taglio)
    (144.3, 0.4, 1.0, (540, 960, 1.08), (540, 960, 1.08), 0.0),   # 2 cintura messa (mini taglio)
    (148.3, 0.5, 1.0, (520, 880, 1.08), (520, 880, 1.08), 0.0),   # 3 già in oscillazione
    (152.2, 3.1, 1.25, (500, 820, 1.1), (490, 700, 1.2), 0.0),   # 4 muscle up con 15 kg
    (156.2, 0.8, 1.6, (500, 820, 1.1), (500, 860, 1.1), 0.0),     # 5 scende dalla sbarra
    (158.9, 1.5, 1.0, (540, 960, 1.0), (560, 960, 1.04), 0.0),    # 6 io che cammino verso la camera e rido
]


def run(cmd):
    subprocess.run(cmd, check=True)


lst, starts, t = [], [], 0.0
for i, (ss, d, sp, c0, c1, fz) in enumerate(CUTS):
    out_d = d / sp + fz
    nfr = round(out_d * FPS)
    nmove = max(round(d / sp * FPS) - 1, 1)
    p = f"min(on/{nmove},1)"
    ez = f"({p})*({p})*(3-2*({p}))"  # smoothstep
    z = f"({c0[2]}+({c1[2]}-{c0[2]})*{ez})"
    cx = f"2*({c0[0]}+({c1[0]}-{c0[0]})*{ez})"
    cy = f"2*({c0[1]}+({c1[1]}-{c0[1]})*{ez})"
    vf = (f"setpts=PTS/{sp},fps={FPS}" + (f",tpad=stop_mode=clone:stop_duration={fz}" if fz else "")
          + f",scale={W * 2}:{H * 2}:flags=lanczos,zoompan=z='{z}':x='max(0,min(iw-iw/zoom,{cx}-iw/zoom/2))'"
          f":y='max(0,min(ih-ih/zoom,{cy}-ih/zoom/2))':d=1:s={W}x{H}:fps={FPS},setsar=1")
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
    """entrata morbida (dissolvenza + piccola salita) e poi ferma, per leggere bene."""
    ev.append(f"Dialogue: 4,{ass_t(t0)},{ass_t(t1)},Lab,,0,0,0,,{{\\an8\\move(540,{y + 24},540,{y},0,220)\\fad(200,120)"
              f"\\frz{rot}\\3c{box}\\fs{size}}}{txt}")
    if sfx:
        SFX.append((t0, sfx[0], sfx[1]))


c0, c1, c2, c3, c4, c5, c6 = starts
OVER_BAR = c4 + (153.6 - CUTS[4][0]) / CUTS[4][2]  # quando supera la sbarra
# testi pochi e fermi: si costruisce una frase che resta leggibile
# 1) io (hook: entra subito, tutto insieme)
label(0.0, c1, "IO:", 1330, size=100)
label(0.0, c1, "TRAZIONI CON 15 KG", 1450, box=ORANGE, size=84)
# 2-3) lui: in alto mentre si prepara (la mia testa è in basso), poi "DI MUSCLE UP" in basso quando lui sale
label(c1, OVER_BAR, "POI ARRIVA LUI", 300, size=92)
label(c1, OVER_BAR, "E SI SCALDA CON 15 KG", 425, box=ORANGE, size=80)
label(OVER_BAR, c6, "DI MUSCLE UP", 1470, box=ORANGE, size=96, sfx=("hit", 0.4))
# 4) io che arrivo ridendo
JOKE = c6
label(JOKE, TOTAL, "ALMENO L'HO", 300, size=96)
label(JOKE, TOTAL, "ALLENATO BENE", 425, box=ORANGE, size=96)
SFX.append((JOKE, "pop", 0.25))
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

# emoji 😂 accanto a "ALLENATO BENE" (libass non disegna emoji a colori: PNG da Noto Color Emoji)
from PIL import Image, ImageDraw, ImageFont
fe = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
em = Image.new("RGBA", (140, 140))
ImageDraw.Draw(em).text((10, 10), "😂", font=fe, embedded_color=True)
em = em.crop(em.getbbox()).resize((96, 86), Image.LANCZOS)
em.save(f"{OUT}/emoji.png")
lw = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf", 96).getlength("ALLENATO BENE")
EX, EY = int(540 + lw / 2 + 36), 438
E0 = JOKE + 0.05
run(["ffmpeg", "-v", "error", "-y", "-i", f"{OUT}/base.mp4", "-i", f"{OUT}/sfx.wav", "-loop", "1", "-i",
     f"{OUT}/emoji.png", "-filter_complex",
     f"[0:v]ass={OUT}/subs.ass[s];[2:v]format=rgba,fade=t=in:st={E0:.3f}:d=0.12:alpha=1[e];"
     f"[s][e]overlay={EX}:{EY}:shortest=1:enable='gte(t,{E0:.3f})',format=yuv420p[v];[0:a][1:a]amix=inputs=2:normalize=0:duration=first,"
     f"alimiter=limit=0.95[a]", "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "slow",
     "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{TOTAL:.3f}",
     f"{OUT}/reel_allievo_maestro.mp4"])
print("TOTAL", round(TOTAL, 2), [round(x, 2) for x in starts])
