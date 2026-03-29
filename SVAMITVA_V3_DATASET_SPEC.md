# SVAMITVA V3 Dataset Specification & Folder Guide

This document provides a detailed breakdown of the SVAMITVA V3 dataset, mapping raw source ZIPs to specific village imageries and their final packaged output.

---

## 🏗️ 1. Source-to-Village Mapping

| Source ZIP Name | Included Villages / Imagery Files | Format | Link |
| :--- | :--- | :--- | :--- |
| **PB_37458_37774.zip** | 37458_fattu_bhila_ortho, 37774_bagga_ortho | TIF | [Link](https://svamitva.nic.in/DownloadPDF/TifFile/PB_37458_37774.zip) |
| **CG_450163.zip** | Samlur, Siyanar, Kutulnar, Binjam, Jhodiyawadam | TIF | [Link](https://svamitva.nic.in/DownloadPDF/TifFile/CG_450163.zip) |
| **Training_dataSet_2.zip**| Badetumnar, Bangapal, Chhotetumar, Mofalnar | TIF | [Link](https://svamitva.nic.in/DownloadPDF/TifFile/CG_Training_dataSet_2.zip) |
| **Training_dataSet_2.zip**| Kutru, Aaklanka (BigTIFF version) | TIF | [Link](https://svamitva.nic.in/DownloadPDF/TifFile/CG_Training_dataSet_2.zip) |
| **Training_dataSet_3.zip**| Murdanda, Awapalli, Chintakonta | TIF | [Link](https://svamitva.nic.in/DownloadPDF/TifFile/CG_Training_dataSet_3.zip) |
| **Training_dataSet_3.zip**| Nagul, Madase, Ghotpal | TIF | [Link](https://svamitva.nic.in/DownloadPDF/TifFile/CG_Training_dataSet_3.zip) |
| **CG_451189_ecw.zip** | Kutru, Aaklanka (ECW Format) | ECW | [Link](https://svamitva.nic.in/DownloadPDF/TifFile/CG_451189_ecw.zip) |

---

## 📂 2. Extraction & Internal Structure
Inside `data/raw/v3_temp/`, the orchestrator extracts ZIPs into sub-folders.

### Example: Punjab Archive
```text
data/raw/v3_temp/PB_37458_37774/
└── PB_37458_37774/
    ├── 37458_fattu_bhila_ortho_3857.tif  <-- (Village 1)
    └── 37774_bagga ortho_3857.tif        <-- (Village 2)
```

### Example: Chhattisgarh Archive
```text
data/raw/v3_temp/CG_450163/
└── CG_450163/
    └── SAMLUR_450163_SIYANAR_450164_..._ORTHO.tif
```

---

## 📦 3. Final Packaged Output (Kaggle Ready)
Located in `data/tiles/v3_packaged/`. Each village is its own volume to preserve high resolution.

### Package Structure (`V3_VillageName_vol1.zip`)
*   `images/`: 1280x1280 JPG tiles with high-precision feature alignment.
*   `labels/`: YOLO format text files (`class x_center y_center w h`).
*   `data.yaml`: YOLO configuration file with 15 classes (Built-Up, Road, etc.).
*   `V3_VillageName_manifest.json`: Detailed summary of positives, negatives, and shifted tiles.

---

## 🎯 4. Feature Engineering Applied
1.  **Positive Tiling**: 1280px tiles containing buildings/roads. 
2.  **Boundary-Shift Overlap**: Buildings at tile edges are sampled twice with random offsets for edge-case training.
3.  **Hard Negative Mining (HNM)**: 30% ratio of tiles containing agriculture/trees but **zero** buildings to reduce False Positives.
4.  **Label Filtering**: Fragments `< 20px` or `> 80% out of bounds` are automatically filtered out.

---

## 🛠️ 5. Label Schema (15 Classes)
| ID | Class Name | Description |
| :--- | :--- | :--- |
| **0** | Built_Up_Area | Primary village boundary or cluster |
| **1-3** | Building (Perm/Semi/Structure)| Categorized rooftops |
| **4** | Road | Paved or unpaved village paths |
| **5** | Water_Body | Ponds, tanks, and streams |
| **11** | Road_Centre_Line | Vector path markers |
| **13** | Utility_Poly | Substations, pumps, and towers |

---
**Status**: Balanced training set (1,267 Positives) ready for YOLOv8/v10.
