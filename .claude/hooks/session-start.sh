#!/bin/bash
# Prepara l'ambiente cloud per generare reel: dipendenze Python, modelli e font.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
M="$ROOT/models"
mkdir -p "$M"

pip install -q --break-system-packages -r "$ROOT/requirements.txt" 2>&1 | grep -v "WARNING: Running pip" || true

dl() {  # dl URL DEST
  if [ ! -s "$2" ]; then curl -fsSL --retry 3 -o "$2.part" "$1" && mv "$2.part" "$2"; fi
}
# scontorno persona (U^2-Net human seg)
dl https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx "$M/u2net_human_seg.onnx"
# font sottotitoli/copertina
dl https://raw.githubusercontent.com/google/fonts/main/ofl/anton/Anton-Regular.ttf "$M/Anton-Regular.ttf"
# trascrizione italiana con timestamp (parakeet-tdt-0.6b-v3, multilingua)
P="$M/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"
if [ ! -s "$P/tokens.txt" ]; then
  curl -fsSL --retry 3 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2 | tar xj -C "$M"
fi
