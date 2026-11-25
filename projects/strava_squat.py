#!/usr/bin/env python3
"""Reel "squat con lo sticker di Strava" (25/11/2026, riferimento di Manuel): sopra lo squat di IMG_9301 le statistiche
di corsa (Distanza 0 km, Passo 00:00 /km, Tempo 2h 50m) + una piccola pista d'atletica col puntino arancio fermo sulla
partenza (la corsa e' zero) + scritta STRAVA piccola. Nient'altro. Audio originale.
V1 = layout del riferimento (niente zoom, sticker a meta' a sinistra).
V2 = zoom 1,2x tenendo fermo il bordo sinistro (Manuel piu' grande e a destra), sticker sul muro in alto a sinistra
con bordo nero (sul bianco altrimenti non si legge): non lo copre mai, ne' in piedi ne' in buca."""
import subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

R = "/home/user/Video-maker"
SRC, OUT = f"{R}/src_25nov/mio.mov", f"{R}/out/strava_squat"
W, H = 1080, 1920
ORANGE = (252, 76, 2)
CFG = {
    "V1": dict(z=1.0, y0=0, cx=315, y=930, fl=31, fv=72, gap=136, dv=60, stroke=0),
    "V2": dict(z=1.2, y0=160, cx=205, y=300, fl=25, fv=52, gap=110, dv=48, stroke=5),
}


def sticker(c):
    FL = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", c["fl"])
    FV = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", c["fv"])
    FS = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf", int(c["fl"] * 1.05))
    k = c["fv"] / 72  # scala rispetto alla V1
    sw = c["stroke"]
    blk = (0, 0, 0, 255)
    im = Image.new("RGBA", (W * 3, H * 3), (0, 0, 0, 0))   # disegno a 3x per bordi puliti
    d = ImageDraw.Draw(im)
    S = lambda v: int(round(v * 3))
    cx = c["cx"]
    y = c["y"]
    for lab, val in (("Distanza", "0 km"), ("Passo", "00:00 /km"), ("Tempo", "2h 50m")):
        d.text((S(cx), S(y)), lab, font=FL.font_variant(size=S(c["fl"])), fill=(255, 255, 255, 255), anchor="mm",
               stroke_width=S(sw * 0.6), stroke_fill=blk)
        d.text((S(cx), S(y + c["dv"])), val, font=FV.font_variant(size=S(c["fv"])), fill=(255, 255, 255, 255),
               anchor="mm", stroke_width=S(sw), stroke_fill=blk)
        y += c["gap"]
    # pista d'atletica stilizzata (ovale a stadio) col puntino fermo sulla linea di partenza
    tw, th, lw = 190 * k, 84 * k, 7 * k
    ty = y + 5 * k
    x0, x1, y0, y1 = cx - tw / 2, cx + tw / 2, ty, ty + th
    if sw:
        d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], radius=S(th / 2), outline=blk, width=S(lw + 6))
    d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], radius=S(th / 2), outline=(255, 255, 255, 235), width=S(lw))
    sx = cx - tw * 0.12                                     # linea di partenza sul rettilineo in basso
    d.line([S(sx), S(y1 - lw * 2.2), S(sx), S(y1 + lw * 1.2)], fill=(255, 255, 255, 255), width=S(3 * k))
    r = 14 * k
    if sw:
        d.ellipse([S(sx - r - 3), S(y1 - lw / 2 - r - 3), S(sx + r + 3), S(y1 - lw / 2 + r + 3)], fill=blk)
    d.ellipse([S(sx - r), S(y1 - lw / 2 - r), S(sx + r), S(y1 - lw / 2 + r)], fill=ORANGE + (255,))
    # STRAVA piccolo sotto
    d.text((S(cx), S(y1 + 42 * k)), "STRAVA", font=FS.font_variant(size=S(int(c["fl"] * 1.05))),
           fill=ORANGE + (255,), anchor="mm", stroke_width=S(sw * 0.6), stroke_fill=blk)
    im = im.resize((W, H), Image.LANCZOS)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(im.split()[3].point(lambda v: int(v * 0.35)))
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 3))
    out.alpha_composite(im)
    return out


def build(v):
    c = CFG[v]
    png = f"{OUT}/sticker_{v}.png"
    sticker(c).save(png)
    zoom = ""
    if c["z"] != 1.0:  # zoom tenendo fermo il bordo sinistro: Manuel si ingrandisce e va a destra
        zoom = f"crop={W / c['z']:.0f}:{H / c['z']:.0f}:0:{c['y0']},scale={W}:{H}:flags=lanczos,unsharp=5:5:0.45,"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-i", png, "-filter_complex",
                    f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},{zoom}setsar=1[v];"
                    "[v][1:v]overlay=0:0,format=yuv420p[o]", "-map", "[o]", "-map", "0:a:0", "-c:v", "libx264",
                    "-crf", "14", "-preset", "slow", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    f"{OUT}/strava_squat_{v}.mp4"], check=True)
    print(v, "ok", Image.open(png).getbbox())


if __name__ == "__main__":
    for v in sys.argv[1:] or ["V1", "V2"]:
        build(v)
