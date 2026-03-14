"""
Tile Generator Script for SVAMITVA Feature Extraction Model Training.
Author: Ram
Role: Extract 640x640 patches from raw large GeoTIFFs to feed the YOLO/EfficientNet models.

This script uses `rasterio` to read a large village TIF and output small 640x640
tiled patches while safely managing memory constraints.
"""

import os
import gc
import logging
import rasterio
from rasterio.windows import Window
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_tiles(input_tif: str, output_dir: str, tile_size: int = 640, overlap: int = 0):
    """
    Reads a large GeoTIFF and slices it into `tile_size` x `tile_size` patches.
    Saves the output patches to `output_dir`.
    
    Args:
        input_tif (str): Path to the input large GeoTIFF.
        output_dir (str): Directory where the output tiles will be saved.
        tile_size (int): Dimensions of the output tiles (default: 640 for YOLOv8).
        overlap (int): Number of pixels to overlap between tiles (default: 0).
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    logging.info(f"Starting tiling for: {input_tif}")
    
    try:
        with rasterio.open(input_tif) as src:
            meta = src.meta.copy()
            width, height = src.width, src.height
            
            logging.info(f"Original image size: {width}x{height}")
            
            # Update meta for the small tiles
            meta.update({
                "width": tile_size,
                "height": tile_size
            })
            
            stride = tile_size - overlap
            tile_count = 0
            
            # Calculate total windows for progress bar
            # (Adding stride-1 to ceil the division)
            num_cols = (width + stride - 1) // stride
            num_rows = (height + stride - 1) // stride
            total_tiles = num_cols * num_rows

            with tqdm(total=total_tiles, desc="Generating Tiles") as pbar:
                for col_off in range(0, width, stride):
                    for row_off in range(0, height, stride):
                        
                        # Adjust window sizes if they hit the edge of the image
                        w = min(tile_size, width - col_off)
                        h = min(tile_size, height - row_off)
                        
                        # If the tile on the edge is too small, we might want to pad it, 
                        # but for now we skip tiles that aren't perfectly square
                        if w < tile_size or h < tile_size:
                            pbar.update(1)
                            continue

                        window = Window(col_off, row_off, tile_size, tile_size)
                        
                        # Read the specific window block
                        block = src.read(window=window)
                        
                        # Calculate the new transform for this specific tile
                        tile_transform = src.window_transform(window)
                        meta.update({"transform": tile_transform})
                        
                        output_filename = os.path.join(output_dir, f"tile_{col_off}_{row_off}.tif")
                        
                        with rasterio.open(output_filename, 'w', **meta) as dest:
                            dest.write(block)
                            
                        tile_count += 1
                        pbar.update(1)
                        
                        # Memory management for large processes
                        del block, window, tile_transform
                        
                    # Force garbage collection occasionally per column
                    gc.collect()

        logging.info(f"Successfully generated {tile_count} tiles in {output_dir}")
        
    except Exception as e:
        logging.error(f"Failed to generate tiles: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate 640x640 tiles from a GeoTIFF.")
    parser.add_argument("--input", required=True, help="Path to input .tif file")
    parser.add_argument("--output", required=True, help="Path to output directory")
    parser.add_argument("--size", type=int, default=640, help="Tile size (default 640)")
    
    args = parser.parse_args()
    generate_tiles(args.input, args.output, tile_size=args.size)
