#!/usr/bin/env python3
"""Monta un reel 9:16 (1080x1920): video di sfondo + busto scontornato + sottotitoli karaoke.

Uso:  python3 make_reel.py progetto.json

Il progetto JSON descrive i segmenti parlati (clip, taglio, parole con tempi) e quale
porzione dello sfondo mostrare sotto ogni segmento. Vedi projects/streetlifting_635.json.
"""
import json, os, subprocess, sys
import numpy as np, cv2, onnxruntime as ort

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))

# HLG iPhone -> SDR mantenendo il colore della pelle (hable lo rendeva pallido)
HDR_TO_SDR = ("zscale=t=linear:npl=150,format=gbrpf32le,zscale=p=bt709,"
              "tonemap=mobius:param=0.3:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
              "eq=saturation=1.15:contrast=1.05")


def probe_hdr(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=color_transfer", "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return out.strip() in ("arib-std-b67", "smpte2084")


def read_frames(path, start, dur, w, h, speed=1.0, fit="cover"):
    """Decodifica [start, start+dur*speed] di path, accelerato di `speed`, in frame BGR w x h."""
    vf = []
    if probe_hdr(path):
        vf.append(HDR_TO_SDR)
    if speed != 1.0:
        vf.append(f"setpts=PTS/{speed}")
    if fit == "cover":
        vf.append(f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}")
    else:
        vf.append(f"scale={w}:{h}")
    vf.append(f"fps={FPS}")
    n = int(round(dur * FPS))
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{start}", "-t", f"{dur * speed + 0.5}", "-i", path,
           "-vf", ",".join(vf), "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    if len(frames) < n:  # allunga l'ultimo frame se la sorgente finisce prima
        frames = np.concatenate([frames, np.repeat(frames[-1:], n - len(frames), 0)])
    return frames


class Matter:
    """Scontorno persona con U^2-Net human seg + smoothing temporale."""

    def __init__(self, model):
        self.sess = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
        self.inp = self.sess.get_inputs()[0].name

    def mask(self, bgr):
        x = cv2.resize(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), (320, 320)).astype(np.float32) / 255.0
        x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
        x = x.transpose(2, 0, 1)[None].astype(np.float32)
        m = self.sess.run(None, {self.inp: x})[0][0, 0]
        m = (m - m.min()) / max(m.max() - m.min(), 1e-6)
        return cv2.resize(m, (bgr.shape[1], bgr.shape[0]), interpolation=cv2.INTER_LINEAR)

    def run(self, frames):
        alphas, prev = [], None
        for f in frames:
            a = self.mask(f)
            prev = a if prev is None else 0.6 * a + 0.4 * prev
            a = np.clip((prev - 0.15) / 0.7, 0, 1)            # contrasto sul bordo
            # vicino al bordo togli i pixel chiari e poco saturi (muro bianco dietro capelli/spalle)
            core = cv2.erode((a > 0.5).astype(np.uint8), np.ones((31, 31), np.uint8)).astype(np.float32)
            core = cv2.GaussianBlur(core, (0, 0), 6)
            hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(np.float32) / 255.0
            wall = np.clip((hsv[..., 2] - 0.55) / 0.15, 0, 1) * np.clip((0.22 - hsv[..., 1]) / 0.1, 0, 1)
            a = a * (1 - wall * (1 - core))
            a = cv2.erode(a, np.ones((3, 3), np.uint8))
            a = cv2.GaussianBlur(a, (0, 0), 1.0)               # bordo morbido
            alphas.append(a.astype(np.float32))
        return alphas


def ease_out(t):
    return 1 - (1 - min(max(t, 0), 1)) ** 3


def layout_at(keys, t, tr):
    """Interpola (cx, cy, larghezza, opacita', punch) tra i keyframe di layout."""
    prev = keys[0][1]
    cur, t0 = prev, keys[0][0]
    for kt, lay in keys:
        if kt > t:
            break
        prev, cur, t0 = cur, lay, kt
    u = min(max((t - t0) / tr, 0), 1) if cur is not prev else 1.0
    if cur.get("hidden"):
        e = u ** 2  # esce accelerando verso il basso
        cx, cy, wid = prev["cx"], prev["cy"] + (H * 0.75) * e, prev["w"] * (1 - 0.3 * e)
        return cx, cy, wid, 1 - e, 1.0
    if prev.get("hidden"):
        prev = dict(cur, cy=cur["cy"] + H * 0.6)
    e = ease_out(u)
    lerp = lambda x, y: x + (y - x) * e
    # piccolo "punch" (overshoot) quando entra un layout grande
    pk = 1 + cur.get("punch", 0) * np.sin(np.pi * u) if u < 1 else 1.0
    return lerp(prev["cx"], cur["cx"]), lerp(prev["cy"], cur["cy"]), lerp(prev["w"], cur["w"]), 1.0, pk


def bg_blur_fill(frames, letterbox, strip_y=None):
    """Per uno sfondo con bande nere: striscia nitida al centro + copia sfocata a tutto schermo."""
    y0, y1 = letterbox
    out = []
    for f in frames:
        strip = f[int(y0 * H):int(y1 * H)]
        blur = cv2.resize(strip, (W, H), interpolation=cv2.INTER_LINEAR)
        blur = cv2.GaussianBlur(blur, (0, 0), 30)
        blur = (blur * 0.55).astype(np.uint8)
        sh = strip.shape[0]
        big = cv2.resize(strip, (int(W * 1.15), int(sh * 1.15)))  # un po' di zoom sulla striscia
        x = (big.shape[1] - W) // 2
        big = big[:, x:x + W]
        yy = (H - big.shape[0]) // 2 - 120 if strip_y is None else int(strip_y)
        blur[yy:yy + big.shape[0]] = big
        out.append(blur)
    return out


def ass_time(t):
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def build_ass(pages, style, path):
    s = style
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{s['font']},{s['size']},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,{s.get('spacing', 1)},0,1,{s['outline']},{s['shadow']},2,60,60,{s['margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    hl = s["highlight"]  # RRGGBB
    hl_ass = f"&H00{hl[4:6]}{hl[2:4]}{hl[0:2]}&"
    lines = []
    for words, pend in pages:
        for i, (w, t0) in enumerate(words):
            t1 = words[i + 1][1] if i + 1 < len(words) else pend
            txt = " ".join((f"{{\\c{hl_ass}}}{x}{{\\c&H00FFFFFF&}}" if j == i else x)
                           for j, (x, _) in enumerate(words))
            pop = "{\\fscx108\\fscy108\\t(0,90,\\fscx100\\fscy100)}" if i == 0 else ""
            lines.append(f"Dialogue: 0,{ass_time(t0)},{ass_time(t1)},Sub,,0,0,0,,{pop}{txt}")
    open(path, "w").write(head + "\n".join(lines) + "\n")


def paginate(words, max_words, max_chars):
    pages, cur = [], []
    for w in words:
        if cur and (len(cur) >= max_words or len(" ".join(x for x, _ in cur + [w])) > max_chars):
            pages.append(cur)
            cur = []
        cur.append(w)
    if cur:
        pages.append(cur)
    return pages


def main(cfg_path):
    cfg = json.load(open(cfg_path))
    base = os.path.dirname(os.path.abspath(cfg_path))
    P = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    speed = cfg.get("speed", 1.0)
    out = P(cfg["output"])
    tmp = out + ".work"
    os.makedirs(tmp, exist_ok=True)
    matter = Matter(P(cfg["matting_model"]))
    bust = cfg["bust"]
    layouts = cfg["layouts"]
    keys = []

    pages_all, audio_parts, t_out = [], [], 0.0
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "medium",
                            "-pix_fmt", "yuv420p", f"{tmp}/video.mp4"], stdin=subprocess.PIPE)

    for si, seg in enumerate(cfg["segments"]):
        src = P(seg["clip"])
        a, b = seg["cut"]
        dur = (b - a) / speed
        nfr = int(round(dur * FPS))
        dur = nfr / FPS
        print(f"[{si + 1}/{len(cfg['segments'])}] {os.path.basename(src)} {dur:.2f}s", flush=True)

        # busto a piena risoluzione, poi posizionato con keyframe di layout
        sp = read_frames(src, a, dur, W, H, speed, fit="cover")
        alphas = matter.run(sp)

        # sfondo: lista di (file, start, dur_out) in sequenza
        bg = []
        for part in seg["background"]:
            n = int(round(part["dur"] * FPS)) if "dur" in part else nfr - len(bg)
            fr = list(read_frames(P(part["file"]), part["start"], n / FPS + 0.05, W, H, part.get("speed", 1.0)))[:n]
            if "letterbox" in part:
                fr = bg_blur_fill(fr, part["letterbox"], part.get("strip_y"))
            bg += fr
        bg = (bg + [bg[-1]] * nfr)[:nfr]

        # keyframe: [[t_sorgente, layout], ...] -> tempi in uscita
        lay = seg["layout"] if isinstance(seg["layout"], list) else [[a, seg["layout"]]]
        for ts, name in lay:
            keys.append((t_out + max(ts - a, 0) / speed, layouts[name]))

        for k in range(nfr):
            t = t_out + k / FPS
            cx, cy, wid, op, pk = layout_at(keys, t, cfg.get("transition", 0.22))
            if op <= 0.01:
                frame = bg[k].astype(np.float32)
            else:
                sway = bust.get("sway", 8) * np.sin(2 * np.pi * t / 2.6)
                bob = bust.get("bob", 5) * np.sin(2 * np.pi * t / 1.9)
                sc = wid / W * (1 + bust.get("zoom", 0.03) * (k / max(nfr, 1)))
                ax, ay = W * bust["anchor"][0], H * bust["anchor"][1]
                M = cv2.getRotationMatrix2D((ax, ay), np.sin(2 * np.pi * t / 3.1) * bust.get("tilt", 1.0), sc * pk)
                M[0, 2] += cx + sway - ax
                M[1, 2] += cy + bob - ay
                fg = cv2.warpAffine(sp[k], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
                al = cv2.warpAffine(alphas[k], M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0) * op
                frame = bg[k].astype(np.float32)
                sh = cv2.GaussianBlur(al, (0, 0), 18)[..., None]  # ombra morbida dietro il busto
                al = al[..., None]
                frame *= 1 - 0.35 * sh
                frame = frame * (1 - al) + fg.astype(np.float32) * al
            enc.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())

        # audio del segmento
        ap = f"{tmp}/a{si}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(b - a), "-i", src, "-map", "0:a:0",
                        "-af", f"atempo={speed},afade=t=in:d=0.02,afade=t=out:st={max(dur - 0.03, 0)}:d=0.03,"
                               "aresample=48000", "-ac", "2", "-t", f"{dur}", ap], check=True)
        audio_parts.append(ap)

        # parole -> tempi in uscita
        words = [(w, t_out + max(ts - a, 0) / speed) for w, ts in seg["words"]]
        for pg in paginate(words, cfg["subs"].get("max_words", 3), cfg["subs"].get("max_chars", 18)):
            pages_all.append(pg)
        t_out += dur

    enc.stdin.close()
    enc.wait()

    # fine di ogni pagina = inizio della successiva (o fine video)
    pages = []
    for i, pg in enumerate(pages_all):
        end = pages_all[i + 1][0][1] if i + 1 < len(pages_all) else t_out
        pages.append((pg, end))
    build_ass(pages, cfg["subs"], f"{tmp}/subs.ass")

    with open(f"{tmp}/alist.txt", "w") as f:
        f.writelines(f"file '{p}'\n" for p in audio_parts)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/alist.txt",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", f"{tmp}/audio.wav"], check=True)
    fontsdir = os.path.dirname(P(cfg["subs"]["font_file"]))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{tmp}/video.mp4", "-i", f"{tmp}/audio.wav",
                    "-vf", f"ass={tmp}/subs.ass:fontsdir={fontsdir}", "-c:v", "libx264", "-crf", "18",
                    "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-shortest", out], check=True)
    print(f"OK -> {out} ({t_out:.2f}s)")


if __name__ == "__main__":
    main(sys.argv[1])
