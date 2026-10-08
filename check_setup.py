"""Run this first on any computer:  python check_setup.py
It tells you exactly what is missing. Works on Windows, macOS and Linux."""
import importlib.util
import os
import sys

MODEL = os.getenv("KG_LLM_MODEL", "qwen2.5:3b")
HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
bad = 0


def show(ok, msg, fix=""):
    global bad
    print(("[OK]   " if ok else "[FIX]  ") + msg)
    if not ok:
        bad += 1
        if fix:
            print("       -> " + fix)


v = sys.version_info
show((3, 10) <= v[:2] <= (3, 12), f"Python {v.major}.{v.minor}.{v.micro} (3.10 to 3.12 recommended)",
     "Install Python 3.11 from python.org, then make a new .venv with it")
for pkg in ["streamlit", "pandas", "faster_whisper", "ollama"]:
    show(importlib.util.find_spec(pkg) is not None, f"package {pkg}",
         "Activate the .venv, then run: pip install -r requirements.txt")
try:
    import ollama
    names = []
    resp = ollama.Client(host=HOST).list()
    for m in (resp["models"] if isinstance(resp, dict) else resp.models):
        names.append((m.get("model") if isinstance(m, dict) else getattr(m, "model", "")) or "")
    show(True, f"Ollama is running at {HOST}")
    show(any(n.startswith(MODEL) for n in names), f"model {MODEL} is downloaded",
         f"Run: ollama pull {MODEL}")
except Exception as e:
    show(False, f"Ollama is not reachable ({type(e).__name__})",
         "Windows/Mac: open the Ollama app. Linux: run 'ollama serve' in another terminal")
try:
    from faster_whisper import WhisperModel
    WhisperModel(os.getenv("KG_WHISPER_SIZE", "small"), device="cpu", compute_type="int8")
    show(True, "Whisper model loads (the first time it downloads about 460 MB)")
except Exception as e:
    show(False, f"Whisper could not load ({type(e).__name__}: {e})",
         "Connect to the internet once so it can download, or set KG_WHISPER_SIZE=base")
print()
print("Everything is ready." if bad == 0 else f"{bad} thing(s) to fix. Fix them top to bottom, then run this again.")
