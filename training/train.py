import os
import sys
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR

from config import (
    MODEL_CHECKPOINT_PATH,
    NUM_CLASSES,
    LEARNING_RATE,
    NUM_EPOCHS,
    MODELS_DIR
)
from models.architecture import SareeDesignNet
from training.dataset_loader import get_dataloaders


def train_model(
    epochs: int = NUM_EPOCHS,
    lr: float = LEARNING_RATE,
    checkpoint_path: Path = MODEL_CHECKPOINT_PATH
):
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Training] Using compute device: {device}")

    # Build DataLoaders
    train_loader, val_loader, test_loader = get_dataloaders()
    print(f"[Training] Loaded {len(train_loader.dataset)} training samples, "
          f"{len(val_loader.dataset)} validation samples, {len(test_loader.dataset)} test samples.")

    # Initialize model
    model = SareeDesignNet(num_classes=NUM_CLASSES, pretrained=True).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs)

    best_val_acc = 0.0
    best_epoch = 0

    print("\n" + "=" * 65)
    print(f"{'Epoch':<8}{'Train Loss':<14}{'Train Acc':<14}{'Val Loss':<14}{'Val Acc':<10}")
    print("=" * 65)

    start_time = time.time()

    for epoch in range(1, epochs + 1):
        # Training Phase
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels, _ in train_loader:
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            logits, _ = model(images)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            preds = torch.argmax(logits, dim=1)
            correct += torch.sum(preds == labels).item()
            total += labels.size(0)

        train_loss = running_loss / total
        train_acc = correct / total

        # Validation Phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for images, labels, _ in val_loader:
                images = images.to(device)
                labels = labels.to(device)

                logits, _ = model(images)
                loss = criterion(logits, labels)

                val_loss += loss.item() * images.size(0)
                preds = torch.argmax(logits, dim=1)
                val_correct += torch.sum(preds == labels).item()
                val_total += labels.size(0)

        val_loss = val_loss / val_total
        val_acc = val_correct / val_total
        scheduler.step()

        print(f"{epoch:<8}{train_loss:<14.4f}{train_acc * 100:<13.1f}%{val_loss:<14.4f}{val_acc * 100:<9.1f}%")

        # Save best model
        if val_acc >= best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch
            torch.save(model.state_dict(), checkpoint_path)

    elapsed = time.time() - start_time
    print("=" * 65)
    print(f"[Training Complete] Best Validation Accuracy: {best_val_acc * 100:.2f}% (Epoch {best_epoch}) in {elapsed:.1f}s")
    print(f"[Model Saved] -> {checkpoint_path}")


if __name__ == "__main__":
    train_model(epochs=15)
