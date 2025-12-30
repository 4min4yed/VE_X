#core.security.py - provides security utilities for token creation and user authentication
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose.exceptions import ExpiredSignatureError
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from typing import Optional

security = HTTPBearer()  # class provides HTTP Bearer authentication for FastAPI routes

security = HTTPBearer() #class provides HTTP Bearer authentication for FastAPI routes // 
#the http bearer scheme is commonly used for transmitting access tokens
REFRESH_TOKENS=set() # In-memory store for issued refresh tokens    
def create_access_token(user_id: int, email: str):
# Note: For production you should persist refresh tokens in a DB table (store hashed tokens).
# This in-memory set is only acceptable for development / demo.
REFRESH_TOKENS = set()

def create_access_token(user_id: int, email: str, username: Optional[str] = None):
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    # include username if provided (helps avoid extra DB hit in some flows)
    if username:
        payload["username"] = username
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: int):
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    # Add token to refresh-token store (in-memory for now)
    REFRESH_TOKENS.add(token)
    return token

def revoke_refresh_token(token: str):
    """Revoke a refresh token (remove from refresh store)."""
    REFRESH_TOKENS.discard(token)

def revoke_all_refresh_tokens_for_user(user_id: int):
    """Revoke all refresh tokens for a user (useful for forced logout)."""
    to_remove = {t for t in REFRESH_TOKENS if _token_belongs_to_user(t, user_id)}
    for t in to_remove:
        REFRESH_TOKENS.discard(t)

def _token_belongs_to_user(token: str, user_id: int) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return str(user_id) == payload.get("sub")
    except Exception:
        return False

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):  # Get current user from token
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])

        # Verify token type
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")

        # Convert subject to int here so downstream code can rely on int id
        return {
            "id": int(payload["sub"]),
            "email": payload["email"],
            "username": payload.get("username")
        }
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_refresh_token(token: str):
    # Verify signature and expiry, and make sure token is in the refresh store
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    if token not in REFRESH_TOKENS:
        # token was not issued by this server or was revoked
        raise HTTPException(status_code=401, detail="Refresh token revoked or unknown")

    return int(payload["sub"])