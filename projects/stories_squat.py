#!/usr/bin/env python3
"""Set di storie (squat/presa): 2 domande, 1 spiegazione, (il reel lo condivide Manuel), 1 CTA col link.
Stile del reel trazioni v2 ma più calmo: foto reale scurita in navy, etichette in corsivo bold, arancio come accento.
Le zone per sticker (domande/link) restano libere dentro la safe zone 1080x1920 (y 250-1580)."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = "/home/user/Video-maker/out/stories"
W, H = 1080, 1920
NAVY, NAVY_D, ORANGE, IVORY = (20, 48, 79), (10, 26, 44), (232, 102, 44), (242, 238, 227)
FB = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
FS = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
FX = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"


def f(path, sz):
    return ImageFont.truetype(path, sz)


def background(photo, crop_y=0.5, dark=0.55, blur=0, zoom=1.0, cx=0.5):
    im = Image.open(photo).convert("RGB")
    s = max(W / im.width, H / im.height) * zoom
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x = int((im.width - W) * cx)
    y = int((im.height - H) * crop_y)
    im = im.crop((x, y, x + W, y + H))
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    im = im.convert("RGBA")
    # velatura navy verticale: più scura in alto e in basso, dove stanno testi e sticker
    ov = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(ov)
    for yy in range(H):
        t = yy / H
        a = dark + 0.30 * max(0, (0.45 - t)) / 0.45 + 0.35 * max(0, (t - 0.5)) / 0.5
        d.line([(0, yy), (W, yy)], fill=NAVY_D + (int(255 * min(a, 0.93)),))
    im.alpha_composite(ov)
    # righe diagonali leggerissime (richiamo al reel, senza aggressività)
    st = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(st)
    for x0 in range(-H, W + 120, 120):
        d.polygon([(x0, 0), (x0 + 46, 0), (x0 + 46 + H * 0.45, H), (x0 + H * 0.45, H)], fill=NAVY + (38,))
    im.alpha_composite(st)
    return im


def label(im, txt, y, size=96, box=(0, 0, 0), fg=(255, 255, 255), cx=W / 2):
    ft = f(FB, size)
    l, t, r, b = ft.getbbox(txt)
    pw, ph = 30, 16
    w, h = r - l + pw * 2, b - t + ph * 2
    d = ImageDraw.Draw(im)
    x0 = cx - w / 2
    d.rectangle([x0, y, x0 + w, y + h], fill=box + (255,))
    d.text((x0 + pw - l, y + ph - t), txt, font=ft, fill=fg)
    return y + h


def text_block(im, lines, y, size=50, font=FS, color=IVORY, gap=14, hl=None):
    """righe centrate; hl = parole da colorare in arancio."""
    ft = f(font, size)
    d = ImageDraw.Draw(im)
    for ln in lines:
        words = ln.split(" ")
        widths = [ft.getlength(w + " ") for w in words]
        x = (W - (sum(widths) - ft.getlength(" "))) / 2
        for w, ww in zip(words, widths):
            col = ORANGE if hl and w.strip(".,?!:").upper() in hl else color
            d.text((x, y), w, font=ft, fill=col)
            x += ww
        y += size + gap
    return y


def chevrons_down(im, cx, y, n=3, size=46, color=ORANGE):
    d = ImageDraw.Draw(im)
    for k in range(n):
        yy = y + k * (size * 0.62)
        a = int(255 * (0.45 + 0.55 * (k + 1) / n))
        pts = [(cx - size, yy), (cx, yy + size * 0.8), (cx + size, yy)]
        d.line(pts, fill=color + (a,), width=12, joint="curve")


def sticker_zone(im, y0, y1, hint):
    """area libera per lo sticker: solo un'etichetta piccola sopra, niente riquadri da coprire."""
    d = ImageDraw.Draw(im)
    ft = f(FX, 34)
    w = ft.getlength(hint)
    d.text(((W - w) / 2, y0 - 70), hint, font=ft, fill=IVORY + (200,))
    chevrons_down(im, W / 2, y0 - 22, n=2, size=26, color=IVORY)


def footer(im, n):
    d = ImageDraw.Draw(im)
    ft = f(FX, 30)
    txt = "@_manuelferrante"
    d.text(((W - ft.getlength(txt)) / 2, 1528), txt, font=ft, fill=IVORY + (170,))
    # puntini di avanzamento del set (5 storie)
    for k in range(5):
        x = W / 2 - 2 * 34 + k * 34
        r = 8 if k == n else 6
        d.ellipse([x - r, 1495 - r, x + r, 1495 + r], fill=(ORANGE if k == n else IVORY) + ((255,) if k == n else (120,)))


def save(im, name):
    im.convert("RGB").save(f"{D}/{name}.png", optimize=True)
    # anteprima con le zone non sicure di Instagram (solo per controllo)
    pv = im.convert("RGBA").copy()
    ov = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(ov)
    d.rectangle([0, 0, W, 250], fill=(255, 0, 0, 70))
    d.rectangle([0, 1580, W, H], fill=(255, 0, 0, 70))
    pv.alpha_composite(ov)
    pv.convert("RGB").resize((540, 960)).save(f"{D}/_check_{name}.jpg", quality=85)


# 1) DOMANDA 1: problema
im = background(f"{D}/f_squat.png", crop_y=0.0, dark=0.42, zoom=1.25, cx=0.62)
y = label(im, "IL TUO SQUAT", 300, 104)
y = label(im, "NON GIRA?", y + 6, 118, box=ORANGE)
text_block(im, ["Prima di cambiare programma,", "dove guarderesti per primo?"], y + 50, 54, hl={"PRIMO?"})
sticker_zone(im, 850, 1170, "RISPONDI QUI SOTTO")
footer(im, 0)
save(im, "storia_1_domanda")

# 2) DOMANDA 2: la presa
im = background(f"{D}/f_presa.png", crop_y=0.4, dark=0.8, zoom=1.08, cx=0.6, blur=14)
# foto della presa in un riquadro in basso, sotto lo sticker
ph = Image.open(f"{D}/f_presa.png").convert("RGB")
ph = ph.crop((100, 470, 1080, 826)).resize((880, 320), Image.LANCZOS)
mask = Image.new("L", ph.size, 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, ph.width, ph.height], radius=36, fill=255)
card = Image.new("RGBA", ph.size)
card.paste(ph, (0, 0), mask)
im.alpha_composite(card, ((W - ph.width) // 2, 1140))
ImageDraw.Draw(im).rounded_rectangle([(W - ph.width) // 2, 1140, (W + ph.width) // 2, 1140 + ph.height], radius=36,
                                     outline=IVORY + (220,), width=4)
y = label(im, "E LA TUA PRESA", 300, 100)
y = label(im, "COM'È?", y + 6, 118, box=ORANGE)
text_block(im, ["Quanto larghe tieni le mani", "sul bilanciere nello squat?"], y + 50, 54, hl={"MANI"})
sticker_zone(im, 850, 1120, "SCEGLI LA TUA")
footer(im, 1)
save(im, "storia_2_domanda")

# 3) SPIEGAZIONE (contenuto del reel, senza aggiunte)
im = background(f"{D}/f_elia.png", crop_y=0.12, dark=0.5, zoom=1.55, cx=0.45)
# cerchio rosso sul gomito, come nel reel
d = ImageDraw.Draw(im)
ex, ey = 600, 640
d.ellipse([ex - 120, ey - 120, ex + 120, ey + 120], outline=(230, 46, 46, 255), width=7)
y = label(im, "LA RISPOSTA:", 300, 70, box=(0, 0, 0))
y = label(im, "GUARDA I GOMITI", y + 6, 96, box=ORANGE)
y = 880
y = text_block(im, ["La larghezza della presa", "decide dove finiscono."], y, 56, font=FX, color=(255, 255, 255),
               hl={"PRESA"})
y = text_block(im, ["Più stretta: schiena più compatta", "sotto il bilanciere, ma serve", "mobilità di spalla."],
               y + 36, 46, hl={"STRETTA:", "MOBILITÀ"})
y = text_block(im, ["Ti irrigidisce o ti dà fastidio?", "Allargala."], y + 30, 46, hl={"ALLARGALA."})
label(im, "IL REEL NELLA PROSSIMA STORIA", 1385, 44, box=(0, 0, 0))
footer(im, 2)
save(im, "storia_3_spiegazione")

# 5) CTA con link
im = background(f"{D}/f_man_63.5.png", crop_y=0.2, dark=0.40, zoom=1.0, cx=0.5)
y = label(im, "VUOI CHE TI SEGUA", 300, 92)
y = label(im, "ANCHE TU?", y + 6, 118, box=ORANGE)
y = text_block(im, ["Programmazione e correzione", "della tecnica, costruite su di te."], y + 46, 50, hl={"TECNICA,"})
# zona link: frecce ai lati che puntano al centro + scritta
zy = 1260
d = ImageDraw.Draw(im)
ft = f(FB, 60)
txt = "CLICCA IL LINK"
d.text(((W - ft.getlength(txt)) / 2, zy - 190), txt, font=ft, fill=(255, 255, 255))
chevrons_down(im, W / 2, zy - 100, n=3, size=40)
for side in (-1, 1):  # frecce laterali verso lo sticker
    x = W / 2 + side * 380
    for k in range(3):
        xx = x - side * k * 34
        d.line([(xx, zy - 26), (xx - side * 30, zy + 10), (xx, zy + 46)], fill=ORANGE + (int(255 * (0.4 + 0.2 * k)),),
               width=11, joint="curve")
footer(im, 4)
save(im, "storia_5_link")
print("ok")
