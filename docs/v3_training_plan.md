# V3 Model Retraining Plan: "Total Feature Inclusion"

This plan addressed the observed failures where the model incorrectly identifies agricultural fields as water bodies/buildings and fails on rare classes.

## 🚀 Key Improvements

1.  **Resolution Boost**: Retile and train at `imgsz=1280` (Mandatory). This reduces texture aliasing and provides better context for small buildings vs. crops.
2.  **Hard Negative Inclusion**: Adjust the sampling pipeline to include **more background tiles** from the "Punjab" and agricultural regions. This explicitly teaches the model: `Field Pattern != Building/Water`.
3.  **Class Balancing**: Implement oversampling for rare classes (Overhead Tank, Transformer, Waterbody Point) and use weighted loss if supported by the trainer.
4.  **Higher Capacity Model**: Switch from `YOLO11s` (Small) to `YOLO11m` (Medium) or `YOLO11l` (Large) to better separate complex aerial features.
5.  **Longer Convergence**: Increase epochs to 200 with aggressive early stopping and high-resolution augmentations (MixUp, Copy-Paste).

## 🛠️ Implementation Steps

### 1. Data Preparation (Tiling & Processing)
*   Update `tile_generator.py` (or use CLI) to generate **1280x1280** tiles.
*   Update `smart_processor.py` to increase `neg_ratio` from `0.1` to `0.5` or `1.0` (Full inclusion of background context).

### 2. Dataset Packaging
*   Modify `package_datasets.py` to:
    *   Implement **10x Copy-Paste augmentation** for rare classes during packaging (if offline) OR use YOLO's internal oversampling.
    *   Ensure all villages from both Chhattisgarh and Punjab are included to reduce domain shift.

### 3. V3 Training Configuration
*   Create `data/v3_training.yaml`.
*   Establish the training CLI command with `1280` resolution.

## 📝 Proposed Config Changes

| Parameter | V2 (Current) | V3 (Proposed) | Rationale |
| :--- | :--- | :--- | :--- |
| **Model** | YOLO11s | **YOLO11m** | Higher param count for better feature separation. |
| **imgsz** | 640 | **1280** | Vital for small object detection in fields. |
| **Neg Ratio** | ~10% | **50% - 100%** | Learn rural textures to suppress false positives. |
| **Epochs** | 100 | **200** | Allow model to converge on complex patterns. |
| **Augments** | Default | **MixUp + CopyPaste** | Vital for handling class imbalance. |
