#!/usr/bin/env python3
"""Trascrive un parlato lungo a blocchi di voce (parakeet salta pezzi nelle clip lunghe con pause).
Uso: python3 trascrivi_blocchi.py clip.MOV [out.json]
Blocchi = tratti sopra (picco - 32 dB) a 10 ms, uniti se la pausa < 0,35 s. Per ogni blocco: tempi e testo, piu'
i tempi parola (token del modello, in anticipo ~0,3 s)."""
import json, sys
import numpy as np
sys.path.insert(0, "/home/user/Video-maker")
from analyze_clips import load_audio, words_from_tokens, MODEL
import sherpa_onnx


def blocks(a, sr, below=32, gap=0.35, minlen=0.25):
    hop = sr // 100
    n = len(a) // hop
    db = 20 * np.log10(np.sqrt(np.mean(a[:n * hop].reshape(n, hop) ** 2, axis=1)) + 1e-9)
    v = db > np.percentile(db, 99) - below
    out, s = [], None
    for i, x in enumerate(v):
        if x and s is None:
            s = i
        if not x and s is not None:
            out.append([s, i]); s = None
    if s is not None:
        out.append([s, n])
    merged = []
    for b in out:
        if merged and (b[0] - merged[-1][1]) * 0.01 < gap:
            merged[-1][1] = b[1]
        else:
            merged.append(b)
    return [(s * 0.01, e * 0.01) for s, e in merged if (e - s) * 0.01 >= minlen]


def main(clip, out=None):
    rec = sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=f"{MODEL}/encoder.int8.onnx", decoder=f"{MODEL}/decoder.int8.onnx",
        joiner=f"{MODEL}/joiner.int8.onnx", tokens=f"{MODEL}/tokens.txt",
        model_type="nemo_transducer", num_threads=4)
    a, sr = load_audio(clip)
    res = []
    for s, e in blocks(a, sr):
        s0, e0 = max(s - 0.05, 0), min(e + 0.05, len(a) / sr)
        st = rec.create_stream()
        st.accept_waveform(sr, a[int(s0 * sr):int(e0 * sr)])
        rec.decode_stream(st)
        r = st.result
        w = [[x, round(s0 + t, 2)] for x, t in words_from_tokens(list(r.tokens), list(r.timestamps))]
        res.append({"s": round(s, 2), "e": round(e, 2), "text": r.text.strip(), "words": w})
        print(f"{s:7.2f}-{e:7.2f}  {r.text.strip()}")
    if out:
        json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main(*sys.argv[1:])
