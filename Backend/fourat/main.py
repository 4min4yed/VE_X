#Purpose: create app, add middleware, integrate auth with file upload
from fastapi import FastAPI, HTTPException, Depends, UploadFile #fastapi tools and error handling
from fastapi.middleware.cors import CORSMiddleware #middleware for handling CORS
from routes.auth import router as auth_router #importing the route modules
from core.security import get_current_user
import os
import uuid
import shutil
import hashlib
import mysql.connector
from mysql.connector import Error as MySQLError
from core.config import DB_HOST, DB_USER, DB_PASS, DB_NAME

app = FastAPI(title="VEX - Analysis API with Authentication") #API instance that gives you ip to get access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "uploads")

def get_db_connection():
    """Get database connection"""
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        autocommit=False,
    )

@app.post("/api/analyze")
async def upload_and_analyze(file: UploadFile, user=Depends(get_current_user)):
    """Upload and analyze a file - requires authentication"""
    user_id = int(user["id"])
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Use UUID-based filename to avoid collisions
    stored_filename = f"{uuid.uuid4()}.exe"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)

    try:
        # Save uploaded file
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        file_size = os.path.getsize(file_path)
        
        # Compute SHA256 hash
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        file_hash = sha256_hash.hexdigest()
        
        # Store file metadata in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO files (user_id, filename, stored_path, file_hash, file_size) 
               VALUES (%s, %s, %s, %s, %s)""",
            (user_id, file.filename, stored_filename, file_hash, file_size)
        )
        file_id = cursor.lastrowid
        
        # Create analysis record
        cursor.execute(
            """INSERT INTO analyses (file_id, status) VALUES (%s, %s)""",
            (file_id, "pending")
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "file_hash": file_hash,
            "file_size": file_size,
            "status": "pending"
        }
    
    except Exception as e:
        # Cleanup on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@app.get("/api/files")
async def get_user_files(user=Depends(get_current_user)):
    """Get all files uploaded by the authenticated user"""
    user_id = int(user["id"])
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT f.id, f.filename, f.file_size, f.uploaded_at, a.status, a.score 
               FROM files f
               LEFT JOIN analyses a ON f.id = a.file_id
               WHERE f.user_id = %s
               ORDER BY f.uploaded_at DESC""",
            (user_id,)
        )
        
        files = cursor.fetchall()
        cursor.close()
        conn.close()
        
        
        return {
            "success": True,
            "files": files
        }
    
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/analysis/{file_id}")
async def get_analysis(file_id: int, user=Depends(get_current_user)):
    """Get analysis results for a specific file"""
    user_id = int(user["id"])
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verify ownership
        cursor.execute(
            """SELECT a.*, f.user_id FROM analyses a
               JOIN files f ON a.file_id = f.id
               WHERE a.file_id = %s AND f.user_id = %s""",
            (file_id, user_id)
        )
        
        analysis = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {
            "success": True,
            "analysis": analysis
        }
    
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
