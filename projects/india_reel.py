#!/usr/bin/env python3
"""Reel "un mese in India": selfie in palestra (hook) -> imbarco -> cartina Italia/India -> arrivo -> palestra -> seguimi.
Due versioni: "voce" (voiceover tagliato a 1.1x + sottotitoli) e "scritte" (solo testo, senza voce).
Testo bianco con bordo nero, senza riquadro, centrato sotto la metà (sotto la faccia). Effetti sonori pochi; la musica la mette Manuel.
Uso: python3 projects/india_reel.py"""
import os, subprocess, wave
import numpy as np

R = "/home/user/Video-maker"
S = f"{R}/src_india"
OUT = f"{R}/out/india"
SFXD = f"{R}/sfx"
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
SP = 1.1  # velocità della voce


def run(cmd):
    subprocess.run(cmd, check=True)


# ---------- voce: tre frasi tagliate sulla voce reale (sorgente, inizio, fine) ----------
VOICE = [(9.86, 11.72), (12.30, 13.56), (13.89, 16.80)]
V_AT = [0.0, 3.80, 4.98]  # dove parte ogni frase nel reel
# parole (tempo sorgente del modello +0.08) -> tempo nel reel
WORDS = [
    (0, [("RIUSCIRÒ", 9.8), ("AD", 10.28), ("ALLENARMI", 10.44), ("UN", 10.92), ("MESE", 11.0), ("IN", 11.24),
         ("INDIA?", 11.32)]),
    (1, [("BEH,", 12.2), ("IO", 12.6), ("SONO", 12.84), ("ARRIVATO", 13.08)]),
    (2, [("PROVERÒ", 13.8), ("TUTTE", 14.36), ("LE", 14.52), ("PALESTRE", 14.6), ("SE", 15.16), ("VUOI", 15.32),
         ("SCOPRIRLO:", 15.48), ("SEGUIMI", 16.2)]),
]


def wt(i, t):
    return V_AT[i] + max(t + 0.08 - VOICE[i][0], 0) / SP


# ---------- immagini: (file, inizio sorgente, durata, zoom iniziale, zoom finale) ----------
MAP = f"{OUT}/map15.mov"
SHOTS = [
    ("IMG_8231", 0.60, 1.25, 1.18, 1.0),   # selfie in palestra (hook, entra con zoom)
    ("IMG_8223", 1.75, 0.40, 1.0, 1.06),   # pontile d'imbarco
    ("IMG_8218", 1.05, 0.40, 1.0, 1.06),   # porta dell'aereo
    ("IMG_8221", 0.10, 0.45, 1.0, 1.08),   # finestrino, motore
    ("MAP", 0.0, 1.50, 1.0, 1.0),          # cartina Italia -> India
    ("IMG_8217", 0.85, 0.45, 1.0, 1.05),   # aereo al gate in India
    ("IMG_8214", 0.70, 0.65, 1.0, 1.04),   # io sorridente in aeroporto
    ("IMG_8231", 3.05, 0.40, 1.0, 1.0),    # palestra: ragazzo che passa
    ("IMG_8231", 5.70, 0.40, 1.0, 1.0),    # rack e bilanciere
    ("IMG_8231", 7.05, 0.40, 1.0, 1.0),    # sala
    ("IMG_8231", 8.75, 0.90, 1.0, 1.05),   # sala grande con gente
    ("IMG_8231", 0.00, 1.10, 1.0, 1.08),   # di nuovo io (chiude il loop con l'inizio)
]

subprocess.run([f"python3", f"{R}/projects/map_italia_india.py", "1.5", MAP], check=True)

lst, starts, t = [], [], 0.0
for i, (src, ss, d, z0, z1) in enumerate(SHOTS):
    nfr = round(d * FPS)
    p = f"min(on/{max(nfr - 1, 1)},1)"
    ez = f"(1-(1-{p})*(1-{p}))" if z0 > z1 else f"({p})"  # zoom d'ingresso veloce che rallenta
    z = f"({z0}+({z1}-{z0})*{ez})"
    vf = (f"fps={FPS},scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase:flags=lanczos,crop={W * 2}:{H * 2},"
          f"zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps={FPS},setsar=1")
    if src == "MAP":
        inp = ["-i", MAP]
        vf = f"[0:v]format=rgba[m];color=c=0x0C1C2E:s={W}x{H}:r={FPS}[bg];[bg][m]overlay=shortest=1,setsar=1"
        cmd = ["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", vf]
    else:
        inp = ["-ss", f"{ss}", "-t", f"{d + 0.1}", "-i", f"{S}/{src}.mov"]
        cmd = ["ffmpeg", "-v", "error", "-y", *inp, "-vf", vf, "-an"]
    run(cmd + ["-frames:v", str(nfr), "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
               "-r", str(FPS), f"{OUT}/s{i}.mp4"])
    lst.append(f"file '{OUT}/s{i}.mp4'")
    starts.append(t)
    t += nfr / FPS
TOTAL = t
open(f"{OUT}/shots.txt", "w").write("\n".join(lst) + "\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/shots.txt", "-c", "copy",
     f"{OUT}/base.mp4"])
T_MAP = starts[4]
T_GYM = starts[7]

# ---------- audio ----------
sr = 48000


def load(path, tempo=None, trim=None):
    af = []
    if trim:
        af.append(f"atrim={trim[0]}:{trim[1]},asetpts=N/SR/TB,afade=t=in:d=0.02,"
                  f"afade=t=out:st={trim[1] - trim[0] - 0.03:.3f}:d=0.03")
    if tempo:
        af.append(f"atempo={tempo}")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path] + (["-af", ",".join(af)] if af else []) +
                         ["-ac", "2", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


def place(buf, x, t0, vol=1.0):
    i0 = int(t0 * sr)
    i1 = min(i0 + len(x), len(buf))
    buf[i0:i1] += x[:i1 - i0] * vol


def write(path, x):
    with wave.open(path, "wb") as wv:
        wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(sr)
        wv.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


n = int((TOTAL + 0.5) * sr)
voice = np.zeros((n, 2), np.float32)
for (a, b), at in zip(VOICE, V_AT):
    place(voice, load(f"{S}/voce.m4a", SP, (a, b)), at)
write(f"{OUT}/voce_raw.wav", voice)
run(["ffmpeg", "-v", "error", "-y", "-i", f"{OUT}/voce_raw.wav", "-af", "highpass=f=80,loudnorm=I=-14:TP=-1.5:LRA=9",
     "-ar", str(sr), f"{OUT}/voce_norm.wav"])
voice = load(f"{OUT}/voce_norm.wav")[:n]

sfx = np.zeros((n, 2), np.float32)
SFX = [
    (0.0, "whoosh", 0.35),                 # ingresso del selfie
    (starts[1] - 0.05, "swoosh", 0.25),    # si parte
    (starts[3] - 0.15, "aereo_decollo", 0.55),
    (T_MAP + 0.36, "aereo_atterraggio", 0.6),  # tonfo quando l'aereo arriva in India (~1.0 s nella cartina)
    (T_GYM - 0.08, "whoosh", 0.35),        # dentro la palestra
    (starts[11] + 0.1, "pop", 0.45),       # seguimi
]
for t0, nm, vol in SFX:
    place(sfx, load(f"{SFXD}/{nm}.wav"), max(t0, 0), vol)


def ass_t(x):
    x = max(x, 0)
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


Y = 1450  # sotto la metà, appena sotto la barba nei selfie (la faccia sta tra y 700 e 1380)


def ev(t0, t1, txt, y=Y, size=84, pop=True):
    fx = f"\\an5\\pos(540,{y})\\fs{size}"
    if pop:
        fx += "\\fscx85\\fscy85\\t(0,110,\\fscx104\\fscy104)\\t(110,190,\\fscx100\\fscy100)"
    return f"Dialogue: 1,{ass_t(t0)},{ass_t(t1)},Txt,,0,0,0,,{{{fx}}}{txt}"


def ass(events, path):
    open(path, "w").write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Txt,Inter ExtraBold,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,7,3,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(events) + "\n")


# versione voce: hook intero subito, poi pagine sincronizzate con la voce
w = {k: [wt(i, tt) for _, tt in ws] for k, (i, ws) in enumerate(WORDS)}
EV_V = [
    ev(0.0, w[0][6] + 0.45, "RIUSCIRÒ AD ALLENARMI\\NUN MESE IN INDIA?"),
    ev(w[1][0], w[2][0], "BEH, IO SONO\\NARRIVATO"),
    ev(w[2][0], w[2][4], "PROVERÒ TUTTE\\NLE PALESTRE"),
    ev(w[2][4], w[2][7], "SE VUOI\\NSCOPRIRLO:"),
    ev(w[2][7], TOTAL, "SEGUIMI", size=110),
]
# versione scritte: stessi momenti ma un po' più lunghe per poterle leggere
EV_S = [
    ev(0.0, T_MAP, "RIUSCIRÒ AD ALLENARMI\\NUN MESE IN INDIA?"),
    ev(starts[5], T_GYM, "BEH, IO SONO\\NARRIVATO"),
    ev(T_GYM, starts[10] + 0.3, "PROVERÒ TUTTE\\NLE PALESTRE"),
    ev(starts[10] + 0.3, starts[11] + 0.1, "SE VUOI\\NSCOPRIRLO:"),
    ev(starts[11] + 0.1, TOTAL, "SEGUIMI", size=110),
]

for name, events, mix in (("voce", EV_V, voice + sfx * 0.9), ("scritte", EV_S, sfx)):
    ass(events, f"{OUT}/subs_{name}.ass")
    write(f"{OUT}/audio_{name}.wav", mix * (1.0 if name == "voce" else 1.4))
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{OUT}/base.mp4", "-i", f"{OUT}/audio_{name}.wav", "-vf",
         f"ass={OUT}/subs_{name}.ass", "-af", "alimiter=limit=0.95", "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-t", f"{TOTAL:.3f}", f"{OUT}/reel_india_{name}.mp4"])
print("TOTAL", round(TOTAL, 2), [round(x, 2) for x in starts], {k: [round(x, 2) for x in v] for k, v in w.items()})
