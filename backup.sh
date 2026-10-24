#!/usr/bin/env bash
set -euo pipefail
mkdir -p backups
docker compose exec -T postgres pg_dump -U "${POSTGRES_USER}" "${POSTGRES_DB}" > "backups/quant_$(date -u +%Y%m%dT%H%M%SZ).sql"
echo "Backup written to backups/"
