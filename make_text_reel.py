#!/usr/bin/env python3
"""Reel senza voce: solo b-roll + testo a schermo (la musica la aggiunge Manuel su Instagram).

Uso:  python3 make_text_reel.py progetto.json

JSON: "background" come in make_reel (file/start/dur/crop/zoom/...), "beats" = lista di
{"t": [inizio, fine], "lines": ["RIGA CON *PAROLA", ...], "size": 92, "y": 1250, "punch": true}.
Le parole con * su riquadro azzurro, il resto nero su riquadro bianco. Ogni beat entra con un pop.
"""
import json, os, subprocess, sys
import numpy as np, cv2
import make_reel as m

W, H, FPS = m.W, m.H, m.FPS


def main(cfg_path):
    cfg = m.load_cfg(cfg_path)
    base = os.path.dirname(os.path.abspath(cfg_path))
    out = os.path.join(base, cfg["output"])
    tmp = out + ".work"
    os.makedirs(tmp, exist_ok=True)
    total = cfg["duration"]
    nfr = int(round(total * FPS))

    # sfondo: stessa logica di make_reel (zoom/punch inclusi)
    frames = []
    for part in cfg["background"]:
        n = int(round(part["dur"] * FPS)) if "dur" in part else nfr - len(frames)
        fr = list(m.read_frames(part["file"], part["start"], n / FPS + 0.05, W, H, part.get("speed", 1.0),
                                crop=part.get("crop")))[:n]
        if "zoom" in part:
            z0, z1 = part["zoom"]
            cx, cy = part.get("zoom_center", [0.5, 0.5])
            for i in range(len(fr)):
                u = i / max(len(fr) - 1, 1)
                u = m.ease_out(u) if part.get("zoom_ease") == "punch" else u
                z = z0 + (z1 - z0) * u
                M = np.array([[z, 0, W * cx * (1 - z)], [0, z, H * cy * (1 - z)]], np.float32)
                fr[i] = cv2.warpAffine(fr[i], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        frames += fr
    frames = (frames + [frames[-1]] * nfr)[:nfr]
    # testo: riquadri bianchi arrotondati, parola chiave (con *) su riquadro azzurro, pop d'ingresso
    from PIL import Image, ImageDraw, ImageFont
    font_path = os.path.join(m.HERE, "models", "Montserrat-ExtraBold.ttf")
    hl = tuple(int(cfg["subs"]["highlight"][i:i + 2], 16) for i in (0, 2, 4))

    def render(lines, size):
        f = ImageFont.truetype(font_path, size)
        try:
            f.set_variation_by_name("Black")
        except Exception:
            pass
        pad, gap, r = int(size * 0.28), int(size * 0.16), int(size * 0.3)
        rows = []
        for line in lines:
            words = line.split()
            ws = [(w.lstrip("*"), w.startswith("*")) for w in words]
            space = f.getlength(" ")
            widths = [f.getlength(w) for w, _ in ws]
            rows.append((ws, widths, sum(widths) + space * (len(ws) - 1), space))
        asc, desc = f.getmetrics()
        lh = asc + int(desc * 0.3)
        bw = int(max(r_[2] for r_ in rows) + 2 * pad)
        img = Image.new("RGBA", (W, (lh + 2 * pad + gap) * len(rows) + 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        y = 20
        for ws, widths, tw, space in rows:
            x0 = (W - tw) / 2 - pad
            d.rounded_rectangle([x0, y, x0 + tw + 2 * pad, y + lh + 2 * pad], r, fill=(255, 255, 255, 255))
            x = x0 + pad
            for (w, h), wd in zip(ws, widths):
                if h:
                    d.rounded_rectangle([x - pad * 0.45, y + pad * 0.35, x + wd + pad * 0.45, y + lh + pad * 1.65],
                                        int(r * 0.7), fill=hl + (255,))
                d.text((x, y + pad), w, font=f, fill=(15, 15, 15, 255))
                x += wd + space
            y += lh + 2 * pad + gap
        img = img.crop((0, 0, W, y + 20))
        return np.array(img)  # RGBA

    overlays = []
    for b in cfg["beats"]:
        ov = render(b["lines"], b.get("size", 80))
        overlays.append((b, ov))

    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                            "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for k, f in enumerate(frames):
        t = k / FPS
        fr = f.astype(np.float32)
        for b, ov in overlays:
            t0, t1 = b["t"]
            if not (t0 <= t < t1):
                continue
            u = min((t - t0) / 0.14, 1)
            sc = (1.18 if b.get("punch") else 1.08) - ((1.18 if b.get("punch") else 1.08) - 1) * m.ease_out(u)
            o = cv2.resize(ov, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR) if sc != 1 else ov
            oh, ow = o.shape[:2]
            cy = b.get("y", 1250)
            y0, x0 = int(cy - oh / 2), int(W / 2 - ow / 2)
            ys, xs = max(y0, 0), max(x0, 0)
            ye, xe = min(y0 + oh, H), min(x0 + ow, W)
            o = o[ys - y0:ye - y0, xs - x0:xe - x0]
            al = o[..., 3:4].astype(np.float32) / 255 * min(u * 2.5, 1)
            fr[ys:ye, xs:xe] = fr[ys:ye, xs:xe] * (1 - al) + o[..., 2::-1][..., :3].astype(np.float32) * al
        enc.stdin.write(np.clip(fr, 0, 255).astype(np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    print("OK ->", out)


if __name__ == "__main__":
    main(sys.argv[1])
