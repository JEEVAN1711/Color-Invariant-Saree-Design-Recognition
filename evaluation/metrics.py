import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import Dict, List, Tuple
import torch
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

from config import (
    MODEL_CHECKPOINT_PATH,
    CLASSES,
    CLASS_TO_IDX,
    PRESET_SAREES_DIR
)
from models.architecture import SareeDesignNet, build_model
from training.dataset_loader import get_dataloaders
from training.augmentation import ColorInvariantAugmentation
from PIL import Image


def evaluate_model(checkpoint_path: Path = MODEL_CHECKPOINT_PATH) -> Dict[str, float]:
    """
    Evaluates the model on test split, computes Accuracy, Precision, Recall, F1,
    and saves the confusion matrix heatmap.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _, _, test_loader = get_dataloaders()

    model = build_model(str(checkpoint_path), device=device)
    model.eval()

    all_preds: List[int] = []
    all_labels: List[int] = []

    with torch.no_grad():
        for images, labels, _ in test_loader:
            images = images.to(device)
            logits, _ = model(images)
            preds = torch.argmax(logits, dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.numpy())

    y_true = np.array(all_labels)
    y_pred = np.array(all_preds)

    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)

    # Plot & Save Confusion Matrix
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(CLASSES))))
    plt.figure(figsize=(9, 7))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=CLASSES,
        yticklabels=CLASSES
    )
    plt.title("Saree Design Recognition — Confusion Matrix")
    plt.xlabel("Predicted Design")
    plt.ylabel("Ground Truth Design")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    out_plot = Path(__file__).resolve().parent / "confusion_matrix.png"
    plt.savefig(out_plot, dpi=150)
    plt.close()

    metrics = {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1_score": float(f1),
        "confusion_matrix_path": str(out_plot)
    }

    print("\n" + "=" * 50)
    print("        MODEL EVALUATION RESULTS")
    print("=" * 50)
    print(f"Accuracy  : {acc * 100:.2f}%")
    print(f"Precision : {prec * 100:.2f}%")
    print(f"Recall    : {rec * 100:.2f}%")
    print(f"F1 Score  : {f1 * 100:.2f}%")
    print(f"Confusion Matrix saved to: {out_plot}")
    print("=" * 50 + "\n")

    return metrics


def run_color_invariance_stress_test(checkpoint_path: Path = MODEL_CHECKPOINT_PATH) -> Dict:
    """
    Stress-tests color invariance: Takes saree designs and rotates hue through 12 distinct steps
    (Red, Amber, Yellow, Lime, Green, Cyan, Sky, Blue, Violet, Magenta, Crimson, Pink).
    Measures how consistently the model classifies the design despite drastic chromatic shifts.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(str(checkpoint_path), device=device)
    model.eval()

    test_images = list(PRESET_SAREES_DIR.glob("*__Crimson_Red.jpg"))
    if not test_images:
        test_images = list(PRESET_SAREES_DIR.glob("*.jpg"))[:8]

    from preprocessing.color_invariance import SareeColorShifter
    hue_deg_shifts = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
    total_evals = 0
    stable_evals = 0

    print("\n" + "=" * 60)
    print("       COLOR-INVARIANCE STRESS TEST")
    print("=" * 60)

    for img_path in test_images:
        pil_img = Image.open(img_path).convert("RGB")
        np_base = np.array(pil_img)
        # Base prediction
        t_base = ColorInvariantAugmentation.get_val_transforms()(pil_img).unsqueeze(0).to(device)
        with torch.no_grad():
            base_logits, _ = model(t_base)
            base_class_idx = int(torch.argmax(base_logits, dim=1).item())
            base_class_name = CLASSES[base_class_idx]

        design_matches = 0
        for deg in hue_deg_shifts:
            recolored_arr = SareeColorShifter.shift_hue(np_base, deg)
            recolored_pil = Image.fromarray(recolored_arr)
            t_shifted = ColorInvariantAugmentation.get_val_transforms()(recolored_pil).unsqueeze(0).to(device)
            with torch.no_grad():
                shifted_logits, _ = model(t_shifted)
                shifted_class_idx = int(torch.argmax(shifted_logits, dim=1).item())

            total_evals += 1
            if shifted_class_idx == base_class_idx:
                design_matches += 1
                stable_evals += 1

        stability_pct = (design_matches / len(hue_deg_shifts)) * 100
        print(f"Design '{base_class_name:<20}': Invariance Stability = {stability_pct:5.1f}% across 12 color shifts")

    overall_stability = (stable_evals / max(total_evals, 1)) * 100
    print("=" * 60)
    print(f"Overall Color-Invariance Index: {overall_stability:.2f}%\n")
    return {"color_invariance_index": overall_stability, "total_evals": total_evals}


if __name__ == "__main__":
    evaluate_model()
    run_color_invariance_stress_test()
