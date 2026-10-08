#!/usr/bin/env bash
cd "$(dirname "$0")"
# Python 3.12 is the safest. Newer versions (3.13, 3.14) may be missing some packages.
PY=python3.12; command -v $PY >/dev/null 2>&1 || PY=python3
echo "Using: $($PY --version)"
$PY -m venv .venv && source .venv/bin/activate || exit 1
pip install -r requirements.txt || { echo "pip install failed"; exit 1; }
python -c "from faster_whisper import WhisperModel; WhisperModel(\"small\")" || exit 1
ollama pull qwen2.5:3b
python check_setup.py
