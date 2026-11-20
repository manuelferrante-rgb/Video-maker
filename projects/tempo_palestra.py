#!/usr/bin/env python3
"""Reel 3 del 20/11: IL TEMPO IN PALESTRA (solo testo sopra lo squat di Manuel, 13 s). A/B = solo il gancio.
Girato: IMG_9126.MOV (squat, Drive parlati, nessun parlato: solo rumore di palestra -> muto).
Ripetizioni in IMG_9126: discese ~3.0 / 7.9 / 12.8 / 18.3, buca ~4.3 / 9.1 / 14.0 / 19.5, rerack da 23.
Testi nella fascia bassa (y ~1330): la fascia y ~760 del brief passa sulla faccia di Manuel in piedi e in buca."""
import sys
sys.path.insert(0, "/home/user/Video-maker/projects")
import tl_kit as k
from PIL import Image, ImageDraw

SRC = "/home/user/Video-maker/src_20nov/IMG_9126.MOV"
OUT = "/home/user/Video-maker/out/tempo_palestra"
TOTAL = 13.0

SHOTS = [
    dict(t0=0.0, t1=3.0, src=SRC, ss=18.2, z0=1.0, z1=1.07, c=(560, 900)),     # ripetizione pesante
    dict(t0=3.0, t1=7.0, src=SRC, ss=2.8, z0=1.10, z1=1.02, c=(520, 1000)),    # altra ripetizione
    dict(t0=7.0, t1=10.5, src=SRC, ss=7.7, z0=1.0, z1=1.08, c=(560, 950)),
    dict(t0=10.5, t1=13.0, src=SRC, ss=12.75, z0=1.12, z1=1.06, c=(600, 1000)),  # ultima: si rialza -> loop
]

# Manuel 20/11 (2a correzione): UNA sola versione; testi proprio al centro dello schermo, senza animazioni (entrano
# e basta, niente pop), ogni testo e' un blocco unico che entra tutto insieme; tolto il riquadro "60-90 MIN".
YC = 960
BLOCKS = [
    (0.0, 3.0, "Allenarti non ti ruba tempo.\n*Lo* *perdi* *tu.*", 74),
    (3.0, 7.0, "*30* *minuti* di riscaldamento.\n*Chiacchiere* tra le serie.\n*Telefono* in mano.", 66),
    (7.0, 10.5, "Un allenamento si chiude\nin *60-90* *minuti.*", 74),
    (10.5, 13.0, "E il tuo?\nSopra o sotto i *90* *minuti?*", 74),
]


def layers():
    return [k.popped(lambda tx=tx, sz=sz: k.text_img(tx, size=sz, maxw=1000), t0, t1, 540, YC, dur_out=0.001,
                     still=True) for t0, t1, tx, sz in BLOCKS]


SFX = []  # niente animazioni -> niente effetti: audio muto, la musica la mette Manuel

if __name__ == "__main__":
    k.build(f"{OUT}/tempo_palestra.mp4", TOTAL, SHOTS, layers(), SFX, cut_swoosh=0)
    k.sheet(f"{OUT}/tempo_palestra.mp4", f"{OUT}/sheet.jpg", n=26, cols=13)
