# Hisaab Guru
One site, two modes. Everything runs on your own computer (localhost only). No login, no cloud.
- Shopkeeper mode = Khata Guru: speak your udhaar in Hindi or English, confirm it, see who to chase. Uses Whisper + Qwen 2.5 3B through Ollama.
- Student mode = SpendWise: expenses, monthly budget, needs vs wants, analytics, savings goals. Works instantly on local SQLite.

## Before you start (one time, with internet)
1. Python 3.12: https://www.python.org/downloads/ (Windows: tick "Add python.exe to PATH").
2. Ollama: https://ollama.com/download (open it once so it keeps running).

## Setup (one time)
- Mac/Linux: open Terminal in this folder and run `bash setup.sh`
- Windows: double-click `setup.bat`
It makes the .venv, installs packages, downloads Whisper (about 460 MB) and Qwen (about 2 GB), then checks everything.

## Run
- Mac/Linux: `bash run.sh`
- Windows: double-click `run.bat`
Opens at http://localhost:8501. Allow the microphone when asked.

## If something is red
Run `python check_setup.py` (with the .venv active). Every line marked [FIX] tells you what to do.
Change the site name: APP_NAME at the top of app.py.
Look: edit colors/radii in theme.py (see design-system.md).
