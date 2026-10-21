#!/usr/bin/env python3
"""Due set di storie: (P) parte esterna del piede nello squat, (R) respiro in panca.
Stessi helper e stile dei set precedenti (projects/stories_set2.py): foto scurita in navy, etichette in corsivo,
arancio come accento, logo in alto a sinistra, zone libere per gli sticker. La 4ª storia è il reel (lo mette Manuel)."""
import os

R = "/home/user/Video-maker"
src = open(f"{R}/projects/stories_set2.py").read()
exec(src[:src.index("# ===================== SET A")])  # solo gli helper (background, label, text_block, ...)

D = f"{R}/out/stories3"
os.makedirs(D, exist_ok=True)

# ===================== SET P: parte esterna del piede ======================================================
# P1 domanda a risposta multipla (avanti / dietro / esterno)
im = background(f"{D}/p_front.png", crop_y=0.75, dark=0.45, zoom=1.15, cx=0.45)
y = label(im, "NELLO SQUAT", 400, 104)
y = label(im, "DOVE SENTI LA PRESSIONE", y + 6, 70, box=ORANGE)
text_block(im, ["sotto il piede?"], y + 40, 60, font=FX, color=(255, 255, 255), hl={"PIEDE?"})
sticker_zone(im, 860, 1180, "SCEGLI LA TUA RISPOSTA")
footer(im, 0)
save(im, "P1_domanda")

# P2 domanda a risposta multipla: su cosa ti concentri
im = background(f"{D}/p_side.png", crop_y=0.3, dark=0.5, zoom=1.0, cx=0.5)
y = label(im, "SU COSA TI CONCENTRI", 400, 82)
y = label(im, "PER UNA SPINTA EFFICIENTE", y + 6, 66, box=ORANGE)
text_block(im, ["mentre fai squat?"], y + 40, 60, font=FX, color=(255, 255, 255), hl={"SQUAT?"})
sticker_zone(im, 860, 1180, "SCEGLI LA TUA RISPOSTA")
footer(im, 1)
save(im, "P2_domanda")

# P3 spiegazione minima + rimando al reel (il piede coi 3 punti è il fotogramma del reel)
im = background(f"{D}/p_foot.png", crop_y=0.0, dark=0.15, zoom=1.0, cx=0.5)
y = label(im, "IL PIEDE HA 3 PUNTI", 1090, 80)
y = label(im, "QUASI TUTTI PERDONO IL 3°", y + 6, 66, box=ORANGE)
text_block(im, ["Tieni la pressione sulla parte esterna,", "in discesa e in risalita."], y + 22, 44, font=FX,
           color=(255, 255, 255), hl={"ESTERNA,"})
label(im, "IL REEL NELLA PROSSIMA STORIA", 1405, 42)
footer(im, 2)
save(im, "P3_spiegazione")

# P5 link: correzione dello squat
im = background(f"{D}/p_man.png", crop_y=0.2, dark=0.42, zoom=1.0, cx=0.5)
y = label(im, "VUOI FARTI CORREGGERE", 400, 72)
y = label(im, "IL TUO SQUAT DA ME?", y + 6, 84, box=ORANGE)
link_zone(im, 1280, "CLICCA QUI")
footer(im, 4)
save(im, "P5_link")

# ===================== SET R: respiro in panca ==============================================================
# R1 com'è il tuo setting (Manuel mette lo slider)
im = background(f"{D}/r_bench1.png", crop_y=0.4, dark=0.45, zoom=1.0, cx=0.5)
y = label(im, "COM'È IL TUO", 400, 104)
y = label(im, "SETTING IN PANCA?", y + 6, 88, box=ORANGE)
text_block(im, ["Valutalo qui sotto", "e scopri le prossime storie."], y + 40, 54, font=FX, color=(255, 255, 255),
           hl={"PROSSIME"})
sticker_zone(im, 980, 1200, "SPOSTA LO SLIDER")
footer(im, 0)
save(im, "R1_setting")

# R2 domanda: riprendi aria a ogni ripetizione?
im = background(f"{D}/r_bench2.png", crop_y=0.4, dark=0.5, zoom=1.0, cx=0.5)
y = label(im, "IN PANCA", 400, 104)
y = label(im, "RIPRENDI ARIA", y + 6, 110, box=ORANGE)
text_block(im, ["a ogni ripetizione?"], y + 40, 62, font=FX, color=(255, 255, 255), hl={"OGNI"})
sticker_zone(im, 860, 1180, "SCEGLI LA TUA RISPOSTA")
footer(im, 1)
save(im, "R2_domanda")

# R3 spiegazione (senza citare il campione) + rimando al reel
im = background(f"{D}/r_bench1.png", crop_y=0.5, dark=0.8, zoom=1.0, cx=0.5, blur=16)
y = label(im, "HAI MAI PENSATO", 400, 96)
y = label(im, "DI NON RIPRENDERE ARIA", y + 6, 76, box=ORANGE)
y = text_block(im, ["ogni volta?"], y + 30, 60, font=FX, color=(255, 255, 255), hl={"VOLTA?"})
y = text_block(im, ["Con tante ripetizioni da fare", "e un setting che tiene,", "più ripetizioni con lo stesso respiro",
                    "ti fanno restare compatto."], y + 50, 46, hl={"RIPETIZIONI", "SETTING", "COMPATTO."})
text_block(im, ["Non è per tutti."], y + 26, 46, font=FX, color=(255, 255, 255))
label(im, "IL REEL NELLA PROSSIMA STORIA", 1400, 44)
footer(im, 2)
save(im, "R3_spiegazione")

# R5 domanda finale corta
im = background(f"{D}/r_man.png", crop_y=0.2, dark=0.42, zoom=1.0, cx=0.5)
y = label(im, "TU COME FAI?", 400, 110)
y = label(im, "UN RESPIRO A OGNI REP", y + 6, 76, box=ORANGE)
text_block(im, ["o più rep in apnea?"], y + 40, 60, font=FX, color=(255, 255, 255), hl={"APNEA?"})
sticker_zone(im, 860, 1180, "RISPONDI QUI SOTTO")
footer(im, 4)
save(im, "R5_domanda")
print("ok")
