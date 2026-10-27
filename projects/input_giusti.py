#!/usr/bin/env python3
"""Serie "Input giusti" (4 reel: muscle up, trazioni, dip, squat).
Intro uguale per tutti ("input giusti per trasformare un'informazione in qualcosa di utile"), poi l'esercizio:
prima l'informazione tecnica (etichetta nera "L'INFORMAZIONE"), poi l'input da dare all'atleta (etichetta arancio
"L'INPUT GIUSTO"). Titolo in alto: [INPUT GIUSTI] + [ESERCIZIO] in arancio che entra quando lo nomino.
B-roll: i miei esercizi, neuroni (Pixabay) su "informazione", scheletro in squat (Pixabay) sul baricentro,
zoom con evidenziatore arancio sulla spalla per lo spazio subacromiale.
Uso: python3 projects/input_giusti.py [mu|trazioni|dip|squat ...]   (senza argomenti: tutti e 4)"""
import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R = "/home/user/video-maker"
S = f"{R}/src_input"
SFXD = f"{R}/sfx"
W, H, FPS, SP = 1080, 1920, 30, 1.1
TONEMAP = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
HDR = {"IMG_7636", "IMG_7607", "IMG_7642", "IMG_7650"}
ORANGE, BLACK = (232, 102, 44), (12, 12, 12)
FBI = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
OR, WH = "{\\c&H2C66E8&}", "{\\c&HFFFFFF&}"

INTRO = ("IMG_8550", 0.72, 3.48)
INTRO_PAGES = [(1.45, "PER TRASFORMARE\\NUN'INFORMAZIONE"), (2.58, f"IN QUALCOSA\\NDI {OR}UTILE")]
INTRO_BR = [(2.05, 2.58, "pix/p362123", 2.0, 1.0, 1.0, None)]  # "un'informazione": neuroni

# per ogni reel: parlato (clip, segmenti sorgente: nome, informazione, input), pagine sottotitoli (inizio sorgente,
# testo), B-roll (inizio, fine sorgente, file, inizio file, velocità, zoom, centro zoom), effetti grafici
REELS = {
    "mu": dict(
        name="MUSCLE UP", clip="IMG_8555", segs=[(0.46, 1.15), (1.30, 3.97), (13.48, 15.61)],
        pages=[(1.30, "ATTIVA IL DORSALE"), (2.38, "E NON EXTRARUOTARE\\NLE SPALLE"), (13.48, "GIÙ LA SBARRA"),
               (14.05, f"GOMITI VICINO,\\N{OR}SPALLE AVANTI!")],
        br=[(0.46, 2.38, "IMG_8335", 7.3, 1.25, 1.0, None),
            (14.05, 15.61, "IMG_7636", 1.75, 1.0, 1.0, None)]),
    "trazioni": dict(
        name="TRAZIONI", clip="IMG_8559", segs=[(0.45, 1.12), (1.26, 3.90), (15.32, 17.66)],
        pages=[(1.26, "SCAPOLE DEPRESSE"), (2.30, "AUMENTA LO SPAZIO\\NSUBACROMIALE"), (15.32, "GIÙ LA SBARRA"),
               (16.05, "VICINO, VICINO,\\NVICINO"), (17.0, f"{OR}GAMBE AVANTI")],
        br=[(0.45, 2.30, "IMG_8337", 0.3, 1.0, 1.0, None),
            (2.30, 3.90, "IMG_8335", 1.0, 1.0, 1.5, (650, 900)),
            (16.05, 17.66, "IMG_7607", 1.0, 1.3, 1.0, None)],
        glow=(2.30, 3.90, (525, 940))),  # spazio subacromiale: evidenziatore sulla spalla (nello zoom)
    "dip": dict(
        name="DIP", clip="IMG_8560", segs=[(0.48, 0.89), (1.01, 2.63), (4.91, 7.55)],
        pages=[(1.01, "ATTIVA I DEPRESSORI\\NSCAPOLARI"), (4.91, "FORTE CONTRO\\NLE PARALLELE"),
               (6.28, f"{OR}SPALLE AVANTI{WH}\\NE ADDOME DURO")],
        br=[(0.48, 2.63, "IMG_7642", 0.3, 1.0, 1.3, (330, 1150)),
            (6.28, 7.55, "IMG_8485", 1.9, 1.0, 1.0, None)]),
    "squat": dict(
        name="SQUAT", clip="IMG_8562", segs=[(0.20, 0.77), (1.09, 3.93), (9.35, 11.40)],
        pages=[(1.09, "RESPIRA COL DIAFRAMMA"), (2.42, "MANTIENI IL BARICENTRO\\NAL CENTRO"),
               (9.35, "RILASSA IL CARICO"), (10.38, f"{OR}PANCIA TRA LE GAMBE")],
        br=[(0.20, 2.42, "IMG_8492", 1.0, 1.0, 1.0, None),
            (2.42, 3.93, "pix/p302326", 0.0, 1.0, 1.0, None),
            (10.38, 11.40, "IMG_7650", 3.2, 1.0, 1.0, None)]),
}


def run(cmd):
    subprocess.run(cmd, check=True)


def snap(x):
    return round(x * FPS) / FPS


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def src_path(name):
    return f"{S}/{name}.mp4" if name.startswith("pix/") else f"{S}/{name}.mov"


def render_clip(src, ss, dur, sp, z, c, out):
    nfr = round(dur * FPS)
    pre = (TONEMAP + ",") if src in HDR else ""
    zf = ""
    if z != 1.0:
        cx, cy = c
        zf = f",crop={W / z:.0f}:{H / z:.0f}:{cx - W / z / 2:.0f}:{cy - H / z / 2:.0f},scale={W}:{H}:flags=lanczos"
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss}", "-t", f"{dur * sp + 0.3}", "-i", src_path(src),
         "-vf", f"{pre}setpts=PTS/{sp},fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
                f"crop={W}:{H}{zf},setsar=1,tpad=stop_mode=clone:stop_duration=1",
         "-an", "-frames:v", str(nfr), "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
         out])


def writer(path):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", path],
                            stdin=subprocess.PIPE)


def ass_t(x):
    x = max(x, 0)
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


def load(path, sr=48000):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


# ---------------- grafiche: titolo in alto e etichette sopra i sottotitoli ----------------
FT = ImageFont.truetype(FBI, 70)
FTAG = ImageFont.truetype(FBI, 46)


def box(txt, font, bg, padx, h):
    l, t, r, b = font.getbbox(txt)
    im = Image.new("RGBA", (r - l + 2 * padx, h), bg + (255,))
    ImageDraw.Draw(im).text(((r - l) / 2 + padx, h / 2 + 2), txt, font=font, fill=(255, 255, 255, 255), anchor="mm")
    return im


def scaled(im, s, a):
    if s <= 0 or a <= 0:
        return None
    im = im.resize((max(int(im.width * s), 1), max(int(im.height * s), 1)), Image.LANCZOS)
    if a < 1:
        im.putalpha(im.split()[3].point(lambda v: int(v * a)))
    return im


def pop(x):  # 0 -> 1.06 -> 1
    if x <= 0:
        return 0
    if x < 0.6:
        return 0.7 + 0.36 * ease(x / 0.6)
    return 1.06 - 0.06 * ease((x - 0.6) / 0.4)


def make_gfx(cfg, T, out):
    t_name, t_info, t_inp, t_end, glow = T["name"], T["info"], T["inp"], T["end"], T.get("glow")
    b1 = box("INPUT GIUSTI", FT, BLACK, 32, 100)
    b2 = box(cfg["name"], FT, ORANGE, 32, 100)
    gap = 12
    x1_alone = (W - b1.width) / 2
    x1_pair = (W - b1.width - gap - b2.width) / 2
    YT = 300  # centro della riga dei titoli (fascia 250-350)
    tag_i = box("L'INFORMAZIONE", FTAG, BLACK, 24, 70)
    tag_p = box("L'INPUT GIUSTO", FTAG, ORANGE, 24, 70)
    YG = 1280
    p = writer(out)
    for k in range(round(t_end * FPS)):
        tt = k / FPS
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        fade_t = 1 - ease((tt - (t_inp - 0.15)) / 0.15)  # il titolo esce quando arriva l'input
        if fade_t > 0:
            m = ease((tt - t_name) / 0.25)
            x1 = x1_alone + (x1_pair - x1_alone) * m
            s1 = pop(tt / 0.3)
            b = scaled(b1, s1, fade_t)
            if b:
                im.alpha_composite(b, (int(x1 + b1.width / 2 - b.width / 2), int(YT - b.height / 2)))
            if tt >= t_name:  # l'esercizio entra da destra
                x2 = x1_pair + b1.width + gap + 120 * (1 - m)
                b = scaled(b2, pop((tt - t_name) / 0.3), fade_t * min(m * 1.5, 1))
                if b:
                    im.alpha_composite(b, (int(x2 + b2.width / 2 - b.width / 2), int(YT - b.height / 2)))
        for tg, a0, a1 in ((tag_i, t_info, t_inp), (tag_p, t_inp, t_end + 1)):
            if a0 <= tt < a1:
                b = scaled(tg, pop((tt - a0) / 0.25), 1 - ease((tt - (a1 - 0.1)) / 0.1))
                if b:
                    im.alpha_composite(b, (int(W / 2 - b.width / 2), int(YG - b.height / 2)))
        if glow and glow[0] <= tt < glow[1]:  # evidenziatore arancio che pulsa sulla spalla
            g0, g1, (gx, gy) = glow
            e = ease((tt - g0 - 0.12) / 0.25) * (1 - ease((tt - (g1 - 0.12)) / 0.12))
            puls = 0.8 + 0.2 * math.sin((tt - g0) * 8)
            d = ImageDraw.Draw(im)
            for kk in range(6, 0, -1):
                rr = (40 + kk * 9) * (0.6 + 0.4 * e)
                d.ellipse([gx - rr, gy - rr, gx + rr, gy + rr], fill=ORANGE + (int(26 * e * puls),))
            rr = 70 * (0.6 + 0.4 * e)
            d.ellipse([gx - rr, gy - rr, gx + rr, gy + rr], outline=ORANGE + (int(255 * e),), width=7)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()


# ---------------- un reel ----------------
def build(key):
    cfg = REELS[key]
    OUT = f"{R}/out/input_giusti/{key}"
    os.makedirs(OUT, exist_ok=True)
    clip = cfg["clip"]
    SEGS = [(INTRO[0], INTRO[1], INTRO[2])] + [(clip, a, b) for a, b in cfg["segs"]]

    # parlato: un ffmpeg per segmento a 1.1x, concat, loudnorm
    lst, SO, t = [], [], 0.0
    for i, (f, a, b) in enumerate(SEGS):
        d = b - a
        nfr = round(d / SP * FPS)
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-t", f"{d + 0.1}", "-i", f"{S}/{f}.mov",
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
         "-af", "highpass=f=80,loudnorm=I=-14:TP=-1.5:LRA=9", "-c:a", "pcm_s16le", "-ar", "48000",
         f"{OUT}/talk.mov"])

    def ot(src, intro=False):
        """tempo sorgente -> tempo nel reel (intro o parlato dell'esercizio)."""
        for (f, a, b), s0 in zip(SEGS, SO):
            if (f == INTRO[0]) == intro and a - 0.2 <= src <= b + 0.05:
                return s0 + max(src - a, 0) / SP
        raise ValueError(src)

    # B-roll (+0.1 s di margine, anticipati di 0.02 s all'overlay)
    BR = []
    items = [(ot(a, True), ot(b, True), *rest) for a, b, *rest in INTRO_BR]
    items += [(ot(a), ot(b) if b < cfg["segs"][-1][1] else TOTAL, *rest) for a, b, *rest in cfg["br"]]
    for i, (t0, t1, src, ss, sp, z, c) in enumerate(items):
        t0, t1 = snap(t0), snap(t1)
        render_clip(src, ss, t1 - t0 + 0.1, sp, z, c, f"{OUT}/br{i}.mp4")
        BR.append((t0, t1, f"{OUT}/br{i}.mp4"))

    T = dict(name=SO[1], info=SO[2], inp=SO[3], end=TOTAL)
    if "glow" in cfg:
        g0, g1, xy = cfg["glow"]
        T["glow"] = (ot(g0), ot(g1), xy)
    make_gfx(cfg, T, f"{OUT}/gfx.mov")

    # sottotitoli standard (bianchi, bordo nero, y 1450); sul nome dell'esercizio parla il titolo
    starts = [(ot(a, True), txt) for a, txt in INTRO_PAGES] + [(ot(a), txt) for a, txt in cfg["pages"]]
    ends = [s for s, _ in starts[1:]] + [TOTAL]
    ends[len(INTRO_PAGES) - 1] = SO[1]
    POP = "\\fscx85\\fscy85\\t(0,110,\\fscx104\\fscy104)\\t(110,190,\\fscx100\\fscy100)"
    ev = [f"Dialogue: 1,{ass_t(a)},{ass_t(b)},Txt,,0,0,0,,{{\\an5\\pos(540,1450){POP}}}{txt}"
          for (a, txt), b in zip(starts, ends)]
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

    # effetti sonori leggeri
    sr = 48000
    mix = np.zeros((int((TOTAL + 1) * sr), 2), np.float32)
    SFX = [(0.0, "comparsa", 0.22), (T["name"] - 0.12, "whoosh", 0.28), (T["info"], "pop", 0.16),
           (T["inp"], "punto_3", 0.3)]
    SFX += [(t0 - 0.06, "swoosh", 0.06) for t0, _, _ in BR if abs(t0 - T["name"]) > 0.1]
    if "glow" in T:
        SFX.append((T["glow"][0] + 0.1, "punto_1", 0.22))
    for t0, nm, vol in SFX:
        x = load(f"{SFXD}/{nm}.wav")
        i0 = max(int(t0 * sr), 0)
        i1 = min(i0 + len(x), len(mix))
        mix[i0:i1] += x[:i1 - i0] * vol
    with wave.open(f"{OUT}/sfx.wav", "wb") as wv:
        wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(sr)
        wv.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())

    # montaggio finale
    inp = ["-i", f"{OUT}/talk.mov", "-i", f"{OUT}/sfx.wav", "-i", f"{OUT}/gfx.mov"]
    fc = ["[0:v]setpts=PTS-STARTPTS[v0]"]
    last = "v0"
    for i, (t0, t1, path) in enumerate(BR):
        inp += ["-i", path]
        fc.append(f"[{3 + i}:v]setpts=PTS-STARTPTS+{max(t0 - 0.02, 0):.4f}/TB[b{i}]")
        fc.append(f"[{last}][b{i}]overlay=eof_action=pass:enable='between(t,{t0 - 0.01:.4f},{t1 - 0.01:.4f})'[o{i}]")
        last = f"o{i}"
    fc.append(f"[2:v]setpts=PTS-STARTPTS[gx];[{last}][gx]overlay=eof_action=pass,ass={OUT}/subs.ass,format=yuv420p[v]")
    fc.append("[0:a][1:a]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[a]")
    name = f"{OUT}/reel_input_giusti_{key}.mp4"
    run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-t", f"{TOTAL:.3f}", name])
    # loudnorm a passata singola su clip così corte resta alto di 1-2 LU: correggo col guadagno misurato
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", name, "-af", "loudnorm=print_format=json",
                           "-f", "null", "-"], capture_output=True, text=True).stderr
    li = float(meas[meas.rindex("{"):].split('"input_i" : "')[1].split('"')[0])
    tmp = name.replace(".mp4", "_tmp.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-i", name, "-c:v", "copy", "-af", f"volume={-14 - li:.2f}dB",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", tmp])
    os.replace(tmp, name)
    print(key, "TOTAL", round(TOTAL, 2), "segmenti", [round(x, 2) for x in SO],
          "B-roll", [(round(a, 2), round(b, 2)) for a, b, _ in BR])


if __name__ == "__main__":
    for k in (sys.argv[1:] or list(REELS)):
        build(k)
