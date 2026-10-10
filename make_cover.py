#!/usr/bin/env python3
"""Copertina 9:16 per il reel: frame di sfondo + busto scontornato grande + titolo a 2 righe.

Uso:  python3 make_cover.py progetto.json   (usa la sezione "cover" del progetto)
"""
import json, os, subprocess, sys
import numpy as np, cv2
import make_reel as m

W, H = m.W, m.H


def main(cfg_path):
    cfg = json.load(open(cfg_path))
    c = cfg["cover"]
    out = c["output"]
    tmp = out + ".work"
    os.makedirs(tmp, exist_ok=True)

    # sfondo: ritaglio della parte alta del frame (via le scritte in basso) scalato a pieno schermo
    b = c["background"]
    src = m.read_frames(b["file"], b["time"], 1 / 30, 720, 1280, fit="cover")[0]
    x0, y0, x1, y1 = b["crop"]
    bg = cv2.resize(src[y0:y1, x0:x1], (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    bg *= b.get("dim", 0.9)

    # busto
    f = c["face"]
    fr = m.read_frames(f["file"], f["time"], 1 / 30, W, H, fit="cover")
    alpha = m.Matter(cfg["matting_model"]).run(fr)[0]
    fr = fr[0]
    ax, ay = W * cfg["bust"]["anchor"][0], H * cfg["bust"]["anchor"][1]
    M = cv2.getRotationMatrix2D((ax, ay), f.get("tilt", 0), f["w"] / W)
    M[0, 2] += f["cx"] - ax
    M[1, 2] += f["cy"] - ay
    fg = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC).astype(np.float32)
    al = cv2.warpAffine(alpha, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
    sh = cv2.GaussianBlur(al, (0, 0), 22)[..., None]
    al = al[..., None]
    img = bg * (1 - 0.4 * sh)
    img = img * (1 - al) + fg * al
    cv2.imwrite(f"{tmp}/base.png", np.clip(img, 0, 255).astype(np.uint8))

    # titolo: righe di parole, quelle con * in azzurro
    s = cfg["subs"]
    hl = s["highlight"]
    hl_ass = f"&H00{hl[4:6]}{hl[2:4]}{hl[0:2]}&"
    lines = []
    for i, line in enumerate(c["title"]):
        words = [(f"{{\\c{hl_ass}}}{w[1:]}{{\\c&H00FFFFFF&}}" if w.startswith("*") else w) for w in line.split()]
        y = c["title_y"] + i * c["line_gap"]
        lines.append(f"Dialogue: 0,0:00:00.00,0:00:05.00,T,,0,0,0,,{{\\an5\\pos({W // 2},{y})}}{' '.join(words)}")
    ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: T,{s['font']},{c['size']},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,{c['outline']},{c['shadow']},5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(lines) + "\n"
    open(f"{tmp}/title.ass", "w").write(ass)
    fontsdir = os.path.dirname(s["font_file"])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{tmp}/base.png", "-vf",
                    f"ass={tmp}/title.ass:fontsdir={fontsdir}", "-frames:v", "1", "-q:v", "2", out], check=True)
    print("OK ->", out)


if __name__ == "__main__":
    main(sys.argv[1])
