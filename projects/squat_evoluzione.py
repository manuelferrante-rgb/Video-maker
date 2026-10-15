#!/usr/bin/env python3
"""Reel "per essere forte nello squat devi avere i muscoli": contrasto prima (squat con kettlebell, magro) e ora
(230 kg in gara), complementari (stacco, affondi, GHD), check fisico su forza/ipertrofia, domanda finale per i commenti.
Stesso stile del reel "squat 51%": etichette a pop, B-roll legati al parlato, momenti salienti, pochi effetti sonori."""
import math, os, subprocess, wave
import numpy as np

SRC = "/home/user/Video-maker/src_evo"
OUT = "/home/user/Video-maker/out/squat_evoluzione"
SFXD = "/home/user/Video-maker/sfx"
os.makedirs(OUT, exist_ok=True)
W, H, FPS, SPEED = 1080, 1920, 30, 1.15
P = f"{SRC}/IMG_8153.MOV"

SEGS = [
    (0.35, 1.88, 1.00, [("ABBIAMO", 0.47), ("PARLATO", 0.79), ("DI", 1.11), ("GOMITI.", 1.19)]),
    (2.08, 4.86, 1.00, [("MA", 1.98), ("PER", 2.22), ("ESSERE", 2.38), ("FORTE", 2.62), ("|NELLO", 2.86), ("SQUAT", 3.1),
                        ("|DEVI", 3.82), ("AVERE", 4.06), ("I", 4.22), ("MUSCOLI.", 4.3)]),
    (13.24, 15.21, 1.12, [("QUINDI", 13.14), ("CONCENTRATI", 13.46), ("|DI", 14.02), ("DIVENTARE", 14.18),
                          ("|PIÙ", 14.58), ("GROSSO.", 14.74)]),
    (19.31, 22.28, 1.00, [("SE", 19.21), ("SEI", 19.37), ("IN", 19.55), ("UNA", 19.61), ("|FASE", 19.77), ("DI", 20.01),
                          ("COSTRUZIONE,", 20.09), ("|AUMENTA", 20.81), ("LE", 21.29), ("RIPETIZIONI,", 21.45)]),
    (23.64, 25.06, 1.00, [("IL", 23.62), ("TEMPO", 23.78), ("|SOTTO", 24.1), ("TENSIONE", 24.42)]),
    (35.50, 37.51, 1.00, [("E", 35.4), ("USA", 35.56), ("COMPLEMENTARI", 35.8), ("|PER", 36.36), ("AUMENTARE", 36.44),
                          ("L'IPERTROFIA.", 36.76)]),
    (49.62, 50.22, 1.12, [("SECONDO", 49.57), ("TE,", 49.97)]),
    (64.89, 67.72, 1.12, [("È", 64.79), ("LA", 65.03), ("FORZA", 65.11), ("|CHE", 65.27), ("PORTA", 65.43),
                          ("IPERTROFIA", 65.75), ("|O", 66.23), ("L'IPERTROFIA", 66.31), ("|CHE", 67.03), ("PORTA", 67.11),
                          ("FORZA?", 67.35)]),
]
SEGS = [(s, s + round((e - s) * FPS) / FPS, *r) for s, e, *r in SEGS]
TAIL = 0.45
starts, t = [], 0.0
for s, e, *_ in SEGS:
    starts.append(t)
    t += (e - s) / SPEED
VOICE_END = t
TOTAL = t + TAIL


def out_t(seg, src_t):
    return starts[seg] + (src_t - SEGS[seg][0]) / SPEED


def word_t(seg, w, nth=0):
    k = 0
    for txt, tt in SEGS[seg][3]:
        if txt.lstrip("|") == w:
            if k == nth:
                return max(out_t(seg, tt + 0.08), starts[seg])
            k += 1
    raise KeyError(w)


def seg_end(i):
    return starts[i] + (SEGS[i][1] - SEGS[i][0]) / SPEED


def snap(x):
    return round(x * FPS) / FPS


TONEMAP = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")


def run(cmd):
    subprocess.run(cmd, check=True)


def is_hlg(f):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer",
                        "-of", "csv=p=0", f], capture_output=True, text=True).stdout
    return "arib-std-b67" in o


# 1) A-roll: voce pulita, nessuna correzione colore, zoom leggero solo come cambio d'inquadratura
lst = []
for i, (s, e, z, _) in enumerate(SEGS):
    cw, ch = int(W / z) // 2 * 2, int(H / z) // 2 * 2
    d = e - s
    extra = f",tpad=stop_mode=clone:stop_duration={TAIL * SPEED:.3f}" if i == len(SEGS) - 1 else ""
    af = f"afade=t=in:d=0.015,afade=t=out:st={d - 0.03:.3f}:d=0.03" + (f",apad=pad_dur={TAIL * SPEED:.3f}" if extra else "")
    nfr = round(d * FPS) + (round(TAIL * SPEED * FPS) if extra else 0)
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.3f}", "-t", f"{d:.4f}", "-i", P, "-vf",
         f"scale={W}:{H},crop={cw}:{ch}:(iw-{cw})/2:(ih-{ch})*0.0,scale={W}:{H}:flags=lanczos,setsar=1,fps={FPS}{extra}",
         "-af", af, "-frames:v", str(nfr), "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
         "-c:a", "pcm_s16le", "-ar", "48000", f"{OUT}/s{i}.mov"])
    lst.append(f"file '{OUT}/s{i}.mov'")
open(f"{OUT}/segs.txt", "w").write("\n".join(lst) + "\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/segs.txt", "-filter_complex",
     f"[0:v]setpts=PTS/{SPEED},fps={FPS}[vo];[0:a]atempo={SPEED},highpass=f=80,"
     f"acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-14:TP=-1.5:LRA=7[ao]",
     "-map", "[vo]", "-map", "[ao]", "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "192k", "-ar", "48000", f"{OUT}/aroll.mp4"])


# 2) B-roll: solo i momenti salienti, muti. crop = (cx, cy, zoom) sul fotogramma 1080x1920
def clip(name, f, ss, dur, sp=1.0, crop=None, size=(W, H), extra=""):
    vf = []
    if is_hlg(f"{SRC}/{f}"):
        vf.append(TONEMAP)
    vf += [f"setpts=PTS/{sp}", f"fps={FPS}", f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos",
           f"crop={W}:{H}"]
    if crop:
        cx, cy, z = crop
        cw, ch = int(W / z) // 2 * 2, int(H / z) // 2 * 2
        x0 = int(min(max(cx - cw / 2, 0), W - cw))
        y0 = int(min(max(cy - ch / 2, 0), H - ch))
        vf += [f"crop={cw}:{ch}:{x0}:{y0}", f"scale={W}:{H}:flags=lanczos"]
    if size != (W, H):
        tw, th = size
        vf += [f"scale={tw}:-2:flags=lanczos", f"crop={tw}:{th}"]
    vf += ["tpad=stop_mode=clone:stop_duration=2", "setsar=1", "format=yuv420p"]
    if extra:
        vf.append(extra)
    nfr = int(round(dur * FPS))
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", f"{SRC}/{f}", "-vf", ",".join(vf), "-frames:v", str(nfr),
         "-an", "-c:v", "libx264", "-crf", "15", "-preset", "fast", f"{OUT}/{name}.mp4"])
    return f"{OUT}/{name}.mp4"


OVER = []  # (t0, t1, file)
# hook: PRIMA (squat con kettlebell, magro) -> ORA (230 kg in gara)
K1 = snap(starts[1])
OVER.append((0.0, K1, clip("prima", "v2100.mp4", 0.75, K1 + 0.1, 1.0, crop=(400, 1100, 1.25))))
D1 = snap(word_t(1, "DEVI"))
OVER.append((K1, D1, clip("ora", "IMG_4930.MOV", 33.2, D1 - K1 + 0.1, 1.0, crop=(800, 1450, 1.8))))
# fase di costruzione / ripetizioni: stacco, più ripetizioni di fila
R0, R1 = snap(starts[3]), snap(seg_end(3))
OVER.append((R0, R1, clip("stacco", "IMG_7217.MOV", 1.2, R1 - R0 + 0.1, 1.15, crop=(650, 1000, 1.3))))
# tempo sotto tensione: affondi rallentati
T0, T1 = snap(starts[4]), snap(seg_end(4))
OVER.append((T0, T1, clip("affondi", "IMG_7218.MOV", 1.0, T1 - T0 + 0.1, 0.75, crop=(600, 1000, 1.3))))
# complementari: GHD, poi affondi (altra ripetizione)
C0, Cm, C1 = snap(starts[5]), snap(word_t(5, "PER")), snap(seg_end(5))
OVER.append((C0, Cm, clip("ghd", "ghd.mp4", 8.4, Cm - C0 + 0.1, 1.0)))
OVER.append((Cm, C1, clip("affondi2", "IMG_7218.MOV", 17.0, C1 - Cm + 0.1, 1.0, crop=(600, 1000, 1.3))))
# domanda finale: forza (squat 230 in discesa) / ipertrofia (check fisico) / forza (risalita)
F0 = snap(word_t(7, "FORZA") - 0.12)
I0 = snap(word_t(7, "IPERTROFIA") - 0.1)
I1 = snap(word_t(7, "L'IPERTROFIA") - 0.1)
F1 = snap(word_t(7, "FORZA?") - 0.12)
OVER.append((F0, I0, clip("forza1", "IMG_4930.MOV", 31.6, I0 - F0 + 0.1, 1.0, crop=(800, 1450, 1.8))))
OVER.append((I0, I1, clip("fisico1", "IMG_5235a.mov", 0.2, I1 - I0 + 0.1, 1.0)))
OVER.append((I1, F1, clip("fisico2", "IMG_5235b.mov", 3.3, F1 - I1 + 0.1, 1.0)))
OVER.append((F1, snap(TOTAL), clip("forza2", "IMG_4930.MOV", 34.0, TOTAL - F1 + 0.1, 1.0, crop=(800, 1450, 1.8))))

# 3) Sottotitoli, etichette, grafiche (ASS) -----------------------------------------------------------------
def ass_t(x):
    x = max(x, 0)
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


ORANGE_A, BLACK_A, WHITE_A, GREEN_A = "&H002C66E8&", "&H00000000&", "&H00FFFFFF&", "&H0096D67E&"
KEY = {"GOMITI.", "SQUAT", "MUSCOLI.", "GROSSO.", "RIPETIZIONI,", "TENSIONE", "COMPLEMENTARI", "L'IPERTROFIA.", "FORZA", "IPERTROFIA", "L'IPERTROFIA", "FORZA?"}
SFX = []
ev = []

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
for j, pg in enumerate(pages):
    st, seg = pg[0][1], pg[0][2]
    en = pages[j + 1][0][1] if j + 1 < len(pages) and pages[j + 1][0][2] == seg else seg_end(seg)
    if j + 1 == len(pages):
        en = VOICE_END + 0.1
    words = [f"{{\\c{ORANGE_A if w in KEY else WHITE_A}}}{w.rstrip(',.?:')}" for w, *_ in pg]
    ev.append(f"Dialogue: 5,{ass_t(st)},{ass_t(en)},Sub,,0,0,0,,{{\\fad(60,0)}}{' '.join(words)}")


def label(t0, t1, txt, y, box=BLACK_A, fg=WHITE_A, size=96, x=540, an=8):
    pop = (rf"{{\an{an}\pos({x},{y})\3c{box}\c{fg}\fs{size}\fscx0\fscy0\t(0,90,\fscx112\fscy112)"
           rf"\t(90,170,\fscx100\fscy100)}}")
    ev.append(f"Dialogue: 4,{ass_t(t0)},{ass_t(t1)},Lab,,0,0,0,,{pop}{txt}")


ORANGE_A, BLACK_A, WHITE_A = "&H002C66E8&", "&H00000000&", "&H00FFFFFF&"
label(0.03, K1, "PRIMA", 640, size=110, x=800)
label(K1, D1, "230 KG IN GARA", 300, box=ORANGE_A, size=100)
SFX += [(0.0, "pop", 0.3), (K1, "hit", 0.42)]
label(D1, seg_end(1), "MUSCOLI", 270, box=ORANGE_A, size=110)
SFX.append((D1, "pop", 0.3))
label(word_t(2, "PIÙ"), seg_end(2), "PIÙ GROSSO", 270, size=110)
SFX.append((word_t(2, "PIÙ"), "pop", 0.28))
label(R0 + 0.03, word_t(3, "AUMENTA"), "FASE DI COSTRUZIONE", 1060, size=76)
label(word_t(3, "AUMENTA"), R1, "+ RIPETIZIONI", 1060, box=ORANGE_A, size=96)
SFX += [(R0 - 0.04, "swoosh", 0.28), (word_t(3, "AUMENTA"), "pop", 0.25)]
label(T0 + 0.03, T1, "TEMPO SOTTO TENSIONE", 1060, box=ORANGE_A, size=80)
label(C0 + 0.03, C1, "COMPLEMENTARI", 1060, box=ORANGE_A, size=92)
label(word_t(5, "L'IPERTROFIA."), C1, "IPERTROFIA", 1180, size=80)
SFX += [(C0 - 0.04, "swoosh", 0.25), (word_t(5, "L'IPERTROFIA."), "pop", 0.25)]
label(starts[6] + 0.02, F0, "SECONDO TE", 270, size=100)
label(F0, I0, "FORZA", 1060, box=ORANGE_A, size=120)
label(I0, I1, "IPERTROFIA", 1060, size=110)
label(I1, F1, "IPERTROFIA", 1060, size=110)
label(F1, TOTAL, "FORZA?", 1060, box=ORANGE_A, size=120)
SFX += [(F0, "hit", 0.35), (I0, "swoosh", 0.25), (F1, "hit", 0.35)]
label(F1 + 0.15, TOTAL, "SCRIVILO NEI COMMENTI", 300, size=70)
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter Black,56,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,3,12,0,2,80,80,450,1
Style: Lab,Inter Black,90,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,1,0,0,100,100,0,0,3,16,0,8,40,40,0,1
Style: Shp,Inter Black,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Btn,Inter Black,96,&H00FFFFFF,&H00FFFFFF,&H002C66E8,&H00000000,0,1,0,0,100,100,2,0,3,26,0,8,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n"
open(f"{OUT}/subs.ass", "w").write(ass)

# 4) Effetti sonori (traccia sotto la voce)
sr = 48000
mix = np.zeros((int((TOTAL + 1) * sr), 2), np.float32)
for t0, nm, vol in SFX:
    with wave.open(f"{SFXD}/{nm}.wav") as wv:
        x = np.frombuffer(wv.readframes(wv.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32767
    i0 = max(int(t0 * sr), 0)
    i1 = min(i0 + len(x), len(mix))
    mix[i0:i1] += x[:i1 - i0] * vol
with wave.open(f"{OUT}/sfx.wav", "wb") as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(sr)
    wv.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())

# 5) Composizione
inputs = ["-i", f"{OUT}/aroll.mp4"]
fc, last, k_in = [], "[0:v]", 1
for k, (t0, t1, f) in enumerate(OVER):
    inputs += ["-i", f]
    fc.append(f"[{k_in}:v]setpts=PTS-STARTPTS+{t0:.4f}/TB[bb{k}]")
    fc.append(f"{last}[bb{k}]overlay=eof_action=pass:enable='between(t,{t0 - 0.004:.4f},{t1 - 0.02:.4f})'[o{k}]")
    last, k_in = f"[o{k}]", k_in + 1
inputs += ["-i", f"{OUT}/sfx.wav"]
fc.append(f"{last}ass={OUT}/subs.ass,format=yuv420p[vf]")
fc.append(f"[0:a]apad[va];[va][{k_in}:a]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[af]")
run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[vf]", "-map", "[af]",
     "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p",
     "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{TOTAL:.3f}",
     f"{OUT}/reel_squat_evoluzione.mp4"])
print("TOTAL", round(TOTAL, 2))
