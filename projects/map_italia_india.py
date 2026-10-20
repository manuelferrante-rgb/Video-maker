#!/usr/bin/env python3
"""Animazione cartina: volo Italia -> India (verticale 1080x1920). Uso: map_italia_india.py durata_s uscita.mov [dy]
Terre da Natural Earth (assets/geo), Italia e India evidenziate, rotta tratteggiata che si disegna, aereo che la segue,
la camera parte sull'Italia, si allarga durante il volo e stringe sull'India. Uscita RGBA (qtrle) per sovrapporla."""
import json, math, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 1.9
OUTP = sys.argv[2] if len(sys.argv) > 2 else "/home/user/Video-maker/out/map_italia_india.mov"
DY = float(sys.argv[3]) if len(sys.argv) > 3 else 0  # sposta la cartina in alto di DY px (spazio per i sottotitoli)
GEO = "/home/user/Video-maker/assets/geo"
OCEAN, LAND, LAND_EDGE = (12, 28, 46), (52, 72, 96), (78, 100, 126)
ORANGE, IVORY = (232, 102, 44), (242, 238, 227)
FB = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"

A = (12.5, 41.9)   # Roma
B = (77.2, 28.6)   # Nuova Delhi (punto indicativo sull'India)


def polys(path, names=None):
    d = json.load(open(path))
    out = []
    for f in d["features"]:
        if names and f["properties"].get("NAME") not in names:
            continue
        g = f["geometry"]
        rings = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for poly in rings:
            out.append(poly[0])
    return out


LAND_P = polys(f"{GEO}/ne_50m_land.geojson")
HL = {n: polys(f"{GEO}/ne_50m_countries.geojson", {n}) for n in ("Italy", "India")}
# solo le terre vicine alla rotta (velocità)
LAND_P = [r for r in LAND_P if any(-30 < x < 120 and -15 < y < 75 for x, y in r[::5])]


def merc(lon, lat):
    return lon, math.degrees(math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)))


def ease(x):
    x = min(max(x, 0), 1)
    return x * x * (3 - 2 * x)


def arc(t):
    """rotta curva (un po' verso nord) tra A e B, t 0..1, in coordinate mercatore."""
    ax, ay = merc(*A)
    bx, by = merc(*B)
    mx, my = (ax + bx) / 2, (ay + by) / 2 + 14
    x = (1 - t) ** 2 * ax + 2 * (1 - t) * t * mx + t * t * bx
    y = (1 - t) ** 2 * ay + 2 * (1 - t) * t * my + t * t * by
    return x, y


def camera(t):
    """centro e scala (px per grado): stretto sull'Italia, largo a metà, stretto sull'India."""
    p = ease(t)
    cx, cy = arc(p)
    zoom_out = math.sin(math.pi * min(t * 1.05, 1)) ** 1.2
    s = 30 - 18 * zoom_out
    return cx, cy, s


fe = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
plane0 = Image.new("RGBA", (140, 140))
ImageDraw.Draw(plane0).text((10, 10), "✈", font=fe, embedded_color=True)
plane0 = plane0.crop(plane0.getbbox())
fl = ImageFont.truetype(FB, 64)


def render(fr, n):
    t = fr / max(n - 1, 1)
    fly = ease((t - 0.08) / 0.84)  # avanzamento del volo
    cx, cy, s = camera(t)

    def P(lon, lat):
        x, y = merc(lon, lat)
        return W / 2 + (x - cx) * s, H / 2 - DY - (y - cy) * s

    im = Image.new("RGBA", (W, H), OCEAN + (255,))
    d = ImageDraw.Draw(im)
    for r in LAND_P:
        d.polygon([P(*q) for q in r], fill=LAND + (255,), outline=LAND_EDGE + (255,))
    for name, rings in HL.items():
        lit = name == "Italy" or fly > 0.85
        col = ORANGE if lit else (120, 130, 150)
        for r in rings:
            d.polygon([P(*q) for q in r], fill=col + (255,))
    # rotta tratteggiata fino al punto raggiunto
    pts = [arc(k / 200) for k in range(201)]
    pts = [(W / 2 + (x - cx) * s, H / 2 - DY - (y - cy) * s) for x, y in pts]
    upto = int(fly * 200)
    for k in range(0, upto, 6):
        d.line(pts[k:min(k + 4, upto) + 1], fill=IVORY + (255,), width=7)
    for (lon, lat), show in ((A, True), (B, fly > 0.85)):
        if show:
            x, y = P(lon, lat)
            d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=IVORY + (255,), outline=(0, 0, 0, 255), width=4)
    # aereo orientato lungo la rotta
    k = min(max(upto, 1), 199)
    (x0, y0), (x1, y1) = pts[k - 1], pts[k + 1]
    ang = math.degrees(math.atan2(-(y1 - y0), x1 - x0))
    pl = plane0.rotate(ang - 45, expand=True, resample=Image.BICUBIC)  # il muso dell'emoji punta a 45° (alto a destra)
    pl = pl.resize((int(pl.width * 0.9), int(pl.height * 0.9)), Image.LANCZOS)
    px, py = pts[k]
    im.alpha_composite(pl, (int(px - pl.width / 2), int(py - pl.height / 2)))
    # etichette paesi
    for (lon, lat), txt, show in ((A, "ITALIA", fly < 0.5), (B, "INDIA", fly > 0.85)):
        if show:
            x, y = P(lon, lat)
            l, tt, rr, bb = fl.getbbox(txt)
            w, h = rr - l + 44, bb - tt + 24
            box = Image.new("RGBA", (w, h), (0, 0, 0, 255))
            ImageDraw.Draw(box).text((22 - l, 12 - tt), txt, font=fl, fill=(255, 255, 255))
            im.alpha_composite(box, (int(x - w / 2), int(y - 150)))
    # leggera vignettatura
    v = Image.new("L", (W, H), 0)
    ImageDraw.Draw(v).ellipse([-300, -200, W + 300, H + 200], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(160))
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 120))
    dark.putalpha(v.point(lambda a: 120 - a * 120 // 255))
    im.alpha_composite(dark)
    return im


n = int(round(DUR * FPS))
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r",
                      str(FPS), "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", OUTP], stdin=subprocess.PIPE)
for fr in range(n):
    p.stdin.write(render(fr, n).tobytes())
p.stdin.close()
p.wait()
print("ok", OUTP, n)
