#!/usr/bin/env python3
"""Storie della serie "Input giusti" (una puntata a settimana: muscle up, trazioni, dip, squat).
Per ogni puntata: 1) puzzle a 4 pezzi che si scopre un pezzo alla volta, 2) "Quale input utilizzeresti?" con zona
libera per lo sticker (le opzioni le mette Manuel), 3) la soluzione argomentata come nel reel + "il reel nella
prossima storia", (4 = il reel), 5) "Vuoi farti analizzare ...? Compila il form qua sotto" con zona per il link.
Helper e stile da projects/stories_set2.py (foto scurita in navy, etichette, arancio, logo, footer)."""
import os
from PIL import Image, ImageDraw, ImageFilter

R = "/home/user/video-maker"
src = open(f"{R}/projects/stories_set2.py").read()
exec(src[:src.index("# ===================== SET A")])  # solo gli helper (background, label, text_block, ...)

D = f"{R}/out/input_giusti/stories"
os.makedirs(D, exist_ok=True)

EPS = [  # chiave, nome, foto, informazione, input, spiegazione, soggetto del form
    ("mu", "MUSCLE UP",
     ["«Attiva il dorsale e non", "extraruotare le spalle»"],
     ["Giù la sbarra, gomiti vicino,", "spalle avanti!"],
     ["Il dorsale lavora quando porti", "la sbarra giù verso di te.", "Gomiti vicino e spalle avanti",
      "ti portano sopra la sbarra", "nella transizione."],
     "IL TUO MUSCLE UP?"),
    ("tr", "TRAZIONI",
     ["«Scapole depresse: aumenta lo", "spazio subacromiale»"],
     ["Giù la sbarra, vicino vicino,", "gambe avanti!"],
     ["Se pensi a tirare la sbarra giù", "e vicino al petto, le scapole", "scendono da sole.",
      "Gambe avanti: resti compatto", "e non dondoli."],
     "LE TUE TRAZIONI?"),
    ("dp", "DIP",
     ["«Attiva i depressori", "scapolari»"],
     ["Forte contro le parallele,", "spalle avanti e addome duro!"],
     ["Spingendo forte contro le", "parallele le scapole scendono", "senza pensarci.",
      "Spalle avanti e addome duro", "ti tengono stabile."],
     "I TUOI DIP?"),
    ("sq", "SQUAT",
     ["«Respira col diaframma, mantieni", "il baricentro al centro del piede»"],
     ["Rilassa il carico, pancia tra", "le gambe, bilanciere contro!"],
     ["Mentre scendi non hai tempo", "di pensare al baricentro.", "Pancia tra le gambe e bilanciere",
      "contro ti fanno restare compatto", "e in equilibrio sotto il carico."],
     "IL TUO SQUAT?"),
]
NAMES = [e[1] for e in EPS]


# ---------------- puzzle 2x2 ----------------
def piece_mask(size, k, cell, knob):
    """maschera del pezzo k (0 alto-sx, 1 alto-dx, 2 basso-sx, 3 basso-dx) dentro un riquadro size x size."""
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    r, c = divmod(k, 2)
    x0, y0 = c * cell, r * cell
    d.rounded_rectangle([x0 + 6, y0 + 6, x0 + cell - 6, y0 + cell - 6], radius=26, fill=255)
    # incastri: (bordo condiviso, chi ha la sporgenza)
    joints = [((cell, cell / 2), 0), ((cell / 2, cell), 1), ((cell * 1.5, cell), 3), ((cell, cell * 1.5), 2)]
    pieces_of = {0: (0, 1), 1: (0, 2), 2: (1, 3), 3: (2, 3)}
    for j, ((jx, jy), owner) in enumerate(joints):
        a, b = pieces_of[j]
        if k not in (a, b):
            continue
        box = [jx - knob, jy - knob, jx + knob, jy + knob]
        d.ellipse(box, fill=255 if k == owner else 0)
    return m


def puzzle(im, ep, y0, size=700):
    cell = size // 2
    knob = 58
    x0 = (W - size) // 2
    photos = [f"{D}/mu_a.png", f"{D}/tr_b.png", f"{D}/dp_a.png", f"{D}/sq_a.png"]
    sh = Image.new("RGBA", (size + 120, size + 120), (0, 0, 0, 0))
    full = Image.new("L", (size, size), 0)
    for k in range(4):
        full = Image.composite(Image.new("L", (size, size), 255), full, piece_mask(size, k, cell, knob))
    sh.paste(Image.new("RGBA", (size, size), (0, 0, 0, 150)), (60, 70), full)
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)), (x0 - 60, y0 - 60))
    fn = f(FB, 52)
    fq = f(FB, 150)
    for k in range(4):
        m = piece_mask(size, k, cell, knob)
        r, c = divmod(k, 2)
        cx, cy = c * cell + cell / 2, r * cell + cell / 2
        if k <= ep:  # pezzo scoperto: foto dell'esercizio + nome
            ph = Image.open(photos[k]).convert("RGB")
            s = size / ph.width * 1.0
            ph = ph.resize((size, int(ph.height * s)), Image.LANCZOS)
            oy = int(ph.height * 0.30 - cy)
            ph = ph.crop((0, oy, size, oy + size)).convert("RGBA")
            ov = Image.new("RGBA", (size, size), NAVY_D + (90 if k == ep else 150,))
            ph.alpha_composite(ov)
            layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            layer.paste(ph, (0, 0), m)
        else:  # pezzo ancora coperto
            layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            layer.paste(Image.new("RGBA", (size, size), NAVY + (255,)), (0, 0), m)
        # bordo del pezzo
        edge = m.filter(ImageFilter.MaxFilter(9))
        border = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        col = ORANGE if k == ep else IVORY
        border.paste(Image.new("RGBA", (size, size), col + (255,)), (0, 0), edge)
        border.alpha_composite(layer)
        d = ImageDraw.Draw(border)
        if k <= ep:
            l, t, rr, b = fn.getbbox(NAMES[k])
            bw, bh = rr - l + 36, b - t + 24
            d.rectangle([cx - bw / 2, cy + 60, cx + bw / 2, cy + 60 + bh], fill=(ORANGE if k == ep else (0, 0, 0)) + (255,))
            d.text((cx - bw / 2 + 18 - l, cy + 60 + 12 - t), NAMES[k], font=fn, fill=(255, 255, 255))
            d.text((cx, cy - 30), str(k + 1), font=f(FB, 96), fill=IVORY + (235,), anchor="mm")
        else:
            d.text((cx, cy), "?", font=fq, fill=IVORY + (110,), anchor="mm")
        im.alpha_composite(border, (x0, y0))


for ep, (key, name, info, inp, expl, form) in enumerate(EPS):
    # 1) puzzle: un pezzo nuovo a puntata
    im = background(f"{D}/{key}_m.png" if key != "mu" else f"{D}/intro_m.png", crop_y=0.3, dark=0.62, blur=14)
    y = label(im, "INPUT GIUSTI", 400, 104)
    text_block(im, ["per trasformare informazioni", "in qualcosa di utile"], y + 26, 50, font=FX,
               color=(255, 255, 255), hl={"UTILE"})
    puzzle(im, ep, 690)
    label(im, f"PEZZO {ep + 1} DI 4: {name}", 1420, 50, box=ORANGE)
    footer(im, 0)
    save(im, f"{key}_1_puzzle")

    # 2) domanda: quale input utilizzeresti? (sticker di Manuel)
    im = background(f"{D}/{key}_a.png", crop_y=0.3, dark=0.55)
    y = label(im, name, 400, 110, box=ORANGE)
    y = label(im, "L'INFORMAZIONE", y + 40, 48)
    y = text_block(im, info, y + 22, 50, font=FX, color=(255, 255, 255))
    y = label(im, "QUALE INPUT", y + 46, 92)
    label(im, "UTILIZZERESTI?", y + 6, 92, box=ORANGE)
    sticker_zone(im, 1130, 1420, "SCEGLI LA TUA RISPOSTA")
    footer(im, 1)
    save(im, f"{key}_2_domanda")

    # 3) soluzione + rimando al reel
    im = background(f"{D}/{key}_b.png", crop_y=0.3, dark=0.72, blur=10)
    y = label(im, "L'INPUT GIUSTO", 400, 96, box=ORANGE)
    y = text_block(im, inp, y + 30, 58, font=FB, color=(255, 255, 255))
    y = text_block(im, expl, y + 40, 46, hl={"GIÙ", "SBARRA", "SCENDONO", "COMPATTO", "STABILE.", "EQUILIBRIO",
                                             "TRANSIZIONE.", "PANCIA", "GAMBE"})
    text_block(im, ["Un'informazione è utile quando", "diventa qualcosa che puoi fare."], y + 30, 42, font=FX,
               color=(255, 255, 255))
    label(im, "IL REEL NELLA PROSSIMA STORIA", 1400, 44)
    footer(im, 2)
    save(im, f"{key}_3_soluzione")

    # 5) form per l'analisi
    im = background(f"{D}/{key}_m.png", crop_y=0.25, dark=0.45)
    y = label(im, "VUOI FARTI ANALIZZARE", 400, 72)
    y = label(im, form, y + 6, 92 if len(form) < 16 else 80, box=ORANGE)
    link_zone(im, 1300, "COMPILA IL FORM QUA SOTTO")
    footer(im, 4)
    save(im, f"{key}_5_form")
print("ok")
