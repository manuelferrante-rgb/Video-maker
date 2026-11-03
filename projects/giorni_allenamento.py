#!/usr/bin/env python3
"""Reel "In che giorni allenarsi" (format IG1), due versioni di prova dallo stesso parlato IMG_8742:
  B (~23 s): script completo;  A (~18 s): senza la frase dei distretti e con la chiusura corta.
Io compaio a inizio e fine; nel mezzo schede animate (giorni_cards.py), B-roll a tutto schermo e, quando parlo,
B-roll in riquadro con didascalia in corsivo. Tutte le pause tagliate, 1.1x, sottotitoli standard, sfx leggeri.
Uso: python3 projects/giorni_allenamento.py [A|B ...]"""
import os, sys
sys.path.insert(0, "/home/user/video-maker/projects")
from reel_kit import build, OR, R
from ig1_cards import ClipFrames, export, rounded_frame, font, FSI, ease, eout, WHITE, alpha
from giorni_cards import card_intro, card_recupero, card_split, card_riposo, card_energia
from PIL import ImageDraw

S = f"{R}/src_giorni"
T = f"{S}/IMG_8742.mov"
OUT = f"{R}/out/giorni"
CARDS = f"{OUT}/cards"
os.makedirs(CARDS, exist_ok=True)

# parlato: (nome, inizio, fine) nel sorgente, pause interne tagliate sull'energia della voce
P = {"H1": (0.27, 2.18),        # ti alleni quattro volte a settimana ad alta intensità
     "H2": (2.42, 5.46),        # allora i giorni in cui ti alleni contano quanto la programmazione
     "P1": (66.55, 68.85),      # una seduta pesante stressa anche il sistema nervoso
     "P2": (68.95, 71.62),      # se non recuperi abbastanza ti senti ancora stanco
     "Q": (96.92, 100.10),      # allena più distretti a seduta, ma con una priorità diversa
     "M1": (130.62, 133.23),    # per questo ai miei atleti dico anche quando allenarsi
     "M2": (135.16, 136.78),    # per ottenere il massimo dei risultati
     "R1a": (151.77, 152.93),   # le sedute intense
     "R1b": (153.09, 154.45),   # mettile dopo i giorni di riposo
     "R2": (154.79, 156.88),    # così riesci ad avere il massimo delle energie
     "C1": (16.26, 17.12),      # ti è stato utile?
     "C2": (17.44, 19.85),      # qual è la tua split settimanale? fammelo sapere nei commenti
     "C2s": (17.44, 18.66)}     # qual è la tua split settimanale?
PAGES = {"H1": [(0.27, "TI ALLENI 4 VOLTE\\NA SETTIMANA"), (1.40, f"AD {OR}ALTA INTENSITÀ?")],
         "H2": [(2.42, "ALLORA I GIORNI\\NIN CUI TI ALLENI"), (4.04, f"CONTANO QUANTO LA\\N{OR}PROGRAMMAZIONE")],
         "P1": [(66.55, "UNA SEDUTA PESANTE"), (67.64, f"STRESSA ANCHE IL\\N{OR}SISTEMA NERVOSO")],
         "P2": [(68.95, "SE NON RECUPERI\\NABBASTANZA"), (70.28, f"TI SENTI\\N{OR}ANCORA STANCO")],
         "Q": [(96.92, "ALLENA PIÙ DISTRETTI\\NA SEDUTA"), (98.68, f"MA CON UNA\\N{OR}PRIORITÀ DIVERSA")],
         "M1": [(130.62, "PER QUESTO\\NAI MIEI ATLETI"), (131.80, f"DICO ANCHE\\N{OR}QUANDO ALLENARSI")],
         "M2": [(135.16, f"PER OTTENERE\\NIL {OR}MASSIMO"), (135.95, f"DEI {OR}RISULTATI")],
         "R1a": [(151.77, f"LE SEDUTE {OR}INTENSE")],
         "R1b": [(153.09, f"METTILE DOPO I\\NGIORNI DI {OR}RIPOSO")],
         "R2": [(154.79, "COSÌ RIESCI AD AVERE"), (155.98, f"IL {OR}MASSIMO\\NDELLE ENERGIE")],
         "C1": [(16.26, "TI È STATO UTILE?")],
         "C2": [(17.44, f"QUAL È LA TUA\\N{OR}SPLIT SETTIMANALE?"), (18.82, "FAMMELO SAPERE\\NNEI COMMENTI")],
         "C2s": [(17.44, f"QUAL È LA TUA\\N{OR}SPLIT SETTIMANALE?")]}
VERSIONS = {"B": ["H1", "H2", "P1", "P2", "Q", "M1", "M2", "R1a", "R1b", "R2", "C1", "C2"],
            "A": ["H1", "H2", "P1", "P2", "M1", "M2", "R1a", "R1b", "R2", "C2s"]}


def render_cards():
    clip = ClipFrames(f"{S}/IMG_8641.mov", 12.0, 4.0)
    for nm, fn in [("intro", card_intro(clip)), ("recupero", card_recupero()), ("split", card_split()),
                   ("riposo", card_riposo()), ("energia", card_energia())]:
        if not os.path.exists(f"{CARDS}/{nm}.mp4"):
            export(fn, 4.5, f"{CARDS}/{nm}.mp4")


def pip(path, ss, caption, sp=1.0):
    """B-roll in riquadro arrotondato in alto a sinistra mentre parlo, con didascalia in corsivo."""
    clip = ClipFrames(path, ss, 4.0, sp, w=330, h=470)

    def draw(im, t, dur):
        a = ease(t / 0.22) * (1 - ease((t - (dur - 0.15)) / 0.15))
        if a <= 0:
            return
        s = 0.9 + 0.1 * eout(t / 0.3)
        w, h = 330 * s, 470 * s
        x0, y0 = 50, 300
        rounded_frame(im, clip.at(t), (x0, y0, x0 + w, y0 + h), a, radius=24, border=(255, 255, 255, 110))
        d = ImageDraw.Draw(im)
        f = font(FSI, 46)
        d.text((x0 + 22, y0 + h - 22), caption, font=f, fill=alpha(WHITE, a), anchor="ls",
               stroke_width=2, stroke_fill=(0, 0, 0, int(160 * a)))
    return draw


def make(ver):
    names = VERSIONS[ver]
    k = {n: i for i, n in enumerate(names)}
    segs = [(T, *P[n]) for n in names]
    pages = [((k[n], s), txt) for n in names for s, txt in PAGES[n]]
    nxt = lambda n: (k[names[names.index(n) + 1]], P[names[names.index(n) + 1]][0])  # inizio frase dopo
    br = [((k["H2"], 2.70), nxt("H2"), f"{CARDS}/intro.mp4", 0, 1.0, 1.0, None, 0.12),
          ((k["P1"], 66.55), (k["P1"], 67.60), f"{S}/IMG_8636.mov", 6.0, 1.0, 1.0, None),
          ((k["P1"], 67.60), (k["P2"], 70.25), f"{CARDS}/recupero.mp4", 0, 1.0, 1.0, None),
          ((k["P2"], 70.25), nxt("P2"), f"{S}/IMG_8454.mov", 45.0, 1.0, 1.0, None),
          ((k["M2"], 135.16), nxt("M2"), f"{S}/IMG_8641.mov", 19.0, 1.0, 1.0, None),
          ((k["R1a"], 151.77), nxt("R1b"), f"{CARDS}/riposo.mp4", 0, 1.0, 1.0, None),
          ((k["R2"], 154.79), nxt("R2"), f"{CARDS}/energia.mp4", 0, 1.0, 1.0, None)]
    overlays = [((k["M1"], 130.62), (k["M1"], 133.23), pip(f"{S}/IMG_8634.mov", 5.5, "i miei atleti"))]
    sfx = [((k["H1"], 0.27), 0.0, "comparsa", 0.18),
           ((k["H2"], 2.70), -0.08, "whoosh", 0.22),
           ((k["P1"], 67.60), -0.08, "whoosh", 0.2), ((k["P1"], 67.60), 0.4, "disegno", 0.22),
           ((k["M1"], 130.62), 0.0, "pop", 0.15),
           ((k["R1a"], 151.77), -0.08, "whoosh", 0.2),
           ((k["R1a"], 151.77), 1.0, "pop", 0.16), ((k["R1a"], 151.77), 1.25, "pop", 0.16),
           ((k["R2"], 154.79), -0.08, "whoosh", 0.2), ((k["R2"], 154.79), 1.35, "ding", 0.14)]
    if "Q" in k:
        br.append(((k["Q"], 98.60), nxt("Q"), f"{CARDS}/split.mp4", 0, 1.0, 1.0, None, 0.12))
        overlays.append(((k["Q"], 96.92), (k["Q"], 98.60), pip(f"{S}/IMG_8452.mov", 2.0, "più distretti")))
        sfx += [((k["Q"], 96.92), 0.0, "pop", 0.15), ((k["Q"], 98.60), -0.08, "whoosh", 0.2)]
        sfx += [((k["Q"], 98.60), 0.3 + 0.22 * j, "tick", 0.14) for j in range(4)]
    br.sort(key=lambda b: (b[0][0], b[0][1]))
    build(dict(out=f"{OUT}/{ver}", name=f"reel_giorni_{ver}", segs=segs, pages=pages, br=br, overlays=overlays,
               sfx=sfx))


if __name__ == "__main__":
    render_cards()
    for v in (sys.argv[1:] or ["A", "B"]):
        make(v)
