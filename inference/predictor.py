import io
from pathlib import Path
from typing import Dict, Any, Optional
import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image

from config import (
    MODEL_CHECKPOINT_PATH,
    CLASSES,
    IDX_TO_CLASS,
    IMAGE_SIZE
)
from models.architecture import build_model
from preprocessing.image_processor import ImageProcessor
from preprocessing.color_invariance import ColorInvariantTransformer, SareeColorShifter
from training.augmentation import ColorInvariantAugmentation
from inference.similarity import SareeSimilarityEngine


class SareePredictor:
    """
    Production Inference Engine for Color-Invariant Saree Design Recognition.
    Processes images, extracts color-invariant feature stages, computes design predictions,
    and retrieves top similar designs via cosine similarity.
    """

    def __init__(self, checkpoint_path: Optional[Path] = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        path_str = str(checkpoint_path or MODEL_CHECKPOINT_PATH)
        print(f"[Predictor] Initializing SareeDesignNet on device: {self.device}...")
        self.model = build_model(path_str, device=self.device)
        self.transform = ColorInvariantAugmentation.get_val_transforms()
        self.similarity_engine = SareeSimilarityEngine(self.model, self.device)
        print("[Predictor] Ready for inference.")

    def predict_image(
        self,
        image_bytes: bytes,
        filename: str = "saree_upload.jpg",
        top_k_similar: int = 4
    ) -> Dict[str, Any]:
        """
        Runs complete inference pipeline on uploaded saree image.
        """
        # 1. Validation & Orientation Correction
        pil_img = ImageProcessor.validate_image_bytes(image_bytes, filename=filename)

        # 2. Resize & Bilateral Edge-Preserving Denoising
        np_rgb = ImageProcessor.resize_and_denoise(pil_img, target_size=IMAGE_SIZE)

        # 3. Extract Visual Processing Stages for Frontend Inspection
        visual_stages = ColorInvariantTransformer.get_visual_stages(np_rgb)

        # 4. Transform to Normalized PyTorch Tensor
        processed_pil = Image.fromarray(np_rgb)
        tensor = self.transform(processed_pil).unsqueeze(0).to(self.device)

        # 5. Forward Pass
        self.model.eval()
        with torch.no_grad():
            logits, embedding = self.model(tensor)
            probs = F.softmax(logits, dim=1).squeeze(0).cpu().numpy()

        # 6. Extract Top Prediction & Class Probabilities
        top_idx = int(np.argmax(probs))
        top_class = IDX_TO_CLASS[top_idx]
        confidence = float(probs[top_idx])

        # Sorted rankings
        sorted_indices = np.argsort(-probs)
        class_rankings = [
            {
                "class_name": IDX_TO_CLASS[int(idx)],
                "probability": round(float(probs[idx]), 4),
                "percentage": round(float(probs[idx]) * 100, 1)
            }
            for idx in sorted_indices
        ]

        # 7. Similar Designs Retrieval via Embedding Cosine Search
        similar_items = self.similarity_engine.find_top_k(embedding, k=top_k_similar, exclude_filename=filename)

        # 8. Feature Vector sample (first 10 elements of normalized 512-dim embedding)
        raw_vector_sample = [round(float(v), 4) for v in embedding.squeeze(0).cpu().numpy()[:10]]

        return {
            "success": True,
            "filename": filename,
            "predicted_design": top_class,
            "confidence": round(confidence, 4),
            "confidence_percentage": round(confidence * 100, 1),
            "class_rankings": class_rankings,
            "embedding_sample": raw_vector_sample,
            "embedding_dim": embedding.shape[1],
            "visual_stages": visual_stages,
            "similar_designs": similar_items
        }

    def recolor_and_predict(
        self,
        image_bytes: bytes,
        target_color_hex: Optional[str] = None,
        hue_shift_deg: Optional[float] = None,
        preserve_zari: bool = True,
        blend_intensity: float = 0.90,
        filename: str = "saree_recolor.jpg"
    ) -> Dict[str, Any]:
        """
        Dynamically recolors a saree image (either by target hex or hue rotation),
        and runs color-invariant inference on the recolored image to demonstrate
        that the predicted design remains rock-solid.
        """
        pil_img = ImageProcessor.validate_image_bytes(image_bytes, filename=filename)
        
        # Preserve full saree dimensions and aspect ratio for high-resolution visual display
        w, h = pil_img.size
        max_dim = 1200
        if max(w, h) > max_dim:
            scale = max_dim / float(max(w, h))
            full_pil = pil_img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
        else:
            full_pil = pil_img
            
        full_np = np.array(full_pil)

        # Apply photorealistic recoloring across the entire full saree
        if target_color_hex:
            recolored_full = SareeColorShifter.recolor_to_target_hex(
                full_np,
                target_color_hex,
                preserve_zari=preserve_zari,
                blend_intensity=blend_intensity
            )
        elif hue_shift_deg is not None:
            recolored_full = SareeColorShifter.shift_hue(full_np, hue_shift_deg)
        else:
            recolored_full = full_np

        recolored_b64 = SareeColorShifter.to_base64_data_url(recolored_full)

        # Encode recolored image to bytes for inference
        buf = io.BytesIO()
        Image.fromarray(recolored_full).save(buf, format="JPEG", quality=95)
        recolored_bytes = buf.getvalue()

        # Run inference on recolored image
        inference_result = self.predict_image(recolored_bytes, filename=f"recolored_{filename}")
        inference_result["recolored_image"] = recolored_b64
        inference_result["applied_color_hex"] = target_color_hex
        inference_result["applied_hue_shift"] = hue_shift_deg
        inference_result["preserved_zari"] = preserve_zari
        inference_result["blend_intensity"] = blend_intensity

        return inference_result
