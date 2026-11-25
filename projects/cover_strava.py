#!/usr/bin/env python3
"""Copertina del reel Strava squat (Manuel 25/11: "solo io che faccio squat e lo sticker centrale, senza testo"):
fotogramma in buca (IMG_9301, 3,0 s) ingrandito 1,4x (con un filo di nitidezza) con Manuel al centro, sticker di Strava (stesso del reel V2,
bordo nero) centrato sopra la testa. Nessun titolo. Anteprima del ritaglio 3:4 della griglia."""
import subprocess, sys
from PIL import Image, ImageFilter
sys.path.insert(0, "/home/user/Video-maker/projects")
import strava_squat as st

R, W, H = "/home/user/Video-maker", 1080, 1920
Z, CX, CY = 1.4, 390, 1172   # Manuel al centro (testa a ~y 900), sticker sul muro sopra
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "3.0", "-i", f"{R}/src_25nov/mio.mov", "-frames:v", "1",
                      "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                     capture_output=True, check=True).stdout
fr = Image.frombytes("RGB", (W, H), raw)
w, h = W / Z, H / Z
x0, y0 = min(max(CX - w / 2, 0), W - w), min(max(CY - h / 2, 0), H - h)
fr = fr.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h))
fr = fr.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2)).convert("RGBA")
fr.alpha_composite(st.sticker(dict(st.CFG["V1"], cx=540, y=270, stroke=6)))  # piu grande (Manuel)
out = fr.convert("RGB")
out.save(f"{R}/out/cover_strava.jpg", quality=95)
out.crop((0, 240, W, 1680)).save(f"{R}/out/cover_strava_griglia34.jpg", quality=90)
print("ok")
