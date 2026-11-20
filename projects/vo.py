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


def refine(path, a, b, below=32, pad=0.04):
    """Stringe [a, b] sulla voce reale (blocchi 10 ms sopra picco - 32 dB)."""
    db = audio(path)
    thr = np.percentile(db, 99) - below
    i0, i1 = int(max(a - 0.12, 0) * 100), int((b + 0.12) * 100)
    idx = [i for i in range(i0, min(i1, len(db))) if db[i] > thr]
    if not idx:
        return a, b
    return max(idx[0] / 100 - pad, 0), (idx[-1] + 1) / 100 + pad


def norm(w):
    w = unicodedata.normalize("NFKD", w.lower())
    return "".join(c for c in w if c.isalnum())


def layout(pieces, t0=0.0, gap=0.0):
    """-> voice [(t_reel, file, a, b)], words [(t_reel, parola_testo)], pagine, fine."""
    voice, t = [], t0
    for pc in pieces:
        path, a, b, txt = pc[:4]
        a2, b2 = refine(path, a, b)
        if len(pc) > 4 and pc[4] == "fix_a":  # inizio scelto a mano (es. primo fotogramma con gli occhi aperti)
            a2 = a
        voice.append((t, path, a2, b2, txt))
        t += (b2 - a2) / SP + gap
    return voice, t


def kara_pages(voice, trjson):
    """Pagine karaoke: ogni '|' nel testo apre una pagina; i tempi parola dal json (sequenza dentro il pezzo)."""
    tr = {}
    for path, js in trjson.items():
        tr[path] = [(w, t + 0.2) for blk in json.load(open(js)) for w, t in blk["words"]]
    pages = []
    for t_reel, path, a, b, txt in voice:
        words_src = [(w, t) for w, t in tr[path] if a - 0.25 <= t <= b + 0.1]
        toks = txt.replace("|", " | ").replace("/", " / ").split()
        n_words = [x for x in toks if x not in ("|", "/")]
        # allinea in ordine: per ogni parola del testo il primo tempo utile con parola simile, altrimenti interpola
        times, j = [], 0
        for w in n_words:
            found = None
            for jj in range(j, min(j + 4, len(words_src))):
                if norm(words_src[jj][0])[:4] == norm(w)[:4] and norm(w):
                    found = jj
                    break
            if found is not None:
                times.append(words_src[found][1]); j = found + 1
            else:
                times.append(None)
        # interpola i mancanti
        dur = b - a
        for i, x in enumerate(times):
            if x is None:
                prev = next((times[q] for q in range(i - 1, -1, -1) if times[q] is not None), a)
                nxt = next((times[q] for q in range(i + 1, len(times)) if times[q] is not None), b)
                cnt = sum(1 for q in range(i, len(times)) if times[q] is None and
                          all(times[r] is None for r in range(i, q + 1)))
                times[i] = prev + (nxt - prev) / (cnt + 1)
        to_reel = lambda s, t_reel=t_reel, a=a, b=b: t_reel + (max(min(s, b), a) - a) / SP
        cur, wi = [], 0
        for x in toks:
            if x == "|":
                if cur:
                    pages.append(cur); cur = []
            elif x == "/":
                cur.append(("\n", None))
            else:
                tt = to_reel(times[wi])
                cur.append((x, tt)); wi += 1
        if cur:
            pages.append(cur)
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
            k.put(im, cache[key], 540, y, k.pop((t - starts[i]) / 0.2) if starts[i] > 0.05 else 1)
            return
    return fn
