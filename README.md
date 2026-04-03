# AI-Powered Feature Extraction System

High-precision object detection pipeline for SVAMITVA V3 aerial imagery utilizing YOLO11 at 1280px resolution for rural infrastructure extraction.

## Model Technical Specification

- **Architecture**: YOLO11s (Single-Pass Object Detection)
- **Input Resolution**: 1280 x 1280 pixels (RGB)
- **Training Environment**: Kaggle Dual Tesla T4 (DDP - Distributed Data Parallel)
- **Framework**: torch-2.10.0+cu128 / Ultralytics 8.4.32

### Training Hyperparameters

- **Batch Size**: 8 (Split across dual GPUs)
- **Optimizer**: Auto (AdamW / SGD based on weight decay)
- **Initial Learning Rate**: 0.01 (lr0)
- **Final Learning Rate**: 0.01 (lrf)
- **Epochs**: 150 (Cumulative across sessions)
- **Augmentation Pipeline**:
    - Mosaic: 1.0
    - Mixup: 0.2
    - Degrees: 45.0
    - Scale: 0.5
    - Fliplr: 0.5

## Dataset and Class Definitions

The model is trained on the SVAMITVA V3 Unified 14-Class Dataset.

| ID | Class Name | Feature Type | Description |
|---|---|---|---|
| 0 | Building_RCC | Polygon | Permanent concrete roof structures |
| 1 | Building_Tiled | Polygon | Structures with tiled roofs |
| 2 | Building_Tin | Polygon | Structures with metallic/tin roofs |
| 3 | Building_Other | Polygon | Temporary or mixed-material buildings |
| 4 | Road_Polygon | Polygon | Mapped road surfaces |
| 5 | Water_Body_Polygon | Polygon | Ponds, tanks, and stagnant water bodies |
| 6 | Transformer | Polygon | Electrical transformers and substations |
| 7 | Overhead_Tank | Polygon | Elevated water storage tanks |
| 8 | Well | Point/Polygon | Open wells and borewells |
| 9 | Bridge | Polygon | Road or pedestrian bridges over water/rail |
| 10 | Railway | Line/Polygon | Railway tracks and infrastructure |
| 11 | Road_Center_Line | Line | Linear reference for road networks |
| 12 | Water_Body_Line | Line | Canals and narrow water channels |
| 13 | Utility_Polygon | Polygon | Other miscellaneous utility infrastructure |
| 14 | Waterbody_Point | Point | Small-scale water sources |

## Input and Output Specifications

### Input Specification
- **Format**: JPG or PNG (24-bit RGB)
- **Dimensions**: 1280 x 1280 pixels
- **Resolution**: Normalized 1280px tiles

### Output Specification
- **Format**: Text (.txt) files (YOLOv8/V11 normalized)
- **Content**: `<class_id> <x_center> <y_center> <width> <height>`
- **Normalization**: Relative to 1280px dimensions (range 0.0 - 1.0)

## Training Pipeline Sessions

The model was iteratively refined through three major training sessions to ensure stability and convergence across 15 infrastructure classes.

### [Foundation Session](notebooks/1280px-training-session-1.ipynb)
- **Objective**: Establish baseline weights for high-resolution 1280px feature sets.
- **Data**: SVAMITVA V3 Volume 1 (Initial 1030 image set).
- **Strategy**: Transfer learning from YOLO11s pretrained weights to establish building and road morphology.

### [Scaling Session](notebooks/1280px-training-session-2.ipynb)
- **Objective**: Dataset expansion and robustness training.
- **Data**: SVAMITVA V3 Volumes 1-5 (Unified dataset expansion).
- **Strategy**: Dual-GPU Distributed Data Parallel (DDP) execution on Tesla T4 hardware. High-intensity Mosaic (1.0) and Mixup (0.2) augmentation enabled to combat agricultural false positives.

### [Optimization Session](notebooks/1280px-training-session-3.ipynb)
- **Objective**: Final precision refinement of boundary localization.
- **Checkpoint**: Resumed from Cumulative Epoch 97.
- **Strategy**: Fine-tuning of class weights for Utility_Polygon (Transformer/Overhead Tank) and high-accuracy boundary localization for overlapping feature classes.

## Project Structure

- **data/**: Raw and processed SVAMITVA imagery volumes.
- **notebooks/**: Jupyter notebooks for the three-stage training pipeline.
- **src/feature_engineering/**: Scripts for TIF-to-JPG tiling and SHP boundary-shift alignment.
- **src/training/**: Configuration files and training scripts for the Ultralytics engine.
