# Video-maker

`make_reel.py` monta un reel Instagram 9:16 (1080x1920):
- video di sfondo (tagliato per segmento, con riempimento sfocato se ha bande nere)
- busto scontornato (U^2-Net human seg + pulizia del muro bianco) in basso a sinistra, con leggero movimento
- audio dei clip parlati accelerato (es. 1.1x), normalizzato a -14 LUFS
- sottotitoli maiuscoli bianchi con bordo nero, parola pronunciata in azzurro

Dipendenze: ffmpeg (con zscale/libass), `pip install onnxruntime opencv-python-headless numpy`,
modello `u2net_human_seg.onnx`, font Anton. Trascrizione con sherpa-onnx (parakeet-tdt-0.6b-v3 + whisper-medium).

    python3 make_reel.py projects/streetlifting_635.json
