#!/usr/bin/env bash
set -euo pipefail
curl -fsS "http://localhost:${API_PORT:-8080}/health"
echo
