#!/usr/bin/env python3
"""Storie per il reel "Tacco nello squat" (Jasmin col tacco, Nicolo' senza). Set da 5 (la 4a e' il reel):
1) sondaggio "in buca il tuo peso dove finisce?" (tallone / meta' piede / punta),
2) slider "quanto e' rigida la tua caviglia?", 3) spiegazione in 3 punti + rimando al reel,
5) "non sai se il tacco ti serve? rispondi a questa storia con il tuo squat di lato" (stessa CTA del reel, DM).
Helper e stile da projects/stories_set2.py."""
import os

R = "/home/user/video-maker"
src = open(f"{R}/projects/stories_set2.py").read()
exec(src[:src.index("# ===================== SET A")])

D = f"{R}/out/tacco/stories"
os.makedirs(D, exist_ok=True)
S = f"{R}/out/tacco/st"

# 1 sondaggio: Jasmin senza tacco in buca
im = background(f"{S}/b5buca.png", crop_y=0.5, dark=0.5)
y = label(im, "IN BUCA IL TUO PESO", 400, 84)
y = label(im, "DOVE FINISCE?", y + 6, 100, box=ORANGE)
text_block(im, ["Tallone, metà piede o punta:", "guardati di lato e rispondi"], y + 40, 50, font=FX,
           color=(255, 255, 255), hl={"LATO"})
sticker_zone(im, 1010, 1400, "SCEGLI LA TUA RISPOSTA")
footer(im, 0)
save(im, "T1_sondaggio_peso")

# 2 slider: primo piano della scarpa col tacco
im = background(f"{S}/bgj.png", crop_y=0.9, dark=0.5, zoom=2.0, cx=0.47)
y = label(im, "QUANTO È RIGIDA", 400, 96)
y = label(im, "LA TUA CAVIGLIA?", y + 6, 96, box=ORANGE)
text_block(im, ["Da sinistra (mobile)", "a destra (bloccata)"], y + 40, 50, font=FX, color=(255, 255, 255))
sticker_zone(im, 1010, 1400, "TRASCINA LO SLIDER")
footer(im, 1)
save(im, "T2_slider_caviglia")

# 3 spiegazione + rimando al reel: Nicolo' in gara sullo sfondo
im = background(f"{S}/bg2.png", crop_y=0.55, dark=0.78, blur=10, zoom=1.4, cx=0.62)
y = label(im, "IL TACCO", 400, 100)
y = label(im, "NON È PER TUTTI", y + 6, 92, box=ORANGE)
d = ImageDraw.Draw(im)
y += 50
for n, (t1, t2) in enumerate([("Caviglia rigida, finisci sul tallone:", "il tacco ti aiuta"),
                              ("Caviglia mobile, busto già verticale:", "il tacco non ti serve"),
                              ("In ogni caso si lavora su", "mobilità e dinamica")], 1):
    x0 = 90
    d.rectangle([x0, y, x0 + 84, y + 84], fill=ORANGE + (255,))
    d.text((x0 + 42, y + 42), str(n), font=f(FB, 60), fill=(255, 255, 255), anchor="mm")
    d.text((x0 + 112, y + 4), t1, font=f(FX, 40), fill=(255, 255, 255))
    d.text((x0 + 112, y + 52), t2, font=f(FS, 40), fill=IVORY)
    y += 140
label(im, "IL REEL NELLA PROSSIMA STORIA", 1360, 44)
footer(im, 2)
save(im, "T3_spiegazione")

# 5 CTA: stessa del reel (mandami il tuo squat), via risposta alla storia
im = background(f"{S}/f_23.9.png", crop_y=0.3, dark=0.45)
y = label(im, "NON SAI SE IL TACCO", 400, 76)
y = label(im, "TI SERVE?", y + 6, 110, box=ORANGE)
text_block(im, ["Rispondi a questa storia", "con il tuo squat ripreso di lato:", "lo guardiamo insieme"],
           1180, 50, font=FX, color=(255, 255, 255), hl={"LATO:"})
chevrons_down(im, W / 2, 1390, n=3, size=40)
footer(im, 4)
save(im, "T5_manda_squat")
print("ok")
