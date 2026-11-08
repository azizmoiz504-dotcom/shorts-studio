#!/usr/bin/env bash
# One-time setup in a fresh session (about 2-4 minutes). Run from the repo root: bash setup.sh
set -e
pip install --break-system-packages -q skia-python kokoro-onnx soundfile pocketsphinx scipy pillow numpy 2>&1 | tail -1 || true
mkdir -p models
[ -s models/kokoro-v1.0.onnx ] || curl -sSL -o models/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -s models/voices-v1.0.bin ] || curl -sSL -o models/voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
python3 -c "import skia, kokoro_onnx, pocketsphinx, soundfile, scipy; print('SETUP OK')"
which ffmpeg ffprobe >/dev/null && echo "ffmpeg OK"
