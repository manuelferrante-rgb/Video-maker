#!/usr/bin/env python3
"""Motore comune per i reel parlati (stile approvato): parlato a 1.1x tagliato a segmenti, B-roll in overlay,
titoli in alto in riquadri (Inter Black Italic, nero/arancio, con barra o numero), evidenziatore arancio,
sottotitoli standard, sfx leggeri, loudness -14 LUFS esatti.
I tempi si scrivono come (indice segmento, secondo nel file sorgente); il parlato ha +0.1 s di margine nei tagli.
Uso: da uno script di progetto, build(cfg) con cfg = dict(out, segs, pages, br, titles, sfx, glow, name)."""
import math, os, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R = "/home/user/video-maker"
SFXD = f"{R}/sfx"
W, H, FPS, SP = 1080, 1920, 30, 1.1
TONEMAP = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
ORANGE, BLACK = (232, 102, 44), (12, 12, 12)
FBI = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
OR, WH = "{\\c&H2C66E8&}", "{\\c&HFFFFFF&}"
FT = ImageFont.truetype(FBI, 70)


def run(cmd):
    subprocess.run(cmd, check=True)


def snap(x):
    return round(x * FPS) / FPS


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def is_hdr(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=color_transfer", "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return "arib-std-b67" in out


def render_clip(path, ss, dur, sp, z, c, out):
    nfr = round(dur * FPS)
    pre = (TONEMAP + ",") if is_hdr(path) else ""
    zf = ""
    if z != 1.0:
        cx, cy = c
        zf = f",crop={W / z:.0f}:{H / z:.0f}:{cx - W / z / 2:.0f}:{cy - H / z / 2:.0f},scale={W}:{H}:flags=lanczos"
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss}", "-t", f"{dur * sp + 0.3}", "-i", path,
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


def box(txt, bg, font=FT, padx=32, h=100):
    l, t, r, b = font.getbbox(txt)
    im = Image.new("RGBA", (int(r - l + 2 * padx), h), bg + (255,))
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


def build(cfg):
    OUT = cfg["out"]
    os.makedirs(OUT, exist_ok=True)
    SEGS = cfg["segs"]

    # ---- parlato: un ffmpeg per segmento a 1.1x, concat, loudnorm
    lst, SO, t = [], [], 0.0
    for i, (f, a, b) in enumerate(SEGS):
        d = b - a
        nfr = round(d / SP * FPS)
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-t", f"{d + 0.1}", "-i", f,
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

    def ot(spec):
        """(segmento, secondo sorgente) -> secondo nel reel; "end" = fine del reel."""
        if spec == "end":
            return TOTAL
        k, src = spec
        f, a, b = SEGS[k]
        return SO[k] + min(max(src - a, 0), b - a) / SP

    # ---- B-roll (+0.1 s di margine, anticipati di 0.02 s all'overlay)
    BR = []
    for i, (s0, s1, path, ss, sp, z, c) in enumerate(cfg["br"]):
        t0, t1 = snap(ot(s0)), snap(ot(s1))
        render_clip(path, ss, t1 - t0 + 0.1, sp, z, c, f"{OUT}/br{i}.mp4")
        BR.append((t0, t1, f"{OUT}/br{i}.mp4"))

    # ---- grafiche: righe di titoli in alto (con barra animata o numero), evidenziatore
    YT = 300
    rows = []
    for tt in cfg.get("titles", []):
        boxes = []
        for it in tt["items"]:
            boxes.append(box(it[0], ORANGE if it[1] == "o" else BLACK, padx=26 if len(it[0]) <= 2 else 32))
        strike = ot(tt["strike"]) if "strike" in tt else None
        rows.append((ot(tt["t0"]), ot(tt["t1"]), boxes, strike))
    glows = [(ot(g0), ot(g1), xy) for g0, g1, xy in cfg.get("glow", [])]
    p = writer(f"{OUT}/gfx.mov")
    for k in range(round(TOTAL * FPS)):
        tt = k / FPS
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for t0, t1, boxes, strike in rows:
            if not (t0 <= tt < t1):
                continue
            fade = 1 - ease((tt - (t1 - 0.12)) / 0.12)
            gap = 12
            wtot = sum(b.width for b in boxes) + gap * (len(boxes) - 1)
            x = (W - wtot) / 2
            for j, b in enumerate(boxes):
                sb = scaled(b, pop((tt - t0 - 0.08 * j) / 0.3), fade)
                if sb:
                    im.alpha_composite(sb, (int(x + b.width / 2 - sb.width / 2), int(YT - sb.height / 2)))
                x += b.width + gap
            if strike is not None and tt >= strike:  # barra arancio che attraversa l'ultimo riquadro
                b = boxes[-1]
                xs = (W - wtot) / 2 + wtot - b.width - 10
                e = ease((tt - strike) / 0.22)
                d.line([(xs, YT + 26), (xs + (b.width + 20) * e, YT - 26)], fill=ORANGE + (int(255 * fade),),
                       width=14)
        for g0, g1, (gx, gy) in glows:
            if not (g0 <= tt < g1):
                continue
            e = ease((tt - g0 - 0.12) / 0.25) * (1 - ease((tt - (g1 - 0.12)) / 0.12))
            puls = 0.8 + 0.2 * math.sin((tt - g0) * 8)
            for kk in range(6, 0, -1):
                rr = (40 + kk * 9) * (0.6 + 0.4 * e)
                d.ellipse([gx - rr, gy - rr, gx + rr, gy + rr], fill=ORANGE + (int(26 * e * puls),))
            rr = 70 * (0.6 + 0.4 * e)
            d.ellipse([gx - rr, gy - rr, gx + rr, gy + rr], outline=ORANGE + (int(255 * e),), width=7)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()

    # ---- sottotitoli standard (bianchi, bordo nero, y 1450); il parlato è continuo: ogni pagina resta fino
    #      alla successiva
    pages = [(ot(s), txt) for s, txt in cfg["pages"]]
    ev = []
    POP = "\\fscx85\\fscy85\\t(0,110,\\fscx104\\fscy104)\\t(110,190,\\fscx100\\fscy100)"
    for i, (a, txt) in enumerate(pages):
        b = pages[i + 1][0] if i + 1 < len(pages) else TOTAL
        ev.append(f"Dialogue: 1,{ass_t(a)},{ass_t(b)},Txt,,0,0,0,,{{\\an5\\pos(540,1450){POP}}}{txt}")
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

    # ---- effetti sonori leggeri
    sr = 48000
    mix = np.zeros((int((TOTAL + 1) * sr), 2), np.float32)
    SFX = [(ot(s) + dt, nm, vol) for s, dt, nm, vol in cfg.get("sfx", [])]
    SFX += [(t0 - 0.06, "swoosh", 0.06) for t0, _, _ in BR]
    for t0, nm, vol in SFX:
        x = load(f"{SFXD}/{nm}.wav")
        i0 = max(int(t0 * sr), 0)
        i1 = min(i0 + len(x), len(mix))
        mix[i0:i1] += x[:i1 - i0] * vol
    with wave.open(f"{OUT}/sfx.wav", "wb") as wv:
        wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(sr)
        wv.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())

    # ---- montaggio finale
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
    name = f"{OUT}/{cfg['name']}.mp4"
    run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-t", f"{TOTAL:.3f}", name])
    # loudnorm a passata singola su clip corte resta alto di 1-2 LU: correggo col guadagno misurato
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", name, "-af", "loudnorm=print_format=json",
                           "-f", "null", "-"], capture_output=True, text=True).stderr
    li = float(meas[meas.rindex("{"):].split('"input_i" : "')[1].split('"')[0])
    tmp = name.replace(".mp4", "_tmp.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-i", name, "-c:v", "copy", "-af", f"volume={-14 - li:.2f}dB",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", tmp])
    os.replace(tmp, name)
    print(cfg["name"], "TOTAL", round(TOTAL, 2), "segmenti", [round(x, 2) for x in SO],
          "B-roll", [(round(a, 2), round(b, 2)) for a, b, _ in BR])
    return TOTAL
