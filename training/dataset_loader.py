import os
from pathlib import Path
from typing import List, Tuple, Optional
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import numpy as np

from config import (
    PRESET_SAREES_DIR,
    CLASSES,
    CLASS_TO_IDX,
    BATCH_SIZE
)
from training.augmentation import ColorInvariantAugmentation
from preprocessing.color_invariance import ColorInvariantTransformer


def parse_class_from_filename(filename: str) -> Optional[str]:
    """
    Parses class name from filename like 'Temple_Border__Crimson_Red.jpg'
    or 'Checks_and_Stripes__Emerald_Green.jpg'
    """
    prefix = filename.split("__")[0]
    # Map back to canonical class names
    mapping = {
        "Temple_Border": "Temple Border",
        "Peacock_Motif": "Peacock Motif",
        "Floral_Jaal": "Floral Jaal",
        "Paisley_Kalka": "Paisley (Kalka)",
        "Geometric_Weave": "Geometric Weave",
        "Checks_and_Stripes": "Checks & Stripes",
        "Butta_Dots": "Butta Dots",
        "Traditional_Zari": "Traditional Zari",
    }
    return mapping.get(prefix, None)


class SareeDataset(Dataset):
    """
    PyTorch Dataset for Saree Design Recognition.
    Loads images, associates them with their invariant design category,
    and applies color-invariant transformations.
    """

    def __init__(
        self,
        samples: List[Tuple[Path, int]],
        transform=None,
        use_composite_features: bool = False
    ):
        self.samples = samples
        self.transform = transform
        self.use_composite_features = use_composite_features

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int, str]:
        img_path, label_idx = self.samples[idx]
        pil_img = Image.open(img_path).convert("RGB")

        if self.use_composite_features:
            # Transform image to 3-channel (Luminance, Sobel Edge, Texture) composite
            np_arr = np.array(pil_img)
            composite_arr = ColorInvariantTransformer.create_color_invariant_composite(np_arr)
            pil_img = Image.fromarray(composite_arr)

        if self.transform is not None:
            tensor_img = self.transform(pil_img)
        else:
            tensor_img = ColorInvariantAugmentation.get_val_transforms()(pil_img)

        return tensor_img, label_idx, str(img_path)


def get_dataloaders(
    data_dir: Path = PRESET_SAREES_DIR,
    batch_size: int = BATCH_SIZE,
    train_split: float = 0.7,
    val_split: float = 0.15,
    seed: int = 42
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Scans the saree image directory, creates stratified/random train/val/test splits,
    and returns PyTorch DataLoaders.
    """
    all_files = list(data_dir.glob("*.jpg")) + list(data_dir.glob("*.png"))
    samples: List[Tuple[Path, int]] = []

    for f in all_files:
        cls_name = parse_class_from_filename(f.name)
        if cls_name and cls_name in CLASS_TO_IDX:
            samples.append((f, CLASS_TO_IDX[cls_name]))

    if not samples:
        raise ValueError(f"No valid labeled saree images found in {data_dir}")

    # Reproducible shuffle
    rng = np.random.RandomState(seed)
    indices = np.arange(len(samples))
    rng.shuffle(indices)

    n_total = len(samples)
    n_train = int(n_total * train_split)
    n_val = int(n_total * val_split)

    train_idx = indices[:n_train]
    val_idx = indices[n_train:n_train + n_val]
    test_idx = indices[n_train + n_val:]

    train_samples = [samples[i] for i in train_idx]
    val_samples = [samples[i] for i in val_idx]
    test_samples = [samples[i] for i in test_idx]

    train_dataset = SareeDataset(train_samples, transform=ColorInvariantAugmentation.get_train_transforms())
    val_dataset = SareeDataset(val_samples, transform=ColorInvariantAugmentation.get_val_transforms())
    test_dataset = SareeDataset(test_samples, transform=ColorInvariantAugmentation.get_val_transforms())

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=False)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, val_loader, test_loader
