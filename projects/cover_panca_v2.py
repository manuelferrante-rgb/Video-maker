#!/usr/bin/env python3
"""Copertina v2 del reel "fermi lunghi in panca": io scontornato a mezzo busto in primo piano, centrato, con
l'espressione dubbiosa (fotogramma 2,95 s del reel, "sembra un controsenso"); sullo sfondo, in alto a destra, io che
faccio panca (foto mandata da Manuel). Titolo centrato su 2 righe sotto il mento (riquadro nero + arancio,
Inter Black Italic). Salva anche l'anteprima del ritaglio 3:4 della griglia (y 240-1680)."""
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R, W, H = "/home/user/video-maker", 1080, 1920
sys.path.insert(0, R)
from make_reel import Matter

ORANGE = (232, 102, 44)
FB = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
D = f"{R}/out/cover_panca"
BG = f"{R}/src_cover_panca/1d3bda50-image.png"     # screenshot 1206x2622 con bande nere
FACE = f"{D}/f_2.95.png"                            # fotogramma del reel (ffmpeg -ss 2.95), il più perplesso


def label(im, txt, cx, y, size, box=(0, 0, 0), fg=(255, 255, 255)):
    ft = ImageFont.truetype(FB, size)
    l, t, r, b = ft.getbbox(txt)
    pw, ph = 34, 18
    w, h = r - l + pw * 2, b - t + ph * 2
    d = ImageDraw.Draw(im)
    d.rectangle([cx - w / 2, y, cx + w / 2, y + h], fill=box + (255,))
    d.text((cx - w / 2 + pw - l, y + ph - t), txt, font=ft, fill=fg)
    return y + h


# sfondo: tolgo le bande nere, ingrandisco e sposto la panca in alto a destra
src = cv2.imread(BG)
rows = np.where(src.mean(axis=(1, 2)) > 12)[0]
src = cv2.resize(src[rows[0]:rows[-1] + 1], (W, H), interpolation=cv2.INTER_AREA)
S, TX, TY = 1.3, -24, -566          # il mio viso sulla panca (634,1020) finisce a ~(800,760)
bg = cv2.warpAffine(src, np.float32([[S, 0, TX], [0, S, TY]]), (W, H), flags=cv2.INTER_CUBIC).astype(np.float32)
yy = np.linspace(0, 1, H)[:, None, None]
bg = bg * (0.55 + 0.17 * np.exp(-((yy - 0.3) / 0.18) ** 2))   # più leggibile in alto, scuro sotto il titolo

# io in primo piano: tolgo il sottotitolo bruciato sul petto (inpaint sulla maglia)
fr = cv2.resize(cv2.imread(FACE), (W, H))
x0, x1, y0, y1 = 250, 810, 1360, 1540
roi = fr[y0:y1, x0:x1].astype(int)
white = (roi.min(2) > 150).astype(np.uint8)
near = cv2.dilate(white, np.ones((15, 15), np.uint8)) > 0
txt = (white > 0) | ((roi.max(2) < 22) & near)       # lettere bianche + il loro bordo nero, niente ombre della mano
mask = np.zeros(fr.shape[:2], np.uint8)
mask[y0:y1, x0:x1] = txt.astype(np.uint8) * 255
mask = cv2.dilate(mask, np.ones((11, 11), np.uint8))
fr = cv2.inpaint(fr, mask, 9, cv2.INPAINT_TELEA)
orig = fr.copy()
mt = Matter(f"{R}/models/u2net_human_seg.onnx")
mt.wall_thr = 60                                    # più aggressivo sul muro bianco tra i ricci
alpha = mt.run([fr])[0]
# sotto il mento (maglia, mano) niente decontaminazione: alfa piena senza buchi e colori originali
body = (np.arange(H) > 900)[:, None]
hsv = cv2.cvtColor(orig, cv2.COLOR_BGR2HSV)
skin = (hsv[..., 0] < 25) & (hsv[..., 1] > 45) & (hsv[..., 2] > 70)      # la mano: il muro grigio non è pelle
near = cv2.dilate((alpha > 0.4).astype(np.uint8), np.ones((41, 41), np.uint8)) > 0
solid = ((alpha > 0.4) | (skin & near)).astype(np.uint8)
solid = cv2.morphologyEx(solid, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
solid = cv2.GaussianBlur(solid.astype(np.float32), (0, 0), 1.5)
alpha = np.where(body, solid, alpha)
alpha = cv2.erode(alpha, np.ones((7, 7), np.uint8)) ** 1.6
x = np.arange(W)
alpha = alpha * np.clip(np.minimum(x, W - 1 - x) / 160.0, 0, 1)[None, :]   # i tagli ai bordi sfumano nel fondo
fr = np.where(body[..., None], orig, mt.clean[0])
SC, DX = 0.8, -40                   # spostato a sinistra: a destra si vede la panca, busto ancorato in basso
M = np.float32([[SC, 0, W / 2 * (1 - SC) + DX], [0, SC, H * (1 - SC)]])
fg = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)  # solo colore, l'alfa fuori è 0
al = cv2.warpAffine(alpha, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
sh = cv2.GaussianBlur(al, (0, 0), 28)[..., None]
img = bg * (1 - 0.5 * sh)
al = cv2.GaussianBlur(al, (0, 0), 1.2)              # bordo meno a scalini
hair = (np.arange(H) < 1060)[:, None]               # solo sui capelli (la mano resta pulita)
edge = np.where(hair, np.clip((al - 0.35) / 0.55, 0, 1), 1.0)[..., None]
HAIR = np.float32([28, 34, 44])                     # BGR: castano scuro dei ricci al posto dell'alone del muro
fg = fg * edge + HAIR * (1 - edge)
al = np.where(hair, al, np.clip(al * 1.15, 0, 1))
img = img * (1 - al[..., None]) + fg * al[..., None]
# in fondo (fuori dalla griglia 3:4) sfumo tutto verso lo scuro: la mano non distrae
g = np.clip((np.arange(H) - 1640) / 280.0, 0, 1)[:, None, None]
img = img * (1 - 0.75 * g)
im = Image.fromarray(cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)).convert("RGBA")
y = label(im, "FAI FATICA AL PETTO?", W / 2, 1090, 84)
label(im, "NON FARE I FERMI LUNGHI", W / 2, y + 10, 70, box=ORANGE)
im.convert("RGB").save(f"{D}/copertina_panca_v2.jpg", quality=95)
im.convert("RGB").crop((0, 240, 1080, 1680)).resize((540, 720)).save(f"{D}/_check_griglia.jpg", quality=85)
print("ok")
