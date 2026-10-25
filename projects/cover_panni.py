#!/usr/bin/env python3
"""Copertina "POV panni nella giungla": foto dei panni stesi + stessa scritta del reel (bianca, bordo nero, ombra,
centrata un po' sopra il centro). Controllo del ritaglio 3:4 della griglia."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = "/home/user/Video-maker/out/cover_panni"
W, H = 1080, 1920
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
size = 76
while ImageFont.truetype(FONT, size).getlength("POV: DEVI STENDERE I PANNI") > 900:  # dentro la safe zone (x 90-990)
    size -= 2
ft = ImageFont.truetype(FONT, size)

im = Image.open(f"{D}/foto.jpg").convert("RGB")
s = max(W / im.width, H / im.height)
im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
x0, y0 = (im.width - W) // 2, (im.height - H) // 2
im = im.crop((x0, y0, x0 + W, y0 + H)).convert("RGBA")

LINES = ["POV: DEVI STENDERE I PANNI", "NELLA GIUNGLA INDIANA", "E NON SAI COME FARE"]
LH = int(size * 1.2)
top = 760 - LH * len(LINES) / 2 + LH / 2
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))  # ombra morbida come nel reel
ds = ImageDraw.Draw(sh)
for k, ln in enumerate(LINES):
    ds.text((W / 2 + 4, top + k * LH + 5), ln, font=ft, anchor="mm", fill=(0, 0, 0, 150), stroke_width=7,
            stroke_fill=(0, 0, 0, 150))
im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)))
d = ImageDraw.Draw(im)
for k, ln in enumerate(LINES):
    d.text((W / 2, top + k * LH), ln, font=ft, anchor="mm", fill=(255, 255, 255), stroke_width=7, stroke_fill=(0, 0, 0))
im.convert("RGB").save(f"{D}/copertina_panni_giungla.jpg", quality=95)
im.convert("RGB").crop((0, 240, 1080, 1680)).resize((540, 720)).save(f"{D}/_check_griglia.jpg", quality=85)
print("ok")
