import io
import base64
from typing import Dict, Tuple, Union
import numpy as np
import cv2
from PIL import Image

class ColorInvariantTransformer:
    """
    Transforms RGB saree images into color-decoupled, geometry- and texture-preserving
    feature maps to ensure design classification is completely independent of fabric color.
    """

    @staticmethod
    def extract_luminance_clahe(rgb_array: np.ndarray) -> np.ndarray:
        """
        Extracts perceptual luminance via CIE LAB color space and applies
        Contrast Limited Adaptive Histogram Equalization (CLAHE) to enhance
        intricate zari borders, jaal threads, and motifs.
        """
        # Convert RGB to LAB (L* channel = 0-255 in OpenCV)
        lab = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2LAB)
        l_channel, _, _ = cv2.split(lab)

        # Apply CLAHE to equalize local thread and weave contrast
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        enhanced_l = clahe.apply(l_channel)
        return enhanced_l

    @staticmethod
    def extract_edge_gradient_map(luminance: np.ndarray) -> np.ndarray:
        """
        Computes Sobel gradient magnitude to capture motif contours, borders,
        and geometric lines regardless of whether the saree is light or dark colored.
        """
        grad_x = cv2.Sobel(luminance, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(luminance, cv2.CV_32F, 0, 1, ksize=3)
        magnitude = cv2.magnitude(grad_x, grad_y)
        normalized_mag = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
        return normalized_mag.astype(np.uint8)

    @staticmethod
    def extract_laplacian_texture(luminance: np.ndarray) -> np.ndarray:
        """
        Extracts high-frequency weaving texture and fine zari motifs using Laplacian filter.
        """
        laplacian = cv2.Laplacian(luminance, cv2.CV_32F, ksize=3)
        laplacian = np.clip(np.abs(laplacian), 0, 255).astype(np.uint8)
        return laplacian

    @classmethod
    def create_color_invariant_composite(cls, rgb_array: np.ndarray) -> np.ndarray:
        """
        Synthesizes a 3-channel color-invariant representation:
        - Channel 0: CLAHE-enhanced Luminance (L*)
        - Channel 1: Sobel Gradient Magnitude (Edges & Borders)
        - Channel 2: High-Frequency Laplacian Texture (Weave & Motif detailing)
        Output is uint8 of shape (H, W, 3).
        """
        lum = cls.extract_luminance_clahe(rgb_array)
        edge = cls.extract_edge_gradient_map(lum)
        texture = cls.extract_laplacian_texture(lum)
        composite = np.stack([lum, edge, texture], axis=-1)
        return composite

    @classmethod
    def get_visual_stages(cls, rgb_array: np.ndarray) -> Dict[str, str]:
        """
        Encodes intermediate color-invariant processing stages into base64 PNG data URLs
        for interactive rendering in the frontend dashboard.
        """
        lum = cls.extract_luminance_clahe(rgb_array)
        edge = cls.extract_edge_gradient_map(lum)
        texture = cls.extract_laplacian_texture(lum)
        composite = cls.create_color_invariant_composite(rgb_array)

        def to_b64(img_arr: np.ndarray) -> str:
            if len(img_arr.shape) == 2:
                pil_img = Image.fromarray(img_arr, mode="L")
            else:
                pil_img = Image.fromarray(img_arr, mode="RGB")
            buf = io.BytesIO()
            pil_img.save(buf, format="PNG")
            return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

        return {
            "luminance_map": to_b64(lum),
            "edge_map": to_b64(edge),
            "texture_map": to_b64(texture),
            "composite_invariant": to_b64(composite)
        }


class SareeColorShifter:
    """
    Shifts or recolors saree images while perfectly preserving motif structures,
    shadows, textures, and gold/silver zari borders. Used for real-time interactive
    color changing demonstrations in the React UI.
    """

    @staticmethod
    def hex_to_hsv(hex_color: str) -> Tuple[int, int, int]:
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # Convert RGB to HSV using OpenCV standard scale (H: 0-179, S: 0-255, V: 0-255)
        rgb_norm = np.uint8([[[r, g, b]]])
        hsv = cv2.cvtColor(rgb_norm, cv2.COLOR_RGB2HSV)[0][0]
        return int(hsv[0]), int(hsv[1]), int(hsv[2])

    @classmethod
    def shift_hue(cls, rgb_array: np.ndarray, shift_degrees: float) -> np.ndarray:
        """
        Shifts the hue of the entire saree by a specified degree (0 - 360).
        OpenCV hue is 0-179, so shift is scaled to (shift_degrees / 2.0).
        """
        hsv = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2HSV).astype(np.float32)
        h_channel, s_channel, v_channel = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

        shift_val = (shift_degrees / 2.0) % 180.0
        h_channel = (h_channel + shift_val) % 180.0

        shifted_hsv = np.stack([h_channel, s_channel, v_channel], axis=-1).astype(np.uint8)
        recolored_rgb = cv2.cvtColor(shifted_hsv, cv2.COLOR_HSV2RGB)
        return recolored_rgb

    @classmethod
    def recolor_to_target_hex(
        cls,
        rgb_array: np.ndarray,
        target_hex: str,
        preserve_zari: bool = True,
        blend_intensity: float = 0.85
    ) -> np.ndarray:
        """
        Photorealistically recolors the saree fabric to the target hex color.
        Uses direct target dye replacement with natural fold shading and
        protects gold/silver zari threads as well as neutral background.
        """
        hex_clean = target_hex.lstrip('#')
        r_val, g_val, b_val = tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))
        target_bgr = np.uint8([[[b_val, g_val, r_val]]])
        target_hsv = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2HSV)[0, 0]
        target_h = float(target_hsv[0])
        target_s = float(target_hsv[1])

        bgr = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
        h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

        # 1. Detect metallic gold and silver zari in traditional sarees
        if preserve_zari:
            gold_mask = ((h >= 12) & (h <= 42) & (s >= 35) & (v >= 95)).astype(np.float32)
            silver_mask = ((s < 30) & (v >= 170)).astype(np.float32)
            zari = np.clip(gold_mask + silver_mask, 0.0, 1.0)
            zari = cv2.GaussianBlur(zari, (7, 7), 0)
        else:
            zari = np.zeros_like(h)

        # 2. Detect neutral/white background (don't tint pure white studio background)
        bg_mask = ((s < 20) & (v > 235)).astype(np.float32)
        bg_mask = cv2.GaussianBlur(bg_mask, (5, 5), 0)

        # 3. Calculate fabric dyeing weight (1.0 = fully dyed fabric, 0.0 = preserved zari/bg)
        fabric_weight = np.clip((1.0 - zari * 0.92) * (1.0 - bg_mask * 0.98) * blend_intensity, 0.0, 1.0)
        fabric_weight_3d = fabric_weight[:, :, np.newaxis]

        # 4. Synthesize dyed fabric in HSV
        dyed_h = np.full_like(h, target_h)
        mean_s = np.mean(s) if np.mean(s) > 10 else 120.0
        sat_scale = np.clip(target_s / mean_s, 0.65, 1.5)
        dyed_s = np.clip(s * sat_scale, 35, 255)
        dyed_hsv = np.stack([dyed_h, dyed_s, v], axis=-1).astype(np.uint8)
        dyed_bgr = cv2.cvtColor(dyed_hsv, cv2.COLOR_HSV2BGR).astype(np.float32)

        # 5. Blend dyed fabric with original fabric to retain natural luster and fold depth
        orig_bgr = bgr.astype(np.float32)
        final_bgr = orig_bgr * (1.0 - fabric_weight_3d) + dyed_bgr * fabric_weight_3d
        final_bgr = np.clip(final_bgr, 0, 255).astype(np.uint8)
        final_rgb = cv2.cvtColor(final_bgr, cv2.COLOR_BGR2RGB)

        return final_rgb

    @classmethod
    def to_base64_data_url(cls, rgb_array: np.ndarray) -> str:
        pil_img = Image.fromarray(rgb_array, mode="RGB")
        buf = io.BytesIO()
        pil_img.save(buf, format="JPEG", quality=96)
        return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

