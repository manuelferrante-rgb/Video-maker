#!/usr/bin/env python3
"""Puntata 2 "Due atleti, una scelta": lo sguardo nel dip (18/11/2026, script in projects/script_dip_sguardo.md).
Primo fotogramma = split Lorenzo (V0928, petto nudo, guarda giu') | Giacomo (IMG_6375, disco giallo, guarda in alto)
con la voce sopra e una parola per lato; Manuel in camera da "Li alleno tutti e due"; Lorenzo che scende e si ferma
in basso con la linea dello sguardo verso il basso; Giacomo all'aperto che sale a fatica ("ti pianti in chiusura?")
poi Giacomo col disco giallo che sale guardando in alto con la linea dello sguardo; CTA in camera; "Prima pero',
guarda le loro teste" sullo split iniziale (loop).
A: "Lorenzo fa dip con 70 kg guardando in giu', Giacomo in alto."  B: "Nel dip ti pianti in chiusura? Lorenzo guarda
in giu', Giacomo in su."  Parlato: src_dip/IMG_9140.MOV -> src_dip/p_norm.mov (1080x1920).
B-roll preparati in out/dip/br (comandi in prep()). Uso: python3 projects/dip_sguardo.py [A B]"""
import os, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, "/home/user/video-maker/projects")
from reel_kit import build, OR, WH, R, ORANGE, BLACK, ease
from PIL import Image, ImageDraw, ImageFont

S = f"{R}/src_dip"
NORM = f"{S}/p_norm.mov"
BR = f"{R}/out/dip/br"
OUT = f"{R}/out/dip"
FBI = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"


def sh(c):
    subprocess.run(c, shell=True, check=True)


def prep():
    os.makedirs(BR, exist_ok=True)
    if not os.path.exists(NORM):
        sh(f"ffmpeg -v error -y -i {S}/IMG_9140.MOV -vf scale=1080:1920:flags=lanczos,setsar=1 -c:v libx264 -crf 14 "
           f"-preset fast -pix_fmt yuv420p -c:a pcm_s16le -ar 48000 -ac 2 {NORM}")
    if not os.path.exists(f"{OUT}/parlato.wav"):
        sh(f"ffmpeg -v error -y -i {S}/IMG_9140.MOV -vn -ac 1 -ar 16000 {OUT}/parlato.wav")
    # split: Lorenzo (V0928 da 1.5 s, 464x832 -> ritaglio sul corpo) | Giacomo (IMG_6375 da 15.8 s)
    sh(f"ffmpeg -v error -y -ss 1.5 -t 4.6 -i {S}/V0928.mp4 -ss 15.8 -t 4.6 -i {S}/IMG_6375.MOV -filter_complex "
       f"\"[0:v]fps=30,scale=1080:-2:flags=lanczos,crop=1080:1920,unsharp=5:5:0.5,crop=540:1920:240:0[l];"
       f"[1:v]fps=30,scale=1080:1920:flags=lanczos,crop=540:1920:250:0[r];[l][r]hstack,"
       f"drawbox=x=537:y=0:w=6:h=1920:color=white:t=fill,setsar=1[v]\" -map \"[v]\" -an -frames:v 138 "
       f"-c:v libx264 -crf 15 -pix_fmt yuv420p {BR}/split.mp4")
    # Lorenzo: scende (sorgente 23.6) e si ferma in basso (fermo immagine sul fotogramma 25.0)
    sh(f"ffmpeg -v error -y -ss 23.6 -t 1.4 -i {S}/V0928.mp4 -vf \"fps=30,scale=1080:-2:flags=lanczos,crop=1080:1920,"
       f"unsharp=5:5:0.5,setsar=1,tpad=stop_mode=clone:stop_duration=3\" -an -c:v libx264 -crf 15 -pix_fmt yuv420p "
       f"{BR}/lor_hold.mp4")
    # Giacomo all'aperto: la salita lenta (telegram_video 4.0-5.4)
    sh(f"ffmpeg -v error -y -ss 4.0 -t 1.4 -i {S}/telegram_video.mp4 -vf fps=30,scale=1080:1920:flags=lanczos,setsar=1 "
       f"-an -c:v libx264 -crf 15 -pix_fmt yuv420p {BR}/gia_out.mp4")
    # Giacomo disco giallo: ultima salita guardando in alto (IMG_6375 20.6-22.25)
    sh(f"ffmpeg -v error -y -ss 20.6 -t 1.65 -i {S}/IMG_6375.MOV -vf \"fps=30,scale=1080:1920:flags=lanczos,setsar=1,"
       f"tpad=stop_mode=clone:stop_duration=0.5\" -an -c:v libx264 -crf 15 -pix_fmt yuv420p {BR}/gia.mp4")


PH = {"HA": (36.61, 39.80),   # Lorenzo fa dip con 70 kg guardando in giu', Giacomo in alto
      "HB": (55.17, 58.45),   # Nel dip ti pianti in chiusura? Lorenzo guarda in giu', Giacomo in su
      "S2": (80.51, 83.18),   # Li alleno tutti e due io e decide il tuo punto debole
      "S3": (109.92, 113.19),  # Perdi la posizione in basso? Guarda in giu' e resti compatto
      "S4": (129.11, 132.05),  # Ti pianti in chiusura? Guarda in alto mentre sali
      "S5": (152.36, 155.04),  # E tu dove guardi? Scrivi giu' o in alto
      "S6": (164.43, 166.15)}  # Prima pero' guarda le loro teste
BODY = ["S2", "S3", "S4", "S5", "S6"]
D = 0.18  # parakeet e' in anticipo: tempo parola = parakeet + D
KARA = {"HA": [("LORENZO", 36.51), ("FA", 36.91), ("DIP", 37.1), ("|", 0), ("CON", 37.39), ("70", 37.47),
               ("KG", 37.79), ("/", 0), ("GUARDANDO", 38.11), ("IN", 38.51), ("GIÙ,", 38.59), ("/", 0),
               ("GIACOMO", 38.83), ("IN", 39.31), ("ALTO", 39.47)],
        "HB": [("NEL", 55.07), ("DIP", 55.23), ("TI", 55.55), ("PIANTI", 55.63), ("|", 0), ("IN", 55.95),
               ("CHIUSURA?", 56.03), ("/", 0), ("LORENZO", 56.59), ("GUARDA", 57.07), ("|", 0), ("IN", 57.39),
               ("GIÙ,", 57.47), ("/", 0), ("GIACOMO", 57.71), ("IN", 58.19), ("SU", 58.27)],
        "S2": [("LI", 80.41), ("ALLENO", 80.65), ("TUTTI", 80.97), ("|", 0), ("E", 81.13), ("DUE", 81.21),
               ("IO", 81.37), ("/", 0), ("E", 81.61), ("DECIDE", 81.69), ("IL", 82.09), ("TUO", 82.17), ("|", 0),
               ("PUNTO", 82.41), ("DEBOLE", 82.73)],
        "S3": [("PERDI", 109.82), ("LA", 110.30), ("POSIZIONE", 110.38), ("|", 0), ("IN", 110.70),
               ("BASSO?", 110.78), ("/", 0), ("GUARDA", 111.26), ("IN", 111.66), ("GIÙ", 111.74), ("|", 0),
               ("E", 111.98), ("RESTI", 112.14), ("COMPATTO", 112.54)],
        "S4": [("TI", 129.01), ("PIANTI", 129.25), ("|", 0), ("IN", 129.65), ("CHIUSURA?", 129.73), ("/", 0),
               ("GUARDA", 130.37), ("IN", 130.85), ("ALTO", 131.01), ("|", 0), ("MENTRE", 131.33), ("SALI", 131.65)],
        "S5": [("E", 152.26), ("TU", 152.42), ("DOVE", 152.58), ("GUARDI?", 152.90), ("/", 0), ("SCRIVI", 153.38),
               ("GIÙ", 153.94), ("|", 0), ("O", 154.26), ("IN", 154.42), ("ALTO", 154.58)],
        "S6": [("PRIMA", 164.38), ("PERÒ,", 164.70), ("|", 0), ("GUARDA", 165.02), ("LE", 165.34), ("LORO", 165.50),
               ("|", 0), ("TESTE", 165.74)]}


def kara_pages(n):
    """una riga ASS per parola: stessa pagina, la parola detta in arancio (pop solo sulla prima)"""
    pages, cur = [], []
    for w, t in KARA[n] + [("/", 0)]:
        if w == "/":
            if cur:
                pages.append(cur)
            cur = []
        else:
            cur.append((w, t + D))
    out = []
    for pg in pages:
        words = [x for x in pg if x[0] != "|"]
        for k, (w, t) in enumerate(words):
            parts, j = [], 0
            for x, _ in pg:
                if x == "|":
                    parts.append("\\N")
                    continue
                parts.append((OR + x + WH) if j == k else x)
                j += 1
            txt = " ".join(parts).replace(" \\N ", "\\N")
            out.append((t if k else t - 0.05, ("" if k == 0 else "§") + txt))
    return out


# una parola per lato sullo split: (lato, testo, istante sorgente in cui compare; None = dal primo fotogramma)
HOOK_TXT = {"HA": [("L", "70 KG", None), ("R", "IN ALTO", 39.25)],
            "HB": [("L", "GIÙ", None), ("R", "IN ALTO", 58.05)]}

_a, _sr = sf.read(f"{OUT}/parlato.wav", dtype="float32")
_n = len(_a) // 160
_DB = 20 * np.log10(np.sqrt((_a[:_n * 160].reshape(_n, 160) ** 2).mean(1)) + 1e-9)
_V = _DB > np.percentile(_DB, 98) - 32


def subsegs(a, b, gap=0.16, pre=0.05, post=0.07):
    i, e = int(a * 100), int(b * 100)
    runs = []
    while i < e:
        if _V[i]:
            j = i
            while j < e and _V[j:j + int(gap * 100)].any():
                j += 1
            runs.append([i / 100, j / 100])
            i = j
        else:
            i += 1
    runs = [r for r in runs if r[1] - r[0] >= 0.06] or [[a, b]]
    out = [[max(r[0] - pre, a), min(r[1] + post, b)] for r in runs]
    out[0][0], out[-1][1] = a, b
    return out


def label(txt, bg, size):
    ft = ImageFont.truetype(FBI, size)
    l, t, r, b = ft.getbbox(txt)
    im = Image.new("RGBA", (r - l + 52, b - t + 40), bg + (255,))
    ImageDraw.Draw(im).text((26 - l, 20 - t), txt, font=ft, fill=(255, 255, 255))
    return im


def popscale(x):
    return 0.75 + 0.25 * ease(x / 0.18) if x < 0.18 else 1.0


def hook_text(items, t_of):
    """una parola per lato sullo split, sopra le teste (y 262)"""
    labs = [(side, label(txt, ORANGE if side == "L" else BLACK, 68), None if src is None else t_of(src))
            for side, txt, src in items]

    def draw(im, t, dur):
        for side, lab, t0 in labs:
            if t0 is not None and t < t0:
                continue
            s = 1.0 if t0 is None else popscale(t - t0)
            lb = lab.resize((int(lab.width * s), int(lab.height * s)), Image.LANCZOS)
            cx = 270 if side == "L" else 760
            im.alpha_composite(lb, (int(cx - lb.width / 2), int(262 - lb.height / 2)))
    return draw


def titles(rows, cx=540):
    """titolo in alto su piu' righe (riquadri nero/arancio), pop in ingresso, sfuma in uscita"""
    labs = [(label(txt, ORANGE if c == "o" else BLACK, 72), y, cx) for txt, c, y in rows]

    def draw(im, t, dur):
        fade = 1 - ease((t - (dur - 0.12)) / 0.12)
        for k, (lab, y, x0) in enumerate(labs):
            x = t - 0.08 * k
            if x < 0:
                continue
            s = popscale(x)
            lb = lab.resize((int(lab.width * s), int(lab.height * s)), Image.LANCZOS)
            if fade < 1:
                lb.putalpha(lb.split()[3].point(lambda v: int(v * fade)))
            im.alpha_composite(lb, (int(x0 - lb.width / 2), int(y - lb.height / 2)))
    return draw


def gaze(track, t_line, t_title, word, word_xy, dash=True):
    """linea sottile bianca dello sguardo dall'occhio (seguito per fotogrammi chiave) verso dove guarda, punto
    arancio in fondo; track = [(t, (ex, ey), (dx, dy))] nel tempo locale del pezzo"""
    lab = label(word, ORANGE, 72)

    def at(t):
        if t <= track[0][0]:
            return track[0][1], track[0][2]
        for (t0, e0, d0), (t1, e1, d1) in zip(track, track[1:]):
            if t <= t1:
                f = (t - t0) / (t1 - t0)
                return ([e0[i] + (e1[i] - e0[i]) * f for i in (0, 1)], [d0[i] + (d1[i] - d0[i]) * f for i in (0, 1)])
        return track[-1][1], track[-1][2]

    def draw(im, t, dur):
        x = t - t_line
        if x >= 0:
            (ex, ey), (dx, dy) = at(t)
            e = ease(x / 0.35)
            d = ImageDraw.Draw(im)
            L = 1.0 * e
            n = 14
            for k in range(n):
                if dash and k % 2:
                    continue
                a0, a1 = k / n * L, (k + 1) / n * L
                d.line([(ex + dx * a0, ey + dy * a0), (ex + dx * a1, ey + dy * a1)], fill=(255, 255, 255, 235), width=6)
            px, py = ex + dx * L, ey + dy * L
            r = 15
            d.ellipse([px - r - 6, py - r - 6, px + r + 6, py + r + 6], outline=(255, 255, 255, 230), width=4)
            d.ellipse([px - r, py - r, px + r, py + r], fill=ORANGE + (255,))
            d.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], fill=(255, 255, 255, 255))
        y = t - t_title
        if y >= 0:
            s = popscale(y)
            fade = 1 - ease((t - (dur - 0.12)) / 0.12)
            lb = lab.resize((int(lab.width * s), int(lab.height * s)), Image.LANCZOS)
            if fade < 1:
                lb.putalpha(lb.split()[3].point(lambda v: int(v * fade)))
            im.alpha_composite(lb, (int(word_xy[0] - lb.width / 2), int(word_xy[1] - lb.height / 2)))
    return draw


# occhi (coordinate nel B-roll a 1080x1920, tempo locale del clip a velocita' reale)
LOR_EYE = [(0.0, (680, 1012), (50, 310))]                      # fermo immagine in basso: guarda giu' e avanti
GIA_EYE = [(0.6, (615, 565), (230, -170)), (0.7, (565, 485), (230, -170)), (0.8, (535, 465), (230, -170)),
           (0.9, (505, 395), (230, -150)), (1.0, (495, 410), (230, -140)), (1.1, (515, 400), (230, -140)),
           (1.2, (535, 400), (230, -140))]


def make(v):
    hook = f"H{v}"
    names = [hook] + BODY
    segs = []
    for n in names:
        a, b = PH[n]
        for s0, s1 in subsegs(a, b):
            segs.append((NORM, s0, s1))

    def ref(src):
        for k, (_, s0, s1) in enumerate(segs):
            if src < s1:
                return (k, max(src, s0))
        return (len(segs) - 1, segs[-1][2])

    def start(n):
        return ref(PH[n][0])

    def nxt(n):
        i = names.index(n)
        return start(names[i + 1]) if i + 1 < len(names) else "end"

    SO, t = [], 0.0
    for _, a, b in segs:
        SO.append(t)
        t += round((b - a) / 1.1 * 30) / 30

    def t_of(src):
        k, s = ref(src)
        return SO[k] + (s - segs[k][1]) / 1.1

    def loc(src, n):  # tempo dentro il pezzo n
        return t_of(src) - t_of(PH[n][0])

    pages = [(ref(PH[n][0]) if i == 0 else ref(s), txt)
             for n in names for i, (s, txt) in enumerate(kara_pages(n))]
    g_from = ref(130.43)  # "Guarda in alto": stacco sul disco giallo
    br = [(start(hook), nxt(hook), f"{BR}/split.mp4", 0.0, 1.0, 1.0, None),
          (start("S3"), nxt("S3"), f"{BR}/lor_hold.mp4", 0.0, 1.0, 1.0, None),
          (start("S4"), g_from, f"{BR}/gia_out.mp4", 0.0, 1.0, 1.0, None),
          (g_from, nxt("S4"), f"{BR}/gia.mp4", 0.0, 1.0, 1.0, None),
          (start("S6"), "end", f"{BR}/split.mp4", 0.0, 1.0, 1.0, None)]
    # linee dello sguardo: tempo locale del pezzo (la clip gira a velocita' reale)
    t_gl = loc(111.26 + D, "S3")
    lor = gaze([(0, LOR_EYE[0][1], LOR_EYE[0][2])], t_gl, t_gl + 0.45, "COMPATTO", (540, 300))
    t_ga = t_of(130.85 + D) - t_of(130.43)
    gtrack = [(tt, e, d) for tt, e, d in GIA_EYE]
    gia = gaze(gtrack, max(t_ga, 0.6), max(t_ga, 0.6) + 0.4, "CHIUDI", (850, 640))
    overlays = [(start(hook), nxt(hook), hook_text(HOOK_TXT[hook], lambda s: t_of(s) - t_of(PH[hook][0]))),
                (start("S2"), nxt("S2"), titles([("DECIDE IL TUO", "n", 290), ("PUNTO DEBOLE", "o", 392)])),
                (start("S3"), nxt("S3"), lor),
                (g_from, nxt("S4"), gia)]
    sfx = [(start(hook), 0.0, "comparsa", 0.14),
           (ref(HOOK_TXT[hook][1][2]), 0.0, "pop", 0.14),
           (start("S2"), 0.0, "whoosh", 0.12),
           (ref(111.26 + D), 0.0, "disegno", 0.14),
           (ref(111.26 + D), 0.5, "pop", 0.11),
           (start("S4"), 0.0, "whoosh", 0.10),
           (ref(130.85 + D), 0.0, "disegno", 0.14),
           (ref(130.85 + D), 0.45, "pop", 0.11)]
    def cut(fn):  # le grafiche spariscono mezzo fotogramma prima dello stacco (niente residui sul pezzo dopo)
        return lambda im, t, dur: None if t >= dur - 1 / 60 else fn(im, t, dur)
    overlays = [(a0, a1, cut(fn)) for a0, a1, fn in overlays]
    tot = build(dict(out=f"{OUT}/{v}", name=f"dip_sguardo_{v}", segs=segs, pages=pages, br=br, titles=[],
                     glow=[], overlays=overlays, sfx=sfx))
    # picco sotto -1 dBTP (la A usciva a -0,8): limiter leggero, la loudness resta -14
    f = f"{OUT}/{v}/dip_sguardo_{v}.mp4"
    sh(f"ffmpeg -v error -y -i {f} -c:v copy -af aresample=192000,alimiter=limit=0.85:level=false,aresample=48000 "
       f"-c:a aac -b:a 192k -movflags +faststart {f}.tmp.mp4 && mv {f}.tmp.mp4 {f}")
    return tot


if __name__ == "__main__":
    args = sys.argv[1:]
    if "prep" in args:
        prep()
        args.remove("prep")
    for v in (args or ["A", "B"]):
        make(v)
