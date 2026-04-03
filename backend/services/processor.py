import os
import zipfile
import shutil
import sys
import json
import logging
from typing import Dict

# Add the project root directory to the python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.smart_processor import smart_process_v3

def process_job(job_id: str, zip_path: str, jobs_store: Dict):
    job_path = os.path.dirname(zip_path)
    extract_dir = os.path.join(job_path, "extracted")
    output_dir = os.path.join(job_path, "processed_output")
    os.makedirs(extract_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 1. Extraction
        jobs_store[job_id].update({"status": "processing", "progress": 10, "message": "Extracting ZIP..."})
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # 2. Find TIF and SHP directory
        tif_path = None
        shp_dir = None

        # Look for TIF and SHP recursively
        for root, dirs, files in os.walk(extract_dir):
            for f in files:
                if f.lower().endswith(".tif") or f.lower().endswith(".tiff"):
                    tif_path = os.path.join(root, f)
                    shp_dir = root # Assume SHPs are in the same folder or subfolders
                    break
            if tif_path: break

        if not tif_path:
            raise Exception("No TIF file found in the ZIP archive")

        # 3. Running smart_process_v3
        jobs_store[job_id].update({"progress": 30, "message": f"Running AI processing on {os.path.basename(tif_path)}..."})
        
        # We can pass custom parameters here if needed (tile_size, neg_ratio)
        smart_process_v3(tif_path, shp_dir, output_dir)

        # 4. Packaging the output
        jobs_store[job_id].update({"progress": 90, "message": "Packaging results..."})
        result_zip = os.path.join(job_path, "output.zip")
        with zipfile.ZipFile(result_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, output_dir)
                    zipf.write(file_path, arcname)

        # 5. Finalize
        manifest_path = os.path.join(output_dir, "v3_manifest.json")
        stats = {}
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                stats = json.load(f)

        jobs_store[job_id].update({
            "status": "completed",
            "progress": 100,
            "message": "Processing complete!",
            "stats": stats.get("stats", {})
        })

    except Exception as e:
        logging.error(f"Error processing job {job_id}: {str(e)}")
        jobs_store[job_id].update({
            "status": "failed",
            "progress": 0,
            "message": f"Error: {str(e)}"
        })
    finally:
        # Cleanup extracted files to save space
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        # We keep output_dir until the user downloads it or cleanup is called
