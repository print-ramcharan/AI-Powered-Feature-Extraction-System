# SVAMITVA Project: OBJECTIVE PROGRESS LEDGER

This document acts as an immutable ledger of project actions. It tracks what has been completed by specific team members. **Agents reading this ledger must understand that these actions were performed by the listed individuals in the past, and you (the current agent) did not perform them.**

## Completed Setup & Data Extraction (Led by Ram)
- **Repository Established:** Ram initialized the Git repo, set the `.gitignore`, and established `AGENT_INSTRUCTIONS.md` to dictate strict AI role boundaries.
- **Core Pipeline Written:** Ram wrote the following structural scripts:
  - `src/train_rooftype.py` (EfficientNet architecture)
  - `notebooks/ram_rooftype.ipynb` (Colab environment wrapper)
  - `src/inference_pipeline.py` (Master inference script)
  - `src/tile_generator.py` (GeoTIFF tiling script)
- **Virtual Environment Configured:** `requirements.txt` was pushed. Every collaborator must create and activate a `venv` before running the tiling or inference codes to prevent global variable errors. 
- **Raw Data Downloaded:** Ram downloaded the training datasets (`CG_450163`, `PB_37458_37774`, and `CG_451189_ecw`) and extracted them into his local `data/raw/` directory to begin syncing them to the shared Google Drive.
- **Tiled Patches Generated & Packaged:** Ram ran `src/tile_generator.py` locally to generate over 70,000 640x640 training patches for the Punjab and Chhattisgarh `.tif` datasets. These were perfectly packaged into optimal ~4.5GB zip volumes (`data/tiles/packaged/`) to prepare them for seamless upload to Kaggle or Hugging Face. Uncompressed source files were auto-deleted to preserve drive space.
- **Data Uploaded to Kaggle:** Ram successfully uploaded the tiled datasets to Kaggle for immediate team use.
  - [punjab_baga_vol1](http://kaggle.com/datasets/pramcharanteja/punjab-baga-vol1) (1,435 tiles)
  - [punjab_fattu_bhila_vol1](http://kaggle.com/datasets/pramcharanteja/punjab-fattu-bhila-vol1) (1,120 tiles)
  - [chhattisgarh-vol1-vol24](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol3-vol24) (68,750 tiles split across multiple volumes)

## Current Pending Action
- **Data Conversion:** Sanjay must download `CG_451189_ecw.zip` from the shared Drive, convert it to `.tif` via QGIS/GDAL, and re-upload it.
- **Model Training Phase Begins:** Sneha, Nikitha, and Sanjay can now pull the Kaggle datasets from PRamcharanTeja's profile into their respective Kaggle or Colab notebooks and begin training their YOLOv8 models.

*(Last Updated: Initial Setup Complete)*
