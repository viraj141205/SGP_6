"""Quick data exploration for yield prediction model design."""
import pandas as pd
import numpy as np
import os

base = os.path.join(os.path.dirname(__file__), "..", "data")

print("=" * 60)
print("DATASET 1: yield_df.csv (Global - Pre-merged)")
print("=" * 60)
df = pd.read_csv(os.path.join(base, "raw", "yield_global", "yield_df.csv"))
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(df.describe())
print(f"\nUnique Items (crops): {df['Item'].nunique()}")
print(f"Items: {df['Item'].unique()}")
print(f"Unique Areas (countries): {df['Area'].nunique()}")
print(f"Year range: {df['Year'].min()} - {df['Year'].max()}")
print(f"Yield range: {df['hg/ha_yield'].min()} - {df['hg/ha_yield'].max()}")
print(f"Missing values:\n{df.isnull().sum()}")

print("\n" + "=" * 60)
print("DATASET 2: crop_yield.csv (India)")
print("=" * 60)
df2 = pd.read_csv(os.path.join(base, "raw", "yield_india", "crop_yield.csv"))
print(f"Shape: {df2.shape}")
print(f"Columns: {list(df2.columns)}")
print(df2.describe())
print(f"\nUnique Crops: {df2['Crop'].nunique()}")
print(f"Crops (first 20): {list(df2['Crop'].unique()[:20])}")
print(f"Unique States: {df2['State'].nunique()}")
print(f"States: {list(df2['State'].unique()[:15])}")
print(f"Seasons: {list(df2['Season'].unique())}")
print(f"Year range: {df2['Crop_Year'].min()} - {df2['Crop_Year'].max()}")
print(f"Missing values:\n{df2.isnull().sum()}")

print("\n" + "=" * 60)
print("CURRENT combined_yield.csv")
print("=" * 60)
df3 = pd.read_csv(os.path.join(base, "processed", "yield", "combined_yield.csv"))
print(f"Shape: {df3.shape}")
print(f"Columns: {list(df3.columns)}")
print(f"Yield stats: mean={df3['yield_per_hectare'].mean():.2f}, std={df3['yield_per_hectare'].std():.2f}")
print(f"Unique crops: {df3['crop_type'].nunique()}")
