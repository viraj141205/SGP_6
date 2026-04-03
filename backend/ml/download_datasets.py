"""
AgroVision AI - Kaggle Dataset Downloader
Run: python ml/download_datasets.py
Requires: KAGGLE_USERNAME and KAGGLE_KEY in .env or environment
"""
import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent / "data" / "raw"
DISEASE_DIR = BASE_DIR / "disease"
YIELD_DIR = BASE_DIR / "yield"

DISEASE_DATASETS = [
    {
        "name": "PlantVillage",
        "slug": "vipoooool/new-plant-diseases-dataset",
        "description": "54,306 images, 38 classes — Primary disease dataset"
    },
    {
        "name": "Crop Pest and Disease Detection",
        "slug": "nirmalsankalana/crop-pest-and-disease-detection",
        "description": "20,000+ real-world field images"
    },
    {
        "name": "20K Multi-Class Crop Disease",
        "slug": "jawadali1045/20k-multi-class-crop-disease-images",
        "description": "Extra diversity and coverage"
    },
    {
        "name": "Rice Leaf Diseases",
        "slug": "vbookshelf/rice-leaf-diseases",
        "description": "BrownSpot, Hispa, LeafBlast (critical for South Asia)"
    },
    {
        "name": "Five Crop Diseases",
        "slug": "shubham2703/five-crop-diseases-dataset",
        "description": "Wheat, Corn, Rice, Sugarcane, Cotton diseases"
    },
]

YIELD_DATASETS = [
    {
        "name": "Crop Yield Prediction (Global)",
        "slug": "patelris/crop-yield-prediction-dataset",
        "description": "28,000+ entries, FAO-sourced global yield data"
    },
    {
        "name": "Crop Yield in Indian States",
        "slug": "akshatgupta7/crop-yield-in-indian-states-dataset",
        "description": "State-wise India yield data"
    },
    {
        "name": "Crop Recommendation (NPK + Climate)",
        "slug": "atharvaingle/crop-recommendation-dataset",
        "description": "N, P, K, temperature, humidity, pH, rainfall"
    },
    {
        "name": "Crop Yield Soil + Weather",
        "slug": "gurudathg/crop-yield-prediction-using-soil-and-weather",
        "description": "Adds soil type as a feature"
    },
]


def check_kaggle_auth():
    username = os.getenv("KAGGLE_USERNAME")
    key = os.getenv("KAGGLE_KEY")

    if not username or not key:
        kaggle_json = os.path.expanduser("~/.kaggle/kaggle.json")
        if not os.path.exists(kaggle_json):
            print("ERROR: Kaggle credentials not found!")
            print("Options:")
            print("  1. Set KAGGLE_USERNAME and KAGGLE_KEY in .env file")
            print("  2. Place kaggle.json in ~/.kaggle/")
            print("  Get your API key at: https://www.kaggle.com/account")
            return False
    else:
        os.environ["KAGGLE_USERNAME"] = username
        os.environ["KAGGLE_KEY"] = key
    return True


def download_dataset(slug: str, dest_dir: Path, name: str) -> bool:
    dest_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n  Downloading: {name}")
    print(f"  Dataset: {slug}")
    print(f"  Destination: {dest_dir}")

    try:
        result = subprocess.run(
            ["kaggle", "datasets", "download", "-d", slug, "-p", str(dest_dir), "--unzip"],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode == 0:
            print(f"  ✓ Successfully downloaded {name}")
            return True
        else:
            print(f"  ✗ Failed: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  ✗ Timeout downloading {name}")
        return False
    except FileNotFoundError:
        print("  ✗ 'kaggle' command not found. Install it: pip install kaggle")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def download_all():
    print("=" * 60)
    print("AgroVision AI — Kaggle Dataset Downloader")
    print("=" * 60)

    if not check_kaggle_auth():
        sys.exit(1)

    print("\n[1/2] Downloading Disease Detection Datasets...")
    disease_results = []
    for ds in DISEASE_DATASETS:
        dest = DISEASE_DIR / ds["slug"].split("/")[-1]
        ok = download_dataset(ds["slug"], dest, ds["name"])
        disease_results.append((ds["name"], ok))

    print("\n[2/2] Downloading Yield Prediction Datasets...")
    yield_results = []
    for ds in YIELD_DATASETS:
        dest = YIELD_DIR / ds["slug"].split("/")[-1]
        ok = download_dataset(ds["slug"], dest, ds["name"])
        yield_results.append((ds["name"], ok))

    print("\n" + "=" * 60)
    print("DOWNLOAD SUMMARY")
    print("=" * 60)
    print("\nDisease Datasets:")
    for name, ok in disease_results:
        status = "✓" if ok else "✗"
        print(f"  {status} {name}")

    print("\nYield Datasets:")
    for name, ok in yield_results:
        status = "✓" if ok else "✗"
        print(f"  {status} {name}")

    total = len(disease_results) + len(yield_results)
    success = sum(1 for _, ok in disease_results + yield_results if ok)
    print(f"\nCompleted: {success}/{total} datasets downloaded")

    if success == 0:
        print("\nNOTE: No datasets downloaded. The app will run in DEMO MODE.")
        print("Demo mode uses realistic synthetic data for testing.")
    elif success < total:
        print("\nNOTE: Some datasets missing. App will use demo mode for missing data.")

    print("\nNext steps:")
    print("  python ml/data_pipeline.py   # Process downloaded data")
    print("  python ml/train_disease_model.py  # Train disease model")
    print("  python ml/train_yield_model.py    # Train yield model")


if __name__ == "__main__":
    download_all()
