#!/usr/bin/env python3
"""Reel "Le 3 regole d'oro per riprendersi dall'infortunio" (~10 s).
Hook: io + titolo, su "infortunio" la struttura del dip che traballa; poi le 3 regole numerate in alto
(1 senza fastidio, 2 rinforzo, 3 gradualità) con i B-roll in tema, chiusura sul dip che risale.
Uso: python3 projects/infortunio_regole.py"""
import sys
sys.path.insert(0, "/home/user/video-maker/projects")
from reel_kit import build, OR, WH, R

A = f"{R}/src_dA"
SEGS = [(f"{A}/IMG_8577.mov", 3.15, 5.40),    # le tre regole d'oro per riprendersi dall'infortunio (2ª take)
        (f"{A}/IMG_8582.mov", 0.28, 2.88),    # lavora su porzioni di movimento che non ti danno fastidio
        (f"{A}/IMG_8582.mov", 4.62, 6.25),    # a bassa intensità e volume
        (f"{A}/IMG_8582.mov", 11.90, 13.94),  # e lavora sul rinforzo muscolare e tendineo
        (f"{A}/IMG_8582.mov", 20.65, 22.58),  # gradualmente reinserisci tutto
        (f"{A}/IMG_8582.mov", 32.68, 34.20)]  # e vedrai che recupererai (ripetuta, tengo la seconda)
build(dict(
    out=f"{R}/out/infortunio", name="reel_infortunio_3_regole", segs=SEGS,
    pages=[((0, 3.15), "LE 3 REGOLE D'ORO"), ((0, 4.11), f"PER RIPRENDERSI\\NDALL'{OR}INFORTUNIO"),
           ((1, 0.28), "LAVORA SU PORZIONI\\NDI MOVIMENTO"), ((1, 1.64), f"CHE NON TI DANNO\\N{OR}FASTIDIO"),
           ((2, 4.62), "A BASSA INTENSITÀ\\NE VOLUME"),
           ((3, 11.90), "E LAVORA SUL\\NRINFORZO"), ((3, 12.86), f"{OR}MUSCOLARE\\N{OR}E TENDINEO"),
           ((4, 20.65), "GRADUALMENTE"), ((4, 21.45), f"{OR}REINSERISCI TUTTO"),
           ((5, 32.68), f"E VEDRAI\\NCHE {OR}RECUPERERAI")],
    titles=[dict(t0=(0, 3.15), t1=(0, 4.11), items=[("LE 3 REGOLE", "k"), ("D'ORO", "o")]),
            dict(t0=(1, 0.28), t1=(3, 11.90), items=[("1", "o"), ("SENZA FASTIDIO", "k")]),
            dict(t0=(3, 11.90), t1=(4, 20.65), items=[("2", "o"), ("RINFORZO", "k")]),
            dict(t0=(4, 20.65), t1=(5, 32.68), items=[("3", "o"), ("GRADUALITÀ", "k")])],
    br=[((0, 4.11), (1, 0.28), f"{A}/dip_infortunio.mov", 17.0, 1.0, 1.0, None),  # la struttura che traballa
        ((1, 0.28), (1, 1.64), f"{A}/IMG_6813.mov", 0.0, 1.0, 1.0, None),        # porzione di movimento
        ((2, 4.62), (3, 11.90), f"{A}/IMG_7869.mov", 0.3, 1.0, 1.0, None),       # manubri leggeri
        ((3, 11.90), (4, 20.65), f"{A}/IMG_7873.mov", 0.2, 1.0, 1.0, None),      # rinforzo
        ((4, 20.65), (5, 32.68), f"{A}/IMG_8208.mov", 0.0, 0.75, 1.0, None),     # reinserisci tutto
        ((5, 32.68), "end", f"{A}/dip_infortunio.mov", 12.8, 1.0, 1.0, None)],   # risale: recuperato
    sfx=[((0, 3.15), 0.0, "comparsa", 0.22), ((0, 4.11), -0.12, "whoosh", 0.25),
         ((1, 0.28), 0.0, "punto_1", 0.4), ((3, 11.90), 0.0, "punto_2", 0.4), ((4, 20.65), 0.0, "punto_3", 0.4)],
))
