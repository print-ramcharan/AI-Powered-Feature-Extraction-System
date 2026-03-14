"""
Rooftop Image Classifier for SVAMITVA Feature Extraction.
Author: Ram
Role: Train PyTorch EfficientNet to classify roof types (e.g., RCC, Asbestos, Tin, Thatch).

This script handles dataset loading, model training, and exporting weights.
Designed to be run on Kaggle/Colab environments with GPUs.
"""

import os
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def get_data_loaders(data_dir, batch_size=32):
    """Loads dataset and applies augmentations."""
    
    # Standard EfficientNet image size
    img_size = 224
    
    train_transforms = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2), # Augmentation to handle CG/PB terrain diffs
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    val_transforms = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    train_dir = os.path.join(data_dir, 'train')
    val_dir = os.path.join(data_dir, 'val')
    
    train_dataset = datasets.ImageFolder(train_dir, transform=train_transforms)
    val_dataset = datasets.ImageFolder(val_dir, transform=val_transforms)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)
    
    return train_loader, val_loader, train_dataset.classes

def build_model(num_classes, checkpoint_path=None):
    """Builds EfficientNet B0, optionally loading from a checkpoint."""
    # Using v0.15+ PyTorch syntax for weights
    weights = models.EfficientNet_B0_Weights.DEFAULT
    model = models.efficientnet_b0(weights=weights)
    
    # Replace the classifier block
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(in_features, num_classes)
    )

    if checkpoint_path and os.path.exists(checkpoint_path):
        logging.info(f"Loading checkpoint from {checkpoint_path}")
        model.load_state_dict(torch.load(checkpoint_path))
    else:
        # Freeze core layers initially ONLY if no checkpoint (Transfer Learning)
        for param in model.parameters():
            param.requires_grad = False
        # Ensure our new classifier is trainable
        for param in model.classifier.parameters():
            param.requires_grad = True
        
    return model

def train_rooftype_model(data_dir, epochs=10, batch_size=32, checkpoint_path=None, save_path="models/rooftype_last.pt"):
    """Main training loop for rooftop classification with incremental support."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logging.info(f"Using device: {device}")
    
    train_loader, val_loader, classes = get_data_loaders(data_dir, batch_size)
    logging.info(f"Classes found: {classes}")
    
    model = build_model(len(classes), checkpoint_path).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.classifier.parameters(), lr=0.001)
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            
        epoch_loss = running_loss / len(train_loader.dataset)
        logging.info(f"Epoch {epoch+1}/{epochs} - Train Loss: {epoch_loss:.4f}")
        
    # Save Model
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    torch.save(model.state_dict(), save_path)
    logging.info(f"Model saved to {save_path}")
    
    return model

if __name__ == "__main__":
    # Example execution
    # train_rooftype_model(data_dir="../data/roof_crops/")
    pass
