#!/usr/bin/env python3
"""Storie per il reel "In che giorni allenarsi". Set da 5 (la 4ª è il reel):
1) sondaggio "ti alleni 4 volte a settimana? e il giorno dopo una seduta pesante ti alleni di nuovo?",
2) slider "il giorno dopo una seduta pesante quanto ti senti carico?", 3) spiegazione in 3 punti + rimando al reel,
5) "vuoi una programmazione su misura per te? compila il form". Helper e stile da projects/stories_set2.py."""
import os

R = "/home/user/video-maker"
src = open(f"{R}/projects/stories_set2.py").read()
exec(src[:src.index("# ===================== SET A")])  # solo gli helper (background, label, text_block, ...)

D = f"{R}/out/giorni/stories"
os.makedirs(D, exist_ok=True)
S = f"{R}/out/giorni/st"

# 1 sondaggio
im = background(f"{S}/f_131.4.png", crop_y=0.3, dark=0.55)
y = label(im, "TI ALLENI", 400, 100)
y = label(im, "4 VOLTE A SETTIMANA?", y + 6, 72, box=ORANGE)
text_block(im, ["E il giorno dopo una seduta pesante", "ti alleni di nuovo?"], y + 40, 52, font=FX,
           color=(255, 255, 255), hl={"PESANTE"})
sticker_zone(im, 1010, 1400, "SCEGLI LA TUA RISPOSTA")
footer(im, 0)
save(im, "G1_sondaggio")

# 2 slider
im = background(f"{S}/fatica.png", crop_y=0.3, dark=0.55)
y = label(im, "IL GIORNO DOPO", 400, 96)
y = label(im, "UNA SEDUTA PESANTE", y + 6, 84, box=ORANGE)
text_block(im, ["quanto ti senti carico?"], y + 40, 60, font=FX, color=(255, 255, 255), hl={"CARICO?"})
sticker_zone(im, 1010, 1400, "TRASCINA LO SLIDER")
footer(im, 1)
save(im, "G2_slider")

# 3 spiegazione + rimando al reel
im = background(f"{S}/panca.png", crop_y=0.4, dark=0.78, blur=12)
y = label(im, "I GIORNI CONTANO", 400, 92)
y = label(im, "QUANTO LA PROGRAMMAZIONE", y + 6, 60, box=ORANGE)
d = ImageDraw.Draw(im)
y += 40
for n, (t1, t2) in enumerate([("Una seduta pesante stressa", "anche il sistema nervoso"),
                              ("Una priorità diversa", "per ogni seduta"),
                              ("Le sedute più intense", "dopo il riposo")], 1):
    x0 = 120
    d.rectangle([x0, y, x0 + 84, y + 84], fill=ORANGE + (255,))
    d.text((x0 + 42, y + 42), str(n), font=f(FB, 60), fill=(255, 255, 255), anchor="mm")
    d.text((x0 + 116, y + 4), t1, font=f(FX, 44), fill=(255, 255, 255))
    d.text((x0 + 116, y + 54), t2, font=f(FS, 40), fill=IVORY)
    y += 140
label(im, "IL REEL NELLA PROSSIMA STORIA", 1400, 44)
footer(im, 2)
save(im, "G3_spiegazione")

# 5 form
im = background(f"{S}/f_99.2.png", crop_y=0.25, dark=0.45)
y = label(im, "VUOI UNA PROGRAMMAZIONE", 400, 60)
y = label(im, "SU MISURA PER TE?", y + 6, 92, box=ORANGE)
link_zone(im, 1300, "COMPILA IL FORM QUA SOTTO")
footer(im, 4)
save(im, "G5_form")
print("ok")
