import random
import json
import os
import numpy as np
from datetime import datetime
from typing import Optional

# All 38 PlantVillage classes with comprehensive disease information
DISEASE_DATABASE = {
    "Apple___Apple_scab": {
        "crop": "Apple", "disease": "Apple Scab", "severity": "Medium",
        "description": "Fungal disease caused by Venturia inaequalis producing olive-green to brown scabby lesions on leaves and fruit.",
        "symptoms": ["Olive-green spots on young leaves", "Dark scabby lesions on fruit", "Premature leaf drop", "Cracked and distorted fruit"],
        "treatment": ["Apply fungicide (Captan or Mancozeb) from bud break", "Remove infected leaves and fruit", "Prune for air circulation", "Lime sulfur spray during dormancy"],
        "prevention": ["Plant resistant varieties (Liberty, Redfree)", "Remove fallen leaves", "Avoid overhead irrigation", "Monitor weather for scab risk"]
    },
    "Apple___Black_rot": {
        "crop": "Apple", "disease": "Black Rot", "severity": "High",
        "description": "Caused by Botryosphaeria obtusa, affects fruit, leaves, and bark. Creates frog-eye leaf spots and fruit rot.",
        "symptoms": ["Frog-eye leaf spots with purple margins", "Brown to black rotting on fruit", "Cankers on branches", "Mummified fruit on tree"],
        "treatment": ["Remove mummified fruit and cankers", "Apply Captan or Thiophanate-methyl", "Prune dead and diseased wood", "Fungicide at petal fall"],
        "prevention": ["Good sanitation", "Remove dead wood", "Proper spacing", "Avoid wounding fruit"]
    },
    "Apple___Cedar_apple_rust": {
        "crop": "Apple", "disease": "Cedar Apple Rust", "severity": "Medium",
        "description": "Caused by Gymnosporangium juniperi-virginianae. Requires both apple and cedar/juniper hosts to complete lifecycle.",
        "symptoms": ["Bright orange-yellow spots on upper leaf surface", "Tube-like structures on leaf undersides", "Spots on fruit", "Premature defoliation"],
        "treatment": ["Apply myclobutanil fungicide at pink bud stage", "Remove nearby cedar/juniper trees within 2 miles", "Fungicide every 7-10 days during wet spring", "Remove galls from juniper in winter"],
        "prevention": ["Plant resistant varieties", "Remove juniper hosts", "Monitor in spring after rain", "Maintain tree vigor"]
    },
    "Apple___healthy": {
        "crop": "Apple", "disease": "Healthy", "severity": "None",
        "description": "Your apple plant appears healthy with no signs of disease.",
        "symptoms": ["No symptoms detected"],
        "treatment": ["Continue regular monitoring", "Maintain fertilization schedule"],
        "prevention": ["Regular scouting", "Balanced nutrition", "Proper pruning"]
    },
    "Blueberry___healthy": {
        "crop": "Blueberry", "disease": "Healthy", "severity": "None",
        "description": "Your blueberry plant appears healthy with no signs of disease.",
        "symptoms": ["No symptoms detected"],
        "treatment": ["Continue regular monitoring", "Maintain acidic soil pH (4.5-5.5)"],
        "prevention": ["Proper mulching", "Adequate watering", "Annual pruning"]
    },
    "Cherry_(including_sour)___Powdery_mildew": {
        "crop": "Cherry", "disease": "Powdery Mildew", "severity": "Medium",
        "description": "Caused by Podosphaera clandestina. White powdery coating on leaves, shoots, and fruit.",
        "symptoms": ["White powdery coating on leaves", "Curled and distorted new growth", "Stunted shoots", "Russeted fruit"],
        "treatment": ["Apply sulfur-based fungicide", "Use myclobutanil at first sign", "Prune for air circulation", "Remove infected shoots"],
        "prevention": ["Plant resistant varieties", "Avoid overhead irrigation", "Proper spacing", "Reduce nitrogen fertilization"]
    },
    "Cherry_(including_sour)___healthy": {
        "crop": "Cherry", "disease": "Healthy", "severity": "None",
        "description": "Your cherry plant appears healthy with no signs of disease.",
        "symptoms": ["No symptoms detected"],
        "treatment": ["Continue regular monitoring", "Maintain proper irrigation"],
        "prevention": ["Regular pruning", "Good sanitation", "Balanced fertilization"]
    },
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "crop": "Corn", "disease": "Gray Leaf Spot", "severity": "High",
        "description": "Caused by Cercospora zeae-maydis. Rectangular gray-brown lesions between leaf veins. Major yield reducer.",
        "symptoms": ["Rectangular gray to tan lesions", "Lesions parallel to leaf veins", "Leaves turn gray-green then tan", "Premature leaf death"],
        "treatment": ["Apply strobilurin fungicide at tasseling", "Scout regularly from V8 stage", "Foliar fungicide if disease is spreading", "Ensure good crop nutrition"],
        "prevention": ["Plant resistant hybrids", "Rotate away from corn", "Tillage to bury crop residue", "Avoid continuous corn planting"]
    },
    "Corn_(maize)___Common_rust_": {
        "crop": "Corn", "disease": "Common Rust", "severity": "Medium",
        "description": "Caused by Puccinia sorghi. Brick-red oval pustules on both leaf surfaces reducing photosynthesis.",
        "symptoms": ["Brick-red to brown oval pustules", "Pustules on both leaf surfaces", "Yellowing around pustules", "Premature leaf death in severe cases"],
        "treatment": ["Apply triazole fungicide (Propiconazole)", "Scout from tasseling stage", "Foliar fungicide if spreading rapidly", "Ensure good crop nutrition"],
        "prevention": ["Plant resistant hybrids", "Avoid low-lying areas", "Monitor weather conditions", "Scout from mid-July"]
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "crop": "Corn", "disease": "Northern Leaf Blight", "severity": "High",
        "description": "Caused by Exserohilum turcicum. Long cigar-shaped gray-green lesions on leaves.",
        "symptoms": ["Large cigar-shaped gray-green lesions", "Lesions 1-6 inches long", "Lesions start on lower leaves", "Gray-green appearance when wet"],
        "treatment": ["Apply foliar fungicide at tasseling", "Use azoxystrobin or propiconazole", "Scout from V8 stage", "Apply before disease reaches ear leaf"],
        "prevention": ["Plant resistant hybrids", "Rotate crops", "Tillage to bury residue", "Avoid late planting"]
    },
    "Corn_(maize)___healthy": {
        "crop": "Corn", "disease": "Healthy", "severity": "None",
        "description": "Your corn plant appears healthy with no signs of disease.",
        "symptoms": ["No symptoms detected"],
        "treatment": ["Continue regular monitoring", "Maintain fertigation schedule"],
        "prevention": ["Regular scouting", "Crop rotation", "Balanced nutrition"]
    },
    "Grape___Black_rot": {
        "crop": "Grape", "disease": "Black Rot", "severity": "High",
        "description": "Caused by Guignardia bidwellii. Affects leaves, shoots, and fruit. Can destroy entire crop.",
        "symptoms": ["Circular reddish-brown spots on leaves", "Black pycnidia in lesion centers", "Fruit shrivels to hard black mummies", "Shoot lesions"],
        "treatment": ["Apply mancozeb or myclobutanil fungicide", "Remove mummified fruit", "Spray from bud break through veraison", "Use systemic fungicide in wet years"],
        "prevention": ["Remove mummies and infected canes", "Good canopy management", "Proper air circulation", "Sanitation pruning"]
    },
    "Grape___Esca_(Black_Measles)": {
        "crop": "Grape", "disease": "Esca (Black Measles)", "severity": "High",
        "description": "Complex fungal disease caused by multiple fungi. Causes tiger-stripe leaf symptoms and internal wood decay.",
        "symptoms": ["Tiger-stripe pattern on leaves", "Interveinal chlorosis and necrosis", "Dark spotting on berries", "Internal wood staining"],
        "treatment": ["No effective chemical cure", "Retrain affected vines from suckers", "Remove severely affected vines", "Wound protectants after pruning"],
        "prevention": ["Minimize large pruning wounds", "Apply wound protectants", "Avoid stress conditions", "Use certified planting material"]
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "crop": "Grape", "disease": "Leaf Blight (Isariopsis)", "severity": "Medium",
        "description": "Caused by Pseudocercospora vitis. Brown necrotic lesions on leaves leading to defoliation.",
        "symptoms": ["Dark brown irregular lesions on leaves", "Lesions with yellow halos", "Premature defoliation", "Reduced fruit quality"],
        "treatment": ["Apply copper-based fungicide", "Use mancozeb preventatively", "Remove infected leaves", "Improve canopy airflow"],
        "prevention": ["Good canopy management", "Avoid overhead irrigation", "Regular scouting", "Balanced fertilization"]
    },
    "Grape___healthy": {
        "crop": "Grape", "disease": "Healthy", "severity": "None",
        "description": "Your grape vine appears healthy with no signs of disease.",
        "symptoms": ["No symptoms detected"],
        "treatment": ["Continue regular monitoring", "Maintain canopy management"],
        "prevention": ["Regular pruning", "Good air circulation", "Balanced nutrition"]
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "crop": "Orange", "disease": "Huanglongbing (Citrus Greening)", "severity": "High",
        "description": "Bacterial disease spread by Asian citrus psyllid. Most devastating citrus disease worldwide. No cure exists.",
        "symptoms": ["Asymmetric blotchy mottling of leaves", "Yellow shoots", "Lopsided, bitter fruit", "Premature fruit drop"],
        "treatment": ["No cure — manage symptoms", "Nutritional sprays to extend tree life", "Remove severely affected trees", "Control psyllid vectors with insecticide"],
        "prevention": ["Control Asian citrus psyllid populations", "Use certified disease-free nursery stock", "Scout regularly for psyllids", "Remove infected trees promptly"]
    },
    "Peach___Bacterial_spot": {
        "crop": "Peach", "disease": "Bacterial Spot", "severity": "Medium",
        "description": "Caused by Xanthomonas arboricola pv. pruni. Affects leaves, fruit, and twigs.",
        "symptoms": ["Angular water-soaked spots on leaves", "Shot-hole appearance on leaves", "Sunken lesions on fruit", "Twig cankers"],
        "treatment": ["Copper sprays at leaf fall and bud swell", "Oxytetracycline during bloom", "Remove infected twigs", "Avoid overhead irrigation"],
        "prevention": ["Plant resistant varieties", "Proper tree spacing", "Avoid wetting foliage", "Good sanitation"]
    },
    "Peach___healthy": {
        "crop": "Peach", "disease": "Healthy", "severity": "None",
        "description": "Your peach tree appears healthy with no signs of disease.",
        "symptoms": ["No symptoms detected"],
        "treatment": ["Continue regular monitoring", "Maintain pruning schedule"],
        "prevention": ["Annual pruning", "Good sanitation", "Balanced fertilization"]
    },
    "Pepper,_bell___Bacterial_spot": {
        "crop": "Pepper", "disease": "Bacterial Spot", "severity": "Medium",
        "description": "Caused by Xanthomonas campestris pv. vesicatoria. Affects leaves, stems, and fruit.",
        "symptoms": ["Small water-soaked spots on leaves", "Spots turn brown with yellow halo", "Raised scab-like spots on fruit", "Defoliation in severe cases"],
        "treatment": ["Copper-based bactericides", "Remove infected plant debris", "Avoid working with wet plants", "Use disease-free transplants"],
        "prevention": ["Use certified disease-free seed", "Crop rotation (2-3 years)", "Avoid overhead irrigation", "Resistant varieties"]
    },
    "Pepper,_bell___healthy": {
        "crop": "Pepper", "disease": "Healthy", "severity": "None",
        "description": "Your pepper plant appears healthy with no signs of disease.",
        "symptoms": ["No symptoms detected"],
        "treatment": ["Continue regular care", "Monitor for pests"],
        "prevention": ["Crop rotation", "Proper spacing", "Balanced watering"]
    },
    "Potato___Early_blight": {
        "crop": "Potato", "disease": "Early Blight", "severity": "Medium",
        "description": "Caused by Alternaria solani. Target-spot lesions on older leaves, spreading upward.",
        "symptoms": ["Brown spots with concentric rings", "Yellow halo around lesions", "Lower leaves affected first", "Stem lesions near soil"],
        "treatment": ["Remove infected leaves", "Copper-based fungicide every 7-10 days", "Mancozeb or Chlorothalonil", "Drip irrigation instead of overhead"],
        "prevention": ["Crop rotation (2-3 years)", "Resistant varieties", "Proper plant spacing", "Mulch to prevent soil splash"]
    },
    "Potato___Late_blight": {
        "crop": "Potato", "disease": "Late Blight", "severity": "High",
        "description": "Caused by Phytophthora infestans — the pathogen behind the Irish Potato Famine. Highly destructive.",
        "symptoms": ["Water-soaked dark lesions on leaves", "White sporulation on leaf undersides", "Black rotted stems", "Brown dry rot in tubers"],
        "treatment": ["Apply Metalaxyl + Mancozeb immediately", "Destroy infected plant material", "Increase spray frequency in cool wet weather", "Haulm destruction before harvest"],
        "prevention": ["Use certified disease-free seed", "Resistant varieties (Sarpo Mira)", "Good drainage and air circulation", "Avoid excess nitrogen"]
    },
    "Potato___healthy": {
        "crop": "Potato", "disease": "Healthy", "severity": "None",
        "description": "Your potato plant appears healthy with no signs of disease.",
        "symptoms": ["No symptoms detected"],
        "treatment": ["Continue regular monitoring", "Maintain proper hilling"],
        "prevention": ["Crop rotation", "Certified seed potatoes", "Proper irrigation"]
    },
    "Raspberry___healthy": {
        "crop": "Raspberry", "disease": "Healthy", "severity": "None",
        "description": "Your raspberry plant appears healthy with no signs of disease.",
        "symptoms": ["No symptoms detected"],
        "treatment": ["Continue regular monitoring", "Maintain trellis support"],
        "prevention": ["Annual cane removal", "Good air circulation", "Proper watering"]
    },
    "Soybean___healthy": {
        "crop": "Soybean", "disease": "Healthy", "severity": "None",
        "description": "Your soybean plant appears healthy with no signs of disease.",
        "symptoms": ["No symptoms detected"],
        "treatment": ["Continue regular monitoring", "Check for pest activity"],
        "prevention": ["Crop rotation", "Proper seeding rate", "Weed management"]
    },
    "Squash___Powdery_mildew": {
        "crop": "Squash", "disease": "Powdery Mildew", "severity": "Medium",
        "description": "Caused by Podosphaera xanthii. White powdery growth on leaf surfaces.",
        "symptoms": ["White powdery spots on upper leaf surface", "Spots expand to cover entire leaf", "Yellowing and browning of leaves", "Premature leaf death"],
        "treatment": ["Apply potassium bicarbonate spray", "Use sulfur-based fungicide", "Neem oil for organic control", "Remove severely infected leaves"],
        "prevention": ["Plant resistant varieties", "Proper plant spacing", "Avoid overhead watering", "Morning irrigation to allow drying"]
    },
    "Strawberry___Leaf_scorch": {
        "crop": "Strawberry", "disease": "Leaf Scorch", "severity": "Medium",
        "description": "Caused by Diplocarpon earlianum. Irregular purple blotches on leaves.",
        "symptoms": ["Irregular purple to brown spots", "Spots may coalesce", "Leaf margins dry and curl", "Reduced fruit production"],
        "treatment": ["Remove infected leaves", "Apply captan fungicide", "Renovate beds after harvest", "Improve drainage"],
        "prevention": ["Plant resistant varieties", "Good air circulation", "Avoid overhead irrigation", "Remove old leaves in spring"]
    },
    "Strawberry___healthy": {
        "crop": "Strawberry", "disease": "Healthy", "severity": "None",
        "description": "Your strawberry plant appears healthy with no signs of disease.",
        "symptoms": ["No symptoms detected"],
        "treatment": ["Continue regular care", "Monitor for runners"],
        "prevention": ["Proper mulching", "Adequate spacing", "Regular renovation"]
    },
    "Tomato___Bacterial_spot": {
        "crop": "Tomato", "disease": "Bacterial Spot", "severity": "Medium",
        "description": "Caused by Xanthomonas species. Small dark spots on leaves, stems, and fruit.",
        "symptoms": ["Small dark water-soaked spots on leaves", "Spots with yellow halos", "Raised scab-like spots on fruit", "Defoliation"],
        "treatment": ["Copper-based bactericide", "Remove infected debris", "Avoid working with wet plants", "Use resistant varieties"],
        "prevention": ["Certified disease-free seed", "Crop rotation", "Avoid overhead irrigation", "Proper spacing"]
    },
    "Tomato___Early_blight": {
        "crop": "Tomato", "disease": "Early Blight", "severity": "Medium",
        "description": "Caused by Alternaria solani. Target-spot lesions on older leaves, spreading upward.",
        "symptoms": ["Brown spots with concentric rings", "Yellow halo around lesions", "Lower leaves first", "Stem lesions near soil"],
        "treatment": ["Remove infected leaves", "Copper-based fungicide", "Mancozeb or Chlorothalonil", "Drip irrigation"],
        "prevention": ["Crop rotation", "Resistant varieties", "Proper spacing", "Mulch to prevent splash"]
    },
    "Tomato___Late_blight": {
        "crop": "Tomato", "disease": "Late Blight", "severity": "High",
        "description": "Caused by Phytophthora infestans. Spreads rapidly in cool, wet conditions.",
        "symptoms": ["Water-soaked pale green spots", "White fuzzy growth on undersides", "Dark brown stem lesions", "Firm brown spots on fruit"],
        "treatment": ["Copper hydroxide or chlorothalonil immediately", "Remove all infected material", "Systemic fungicide for severe cases", "Avoid wet conditions"],
        "prevention": ["Certified disease-free seed", "Resistant varieties", "Good drainage", "Monitor temperatures below 15°C"]
    },
    "Tomato___Leaf_Mold": {
        "crop": "Tomato", "disease": "Leaf Mold", "severity": "Medium",
        "description": "Caused by Passalora fulva (Cladosporium fulvum). Thrives in high humidity greenhouse conditions.",
        "symptoms": ["Pale green to yellow spots on upper leaf", "Olive-green to brown velvety growth underneath", "Leaves curl and wither", "Can affect fruit in severe cases"],
        "treatment": ["Improve greenhouse ventilation", "Apply chlorothalonil fungicide", "Remove infected leaves", "Reduce humidity below 85%"],
        "prevention": ["Good ventilation", "Avoid leaf wetness", "Resistant varieties", "Proper plant spacing"]
    },
    "Tomato___Septoria_leaf_spot": {
        "crop": "Tomato", "disease": "Septoria Leaf Spot", "severity": "Medium",
        "description": "Caused by Septoria lycopersici. Small circular spots with dark borders and gray centers.",
        "symptoms": ["Small circular spots with dark borders", "Gray-white centers with dark specks", "Lower leaves affected first", "Progressive defoliation upward"],
        "treatment": ["Remove infected lower leaves", "Apply chlorothalonil or copper fungicide", "Mulch to prevent soil splash", "Fungicide every 7-10 days when wet"],
        "prevention": ["Crop rotation (2 years)", "Stake and prune for airflow", "Avoid overhead irrigation", "Remove crop debris"]
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "crop": "Tomato", "disease": "Spider Mites", "severity": "Medium",
        "description": "Two-spotted spider mite (Tetranychus urticae) infestation. Tiny pests causing stippling damage.",
        "symptoms": ["Fine stippling on leaves", "Yellow to bronze discoloration", "Fine webbing on leaf undersides", "Leaf drop in severe cases"],
        "treatment": ["Spray with miticide (abamectin)", "Insecticidal soap or neem oil", "Release predatory mites (Phytoseiulus)", "Strong water spray to dislodge"],
        "prevention": ["Avoid dusty conditions", "Maintain adequate humidity", "Monitor with hand lens", "Avoid broad-spectrum insecticides"]
    },
    "Tomato___Target_Spot": {
        "crop": "Tomato", "disease": "Target Spot", "severity": "Medium",
        "description": "Caused by Corynespora cassiicola. Concentric ring lesions on leaves and fruit.",
        "symptoms": ["Brown spots with concentric rings", "Lesions on leaves, stems, and fruit", "Large lesions may crack", "Premature defoliation"],
        "treatment": ["Apply chlorothalonil or mancozeb", "Remove infected plant parts", "Improve air circulation", "Avoid overhead irrigation"],
        "prevention": ["Crop rotation", "Resistant varieties", "Proper plant spacing", "Good sanitation"]
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "crop": "Tomato", "disease": "Yellow Leaf Curl Virus", "severity": "High",
        "description": "TYLCV transmitted by whiteflies (Bemisia tabaci). Causes severe stunting and yield loss.",
        "symptoms": ["Severe upward leaf curling", "Yellow leaf margins", "Stunted growth", "Flower drop and reduced fruit set"],
        "treatment": ["No cure — remove infected plants", "Control whitefly with imidacloprid", "Use yellow sticky traps", "Apply reflective mulch"],
        "prevention": ["Use TYLCV-resistant varieties", "Control whitefly populations", "Use insect-proof netting", "Remove infected plants immediately"]
    },
    "Tomato___Tomato_mosaic_virus": {
        "crop": "Tomato", "disease": "Tomato Mosaic Virus", "severity": "High",
        "description": "ToMV is a highly stable virus spread by contact. Causes mosaic patterns and leaf distortion.",
        "symptoms": ["Light and dark green mosaic pattern", "Leaf distortion and curling", "Stunted growth", "Fruit with yellow blotches"],
        "treatment": ["No chemical cure", "Remove and destroy infected plants", "Disinfect tools with 10% bleach", "Wash hands between plants"],
        "prevention": ["Use resistant varieties (Tm-2 gene)", "Disinfect tools and hands", "Avoid tobacco products near plants", "Use disease-free seed"]
    },
    "Tomato___healthy": {
        "crop": "Tomato", "disease": "Healthy", "severity": "None",
        "description": "Your tomato plant appears healthy with no signs of disease.",
        "symptoms": ["No symptoms detected"],
        "treatment": ["Continue regular monitoring", "Maintain fertigation schedule"],
        "prevention": ["Regular scouting", "Balanced nutrition", "Crop rotation"]
    },
}

HEALTHY_CLASSES = {k for k in DISEASE_DATABASE if "healthy" in k.lower()}


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
                
                class CustomDense(tf.keras.layers.Dense):
                    def __init__(self, **kwargs):
                        kwargs.pop('quantization_config', None)
                        super().__init__(**kwargs)

                class CustomBatchNormalization(tf.keras.layers.BatchNormalization):
                    def __init__(self, **kwargs):
                        kwargs.pop('renorm', None)
                        kwargs.pop('renorm_clipping', None)
                        kwargs.pop('renorm_momentum', None)
                        super().__init__(**kwargs)

                self.model = tf.keras.models.load_model(
                    model_path, 
                    custom_objects={'Dense': CustomDense, 'BatchNormalization': CustomBatchNormalization},
                    compile=False
                )
                with open(class_names_path, "r") as f:
                    self.class_names = json.load(f)
                self.demo_mode = False
                print(f"[DiseasePredictor] Model loaded. Classes: {len(self.class_names)}")
            except Exception as e:
                print(f"[DiseasePredictor] Failed to load model: {e}. Demo mode active.")
                self.demo_mode = True
        else:
            print("[DiseasePredictor] No trained model found. Demo mode.")
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
            print(f"[DiseasePredictor] Prediction error: {e}. Falling back to demo.")
            return self._demo_predict()

    def _demo_predict(self) -> dict:
        classes = list(DISEASE_DATABASE.keys())
        class_name = random.choice(classes)
        confidence = round(random.uniform(0.78, 0.97), 4)
        return self._build_result(class_name, confidence, demo=True)

    def _build_result(self, class_name: str, confidence: float, demo: bool) -> dict:
        info = DISEASE_DATABASE.get(class_name, {
            "crop": class_name.split("___")[0] if "___" in class_name else "Unknown",
            "disease": class_name.split("___")[1].replace("_", " ") if "___" in class_name else "Unknown",
            "severity": "Medium",
            "description": "Disease details not available in database.",
            "symptoms": ["Abnormal leaf coloration", "Lesions on leaves"],
            "treatment": ["Consult agricultural extension officer", "Apply broad-spectrum fungicide"],
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
