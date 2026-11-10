#!/usr/bin/env python3
"""Copertina "THIS IS STREETLIFTING" (stessa per A e B): squat in buca, stesso look del reel, scritta Anton come nel
reel. Esce anche l'anteprima del ritaglio 3:4 della griglia (y 240-1680)."""
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/user/video-maker/projects")
import this_is_streetlifting as T

sh = (0, 1, "IMG_7178", 26.7, 1.0, 1.3, 1.3, 0.56, 0.55, "col")
fr = T.decode((0, 1 / T.FPS, "IMG_7178", 26.7, 1.0))[0]
img = T.process(fr, 5.0, 0, sh, np.random.default_rng(1))
T.draw_text(img, "THIS IS", 120, 1420, 1)
T.draw_text(img, "STREETLIFTING", 176, 1570, 1)
out = np.clip(img, 0, 255).astype(np.uint8)
Image.fromarray(out).save(f"{T.OUT}/cover_streetlifting.jpg", quality=95)
prev = Image.fromarray(out).crop((0, 240, 1080, 1680))
Image.fromarray(out).resize((540, 960)).save(f"{T.OUT}/tmp/cover_full_small.jpg")
prev.resize((540, 720)).save(f"{T.OUT}/cover_streetlifting_griglia_3x4.jpg", quality=92)
print("ok")
