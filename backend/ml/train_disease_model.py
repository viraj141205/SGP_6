"""
AgroVision AI - Disease Model Training (MobileNetV2 Transfer Learning)
Optimized for CPU training. Targets 90%+ validation accuracy.
Run: python ml/train_disease_model.py
"""
import os
import json
import sys
import shutil
import random as pyrandom
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
PROC_DISEASE_DIR = BASE_DIR / "data" / "processed" / "disease"
SAVED_MODELS_DIR = Path(__file__).parent / "saved_models"
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)

# -- Hyperparameters (CPU-optimized) --
IMAGE_SIZE = (128, 128)       # Smaller for faster CPU training
BATCH_SIZE = 32
EPOCHS_PHASE1 = 8             # Transfer learning (frozen base)
EPOCHS_PHASE2 = 12            # Fine-tuning (unfreeze top layers)
LABEL_SMOOTHING = 0.1
FINE_TUNE_LAYERS = 30         # Unfreeze top N layers
MAX_IMAGES_PER_CLASS = 500    # Limit per class for CPU training speed


def check_data():
    if not PROC_DISEASE_DIR.exists():
        print("ERROR: Processed disease data not found.")
        print("Run: python ml/data_pipeline.py first")
        return False, [], 0
    class_dirs = [d for d in PROC_DISEASE_DIR.iterdir() if d.is_dir()]
    if len(class_dirs) < 2:
        print("ERROR: Need at least 2 disease classes.")
        return False, [], 0
    class_names = sorted([d.name for d in class_dirs])
    total = sum(len(list(d.glob("*.*"))) for d in class_dirs)
    return True, class_names, total


def prepare_subset_data(class_names):
    """Create a balanced subset of data for faster CPU training."""
    subset_dir = BASE_DIR / "data" / "processed" / "disease_subset"

    # Check if subset already exists and is valid
    if subset_dir.exists():
        existing = [d for d in subset_dir.iterdir() if d.is_dir()]
        if len(existing) == len(class_names):
            total = sum(len(list(d.glob("*.*"))) for d in existing)
            if total > 0:
                print(f"  Using existing subset: {total} images across {len(existing)} classes")
                return subset_dir, total

    # Create balanced subset
    print(f"  Creating balanced subset (max {MAX_IMAGES_PER_CLASS} per class)...")
    if subset_dir.exists():
        shutil.rmtree(subset_dir)
    subset_dir.mkdir(parents=True)

    total_copied = 0
    for cls in class_names:
        src = PROC_DISEASE_DIR / cls
        dst = subset_dir / cls
        dst.mkdir(parents=True, exist_ok=True)

        images = list(src.glob("*.*"))
        if len(images) > MAX_IMAGES_PER_CLASS:
            pyrandom.seed(42)
            images = pyrandom.sample(images, MAX_IMAGES_PER_CLASS)

        for img in images:
            shutil.copy2(img, dst / img.name)
        total_copied += len(images)
        print(f"    {cls}: {len(images)} images")

    print(f"  Subset total: {total_copied} images")
    return subset_dir, total_copied


def build_model(num_classes: int):
    import tensorflow as tf
    from tensorflow.keras import layers, Model
    from tensorflow.keras.applications import MobileNetV2

    base = MobileNetV2(
        include_top=False,
        weights="imagenet",
        input_shape=(*IMAGE_SIZE, 3)
    )
    base.trainable = False  # Freeze for Phase 1

    inputs = tf.keras.Input(shape=(*IMAGE_SIZE, 3))
    x = base(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = Model(inputs, outputs)
    return model, base


def get_callbacks(phase: int):
    import tensorflow as tf
    checkpoint = str(SAVED_MODELS_DIR / "disease_model.h5")
    return [
        tf.keras.callbacks.ModelCheckpoint(
            checkpoint, monitor="val_accuracy",
            save_best_only=True, verbose=1
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=4 if phase == 1 else 6,
            restore_best_weights=True, verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.3,
            patience=2, min_lr=1e-7, verbose=1
        ),
    ]


def create_datasets(data_dir, class_names):
    import tensorflow as tf
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

    augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.15),
        tf.keras.layers.RandomZoom(0.1),
    ])

    train_ds = tf.keras.utils.image_dataset_from_directory(
        str(data_dir),
        validation_split=0.15,
        subset="training",
        seed=42,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
        class_names=class_names
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        str(data_dir),
        validation_split=0.15,
        subset="validation",
        seed=42,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
        class_names=class_names
    )

    # MobileNetV2 preprocess_input maps [0,255] -> [-1,1]
    # Augment first (on uint8), then preprocess
    def train_preprocess(x, y):
        x = augmentation(x, training=True)
        x = preprocess_input(tf.cast(x, tf.float32))
        return x, y

    def val_preprocess(x, y):
        x = preprocess_input(tf.cast(x, tf.float32))
        return x, y

    train_ds = train_ds.map(train_preprocess)
    val_ds = val_ds.map(val_preprocess)

    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().prefetch(AUTOTUNE)
    val_ds = val_ds.cache().prefetch(AUTOTUNE)

    return train_ds, val_ds


def train():
    print("=" * 60)
    print("AgroVision AI - Disease Model Training (MobileNetV2)")
    print("=" * 60)

    ok, class_names, total_images = check_data()
    if not ok:
        sys.exit(1)

    print(f"\nFull dataset: {len(class_names)} classes, {total_images} images")

    import tensorflow as tf
    print(f"TensorFlow: {tf.__version__}")
    gpus = tf.config.list_physical_devices('GPU')
    print(f"GPUs available: {len(gpus)}")
    if gpus:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)

    # Prepare subset for CPU training
    data_dir, subset_total = prepare_subset_data(class_names)

    train_ds, val_ds = create_datasets(data_dir, class_names)
    model, base_model = build_model(len(class_names))

    # -- Phase 1: Transfer Learning (frozen base) --
    print("\n-- Phase 1: Transfer Learning (frozen base) --")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=LABEL_SMOOTHING),
        metrics=["accuracy"]
    )
    model.summary()

    h1 = model.fit(
        train_ds, validation_data=val_ds,
        epochs=EPOCHS_PHASE1,
        callbacks=get_callbacks(1)
    )
    p1_acc = max(h1.history.get("val_accuracy", [0]))
    print(f"\n  Phase 1 best val_accuracy: {p1_acc*100:.2f}%")

    # -- Phase 2: Fine-tuning (unfreeze top layers) --
    print(f"\n-- Phase 2: Fine-tuning (unfreeze top {FINE_TUNE_LAYERS} layers) --")
    base_model.trainable = True
    for layer in base_model.layers[:-FINE_TUNE_LAYERS]:
        layer.trainable = False

    trainable = sum(1 for l in model.layers if l.trainable)
    print(f"  Trainable layers: {trainable}")

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=LABEL_SMOOTHING),
        metrics=["accuracy"]
    )

    h2 = model.fit(
        train_ds, validation_data=val_ds,
        epochs=EPOCHS_PHASE2,
        callbacks=get_callbacks(2)
    )
    p2_acc = max(h2.history.get("val_accuracy", [0]))
    print(f"\n  Phase 2 best val_accuracy: {p2_acc*100:.2f}%")

    # -- Final Evaluation --
    print("\n-- Final Evaluation --")
    results = model.evaluate(val_ds, verbose=1)
    val_loss, val_accuracy = results[0], results[1]

    # Save class names
    with open(SAVED_MODELS_DIR / "class_names.json", "w") as f:
        json.dump(class_names, f, indent=2)

    # Save metadata
    best_acc = max(p1_acc, p2_acc, val_accuracy)
    metadata = {
        "model_type": "MobileNetV2",
        "num_classes": len(class_names),
        "image_size": list(IMAGE_SIZE),
        "val_accuracy": float(best_acc),
        "val_loss": float(val_loss),
        "phase1_best_accuracy": float(p1_acc),
        "phase2_best_accuracy": float(p2_acc),
        "label_smoothing": LABEL_SMOOTHING,
        "fine_tune_layers": FINE_TUNE_LAYERS,
        "training_date": datetime.now().isoformat(),
        "total_images": total_images,
        "subset_images": subset_total,
        "class_names": class_names
    }
    with open(SAVED_MODELS_DIR / "disease_model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n{'='*60}")
    print(f"  TRAINING COMPLETE!")
    print(f"  Best Validation Accuracy: {best_acc*100:.2f}%")
    print(f"  Model: {SAVED_MODELS_DIR / 'disease_model.h5'}")
    print(f"  Classes: {SAVED_MODELS_DIR / 'class_names.json'}")
    print(f"{'='*60}")

    if best_acc >= 0.90:
        print("  [OK] TARGET ACHIEVED: 90%+ accuracy!")
    else:
        print(f"  [!!] Below 90% target. Consider more epochs or data.")


if __name__ == "__main__":
    train()
