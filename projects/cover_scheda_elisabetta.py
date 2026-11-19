#!/usr/bin/env python3
"""Copertina "Ti fidi della tua scheda?" (Elisabetta, 19/11): impianto di cover_dip_sguardo.py.
Fondo: Elisabetta in cima alla trazione con 10 kg (IMG_5416b 2,4 s), a destra; davanti io scontornato un po' a sinistra,
fotogramma 164,0 del parlato (sopracciglio alzato, "ti fidi?"). Titolo: TI FIDI DELLA SCHEDA? / TU L'OBIETTIVO, IO IL
PERCORSO + anteprima del ritaglio 3:4."""
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R, W, H = "/home/user/video-maker", 1080, 1920
sys.path.insert(0, R)
from make_reel import Matter

ORANGE = (232, 102, 44)
FB = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
D = f"{R}/out/eli"


def label(im, txt, cx, y, size, box=(0, 0, 0), fg=(255, 255, 255)):
    ft = ImageFont.truetype(FB, size)
    l, t, r, b = ft.getbbox(txt)
    pw, ph = 34, 18
    w, h = r - l + pw * 2, b - t + ph * 2
    d = ImageDraw.Draw(im)
    d.rectangle([cx - w / 2, y, cx + w / 2, y + h], fill=box + (255,))
    d.text((cx - w / 2 + pw - l, y + ph - t), txt, font=ft, fill=fg)
    return y + h


def panel(path, cx_src, cx_dst, zoom=1.0, dy=0):
    """fotogramma 1080x1920, ingrandito, con il soggetto (cx_src) portato a cx_dst"""
    im = cv2.resize(cv2.imread(path), (int(W * zoom), int(H * zoom)))
    x0 = int(cx_src * zoom - cx_dst)
    y0 = int((H * zoom - H) / 2 + dy)
    out = np.zeros((H, W, 3), np.float32)
    xs, xe = max(x0, 0), min(x0 + W, im.shape[1])
    ys, ye = max(y0, 0), min(y0 + H, im.shape[0])
    out[ys - y0:ye - y0, xs - x0:xe - x0] = im[ys:ye, xs:xe]
    if ys - y0 > 0:  # sopra l'immagine: ripeto la prima riga (poi scurita)
        out[:ys - y0] = out[ys - y0]
    if ye - y0 < H:  # sotto l'immagine: ripeto l'ultima riga (pavimento)
        out[ye - y0:] = out[ye - y0 - 1]
    return out


# sfondo: Jasmin (b3, col tacco, soggetto a x~495) a sinistra, Nicolo' (b2, x~570) a destra
left = panel(f"{D}/st/bgE.png", 600, 630, 1.05, dy=-40)
right = left  # corpo (x~510) al centro della meta' destra
xx = np.arange(W, dtype=np.float32)[None, :, None]
mix = np.clip((xx - 560) / 80, 0, 1)
bg = (left * (1 - mix) + right * mix) * 0.6
yb = np.arange(H, dtype=np.float32)[:, None, None]
bg = bg * np.clip((1880 - yb) / 260, 0.0, 1.0) * np.clip((yb + 40) / 300, 0.0, 1.0)  # fondo sfumato al buio (niente pavimento ripetuto)

fr = cv2.resize(cv2.imread(f"{D}/st/f_164.0.png"), (W, H))
mt = Matter(f"{R}/models/u2net_human_seg.onnx")
mt.wall_thr = 8
a = mt.run([fr])[0]
hard = (a > 0.5).astype(np.uint8)
ff = hard.copy(); cv2.floodFill(ff, np.zeros((H + 2, W + 2), np.uint8), (0, 0), 1)
hard = np.maximum(hard, 1 - ff)                               # buchi interni (viso) riempiti
hard = cv2.morphologyEx(hard, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
# bordo: i pixel vicino al contorno prendono il colore dell'interno (via il beige tra i ricci)
inner = cv2.erode(hard, np.ones((15, 15), np.uint8)).astype(np.float32)
num = cv2.GaussianBlur(fr.astype(np.float32) * inner[..., None], (0, 0), 6)
den = cv2.GaussianBlur(inner, (0, 0), 6)[..., None]
interior = num / np.maximum(den, 1e-3)
band = np.clip(1 - cv2.GaussianBlur(inner, (0, 0), 3), 0, 1)[..., None] * hard[..., None]
lab = cv2.cvtColor(fr, cv2.COLOR_BGR2LAB).astype(np.float32)
wall = np.median(lab[ff.astype(bool)[:H, :W] & (hard == 0)].reshape(-1, 3), 0)
dwall = np.sqrt(((lab - wall) ** 2).sum(-1))
skin = np.median(lab[790:815, 390:420].reshape(-1, 3), 0)      # fronte
dskin = np.sqrt(((lab - skin) ** 2).sum(-1))
# "muro" solo se e' piu' vicino al muro che alla pelle (la fronte resta intatta)
wallish = (np.clip((30 - dwall) / 15, 0, 1) * (dwall < 0.8 * dskin))[..., None]
fg = fr.astype(np.float32) * (1 - band * wallish) + interior * band * wallish
# vicino al contorno (entro ~70 px) il muro rimasto tra i ricci diventa trasparente
dist = cv2.distanceTransform(hard, cv2.DIST_L2, 5)
outer = (dist < 70).astype(np.float32)
wallcut = (wallish[..., 0] > 0.35).astype(np.uint8) * outer.astype(np.uint8)
wallcut = cv2.dilate(wallcut, np.ones((3, 3), np.uint8))
wallcut[1120:] = 0  # solo sui capelli: la maglietta bianca non va toccata
hard2 = hard * (1 - wallcut)
hard2 = cv2.morphologyEx(hard2, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
f2 = hard2.copy(); cv2.floodFill(f2, np.zeros((H + 2, W + 2), np.uint8), (0, 0), 1)
hard2 = np.maximum(hard2, 1 - f2)                             # nessun buco dentro il viso
n, lbl, st, _ = cv2.connectedComponentsWithStats(hard2)
hard2 = (lbl == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)   # via i pezzetti staccati
# capelli: i pixel chiari (muro beige tra i ricci) vicino al bordo diventano trasparenti, la pelle no
L = lab[..., 0]
d2 = cv2.distanceTransform(hard2, cv2.DIST_L2, 5)
light = (L > 115) & (d2 < 120) & (dskin > 22) & (np.arange(H)[:, None] < 930)
# solo il chiaro collegato al fondo esterno (la fronte, racchiusa dai capelli, resta)
reach = (light | (hard2 == 0)).astype(np.uint8)
nl, ll = cv2.connectedComponents(reach)
outside = ll == ll[0, 0]
hard2 = hard2 * (1 - (light & (outside | (d2 < 45))).astype(np.uint8))  # + chiaro tra i ricci vicino al bordo
hard2 = cv2.morphologyEx(hard2, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
n, lbl, st, _ = cv2.connectedComponentsWithStats(hard2)
hard2 = (lbl == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
# il bordo che resta (mezzi toni chiari) prende il colore scuro dei capelli vicini
hairband = ((cv2.distanceTransform(hard2, cv2.DIST_L2, 5) < 6) & (d2 < 120) & (L > 85) & (dskin > 22)
            & (np.arange(H)[:, None] < 930))[..., None]
fg = np.where(hairband, interior * 0.85, fg)
alpha = cv2.GaussianBlur(cv2.erode(hard2, np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 1.4)
yy = np.arange(H, dtype=np.float32)[:, None]
alpha = alpha * np.clip((1560 - yy) / 240, 0, 1)                # niente scrivania: sfumo il busto

SC, TX, TY = 0.85, 430 - 402 * 0.85, 1050 - 887 * 0.85         # viso (402, 887) -> (430, 1050)
M = np.float32([[SC, 0, TX], [0, SC, TY]])
fgw = cv2.warpAffine(fg, M, (W, H), flags=cv2.INTER_CUBIC)
al = cv2.warpAffine(alpha, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
sh = cv2.GaussianBlur(al, (0, 0), 30)[..., None]
img = bg * (1 - 0.5 * sh)
img = img * (1 - al[..., None]) + fgw * al[..., None]
im = Image.fromarray(cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)).convert("RGBA")
y = label(im, "TI FIDI DELLA SCHEDA?", W / 2, 1385, 76)
label(im, "TU L'OBIETTIVO, IO IL PERCORSO", W / 2, y + 10, 58, box=ORANGE)
im.convert("RGB").save(f"{D}/copertina_scheda_elisabetta.jpg", quality=95)
im.convert("RGB").crop((0, 240, 1080, 1680)).resize((540, 720)).save(f"{D}/_check_griglia_eli.jpg", quality=85)
print("ok")
