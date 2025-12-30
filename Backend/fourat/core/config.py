# core.config.py - configuration settings for the application // centralize secrets & constants
import os

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Database configuration
DB_HOST = os.getenv("DB_HOST", "db")
DB_USER = os.getenv("DB_USER", "vexuser")
DB_PASS = os.getenv("DB_PASS", "vexpass")
DB_NAME = os.getenv("DB_NAME", "vex")
