#!/usr/bin/env python3
"""Reel "l'era del calisthenics senza gambe è finita": squat = 51% del totale (FinalRep, Team Italy Euros 2026).
Stile del reel trazioni v2: etichette in corsivo a pop, schermata dati animata (verde FinalRep), griglia delle 4 alzate,
montaggio veloce dei momenti salienti, pochi effetti sonori. Audio: solo voce + effetti (B-roll muti)."""
import math, os, subprocess, wave
import numpy as np

SRC = "/home/user/Video-maker/src_tot"
OUT = "/home/user/Video-maker/out/squat_totale"
SFXD = "/home/user/Video-maker/sfx"
os.makedirs(OUT, exist_ok=True)
W, H, FPS, SPEED = 1080, 1920, 30, 1.1
P = f"{SRC}/IMG_8147.MOV"

# voce (sorgente): inizio, fine, zoom, parole
SEGS = [
    (0.25, 3.10, 1.00, [("L'ERA", 0.15), ("DEL", 0.47), ("CALISTHENICS", 0.63), ("|SENZA", 1.43), ("GAMBE", 1.67),
                        ("|È", 2.23), ("FINITA.", 2.39)]),
    (9.60, 11.12, 1.00, [("I", 9.59), ("DATI", 9.75), ("DELL'ITALIA", 9.99), ("|ALL'EUROPEO:", 10.55)]),
    (11.62, 14.75, 1.00, [("LO", 11.51), ("SQUAT", 11.67), ("PESA", 12.15), ("|IL", 12.47), ("51%,", 12.63),
                          ("|PIÙ", 13.67), ("DELLA", 13.91), ("METÀ.", 14.15)]),
    (21.90, 24.42, 1.00, [("CHI", 21.8), ("VINCE", 22.12), ("|HA", 22.6), ("TUTTE", 22.76), ("E", 22.92),
                          ("QUATTRO", 23.08), ("|LE", 23.32), ("ALZATE", 23.48), ("FORTI.", 24.04)]),
    (28.60, 31.58, 1.12, [("SE", 28.53), ("UNA", 28.69), ("TUA", 28.93), ("ALZATA", 29.09), ("|È", 29.49),
                          ("DEBOLE,", 29.57), ("|IL", 30.21), ("TOTALE", 30.37), ("|SI", 30.77), ("FERMA", 30.93),
                          ("LÀ.", 31.33)]),
    (38.20, 41.15, 1.00, [("PER", 38.12), ("QUESTO", 38.44), ("|CON", 38.68), ("I", 38.92), ("MIEI", 39.0),
                          ("ATLETI", 39.32), ("|LAVORIAMO", 39.8), ("SU", 40.44), ("TUTTO.", 40.68)]),
    (46.65, 49.85, 1.10, [("PER", 46.56), ("VINCERE", 46.88), ("|E", 47.36), ("PER", 47.52), ("ESSERE", 47.68),
                          ("FORTI", 48.0), ("|BISOGNA", 48.48), ("ESSERE", 48.88), ("COMPLETI.", 49.2)]),
]
SEGS = [(s, s + round((e - s) * FPS) / FPS, *r) for s, e, *r in SEGS]
TAIL = 0.9  # fermo finale per il pulsante SEGUIMI
starts, t = [], 0.0
for s, e, *_ in SEGS:
    starts.append(t)
    t += (e - s) / SPEED
VOICE_END = t
TOTAL = t + TAIL


def out_t(seg, src_t):
    return starts[seg] + (src_t - SEGS[seg][0]) / SPEED


def word_t(seg, w):
    for txt, tt in SEGS[seg][3]:
        if txt.lstrip("|") == w:
            return max(out_t(seg, tt + 0.08), starts[seg])
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


OVER = []  # (t0, t1, file) sovrapposizioni a tutto schermo
# hook: squat in gara, risalita dal fondo
HOOK1 = snap(word_t(0, "SENZA"))
OVER.append((0.0, HOOK1, clip("hook", "v6148.mp4", 17.35, HOOK1 + 0.1, 1.0, crop=(760, 1180, 1.5))))

# schermata dati FinalRep (verde): parte su "all'Europeo", lo squat 51% si evidenzia sulla parola
C0 = snap(word_t(1, "ALL'EUROPEO:") - 0.05)
C1 = snap(seg_end(2) + 0.05)
t51 = word_t(2, "51%,") - C0
tmeta = word_t(2, "PIÙ") - C0
run(["python3", "/home/user/Video-maker/projects/finalrep_card.py", f"{C1 - C0:.3f}", f"{OUT}/card51.mov",
     f"{t51:.3f}", f"{tmeta:.3f}"])

# griglia delle 4 alzate su "chi vince ha tutte e quattro le alzate forti" + "se una tua alzata è debole"
G0 = snap(word_t(3, "TUTTE") - 0.05)
G1 = snap(word_t(4, "IL"))
gd = G1 - G0 + 0.2
cw2, ch2 = W // 2, H // 2
REVEAL = [snap(word_t(3, "TUTTE") - G0), snap(word_t(3, "E") - G0 + 0.05), snap(word_t(3, "QUATTRO") - G0),
          snap(word_t(3, "ALZATE") - G0)]
WEAK = word_t(4, "DEBOLE,") - G0
cells = [  # nome, file, inizio sorgente, velocità, crop
    ("SQUAT", "v4824.mp4", 37.0, 1.0, (456, 600, 1.8)),
    ("MUSCLE UP", "IMG_1766.MOV", 12.6, 0.9, (560, 640, 1.25)),
    ("TRAZIONI", "IMG_6080.MOV", 8.4, 1.0, (520, 1000, 1.9)),
    ("DIP", "IMG_6085.MOV", 4.1, 1.0, (645, 990, 2.4)),
]
gfiles = []
for k, (nm, f, ss, sp, cr) in enumerate(cells):
    # prima di "accendersi" la cella resta scura e sfocata, poi diventa nitida sulla parola
    ex = (f"boxblur=12:2:enable='lt(t,{REVEAL[k]:.3f})',eq=brightness=-0.32:saturation=0.4:enable='lt(t,{REVEAL[k]:.3f})'")
    if k == 3:  # l'alzata "debole" si spegne
        ex += f",hue=s=0:enable='gte(t,{WEAK:.3f})',eq=brightness=-0.18:enable='gte(t,{WEAK:.3f})'"
    gfiles.append(clip(f"g{k}", f, ss, gd, sp, crop=cr, size=(cw2, ch2), extra=ex))
run(["ffmpeg", "-v", "error", "-y", *sum([["-i", g] for g in gfiles], []), "-filter_complex",
     "[0:v][1:v][2:v][3:v]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0[v]", "-map", "[v]", "-c:v", "libx264", "-crf", "15",
     "-preset", "fast", "-pix_fmt", "yuv420p", f"{OUT}/grid.mp4"])
OVER.append((G0, G1, f"{OUT}/grid.mp4"))

# "con i miei atleti lavoriamo su tutto": montaggio veloce dei momenti salienti
M0 = snap(word_t(5, "CON"))
M3 = snap(seg_end(5) + 0.05)
m1 = snap(M0 + (M3 - M0) / 3)
m2 = snap(M0 + 2 * (M3 - M0) / 3)
OVER.append((M0, m1, clip("m1", "v2404.mp4", 3.05, m1 - M0 + 0.1, 1.0)))  # trazione: solo la tirata
OVER.append((m1, m2, clip("m2", "v6148.mp4", 17.8, m2 - m1 + 0.1, 1.0, crop=(760, 1180, 1.5))))
OVER.append((m2, M3, clip("m3", "IMG_1766.MOV", 13.2, M3 - m2 + 0.1, 1.0, crop=(560, 640, 1.25))))

# 3) Sottotitoli, etichette, grafiche (ASS) -----------------------------------------------------------------
def ass_t(x):
    x = max(x, 0)
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


ORANGE_A, BLACK_A, WHITE_A, GREEN_A = "&H002C66E8&", "&H00000000&", "&H00FFFFFF&", "&H0096D67E&"
KEY = {"CALISTHENICS", "GAMBE", "SQUAT", "51%,", "METÀ.", "QUATTRO", "DEBOLE,", "TOTALE", "TUTTO.", "COMPLETI."}
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
    if C0 <= st < C1:  # durante la schermata dati i numeri li mostra la grafica
        continue
    words = [f"{{\\c{ORANGE_A if w in KEY else WHITE_A}}}{w.rstrip(',.?:')}" for w, *_ in pg]
    ev.append(f"Dialogue: 5,{ass_t(st)},{ass_t(en)},Sub,,0,0,0,,{{\\fad(60,0)}}{' '.join(words)}")


def label(t0, t1, txt, y, box=BLACK_A, fg=WHITE_A, size=96, x=540, an=8):
    pop = (rf"{{\an{an}\pos({x},{y})\3c{box}\c{fg}\fs{size}\fscx0\fscy0\t(0,90,\fscx112\fscy112)"
           rf"\t(90,170,\fscx100\fscy100)}}")
    ev.append(f"Dialogue: 4,{ass_t(t0)},{ass_t(t1)},Lab,,0,0,0,,{pop}{txt}")


# hook: etichette sopra la testa (una alla volta, non coprono il viso)
label(0.03, HOOK1, "L'ERA DEL CALISTHENICS", 300, size=84)
label(HOOK1, word_t(0, "È"), "SENZA GAMBE", 270, box=ORANGE_A, size=100)
label(word_t(0, "È"), seg_end(0), "È FINITA", 270, size=110)
SFX += [(0.0, "hit", 0.32), (word_t(0, "È"), "hit", 0.38)]
# dati
label(starts[1] + 0.03, C0, "I DATI DELL'ITALIA", 270, size=84)
SFX += [(C0 - 0.06, "whoosh", 0.3), (C0 + t51, "pop", 0.32)]
# griglia: nome dell'alzata quando la cella compare + linee di separazione
for k, (nm, *_r) in enumerate(cells):
    x = 270 + (k % 2) * 540
    y = 290 if k < 2 else 1010
    label(G0 + REVEAL[k], G1, nm, y, box=ORANGE_A if k == 0 else BLACK_A, size=54, x=x)
    SFX.append((G0 + REVEAL[k], "pop", 0.16))
ev.append(f"Dialogue: 3,{ass_t(G0)},{ass_t(G1)},Shp,,0,0,0,,{{\\an7\\pos(537,0)\\1c{BLACK_A}\\bord0\\shad0\\p1}}m 0 0 l 6 0 l 6 1920 l 0 1920")
ev.append(f"Dialogue: 3,{ass_t(G0)},{ass_t(G1)},Shp,,0,0,0,,{{\\an7\\pos(0,957)\\1c{BLACK_A}\\bord0\\shad0\\p1}}m 0 0 l 1080 0 l 1080 6 l 0 6")
label(G0 + WEAK, G1, "DEBOLE", 1180, box=ORANGE_A, size=64, x=810)
# il totale si ferma
label(word_t(4, "IL"), seg_end(4), "IL TOTALE SI FERMA", 270, size=84)
SFX.append((word_t(4, "IL"), "swoosh", 0.25))
# montaggio atleti: etichette in basso, sul corpo, lontane dalle teste
label(M0, word_t(5, "LAVORIAMO"), "CON I MIEI ATLETI", 1120, size=78)
label(word_t(5, "LAVORIAMO"), seg_end(5), "LAVORIAMO SU TUTTO", 1120, box=ORANGE_A, size=84)
SFX.append((M0 - 0.04, "swoosh", 0.28))
# chiusura
label(word_t(6, "COMPLETI."), TOTAL, "COMPLETI", 270, box=ORANGE_A, size=120)
SFX.append((word_t(6, "COMPLETI."), "hit", 0.35))
B0 = VOICE_END + 0.05
CLK = B0 + 0.5
ck = int((CLK - B0) * 1000)
ev.append(f"Dialogue: 4,{ass_t(B0)},{ass_t(TOTAL)},Btn,,0,0,0,,{{\\an8\\pos(540,1330)\\fscx0\\fscy0"
          f"\\t(0,100,\\fscx112\\fscy112)\\t(100,180,\\fscx100\\fscy100)"
          f"\\t({ck},{ck + 80},\\fscx92\\fscy92)\\t({ck + 80},{ck + 180},\\fscx100\\fscy100)}}  SEGUIMI  ")
cursor = "m 0 0 l 0 105 l 27 81 l 45 123 l 63 114 l 45 75 l 81 75"
ev.append(f"Dialogue: 6,{ass_t(B0 + 0.1)},{ass_t(TOTAL)},Shp,,0,0,0,,{{\\an7\\move(800,1560,640,1400,0,{ck - 100})"
          f"\\1c{WHITE_A}\\bord4\\3c{BLACK_A}\\shad0\\p1}}{cursor}")
SFX += [(B0, "pop", 0.28), (CLK, "click", 0.5)]

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
inputs += ["-i", f"{OUT}/card51.mov"]
fc.append(f"[{k_in}:v]format=rgba,setpts=PTS-STARTPTS+{C0:.4f}/TB[cc]")
fc.append(f"{last}[cc]overlay=eof_action=pass:format=auto:enable='between(t,{C0 - 0.004:.4f},{C1 - 0.02:.4f})'[q]")
last, k_in = "[q]", k_in + 1
inputs += ["-i", f"{OUT}/sfx.wav"]
fc.append(f"{last}ass={OUT}/subs.ass,format=yuv420p[vf]")
fc.append(f"[0:a]apad[va];[va][{k_in}:a]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[af]")
run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[vf]", "-map", "[af]",
     "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p",
     "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{TOTAL:.3f}",
     f"{OUT}/reel_squat_totale.mp4"])
print("TOTAL", round(TOTAL, 2), "card", round(C0, 2), round(C1, 2), "grid", G0, G1, "mont", M0, M3)
