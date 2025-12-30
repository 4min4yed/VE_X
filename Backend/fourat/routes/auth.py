# routes.auth.py - handles user authentication routes using FastAPI
from fastapi import APIRouter, HTTPException, Depends
from schemas.authy import LoginRequest, RegisterRequest, RefreshRequest
from core.hashing import hash_password, verify_password
from core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    verify_refresh_token,
    revoke_refresh_token,
    revoke_all_refresh_tokens_for_user,
)
from database.fake_db import get_user_by_email, get_user_by_id, create_user, user_exists
from jose import jwt, JWTError
from core.config import SECRET_KEY, ALGORITHM

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

    # Create tokens (include username in access token to reduce DB hits)
    access_token = create_access_token(user["id"], user["email"], username=user.get("username"))
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
    access_token = create_access_token(user_id, request.email, username=request.username)
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

@router.post("/refresh")
def refresh(request: RefreshRequest):
    """
    Exchange a refresh token for a new access token.
    Consider rotating refresh tokens in production.
    """
    user_id = verify_refresh_token(request.refresh_token)

    # Optionally rotate refresh token: revoke old and issue a new one
    revoke_refresh_token(request.refresh_token)
    new_refresh = create_refresh_token(user_id)

    # Create a new access token
    # You might want to get user's email/username from DB for the payload:
    user = get_user_by_id(user_id)
    email = user["email"] if user else ""
    username = user["username"] if user else None
    new_access = create_access_token(user_id, email, username=username)

    return {"success": True, "access_token": new_access, "refresh_token": new_refresh}

@router.post("/logout")
def logout(request: RefreshRequest):
    """
    Logout by refresh token only: verify and revoke the provided refresh token.
    This allows clients to logout even when their access token has expired.
    """
    # Verify refresh token and get owner (will raise HTTPException on invalid/expired)
    user_id = verify_refresh_token(request.refresh_token)

    # Revoke the specific refresh token
    revoke_refresh_token(request.refresh_token)

    return {"success": True, "message": "Logged out successfully"}