#!/usr/bin/env python3
"""Copertine dei tre reel del 20/11: fotogramma forte + titolo su 2 righe (riquadro nero + arancio, Inter Black
Italic) nella fascia y ~1060-1250; anteprima del ritaglio 3:4 della griglia (y 240-1680).
Uso: python3 cover_20nov.py tempo|trazioni|panca"""
import subprocess, sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

R = "/home/user/Video-maker"
W, H = 1080, 1920
ORANGE, BLACK = (232, 102, 44), (12, 12, 12)
FBI = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
TONEMAP = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")

COVERS = {
    # nome: (file, secondo, hdr, zoom, centro, riga nera, riga arancio, y centro titolo)
    "tempo": (f"{R}/src_20nov/IMG_9126.MOV", 18.35, False, 1.12, (600, 900), "3 ORE IN PALESTRA?",
              "NE BASTANO 90 MINUTI", 1150),
    "trazioni": (f"{R}/src_20nov/IMG_5418.MOV", 6.4, True, 1.0, (540, 960), "UN MESE DI TRAZIONI",
                 "IN 30 SECONDI", 1150),
    "panca": (f"{R}/src_20nov/IMG_5153.MOV", 1.3, False, 1.6, (470, 1250), "DITA O PALMO?",
              "LA LINEA DELLA PANCA", 1150),
}


def frame(path, t, hdr):
    pre = TONEMAP + "," if hdr else ""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", path, "-frames:v", "1", "-vf",
                          f"{pre}scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return Image.frombytes("RGB", (W, H), raw)


def row(txt, bg, size=96):
    f = ImageFont.truetype(FBI, size)
    l, t, r, b = f.getbbox(txt)
    h = int(size * 1.42)
    im = Image.new("RGBA", (int(r - l + 64), h), bg + (255,))
    ImageDraw.Draw(im).text(((r - l) / 2 + 32, h / 2 + 3), txt, font=f, fill=(255, 255, 255, 255), anchor="mm")
    return im


def make(name):
    path, t, hdr, z, (cx, cy), l1, l2, yc = COVERS[name]
    im = frame(path, t, hdr)
    if z != 1:
        w, h = W / z, H / z
        x0, y0 = min(max(cx - w / 2, 0), W - w), min(max(cy - h / 2, 0), H - h)
        im = im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h))
    im = ImageEnhance.Contrast(im).enhance(1.05).convert("RGBA")
    # leggera ombra dietro al titolo per staccarlo dal fondo
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([0, yc - 190, W, yc + 190], fill=(0, 0, 0, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(60)))
    size = 96
    while True:
        r1, r2 = row(l1, BLACK, size), row(l2, ORANGE, size)
        if max(r1.width, r2.width) <= 960:
            break
        size -= 4
    im.alpha_composite(r1, ((W - r1.width) // 2, yc - r1.height - 6))
    im.alpha_composite(r2, ((W - r2.width) // 2, yc + 6))
    out = f"{R}/out/cover_{name}.jpg"
    im.convert("RGB").save(out, quality=94)
    crop = im.crop((0, 240, W, 1680)).convert("RGB")
    crop.save(f"{R}/out/cover_{name}_griglia34.jpg", quality=90)
    print(out, "font", size)


if __name__ == "__main__":
    for n in sys.argv[1:] or COVERS:
        make(n)
