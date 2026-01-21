import os
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt

ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALG = "HS256"

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(hash: str, password: str) -> bool:
    try:
        return ph.verify(hash, password)
    except VerifyMismatchError:
        return False

def random_token(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)

def hash_token(token: str) -> str:
    # use HMAC-SHA256 with a server secret for token hashing
    return hmac.new(JWT_SECRET.encode(), token.encode(), hashlib.sha256).hexdigest()

def create_access_token(sub: str, expires_minutes: int = 10, extra_claims: dict | None = None) -> str:
    now = datetime.utcnow()
    payload = {"sub": sub, "exp": now + timedelta(minutes=expires_minutes), "iat": now}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
