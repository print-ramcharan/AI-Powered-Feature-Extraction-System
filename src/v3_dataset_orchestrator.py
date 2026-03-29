import os
import subprocess
import shutil
import logging
import json
import rasterio
from datetime import datetime
from tqdm import tqdm

# --- V3 Orchestration Config ---
OFFICIAL_LINKS = {
    "CG_451189_ecw": "https://svamitva.nic.in/DownloadPDF/TifFile/CG_451189_ecw.zip",
    "CG_450163": "https://svamitva.nic.in/DownloadPDF/TifFile/CG_450163.zip",
    "PB_37458_37774": "https://svamitva.nic.in/DownloadPDF/TifFile/PB_37458_37774.zip",
    "CG_Training_dataSet_2": "https://svamitva.nic.in/DownloadPDF/TifFile/CG_Training_dataSet_2.zip",
    "CG_Training_dataSet_3": "https://svamitva.nic.in/DownloadPDF/TifFile/CG_Training_dataSet_3.zip",
    "CG_shp_file": "https://svamitva.nic.in/DownloadPDF/TifFile/CG_shp-file.zip",
    "PB_shp_file": "https://svamitva.nic.in/DownloadPDF/TifFile/PB_training_dataSet_shp_file.zip"
}

RAW_DIR = "data/raw/v3_temp"
SHP_POOL = "data/raw/v3_shps"
PACKAGED_DIR = "data/tiles/v3_packaged"
PYTHON_BIN = "./venv/bin/python3"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def run_command(cmd, env=None):
    logging.info(f"Executing: {cmd}")
    
    # Base environment with path priorities
    full_env = os.environ.copy()
    priority_paths = ":".join([
        os.path.expanduser("~/miniforge3/bin"),
        os.path.expanduser("~/opt/miniforge3/bin"),
        os.path.expanduser("~/anaconda3/bin"),
        os.path.expanduser("~/miniconda3/bin"),
        "/opt/homebrew/bin",
        "/usr/local/bin",
        "/usr/bin",
        "/bin"
    ])
    full_env["PATH"] = priority_paths + ":" + full_env.get("PATH", "")
    
    # Merge custom env if provided
    if env:
        full_env.update(env)
    
    # We remove capture_output=True so that the user can see real-time progress bars (curl, tqdm)
    result = subprocess.run(cmd, shell=True, env=full_env)
    if result.returncode != 0:
        logging.error(f"Command failed with return code {result.returncode}")
        return False
    return True

def find_gdal_bin(bin_name):
    """Scan common Mac locations for a GDAL binary, including Miniforge/conda."""
    import shutil
    # Check PATH first (handles conda activate, venv, etc.)
    which_result = shutil.which(bin_name)
    if which_result:
        return which_result
    # Explicit fallback candidates (miniforge first, then homebrew, then system)
    candidates = [
        os.path.expanduser(f"~/miniforge3/bin/{bin_name}"),
        os.path.expanduser(f"~/opt/miniforge3/bin/{bin_name}"),
        os.path.expanduser(f"~/anaconda3/bin/{bin_name}"),
        os.path.expanduser(f"~/miniconda3/bin/{bin_name}"),
        f"/opt/homebrew/bin/{bin_name}",
        f"/usr/local/bin/{bin_name}",
        f"/usr/bin/{bin_name}"
    ]
    for c in candidates:
        if os.path.exists(c): return c
    return None

def convert_ecw_via_rasterio(ecw_path, out_tif):
    """Fallback: Convert ECW to TIFF using rasterio if GDAL binaries are missing."""
    logging.info(f"GDAL binary missing. Attempting Rasterio-only ECW conversion: {ecw_path}...")
    try:
        with rasterio.open(ecw_path) as src:
            meta = src.meta.copy()
            meta.update(driver='GTiff')
            with rasterio.open(out_tif, 'w', **meta) as dst:
                for i in range(1, src.count + 1):
                    dst.write(src.read(i), i)
        return True
    except Exception as e:
        logging.error(f"Rasterio conversion failed: {e}")
        return False

def prepare_shp_pool():
    """Download and extract secondary SHP-only zips to a common pool."""
    os.makedirs(SHP_POOL, exist_ok=True)
    shp_zips = {
        "CG_Global_SHPs": OFFICIAL_LINKS["CG_shp_file"],
        "PB_Global_SHPs": OFFICIAL_LINKS["PB_shp_file"]
    }
    for name, url in shp_zips.items():
        try:
            zip_p = os.path.join("data/raw", f"{name}.zip")

            # Fast-path: if SHP files already exist in the pool, skip download entirely
            existing_shps = []
            for root, _, files in os.walk(SHP_POOL):
                existing_shps.extend([f for f in files if f.lower().endswith(".shp")])
            if existing_shps:
                logging.info(f"SHP pool already populated ({len(existing_shps)} SHPs found). Skipping {name} download.")
                continue

            # Corruption Check: If exists but too small (<1MB), it's likely a failed download
            if os.path.exists(zip_p) and os.path.getsize(zip_p) < 1024 * 1024:
                logging.warning(f"Corrupted ZIP detected ({name}). Deleting and re-fetching...")
                os.remove(zip_p)
                
            if not os.path.exists(zip_p):
                logging.info(f"Pre-fetching Global SHPs: {name} from {url}")
                # Using --progress-bar for better visual feedback
                if not run_command(f"curl -k -L --progress-bar -o {zip_p} {url}"):
                    logging.warning(f"Failed to download {name}. Skipping...")
                    continue
            logging.info(f"Extracting Global SHPs: {name}")
            if run_command(f"unzip -q -o {zip_p} -d {SHP_POOL}"):
                logging.info(f"Purging {zip_p} after extraction...")
                os.remove(zip_p)
            else:
                logging.error(f"Unzip failed for {name}. Deleting corrupted zip...")
                if os.path.exists(zip_p): os.remove(zip_p)
                continue
        except Exception as e:
            logging.error(f"Error preparing SHP pool for {name}: {e}")

def collect_shp_dirs(extract_path, region="CG"):
    """
    Build a merged SHP search path list: local extracted dir first (region-specific),
    then the global pool for that specific region.
    """
    import tempfile, glob

    # Define region-specific global pool sub-folders
    if region == "PB":
        region_pool = os.path.join(SHP_POOL, "PB_training_dataSet_shp_file", "shp-file")
    else:
        # Default to CG
        region_pool = os.path.join(SHP_POOL, "shp-file")

    # Collect all .shp files from local extract
    local_shps = []
    for root, _, files in os.walk(extract_path):
        for f in files:
            if f.lower().endswith(".shp"):
                local_shps.append(os.path.join(root, f))

    # Collect all .shp files from the appropriate global pool
    global_shps = []
    if os.path.exists(region_pool):
        for root, _, files in os.walk(region_pool):
            for f in files:
                if f.lower().endswith(".shp"):
                    global_shps.append(os.path.join(root, f))
    else:
        logging.warning(f"Region pool not found: {region_pool}")

    total = len(local_shps) + len(global_shps)
    logging.info(f"SHP merger ({region}): {len(local_shps)} local + {len(global_shps)} global = {total} total SHPs")

    if not local_shps and total > 0:
        # No local SHPs but we have global ones — just use the region pool directly
        return region_pool

    # Create a temp merged dir with symlinks
    merged_dir = os.path.join("data/raw/v3_temp", f"_merged_shps_{region}")
    shutil.rmtree(merged_dir, ignore_errors=True)
    os.makedirs(merged_dir, exist_ok=True)

    def link_shp_family(shp_path, dest_dir, prefix=""):
        """Symlink all sidecar files (.dbf, .shx, .prj, .cpg, etc.) for a shapefile."""
        base = os.path.splitext(shp_path)[0]
        for sidecar in glob.glob(base + ".*"):
            fname = prefix + os.path.basename(sidecar)
            dst = os.path.join(dest_dir, fname)
            if not os.path.exists(dst):
                os.symlink(os.path.abspath(sidecar), dst)

    # Local SHPs get priority (no prefix) — they match the TIF's region
    for shp in local_shps:
        link_shp_family(shp, merged_dir)

    # Global SHPs get a prefix so they don't overwrite local ones
    for shp in global_shps:
        link_shp_family(shp, merged_dir, prefix="_global_")

    logging.info(f"Merged SHP staging dir: {merged_dir} ({len(os.listdir(merged_dir))} files)")
    return merged_dir


def download_with_retry(url, zip_path, max_attempts=3):
    """Download a URL to zip_path with up to max_attempts retries."""
    for attempt in range(1, max_attempts + 1):
        logging.info(f"Download attempt {attempt}/{max_attempts}: {url}")
        if run_command(f"curl -k -L --progress-bar -o {zip_path} {url}"):
            # Validate minimum size (> 1 MB)
            if os.path.exists(zip_path) and os.path.getsize(zip_path) > 1024 * 1024:
                return True
            else:
                logging.warning(f"Downloaded file too small on attempt {attempt}. Retrying...")
        else:
            logging.warning(f"curl failed on attempt {attempt}.")
    logging.error(f"All {max_attempts} download attempts failed for {url}")
    return False


def check_manifest_has_positives(output_base):
    """Return True if an existing manifest reports > 0 positives (don't reprocess)."""
    manifest_path = f"{output_base}_manifest.json"
    if not os.path.exists(manifest_path):
        return False  # No manifest → treat as not done
    try:
        with open(manifest_path, 'r') as f:
            data = json.load(f)
        positives = data.get("processor_summary", {}).get("positives", 0)
        total_tiles = data.get("total_tiles", 0)
        logging.info(f"Existing manifest: {total_tiles} tiles, {positives} positives")
        return positives > 0
    except Exception as e:
        logging.warning(f"Could not read manifest {manifest_path}: {e}")
        return False


def process_volume(name, url):
    logging.info(f"=== Starting V3 Volume: {name} ===")

    # 1. Download — with retry logic
    zip_path = os.path.join("data/raw", f"{name}.zip")

    # Corruption / size check
    if os.path.exists(zip_path) and os.path.getsize(zip_path) < 1024 * 1024:
        logging.warning(f"Corrupted Imagery ZIP detected ({name}). Skipping automated re-download...")

    if not os.path.exists(zip_path):
        logging.info(f"Downloading {url}...")
        if not download_with_retry(url, zip_path):
            return False

    # 2. Extract
    extract_path = os.path.join(RAW_DIR, name)
    os.makedirs(extract_path, exist_ok=True)

    # Check if extraction already has content (skip re-unzip)
    existing_files = [f for root, _, files in os.walk(extract_path) for f in files]
    if not existing_files:
        logging.info(f"Extracting to {extract_path}...")
        if not run_command(f"unzip -q -o {zip_path} -d {extract_path}"):
            logging.error(f"Unzip failed for imagery {name}. Keeping zip for investigation...")
            shutil.rmtree(extract_path, ignore_errors=True)
            return False
    else:
        logging.info(f"Extraction dir already populated ({len(existing_files)} files). Skipping unzip.")

    # 3. Auto-Locate ALL Imagery (TIF and ECW)
    imagery_to_process = []
    g_trans = find_gdal_bin("gdal_translate")

    for root, _, files in os.walk(extract_path):
        for f in files:
            ext = f.lower()
            if ext.endswith(('.tif', '.tiff')):
                test_path = os.path.join(root, f)
                try:
                    with rasterio.open(test_path) as src:
                        pixels = src.width * src.height
                        if pixels < 1280 * 1280:
                            continue
                        imagery_to_process.append(test_path)
                        logging.info(f"Found TIF: {f} ({src.width}x{src.height})")
                except Exception as e:
                    logging.warning(f"TIF invalid: {f} - {e}")
            elif ext.endswith('.ecw'):
                ecw_path = os.path.join(root, f)
                conv_tif = ecw_path.replace(".ecw", "_v3_converted.tif")
                if not os.path.exists(conv_tif):
                    logging.info(f"Converting ECW: {f}")
                    if g_trans:
                        run_command(f"{g_trans} -of GTiff \"{ecw_path}\" \"{conv_tif}\"")
                    else:
                        convert_ecw_via_rasterio(ecw_path, conv_tif)
                
                if os.path.exists(conv_tif):
                    try:
                        with rasterio.open(conv_tif) as src:
                            if (src.width * src.height) >= 1280 * 1280:
                                imagery_to_process.append(conv_tif)
                                logging.info(f"ECW Converted: {f}")
                    except:
                        pass

    if not imagery_to_process:
        logging.error(f"No suitable imagery found in {name}")
        return False

    # 4. Merge local + global SHPs
    region = "PB" if "PB_" in name else "CG"
    merged_shp_dir = collect_shp_dirs(extract_path, region=region)

    success_any = False
    for tif_file in imagery_to_process:
        # Use a unique name for each sub-imagery to avoid collisions
        sub_name = os.path.splitext(os.path.basename(tif_file))[0].replace(" ", "_")
        
        # New Imagery-Aware Skip Logic
        output_base = os.path.join(PACKAGED_DIR, f"V3_{sub_name}")
        output_zip = f"{output_base}_vol1.zip"
        
        if os.path.exists(output_zip):
            if check_manifest_has_positives(output_base):
                logging.info(f"Skipping Imagery: {sub_name} (Package exists with positives).")
                success_any = True
                continue
            else:
                logging.warning(f"Imagery {sub_name} exists but has 0 positives. Reprocessing...")
                # Remove stale package
                for f in os.listdir(PACKAGED_DIR):
                    if f.startswith(f"V3_{sub_name}"):
                        os.remove(os.path.join(PACKAGED_DIR, f))

        logging.info(f"--- Processing Imagery: {sub_name} ---")

        # 5. Run Refined V3 Smart Processor
        processed_dir = os.path.join("data/tiles/v3_temp_processed", sub_name)
        os.makedirs(processed_dir, exist_ok=True)

        # Set GDAL environment to handle very large directories
        env = os.environ.copy()
        env["GDAL_HTTP_UNSAFESSL"] = "YES"
        env["GDAL_MAX_DATASET_POOL_SIZE"] = "2048"
        env["PROJ_NETWORK"] = "OFF"

        cmd = (
            f"{PYTHON_BIN} src/smart_processor.py "
            f"--tif \"{tif_file}\" "
            f"--shp_dir \"{merged_shp_dir}\" "
            f"--output \"{processed_dir}\" "
            f"--tile_size 1280 "
            f"--neg_ratio 0.3"
        )
        if not run_command(cmd, env=env):
            logging.error(f"Smart processor failed for {sub_name}.")
            continue

        # 6. Package into Kaggle volumes
        logging.info(f"Packaging {sub_name} into Kaggle volumes...")
        cmd = f"{PYTHON_BIN} src/package_datasets.py \"{processed_dir}\" \"{output_base}\""
        if not run_command(cmd):
            continue

        # 7. Success Verification
        manifest_path = f"{output_base}_manifest.json"
        total_tiles = 0
        positives = 0
        try:
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    data = json.load(f)
                    summary = data.get("processor_summary", {})
                    total_tiles = data.get("total_tiles", 0)
                    positives = summary.get("positives", 0)
        except Exception as e:
            logging.error(f"Failed to read manifest for {sub_name}: {e}")

        if total_tiles > 0:
            logging.info(f"Completed Imagery: {sub_name} ({total_tiles} tiles, {positives} positives)")
            success_any = True
            shutil.rmtree(processed_dir, ignore_errors=True)
        else:
            logging.error(f"Imagery {sub_name} produced ZERO tiles.")

    if success_any:
        # If any imagery in the zip was successful, we consider it "partially done"
        # We only purge raw extraction if everything is complete? No, let's just 
        # cleanup to save space. User can always re-unzip.
        shutil.rmtree(extract_path, ignore_errors=True)
        merged_staging = os.path.join(RAW_DIR, f"_merged_shps_{region}")
        shutil.rmtree(merged_staging, ignore_errors=True)
        return True
    
    return False

if __name__ == "__main__":
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PACKAGED_DIR, exist_ok=True)
    
    # Pre-fetch Global SHPs (Ensuring no layer is missing)
    prepare_shp_pool()
    
    # Full Batch Targets (Imagery Volumes)
    batch_targets = [
        "CG_451189_ecw",
        "CG_450163",
        "PB_37458_37774",
        "CG_Training_dataSet_2",
        "CG_Training_dataSet_3"
    ]
    
    # Sequentially Process Batch Volumes
    for name in tqdm(batch_targets, desc="Full V3 Batch"):
        # We always enter process_volume now, and inside it we check for each village/imagery
        if name in OFFICIAL_LINKS:
            process_volume(name, OFFICIAL_LINKS[name])
