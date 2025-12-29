# routes.auth.py - handles user authentication routes using FastAPI  
from fastapi import APIRouter, HTTPException, Depends
from schemas.authy import LoginRequest, RegisterRequest, RefreshRequest
from core.hashing import hash_password, verify_password
from core.security import create_access_token,create_refresh_token, get_current_user, verify_refresh_token
from database.fake_db import USERS, REFRESH_TOKENS
from jose import jwt, JWTError
from core.config import SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta

router = APIRouter(tags=["auth"]) 

@router.post("/login")
def login(request: LoginRequest):
    for user in USERS:
        if (
            user["email"] == request.email and
            verify_password(request.password, user["password"])
        ):
            access_token = create_access_token(user["id"], user["email"])
            refresh_token = create_refresh_token(user["id"])

            return {
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token
            }

        
    raise HTTPException(status_code=401, detail="Invalid email or password")

@router.post("/register")
def register(request: RegisterRequest):
    #check if user already exists
    for user in USERS:
        if user["email"] == request.email:
            raise HTTPException(status_code=400, detail="User already exists")
    # Create a new user
    new_user = {
        "id": len(USERS) + 1,
        "username": request.username,
        "email": request.email,
        "password": hash_password(request.password) #hash the password before storing 
    }
    USERS.append(new_user)
    access_token = create_access_token(new_user["id"], new_user["email"])
    refresh_token = create_refresh_token(new_user["id"])

    return {
        "success": True,
        "access_token": access_token,
        "refresh_token": refresh_token
    }   

@router.get("/me")
def me(user=Depends(get_current_user)):
    return {"success": True, "user": user}

@router.post("/logout")
def logout(request: RefreshRequest):
    REFRESH_TOKENS.pop(request.refresh_token, None) #remove the refresh token from the store
    return {"success": True}

@router.post("/refresh")
def refresh(request: RefreshRequest):
    # validate the refresh token and issue new tokens (rotate refresh token)
    user_id = verify_refresh_token(request.refresh_token)

    # optional: revoke existing refresh token to force rotation (single use)
    REFRESH_TOKENS.pop(request.refresh_token, None)

    # issue new tokens
    # find user email for token creation
    user = next((u for u in USERS if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=401, detail="User not found for refresh token")

    access_token = create_access_token(user["id"], user["email"])
    refresh_token = create_refresh_token(user["id"])
    return {
        "success": True,
        "access_token": access_token,
        "refresh_token": refresh_token
    }

