# Video-maker

Reel Instagram 9:16 (1080x1920) per @_manuelferrante: sfondo + busto scontornato + sottotitoli karaoke,
copertina e caption. Regole e flusso completo in `CLAUDE.md`.

- `analyze_clips.py` – trascrive i clip parlati (parakeet), trova inizio/fine voce, bozza dei segmenti
- `make_reel.py` – monta il reel da `projects/<nome>.json`
- `make_cover.py` – copertina dalla sezione `cover` dello stesso JSON
- `.claude/hooks/session-start.sh` – installa dipendenze, modelli e font nelle sessioni cloud

    python3 analyze_clips.py out/draft.json clip1.mov clip2.mov
    python3 make_reel.py projects/streetlifting_635.json
    python3 make_cover.py projects/streetlifting_635.json
