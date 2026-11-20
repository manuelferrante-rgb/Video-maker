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
YT = 1420  # centro dei testi

SHOTS = [
    dict(t0=0.0, t1=3.0, src=SRC, ss=18.2, z0=1.0, z1=1.07, c=(560, 900)),     # ripetizione pesante
    dict(t0=3.0, t1=7.0, src=SRC, ss=2.8, z0=1.10, z1=1.02, c=(520, 1000)),    # altra ripetizione
    dict(t0=7.0, t1=10.5, src=SRC, ss=7.7, z0=1.0, z1=1.08, c=(560, 950)),
    dict(t0=10.5, t1=13.0, src=SRC, ss=12.75, z0=1.12, z1=1.06, c=(600, 1000)),  # ultima: si rialza -> loop
]

HOOK = {"A": "Allenarti non ti ruba tempo.\n*Lo* *perdi* *tu.*",
        "B": "Un allenamento si chiude\nin *60-90* *minuti.*"}
# Manuel 20/11: via "3 ore in palestra non sono dedizione", e "seduta di forza" -> "allenamento" (piu' generico).
# Nel B la frase dei 60-90 minuti e' gia' il gancio: nel blocco centrale va il come (dalla caption).
MID = {"A": "Un allenamento si chiude\nin *60-90* *minuti.*",
       "B": "Riscaldamento mirato,\nrecuperi *solo* *quanto* *serve.*"}


def label_layer():
    """Riquadro arancio 60-90 MIN in alto (niente cronometro in questo reel: Manuel 20/11)."""
    lab = k.label_img("60-90 MIN", k.ORANGE, size=74)
    return k.popped(lab, 8.2, 10.5, 540, 360)


def layers(v):
    L = [k.popped(lambda: k.text_img(HOOK[v], size=71, maxw=1000), 0.0, 3.0, 540, YT, still=True)]
    items = [("*30* *minuti* di riscaldamento.", 3.15), ("*Chiacchiere* tra le serie.", 4.35),
             ("*Telefono* in mano.", 5.55)]
    for j, (tx, t0) in enumerate(items):
        L.append(k.popped(lambda tx=tx: k.text_img(tx, size=62, maxw=1040), t0, 7.0, 540, YT - 100 + j * 92))
    L.append(label_layer())
    L.append(k.popped(lambda: k.text_img(MID[v], size=70, maxw=1000), 7.0, 10.5,
                      540, YT))
    L.append(k.popped(lambda: k.text_img("E il tuo?\nSopra o sotto i *90* *minuti?*", size=74, maxw=1040), 10.5, 13.0, 540, YT))
    return L


SFX = [(3.15, "pop", 0.35), (4.35, "pop", 0.35), (5.55, "pop", 0.35), (7.0, "whoosh", 0.25),
       (8.2, "hit", 0.3), (10.5, "pop", 0.3)]

if __name__ == "__main__":
    for v in sys.argv[1:] or ["A", "B"]:
        k.build(f"{OUT}/tempo_palestra_{v}.mp4", TOTAL, SHOTS, layers(v), SFX)
        k.sheet(f"{OUT}/tempo_palestra_{v}.mp4", f"{OUT}/sheet_{v}.jpg", n=26, cols=13)
