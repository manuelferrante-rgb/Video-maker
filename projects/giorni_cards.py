#!/usr/bin/env python3
"""Schede animate del reel "In che giorni allenarsi" (format IG1, vedi ig1_cards.py).
card_*(clip) restituisce draw(im, t). Anteprima: python3 projects/giorni_cards.py (fotogrammi in out/giorni/cards)."""
import math, os, sys
sys.path.insert(0, "/home/user/video-maker/projects")
from PIL import ImageDraw
from ig1_cards import (R, W, H, ORANGE, WHITE, MUTED, FK, FB, FBI, font, ease, eout, alpha, header, spaced,
                       rounded_frame, ClipFrames, export, background)

LINE = (245, 240, 232)


def card_intro(clip):
    """4 sedute intense: i giorni contano. B-roll in riquadro arrotondato."""
    def draw(im, t):
        header(im, t, "4 SEDUTE INTENSE", [("I giorni ", False), ("contano", True)])
        a = ease((t - 0.15) / 0.35)
        if a > 0:
            s = 0.92 + 0.08 * eout((t - 0.15) / 0.5)
            w, h = 520 * s, 700 * s
            rounded_frame(im, clip.at(t), (W / 2 - w / 2, 560 + (1 - s) * 200, W / 2 + w / 2, 560 + (1 - s) * 200 + h), a)
    return draw


def card_recupero(clip=None):
    """una seduta pesante stressa il sistema nervoso: il recupero si ferma al 60%."""
    def draw(im, t):
        header(im, t, "SISTEMA NERVOSO", [("Recupero\n", False), ("incompleto", True)])
        d = ImageDraw.Draw(im)
        cx, cy, r = W / 2, 1060, 300
        a = ease((t - 0.2) / 0.3)
        if a <= 0:
            return
        # tacche
        for k in range(21):
            ang = math.radians(180 + 9 * k)
            r0, r1 = (r + 26, r + 50) if k % 5 == 0 else (r + 30, r + 42)
            d.line([(cx + r0 * math.cos(ang), cy + r0 * math.sin(ang)), (cx + r1 * math.cos(ang), cy + r1 * math.sin(ang))],
                   fill=alpha(LINE, a * (0.8 if k % 5 == 0 else 0.4)), width=3)
        d.arc([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=alpha(LINE, a * 0.25), width=10)
        p = 0.6 * eout((t - 0.35) / 1.1)
        if p > 0:
            d.arc([cx - r, cy - r, cx + r, cy + r], 180, 180 + 180 * p, fill=alpha(ORANGE, a), width=14)
            ang = math.radians(180 + 180 * p)
            ex, ey = cx + r * math.cos(ang), cy + r * math.sin(ang)
            d.ellipse([ex - 13, ey - 13, ex + 13, ey + 13], fill=alpha(WHITE, a))
        # segnaposto 100% = seduta successiva
        d.ellipse([cx + r - 9, cy - 9, cx + r + 9, cy + 9], outline=alpha(LINE, a * 0.7), width=3)
        spaced(d, (cx + r - 20, cy + 50), "SEDUTA DOPO", font(FK, 22), alpha(MUTED, a), track=4)
        n = f"{round(p * 100)}%"
        d.text((cx, cy - 120), n, font=font(FB, 150), fill=alpha(WHITE, a), anchor="mm")
        spaced(d, (cx, cy - 20), "RECUPERO", font(FK, 26), alpha(MUTED, a), track=7)
    return draw


SPLIT = [("SQUAT", ["dip", "core"]), ("TRAZIONI", ["dip", "gambe"]), ("DIP", ["trazioni", "core"]),
         ("MUSCLE UP", ["squat", "core"])]


def card_split(clip=None):
    """più distretti a seduta, una priorità diversa ogni volta + complementari leggeri."""
    def draw(im, t):
        header(im, t, "LA SPLIT", [("Una ", False), ("priorità\n", True), ("per seduta", False)])
        d = ImageDraw.Draw(im)
        cw, gap, x0, y0 = 214, 22, 0, 720
        x0 = W / 2 - (4 * cw + 3 * gap) / 2
        for i, (pri, comp) in enumerate(SPLIT):
            a = ease((t - 0.3 - 0.22 * i) / 0.3)
            if a <= 0:
                continue
            dy = 30 * (1 - eout((t - 0.3 - 0.22 * i) / 0.4))
            x = x0 + i * (cw + gap)
            spaced(d, (x + cw / 2, y0 + dy), f"SEDUTA {i + 1}", font(FK, 22), alpha(MUTED, a), track=4)
            d.rounded_rectangle([x, y0 + 36 + dy, x + cw, y0 + 300 + dy], 16, fill=alpha(ORANGE, a))
            fsz = 34 if len(pri) <= 8 else 28
            d.text((x + cw / 2, y0 + 168 + dy), pri, font=font(FBI, fsz), fill=alpha(WHITE, a), anchor="mm")
            for j, c in enumerate(comp):
                yy = y0 + 320 + j * 96 + dy
                aj = ease((t - 0.55 - 0.22 * i - 0.1 * j) / 0.3) * a
                d.rounded_rectangle([x + 18, yy, x + cw - 18, yy + 80], 14, outline=alpha(LINE, aj * 0.7), width=2)
                d.text((x + cw / 2, yy + 40), c, font=font(FK, 28), fill=alpha(LINE, aj * 0.85), anchor="mm")
        a = ease((t - 1.6) / 0.3)
        if a > 0:
            spaced(d, (W / 2, y0 + 560), "PRIORITÀ   +   COMPLEMENTARI LEGGERI", font(FK, 22), alpha(MUTED, a), track=4)
    return draw


WEEK = [("L", "I"), ("M", "S"), ("M", "R"), ("G", "I"), ("V", "S"), ("S", "R"), ("D", "R")]


def card_riposo(clip=None):
    """le sedute più intense subito dopo il riposo: settimana con le frecce riposo -> intensa."""
    def draw(im, t):
        header(im, t, "LA REGOLA", [("Intensa dopo\nil ", False), ("riposo", True)])
        d = ImageDraw.Draw(im)
        cw, gap, y0 = 128, 10, 800
        x0 = W / 2 - (7 * cw + 6 * gap) / 2
        cells = []
        for i, (g, k) in enumerate(WEEK):
            a = ease((t - 0.3 - 0.07 * i) / 0.25)
            x = x0 + i * (cw + gap)
            cells.append(x)
            if a <= 0:
                continue
            spaced(d, (x + cw / 2, y0 - 30), g, font(FK, 26), alpha(MUTED, a), track=0)
            if k == "R":
                d.rounded_rectangle([x, y0, x + cw, y0 + 230], 14, outline=alpha(LINE, a * 0.35), width=2)
                d.text((x + cw / 2, y0 + 115), "riposo", font=font(FK, 24), fill=alpha(LINE, a * 0.6), anchor="mm")
            elif k == "S":
                d.rounded_rectangle([x, y0, x + cw, y0 + 230], 14, fill=alpha((60, 54, 50), a))
                d.text((x + cw / 2, y0 + 115), "seduta", font=font(FK, 24), fill=alpha(LINE, a * 0.9), anchor="mm")
        # le intense si accendono dopo
        for i, (g, k) in enumerate(WEEK):
            if k != "I":
                continue
            a = ease((t - 1.0 - 0.25 * (i > 0)) / 0.3)
            if a <= 0:
                continue
            x = cells[i]
            s = 0.85 + 0.15 * eout((t - 1.0 - 0.25 * (i > 0)) / 0.3)
            cx, cy = x + cw / 2, y0 + 115
            d.rounded_rectangle([cx - cw / 2 * s, cy - 115 * s, cx + cw / 2 * s, cy + 115 * s], 14, fill=alpha(ORANGE, a))
            # fulmine
            bolt = [(0, -60), (-26, 6), (-2, 6), (-14, 60), (28, -14), (2, -14), (16, -60)]
            d.polygon([(cx + bx * s * 0.8, cy - 20 + by * s * 0.8) for bx, by in bolt], fill=alpha(WHITE, a))
            d.text((cx, cy + 80), "intensa", font=font(FK, 22), fill=alpha(WHITE, a), anchor="mm")
        # frecce dal riposo alla seduta intensa (D -> L "settimana dopo", M -> G)
        a = ease((t - 1.5) / 0.4)
        if a > 0:
            xa, xb = cells[2] + cw / 2, cells[3] + cw / 2
            yy = y0 + 270
            d.line([(xa, yy), (xa, yy + 40), (xb, yy + 40), (xb, yy)], fill=alpha(ORANGE, a), width=4)
            d.polygon([(xb - 12, yy + 14), (xb + 12, yy + 14), (xb, yy - 4)], fill=alpha(ORANGE, a))
            spaced(d, (W / 2, y0 + 380), "PRIMA RIPOSI, POI SPINGI", font(FK, 24), alpha(MUTED, a), track=5)
    return draw


def card_energia(clip=None):
    """così dai il massimo: barra dell'energia che si riempie al 100%."""
    def draw(im, t):
        header(im, t, "IL RISULTATO", [("Il ", False), ("massimo\n", True), ("delle energie", False)])
        d = ImageDraw.Draw(im)
        a = ease((t - 0.25) / 0.3)
        if a <= 0:
            return
        x0, y0, w, h = W / 2 - 300, 860, 600, 210
        d.rounded_rectangle([x0, y0, x0 + w, y0 + h], 30, outline=alpha(LINE, a), width=5)
        d.rounded_rectangle([x0 + w + 8, y0 + 70, x0 + w + 30, y0 + h - 70], 8, fill=alpha(LINE, a))
        p = eout((t - 0.4) / 1.0)
        if p > 0:
            d.rounded_rectangle([x0 + 16, y0 + 16, x0 + 16 + (w - 32) * p, y0 + h - 16], 20, fill=alpha(ORANGE, a))
        d.text((W / 2, y0 + h / 2), f"{round(p * 100)}%", font=font(FB, 110), fill=alpha(WHITE, a), anchor="mm")
        spaced(d, (W / 2, y0 + h + 60), "OGNI SEDUTA PESANTE", font(FK, 24), alpha(MUTED, a), track=6)
    return draw


if __name__ == "__main__":
    from PIL import Image
    D = f"{R}/out/giorni/cards"
    os.makedirs(D, exist_ok=True)
    clip = ClipFrames(f"{R}/src_giorni/IMG_8641.mov", 14.0, 3.0)
    cards = [("intro", card_intro(clip)), ("recupero", card_recupero()), ("split", card_split()),
             ("riposo", card_riposo()), ("energia", card_energia())]
    thumbs = []
    for nm, dr in cards:
        for tt in (0.4, 2.2):
            im = background()
            dr(im, tt)
            thumbs.append(im.convert("RGB").resize((360, 640)))
    sheet = Image.new("RGB", (360 * 5, 640 * 2))
    for i, th in enumerate(thumbs):
        sheet.paste(th, ((i // 2) * 360, (i % 2) * 640))
    sheet.save(f"{D}/preview.png")
    print("ok")
