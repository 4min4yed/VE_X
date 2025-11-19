from fastapi import FastAPI, UploadFile
import hashlib
import shutil
import uuid
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ---- ENABLE CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = "uploads"
file_number = 1

@app.post("/api/analyze")
async def upload(file: UploadFile):
    file_id = str(uuid.uuid4())
    global file_number
    
    file_path = f"{UPLOAD_DIR}/file{file_number}.exe"
    file_number += 1

    # Save
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Hash
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256.update(block)

    digest = sha256.hexdigest()

    return {"id": file_id, "hash": digest}
