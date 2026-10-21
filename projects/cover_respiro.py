#!/usr/bin/env python3
"""Copertina "non prendere aria a ogni ripetizione": io in primo piano (fotogramma a 3,9 s, espressione stupita), titolo nella fascia 3:4 (stile copertina piede)."""
from PIL import Image, ImageDraw, ImageFont

D = "/home/user/Video-maker/out/cover_respiro"
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
y = label(im, "NON PRENDERE ARIA", W / 2, 1060, 86)
label(im, "AD OGNI RIPETIZIONE", W / 2, y + 8, 76, box=ORANGE)
im.convert("RGB").save(f"{D}/copertina_respiro.jpg", quality=95)
im.convert("RGB").crop((0, 240, 1080, 1680)).resize((540, 720)).save(f"{D}/_check_griglia.jpg", quality=85)
print("ok")
