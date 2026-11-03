@echo off
REM Chay VieNeu TTS API tren Windows
cd /d "%~dp0"
if not exist ".venv" (
    echo [1/3] Tao moi truong ao...
    py -m venv .venv
)
echo [2/3] Cai dat thu vien...
.venv\Scripts\pip install -q -r requirements.txt
echo [3/3] Khoi dong API...
if "%VIENEU_MODE%"=="" set VIENEU_MODE=v3nano
.venv\Scripts\uvicorn server:app --host 0.0.0.0 --port 8000
