#!/usr/bin/env python3
"""Reel "THIS IS STREETLIFTING" (novembre 2026): edit hype sui 4 esercizi di Manuel (muscle up, chin up, dip, squat)
nello stile dei riferimenti in Drive (cartella "Riferimenti"): intro in bianco e nero con flash negativi e battito,
drop a colori sul beat, stacchi a tempo, punch-in, flash, raffica finale, chiusura "THIS IS STREETLIFTING".
Musica originale `sfx/make_phonk.py` (130 BPM, tutto il montaggio e' a tempo sulle sue battute).

V2 (feedback Manuel): niente intro lenta (solo 2 beat di preparazione), niente ripetizioni, tutto "tremato" e a
jump-cut come la raffica, ogni alzata completa, ~15.7 s cosi' il finale lo vedono tutti.
Due versioni (stessa durata, cambia solo la grafica):
  A = scritte degli esercizi (MUSCLE UP / CHIN UP / DIP / SQUAT) + THIS IS STREETLIFTING
  B = solo THIS IS STREETLIFTING alla fine
Sorgenti: Drive 1Ko5w_pQKPRjSpGm9DkB8uOMUMCLhHmxh -> src_sl/raw/IMG_71xx.MOV (HLG, ruotati -90).
Uso: python3 projects/this_is_streetlifting.py [A|B|all]"""
import os, sys, subprocess, json
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

R = "/home/user/video-maker"
sys.path.insert(0, f"{R}/sfx")
from make_phonk import make_phonk, SR  # noqa: E402

W, H, FPS = 1080, 1920, 30
SRC = f"{R}/src_sl/raw"
OUT = f"{R}/out/this_is_streetlifting"
TMP = f"{OUT}/tmp"
ANTON = f"{R}/models/Anton-Regular.ttf"
ORANGE = np.array([232, 102, 44], np.float32)
# Clip iPhone HLG: il tonemap zscale (mobius/hable) gonfiava i colori (pareti rosa, pelle rossa, viola acceso = "si vede
# che era HDR", feedback di Manuel). Base piu' naturale: leggere l'HLG come SDR (solo matrice bt2020 -> bt709),
# poi il look cinematografico di grade().
TONEMAP = "scale=in_color_matrix=bt2020:out_color_matrix=bt709:in_range=tv:out_range=tv"

BPM = 130
BEAT = 60 / BPM
BAR = 4 * BEAT
S16 = BEAT / 4
T_DROP = 2 * BEAT          # 0.92: intro di un attimo (preparazione allo squat), poi subito il drop
T_STOP = T_DROP + 6 * BAR   # 12.0
T_HIT = T_STOP + BAR        # 13.85
DUR = T_STOP + 3.7          # 15.7


def b(n):  # tempo della n-esima battuta (beat) dall'inizio
    return n * BEAT


def rep(beat0, file, src0, cuts, per=2):
    """un'alzata COMPLETA a velocita' reale, spezzata in jump-cut ogni `per` beat con zoom diversi.
    cuts: lista di (z, cx, cy) per ogni pezzo; il tempo sorgente scorre continuo."""
    out = []
    for k, (z, cx, cy) in enumerate(cuts):
        t0, t1 = b(beat0 + k * per), b(beat0 + (k + 1) * per)
        out.append((t0, t1, file, src0 + (t0 - b(beat0)), 1.0, z, z * 1.04, cx, cy, "col"))
    return out


# (t0, t1, file, src_start, speed, z0, z1, cx, cy, look)   look: bw / col
# Ordine fisso (Manuel): muscle up -> chin up -> dip -> squat, ogni esercizio una volta sola (niente ripetizioni).
SHOTS = (
    [(b(0), b(2), "IMG_7178", 6.0, 1.0, 1.3, 1.45, 0.56, 0.30, "bw")]            # entra sotto il bilanciere
    + rep(2, "IMG_7167", 5.35, [(1.15, 0.42, 0.40), (1.45, 0.52, 0.33), (1.2, 0.50, 0.36), (1.5, 0.55, 0.33)])
    + rep(10, "IMG_7171", 1.95, [(1.15, 0.40, 0.42), (1.5, 0.42, 0.30)])
    + rep(14, "IMG_7163", 3.6, [(1.25, 0.33, 0.66), (1.55, 0.32, 0.68)])
    + rep(18, "IMG_7178", 24.6, [(1.1, 0.55, 0.50), (1.35, 0.57, 0.47), (1.6, 0.60, 0.52), (1.2, 0.56, 0.47)])
    # chiusura: cammina verso la camera, rallentato, colore sul colpo con THIS IS STREETLIFTING
    + [(b(26), DUR, "IMG_7167", 10.0, 0.8, 1.0, 1.14, 0.50, 0.42, "bw_then_col")]
)

LABELS = [  # solo versione A: (t0, t1, testo), una volta per esercizio
    (b(2) + 0.05, b(10) - 0.2, "MUSCLE UP"),
    (b(10) + 0.03, b(14) - 0.2, "CHIN UP"),
    (b(14) + 0.03, b(18) - 0.2, "DIP"),
    (b(18) + 0.03, b(26) - 0.2, "SQUAT"),
]
FINAL = [(T_STOP + 2 * BEAT, "THIS IS", 112, 1180), (T_HIT, "STREETLIFTING", 168, 1330)]
LABEL_Y = 1330

CUTS = [s[0] for s in SHOTS[1:]]
PUNCH = sorted(set(CUTS[:-1] + [T_HIT]))
NEG = [b(1), b(10), b(14), b(18)]
TINT = [b(1) + 2 * S16, b(6), b(22)]
WHITE = [T_DROP, T_HIT]
SHAKE = [(T_DROP, T_STOP, 8)]
WHIP = [b(10), b(14), b(18), b(26)]


def decode(sh):
    t0, t1, f, s0, sp = sh[:5]
    n = int(round(t1 * FPS)) - int(round(t0 * FPS))
    need = n / FPS * sp + 0.2
    vf = TONEMAP
    if sp != 1.0:
        vf += f",setpts=PTS/{sp},minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:vsbmc=1"
    vf += f",fps={FPS},scale={W}:{H}"
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{s0:.3f}", "-t", f"{need:.3f}", "-i", f"{SRC}/{f}.MOV",
           "-vf", vf, "-pix_fmt", "rgb24", "-f", "rawvideo", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    if len(fr) < n:
        fr = np.concatenate([fr, np.repeat(fr[-1:], n - len(fr), 0)])
    return fr[:n]


def text_img(txt, size, track=4):
    font = ImageFont.truetype(ANTON, size)
    widths = [font.getbbox(c)[2] for c in txt]
    tw = sum(widths) + track * (len(txt) - 1)
    pad = 60
    im = Image.new("L", (tw + 2 * pad, size + 2 * pad), 0)
    d = ImageDraw.Draw(im)
    x = pad
    for c, w_ in zip(txt, widths):
        d.text((x, pad - font.getbbox("H")[1] + 10), c, font=font, fill=255)
        x += w_ + track
    a = np.asarray(im, np.float32) / 255
    glow = np.asarray(im.filter(ImageFilter.GaussianBlur(18)), np.float32) / 255
    shadow = np.asarray(im.filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
    return a, glow, shadow


TXT_CACHE = {}


def draw_text(img, txt, size, cy, age):
    """testo bianco Anton con alone, pop d'ingresso (scala 1.25 -> 1 in 4 fotogrammi), primo fotogramma RGB split."""
    key = (txt, size)
    if key not in TXT_CACHE:
        TXT_CACHE[key] = text_img(txt, size)
    a, glow, shadow = TXT_CACHE[key]
    k = min(1.0, age * FPS / 4)
    sc = 1.25 - 0.25 * (1 - (1 - k) ** 2)
    if sc != 1.0:
        hh, ww = a.shape
        nw, nh = int(ww * sc), int(hh * sc)
        a, glow, shadow = (cv2.resize(m, (nw, nh), interpolation=cv2.INTER_LINEAR) for m in (a, glow, shadow))
    hh, ww = a.shape
    x0, y0 = W // 2 - ww // 2, int(cy - hh // 2)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + ww), min(H, y0 + hh)
    sl = (slice(ya - y0, yb - y0), slice(xa - x0, xb - x0))
    reg = img[ya:yb, xa:xb]
    sh = shadow[sl][..., None] * 0.8
    reg *= (1 - sh)
    reg += glow[sl][..., None] * 0.25 * 255 * np.array([1.0, 0.92, 0.85])
    al = a[sl][..., None]
    if age < 1.5 / FPS:  # split RGB sul primo fotogramma
        for ch, dx in ((0, -10), (2, 10)):
            m = np.roll(a[sl], dx, axis=1)
            reg[..., ch] = reg[..., ch] * (1 - m) + 255 * m
    reg[:] = reg * (1 - al) + 255 * al
    np.clip(reg, 0, 255, out=reg)


VIG = None


def vignette():
    global VIG
    if VIG is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
        VIG = (1 - 0.55 * np.clip((r - 0.35) / 0.65, 0, 1) ** 1.6)[..., None].astype(np.float32)
    return VIG


def near(t, events, win):
    for e in events:
        if 0 <= t - e < win:
            return t - e
    return None


def grade(img):
    """look cinematografico come i riferimenti (i clip sono HDR: prima tonemap, poi questo): neri profondi,
    contrasto a S, saturazione contenuta (le luci viola della palestra si calmano), ombre fredde e luci calde."""
    x = img / 255
    lum = x @ np.float32([0.299, 0.587, 0.114])
    # saturazione: -15%, e piu' bassa sui viola/blu saturi
    purple = np.clip((x[..., 2] - x[..., 1]) * 2.2, 0, 1)
    sat = 0.85 - 0.35 * purple
    x = lum[..., None] + (x - lum[..., None]) * sat[..., None]
    # curva: punto del nero, S marcata
    x = np.clip((x - 0.035) / 0.965, 0, 1)
    x = 0.5 + 0.5 * np.tanh(1.7 * (x - 0.52)) / np.tanh(0.85)
    x = np.clip(x, 0, 1) ** 1.12  # medi piu' scuri, atmosfera da gara
    # split toning: ombre teal, luci calde
    l2 = (x @ np.float32([0.299, 0.587, 0.114]))[..., None]
    sh_w = np.clip(1 - l2 / 0.45, 0, 1)
    hi_w = np.clip((l2 - 0.55) / 0.45, 0, 1)
    x = x + sh_w * np.float32([-0.035, 0.012, 0.03]) + hi_w * np.float32([0.04, 0.012, -0.03])
    return np.clip(x, 0, 1) * 255


def process(fr, t, u, sh, rng):
    _, _, _, _, _, z0, z1, cx, cy, look = sh
    z = z0 + (z1 - z0) * u
    for p in PUNCH:
        if 0 <= t - p < 0.6:
            z *= 1 + 0.075 * np.exp(-(t - p) / 0.11)
    dx = dy = 0.0
    for a_, b_, amp in SHAKE:
        if a_ <= t < b_:
            dx, dy = rng.normal(0, amp, 2)
    hw, hh = W / (2 * z), H / (2 * z)
    px = np.clip(cx * W, hw, W - hw)
    py = np.clip(cy * H, hh, H - hh)
    M = np.float32([[z, 0, W / 2 - z * px + dx], [0, z, H / 2 - z * py + dy]])
    img = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # mosso verticale sugli stacchi "whip" (2 fotogrammi prima e dopo)
    for c in WHIP:
        d = t - c
        if -2.5 / FPS < d < 2.5 / FPS:
            k = int(90 * (1 - abs(d) * FPS / 2.5)) | 1
            img = cv2.blur(img, (1, max(3, k)))
    img = img.astype(np.float32)
    bw = look == "bw" or (look == "bw_then_col" and t < T_HIT)
    if bw:
        g = img @ np.float32([0.299, 0.587, 0.114])
        g = 255 * (g / 255) ** (1 / 1.2)
        g = np.clip((g - 128) * 1.18 + 128, 0, 255)
        img = np.repeat(g[..., None], 3, 2)
    else:
        img = grade(img)
    if near(t, TINT, 1.5 / FPS) is not None:   # B/N virato arancio scuro (come i flash rossi dei riferimenti)
        g = img @ np.float32([0.299, 0.587, 0.114]) / 255
        img = (g[..., None] ** 0.9) * ORANGE * 1.15
    if near(t, NEG, 1.5 / FPS) is not None:
        img = 255 - img
        sh_ = 8
        img[..., 0] = np.roll(img[..., 0], sh_, axis=1)
        img[..., 2] = np.roll(img[..., 2], -sh_, axis=1)
    img *= vignette()
    wd = near(t, WHITE, 0.25)
    if wd is not None:
        a = np.exp(-wd / 0.07)
        img = img * (1 - a) + 255 * a
    img += rng.normal(0, 5, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1).astype(np.float32)
    return img


def render(version):
    os.makedirs(TMP, exist_ok=True)
    music = f"{TMP}/music.wav"
    _, info = make_phonk(music, bpm=BPM, intro_beats=2, main_bars=6, tail=DUR - T_STOP)
    assert abs(info["drop"] - T_DROP) < 1e-6 and abs(info["hit"] - T_HIT) < 1e-6
    silent = f"{TMP}/video_{version}.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
                            "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                            "-colorspace", "bt709", silent], stdin=subprocess.PIPE)
    rng = np.random.default_rng(3)
    labels = LABELS if version == "A" else []
    for sh in SHOTS:
        fr = decode(sh)
        n0 = int(round(sh[0] * FPS))
        for i, f in enumerate(fr):
            t = (n0 + i) / FPS
            u = i / max(1, len(fr) - 1)
            img = process(f, t, u, sh, rng)
            for a_, b_, txt in labels:
                if a_ <= t < b_:
                    draw_text(img, txt, 128, LABEL_Y, t - a_)
            for ta, txt, size, y in FINAL:
                if t >= ta:
                    draw_text(img, txt, size, y, t - ta)
            if t > DUR - 0.35:  # dissolvenza a nero, la scritta resta
                k = (t - (DUR - 0.35)) / 0.35
                img *= 1 - 0.75 * k
            enc.stdin.write(np.clip(img, 0, 255).astype(np.uint8).tobytes())
        print(f"  {version}: shot {sh[2]} @ {sh[0]:.2f}s ok", flush=True)
    enc.stdin.close()
    enc.wait()
    # audio: musica + whoosh leggeri sugli stacchi whip, loudness -14 LUFS (guadagno misurato + limiter)
    mix = f"{TMP}/mix.wav"
    sfx = [(c - 0.18, f"{R}/sfx/whoosh.wav", 0.12) for c in WHIP]
    inputs = ["-i", music]
    flt = []
    for k, (t, f, v) in enumerate(sfx):
        inputs += ["-i", f]
        flt.append(f"[{k + 1}]volume={v},adelay={int(t * 1000)}|{int(t * 1000)}[s{k}]")
    flt.append("[0]" + "".join(f"[s{k}]" for k in range(len(sfx))) +
               f"amix=inputs={len(sfx) + 1}:normalize=0,atrim=0:{DUR:.3f}[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(flt), "-map", "[a]",
                    "-ar", str(SR), mix], check=True)
    meas = subprocess.run(["ffmpeg", "-i", mix, "-af", "ebur128", "-f", "null", "-"], capture_output=True,
                          text=True).stderr
    lufs = float(meas.split("Integrated loudness:")[1].split("I:")[1].split("LUFS")[0])
    gain = -14.0 - lufs
    final = f"{OUT}/this_is_streetlifting_{version}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", mix, "-filter_complex",
                    f"[1]volume={gain:.2f}dB,alimiter=limit=0.94:level=0[a]", "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", final],
                   check=True)
    print("ok", final, f"(gain {gain:+.1f} dB)")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for v in (["A", "B"] if which == "all" else [which]):
        render(v)
