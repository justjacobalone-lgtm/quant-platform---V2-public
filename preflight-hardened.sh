#!/usr/bin/env bash
set -euo pipefail
fail(){ echo "PREFLIGHT FAILED: $*" >&2; exit 1; }
command -v docker >/dev/null || fail "docker is required"
command -v docker compose >/dev/null || fail "docker compose is required"
[[ -f .env ]] || fail ".env missing; copy .env.example and set strong secrets"
for k in POSTGRES_PASSWORD LIVE_ENABLE_TOKEN; do
  v=$(grep -E "^${k}=" .env | tail -1 | cut -d= -f2- || true)
  [[ -n "$v" && "$v" != *CHANGE_ME* ]] || fail "$k is unset/placeholder"
done
if grep -Eq '^ALLOW_LIVE_TRADING=true' .env; then
  echo "WARNING: LIVE trading explicitly enabled. Do not proceed unless production gates are signed off." >&2
fi
docker compose config >/dev/null
echo "PREFLIGHT OK"
