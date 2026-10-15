#!/usr/bin/env python3
"""Schermata animata in stile FinalRep (verde) per il dato: Team Italy, Euros 2026, totale 8.811 kg,
contributo per alzata: squat 51%, dip 27%, trazioni 17%, muscle up 6%.
Uso: python3 finalrep_card.py durata_secondi uscita.mov  (RGBA qtrle, opaca; ultimi frame con uscita a diagonale)"""
import math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 3.6
OUTP = sys.argv[2] if len(sys.argv) > 2 else "/home/user/Video-maker/out/card_51.mov"
T51 = float(sys.argv[3]) if len(sys.argv) > 3 else 1.55  # quando si evidenzia lo squat 51%
TMETA = float(sys.argv[4]) if len(sys.argv) > 4 else 2.1  # quando compare "più della metà"

BG0, BG1 = (14, 38, 22), (34, 74, 44)
PANEL = (9, 26, 16)
G_SQ, G_DIP, G_PU, G_MU = (126, 214, 150), (78, 160, 100), (56, 120, 76), (196, 236, 206)
WHITE, MUTED = (240, 246, 241), (150, 190, 160)
RED = (214, 64, 64)

FI = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FIB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SLICES = [("SQUAT", 51, G_SQ), ("DIPS", 27, G_DIP), ("PU", 17, G_PU), ("MU", 6, G_MU)]  # 101 per arrotondamento
TOT = sum(s[1] for s in SLICES)


def f(p, s):
    return ImageFont.truetype(p, s)


def ease(x):
    x = min(max(x, 0), 1)
    return 1 - (1 - x) ** 3


def spaced(d, xy, txt, font, fill, sp=6):
    x, y = xy
    for ch in txt:
        d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + sp


def spaced_w(txt, font, sp=6):
    return sum(font.getlength(c) + sp for c in txt) - sp


# sfondo fisso (gradiente verde + pannello)
bg = Image.new("RGBA", (W, H))
arr = np.zeros((H, W, 4), np.uint8)
t = np.linspace(0, 1, H)[:, None]
for c in range(3):
    arr[..., c] = (BG0[c] + (BG1[c] - BG0[c]) * (0.5 + 0.5 * np.sin(t * 3.1 - 1.2))).astype(np.uint8)
arr[..., 3] = 255
bg = Image.fromarray(arr)
d0 = ImageDraw.Draw(bg)
PX0, PY0, PX1, PY1 = 70, 470, W - 70, 1480
d0.rounded_rectangle([PX0, PY0, PX1, PY1], radius=44, fill=PANEL + (255,))
fm = f(FM, 30)
hdr = "TEAM ANALYSIS · FINALREP EUROS 2026"
spaced(d0, ((W - spaced_w(hdr, fm, 5)) / 2, 280), hdr, fm, MUTED, 5)
CX, CY, R0, R1 = W / 2, 1040, 175, 330  # anello


def frame(fr):
    tt = fr / FPS
    im = bg.copy()
    d = ImageDraw.Draw(im)
    # titolo
    a = ease(tt / 0.35)
    ft = f(FIB, 104)
    title = [("TEAM ", WHITE), ("ITALY", RED)]
    tw = sum(ft.getlength(s) for s, _ in title)
    x = (W - tw) / 2
    for s, col in title:
        d.text((x, 360 - 30 * (1 - a)), s, font=ft, fill=col + (int(255 * a),))
        x += ft.getlength(s)
    spaced(d, (PX0 + 50, PY0 + 50), "TOTAL & CONTRIBUTION", f(FM, 32), MUTED, 6)
    # anello: le fette si disegnano in sequenza
    prog = ease((tt - 0.15) / max(T51 - 0.3, 0.6)) * TOT
    start = -90.0
    acc = 0
    pop = ease((tt - T51) / 0.3)  # la fetta squat si stacca un po'
    for name, pct, col in SLICES:
        seg = max(min(prog - acc, pct), 0)
        if seg > 0:
            ang0 = start + acc / TOT * 360
            ang1 = start + (acc + seg) / TOT * 360
            off = 18 * pop if name == "SQUAT" else 0
            mid = math.radians((ang0 + ang1) / 2)
            ox, oy = off * math.cos(mid), off * math.sin(mid)
            lay = Image.new("RGBA", (W, H))
            ld = ImageDraw.Draw(lay)
            ld.pieslice([CX - R1 + ox, CY - R1 + oy, CX + R1 + ox, CY + R1 + oy], ang0, ang1, fill=col + (255,))
            ld.ellipse([CX - R0 + ox, CY - R0 + oy, CX + R0 + ox, CY + R0 + oy], fill=(0, 0, 0, 0))
            im.alpha_composite(lay)
            # separatori sottili
            for ang in (ang0, ang1):
                r = math.radians(ang)
                d.line([(CX + R0 * math.cos(r), CY + R0 * math.sin(r)), (CX + R1 * math.cos(r), CY + R1 * math.sin(r))],
                       fill=PANEL + (255,), width=5)
            # etichetta fetta, quando è completa
            if seg >= pct and name != "SQUAT":
                lr = (R0 + R1) / 2
                lx, ly = CX + lr * math.cos(mid), CY + lr * math.sin(mid)
                fl, fp = f(FM, 30 if pct > 10 else 24), f(FI, 34 if pct > 10 else 26)
                d.text((lx, ly - 20), name, font=fl, fill=PANEL, anchor="mm")
                d.text((lx, ly + 18), f"{pct}%", font=fp, fill=PANEL, anchor="mm")
        acc += pct
    d.ellipse([CX - R0 + 8, CY - R0 + 8, CX + R0 - 8, CY + R0 - 8], fill=PANEL + (255,))
    # contatore totale al centro
    val = int(round(8811 * ease((tt - 0.15) / max(T51 - 0.3, 0.6))))
    d.text((CX, CY - 18), f"{val:,}".replace(",", "."), font=f(FIB, 86), fill=WHITE, anchor="mm")
    d.text((CX, CY + 52), "KG TOTALE", font=f(FM, 28), fill=MUTED, anchor="mm")
    # evidenza squat: etichetta dentro la fetta che cresce, poi "PIÙ DELLA METÀ" sotto
    if tt > T51:
        sp_ = ease((tt - T51) / 0.3)
        mid = math.radians(-90 + 51 / TOT * 180)
        lr = (R0 + R1) / 2 + 18 * pop
        lx, ly = CX + lr * math.cos(mid), CY + lr * math.sin(mid)
        lay = Image.new("RGBA", (W, H))
        ld = ImageDraw.Draw(lay)
        ld.text((lx, ly - 40), "SQUAT", font=f(FM, int(32 + 4 * sp_)), fill=PANEL + (255,), anchor="mm")
        ld.text((lx, ly + 16), "51%", font=f(FIB, int(52 + 16 * sp_)), fill=PANEL + (255,), anchor="mm")
        im.alpha_composite(lay)
    if tt > TMETA:
        s2 = ease((tt - TMETA) / 0.3)
        ImageDraw.Draw(im).text((CX, 1420 - 25 * (1 - s2)), "PIÙ DELLA METÀ DEL TOTALE", font=f(FM, 34),
                                fill=G_SQ + (int(255 * s2),), anchor="mm")
    # fonte
    d = ImageDraw.Draw(im)
    d.text((CX, 1530), "Fonte: FinalRep · Team Italy, Euros 2026", font=f(FI, 30), fill=MUTED, anchor="mm")
    return im


def wipe(img, p, col=(126, 214, 150)):
    yy, xx = np.mgrid[0:H, 0:W]
    s = (xx + (H - yy) * 0.35) / (W + H * 0.35)
    pos = -0.15 + 1.35 * p
    a = np.array(img)
    a[s < pos - 0.07, 3] = 0
    a[(s >= pos - 0.07) & (s < pos)] = list(col) + [255]
    return Image.fromarray(a)


n = int(round(DUR * FPS))
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r",
                      str(FPS), "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", OUTP], stdin=subprocess.PIPE)
WF = 7
for fr in range(n):
    im = frame(fr)
    k = fr - (n - WF)
    if k >= 0:
        im = wipe(im, (k + 1) / WF)
    p.stdin.write(im.tobytes())
p.stdin.close()
p.wait()
print("ok", OUTP, n)
