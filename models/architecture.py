import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from typing import Tuple, Dict

from config import EMBEDDING_DIM, NUM_CLASSES


class SareeDesignNet(nn.Module):
    """
    Dual-head Deep Learning Architecture for Color-Invariant Saree Design Recognition.
    - Backbone: Pretrained MobileNetV3 / ResNet feature extractor
    - Head 1 (Embedding Head): 512-dimensional L2-normalized vector for cosine similarity retrieval
    - Head 2 (Classification Head): Multi-class softmax classification for design motifs/patterns
    """

    def __init__(self, num_classes: int = NUM_CLASSES, embedding_dim: int = EMBEDDING_DIM, pretrained: bool = True):
        super().__init__()
        self.num_classes = num_classes
        self.embedding_dim = embedding_dim

        # Use MobileNetV3-Large or ResNet18 backbone
        # MobileNetV3 provides excellent geometric & edge pattern extraction with sub-20ms inference
        backbone = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT if pretrained else None)
        
        # Extract convolutional feature extractor
        self.features = backbone.features
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))

        in_features = 960  # MobileNetV3-Large pooled feature dimension

        # Embedding projection head (512-dimensional)
        self.embedding_head = nn.Sequential(
            nn.Linear(in_features, 512),
            nn.LayerNorm(512),
            nn.Hardswish(),
            nn.Dropout(p=0.2),
            nn.Linear(512, embedding_dim)
        )

        # Classification head for design classes
        self.classifier = nn.Sequential(
            nn.LayerNorm(embedding_dim),
            nn.Hardswish(),
            nn.Dropout(p=0.3),
            nn.Linear(embedding_dim, num_classes)
        )

    def extract_embedding(self, x: torch.Tensor) -> torch.Tensor:
        """
        Extracts L2-normalized feature representation vector (512-D).
        Cosine similarity between two normalized embeddings is simply their dot product.
        """
        feats = self.features(x)
        pooled = self.avgpool(feats)
        flattened = torch.flatten(pooled, 1)
        raw_embed = self.embedding_head(flattened)
        normalized_embed = F.normalize(raw_embed, p=2, dim=1)
        return normalized_embed

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Returns:
            logits: (Batch, Num_Classes) unnormalized classification scores
            embedding: (Batch, Embedding_Dim) L2-normalized feature vector
        """
        normalized_embed = self.extract_embedding(x)
        logits = self.classifier(normalized_embed)
        return logits, normalized_embed


def build_model(checkpoint_path: str = None, device: torch.device = None) -> SareeDesignNet:
    """Instantiates the model and loads weights if available."""
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = SareeDesignNet()
    if checkpoint_path and torch.cuda.is_available() or checkpoint_path:
        import os
        if os.path.exists(checkpoint_path):
            try:
                state_dict = torch.load(checkpoint_path, map_location=device, weights_only=True)
                model.load_state_dict(state_dict)
            except Exception as e:
                print(f"[Warning] Failed to load checkpoint {checkpoint_path}: {e}")

    model.to(device)
    model.eval()
    return model
