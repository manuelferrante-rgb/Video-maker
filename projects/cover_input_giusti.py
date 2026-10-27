#!/usr/bin/env python3
"""Copertine serie "Input giusti": fotogramma forte dell'esercizio (faccia visibile), titolo su 2 righe nella fascia
y ~1060-1250: [INPUT GIUSTI] nero + [ESERCIZIO] arancio (Inter Black Italic). Stesso schema per i 4 reel,
così in griglia si legge come una serie. Salva anche l'anteprima del ritaglio 3:4 (y 240-1680)."""
import subprocess
from PIL import Image, ImageDraw, ImageFont

R = "/home/user/video-maker"
S = f"{R}/src_input"
W, H = 1080, 1920
ORANGE = (232, 102, 44)
FB = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
TONEMAP = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,")
# reel: (clip, secondo, hdr, nome)
COVERS = {"mu": ("IMG_7636", 4.2, True, "MUSCLE UP"), "trazioni": ("IMG_8337", 1.9, False, "TRAZIONI"),
          "dip": ("IMG_8485", 0.5, False, "DIP"), "squat": ("IMG_7650", 2.5, True, "SQUAT")}


def label(im, txt, cx, y, size, box=(0, 0, 0), fg=(255, 255, 255)):
    ft = ImageFont.truetype(FB, size)
    l, t, r, b = ft.getbbox(txt)
    pw, ph = 34, 18
    w, h = r - l + pw * 2, b - t + ph * 2
    d = ImageDraw.Draw(im)
    d.rectangle([cx - w / 2, y, cx + w / 2, y + h], fill=box + (255,))
    d.text((cx - w / 2 + pw - l, y + ph - t), txt, font=ft, fill=fg)
    return y + h


grid = []
for key, (clip, ss, hdr, name) in COVERS.items():
    D = f"{R}/out/input_giusti/{key}"
    base = f"{D}/cover_base.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", f"{S}/{clip}.mov", "-frames:v", "1",
                    "-vf", f"{TONEMAP if hdr else ''}scale={W}:{H}:flags=lanczos", base], check=True)
    im = Image.open(base).convert("RGBA")
    y = label(im, "INPUT GIUSTI", W / 2, 1062, 92)
    label(im, name, W / 2, y + 10, 118, box=ORANGE)
    im.convert("RGB").save(f"{D}/copertina_input_giusti_{key}.jpg", quality=95)
    g = im.convert("RGB").crop((0, 240, 1080, 1680)).resize((360, 480))
    g.save(f"{D}/_check_griglia.jpg", quality=85)
    grid.append(g)
sheet = Image.new("RGB", (360 * 4 + 30, 480), "white")
for k, g in enumerate(grid):
    sheet.paste(g, (k * 370, 0))
sheet.save(f"{R}/out/input_giusti/_griglia_4.jpg", quality=85)
print("ok")
