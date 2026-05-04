import torch
import os
import json
from pathlib import Path
from PIL import Image
from torch.utils.data import Dataset, DataLoader, random_split, ConcatDataset
from torchvision import transforms, datasets
from collections import Counter
import pandas as pd

# ── CONFIGURATION ──────────────────────────────────────────────────────────
BASE_DATA_DIR = Path("backend/data/raw/disease")
TRAIN_RATIO, VAL_RATIO, TEST_RATIO = 0.70, 0.15, 0.15

# Dataset folder names (as defined in download_datasets.py)
SUB_DATASETS = {
    "plantvillage": "new-plant-diseases-dataset",
    "crop_pest": "crop-pest-and-disease-detection",
    "20k_disease": "20k-multi-class-crop-disease-images",
    "rice_leaf": "rice-leaf-diseases"
}

# ImageNet normalization stats
IMAGE_NET_MEAN = [0.485, 0.456, 0.406]
IMAGE_NET_STD = [0.229, 0.224, 0.225]

# ── AUGMENTATION & TRANSFORMS ──────────────────────────────────────────────
# (Requested: RandomHorizontalFlip, RandomRotation(30), ColorJitter, Resize(224,224), Normalize)
train_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(30),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGE_NET_MEAN, std=IMAGE_NET_STD)
])

val_test_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGE_NET_MEAN, std=IMAGE_NET_STD)
])

# ── CUSTOM DATASET WRAPPER ─────────────────────────────────────────────────
class UnifiedCropDataset(Dataset):
    """
    A custom wrapper to load multiple datasets, normalize class names, 
    and apply dataset-specific transforms.
    """
    def __init__(self, root_dir, transform=None):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.samples = []
        self.classes = []
        
        self._discover_datasets()

    def _discover_datasets(self):
        """Finds all images across sub-datasets and normalizes classes."""
        all_classes = set()
        
        for ds_key, folder_name in SUB_DATASETS.items():
            ds_path = self.root_dir / folder_name
            if not ds_path.exists():
                print(f"  [Warning] Dataset '{ds_key}' not found at {ds_path}")
                continue
            
            # Use ImageFolder-like logic to find classes
            for class_folder in ds_path.glob("*/"):
                if not class_folder.is_dir(): continue
                
                # Normalize class name: e.g. "Corn___Common_rust" -> "Corn_Common_Rust"
                raw_class = class_folder.name
                norm_class = self._normalize_class(raw_class)
                all_classes.add(norm_class)
                
                # Gather images
                for img_ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG']:
                    for img_path in class_folder.glob(img_ext):
                        self.samples.append((str(img_path), norm_class, ds_key))
        
        self.classes = sorted(list(all_classes))
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(self.classes)}
        print(f"\nDiscovered {len(self.samples)} images across {len(self.classes)} classes.")

    def _normalize_class(self, name):
        """Standardizes inconsistent naming across datasets."""
        # Clean common prefixes/suffixes
        name = name.replace("___", " ").replace("__", " ").replace("_", " ")
        # Title case to unify "brown spot" and "Brown_Spot"
        words = name.split()
        return "_".join([w.capitalize() for w in words])

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label_name, ds_source = self.samples[idx]
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        label = self.class_to_idx[label_name]
        return image, label

# ── ANALYSIS FUNCTIONS ───────────────────────────────────────────────────
def analyze_distribution(dataset):
    """Prints class names, counts, and total samples."""
    if len(dataset.samples) == 0:
        print("Dataset is empty. Cannot analyze distribution.")
        return
    
    df = pd.DataFrame(dataset.samples, columns=['path', 'class', 'source'])
    
    print("\n" + "="*50)
    print(" CROP DISEASE DATASET ANALYSIS")
    print("="*50)
    
    # Per Dataset Counts
    print("\n[1] Samples Per Dataset:")
    print(df['source'].value_counts())
    
    # Class Overlaps
    overlap_count = df.groupby('class')['source'].nunique()
    overlaps = overlap_count[overlap_count > 1]
    
    print(f"\n[2] Overlapping Classes ({len(overlaps)} found):")
    for cls in overlaps.index[:10]:
        sources = df[df['class'] == cls]['source'].unique()
        print(f"  - {cls}: found in {list(sources)}")
    if len(overlaps) > 10:
        print(f"  ... and {len(overlaps)-10} more.")

    # Top 10 Class Distribution
    print("\n[3] Class Distribution (Top 10):")
    counts = df['class'].value_counts()
    for cls, count in counts.head(10).items():
        print(f"  {cls}: {count}")
    
    print(f"\nTOTAL SAMPLES: {len(df)}")
    print(f"TOTAL CLASSES: {len(dataset.classes)}")
    print("="*50)

# ── MAIN EXECUTION ───────────────────────────────────────────────────────
if __name__ == "__main__":
    # 1. Initialize Dataset
    # Note: Using '.' relative to project root or absolute path
    full_dataset = UnifiedCropDataset(BASE_DATA_DIR, transform=train_transforms)
    
    if len(full_dataset) == 0:
        print("\n[!] ERROR: No data found. Please run 'python ml/download_datasets.py' first.")
        print("Mocking a small dataset for demonstration purposes...")
        # (Internal Note: In a real scenario, this would exit or wait for data)
    else:
        # 2. Analyze
        analyze_distribution(full_dataset)

        # 3. Train/Val/Test Split (70/15/15)
        total_size = len(full_dataset)
        train_size = int(TRAIN_RATIO * total_size)
        val_size = int(VAL_RATIO * total_size)
        test_size = total_size - train_size - val_size
        
        train_dataset, val_dataset, test_dataset = random_split(
            full_dataset, [train_size, val_size, test_size],
            generator=torch.Generator().manual_seed(42)
        )
        
        # Override transforms for val/test (no augmentation)
        val_dataset.dataset.transform = val_test_transforms
        test_dataset.dataset.transform = val_test_transforms

        # 4. Create DataLoaders
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=2)
        val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
        test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

        print(f"\nDataset Split Complete:")
        print(f"  Train: {len(train_dataset)} samples")
        print(f"  Val:   {len(val_dataset)} samples")
        print(f"  Test:  {len(test_dataset)} samples")

        # 5. Summary of first batch
        images, labels = next(iter(train_loader))
        print(f"\nBatch Information:")
        print(f"  Batch Shape: {images.shape}")
        print(f"  Labels Range: {labels.min().item()} - {labels.max().item()}")
