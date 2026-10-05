import io
from pathlib import Path
from typing import Tuple, Union, Optional
from PIL import Image, ImageOps
import numpy as np
import cv2

from config import IMAGE_SIZE, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES


class ImageValidationError(Exception):
    """Raised when an uploaded image fails validation."""
    pass


class ImageProcessor:
    """Handles image validation, noise reduction, and standard resizing."""

    @staticmethod
    def validate_image_bytes(image_bytes: bytes, filename: str = "upload.jpg") -> Image.Image:
        """
        Validates file size, extension, dimensions, and integrity.
        Returns a PIL Image in RGB format.
        """
        if len(image_bytes) == 0:
            raise ImageValidationError("Uploaded image is empty.")

        if len(image_bytes) > MAX_FILE_SIZE_BYTES:
            raise ImageValidationError(
                f"File size exceeds maximum allowed limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
            )

        suffix = Path(filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS and suffix != "":
            raise ImageValidationError(
                f"Unsupported file format '{suffix}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.verify()  # Check for corruption
            # Reopen after verify()
            image = Image.open(io.BytesIO(image_bytes))
            # Auto-orient if EXIF orientation metadata exists
            image = ImageOps.exif_transpose(image)
            image = image.convert("RGB")
        except Exception as e:
            raise ImageValidationError(f"Invalid or corrupted image file: {str(e)}")

        width, height = image.size
        if width < 32 or height < 32:
            raise ImageValidationError(f"Image dimensions ({width}x{height}) are too small (minimum 32x32).")
        if width > 4096 or height > 4096:
            raise ImageValidationError(f"Image dimensions ({width}x{height}) are too large (maximum 4096x4096).")

        return image

    @staticmethod
    def resize_and_denoise(
        image: Union[Image.Image, np.ndarray],
        target_size: Tuple[int, int] = IMAGE_SIZE
    ) -> np.ndarray:
        """
        Converts to numpy RGB array, resizes using high-quality anti-aliasing,
        and applies gentle bilateral or Gaussian filtering to suppress sensor noise
        while preserving sharp weave and border edges.
        """
        if isinstance(image, Image.Image):
            np_img = np.array(image)
        else:
            np_img = image.copy()

        # Resize to standard model input dimensions
        resized = cv2.resize(np_img, target_size, interpolation=cv2.INTER_AREA)

        # Bilateral filter preserves sharp motif edges while smoothing fabric sensor noise
        denoised = cv2.bilateralFilter(resized, d=5, sigmaColor=35, sigmaSpace=35)
        return denoised
