import os

_disease_predictor = None
_yield_predictor = None


def get_disease_predictor():
    global _disease_predictor
    if _disease_predictor is None:
        from ml.disease_predictor import DiseasePredictor
        _disease_predictor = DiseasePredictor()
    return _disease_predictor


def get_yield_predictor():
    global _yield_predictor
    if _yield_predictor is None:
        from ml.yield_predictor import YieldPredictor
        _yield_predictor = YieldPredictor()
    return _yield_predictor


def load_all_models():
    print("[ModelLoader] Loading disease predictor...")
    get_disease_predictor()
    print("[ModelLoader] Loading yield predictor...")
    get_yield_predictor()
    print("[ModelLoader] All models initialized.")
