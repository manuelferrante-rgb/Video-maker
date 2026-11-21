#!/usr/bin/env python3
"""Copertina del reel panca "la linea sul palmo" (indicazioni di Manuel 21/11): sfondo = la mano di IMG_9153 con i
puntini e la linea arancio disegnati nel reel; davanti Manuel scontornato dal parlato IMG_9210 (107,5 s, un po'
perplesso), ricci scontornati sul colore del muro (niente alone bianco); titolo APPOGGIALO QUI, / COSI' MIGLIORERA'
LA TUA PANCA sotto il mento.
Salva anche l'anteprima del ritaglio 3:4 della griglia."""
import subprocess, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R, W, H = "/home/user/video-maker", 1080, 1920
sys.path.insert(0, R)
from make_reel import Matter

ORANGE = (232, 102, 44)
FB = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
D = f"{R}/out/cover_panca_palmo"


def grab(path, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", path, "-frames:v", "1", "-vf",
                          f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", "-f", "rawvideo",
                          "-pix_fmt", "bgr24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3).copy()


def label(im, txt, cx, y, size, box=(0, 0, 0), fg=(255, 255, 255)):
    ft = ImageFont.truetype(FB, size)
    l, t, r, b = ft.getbbox(txt)
    pw, ph = 34, 18
    w, h = r - l + pw * 2, b - t + ph * 2
    d = ImageDraw.Draw(im)
    d.rectangle([cx - w / 2, y, cx + w / 2, y + h], fill=box + (255,))
    d.text((cx - w / 2 + pw - l, y + ph - t), txt, font=ft, fill=fg)
    return y + h


# sfondo: la mano di IMG_9153 (8,25 s) con i puntini e la linea arancio del reel, in alto a destra
src = grab(f"{R}/src_20nov/IMG_9153.MOV", 8.25)
Z, X0, Y0 = 3.0, 8, 770
bg = cv2.resize(src[Y0:Y0 + int(H / Z), X0:X0 + int(W / Z)], (W, H), interpolation=cv2.INTER_CUBIC)
bgi = Image.fromarray(cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)).convert("RGBA")
P1, P2 = [((x - X0) * Z, (y - Y0) * Z) for x, y in ((308, 926), (210, 952))]
SS = 3
lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
d = ImageDraw.Draw(lay)
q = lambda p: (p[0] * SS, p[1] * SS)
d.line([q(P1), q(P2)], fill=(255, 255, 255, 255), width=30 * SS)
d.line([q(P1), q(P2)], fill=ORANGE + (255,), width=18 * SS)
for p in (P1, P2):
    for r, c in ((31, (255, 255, 255)), (24, ORANGE)):
        d.ellipse([q((p[0] - r, p[1] - r)), q((p[0] + r, p[1] + r))], fill=c + (255,))
bgi.alpha_composite(lay.resize((W, H), Image.LANCZOS))
bg = cv2.cvtColor(np.array(bgi.convert("RGB")), cv2.COLOR_RGB2BGR).astype(np.float32)
yy = np.linspace(0, 1, H)[:, None, None]
bg = bg * (0.6 + 0.25 * np.exp(-((yy - 0.25) / 0.2) ** 2))

# io in primo piano (107,5 s, un po' perplesso). Scontorno: u2net per la sagoma + colore del muro per i ricci
fr = grab(f"{R}/src_parlato20/IMG_9210.MOV", 107.5)
mt = Matter(f"{R}/models/u2net_human_seg.onnx")
a0 = mt.run([fr])[0]
person = (a0 > 0.3).astype(np.uint8)
band = cv2.dilate(person, np.ones((61, 61), np.uint8))
core = cv2.erode((a0 > 0.8).astype(np.uint8), np.ones((25, 25), np.uint8))
small = cv2.resize(fr, (W // 4, H // 4))
msk = cv2.resize(band * 255, (W // 4, H // 4), interpolation=cv2.INTER_NEAREST)
wall = cv2.resize(cv2.inpaint(small, msk, 15, cv2.INPAINT_TELEA), (W, H), interpolation=cv2.INTER_CUBIC)
wall = cv2.GaussianBlur(wall, (0, 0), 6).astype(np.float32)
f32 = fr.astype(np.float32)
diff = np.abs(f32 - wall).max(axis=2)          # quanto il pixel si stacca dal muro (bianco)
aw = np.clip((diff - 18) / 55.0, 0, 1)
alpha = np.where(core > 0, 1.0, aw * (band > 0))
alpha = cv2.GaussianBlur(alpha.astype(np.float32), (0, 0), 0.8)
# colore "pulito" sui bordi: tolgo la parte di muro mescolata nei ricci (niente alone bianco)
am = np.clip(alpha, 0.05, 1)[..., None]
fgc = np.clip((f32 - (1 - am) * wall) / am, 0, 255)
fgc = np.where(alpha[..., None] > 0.98, f32, fgc)
alpha = np.clip((alpha - 0.12) / 0.88, 0, 1)      # via la nebbia chiara attorno ai capelli
x = np.arange(W)
alpha = alpha * np.clip(np.minimum(x, W - 1 - x) / 120.0, 0, 1)[None, :]
alpha = alpha * np.clip((H - 1 - np.arange(H)) / 140.0, 0, 1)[:, None]   # il busto sfuma in basso, niente taglio dritto
SC, DX, DY = 0.56, -170, -330
M = np.float32([[SC, 0, W / 2 * (1 - SC) + DX], [0, SC, H * (1 - SC) + DY]])
fg = cv2.warpAffine(fgc, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
al = cv2.warpAffine(alpha, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
sh = cv2.GaussianBlur(al, (0, 0), 30)[..., None]
img = bg * (1 - 0.55 * sh)
img = img * (1 - al[..., None]) + fg * al[..., None]
g = np.clip((np.arange(H) - 1380) / 220.0, 0, 1)[:, None, None]   # il busto si chiude nel buio in basso
img = img * (1 - 0.92 * g)
im = Image.fromarray(cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)).convert("RGBA")
y = label(im, "APPOGGIALO QUI,", W / 2, 1130, 84)
label(im, "COSÌ MIGLIORERÀ LA TUA PANCA", W / 2, y + 10, 58, box=ORANGE)
im.convert("RGB").save(f"{D}/copertina_panca_palmo.jpg", quality=95)
im.convert("RGB").crop((0, 240, 1080, 1680)).resize((540, 720)).save(f"{D}/_check_griglia.jpg", quality=85)
print("ok")
