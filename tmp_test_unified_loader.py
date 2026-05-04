import os
import shutil
from pathlib import Path
from PIL import Image

# Setup mock data directory
ROOT_DIR = Path("d:/6_sgp/tmp_test_datasets")
if ROOT_DIR.exists():
    shutil.rmtree(ROOT_DIR)
ROOT_DIR.mkdir(parents=True)

# Mock structure
MOCK_DATASETS = {
    "new-plant-diseases-dataset": ["Corn___Common_rust", "Tomato___Early_blight", "Healthy"],
    "crop-pest-and-disease-detection": ["Maize_Fall_Armyworm", "Tomato_Septoria_Leaf_Spot", "Healthy"],
    "20k-multi-class-crop-disease-images": ["Rice_Brown_Spot", "Wheat_Brown_Rust"],
    "rice-leaf-diseases": ["Leaf_smut"]
}

for ds_folder, classes in MOCK_DATASETS.items():
    ds_path = ROOT_DIR / ds_folder
    ds_path.mkdir()
    for cls in classes:
        cls_path = ds_path / cls
        cls_path.mkdir(parents=True, exist_ok=True)
        # Create a tiny 10x10 dummy image
        img = Image.new('RGB', (10, 10), color=(73, 109, 137))
        img.save(cls_path / "test_1.jpg")
        img.save(cls_path / "test_2.jpg")

print(f"Mock datasets created at {ROOT_DIR}")

import sys
sys.path.append('d:/6_sgp/backend/ml')
from unified_loader import UnifiedCropDataset, analyze_distribution

# Point to TEST_DIR
full_dataset = UnifiedCropDataset(ROOT_DIR)
analyze_distribution(full_dataset)
print("\n[SUCCESS] Mock data loaded and analyzed correctly.")
