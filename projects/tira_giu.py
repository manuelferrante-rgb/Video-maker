#!/usr/bin/env python3
"""Reel "Tira giù la sbarra" (trazioni 75 kg, 27/11/2026). Copy e scaletta: projects/trazioni_tira_giu.md.
B (trial 1) = gancio sul dorso nudo "Non faccio le trazioni tirandomi su, ma tiro giù la sbarra." + "E faccio 75 kg."
A (trial 2) = gancio sulla gara "Faccio trazioni con 75 kg e penso una cosa sola: tirare giù la sbarra."
Girato (Drive parlati 27/11, in src_27nov/): IMG_9358 = parlato in camera (4K, mattarello vero 66,5-69 s, non si spezza:
niente crack); IMG_6935 = dorso nudo all'aperto (ripetizione 2,55 braccia tese -> 3,28 mento sopra la sbarra);
IMG_7089 = trazione normale maglia nera (tirata 7,1 -> 7,9); gara.mov = 75 kg in gara (parte 12,9, su 14,05);
mattarello.mov = la presa sulla sbarra (mani che si chiudono)."""
import math, sys
sys.path.insert(0, "/home/user/Video-maker/projects")
import tl_kit as k
import vo
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

S = "/home/user/Video-maker/src_27nov"
P = f"{S}/IMG_9358.MOV"
TRJ = {P: f"{S}/tr9358.json"}
DORSO, NORM, GARA, PRESA = f"{S}/IMG_6935.MOV", f"{S}/IMG_7089.MOV", f"{S}/gara.mov", f"{S}/mattarello.mov"
OUT = "/home/user/Video-maker/out/tira_giu"

HOOK = {"B": [(P, 26.14, 28.96, "Non faccio le trazioni / tirandomi su, | ma tiro giù / la sbarra."),
              (P, 29.44, 30.79, "E faccio 75 kg.")],
        "A": [(P, 145.01, 146.8, "Faccio trazioni / con 75 kg", "fix_b"),
              (P, 146.8, 149.13, "e penso una cosa sola: | tirare giù / la sbarra.", "fix_a")]}
BODY = [(P, 66.5, 68.95, "Come se volessi spezzarla, | come con questo / mattarello."),
        (P, 75.93, 78.42, "Così le scapole scendono | e il dorsale / lavora."),
        (P, 88.06, 88.91, "Presa salda."),
        (P, 95.03, 96.82, "Traiettoria / più verticale possibile."),
        (P, 101.83, 102.55, "E tira giù."),
        (P, 109.29, 111.25, "Salvalo e provalo / nella prossima serie.", "fix_b")]
PONTE = {"B": [(P, 132.77, 134.35, "Perché io, / alla sbarra,")],
         "A": [(P, 111.25, 112.27, "È così che", "fix_a")]}

# coordinate nel fotogramma sorgente 1080x1920
# Manuel 27/11: il dorso nudo NON va ne' rallentato ne' zoomato (e niente rallenty in generale): velocita' reale
DREP0, DTOP = 1.4, 3.45           # IMG_6935: braccia tese da 1,4 s, mento sopra la sbarra a 3,45 s
GZ, GC = 1.6, (680, 1060)         # gara
PZ, PC = 1.5, (470, 760)          # presa sulla sbarra
SH = 0.86                         # trazione normale rimpicciolita sopra il suo sfondo sfocato (mani sotto la domanda)


def shrink(fr, t):
    w, h = int(1080 * SH), int(1920 * SH)
    bg = ImageEnhance.Brightness(fr.filter(ImageFilter.GaussianBlur(28))).enhance(0.55)
    bg.paste(fr.resize((w, h), Image.LANCZOS), ((1080 - w) // 2, 1920 - h))
    return bg


def sh_pt(p):
    return ((1080 - 1080 * SH) / 2 + p[0] * SH, 1920 - 1920 * SH + p[1] * SH)


def plan(v):
    voice, total = vo.layout(HOOK[v] + BODY + PONTE[v])
    G = vo.groups(voice)
    T = [g[0] for g in G] + [total]
    if v == "B":
        h0, h1, spz, scap, presa, traj, tira, salva, ponte, end = T
    else:
        h0, h1, spz, scap, presa, traj, tira, salva, ponte, end = T
    # "come con questo mattarello": da qui Manuel in camera col mattarello vero
    t_come = vo.src_to_reel(voice, P, 67.86)
    dorso_rep = lambda t0, t1: dict(t0=t0, t1=t1, src=DORSO, ss=DREP0)          # dalle braccia tese, tempo reale
    gara_up = lambda t0, t1, top=14.05: dict(t0=t0, t1=t1, src=GARA, ss=max(top - (t1 - t0), 12.3), z0=GZ,
                                             z1=GZ + 0.06, c=GC)                 # finisce col mento sopra
    if v == "B":
        opening = [dorso_rep(0, h1), gara_up(h1, spz)]
        loop = dict(t0=ponte, t1=end, src=DORSO, ss=DREP0 - (end - ponte))        # finisce sul primo fotogramma
    else:
        g0 = 12.45                                                               # braccia tese, tempo reale
        opening = [dict(t0=0, t1=h1, src=GARA, ss=g0, z0=GZ, z1=GZ + 0.06, c=GC), dorso_rep(h1, spz)]
        loop = dict(t0=ponte, t1=end, src=GARA, ss=g0 - (end - ponte), z0=GZ + 0.06, z1=GZ, c=GC)
    cam = [s for s in vo.cam_shots(G[2], scap, z0=1.0, z1=1.05, c=(540, 960)) if s["t1"] > t_come]
    for s in cam:  # la parte in camera parte da "come con questo mattarello"
        if s["t0"] < t_come:
            s["ss"] += (t_come - s["t0"]) * vo.SP
            s["t0"] = t_come
    cam[0]["nosw"] = False
    shots = opening + [dict(t0=spz, t1=t_come, src=PRESA, ss=0.1, z0=PZ, z1=PZ + 0.06, c=PC)] + cam + [
        dict(t0=scap, t1=presa, src=DORSO, ss=0.0, live=0.75),     # prima ripetizione a tempo reale, fermo in alto
        dict(t0=presa, t1=traj, src=PRESA, ss=2.3, z0=PZ + 0.1, z1=PZ + 0.16, c=PC),
        dict(t0=traj, t1=tira, src=NORM, ss=7.1 - (tira - traj), pre=shrink),
        dict(t0=tira, t1=salva, src=NORM, ss=7.1, pre=shrink),
        gara_up(salva, ponte), loop]
    m = dict(h1=h1, spz=spz, come=t_come, scap=scap, presa=presa, traj=traj, tira=tira, salva=salva, ponte=ponte,
             end=end)
    return voice, shots, m


# ------------------------------------------------------------------ grafiche
def arrows_scap(t_on, t_off, sh):
    def fn(im, t):
        if not (t_on <= t < t_off):
            return
        z = k.shot_z(sh, t)
        pr = k.ease_out((t - t_on) / 0.5)
        a1 = [k.map_pt(p, z, sh.get("c", (540, 960))) for p in ((352, 690), (352, 830))]
        a2 = [k.map_pt(p, z, sh.get("c", (540, 960))) for p in ((410, 700), (410, 840))]
        lat = [k.map_pt(p, z, sh.get("c", (540, 960))) for p in ((410, 805), (420, 880), (432, 965))]
        pl = k.ease_out((t - t_on - 0.35) / 0.5)

        def draw(d, P_, ss):
            k.arrow(d, P_, ss, a1, pr, color=k.ORANGE, width=9, head=28, accent=k.ORANGE)
            k.arrow(d, P_, ss, a2, pr, color=k.ORANGE, width=9, head=28, accent=k.ORANGE)
            if pl > 0:
                pts = lat
                n = max(int(len(pts) * pl + 0.999), 2)
                seg = pts[:n]
                d.line([P_(*p) for p in seg], fill=(255, 255, 255, 230), width=5 * ss, joint="curve")
        xs = [p[0] for p in a1 + a2 + lat]
        ys = [p[1] for p in a1 + a2 + lat]
        k.aa(im, (min(xs) - 60, min(ys) - 60, max(xs) + 60, max(ys) + 60), draw)
    return fn


def dots_hands(t_on, t_off, sh):
    HANDS = [(300, 625), (612, 702)]

    def fn(im, t):
        if not (t_on <= t < t_off):
            return
        z = k.shot_z(sh, t)
        pts = [k.map_pt(p, z, sh.get("c", (540, 960))) for p in HANDS]

        def draw(d, P_, ss):
            for i, (x, y) in enumerate(pts):
                k.dot(d, P_, ss, x, y, 15, k.pop((t - t_on - 0.12 * i) / 0.25))
        k.aa(im, (min(p[0] for p in pts) - 50, min(p[1] for p in pts) - 50, max(p[0] for p in pts) + 50,
                  max(p[1] for p in pts) + 50), draw)
    return fn


def line_vert(t_on, t_off):
    a, b = sh_pt((870, 420)), sh_pt((870, 1480))

    def fn(im, t):
        if not (t_on <= t < t_off):
            return
        pr = k.ease_out((t - t_on) / 0.6)
        e = (a[0], a[1] + (b[1] - a[1]) * pr)

        def draw(d, P_, ss):
            d.line([P_(*a), P_(*e)], fill=(255, 255, 255, 255), width=14 * ss)
            d.line([P_(*a), P_(*e)], fill=k.ORANGE + (255,), width=8 * ss)
        k.aa(im, (a[0] - 30, a[1] - 30, a[0] + 30, b[1] + 30), draw)
    return fn


def arrow_down(t_on, t_off):
    pts = [sh_pt((900, 250)), sh_pt((900, 620))]

    def fn(im, t):
        if not (t_on <= t < t_off):
            return
        pr = k.ease_out((t - t_on) / 0.45)
        k.aa(im, (pts[0][0] - 60, pts[0][1] - 40, pts[0][0] + 60, pts[1][1] + 60),
             lambda d, P_, ss: k.arrow(d, P_, ss, pts, pr, width=12, head=40))
    return fn


FB = k.font(k.F_BI, 46)


def scheda(times, end):
    """1 PRESA SALDA / 2 VERTICALE / 3 TIRA GIÙ in basso a sinistra: si riempie e resta fino alla fine."""
    items = ["PRESA SALDA", "VERTICALE", "TIRA GIÙ"]
    imgs = []
    for i, txt in enumerate(items):
        num = k.label_img(str(i + 1), k.ORANGE, size=46, padx=20, h=72)
        lab = k.label_img(txt, k.BLACK, size=46, padx=22, h=72)
        im = Image.new("RGBA", (num.width + lab.width, 72), (0, 0, 0, 0))
        im.alpha_composite(num, (0, 0)); im.alpha_composite(lab, (num.width, 0))
        imgs.append(im)
    Y0 = 1110

    def fn(im, t):
        for i, (img, t0) in enumerate(zip(imgs, times)):
            if t0 <= t < end:
                s = k.pop((t - t0) / 0.28)
                k.put(im, img, 50 + img.width / 2, Y0 + i * 84, s)
    return fn


def domanda(t0, end):
    r1 = k.label_img("TU COME LE FAI?", k.BLACK, size=54)
    r2 = k.label_img("CI AVEVI MAI PENSATO?", k.ORANGE, size=54)
    em = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(em).text((0, 0), "👇", font=ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
                                                                  109), embedded_color=True)
    em = em.crop(em.getbbox()).resize((62, 62), Image.LANCZOS)
    w = max(r1.width, r2.width + 74)
    img = Image.new("RGBA", (w, r1.height + r2.height + 10), (0, 0, 0, 0))
    img.alpha_composite(r1, ((w - r1.width) // 2, 0))
    x2 = (w - r2.width - 74) // 2
    img.alpha_composite(r2, (x2, r1.height + 10))
    img.alpha_composite(em, (x2 + r2.width + 12, r1.height + 10 + (r2.height - 62) // 2))

    def fn(im, t):
        if t0 <= t < end:
            k.put(im, img, 540, 340, k.pop((t - t0) / 0.3))
    return fn


def salva_icon(t0, t1):
    def fn(im, t):
        if not (t0 <= t < t1):
            return
        s = k.pop((t - t0) / 0.3)
        a = 1 - k.ease((t - (t1 - 0.12)) / 0.12)
        cx, cy, w, h = 930, 1200, 64 * s, 88 * s
        if s <= 0:
            return

        def draw(d, P_, ss):
            pts = [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx, cy + h / 4),
                   (cx - w / 2, cy + h / 2)]
            d.polygon([P_(*p) for p in pts], fill=(255, 255, 255, int(255 * a)), outline=(0, 0, 0, int(255 * a)),
                      width=4 * ss)
        k.aa(im, (cx - 60, cy - 70, cx + 60, cy + 70), draw)
    return fn


def build(v):
    voice, shots, m = plan(v)
    sh = {s["t0"]: s for s in shots}
    pages = vo.kara_pages(voice, TRJ)
    big75 = lambda: k.label_img("+75 KG", k.ORANGE, size=96, padx=36)
    t75 = (m["h1"], m["spz"]) if v == "B" else (0.0, m["h1"])
    cam_on = lambda t: m["come"] <= t < m["scap"]
    L = [k.popped(big75, t75[0], t75[1], 250, 820, still=(v == "A")),
         arrows_scap(m["scap"] + 0.78, m["presa"], sh[m["scap"]]),
         dots_hands(m["presa"] + 0.05, m["traj"], sh[m["presa"]]),
         line_vert(m["traj"] + 0.1, m["tira"]),
         arrow_down(m["tira"] + 0.02, m["salva"]),
         scheda([m["presa"] + 0.05, m["traj"] + 0.05, m["tira"] + 0.02], m["end"]),
         domanda(7.0, m["end"]),
         salva_icon(m["salva"] + 0.1, m["ponte"]),
         vo.kara_layer(pages, y=lambda t: 330 if cam_on(t) else 1480, size=68, end=m["end"], first_from=0.0)]
    sfx = [(m["scap"] + 0.78, "disegno", 0.22), (m["presa"] + 0.05, "pop", 0.3), (m["presa"] + 0.17, "pop", 0.3),
           (m["traj"] + 0.1, "disegno", 0.25), (m["tira"] + 0.02, "whoosh", 0.22), (7.0, "pop", 0.25),
           (m["salva"] + 0.1, "pop", 0.25)]
    sfx += [(m["h1"], "hit", 0.15)] if v == "B" else []
    out = f"{OUT}/tira_giu_{v}.mp4"
    k.build(out, round(m["end"], 3), shots, L, sfx, [x[:4] for x in voice])
    k.sheet(out, f"{OUT}/sheet_{v}.jpg", n=30, cols=10)
    print(v, {kk: round(vv, 2) for kk, vv in m.items()})


if __name__ == "__main__":
    for v in sys.argv[1:] or ["B", "A"]:
        build(v)
