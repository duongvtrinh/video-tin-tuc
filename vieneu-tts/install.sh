#!/bin/bash
# Cai dat VieNeu TTS — CHI CAI DAT, khong chay server (BOOTSTRAP C2).
# Tao venv + cai goi theo requirements.txt + kiem tra import soundfile.
# Chay server rieng bang start.sh sau khi cai xong.
# Chay tu thu muc vieneu-tts/: bash install.sh
set -e
cd "$(dirname "$0")"
if [ ! -d ".venv" ]; then
  echo "[1/3] Tao moi truong ao..."
  python3 -m venv .venv
fi
echo "[2/3] Cai dat thu vien..."
.venv/bin/pip install -q -r requirements.txt
echo "[3/3] Kiem tra import soundfile..."
if ! .venv/bin/python -c "import soundfile" 2>/dev/null; then
  echo "THIEU libsndfile (thu vien soundfile can tren Linux)."
  echo "Cai bang: sudo apt-get install -y libsndfile1 (Debian/Ubuntu) roi chay lai install.sh."
  exit 1
fi
echo "Cai xong. Chay server bang: bash start.sh"
