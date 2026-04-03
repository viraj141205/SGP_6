import random
import json
import os
import numpy as np
from datetime import datetime
from typing import Optional

DISEASE_DATABASE = {
    "Apple___Apple_scab": {
        "crop": "Apple", "disease": "Apple Scab", "severity": "Medium",
        "description": "Apple scab is a fungal disease caused by Venturia inaequalis. It produces olive-green to brown scabby lesions on leaves and fruit surfaces.",
        "symptoms": ["Olive-green spots on young leaves", "Dark scabby lesions on fruit", "Premature leaf drop", "Cracked and distorted fruit"],
        "treatment": ["Apply fungicide (Captan or Mancozeb) preventively from bud break", "Remove and destroy infected leaves and fruit", "Prune trees to improve air circulation", "Apply lime sulfur spray during dormant season"],
        "prevention": ["Plant resistant apple varieties like Liberty or Redfree", "Practice good sanitation by removing fallen leaves", "Avoid overhead irrigation", "Monitor weather for high scab risk periods"]
    },
    "Tomato___Early_blight": {
        "crop": "Tomato", "disease": "Early Blight", "severity": "Medium",
        "description": "Early blight is caused by Alternaria solani, producing characteristic target-spot lesions on older leaves first, then spreading upward.",
        "symptoms": ["Brown spots with concentric rings (target pattern)", "Yellow halo around lesions", "Lower leaves affected first", "Stem lesions near soil line"],
        "treatment": ["Remove and destroy infected leaves immediately", "Apply copper-based fungicide every 7-10 days", "Use Mancozeb or Chlorothalonil fungicide", "Avoid overhead watering — use drip irrigation"],
        "prevention": ["Practice crop rotation every 2-3 years", "Use disease-resistant tomato varieties", "Ensure proper plant spacing for air circulation", "Apply mulch to prevent soil splash"]
    },
    "Tomato___Late_blight": {
        "crop": "Tomato", "disease": "Late Blight", "severity": "High",
        "description": "Late blight caused by Phytophthora infestans is a devastating disease. It spreads rapidly in cool, wet conditions and can destroy an entire crop within days.",
        "symptoms": ["Water-soaked pale green spots on leaves", "White fuzzy growth on leaf undersides", "Dark brown lesions on stems", "Firm brown spots on fruit"],
        "treatment": ["Apply copper hydroxide or chlorothalonil fungicide immediately", "Remove and bag all infected plant material", "Avoid working in field when plants are wet", "Apply systemic fungicide (Metalaxyl) for severe cases"],
        "prevention": ["Plant certified disease-free seed", "Use resistant varieties (Mountain Magic, Iron Lady)", "Ensure good drainage and air circulation", "Monitor nightly temperatures — risk is high below 15°C with high humidity"]
    },
    "Tomato___Healthy": {
        "crop": "Tomato", "disease": "Healthy", "severity": "None",
        "description": "Your tomato plant appears to be healthy. No signs of disease were detected.",
        "symptoms": ["No symptoms detected"],
        "treatment": ["Continue regular monitoring", "Maintain proper fertigation schedule", "Ensure adequate spacing"],
        "prevention": ["Regular scouting for early pest/disease detection", "Maintain balanced nutrition", "Practice crop rotation"]
    },
    "Corn___Common_rust": {
        "crop": "Corn", "disease": "Common Rust", "severity": "Medium",
        "description": "Common rust of corn is caused by Puccinia sorghi. Pustules appear on both leaf surfaces and can reduce photosynthesis significantly.",
        "symptoms": ["Brick-red to brown oval pustules on both leaf surfaces", "Pustules rupture to release rusty spores", "Yellowing around pustules", "Severe infection causes premature leaf death"],
        "treatment": ["Apply triazole fungicide (Propiconazole) at first sign", "Scout fields regularly from tasseling stage", "Apply foliar fungicide if disease is developing rapidly", "Ensure good crop nutrition to reduce susceptibility"],
        "prevention": ["Plant resistant hybrid varieties", "Avoid planting in low-lying areas with poor air movement", "Monitor weather conditions favorable to rust", "Scout from mid-July onward"]
    },
    "Potato___Late_blight": {
        "crop": "Potato", "disease": "Late Blight", "severity": "High",
        "description": "Potato late blight caused by Phytophthora infestans is the same pathogen that caused the Irish Potato Famine. It is highly destructive.",
        "symptoms": ["Water-soaked dark green to black lesions on leaves", "White sporulation on leaf undersides", "Black rotted stems", "Brown dry rot in tubers"],
        "treatment": ["Apply fungicide immediately (Metalaxyl + Mancozeb)", "Haulm destruction before harvest", "Do not store infected tubers", "Increase spray frequency during cool wet weather"],
        "prevention": ["Use certified disease-free seed potatoes", "Plant resistant varieties (Sarpo Mira, Melody)", "Allow proper hilling to protect tubers", "Avoid excessive nitrogen fertilization"]
    },
    "Rice___Brown_Spot": {
        "crop": "Rice", "disease": "Brown Spot", "severity": "Medium",
        "description": "Rice brown spot caused by Cochliobolus miyabeanus affects both leaves and grains, reducing yield and grain quality.",
        "symptoms": ["Circular to oval brown spots with gray-white centers", "Brown margins around spots", "Spots on leaf sheaths and grains", "Spots may coalesce in heavy infection"],
        "treatment": ["Apply contact fungicide (Mancozeb) or systemic (Propiconazole)", "Seed treatment with thiram or captan", "Improve crop nutrition especially potassium", "Apply foliar spray at booting stage"],
        "prevention": ["Use disease-free certified seed", "Maintain proper silicon nutrition", "Avoid excess nitrogen and correct potassium deficiency", "Drain and dry fields periodically"]
    },
    "Wheat___Yellow_Rust": {
        "crop": "Wheat", "disease": "Yellow Rust", "severity": "High",
        "description": "Yellow rust (stripe rust) caused by Puccinia striiformis is one of the most destructive wheat diseases worldwide.",
        "symptoms": ["Yellow-orange stripe-like pustules on leaves", "Pustules arranged in stripes between leaf veins", "White spore masses on greener parts of plant", "Leaves turn completely yellow in severe infection"],
        "treatment": ["Apply triazole fungicide (Tebuconazole) immediately", "Spray in early morning or evening for best efficacy", "Repeat spray after 14-21 days if needed", "Remove and destroy heavily infected plants"],
        "prevention": ["Plant resistant varieties (WB02, DBW187)", "Avoid late sowing which increases rust risk", "Monitor crop from tillering stage", "Do not over-apply nitrogen fertilizer"]
    }
}

HEALTHY_CLASSES = {"Tomato___Healthy", "Corn___healthy", "Potato___healthy", "Apple___healthy"}

CROP_AVERAGES = {
    "Tomato": 35.0, "Apple": 28.0, "Corn": 22.0, "Potato": 180.0,
    "Rice": 25.0, "Wheat": 32.0, "Grape": 45.0, "Peach": 30.0
}


class DiseasePredictor:
    def __init__(self):
        self.model = None
        self.class_names = []
        self.demo_mode = True
        self._load_model()

    def _load_model(self):
        model_path = os.path.join(os.path.dirname(__file__), "saved_models", "disease_model.h5")
        class_names_path = os.path.join(os.path.dirname(__file__), "saved_models", "class_names.json")

        if os.path.exists(model_path) and os.path.exists(class_names_path):
            try:
                import tensorflow as tf
                self.model = tf.keras.models.load_model(model_path)
                with open(class_names_path, "r") as f:
                    self.class_names = json.load(f)
                self.demo_mode = False
                print(f"[DiseasePredictor] Model loaded. Classes: {len(self.class_names)}")
            except Exception as e:
                print(f"[DiseasePredictor] Failed to load model: {e}. Falling back to demo mode.")
                self.demo_mode = True
        else:
            print("[DiseasePredictor] No trained model found. Running in demo mode.")
            self.demo_mode = True

    def predict(self, image_array: Optional[np.ndarray] = None) -> dict:
        if self.demo_mode or self.model is None:
            return self._demo_predict()

        try:
            predictions = self.model.predict(image_array, verbose=0)
            class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][class_idx])
            class_name = self.class_names[class_idx]
            return self._build_result(class_name, confidence, demo=False)
        except Exception as e:
            print(f"[DiseasePredictor] Prediction error: {e}. Falling back to demo mode.")
            return self._demo_predict()

    def _demo_predict(self) -> dict:
        classes = list(DISEASE_DATABASE.keys())
        weights = [0.15, 0.20, 0.12, 0.08, 0.10, 0.08, 0.10, 0.08, 0.09]
        while len(weights) < len(classes):
            weights.append(0.05)
        weights = weights[:len(classes)]
        total = sum(weights)
        weights = [w / total for w in weights]
        class_name = random.choices(classes, weights=weights, k=1)[0]
        confidence = round(random.uniform(0.78, 0.97), 4)
        return self._build_result(class_name, confidence, demo=True)

    def _build_result(self, class_name: str, confidence: float, demo: bool) -> dict:
        info = DISEASE_DATABASE.get(class_name, {
            "crop": "Unknown", "disease": "Unknown Disease", "severity": "Medium",
            "description": "Disease details not available in database.",
            "symptoms": ["Abnormal leaf coloration", "Lesions on leaves"],
            "treatment": ["Consult local agricultural extension officer", "Apply broad-spectrum fungicide"],
            "prevention": ["Regular crop monitoring", "Good sanitation practices"]
        })

        severity = info["severity"]
        severity_color_map = {"None": "green", "Low": "green", "Medium": "orange", "High": "red"}
        is_healthy = (severity == "None" or "healthy" in class_name.lower())

        return {
            "class_name": class_name,
            "crop_type": info["crop"],
            "disease_name": info["disease"],
            "is_healthy": is_healthy,
            "confidence": confidence,
            "severity": severity if not is_healthy else "None",
            "severity_color": severity_color_map.get(severity, "orange"),
            "description": info["description"],
            "symptoms": info["symptoms"],
            "treatment": info["treatment"],
            "prevention": info["prevention"],
            "is_demo_mode": demo
        }
