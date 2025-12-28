# routes.auth.py - handles user authentication routes using FastAPI  
from fastapi import APIRouter, HTTPException, Depends
from schemas.authy import LoginRequest, RegisterRequest, RefreshRequest
from core.hashing import hash_password, verify_password
from core.security import create_access_token,create_refresh_token, get_current_user
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
