#!/usr/bin/env python3
"""Copertine dei reel "3 regole d'oro per l'infortunio" (io che faccio 3 con le dita) e "fermi lunghi in panca"
(io perplesso sul controsenso). Titolo su 2 righe: riquadro nero + arancio (Inter Black Italic).
Salva anche l'anteprima del ritaglio 3:4 della griglia (y 240-1680)."""
from PIL import Image, ImageDraw, ImageFont

R = "/home/user/video-maker"
W, H = 1080, 1920
ORANGE = (232, 102, 44)
FB = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"


def label(im, txt, cx, y, size, box=(0, 0, 0), fg=(255, 255, 255)):
    ft = ImageFont.truetype(FB, size)
    l, t, r, b = ft.getbbox(txt)
    pw, ph = 34, 18
    w, h = r - l + pw * 2, b - t + ph * 2
    d = ImageDraw.Draw(im)
    d.rectangle([cx - w / 2, y, cx + w / 2, y + h], fill=box + (255,))
    d.text((cx - w / 2 + pw - l, y + ph - t), txt, font=ft, fill=fg)
    return y + h


# (cartella, fotogramma, y titolo, riga nera, riga arancio, dimensioni)
COVERS = [("infortunio", "st/c1.png", 1270, "LE 3 REGOLE D'ORO", "DOPO UN INFORTUNIO", (84, 84)),
          ("panca", "st/c4.png", 1062, "FAI FATICA AL PETTO?", "NON FARE I FERMI LUNGHI", (84, 70))]
for key, frame, y0, l1, l2, (s1, s2) in COVERS:
    D = f"{R}/out/{key}"
    im = Image.open(f"{D}/{frame}").convert("RGBA")
    y = label(im, l1, W / 2, y0, s1)
    label(im, l2, W / 2, y + 10, s2, box=ORANGE)
    im.convert("RGB").save(f"{D}/copertina_{key}.jpg", quality=95)
    im.convert("RGB").crop((0, 240, 1080, 1680)).resize((540, 720)).save(f"{D}/_check_griglia.jpg", quality=85)
print("ok")
