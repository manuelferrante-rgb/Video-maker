#!/usr/bin/env python3
"""Reel "non prendere aria a ogni ripetizione" (panca).
Hook su di me, "ad ogni ripetizione" sulle ripetizioni in panca, "ci hanno sempre consigliato il contrario" su una
scheda col consiglio classico che viene barrato, poi la clip del campione del mondo con la traduzione, B-roll sulle
condizioni (tante ripetizioni, setting), chiusura in camera con la domanda. Sottotitoli standard, effetti leggeri.
Uso: python3 projects/respiro_panca.py"""
import math, os, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

R = "/home/user/Video-maker"
S = f"{R}/src_next"
OUT = f"{R}/out/respiro"
SFXD = f"{R}/sfx"
os.makedirs(OUT, exist_ok=True)
W, H, FPS, SP = 1080, 1920, 30, 1.1
ORANGE, NAVY_D = (232, 102, 44), (10, 26, 44)
FBI = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"


def run(cmd):
    subprocess.run(cmd, check=True)


# ---------------- parlato (file, inizio, fine); "GAP" = pausa muta per la clip del campione ----------------
GAP = 1.9
SEGS = [("IMG_8368", 0.00, 2.92),    # non prendere aria ad ogni ripetizione
        ("IMG_8368", 3.85, 6.22),    # sembra assurdo, ci hanno sempre consigliato il contrario
        ("IMG_8368", 6.95, 9.15),    # eppure il campione del mondo di powerlifting
        ("IMG_8368", 14.62, 15.47),  # dice questo
        ("GAP", 0, GAP),             # la clip del campione parla da sola
        ("IMG_8369", 0.00, 3.00),    # va contestualizzato quando abbiamo tante ripetizioni da fare
        ("IMG_8369", 4.66, 6.50),    # e riusciamo a mantenere un ottimo setting
        ("IMG_8369", 10.03, 11.73),  # magari non lo consiglierei a tutti
        ("IMG_8369", 14.80, 15.89)]  # e tu, cosa ne pensi?
ZOOM = {0: (1.12, 1.0), 8: (1.0, 1.1)}  # punch d'ingresso sull'hook, leggero zoom sulla domanda finale
FACE = (540, 600)

lst, SO, t = [], [], 0.0
for i, (f, a, b) in enumerate(SEGS):
    if f == "GAP":
        nfr = round(GAP * FPS)
        run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}", "-f", "lavfi",
             "-i", "anullsrc=r=48000:cl=stereo", "-frames:v", str(nfr), "-t", f"{nfr / FPS:.4f}", "-c:v", "libx264",
             "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", f"{OUT}/t{i}.mov"])
    else:
        d = b - a
        nfr = round(d / SP * FPS)
        zf = ""
        if i in ZOOM:
            z0, z1 = ZOOM[i]
            pp = f"min(on/{nfr - 1},1)"
            ez = f"(1-(1-{pp})*(1-{pp}))" if z0 > z1 else f"({pp})"
            zf = (f",scale={W * 2}:{H * 2}:flags=lanczos,zoompan=z='{z0}+({z1}-{z0})*{ez}'"
                  f":x='max(0,min(iw-iw/zoom,{FACE[0] * 2}-iw/zoom/2))':y='max(0,min(ih-ih/zoom,{FACE[1] * 2}-ih/zoom/2))'"
                  f":d=1:s={W}x{H}:fps={FPS}")
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-t", f"{d + 0.1}", "-i", f"{S}/{f}.MOV",
             "-vf", f"setpts=PTS/{SP},fps={FPS},scale={W}:{H}{zf},setsar=1",
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


def w(k, src):
    """parola del segmento k (tempo sorgente del modello) -> tempo nel reel."""
    _, a, _ = SEGS[k]
    return SO[k] + max(src + 0.08 - a, 0) / SP


def snap(x):
    return round(x * FPS) / FPS


# ---------------- B-roll ----------------
def render_clip(src, ss, dur, out, sp=1.0):
    nfr = round(dur * FPS)
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss}", "-t", f"{dur * sp + 0.3}", "-i", src,
         "-vf", f"setpts=PTS/{sp},fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
                f"crop={W}:{H},setsar=1,tpad=stop_mode=clone:stop_duration=1",
         "-an", "-frames:v", str(nfr), "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p", out])


CHAMP = f"{S}/b_2a21b11a.mp4"
BENCH_A, BENCH_B = f"{S}/b_IMG_8061_a.mov", f"{S}/b_IMG_8061_b.mov"
T_CHAMP0 = w(2, 7.44)                      # "campione": parte la clip
T_CHAMP1 = SO[5]                           # fino a quando riprendo a parlare
T_X0, T_X1 = w(1, 4.52), SO[2]             # "ci hanno sempre consigliato il contrario": scheda barrata
B = [
    (w(0, 1.56), SO[1], BENCH_B, 0.2),     # "ad ogni ripetizione": ripetizioni in panca
    (T_CHAMP0, T_CHAMP1, CHAMP, 0.0),      # campione del mondo
    (w(5, 1.52), SO[6], BENCH_A, 0.0),     # "tante ripetizioni da fare"
    (SO[6], SO[7], BENCH_B, 1.2),          # "ottimo setting"
]
BR = []
for i, (t0, t1, src, ss) in enumerate(B):
    t0, t1 = snap(t0), snap(t1)
    render_clip(src, ss, t1 - t0 + 0.1, f"{OUT}/br{i}.mp4")  # qualche fotogramma in più: niente buchi agli stacchi
    BR.append((t0, t1, f"{OUT}/br{i}.mp4"))

# scheda "il consiglio classico" barrato: sfondo panca sfocato e scurito
render_clip(BENCH_A, 1.0, 0.04, f"{OUT}/xbg.mp4")
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{OUT}/xbg.mp4", "-frames:v", "1", "-f", "rawvideo",
                      "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
XBG = Image.frombytes("RGB", (W, H), raw).filter(ImageFilter.GaussianBlur(26)).convert("RGBA")
XBG.alpha_composite(Image.new("RGBA", (W, H), NAVY_D + (165,)))


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def label_img(txt, size, box=(0, 0, 0), fg=(255, 255, 255)):
    ft = ImageFont.truetype(FBI, size)
    l, tt, r, b = ft.getbbox(txt)
    pw, ph = 30, 16
    im = Image.new("RGBA", (r - l + pw * 2, b - tt + ph * 2), box + (255,))
    ImageDraw.Draw(im).text((pw - l, ph - tt), txt, font=ft, fill=fg)
    return im


L1, L2 = label_img("RESPIRA", 104), label_img("AD OGNI RIPETIZIONE", 80, box=ORANGE)
TAG = label_img("CAMPIONE DEL MONDO", 66, box=ORANGE)


def gfx(tt):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if T_X0 <= tt < T_X1:  # consiglio classico che viene barrato
        im = XBG.copy()
        e = ease((tt - T_X0) / 0.18)
        y0 = 700
        for k, L in enumerate((L1, L2)):
            sc = 0.85 + 0.15 * e
            Ls = L.resize((int(L.width * sc), int(L.height * sc)), Image.LANCZOS)
            Ls.putalpha(Ls.split()[3].point(lambda v: int(v * e)))
            im.alpha_composite(Ls, (int(W / 2 - Ls.width / 2), int(y0 + k * 150 - (Ls.height - L.height) / 2)))
        s = ease((tt - (T_X0 + 0.45)) / 0.22)  # linea che barra
        if s > 0:
            d = ImageDraw.Draw(im)
            x0, x1 = 140, 140 + (W - 280) * s
            d.line([(x0, 880), (x1, 760)], fill=ORANGE + (255,), width=22)
            d.line([(x0, 880), (x1, 760)], fill=(255, 255, 255, 255), width=6)
    if T_CHAMP0 <= tt < T_CHAMP1:  # etichetta sulla clip del campione
        e = ease((tt - T_CHAMP0) / 0.2)
        T = TAG.copy()
        T.putalpha(T.split()[3].point(lambda v: int(v * e)))
        im.alpha_composite(T, (int(W / 2 - T.width / 2), int(300 - 20 * (1 - e))))
    return im


p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r",
                      str(FPS), "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", f"{OUT}/gfx.mov"],
                     stdin=subprocess.PIPE)
for k in range(round(TOTAL * FPS)):
    p.stdin.write(gfx(k / FPS).tobytes())
p.stdin.close(); p.wait()

# ---------------- sottotitoli (standard: bianchi, bordo nero, niente riquadro, y 1450) ----------------


def ass_t(x):
    x = max(x, 0)
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


OR, WH = "{\\c&H2C66E8&}", "{\\c&HFFFFFF&}"
PAGES = [
    (0.0, SO[1], f"NON PRENDERE ARIA\\NAD {OR}OGNI{WH} RIPETIZIONE"),
    (SO[1], w(1, 4.52), "SEMBRA ASSURDO"),
    (w(1, 4.52), SO[2], "CI HANNO SEMPRE\\NCONSIGLIATO IL CONTRARIO"),
    (SO[2], SO[3], "EPPURE IL CAMPIONE DEL\\NMONDO DI POWERLIFTING"),
    (SO[3], SO[4] + 0.15, "DICE QUESTO:"),
    (SO[4] + 0.15, SO[5], f"\"SMETTI DI RIPRENDERE FIATO\\NA {OR}OGNI{WH} RIPETIZIONE\""),
    (SO[5], SO[6], "VA CONTESTUALIZZATO:\\NTANTE RIPETIZIONI DA FARE"),
    (SO[6], SO[7], "E UN OTTIMO SETTING\\NDA MANTENERE"),
    (SO[7], SO[8], "MAGARI NON LO\\NCONSIGLIEREI A TUTTI"),
    (SO[8], TOTAL, "E TU, COSA NE PENSI?"),
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
Style: Txt,Inter ExtraBold,78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,7,3,5,40,40,0,1

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
SFX = [(0.0, "whoosh", 0.3), (T_X0, "swoosh", 0.25), (T_X0 + 0.45, "hit", 0.45), (T_CHAMP0 - 0.05, "whoosh", 0.3),
       (SO[4] + 0.15, "pop", 0.35), (SO[8], "pop", 0.3)]
SFX += [(t0 - 0.06, "swoosh", 0.2) for t0, _, p_ in BR if p_ != f"{OUT}/br1.mp4"]
for t0, nm, vol in SFX:
    x = load(f"{SFXD}/{nm}.wav")
    i0 = max(int(t0 * sr), 0)
    i1 = min(i0 + len(x), len(mix))
    mix[i0:i1] += x[:i1 - i0] * vol
with wave.open(f"{OUT}/sfx.wav", "wb") as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(sr)
    wv.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())

# ---------------- montaggio finale ----------------
inp = ["-i", f"{OUT}/talk.mov", "-i", f"{OUT}/sfx.wav", "-i", f"{OUT}/gfx.mov"]
fc = ["[0:v]setpts=PTS-STARTPTS[v0]"]
last = "v0"
for i, (t0, t1, path) in enumerate(BR):
    inp += ["-i", path]
    fc.append(f"[{3 + i}:v]setpts=PTS-STARTPTS+{t0:.4f}/TB[b{i}]")
    fc.append(f"[{last}][b{i}]overlay=eof_action=pass:enable='between(t,{t0:.4f},{t1 - 0.001:.4f})'[o{i}]")
    last = f"o{i}"
fc.append(f"[2:v]setpts=PTS-STARTPTS[gx];[{last}][gx]overlay=eof_action=pass,ass={OUT}/subs.ass,format=yuv420p[v]")
fc.append("[0:a][1:a]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]")
run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
     "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", "-t", f"{TOTAL:.3f}", f"{OUT}/reel_respiro_panca.mp4"])
print("TOTAL", round(TOTAL, 2), [round(x, 2) for x in SO], "B-roll", [(round(a, 2), round(b, 2)) for a, b, _ in BR],
      "X", round(T_X0, 2), round(T_X1, 2))
