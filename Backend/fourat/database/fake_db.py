import mysql.connector
from mysql.connector import Error as MySQLError
import os
from typing import Optional, Dict

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
