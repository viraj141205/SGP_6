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
RAW_DISEASE_DIR = BASE_DIR / "raw" / "disease"
RAW_YIELD_DIR = BASE_DIR / "raw" / "yield"
PROC_DISEASE_DIR = BASE_DIR / "processed" / "disease"
PROC_YIELD_DIR = BASE_DIR / "processed" / "yield"
SAVED_MODELS_DIR = Path(__file__).parent / "saved_models"


# ── LABEL NORMALIZATION ────────────────────────────────────────────────
def normalize_class_name(raw_name: str) -> str:
    """Convert any dataset format to 'Crop - Disease Name'."""
    name = raw_name.replace("___", " - ").replace("__", " - ").replace("_", " ")
    name = " ".join(word.capitalize() for word in name.split())
    return name


# ── IMAGE DEDUPLICATION ────────────────────────────────────────────────
def get_image_hash(filepath: Path) -> str:
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def process_disease_data():
    print("\n" + "=" * 60)
    print("STEP 1: Processing Disease Detection Data")
    print("=" * 60)

    PROC_DISEASE_DIR.mkdir(parents=True, exist_ok=True)

    # Extract any zip files
    for zip_file in RAW_DISEASE_DIR.rglob("*.zip"):
        print(f"  Extracting {zip_file.name}...")
        with zipfile.ZipFile(zip_file, "r") as z:
            z.extractall(zip_file.parent)

    # Gather all image files and their class labels
    seen_hashes = set()
    class_images = {}
    skipped_dupes = 0

    for img_path in RAW_DISEASE_DIR.rglob("*"):
        if img_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        # Parent folder name = class label
        raw_class = img_path.parent.name
        if not raw_class or raw_class == img_path.parent.parent.name:
            continue
        normalized = normalize_class_name(raw_class)

        img_hash = get_image_hash(img_path)
        if img_hash in seen_hashes:
            skipped_dupes += 1
            continue
        seen_hashes.add(img_hash)

        if normalized not in class_images:
            class_images[normalized] = []
        class_images[normalized].append(img_path)

    if not class_images:
        print("  No disease images found in raw directory.")
        print("  Run ml/download_datasets.py first to download data.")
        print("  Skipping disease data processing.")
        return []

    print(f"\n  Found {len(class_images)} classes, {sum(len(v) for v in class_images.values())} unique images")
    print(f"  Skipped {skipped_dupes} duplicate images")

    # Copy to processed directory with unified structure
    for class_name, images in class_images.items():
        class_dir = PROC_DISEASE_DIR / class_name
        class_dir.mkdir(parents=True, exist_ok=True)
        for img_path in images:
            dest = class_dir / img_path.name
            if not dest.exists():
                shutil.copy2(img_path, dest)

    class_names = sorted(class_images.keys())

    # Save class names
    class_names_path = PROC_DISEASE_DIR / "class_names.json"
    with open(class_names_path, "w") as f:
        json.dump(class_names, f, indent=2)
    print(f"  Saved {len(class_names)} class names to {class_names_path}")

    # Dataset summary
    print("\n  Dataset Summary:")
    total = 0
    for cls in class_names[:10]:
        count = len(class_images[cls])
        total += count
        print(f"    {cls}: {count} images")
    if len(class_names) > 10:
        rest = sum(len(class_images[c]) for c in class_names[10:])
        total += rest
        print(f"    ... {len(class_names) - 10} more classes, {rest} more images")
    print(f"\n  Total: {total} images across {len(class_names)} classes")
    return class_names


def process_yield_data():
    print("\n" + "=" * 60)
    print("STEP 2: Processing Yield Prediction Data")
    print("=" * 60)

    PROC_YIELD_DIR.mkdir(parents=True, exist_ok=True)

    # Extract zips
    for zip_file in RAW_YIELD_DIR.rglob("*.zip"):
        print(f"  Extracting {zip_file.name}...")
        with zipfile.ZipFile(zip_file, "r") as z:
            z.extractall(zip_file.parent)

    # Load all CSV files
    dfs = []
    csv_files = list(RAW_YIELD_DIR.rglob("*.csv"))

    if not csv_files:
        print("  No yield CSV files found. Generating synthetic training data...")
        df = generate_synthetic_yield_data()
        dfs.append(df)
    else:
        for csv_path in csv_files:
            try:
                df = pd.read_csv(csv_path)
                df.columns = [c.strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]
                print(f"  Loaded {csv_path.name}: {len(df)} rows, columns: {list(df.columns)}")
                dfs.append(df)
            except Exception as e:
                print(f"  Warning: Could not load {csv_path.name}: {e}")

    if not dfs:
        print("  No data found at all. Generating synthetic data.")
        dfs = [generate_synthetic_yield_data()]

    # Normalize column names across datasets
    column_mappings = {
        "area_(1000_ha)": "area_hectares",
        "area": "area_hectares",
        "production_(1000_tonnes)": "production",
        "yield_(kg_per_ha)": "yield_per_hectare",
        "yield_quintals_per_hectare": "yield_per_hectare",
        "crop_production": "production",
        "annual_rainfall": "rainfall",
        "avg_temp": "temperature",
        "temp": "temperature",
        "n": "nitrogen",
        "p": "phosphorus",
        "k": "potassium",
        "ph": "soil_ph",
        "label": "crop_type",
        "crop": "crop_type",
        "state": "region",
        "state_name": "region",
        "country": "region",
    }

    normalized = []
    for df in dfs:
        df = df.rename(columns=column_mappings)
        normalized.append(df)

    # Combine all DataFrames
    combined = pd.concat(normalized, ignore_index=True)

    # Fill missing value columns
    for col in ["nitrogen", "phosphorus", "potassium", "soil_ph", "temperature", "rainfall", "humidity"]:
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce")
            if "crop_type" in combined.columns:
                combined[col] = combined.groupby("crop_type")[col].transform(
                    lambda x: x.fillna(x.median())
                )
            combined[col] = combined[col].fillna(combined[col].median())

    # Ensure target variable exists
    if "yield_per_hectare" not in combined.columns:
        if "production" in combined.columns and "area_hectares" in combined.columns:
            combined["yield_per_hectare"] = combined["production"] / (combined["area_hectares"] + 0.001)
        else:
            print("  Creating synthetic yield_per_hectare from available data...")
            combined["yield_per_hectare"] = np.random.uniform(5, 200, len(combined))

    combined["yield_per_hectare"] = pd.to_numeric(combined["yield_per_hectare"], errors="coerce")
    combined = combined.dropna(subset=["yield_per_hectare"])

    # Remove outliers via IQR
    Q1 = combined["yield_per_hectare"].quantile(0.05)
    Q3 = combined["yield_per_hectare"].quantile(0.95)
    IQR = Q3 - Q1
    before = len(combined)
    combined = combined[
        (combined["yield_per_hectare"] >= Q1 - 3 * IQR) &
        (combined["yield_per_hectare"] <= Q3 + 3 * IQR)
    ]
    print(f"  Removed {before - len(combined)} outliers via IQR method")

    # Fill remaining categoricals
    if "crop_type" not in combined.columns:
        combined["crop_type"] = "Unknown"
    if "region" not in combined.columns:
        combined["region"] = "Unknown"
    if "season" not in combined.columns:
        combined["season"] = "Kharif"
    if "soil_type" not in combined.columns:
        combined["soil_type"] = "Loam"
    if "area_hectares" not in combined.columns:
        combined["area_hectares"] = 1.0
    for col in ["nitrogen", "phosphorus", "potassium"]:
        if col not in combined.columns:
            combined[col] = 60.0
    if "soil_ph" not in combined.columns:
        combined["soil_ph"] = 6.5
    if "rainfall" not in combined.columns:
        combined["rainfall"] = 800.0
    if "temperature" not in combined.columns:
        combined["temperature"] = 25.0
    if "humidity" not in combined.columns:
        combined["humidity"] = 65.0

    # Feature engineering
    combined["npk_ratio"] = combined["nitrogen"] / (combined["phosphorus"] + combined["potassium"] + 1)
    combined["temp_rainfall_interaction"] = combined["temperature"] * combined["rainfall"]

    # Encode categoricals
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
    X_scaled = scaler.fit_transform(X)

    # Save processed data
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
    print(f"  Target stats — Mean: {y.mean():.2f}, Std: {y.std():.2f}, Min: {y.min():.2f}, Max: {y.max():.2f}")
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
        "crop_type": crop_choices,
        "region": np.random.choice(regions, n_samples),
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
        0.7 + 0.3 * (data["nitrogen"] / 140) +
        0.2 * (data["rainfall"] / 2500) +
        0.1 * np.where(np.array(data["soil_ph"]) > 7.5, 0.8, 1.0)
    )
    print(f"  Generated {n_samples} synthetic training samples")
    return pd.DataFrame(data)


def main():
    print("AgroVision AI — Data Pipeline")
    print("=" * 60)

    # Processing Disease Data
    class_names = process_disease_data()

    # Processing Yield Data
    result = process_yield_data()

    print("\n" + "=" * 60)
    print("DATA PIPELINE COMPLETE")
    print("=" * 60)
    if class_names:
        print(f"  Disease classes: {len(class_names)}")
    print("\nNext steps:")
    print("  python ml/train_disease_model.py")
    print("  python ml/train_yield_model.py")


if __name__ == "__main__":
    main()
