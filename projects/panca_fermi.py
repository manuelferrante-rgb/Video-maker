#!/usr/bin/env python3
"""Reel panca: "Non fare i fermi lunghi in panca se fai fatica al petto" (~14 s).
Hook: io + [PANCA][FERMI LUNGHI] con la barra arancio che cancella i fermi; poi come ci arrivi (discesa al petto),
setting scapolare (zoom sulla spalla con evidenziatore), a braccia tese rilassa il carico, discese lente,
chiusura con la risalita: "e vedrai che la tua panca migliorerà immediatamente".
Uso: python3 projects/panca_fermi.py"""
import sys
sys.path.insert(0, "/home/user/video-maker/projects")
from reel_kit import build, OR, WH, R

A, B = f"{R}/src_dA", f"{R}/src_dB"
SEGS = [(f"{B}/IMG_8574.mov", 0.28, 2.92),   # non fare i fermi lunghi nella panca se fai fatica al petto
        (f"{B}/IMG_8574.mov", 4.15, 14.97),  # sembra un controsenso ... discese lente e controllate
        (f"{B}/IMG_8573.mov", 0.0, 2.10)]    # e vedrai che la tua panca migliorerà immediatamente
build(dict(
    out=f"{R}/out/panca", name="reel_panca_fermi", segs=SEGS,
    pages=[((0, 0.28), "NON FARE I FERMI\\NLUNGHI NELLA PANCA"), ((0, 1.72), f"SE FAI FATICA\\NAL {OR}PETTO"),
           ((1, 4.15), "SEMBRA UN\\NCONTROSENSO"), ((1, 5.19), "MA È PIÙ IMPORTANTE"),
           ((1, 5.91), f"CAPIRE {OR}COME\\N{OR}CI ARRIVI"), ((1, 7.35), "QUINDI CONCENTRATI\\NSUL MANTENERE"),
           ((1, 8.87), f"UN SETTING\\N{OR}SCAPOLARE{WH} OTTIMALE"), ((1, 10.23), "A BRACCIA TESE"),
           ((1, 11.03), "RILASSA BENE\\NIL CARICO"), ((1, 12.31), "MAGARI LAVORA SU"),
           ((1, 13.11), f"{OR}DISCESE LENTE\\N{WH}E CONTROLLATE"),
           ((2, 0.0), "E VEDRAI CHE\\NLA TUA PANCA"), ((2, 0.96), f"{OR}MIGLIORERÀ\\N{WH}IMMEDIATAMENTE")],
    titles=[dict(t0=(0, 0.28), t1=(1, 4.15), items=[("PANCA", "o"), ("FERMI LUNGHI", "k")], strike=(0, 1.40)),
            dict(t0=(1, 5.91), t1=(1, 7.35), items=[("COME CI ARRIVI", "o")]),
            dict(t0=(1, 8.87), t1=(1, 10.23), items=[("SETTING SCAPOLARE", "k")]),
            dict(t0=(1, 13.11), t1=(2, 0.0), items=[("DISCESE LENTE", "o")])],
    br=[((0, 1.72), (0, 2.92), f"{B}/IMG_8061.mov", 0.5, 1.0, 1.0, None),          # fatica al petto
        ((1, 5.19), (1, 7.35), f"{A}/IMG_7865.mov", 0.0, 0.7, 1.0, None),          # come ci arrivi
        ((1, 8.87), (1, 10.23), f"{B}/IMG_7506.mov", 0.0, 0.6, 1.5, (420, 1080)),  # setting scapolare (zoom)
        ((1, 10.23), (1, 12.31), f"{B}/IMG_7981.mov", 0.0, 0.9, 1.0, None),        # a braccia tese
        ((1, 12.31), (2, 0.0), f"{B}/IMG_7506.mov", 0.3, 1.0, 1.0, None),          # discesa lenta
        ((2, 0.0), (2, 0.96), f"{B}/IMG_7506.mov", 3.5, 1.0, 1.0, None)],          # risalita
    glow=[((1, 8.87), (1, 10.23), (480, 1020))],
    sfx=[((0, 0.28), 0.0, "comparsa", 0.22), ((0, 1.40), 0.0, "disegno", 0.3), ((1, 5.91), 0.0, "pop", 0.15),
         ((1, 8.87), 0.1, "punto_1", 0.22), ((1, 13.11), 0.0, "pop", 0.15)],
))
