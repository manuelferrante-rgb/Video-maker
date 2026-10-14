#!/usr/bin/env python3
"""Reel trazioni v2, stile "motion graphics": etichette in corsivo che entrano a pop, schermate grafiche a pieno
schermo (contatore, scritta barrata, uscita con diagonale arancio), frecce animate, pulsante finale, effetti sonori.
Colori brand: navy #14304F, arancio #E8662C, avorio #F2EEE3. Colore video: parlato non toccato, HDR solo convertito."""
import math, os, subprocess

SRC = "/home/user/Video-maker/src_traz"
OUT = "/home/user/Video-maker/out/trazioni_v2"
os.makedirs(OUT, exist_ok=True)
W, H, FPS, SPEED = 1080, 1920, 30, 1.05
P = f"{SRC}/parlato.MOV"

# voce (sorgente): inizio, fine, zoom A-roll, parole (tempi modello)
SEGS = [
    (0.00, 3.02, 1.30, [("SE", 0.0), ("TI", 0.16), ("DICO", 0.24), ("|ATTIVA", 0.56), ("IL", 0.96), ("DORSALE,", 1.04),
                        ("|NON", 1.52), ("TI", 1.68), ("STO", 1.76), ("SPIEGANDO", 2.0), ("NIENTE.", 2.48)]),
    (9.02, 10.88, 1.00, [("NELLE", 8.93), ("TRAZIONI,", 9.25), ("|PENSA", 9.73), ("SOLO", 10.05), ("|UNA", 10.29),
                         ("COSA.", 10.45)]),
    (10.98, 12.15, 1.30, [("TIRA", 10.95), ("GIÙ", 11.25), ("|LA", 11.49), ("SBARRA.", 11.65)]),
    (24.50, 25.75, 1.30, [("QUEL", 24.42), ("MOVIMENTO", 24.82)]),
    (25.98, 27.53, 1.00, [("ABBASSA", 25.89), ("LE", 26.61), ("SCAPOLE", 26.85)]),
    (27.70, 29.45, 1.00, [("ED", 27.6), ("È", 27.81), ("LÌ", 27.97), ("CHE", 28.13), ("|IL", 28.29), ("DORSALE", 28.37),
                          ("LAVORA.", 29.01)]),
    (49.42, 53.25, 1.00, [("NON", 49.35), ("SERVONO", 49.59), ("|MILLE", 50.07), ("TECNICISMI,", 50.39), ("|MA", 51.11),
                          ("CAPIRE", 51.35), ("|QUELLO", 51.83), ("CHE", 52.15), ("|SI", 52.31), ("STA", 52.47),
                          ("FACENDO.", 52.71)]),
    (55.50, 57.30, 1.30, [("SPERO", 55.42), ("TI", 55.82), ("|SIA", 55.9), ("UTILE.", 56.14)]),
]
SEGS = [(s, s + round((e - s) * FPS) / FPS, *r) for s, e, *r in SEGS]
KEY = {"DORSALE", "SBARRA.", "SCAPOLE", "TECNICISMI,", "CAPIRE", "TIRA", "GIÙ", "ABBASSA"}
# pagine evidenziate per intero e più grandi (hook)
BIG_PAGES = {("ATTIVA", "IL", "DORSALE,"), ("NON", "TI", "STO", "SPIEGANDO", "NIENTE.")}

starts, t = [], 0.0
for s, e, *_ in SEGS:
    starts.append(t)
    t += (e - s) / SPEED
TOTAL = t


def out_t(seg, src_t):
    return starts[seg] + (src_t - SEGS[seg][0]) / SPEED


def word_t(seg, w):
    for txt, tt in SEGS[seg][3]:
        if txt.lstrip("|") == w:
            return max(out_t(seg, tt + 0.08), starts[seg])
    raise KeyError(w)


def seg_end(i):
    return starts[i] + (SEGS[i][1] - SEGS[i][0]) / SPEED


TONEMAP = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")


def run(cmd):
    subprocess.run(cmd, check=True)


# 1) A-roll (nessuna correzione colore): zoom leggero solo per togliere il disordine in basso
lst = []
for i, (s, e, z, _) in enumerate(SEGS):
    cw, ch = int(W / z) // 2 * 2, int(H / z) // 2 * 2
    d = e - s
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.3f}", "-i", P, "-t", f"{d:.4f}", "-frames:v",
         str(round(d * FPS)), "-vf",
         f"scale={W}:{H},crop={cw}:{ch}:(iw-{cw})/2:(ih-{ch})*0.06,scale={W}:{H}:flags=lanczos,setsar=1,fps={FPS}",
         "-af", f"afade=t=in:d=0.015,afade=t=out:st={d - 0.03:.3f}:d=0.03", "-c:v", "libx264", "-crf", "14",
         "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-ar", "48000", f"{OUT}/s{i}.mov"])
    lst.append(f"file '{OUT}/s{i}.mov'")
open(f"{OUT}/segs.txt", "w").write("\n".join(lst) + "\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/segs.txt", "-filter_complex",
     f"[0:v]setpts=PTS/{SPEED},fps={FPS}[vo];[0:a]atempo={SPEED},highpass=f=80,"
     f"acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-14:TP=-1.5:LRA=7[ao]",
     "-map", "[vo]", "-map", "[ao]", "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "192k", "-ar", "48000", f"{OUT}/aroll.mp4"])

# 2) B-roll
DEP_SP = 0.75  # depressione rallentata leggermente
DEP_T0 = starts[4]
DEP_T1 = seg_end(5) + 1.5 / FPS
DEP_SRC = (0.0, 2.45)  # tratto con le depressioni scapolari, prima della trazione
# zoom fisso su spalle/scapole e dorsale (coordinate sorgente 1080x1920)
DZ, DCX, DCY = 1.55, 520, 840
FULL0 = word_t(6, "MA")
BROLL = [  # inizio, fine, file, inizio sorgente, velocità, tipo
    (0.0, word_t(0, "ATTIVA"), "esecuzioni.mov", 0.35, 1.0, "full"),  # apertura d'impatto, poi subito il parlato
    (word_t(2, "TIRA"), seg_end(2) + 1.5 / FPS, "depressione.mov", 2.3, 0.9, "full"),  # tira giù la sbarra: trazione reale
    (DEP_T0, DEP_T1, "depressione.mov", DEP_SRC[0], DEP_SP, "dep"),
    (FULL0, seg_end(6) + 1.5 / FPS, "esecuzioni.mov", 1.6, 1.0, "full"),  # trazione completa
]
BROLL = [(round(t0 * FPS) / FPS, round(t1 * FPS) / FPS, *r) for t0, t1, *r in BROLL]

for k, (t0, t1, f, ss, sp, kind) in enumerate(BROLL):
    nfr = int(round((t1 - t0) * FPS))
    vf = [TONEMAP, f"setpts=PTS/{sp}", f"fps={FPS}"]
    if kind == "dep":
        cw, ch = int(W / DZ) // 2 * 2, int(H / DZ) // 2 * 2
        vf += [f"trim=0:{(DEP_SRC[1] - DEP_SRC[0]) / sp:.3f}", f"crop={cw}:{ch}:{DCX - cw // 2}:{DCY - ch // 2}",
               f"scale={W}:{H}:flags=lanczos", "tpad=stop_mode=clone:stop_duration=2"]
    else:
        vf += [f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos", f"crop={W}:{H}",
               "tpad=stop_mode=clone:stop_duration=1"]
    vf += ["setsar=1", "format=yuv420p"]
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", f"{SRC}/{f}", "-vf", ",".join(vf), "-frames:v",
         str(nfr), "-an", "-c:v", "libx264", "-crf", "15", "-preset", "fast", f"{OUT}/b{k}.mp4"])



# 3) Schermate grafiche a pieno schermo (PIL, RGBA con alfa) --------------------------------------------
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_BI = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
NAVY, NAVY_D, ORANGE, IVORY = (20, 48, 79), (10, 26, 44), (232, 102, 44), (242, 238, 227)


def font(sz):
    return ImageFont.truetype(FONT_BI, sz)


def ease_out(x):
    x = min(max(x, 0), 1)
    return 1 - (1 - x) ** 3


def pop_scale(x):  # 0 -> 1.1 -> 1
    if x <= 0:
        return 0.0
    if x < 0.6:
        return 1.1 * ease_out(x / 0.6)
    return 1.1 - 0.1 * ease_out((x - 0.6) / 0.4)


def stripes_bg(frame):
    img = Image.new("RGBA", (W, H), NAVY_D + (255,))
    d = ImageDraw.Draw(img)
    off = (frame * 3) % 120
    for x in range(-H, W + 120, 120):
        x0 = x + off
        d.polygon([(x0, 0), (x0 + 50, 0), (x0 + 50 + H * 0.45, H), (x0 + H * 0.45, H)], fill=NAVY + (255,))
    return img


def text_box(txt, size, fg, bg, pad=(34, 18), border=None):
    f = font(size)
    l, t, r, b = f.getbbox(txt)
    w, h = r - l + pad[0] * 2, b - t + pad[1] * 2
    im = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([4, 4, w + 4, h + 4], radius=14, fill=bg + (255,),
                        outline=(border + (255,)) if border else None, width=5 if border else 0)
    d.text((4 + pad[0] - l, 4 + pad[1] - t), txt, font=f, fill=fg + (255,))
    return im


def paste_scaled(base, im, cx, cy, s, alpha=1.0):
    if s <= 0.01:
        return
    w, h = max(int(im.width * s), 1), max(int(im.height * s), 1)
    im2 = im.resize((w, h), Image.LANCZOS)
    if alpha < 1:
        a = im2.split()[3].point(lambda v: int(v * alpha))
        im2.putalpha(a)
    base.alpha_composite(im2, (int(cx - w / 2), int(cy - h / 2)))


def strike(d, box_xy, p, width=16):
    """X arancio disegnata progressivamente (p 0..1) sopra un riquadro."""
    x0, y0, x1, y1 = box_xy
    p1, p2 = min(p * 2, 1), min(max(p * 2 - 1, 0), 1)
    if p1 > 0:
        d.line([(x0, y0), (x0 + (x1 - x0) * p1, y0 + (y1 - y0) * p1)], fill=ORANGE + (255,), width=width)
    if p2 > 0:
        d.line([(x1, y0), (x1 - (x1 - x0) * p2, y0 + (y1 - y0) * p2)], fill=ORANGE + (255,), width=width)


def wipe(img, p):
    """uscita: diagonale arancio che attraversa lo schermo e scopre il video sotto (p 0..1)."""
    if p <= 0:
        return img
    yy, xx = np.mgrid[0:H, 0:W]
    s = (xx + (H - yy) * 0.35) / (W + H * 0.35)
    pos = -0.15 + 1.35 * p
    arr = np.array(img)
    gone = s < pos - 0.07
    band = (s >= pos - 0.07) & (s < pos)
    arr[gone, 3] = 0
    arr[band] = list(ORANGE) + [255]
    return Image.fromarray(arr)


def render_card(name, dur, draw_fn, wipe_frames=7):
    n = int(round(dur * FPS))
    path = f"{OUT}/{name}.mov"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", path], stdin=subprocess.PIPE)
    for fr in range(n):
        img = draw_fn(fr, fr / FPS)
        k = fr - (n - wipe_frames)
        if k >= 0:
            img = wipe(img, (k + 1) / wipe_frames)
        p.stdin.write(img.tobytes())
    p.stdin.close()
    p.wait()
    return path


SFX = []  # (tempo, nome, volume)

# card 1: "ATTIVA IL DORSALE" barrato su "non ti sto spiegando niente"
C1_T0 = word_t(0, "NON") - 0.05
C1_T1 = seg_end(0) + 2 / FPS
C1_X = word_t(0, "NIENTE.") - C1_T0 - 0.05
box1 = text_box("ATTIVA IL DORSALE", 86, IVORY, NAVY_D, pad=(40, 30), border=IVORY)
hdr1 = text_box("SE TI DICO...", 64, IVORY, (0, 0, 0), pad=(26, 14))


def card1(fr, t):
    img = stripes_bg(fr)
    paste_scaled(img, hdr1, W / 2, 640, pop_scale(t / 0.25))
    paste_scaled(img, box1, W / 2, 860, pop_scale((t - 0.08) / 0.3))
    if t >= C1_X:
        d = ImageDraw.Draw(img)
        bw, bh = box1.width, box1.height
        strike(d, (W / 2 - bw / 2 - 10, 860 - bh / 2 - 20, W / 2 + bw / 2 + 10, 860 + bh / 2 + 20),
               ease_out((t - C1_X) / 0.22))
    return img


render_card("card1", C1_T1 - C1_T0, card1)
SFX += [(C1_T0 - 0.08, "whoosh", 0.35), (C1_T0 + C1_X, "hit", 0.5), (C1_T1 - 0.2, "swoosh", 0.3)]

# card 2: contatore "+1000 TECNICISMI" barrato su "non servono mille tecnicismi"
C2_T0 = starts[6]
C2_T1 = word_t(6, "MA") + 2 / FPS
C2_CNT = (0.15, word_t(6, "TECNICISMI,") - C2_T0)  # il numero sale fino a quando dice "tecnicismi"
C2_X = C2_CNT[1] + 0.25
lab2 = text_box("TECNICISMI", 64, IVORY, (0, 0, 0), pad=(24, 12))


def card2(fr, t):
    img = stripes_bg(fr)
    d = ImageDraw.Draw(img)
    s = pop_scale((t + 0.12) / 0.3)
    # riquadro contatore
    bw, bh = 760, 340
    box = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    bd = ImageDraw.Draw(box)
    bd.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=26, fill=(8, 18, 32, 255), outline=NAVY + (255,), width=4)
    x = (t - C2_CNT[0]) / max(C2_CNT[1] - C2_CNT[0], 0.1)
    val = int(round(1000 * ease_out(x))) if x > 0 else 0
    txt = f"+{val:,}".replace(",", ".")
    f = font(180)
    l, tt, r, b = f.getbbox(txt)
    bd.text(((bw - (r - l)) / 2 - l, (bh - (b - tt)) / 2 - tt + 20), txt, font=f, fill=IVORY + (255,))
    paste_scaled(img, box, W / 2, 900, s)
    paste_scaled(img, lab2, W / 2, 900 - bh / 2 - 10, pop_scale((t - 0.1) / 0.25))
    if t >= C2_X:
        strike(d, (W / 2 - bw / 2 - 20, 900 - bh / 2 - 20, W / 2 + bw / 2 + 20, 900 + bh / 2 + 20),
               ease_out((t - C2_X) / 0.22))
    return img


render_card("card2", C2_T1 - C2_T0, card2)
SFX += [(C2_T0 - 0.06, "whoosh", 0.35), (C2_T0 + C2_X, "hit", 0.5), (C2_T1 - 0.2, "swoosh", 0.3)]
# tick del contatore
tt_ = C2_CNT[0]
while tt_ < C2_CNT[1]:
    SFX.append((C2_T0 + tt_, "tick", 0.25))
    tt_ += 0.07 + 0.25 * ((tt_ - C2_CNT[0]) / (C2_CNT[1] - C2_CNT[0])) ** 2

CARDS = [(C1_T0, C1_T1, "card1"), (C2_T0, C2_T1, "card2")]


# 4) Sottotitoli (piccoli, riquadro nero, parola chiave arancio) + etichette + grafiche ASS ------------------
def ass_t(x):
    x = max(x, 0)
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


ORANGE_A, IVORY_A, BLACK_A, NAVY_A, WHITE_A, RED = "&H002C66E8&", "&H00E3EEF2&", "&H00000000&", "&H004F3014&", "&H00FFFFFF&", "&H002E2EE6&"
KEY = {"DORSALE", "DORSALE,", "SBARRA.", "SCAPOLE", "TECNICISMI,", "CAPIRE", "NIENTE.", "COSA."}

pages = []
for i, seg in enumerate(SEGS):
    cur = []
    for txt, tt in seg[3]:
        brk = txt.startswith("|")
        txt = txt.lstrip("|")
        if cur and (brk or len(cur) == 4):
            pages.append(cur)
            cur = []
        cur.append((txt, max(out_t(i, tt + 0.08), starts[i]), i))
    pages.append(cur)
voice_end = out_t(7, 56.62)
ev = []
for j, pg in enumerate(pages):
    st, seg = pg[0][1], pg[0][2]
    en = pages[j + 1][0][1] if j + 1 < len(pages) and pages[j + 1][0][2] == seg else seg_end(seg)
    if j + 1 == len(pages):
        en = voice_end + 0.1
    words = [f"{{\\c{ORANGE_A if w in KEY else WHITE_A}}}{w.rstrip(',.?')}" for w, *_ in pg]
    ev.append(f"Dialogue: 5,{ass_t(st)},{ass_t(en)},Sub,,0,0,0,,{{\\fad(60,0)}}{' '.join(words)}")


def label(t0, t1, txt, y, box=BLACK_A, fg=WHITE_A, size=90, sfx=True, rot=0):
    pop = rf"{{\an8\pos(540,{y})\frz{rot}\3c{box}\c{fg}\fs{size}\fscx0\fscy0\t(0,90,\fscx112\fscy112)\t(90,170,\fscx100\fscy100)}}"
    ev.append(f"Dialogue: 4,{ass_t(t0)},{ass_t(t1)},Lab,,0,0,0,,{pop}{txt}")
    if sfx:
        SFX.append((t0, "pop", 0.28))


# hook
label(0.02, word_t(0, "ATTIVA"), "SE TI DICO...", 300, size=100)
label(word_t(0, "ATTIVA"), C1_T0, "ATTIVA", 290, size=110)
label(word_t(0, "DORSALE,"), C1_T0, "IL DORSALE?", 430, box=ORANGE_A, size=110)
SFX.append((0.0, "hit", 0.35))
# nelle trazioni pensa solo una cosa
label(starts[1] + 0.05, seg_end(1), "NELLE TRAZIONI", 240)
label(word_t(1, "PENSA"), seg_end(1), "PENSA SOLO", 350)
label(word_t(1, "UNA"), seg_end(1), "UNA COSA", 465, box=ORANGE_A, size=110)
# tira giù la sbarra (trazione reale) + frecce che scendono
TIRA = word_t(2, "TIRA")
label(TIRA, seg_end(2), "TIRA GIÙ", 290, box=ORANGE_A, size=120, sfx=False)
label(word_t(2, "LA"), seg_end(2), "LA SBARRA", 450, size=100)
SFX += [(TIRA - 0.05, "swoosh", 0.3), (TIRA, "hit", 0.45)]
chev = "m 0 0 l 40 40 l 80 0 l 80 22 l 40 62 l 0 22"
for side_x in (110, 890):
    for k in range(3):
        y = 760 + k * 70
        t0 = TIRA + 0.1 + k * 0.12
        ev.append(f"Dialogue: 4,{ass_t(t0)},{ass_t(seg_end(2))},Shp,,0,0,0,,{{\\an7\\pos({side_x},{y})\\1c{ORANGE_A}"
                  f"\\bord3\\3c{BLACK_A}\\shad0\\alpha&HFF&\\t(0,120,\\alpha&H00&)\\p1}}{chev}")
# quel movimento -> stacco
SFX.append((starts[3], "swoosh", 0.25))
# depressione scapolare: cerchio e dorsale che seguono il corpo (come v1, in rosso sottile)


def ellipse(rx, ry):
    """ellisse con origine in alto a sinistra (0..2rx, 0..2ry): si posiziona con \\an7 a (x-rx, y-ry)."""
    k = 0.552
    pts = [(0, -ry), (k * rx, -ry), (rx, -k * ry), (rx, 0), (rx, k * ry), (k * rx, ry), (0, ry), (-k * rx, ry),
           (-rx, k * ry), (-rx, 0), (-rx, -k * ry), (-k * rx, -ry), (0, -ry)]
    p = [(x + rx, y + ry) for x, y in pts]
    s = f"m {p[0][0]:.0f} {p[0][1]:.0f}"
    for i in range(1, 13, 3):
        s += " b " + " ".join(f"{x:.0f} {y:.0f}" for x, y in p[i:i + 3])
    return s, rx, ry


# spostamento verticale reale della parte alta (tracking del volto, px sorgente) nel tratto della depressione
TRACK = [(0.0, 0), (0.2, -1), (0.3, -4), (0.4, -8), (0.5, -10), (0.7, -12), (0.9, -14), (1.1, -11), (1.3, -8),
         (1.5, -4), (1.7, -1), (1.9, -4), (2.1, -7), (2.3, -12), (2.45, -19)]


def dep_pos(src_t, x, y):
    for (a, da), (b, db) in zip(TRACK, TRACK[1:]):
        if a <= src_t <= b:
            dy = da + (db - da) * (src_t - a) / (b - a)
            break
    else:
        dy = TRACK[-1][1]
    cw, ch = W / DZ, H / DZ
    return (x - (DCX - cw / 2)) * DZ, (y + dy - (DCY - ch / 2)) * DZ


def tracked(t0, t1, x, y, tags, shp, layer=2):
    """evento spezzato in tratti da 0.1 s con \\move che segue il corpo."""
    shape, rx, ry = shp
    b0 = BROLL[2][0]
    tt, first = t0, True
    while tt < t1 - 1e-3:
        te = min(tt + 0.1, t1)
        x0, y0 = dep_pos(min(DEP_SRC[0] + (tt - b0) * DEP_SP, DEP_SRC[1]), x, y)
        x1, y1 = dep_pos(min(DEP_SRC[0] + (te - b0) * DEP_SP, DEP_SRC[1]), x, y)
        tg = tags.replace("|", "") if first else tags.split("|")[0]
        ev.append(f"Dialogue: {layer},{ass_t(tt)},{ass_t(te)},Shp,,0,0,0,,{{\\an7\\move({x0 - rx:.0f},{y0 - ry:.0f},"
                  f"{x1 - rx:.0f},{y1 - ry:.0f}){tg}\\p1}}{shape}")
        first = False
        tt = te


OUT_L = rf"\1a&HFF&\3c{RED}\bord5\shad0\blur0.6"
dep_b0 = BROLL[2][0]
sc_t = word_t(4, "SCAPOLE") - 0.25
dor_t = word_t(5, "DORSALE") - 0.1
tracked(dep_b0 + 0.25, dor_t, 612, 810, OUT_L + r"|\alpha&HFF&\t(0,160,\alpha&H00&\1a&HFF&)", ellipse(105, 105))
tracked(dor_t, seg_end(5), 400, 950, OUT_L + r"|\alpha&HFF&\t(0,160,\alpha&H00&\1a&HFF&)", ellipse(75, 165))
tracked(dor_t, seg_end(5), 400, 950, rf"\1c{RED}\1a&HD8&\bord0\shad0\blur12|\alpha&HFF&\t(0,200,\alpha&H00&\1a&HD8&)",
        ellipse(66, 156), layer=1)
label(sc_t, dor_t, "DEPRESSIONE", 250, box=ORANGE_A, size=84, sfx=False)
label(sc_t + 0.12, dor_t, "SCAPOLARE", 370, size=84, sfx=False)
label(dor_t, seg_end(5), "DORSALE", 250, box=ORANGE_A, size=96, sfx=False)
SFX += [(dep_b0 - 0.05, "swoosh", 0.3), (sc_t, "ding", 0.22), (dor_t, "pop", 0.3)]

# ma capire quello che si sta facendo: trazione completa + etichetta con spunta
CAP = word_t(6, "CAPIRE")
label(CAP, seg_end(6), "CAPIRE", 290, box=ORANGE_A, size=120, sfx=False)
check = "m 0 34 l 22 12 l 46 36 l 98 0 l 118 22 l 46 78"
ev.append(f"Dialogue: 4,{ass_t(CAP + 0.15)},{ass_t(seg_end(6))},Shp,,0,0,0,,{{\\an7\\pos(810,318)\\1c{WHITE_A}"
          f"\\bord4\\3c{BLACK_A}\\shad0\\fscx0\\fscy0\\t(0,120,\\fscx110\\fscy110)\\t(120,180,\\fscx100\\fscy100)\\p1}}{check}")
SFX += [(C2_T1 - 0.02, "swoosh", 0.2), (CAP + 0.15, "ding", 0.22)]

# chiusura: pulsante "SEGUIMI" con cursore che clicca
B0 = starts[7] + 0.1
CLK = B0 + 0.55
ev.append(f"Dialogue: 4,{ass_t(B0)},{ass_t(TOTAL)},Btn,,0,0,0,,{{\\an8\\pos(540,300)\\fscx0\\fscy0"
          f"\\t(0,100,\\fscx112\\fscy112)\\t(100,180,\\fscx100\\fscy100)"
          f"\\t({int((CLK - B0) * 1000)},{int((CLK - B0) * 1000) + 80},\\fscx92\\fscy92)"
          f"\\t({int((CLK - B0) * 1000) + 80},{int((CLK - B0) * 1000) + 180},\\fscx100\\fscy100)}}  SEGUIMI  ")
cursor = "m 0 0 l 0 105 l 27 81 l 45 123 l 63 114 l 45 75 l 81 75"
ev.append(f"Dialogue: 6,{ass_t(B0 + 0.15)},{ass_t(TOTAL)},Shp,,0,0,0,,{{\\an7\\move(800,600,640,370,0,{int((CLK - B0 - 0.15) * 1000)})"
          f"\\1c{WHITE_A}\\bord4\\3c{BLACK_A}\\shad0\\p1}}{cursor}")
SFX += [(B0, "pop", 0.3), (CLK, "click", 0.5)]

ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter Black,56,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,3,12,0,2,80,80,560,1
Style: Lab,Inter Black,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,1,0,0,100,100,0,0,3,16,0,8,40,40,0,1
Style: Shp,Inter Black,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Btn,Inter Black,96,&H00FFFFFF,&H00FFFFFF,&H002C66E8,&H00000000,0,1,0,0,100,100,2,0,3,26,0,8,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n"
open(f"{OUT}/subs.ass", "w").write(ass)

# 5) Effetti sonori: traccia separata da mescolare sotto la voce
SFXD = "/home/user/Video-maker/sfx"
sr = 48000
mix = np.zeros(int((TOTAL + 1) * sr) * 2, np.float32).reshape(-1, 2)
import wave
for t0, nm, vol in SFX:
    with wave.open(f"{SFXD}/{nm}.wav") as wv:
        x = np.frombuffer(wv.readframes(wv.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32767
    i0 = max(int(t0 * sr), 0)
    i1 = min(i0 + len(x), len(mix))
    mix[i0:i1] += x[:i1 - i0] * vol
mix = np.clip(mix, -1, 1)
with wave.open(f"{OUT}/sfx.wav", "wb") as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(sr)
    wv.writeframes((mix * 32767).astype(np.int16).tobytes())

# 6) Composizione
inputs = ["-i", f"{OUT}/aroll.mp4"]
fc, last, k_in = [], "[0:v]", 1
for k, (t0, t1, *_r) in enumerate(BROLL):
    inputs += ["-i", f"{OUT}/b{k}.mp4"]
    fc.append(f"[{k_in}:v]setpts=PTS-STARTPTS+{t0:.4f}/TB[bb{k}]")
    fc.append(f"{last}[bb{k}]overlay=eof_action=pass:enable='between(t,{t0 - 0.004:.4f},{t1 - 0.02:.4f})'[o{k}]")
    last, k_in = f"[o{k}]", k_in + 1
for k, (t0, t1, nm) in enumerate(CARDS):
    inputs += ["-i", f"{OUT}/{nm}.mov"]
    fc.append(f"[{k_in}:v]format=rgba,setpts=PTS-STARTPTS+{t0:.4f}/TB[cc{k}]")
    fc.append(f"{last}[cc{k}]overlay=eof_action=pass:format=auto:enable='between(t,{t0 - 0.004:.4f},{t1 - 0.02:.4f})'[q{k}]")
    last, k_in = f"[q{k}]", k_in + 1
inputs += ["-i", f"{OUT}/sfx.wav"]
fc.append(f"{last}ass={OUT}/subs.ass,format=yuv420p[vf]")
fc.append(f"[0:a]apad[va];[va][{k_in}:a]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[af]")
run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[vf]", "-map", "[af]",
     "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p",
     "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{TOTAL:.3f}",
     f"{OUT}/reel_trazioni_v2.mp4"])
print("TOTAL", round(TOTAL, 2))
