#!/usr/bin/env python3
"""Reel 2 del 20/11: PANCA, LA LINEA SUL PALMO (14,5 s). A = 150 kg nel primo fotogramma, B = la mano con i puntini.
Girati (Drive parlati, 20/11): IMG_5153 (panca 150 kg, dischi rossi Eleiko, 3 s), IMG_9153 (Manuel che si sistema,
ripreso dai piedi: palmo verso la camera a 7.5-8.4, presa che si chiude a 4.2-5.0), IMG_9189 (panca, maglia bianca).
VOCE: le frasi del brief non sono ancora registrate. Finché VOICE e' vuoto si monta l'anteprima con i sottotitoli
sui tempi del piano e un segnaposto al posto di Manuel in camera. Quando arrivano: riempire VOICE e ritarare PAGES."""
import math, sys
sys.path.insert(0, "/home/user/Video-maker/projects")
import tl_kit as k
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

S = "/home/user/Video-maker/src_20nov"
OUT = "/home/user/Video-maker/out/panca_palmo"
TOTAL = 14.5
BENCH, HAND, WHITE_B = f"{S}/IMG_5153.MOV", f"{S}/IMG_9153.MOV", f"{S}/IMG_9189.MOV"
VOICE = []  # [(t_reel, file, da, a)] quando Manuel registra

# punti sul palmo nel fotogramma 8.25 di IMG_9153 (1080x1920): tra pollice e indice / dove si incrociano le linee
P_WEB, P_CROSS = (308, 926), (210, 952)
HC = (255, 935)  # centro dello zoom sulla mano


def blur_dark(r=18, b=0.45):
    def pre(fr, t):
        return ImageEnhance.Brightness(fr.filter(ImageFilter.GaussianBlur(r))).enhance(b)
    return pre


def shots(v):
    rep = lambda t0, t1: dict(t0=t0, t1=t1, src=BENCH, ss=0.9, z0=1.85, z1=1.95, c=(450, 1100))
    hand_live = dict(t0=1.5, t1=5.5, src=HAND, ss=7.35, sp=0.75, live=1.2, z0=2.6, z1=3.1, c=HC)
    hand_still = lambda t0, t1, z0, z1: dict(t0=t0, t1=t1, src=HAND, ss=8.25, live=0.0, z0=z0, z1=z1, c=HC)
    common = [
        dict(t0=5.5, t1=8.5, src=HAND, ss=3.6, sp=0.5, mi=True, z0=1.35, z1=1.42, c=(300, 1080)),  # presa
        dict(t0=8.5, t1=11.5, src=WHITE_B, ss=3.0, pre=blur_dark()),                                # animazione
        dict(t0=11.5, t1=13.5, src=WHITE_B, ss=9.0, pre=blur_dark(10, 0.6)),                       # SEGNAPOSTO
    ]
    if v == "A":
        return [rep(0, 1.5), hand_live] + common + [rep(13.5, 14.5)]
    return [hand_still(0, 1.5, 2.9, 3.0), rep(1.5, 3.0), hand_still(3.0, 5.5, 3.0, 3.2)] + common + \
        [hand_still(13.5, 14.5, 2.9, 3.0)]


def hand_gfx(sh, t_dots, t_line, t_end):
    """Puntini (pop pop) e linea arancio che si disegna tra i due punti, agganciati alla mano vera."""
    def fn(im, t):
        if not (sh["t0"] <= t < t_end) or t < t_dots:
            return
        z = k.shot_z(sh, t)
        a, b = k.map_pt(P_WEB, z, sh["c"]), k.map_pt(P_CROSS, z, sh["c"])
        s1, s2 = k.pop((t - t_dots) / 0.25), k.pop((t - t_dots - 0.15) / 0.25)
        pr = k.ease_out((t - t_line) / 0.7) if t_line is not None else 0

        def draw(d, P, ss):
            if pr > 0:
                e = (a[0] + (b[0] - a[0]) * pr, a[1] + (b[1] - a[1]) * pr)
                d.line([P(*a), P(*e)], fill=(255, 255, 255, 255), width=18 * ss)
                d.line([P(*a), P(*e)], fill=k.ORANGE + (255,), width=10 * ss)
            k.dot(d, P, ss, a[0], a[1], 15, s1)
            k.dot(d, P, ss, b[0], b[1], 15, s2)
        x0, x1 = min(a[0], b[0]) - 60, max(a[0], b[0]) + 60
        y0, y1 = min(a[1], b[1]) - 60, max(a[1], b[1]) + 60
        k.aa(im, (x0, y0, x1, y1), draw)
    return fn


def grip_arrow(sh):
    """Freccia bilanciere -> polso -> avambraccio sulla presa che si chiude (IMG_9153 3.6-5.1 a 0,5x)."""
    KX = [(4.3, 242), (4.7, 248), (5.1, 246)]

    def fn(im, t):
        if not (6.9 <= t < sh["t1"]):
            return
        src = sh["ss"] + (t - sh["t0"]) * sh["sp"]
        x = KX[0][1] if src <= KX[0][0] else KX[-1][1]
        for (s0, x0), (s1, x1) in zip(KX, KX[1:]):
            if s0 <= src <= s1:
                x = x0 + (x1 - x0) * (src - s0) / (s1 - s0)
        z = k.shot_z(sh, t)
        pts = [k.map_pt(p, z, sh["c"]) for p in ((x + 2, 905), (x + 6, 1030), (x - 8, 1235))]
        pr = k.ease_out((t - 6.9) / 0.6)
        k.aa(im, (pts[0][0] - 80, pts[0][1] - 60, pts[0][0] + 80, pts[-1][1] + 60),
             lambda d, P, ss: k.arrow(d, P, ss, pts, pr, width=9, head=34))
    return fn


def wrist_anim(im, t):
    """8.5-11.5: avambraccio e mano stilizzati, bilanciere verso le dita, il polso si piega, X rossa."""
    if not (8.5 <= t < 11.5):
        return
    a = 1 - k.ease((t - 11.36) / 0.14)
    WX, WY, L, LF, TH = 470, 900, 280, 380, 108
    draw_p = k.ease_out((t - 8.5) / 0.45)
    ang = math.radians(50) * k.ease((t - 9.3) / 0.6)
    hx, hy = WX + L * math.sin(ang), WY - L * math.cos(ang)
    bd = 215
    bx, by = WX + bd * math.sin(ang) + 70 * math.cos(ang), WY - bd * math.cos(ang) + 70 * math.sin(ang)
    bs = k.pop((t - 9.0) / 0.28)
    arr = k.ease_out((t - 9.95) / 0.45)
    xp = k.ease_out((t - 10.4) / 0.3)
    al = int(255 * a)

    def capsule(d, P, p0, p1, w):
        d.line([P(*p0), P(*p1)], fill=(255, 255, 255, al), width=int((w + 14) * 3))
        for q in (p0, p1):
            r = (w + 14) / 2
            d.ellipse([P(q[0] - r, q[1] - r), P(q[0] + r, q[1] + r)], fill=(255, 255, 255, al))
        d.line([P(*p0), P(*p1)], fill=(28, 28, 30, al), width=int(w * 3))
        for q in (p0, p1):
            r = w / 2
            d.ellipse([P(q[0] - r, q[1] - r), P(q[0] + r, q[1] + r)], fill=(28, 28, 30, al))

    def draw(d, P, ss):
        capsule(d, P, (WX, WY), (WX, WY + LF * draw_p), TH)                                   # avambraccio
        capsule(d, P, (WX, WY), (WX + (hx - WX) * draw_p, WY + (hy - WY) * draw_p), TH * 0.95)  # mano
        d.ellipse([P(WX - 16, WY - 16), P(WX + 16, WY + 16)], fill=k.ORANGE + (al,))           # polso
        if bs > 0:  # sezione del bilanciere sulle dita
            r = 58 * bs
            d.ellipse([P(bx - r - 7, by - r - 7), P(bx + r + 7, by + r + 7)], fill=(255, 255, 255, al))
            d.ellipse([P(bx - r, by - r), P(bx + r, by + r)], fill=(165, 165, 172, al))
        if arr > 0:  # la spinta scende fuori dall'avambraccio
            k.arrow(d, P, ss, [(bx, by + 75), (bx, by + 75 + 360)], arr, width=10, head=36)
        if xp > 0:
            k.xmark(d, P, ss, 800, 560, 85, xp, width=22)
    k.aa(im, (250, 420, 960, 1360), draw)


def layers(v):
    sh = {s["t0"]: s for s in shots(v)}
    L = []
    big150 = lambda: k.text_img("*150* *KG*", size=150, stroke=9)
    if v == "A":
        L.append(k.popped(big150, 0, 1.5, 540, 560, still=True))
        L.append(hand_gfx(sh[1.5], 2.72, 3.25, 5.5))
    else:
        L.append(hand_gfx(sh[0], 0.0, None, 1.5))
        L.append(k.popped(big150, 1.5, 3.0, 540, 560))
        L.append(hand_gfx(sh[3.0], 3.0, 3.25, 5.5))
        L.append(hand_gfx(sh[13.5], 13.5, None, 14.5))
    L.append(k.popped(lambda: k.label_img("QUI IL BILANCIERE", k.BLACK, size=64), 3.6, 5.5, 540, 330))
    L.append(grip_arrow(sh[5.5]))
    L.append(k.popped(lambda: k.label_img("IN LINEA", k.ORANGE, size=64), 7.2, 8.5, 540, 330))
    L.append(wrist_anim)
    L.append(k.popped(lambda: k.label_img("VERSO LE DITA", k.BLACK, size=64), 8.6, 11.5, 540, 330))
    if not VOICE:
        L.append(k.placeholder("MANUEL IN CAMERA: DA REGISTRARE"))
        L[-1] = (lambda f: (lambda im, t: f(im, t) if 11.5 <= t < 13.5 else None))(L[-1])
    first = [(1.5, 3.0, "E il bilanciere lo appoggio *qui.*")] if v == "A" else \
        [(0.0, 1.5, "Il bilanciere\nlo appoggio *qui.*")]
    L.append(k.subs(first + [
        (3.0, 4.25, "Dal punto tra\n*pollice* e *indice*"),
        (4.25, 5.5, "fino a dove si *incrociano*\nle linee della mano."),
        (5.5, 7.0, "Così il peso scende\ndritto *sull'avambraccio*"),
        (7.0, 8.5, "e il polso resta *in* *linea.*"),
        (8.5, 10.0, "Verso le *dita*\nil polso si piega"),
        (10.0, 11.5, "e la spinta si *disperde.*"),
        (11.5, 12.5, "Tu dove lo appoggi?"),
        (12.5, 13.5, "Scrivimi *dita* o *palmo.*"),
        (13.5, 14.5, "Per *questo...*")]))
    return L


def sfx(v):
    d = 2.72 if v == "A" else 0.0
    out = [(d, "pop", 0.35), (d + 0.15, "pop", 0.35), (3.25, "disegno", 0.3), (3.6, "comparsa", 0.2),
           (6.9, "disegno", 0.25), (7.2, "pop", 0.25), (8.5, "disegno", 0.25), (9.0, "pop", 0.3),
           (9.3, "trascina", 0.2), (10.4, "hit", 0.22), (8.6, "comparsa", 0.15)]
    if v == "B":
        out += [(3.0, "pop", 0.3), (1.5, "hit", 0.2)]
    return out


if __name__ == "__main__":
    for v in sys.argv[1:] or ["A", "B"]:
        k.build(f"{OUT}/panca_palmo_{v}.mp4", TOTAL, shots(v), layers(v), sfx(v), VOICE)
        k.sheet(f"{OUT}/panca_palmo_{v}.mp4", f"{OUT}/sheet_{v}.jpg", n=29, cols=10)
