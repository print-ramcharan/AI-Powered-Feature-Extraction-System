# AGENT INSTRUCTIONS for SVAMITVA Project

This document provides system instructions for AI agents (like Antigravity) working on the **SVAMITVA Geo-Intel Lab Challenge** codebase. 
**ALL AGENTS MUST READ AND ADHERE TO THESE INSTRUCTIONS.**

## 1. Project Overview
- **Objective:** AI-Powered Feature Extraction System for rural mapping (buildings, roads, waterbodies, utilities, rooftop types).
- **Core Strategy:** Fine-tuned YOLOv8 models for feature extraction, SAM for zero-shot annotation generation, EfficientNet for roof classification.
- **Constraints:** Inference on local machines (Mac, Windows) without GPU; Training on free cloud GPUs (Colab, Kaggle).

## 2. User Identification & Role Context
**CRITICAL: IDENTIFY THE USER FIRST.** Before starting any work or suggesting next steps, you MUST identify which team member you are currently assisting. 
- You can automatically identify the user by checking their system username (e.g., running `whoami`), examining their home directory path, or checking their Git configuration (`git config user.name`).
- Once identified, match them to their role below. Read the `.docx` project plan and context to determine what they should be working on right now, what files they own, and what their immediate next steps are.

**Team Roles & Ownership:**
- **Ram (Project Lead):** Focused on rooftop classifier (`train_rooftype.py`), model fusion/inference (`inference_pipeline.py`), and the final project report.
- **Sanjay:** Focused on the building footprint model (`train_buildings.py`), hosting raw training data, and ECW to GeoTIFF conversions.
- **Sneha:** Focused on road and waterbody extraction models (`train_roads.py`, `train_water.py`), and QGIS annotations.
- **Nikitha:** Focused on utility detection (`train_utilities.py`), post-processing pipeline (`stitch_tiles.py`, `export_geojson.py`, `compute_metrics.py`), and scoring test data.

*(If you cannot determine the user automatically, politely ask them to identify themselves from the list above before proceeding.)*

## 3. Directory Structure Rules
If creating or modifying files, ensure they fit into this architecture:
- `data/` - For raw imagery and annotations (NOT tracked in git)
- `models/` - For ONNX weights (NOT tracked in git, synced via Drive)
- `src/` - For all Python scripts (`tile_generator.py`, `inference_pipeline.py`, etc.)
- `notebooks/` - For Jupyter/Colab notebooks (`ram_rooftype.ipynb`, etc.)
- `outputs/` - Final GeoJSON predictions and `.tif` overlays
- `docs/` - Project documentation and reports

## 4. Coding & Implementation Guidelines
- **Libraries:** Use `rasterio` for GeoTIFF manipulation, `gdal` (if needed), `ultralytics` for YOLOv8, `onnxruntime` for inference.
- **Memory Management:** For large imagery, use tiling (e.g., 640x640 patches). Explicitly use `del` and `gc.collect()` to manage RAM on resource-constrained local machines.
- **Formats:** Return predictions in proper GeoJSON format with properties (class, confidence, area/width).
- **Documentation:** Always add clear docstrings and typing to Python functions. Ensure paths are relative to the project root or configurable.

## 5. Collaboration via Git
- Always make concise and descriptive commit messages.
- Do not commit large files (`.tif`, `.ecw`, `.onnx`, `.pt`). Ensure `.gitignore` handles these securely.
- When generating scripts, update the `README.md` or this document if architectural changes are made.

*Follow the sprint plan, adhere to role assignments, and assist Ram proactively with the pipeline and model fusion.*
