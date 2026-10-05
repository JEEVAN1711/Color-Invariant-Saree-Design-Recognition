import torch
import torchvision.transforms as T
from PIL import Image
import numpy as np

class ColorInvariantAugmentation:
    """
    Data augmentation pipeline designed specifically to destroy color correlation
    while preserving motif shapes, border geometries, and weaving patterns.
    """

    @staticmethod
    def get_train_transforms():
        return T.Compose([
            T.Resize((224, 224)),
            T.RandomHorizontalFlip(p=0.5),
            T.RandomVerticalFlip(p=0.2),
            T.RandomRotation(degrees=15),
            # Aggressive Color Distortion to force model to ignore hue/chroma
            T.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.6, hue=0.5),
            T.RandomGrayscale(p=0.4),  # 40% of images are presented in pure grayscale
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    @staticmethod
    def get_val_transforms():
        return T.Compose([
            T.Resize((224, 224)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    @staticmethod
    def get_color_shift_transform(hue_shift: float = 0.5):
        """Generates transforms for color-invariance stress testing."""
        return T.Compose([
            T.Resize((224, 224)),
            T.ColorJitter(hue=hue_shift),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
