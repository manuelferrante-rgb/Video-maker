#!/usr/bin/env python3
"""Trial "Tacco nello squat" (16/11/2026): Jasmin col tacco, Nicolo' senza. 3 versioni, cambia SOLO il gancio.
Parlato src_tacco/parlato.MOV (proxy 1080x1920: p_norm.mov e p_zoom.mov = 1.18x sul viso, alternati per i jump cut).
B-roll: b5 Jasmin SENZA tacco, b3 Jasmin CON tacco, b2 Nicolo' in gara, b4 Nicolo' da dietro (256x480 -> solo in
riquadro), b1 box squat westside. Copy: projects/copy_trial_novembre.md (v5).
Uso: python3 projects/tacco.py [1 2 3]"""
import sys
import numpy as np, soundfile as sf
sys.path.insert(0, "/home/user/video-maker/projects")
from reel_kit import build, OR, WH, R
from ig1_cards import ClipFrames, rounded_frame, font, FSI, ease, eout, WHITE, alpha
from PIL import ImageDraw

S = f"{R}/src_tacco"
NORM, ZOOM = f"{S}/p_norm.mov", f"{S}/p_zoom.mov"
OUT = f"{R}/out/tacco"

# frasi: (inizio, fine) nel sorgente, inquadratura
PH = {"H1": (10.55, 14.12, ZOOM),   # Jasmin 200 kg di squat con il tacco e Nicolo' non lo usa
      "H2": (20.66, 24.66, ZOOM),   # Jasmin squatta con il tacco, Nicolo' no. Li alleno tutti e due io
      "H3": (30.50, 33.07, ZOOM),   # Il tacco ti aiuta? A Jasmin si' e a Nicolo' no
      "P1": (36.51, 37.78, NORM),   # Dipende dal punto debole
      "P2": (41.98, 43.86, ZOOM),   # Jasmin presenta una caviglia rigida
      "P3": (49.99, 52.06, NORM),   # Senza tacco, in buca, finiva sul tallone  (B-roll)
      "P4": (64.07, 67.15, NORM),   # Dopo che abbiamo inserito il tacco, il ginocchio riusciva ad andare piu' avanti
      "P5": (72.05, 73.83, NORM),   # mantenendo il peso al centro del piede  (B-roll)
      "P6": (96.67, 99.06, NORM),   # Nicolo', per conformazione, ha la caviglia piu' mobile  (B-roll)
      "P7": (108.19, 109.21, NORM),  # Quindi non gli serve  (B-roll)
      "P8": (127.60, 130.07, ZOOM),  # Anzi, una dinamica troppo verticale
      "P9": (162.43, 165.55, NORM),  # Con lui ci siamo concentrati di piu' a lavorare sulla catena cinetica posteriore
      "P10": (174.81, 176.90, ZOOM),  # Non so se ti serve, mandami il tuo squat
      "P11": (181.67, 183.58, NORM)}  # Io lo decido cosi', per ognuno  (-> loop sul gancio)
CUTS = {"P9": [(163.62, 164.12)]}   # "di piu' a lavorare" tolto per stare sui ~22 s
BODY = ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11"]

PAGES = {"H1": [(10.55, f"JASMIN: {OR}200 KG{WH}\\NDI SQUAT"), (12.09, f"CON IL {OR}TACCO"),
                (13.02, f"E NICOLÒ\\N{OR}NON LO USA")],
         "H2": [(20.66, f"JASMIN SQUATTA\\NCON IL {OR}TACCO"), (22.17, f"NICOLÒ {OR}NO"),
                (23.50, "LI ALLENO\\NTUTTI E DUE IO")],
         "H3": [(30.50, f"IL TACCO\\NTI {OR}AIUTA?"), (31.58, f"A JASMIN {OR}SÌ"), (32.34, f"A NICOLÒ {OR}NO")],
         "P1": [(36.51, f"DIPENDE DAL\\N{OR}PUNTO DEBOLE")],
         "P2": [(41.98, f"JASMIN PRESENTA UNA\\NCAVIGLIA {OR}RIGIDA")],
         "P3": [(49.99, "SENZA TACCO,\\NIN BUCA"), (51.40, f"FINIVA SUL\\N{OR}TALLONE")],
         "P4": [(64.07, f"DOPO CHE ABBIAMO\\NINSERITO IL {OR}TACCO"), (65.33, f"IL {OR}GINOCCHIO{WH} RIUSCIVA\\NAD ANDARE PIÙ AVANTI")],
         "P5": [(72.05, f"MANTENENDO IL PESO\\NAL {OR}CENTRO DEL PIEDE")],
         "P6": [(96.67, "NICOLÒ, PER\\NCONFORMAZIONE,"), (98.05, f"HA LA CAVIGLIA\\NPIÙ {OR}MOBILE")],
         "P7": [(108.19, f"QUINDI\\N{OR}NON GLI SERVE")],
         "P8": [(127.60, f"ANZI, HA UNA DINAMICA\\N{OR}TROPPO VERTICALE")],
         "P9": [(162.43, "CON LUI CI SIAMO\\NCONCENTRATI"), (164.12, f"SULLA CATENA\\N{OR}CINETICA POSTERIORE")],
         "P10": [(174.81, "NON SO SE TI SERVE:"), (175.85, f"MANDAMI IL TUO\\N{OR}SQUAT")],
         "P11": [(181.67, "IO LO DECIDO COSÌ,\\NPER OGNUNO")]}

HOOK_TITLES = {"H1": [("200 KG", "n"), ("COL TACCO", "o")],
               "H2": [("TACCO SÌ", "n"), ("TACCO NO", "o")],
               "H3": [("IL TACCO", "n"), ("AIUTA?", "o")]}

# energia della voce (blocchi da 10 ms) per tagliare le pause interne
_a, _sr = sf.read(f"{R}/out/tacco/parlato16k.wav", dtype="float32")
_n = len(_a) // 160
_DB = 20 * np.log10(np.sqrt((_a[:_n * 160].reshape(_n, 160) ** 2).mean(1)) + 1e-9)
_V = _DB > np.percentile(_DB, 98) - 32


def subsegs(a, b, gap=0.16, pre=0.05, post=0.07):
    """tratti di voce dentro [a, b]; le pause interne >= gap vengono tolte (restano pre/post di margine)."""
    i, e = int(a * 100), int(b * 100)
    runs = []
    while i < e:
        if _V[i]:
            j = i
            while j < e and _V[j:j + int(gap * 100)].any():
                j += 1
            runs.append([i / 100, j / 100])
            i = j
        else:
            i += 1
    runs = [r for r in runs if r[1] - r[0] >= 0.06] or [[a, b]]
    out = [[max(r[0] - pre, a), min(r[1] + post, b)] for r in runs]
    out[0][0], out[-1][1] = a, b
    return out


def pip(path, ss, caption, sp=1.0):
    clip = ClipFrames(path, ss, 3.0, sp, w=330, h=620)

    def draw(im, t, dur):
        a = ease(t / 0.22) * (1 - ease((t - (dur - 0.15)) / 0.15))
        if a <= 0:
            return
        s = 0.9 + 0.1 * eout(t / 0.3)
        w, h = 330 * s, 620 * s
        x0, y0 = 50, 300
        rounded_frame(im, clip.at(t), (x0, y0, x0 + w, y0 + h), a, radius=24, border=(255, 255, 255, 110))
        ImageDraw.Draw(im).text((x0 + 22, y0 + h - 22), caption, font=font(FSI, 46), fill=alpha(WHITE, a),
                                anchor="ls", stroke_width=2, stroke_fill=(0, 0, 0, int(160 * a)))
    return draw


def make(v):
    hook = f"H{v}"
    names = [hook] + BODY
    segs, owner = [], []
    for n in names:
        a, b, f = PH[n]
        parts, x = [], a
        for c0, c1 in CUTS.get(n, []):
            parts.append((x, c0)); x = c1
        parts.append((x, b))
        for pa, pb in parts:
          for s0, s1 in subsegs(pa, pb):
            segs.append((f, s0, s1))
            owner.append(n)

    def ref(src):
        """secondo del sorgente -> (indice segmento, secondo) per reel_kit"""
        for k, (_, s0, s1) in enumerate(segs):
            if src < s1:
                return (k, max(src, s0))
        return (len(segs) - 1, segs[-1][2])

    def start(n):
        return ref(PH[n][0])

    def nxt(n):
        i = names.index(n)
        return start(names[i + 1]) if i + 1 < len(names) else "end"

    pages = [(ref(s), txt) for n in names for s, txt in PAGES[n]]
    br = [(start("P3"), nxt("P3"), f"{S}/b5.mp4", 1.25, 1.0, 1.15, (540, 1000)),          # Jasmin senza tacco
          (ref(65.33), nxt("P5"), f"{S}/b3.mp4", 0.45, 0.85, 1.3, (540, 1250)),           # Jasmin col tacco
          (ref(98.05), nxt("P7"), f"{S}/b2.mp4", 0.9, 1.0, 1.0, None),                   # Nicolo' in gara
          (ref(164.12), nxt("P9"), f"{S}/b1.mp4", 0.0, 0.9, 1.0, None)]                   # box squat
    titles = [dict(t0=start(hook), t1=nxt(hook), items=HOOK_TITLES[hook]),
              dict(t0=start("P1"), t1=nxt("P1"), items=[("PUNTO DEBOLE", "o")]),
              dict(t0=start("P2"), t1=nxt("P2"), items=[("CAVIGLIA RIGIDA", "n")]),
              dict(t0=start("P3"), t1=nxt("P3"), items=[("SENZA TACCO", "n")]),
              dict(t0=start("P4"), t1=nxt("P5"), items=[("CON TACCO", "o")]),
              dict(t0=start("P6"), t1=start("P7"), items=[("CAVIGLIA MOBILE", "n")]),
              dict(t0=start("P7"), t1=nxt("P7"), items=[("TACCO NO", "o")]),
              dict(t0=start("P8"), t1=nxt("P8"), items=[("TROPPO VERTICALE", "n")]),
              dict(t0=ref(164.12), t1=nxt("P9"), items=[("CATENA POSTERIORE", "o")])]
    glow = [(ref(51.40), nxt("P3"), (695, 1262)),     # tallone in buca (senza tacco)
            (start("P5"), nxt("P5"), (530, 1278))]    # meta' piede (col tacco)
    overlays = [(start("P9"), ref(164.12), pip(f"{S}/b4.mp4", 1.0, "Nicolò, oggi"))]
    sfx = [(start(hook), 0.0, "comparsa", 0.16),
           (start("P1"), 0.0, "pop", 0.13),
           (start("P4"), 0.0, "pop", 0.13),
           (ref(51.40), 0.05, "disegno", 0.16),
           (start("P5"), 0.05, "disegno", 0.16),
           (start("P7"), 0.0, "pop", 0.13),
           (start("P9"), 0.0, "pop", 0.12),
           (ref(164.12), 0.0, "hit", 0.10)]
    return build(dict(out=f"{OUT}/v{v}", name=f"tacco_gancio{v}", segs=segs, pages=pages, br=br, titles=titles,
                      glow=glow, overlays=overlays, sfx=sfx))


if __name__ == "__main__":
    for v in (sys.argv[1:] or ["1", "2", "3"]):
        make(v)
