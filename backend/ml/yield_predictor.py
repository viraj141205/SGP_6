import random
import json
import os
import numpy as np
import pickle
from typing import Optional

CROP_AVERAGES = {
    "Rice": 22.0, "Wheat": 32.0, "Maize": 35.0, "Cotton": 15.0,
    "Sugarcane": 350.0, "Soybean": 18.0, "Tomato": 200.0, "Potato": 180.0,
    "Onion": 120.0, "Mustard": 10.0, "Groundnut": 14.0, "Sunflower": 12.0,
    "Bajra": 18.0, "Jowar": 20.0, "Barley": 28.0, "Chickpea": 10.0,
    "Lentil": 8.0, "Mango": 80.0, "Banana": 120.0, "Grapes": 90.0,
    "Turmeric": 50.0, "Ginger": 70.0
}

CROP_RECOMMENDATIONS = {
    "Rice": [
        "Ensure standing water of 5-7 cm during the vegetative stage.",
        "Apply split doses of nitrogen — 1/3 at transplanting, 1/3 at tillering, 1/3 at panicle initiation.",
        "Monitor for Brown Plant Hopper from 30 days after transplanting.",
        "Drain fields 10 days before harvest to facilitate combine operations."
    ],
    "Wheat": [
        "Timely sowing (Nov 1-15) is critical for optimum yield.",
        "Apply the first irrigation at Crown Root Initiation stage (21 days after sowing).",
        "Use seed treatment with Carboxin + Thiram to prevent loose smut.",
        "Monitor for yellow rust from January onwards."
    ],
    "default": [
        "Maintain optimal soil moisture throughout the crop growth cycle.",
        "Follow integrated pest management practices to reduce chemical usage.",
        "Get soil tested every 2-3 years and apply inputs based on soil health card recommendations.",
        "Practice crop rotation to break pest/disease cycles and improve soil health."
    ]
}


class YieldPredictor:
    def __init__(self):
        self.xgb_model = None
        self.rf_model = None
        self.dnn_model = None
        self.scaler = None
        self.label_encoders = {}
        self.feature_columns = []
        self.demo_mode = True
        self._load_models()

    def _load_models(self):
        base_path = os.path.join(os.path.dirname(__file__), "saved_models")
        try:
            xgb_path = os.path.join(base_path, "xgboost_model.pkl")
            rf_path = os.path.join(base_path, "rf_model.pkl")
            dnn_path = os.path.join(base_path, "dnn_yield_model.h5")
            scaler_path = os.path.join(base_path, "scaler.pkl")
            le_path = os.path.join(base_path, "label_encoders.pkl")
            fc_path = os.path.join(base_path, "feature_columns.json")

            if all(os.path.exists(p) for p in [xgb_path, rf_path, scaler_path, le_path]):
                import joblib
                self.xgb_model = joblib.load(xgb_path)
                self.rf_model = joblib.load(rf_path)
                with open(le_path, "rb") as f:
                    self.label_encoders = pickle.load(f)
                with open(scaler_path, "rb") as f:
                    self.scaler = pickle.load(f)
                if os.path.exists(fc_path):
                    with open(fc_path, "r") as f:
                        self.feature_columns = json.load(f)
                if os.path.exists(dnn_path):
                    import tensorflow as tf
                    self.dnn_model = tf.keras.models.load_model(dnn_path)
                self.demo_mode = False
                print("[YieldPredictor] Models loaded successfully.")
            else:
                print("[YieldPredictor] No trained models found. Running in demo mode.")
        except Exception as e:
            print(f"[YieldPredictor] Failed to load models: {e}. Demo mode active.")

    def predict(self, input_data: dict) -> dict:
        if self.demo_mode or self.xgb_model is None:
            return self._demo_predict(input_data)
        try:
            return self._real_predict(input_data)
        except Exception as e:
            print(f"[YieldPredictor] Prediction error: {e}. Falling back to demo.")
            return self._demo_predict(input_data)

    def _real_predict(self, input_data: dict) -> dict:
        crop = input_data.get("crop_type", "Wheat")
        features = self._encode_features(input_data)
        features_scaled = self.scaler.transform([features])
        xgb_pred = float(self.xgb_model.predict(features_scaled)[0])
        rf_pred = float(self.rf_model.predict(features_scaled)[0])
        if self.dnn_model:
            dnn_pred = float(self.dnn_model.predict(features_scaled, verbose=0)[0][0])
            ensemble_pred = 0.45 * xgb_pred + 0.35 * dnn_pred + 0.20 * rf_pred
        else:
            ensemble_pred = 0.7 * xgb_pred + 0.3 * rf_pred
        avg_yield = CROP_AVERAGES.get(crop, 30.0)
        return self._build_result(ensemble_pred, avg_yield, crop, input_data, demo=False)

    def _demo_predict(self, input_data: dict) -> dict:
        crop = input_data.get("crop_type", "Wheat")
        avg_yield = CROP_AVERAGES.get(crop, 30.0)
        n = input_data.get("nitrogen", 60)
        p = input_data.get("phosphorus", 40)
        k = input_data.get("potassium", 40)
        rainfall = input_data.get("rainfall", 800)
        temp = input_data.get("temperature", 25)
        ph = input_data.get("soil_ph", 6.5)

        npk_factor = min((n + p + k) / 200, 1.3)
        rain_factor = min(rainfall / 1000, 1.2)
        temp_factor = 1.0 if 15 <= temp <= 35 else 0.85
        ph_factor = 1.0 if 5.5 <= ph <= 7.5 else 0.9
        variance = random.uniform(0.88, 1.12)

        predicted = avg_yield * npk_factor * rain_factor * temp_factor * ph_factor * variance
        return self._build_result(predicted, avg_yield, crop, input_data, demo=True)

    def _build_result(self, predicted: float, avg_yield: float, crop: str, input_data: dict, demo: bool) -> dict:
        predicted = max(predicted, 0.5)
        margin = predicted * 0.12
        confidence_lower = round(predicted - margin, 2)
        confidence_upper = round(predicted + margin, 2)

        diff_pct = ((predicted - avg_yield) / avg_yield) * 100 if avg_yield > 0 else 0
        if diff_pct > 20:
            comparison = f"{diff_pct:.1f}% above average"
            rating = "Excellent"
        elif diff_pct > 5:
            comparison = f"{diff_pct:.1f}% above average"
            rating = "Good"
        elif diff_pct > -10:
            comparison = "Near average"
            rating = "Average"
        else:
            comparison = f"{abs(diff_pct):.1f}% below average"
            rating = "Poor"

        recommendations = self._generate_recommendations(crop, input_data, predicted, avg_yield)
        dnn_used = "XGBoost + DNN + RandomForest" if not demo else "Demo Ensemble"

        return {
            "predicted_yield": round(predicted, 2),
            "yield_unit": "quintals/acre",
            "confidence_lower": confidence_lower,
            "confidence_upper": confidence_upper,
            "avg_yield_for_crop": avg_yield,
            "yield_comparison": comparison,
            "performance_rating": rating,
            "recommendations": recommendations,
            "model_used": f"Ensemble ({dnn_used})",
            "is_demo_mode": demo
        }

    def _generate_recommendations(self, crop: str, inputs: dict, predicted: float, avg: float) -> list:
        recs = []
        n = inputs.get("nitrogen", 60)
        p = inputs.get("phosphorus", 40)
        k = inputs.get("potassium", 40)
        ph = inputs.get("soil_ph", 6.5)
        rain = inputs.get("rainfall", 800)

        if n < 40:
            recs.append("Nitrogen levels are low. Apply urea (46% N) at 60-80 kg/ha to boost vegetative growth.")
        if p < 25:
            recs.append("Phosphorus is deficient. Apply DAP (18-46-0) at 100 kg/ha at sowing time.")
        if k < 30:
            recs.append("Potassium is low. Apply MOP (0-0-60) at 50 kg/ha to improve crop stress tolerance.")
        if ph < 5.5:
            recs.append("Soil is too acidic (pH < 5.5). Apply agricultural lime at 2-3 tonnes/ha.")
        elif ph > 7.5:
            recs.append(f"Soil pH is high ({ph:.1f}). Add agricultural sulfur to reduce pH by 0.3 units.")
        if rain < 500:
            recs.append("Low rainfall area — consider installing drip irrigation for supplemental water supply.")

        crop_specific = CROP_RECOMMENDATIONS.get(crop, CROP_RECOMMENDATIONS["default"])
        recs.extend(crop_specific[:max(0, 4 - len(recs))])

        if predicted > avg * 1.1:
            recs.append("Your input parameters are favorable. Continue current agronomy practices for sustained high yield.")

        return recs[:5]

    def _encode_features(self, input_data: dict) -> list:
        crop = input_data.get("crop_type", "Wheat")
        region = input_data.get("region", "Unknown")
        season = input_data.get("season", "Kharif")
        features = []
        for col in self.feature_columns:
            if col == "crop_encoded":
                le = self.label_encoders.get("crop_type")
                val = le.transform([crop])[0] if le and crop in le.classes_ else 0
            elif col == "region_encoded":
                le = self.label_encoders.get("region")
                val = le.transform([region])[0] if le and region in le.classes_ else 0
            elif col == "season_encoded":
                le = self.label_encoders.get("season")
                val = le.transform([season])[0] if le and season in le.classes_ else 0
            elif col == "soil_type_encoded":
                le = self.label_encoders.get("soil_type")
                s = input_data.get("soil_type", "Loam")
                val = le.transform([s])[0] if le and s in le.classes_ else 0
            elif col == "area_hectares":
                val = (input_data.get("area_acres", 1.0) or 1.0) * 0.4047
            elif col == "npk_ratio":
                n, p, k = input_data.get("nitrogen", 60), input_data.get("phosphorus", 40), input_data.get("potassium", 40)
                val = n / (p + k + 1)
            elif col == "temp_rainfall_interaction":
                val = input_data.get("temperature", 25) * input_data.get("rainfall", 800)
            else:
                val = input_data.get(col, 0) or 0
            features.append(float(val))
        return features
