#!/usr/bin/env python3
"""Animazione della scheda vera di Elisabetta (ultima scheda, dal 02/11/2026) per il reel "Ti fidi della tua scheda?",
sulla frase "La programmazione la decido io" (subito prima di Manuel che corregge i video).
Fonte: PDF esportato dal foglio Drive "Elisabetta Scheda" (src_eli/scheda/scheda.pdf), ritagli a 1200 dpi.
Tre blocchi con metodologie diverse che scorrono uno dopo l'altro (slide a sinistra), su ognuno un riquadro arancio
passa le settimane:
  1) CHIN UP (giorno 1): serie a RPE con carico;
  2) SQUAT LB (giorno 1): top set + back off "8@8 + 2rir2 stesso peso";
  3) TRAZIONI ESPLOSIVE (giorno 3): cluster "4x1-1-1" con elastico (colonna VARIANTE).
Le colonne RPE / FEEDBACK (note personali di Elisabetta) restano sempre fuori. Niente etichette sopra (Manuel, 19/11).
Sfondo: fotogramma sfocato della clip successiva (Manuel al computer). Uscita: out/eli/anim/scheda.mp4 (1080x1920).
Uso: python3 projects/anim_scheda_elisabetta.py [durata_s]"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

R = "/home/user/video-maker"
D = f"{R}/out/eli/anim"
PDF = f"{R}/src_eli/scheda/scheda.pdf"
W, H, FPS = 1080, 1920, 30
ORANGE = (232, 102, 44)
DPI = 1200
K = DPI / 72.0

# (nome, colonne in pt [(x0, x1)...], header y (pt), confini righe WEEK 1-4 (pt))
BLOCKS = [("CHIN UP", [(77.4, 118.8)], (98.2, 102.5), [102.5, 105.3, 107.2, 109.1, 111.0]),
          ("SQUAT LB", [(77.4, 118.8)], (98.2, 102.5), [148.4, 153.8, 157.0, 159.5, 161.6]),
          ("TRAZIONI ESPLOSIVE", [(211.6, 236.5), (249.0, 271.0)], (98.2, 102.5),
           [102.5, 105.3, 107.2, 109.1, 111.0])]


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def crop(x0, y0, x1, y1, name):
    out = f"{D}/{name}"
    subprocess.run(["pdftoppm", "-r", str(DPI), "-f", "1", "-l", "1", "-x", str(round(x0 * K)), "-y",
                    str(round(y0 * K)), "-W", str(round((x1 - x0) * K)), "-H", str(round((y1 - y0) * K)),
                    "-png", "-singlefile", PDF, out], check=True)
    return Image.open(out + ".png").convert("RGB")


def make_card(i, name, cols, hdr, rows):
    """immagine della tabella (header + righe WEEK 1-4, colonne affiancate) -> scheda bianca arrotondata"""
    parts = []
    for j, (x0, x1) in enumerate(cols):
        top = crop(x0, hdr[0], x1, hdr[1], f"b{i}h{j}")
        body = crop(x0, rows[0], x1, rows[-1], f"b{i}r{j}")
        col = Image.new("RGB", (top.width, top.height + body.height), "white")
        col.paste(top, (0, 0)); col.paste(body, (0, top.height))
        parts.append(col)
    tab = Image.new("RGB", (sum(p.width for p in parts) + 6 * (len(parts) - 1), parts[0].height), "white")
    x = 0
    for p in parts:
        tab.paste(p, (x, 0)); x += p.width + 6
    CW = 960
    s = CW / tab.width
    tab = tab.resize((CW, int(tab.height * s)), Image.LANCZOS)
    y_rows = [((hdr[1] - hdr[0]) + (r - rows[0])) * K * s for r in rows]
    pad, top_h = 26, 96
    card = Image.new("RGBA", (CW + 2 * pad, tab.height + 2 * pad + top_h), (255, 255, 255, 255))
    dc = ImageDraw.Draw(card)
    dc.text((pad, 30), "SCHEDA DI ALLENAMENTO", font=ImageFont.truetype(
        "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", 40), fill=(20, 20, 20))
    dc.text((CW + pad, 38), name, font=ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 30),
            fill=(120, 120, 120), anchor="ra")
    card.paste(tab, (pad, pad + top_h))
    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, card.width - 1, card.height - 1], 34, fill=255)
    card.putalpha(mask)
    rows_px = [(pad + top_h + y_rows[k], pad + top_h + y_rows[k + 1]) for k in range(4)]
    return card, rows_px, pad, CW


def main(dur):
    os.makedirs(D, exist_ok=True)
    cards = [make_card(i, *b) for i, b in enumerate(BLOCKS)]
    bg = Image.open(f"{D}/bg.png").convert("RGB").resize((W, H)).filter(ImageFilter.GaussianBlur(26))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (10, 20, 34)), 0.55)
    cx, cy = W // 2, 820
    n = round(dur * FPS)
    seg = dur / len(cards)              # tempo per blocco
    SL = 0.17                           # durata dello slide tra un blocco e l'altro
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "15", "-pix_fmt", "yuv420p",
                          f"{D}/scheda.mp4"], stdin=subprocess.PIPE)
    for k in range(n):
        t = k / FPS
        fr = bg.copy().convert("RGBA")
        e_in = ease(t / 0.22)                                    # entrata della prima scheda
        zoom = 1 + 0.05 * ease(t / dur)                          # avvicinamento lento continuo
        for i, (card, rows, pad, CW) in enumerate(cards):
            t0 = i * seg
            # posizione orizzontale: entra da destra (tranne la prima), esce a sinistra quando arriva la successiva
            x_in = 0.0 if i == 0 else (1 - ease((t - t0) / SL)) * W
            x_out = -ease((t - (t0 + seg)) / SL) * W if i < len(cards) - 1 else 0.0
            if t < t0 - 0.001 or (i < len(cards) - 1 and t > t0 + seg + SL):
                continue
            c = card.copy()
            d = ImageDraw.Draw(c)
            # riquadro arancio che scorre WEEK 1 -> 4
            tl = t - (t0 + (0.12 if i == 0 else SL))
            step = (seg - SL - 0.05) / 4
            j = min(int(tl / step), 3) if tl >= 0 else -1
            if j >= 0:
                a, b = rows[j]
                if j > 0:
                    f = ease((tl - j * step) / min(0.08, step))
                    pa, pb = rows[j - 1]
                    a, b = pa + (a - pa) * f, pb + (b - pb) * f
                d.rounded_rectangle([pad - 6, a - 2, pad + CW + 6, b + 2], 10, outline=ORANGE + (255,), width=7)
            sc = zoom * (0.93 + 0.07 * e_in if i == 0 else 1.0)
            cs = c.resize((int(c.width * sc), int(c.height * sc)), Image.LANCZOS)
            al = e_in if i == 0 else 1.0
            if al < 1:
                cs.putalpha(cs.split()[3].point(lambda v: int(v * al)))
            x0 = cx - cs.width / 2 + x_in + x_out
            y0 = cy - cs.height / 2 + (90 * (1 - e_in) if i == 0 else 0)
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(sh).rounded_rectangle([x0 + 8, y0 + 18, x0 + cs.width + 8, y0 + cs.height + 18], 34,
                                                 fill=(0, 0, 0, int(110 * al)))
            fr.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))   # paste accetta coordinate negative (slide fuori)
            lay.paste(cs, (int(x0), int(y0)), cs)
            fr.alpha_composite(lay)
        p.stdin.write(fr.convert("RGB").tobytes())
    p.stdin.close(); p.wait()


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 1.6)
