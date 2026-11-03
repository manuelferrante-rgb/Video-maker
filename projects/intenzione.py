#!/usr/bin/env python3
"""Reel muto "L'intenzione" (sul modello del riferimento 2IG: 2 atleti, stesso programma, solo uno migliora),
con i miei B-roll in src_giorni e musica originale (sfx/make_music.py). Due approcci da testare:
  V1 split screen: sopra l'atleta senza intenzione (bianco e nero, rallentato, pause con "POCO RECUPERO" e
     "CELLULARE"), sotto quello con intenzione (colore, velocità reale); scritte sulla linea di mezzo;
     drop della musica su "L'INTENZIONE".
  V2 a tutto schermo: prima tutto in bianco e nero rallentato con le pause, poi sul drop colore e stacchi a tempo
     di musica sulle alzate vere, con "L'INTENZIONE" fissa.
Uso: python3 projects/intenzione.py [1|2 ...]"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R = "/home/user/video-maker"
sys.path.insert(0, f"{R}/sfx")
from make_music import make_music

S = f"{R}/src_giorni"
OUT = f"{R}/out/intenzione"
W, H, FPS, DUR = 1080, 1920, 30, 23.0
ORANGE = (232, 102, 44)
FX = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FBI = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
os.makedirs(OUT, exist_ok=True)


def run(cmd):
    subprocess.run(cmd, check=True)


def part(path, ss, dur, sp, bw, h, cy, out):
    """pezzo di clip lungo `dur` s nel reel: velocità sp (<1 = rallentato, fotogrammi fusi), bianco e nero
    opzionale, ritaglio 1080 x h centrato in verticale su cy (coordinate del clip 1080x1920)."""
    y0 = int(min(max(cy - h / 2, 0), 1920 - h))
    vf = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,crop=1080:{h}:0:{y0},setpts=PTS/{sp}"
    if sp < 1:
        vf += f",framerate=fps={FPS}:interp_start=0:interp_end=255:scene=100"
    vf += f",fps={FPS}"
    if bw:
        vf += ",hue=s=0,eq=contrast=1.12:brightness=-0.03,vignette=PI/5"
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss}", "-t", f"{dur * sp + 0.5}", "-i", path, "-vf", vf + ",setsar=1",
         "-an", "-frames:v", str(round(dur * FPS)), "-c:v", "libx264", "-crf", "15", "-preset", "fast",
         "-pix_fmt", "yuv420p", out])


def concat(files, out):
    open(out + ".txt", "w").write("".join(f"file '{f}'\n" for f in files))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", out + ".txt", "-c", "copy", out])


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def center_text(d, txt, y, size, a, color=(255, 255, 255)):
    f = ImageFont.truetype(FX, size)
    for k, ln in enumerate(txt.split("\n")):
        d.text((W / 2, y + k * size * 1.12), ln, font=f, fill=color + (int(255 * a),), anchor="mm",
               stroke_width=7, stroke_fill=(0, 0, 0, int(255 * a)))


def tag(im, txt, x, y, a, box=(0, 0, 0), size=44):
    """etichetta piccola nei riquadri (Inter Black Italic), con il pallino arancio a sinistra."""
    f = ImageFont.truetype(FBI, size)
    l, t, r, b = f.getbbox(txt)
    w, h = r - l + 70, b - t + 28
    lay = Image.new("RGBA", (int(w), int(h)), box + (230,))
    d = ImageDraw.Draw(lay)
    d.ellipse([18, h / 2 - 9, 36, h / 2 + 9], fill=ORANGE + (255,))
    d.text((50 - l, 14 - t), txt, font=f, fill=(255, 255, 255, 255))
    if a < 1:
        lay.putalpha(lay.split()[3].point(lambda v: int(v * a)))
    im.alpha_composite(lay, (int(x), int(y)))


def big_word(im, txt, y, a, s):
    """parola finale grande in riquadro arancio con un piccolo pop."""
    f = ImageFont.truetype(FBI, 110)
    l, t, r, b = f.getbbox(txt)
    w, h = r - l + 80, b - t + 50
    lay = Image.new("RGBA", (int(w), int(h)), ORANGE + (255,))
    ImageDraw.Draw(lay).text((40 - l, 25 - t), txt, font=f, fill=(255, 255, 255, 255))
    lay = lay.resize((max(int(w * s), 1), max(int(h * s), 1)), Image.LANCZOS)
    if a < 1:
        lay.putalpha(lay.split()[3].point(lambda v: int(v * a)))
    im.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(y - lay.height / 2)))


def pop(x):
    if x <= 0:
        return 0
    if x < 0.6:
        return 0.7 + 0.36 * ease(x / 0.6)
    return 1.06 - 0.06 * ease((x - 0.6) / 0.4)


def gfx(draw, out):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", out], stdin=subprocess.PIPE)
    for k in range(round(DUR * FPS)):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw(im, k / FPS)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()


def window(t, t0, t1, fin=0.25, fout=0.2):
    return ease((t - t0) / fin) * (1 - ease((t - (t1 - fout)) / fout))


def finish(video, gfxmov, music, name):
    tmp = f"{OUT}/{name}_tmp.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", gfxmov, "-i", music, "-filter_complex",
         "[0:v][1:v]overlay=eof_action=pass,format=yuv420p[v];[2:a]loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-c:a", "aac", "-b:a",
         "192k", "-t", f"{DUR}", "-movflags", "+faststart", tmp])
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", tmp, "-af", "loudnorm=print_format=json",
                           "-f", "null", "-"], capture_output=True, text=True).stderr
    li = float(meas[meas.rindex("{"):].split('"input_i" : "')[1].split('"')[0])
    run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-c:v", "copy", "-af", f"volume={-14 - li:.2f}dB", "-c:a", "aac",
         "-b:a", "192k", "-movflags", "+faststart", f"{OUT}/{name}.mp4"])
    os.remove(tmp)


# ---------------- V1: split screen ----------------
DROP1 = 17.4
# (inizio, fine, sopra: file, ss, vel, centro y, etichetta | sotto: file, ss, vel, centro y)
V1 = [(0.0, 4.4, ("IMG_8442", 19.0, 0.5, 1050, None), ("IMG_8636", 3.5, 1.0, 1100)),
      (4.4, 8.8, ("IMG_8454", 0.0, 0.6, 780, "POCO RECUPERO"), ("IMG_8695", 1.0, 1.0, 860)),
      (8.8, 13.0, ("IMG_8452", 25.8, 0.35, 1000, "CELLULARE"), ("IMG_8643", 3.0, 1.0, 820)),
      (13.0, DROP1, ("IMG_8454", 43.6, 0.6, 820, "POCO RECUPERO"), ("IMG_8641", 13.0, 1.0, 1250)),
      (DROP1, DUR, ("IMG_8442", 22.6, 0.5, 1000, None), ("IMG_8641", 17.6, 1.0, 1250))]
TEXT1 = [(0.0, 4.4, "2 ATLETI.\nSTESSO PROGRAMMA."), (4.4, 8.8, "PERCHÉ SOLO UNO\nDIVENTA PIÙ FORTE?"),
         (8.8, DROP1, "LA DIFFERENZA?")]


def v1():
    D = f"{OUT}/v1"
    os.makedirs(D, exist_ok=True)
    segs = []
    for i, (a, b, top, bot) in enumerate(V1):
        part(f"{S}/{top[0]}.mov", top[1], b - a, top[2], True, 960, top[3], f"{D}/t{i}.mp4")
        part(f"{S}/{bot[0]}.mov", bot[1], b - a, bot[2], False, 960, bot[3], f"{D}/b{i}.mp4")
        run(["ffmpeg", "-v", "error", "-y", "-i", f"{D}/t{i}.mp4", "-i", f"{D}/b{i}.mp4", "-filter_complex",
             "vstack", "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p", f"{D}/s{i}.mp4"])
        segs.append(f"{D}/s{i}.mp4")
    concat(segs, f"{D}/video.mp4")

    def draw(im, t):
        d = ImageDraw.Draw(im)
        d.rectangle([0, 957, W, 963], fill=(0, 0, 0, 255))  # linea di mezzo
        for a, b, txt in TEXT1:
            if a <= t < b:
                center_text(d, txt, 960 - (40 if "\n" in txt else 0), 64, window(t, a, b))
        for a, b, top, _ in V1:
            if top[4] and a <= t < b:
                tag(im, top[4], 50, 660, window(t, a + 0.5, b, 0.2, 0.2), size=58)
        if t >= DROP1:
            big_word(im, "L'INTENZIONE", 960, 1.0, pop((t - DROP1) / 0.3))
    gfx(draw, f"{D}/gfx.mov")
    make_music(DUR, DROP1, 7, f"{D}/music.wav")
    finish(f"{D}/video.mp4", f"{D}/gfx.mov", f"{D}/music.wav", "reel_intenzione_v1_split")


# ---------------- V2: bianco e nero -> colore sul drop ----------------
BEAT = 60 / 92
DROP2 = 16 * BEAT  # 4 battute a 92 BPM (10.43 s)
V2 = [(0.0, 3.6, "IMG_8442", 19.0, 0.5, True, None),
      (3.6, 7.0, "IMG_8454", 0.0, 0.6, True, "POCO RECUPERO"),
      (7.0, DROP2, "IMG_8452", 25.8, 0.35, True, "CELLULARE")]
CUTS = ["IMG_8641", 17.6], ["IMG_8636", 3.5], ["IMG_8695", 1.5], ["IMG_8641", 13.2], ["IMG_8643", 3.0], \
       ["IMG_8636", 9.0], ["IMG_8641", 21.0]
TEXT2 = [(0.0, 3.6, "STESSO PROGRAMMA."), (3.6, DROP2, "RISULTATI DIVERSI?")]


def v2():
    D = f"{OUT}/v2"
    os.makedirs(D, exist_ok=True)
    segs = []
    for i, (a, b, f, ss, sp, bw, _) in enumerate(V2):
        part(f"{S}/{f}.mov", ss, b - a, sp, bw, 1920, 960, f"{D}/s{i}.mp4")
        segs.append(f"{D}/s{i}.mp4")
    # dopo il drop: uno stacco ogni 3 battute, a colori e a velocità reale
    t, k = DROP2, 0
    while t < DUR - 1e-3:
        b = min(t + 3 * BEAT, DUR)
        f, ss = CUTS[k % len(CUTS)]
        part(f"{S}/{f}.mov", ss, b - t, 1.0, False, 1920, 960, f"{D}/c{k}.mp4")
        segs.append(f"{D}/c{k}.mp4")
        t, k = b, k + 1
    concat(segs, f"{D}/video.mp4")

    def draw(im, t):
        d = ImageDraw.Draw(im)
        for a, b, txt in TEXT2:
            if a <= t < b:
                center_text(d, txt, 760, 72, window(t, a, b))
        for a, b, f, ss, sp, bw, lab in V2:
            if lab and a <= t < b:
                tag(im, lab, W / 2 - 230, 1150, window(t, a + 0.5, b, 0.2, 0.2), size=60)
        if t >= DROP2:
            big_word(im, "L'INTENZIONE", 760, 1.0, pop((t - DROP2) / 0.3))
    gfx(draw, f"{D}/gfx.mov")
    make_music(DUR, DROP2, 4, f"{D}/music.wav")
    finish(f"{D}/video.mp4", f"{D}/gfx.mov", f"{D}/music.wav", "reel_intenzione_v2_colore")


if __name__ == "__main__":
    for v in (sys.argv[1:] or ["1", "2"]):
        {"1": v1, "2": v2}[v]()
