#!/usr/bin/env python3
"""Reel squat/presa v2: hook col video dello squat, analisi gomiti con freeze e cerchio,
presa evidenziata, colore uniformato, sottotitoli grandi ad alto contrasto."""
import os, subprocess

SRC = "/home/user/Video-maker/src_squat"
OUT = "/home/user/Video-maker/out/squat2"
os.makedirs(OUT, exist_ok=True)
W, H, FPS, SPEED = 1080, 1920, 30, 1.1
P = f"{SRC}/Squat_parlato.MOV"

# voce (sorgente): inizio, fine, zoom A-roll, parole (tempi modello)
SEGS = [
    (1.00, 2.28, 1.00, [("LO", 1.0), ("SQUAT", 1.2), ("|NON", 1.7), ("GIRA?", 1.86)]),
    (3.97, 5.00, 1.10, [("GUARDA", 4.0), ("I", 4.44), ("GOMITI.", 4.52)]),
    (13.90, 16.75, 1.00, [("LA", 13.92), ("LARGHEZZA", 14.12), ("|DELLA", 14.6), ("PRESA", 14.92), ("|DECIDE", 15.48),
                          ("DOVE", 15.96), ("FINISCONO.", 16.2)]),
    (34.55, 38.40, 1.00, [("UNA", 34.6), ("PRESA", 34.8), ("|PIÙ", 35.28), ("STRETTA", 35.44), ("|RENDE", 36.08),
                          ("PIÙ", 36.48), ("COMPATTA", 36.64), ("|LA", 37.12), ("SCHIENA", 37.2), ("|SOTTO", 37.44),
                          ("IL", 37.76), ("BILANCIERE.", 37.84)]),
    (42.25, 43.95, 1.18, [("MA", 42.3), ("SERVE", 42.42), ("|MOBILITÀ", 42.9), ("DI", 43.3), ("SPALLA.", 43.46)]),
    (53.80, 56.35, 1.00, [("SE", 53.82), ("TI", 54.0), ("IRRIGIDISCE", 54.16), ("|E", 54.88), ("TI", 54.96), ("DÀ", 55.04),
                          ("FASTIDIO,", 55.2), ("|ALLARGALA.", 55.68)]),
    (62.48, 67.00, 1.08, [("LA", 62.5), ("PRESA", 62.7), ("GIUSTA", 63.1), ("|È", 63.42), ("QUELLA", 63.5), ("CHE", 63.74),
                          ("|TIENE", 63.9), ("IL", 64.3), ("|BILANCIERE", 64.38), ("SALDO", 65.1),
                          ("|SENZA", 65.74), ("TENSIONI", 66.14), ("INUTILI.", 66.54)]),
]
KEY = {"SQUAT", "LARGHEZZA", "PRESA", "STRETTA", "COMPATTA", "MOBILITÀ", "SPALLA.", "ALLARGALA.", "GIUSTA",
       "SALDO", "TENSIONI"}
BIG = {1}  # segmento "GUARDA I GOMITI": tutto evidenziato e più grande

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
            return out_t(seg, tt + 0.08)
    raise KeyError(w)


def seg_end(i):
    return starts[i] + (SEGS[i][1] - SEGS[i][0]) / SPEED


# Colore: correzioni leggere e uguali per tutti (alte luci recuperate, niente look "HDR")
# neutro: niente curve né desaturazione (la v2 con le alte luci compresse sembrava opaca)
GRADE_AROLL = "colorbalance=rm=-0.015:gm=0.01:rh=-0.01"
TONEMAP = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
GRADE_GYM = "colorbalance=rm=-0.02:rh=-0.01"
GRADE_ELIA = "eq=brightness=0.03:saturation=0.88,colorbalance=rs=0.04:bs=-0.06:rm=0.03:bm=-0.05"


def run(cmd):
    subprocess.run(cmd, check=True)


# 1) A-roll
lst = []
for i, (s, e, z, _) in enumerate(SEGS):
    cw, ch = int(W / z) // 2 * 2, int(H / z) // 2 * 2
    d = e - s
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.3f}", "-i", P, "-t", f"{d:.3f}", "-vf",
         f"scale={W}:{H},crop={cw}:{ch}:(iw-{cw})/2:(ih-{ch})*0.25,scale={W}:{H}:flags=lanczos,{GRADE_AROLL},"
         f"setsar=1,fps={FPS}",
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
# Elia: gomiti alti. Movimento reale rallentato (0.8x) solo nel tratto fermo, poi fermo immagine per l'analisi.
EL_T0, EL_T1 = starts[2], seg_end(2)
# Mani sulla presa, poi entrata sotto il bilanciere
HA_T0, HA_T1 = starts[3], word_t(3, "RENDE")
BI_T0, BI_T1 = HA_T1, seg_end(3)
FR_T0, FR_T1 = word_t(6, "TIENE"), word_t(6, "SENZA")
BROLL = [  # inizio, fine, file, inizio sorgente, velocità, filtro extra
    (0.0, seg_end(0), "ultimarep.mov", 0.35, 1.0, None),
    (EL_T0, EL_T1, "GomitialtiElia.mov", 0.0, 0.8, "elia"),
    (HA_T0, HA_T1, "Sistemazionepresamani.mov", 0.45, 1.0, None),
    (BI_T0, BI_T1, "Sistemazionebilanciere.mov", 0.0, 0.85, None),
    (FR_T0, FR_T1, "Squatfrontale.mov", 0.0, 1.0, None),
]
EL_PLAY = 1.30  # secondi sorgente in cui Elia è fermo prima di uscire dal rack
EL_ZOOM, EL_CX, EL_CY = 1.25, 560, 820  # zoom finale e centro (coord. 1080x1920): gomito + bilanciere in quadro
EL_ZOOM_FR = 15  # frame di zoom in (0.5 s), poi inquadratura ferma


def is_hlg(f):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer",
                        "-of", "csv=p=0", f], capture_output=True, text=True).stdout
    return "arib-std-b67" in o


for k, (t0, t1, f, ss, sp, extra) in enumerate(BROLL):
    nfr = int(round((t1 - t0) * FPS))
    vf = []
    if extra == "elia":
        play = EL_PLAY / sp
        z = f"min(1+({EL_ZOOM}-1)*(1-pow(1-on/{EL_ZOOM_FR},3)),{EL_ZOOM})"
        p = f"(zoom-1)/({EL_ZOOM}-1)"
        vf += [GRADE_ELIA, f"trim=0:{EL_PLAY}", f"setpts=PTS/{sp}", f"fps={FPS}",
               f"tpad=stop_mode=clone:stop_duration={max(t1 - t0 - play, 0) + 0.2:.3f}",
               f"scale={W}:-2:flags=lanczos", f"crop={W}:{H}", "hqdn3d=1.5:1.5:3:3", "unsharp=5:5:0.3",
               f"scale={W * 2}:{H * 2}:flags=lanczos",
               f"zoompan=z='{z}':x='2*(540+({EL_CX}-540)*{p})-iw/zoom/2':y='2*(960+({EL_CY}-960)*{p})-ih/zoom/2'"
               f":d=1:s={W}x{H}:fps={FPS}"]
    else:
        if is_hlg(f"{SRC}/{f}"):
            vf.append(TONEMAP)
        vf += [GRADE_GYM, f"setpts=PTS/{sp}", f"fps={FPS}",
               f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos", f"crop={W}:{H}",
               f"tpad=stop_mode=clone:stop_duration=1"]
    vf += ["setsar=1", "format=yuv420p"]
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", f"{SRC}/{f}", "-vf", ",".join(vf), "-frames:v",
         str(nfr), "-an", "-c:v", "libx264", "-crf", "15", "-preset", "fast", f"{OUT}/b{k}.mp4"])


# 3) Sottotitoli + grafiche (ASS)
def ass_t(x):
    x = max(x, 0)
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


pages = []
for i, seg in enumerate(SEGS):
    cur = []
    for txt, tt in seg[3]:
        brk = txt.startswith("|")
        txt = txt.lstrip("|")
        if cur and (brk or len(cur) == 3):
            pages.append(cur)
            cur = []
        cur.append((txt, out_t(i, tt + 0.08), i))
    pages.append(cur)

YELLOW, RED = "&H0033D1FF&", "&H002E2EE6&"
ev = []
for j, pg in enumerate(pages):
    st, seg = pg[0][1], pg[0][2]
    en = pages[j + 1][0][1] if j + 1 < len(pages) and pages[j + 1][0][2] == seg else seg_end(seg)
    if j + 1 == len(pages):
        en = TOTAL
    if seg in BIG:
        txt = " ".join(w.rstrip(",.?") for w, *_ in pg)
        pop = r"{\fs124\bord7\fscx80\fscy80\t(0,140,\fscx100\fscy100)}"
        ev.append(f"Dialogue: 0,{ass_t(st)},{ass_t(seg_end(seg))},Main,,0,0,0,,{pop}{{\\c{YELLOW}}}{txt}")
        continue
    words = [f"{{\\c{YELLOW if w in KEY else '&H00FFFFFF&'}}}{w.rstrip(',.?')}" for w, *_ in pg]
    pop = r"{\fscx108\fscy108\t(0,100,\fscx100\fscy100)}"
    ev.append(f"Dialogue: 0,{ass_t(st)},{ass_t(en)},Main,,0,0,0,,{pop}{' '.join(words)}")


def circle(r):
    k = r * 0.552
    return (f"m 0 {-r} b {k:.0f} {-r} {r} {-k:.0f} {r} 0 b {r} {k:.0f} {k:.0f} {r} 0 {r} "
            f"b {-k:.0f} {r} {-r} {k:.0f} {-r} 0 b {-r} {-k:.0f} {-k:.0f} {-r} 0 {-r}")


def rrect(w, h, r):
    k = r * 0.552
    return (f"m {r} 0 l {w - r} 0 b {w - r + k:.0f} 0 {w} {r - k:.0f} {w} {r} l {w} {h - r} "
            f"b {w} {h - r + k:.0f} {w - r + k:.0f} {h} {w - r} {h} l {r} {h} b {r - k:.0f} {h} 0 {h - r + k:.0f} 0 {h - r} "
            f"l 0 {r} b 0 {r - k:.0f} {r - k:.0f} 0 {r} 0")


OUTLINE = r"\1a&HFF&\bord5\shad0\blur0.6"
# gomito di Elia: cerchio rosso sottile + freccia, quando lo zoom è fermo
ex, ey = 626, 774
g0 = EL_T0 + EL_ZOOM_FR / FPS + 0.05
ev.append(f"Dialogue: 2,{ass_t(g0)},{ass_t(EL_T1)},Main,,0,0,0,,{{\\an7\\pos({ex},{ey})\\3c{RED}{OUTLINE}"
          f"\\fscx70\\fscy70\\alpha&HFF&\\t(0,180,\\fscx100\\fscy100\\alpha&H00&\\1a&HFF&)\\p1}}{circle(118)}")
# freccia da destra verso il gomito
arrow = "m 0 0 l 60 -34 l 60 -12 l 170 -12 l 170 12 l 60 12 l 60 34"
ev.append(f"Dialogue: 2,{ass_t(g0 + 0.15)},{ass_t(EL_T1)},Main,,0,0,0,,{{\\an4\\1c{RED}\\bord0\\shad0"
          f"\\move({ex + 175},{ey},{ex + 135},{ey},0,220)\\alpha&HFF&\\t(0,150,\\alpha&H00&)\\p1}}{arrow}")
# presa: riquadro rosso sottile sulle mani
ev.append(f"Dialogue: 2,{ass_t(HA_T0 + 0.1)},{ass_t(HA_T1)},Main,,0,0,0,,{{\\an7\\pos(455,560)\\3c{RED}{OUTLINE}"
          f"\\alpha&HFF&\\t(0,180,\\alpha&H00&\\1a&HFF&)\\p1}}{rrect(540, 210, 40)}")

# "allargala": linea tra le mani che si allarga seguendo il gesto (mani: sorgente 55.45 -> 55.95)
la0, la1 = out_t(5, 55.42), out_t(5, 55.92)
lend = seg_end(5)
dur_ms = int((la1 - la0) * 1000)
ev.append(f"Dialogue: 2,{ass_t(la0)},{ass_t(lend)},Main,,0,0,0,,{{\\an5\\move(600,1320,540,1225,0,{dur_ms})"
          f"\\1c{YELLOW}\\bord0\\shad2\\4c&H000000&\\fscx8\\t(0,{dur_ms},\\fscx100)\\p1}}m 0 0 l 940 0 l 940 9 l 0 9")
for x0, x1 in ((600 - 40, 540 - 470), (600 + 40, 540 + 470)):
    ev.append(f"Dialogue: 2,{ass_t(la0)},{ass_t(lend)},Main,,0,0,0,,{{\\an5\\move({x0},1320,{x1},1225,0,{dur_ms})"
              f"\\1c{YELLOW}\\bord0\\shad2\\4c&H000000&\\p1}}m 0 0 l 10 0 l 10 64 l 0 64")

ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Inter Black,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,0,0,1,6,3,2,80,80,470,1

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
    fc.append(f"{last}[bb{k}]overlay=eof_action=pass:enable='between(t,{t0:.4f},{t1 - 0.001:.4f})'[o{k}]")
    last = f"[o{k}]"
fc.append(f"{last}ass={OUT}/subs.ass,format=yuv420p[vf]")
run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[vf]", "-map", "0:a",
     "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p",
     "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{TOTAL:.3f}",
     f"{OUT}/reel_squat_presa_v3.mp4"])
print("TOTAL", round(TOTAL, 2))
for k, b in enumerate(BROLL):
    print("broll", k, b[2], round(b[0], 2), round(b[1], 2))
for p in pages:
    print(round(p[0][1], 2), " ".join(w for w, *_ in p))
