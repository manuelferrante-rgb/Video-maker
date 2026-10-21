#!/usr/bin/env python3
"""Reel "la parte esterna del piede nello squat".
Hook: indico in alto a destra, lì parte un riquadro con lo squat; con la mano lo "trascino" e si apre a tutto schermo.
Poi 3 punti del piede che si accendono (1 tallone, 2 alluce, 3 esterno) con il piede disegnato intorno, il punto 3
si illumina su "parte esterna"; B-roll degli atleti sulle parole, sottotitoli standard, effetti leggeri.
Uso: python3 projects/piede_esterno.py"""
import math, os, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

R = "/home/user/Video-maker"
S = f"{R}/src_piede"
OUT = f"{R}/out/piede"
SFXD = f"{R}/sfx"
os.makedirs(OUT, exist_ok=True)
W, H, FPS, SP = 1080, 1920, 30, 1.1
TALK = f"{S}/parlato_IMG_8364.MOV"
TONEMAP = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
ORANGE, IVORY = (232, 102, 44), (242, 238, 227)
FB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"


def run(cmd):
    subprocess.run(cmd, check=True)


# ---------------- parlato: frasi tenute (sorgente), tutto il resto via ----------------
SEGS = [(7.73, 10.06),    # nessuno ti dice questo sul tuo squat (indico in alto)
        (16.40, 18.80),   # immagina il piede composto da tre punti (+ fine del gesto)
        (24.56, 28.42),   # concentrati su mantenere la pressione sulla parte esterna del piede
        (29.33, 30.46),   # mentre scendi
        (30.74, 36.16),   # pensa di mantenerla, il ginocchio seguirà e tu manterrai una sensazione di spinta ottimale
        (36.50, 40.66),   # è il primo consiglio che do ai miei atleti e subito l'alzata diventa più efficace
        (62.98, 64.18)]   # provaci e fammi sapere (il "link in bio" è tolto)
lst, SO, t = [], [], 0.0
for i, (a, b) in enumerate(SEGS):
    d = b - a
    nfr = round(d / SP * FPS)
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-t", f"{d + 0.1}", "-i", TALK,
         "-vf", f"setpts=PTS/{SP},fps={FPS},scale={W}:{H},setsar=1",
         "-af", f"atempo={SP},afade=t=in:d=0.02,afade=t=out:st={d / SP - 0.04:.3f}:d=0.04,apad",
         "-frames:v", str(nfr), "-t", f"{nfr / FPS:.4f}", "-c:v", "libx264", "-crf", "15", "-preset", "fast",
         "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", f"{OUT}/t{i}.mov"])
    lst.append(f"file '{OUT}/t{i}.mov'")
    SO.append(t)
    t += nfr / FPS
TOTAL = t
open(f"{OUT}/talk.txt", "w").write("\n".join(lst) + "\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/talk.txt", "-c:v", "copy",
     "-af", "highpass=f=80,loudnorm=I=-14:TP=-1.5:LRA=9", "-c:a", "pcm_s16le", "-ar", "48000", f"{OUT}/talk.mov"])


def ot(src):
    """tempo sorgente del parlato -> tempo nel reel."""
    for (a, b), s0 in zip(SEGS, SO):
        if a - 0.2 <= src <= b + 0.05:
            return s0 + max(src - a, 0) / SP
    raise ValueError(src)


def w(src):  # tempi parola del modello (+0.08)
    return ot(src + 0.08)


# ---------------- B-roll: (inizio nel reel, fine, file, inizio sorgente, velocità, zoom, centro zoom) ----------------
HOOK_END = 2.6
B = [  # ogni atleta compare una volta sola
    (SO[3], w(32.29), "b_-5241644845136615582", 0.05, 1.0, 1.0, None),    # mentre scendi, pensa di mantenerla
    (w(32.29), w(33.49), "b_IMG_5440_c", 0.45, 1.0, 1.35, (480, 1560)),   # il ginocchio seguirà: ginocchia e piedi
    (SO[5], SO[5] + 0.40, "b_IMG_5440_a", 0.0, 1.0, 1.0, None),          # è il primo consiglio: io che mi sistemo
    (SO[5] + 0.40, w(37.25), "b_IMG_5440_b", 0.3, 1.0, 1.0, None),        #   (seconda inquadratura, stacco veloce)
    (w(37.25), w(38.29), "b_6066581454588218446", 0.6, 1.1, 1.0, None),   # che do ai miei atleti
    (w(38.29), w(38.29) + 0.72, "b_152768267402597092", 0.9, 1.1, 1.0, None),  # e subito: altri atleti, bam bam
    (w(38.29) + 0.72, w(39.89), "b_-5241644845136615582", 1.65, 1.15, 1.0, None),
]
KNEE = B[1]


def snap(x):
    return round(x * FPS) / FPS


def render_clip(src, ss, dur, sp, z, c, out):
    nfr = round(dur * FPS)
    hdr = "5440" in src
    pre = (TONEMAP + ",") if hdr else ""
    zf = ""
    if z != 1.0:
        cx, cy = c
        zf = f",crop={W / z:.0f}:{H / z:.0f}:{cx - W / z / 2:.0f}:{cy - H / z / 2:.0f},scale={W}:{H}:flags=lanczos"
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss}", "-t", f"{dur * sp + 0.2}", "-i", f"{S}/{src}.mov",
         "-vf", f"{pre}setpts=PTS/{sp},fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
                f"crop={W}:{H}{zf},setsar=1,tpad=stop_mode=clone:stop_duration=1",
         "-an", "-frames:v", str(nfr), "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
         out])


BR = []
for i, (t0, t1, src, ss, sp, z, c) in enumerate(B):
    t0, t1 = snap(t0), snap(t1)
    render_clip(src, ss, t1 - t0 + 0.1, sp, z, c, f"{OUT}/br{i}.mp4")  # qualche fotogramma in più: niente buchi agli stacchi
    BR.append((t0, t1, f"{OUT}/br{i}.mp4"))

# clip dell'hook: atleta fermo col bilanciere, poi scende (2.6 s)
render_clip("b_IMG_5440_b", 0.0, 1.0, 1.0, 1.0, None, f"{OUT}/h0.mp4")
render_clip("b_IMG_5440_c", 0.0, 1.6, 1.0, 1.0, None, f"{OUT}/h1.mp4")
open(f"{OUT}/hook.txt", "w").write(f"file '{OUT}/h0.mp4'\nfile '{OUT}/h1.mp4'\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/hook.txt", "-c", "copy",
     f"{OUT}/hookclip.mp4"])


def frames(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def writer(path):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", path],
                            stdin=subprocess.PIPE)


# ---------------- hook: riquadro che parte dal dito e si apre seguendo la mano ----------------
T_POP, T_EXP0, T_EXP1 = 0.0, ot(9.22), ot(9.58)
C0, CW0 = (235, 470), 290                       # riquadro vicino al dito (in alto, alla mia destra)
HAND = (470, 1060)                               # dove passa la mano che spinge
HF = frames(f"{OUT}/hookclip.mp4")
p = writer(f"{OUT}/card.mov")
for k in range(round(HOOK_END * FPS)):
    tt = k / FPS
    fr = Image.fromarray(HF[min(k, len(HF) - 1)])
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    e = ease((tt - T_EXP0) / (T_EXP1 - T_EXP0))
    if e >= 1:
        im = fr.convert("RGBA")
    else:
        pop = ease((tt - T_POP) / 0.18)
        s = (0.6 + 0.4 * pop) if e == 0 else 1.0
        # centro su una curva (dito -> mano -> centro), larghezza da riquadro a schermo intero
        bx = (1 - e) ** 2 * C0[0] + 2 * (1 - e) * e * HAND[0] + e * e * W / 2
        by = (1 - e) ** 2 * C0[1] + 2 * (1 - e) * e * HAND[1] + e * e * H / 2
        cw = (CW0 + (W - CW0) * e ** 1.3) * s
        ch = cw * H / W
        rad = int(30 * (1 - e) + 2)
        card = fr.resize((max(int(cw), 2), max(int(ch), 2)), Image.LANCZOS).convert("RGBA")
        m = Image.new("L", card.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, card.width - 1, card.height - 1], radius=rad, fill=255)
        x0, y0 = int(bx - card.width / 2), int(by - card.height / 2)
        sh = Image.new("RGBA", (card.width + 80, card.height + 80), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([40, 48, card.width + 40, card.height + 48], radius=rad,
                                             fill=(0, 0, 0, int(140 * pop * (1 - e))))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)), (x0 - 40, y0 - 40))
        a = int(255 * min(pop * 1.6, 1))
        card.putalpha(m.point(lambda v: v * a // 255))
        im.alpha_composite(card, (x0, y0))
        if e < 0.9:
            ImageDraw.Draw(im).rounded_rectangle([x0, y0, x0 + card.width, y0 + card.height], radius=rad,
                                                 outline=IVORY + (int(a * (1 - e)),), width=6)
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait()

# ---------------- grafiche: piede con i 3 punti, glow sui piedi nel B-roll delle ginocchia ----------------
FX0, FY0, FWd, FHt = 60, 270, 390, 720          # riquadro del piede (in alto a sinistra, dove indico)


def fp(x, y):
    return FX0 + x * FWd, FY0 + y * FHt


SOLE = [(0.5, 1.0), (0.70, 0.94), (0.71, 0.78), (0.64, 0.62), (0.80, 0.42), (0.87, 0.26), (0.79, 0.18),
        (0.56, 0.16), (0.36, 0.19), (0.21, 0.26), (0.15, 0.38), (0.19, 0.58), (0.26, 0.80), (0.33, 0.95)]
TOES = [((0.78, 0.075), 0.085), ((0.60, 0.075), 0.06), ((0.47, 0.095), 0.052), ((0.355, 0.125), 0.047),
        ((0.255, 0.175), 0.042)]
LATERAL = [(0.21, 0.26), (0.15, 0.38), (0.19, 0.58), (0.26, 0.80), (0.33, 0.95)]
PTS = [((0.50, 0.86), "TALLONE"), ((0.74, 0.30), "ALLUCE"), ((0.25, 0.40), "ESTERNO")]


def catmull(pts, closed=True, n=16):
    out = []
    P = pts + pts[:3] if closed else [pts[0]] + pts + [pts[-1]]
    for i in range(len(P) - 3):
        p0, p1, p2, p3 = P[i:i + 4]
        for k in range(n):
            u = k / n
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * u + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * u * u
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * u ** 3) for j in (0, 1)))
    return out


SOLE_P = [fp(*q) for q in catmull(SOLE)]
LAT_P = [fp(*q) for q in catmull(LATERAL, closed=False)]
T_P = [ot(18.04), ot(18.45), ot(18.68)]          # quando il dito si ferma sui punti
T_DRAW0, T_DRAW1 = ot(18.72), ot(18.72) + 0.5    # piede che si disegna intorno
T_EXT = w(26.91)                                  # "parte esterna": si illumina il bordo esterno
T_FOOT_END = SO[3]
fl = ImageFont.truetype(FB, 34)
fn = ImageFont.truetype(FB, 38)


def glow_dot(d, x, y, r, col, a=255):
    for k in range(6, 0, -1):
        rr = r + k * 7
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col + (int(a * 0.07),))
    d.ellipse([x - r, y - r, x + r, y + r], fill=col + (a,), outline=(255, 255, 255, a), width=4)


def outlined(d, xy, txt, font, fill=(255, 255, 255, 255), anchor="mm", a=255):
    d.text(xy, txt, font=font, fill=fill[:3] + (a,), anchor=anchor, stroke_width=5, stroke_fill=(0, 0, 0, a))


def foot_layer(tt):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fade = 1 - ease((tt - (T_FOOT_END - 0.25)) / 0.25)
    if fade <= 0:
        return im
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    dr = ease((tt - T_DRAW0) / (T_DRAW1 - T_DRAW0))
    if dr > 0:  # sagoma che si traccia + dita
        n = max(int(len(SOLE_P) * dr), 2)
        d.polygon(SOLE_P, fill=(20, 48, 79, int(150 * dr)))
        d.line(SOLE_P[:n] + ([SOLE_P[0]] if dr >= 1 else []), fill=(255, 255, 255, 255), width=9, joint="curve")
        for (cx, cy), r in TOES:
            x, y = fp(cx, cy)
            rr = r * FWd * dr
            d.ellipse([x - rr, y - rr * 1.15, x + rr, y + rr * 1.15], fill=(20, 48, 79, int(150 * dr)),
                      outline=(255, 255, 255, int(255 * dr)), width=6)
    ex = ease((tt - T_EXT) / 0.35)
    if ex > 0:  # bordo esterno in arancio che pulsa
        puls = 0.75 + 0.25 * math.sin((tt - T_EXT) * 9)
        for wd, al in ((40, 50), (26, 90), (12, 255)):
            d.line(LAT_P, fill=ORANGE + (int(al * ex * puls),), width=wd, joint="curve")
    for k, ((px, py), name) in enumerate(PTS):
        tp = T_P[k]
        if tt < tp:
            continue
        x, y = fp(px, py)
        e = ease((tt - tp) / 0.12)
        bounce = 1 + 0.35 * math.sin(min((tt - tp) / 0.25, 1) * math.pi)
        dim = 0.45 if (ex > 0 and k < 2) else 1.0
        col = ORANGE if (k == 2 and ex > 0) else (255, 255, 255)
        r = 30 * e * bounce * (1.25 if (k == 2 and ex > 0) else 1)
        glow_dot(d, x, y, r, col, int(255 * dim))
        if e > 0.6:  # numero pieno, senza bordo (leggibile dentro il pallino)
            d.text((x, y + 1), str(k + 1), font=fn, anchor="mm",
                   fill=((20, 48, 79) if col == (255, 255, 255) else (255, 255, 255)) + (int(255 * dim),))
        lx, ly = x, y + 62
        outlined(d, (lx, ly), name, fl, fill=(ORANGE + (255,)) if (k == 2 and ex > 0) else (255, 255, 255, 255),
                 a=int(255 * dim * e))
    if fade < 1:
        g.putalpha(g.split()[3].point(lambda v: int(v * fade)))
    im.alpha_composite(g)
    return im


# B-roll ginocchia: i piedi (zoom 1.35 su 480,1420) con il bordo esterno che si accende
K0, K1 = snap(KNEE[0]), snap(KNEE[1])
FEET = [(245, 1570), (800, 1570)]  # bordo esterno delle scarpe nello zoom (il crop resta in basso)


def knee_layer(tt):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if not (K0 <= tt < K1):
        return im
    d = ImageDraw.Draw(im)
    e = ease((tt - K0 - 0.15) / 0.2)
    puls = 0.8 + 0.2 * math.sin((tt - K0) * 10)
    for (x, y), side in zip(FEET, (-1, 1)):
        for k in range(5, 0, -1):
            rr = (22 + k * 10) * e
            d.ellipse([x - rr, y - rr * 1.6, x + rr, y + rr * 1.6], fill=ORANGE + (int(45 * puls),))
    return im


T_SP0, T_SP1 = snap(w(34.53)), snap(SO[5])   # "sensazione di spinta ottimale"
SP_P = [(290 + x * 500, 330 + y * 930) for x, y in catmull(SOLE)]
SP_LAT = [(290 + x * 500, 330 + y * 930) for x, y in catmull(LATERAL, closed=False)]


def spinta_layer(tt):
    im = Image.new("RGBA", (W, H), (20, 48, 79, 255))
    d = ImageDraw.Draw(im)
    e = ease((tt - T_SP0) / 0.25)
    d.polygon(SP_P, fill=(10, 26, 44, 255))
    d.line(SP_P + [SP_P[0]], fill=(255, 255, 255, 255), width=10, joint="curve")
    for (cx, cy), r in TOES:
        x, y = 290 + cx * 500, 330 + cy * 930
        rr = r * 500
        d.ellipse([x - rr, y - rr * 1.15, x + rr, y + rr * 1.15], fill=(10, 26, 44, 255), outline=(255, 255, 255, 255),
                  width=8)
    puls = 0.75 + 0.25 * math.sin((tt - T_SP0) * 9)
    for wd, al in ((60, 50), (36, 100), (16, 255)):
        d.line(SP_LAT, fill=ORANGE + (int(al * e * puls),), width=wd, joint="curve")
    for k in range(3):  # frecce di spinta che salgono
        ph = ((tt - T_SP0) * 1.6 + k / 3) % 1
        y = 1180 - ph * 520
        a = int(255 * e * math.sin(ph * math.pi))
        d.line([(160, y + 70), (230, y), (300, y + 70)], fill=ORANGE + (a,), width=16, joint="curve")
    return im


p = writer(f"{OUT}/gfx.mov")
for k in range(round(TOTAL * FPS)):
    tt = k / FPS
    im = foot_layer(tt) if T_P[0] - 0.05 <= tt < T_FOOT_END else Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im.alpha_composite(knee_layer(tt))
    if T_SP0 <= tt < T_SP1:
        im = spinta_layer(tt)
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait()

# ---------------- sottotitoli (standard: bianchi, bordo nero, niente riquadro, y 1450) ----------------


def ass_t(x):
    x = max(x, 0)
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


OR = "{\\c&H2C66E8&}"
WH = "{\\c&HFFFFFF&}"
PAGES = [
    (0.0, w(16.35), "NESSUNO TI DICE QUESTO\\NSUL TUO SQUAT"),
    (w(16.35), w(24.51), "IMMAGINA IL PIEDE\\NCOMPOSTO DA 3 PUNTI"),
    (w(24.51), w(26.43), "CONCENTRATI SU MANTENERE\\NLA PRESSIONE"),
    (w(26.43), SO[3], f"SULLA PARTE {OR}ESTERNA{WH}\\NDEL PIEDE"),
    (SO[3], w(32.13), "MENTRE SCENDI,\\NPENSA DI MANTENERLA"),
    (w(32.13), w(33.49), "IL GINOCCHIO SEGUIRÀ"),
    (w(33.49), w(34.37), "E TU MANTERRAI"),
    (w(34.37), SO[5], "UNA SENSAZIONE\\NDI SPINTA OTTIMALE"),
    (SO[5], w(38.29), "È IL PRIMO CONSIGLIO\\NCHE DO AI MIEI ATLETI"),
    (w(38.29), SO[6], "E SUBITO L'ALZATA\\NDIVENTA PIÙ EFFICACE"),
    (SO[6], TOTAL, "PROVACI E\\NFAMMI SAPERE"),
]
POP = "\\fscx85\\fscy85\\t(0,110,\\fscx104\\fscy104)\\t(110,190,\\fscx100\\fscy100)"
ev = [f"Dialogue: 1,{ass_t(a)},{ass_t(b)},Txt,,0,0,0,,{{\\an5\\pos(540,1450){POP}}}{txt}" for a, b, txt in PAGES]
open(f"{OUT}/subs.ass", "w").write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Txt,Inter ExtraBold,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,7,3,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n")

# ---------------- effetti sonori ----------------
sr = 48000


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


mix = np.zeros((int((TOTAL + 1) * sr), 2), np.float32)
SFX = [(0.0, "comparsa", 0.22), (T_EXP1 - 0.53, "trascina", 0.32),  # più leggeri sul riquadro
       (T_P[0], "punto_1", 0.45), (T_P[1], "punto_2", 0.45), (T_P[2], "punto_3", 0.45), (T_DRAW0, "disegno", 0.4),
       (T_EXT, "punto_3", 0.35)]
SFX += [(t0 - 0.06, "swoosh", 0.06) for t0, _, _ in BR if t0 > 1]  # fruscio appena accennato
SFX += [(T_SP0, "punto_3", 0.25)]
for t0, nm, vol in SFX:
    x = load(f"{SFXD}/{nm}.wav")
    i0 = max(int(t0 * sr), 0)
    i1 = min(i0 + len(x), len(mix))
    mix[i0:i1] += x[:i1 - i0] * vol
with wave.open(f"{OUT}/sfx.wav", "wb") as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(sr)
    wv.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())

# ---------------- montaggio finale ----------------
inp = ["-i", f"{OUT}/talk.mov", "-i", f"{OUT}/sfx.wav", "-i", f"{OUT}/card.mov", "-i", f"{OUT}/gfx.mov"]
fc = ["[0:v]setpts=PTS-STARTPTS[v0]"]
last = "v0"
for i, (t0, t1, path) in enumerate(BR):
    inp += ["-i", path]
    fc.append(f"[{4 + i}:v]setpts=PTS-STARTPTS+{t0 - 0.02:.4f}/TB[b{i}]")  # leggero anticipo: niente fotogrammi scoperti
    fc.append(f"[{last}][b{i}]overlay=eof_action=pass:enable='between(t,{t0 - 0.01:.4f},{t1 - 0.01:.4f})'[o{i}]")
    last = f"o{i}"
fc.append(f"[2:v]setpts=PTS-STARTPTS[cd];[{last}][cd]overlay=eof_action=pass[oc]")
fc.append(f"[3:v]setpts=PTS-STARTPTS[gx];[oc][gx]overlay=eof_action=pass,ass={OUT}/subs.ass,format=yuv420p[v]")
fc.append("[0:a][1:a]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]")
run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
     "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", "-t", f"{TOTAL:.3f}", f"{OUT}/reel_piede_esterno.mp4"])
print("TOTAL", round(TOTAL, 2), "segmenti", [round(x, 2) for x in SO], "punti", [round(x, 2) for x in T_P],
      "espansione", round(T_EXP0, 2), round(T_EXP1, 2), "B-roll", [(round(a, 2), round(b, 2)) for a, b, _ in BR])
