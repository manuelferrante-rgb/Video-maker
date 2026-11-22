"""Copertina del reel "Un mese di trazioni zavorrate in 30 secondi" sul modello della copertina panca (21/11):
sfondo Elisabetta col disco nero + cronometro rosso 00:30, Manuel scontornato dal parlato IMG_9209 (57 s, deciso),
ricci scontornati sul colore del muro, titolo UN MESE DI TRAZIONI / IN 30 SECONDI."""
import subprocess, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R, W, H = "/home/user/video-maker", 1080, 1920
sys.path.insert(0, R)
from make_reel import Matter

ORANGE = (232, 102, 44)
FB = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
D = f"{R}/out/cover_trazioni_30s"
sys.path.insert(0, f"{R}/projects")
import tl_kit as k


def grab(path, t, hdr=False):
    pre = k.TONEMAP + "," if hdr else ""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", path, "-frames:v", "1", "-vf",
                          pre + f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", "-f", "rawvideo",
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


# sfondo: Elisabetta in cima alla trazione col disco nero (IMG_5418, 6,4 s), spostata in alto a destra,
# e il cronometro rosso del reel su 00:30
src = grab(f"{R}/src_20nov/IMG_5418.MOV", 6.4, hdr=True)
S, TX, TY = 0.72, 440, 60   # tutta Elisabetta col disco nella colonna di destra
fill = cv2.GaussianBlur(cv2.resize(src, (W, H)), (0, 0), 30)
fill = (fill.astype(np.float32) * 0.6).astype(np.uint8)
bg = cv2.warpAffine(src, np.float32([[S, 0, TX], [0, S, TY]]), (W, H), flags=cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
m = cv2.warpAffine(np.ones(src.shape[:2], np.float32), np.float32([[S, 0, TX], [0, S, TY]]), (W, H))
m = cv2.GaussianBlur(m, (0, 0), 12)[..., None]
bg = (bg * m + fill * (1 - m)).astype(np.uint8)
bgi = Image.fromarray(cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)).convert("RGBA")
k.put(bgi, k.timer_img("00:30", dh=90), 270, 420)
bg = cv2.cvtColor(np.array(bgi.convert("RGB")), cv2.COLOR_RGB2BGR).astype(np.float32)
yy = np.linspace(0, 1, H)[:, None, None]
bg = bg * (0.62 + 0.25 * np.exp(-((yy - 0.25) / 0.22) ** 2))

# io in primo piano (107,5 s, un po' perplesso). Scontorno: u2net per la sagoma + colore del muro per i ricci
fr = grab(f"{R}/src_parlato20/IMG_9209.MOV", 57.0)
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
y = label(im, "UN MESE DI TRAZIONI", W / 2, 1130, 80)
label(im, "IN 30 SECONDI", W / 2, y + 10, 84, box=ORANGE)
im.convert("RGB").save(f"{D}/copertina_trazioni_30s.jpg", quality=95)
im.convert("RGB").crop((0, 240, 1080, 1680)).resize((540, 720)).save(f"{D}/_check_griglia.jpg", quality=85)
print("ok")
