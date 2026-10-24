#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[1/9] Prerequisites"
command -v docker >/dev/null 2>&1 || { echo "Docker is required."; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "Docker Compose plugin is required."; exit 1; }

echo "[2/9] Configuration"
if [ ! -f .env ]; then
  cp .env.example .env
  chmod 600 .env
  ./deploy/configure-secrets.sh
fi

echo "[3/9] Preflight"
./deploy/preflight.sh

echo "[4/9] Build"
docker compose build

echo "[5/9] Start"
docker compose up -d

echo "[6/9] Database"
./deploy/migrate-db.sh

echo "[7/9] Health"
sleep 5
./deploy/health-check.sh

echo "[8/9] Firewall"
./deploy/configure-firewall.sh || true

echo "[9/9] Deployment complete"
echo "Mode is intentionally non-LIVE."
echo "Run health/status checks before any promotion."
