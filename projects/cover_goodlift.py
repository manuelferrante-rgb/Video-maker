#!/usr/bin/env python3
"""Copertine BOZZA dei trial reel GoodLift (novembre 2026), dai girati gia' in archivio (src_sl/raw):
A (gare)        = squat in buca di Manuel, titolo "VALIDA IN PALESTRA" / "NO REP IN GARA"
B (calisthenics)= chin up zavorrato al punto piu' alto, titolo "TRAZIONI PULITE?" / "SICURO?"
Quando arriva il parlato si rifanno col metodo standard (cover_panca_v2.py: Manuel scontornato davanti con
l'espressione piu' forte). Colore naturale: HLG letto come SDR. Esce anche l'anteprima 3:4 della griglia."""
import os, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

R, W, H = "/home/user/video-maker", 1080, 1920
OUT = f"{R}/out/goodlift"
FB = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
ORANGE = (232, 102, 44)
BASE = "scale=in_color_matrix=bt2020:out_color_matrix=bt709:in_range=tv:out_range=tv"


def frame(f, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", f"{R}/src_sl/raw/{f}.MOV", "-vf",
                          BASE + f",scale={W}:{H}", "-frames:v", "1", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3)


def crop(img, z, cx, cy):
    hw, hh = W / (2 * z), H / (2 * z)
    px, py = np.clip(cx * W, hw, W - hw), np.clip(cy * H, hh, H - hh)
    M = np.float32([[z, 0, W / 2 - z * px], [0, z, H / 2 - z * py]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC)


def label(im, txt, cx, y, size, box=(0, 0, 0), fg=(255, 255, 255)):
    ft = ImageFont.truetype(FB, size)
    l, t, r, b = ft.getbbox(txt)
    pw, ph = 34, 18
    w, h = r - l + pw * 2, b - t + ph * 2
    d = ImageDraw.Draw(im)
    d.rectangle([cx - w / 2, y, cx + w / 2, y + h], fill=box + (255,))
    d.text((cx - w / 2 + pw - l, y + ph - t), txt, font=ft, fill=fg)
    return y + h


def cover(name, f, t, z, cx, cy, l1, l2, ytitle, size=96):
    img = crop(frame(f, t), z, cx, cy).astype(np.float32)
    yy = np.linspace(0, 1, H)[:, None, None]
    img *= 1 - 0.45 * np.clip((yy - 0.55) / 0.35, 0, 1)        # fondo scurito sotto il titolo
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    y = label(im, l1, W / 2, ytitle, size)
    label(im, l2, W / 2, y + 6, size, box=ORANGE)
    im = im.convert("RGB")
    im.save(f"{OUT}/cover_{name}.jpg", quality=95)
    im.crop((0, 240, W, 1680)).resize((540, 720)).save(f"{OUT}/cover_{name}_griglia_3x4.jpg", quality=92)


os.makedirs(OUT, exist_ok=True)
cover("A_gare", "IMG_7178", 26.7, 1.3, 0.60, 0.60, "VALIDA IN PALESTRA", "NO REP IN GARA", 1210, 92)
cover("B_calisthenics", "IMG_7171", 3.05, 1.35, 0.42, 0.40, "TRAZIONI PULITE?", "SICURO?", 1180, 104)
print("ok")
