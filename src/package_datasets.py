import os
import zipfile
import logging
import json
from tqdm import tqdm
import yaml
from datetime import datetime

# --- V3 Configuration ---
V3_VERSION = "3.0.0"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def get_class_counts_from_label(label_path):
    """Parses YOLO label file and returns a frequency dict of class IDs."""
    counts = {}
    if os.path.exists(label_path):
        with open(label_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if parts:
                    cls_id = int(parts[0])
                    counts[cls_id] = counts.get(cls_id, 0) + 1
    return counts

def calculate_v3_weights(global_counts, strategy='inverse_sqrt'):
    """
    Refinement 3: Generate class weights for training.
    """
    total = sum(global_counts.values())
    weights = {}
    nc = max(global_counts.keys()) + 1 if global_counts else 0
    
    for cls_id, count in global_counts.items():
        if strategy == 'inverse':
            weights[cls_id] = total / (nc * count)
        elif strategy == 'inverse_sqrt':
            weights[cls_id] = (total / (nc * count)) ** 0.5
            
    # Normalize to [0.5, 10.0] range
    if weights:
        max_w = max(weights.values())
        norm_weights = {k: float(round(min(10.0, max(0.5, v/max_w * 5)), 2)) 
                        for k, v in weights.items()}
        return norm_weights
    return {}

def create_v3_package(input_dir, output_zip_base, max_size_mb=4500):
    """
    Packages V3 processed tiles into Kaggle-ready volumes with expanded manifests.
    Expects input_dir containing 'images/', 'labels/', and 'v3_manifest.json'.
    """
    img_dir = os.path.join(input_dir, "images")
    lbl_dir = os.path.join(input_dir, "labels")
    v3_mani_path = os.path.join(input_dir, "v3_manifest.json")
    
    if not os.path.exists(img_dir):
        logging.error(f"Image directory {img_dir} not found.")
        return

    # 1. Load the processor's manifest
    processor_stats = {}
    if os.path.exists(v3_mani_path):
        with open(v3_mani_path, 'r') as f:
            processor_stats = json.load(f)

    # 1b. Determine Domain (State)
    village_name = os.path.basename(input_dir)
    state = "Punjab" if "PB_" in village_name.upper() else "Chhattisgarh" if "CG_" in village_name.upper() else "Unknown"

    # 2. Gather all image/label pairs
    all_images = [f for f in os.listdir(img_dir) if f.endswith('.jpg')]
    logging.info(f"Packaging {len(all_images)} tiles from {village_name} ({state})...")
    
    global_class_counts = {}
    files_to_zip = []
    
    for img_name in all_images:
        base = os.path.splitext(img_name)[0]
        img_path = os.path.join(img_dir, img_name)
        lbl_path = os.path.join(lbl_dir, base + ".txt")
        
        if os.path.exists(lbl_path):
            counts = get_class_counts_from_label(lbl_path)
            for cid, count in counts.items():
                global_class_counts[cid] = global_class_counts.get(cid, 0) + count
            files_to_zip.append((img_path, lbl_path))
        else:
            files_to_zip.append((img_path, None))

    # 3. Create Zips
    vol_idx = 1
    current_zip_path = f"{output_zip_base}_vol{vol_idx}.zip"
    os.makedirs(os.path.dirname(current_zip_path), exist_ok=True)
    
    current_zip = zipfile.ZipFile(current_zip_path, 'w', zipfile.ZIP_DEFLATED)
    current_size = 0
    
    for img_p, lbl_p in tqdm(files_to_zip, desc="Zipping V3"):
        f_size = os.path.getsize(img_p)
        if lbl_p: f_size += os.path.getsize(lbl_p)
        
        if current_size + f_size > (max_size_mb * 1024 * 1024):
            current_zip.close()
            vol_idx += 1
            current_zip_path = f"{output_zip_base}_vol{vol_idx}.zip"
            current_zip = zipfile.ZipFile(current_zip_path, 'w', zipfile.ZIP_DEFLATED)
            current_size = 0
            
        # Write to zip (relative paths)
        current_zip.write(img_p, os.path.join("images", os.path.basename(img_p)))
        if lbl_p:
            current_zip.write(lbl_p, os.path.join("labels", os.path.basename(lbl_p)))
        
        current_size += f_size
        
        # Immediate Purge to save disk
        os.remove(img_p)
        if lbl_p: os.remove(lbl_p)

    # 4. Final Metadata
    v3_weights = calculate_v3_weights(global_class_counts)
    
    final_manifest = {
        "dataset_version": V3_VERSION,
        "village": processor_stats.get("village", village_name),
        "state": state,
        "total_volumes": vol_idx,
        "total_tiles": len(all_images),
        "class_distribution": global_class_counts,
        "recommended_class_weights": v3_weights,
        "processor_summary": processor_stats.get("stats", {})
    }
    
    # Save Manifest inside the last zip or as a sidecar
    mani_path = f"{output_zip_base}_manifest.json"
    with open(mani_path, 'w') as f:
        json.dump(final_manifest, f, indent=4)
        
    weights_path = f"{output_zip_base}_class_weights.yaml"
    with open(weights_path, 'w') as f:
        yaml.dump({"class_weights": v3_weights}, f)

    current_zip.close()
    logging.info(f"Done. Packaged into {vol_idx} volumes. Manifest saved to {mani_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 package_datasets.py <input_dir> <output_zip_base>")
        sys.exit(1)
    create_v3_package(sys.argv[1], sys.argv[2])
