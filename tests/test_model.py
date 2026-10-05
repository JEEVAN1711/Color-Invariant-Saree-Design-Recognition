import pytest
import torch
from models.architecture import SareeDesignNet
from config import NUM_CLASSES, EMBEDDING_DIM


def test_model_forward_shape():
    model = SareeDesignNet(num_classes=NUM_CLASSES, embedding_dim=EMBEDDING_DIM, pretrained=False)
    model.eval()

    dummy_input = torch.randn(2, 3, 224, 224)
    with torch.no_grad():
        logits, embedding = model(dummy_input)

    assert logits.shape == (2, NUM_CLASSES)
    assert embedding.shape == (2, EMBEDDING_DIM)

    # Embedding should be L2-normalized: norm of each vector must be approximately 1.0
    norms = torch.norm(embedding, p=2, dim=1)
    assert torch.allclose(norms, torch.ones_like(norms), atol=1e-5)


def test_extract_embedding_single_sample():
    model = SareeDesignNet(num_classes=NUM_CLASSES, embedding_dim=EMBEDDING_DIM, pretrained=False)
    model.eval()

    single_input = torch.randn(1, 3, 224, 224)
    with torch.no_grad():
        embedding = model.extract_embedding(single_input)

    assert embedding.shape == (1, EMBEDDING_DIM)
    assert abs(torch.norm(embedding, p=2).item() - 1.0) < 1e-5
