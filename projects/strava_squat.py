#!/usr/bin/env python3
"""Reel "squat con lo sticker di Strava" (25/11/2026, riferimento mandato da Manuel): sopra lo squat di IMG_9301 lo
sticker delle statistiche di corsa (Distanza 0 km, Passo 00:00 /km, Tempo, puntino arancio del percorso), stessa
posizione e proporzioni del riferimento (colonna a sinistra, ~48-70% dell'altezza). Nient'altro: niente sottotitoli,
effetti o outro. Audio originale."""
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

R = "/home/user/Video-maker"
SRC, OUT = f"{R}/src_25nov/mio.mov", f"{R}/out/strava_squat"
W, H = 1080, 1920
FL = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 31)
FV = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 72)
CX = 315
ROWS = [("Distanza", "0 km", 930), ("Passo", "00:00 /km", 1066), ("Tempo", "2h 23m", 1200)]

im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
for lab, val, y in ROWS:
    d.text((CX, y), lab, font=FL, fill=(255, 255, 255, 255), anchor="mm")
    d.text((CX, y + 60), val, font=FV, fill=(255, 255, 255, 255), anchor="mm")
r = 17
d.ellipse([CX - r, 1400 - r, CX + r, 1400 + r], fill=(252, 76, 2, 255))   # arancio Strava
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sh.putalpha(im.split()[3].point(lambda v: int(v * 0.35)))
sh = sh.filter(ImageFilter.GaussianBlur(5))
out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
out.alpha_composite(sh, (0, 3))
out.alpha_composite(im)
out.save(f"{OUT}/sticker.png")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-i", f"{OUT}/sticker.png", "-filter_complex",
                f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[v];[v][1:v]overlay=0:0,"
                "format=yuv420p[o]", "-map", "[o]", "-map", "0:a:0", "-c:v", "libx264", "-crf", "16", "-preset", "slow",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", f"{OUT}/strava_squat.mp4"], check=True)
print("ok")
