import json
from datetime import datetime, timedelta
from typing import Optional
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
import os


SECRET_KEY =  os.environ["JWT_SECRET_KEY"]
ALGORITHM = os.environ["JWT_ALGORITHM"]


password_hash = PasswordHash.recommended()


def verify_password(stored_password: str, given_password: str) -> bool:
    """Fake password verification for now."""
    # return pwd_context.verify(given_password, stored_password)
    return password_hash.verify(given_password, stored_password)


def encrypt_password(password: str) -> str:
    """Fake password encryption using placeholder prefix."""
    return password_hash.hash(password)


# ============================================================
# 🧩 Token Utilities
# ============================================================

def encrypt_access_token(data: dict, expires_delta: timedelta | None = timedelta(weeks=1)) -> str:
    """Create a JWT access token with a default expiration of 1 week."""
    expire = datetime.now(timezone.utc) + (expires_delta)
    data.update({"exp": int(expire.timestamp())})
    return jwt.encode({k: str(v) for k, v in data.items()}, SECRET_KEY, algorithm=ALGORITHM)


def decrypt_access_token(token: str) -> dict:
    """Reverse of encrypt_access_token — parse JSON back to dict."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
