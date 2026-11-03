#!/usr/bin/env python3
"""Copertina del reel "L'intenzione" (uguale per le due versioni di prova): split screen come il video,
sopra l'atleta in pausa in bianco e nero, sotto io a colori che spingo in panca; al centro il titolo su 2 righe
(riquadro nero + arancio, Inter Black Italic). Salva anche l'anteprima del ritaglio 3:4 della griglia."""
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance

R, W, H = "/home/user/video-maker", 1080, 1920
ORANGE = (232, 102, 44)
FB = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
D = f"{R}/out/intenzione"


def frame(name, t, cy):
    out = f"{D}/_{name}_{t}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t}", "-i", f"{R}/src_giorni/{name}.mov", "-frames:v", "1",
                    out], check=True)
    im = Image.open(out).convert("RGB").resize((W, H))
    y0 = int(min(max(cy - 480, 0), H - 960))
    return im.crop((0, y0, W, y0 + 960))


def label(im, txt, cx, y, size, box=(0, 0, 0)):
    ft = ImageFont.truetype(FB, size)
    l, t, r, b = ft.getbbox(txt)
    w, h = r - l + 68, b - t + 36
    d = ImageDraw.Draw(im)
    d.rectangle([cx - w / 2, y, cx + w / 2, y + h], fill=box)
    d.text((cx - w / 2 + 34 - l, y + 18 - t), txt, font=ft, fill=(255, 255, 255))
    return y + h


top = ImageOps.grayscale(frame("IMG_8454", 1.2, 780)).convert("RGB")
top = ImageEnhance.Contrast(top).enhance(1.12)
bot = frame("IMG_8636", 4.5, 1100)
im = Image.new("RGB", (W, H))
im.paste(top, (0, 0))
im.paste(bot, (0, 960))
ImageDraw.Draw(im).rectangle([0, 957, W, 963], fill=(0, 0, 0))
y = label(im, "STESSO PROGRAMMA", W / 2, 860, 76)
label(im, "SOLO UNO MIGLIORA", W / 2, y + 8, 76, box=ORANGE)
im.save(f"{D}/copertina_intenzione.jpg", quality=95)
im.crop((0, 240, 1080, 1680)).resize((540, 720)).save(f"{D}/_check_griglia.jpg", quality=85)
print("ok")
