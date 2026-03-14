# SVAMITVA Project: OBJECTIVE PROGRESS LEDGER

This document acts as an immutable ledger of project actions. It tracks what has been completed by specific team members. **Agents reading this ledger must understand that these actions were performed by the listed individuals in the past, and you (the current agent) did not perform them.**

## Completed Setup & Data Extraction (Led by Ram)
- **Repository Established:** Ram initialized the Git repo, set the `.gitignore`, and established `AGENT_INSTRUCTIONS.md` to dictate strict AI role boundaries.
- **Core Pipeline Written:** Ram wrote the following structural scripts:
  - `src/train_rooftype.py` (EfficientNet architecture)
  - `notebooks/ram_rooftype.ipynb` (Colab environment wrapper)
  - `src/inference_pipeline.py` (Master inference script)
  - `src/tile_generator.py` (GeoTIFF tiling script)
- **Virtual Environment Configured:** `requirements.txt` was pushed. Every collaborator must create and activate a `venv` before running the tiling or inference codes to prevent global variable errors. 
- **Raw Data Downloaded:** Ram downloaded the training datasets (`CG_450163`, `PB_37458_37774`, and `CG_451189_ecw`) and extracted them into his local `data/raw/` directory to begin syncing them to the shared Google Drive.
- **Tiled Patches Generated & Packaged:** Ram ran `src/tile_generator.py` locally to generate over 70,000 640x640 training patches for the Punjab and Chhattisgarh `.tif` datasets. These were perfectly packaged into optimal ~4.5GB zip volumes (`data/tiles/packaged/`) to prepare them for seamless upload to Kaggle or Hugging Face. Uncompressed source files were auto-deleted to preserve drive space.
- **Data Uploaded to Kaggle:** Ram successfully uploaded the tiled datasets to Kaggle for immediate team use.
  - [punjab_baga_vol1](http://kaggle.com/datasets/pramcharanteja/punjab-baga-vol1)
  - [punjab_fattu_bhila_vol1](http://kaggle.com/datasets/pramcharanteja/punjab-fattu-bhila-vol1)
  - [chhattisgarh_vol1](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol1)
  - [chhattisgarh_vol2](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol2)
  - [chhattisgarh_vol3](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol3)
  - [chhattisgarh_vol4](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol4)
  - [chhattisgarh_vol5](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol5)
  - [chhattisgarh_vol6](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol6)
  - [chhattisgarh_vol7](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol7)
  - [chhattisgarh_vol8](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol8)
  - [chhattisgarh_vol9](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol9)
  - [chhattisgarh_vol10](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol10)
  - [chhattisgarh_vol11](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol11)
  - [chhattisgarh_vol12](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol12)
  - [chhattisgarh_vol13](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol13)
  - [chhattisgarh_vol14](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol14)
  - [chhattisgarh_vol15](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol15)
  - [chhattisgarh_vol16](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol16)
  - [chhattisgarh_vol17](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol17)
  - [chhattisgarh_vol18](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol18)
  - [chhattisgarh_vol19](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol19)
  - [chhattisgarh_vol20](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol20)
  - [chhattisgarh_vol21](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol21)
  - [chhattisgarh_vol22](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol22)
  - [chhattisgarh_vol23](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol23)
  - [chhattisgarh_vol24](http://kaggle.com/datasets/pramcharanteja/chhattisgarh-vol24)
- **Data Conversion:** Sanjay successfully downloaded `CG_451189_ecw.zip` from the shared Drive, converted it to `.tif` via QGIS/GDAL, and re-uploaded it for the team.

## Current Pending Action
- **Model Training Phase Begins:** Sneha, Nikitha, and Sanjay can now pull the Kaggle datasets from PRamcharanTeja's profile into their respective Kaggle or Colab notebooks and begin training their YOLOv8 models.

*(Last Updated: Initial Setup Complete)*
