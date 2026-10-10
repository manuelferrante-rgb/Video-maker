#!/usr/bin/env python3
"""Trascrive i clip parlati e prepara la bozza dei segmenti per make_reel.py.

Uso:  python3 analyze_clips.py out.json clip1.mov clip2.mov ...

Per ogni clip: testo (parakeet), inizio/fine reale della voce (energia audio, i timestamp
del modello sono spesso in anticipo di 0.3-0.5 s) e tempi parola rimappati dentro la voce.
Il risultato va RILETTO: correggere parole sbagliate (es. "masso l'app" = muscle up),
numeri, e poi aggiungere a mano "layout" e "background" per ogni segmento.
"""
import json, os, subprocess, sys
import numpy as np, sherpa_onnx

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, "models", "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8")


def load_audio(path, sr=16000):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:a:0", "-ac", "1", "-ar", str(sr),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32), sr


def speech_bounds(a, sr, below_peak_db=28, pad=0.03):
    """Primo e ultimo tratto sopra (picco - 28 dB), a blocchi di 10 ms; ignora click isolati."""
    hop = sr // 100
    n = len(a) // hop
    db = 20 * np.log10(np.sqrt(np.mean(a[:n * hop].reshape(n, hop) ** 2, axis=1)) + 1e-9)
    v = db > np.percentile(db, 98) - below_peak_db
    # tieni solo tratti di voce >= 80 ms
    idx = [i for i in range(n) if v[i] and v[i:i + 8].sum() >= 6]
    s, e = idx[0] * 0.01, (idx[-1] + 1) * 0.01
    return max(s - pad, 0), min(e + pad, len(a) / sr)


def words_from_tokens(tokens, ts):
    words = []
    for tok, t in zip(tokens, ts):
        if tok.startswith(" ") or not words:
            words.append([tok.strip(), t])
        else:
            words[-1][0] += tok
    return [w for w in words if w[0] and w[0] not in ".,!?"]


def main(out, clips):
    rec = sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=f"{MODEL}/encoder.int8.onnx", decoder=f"{MODEL}/decoder.int8.onnx",
        joiner=f"{MODEL}/joiner.int8.onnx", tokens=f"{MODEL}/tokens.txt",
        model_type="nemo_transducer", num_threads=4)
    segs = []
    for c in clips:
        a, sr = load_audio(c)
        st = rec.create_stream()
        st.accept_waveform(sr, a)
        rec.decode_stream(st)
        r = st.result
        s, e = speech_bounds(a, sr)
        words = words_from_tokens(list(r.tokens), list(r.timestamps))
        if words:  # rimappa linearmente i tempi del modello dentro la voce reale
            t0, t1 = words[0][1], max(r.timestamps[-1], words[-1][1] + 0.2)
            k = (e - s) / max(t1 - t0, 1e-3)
            words = [[w.upper().strip(".,!?"), round(s + (t - t0) * k, 2)] for w, t in words]
        print(f"{os.path.basename(c)}  voce {s:.2f}-{e:.2f}s  | {r.text}")
        segs.append({"clip": os.path.abspath(c), "cut": [round(s, 2), round(e, 2)], "text": r.text,
                     "words": words, "layout": "mid_c", "background": []})
    json.dump(segs, open(out, "w"), indent=1, ensure_ascii=False)
    print("bozza ->", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
