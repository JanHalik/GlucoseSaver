import time, hmac, hashlib, base64, secrets
import uuid
from typing import Optional
from fastapi import Header, HTTPException

HMAC_KEY = b"dev_secret"
TOKEN_TTL = 60  # 1 minuta

_store = {}  # token_hash -> (payload_dict, expires_at)

def _hash_token(raw_token: bytes) -> str:
    mac = hmac.new(HMAC_KEY, raw_token, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).decode().rstrip("=")

def create_token_for_user_mem(user_id: uuid.UUID) -> str:
    raw = secrets.token_urlsafe(32).encode()
    token_hash = _hash_token(raw)
    expires = time.time() + TOKEN_TTL
    _store[token_hash] = ({"user_id": user_id, "iat": int(time.time())}, expires)
    return raw.decode()

def verify_token_and_get_user_mem(raw_token: str):
    token_hash = _hash_token(raw_token.encode())
    entry = _store.get(token_hash)
    if not entry:
        return None
    payload, expires = entry
    if time.time() > expires:
        del _store[token_hash]
        return None
    return payload["user_id"]

def revoke_token_mem(raw_token: str):
    token_hash = _hash_token(raw_token.encode())
    _store.pop(token_hash, None)


async def get_user_id(authorization: Optional[str] = Header(None)):
    #If authorization present in Header try to use Incognito API Auth
    token=None
    if authorization:
        # Expected format "Bearer=<token>"
        if authorization.startswith("Bearer="):
            token = authorization.split("=", 1)[1]
            if token:
                user_id = verify_token_and_get_user_mem(token)
                if user_id:
                    return user_id
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")