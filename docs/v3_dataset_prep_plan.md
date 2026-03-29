# V3 Dataset "Clear-Cut" Preparation: Feature Engineering for Kaggle

This plan focuses on building a high-quality, balanced dataset for SVAMITVA V3 training. The goal is to maximize the model's ability to distinguish fields from buildings/water by including enough "hard negatives" and boosting rare features.

## 🛠️ Feature Engineering Strategy

1.  **Context-Rich Tiling (1280x1280)**: 
    *   Scale up from 640 to 1280. This gives the model significantly more spatial context to identify large fields and avoid pixel-level pattern hallucinations.
2.  **Rural Baseline (Hard Negatives)**:
    *   Force inclusion of background tiles containing field textures from both Punjab and Chhattisgarh. 
    *   Ratio: **1.0x background inclusion** (1 negative for every 1 positive tile) to ensure the model learns "empty" textures.
3.  **Rare Class Injection (Pre-Kaggle Oversampling)**:
    *   Instead of just repeating files in a zip, we will explicitly balance the file list in the `data.yaml` or a dedicated manifest.
4.  **Domain Balancing**:
    *   Ensure an equal (or weighted) representation of villages from different states to prevent domain bias.

## 📝 Proposed Changes

### [src/smart_processor.py](file:///Users/ram/Desktop/AI-Powered Feature Extraction System/src/smart_processor.py)
#### [MODIFY] Update for V3 Feature Extraction
*   Hardcode or default `--tile_size` to `1280`.
*   Ensure `neg_ratio` is high (`0.5` or `1.0`) to capture the "what not to do" field textures.
*   Add a **Class Summary Generator** that outputs `data/dataset_v3_manifest.json` after processing a village.

### [src/package_datasets.py](file:///Users/ram/Desktop/AI-Powered Feature Extraction System/src/package_datasets.py)
#### [MODIFY] Balanced Packaging Logic
*   Implement a **Global Aggregator**: Collect stats from all processed villages before zipping.
*   **Virtual Balancing**: Ensure rare classes are represented at least 15% in the final tile distribution.

### [NEW] Dataset Review Tool (`src/review_v3_dataset.py`)
#### [NEW] Feature Diagnostic & Stat Report
*   Generate a markdown/JSON report showing:
    *   Total Tiles (Positives vs. Negatives).
    *   Class Histograms.
    *   Sample visualization of "Hard Negatives" (tiles with no objects but complex textures).

## 🚀 Execution Workflow

1.  **Refine Smart Processor**: Finalize the 1280px logic and negative sampling.
2.  **Execute Preparation**: Run the processor on the raw village data (Punjab + Chhattisgarh).
3.  **Feature Diagnostic**: Generate the Review Report for your approval.
4.  **Final Packaging**: Create the Kaggle-ready ZIP segments once the stats are approved.

## ❓ Open Questions
*   Do you have a specific list of villages from **Punjab** that are currently failing? I can set a higher `neg_ratio` for those specific villages to capture more field patterns.
*   Would you like the 1280 tiles to be **downsampled to 640** before upload (saves space) or kept at full **1280** (better for training)?
