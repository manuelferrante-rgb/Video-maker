#!/usr/bin/env python3
"""Copertina del reel "In che giorni allenarsi" (versioni A e B): io serio in camera, titolo su 2 righe
(riquadro nero + arancio, Inter Black Italic). Salva anche l'anteprima del ritaglio 3:4 della griglia."""
from PIL import Image, ImageDraw, ImageFont

R, W = "/home/user/video-maker", 1080
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

D = f"{R}/out/giorni"
im = Image.open(f"{D}/st/f_98.3.png").convert("RGBA").resize((1080, 1920))
y = label(im, "4 SEDUTE INTENSE?", W / 2, 1090, 84)
label(im, "SCEGLI I GIORNI GIUSTI", W / 2, y + 10, 74, box=ORANGE)
im.convert("RGB").save(f"{D}/copertina_giorni.jpg", quality=95)
im.convert("RGB").crop((0, 240, 1080, 1680)).resize((540, 720)).save(f"{D}/_check_griglia.jpg", quality=85)
print("ok")
