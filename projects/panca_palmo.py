#!/usr/bin/env python3
"""Reel 2 del 20/11: PANCA, LA LINEA SUL PALMO, con il parlato di Manuel (IMG_9210, registrato il 20/11 sera).
A = 150 kg nel primo fotogramma ("Spingo 150 kg di panca, il bilanciere lo appoggio qui." con Manuel che disegna la
linea sul palmo dentro i 3 s, come ha chiesto); B = la mano con la linea gia' disegnata ("Il bilanciere lo appoggio qui
e spingo 150 kg."). Spiegazione di Manuel: il bilanciere va TRA L'ANULARE E IL POLLICE (linea dalla base
dell'anulare alla base del pollice). Manuel: "questo del dito lo possiamo lasciare, mi piace che lo disegni e si deve
vedere" -> il suo disegno col pennarello resta ben visibile.
Girati: IMG_5153 (150 kg), IMG_9153 (si sistema: palmo 8.25, presa 3.6-5.1), IMG_9189 (sfondo animazione),
IMG_9210 (parlato + disegno sul palmo 185.6-187.0)."""
import math, sys
sys.path.insert(0, "/home/user/Video-maker/projects")
import tl_kit as k
import vo
from PIL import ImageFilter, ImageEnhance

S = "/home/user/Video-maker/src_20nov"
P = "/home/user/Video-maker/src_parlato20/IMG_9210.MOV"
TRJ = {P: "/home/user/Video-maker/src_parlato20/tr9210.json"}
OUT = "/home/user/Video-maker/out/panca_palmo"
NEW = "/home/user/Video-maker/src_parlato20/IMG_9213.MOV"  # linea corretta disegnata sul palmo (8.8-9.9)
BENCH, HAND, WHITE_B = f"{S}/IMG_5153.MOV", f"{S}/IMG_9153.MOV", f"{S}/IMG_9189.MOV"

# i due pezzi del gancio sono tagliati nello stesso punto (fix_b / fix_a): prima si sovrapponevano -> eco
HOOK = {"A": [(P, 37.32, 38.88, "Spingo 150 kg di panca,", "fix_b"),
              (P, 38.88, 40.45, "il bilanciere lo appoggio qui.", "fix_a")],
        "B": [(P, 42.02, 43.27, "Il bilanciere lo appoggio qui", "fix_b"),
              (P, 43.27, 44.6, "e spingo 150 kg.", "fix_a")]}
PEN = (8.7, 9.9)  # IMG_9213: la penna tocca il palmo / la linea e' finita
BODY = [(P, 98.95, 100.75, "Appoggialo tra l'anulare / e il pollice."),
        (P, 196.6, 198.75, "Così scaricherai meglio / il peso sulla mano."),
        (P, 200.05, 203.0, "Di conseguenza l'avambraccio | rimarrà perpendicolare / al terreno."),
        (P, 217.8, 220.9, "Eviterai di piegare il polso | e la spinta / rimarrà efficiente."),
        (P, 222.5, 223.65, "E tu dove l'appoggi?"),
        (P, 230.52, 231.85, "Scrivimelo nei commenti.")]

# palmo di IMG_9153 al fotogramma 8.25 (1080x1920): base dell'anulare / base del pollice
# Manuel 20/11 sera: "ho sbagliato linea, questa e' quella corretta" (IMG_9213): la linea va dal punto tra pollice e
# indice al palmo verso il mignolo -> puntini di nuovo su quei due punti (audio e testo invariati).
P_RING, P_THUMB = (308, 926), (210, 952)
HC = (255, 930)


def blur_dark(r=18, b=0.42):
    return lambda fr, t: ImageEnhance.Brightness(fr.filter(ImageFilter.GaussianBlur(r))).enhance(b)


def plan(v):
    voice, total = vo.layout(HOOK[v] + BODY)
    G = vo.groups(voice)
    T = [g[0] for g in G] + [total]  # inizio di ogni frase
    h1, h2, anul, cosi, dicons, evit, etu, scriv, end = T
    rep = lambda t0, t1: dict(t0=t0, t1=t1, src=BENCH, ss=0.9, z0=1.85, z1=1.95, c=(450, 1100))
    # la penna scrive dall'inizio alla fine esattamente mentre dice "il bilanciere lo appoggio qui"
    pen = lambda t0, t1: dict(t0=t0, t1=t1, src=NEW, ss=PEN[0], sp=(PEN[1] - PEN[0]) / (t1 - t0), z0=1.0,
                              z1=1.08, c=(540, 900))
    opening = [rep(0, h2), pen(h2, anul)] if v == "A" else [pen(0, h2), rep(h2, anul)]
    shots = opening + [
        dict(t0=anul, t1=cosi, src=HAND, ss=7.95, live=0.25, z0=2.7, z1=3.0, c=HC),          # puntini e linea
        dict(t0=cosi, t1=evit, src=HAND, ss=3.6, sp=0.77, live=dicons - cosi, z0=1.32, z1=1.5, c=(300, 1060)),
        dict(t0=evit, t1=etu, src=WHITE_B, ss=3.0, pre=blur_dark()),                            # animazione
    ] + vo.cam_shots(G[6], scriv, z0=1.0, z1=1.04, c=(540, 900)) + \
        vo.cam_shots(G[7], end, z0=1.06, z1=1.1, c=(540, 900))
    return voice, shots, dict(h2=h2, anul=anul, cosi=cosi, dicons=dicons, evit=evit, etu=etu, end=end)


def hand_gfx(sh, t_dots, t_line, t_end):
    """Puntini (pop pop) sulla base dell'anulare e del pollice e linea arancio che si disegna tra i due."""
    def fn(im, t):
        if not (sh["t0"] <= t < t_end) or t < t_dots:
            return
        z = k.shot_z(sh, t)
        a, b = k.map_pt(P_RING, z, sh["c"]), k.map_pt(P_THUMB, z, sh["c"])
        s1, s2 = k.pop((t - t_dots) / 0.25), k.pop((t - t_dots - 0.15) / 0.25)
        pr = k.ease_out((t - t_line) / 0.6)

        def draw(d, P_, ss):
            if pr > 0:
                e = (a[0] + (b[0] - a[0]) * pr, a[1] + (b[1] - a[1]) * pr)
                d.line([P_(*a), P_(*e)], fill=(255, 255, 255, 255), width=18 * ss)
                d.line([P_(*a), P_(*e)], fill=k.ORANGE + (255,), width=10 * ss)
            k.dot(d, P_, ss, a[0], a[1], 15, s1)
            k.dot(d, P_, ss, b[0], b[1], 15, s2)
        k.aa(im, (min(a[0], b[0]) - 60, min(a[1], b[1]) - 60, max(a[0], b[0]) + 60, max(a[1], b[1]) + 60), draw)
    return fn


def grip_arrow(sh, t_on):
    """Freccia bilanciere -> polso -> avambraccio sulla presa chiusa (fermo su IMG_9153 5.1)."""
    x = 246

    def fn(im, t):
        if not (t_on <= t < sh["t1"]):
            return
        z = k.shot_z(sh, t)
        pts = [k.map_pt(p, z, sh["c"]) for p in ((x + 2, 905), (x + 6, 1030), (x - 8, 1235))]
        pr = k.ease_out((t - t_on) / 0.6)
        k.aa(im, (pts[0][0] - 80, pts[0][1] - 60, pts[0][0] + 80, pts[-1][1] + 60),
             lambda d, P_, ss: k.arrow(d, P_, ss, pts, pr, width=9, head=34))
    return fn


def wrist_anim(t0, t1):
    """Avambraccio e mano stilizzati: il bilanciere verso le dita piega il polso (X), poi la mano torna dritta e la
    spinta scende lungo l'avambraccio ("Eviterai di piegare il polso e la spinta rimarra' efficiente")."""
    def fn(im, t):
        if not (t0 <= t < t1):
            return
        u = t - t0
        a = 1 - k.ease((t - (t1 - 0.14)) / 0.14)
        WX, WY, L, LF, TH = 470, 900, 280, 380, 108
        draw_p = k.ease_out(u / 0.35)
        bend = k.ease((u - 0.45) / 0.45) * (1 - k.ease((u - 1.55) / 0.4))
        ang = math.radians(50) * bend
        hx, hy = WX + L * math.sin(ang), WY - L * math.cos(ang)
        bd = 215
        bx, by = WX + bd * math.sin(ang) + 70 * math.cos(ang), WY - bd * math.cos(ang) + 70 * math.sin(ang)
        bs = k.pop((u - 0.25) / 0.28)
        xp = k.ease_out((u - 1.0) / 0.3) * (1 - k.ease((u - 1.55) / 0.25))
        arr = k.ease_out((u - 2.0) / 0.45)
        al = int(255 * a)

        def capsule(d, P_, p0, p1, w):
            for col, ww in (((255, 255, 255, al), w + 14), ((28, 28, 30, al), w)):
                d.line([P_(*p0), P_(*p1)], fill=col, width=int(ww * 3))
                for q in (p0, p1):
                    r = ww / 2
                    d.ellipse([P_(q[0] - r, q[1] - r), P_(q[0] + r, q[1] + r)], fill=col)

        def draw(d, P_, ss):
            capsule(d, P_, (WX, WY), (WX, WY + LF * draw_p), TH)
            capsule(d, P_, (WX, WY), (WX + (hx - WX) * draw_p, WY + (hy - WY) * draw_p), TH * 0.95)
            d.ellipse([P_(WX - 16, WY - 16), P_(WX + 16, WY + 16)], fill=k.ORANGE + (al,))
            if bs > 0:
                r = 58 * bs
                d.ellipse([P_(bx - r - 7, by - r - 7), P_(bx + r + 7, by + r + 7)], fill=(255, 255, 255, al))
                d.ellipse([P_(bx - r, by - r), P_(bx + r, by + r)], fill=(165, 165, 172, al))
            if xp > 0.01:
                k.xmark(d, P_, ss, 800, 560, 85, min(xp * 1.5, 1), width=22)
            if arr > 0:  # spinta dritta lungo l'avambraccio
                k.arrow(d, P_, ss, [(bx, by + 75), (bx, by + 75 + 420)], arr, width=10, head=36)
        k.aa(im, (250, 420, 960, 1460), draw)
    return fn


def build(v):
    voice, shots, m = plan(v)
    pages = vo.kara_pages(voice, TRJ)
    # Manuel: sottotitoli SEMPRE, anche nel gancio (chi guarda senza volume e' quello che salta)
    pages_vis = pages
    sh = {s["t0"]: s for s in shots}
    big150 = lambda: k.text_img("*150* *KG*", size=150, stroke=9)
    L = []
    if v == "A":
        L.append(k.popped(big150, 0, m["h2"], 540, 560, still=True))
    else:
        L.append(k.popped(big150, m["h2"], m["anul"], 540, 560))
    L += [hand_gfx(sh[m["anul"]], m["anul"] + 0.12, m["anul"] + 0.45, m["cosi"]),
          k.popped(lambda: k.label_img("QUI IL BILANCIERE", k.BLACK, size=60), m["anul"] + 0.3, m["cosi"], 540, 330),
          grip_arrow(sh[m["cosi"]], m["dicons"] + 0.1),
          k.popped(lambda: k.label_img("PERPENDICOLARE", k.ORANGE, size=60), m["dicons"] + 0.5, m["evit"], 540, 330),
          wrist_anim(m["evit"], m["etu"]),
          vo.kara_layer(pages_vis, y=1450, size=74, end=m["end"],
                        first_from=0.0)]
    sfx = [(m["anul"] + 0.12, "pop", 0.35), (m["anul"] + 0.27, "pop", 0.35), (m["anul"] + 0.45, "disegno", 0.3),
           (m["anul"] + 0.3, "comparsa", 0.15), (m["dicons"] + 0.1, "disegno", 0.25),
           (m["dicons"] + 0.5, "pop", 0.25), (m["evit"], "disegno", 0.22), (m["evit"] + 0.25, "pop", 0.3),
           (m["evit"] + 0.45, "trascina", 0.18), (m["evit"] + 1.0, "hit", 0.2), (m["evit"] + 2.0, "whoosh", 0.18)]
    sfx += [] if v == "A" else [(m["h2"], "hit", 0.15)]  # niente effetti sul primo fotogramma
    out = f"{OUT}/panca_palmo_{v}.mp4"
    k.build(out, round(m["end"], 3), shots, L, sfx, [x[:4] for x in voice])
    k.sheet(out, f"{OUT}/sheet_{v}.jpg", n=30, cols=10)
    print(v, {kk: round(vv, 2) for kk, vv in m.items()})


if __name__ == "__main__":
    for v in sys.argv[1:] or ["A", "B"]:
        build(v)
