#!/usr/bin/env python3
"""Reel squat/presa: A-roll parlato + B-roll di esecuzione + sottotitoli ASS."""
import os, subprocess

SRC = "/home/user/Video-maker/src_squat"
OUT = "/home/user/Video-maker/out/squat"
os.makedirs(OUT, exist_ok=True)
W, H, FPS, SPEED = 1080, 1920, 30, 1.1
P = f"{SRC}/Squat_parlato.MOV"

# segmenti di voce (sorgente), zoom A-roll (scala, centro y relativo), parole con tempi sorgente
SEGS = [
    (1.00, 2.28, 1.00, [("LO", 1.0), ("SQUAT", 1.2), ("|NON", 1.7), ("GIRA?", 1.86)]),
    (2.70, 5.00, 1.00, [("PRIMA", 2.75), ("DI", 2.95), ("|CAMBIARE", 3.1), ("PROGRAMMA,", 3.56), ("|GUARDA", 3.98),
                        ("I", 4.44), ("GOMITI.", 4.52)]),
    (13.90, 16.75, 1.14, [("LA", 13.92), ("LARGHEZZA", 14.12), ("|DELLA", 14.6), ("PRESA", 14.92), ("|DECIDE", 15.48),
                          ("DOVE", 15.96), ("FINISCONO.", 16.2)]),
    (34.55, 38.40, 1.00, [("UNA", 34.6), ("PRESA", 34.8), ("|PIÙ", 35.28), ("STRETTA", 35.44), ("|RENDE", 36.08),
                          ("PIÙ", 36.48), ("COMPATTA", 36.64), ("|LA", 37.12), ("SCHIENA", 37.2), ("|SOTTO", 37.44),
                          ("IL", 37.76), ("BILANCIERE.", 37.84)]),
    (42.25, 43.95, 1.22, [("MA", 42.3), ("SERVE", 42.42), ("|MOBILITÀ", 42.9), ("DI", 43.3), ("SPALLA.", 43.46)]),
    (53.80, 56.35, 1.00, [("SE", 53.82), ("TI", 54.0), ("|IRRIGIDISCE", 54.16), ("|E", 54.88), ("TI", 54.96), ("DÀ", 55.04),
                          ("FASTIDIO,", 55.2), ("|ALLARGALA.", 55.68)]),
    (62.48, 67.00, 1.12, [("LA", 62.5), ("PRESA", 62.7), ("GIUSTA", 63.1), ("|È", 63.42), ("QUELLA", 63.5), ("CHE", 63.74),
                          ("|TIENE", 63.9), ("IL", 64.3), ("|BILANCIERE", 64.38), ("SALDO", 65.1),
                          ("|SENZA", 65.74), ("TENSIONI", 66.14), ("INUTILI.", 66.54)]),
]
KEY = {"SQUAT", "GOMITI.", "LARGHEZZA", "PRESA", "STRETTA", "COMPATTA", "MOBILITÀ", "SPALLA.", "FASTIDIO,",
       "ALLARGALA.", "GIUSTA", "SALDO", "TENSIONI"}

# tempo in uscita
starts, t = [], 0.0
for s, e, *_ in SEGS:
    starts.append(t)
    t += (e - s) / SPEED
TOTAL = t


def out_t(seg, src_t):
    return starts[seg] + (src_t - SEGS[seg][0]) / SPEED


def word_t(seg, w):  # parola come pronunciata, tempi del modello ~0.1 s in anticipo
    for txt, tt in SEGS[seg][3]:
        if txt.lstrip("|") == w:
            return out_t(seg, tt + 0.08)
    raise KeyError(w)


# B-roll: (inizio uscita, fine uscita, file, inizio sorgente, velocità, zoom finale)
BROLL = [
    (0.0, starts[1], "ultimarep.mov", 0.35, 1.0, 1.10),
    (word_t(1, "GOMITI."), starts[2] + 0.15, "GomitialtiElia.mov", 0.2, 1.0, 1.10),
    (word_t(2, "PRESA"), starts[3], "Sistemazionepresamani.mov", 1.2, 1.0, 1.12),
    (word_t(3, "RENDE"), starts[4], "Sistemazionebilanciere.mov", 0.0, 0.8, 1.10),
    (word_t(6, "TIENE"), word_t(6, "SENZA"), "Squatfrontale.mov", 0.0, 1.0, 1.08),
    (word_t(6, "SENZA"), TOTAL, "ultimarep.mov", 2.7, 1.0, 1.06),
]

TONEMAP = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=saturation=1.12:contrast=1.04")


def run(cmd):
    subprocess.run(cmd, check=True)


def is_hlg(f):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer",
                        "-of", "csv=p=0", f], capture_output=True, text=True).stdout
    return "arib-std-b67" in o


# 1) A-roll: segmenti con zoom alternato (cambio inquadratura simulato), velocità 1.1
lst = []
for i, (s, e, z, _) in enumerate(SEGS):
    cw, ch = int(W / z) // 2 * 2, int(H / z) // 2 * 2
    d = e - s
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.3f}", "-i", P, "-t", f"{d:.3f}", "-vf",
         f"scale={W}:{H},crop={cw}:{ch}:(iw-{cw})/2:(ih-{ch})*0.30,scale={W}:{H},setsar=1,fps={FPS}",
         "-af", f"afade=t=in:d=0.02,afade=t=out:st={d - 0.03:.3f}:d=0.03", "-c:v", "libx264", "-crf", "15",
         "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-ar", "48000", f"{OUT}/s{i}.mov"])
    lst.append(f"file '{OUT}/s{i}.mov'")
open(f"{OUT}/segs.txt", "w").write("\n".join(lst) + "\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/segs.txt", "-filter_complex",
     f"[0:v]setpts=PTS/{SPEED},fps={FPS}[vo];[0:a]atempo={SPEED},highpass=f=80,"
     f"acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-14:TP=-1.5:LRA=7[ao]",
     "-map", "[vo]", "-map", "[ao]", "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "192k", "-ar", "48000", f"{OUT}/aroll.mp4"])

# 2) B-roll: tonemap HLG, riempi 9:16, lento zoom in
CROP = {"GomitialtiElia.mov": "crop=300:533:80:40,eq=brightness=0.05:contrast=1.08:saturation=0.85"}
for k, (t0, t1, f, ss, sp, zend) in enumerate(BROLL):
    dur = t1 - t0
    nfr = int(round(dur * FPS))
    vf = []
    if is_hlg(f"{SRC}/{f}"):
        vf.append(TONEMAP)
    if f in CROP:
        vf.append(CROP[f])
    vf += [f"setpts=PTS/{sp}", f"fps={FPS}", f"scale={W}:{H}:force_original_aspect_ratio=increase", f"crop={W}:{H}",
           f"scale={W * 2}:{H * 2}",
           f"zoompan=z='1+({zend}-1)*on/{max(nfr - 1, 1)}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:"
           f"s={W}x{H}:fps={FPS}", "setsar=1", "format=yuv420p"]
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", f"{SRC}/{f}", "-vf", ",".join(vf), "-frames:v",
         str(nfr), "-an", "-c:v", "libx264", "-crf", "16", "-preset", "fast", f"{OUT}/b{k}.mp4"])


# 3) Sottotitoli ASS: pagine da max 3 parole, parole chiave in giallo, entrata con pop leggero
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

ev = []
for j, pg in enumerate(pages):
    st = pg[0][1]
    seg = pg[0][2]
    seg_end = starts[seg] + (SEGS[seg][1] - SEGS[seg][0]) / SPEED
    en = pages[j + 1][0][1] if j + 1 < len(pages) and pages[j + 1][0][2] == seg else seg_end
    en = min(en, seg_end) if j + 1 < len(pages) else TOTAL
    words = []
    for txt, wt, _ in pg:
        col = "&H003CCBFF&" if txt in KEY else "&H00FFFFFF&"
        words.append(f"{{\\c{col}}}{txt.rstrip(',.?')}")
    pop = r"{\fscx112\fscy112\t(0,110,\fscx100\fscy100)\fad(40,0)}"
    ev.append(f"Dialogue: 0,{ass_t(st)},{ass_t(en)},Main,,0,0,0,,{pop}{' '.join(words)}")

# cerchio che evidenzia il gomito di Elia
t0, t1 = BROLL[1][0] + 0.12, BROLL[1][1]
r, k = 120, 66
circ = (f"m 0 {-r} b {k} {-r} {r} {-k} {r} 0 b {r} {k} {k} {r} 0 {r} b {-k} {r} {-r} {k} {-r} 0 "
        f"b {-r} {-k} {-k} {-r} 0 {-r}")
ev.append(f"Dialogue: 1,{ass_t(t0)},{ass_t(t1)},Main,,0,0,0,,{{\\an5\\pos(700,930)\\1a&HFF&\\3c&H003CCBFF&"
          f"\\bord7\\shad0\\fscx40\\fscy40\\alpha&HFF&\\t(0,180,\\fscx100\\fscy100\\alpha&H00&\\1a&HFF&)\\p1}}{circ}")

ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Inter Black,88,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,0,0,0,0,100,100,0,0,1,5,3,2,90,90,560,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n"
open(f"{OUT}/subs.ass", "w").write(ass)

# 4) Composizione finale
inputs = ["-i", f"{OUT}/aroll.mp4"]
fc = []
last = "[0:v]"
for k, (t0, t1, *_r) in enumerate(BROLL):
    inputs += ["-i", f"{OUT}/b{k}.mp4"]
    fc.append(f"[{k + 1}:v]setpts=PTS-STARTPTS+{t0:.4f}/TB[bb{k}]")
    fc.append(f"{last}[bb{k}]overlay=eof_action=pass:enable='between(t,{t0:.4f},{t1 - 0.001:.4f})'[o{k}]")
    last = f"[o{k}]"
fc.append(f"{last}ass={OUT}/subs.ass,format=yuv420p[vf]")
run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[vf]", "-map", "0:a",
     "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-profile:v", "high", "-pix_fmt", "yuv420p",
     "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{TOTAL:.3f}",
     f"{OUT}/reel_squat_presa.mp4"])
print("TOTAL", round(TOTAL, 2))
for p in pages:
    print(round(p[0][1], 2), " ".join(w for w, *_ in p))
