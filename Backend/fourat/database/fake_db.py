import mysql.connector
from mysql.connector import Error as MySQLError
import os
from typing import Optional, Dict
from datetime import datetime
import traceback

# Database connection configuration
DB_CONFIG = {
    # Default to localhost for host-based development. When running in Docker
    # Compose use environment DB_HOST=db so services can resolve by name.
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "vexuser"),
    "password": os.getenv("DB_PASS", "vexpass"),
    "database": os.getenv("DB_NAME", "vex"),
}



def get_db():
    """Get a MySQL database connection"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except MySQLError as e:
        print(f"Database connection error: {e}")
        raise

def get_user_by_email(email: str) -> Optional[Dict]:
    """Fetch user from database by email"""
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, email, password_hash FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except MySQLError as e:
        print(f"Error fetching user: {e}")
        return None

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Fetch user from database by ID"""
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except MySQLError as e:
        print(f"Error fetching user: {e}")
        return None

def create_user(username: str, email: str, password_hash: str) -> Optional[int]:
    """Create a new user in database"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return user_id
    except MySQLError as e:
        print(f"Error creating user: {e}")
        return None


def user_exists(email: str) -> bool:
    """Check if user exists by email"""
    return get_user_by_email(email) is not None


def store_refresh_token(token: str, user_id: int, expires_at: datetime) -> bool:
    """Store a refresh token in the database."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO refresh_tokens (token, user_id, expires_at) VALUES (%s, %s, %s)",
            (token, user_id, expires_at.strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except MySQLError as e:
        print(f"Error storing refresh token: {e}")
        traceback.print_exc()
        return False


def is_refresh_token_present(token: str) -> bool:
    """Return True if the refresh token exists and has not expired."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(1) FROM refresh_tokens WHERE token = %s AND expires_at > NOW()",
            (token,)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return bool(row and row[0])
    except MySQLError as e:
        print(f"Error checking refresh token: {e}")
        return False


def get_user_id_for_refresh(token: str) -> Optional[int]:
    """Return the user_id associated with a refresh token, or None."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM refresh_tokens WHERE token = %s", (token,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return int(row[0]) if row else None
    except MySQLError as e:
        print(f"Error fetching refresh-token owner: {e}")
        return None


def revoke_refresh_token_db(token: str) -> None:
    """Delete a refresh token from the database."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM refresh_tokens WHERE token = %s", (token,))
        conn.commit()
        cursor.close()
        conn.close()
    except MySQLError as e:
        print(f"Error revoking refresh token: {e}")


def revoke_all_refresh_tokens_for_user_db(user_id: int) -> None:
    """Delete all refresh tokens for a given user."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM refresh_tokens WHERE user_id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except MySQLError as e:
        print(f"Error revoking all refresh tokens for user {user_id}: {e}")
