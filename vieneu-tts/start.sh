#!/bin/bash
# Chạy VieNeu TTS API trên Linux
set -e
cd "$(dirname "$0")"
if [ ! -d ".venv" ]; then
  echo "[1/3] Tạo môi trường ảo..."
  python3 -m venv .venv
fi
echo "[2/3] Cài đặt thư viện..."
.venv/bin/pip install -q -r requirements.txt
# soundfile chỉ import lười khi xử lý WAV nên server vẫn lên mà request
# /speak đầu tiên mới lỗi: kiểm tra ngay tại đây để fail nhanh, rõ lý do.
if ! .venv/bin/python -c "import soundfile" 2>/dev/null; then
  echo "THIẾU libsndfile (thư viện soundfile cần trên Linux)."
  echo "Cài bằng: sudo apt-get install -y libsndfile1 (Debian/Ubuntu) rồi chạy lại start.sh."
  exit 1
fi
echo "[3/3] Khởi động API..."
export VIENEU_MODE="${VIENEU_MODE:-v3nano}"
.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000
