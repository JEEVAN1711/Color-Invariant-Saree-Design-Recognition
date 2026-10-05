import os
from pathlib import Path
from typing import List, Dict, Optional
import torch
import numpy as np
from PIL import Image

from config import PRESET_SAREES_DIR, CLASSES
from training.dataset_loader import parse_class_from_filename
from training.augmentation import ColorInvariantAugmentation


class SareeSimilarityEngine:
    """
    Computes cosine similarity between saree feature vectors (512-D L2-normalized embeddings)
    to retrieve visually and structurally similar designs regardless of fabric color.
    """

    def __init__(self, model, device: torch.device):
        self.model = model
        self.device = device
        self.reference_samples: List[Dict] = []
        self.reference_embeddings: Optional[torch.Tensor] = None
        self._index_reference_sarees()

    def _index_reference_sarees(self):
        """Indexes all reference preset sarees into normalized embedding memory."""
        all_imgs = sorted(list(PRESET_SAREES_DIR.glob("*.jpg")))
        if not all_imgs:
            return

        transform = ColorInvariantAugmentation.get_val_transforms()
        embed_list = []
        self.reference_samples = []

        self.model.eval()
        with torch.no_grad():
            for p in all_imgs:
                try:
                    pil_img = Image.open(p).convert("RGB")
                    tensor = transform(pil_img).unsqueeze(0).to(self.device)
                    embed = self.model.extract_embedding(tensor)  # (1, 512) L2 normalized
                    embed_list.append(embed.cpu())

                    cls_name = parse_class_from_filename(p.name) or "Unknown Design"
                    color_variant = p.stem.split("__")[-1].replace("_", " ")

                    self.reference_samples.append({
                        "filename": p.name,
                        "design": cls_name,
                        "color": color_variant,
                        "relative_path": f"/presets/{p.name}"
                    })
                except Exception as e:
                    print(f"[Similarity Index] Error indexing {p.name}: {e}")

        if embed_list:
            self.reference_embeddings = torch.cat(embed_list, dim=0)  # (N, 512)
            print(f"[Similarity Engine] Successfully indexed {len(self.reference_samples)} reference saree designs.")

    def find_top_k(self, query_embedding: torch.Tensor, k: int = 4, exclude_filename: Optional[str] = None) -> List[Dict]:
        """
        Computes dot-product cosine similarity against reference embeddings
        and returns the top-K closest matching saree designs.
        """
        if self.reference_embeddings is None or len(self.reference_samples) == 0:
            return []

        # query_embedding is (1, 512) or (512,)
        q = query_embedding.view(1, -1).cpu()
        # Cosine similarity for L2-normalized vectors is dot product
        similarities = torch.mm(q, self.reference_embeddings.T).squeeze(0).numpy()

        # Sort indices descending
        ranked_indices = np.argsort(-similarities)
        results = []

        for idx in ranked_indices:
            sample = self.reference_samples[idx]
            if exclude_filename and sample["filename"] == exclude_filename:
                continue

            sim_score = float(similarities[idx])
            # Scale cosine similarity (-1 to 1) into percentage (0% to 100%)
            match_pct = max(0.0, min(100.0, ((sim_score + 1.0) / 2.0) * 100.0))

            results.append({
                "design": sample["design"],
                "color": sample["color"],
                "filename": sample["filename"],
                "image_url": sample["relative_path"],
                "similarity_score": round(sim_score, 4),
                "match_percentage": round(match_pct, 1)
            })

            if len(results) >= k:
                break

        return results
