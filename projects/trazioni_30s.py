#!/usr/bin/env python3
"""Reel 1 del 20/11: UN MESE DI TRAZIONI ZAVORRATE IN 30 SECONDI (format cronometro, 30 s).
Scheda vera di Elisabetta (chin up): sett.1 4 serie RPE8 +2,5 kg; sett.2 3 serie RPE9 +3,75 kg; sett.3 5 serie RPE7
0 kg (scarico); sett.4 2 x massimale. A = Manuel in camera nel primo fotogramma, B = Elisabetta che chiude la trazione.
Clip: IMG_5415 / IMG_5416 / IMG_5418 (HLG), tg_9mb (palestra arancio, a corpo libero), tg42 (nuovo, anelli), IMG_9172.
Voce: IMG_9209 (parlato di Manuel del 20/11 sera). Layout: scheda piccola in alto a sinistra (sul muro), cronometro in basso a destra (non copre il disco),
sottotitoli a y 1200 (sotto la faccia, sopra il disco)."""
import sys
sys.path.insert(0, "/home/user/Video-maker/projects")
import tl_kit as k
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

import vo

S = "/home/user/Video-maker/src_20nov"
P = "/home/user/Video-maker/src_parlato20/IMG_9209.MOV"
TRJ = {P: "/home/user/Video-maker/src_parlato20/tr9209.json"}
OUT = "/home/user/Video-maker/out/trazioni_30s"
YS = 1290

# parlato di Manuel (IMG_9209, 20/11 sera): frasi sue, tagliate di tutte le pause; "Intanto guardo i suoi video e
# correggo" non e' stata registrata -> tolta. Settimana 1 senza "da qui"; settimana 4 senza "tornando a quello che
# avevamo deciso" e settimana 2 senza "magari manteniamoci su tre" (per stare nei 30 s).
PIECES = [
    (P, 6.78, 9.6, "Un mese di trazioni zavorrate / in 30 secondi.", "fix_a"),  # 6.78: occhi aperti
    (P, 26.3, 28.68, "Primo, tu scegli i chili / e io come arrivarci."),
    (P, 40.41, 45.47, "Parti con un carico basso | che riesci a gestire / tra le 5 e le 8 ripetizioni,"),
    (P, 46.17, 49.0, "su 4 serie, | cerca di tenere / un paio di margine."),
    (P, 55.69, 60.97, "Nella settimana 2 invece / alzeremo il carico | e manterremo più alta / l'intensità. | "
                      "Abbassando / il numero di serie."),
    (P, 80.27, 84.34, "Nella penultima settimana / invece abbassiamo il carico, | mantenendo / un volume discreto."),
    (P, 94.48, 95.28, "Nell'ultima, invece,"),
    (P, 96.85, 100.51, "facciamo dei test massimali, | o di ripetizioni / o di carichi assoluti."),
    (P, 133.12, 134.27, "Poi parte il blocco dopo."),
    (P, 135.98, 139.63, "Vuoi il mio protocollo / per le trazioni? | Scrivimi TRAZIONI / e te lo mando subito."),
]
SPV = 1.15  # Manuel: "un po' lento" -> 1,15x (e pause/respiri tolti anche dentro le frasi)
VOICE, TOTAL = vo.layout(PIECES, sp=SPV)
G = vo.groups(VOICE)
T = [g[0] for g in G] + [TOTAL]
T_PRIMO, T_W1, T_W2, T_W3, T_W4, T_POI, T_CTA = T[1], T[2], T[4], T[5], T[6], T[8], T[9]
WK = [T_W1, T_W2, T_W3, T_W4, T_POI]


def blur_dark(r=16, b=0.5):
    return lambda fr, t: ImageEnhance.Brightness(fr.filter(ImageFilter.GaussianBlur(r))).enhance(b)


def cam(i, t1, z0=1.0, z1=1.06):
    return vo.cam_shots(G[i], t1, sp=SPV, z0=z0, z1=z1, c=(540, 820))


def shots(v):
    h = (cam(0, T_PRIMO) if v == "A" else
         [dict(t0=0, t1=T_PRIMO, src=f"{S}/IMG_5418.MOV", ss=5.6, z0=1.0, z1=1.06, c=(560, 700))])
    w1m = T[3]
    return h + cam(1, T_W1, 1.04, 1.12) + [
            dict(t0=T_W1, t1=w1m, src=f"{S}/IMG_5415.MOV", ss=1.0, z0=1.0, z1=1.07, c=(600, 800)),
            dict(t0=w1m, t1=T_W2, src=f"{S}/IMG_5416b.mov", ss=1.3, z0=1.08, z1=1.0, c=(600, 800)),
            dict(t0=T_W2, t1=T_W3, src=f"{S}/IMG_5416.MOV", ss=2.6, z0=1.0, z1=1.08, c=(600, 800)),
            dict(t0=T_W3, t1=T_W4, src=f"{S}/tg_9mb.mp4", ss=14.0, z0=1.2, z1=1.28, c=(470, 900)),
            dict(t0=T_W4, t1=T_POI, src=f"{S}/tg42.mp4", ss=18.5, z0=1.25, z1=1.32, c=(400, 760)),
            dict(t0=T_POI, t1=T_CTA, src=f"{S}/IMG_9172.mov", ss=0.6, z0=1.0, z1=1.05, c=(540, 1200))] + \
        cam(9, TOTAL, 1.0, 1.08)


# ------------------------------------------------------------------ cronometro (00:00 -> 00:30)
def timer(im, t):
    sec = min(int(t), 30) if t < TOTAL - 0.25 else 30
    s = f"00:{sec:02d}"
    if s not in timer.cache:
        timer.cache[s] = k.timer_img(s, dh=86)
    img = timer.cache[s]
    k.put(im, img, 540, 1505)  # Manuel: centrato, visibile, nella zona sicura (sotto, sopra i pulsanti)
timer.cache = {}


# ------------------------------------------------------------------ scheda piccola che si accende riga per riga
ROWS = [("S1", "4 serie · RPE 8", "+2,5", WK[0]), ("S2", "3 serie · RPE 9", "+3,75", WK[1]),
        ("S3", "5 serie · RPE 7", "0", WK[2]), ("S4", "2 x massimale", "MAX", WK[3])]
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
    return XL + (XR - XL) * k.ease((t - WK[2] + 0.15) / 0.3)


def card(im, t):
    if not (WK[0] <= t < WK[4]):
        return
    n = sum(t >= r[3] for r in ROWS)
    active = n - 1
    if (active, n) not in card.cache:
        card.cache[(active, n)] = card_img(active, n)
    img = card.cache[(active, n)]
    x = card_x(t)
    s = k.pop((t - WK[0]) / 0.3)
    a = 1 - k.ease((t - WK[4] + 0.14) / 0.14)
    k.put(im, img, x, YC + img.height / 2, s, a)
    t_row = ROWS[active][3]
    if 0 <= t - t_row < 0.3 and t > WK[0] + 0.3:  # lampo arancio sulla riga che si accende
        glow = Image.new("RGBA", (CW - 16, RH - 6), k.ORANGE + (int(130 * (1 - (t - t_row) / 0.3)),))
        k.put(im, glow, x, YC + HEAD + active * RH + 2 + (RH - 6) / 2, 1, a)
card.cache = {}


def num_layer():
    """Numero in riquadro arancio sopra la scheda: +2,5 KG / +3,75 KG / 0 KG (scende) / MASSIMALE."""
    imgs = {i: k.label_img(lab, k.ORANGE if i != 2 else k.BLACK, size=60) for i, lab in
            enumerate(["+2,5 KG", "+3,75 KG", "0 KG", "MASSIMALE"])}

    def fn(im, t):
        for i, (_, _, _, t0) in enumerate(ROWS):
            t1 = ROWS[i + 1][3] if i < 3 else WK[4]
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


def title_open(v):
    """Titolo-promessa per i primi 2 s: in A sotto il mento di Manuel, in B sul busto di Elisabetta."""
    r1 = k.label_img("UN MESE DI TRAZIONI ZAVORRATE", k.BLACK, size=56)
    r2 = k.label_img("IN 30 SECONDI", k.ORANGE, size=72)
    im2 = Image.new("RGBA", (max(r1.width, r2.width), r1.height + r2.height + 12), (0, 0, 0, 0))
    im2.alpha_composite(r1, ((im2.width - r1.width) // 2, 0))
    im2.alpha_composite(r2, ((im2.width - r2.width) // 2, r1.height + 12))
    return k.popped(im2, 0, T_PRIMO, 540, 1180 if v == "A" else 900, still=True)


def layers(v):
    pages = vo.kara_pages(VOICE, TRJ, sp=SPV)  # sottotitoli sempre, anche nel gancio (al posto del titolo)
    return [card, num_layer(),
            k.popped(lambda: k.label_img('COMMENTA "TRAZIONI"', k.ORANGE, size=62), T[9] + 1.6, TOTAL, 540, 1060),
            vo.kara_layer(pages, y=YS, size=68, end=TOTAL, first_from=0.0), timer]


SFX = [(WK[0], "comparsa", 0.2),  # niente tick all'inizio e alla fine (Manuel: effetto "horror")
       (WK[0] + 0.45, "pop", 0.3), (WK[1], "pop", 0.3), (WK[1] + 0.45, "pop", 0.3), (WK[2], "pop", 0.3),
       (WK[2] + 0.45, "whoosh", 0.3), (WK[2] - 0.15, "trascina", 0.15), (WK[3], "pop", 0.3),
       (WK[3] + 0.45, "hit", 0.25), (T[9] + 1.6, "pop", 0.3)]

if __name__ == "__main__":
    print({n: round(x, 2) for n, x in zip(["primo", "w1", "w2", "w3", "w4", "poi", "cta", "tot"],
                                         [T_PRIMO, T_W1, T_W2, T_W3, T_W4, T_POI, T_CTA, TOTAL])})
    for v in sys.argv[1:] or ["A", "B"]:
        out = f"{OUT}/trazioni_30s_{v}.mp4"
        k.build(out, round(TOTAL, 3), shots(v), layers(v), SFX, [x[:4] for x in VOICE], voice_sp=SPV)
        k.sheet(out, f"{OUT}/sheet_{v}.jpg", n=40, cols=10)
