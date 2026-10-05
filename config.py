import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset"
RAW_DATA_DIR = DATASET_DIR / "raw"
PRESET_SAREES_DIR = DATASET_DIR / "preset_sarees"
MODELS_DIR = BASE_DIR / "models"
MODEL_CHECKPOINT_PATH = MODELS_DIR / "saree_model.pth"
STATIC_DIR = BASE_DIR / "frontend" / "dist"

# Ensure directories exist
for directory in [DATASET_DIR, RAW_DATA_DIR, PRESET_SAREES_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Image & Model Specifications
IMAGE_SIZE = (224, 224)
EMBEDDING_DIM = 512
BATCH_SIZE = 16
LEARNING_RATE = 1e-3
NUM_EPOCHS = 20

# Design Classes (Motifs, Borders, Weaves)
CLASSES = [
    "Temple Border",
    "Peacock Motif",
    "Floral Jaal",
    "Paisley (Kalka)",
    "Geometric Weave",
    "Checks & Stripes",
    "Butta Dots",
    "Traditional Zari"
]

NUM_CLASSES = len(CLASSES)
CLASS_TO_IDX = {cls_name: idx for idx, cls_name in enumerate(CLASSES)}
IDX_TO_CLASS = {idx: cls_name for idx, cls_name in enumerate(CLASSES)}

# Supported formats & Upload limits
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

# Preset Color Palette for Dynamic Color Invariance Demonstration
DEMO_PALETTES = [
    {"name": "Crimson Red", "hex": "#C92A2A", "hue_shift": 0},
    {"name": "Royal Blue", "hex": "#1864AB", "hue_shift": 110},
    {"name": "Emerald Green", "hex": "#2B8A3E", "hue_shift": 55},
    {"name": "Mustard Yellow", "hex": "#E67700", "hue_shift": 25},
    {"name": "Royal Purple", "hex": "#6741D9", "hue_shift": 140},
    {"name": "Deep Magenta", "hex": "#A61E4D", "hue_shift": 165},
    {"name": "Teal Turquoise", "hex": "#0C8599", "hue_shift": 85},
    {"name": "Tangerine Orange", "hex": "#D9480F", "hue_shift": 12},
]
