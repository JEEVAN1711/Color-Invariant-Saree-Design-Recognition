import pytest
import numpy as np
from PIL import Image
from preprocessing.image_processor import ImageProcessor, ImageValidationError
from preprocessing.color_invariance import ColorInvariantTransformer, SareeColorShifter


def test_image_processor_valid_image():
    # Create simple dummy RGB image in memory
    arr = (np.random.rand(100, 100, 3) * 255).astype(np.uint8)
    img = Image.fromarray(arr)
    
    import io
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    raw_bytes = buf.getvalue()

    validated = ImageProcessor.validate_image_bytes(raw_bytes, "test.jpg")
    assert validated.size == (100, 100)

    denoised = ImageProcessor.resize_and_denoise(validated, (224, 224))
    assert denoised.shape == (224, 224, 3)


def test_image_processor_invalid_bytes():
    with pytest.raises(ImageValidationError):
        ImageProcessor.validate_image_bytes(b"not an image", "test.jpg")


def test_color_invariance_transforms():
    arr = (np.random.rand(224, 224, 3) * 255).astype(np.uint8)
    composite = ColorInvariantTransformer.create_color_invariant_composite(arr)
    assert composite.shape == (224, 224, 3)
    assert composite.dtype == np.uint8

    stages = ColorInvariantTransformer.get_visual_stages(arr)
    assert "luminance_map" in stages
    assert "edge_map" in stages
    assert "texture_map" in stages
    assert "composite_invariant" in stages
    assert stages["composite_invariant"].startswith("data:image/png;base64,")


def test_saree_color_shifter():
    arr = np.full((100, 100, 3), [180, 20, 20], dtype=np.uint8)  # Red fabric
    shifted = SareeColorShifter.shift_hue(arr, 120.0)
    assert shifted.shape == (100, 100, 3)

    recolored = SareeColorShifter.recolor_to_target_hex(arr, "#1864AB")  # Royal blue
    assert recolored.shape == (100, 100, 3)
