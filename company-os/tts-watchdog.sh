#!/bin/bash
# Watchdog TTS: cron tts-watchdog gọi mỗi 30 phút.
# - /health OK -> im lặng, exit 0.
# - /health lỗi -> cài lại unit (nếu /etc mất sau khi thay máy) + restart service, chờ, kiểm tra lại.
# - Vẫn lỗi -> kill tiến trình lạ chiếm cổng 8000 rồi restart lần nữa.
# - Vẫn lỗi -> ghi log + exit 1 (cron báo chat COO).
# Chỉ chạm TTS, không chạm việc khác. Log: <thư mục chứa script>/tts-watchdog.log
# Đường dẫn suy ra từ vị trí của chính script (SCRIPT_DIR) nên chạy đúng
# cả ở ~/workspace/company-os/ (máy hiện tại) lẫn ở bản clone mới của
# monorepo (~/workspace/video-tin-tuc/company-os/, qua symlink
# ~/workspace/company-os/ hoặc gọi trực tiếp đường clone).
set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UNIT_SRC="$SCRIPT_DIR/systemd/vieneu-tts.service"
UNIT_DST="/etc/systemd/system/vieneu-tts.service"
LOG="$SCRIPT_DIR/tts-watchdog.log"

healthy() { curl -s -m 5 http://127.0.0.1:8000/health 2>/dev/null | grep -q '"status":"ok"'; }
ts() { date '+%Y-%m-%d %H:%M:%S %Z'; }

if healthy; then exit 0; fi
echo "$(ts) TTS /health loi, thu khoi dong lai" >> "$LOG"

if [ ! -f "$UNIT_DST" ]; then
  echo "$(ts) unit khong co trong /etc (may vua thay the?) — cai lai tu $UNIT_SRC" >> "$LOG"
  cp "$UNIT_SRC" "$UNIT_DST" && systemctl daemon-reload && systemctl enable vieneu-tts >/dev/null 2>&1
fi
systemctl restart vieneu-tts 2>&1 | tail -1 >> "$LOG"
sleep 25
if healthy; then echo "$(ts) TTS da khoi dong lai OK" >> "$LOG"; exit 0; fi

echo "$(ts) van loi sau restart, kill tien trinh chiem cong 8000 roi restart lan nua" >> "$LOG"
fuser -k 8000/tcp >/dev/null 2>&1; sleep 2
systemctl restart vieneu-tts 2>&1 | tail -1 >> "$LOG"
sleep 25
if healthy; then echo "$(ts) TTS da khoi dong lai OK (sau khi don cong 8000)" >> "$LOG"; exit 0; fi

echo "$(ts) FAILED: TTS van khong len sau 2 lan thu — can nguoi kiem tra" >> "$LOG"
exit 1
