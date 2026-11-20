#!/usr/bin/env python3
"""Rimontaggio di "Elisabetta" (20/11/2026, brief_editor_novembre.md sez. 9c), senza nuove riprese.
Ieri (17 s, gancio "Ti fidi della tua scheda?" e split PRIMA/OGGI): 53-72% di salti. Ora si apre sull'alzata forte con
il numero. Frasi usate dal parlato IMG_9169 (e solo queste): "Elisabetta non riusciva a fare una trazione. Oggi la fa
con 10 kg." / "Tu scegli l'obiettivo, il percorso lo decido io." / "E io correggo i video." / "Lei pensa solo alla seduta
di oggi." / "Controlli o ti fidi? Scrivilo nei commenti."
A (prima/dopo): trazione con il disco a tutto schermo + contatore 0 -> +10 KG (unico testo nel primo secondo), riquadro
PRIMA (parco, fatica) su "a fare una trazione", esce su "Oggi"; scheda animata con TU L'OBIETTIVO / IO IL PERCORSO;
Manuel al computer; altra trazione; Manuel in camera con il campo commento (controllo / mi fido); fine = loop.
B (metodo prima): trazione + "Tu scegli l'obiettivo..." con il titolo, poi "Elisabetta non riusciva..." su un'altra
trazione con riquadro PRIMA e contatore; dal "E io correggo i video" identica ad A.
Uso: python3 projects/scheda_eli_v2.py [A B]"""
import os, subprocess, sys
sys.path.insert(0, "/home/user/video-maker/projects")
import scheda_elisabetta as m          # helper: sottotitoli parola per parola, titoli, campo commento, subsegs
from reel_kit import build, R, ORANGE, BLACK, ease
from PIL import Image, ImageDraw

NORM, BR, OUT = m.NORM, m.BR, f"{R}/out/eli2"
D = m.D
PH = {"H": [(38.14, 39.88), (44.35, 45.59)],   # Elisabetta non riusciva a fare una trazione, | oggi la fa con 10 kg.
      "OB": [(55.80, 58.08)],                   # Tu scegli l'obiettivo, il percorso lo decido io.
      "COR": [(109.38, 110.55)],                # E io correggo i video.
      "LEI": [(114.18, 116.15)],                # Lei pensa solo alla seduta di oggi.
      "CTA": [(163.32, 165.59)]}                # Controlli o ti fidi? Scrivilo nei commenti.
m.KARA = {"H": [("ELISABETTA", 38.04), ("NON", 38.68), ("|", 0), ("RIUSCIVA", 38.76), ("/", 0), ("A", 39.08),
                ("FARE", 39.16), ("UNA", 39.24), ("|", 0), ("TRAZIONE.", 39.48), ("/", 0), ("OGGI", 44.33), ("LA", 44.55),
                ("FA", 44.71), ("|", 0), ("CON", 44.87), ("10", 45.03), ("KG", 45.27)],
          "OB": [("TU", 55.73), ("SCEGLI", 55.89), ("|", 0), ("L'OBIETTIVO,", 56.21), ("/", 0), ("IL", 56.85),
                 ("PERCORSO", 57.01), ("|", 0), ("LO", 57.41), ("DECIDO", 57.57), ("IO", 57.89)],
          "COR": [("E", 109.34), ("IO", 109.50), ("CORREGGO", 109.66), ("|", 0), ("I", 110.14), ("VIDEO", 110.22)],
          "LEI": [("LEI", 114.08), ("PENSA", 114.48), ("SOLO", 114.88), ("|", 0), ("ALLA", 115.04), ("SEDUTA", 115.28),
                  ("DI", 115.76), ("OGGI", 115.84)],
          "CTA": [("CONTROLLI", 163.32), ("O", 163.80), ("|", 0), ("TI", 163.88), ("FIDI?", 164.04), ("/", 0),
                  ("SCRIVILO", 164.52), ("|", 0), ("NEI", 165.00), ("COMMENTI", 165.16)]}
PRIMA_SRC = f"{R}/src_eli/tg_3mb.mp4"        # parco al tramonto, senza zavorra, fa fatica (= PRIMA)


def sh(c):
    subprocess.run(c, shell=True, check=True)


def prima_frames():
    """fotogrammi del PRIMA (16,2 -> 17,2 s: la tirata faticosa, il mento resta sotto la sbarra) in 9:16 piccolo"""
    d = f"{OUT}/prima"
    if not os.path.exists(f"{d}/f_030.png"):
        os.makedirs(d, exist_ok=True)
        sh(f"ffmpeg -v error -y -ss 16.2 -t 1.05 -i {PRIMA_SRC} -vf fps=30,scale=478:850,crop=230:409:65:40,scale=300:533:flags=lanczos,unsharp=5:5:0.6 "
           f"{d}/f_%03d.png")
    return [Image.open(f"{d}/{f}").convert("RGBA") for f in sorted(os.listdir(d))]


def counter(t0, t1, cx=640, cy=1100):
    """contatore 0 -> +10 KG (riquadro arancio, Inter Black Italic), conta tra t0 e t1 e poi resta"""
    def draw(im, t, dur):
        if t < t0 - 0.001:
            return
        v = round(10 * ease((t - t0) / max(t1 - t0, 0.05)))
        lab = m.label("0 KG" if v == 0 else f"+{v} KG", ORANGE, 112)
        s = m.popscale(t - t1) if t >= t1 else 1.0
        lb = lab.resize((int(lab.width * s), int(lab.height * s)), Image.LANCZOS)
        im.alpha_composite(lb, (int(cx - lb.width / 2), int(cy - lb.height / 2)))
    return draw


def prima_box(t_in, t_out, frames, x=50, y=560):
    """riquadro PRIMA (video piccolo con bordo bianco + etichetta nera) che entra da sinistra e poi esce"""
    tag = m.label("PRIMA", BLACK, 54)

    def draw(im, t, dur):
        if t < t_in or t > t_out + 0.2:
            return
        e = ease((t - t_in) / 0.2) * (1 - ease((t - t_out) / 0.2))
        fr = frames[min(int((t - t_in) * 30), len(frames) - 1)]          # finito il pezzo resta fermo
        box = Image.new("RGBA", (fr.width + 12, fr.height + 12), (255, 255, 255, 255))
        box.paste(fr, (6, 6))
        mk = Image.new("L", box.size, 0)
        ImageDraw.Draw(mk).rounded_rectangle([0, 0, box.width - 1, box.height - 1], 26, fill=255)
        box.putalpha(mk)
        dx = int(-(box.width + x + 20) * (1 - e))
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        lay.paste(box, (x + dx, y), box)
        lay.paste(tag, (x + dx + 16, y - tag.height + 14), tag)
        im.alpha_composite(lay)
    return draw


def make(v):
    names = ["H", "OB", "COR", "LEI", "CTA"] if v == "A" else ["OB", "H", "COR", "LEI", "CTA"]
    segs = []
    for n in names:
        for a, b in PH[n]:
            for s0, s1 in m.subsegs(a, b):
                segs.append((NORM, s0, s1))

    def ref(src):
        """secondo del parlato -> (segmento, secondo): i pezzi non sono in ordine di registrazione (in B l'obiettivo
        viene prima), quindi si cerca il segmento che lo contiene, altrimenti quello che inizia subito dopo"""
        for k, (_, s0, s1) in enumerate(segs):
            if s0 - 1e-6 <= src < s1:
                return (k, src)
        after = [(s0, k) for k, (_, s0, s1) in enumerate(segs) if s0 >= src]
        if after:
            s0, k = min(after)
            return (k, s0)
        k = max(range(len(segs)), key=lambda k: segs[k][2])
        return (k, segs[k][2])

    def start(n):
        return ref(PH[n][0][0])

    def nxt(n):
        i = names.index(n)
        return start(names[i + 1]) if i + 1 < len(names) else "end"

    SO, t = [], 0.0
    for _, a, b in segs:
        SO.append(t)
        t += round((b - a) / 1.1 * 30) / 30

    def t_of(src):
        k, s = ref(src)
        return SO[k] + (s - segs[k][1]) / 1.1

    def loc(src, n):
        return t_of(src) - t_of(PH[n][0][0])

    # sottotitoli: nel primo secondo un solo testo -> si salta la prima pagina del primo pezzo
    pages = []
    for i_n, n in enumerate(names):
        kp = m.kara_pages(n)
        if i_n == 0:  # salta la prima pagina (le voci fino alla prossima che non inizia con "§")
            j = next(k for k in range(1, len(kp)) if not kp[k][1].startswith("§"))
            kp = kp[j:]
        if v == "B" and n == "OB":
            continue        # in B la frase dell'obiettivo e' gia' scritta nel titolo grande: niente doppio testo
        for i, (s, txt) in enumerate(kp):
            pages.append(((start(n) if (i == 0 and i_n > 0) else ref(s)), txt))

    frames = prima_frames()
    t_a, t_oggi = t_of(39.02), t_of(44.35)                 # "a fare una trazione" / "Oggi"
    h_dur = t_of(45.59) - t_of(38.14)
    if v == "A":
        h_clip, h_ss = f"{BR}/IMG_5416b.mp4", 0.5
        br = [(start("H"), nxt("H"), h_clip, h_ss, 1.0, 1.0, None),
              (start("OB"), nxt("OB"), f"{OUT}/anim_scheda.mp4", 0.0, 1.0, 1.0, None)]
        h0 = t_of(38.14)
        hk = [(start("H"), nxt("H"), counter(0.08, 0.9)),
              (start("H"), nxt("H"), prima_box(t_a - h0, t_oggi - h0 - 0.05, frames))]
        ob = [(start("OB"), nxt("OB"), m.titles([("TU L'OBIETTIVO", "n", 290), ("IO IL PERCORSO", "o", 392)]))]
        s_h = [(start("H"), 0.08, "trascina", 0.07), (start("H"), 0.9, "pop", 0.12),
               (ref(39.02), 0.0, "swoosh", 0.08), (ref(44.35), -0.05, "swoosh", 0.06),
               (start("OB"), 0.0, "whoosh", 0.10)]
        an_dur = t_of(58.08) - t_of(55.80)
    else:
        br = [(start("OB"), nxt("OB"), f"{BR}/IMG_5416b.mp4", 0.5, 1.0, 1.0, None),
              (start("H"), nxt("H"), f"{BR}/IMG_5415.mp4", 1.6, 1.0, 1.0, None)]
        h0 = t_of(38.14)
        ob = [(start("OB"), nxt("OB"), m.titles([("TU L'OBIETTIVO", "n", 1170), ("IO IL PERCORSO", "o", 1272)]))]
        hk = [(start("H"), nxt("H"), prima_box(t_a - h0, t_oggi - h0 - 0.05, frames)),
              (start("H"), nxt("H"), counter(t_oggi - h0, t_of(45.03 + m.D) - h0))]
        s_h = [(start("OB"), 0.0, "comparsa", 0.12), (ref(39.02), 0.0, "swoosh", 0.08),
               (ref(44.35), -0.05, "swoosh", 0.06), (ref(44.35), 0.0, "trascina", 0.07),
               (ref(45.03 + m.D), 0.0, "pop", 0.12)]
        an_dur = None
    br += [(start("COR"), nxt("COR"), f"{BR}/IMG_9172.mp4", 0.2, 1.0, 1.0, None),
           (start("LEI"), nxt("LEI"), f"{BR}/IMG_5418.mp4", 5.0, 1.0, 1.0, None)]
    overlays = hk + ob + [(start("CTA"), nxt("CTA"), m.comment_box(
        0.10, loc(163.32 + m.D - 0.12, "CTA"), loc(163.88 + m.D - 0.1, "CTA"), wa="controllo", wb="mi fido"))]
    sfx = s_h + [(start("CTA"), 0.08, "comparsa", 0.10), (ref(163.32 + m.D), -0.1, "pop", 0.07),
                 (ref(163.88 + m.D), 0.0, "pop", 0.07)]
    if an_dur:  # scheda animata (3 blocchi) della durata esatta della frase
        sh(f"python3 {R}/projects/anim_scheda_elisabetta.py {an_dur + 0.1:.3f} && "
           f"cp {R}/out/eli/anim/scheda.mp4 {OUT}/anim_scheda.mp4")
        sfx += [(start("OB"), an_dur / 3, "swoosh", 0.07), (start("OB"), 2 * an_dur / 3, "swoosh", 0.07)]

    def cut(fn):
        return lambda im, t, dur: None if t >= dur - 1 / 60 else fn(im, t, dur)
    overlays = [(a0, a1, cut(fn)) for a0, a1, fn in overlays]
    tot = build(dict(out=f"{OUT}/{v}", name=f"elisabetta_v2_{v}", segs=segs, pages=pages, br=br, titles=[],
                     glow=[], overlays=overlays, sfx=sfx))
    f = f"{OUT}/{v}/elisabetta_v2_{v}.mp4"
    sh(f"ffmpeg -v error -y -i {f} -c:v copy -af aresample=192000,alimiter=limit=0.79:level=false,aresample=48000 "
       f"-c:a aac -b:a 192k -movflags +faststart {f}.tmp.mp4 && mv {f}.tmp.mp4 {f}")
    return tot


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for v in (sys.argv[1:] or ["A", "B"]):
        make(v)
