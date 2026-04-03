from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uuid
import os
import shutil
import json
from typing import Dict, Optional
from services.processor import process_job
from services.downloader import download_from_url
from services.storage import get_job_path, cleanup_job, ensure_workspace

app = FastAPI(title="AI Feature Extraction API")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory status store (use Redis/Database for production)
jobs: Dict[str, dict] = {}

@app.post("/api/upload")
async def upload_zip(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only ZIP files are supported")
    
    job_id = str(uuid.uuid4())
    job_path = get_job_path(job_id)
    ensure_workspace(job_path)
    
    zip_path = os.path.join(job_path, "input.zip")
    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    jobs[job_id] = {"status": "queued", "progress": 0, "message": "File uploaded, starting extraction..."}
    background_tasks.add_task(process_job, job_id, zip_path, jobs)
    
    return {"job_id": job_id}

@app.post("/api/process-url")
async def process_url(background_tasks: BackgroundTasks, url: str):
    job_id = str(uuid.uuid4())
    job_path = get_job_path(job_id)
    ensure_workspace(job_path)
    
    jobs[job_id] = {"status": "queued", "progress": 0, "message": "Downloading from URL..."}
    background_tasks.add_task(download_and_process, job_id, url, jobs)
    
    return {"job_id": job_id}

async def download_and_process(job_id: str, url: str, jobs_store: dict):
    try:
        zip_path = os.path.join(get_job_path(job_id), "input.zip")
        await download_from_url(url, zip_path)
        jobs_store[job_id]["message"] = "Download complete, processing..."
        await process_job(job_id, zip_path, jobs_store)
    except Exception as e:
        jobs_store[job_id].update({"status": "failed", "message": str(e)})

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

@app.get("/api/download/{job_id}")
async def download_result(job_id: str):
    if job_id not in jobs or jobs[job_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail="Result not ready")
    
    result_zip = os.path.join(get_job_path(job_id), "output.zip")
    if not os.path.exists(result_zip):
        raise HTTPException(status_code=404, detail="Result file missing")
    
    return FileResponse(result_zip, filename=f"processed_{job_id}.zip")

@app.get("/api/cleanup/{job_id}")
async def cleanup(job_id: str):
    if cleanup_job(job_id):
        jobs.pop(job_id, None)
        return {"message": "Job cleaned up"}
    raise HTTPException(status_code=404, detail="Job path not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
