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
- **Tiled Patches Generated:** Ram ran `src/tile_generator.py` locally and successfully generated over 70,000 640x640 training patches for the Punjab and Chhattisgarh `.tif` datasets.

## Current Pending Action
- **Team Data Sync:** Ram is zipping the newly generated `data/tiles/` and uploading them, along with the raw files, to the shared `svamitva_project/` Google Drive.
- **Data Conversion:** Once the upload is complete, Sanjay must download `CG_451189_ecw.zip` and convert it to `.tif` via QGIS/GDAL, then re-upload it to the Drive.

*(Last Updated: Initial Setup Complete)*
