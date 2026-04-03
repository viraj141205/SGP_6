"""
AgroVision AI — Yield Prediction Ensemble Model Training
Architecture: XGBoost + Deep Neural Network + Random Forest
Run: python ml/train_yield_model.py
"""
import os
import json
import pickle
import sys
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).parent.parent
PROC_YIELD_DIR = BASE_DIR / "data" / "processed" / "yield"
SAVED_MODELS_DIR = Path(__file__).parent / "saved_models"
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    csv_path = PROC_YIELD_DIR / "combined_yield.csv"
    if not csv_path.exists():
        print("  Processed yield data not found. Running data pipeline...")
        sys.path.insert(0, str(Path(__file__).parent))
        from data_pipeline import process_yield_data, generate_synthetic_yield_data
        from sklearn.preprocessing import LabelEncoder, StandardScaler

        df = generate_synthetic_yield_data(10000)
        label_encoders = {}
        for col in ["crop_type", "region", "season", "soil_type"]:
            le = LabelEncoder()
            df[f"{col}_encoded"] = le.fit_transform(df[col].astype(str))
            label_encoders[col] = le
        df["npk_ratio"] = df["nitrogen"] / (df["phosphorus"] + df["potassium"] + 1)
        df["temp_rainfall_interaction"] = df["temperature"] * df["rainfall"]
        scaler = StandardScaler()
        feature_columns = [
            "crop_type_encoded", "region_encoded", "season_encoded", "area_hectares",
            "soil_type_encoded", "soil_ph", "nitrogen", "phosphorus", "potassium",
            "rainfall", "temperature", "humidity", "npk_ratio", "temp_rainfall_interaction"
        ]
        X = scaler.fit_transform(df[feature_columns].values)
        y = df["yield_per_hectare"].values
        with open(SAVED_MODELS_DIR / "label_encoders.pkl", "wb") as f:
            pickle.dump(label_encoders, f)
        with open(SAVED_MODELS_DIR / "scaler.pkl", "wb") as f:
            pickle.dump(scaler, f)
        with open(SAVED_MODELS_DIR / "feature_columns.json", "w") as f:
            json.dump(feature_columns, f)
        return X, y, feature_columns, True

    df = pd.read_csv(csv_path)
    with open(SAVED_MODELS_DIR / "scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    with open(SAVED_MODELS_DIR / "feature_columns.json", "r") as f:
        feature_columns = json.load(f)

    feature_columns = [c for c in feature_columns if c in df.columns]
    X = scaler.transform(df[feature_columns].values)
    y = df["yield_per_hectare"].values
    return X, y, feature_columns, False


def train_xgboost(X_train, y_train, X_val, y_val):
    from xgboost import XGBRegressor
    from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
    import joblib

    print("\n  Training XGBoost Regressor...")
    model = XGBRegressor(
        n_estimators=500, max_depth=7, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8,
        reg_alpha=0.1, reg_lambda=1.0,
        random_state=42, n_jobs=-1,
        early_stopping_rounds=20, eval_metric="rmse"
    )
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=50
    )
    preds = model.predict(X_val)
    r2 = r2_score(y_val, preds)
    rmse = np.sqrt(mean_squared_error(y_val, preds))
    mae = mean_absolute_error(y_val, preds)
    print(f"  XGBoost — R²: {r2:.4f}, RMSE: {rmse:.2f}, MAE: {mae:.2f}")

    joblib.dump(model, SAVED_MODELS_DIR / "xgboost_model.pkl")
    return model, r2


def train_random_forest(X_train, y_train, X_val, y_val):
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
    import joblib

    print("\n  Training Random Forest Regressor...")
    model = RandomForestRegressor(
        n_estimators=300, max_depth=15, min_samples_split=5,
        random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_val)
    r2 = r2_score(y_val, preds)
    rmse = np.sqrt(mean_squared_error(y_val, preds))
    mae = mean_absolute_error(y_val, preds)
    print(f"  RandomForest — R²: {r2:.4f}, RMSE: {rmse:.2f}, MAE: {mae:.2f}")

    joblib.dump(model, SAVED_MODELS_DIR / "rf_model.pkl")
    return model, r2


def build_dnn(input_dim: int):
    import tensorflow as tf

    inputs = tf.keras.Input(shape=(input_dim,))
    x = tf.keras.layers.Dense(256, activation="relu")(inputs)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    x = tf.keras.layers.Dense(128, activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.Dense(64, activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.1)(x)
    x = tf.keras.layers.Dense(32, activation="relu")(x)
    outputs = tf.keras.layers.Dense(1, activation="linear")(x)
    model = tf.keras.Model(inputs, outputs)
    return model


def train_dnn(X_train, y_train, X_val, y_val):
    import tensorflow as tf
    from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

    print("\n  Training Deep Neural Network...")
    lr_schedule = tf.keras.optimizers.schedules.CosineDecay(
        initial_learning_rate=0.001, decay_steps=100 * (len(X_train) // 64)
    )
    model = build_dnn(X_train.shape[1])
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=lr_schedule),
        loss=tf.keras.losses.Huber(),
        metrics=["mae"]
    )
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=100, batch_size=64,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(
                monitor="val_loss", patience=10, restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(factor=0.2, patience=5)
        ],
        verbose=1
    )
    preds = model.predict(X_val, verbose=0).flatten()
    r2 = r2_score(y_val, preds)
    rmse = np.sqrt(mean_squared_error(y_val, preds))
    mae = mean_absolute_error(y_val, preds)
    print(f"  DNN — R²: {r2:.4f}, RMSE: {rmse:.2f}, MAE: {mae:.2f}")

    model.save(str(SAVED_MODELS_DIR / "dnn_yield_model.h5"))
    return model, r2


def train():
    print("=" * 60)
    print("AgroVision AI — Yield Model Training (Ensemble)")
    print("=" * 60)

    print("\n[1/4] Loading data...")
    X, y, feature_columns, is_synthetic = load_data()
    if is_synthetic:
        print("  Using synthetic data (demo mode)")

    from sklearn.model_selection import train_test_split
    X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.15, random_state=42)
    print(f"  Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)} samples")

    print("\n[2/4] Training individual models...")
    xgb_model, xgb_r2 = train_xgboost(X_train, y_train, X_val, y_val)
    rf_model, rf_r2 = train_random_forest(X_train, y_train, X_val, y_val)
    dnn_model, dnn_r2 = train_dnn(X_train, y_train, X_val, y_val)

    print("\n[3/4] Evaluating ensemble on test set...")
    from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

    xgb_preds = xgb_model.predict(X_test)
    rf_preds = rf_model.predict(X_test)
    dnn_preds = dnn_model.predict(X_test, verbose=0).flatten()

    ensemble_preds = 0.45 * xgb_preds + 0.35 * dnn_preds + 0.20 * rf_preds

    r2 = r2_score(y_test, ensemble_preds)
    rmse = np.sqrt(mean_squared_error(y_test, ensemble_preds))
    mae = mean_absolute_error(y_test, ensemble_preds)

    print(f"\n  Final Ensemble Test Metrics:")
    print(f"  R²   = {r2:.4f}")
    print(f"  RMSE = {rmse:.2f} quintals/ha")
    print(f"  MAE  = {mae:.2f} quintals/ha")

    print("\n[4/4] Saving metadata...")
    metadata = {
        "model_type": "Ensemble (XGBoost + DNN + RandomForest)",
        "weights": {"xgboost": 0.45, "dnn": 0.35, "random_forest": 0.20},
        "feature_columns": feature_columns,
        "num_features": len(feature_columns),
        "test_metrics": {"r2": float(r2), "rmse": float(rmse), "mae": float(mae)},
        "individual_val_r2": {"xgboost": float(xgb_r2), "dnn": float(dnn_r2), "random_forest": float(rf_r2)},
        "training_date": datetime.now().isoformat(),
        "is_demo_mode": is_synthetic
    }
    with open(SAVED_MODELS_DIR / "yield_model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✓ Training complete!")
    print(f"  Test R²: {r2:.4f}")
    print(f"  Models saved to: {SAVED_MODELS_DIR}")


if __name__ == "__main__":
    train()
