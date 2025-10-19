from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os, shutil

app = FastAPI(title="Chat with Your Docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    os.makedirs("data/uploads", exist_ok=True)
    saved = []
    for f in files:
        path = f"data/uploads/{f.filename}"
        with open(path, "wb") as out:
            shutil.copyfileobj(f.file, out)
        saved.append(path)
    return {"saved": saved}

