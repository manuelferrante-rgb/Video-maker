#!/usr/bin/env python3
"""Due set di storie: (A) squat 51% del totale, (B) squat prima/ora. Helper dal set squat/presa.
Originale: Set di storie (squat/presa): 2 domande, 1 spiegazione, (il reel lo condivide Manuel), 1 CTA col link.
Stile del reel trazioni v2 ma più calmo: foto reale scurita in navy, etichette in corsivo bold, arancio come accento.
Le zone per sticker (domande/link) restano libere dentro la safe zone 1080x1920 (y 250-1580)."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = "/home/user/Video-maker/out/stories2"
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


LOGO = "/home/user/Video-maker/assets/brand/logo_mf_trasparente.png"


def logo(im, w=170, x=56, y=262):
    """logo MF piccolo in alto a sinistra, dentro la safe zone (sotto la barra delle storie)."""
    lg = Image.open(LOGO).convert("RGBA")
    lg = lg.resize((w, int(lg.height * w / lg.width)), Image.LANCZOS)
    im.alpha_composite(lg, (x, y))


def save(im, name):
    logo(im)
    im.convert("RGB").save(f"{D}/{name}.png", optimize=True)
    # anteprima con le zone non sicure di Instagram (solo per controllo)
    pv = im.convert("RGBA").copy()
    ov = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(ov)
    d.rectangle([0, 0, W, 250], fill=(255, 0, 0, 70))
    d.rectangle([0, 1580, W, H], fill=(255, 0, 0, 70))
    pv.alpha_composite(ov)
    pv.convert("RGB").resize((540, 960)).save(f"{D}/_check_{name}.jpg", quality=85)




def photo_card(im, path, crop, x, y, w, h, radius=36, label_txt=None, label_box=(0, 0, 0)):
    """foto ritagliata (crop in pixel sorgente) in un riquadro arrotondato con bordo avorio."""
    ph = Image.open(path).convert("RGB").crop(crop)
    s = max(w / ph.width, h / ph.height)
    ph = ph.resize((int(ph.width * s) + 1, int(ph.height * s) + 1), Image.LANCZOS)
    ox, oy = (ph.width - w) // 2, (ph.height - h) // 2
    ph = ph.crop((ox, oy, ox + w, oy + h))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w, h], radius=radius, fill=255)
    card = Image.new("RGBA", (w, h))
    card.paste(ph, (0, 0), mask)
    im.alpha_composite(card, (x, y))
    ImageDraw.Draw(im).rounded_rectangle([x, y, x + w, y + h], radius=radius, outline=IVORY + (220,), width=4)
    if label_txt:
        label(im, label_txt, y + 22, 52, box=label_box, cx=x + w / 2)


def link_zone(im, zy, title="COMPILA IL FORM"):
    d = ImageDraw.Draw(im)
    ft = f(FB, 60)
    d.text(((W - ft.getlength(title)) / 2, zy - 190), title, font=ft, fill=(255, 255, 255))
    chevrons_down(im, W / 2, zy - 100, n=3, size=40)
    for side in (-1, 1):
        x = W / 2 + side * 380
        for k in range(3):
            xx = x - side * k * 34
            d.line([(xx, zy - 26), (xx - side * 30, zy + 10), (xx, zy + 46)],
                   fill=ORANGE + (int(255 * (0.4 + 0.2 * k)),), width=11, joint="curve")


# ===================== SET A: squat 51% del totale ==========================================================
# A1 intro: il calisthenics si è diviso, lo streetlifting cresce, niente più gambe saltate
im = background(f"{D}/f_mu.png", crop_y=0.25, dark=0.45, zoom=1.0, cx=0.5)
y = label(im, "IL CALISTHENICS", 400, 100)
y = label(im, "NON È PIÙ UNO SOLO", y + 6, 84, box=ORANGE)
y = text_block(im, ["Freestyle, skills, endurance...", "e lo streetlifting che cresce", "gara dopo gara."], y + 50, 52,
               hl={"STREETLIFTING"})
y = label(im, "E QUI LE GAMBE", 1170, 90)
label(im, "NON SONO UN OPTIONAL", y + 6, 64, box=ORANGE)
footer(im, 0)
save(im, "A1_intro")

# A2 domanda (quiz: 20% / 50% / 70%)
im = background(f"{D}/f_sqgara.png", crop_y=0.0, dark=0.45, zoom=1.2, cx=0.62)
y = label(im, "SECONDO TE", 400, 100)
y = label(im, "QUANTO PESA LO SQUAT", y + 6, 76, box=ORANGE)
text_block(im, ["sul totale di gara", "nello streetlifting?"], y + 40, 56, font=FX, color=(255, 255, 255),
           hl={"TOTALE"})
sticker_zone(im, 960, 1280, "SCEGLI LA TUA RISPOSTA")
footer(im, 1)
save(im, "A2_domanda")

# A3 risposta senza numero: grafico FinalRep sfocato con il "?"
im = background(f"{D}/f_card.png", crop_y=0.5, dark=0.25, zoom=1.0, cx=0.5, blur=22)
d = ImageDraw.Draw(im)
fq = f(FB, 420)
d.text((W / 2, 1000), "?", font=fq, fill=(126, 214, 150, 235), anchor="mm")
y = label(im, "IL RISULTATO", 400, 104)
y = label(im, "TI SORPRENDERÀ", y + 6, 104, box=ORANGE)
y = text_block(im, ["Lo squat pesa sul totale", "molto più di quanto pensi."], 1260, 52, font=FX, color=(255, 255, 255),
               hl={"MOLTO"})
label(im, "IL DATO REALE NEL PROSSIMO REEL", 1400, 44)
footer(im, 2)
save(im, "A3_risposta")

# A5 CTA link
im = background(f"{D}/f_man1.png", crop_y=0.2, dark=0.42, zoom=1.0, cx=0.5)
y = label(im, "VUOI UN PERCORSO", 400, 96)
y = label(im, "PERSONALIZZATO", y + 6, 96, box=ORANGE)
text_block(im, ["per migliorare davvero", "nello streetlifting?"], y + 40, 56, font=FX, color=(255, 255, 255),
           hl={"STREETLIFTING?"})
link_zone(im, 1280, "COMPILA QUI")
footer(im, 4)
save(im, "A5_link")

# ===================== SET B: squat prima/ora ===============================================================
# B1 intro
im = background(f"{D}/f_man2.png", crop_y=0.2, dark=0.45, zoom=1.0, cx=0.5)
y = label(im, "GOMITI E SETUP:", 400, 92)
y = label(im, "FATTO.", y + 6, 120, box=ORANGE)
y = text_block(im, ["Ma qual è la vera lacuna", "nel tuo squat?"], y + 40, 58, font=FX, color=(255, 255, 255),
               hl={"LACUNA"})
label(im, "QUELLA CHE PUOI SISTEMARE DA SUBITO", 1330, 44)
footer(im, 0)
save(im, "B1_intro")

# B2 domanda (sondaggio: poco / abbastanza / molto)
im = background(f"{D}/f_fis1.png", crop_y=0.3, dark=0.5, zoom=1.0, cx=0.5)
y = label(im, "QUANTO CONTA", 400, 104)
y = label(im, "ESSERE GROSSI", y + 6, 110, box=ORANGE)
text_block(im, ["per essere forti nello squat?"], y + 40, 56, font=FX, color=(255, 255, 255), hl={"FORTI"})
sticker_zone(im, 960, 1280, "VOTA QUI SOTTO")
footer(im, 1)
save(im, "B2_domanda")

# B3 spiegazione: prima / ora
im = background(f"{D}/f_230.png", crop_y=0.5, dark=0.8, zoom=1.0, cx=0.5, blur=16)
y = label(im, "PER ESSERE FORTE", 400, 96)
y = label(im, "SERVONO MUSCOLI", y + 6, 100, box=ORANGE)
photo_card(im, f"{D}/f_kb.png", (80, 200, 560, 1200), 70, 680, 455, 540, label_txt="PRIMA")
photo_card(im, f"{D}/f_230.png", (560, 1080, 1080, 1800), 555, 680, 455, 540, label_txt="230 KG", label_box=ORANGE)
y = text_block(im, ["Ripetizioni, tempo sotto tensione,", "complementari: così si costruisce."], 1250, 46,
               hl={"RIPETIZIONI,", "TENSIONE,", "COMPLEMENTARI:"})
label(im, "TUTTO NEL PROSSIMO REEL", 1400, 44)
footer(im, 2)
save(im, "B3_spiegazione")

# B5 domanda finale: chi guida chi
im = background(f"{D}/f_fis2.png", crop_y=0.3, dark=0.5, zoom=1.0, cx=0.5)
y = label(im, "SECONDO TE", 400, 100)
y = label(im, "CHI GUIDA CHI?", y + 6, 112, box=ORANGE)
text_block(im, ["La forza porta ipertrofia", "o l'ipertrofia porta forza?"], y + 40, 54, font=FX, color=(255, 255, 255),
           hl={"FORZA", "IPERTROFIA", "FORZA?", "L'IPERTROFIA"})
sticker_zone(im, 1000, 1300, "SCEGLI LA TUA")
footer(im, 4)
save(im, "B5_domanda_finale")
print("ok")
