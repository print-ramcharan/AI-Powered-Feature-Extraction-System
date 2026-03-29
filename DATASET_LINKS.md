# SVAMITVA V3 Dataset Links & Status

This document tracks the official source links and the processing status for the SVAMITVA V3 aerial imagery dataset.

## 🗺️ Live Processing Status (Final Summary)

| Dataset Volume | Village / Imagery | Status | Positives | Total Tiles |
| :--- | :--- | :--- | :--- | :--- |
| **Chhattisgarh (CG_450163)** | Samlur & Siyanar | ✅ **COMPLETED** | 116 | 826 |
| **Punjab (PB_37458_37774)** | 37458 (Fattu Bhila) | ✅ **COMPLETED** | 184 | 912 |
| **Punjab (PB_37458_37774)** | 37774 (Bagga) | ✅ **COMPLETED** | 224 | 1114 |
| **DataSet 2** | Badetumnar, Bangapal, etc. | ✅ **COMPLETED** | 266 | 1771 |
| **DataSet 2** | **Kutru / Aaklanka** | ❌ **ERROR** | - | - |
| **DataSet 3** | Murdanda, Awapalli | ✅ **COMPLETED** | 356 | 2213 |
| **DataSet 3** | Nagul, Madase, etc. | ✅ **COMPLETED** | 121 | 842 |
| **CG_451189_ecw** | Aaklanka & Kutru | ❌ **FAILED** | - | - |

> [!NOTE]
> **Aaklanka & Kutru Notice**: This specific village imagery (451189/451163) appears to be either corrupted on the source server or requires a specialized BigTIFF driver that handles extremely large non-standard directories. We have skipped it for now to avoid blocking the pipeline. All other volumes are **100% processed and packaged**.

## 📂 Official SHP Resources
- [Chhattisgarh Global SHPs](https://svamitva.nic.in/DownloadPDF/TifFile/CG_shp-file.zip)
- [Punjab Global SHPs](https://svamitva.nic.in/DownloadPDF/TifFile/PB_training_dataSet_shp_file.zip)

---

### 🚀 Usage in Pipeline
The `src/v3_dataset_orchestrator.py` script successfully:
1.  Downloaded all ZIP files and managed multi-village extraction.
2.  Auto-aligned local imagery with regional shapefiles.
3.  Generated **1,267 Positive Feature Tiles** across all successful villages.
4.  Packaged everything into Kaggle-ready volumes in `data/tiles/v3_packaged/`.
