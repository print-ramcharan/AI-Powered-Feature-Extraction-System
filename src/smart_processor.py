import os
import sys
import logging
import geopandas as gpd
import rasterio
from rasterio.windows import Window
from shapely.geometry import box
import random
import numpy as np
import cv2
from tqdm import tqdm
import json
from datetime import datetime

# --- V3 Configuration (Adjusted) ---
V3_VERSION = "3.1.0"
PIPELINE_DATE = datetime.now().strftime("%Y-%m-%d")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def classify_negative_type(tile_image):
    """
    Distinguish hard negatives from easy negatives using texture metrics.
    Refinement 2: Texture-based classification.
    """
    try:
        # Check if tile_image is CHW (rasterio format)
        if len(tile_image.shape) == 3 and tile_image.shape[0] < tile_image.shape[1]: 
            tile_image = np.transpose(tile_image, (1, 2, 0))
            
        gray = cv2.cvtColor(tile_image, cv2.COLOR_RGB2GRAY)
        
        # 1. Edge Density (Canny)
        edges = cv2.Canny(gray, 50, 150)
        edge_count = np.count_nonzero(edges)
        edge_density = edge_count / edges.size
        
        # 2. Texture Variance (Laplacian)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # 3. Color Variance (STD)
        color_std = np.std(tile_image, axis=(0, 1)).mean()
        
        # Classification thresholds (Tuned for rural field detection)
        is_hard = (edge_density > 0.05 or laplacian_var > 100 or color_std > 30)
        
        return 'hard' if is_hard else 'easy', {
            "edge_density": float(edge_density),
            "laplacian_var": float(laplacian_var),
            "color_std": float(color_std)
        }
    except Exception as e:
        logging.warning(f"Classification failed: {e}")
        return 'easy', {}

def validate_and_format_labels(labels, img_w=1280, img_h=1280):
    """
    Enhanced Label Validation Pipeline (Balanced).
    Refinement 3: Relative threshold (0.5%) and geometry clipping.
    """
    valid_labels = []
    stats = {
        "removed_too_small": 0, 
        "removed_oob": 0, 
        "clipped": 0, 
        "removed_aspect": 0
    }
    
    # Relative threshold: 0.5% of tile size (6.4px for 1280)
    # This preserves small objects like Tanks while filtering noise.
    min_px = 0.005 * img_w 
    
    for lbl in labels:
        cls, cx, cy, w, h = lbl
        
        # 1. Format Check (Basic Bounds)
        if not (0 <= cx <= 1 and 0 <= cy <= 1):
            stats["removed_oob"] += 1
            continue
            
        # 2. Relative Area Check (0.5% Threshold)
        px_w, px_h = w * img_w, h * img_h
        if px_w < min_px or px_h < min_px:
            stats["removed_too_small"] += 1
            continue
            
        # 3. Aspect Ratio Check (Max 10:1)
        aspect = max(px_w/px_h, px_h/px_w) if px_h > 0 and px_w > 0 else 0
        if aspect > 10:
            stats["removed_aspect"] += 1
            continue
            
        # 4. Clipping to Image Bounds
        x1, y1 = cx - w/2, cy - h/2
        x2, y2 = cx + w/2, cy + h/2
        
        if x1 < 0 or y1 < 0 or x2 > 1 or y2 > 1:
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(1, x2), min(1, y2)
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            w, h = x2 - x1, y2 - y1
            stats["clipped"] += 1
            
        valid_labels.append(f"{int(cls)} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
        
    return valid_labels, stats

def get_yolo_labels(tile_geom, gdfs, inv_transform, col_off, row_off, tile_size):
    """Helper to extract and transform geometries to YOLO format."""
    labels = []
    for gdf, c_id in gdfs:
        # Spatial Filter
        possible = gdf.iloc[gdf.sindex.query(tile_geom, predicate="intersects")]
        for _, row in possible.iterrows():
            geom = row.geometry.intersection(tile_geom)
            if geom.is_empty: continue
            minx, miny, maxx, maxy = geom.bounds
            p_min_col, p_min_row = inv_transform * (minx, maxy)
            p_max_col, p_max_row = inv_transform * (maxx, miny)
            obj_w, obj_h = p_max_col - p_min_col, p_max_row - p_min_row
            x_c = (p_min_col + (obj_w / 2.0) - col_off) / tile_size
            y_c = (p_min_row + (obj_h / 2.0) - row_off) / tile_size
            labels.append([c_id, x_c, y_c, obj_w/tile_size, obj_h/tile_size])
    return labels

def smart_process_v3(input_tif, shp_dir, output_dir, tile_size=1280, neg_ratio=0.3):
    """
    V3 Sequential Single-Pass Orchestrator.
    Implements Refinement 1 (±320px shift) and Refinement 2 (Texture Capping).
    """
    img_out = os.path.join(output_dir, "images")
    lbl_out = os.path.join(output_dir, "labels")
    os.makedirs(img_out, exist_ok=True)
    os.makedirs(lbl_out, exist_ok=True)

    # Full 15-Class Ontology (Corrected for Type_ID Mapping)
    class_mappings = [
        {"id": 0, "shp": "Built_Up_Area", "filter_col": "Roof_type", "filter_val": 1},  # Permanent (RCC)
        {"id": 1, "shp": "Built_Up_Area", "filter_col": "Roof_type", "filter_val": 2},  # Semi-Permanent (Tiled)
        {"id": 2, "shp": "Built_Up_Area", "filter_col": "Roof_type", "filter_val": 3},  # Tin
        {"id": 3, "shp": "Built_Up_Area", "filter_col": "Roof_type", "filter_val": 4},  # Others
        {"id": 4, "shp": "Road", "filter_col": None, "filter_val": None},
        {"id": 5, "shp": "Water_Body", "filter_col": None, "filter_val": None},
        {"id": 6, "shp": "Utility", "filter_col": "Utility_Ty", "filter_val": 1},  # Transformer
        {"id": 7, "shp": "Utility", "filter_col": "Utility_Ty", "filter_val": 10}, # Overhead Tank (Original spec)
        {"id": 7, "shp": "Utility", "filter_col": "Utility_Ty", "filter_val": 11}, # Overhead Tank (CG specific variation)
        {"id": 8, "shp": "Utility", "filter_col": "Utility_Ty", "filter_val": 14}, # Well
        {"id": 9, "shp": "Bridge", "filter_col": None, "filter_val": None},
        {"id": 10, "shp": "Railway", "filter_col": None, "filter_val": None},
        {"id": 11, "shp": "Road_Centre_Line", "filter_col": None, "filter_val": None},
        {"id": 12, "shp": "Water_Body_Line", "filter_col": None, "filter_val": None},
        {"id": 13, "shp": "Utility_Poly", "filter_col": None, "filter_val": None},
        {"id": 14, "shp": "Waterbody_Point", "filter_col": None, "filter_val": None},
    ]

    manifest = {
        "dataset_version": V3_VERSION,
        "processing_date": PIPELINE_DATE,
        "tile_size": tile_size,
        "village": os.path.basename(input_tif),
        "stats": {
            "positives": 0, "hard_negatives": 0, "easy_negatives": 0, "boundary_shifted": 0,
            "labels_removed_small": 0, "labels_removed_oob": 0, "labels_clipped": 0
        }
    }

    try:
        with rasterio.open(input_tif) as src:
            tif_crs = src.crs
            width, height = src.width, src.height
            transform = src.transform
            inv_transform = ~transform

            # Validate TIF CRS — fall back to EPSG:4326 roundtrip if CRS is non-standard
            try:
                tif_crs.to_epsg()  # Will raise if CRS has no EPSG code
                canonical_crs = tif_crs
            except Exception:
                # Try to round-trip via WKT to get a clean CRS object
                try:
                    from pyproj import CRS as ProjCRS
                    canonical_crs = ProjCRS.from_wkt(tif_crs.to_wkt())
                    logging.info(f"Non-standard TIF CRS — using WKT roundtrip: {canonical_crs.name}")
                except Exception as e:
                    logging.warning(f"CRS normalization failed ({e}), using raw TIF CRS")
                    canonical_crs = tif_crs

            # Compute TIF footprint in WGS84 for spatial pre-filtering
            from rasterio.warp import transform_bounds
            from shapely.geometry import box as shp_box
            try:
                tif_wgs84_bounds = transform_bounds(tif_crs, "EPSG:4326",
                    src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top)
                tif_wgs84_box = shp_box(*tif_wgs84_bounds)
                logging.info(f"TIF WGS84 footprint: lon=[{tif_wgs84_bounds[0]:.4f},{tif_wgs84_bounds[2]:.4f}], "
                             f"lat=[{tif_wgs84_bounds[1]:.4f},{tif_wgs84_bounds[3]:.4f}]")
            except Exception as e:
                logging.warning(f"Could not compute TIF WGS84 footprint: {e}")
                tif_wgs84_box = None

            # 1. Recursive SHP Search Logic
            logging.info(f"Scanning {shp_dir} for SHP layers...")
            all_shp_paths = []
            for root, _, files in os.walk(shp_dir):
                for f in files:
                    if f.lower().endswith(".shp") and not os.path.basename(f).startswith("_global_"):
                        all_shp_paths.append((os.path.join(root, f), False))  # (path, is_global)
                    elif f.lower().endswith(".shp") and os.path.basename(f).startswith("_global_"):
                        all_shp_paths.append((os.path.join(root, f), True))

            def safe_reproject(gdf_in, target_crs):
                """
                Reproject via WGS84 intermediate to avoid silent coordinate
                corruption when target_crs is a custom/non-standard projection.
                """
                try:
                    # Step 1: to WGS84
                    gdf_wgs = gdf_in.to_crs("EPSG:4326")
                    # Step 2: WGS84 -> target
                    return gdf_wgs.to_crs(target_crs)
                except Exception as e:
                    logging.warning(f"WGS84-intermediate reproject failed ({e}), trying direct")
                    return gdf_in.to_crs(target_crs)

            gdfs = []
            total_overlapping_features = 0
            for mapping in class_mappings:
                target_key = mapping["shp"].lower().replace("_", "")
                found_path = None
                is_global = False
                # Prefer local (non-global) SHPs first
                for p, glob_flag in sorted(all_shp_paths, key=lambda x: x[1]):
                    # Normalize filename: strip the '_global_' prefix we added for global SHPs,
                    # then remove underscores for fuzzy matching.
                    # NOTE: do NOT use lstrip() here — it strips individual characters, not
                    # a prefix string, and would corrupt 'builtuparea' into 'uituparea'.
                    raw_basename = os.path.basename(p).lower()
                    if raw_basename.startswith("_global_"):
                        raw_basename = raw_basename[len("_global_"):]
                    file_name = raw_basename.replace("_", "")
                    if target_key in file_name:
                        found_path = p
                        is_global = glob_flag
                        break

                if found_path:
                    try:
                        gdf_raw = gpd.read_file(found_path)

                        # Pre-flight: filter to features that overlap TIF WGS84 footprint
                        if tif_wgs84_box is not None:
                            gdf_wgs = gdf_raw.to_crs("EPSG:4326")
                            mask = gdf_wgs.intersects(tif_wgs84_box)
                            if not mask.any():
                                logging.info(f"  [SKIP] Class {mapping['id']}: {os.path.basename(found_path)} "
                                             f"(0/{len(gdf_raw)} features overlap TIF footprint {'[global]' if is_global else '[local]'})")
                                continue
                            gdf_raw = gdf_raw[mask].copy()
                            logging.info(f"  [FOUND] Class {mapping['id']}: {os.path.basename(found_path)} "
                                         f"({mask.sum()} overlapping features {'[global]' if is_global else '[local]'})")
                        else:
                            logging.info(f"  [FOUND] Class {mapping['id']}: {os.path.basename(found_path)}")

                        # Reproject via WGS84 intermediate
                        gdf = safe_reproject(gdf_raw, tif_crs)

                        # Multi-Class Filtering Logic (Strict Mode)
                        if mapping["filter_col"]:
                            if mapping["filter_col"] in gdf.columns:
                                # Convert to string for robust comparison (handles '1' vs 1)
                                sub = gdf[gdf[mapping["filter_col"]].astype(str).str.strip() == str(mapping["filter_val"])]
                            else:
                                # Column missing -> avoid duplication by returning empty GDF
                                sub = gdf.iloc[0:0].copy()
                        else:
                            # No filter column (e.g. Roads, Water Body) -> use all features
                            sub = gdf

                        if not sub.empty:
                            gdfs.append((sub, mapping["id"]))
                            total_overlapping_features += len(sub)
                    except Exception as e:
                        logging.warning(f"  [ERROR] Failed to read {found_path}: {e}")

            logging.info(f"Pre-flight complete: {len(gdfs)} active SHP layers, "
                         f"{total_overlapping_features} total features overlapping TIF")

            # Refinement 3: Generator-based Grid
            def get_grid_coords(w, h, size):
                for col in range(0, w, size):
                    for row in range(0, h, size):
                        if col + size <= w and row + size <= h:
                            yield (col, row)

            logging.info("Pass 1: Baseline Grid Generation (Stride 1280)...")
            for col_off, row_off in tqdm(get_grid_coords(width, height, tile_size), desc="Processing V3.1"):
                # Spatial Geometry
                x_min, y_max = transform * (col_off, row_off)
                x_max, y_min = transform * (col_off + tile_size, row_off + tile_size)
                tile_geom = box(x_min, y_min, x_max, y_max)
                
                # Label Extraction
                raw_labels = get_yolo_labels(tile_geom, gdfs, inv_transform, col_off, row_off, tile_size)
                valid_yolo, v_stats = validate_and_format_labels(raw_labels, tile_size, tile_size)
                
                save_list = [(col_off, row_off, valid_yolo, False)]
                if valid_yolo:
                    for dx in [-320, 320]:
                        for dy in [-320, 320]:
                            nx, ny = col_off + dx, row_off + dy
                            if 0 <= nx <= width - tile_size and 0 <= ny <= height - tile_size:
                                s_xmin, s_ymax = transform * (nx, ny)
                                s_xmax, s_ymin = transform * (nx + tile_size, ny + tile_size)
                                s_geom = box(s_xmin, s_ymin, s_xmax, s_ymax)
                                s_labels = get_yolo_labels(s_geom, gdfs, inv_transform, nx, ny, tile_size)
                                s_valid, _ = validate_and_format_labels(s_labels, tile_size, tile_size)
                                if s_valid:
                                    save_list.append((nx, ny, s_valid, True))

                for cx, ry, lbls, is_shift in save_list:
                    base_name = f"v3_{cx}_{ry}"
                    if is_shift: base_name += "_shift"
                    if os.path.exists(os.path.join(img_out, base_name + ".jpg")): continue

                    window = Window(cx, ry, tile_size, tile_size)
                    tile_array = src.read(window=window)
                    if tile_array.mean() < 5: continue

                    if not lbls and not is_shift:
                        neg_type, _ = classify_negative_type(tile_array)
                        if neg_type == 'hard':
                            # Harvest more hard negatives (fields/complex textures) to reduce False Positives
                            if manifest["stats"]["hard_negatives"] > (manifest["stats"]["positives"] * 4) + 100:
                                continue 
                            manifest["stats"]["hard_negatives"] += 1
                        else:
                            if random.random() > neg_ratio: continue 
                            manifest["stats"]["easy_negatives"] += 1
                    elif lbls:
                        if is_shift: manifest["stats"]["boundary_shifted"] += 1
                        else: manifest["stats"]["positives"] += 1

                    out_img = np.transpose(tile_array, (1, 2, 0)) 
                    out_img = cv2.cvtColor(out_img, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(os.path.join(img_out, base_name + ".jpg"), out_img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
                    
                    if lbls:
                        with open(os.path.join(lbl_out, base_name + ".txt"), 'w') as f:
                            f.write("\n".join(lbls))

                manifest["stats"]["labels_removed_small"] += v_stats["removed_too_small"]
                manifest["stats"]["labels_removed_oob"] += v_stats["removed_oob"]
                manifest["stats"]["labels_clipped"] += v_stats["clipped"]

    except Exception as e:
        logging.error(f"FATAL ERROR in smart_process_v3: {e}")
        sys.exit(1)

    # Final Manifest Save
    with open(os.path.join(output_dir, "v3_manifest.json"), 'w') as f:
        json.dump(manifest, f, indent=2)
    
    logging.info(f"V3.1 Prep Complete. Manifest: {json.dumps(manifest['stats'], indent=2)}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--tif", required=True)
    parser.add_argument("--shp_dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--tile_size", type=int, default=1280)
    parser.add_argument("--neg_ratio", type=float, default=0.3)
    args = parser.parse_args()
    smart_process_v3(args.tif, args.shp_dir, args.output, args.tile_size, args.neg_ratio)
