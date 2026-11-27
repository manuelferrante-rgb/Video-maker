"""Copertina "TIRA GIU' / LA SBARRA" (27/11): sfondo la trazione da 75 kg in gara, Manuel scontornato dal parlato
IMG_9358 (30 s, sopracciglia alzate), titolo sotto il mento. Anteprima del ritaglio 3:4."""
import subprocess, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R, W, H = "/home/user/video-maker", 1080, 1920
sys.path.insert(0, R)
from make_reel import Matter

ORANGE = (232, 102, 44)
FB = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
D = f"{R}/out/cover_tira_giu"


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


# sfondo: la trazione da 75 kg in gara col mento sopra la sbarra (gara.mov 14,0 s), Manuel in alto a destra
src = grab(f"{R}/src_27nov/gara.mov", 14.0)
Z, CX0, CY0 = 1.9, 560, 1010          # centro del ritaglio sorgente: Manuel finisce in alto a destra
w, h = W / Z, H / Z
x0, y0 = min(max(CX0 - w / 2, 0), W - w), min(max(CY0 - h / 2, 0), H - h)
bg = cv2.resize(src[int(y0):int(y0 + h), int(x0):int(x0 + w)], (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
yy = np.linspace(0, 1, H)[:, None, None]
bg = bg * (0.62 + 0.25 * np.exp(-((yy - 0.25) / 0.22) ** 2))

# io in primo piano (107,5 s, un po' perplesso). Scontorno: u2net per la sagoma + colore del muro per i ricci
fr = grab(f"{R}/src_27nov/IMG_9358.MOV", 22.5)   # scelto da Manuel
mt = Matter(f"{R}/models/u2net_human_seg.onnx")
a0 = mt.run([fr])[0]
person = (a0 > 0.3).astype(np.uint8)
band = cv2.dilate(person, np.ones((61, 61), np.uint8))
# pelle = colore del muro: l'interno della sagoma va riempito tutto (niente buchi sulla guancia)
m0 = (a0 > 0.5).astype(np.uint8)
cnts, _ = cv2.findContours(m0, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
filled = np.zeros_like(m0)
cv2.drawContours(filled, [max(cnts, key=cv2.contourArea)], -1, 1, thickness=-1)
core = cv2.erode(filled, np.ones((9, 9), np.uint8))
small = cv2.resize(fr, (W // 4, H // 4))
msk = cv2.resize(band * 255, (W // 4, H // 4), interpolation=cv2.INTER_NEAREST)
wall = cv2.resize(cv2.inpaint(small, msk, 15, cv2.INPAINT_TELEA), (W, H), interpolation=cv2.INTER_CUBIC)
wall = cv2.GaussianBlur(wall, (0, 0), 6).astype(np.float32)
f32 = fr.astype(np.float32)
diff = np.abs(f32 - wall).max(axis=2)          # quanto il pixel si stacca dal muro (bianco)
aw = np.clip((diff - 24) / 50.0, 0, 1)
alpha = np.where(core > 0, 1.0, aw * (band > 0))
alpha = cv2.GaussianBlur(alpha.astype(np.float32), (0, 0), 0.8)
# colore "pulito" sui bordi: tolgo la parte di muro mescolata nei ricci (niente alone bianco)
am = np.clip(alpha, 0.05, 1)[..., None]
fgc = np.clip((f32 - (1 - am) * wall) / am, 0, 255)
fgc = np.where(alpha[..., None] > 0.98, f32, fgc)
alpha = np.clip((alpha - 0.2) / 0.8, 0, 1)
# niente bordo bianco (Manuel): bordo ristretto di 2 px su tutta la sagoma + bordo dei ricci piu' duro
alpha = cv2.erode(alpha.astype(np.float32), np.ones((5, 5), np.uint8))
edge = (core == 0)
alpha = np.where(edge, np.clip((alpha - 0.3) / 0.7, 0, 1) ** 1.4, alpha)
# fuori dall'interno pieno: i pixel col colore del muro (il bianco tra i ricci) vanno via del tutto
wallish = np.clip((diff - 45) / 35.0, 0, 1)
ring = (filled > 0) & (cv2.erode(filled, np.ones((91, 91), np.uint8)) == 0) & (np.arange(H) < 1250)[:, None]
alpha = np.where(edge | ring, np.minimum(alpha, wallish), alpha)   # anche il bianco tra i ricci dentro la sagoma
alpha = cv2.GaussianBlur(alpha, (0, 0), 0.7)      # via la nebbia chiara attorno ai capelli
x = np.arange(W)
alpha = alpha * np.clip(np.minimum(x, W - 1 - x) / 120.0, 0, 1)[None, :]
alpha = alpha * np.clip((H - 1 - np.arange(H)) / 60.0, 0, 1)[:, None]   # il busto sfuma in basso, niente taglio dritto
SC, DX, DY = 0.74, -150, -170   # piu' busto (Manuel): mezzo busto grande, titolo sul petto
M = np.float32([[SC, 0, W / 2 * (1 - SC) + DX], [0, SC, H * (1 - SC) + DY]])
fg = cv2.warpAffine(fgc, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
al = cv2.warpAffine(alpha, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
sh = cv2.GaussianBlur(al, (0, 0), 30)[..., None]
img = bg * (1 - 0.55 * sh)
img = img * (1 - al[..., None]) + fg * al[..., None]
g = np.clip((np.arange(H) - 1560) / 260.0, 0, 1)[:, None, None]   # il busto si chiude nel buio in basso
img = img * (1 - 0.92 * g)
im = Image.fromarray(cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)).convert("RGBA")
y = label(im, "TIRA GIÙ", W / 2, 1170, 104)
label(im, "LA SBARRA", W / 2, y + 10, 104, box=ORANGE)
im.convert("RGB").save(f"{D}/copertina_tira_giu.jpg", quality=95)
im.convert("RGB").crop((0, 240, 1080, 1680)).resize((540, 720)).save(f"{D}/_check_griglia.jpg", quality=85)
print("ok")
