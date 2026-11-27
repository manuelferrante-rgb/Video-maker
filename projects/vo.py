#!/usr/bin/env python3
"""Voce per tl_kit: pezzi di parlato rifilati sull'energia (pause tagliate), messi in fila a 1,1x, e sottotitoli
parola per parola (karaoke: la parola detta e' arancio).
pieces = [(file, a, b, testo)]   a/b approssimati (secondi nel file); il testo serve per i sottotitoli: '|' = nuova
pagina, '/' = a capo. I tempi parola arrivano dal json di trascrivi_blocchi.py (+0,2 s, parakeet e' in anticipo)."""
import json, subprocess, unicodedata
import numpy as np
import tl_kit as k

SP = 1.1
_aud = {}


def audio(path, sr=16000):
    if path not in _aud:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:a:0", "-ac", "1", "-ar", str(sr),
                              "-f", "f32le", "-"], capture_output=True, check=True).stdout
        a = np.frombuffer(raw, np.float32)
        hop = sr // 100
        n = len(a) // hop
        db = 20 * np.log10(np.sqrt(np.mean(a[:n * hop].reshape(n, hop) ** 2, axis=1)) + 1e-9)
        _aud[path] = db
    return _aud[path]


def thr_for(db, below, a=None, b=None):
    """Soglia voce: picco - below, ma almeno 6 dB sopra il rumore di fondo LOCALE (2 s attorno al pezzo: col mic in
    mano il fondo e' alto e cambia da un punto all'altro)."""
    thr = np.percentile(db, 99) - below
    if a is not None:
        w = db[max(int((a - 1.0) * 100), 0):int((b + 1.0) * 100)]
        if len(w):
            thr = max(thr, np.percentile(w, 10) + 6)
    return thr


def refine(path, a, b, below=26, pad=0.05):
    """Stringe [a, b] sulla voce reale (blocchi 10 ms sopra la soglia)."""
    db = audio(path)
    thr = thr_for(db, below, a, b)
    i0, i1 = int(max(a, 0) * 100), int(b * 100)  # solo restringe: i tagli scelti a mano non si allargano mai
    idx = [i for i in range(i0, min(i1, len(db))) if db[i] > thr]
    if not idx:
        return a, b
    return max(idx[0] / 100 - pad, a), min((idx[-1] + 1) / 100 + pad, b)


def norm(w):
    w = unicodedata.normalize("NFKD", w.lower())
    return "".join(c for c in w if c.isalnum())


def split_gaps(path, a, b, below=25, min_gap=0.11, keep=0.035):
    """Toglie le pause e i respiri DENTRO un pezzo: tratti sotto (picco - 27 dB) piu' lunghi di 0,11 s."""
    db = audio(path)
    thr = thr_for(db, below, a, b)
    i0, i1 = int(a * 100), int(b * 100)
    v = db[i0:i1] > thr
    segs, s0, j = [], 0, 0
    n = len(v)
    while j < n:
        if not v[j]:
            k2 = j
            while k2 < n and not v[k2]:
                k2 += 1
            if (k2 - j) / 100 >= min_gap and j > 0 and k2 < n:
                segs.append((a + s0 / 100, a + j / 100 + keep))
                s0 = max(k2 - int(keep * 100), 0)
            j = k2
        else:
            j += 1
    segs.append((a + s0 / 100, b))
    return [(x, y) for x, y in segs if y - x > 0.06]


def layout(pieces, t0=0.0, gap=0.0, sp=SP, cut_inner=True):
    """-> voice [(t_reel, file, a, b, testo)] (un elemento per sotto-pezzo; il testo sta sul primo), fine.
    pieces: (file, a, b, testo[, "fix_a"])."""
    voice, t = [], t0
    for pc in pieces:
        path, a, b, txt = pc[:4]
        flags = pc[4:] if len(pc) > 4 else ()
        a2, b2 = refine(path, a, b)
        if "fix_a" in flags:
            a2 = a
        if "fix_b" in flags:
            b2 = b
        subs = split_gaps(path, a2, b2) if cut_inner else [(a2, b2)]
        for i, (x, y) in enumerate(subs):
            voice.append((t, path, x, y, txt if i == 0 else None))
            t += (y - x) / sp
        t += gap
    return voice, t


def src_to_reel(voice, path, s, sp=SP):
    """Secondo nel file -> secondo nel reel (dentro il sotto-pezzo che lo contiene, o il piu' vicino)."""
    best = None
    for t_reel, p, a, b, _ in voice:
        if p != path:
            continue
        if a <= s <= b:
            return t_reel + (s - a) / sp
        d = min(abs(s - a), abs(s - b))
        if best is None or d < best[0]:
            best = (d, t_reel + (min(max(s, a), b) - a) / sp)
    return best[1]


def kara_pages(voice, trjson, sp=SP):
    """Pagine karaoke: ogni '|' nel testo apre una pagina, '/' va a capo; tempi parola dal json (+0,2 s)."""
    tr = {}
    for path, js in trjson.items():
        tr[path] = [(w, t + 0.2) for blk in json.load(open(js)) for w, t in blk["words"]]
    groups = []
    for v in voice:
        if v[4] is not None:
            groups.append([v])
        else:
            groups[-1].append(v)
    pages = []
    for g in groups:
        path, txt = g[0][1], g[0][4]
        a, b = g[0][2], g[-1][3]
        words_src = [(w, t) for w, t in tr[path] if a - 0.25 <= t <= b + 0.1]
        toks = txt.replace("|", " | ").replace("/", " / ").split()
        n_words = [x for x in toks if x not in ("|", "/")]
        times, j = [], 0
        for w in n_words:
            found = None
            for jj in range(j, min(j + 4, len(words_src))):
                if norm(w) and norm(words_src[jj][0])[:4] == norm(w)[:4]:
                    found = jj
                    break
            if found is not None:
                times.append(words_src[found][1]); j = found + 1
            else:
                times.append(None)
        for i in range(len(times)):  # interpola i mancanti
            if times[i] is None:
                prev = next((times[q] for q in range(i - 1, -1, -1) if times[q] is not None), a)
                q2 = next((q for q in range(i + 1, len(times)) if times[q] is not None), None)
                nxt = times[q2] if q2 is not None else b
                span = (q2 if q2 is not None else len(times)) - i + 1
                times[i] = prev + (nxt - prev) / span
        cur, wi = [], 0
        for x in toks:
            if x == "|":
                if cur:
                    pages.append(cur); cur = []
            elif x == "/":
                cur.append(("\n", None))
            else:
                cur.append((x, src_to_reel(g, path, times[wi], sp))); wi += 1
        if cur:
            pages.append(cur)
    # la prima pagina parte dal primo fotogramma
    return pages


def kara_layer(pages, y=1450, size=76, end=1e9, maxw=1000, first_from=None):
    """Disegna le pagine: tutte bianche, la parola in corso arancio; pop all'ingresso della pagina.
    Ogni pagina resta fino all'inizio della successiva (la voce e' continua). first_from: inizio della 1a pagina."""
    starts = [next(t for w, t in p if t is not None) for p in pages]
    if first_from is not None:
        starts[0] = first_from
    cache = {}

    def fn(im, t):
        for i, p in enumerate(pages):
            b = starts[i + 1] if i + 1 < len(pages) else end
            if not (starts[i] <= t < b):
                continue
            ws = [(w, tt) for w, tt in p if w != "\n"]
            if not any(w for w, tt in ws):  # pagina nascosta (es. sotto il 150 KG)
                return
            cur = max([j for j, (w, tt) in enumerate(ws) if tt <= t + 0.03] or [0])
            key = (i, cur)
            if key not in cache:
                out, j = [], 0
                for w, tt in p:
                    if w == "\n":
                        out.append("\n")
                    else:
                        out.append(f"*{w}*" if j == cur else w); j += 1
                txt = " ".join(out).replace(" \n ", "\n")
                cache[key] = k.text_img(txt, size=size, maxw=maxw)
            k.put(im, cache[key], 540, y(t) if callable(y) else y, k.pop((t - starts[i]) / 0.2) if starts[i] > 0.05 else 1)
            return
    return fn


def groups(voice):
    """Sotto-pezzi raggruppati per frase: [(t_inizio, [sotto-pezzi])]."""
    out = []
    for v in voice:
        if v[4] is not None:
            out.append((v[0], [v]))
        else:
            out[-1][1].append(v)
    return out


def cam_shots(group, t_end, sp=SP, z0=1.0, z1=1.06, c=(540, 820)):
    """Riprese in camera tagliate come la voce (jump cut sulle pause tolte): il labiale resta a tempo."""
    subs = group[1]
    out = []
    for i, (t, path, a, b, _) in enumerate(subs):
        t1 = subs[i + 1][0] if i + 1 < len(subs) else t_end
        u0 = (t - subs[0][0]) / max(t_end - subs[0][0], 1e-3)
        u1 = (t1 - subs[0][0]) / max(t_end - subs[0][0], 1e-3)
        out.append(dict(t0=t, t1=t1, src=path, ss=a, sp=sp, z0=z0 + (z1 - z0) * u0, z1=z0 + (z1 - z0) * u1, c=c,
                        nosw=i > 0))
    return out
