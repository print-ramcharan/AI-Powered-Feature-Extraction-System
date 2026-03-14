# SVAMITVA Project: SHARED PROGRESS TRACKER

This document tracks all project actions so team members know exactly what has been completed after cloning the repository.

## Completed Setup & Data Extraction (Ram's Work)
- **Repository Established:** Git repo initialized, `.gitignore` set, and `AGENT_INSTRUCTIONS.md` created to assign AI roles automatically.
- **Core Pipeline Written:** 
  - `src/train_rooftype.py` (EfficientNet architecture ready)
  - `notebooks/ram_rooftype.ipynb` (Colab environment wrapper ready)
  - `src/inference_pipeline.py` (Master inference script ready)
  - `src/tile_generator.py` (GeoTIFF tiling script ready)
- **Raw Data Unzipped:** The datasets (`CG_450163`, `PB_37458_37774`, and `CG_451189_ecw`) have been successfully downloaded and extracted into the local `data/raw/` directory.

## Current Pending Action
- **Generate Tiled Patches:** Wait for Ram or another teammate to run `src/tile_generator.py` to convert the massive `.tif` files into 640x640 patches.
- **Google Drive Sync:** The generated 640x640 patches inside `data/tiles/` must be zipped and uploaded to the shared `svamitva_project/data/tiles/` Google Drive folder so Sanjay, Sneha, and Nikitha can begin YOLOv8 training.

*(Last Updated: Initial Setup Complete)*
