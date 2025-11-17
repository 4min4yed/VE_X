from fastapi import FastAPI, UploadFile, HTTPException, status
import hashlib
import shutil
import uuid
import os
import mysql.connector
from mysql.connector import Error as MySQLError

app = FastAPI()

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "uploads")
file_number = 1

# DB config from environment with sensible defaults
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASS = os.environ.get("DB_PASS", "example")
DB_NAME = os.environ.get("DB_NAME", "vex")


def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        autocommit=False,
    )


@app.post("/api/analyze")
async def upload(file: UploadFile):
    file_id = str(uuid.uuid4())
    global file_number

    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = f"{UPLOAD_DIR}/{file_number}.exe"
    file_number += 1

    # Save uploaded file
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save file: {e}")

    # Compute SHA256
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                sha256.update(block)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to hash file: {e}")

    digest = sha256.hexdigest()

    # Persist metadata to DB: ensure a default user exists, then insert into files
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Ensure a default anonymous user exists and get its id
        cur.execute("SELECT id FROM users WHERE username = %s LIMIT 1", ("anonymous",))
        row = cur.fetchone()
        if row:
            user_id = row[0]
        else:
            cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", ("anonymous", "anon@vex.local", ""))
            user_id = cur.lastrowid

        # Insert file record
        cur.execute(
            "INSERT INTO files (user_id, filename, stored_path, file_hash) VALUES (%s, %s, %s, %s)",
            (user_id, getattr(file, 'filename', f"{file_number}.exe"), file_path, digest),
        )
        file_db_id = cur.lastrowid

        conn.commit()
        cur.close()
        conn.close()
    except MySQLError as e:
        # Clean up saved file if DB persist failed
        try:
            os.remove(file_path)
        except Exception:
            pass
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

    return {"id": file_id, "hash": digest, "db_id": file_db_id}
