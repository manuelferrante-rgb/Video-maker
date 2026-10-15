#!/usr/bin/env python3
"""Copertina "stesso peso, esercizi diversi": lui in primo piano sopra la sbarra (muscle up), io in un riquadro
con la trazione. Testo nella fascia 3:4 della griglia profilo (y 240-1680)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = "/home/user/Video-maker/out/cover_am"
W, H = 1080, 1920
ORANGE, IVORY, NAVY_D = (232, 102, 44), (242, 238, 227), (10, 26, 44)
FB = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"


def label(im, txt, cx, y, size, box=(0, 0, 0), fg=(255, 255, 255), rot=0):
    ft = ImageFont.truetype(FB, size)
    l, t, r, b = ft.getbbox(txt)
    pw, ph = 30, 16
    w, h = r - l + pw * 2, b - t + ph * 2
    tile = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(tile)
    d.rectangle([0, 0, w, h], fill=box + (255,))
    d.text((pw - l, ph - t), txt, font=ft, fill=fg)
    if rot:
        tile = tile.rotate(rot, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(tile, (int(cx - tile.width / 2), int(y)))
    return y + h


# sfondo: lui in cima al muscle up, spostato in basso perché la testa stia sotto il titolo
src = Image.open(f"{D}/f_154.8.png").convert("RGB")
S = 1.22
big = src.resize((int(src.width * S), int(src.height * S)), Image.LANCZOS)
head_src = (620, 200)
ox, oy = int(520 - head_src[0] * S), int(640 - head_src[1] * S)
canvas = big.resize((W, H)).filter(ImageFilter.GaussianBlur(40)).convert("RGBA")  # riempimento sopra
canvas.alpha_composite(big.convert("RGBA"), (ox, oy))
# sfumatura per unire la parte alta e scurire leggermente in alto e in basso
ov = Image.new("RGBA", (W, H))
d = ImageDraw.Draw(ov)
for y in range(H):
    a = 0
    if y < oy + 160:
        a = 0.92 * max(0, min(1, (oy + 160 - y) / 260))
    if y > 1500:
        a = max(a, 0.55 * (y - 1500) / 420)
    a = max(a, 0.12)
    d.line([(0, y), (W, y)], fill=NAVY_D + (int(255 * a),))
canvas.alpha_composite(ov)

# riquadro: io con la trazione
me = Image.open(f"{D}/f_74.3.png").convert("RGB").crop((180, 420, 820, 1380))
cw, chh = 400, 600
me = me.resize((cw, chh), Image.LANCZOS)
card = Image.new("RGBA", (cw + 16, chh + 16), (0, 0, 0, 0))
mask = Image.new("L", (cw, chh), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw, chh], radius=30, fill=255)
ImageDraw.Draw(card).rounded_rectangle([0, 0, cw + 15, chh + 15], radius=36, fill=IVORY + (255,))
card.paste(me, (8, 8), mask)
card = card.rotate(4, expand=True, resample=Image.BICUBIC)
shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
shadow.putalpha(card.split()[3].point(lambda v: int(v * 0.55)))
shadow = shadow.filter(ImageFilter.GaussianBlur(18))
cx0, cy0 = 640, 980
canvas.alpha_composite(shadow, (cx0 + 10, cy0 + 16))
canvas.alpha_composite(card, (cx0, cy0))
label(canvas, "IO: TRAZIONI", cx0 + card.width / 2, cy0 + card.height - 40, 54, rot=4)

# lui
label(canvas, "LUI: MUSCLE UP", 330, 1140, 60, box=ORANGE, rot=-3)

# titolo
y = label(canvas, "STESSO PESO", W / 2, 280, 118)
label(canvas, "ESERCIZI DIVERSI", W / 2, y + 8, 92, box=ORANGE)

canvas.convert("RGB").save("/home/user/Video-maker/out/cover_am/copertina_allievo_maestro.jpg", quality=95)
# anteprima ritaglio griglia 3:4
pv = canvas.convert("RGB").crop((0, 240, 1080, 1680)).resize((540, 720))
pv.save("/home/user/Video-maker/out/cover_am/_check_griglia.jpg", quality=85)
print("ok")
