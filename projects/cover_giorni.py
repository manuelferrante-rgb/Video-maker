#!/usr/bin/env python3
"""Copertina del reel "In che giorni allenarsi" (versioni A e B): sullo sfondo io che faccio squat (scurito),
davanti io scontornato più piccolo e spostato a sinistra; titolo su 2 righe (riquadro nero + arancio,
Inter Black Italic) sotto il viso. Salva anche l'anteprima del ritaglio 3:4 della griglia."""
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R, W, H = "/home/user/video-maker", 1080, 1920
sys.path.insert(0, R)
from make_reel import Matter

ORANGE = (232, 102, 44)
FB = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
D = f"{R}/out/giorni"


def label(im, txt, cx, y, size, box=(0, 0, 0), fg=(255, 255, 255)):
    ft = ImageFont.truetype(FB, size)
    l, t, r, b = ft.getbbox(txt)
    pw, ph = 34, 18
    w, h = r - l + pw * 2, b - t + ph * 2
    d = ImageDraw.Draw(im)
    d.rectangle([cx - w / 2, y, cx + w / 2, y + h], fill=box + (255,))
    d.text((cx - w / 2 + pw - l, y + ph - t), txt, font=ft, fill=fg)
    return y + h


# sfondo ingrandito e spostato a destra, così lo squat resta visibile accanto a me
src = cv2.resize(cv2.imread(f"{D}/st/squat_bg.png"), (int(W * 1.18), int(H * 1.18)))
bg = src[int(H * 0.09):int(H * 0.09) + H, 0:W].astype(np.float32) * 0.62
fr = cv2.resize(cv2.imread(f"{D}/st/f_98.3.png"), (W, H))
mt = Matter(f"{R}/models/u2net_human_seg.onnx")
alpha = mt.run([fr])[0]
# bordo dei capelli: stringo un po' la maschera per togliere l'alone chiaro del muro
alpha = cv2.erode(alpha, np.ones((5, 5), np.uint8)) ** 1.4
fr = mt.clean[0]
SC, DX = 0.72, -250  # io più piccolo, ancorato in basso e spostato a sinistra
M = np.float32([[SC, 0, W / 2 * (1 - SC) + DX], [0, SC, H * (1 - SC)]])
fg = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC).astype(np.float32)
al = cv2.warpAffine(alpha, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
sh = cv2.GaussianBlur(al, (0, 0), 24)[..., None]
img = bg * (1 - 0.45 * sh)
img = img * (1 - al[..., None]) + fg * al[..., None]
im = Image.fromarray(cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)).convert("RGBA")
y = label(im, "4 SEDUTE INTENSE?", W / 2, 1270, 84)
label(im, "SCEGLI I GIORNI GIUSTI", W / 2, y + 10, 74, box=ORANGE)
im.convert("RGB").save(f"{D}/copertina_giorni.jpg", quality=95)
im.convert("RGB").crop((0, 240, 1080, 1680)).resize((540, 720)).save(f"{D}/_check_griglia.jpg", quality=85)
print("ok")
