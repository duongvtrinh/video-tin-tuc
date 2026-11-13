#!/bin/bash
# Kiem tra tien quyet truoc khi cai Muse moi (BOOTSTRAP C0).
# In bang dat/thieu cho TOAN BO muc roi moi ket thuc — thieu thi liet ke
# het mot lan, khong dung o muc dau tien. Chi doc, khong cai dat gi.
# Chay: bash ~/workspace/video-tin-tuc/check-prereqs.sh
PASS=0
FAIL=0
check() { # $1 = ten muc, cac doi so con lai = lenh kiem tra (tra 0 la dat)
  local name="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "[DAT]   $name"; PASS=$((PASS + 1))
  else
    echo "[THIEU] $name"; FAIL=$((FAIL + 1))
  fi
}
check "ffmpeg" ffmpeg -version
check "python3 (>= 3.11)" python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"
check "bun" bun --version
check "libsndfile (ldconfig)" bash -c "ldconfig -p | grep -q libsndfile"
check "dia trong >= 20GB" bash -c '[ "$(df --output=avail -BG "$HOME" | tail -1 | tr -dc 0-9)" -ge 20 ]'
check "mang toi HuggingFace" bash -c 'curl -s -m 10 -o /dev/null -w "%{http_code}" https://huggingface.co | grep -q 200'
echo "---"
echo "Dat: $PASS, Thieu: $FAIL"
[ "$FAIL" -eq 0 ] || exit 1
