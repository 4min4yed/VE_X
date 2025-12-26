from fastapi import APIRouter, HTTPException, Depends
from schemas.authy import LoginRequest, RegisterRequest, RefreshRequest
from core.hashing import hash_password, verify_password
from core.security import create_access_token, get_current_user
from database.fake_db import USERS, REFRESH_TOKENS
from jose import jwt, JWTError
from core.config import SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta

router = APIRouter(tags=["auth"])

@router.post("/login")
def login(request: LoginRequest):
    ...

@router.post("/register")
def register(request: RegisterRequest):
    ...

@router.get("/me")
def me(user=Depends(get_current_user)):
    return {"success": True, "user": user}

@router.post("/logout")
def logout(request: RefreshRequest):
    REFRESH_TOKENS.pop(request.refresh_token, None)
    return {"success": True}
