# routes.auth.py - handles user authentication routes using FastAPI  
from fastapi import APIRouter, HTTPException, Depends
from schemas.authy import LoginRequest, RegisterRequest, RefreshRequest
from core.hashing import hash_password, verify_password
from core.security import create_access_token, create_refresh_token, get_current_user
from database.fake_db import get_user_by_email, get_user_by_id, create_user, user_exists
from jose import jwt, JWTError
from core.config import SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta

router = APIRouter(tags=["auth"]) 

@router.post("/login")
def login(request: LoginRequest):
    # Get user from database by email
    user = get_user_by_email(request.email)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create tokens
    access_token = create_access_token(user["id"], user["email"])
    refresh_token = create_refresh_token(user["id"])

    return {
        "success": True,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"]
        }
    }

@router.post("/register")
def register(request: RegisterRequest):
    # Check if user already exists
    if user_exists(request.email):
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Hash password
    password_hash = hash_password(request.password)
    
    # Create new user in database
    user_id = create_user(request.username, request.email, password_hash)
    
    if not user_id:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    # Create tokens
    access_token = create_access_token(user_id, request.email)
    refresh_token = create_refresh_token(user_id)

    return {
        "success": True,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user_id,
            "email": request.email,
            "username": request.username
        }
    }

@router.get("/me")
def me(user=Depends(get_current_user)):
    # Fetch complete user data from database
    db_user = get_user_by_id(int(user["id"]))
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "user": {
            "id": db_user["id"],
            "email": db_user["email"],
            "username": db_user["username"]
        }
    }

@router.post("/logout")
def logout(user=Depends(get_current_user)):
    # In JWT-based auth, logout is handled client-side by discarding the token
    # No server-side state to update
    return {"success": True, "message": "Logged out successfully"}

