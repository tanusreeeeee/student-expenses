@echo off
cd /d "%~dp0"
py -3.12 -m venv .venv || python -m venv .venv
call .venv\Scripts\activate.bat
pip install -r requirements.txt || (echo pip install failed & pause & exit /b 1)
python -c "from faster_whisper import WhisperModel; WhisperModel(\"small\")"
ollama pull qwen2.5:3b
python check_setup.py
echo Setup finished.
pause
