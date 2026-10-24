#!/usr/bin/env bash
set -euo pipefail
fail=0
command -v docker >/dev/null 2>&1 || { echo "FAIL: docker"; fail=1; }
docker compose version >/dev/null 2>&1 || { echo "FAIL: docker compose"; fail=1; }
[ -f .env ] || { echo "FAIL: .env missing"; fail=1; }
if [ -f .env ] && grep -q 'CHANGE_ME' .env; then
  echo "FAIL: placeholder secrets remain in .env"
  fail=1
fi
grep -q '^TRADING_MODE=PAPER$\|^TRADING_MODE=SHADOW$\|^TRADING_MODE=LIVE_CANDIDATE$' .env 2>/dev/null || {
  echo "FAIL: deployment must begin outside LIVE mode"
  fail=1
}
[ "$fail" -eq 0 ] || exit 1
echo "Preflight passed."
