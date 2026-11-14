#!/usr/bin/env python3
"""Storia sondaggio GoodLift (riutilizzabile, nessuna data): fermo immagine di uno squat in buca al limite
+ "VALIDA O NO REP?" + zona libera per lo sticker sondaggio. Il giorno dopo: video della storia con il link
(sticker "PROVA GOODLIFT", link con ?utm_source=instagram&utm_medium=storie) e la risposta vera dell'app.
Helper e stile da projects/stories_set2.py. Fermo immagine: squat di Manuel (src_sl/raw/IMG_7178, 26,75 s);
se si usa il video di un atleta, serve il suo ok."""
import os

R = "/home/user/video-maker"
src = open(f"{R}/projects/stories_set2.py").read()
exec(src[:src.index("# ===================== SET A")])

D = f"{R}/out/goodlift/stories"
os.makedirs(D, exist_ok=True)

im = background(f"{R}/out/goodlift/st/squat_buca.png", crop_y=0.66, dark=0.3, zoom=1.15, cx=0.6)
logo(im)
y = label(im, "VALIDA", 400, 112)
y = label(im, "O NO REP?", y + 6, 112, box=ORANGE)
sticker_zone(im, 740, 940, "SONDAGGIO: VALIDA / NO REP")
footer(im, 0)
save(im, "GL1_sondaggio_valida_no_rep")
print("ok")
