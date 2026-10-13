#!/usr/bin/env python3
"""Reel trazioni: "attivare il dorsale" = tira giù la sbarra / depressione scapolare.
Colore: parlato non toccato, clip HDR solo convertite in SDR (nessun look)."""
import math, os, subprocess

SRC = "/home/user/Video-maker/src_traz"
OUT = "/home/user/Video-maker/out/trazioni"
os.makedirs(OUT, exist_ok=True)
W, H, FPS, SPEED = 1080, 1920, 30, 1.05
P = f"{SRC}/parlato.MOV"

# voce (sorgente): inizio, fine, zoom A-roll, parole (tempi modello)
SEGS = [
    (0.00, 3.02, 1.12, [("SE", 0.0), ("TI", 0.16), ("DICO", 0.24), ("|ATTIVA", 0.56), ("IL", 0.96), ("DORSALE,", 1.04),
                        ("|NON", 1.52), ("TI", 1.68), ("STO", 1.76), ("SPIEGANDO", 2.0), ("NIENTE.", 2.48)]),
    (9.02, 10.88, 1.00, [("NELLE", 8.93), ("TRAZIONI,", 9.25), ("|PENSA", 9.73), ("SOLO", 10.05), ("|UNA", 10.29),
                         ("COSA.", 10.45)]),
    (10.98, 12.15, 1.12, [("TIRA", 10.95), ("GIÙ", 11.25), ("|LA", 11.49), ("SBARRA.", 11.65)]),
    (24.50, 25.75, 1.00, [("QUEL", 24.42), ("MOVIMENTO", 24.82)]),
    (25.98, 27.53, 1.00, [("ABBASSA", 25.89), ("LE", 26.61), ("SCAPOLE", 26.85)]),
    (27.70, 29.45, 1.00, [("ED", 27.6), ("È", 27.81), ("LÌ", 27.97), ("CHE", 28.13), ("|IL", 28.29), ("DORSALE", 28.37),
                          ("LAVORA.", 29.01)]),
    (49.42, 53.25, 1.12, [("NON", 49.35), ("SERVONO", 49.59), ("|MILLE", 50.07), ("TECNICISMI,", 50.39), ("|MA", 51.11),
                          ("CAPIRE", 51.35), ("|QUELLO", 51.83), ("CHE", 52.15), ("|SI", 52.31), ("STA", 52.47),
                          ("FACENDO.", 52.71)]),
    (55.50, 56.62, 1.00, [("SPERO", 55.42), ("TI", 55.82), ("|SIA", 55.9), ("UTILE.", 56.14)]),
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
         f"scale={W}:{H},crop={cw}:{ch}:(iw-{cw})/2:(ih-{ch})*0.1,scale={W}:{H}:flags=lanczos,setsar=1,fps={FPS}",
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


# 3) Sottotitoli + grafiche
def ass_t(x):
    x = max(x, 0)
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


pages = []
for i, seg in enumerate(SEGS):
    cur = []
    for txt, tt in seg[3]:
        brk = txt.startswith("|")
        txt = txt.lstrip("|")
        if cur and (brk or (len(cur) == 4 and tuple(w for w, *_ in cur) not in {p[:4] for p in BIG_PAGES})):
            pages.append(cur)
            cur = []
        cur.append((txt, max(out_t(i, tt + 0.08), starts[i]), i))
    pages.append(cur)

YELLOW, RED, WHITE = "&H0033D1FF&", "&H002E2EE6&", "&H00FFFFFF&"
ev = []
for j, pg in enumerate(pages):
    st, seg = pg[0][1], pg[0][2]
    en = pages[j + 1][0][1] if j + 1 < len(pages) and pages[j + 1][0][2] == seg else seg_end(seg)
    if j + 1 == len(pages):
        en = TOTAL
    ws = tuple(w for w, *_ in pg)
    clean = [w.rstrip(",.?") for w in ws]
    if ws in BIG_PAGES:
        if len(clean) > 3:
            clean[2] += "\\N"
        txt = " ".join(clean)
        pop = r"{\fs112\bord7\fscx85\fscy85\t(0,140,\fscx100\fscy100)}"
        ev.append(f"Dialogue: 0,{ass_t(st)},{ass_t(en)},Main,,0,0,0,,{pop}{{\\c{YELLOW}}}{txt}")
        continue
    words = [f"{{\\c{YELLOW if w in KEY else WHITE}}}{c}" for w, c in zip(ws, clean)]
    if len(" ".join(clean)) > 17 and len(words) == 3:
        words[1] += "\\N"
    pop = r"{\fscx108\fscy108\t(0,100,\fscx100\fscy100)}"
    ev.append(f"Dialogue: 0,{ass_t(st)},{ass_t(en)},Main,,0,0,0,,{pop}{' '.join(words)}")


def ellipse(rx, ry):
    """ellisse con origine in alto a sinistra (0..2rx, 0..2ry): si posiziona con \\an7 a (x-rx, y-ry)."""
    kx, ky = rx * 0.552, ry * 0.552
    pts = (f"m 0 {-ry} b {kx:.0f} {-ry} {rx} {-ky:.0f} {rx} 0 b {rx} {ky:.0f} {kx:.0f} {ry} 0 {ry} "
            f"b {-kx:.0f} {ry} {-rx} {ky:.0f} {-rx} 0 b {-rx} {-ky:.0f} {-kx:.0f} {-ry} 0 {-ry}")
    out = []
    for tok in pts.split():
        out.append(tok)
    # trasla tutti i punti di (+rx, +ry)
    res, nums = [], []
    for tok in pts.split():
        if tok in "mbl":
            res.append(tok)
        else:
            nums.append(tok)
            res.append(None)
    vals = [float(v) for v in nums]
    k = 0
    final = []
    for tok in res:
        if tok is None:
            v = vals[k] + (rx if k % 2 == 0 else ry)
            final.append(f"{v:.0f}")
            k += 1
        else:
            final.append(tok)
    return " ".join(final), rx, ry


# spostamento verticale reale della parte alta (tracking del volto, px sorgente) nel tratto della depressione
TRACK = [(0.0, 0), (0.2, -1), (0.3, -4), (0.4, -8), (0.5, -10), (0.7, -12), (0.9, -14), (1.1, -11), (1.3, -8),
         (1.5, -4), (1.7, -1), (1.9, -4), (2.1, -7), (2.3, -12), (2.45, -19)]


def dep_pos(src_t, x, y):
    """punto sorgente (x,y) -> coordinate di uscita dentro lo zoom, seguendo il movimento."""
    for (a, da), (b, db) in zip(TRACK, TRACK[1:]):
        if a <= src_t <= b:
            dy = da + (db - da) * (src_t - a) / (b - a)
            break
    else:
        dy = TRACK[-1][1]
    cw, ch = W / DZ, H / DZ
    return (x - (DCX - cw / 2)) * DZ, (y + dy - (DCY - ch / 2)) * DZ


def tracked(t0, t1, x, y, tags, shp, layer=2):
    shape, rx, ry = shp
    """evento spezzato in tratti da 0.1 s con \\move che segue il corpo."""
    b0 = BROLL[2][0]
    step = 0.1
    tt = t0
    first = True
    while tt < t1 - 1e-3:
        te = min(tt + step, t1)
        s0 = DEP_SRC[0] + (tt - b0) * DEP_SP
        s1 = DEP_SRC[0] + (te - b0) * DEP_SP
        x0, y0 = dep_pos(min(s0, DEP_SRC[1]), x, y)
        x1, y1 = dep_pos(min(s1, DEP_SRC[1]), x, y)
        fade = tags if first else tags.split("|")[0]
        ev.append(f"Dialogue: {layer},{ass_t(tt)},{ass_t(te)},Main,,0,0,0,,{{\\an7\\move({x0 - rx:.0f},{y0 - ry:.0f},{x1 - rx:.0f},{y1 - ry:.0f})"
                  f"{fade.replace('|', '')}\\p1}}{shape}")
        first = False
        tt = te


OUT_L = rf"\1a&HFF&\3c{RED}\bord5\shad0\blur0.6"
dep_b0 = BROLL[2][0]
sc_t = word_t(4, "SCAPOLE") - 0.25
dor_t = word_t(5, "DORSALE") - 0.1
# scapole/spalla: cerchio rosso che segue la spalla mentre scende e sale
tracked(dep_b0 + 0.25, dor_t, 612, 810, OUT_L + r"|\alpha&HFF&\t(0,160,\alpha&H00&\1a&HFF&)", ellipse(105, 105))
# dorsale: ellisse allungata sul fianco sotto l'ascella + leggerissima velatura
tracked(dor_t, seg_end(5), 400, 950, OUT_L + r"|\alpha&HFF&\t(0,160,\alpha&H00&\1a&HFF&)", ellipse(75, 165))
tracked(dor_t, seg_end(5), 400, 950, rf"\1c{RED}\1a&HD8&\bord0\shad0\blur12|\alpha&HFF&\t(0,200,\alpha&H00&\1a&HD8&)",
        ellipse(66, 156), layer=1)

# etichetta tecnica in alto (zona sicura), non copre il movimento
lab_t = sc_t
for t0_, t1_, txt in ((lab_t, dor_t, "DEPRESSIONE SCAPOLARE"), (dor_t, seg_end(5), "DORSALE")):
    ev.append(f"Dialogue: 3,{ass_t(t0_)},{ass_t(t1_)},Label,,0,0,0,,{{\\fad(120,0)}}{txt}")

ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Inter Black,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,0,0,1,6,3,2,80,80,470,1
Style: Label,Inter Black,62,&H00FFFFFF,&H00FFFFFF,&H302E2EE6,&H00000000,0,0,0,0,100,100,2,0,3,18,0,8,80,80,310,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n"
open(f"{OUT}/subs.ass", "w").write(ass)

# 4) Composizione
inputs = ["-i", f"{OUT}/aroll.mp4"]
fc, last = [], "[0:v]"
for k, (t0, t1, *_r) in enumerate(BROLL):
    inputs += ["-i", f"{OUT}/b{k}.mp4"]
    fc.append(f"[{k + 1}:v]setpts=PTS-STARTPTS+{t0:.4f}/TB[bb{k}]")
    fc.append(f"{last}[bb{k}]overlay=eof_action=pass:enable='between(t,{t0 - 0.004:.4f},{t1 - 0.02:.4f})'[o{k}]")
    last = f"[o{k}]"
fc.append(f"{last}ass={OUT}/subs.ass,format=yuv420p[vf]")
run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[vf]", "-map", "0:a",
     "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p",
     "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{TOTAL:.3f}",
     f"{OUT}/reel_trazioni_dorsale.mp4"])
print("TOTAL", round(TOTAL, 2))
for k, b in enumerate(BROLL):
    print("broll", k, b[2], round(b[0], 2), round(b[1], 2))
for p in pages:
    print(round(p[0][1], 2), " ".join(w for w, *_ in p))
