import os
from ultralytics import YOLO

def train_v3():
    """
    Kicks off V3 Training for SVAMITVA Project.
    Focus: 
    - 1280 resolution (Mandatory for field/building separation)
    - YOLO11m architecture (Better capacity)
    - Class-weighted balanced loss
    - Heavy augmentation (Mosaic + Copy-Paste)
    """
    
    # Load the Medium-sized YOLO11 model (starting from user's best weights)
    # Using 'models/best (10).pt' as requested
    model_path = "models/best (10).pt"
    if not os.path.exists(model_path):
        print(f"Warning: {model_path} not found. Falling back to yolo11m.pt")
        model_path = "yolo11m.pt"
        
    model = YOLO(model_path)
    
    # Define dataset path (relative to repo root)
    data_yaml = "data/v3_training.yaml"
    
    # Training Parameters
    # imgsz=1280: Higher resolution to see field textures clearly
    # batch=8: (Adjust based on GPU VRAM, 1280 uses more memory)
    # epochs=200: Longer training for rare class convergence
    # cls=1.5: Increase classification loss weight to prioritize feature separation
    # mosaic=1.0: Keep small objects mixed
    # mixup=0.15: Generalization
    # copy_paste=0.4: Force model to see buildings on different backgrounds
    
    results = model.train(
        data=data_yaml,
        epochs=200,
        imgsz=1280,
        batch=8,
        device=0, # Use GPU 0
        project="runs/detect",
        name="svamitva_v3_1280_med",
        optimizer="AdamW",
        lr0=0.01,
        lrf=0.01,
        dropout=0.1,
        val=True,
        save=True,
        exist_ok=True,
        pretrained=True,
        # Augmentations
        mosaic=1.0,
        mixup=0.15,
        copy_paste=0.4,
        scale=0.5,
        fliplr=0.5,
        flipud=0.5,
        # Performance/Logging
        patience=30, # Early stopping
        deterministic=True
    )
    
    print("V3 Training Complete. Model saved in runs/detect/svamitva_v3_1280_med")

if __name__ == "__main__":
    train_v3()
