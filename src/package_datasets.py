import os
import zipfile
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def create_split_zips(input_dir, output_dir_base, max_zip_size_mb=4500):
    """
    Packages all files in `input_dir` into zip archives. If an archive
    exceeds `max_zip_size_mb` (default 4.5GB to stay safely under 5GB),
    it creates a new volume (e.g., dataset_vol1.zip, dataset_vol2.zip).
    """
    if not os.path.exists(input_dir):
        logging.error(f"Input directory does not exist: {input_dir}")
        return

    # Ensure output base directory exists
    os.makedirs(os.path.dirname(output_dir_base), exist_ok=True)
    
    max_zip_size_bytes = max_zip_size_mb * 1024 * 1024
    
    files_to_zip = [
        os.path.join(dp, f) 
        for dp, dn, filenames in os.walk(input_dir) 
        for f in filenames if f.endswith('.tif')
    ]
    
    if not files_to_zip:
        logging.info(f"No .tif files found in {input_dir}")
        return
        
    logging.info(f"Found {len(files_to_zip)} files to package in {input_dir}")

    vol_idx = 1
    current_zip_path = f"{output_dir_base}_vol{vol_idx}.zip"
    current_zip = zipfile.ZipFile(current_zip_path, 'w', zipfile.ZIP_DEFLATED)
    current_size = 0
    
    logging.info(f"Writing to {current_zip_path}")

    for file_path in files_to_zip:
        # Check size of the file we're about to add
        file_size = os.path.getsize(file_path)
        
        # If this single file pushes us over the 5GB limit, close current zip and open a new one
        if current_size + file_size > max_zip_size_bytes and current_size > 0:
            current_zip.close()
            logging.info(f"Closed {current_zip_path} (Size limit reached)")
            
            vol_idx += 1
            current_zip_path = f"{output_dir_base}_vol{vol_idx}.zip"
            current_zip = zipfile.ZipFile(current_zip_path, 'w', zipfile.ZIP_DEFLATED)
            current_size = 0
            logging.info(f"Started new volume: {current_zip_path}")
            
        arcname = os.path.relpath(file_path, input_dir)
        current_zip.write(file_path, arcname)
        current_size += file_size
        
        # SPACE SAVING: Delete the original uncompressed file immediately after it is safely zipped
        os.remove(file_path)
        
    current_zip.close()
    logging.info(f"Finished packaging. Final volume: {current_zip_path}")
    
    # SPACE SAVING: Delete the now-empty source directory
    import shutil
    try:
        shutil.rmtree(input_dir)
        logging.info(f"Deleted source directory {input_dir} to free up space.")
    except Exception as e:
        logging.error(f"Could not delete {input_dir}: {e}")

if __name__ == "__main__":
    import sys
    # To run one at a time and save space, take arguments from command line
    if len(sys.argv) < 3:
        print("Usage: python3 package_datasets.py <input_dir> <output_base>")
        sys.exit(1)
        
    input_directory = sys.argv[1]
    output_base_name = sys.argv[2]
    
    create_split_zips(
        input_dir=input_directory,
        output_dir_base=output_base_name,
        max_zip_size_mb=4500
    )
