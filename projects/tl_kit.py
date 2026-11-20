#!/usr/bin/env python3
"""Motore a TIMELINE per i reel del 20/11 (trazioni in 30 s, panca linea sul palmo, tempo in palestra).
Diverso da reel_kit (guidato dal parlato): qui i tempi sono secondi del reel. Ogni fotogramma si compone in Python:
clip (con punch-in animato), grafiche PIL disegnate sopra, testi con pop, cronometro digitale a 7 segmenti.
Audio: voce opzionale (segmenti a 1,1x, -14 LUFS) + sfx leggeri.

shots  = [dict(t0, t1, src, ss, sp=1.0, z0=1.0, z1=1.0, c=(540, 960), hdr=None)]   (c = centro dello zoom)
layers = [fn(im, t)]  disegnano sull'immagine RGBA del fotogramma
sfx    = [(t, nome, volume)]
voice  = [(t_reel, file, da, a)]  (opzionale; ogni pezzo a 1,1x)
"""
import math, os, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

R = "/home/user/Video-maker"
SFXD = f"{R}/sfx"
W, H, FPS, SP = 1080, 1920, 30, 1.1
ORANGE, BLACK, WHITE, RED = (232, 102, 44), (12, 12, 12), (255, 255, 255), (255, 38, 38)
F_EB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
F_BI = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
TONEMAP = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
_fonts = {}


def font(path, size):
    k = (path, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(path, size)
    return _fonts[k]


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def pop(x):  # 0 -> 1.07 -> 1
    if x <= 0:
        return 0
    if x < 0.55:
        return 0.72 + 0.35 * ease(x / 0.55)
    return 1.07 - 0.07 * ease((x - 0.55) / 0.45)


def is_hdr(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=color_transfer", "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return "arib-std-b67" in out


# ------------------------------------------------------------------ clip
class Clip:
    """Legge i fotogrammi di un pezzo di clip già a 1080x1920 (riempie e ritaglia)."""

    def __init__(self, path, ss, n, sp=1.0, hdr=None, vf_extra="", fit="cover", mi=False):
        hdr = is_hdr(path) if hdr is None else hdr
        pre = (TONEMAP + ",") if hdr else ""
        if mi:  # rallenty fluido
            pre += f"setpts=PTS/{sp},minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:vsbmc=1,"
            sp_ = 1.0
        else:
            sp_ = sp
        if fit == "cover":
            sc = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}"
        else:
            sc = f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,pad={W}:{H}:-1:-1"
        vf = f"{pre}setpts=PTS/{sp_},fps={FPS},{sc},setsar=1{vf_extra},tpad=stop_mode=clone:stop_duration=6"
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{ss}", "-t", f"{n / FPS * sp + 0.5}",
                                   "-i", path, "-vf", vf, "-an", "-frames:v", str(n), "-f", "rawvideo",
                                   "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL)
        self.last = None

    def read(self):
        b = self.p.stdout.read(W * H * 3)
        if len(b) == W * H * 3:
            self.last = Image.frombuffer("RGB", (W, H), b, "raw", "RGB", 0, 1)
        return self.last

    def close(self):
        self.p.stdout.close()
        self.p.wait()


def shot_z(sh, t):
    u = min(max((t - sh["t0"]) / max(sh["t1"] - sh["t0"], 1e-3), 0), 1)
    return sh.get("z0", 1.0) + (sh.get("z1", 1.0) - sh.get("z0", 1.0)) * (ease(u) if sh.get("ez") else u)


def map_pt(p, z, c):
    """Punto del fotogramma sorgente (1080x1920) -> punto a schermo dopo lo zoom."""
    cx, cy = c
    w, h = W / z, H / z
    x0 = min(max(cx - w / 2, 0), W - w)
    y0 = min(max(cy - h / 2, 0), H - h)
    return ((p[0] - x0) * z, (p[1] - y0) * z)


def aa(im, box, fn, ss=3):
    """Disegno antialias: fn(draw, P) su una toppa 3x; P(x, y) converte coordinate schermo -> toppa."""
    x0, y0, x1, y1 = [int(v) for v in box]
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, W), min(y1, H)
    if x1 <= x0 or y1 <= y0:
        return
    patch = Image.new("RGBA", ((x1 - x0) * ss, (y1 - y0) * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(patch)
    fn(d, lambda x, y: ((x - x0) * ss, (y - y0) * ss), ss)
    im.alpha_composite(patch.resize((x1 - x0, y1 - y0), Image.LANCZOS), (x0, y0))


def zoom(im, z, c):
    if abs(z - 1) < 1e-3:
        return im
    cx, cy = c
    w, h = W / z, H / z
    x0 = min(max(cx - w / 2, 0), W - w)
    y0 = min(max(cy - h / 2, 0), H - h)
    return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))


# ------------------------------------------------------------------ testo
def text_img(txt, size=84, fpath=F_EB, stroke=7, color=WHITE, hi=ORANGE, spacing=8, maxw=940, shadow=True,
             align="center"):
    """Testo bianco con bordo nero; le parole tra *asterischi* in arancio. '\n' = a capo forzato."""
    f = font(fpath, size)
    lines = []
    for para in txt.split("\n"):
        words, cur = para.split(" "), []
        for w_ in words:
            test = " ".join(cur + [w_]).replace("*", "")
            if cur and f.getlength(test) > maxw:
                lines.append(cur)
                cur = [w_]
            else:
                cur.append(w_)
        lines.append(cur)
    lh = size * 1.12 + spacing
    widths = [f.getlength(" ".join(l).replace("*", "")) for l in lines]
    wi = int(max(widths) + 2 * stroke + 24)
    hi_ = int(lh * len(lines) + 2 * stroke + 24)
    im = Image.new("RGBA", (wi, hi_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for li, (l, lw) in enumerate(zip(lines, widths)):
        x = (wi - lw) / 2 if align == "center" else stroke + 12
        y = stroke + 12 + li * lh
        for w_ in l:
            orange = w_.startswith("*") or w_.endswith("*")
            ww = w_.replace("*", "")
            d.text((x, y), ww, font=f, fill=(hi if orange else color) + (255,), stroke_width=stroke,
                   stroke_fill=(0, 0, 0, 255))
            x += f.getlength(ww + " ")
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        sh.putalpha(im.split()[3].point(lambda v: int(v * 0.45)))
        sh = sh.filter(ImageFilter.GaussianBlur(6))
        out = Image.new("RGBA", (wi, hi_ + 6), (0, 0, 0, 0))
        out.alpha_composite(sh, (0, 6))
        out.alpha_composite(im, (0, 0))
        im = out
    return im


def label_img(txt, bg=BLACK, size=66, padx=30, h=None, fpath=F_BI, fg=WHITE):
    f = font(fpath, size)
    l, t, r, b = f.getbbox(txt)
    h = h or int(size * 1.45)
    im = Image.new("RGBA", (int(r - l + 2 * padx), h), bg + (255,))
    ImageDraw.Draw(im).text(((r - l) / 2 + padx, h / 2 + 2), txt, font=f, fill=fg + (255,), anchor="mm")
    return im


def put(im, src, cx, cy, s=1.0, a=1.0):
    if s <= 0 or a <= 0:
        return
    if s != 1:
        src = src.resize((max(int(src.width * s), 1), max(int(src.height * s), 1)), Image.LANCZOS)
    if a < 1:
        src = src.copy()
        src.putalpha(src.split()[3].point(lambda v: int(v * a)))
    im.alpha_composite(src, (int(cx - src.width / 2), int(cy - src.height / 2)))


def popped(img_or_fn, t0, t1, cx, cy, dur_in=0.28, dur_out=0.14, still=False):
    """Layer: immagine che entra con pop a t0 ed esce in dissolvenza a t1."""
    cache = {}

    def fn(im, t):
        if not (t0 <= t < t1):
            return
        src = cache.setdefault(0, img_or_fn() if callable(img_or_fn) else img_or_fn)
        s = 1.0 if still else pop((t - t0) / dur_in)
        a = 1 - ease((t - (t1 - dur_out)) / dur_out)
        put(im, src, cx, cy, s, a)
    return fn


# ------------------------------------------------------------------ cronometro 7 segmenti
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
       "7": "abc", "8": "abcdefg", "9": "abcdfg"}


def seg_digit(d, ch, x, y, w, h, th, on, off):
    """Cifra a 7 segmenti con angolo in alto a sinistra (x, y)."""
    sk = 0.12 * h  # leggera inclinazione
    def P(px, py):  # inclina
        return (x + px + sk * (1 - py / h), y + py)
    g = -th * 0.3
    hs = [("a", 0, 0), ("g", 0, h / 2), ("d", 0, h)]
    vs = [("f", 0, 0), ("b", w, 0), ("e", 0, h / 2), ("c", w, h / 2)]
    for name, px, py in hs:
        pts = [P(px + g + th / 2, py), P(px + g + th, py - th / 2), P(px + w - g - th, py - th / 2),
               P(px + w - g - th / 2, py), P(px + w - g - th, py + th / 2), P(px + g + th, py + th / 2)]
        d.polygon(pts, fill=on if name in SEG[ch] else off)
    for name, px, py in vs:
        L = h / 2
        pts = [P(px, py + g + th / 2), P(px + th / 2, py + g + th), P(px + th / 2, py + L - g - th),
               P(px, py + L - g - th / 2), P(px - th / 2, py + L - g - th), P(px - th / 2, py + g + th)]
        d.polygon(pts, fill=on if name in SEG[ch] else off)


def timer_img(s, dh=120, color=RED, box=True):
    """Immagine del cronometro: s = stringa tipo '00:12' o '3:00:00'."""
    w, th = dh * 0.52, dh * 0.15
    gap, colw = dh * 0.3, dh * 0.26
    widths = [colw if ch == ":" else w + gap for ch in s]
    tw = sum(widths) - gap + th * 1.6 + dh * 0.12
    pad = dh * 0.32
    im = Image.new("RGBA", (int(tw + 2 * pad), int(dh + 2 * pad)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if box:
        d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=int(dh * 0.18), fill=(8, 8, 8, 200))
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    x = pad + th
    on, off = color + (255,), (38, 14, 14, 255)
    for ch, cw in zip(s, widths):
        if ch == ":":
            r = th * 0.55
            for yy in (pad + dh * 0.3, pad + dh * 0.72):
                for dd in (gd, d):
                    dd.ellipse([x + cw / 2 - r, yy - r, x + cw / 2 + r, yy + r], fill=on)
        else:
            seg_digit(gd, ch, x, pad, w, dh, th, on, (0, 0, 0, 0))
            seg_digit(d, ch, x, pad, w, dh, th, on, off)
        x += cw
    glow = glow.filter(ImageFilter.GaussianBlur(dh * 0.08))
    glow.putalpha(glow.split()[3].point(lambda v: int(v * 0.8)))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(im)
    out.alpha_composite(glow)
    return out


# ------------------------------------------------------------------ audio
def load(path, sr=48000):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


def voice_piece(path, a, b, sr=48000):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a}", "-t", f"{b - a}", "-i", path, "-map", "0:a:0",
                          "-af", f"atempo={SP},afade=t=in:d=0.02,areverse,afade=t=in:d=0.04,areverse",
                          "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


def lufs(path):
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "loudnorm=print_format=json",
                           "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(meas[meas.rindex("{"):].split('"input_i" : "')[1].split('"')[0])


# ------------------------------------------------------------------ build
def build(out, total, shots, layers, sfx=(), voice=(), sfx_target=-20.0, cut_swoosh=0.05):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    N = round(total * FPS)
    tmpv = out.replace(".mp4", "_v.mp4")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "medium",
                            "-pix_fmt", "yuv420p", "-movflags", "+faststart", tmpv], stdin=subprocess.PIPE)
    shots = sorted(shots, key=lambda s: s["t0"])
    cur, clip = None, None
    for k in range(N):
        t = k / FPS
        sh = next((s for s in shots if s["t0"] <= t + 1e-6 < s["t1"]), shots[-1])
        if sh is not cur:
            if clip:
                clip.close()
            n = round((sh["t1"] - sh["t0"]) * FPS) + 2
            clip = Clip(sh["src"], sh["ss"], n, sh.get("sp", 1.0), sh.get("hdr"), sh.get("vf", ""),
                        sh.get("fit", "cover"), sh.get("mi", False))
            cur = sh
        live = sh.get("live")  # secondi di clip "viva", poi fermo immagine sull'ultimo fotogramma letto
        fr = clip.last if (live is not None and t - sh["t0"] >= live and clip.last is not None) else clip.read()
        u = (t - sh["t0"]) / max(sh["t1"] - sh["t0"], 1e-3)
        z = shot_z(sh, t)
        fr = zoom(fr, z, sh.get("c", (540, 960)))
        if sh.get("pre"):
            fr = sh["pre"](fr, t)
        im = fr.convert("RGBA")
        for fn in layers:
            fn(im, t)
        enc.stdin.write(im.convert("RGB").tobytes())
    clip.close()
    enc.stdin.close(); enc.wait()

    # audio
    sr = 48000
    L = int((total + 1) * sr)
    vo = np.zeros((L, 2), np.float32)
    for t0, path, a, b in voice:
        x = voice_piece(path, a, b)
        i0 = int(t0 * sr); i1 = min(i0 + len(x), L)
        vo[i0:i1] += x[:i1 - i0]
    fx = np.zeros((L, 2), np.float32)
    allsfx = list(sfx) + [(s["t0"] - 0.05, "swoosh", cut_swoosh) for s in shots[1:] if cut_swoosh]
    for t0, nm, vol in allsfx:
        x = load(f"{SFXD}/{nm}.wav")
        i0 = max(int(t0 * sr), 0); i1 = min(i0 + len(x), L)
        fx[i0:i1] += x[:i1 - i0] * vol

    def wav(path, a):
        with wave.open(path, "wb") as wv:
            wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(sr)
            wv.writeframes((np.clip(a[:int(total * sr)], -1, 1) * 32767).astype(np.int16).tobytes())
    base = out.replace(".mp4", "")
    if len(voice):
        wav(base + "_vo.wav", vo)
        g = -14 - lufs(base + "_vo.wav")
        vo *= 10 ** (g / 20)
        mixa = vo + fx
    elif not np.any(fx):  # reel muto senza effetti: traccia silenziosa (la musica la mette Manuel)
        mixa = fx
    else:  # reel muto: solo sfx leggeri, livello basso (la musica la mette Manuel)
        wav(base + "_fx.wav", fx)
        g = sfx_target - lufs(base + "_fx.wav")
        mixa = fx * 10 ** (g / 20)
    peak = np.abs(mixa).max()
    if peak > 0.89:
        mixa *= 0.89 / peak
    wav(base + "_mix.wav", mixa)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmpv, "-i", base + "_mix.wav", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    for f_ in (tmpv, base + "_vo.wav", base + "_fx.wav", base + "_mix.wav"):
        if os.path.exists(f_):
            os.remove(f_)
    print(out, "durata", total, "LUFS", lufs(out) if np.any(mixa) else "silenzio")


def sheet(video, out, n=24, cols=8):
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                             capture_output=True, text=True).stdout)
    rows = math.ceil(n / cols)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf",
                    f"fps={n}/{d},scale=270:-2,drawtext=fontfile={F_EB}:text='%{{pts\\:flt}}':x=4:y=4:fontsize=18:"
                    f"fontcolor=yellow:box=1:boxcolor=black,tile={cols}x{rows}", "-frames:v", "1", out], check=True)


def subs(pages, y=1450, size=76, maxw=960):
    """Sottotitoli standard: [(t0, t1, testo)], parola chiave tra *asterischi* in arancio, pop d'ingresso."""
    cache = {}

    def fn(im, t):
        for i, (a, b, txt) in enumerate(pages):
            if a <= t < b:
                src = cache.setdefault(i, text_img(txt, size=size, maxw=maxw))
                put(im, src, 540, y, pop((t - a) / 0.2) if not txt.startswith("§") else 1)
    return fn


def arrow(d, P, ss, pts, prog, color=WHITE, width=8, head=26, accent=ORANGE):
    """Freccia che si disegna lungo una polilinea (prog 0..1), punta arancio."""
    segs = list(zip(pts[:-1], pts[1:]))
    lens = [math.dist(a, b) for a, b in segs]
    tot, todo = sum(lens), sum(lens) * prog
    last, ang = pts[0], 0
    for (a, b), l in zip(segs, lens):
        if todo <= 0:
            break
        f = min(todo / l, 1)
        e = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        d.line([P(*a), P(*e)], fill=color + (255,), width=width * ss)
        d.ellipse([P(a[0] - width / 2, a[1] - width / 2), P(a[0] + width / 2, a[1] + width / 2)], fill=color + (255,))
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        last, todo = e, todo - l
    if prog > 0.05:
        x, y = last
        h = head
        p1 = (x + h * math.cos(ang), y + h * math.sin(ang))
        p2 = (x + h * 0.9 * math.cos(ang + 2.5), y + h * 0.9 * math.sin(ang + 2.5))
        p3 = (x + h * 0.9 * math.cos(ang - 2.5), y + h * 0.9 * math.sin(ang - 2.5))
        d.polygon([P(*p1), P(*p2), P(*p3)], fill=accent + (255,))


def dot(d, P, ss, x, y, r, s=1.0, color=ORANGE):
    """Puntino arancio con bordo bianco (s = scala del pop)."""
    if s <= 0:
        return
    R_ = (r + 5) * s
    d.ellipse([P(x - R_, y - R_), P(x + R_, y + R_)], fill=(255, 255, 255, 255))
    R_ = r * s
    d.ellipse([P(x - R_, y - R_), P(x + R_, y + R_)], fill=color + (255,))


def xmark(d, P, ss, x, y, r, prog, color=(230, 40, 40), width=16):
    for k_, (a, b) in enumerate((((-1, -1), (1, 1)), ((1, -1), (-1, 1)))):
        f = min(max(prog * 2 - k_, 0), 1)
        if f <= 0:
            continue
        p0 = (x + a[0] * r, y + a[1] * r)
        p1 = (p0[0] + (b[0] - a[0]) * r * f, p0[1] + (b[1] - a[1]) * r * f)
        d.line([P(*p0), P(*p1)], fill=color + (255,), width=width * ss)


def placeholder(label):
    """Fermo d'attesa per le riprese ancora da registrare (solo anteprima)."""
    img = label_img(label, (60, 60, 60), size=40)

    def fn(im, t):
        put(im, img, 540, 900)
    return fn
