#!/usr/bin/env python3
"""Copertina "parte esterna del piede": io col piede disegnato (punto 3 acceso), titolo nella fascia 3:4."""
from PIL import Image, ImageDraw, ImageFont

D = "/home/user/Video-maker/out/cover_piede"
W, H = 1080, 1920
ORANGE = (232, 102, 44)
FB = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"


def label(im, txt, cx, y, size, box=(0, 0, 0), fg=(255, 255, 255)):
    ft = ImageFont.truetype(FB, size)
    l, t, r, b = ft.getbbox(txt)
    pw, ph = 30, 16
    w, h = r - l + pw * 2, b - t + ph * 2
    d = ImageDraw.Draw(im)
    d.rectangle([cx - w / 2, y, cx + w / 2, y + h], fill=box + (255,))
    d.text((cx - w / 2 + pw - l, y + ph - t), txt, font=ft, fill=fg)
    return y + h


im = Image.open(f"{D}/base.png").convert("RGBA")
y = label(im, "NESSUNO TE LO DICE", W / 2, 1060, 78)
label(im, "LA PARTE ESTERNA DEL PIEDE", W / 2, y + 8, 64, box=ORANGE)
im.convert("RGB").save(f"{D}/copertina_piede_esterno.jpg", quality=95)
im.convert("RGB").crop((0, 240, 1080, 1680)).resize((540, 720)).save(f"{D}/_check_griglia.jpg", quality=85)
print("ok")
