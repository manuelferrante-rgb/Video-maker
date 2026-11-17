#!/usr/bin/env python3
"""Rifacimento "Tacco o senza" (17/11/2026, brief_editor_novembre.md sez. 5). Max 18 s, a loop.
Primo fotogramma = split screen Jasmin col tacco | Nicolo' senza con la voce sopra; un solo testo grande per lato
("200 KG" / "SENZA"); io in camera dalla frase "Li alleno tutti e due. Decide la caviglia"; Jasmin a tutto schermo
ferma in buca con la linea caviglia-ginocchio; Nicolo' a tutto schermo; CTA in camera; "Ecco perche'..." sullo split
iniziale (riparte il gancio). Versione A: gancio "Jasmin squatta 200 kg col tacco. Nicolo', senza."
Versione B: "Due miei atleti. Uno squatta col tacco, uno senza." Parlato: src_tacco/parlato2.MOV (IMG_9108).
Uso: python3 projects/tacco_v2.py [A B]"""
import sys
import numpy as np, soundfile as sf
sys.path.insert(0, "/home/user/video-maker/projects")
from reel_kit import build, OR, WH, R, ORANGE, BLACK, ease, box
from PIL import Image, ImageDraw, ImageFont

S = f"{R}/src_tacco"
NORM, ZOOM = f"{S}/p2_norm.mov", f"{S}/p2_zoom.mov"
OUT = f"{R}/out/tacco_v2"
FBI = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"

PH = {"HA": (9.70, 12.68, NORM),    # Jasmin squatta 200 kg con il tacco, Nicolo' senza
      "HB": (16.95, 20.04, NORM),   # Due miei atleti, uno squatta col tacco, uno senza
      "S2": (33.40, 35.58, NORM),   # Li alleno tutti e due io, decide la caviglia
      "S3": (59.73, 63.97, NORM),   # Jasmin ha la caviglia rigida, col tacco il ginocchio va avanti e il peso...
      "S4": (82.90, 86.12, NORM),   # Nicolo' ce l'ha mobile, scende gia' verticale, il tacco non gli serve
      "S5": (90.40, 92.85, ZOOM),   # Tu lo usi? Scrivi tacco o senza
      "S6": (93.13, 93.86, NORM)}   # Ecco perche'...
BODY = ["S2", "S3", "S4", "S5", "S6"]
# sottotitoli parola per parola: la parola detta in quel momento e' arancio (tempi = parola nel sorgente).
# "/" = nuova pagina, "|" = a capo.
KARA = {"HA": [("JASMIN", 9.75), ("SQUATTA", 10.39), ("|", 0), ("200", 10.87), ("KG", 11.19), ("CON", 11.51),
               ("IL", 11.59), ("TACCO,", 11.67), ("/", 0), ("NICOLÒ,", 11.99), ("SENZA", 12.47)],
        "HB": [("DUE", 17.0), ("MIEI", 17.4), ("ATLETI,", 17.64), ("/", 0), ("UNO", 18.12), ("SQUATTA", 18.36),
               ("|", 0), ("COL", 18.84), ("TACCO,", 19.08), ("/", 0), ("UNO", 19.48), ("SENZA", 19.8)],
        "S2": [("LI", 33.45), ("ALLENO", 33.69), ("TUTTI", 34.09), ("|", 0), ("E", 34.17), ("DUE", 34.25), ("E", 34.41),
               ("IO,", 34.57), ("/", 0), ("DECIDE", 34.81), ("LA", 35.13), ("|", 0), ("CAVIGLIA", 35.29)],
        "S3": [("JASMIN", 59.75), ("HA", 60.39), ("LA", 60.47), ("|", 0), ("CAVIGLIA", 60.55), ("RIGIDA,", 60.87),
               ("/", 0), ("COL", 61.19), ("TACCO", 61.43), ("IL", 61.75), ("|", 0), ("GINOCCHIO", 61.83), ("VA", 62.23),
               ("AVANTI", 62.31), ("/", 0), ("E", 62.55), ("IL", 62.63), ("PESO", 62.71), ("RIMANE", 63.03), ("|", 0),
               ("AL", 63.35), ("CENTRO", 63.51), ("DEL", 63.75), ("PIEDE", 63.83)],
        "S4": [("NICOLÒ", 82.94), ("CE", 83.30), ("L'HA", 83.45), ("|", 0), ("MOBILE,", 83.66), ("/", 0),
               ("SCENDE", 83.98), ("GIÀ", 84.38), ("|", 0), ("VERTICALE,", 84.62), ("/", 0), ("IL", 85.1),
               ("TACCO", 85.26), ("|", 0), ("NON", 85.66), ("GLI", 85.82), ("SERVE", 85.98)],
        "S5": [("TU", 90.45), ("LO", 90.69), ("USI?", 90.85), ("/", 0), ("SCRIVI", 91.25), ("TACCO", 91.81), ("|", 0),
               ("O", 92.37), ("SENZA", 92.61)],
        "S6": [("ECCO", 93.25), ("PERCHÉ...", 93.65)]}


def kara_pages(n):
    """una riga ASS per ogni parola: stessa pagina, la parola corrente in arancio (la prima della pagina col pop)"""
    pages, cur = [], []
    for w, t in KARA[n] + [("/", 0)]:
        if w == "/":
            if cur:
                pages.append(cur)
            cur = []
        else:
            cur.append((w, t))
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
            # la prima parola della pagina parte al taglio di inizio pagina (niente buchi); le altre sul tempo detto
            out.append((t if k else t - 0.05, ("" if k == 0 else "§") + txt))
    return out


# testo grande sullo split: (lato, testo, istante sorgente in cui compare)
HOOK_TXT = {"HA": [("L", "200 KG", None), ("R", "SENZA", 11.95)],
            "HB": [("L", "COL TACCO", None), ("R", "SENZA", 19.45)]}

_a, _sr = sf.read(f"{R}/out/tacco/parlato2_16k.wav", dtype="float32")
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


def big_label(txt, size):
    ft = ImageFont.truetype(FBI, size)
    l, t, r, b = ft.getbbox(txt)
    pad = 26
    im = Image.new("RGBA", (r - l + 2 * pad, b - t + 2 * pad), (0, 0, 0, 0))
    return im, ft, l, t, pad


def hook_text(items, t_of):
    """un testo grande per lato dello split (riquadro arancio a sinistra, nero a destra), con pop d'ingresso"""
    labs = []
    for side, txt, src in items:
        size = 118 if len(txt) <= 6 else 76
        ft = ImageFont.truetype(FBI, size)
        l, t, r, b = ft.getbbox(txt)
        w, h = r - l + 56, b - t + 44
        im = Image.new("RGBA", (w, h), (ORANGE if side == "L" else BLACK) + (255,))
        ImageDraw.Draw(im).text((28 - l, 22 - t), txt, font=ft, fill=(255, 255, 255))
        labs.append((side, im, 0.0 if src is None else t_of(src)))

    def draw(im, t, dur):
        for side, lab, t0 in labs:
            x = t - t0
            if x < 0:
                continue
            s = 0.75 + 0.25 * ease(x / 0.18) if x < 0.18 else 1.0
            if t0 == 0.0:
                s = 1.0  # il primo testo c'e' gia' dal primo fotogramma
            lb = lab.resize((int(lab.width * s), int(lab.height * s)), Image.LANCZOS)
            cx = 270 if side == "L" else 810
            im.alpha_composite(lb, (int(cx - lb.width / 2), int(470 - lb.height / 2)))
    return draw


def shin_line(t_line, t_dot):
    """linea caviglia-ginocchio su Jasmin ferma in buca + verticale tratteggiata di riferimento"""
    ank, kne = (548, 1285), (655, 1100)

    def draw(im, t, dur):
        x = t - t_line
        if x < 0:
            return
        d = ImageDraw.Draw(im)
        e = ease(x / 0.35)
        # verticale di riferimento (tratteggiata) dalla caviglia in su
        for k in range(0, int(200 * e), 22):
            d.line([(ank[0], ank[1] - k), (ank[0], ank[1] - k - 12)], fill=(255, 255, 255, 200), width=5)
        px = ank[0] + (kne[0] - ank[0]) * e
        py = ank[1] + (kne[1] - ank[1]) * e
        d.line([ank, (px, py)], fill=ORANGE + (255,), width=9)
        for c in (ank, (px, py)):
            d.ellipse([c[0] - 13, c[1] - 13, c[0] + 13, c[1] + 13], fill=(255, 255, 255, 255),
                      outline=ORANGE + (255,), width=5)
        y = t - t_dot  # punto a meta' piede (piccolo, non tocca i sottotitoli)
        if y >= 0:
            r = 20 * (0.6 + 0.4 * ease(y / 0.2))
            mx, my = 522, 1352
            d.ellipse([mx - r - 8, my - r - 8, mx + r + 8, my + r + 8], outline=(255, 255, 255, 230), width=4)
            d.ellipse([mx - r, my - r, mx + r, my + r], fill=ORANGE + (255,))
    return draw


def make(v):
    hook = f"H{v}"
    names = [hook] + BODY
    segs = []
    for n in names:
        a, b, f = PH[n]
        for s0, s1 in subsegs(a, b):
            segs.append((f, s0, s1))

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

    # tempi nel reel per i livelli disegnati: li calcolo come fa reel_kit (1.1x, segmenti a fotogrammi interi)
    SO, t = [], 0.0
    for _, a, b in segs:
        SO.append(t)
        t += round((b - a) / 1.1 * 30) / 30

    def t_of(src):
        k, s = ref(src)
        return SO[k] + (s - segs[k][1]) / 1.1

    pages = [(ref(PH[n][0]) if i == 0 else ref(s), txt)
             for n in names for i, (s, txt) in enumerate(kara_pages(n))]
    br = [(start(hook), nxt(hook), f"{S}/split.mp4", 0.0, 1.0, 1.0, None),
          (start("S3"), nxt("S3"), f"{S}/j_hold.mp4", 0.0, 1.0, 1.15, (540, 1200)),
          (start("S4"), nxt("S4"), f"{S}/b2.mp4", 0.7, 1.0, 1.6, (630, 1330)),
          (start("S6"), "end", f"{S}/split.mp4", 0.0, 1.0, 1.0, None)]
    titles = [dict(t0=start("S2"), t1=nxt("S2"), items=[("DECIDE LA CAVIGLIA", "o")]),
              dict(t0=start("S3"), t1=nxt("S3"), items=[("TACCO SÌ", "o")]),
              dict(t0=start("S4"), t1=nxt("S4"), items=[("TACCO NO", "n")])]
    glow = []
    t_line = t_of(61.17) - t_of(PH["S3"][0])
    t_dot = t_of(62.53) - t_of(PH["S3"][0])
    overlays = [(start(hook), nxt(hook), hook_text(HOOK_TXT[hook], lambda s: t_of(s))),
                (start("S3"), nxt("S3"), shin_line(t_line, t_dot))]
    sfx = [(start(hook), 0.0, "comparsa", 0.14),
           (ref(HOOK_TXT[hook][1][2]), 0.0, "pop", 0.14),
           (start("S2"), 0.0, "whoosh", 0.12),
           (ref(61.17), 0.0, "disegno", 0.16),
           (ref(62.53), 0.05, "pop", 0.12),
           (start("S4"), 0.0, "whoosh", 0.12)]
    return build(dict(out=f"{OUT}/{v}", name=f"tacco_v2_{v}", segs=segs, pages=pages, br=br, titles=titles,
                      glow=glow, overlays=overlays, sfx=sfx))


if __name__ == "__main__":
    for v in (sys.argv[1:] or ["A", "B"]):
        make(v)
