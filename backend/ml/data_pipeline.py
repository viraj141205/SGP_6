"""
AgroVision AI — Data Pipeline
Processes raw downloaded datasets into a unified format for model training.
Run: python ml/data_pipeline.py
"""
import os
import json
import hashlib
import shutil
import pickle
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

BASE_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = BASE_DIR / "raw"
RAW_DISEASE_DIR = RAW_DIR  # datasets are directly under raw/
RAW_YIELD_DIR = RAW_DIR
PROC_DISEASE_DIR = BASE_DIR / "processed" / "disease"
PROC_YIELD_DIR = BASE_DIR / "processed" / "yield"
SAVED_MODELS_DIR = Path(__file__).parent / "saved_models"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def get_image_hash(filepath: Path) -> str:
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def _find_class_directories(root: Path) -> list:
    """Walk raw dataset and find leaf dirs containing images."""
    results = []
    skip_names = {"train", "valid", "test", "validation", "raw", "disease", "images"}
    for dirpath, dirnames, filenames in os.walk(root):
        has_images = any(Path(f).suffix.lower() in IMAGE_EXTENSIONS for f in filenames)
        if has_images:
            class_name = Path(dirpath).name
            if class_name.lower() in skip_names:
                continue
            results.append((class_name, Path(dirpath)))
    return results


def process_disease_data():
    print("\n" + "=" * 60)
    print("STEP 1: Processing Disease Detection Data")
    print("=" * 60)
    PROC_DISEASE_DIR.mkdir(parents=True, exist_ok=True)

    # Extract zips in disease-related directories
    for subdir in ["plantvillage", "20k_disease", "crop_pest", "rice_leaf", "smart_farming"]:
        target = RAW_DIR / subdir
        if not target.exists():
            continue
        for zip_file in target.rglob("*.zip"):
            print(f"  Extracting {zip_file.name}...")
            try:
                with zipfile.ZipFile(zip_file, "r") as z:
                    z.extractall(zip_file.parent)
            except Exception as e:
                print(f"  Warning: Could not extract {zip_file.name}: {e}")

    # Find PlantVillage train directory (primary dataset)
    plantvillage_train = None
    plantvillage_valid = None
    for candidate in [
        RAW_DIR / "plantvillage" / "New Plant Diseases Dataset(Augmented)" / "New Plant Diseases Dataset(Augmented)" / "train",
        RAW_DIR / "plantvillage" / "New Plant Diseases Dataset(Augmented)" / "train",
        RAW_DIR / "plantvillage" / "train",
    ]:
        if candidate.exists():
            plantvillage_train = candidate
            break
    for candidate in [
        RAW_DIR / "plantvillage" / "New Plant Diseases Dataset(Augmented)" / "New Plant Diseases Dataset(Augmented)" / "valid",
        RAW_DIR / "plantvillage" / "New Plant Diseases Dataset(Augmented)" / "valid",
        RAW_DIR / "plantvillage" / "valid",
    ]:
        if candidate.exists():
            plantvillage_valid = candidate
            break

    if plantvillage_train:
        print(f"  Found PlantVillage train: {plantvillage_train}")
        all_class_dirs = _find_class_directories(plantvillage_train)
    else:
        print("  PlantVillage not found. Scanning all raw directories...")
        all_class_dirs = _find_class_directories(RAW_DIR)

    if not all_class_dirs:
        print("  No disease images found. Run ml/download_datasets.py first.")
        return []

    # Gather images with deduplication
    seen_hashes = set()
    class_images = {}
    skipped_dupes = 0

    for class_name, dir_path in all_class_dirs:
        if class_name not in class_images:
            class_images[class_name] = []
        for img_path in dir_path.iterdir():
            if img_path.suffix.lower() not in IMAGE_EXTENSIONS or not img_path.is_file():
                continue
            img_hash = get_image_hash(img_path)
            if img_hash in seen_hashes:
                skipped_dupes += 1
                continue
            seen_hashes.add(img_hash)
            class_images[class_name].append(img_path)

    class_images = {k: v for k, v in class_images.items() if len(v) > 0}
    total_images = sum(len(v) for v in class_images.values())
    print(f"\n  Found {len(class_images)} classes, {total_images} unique images")
    print(f"  Skipped {skipped_dupes} duplicates")

    # Copy to processed directory
    for class_name, images in class_images.items():
        class_dir = PROC_DISEASE_DIR / class_name
        class_dir.mkdir(parents=True, exist_ok=True)
        for img_path in images:
            dest = class_dir / img_path.name
            if not dest.exists():
                shutil.copy2(img_path, dest)

    class_names = sorted(class_images.keys())

    # Save class names
    SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    with open(SAVED_MODELS_DIR / "class_names.json", "w") as f:
        json.dump(class_names, f, indent=2)

    # Save dataset paths for test evaluation
    if plantvillage_valid:
        with open(SAVED_MODELS_DIR / "dataset_paths.json", "w") as f:
            json.dump({
                "plantvillage_train": str(plantvillage_train),
                "plantvillage_valid": str(plantvillage_valid),
            }, f, indent=2)

    print(f"\n  Dataset Summary:")
    for cls in class_names:
        print(f"    {cls}: {len(class_images[cls])} images")
    print(f"\n  Total: {total_images} images across {len(class_names)} classes")
    return class_names


def process_yield_data():
    print("\n" + "=" * 60)
    print("STEP 2: Processing Yield Prediction Data")
    print("=" * 60)
    PROC_YIELD_DIR.mkdir(parents=True, exist_ok=True)

    # Only scan yield-specific directories
    yield_dirs = [RAW_DIR / d for d in ["yield_global", "yield_india"] if (RAW_DIR / d).exists()]

    for ydir in yield_dirs:
        for zip_file in ydir.rglob("*.zip"):
            print(f"  Extracting {zip_file.name}...")
            try:
                with zipfile.ZipFile(zip_file, "r") as z:
                    z.extractall(zip_file.parent)
            except Exception as e:
                print(f"  Warning: Could not extract {zip_file.name}: {e}")

    dfs = []
    csv_files = []
    for ydir in yield_dirs:
        csv_files.extend(list(ydir.rglob("*.csv")))
    if not csv_files:
        print("  No yield CSV files found. Generating synthetic data...")
        dfs.append(generate_synthetic_yield_data())
    else:
        for csv_path in csv_files:
            try:
                df = pd.read_csv(csv_path)
                df.columns = [c.strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]
                print(f"  Loaded {csv_path.name}: {len(df)} rows")
                dfs.append(df)
            except Exception as e:
                print(f"  Warning: Could not load {csv_path.name}: {e}")
    if not dfs:
        dfs = [generate_synthetic_yield_data()]

    col_map = {
        "area_(1000_ha)": "area_hectares", "area": "area_hectares",
        "production_(1000_tonnes)": "production", "yield_(kg_per_ha)": "yield_per_hectare",
        "yield_quintals_per_hectare": "yield_per_hectare", "crop_production": "production",
        "annual_rainfall": "rainfall", "avg_temp": "temperature", "temp": "temperature",
        "n": "nitrogen", "p": "phosphorus", "k": "potassium", "ph": "soil_ph",
        "label": "crop_type", "crop": "crop_type", "state": "region",
        "state_name": "region", "country": "region",
    }
    normalized = [df.rename(columns=col_map) for df in dfs]
    combined = pd.concat(normalized, ignore_index=True)

    for col in ["nitrogen", "phosphorus", "potassium", "soil_ph", "temperature", "rainfall", "humidity"]:
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce")
            if "crop_type" in combined.columns:
                combined[col] = combined.groupby("crop_type")[col].transform(lambda x: x.fillna(x.median()))
            combined[col] = combined[col].fillna(combined[col].median())

    if "yield_per_hectare" not in combined.columns:
        if "production" in combined.columns and "area_hectares" in combined.columns:
            combined["yield_per_hectare"] = combined["production"] / (combined["area_hectares"] + 0.001)
        else:
            combined["yield_per_hectare"] = np.random.uniform(5, 200, len(combined))

    combined["yield_per_hectare"] = pd.to_numeric(combined["yield_per_hectare"], errors="coerce")
    combined = combined.dropna(subset=["yield_per_hectare"])

    Q1 = combined["yield_per_hectare"].quantile(0.05)
    Q3 = combined["yield_per_hectare"].quantile(0.95)
    IQR = Q3 - Q1
    before = len(combined)
    combined = combined[(combined["yield_per_hectare"] >= Q1 - 3 * IQR) & (combined["yield_per_hectare"] <= Q3 + 3 * IQR)]
    print(f"  Removed {before - len(combined)} outliers")

    defaults = {"crop_type": "Unknown", "region": "Unknown", "season": "Kharif", "soil_type": "Loam",
                "area_hectares": 1.0, "nitrogen": 60.0, "phosphorus": 60.0, "potassium": 60.0,
                "soil_ph": 6.5, "rainfall": 800.0, "temperature": 25.0, "humidity": 65.0}
    for col, val in defaults.items():
        if col not in combined.columns:
            combined[col] = val

    combined["npk_ratio"] = combined["nitrogen"] / (combined["phosphorus"] + combined["potassium"] + 1)
    combined["temp_rainfall_interaction"] = combined["temperature"] * combined["rainfall"]

    label_encoders = {}
    for col in ["crop_type", "region", "season", "soil_type"]:
        le = LabelEncoder()
        combined[f"{col}_encoded"] = le.fit_transform(combined[col].astype(str))
        label_encoders[col] = le

    feature_columns = [
        "crop_type_encoded", "region_encoded", "season_encoded", "area_hectares",
        "soil_type_encoded", "soil_ph", "nitrogen", "phosphorus", "potassium",
        "rainfall", "temperature", "humidity", "npk_ratio", "temp_rainfall_interaction"
    ]
    feature_columns = [c for c in feature_columns if c in combined.columns]
    X = combined[feature_columns].values
    y = combined["yield_per_hectare"].values

    scaler = StandardScaler()
    scaler.fit_transform(X)

    output_csv = PROC_YIELD_DIR / "combined_yield.csv"
    combined.to_csv(output_csv, index=False)
    SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    with open(SAVED_MODELS_DIR / "label_encoders.pkl", "wb") as f:
        pickle.dump(label_encoders, f)
    with open(SAVED_MODELS_DIR / "scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    with open(SAVED_MODELS_DIR / "feature_columns.json", "w") as f:
        json.dump(feature_columns, f, indent=2)

    print(f"\n  Final dataset: {len(combined)} rows, {len(feature_columns)} features")
    print(f"  Saved to: {output_csv}")
    return combined, feature_columns


def generate_synthetic_yield_data(n_samples=10000) -> pd.DataFrame:
    """Generate realistic synthetic agricultural yield data."""
    np.random.seed(42)
    crops = ["Rice", "Wheat", "Maize", "Cotton", "Sugarcane", "Soybean", "Tomato",
             "Potato", "Onion", "Mustard", "Groundnut", "Sunflower", "Bajra", "Jowar"]
    regions = ["Punjab", "Haryana", "UP", "Maharashtra", "MP", "Karnataka", "TamilNadu",
                "Gujarat", "Rajasthan", "Bihar"]
    seasons = ["Kharif", "Rabi", "Zaid"]
    soil_types = ["Loam", "Clay", "Sandy", "Silty", "Black", "Red"]
    crop_yield_base = {
        "Rice": 22, "Wheat": 32, "Maize": 35, "Cotton": 15, "Sugarcane": 350,
        "Soybean": 18, "Tomato": 200, "Potato": 180, "Onion": 120, "Mustard": 10,
        "Groundnut": 14, "Sunflower": 12, "Bajra": 18, "Jowar": 20
    }
    crop_choices = np.random.choice(crops, n_samples)
    data = {
        "crop_type": crop_choices, "region": np.random.choice(regions, n_samples),
        "season": np.random.choice(seasons, n_samples),
        "area_hectares": np.random.uniform(0.5, 20, n_samples),
        "soil_type": np.random.choice(soil_types, n_samples),
        "soil_ph": np.random.uniform(5.0, 8.5, n_samples),
        "nitrogen": np.random.uniform(20, 140, n_samples),
        "phosphorus": np.random.uniform(10, 100, n_samples),
        "potassium": np.random.uniform(10, 120, n_samples),
        "rainfall": np.random.uniform(200, 2500, n_samples),
        "temperature": np.random.uniform(10, 45, n_samples),
        "humidity": np.random.uniform(30, 95, n_samples),
    }
    base_yields = np.array([crop_yield_base.get(c, 25) for c in crop_choices])
    noise = np.random.normal(0, 0.15, n_samples)
    data["yield_per_hectare"] = base_yields * (1 + noise) * (
        0.7 + 0.3 * (data["nitrogen"] / 140) + 0.2 * (data["rainfall"] / 2500) +
        0.1 * np.where(np.array(data["soil_ph"]) > 7.5, 0.8, 1.0)
    )
    print(f"  Generated {n_samples} synthetic samples")
    return pd.DataFrame(data)


if __name__ == "__main__":
    print("AgroVision AI — Data Pipeline")
    print("=" * 60)
    class_names = process_disease_data()
    process_yield_data()
    print("\n" + "=" * 60)
    print("DATA PIPELINE COMPLETE")
    if class_names:
        print(f"  Disease classes: {len(class_names)}")
    print("\nNext: python ml/train_disease_model.py")
