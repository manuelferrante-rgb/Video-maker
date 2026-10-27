#!/usr/bin/env python3
"""Storie per i reel "3 regole d'oro dopo un infortunio" (I) e "fermi lunghi in panca" (P).
Set da 5 (la 4ª è il reel). Infortunio: box domande aperto sul tuo infortunio, sondaggio, spiegazione minima,
form. Panca: punto critico, cosa correggeresti per primo, spiegazione, form.
Helper e stile da projects/stories_set2.py."""
import os

R = "/home/user/video-maker"
src = open(f"{R}/projects/stories_set2.py").read()
exec(src[:src.index("# ===================== SET A")])  # solo gli helper (background, label, text_block, ...)

# ===================== SET I: infortunio ====================================================================
D = f"{R}/out/infortunio/stories"
os.makedirs(D, exist_ok=True)
S = f"{R}/out/infortunio/st"

# I1 box domande aperto: il tuo infortunio
im = background(f"{S}/face.png", crop_y=0.3, dark=0.55)
y = label(im, "QUAL È STATO", 400, 100)
y = label(im, "IL TUO INFORTUNIO?", y + 6, 92, box=ORANGE)
text_block(im, ["E come l'hai risolto?", "Raccontamelo qui sotto."], y + 40, 56, font=FX, color=(255, 255, 255),
           hl={"RISOLTO?"})
sticker_zone(im, 1010, 1400, "SCRIVI LA TUA RISPOSTA")
footer(im, 0)
save(im, "I1_domanda_aperta")

# I2 sondaggio: ti fermi o continui?
im = background(f"{S}/dip.png", crop_y=0.3, dark=0.55)
y = label(im, "DOPO UN INFORTUNIO", 400, 84)
y = label(im, "TI FERMI DEL TUTTO", y + 6, 92, box=ORANGE)
text_block(im, ["o continui ad allenarti?"], y + 40, 60, font=FX, color=(255, 255, 255), hl={"CONTINUI"})
sticker_zone(im, 1010, 1400, "SCEGLI LA TUA RISPOSTA")
footer(im, 1)
save(im, "I2_sondaggio")

# I3 spiegazione minima + rimando al reel
im = background(f"{S}/press.png", crop_y=0.3, dark=0.78, blur=12)
y = label(im, "RECUPERARE", 400, 104)
y = label(im, "NON VUOL DIRE STARE FERMI", y + 6, 66, box=ORANGE)
y = text_block(im, ["Ci sono 3 regole d'oro", "per tornare ad allenarti al meglio:"], y + 40, 48, font=FX,
               color=(255, 255, 255), hl={"3", "REGOLE", "D'ORO"})
for n, txt in enumerate(["SENZA FASTIDIO", "RINFORZO", "GRADUALITÀ"], 1):
    ft = f(FB, 64)
    d = ImageDraw.Draw(im)
    x0 = W / 2 - 260
    d.rectangle([x0, y + 26, x0 + 84, y + 110], fill=ORANGE + (255,))
    d.text((x0 + 42, y + 68), str(n), font=ft, fill=(255, 255, 255), anchor="mm")
    d.rectangle([x0 + 96, y + 26, x0 + 96 + 440, y + 110], fill=(0, 0, 0, 255))
    d.text((x0 + 96 + 220, y + 68), txt, font=f(FB, 52), fill=(255, 255, 255), anchor="mm")
    y += 100
text_block(im, ["Sempre con il via libera del tuo medico", "o fisioterapista."], y + 40, 34, color=IVORY)
label(im, "IL REEL NELLA PROSSIMA STORIA", 1400, 44)
footer(im, 2)
save(im, "I3_spiegazione")

# I5 form
im = background(f"{S}/face.png", crop_y=0.25, dark=0.45)
y = label(im, "VUOI TORNARE AD ALLENARTI", 400, 64)
y = label(im, "AL MEGLIO DOPO UN INFORTUNIO?", y + 6, 60, box=ORANGE)
link_zone(im, 1300, "COMPILA IL FORM QUA SOTTO")
footer(im, 4)
save(im, "I5_form")

# ===================== SET P: panca, fermi lunghi ===========================================================
D = f"{R}/out/panca/stories"
os.makedirs(D, exist_ok=True)
S = f"{R}/out/panca/st"

# P1 punto critico (sondaggio sì/no)
im = background(f"{S}/b7506.png", crop_y=0.4, dark=0.55)
y = label(im, "HAI MAI PENSATO CHE", 400, 76)
y = label(im, "IL PUNTO CRITICO", y + 6, 100, box=ORANGE)
text_block(im, ["della tua alzata non è davvero", "quello su cui devi lavorare?"], y + 40, 54, font=FX,
           color=(255, 255, 255), hl={"DAVVERO"})
sticker_zone(im, 1010, 1400, "SCEGLI LA TUA RISPOSTA")
footer(im, 0)
save(im, "P1_punto_critico")

# P2 cosa correggeresti per primo
im = background(f"{S}/c1.png", crop_y=0.4, dark=0.55)
y = label(im, "SE IN PANCA FAI FATICA", 400, 72)
y = label(im, "AL PETTO", y + 6, 110, box=ORANGE)
text_block(im, ["cosa correggeresti per primo?"], y + 40, 58, font=FX, color=(255, 255, 255), hl={"PRIMO?"})
sticker_zone(im, 1010, 1400, "SCEGLI LA TUA RISPOSTA")
footer(im, 1)
save(im, "P2_cosa_correggi")

# P3 spiegazione + rimando al reel
im = background(f"{S}/c2.png", crop_y=0.4, dark=0.78, blur=12)
y = label(im, "NON SERVONO", 400, 100)
y = label(im, "I FERMI LUNGHI", y + 6, 100, box=ORANGE)
y = text_block(im, ["Se fai fatica al petto conta di più", "come ci arrivi:"], y + 40, 48, font=FX,
               color=(255, 255, 255), hl={"COME", "CI", "ARRIVI:"})
y = text_block(im, ["setting scapolare ottimale,", "a braccia tese rilassa bene il carico,",
                    "discese lente e controllate."], y + 30, 46, hl={"SETTING", "SCAPOLARE", "RILASSA", "LENTE"})
label(im, "IL REEL NELLA PROSSIMA STORIA", 1400, 44)
footer(im, 2)
save(im, "P3_spiegazione")

# P5 form
im = background(f"{S}/face.png", crop_y=0.25, dark=0.45)
y = label(im, "VUOI FARTI ANALIZZARE", 400, 72)
y = label(im, "LA TUA PANCA?", y + 6, 96, box=ORANGE)
link_zone(im, 1300, "COMPILA IL FORM QUA SOTTO")
footer(im, 4)
save(im, "P5_form")
print("ok")
