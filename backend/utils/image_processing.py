from PIL import Image
import io
import os
import uuid
from pathlib import Path


def preprocess_image_for_model(image_bytes: bytes, target_size: tuple = (300, 300)):
    """Preprocess image for EfficientNetB3 model input."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != "RGB":
            image = image.convert("RGB")
        image = image.resize(target_size, Image.LANCZOS)
        import numpy as np
        img_array = np.array(image, dtype=np.float32)
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    except Exception as e:
        raise ValueError(f"Failed to preprocess image: {str(e)}")


def save_uploaded_image(image_bytes: bytes, filename: str, upload_dir: str = "uploads") -> str:
    """Save uploaded image to disk and return relative path."""
    os.makedirs(upload_dir, exist_ok=True)
    ext = Path(filename).suffix.lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        ext = ".jpg"
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, unique_name)
    with open(file_path, "wb") as f:
        f.write(image_bytes)
    return file_path


def validate_image(image_bytes: bytes, max_size_mb: float = 10.0) -> bool:
    """Validate image size and format."""
    size_mb = len(image_bytes) / (1024 * 1024)
    if size_mb > max_size_mb:
        raise ValueError(f"Image too large: {size_mb:.1f}MB (max {max_size_mb}MB)")
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()
        return True
    except Exception:
        raise ValueError("Invalid image file. Please upload JPG, PNG, or WEBP.")
