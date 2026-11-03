#!/usr/bin/env python3
"""Schede editoriali del format "IG1": fondo scuro caldo, occhiello piccolo spaziato con trattino arancio, titolo
grande in serif (Instrument Serif, una parte in corsivo), grafiche a linee sottili bianche con accenti arancio,
B-roll opzionale in riquadro arrotondato. Ogni scheda è una funzione draw(im, t) e si esporta in mp4 1080x1920.
Le grafiche stanno tra y 280 e y 1300: sotto passano i sottotitoli standard (y ~1450)."""
import math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

R = "/home/user/video-maker"
W, H, FPS = 1080, 1920, 30
ORANGE, WHITE, MUTED = (232, 102, 44), (245, 240, 232), (170, 160, 150)
FS = f"{R}/assets/fonts/InstrumentSerif-Regular.ttf"
FSI = f"{R}/assets/fonts/InstrumentSerif-Italic.ttf"
FK = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FBI = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
_fc = {}


def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def eout(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def _bg():
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(-1, 1, W)[None, :]
    top, bot = np.array([30, 25, 22]), np.array([14, 12, 11])
    g = top[None, None, :] * (1 - y[..., None]) + bot[None, None, :] * y[..., None]
    vign = 1 - 0.35 * (x ** 2)[..., None]
    g = g * vign
    return Image.fromarray(np.clip(g, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


BG = None


def background():
    global BG
    if BG is None:
        BG = _bg()
    return BG.copy()


def spaced(d, xy, txt, f, fill, track=6, anchor="mm"):
    """testo con spaziatura tra le lettere (occhielli)."""
    widths = [f.getlength(c) for c in txt]
    tot = sum(widths) + track * (len(txt) - 1)
    x, y = xy
    x0 = x - tot / 2 if anchor == "mm" else x
    for c, w in zip(txt, widths):
        d.text((x0, y), c, font=f, fill=fill, anchor="lm")
        x0 += w + track
    return tot


def alpha(c, a):
    return c[:3] + (int(255 * max(0, min(1, a))),)


def header(im, t, kicker, title, y=300, t0=0.0, size=124):
    """occhiello "— KICKER" + titolo serif; title = lista di (testo, corsivo?) sulla stessa riga o "\n" per andare a capo."""
    d = ImageDraw.Draw(im)
    a = ease((t - t0) / 0.3)
    if a <= 0:
        return
    fk = font(FK, 26)
    tw = spaced(d, (-9999, -9999), kicker, fk, (0, 0, 0, 0))
    x0 = W / 2 - (tw + 56) / 2
    d.line([(x0, y), (x0 + 40 * eout((t - t0) / 0.4), y)], fill=alpha(ORANGE, a), width=3)
    spaced(d, (x0 + 56, y), kicker, fk, alpha(MUTED, a), anchor="lm")
    # titolo: righe separate da "\n", ogni riga lista di pezzi (testo, corsivo)
    lines, cur = [], []
    for txt, it in title:
        parts = txt.split("\n")
        for k, p in enumerate(parts):
            if k:
                lines.append(cur); cur = []
            if p:
                cur.append((p, it))
    lines.append(cur)
    yy = y + 40 + size * 0.55
    for j, ln in enumerate(lines):
        aj = ease((t - t0 - 0.08 - 0.1 * j) / 0.35)
        if aj <= 0:
            continue
        dy = 26 * (1 - eout((t - t0 - 0.08 - 0.1 * j) / 0.45))
        wtot = sum(font(FSI if it else FS, size).getlength(p) for p, it in ln)
        x = W / 2 - wtot / 2
        for p, it in ln:
            f = font(FSI if it else FS, size)
            d.text((x, yy + dy), p, font=f, fill=alpha(ORANGE if it else WHITE, aj), anchor="lm")
            x += f.getlength(p)
        yy += size * 1.0


def rounded_frame(im, frame, box, a=1.0, radius=28, border=(255, 255, 255, 60)):
    """incolla un fotogramma (PIL) ritagliato in un riquadro arrotondato con ombra."""
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = x1 - x0, y1 - y0
    fr = frame.convert("RGBA")
    s = max(w / fr.width, h / fr.height)
    fr = fr.resize((int(fr.width * s + 1), int(fr.height * s + 1)), Image.LANCZOS)
    fr = fr.crop(((fr.width - w) // 2, (fr.height - h) // 2, (fr.width - w) // 2 + w, (fr.height - h) // 2 + h))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=int(255 * a))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([x0 + 6, y0 + 18, x1 + 6, y1 + 18], radius, fill=(0, 0, 0, int(150 * a)))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))
    fr.putalpha(m)
    im.alpha_composite(fr, (x0, y0))
    ImageDraw.Draw(im).rounded_rectangle([x0, y0, x1, y1], radius, outline=alpha(border, a * border[3] / 255),
                                         width=2)


class ClipFrames:
    """legge i fotogrammi di una clip (verticale 1080x1920) a 30 fps da un certo secondo, con velocità."""

    def __init__(self, path, ss, dur, sp=1.0, w=540, h=960):
        self.w, self.h = w, h
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ss}", "-t", f"{dur * sp + 0.5}", "-i", path, "-vf",
                              f"setpts=PTS/{sp},fps={FPS},scale={w}:{h}:force_original_aspect_ratio=increase,"
                              f"crop={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True, check=True).stdout
        n = len(raw) // (w * h * 3)
        self.frames = np.frombuffer(raw, np.uint8)[:n * w * h * 3].reshape(n, h, w, 3)

    def at(self, t):
        k = min(max(int(t * FPS), 0), len(self.frames) - 1)
        return Image.fromarray(self.frames[k])


def export(draw, dur, out):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "fast",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for k in range(round(dur * FPS)):
        im = background()
        draw(im, k / FPS)
        p.stdin.write(im.convert("RGBA").tobytes())
    p.stdin.close(); p.wait()
