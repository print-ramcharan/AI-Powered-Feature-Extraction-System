# SVAMITVA Project Setup Task Plan

- [x] Initialize git repository
- [x] Create `.gitignore` to exclude large data and models
- [x] Create `AGENT_INSTRUCTIONS.md` to guide AI agents collaborating on the project
- [x] Commit initial setup to git

## Additional Updates
- [x] Add instructions for AI to automatically identify the user and their associated tasks
- [x] Push project to GitHub remote: `https://github.com/print-ramcharan/AI-Powered-Feature-Extraction-System.git`

## Phase 1: Software Setup & Core Pipeline
- [x] Create a new branch `feature/ram-core-pipeline`
- [x] Create `requirements.txt` based on project needs (YOLO, ONNX, Rasterio, etc.)
- [x] Setup standard directory structure (`src`, `notebooks`, etc.)
- [x] Write `src/tile_generator.py` (Ram's Day 1 task)
- [x] Convert `CG_451189_ecw` to GeoTIFF via QGIS/GDAL and upload (Sanjay's task)
- [x] Merge `feature/ram-core-pipeline` to `main` and push

## Phase 2: Core Modeling & Inference Pipeline (Ram's Work)
- [x] Create `src/train_rooftype.py` (EfficientNet roof classifier)
- [x] Create `notebooks/ram_rooftype.ipynb` (Colab/Kaggle training notebook)
- [x] Create `src/inference_pipeline.py` (Master script for model fusion)
- [x] Commit and push changes to `main`

## Phase 3: Collaborative Agent Protocols & Virtual Env Setup
- [x] Update `AGENT_INSTRUCTIONS.md` to explicitly mandate `venv` usage across all OSs
- [x] Add `venv` updates to `SHARED_PROGRESS.md`
- [x] Commit and Push changes so other agents sync properly

## Phase 4: Strict Agent Authorization Protocols
- [x] Enforce anti-hallucination policies in `AGENT_INSTRUCTIONS.md`
- [x] Rewrite `SHARED_PROGRESS.md` into third-person objective ledger
- [x] Push strict policy updates to GitHub

## Phase 5: Data Tiling & Export
- [x] Generate patches for Punjab (`fattu_bhila` and `bagga`)
- [x] Generate patches for Chhattisgarh (`CG_450163`)

## Phase 6: Dataset Packaging for Hosting (Kaggle/HF)
- [x] Package Punjab and Chhattisgarh tiles into optimized (~5GB) zip volumes

## Phase 7: Team Handoff & Training Guardrails
- [x] Mandate isolated feature branches for all new work
- [x] Mandate subset testing (50-100 images) before full-scale training loops
- [x] Push final handoff-ready documentation to GitHub
