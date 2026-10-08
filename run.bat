@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
streamlit run app.py --server.address 127.0.0.1
pause
