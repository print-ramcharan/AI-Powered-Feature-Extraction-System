import os
import shutil

BASE_WORKSPACE = os.path.join(os.getcwd(), "backend/temp_workspace")

def ensure_workspace(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def get_job_path(job_id: str):
    return os.path.join(BASE_WORKSPACE, job_id)

def cleanup_job(job_id: str):
    job_path = get_job_path(job_id)
    if os.path.exists(job_path):
        shutil.rmtree(job_path)
        return True
    return False

# Initialize the base workspace directory
if not os.path.exists(BASE_WORKSPACE):
    os.makedirs(BASE_WORKSPACE, exist_ok=True)
