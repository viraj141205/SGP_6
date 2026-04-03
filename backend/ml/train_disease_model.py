"""
AgroVision AI — Disease Model Training
Architecture: EfficientNetB3 with Transfer Learning
Run: python ml/train_disease_model.py
"""
import os
import json
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
PROC_DISEASE_DIR = BASE_DIR / "data" / "processed" / "disease"
SAVED_MODELS_DIR = Path(__file__).parent / "saved_models"
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_SIZE = (300, 300)
BATCH_SIZE_PHASE1 = 32
BATCH_SIZE_PHASE2 = 16
EPOCHS_PHASE1 = 15
EPOCHS_PHASE2 = 20
VAL_SPLIT = 0.15
TEST_SPLIT = 0.15


def check_data():
    if not PROC_DISEASE_DIR.exists():
        print("ERROR: Processed disease data not found.")
        print("Run: python ml/data_pipeline.py first")
        return False, [], 0
    class_dirs = [d for d in PROC_DISEASE_DIR.iterdir() if d.is_dir()]
    if len(class_dirs) < 2:
        print("ERROR: Need at least 2 disease classes to train.")
        return False, [], 0
    class_names = sorted([d.name for d in class_dirs])
    total_images = sum(len(list(d.glob("*.*"))) for d in class_dirs)
    return True, class_names, total_images


def build_model(num_classes: int):
    import tensorflow as tf
    from tensorflow.keras import layers, Model
    from tensorflow.keras.applications import EfficientNetB3

    base = EfficientNetB3(
        include_top=False,
        weights="imagenet",
        input_shape=(*IMAGE_SIZE, 3)
    )
    base.trainable = False

    inputs = tf.keras.Input(shape=(*IMAGE_SIZE, 3))
    x = base(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(512, activation="relu")(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = Model(inputs, outputs)
    return model, base


def get_callbacks(phase: int):
    import tensorflow as tf
    checkpoint_path = str(SAVED_MODELS_DIR / "disease_model.h5")
    return [
        tf.keras.callbacks.ModelCheckpoint(
            checkpoint_path, monitor="val_accuracy",
            save_best_only=True, verbose=1
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=5,
            restore_best_weights=True, verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.2, patience=3,
            min_lr=1e-7, verbose=1
        ),
        tf.keras.callbacks.TensorBoard(
            log_dir=str(BASE_DIR / "logs" / f"disease_phase{phase}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            histogram_freq=0
        )
    ]


def create_data_generators(class_names):
    import tensorflow as tf

    # Data augmentation for training
    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal_and_vertical"),
        tf.keras.layers.RandomRotation(0.15),
        tf.keras.layers.RandomZoom(0.1),
        tf.keras.layers.RandomBrightness(0.2),
        tf.keras.layers.RandomContrast(0.2),
    ])

    train_ds = tf.keras.utils.image_dataset_from_directory(
        str(PROC_DISEASE_DIR),
        validation_split=VAL_SPLIT + TEST_SPLIT,
        subset="training",
        seed=42,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE_PHASE1,
        label_mode="categorical",
        class_names=class_names
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        str(PROC_DISEASE_DIR),
        validation_split=VAL_SPLIT + TEST_SPLIT,
        subset="validation",
        seed=42,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE_PHASE1,
        label_mode="categorical",
        class_names=class_names
    )

    # Normalize pixel values
    normalization = tf.keras.layers.Rescaling(1.0 / 255)
    train_ds = train_ds.map(lambda x, y: (data_augmentation(normalization(x), training=True), y))
    val_ds = val_ds.map(lambda x, y: (normalization(x), y))

    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().prefetch(AUTOTUNE)
    val_ds = val_ds.cache().prefetch(AUTOTUNE)

    return train_ds, val_ds


def train():
    print("=" * 60)
    print("AgroVision AI — Disease Model Training (EfficientNetB3)")
    print("=" * 60)

    ok, class_names, total_images = check_data()
    if not ok:
        sys.exit(1)

    print(f"\nDataset: {len(class_names)} classes, {total_images} images")

    import tensorflow as tf
    print(f"TensorFlow version: {tf.__version__}")

    train_ds, val_ds = create_data_generators(class_names)
    model, base_model = build_model(len(class_names))

    print("\n── Phase 1: Transfer Learning (frozen base) ──")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    model.summary()
    history1 = model.fit(
        train_ds, validation_data=val_ds,
        epochs=EPOCHS_PHASE1,
        callbacks=get_callbacks(1)
    )

    print("\n── Phase 2: Fine-tuning (unfreeze top 30 layers) ──")
    base_model.trainable = True
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    history2 = model.fit(
        train_ds, validation_data=val_ds,
        epochs=EPOCHS_PHASE2,
        callbacks=get_callbacks(2)
    )

    # Evaluate
    print("\n── Evaluating on validation set ──")
    results = model.evaluate(val_ds, verbose=1)
    val_accuracy = results[1]
    val_loss = results[0]

    # Save class names for inference
    class_names_path = SAVED_MODELS_DIR / "class_names.json"
    with open(class_names_path, "w") as f:
        json.dump(class_names, f, indent=2)

    # Save metadata
    metadata = {
        "model_type": "EfficientNetB3",
        "num_classes": len(class_names),
        "image_size": list(IMAGE_SIZE),
        "val_accuracy": float(val_accuracy),
        "val_loss": float(val_loss),
        "training_date": datetime.now().isoformat(),
        "total_images": total_images,
        "class_names": class_names
    }
    with open(SAVED_MODELS_DIR / "disease_model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✓ Training complete!")
    print(f"  Validation Accuracy: {val_accuracy * 100:.2f}%")
    print(f"  Model saved to: {SAVED_MODELS_DIR / 'disease_model.h5'}")


if __name__ == "__main__":
    train()
