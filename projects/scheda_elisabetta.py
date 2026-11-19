#!/usr/bin/env python3
"""Puntata 3: "Ti fidi della tua scheda?" (Elisabetta, 19/11/2026, brief sez. 7d, copy in projects/script_scheda_elisabetta.md).
A: primo fotogramma = Elisabetta alla sbarra con 10 kg (IMG_5416b), un solo testo "TI FIDI DELLA / TUA SCHEDA?" in basso,
poi sottotitoli e "+10 KG". B: split PRIMA (video dei primi tempi, all'aperto senza zavorra, fermo prima che il mento
superi la sbarra) | OGGI (10 kg), "0 KG" / "+10 KG". Corpo uguale: Manuel in camera (TU L'OBIETTIVO / IO IL PERCORSO),
Elisabetta in allenamento (palestra arancio), la sua scheda vera animata (anim_scheda_elisabetta.py, 3 blocchi) su
"La programmazione la decido io", Manuel al computer che guarda un video, Elisabetta con Manuel sullo sfondo,
ripetizione chiusa, CTA in camera con il campo commento (controllo / mi fido), ponte sul primo fotogramma (loop).
Parlato: src_eli/IMG_9169.MOV -> src_eli/p_norm.mov. Clip HLG (IMG_54xx) gia' convertiti in out/eli/br.
Uso: python3 projects/scheda_elisabetta.py [prep] [A B]"""
import os, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, "/home/user/video-maker/projects")
from reel_kit import build, OR, WH, R, ORANGE, BLACK, ease
from PIL import Image, ImageDraw, ImageFont

S = f"{R}/src_eli"
NORM = f"{S}/p_norm.mov"
BR = f"{R}/out/eli/br"
OUT = f"{R}/out/eli"
FBI = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
TM = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,"
      "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")


def sh(c):
    subprocess.run(c, shell=True, check=True)


def prep():
    os.makedirs(BR, exist_ok=True)
    if not os.path.exists(NORM):
        sh(f"ffmpeg -v error -y -i {S}/IMG_9169.MOV -vf scale=1080:1920:flags=lanczos,setsar=1 -c:v libx264 -crf 14 "
           f"-preset fast -pix_fmt yuv420p -c:a pcm_s16le -ar 48000 -ac 2 {NORM}")
    if not os.path.exists(f"{OUT}/parlato.wav"):
        sh(f"ffmpeg -v error -y -i {S}/IMG_9169.MOV -vn -ac 1 -ar 16000 {OUT}/parlato.wav")
    for f, ext in (("IMG_5415", "MOV"), ("IMG_5416b", "mov"), ("IMG_5418", "MOV")):   # HLG -> SDR
        if os.path.exists(f"{BR}/{f}.mp4"):
            continue
        sh(f"ffmpeg -v error -y -i {S}/{f}.{ext} -vf \"{TM},scale=1080:1920:flags=lanczos,setsar=1\" -an -c:v libx264 "
           f"-crf 14 -preset fast -pix_fmt yuv420p {BR}/{f}.mp4")
    if not os.path.exists(f"{BR}/IMG_9172.mp4"):
        sh(f"ffmpeg -v error -y -i {S}/IMG_9172.mov -vf scale=1080:1920:flags=lanczos,setsar=1 -an -c:v libx264 -crf 14 "
       f"-preset fast -pix_fmt yuv420p {BR}/IMG_9172.mp4")
    # split del gancio B: PRIMA (tg_3mb 14.7 -> 17.2, poi fermo: il mento non supera la sbarra) | OGGI (5416b da 0.5)
    sh(f"ffmpeg -v error -y -ss 14.7 -t 2.5 -i {S}/tg_3mb.mp4 -ss 0.5 -t 4.0 -i {BR}/IMG_5416b.mp4 -filter_complex "
       f"\"[0:v]fps=30,scale=1080:1920:flags=lanczos,unsharp=5:5:0.5,crop=540:1920:130:0,"
       f"tpad=stop_mode=clone:stop_duration=3[l];[1:v]fps=30,crop=540:1920:360:0[r];[l][r]hstack=shortest=1,"
       f"drawbox=x=537:y=0:w=6:h=1920:color=white:t=fill,setsar=1[v]\" -map \"[v]\" -an -frames:v 120 "
       f"-c:v libx264 -crf 15 -pix_fmt yuv420p {BR}/split.mp4")
    # allenamento (palestra arancio, senza zavorra)
    sh(f"ffmpeg -v error -y -ss 21.0 -t 3.0 -i {S}/tg_9mb.mp4 -vf fps=30,scale=1080:1920:flags=lanczos,"
       f"unsharp=5:5:0.5,setsar=1 -an -c:v libx264 -crf 15 -pix_fmt yuv420p {BR}/allen.mp4")


PH = {"HA": [(22.96, 25.27)],                    # Ti fidi della tua scheda? Elisabetta all'inizio no.
      "HB": [(38.14, 39.88), (44.35, 45.59)],     # Elisabetta non riusciva a fare una trazione, | oggi la fa con 10 kg.
      "S1": [(55.19, 58.08)],                     # Le ho detto, tu scegli l'obiettivo, il percorso lo decido io.
      "S2": [(66.56, 69.21)],                     # Voleva ogni numero e un record a ogni seduta.
      "S3": [(107.84, 110.55)],                   # La programmazione la decido io e io correggo i video.
      "S3b": [(114.18, 116.15)],                  # Lei pensa solo alla seduta di oggi.
      "S4": [(127.70, 130.13)],                   # Da quando si e' affidata ha smesso di bloccarsi.
      "S5": [(163.02, 165.59)],                   # E tu controlli o ti fidi? Scrivilo nei commenti.
      "S6A": [(168.20, 169.38)],                  # Perche' la domanda e' una sola...
      "S6B": [(171.23, 171.92)]}                  # Per questo...
BODY = ["S1", "S2", "S3", "S3b", "S4", "S5"]
D = 0.18
KARA = {"HA": [("TI", 22.93), ("FIDI", 23.09), ("DELLA", 23.41), ("|", 0), ("TUA", 23.57), ("SCHEDA?", 23.73), ("/", 0),
               ("ELISABETTA", 24.05), ("|", 0), ("ALL'INIZIO", 24.61), ("NO.", 25.09)],
        "HB": [("ELISABETTA", 38.04), ("NON", 38.68), ("|", 0), ("RIUSCIVA", 38.76), ("/", 0), ("A", 39.08),
               ("FARE", 39.16), ("UNA", 39.24), ("|", 0), ("TRAZIONE,", 39.48), ("/", 0), ("OGGI", 44.33), ("LA", 44.55),
               ("FA", 44.71), ("|", 0), ("CON", 44.87), ("10", 45.03), ("KG", 45.27)],
        "S1": [("LE", 55.09), ("HO", 55.25), ("DETTO:", 55.41), ("/", 0), ("TU", 55.73), ("SCEGLI", 55.89), ("|", 0),
               ("L'OBIETTIVO,", 56.21), ("/", 0), ("IL", 56.85), ("PERCORSO", 57.01), ("|", 0), ("LO", 57.41),
               ("DECIDO", 57.57), ("IO", 57.89)],
        "S2": [("VOLEVA", 66.46), ("OGNI", 67.02), ("|", 0), ("NUMERO", 67.34), ("/", 0), ("E", 67.58), ("UN", 67.74),
               ("RECORD", 67.90), ("|", 0), ("A", 68.22), ("OGNI", 68.46), ("SEDUTA", 68.70)],
        "S3": [("LA", 107.74), ("PROGRAMMAZIONE", 107.98), ("|", 0), ("LA", 108.62), ("DECIDO", 108.78), ("IO", 109.18),
               ("/", 0), ("E", 109.34), ("IO", 109.50), ("CORREGGO", 109.66), ("|", 0), ("I", 110.14), ("VIDEO", 110.22)],
        "S3b": [("LEI", 114.08), ("PENSA", 114.48), ("SOLO", 114.88), ("|", 0), ("ALLA", 115.04), ("SEDUTA", 115.28),
                ("DI", 115.76), ("OGGI", 115.84)],
        "S4": [("DA", 127.64), ("QUANDO", 127.88), ("SI", 128.12), ("È", 128.20), ("|", 0), ("AFFIDATA", 128.28),
               ("/", 0), ("HA", 128.76), ("SMESSO", 128.92), ("|", 0), ("DI", 129.32), ("BLOCCARSI", 129.48)],
        "S5": [("E", 162.92), ("TU", 163.08), ("CONTROLLI", 163.32), ("|", 0), ("O", 163.80), ("TI", 163.88),
               ("FIDI?", 164.04), ("/", 0), ("SCRIVILO", 164.52), ("|", 0), ("NEI", 165.00), ("COMMENTI", 165.16)],
        "S6A": [("PERCHÉ", 168.10), ("LA", 168.42), ("DOMANDA", 168.50), ("|", 0), ("È", 168.74), ("UNA", 168.90),
                ("SOLA...", 169.14)],
        "S6B": [("PER", 171.21), ("QUESTO...", 171.45)]}

_a, _sr = sf.read(f"{OUT}/parlato.wav", dtype="float32")
_n = len(_a) // 160
_DB = 20 * np.log10(np.sqrt((_a[:_n * 160].reshape(_n, 160) ** 2).mean(1)) + 1e-9)
_V = _DB > np.percentile(_DB, 98) - 32

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


def comment_box(t_in, t_a, t_b, y=1240, wa="giù", wb="in alto"):
    """campo commento stile Instagram (pillola bianca) sul petto, tra faccia e sottotitoli: compare, poi si scrive
    "giu'" (t_a) e "in alto" (t_b) a tempo con la voce, cursore arancio, "Pubblica" si accende alla fine"""
    W0, H0 = 820, 112
    fm = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 46)
    fp = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", 37)
    fs = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 38)

    def card(txt, typed, pub):
        im = Image.new("RGBA", (W0 + 20, H0 + 20), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([12, 14, W0 + 12, H0 + 14], 56, fill=(0, 0, 0, 70))          # ombra leggera
        d.rounded_rectangle([10, 10, W0 + 10, H0 + 10], 56, fill=(255, 255, 255, 255))
        cx, cy, r = 10 + 60, 10 + H0 // 2, 34                                             # avatar generico
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(205, 205, 210, 255))
        d.ellipse([cx - 12, cy - 22, cx + 12, cy + 2], fill=(250, 250, 250, 255))
        d.pieslice([cx - 24, cy + 4, cx + 24, cy + 50], 180, 360, fill=(250, 250, 250, 255))
        x0 = 10 + 118
        if typed:
            d.text((x0, cy), txt, font=fm, fill=(20, 20, 20, 255), anchor="lm")
            w = d.textlength(txt, font=fm)
        else:
            d.text((x0, cy), "Aggiungi un commento...", font=fp, fill=(150, 150, 155, 255), anchor="lm")
            w = 0
        col = ORANGE + (255,) if pub else (232, 102, 44, 110)
        d.text((W0 - 24, cy), "Pubblica", font=fs, fill=col, anchor="rm")
        return im, x0 + w

    def draw(im, t, dur):
        x = t - t_in
        if x < 0:
            return
        e = ease(x / 0.25)
        fade = (1 - ease((t - (dur - 0.15)) / 0.15)) * e
        if t >= t_b:
            k = min(int((t - t_b) / 0.03) + 1, len(wb))
            txt, typed = wb[:k], True
        elif t >= t_a:
            k = min(int((t - t_a) / 0.03) + 1, len(wa))
            txt, typed = wa[:k], True
        else:
            txt, typed = "", False
        c, xc = card(txt, typed, t >= t_b + 0.22)
        if typed and int(t * 3.4) % 2 == 0:  # cursore che lampeggia
            ImageDraw.Draw(c).rectangle([xc + 4, 10 + H0 // 2 - 24, xc + 8, 10 + H0 // 2 + 24], fill=ORANGE + (255,))
        s = 0.9 + 0.1 * e
        c = c.resize((int(c.width * s), int(c.height * s)), Image.LANCZOS)
        if fade < 1:
            c.putalpha(c.split()[3].point(lambda v: int(v * fade)))
        im.alpha_composite(c, (int(540 - c.width / 2), int(y + 30 * (1 - e) - c.height / 2)))
    return draw




def hook_a(t_kg):
    """gancio A: un solo testo (TI FIDI DELLA / TUA SCHEDA?) in basso sul primo fotogramma, poi "+10 KG" in alto a sx"""
    rows = [(label("TI FIDI DELLA", BLACK, 76), 1395), (label("TUA SCHEDA?", ORANGE, 76), 1503)]
    kg = label("+10 KG", ORANGE, 64)

    def draw(im, t, dur):
        for lab, y in rows:
            if t >= t_kg - 0.15:  # quando partono i sottotitoli il titolo sparisce: un solo testo alla volta
                break
            im.alpha_composite(lab, (int(540 - lab.width / 2), int(y - lab.height / 2)))
        x = t - t_kg
        if x >= 0:
            s = popscale(x)
            lb = kg.resize((int(kg.width * s), int(kg.height * s)), Image.LANCZOS)
            im.alpha_composite(lb, (int(215 - lb.width / 2), int(470 - lb.height / 2)))
    return draw


def split_labels(t_r):
    """gancio B: una parola per lato sullo split, sotto i corpi (in alto ci sono sbarra e teste)"""
    labs = [("L", label("0 KG", BLACK, 72), None), ("R", label("+10 KG", ORANGE, 72), t_r)]

    def draw(im, t, dur):
        for side, lab, t0 in labs:
            if t0 is not None and t < t0:
                continue
            s = 1.0 if t0 is None else popscale(t - t0)
            lb = lab.resize((int(lab.width * s), int(lab.height * s)), Image.LANCZOS)
            cx = 270 if side == "L" else 810
            im.alpha_composite(lb, (int(cx - lb.width / 2), int(1240 - lb.height / 2)))
    return draw


def make(v):
    hook, ponte = f"H{v}", f"S6{v}"
    names = [hook] + BODY + [ponte]
    segs = []
    for n in names:
        for a, b in PH[n]:
            for s0, s1 in subsegs(a, b):
                segs.append((NORM, s0, s1))

    def ref(src):
        for k, (_, s0, s1) in enumerate(segs):
            if src < s1:
                return (k, max(src, s0))
        return (len(segs) - 1, segs[-1][2])

    def start(n):
        return ref(PH[n][0][0])

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

    def loc(src, n):
        return t_of(src) - t_of(PH[n][0][0])

    pages = []
    for n in names:
        kp = kara_pages(n)
        if n == "HA":  # nel gancio A il primo testo e' il titolo grande: i sottotitoli partono da "Elisabetta"
            kp = [p for p in kp if "ELISABETTA" in p[1]]
            kp[0] = (kp[0][0], kp[0][1].lstrip("§"))
        for i, (s, txt) in enumerate(kp):
            pages.append(((start(n) if (i == 0 and n != "HA") else ref(s)), txt))
    first = f"{BR}/IMG_5416b.mp4" if v == "A" else f"{BR}/split.mp4"
    br = [(start(hook), nxt(hook), first, 0.5 if v == "A" else 0.0, 1.0, 1.0, None),
          (start("S2"), nxt("S2"), f"{BR}/allen.mp4", 0.0, 1.0, 1.0, None),
          (start("S3"), ref(109.40), f"{OUT}/anim/scheda.mp4", 0.0, 1.0, 1.0, None),   # scheda vera animata
          (ref(109.40), nxt("S3"), f"{BR}/IMG_9172.mp4", 0.2, 1.0, 1.0, None),        # "e io correggo i video"
          (start("S3b"), nxt("S3b"), f"{BR}/IMG_5418.mp4", 5.0, 1.0, 1.0, None),
          (start("S4"), nxt("S4"), f"{BR}/IMG_5415.mp4", 2.7, 1.0, 1.0, None),
          (start(ponte), "end", first, 0.5 if v == "A" else 0.0, 1.0, 1.0, None)]
    if v == "A":
        hk = hook_a(t_of(24.05 + D) - t_of(PH[hook][0][0]) + 0.15)
        s_hook = [(start(hook), 0.0, "comparsa", 0.14), (ref(24.05 + D), 0.15, "pop", 0.12)]
    else:
        hk = split_labels(t_of(44.33 + D) - t_of(PH[hook][0][0]))
        s_hook = [(start(hook), 0.0, "comparsa", 0.14), (ref(44.35), 0.0, "pop", 0.14)]
    overlays = [(start(hook), nxt(hook), hk),
                (start("S1"), nxt("S1"), titles([("TU L'OBIETTIVO", "n", 290), ("IO IL PERCORSO", "o", 392)])),
                (start("S5"), nxt("S5"), comment_box(0.12, loc(163.32 + D - 0.08, "S5"), loc(163.88 + D - 0.1, "S5"),
                                                     wa="controllo", wb="mi fido"))]
    t_an = t_of(109.40) - t_of(107.84)            # durata dell'animazione della scheda (3 blocchi)
    sfx = s_hook + [(start("S1"), 0.0, "whoosh", 0.12),
                    (start("S3"), t_an / 3, "swoosh", 0.08),
                    (start("S3"), 2 * t_an / 3, "swoosh", 0.08),
                    (start("S5"), 0.1, "comparsa", 0.10),
                    (ref(163.32 + D), 0.0, "pop", 0.07),
                    (ref(163.88 + D), 0.0, "pop", 0.07)]

    def cut(fn):
        return lambda im, t, dur: None if t >= dur - 1 / 60 else fn(im, t, dur)
    overlays = [(a0, a1, cut(fn)) for a0, a1, fn in overlays]
    tot = build(dict(out=f"{OUT}/{v}", name=f"scheda_elisabetta_{v}", segs=segs, pages=pages, br=br, titles=[],
                     glow=[], overlays=overlays, sfx=sfx))
    f = f"{OUT}/{v}/scheda_elisabetta_{v}.mp4"
    sh(f"ffmpeg -v error -y -i {f} -c:v copy -af aresample=192000,alimiter=limit=0.79:level=false,aresample=48000 "
       f"-c:a aac -b:a 192k -movflags +faststart {f}.tmp.mp4 && mv {f}.tmp.mp4 {f}")
    return tot


if __name__ == "__main__":
    args = sys.argv[1:]
    if "prep" in args:
        prep()
        args.remove("prep")
    for v in (args or ["A", "B"]):
        make(v)
