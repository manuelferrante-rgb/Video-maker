#!/usr/bin/env python3
"""Copertina "parte esterna del piede": io col piede disegnato ma sfocato (curiosità), in evidenza solo il titolo."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont

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
# piede sfocato: si intuisce la sagoma ma non si leggono punti e scritte
box = (20, 200, 520, 1040)
m = Image.new("L", im.size, 0)
ImageDraw.Draw(m).rounded_rectangle(box, radius=120, fill=255)
m = m.filter(ImageFilter.GaussianBlur(40))
face = Image.new("L", im.size, 0)  # la faccia resta nitida
ImageDraw.Draw(face).ellipse([395, 330, 690, 880], fill=255)
m = Image.composite(Image.new("L", im.size, 0), m, face.filter(ImageFilter.GaussianBlur(14)))
clean = Image.open(f"{D}/clean.png").convert("RGBA")  # stesso fotogramma senza grafica: sulla faccia niente scritte
im = Image.composite(im.filter(ImageFilter.GaussianBlur(9)), clean, m)  # si capisce che è un piede
y = label(im, "NESSUNO TE LO DICE", W / 2, 1060, 78)
y2 = label(im, "LA PARTE ESTERNA DEL PIEDE", W / 2, y + 8, 64, box=ORANGE)
# riquadro arancione sfocato: si vede che c'è una scritta ma non si legge bene (curiosità)
zone = (0, y + 2, W, y2 + 14)
im.paste(im.crop(zone).filter(ImageFilter.GaussianBlur(7)), zone[:2])
im.convert("RGB").save(f"{D}/copertina_piede_esterno.jpg", quality=95)
im.convert("RGB").crop((0, 240, 1080, 1680)).resize((540, 720)).save(f"{D}/_check_griglia.jpg", quality=85)
print("ok")
