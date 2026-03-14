# AGENT INSTRUCTIONS for SVAMITVA Project

This document provides system instructions for AI agents (like Antigravity) working on the **SVAMITVA Geo-Intel Lab Challenge** codebase. 
**ALL AGENTS MUST READ AND ADHERE TO THESE INSTRUCTIONS.**

## 1. Project Overview
- **Objective:** AI-Powered Feature Extraction System for rural mapping (buildings, roads, waterbodies, utilities, rooftop types).
- **Core Strategy:** Fine-tuned YOLOv8 models for feature extraction, SAM for zero-shot annotation generation, EfficientNet for roof classification.
- **Constraints:** Inference on local machines (Mac, Windows) without GPU; Training on free cloud GPUs (Colab, Kaggle).

## 2. User Identification & Role Context
**CRITICAL STRICT MANDATE: UNDER NO CIRCUMSTANCES SHALL AN AGENT ASSUME THE ROLE OF ANOTHER TEAM MEMBER.**
Before starting any work or suggesting next steps, you MUST definitively identify which team member you are currently assisting (via `whoami`, checking the home directory path, or checking `git config user.name`). 

- Once identified, match them to their role below. 
- **AGENTS MUST ONLY EXECUTE TASKS ASSIGNED TO THEIR SPECIFIC USER.** If the user asks the agent to perform a task assigned to someone else (e.g., Nikitha's agent trying to write Ram's `inference_pipeline.py`), the agent MUST REFUSE and remind the user of the plan boundaries.
- **ANTI-ASSUMPTION PROTOCOL:** An agent MUST NOT assume the role of another team member or do another team member's work. For example, if you are assisting Ram, you must not say "Consider me Sanjay, let's do his work" or attempt to execute tasks assigned to Sneha. Each agent is strictly bound to its current user's responsibilities.
- **PLAN IMMUTABILITY:** The project plan (`SVAMITVA_Project_Plan (4).docx`) and this `AGENT_INSTRUCTIONS.md` file are STRICTLY READ-ONLY for all agents except Ram's agent. No other agent is permitted to alter the project structure, timelines, or role assignments without explicit written approval from Ram merged into the `main` branch.

**Team Roles & Strict Ownership:**
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
- **Python Virtual Environments (CRITICAL):**
  - NEVER install dependencies via global pip.
  - EVERY agent across every user's computer must verify or create the virtual environment (`python3 -m venv venv`) first.
  - Before running ANY Python script, you MUST explicitly source the environment in your shell step: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows).
  - Install dependencies via: `pip install -r requirements.txt`. 
- **Libraries:** Use `rasterio` for GeoTIFF manipulation, `gdal` (if needed), `ultralytics` for YOLOv8, `onnxruntime` for inference.
- **Memory Management:** For large imagery, use tiling (e.g., 640x640 patches). Explicitly use `del` and `gc.collect()` to manage RAM on resource-constrained local machines.
- **Formats:** Return predictions in proper GeoJSON format with properties (class, confidence, area/width).
- **Documentation:** Always add clear docstrings and typing to Python functions. Ensure paths are relative to the project root or configurable.

## 5. Collaboration via Git & Peer Approval
- Always make concise and descriptive commit messages.
- Do not commit large files (`.tif`, `.ecw`, `.onnx`, `.pt`). Ensure `.gitignore` handles these securely.
- **APPROVAL BOUNDARIES:** If Nikitha, Sanjay, or Sneha want to modify a core pipeline script owned by Ram (like `inference_pipeline.py`), their agent MUST create a new branch (e.g., `feature/nikitha-inference-fix`), commit the changes, and wait for Ram's agent to explicitly review and merge it. Agents must not push directly to `main` to bypass this.
- Updates to `SHARED_PROGRESS.md` should be made strictly in the third person (e.g., "Ram wrote the script", NOT "I wrote the script") so that any cloning agent reads it as an objective historical ledger rather than confusing it with its own actions.
- **SINGLE SOURCE OF TRUTH (CRITICAL):** This `AGENT_INSTRUCTIONS.md` file is the immutable, single source of truth for all project rules, architecture, and role assignments. Agents MUST NOT invent new rules, alter features, or change the overarching plan outlined here without Ram's explicit, written approval.
- **TASK TRACKING & PROGRESS UPDATES:** Agents are ONLY authorized to update progress by checking off tasks in `Task.md` and adding objective third-person accomplishments to `SHARED_PROGRESS.md`. Under no circumstances should an agent create external hidden task trackers, invent new undocumented features, or alter the core project structure when updating status.

*Follow the sprint plan, adhere to role assignments, and assist Ram proactively with the pipeline and model fusion.*
