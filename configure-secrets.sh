#!/usr/bin/env bash
set -euo pipefail
if [ ! -f .env ]; then cp .env.example .env; fi
python3 - <<'PY'
from pathlib import Path
import secrets
p=Path(".env")
s=p.read_text()
for key in ("POSTGRES_PASSWORD","LIVE_ENABLE_TOKEN","JWT_SECRET"):
    prefix=key+"="
    lines=s.splitlines()
    for i,line in enumerate(lines):
        if line.startswith(prefix) and ("CHANGE_ME" in line or line == prefix):
            lines[i]=prefix+secrets.token_urlsafe(32)
    s="\n".join(lines)+"\n"
p.write_text(s)
p.chmod(0o600)
PY
echo "Secrets initialized in .env. Review before production use."
