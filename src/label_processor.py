import os
import logging
import geopandas as gpd
import rasterio
from shapely.geometry import box
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def convert_shps_to_yolo(input_tif, shp_dir, output_dir, tile_size=640):
    """
    Comprehensive mapping of ALL provided survey layers to YOLO format.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Define the Unified 15-Class Ontology (Total Inclusion)
    class_mappings = [
        {"id": 0, "shp": "Built_Up_Area_typ", "filter_col": "Roof_type", "filter_val": 1, "label": "Building: RCC"},
        {"id": 1, "shp": "Built_Up_Area_typ", "filter_col": "Roof_type", "filter_val": 2, "label": "Building: Tiled"},
        {"id": 2, "shp": "Built_Up_Area_typ", "filter_col": "Roof_type", "filter_val": 3, "label": "Building: Tin"},
        {"id": 3, "shp": "Built_Up_Area_typ", "filter_col": "Roof_type", "filter_val": 4, "label": "Building: Other"},
        {"id": 4, "shp": "Road", "filter_col": None, "filter_val": None, "label": "Road Polygon"},
        {"id": 5, "shp": "Water_Body", "filter_col": None, "filter_val": None, "label": "Water Body Polygon"},
        {"id": 6, "shp": "Utility", "filter_col": "Utility_Ty", "filter_val": 1, "label": "Transformer"},
        {"id": 7, "shp": "Utility", "filter_col": "Utility_Ty", "filter_val": 2, "label": "Overhead Tank"},
        {"id": 8, "shp": "Utility", "filter_col": "Utility_Ty", "filter_val": 3, "label": "Well"},
        {"id": 9, "shp": "Bridge", "filter_col": None, "filter_val": None, "label": "Bridge"},
        {"id": 10, "shp": "Railway", "filter_col": None, "filter_val": None, "label": "Railway"},
        {"id": 11, "shp": "Road_Centre_Line", "filter_col": None, "filter_val": None, "label": "Road Center Line"},
        {"id": 12, "shp": "Water_Body_Line", "filter_col": None, "filter_val": None, "label": "Water Body Line"},
        {"id": 13, "shp": "Utility_Poly", "filter_col": None, "filter_val": None, "label": "Utility Polygon"},
        {"id": 14, "shp": "Waterbody_Point", "filter_col": None, "filter_val": None, "label": "Waterbody Point"},
    ]

    with rasterio.open(input_tif) as src:
        tif_crs = src.crs
        width, height = src.width, src.height
        transform = src.transform
        inv_transform = ~transform

        gdfs = []
        loaded_shps = {}
        
        logging.info(f"Loading survey layers for {input_tif}...")
        for mapping in class_mappings:
            base_name = mapping["shp"]
            # Search for the file with various potential extensions/suffixes
            found_path = None
            for suffix in ["", ".shp", "_type.shp", "_typ.shp", "_.shp"]:
                p = os.path.join(shp_dir, base_name + suffix)
                if os.path.exists(p) and p.endswith(".shp"):
                    found_path = p
                    break
            
            if found_path:
                shp_key = os.path.basename(found_path)
                if shp_key not in loaded_shps:
                    loaded_shps[shp_key] = gpd.read_file(found_path).to_crs(tif_crs)
                
                gdf = loaded_shps[shp_key]
                if mapping["filter_col"] and mapping["filter_col"] in gdf.columns:
                    sub_gdf = gdf[gdf[mapping["filter_col"]] == mapping["filter_val"]]
                else:
                    sub_gdf = gdf
                
                if not sub_gdf.empty:
                    gdfs.append((sub_gdf, mapping["id"]))
                    logging.info(f" -> Mapping Class {mapping['id']} ({mapping['label']}): {len(sub_gdf)} features (Source: {shp_key})")

        if not gdfs:
            logging.warning("No features found in any survey layer for this area.")
            return

        logging.info(f"Generating labels (15-class) with stride {tile_size}...")
        for col_off in tqdm(range(0, width, tile_size), desc="Tiling Rows"):
            for row_off in range(0, height, tile_size):
                w = min(tile_size, width - col_off)
                h = min(tile_size, height - row_off)
                if w < tile_size or h < tile_size: continue

                x_min, y_max = transform * (col_off, row_off)
                x_max, y_min = transform * (col_off + tile_size, row_off + tile_size)
                tile_geom = box(x_min, y_min, x_max, y_max)
                
                yolo_labels = []
                for gdf, c_id in gdfs:
                    possible = gdf.iloc[gdf.sindex.query(tile_geom, predicate="intersects")]
                    for _, row in possible.iterrows():
                        geom = row.geometry.intersection(tile_geom)
                        if geom.is_empty: continue
                        
                        minx, miny, maxx, maxy = geom.bounds
                        p_min_col, p_min_row = inv_transform * (minx, maxy)
                        p_max_col, p_max_row = inv_transform * (maxx, miny)
                        
                        obj_w = p_max_col - p_min_col
                        obj_h = p_max_row - p_min_row
                        x_center = (p_min_col + (obj_w / 2.0) - col_off) / tile_size
                        y_center = (p_min_row + (obj_h / 2.0) - row_off) / tile_size
                        norm_w = obj_w / tile_size
                        norm_h = obj_h / tile_size
                        
                        yolo_labels.append(f"{c_id} {max(0,min(1,x_center)):.6f} {max(0,min(1,y_center)):.6f} {max(0,min(1,norm_w)):.6f} {max(0,min(1,norm_h)):.6f}")

                if yolo_labels:
                    out_path = os.path.join(output_dir, f"tile_{col_off}_{row_off}.txt")
                    with open(out_path, 'w') as f:
                        f.write("\n".join(yolo_labels))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--tif", required=True)
    parser.add_argument("--shp_dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    convert_shps_to_yolo(args.tif, args.shp_dir, args.output)
