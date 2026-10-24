import os, secrets
from fastapi import Header, HTTPException

def require_admin(x_admin_token: str | None = Header(default=None)):
    expected = os.getenv("ADMIN_TOKEN", "")
    if not expected or not x_admin_token or not secrets.compare_digest(x_admin_token, expected):
        raise HTTPException(status_code=401, detail="admin authentication required")
    return True
