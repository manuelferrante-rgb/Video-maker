#!/usr/bin/env python3
"""Reel 1 del 20/11: UN MESE DI TRAZIONI ZAVORRATE IN 30 SECONDI (format cronometro, 30 s).
Scheda vera di Elisabetta (chin up): sett.1 4 serie RPE8 +2,5 kg; sett.2 3 serie RPE9 +3,75 kg; sett.3 5 serie RPE7
0 kg (scarico); sett.4 2 x massimale. A = Manuel in camera nel primo fotogramma, B = Elisabetta che chiude la trazione.
Clip: IMG_5415 / IMG_5416 / IMG_5418 (HLG), tg_9mb (palestra arancio, a corpo libero), tg42 (nuovo, anelli), IMG_9172.
VOCE e Manuel in camera: da registrare. Finché VOICE e' vuoto: anteprima con sottotitoli sui tempi del piano e
segnaposto. Layout: scheda piccola in alto a sinistra (sul muro), cronometro in basso a destra (non copre il disco),
sottotitoli a y 1200 (sotto la faccia, sopra il disco)."""
import sys
sys.path.insert(0, "/home/user/Video-maker/projects")
import tl_kit as k
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

S = "/home/user/Video-maker/src_20nov"
OUT = "/home/user/Video-maker/out/trazioni_30s"
TOTAL = 30.0
VOICE = []  # [(t_reel, file, da, a)]
YS = 1200


def blur_dark(r=16, b=0.5):
    return lambda fr, t: ImageEnhance.Brightness(fr.filter(ImageFilter.GaussianBlur(r))).enhance(b)


PH = lambda t0, t1: dict(t0=t0, t1=t1, src=f"{S}/IMG_9172.mov", ss=0.2, pre=blur_dark(), ph=True)  # segnaposto
OPEN_B = lambda t0, t1: dict(t0=t0, t1=t1, src=f"{S}/IMG_5418.MOV", ss=5.6, z0=1.0, z1=1.06, c=(560, 700))


def shots(v):
    body = [
        dict(t0=5.0, t1=9.0, src=f"{S}/IMG_5415.MOV", ss=1.6, z0=1.0, z1=1.07, c=(600, 800)),
        dict(t0=9.0, t1=12.5, src=f"{S}/IMG_5416.MOV", ss=3.2, z0=1.08, z1=1.0, c=(600, 800)),
        dict(t0=12.5, t1=17.0, src=f"{S}/tg_9mb.mp4", ss=14.0, z0=1.2, z1=1.28, c=(470, 900)),
        dict(t0=17.0, t1=21.0, src=f"{S}/tg42.mp4", ss=18.5, z0=1.25, z1=1.32, c=(400, 760)),
        dict(t0=21.0, t1=25.0, src=f"{S}/IMG_9172.mov", ss=0.05, z0=1.0, z1=1.08, c=(540, 1200)),
        PH(25.0, 28.5),
    ]
    if v == "A":
        return [PH(0, 5.0)] + body + [PH(28.5, 30.0)]
    return [OPEN_B(0, 2.5), PH(2.5, 5.0)] + body + [OPEN_B(28.5, 30.0)]


# ------------------------------------------------------------------ cronometro (00:00 -> 00:30)
def timer(im, t):
    sec = min(int(t) + (1 if t >= 29.8 else 0), 30)
    s = f"00:{sec:02d}"
    if s not in timer.cache:
        timer.cache[s] = k.timer_img(s, dh=92)
    img = timer.cache[s]
    k.put(im, img, 1045 - img.width / 2, 1525, k.pop(t / 0.25) if t < 0.25 else 1)
timer.cache = {}


# ------------------------------------------------------------------ scheda piccola che si accende riga per riga
ROWS = [("S1", "4 serie · RPE 8", "+2,5", 5.0), ("S2", "3 serie · RPE 9", "+3,75", 9.0),
        ("S3", "5 serie · RPE 7", "0", 12.5), ("S4", "2 x massimale", "MAX", 17.0)]
F_R = k.font("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 33)
F_H = k.font(k.F_BI, 25)
CW, RH, HEAD = 430, 62, 50
YC = 640  # bordo alto della scheda: a meta' schermo, sul muro accanto ad Elisabetta
XL, XR = 30 + CW / 2, 1050 - CW / 2  # sett. 1-2 a sinistra, sett. 3-4 a destra (Elisabetta li' e' a sinistra)


def card_img(active, nrows):
    h = HEAD + RH * nrows + 12
    im = Image.new("RGBA", (CW, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, CW - 1, h - 1], radius=20, fill=(10, 10, 12, 210), outline=(255, 255, 255, 70),
                        width=2)
    d.text((20, 15), "CHIN UP · UN MESE", font=F_H, fill=k.ORANGE + (255,))
    for i in range(nrows):
        wk, txt, kg, _ = ROWS[i]
        y = HEAD + i * RH + 2
        on = i == active
        a = 255 if on else 115
        if on:
            d.rounded_rectangle([8, y, CW - 8, y + RH - 6], radius=12,
                                fill=(k.ORANGE + (240,)) if i == 2 else (255, 255, 255, 40))
        tc = (255, 255, 255, a)
        oc = tc if (on and i == 2) else k.ORANGE + (a,)
        d.text((20, y + RH / 2 - 3), wk, font=F_R, fill=oc, anchor="lm")
        d.text((72, y + RH / 2 - 3), txt, font=F_R, fill=tc, anchor="lm")
        d.text((CW - 20, y + RH / 2 - 3), kg, font=F_R, fill=oc, anchor="rm")
    return im


def card_x(t):
    return XL + (XR - XL) * k.ease((t - 12.35) / 0.3)


def card(im, t):
    if not (5.0 <= t < 21.0):
        return
    n = sum(t >= r[3] for r in ROWS)
    active = n - 1
    if (active, n) not in card.cache:
        card.cache[(active, n)] = card_img(active, n)
    img = card.cache[(active, n)]
    x = card_x(t)
    s = k.pop((t - 5.0) / 0.3)
    a = 1 - k.ease((t - 20.86) / 0.14)
    k.put(im, img, x, YC + img.height / 2, s, a)
    t_row = ROWS[active][3]
    if 0 <= t - t_row < 0.3 and t > 5.3:  # lampo arancio sulla riga che si accende
        glow = Image.new("RGBA", (CW - 16, RH - 6), k.ORANGE + (int(130 * (1 - (t - t_row) / 0.3)),))
        k.put(im, glow, x, YC + HEAD + active * RH + 2 + (RH - 6) / 2, 1, a)
card.cache = {}


def num_layer():
    """Numero in riquadro arancio sopra la scheda: +2,5 KG / +3,75 KG / 0 KG (scende) / MASSIMALE."""
    imgs = {i: k.label_img(lab, k.ORANGE if i != 2 else k.BLACK, size=60) for i, lab in
            enumerate(["+2,5 KG", "+3,75 KG", "0 KG", "MASSIMALE"])}

    def fn(im, t):
        for i, (_, _, _, t0) in enumerate(ROWS):
            t1 = ROWS[i + 1][3] if i < 3 else 21.0
            ta = t0 + 0.45
            if not (ta <= t < t1):
                continue
            x, y = card_x(t), YC - 70
            a = 1 - k.ease((t - (t1 - 0.14)) / 0.14)
            if i == 2:  # 0 KG che scende dall'alto
                e = k.ease_out((t - ta) / 0.35)
                k.put(im, imgs[i], x, y - 110 * (1 - e), 1, a * e)
            else:
                k.put(im, imgs[i], x, y, k.pop((t - ta) / 0.28), a)
    return fn


def title_open(im, t):
    """0-2 s: titolo-promessa a centro schermo (sul busto, mai sulla testa)."""
    if t >= 2.1:
        return
    if "img" not in title_open.__dict__:
        r1 = k.label_img("UN MESE DI TRAZIONI ZAVORRATE", k.BLACK, size=56)
        r2 = k.label_img("IN 30 SECONDI", k.ORANGE, size=72)
        im2 = Image.new("RGBA", (max(r1.width, r2.width), r1.height + r2.height + 12), (0, 0, 0, 0))
        im2.alpha_composite(r1, ((im2.width - r1.width) // 2, 0))
        im2.alpha_composite(r2, ((im2.width - r2.width) // 2, r1.height + 12))
        title_open.img = im2
    a = 1 - k.ease((t - 1.96) / 0.14)
    k.put(im, title_open.img, 540, 900, 1, a)


def placeholder_layer(sh_list):
    img = k.label_img("MANUEL IN CAMERA: DA REGISTRARE", (60, 60, 60), size=40)
    ph = [(s["t0"], s["t1"]) for s in sh_list if s.get("ph")]

    def fn(im, t):
        if any(a <= t < b for a, b in ph):
            k.put(im, img, 540, 700)
    return fn


PAGES = [
    (2.5, 5.0, "Primo: l'obiettivo in kg\nlo scegli *tu.*"),
    (5.0, 6.6, "Settimana 1: quattro serie\na *RPE* *8.*"),
    (6.6, 9.0, "Pesante, ma con due\nripetizioni *in* *tasca.*"),
    (9.0, 10.8, "Settimana 2: meno serie,\n*più* *carico.*"),
    (10.8, 12.5, "*RPE* *9.*"),
    (12.5, 14.2, "Settimana 3:\ntolgo la *zavorra.*"),
    (14.2, 15.8, "Più volume,\nma leggero e *pulito:*"),
    (15.8, 17.0, "è lo *scarico.*"),
    (17.0, 18.8, "Settimana 4: *massimale.*"),
    (18.8, 21.0, "Ed è lì che\nil numero *esce.*"),
    (21.0, 23.0, "Intanto guardo\ni suoi *video*"),
    (23.0, 25.0, "e correggo\nquello che *non* *va.*"),
    (25.0, 26.2, "E poi parte\nil blocco *dopo.*"),
    (26.2, 27.3, "Vuoi il mio\nprotocollo *trazioni?*"),
    (27.3, 28.5, "Commenta *TRAZIONI*\ne te lo mando."),
]


def layers(v):
    sh = shots(v)
    return [placeholder_layer(sh), title_open, card, num_layer(),
            k.popped(lambda: k.label_img("L'OBIETTIVO LO SCEGLI TU", k.BLACK, size=60), 2.6, 5.0, 540, 330),
            k.popped(lambda: k.label_img('COMMENTA "TRAZIONI"', k.ORANGE, size=64), 26.0, 28.5, 540, 330),
            k.subs(PAGES, y=YS, size=70, maxw=1000), timer]


SFX = [(0.0, "tick", 0.3), (29.8, "tick", 0.35), (2.6, "comparsa", 0.15), (5.0, "comparsa", 0.2),
       (5.45, "pop", 0.3), (9.0, "pop", 0.3), (9.45, "pop", 0.3), (12.5, "pop", 0.3), (12.95, "whoosh", 0.3),
       (12.35, "trascina", 0.15), (17.0, "pop", 0.3), (17.45, "hit", 0.25), (26.0, "pop", 0.3)]

if __name__ == "__main__":
    for v in sys.argv[1:] or ["A", "B"]:
        k.build(f"{OUT}/trazioni_30s_{v}.mp4", TOTAL, shots(v), layers(v), SFX, VOICE)
        k.sheet(f"{OUT}/trazioni_30s_{v}.mp4", f"{OUT}/sheet_{v}.jpg", n=40, cols=10)
