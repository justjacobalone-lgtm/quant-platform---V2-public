#!/usr/bin/env bash
set -euo pipefail
command -v ufw >/dev/null 2>&1 || exit 0
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
echo "Firewall enabled: SSH/HTTP/HTTPS only."
