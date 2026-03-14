# AGENT INSTRUCTIONS for SVAMITVA Project

This document provides system instructions for AI agents (like Antigravity) working on the **SVAMITVA Geo-Intel Lab Challenge** codebase. 
**ALL AGENTS MUST READ AND ADHERE TO THESE INSTRUCTIONS.**

## 1. Project Overview
- **Objective:** AI-Powered Feature Extraction System for rural mapping (buildings, roads, waterbodies, utilities, rooftop types).
- **Core Strategy:** Fine-tuned YOLOv8 models for feature extraction, SAM for zero-shot annotation generation, EfficientNet for roof classification.
- **Constraints:** Inference on local machines (Mac, Windows) without GPU; Training on free cloud GPUs (Colab, Kaggle).

## 2. Team Structure & Roles
When collaborating with the user (Ram), understand the team context:
- **Ram (User/Lead):** Project lead, focused on rooftop classifier (`train_rooftype.py`), model fusion (`inference_pipeline.py`), and final report.
- **Sanjay:** Building footprint model (`train_buildings.py`), hosts training data, handles ECW to GeoTIFF conversion.
- **Sneha:** Road + waterbody extraction models (`train_roads.py`, `train_water.py`), QGIS annotation.
- **Nikitha:** Utility detection (`train_utilities.py`), post-processing, hosts test data.

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
