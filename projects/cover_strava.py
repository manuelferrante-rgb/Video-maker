#!/usr/bin/env python3
"""Copertina del reel Strava squat (Manuel 25/11: "solo io che faccio squat e lo sticker centrale, senza testo"):
fotogramma all'inizio dello squat (IMG_9301, 0,3 s, Manuel 25/11) ingrandito 1,4x (con un filo di nitidezza) con Manuel al centro, sticker di Strava (stesso del reel V2,
bordo nero) grande e centrato, sotto la faccia (sul petto e sul disco, come nel riferimento). Nessun titolo. Anteprima del ritaglio 3:4 della griglia."""
import subprocess, sys
from PIL import Image, ImageFilter
sys.path.insert(0, "/home/user/Video-maker/projects")
import strava_squat as st

R, W, H = "/home/user/Video-maker", 1080, 1920
Z, CX, CY = 1.1, 500, 1000   # inizio dello squat, in piedi
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "0.3", "-i", f"{R}/src_25nov/mio.mov", "-frames:v", "1",
                      "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                     capture_output=True, check=True).stdout
fr = Image.frombytes("RGB", (W, H), raw)
w, h = W / Z, H / Z
x0, y0 = min(max(CX - w / 2, 0), W - w), min(max(CY - h / 2, 0), H - h)
fr = fr.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h))
fr = fr.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2)).convert("RGBA")
fr.alpha_composite(st.sticker(dict(st.CFG["V1"], cx=540, y=765, stroke=6, fl=35, fv=81, gap=152, dv=67)))  # grande e centrato, sotto la faccia
out = fr.convert("RGB")
out.save(f"{R}/out/cover_strava.jpg", quality=95)
out.crop((0, 240, W, 1680)).save(f"{R}/out/cover_strava_griglia34.jpg", quality=90)
print("ok")
