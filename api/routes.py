import os
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Query
from fastapi.responses import JSONResponse

from config import (
    CLASSES,
    PRESET_SAREES_DIR,
    DEMO_PALETTES,
    MODEL_CHECKPOINT_PATH
)
from api.schemas import (
    HealthResponse,
    PredictionResponse,
    PresetSareeItem,
    ClassRanking,
    SimilarDesign
)
from training.dataset_loader import parse_class_from_filename
from preprocessing.image_processor import ImageValidationError

router = APIRouter(prefix="/api/v1")

# Global predictor reference (injected during startup in main.py)
predictor_instance = None

def get_predictor():
    global predictor_instance
    if predictor_instance is None:
        from inference.predictor import SareePredictor
        predictor_instance = SareePredictor()
    return predictor_instance


@router.get("/health", response_model=HealthResponse)
async def health_check():
    predictor = get_predictor()
    return HealthResponse(
        status="healthy",
        device=str(predictor.device),
        classes_count=len(CLASSES),
        model_loaded=predictor.model is not None
    )


@router.get("/classes")
async def get_design_classes():
    return {
        "classes": CLASSES,
        "count": len(CLASSES),
        "demo_palettes": DEMO_PALETTES
    }


@router.get("/presets", response_model=List[PresetSareeItem])
async def get_preset_sarees():
    """Returns curated preset sarees across design patterns and color themes."""
    items = []
    all_imgs = sorted(list(PRESET_SAREES_DIR.glob("*.jpg")))
    for p in all_imgs:
        cls_name = parse_class_from_filename(p.name) or "Unknown Design"
        color_theme = p.stem.split("__")[-1].replace("_", " ")
        items.append(PresetSareeItem(
            id=p.stem,
            design=cls_name,
            color_theme=color_theme,
            filename=p.name,
            image_url=f"/presets/{p.name}"
        ))
    return items


@router.post("/predict", response_model=PredictionResponse)
async def predict_saree_design(
    file: UploadFile = File(...)
):
    """
    Accepts an uploaded saree image, applies color-invariant transformations,
    and returns design predictions and similar designs.
    """
    predictor = get_predictor()
    try:
        content = await file.read()
        result = predictor.predict_image(content, filename=file.filename or "upload.jpg")
        return result
    except ImageValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@router.post("/recolor", response_model=PredictionResponse)
async def recolor_saree_and_predict(
    file: Optional[UploadFile] = File(None),
    preset_filename: Optional[str] = Form(None),
    target_hex: Optional[str] = Form(None),
    hue_shift_deg: Optional[float] = Form(None),
    preserve_zari: bool = Form(True),
    blend_intensity: float = Form(0.90)
):
    """
    Dynamically shifts or replaces the saree color and proves that the design
    recognition remains invariant to the new color.
    """
    predictor = get_predictor()
    try:
        if file is not None:
            content = await file.read()
            filename = file.filename or "uploaded_saree.jpg"
        elif preset_filename:
            target_file = PRESET_SAREES_DIR / preset_filename
            if not target_file.exists():
                raise HTTPException(status_code=404, detail=f"Preset {preset_filename} not found.")
            with open(target_file, "rb") as f:
                content = f.read()
            filename = preset_filename
        else:
            raise HTTPException(status_code=400, detail="Must provide either an uploaded file or a preset_filename.")

        result = predictor.recolor_and_predict(
            image_bytes=content,
            target_color_hex=target_hex,
            hue_shift_deg=hue_shift_deg,
            preserve_zari=preserve_zari,
            blend_intensity=blend_intensity,
            filename=filename
        )
        return result
    except ImageValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recoloring error: {str(e)}")


@router.post("/sarees/manual-add")
async def manual_add_saree(
    file: UploadFile = File(...),
    design_name: Optional[str] = Form(None),
    color_name: Optional[str] = Form(None)
):
    """
    Manually adds a user's saree into the system repository,
    indexes it for similarity search, and returns prediction & details.
    """
    predictor = get_predictor()
    try:
        content = await file.read()
        # Validate
        from preprocessing.image_processor import ImageProcessor
        pil_img = ImageProcessor.validate_image_bytes(content, filename=file.filename or "saree.jpg")
        
        # Get AI prediction to suggest design if not provided
        pred_result = predictor.predict_image(content, filename=file.filename or "saree.jpg")
        assigned_design = design_name if (design_name and design_name.strip()) else pred_result["predicted_design"]
        assigned_color = color_name if (color_name and color_name.strip()) else "Custom_Color"
        
        clean_design = assigned_design.replace(" ", "_").replace("(", "").replace(")", "").replace("&", "and")
        clean_color = assigned_color.replace(" ", "_")
        
        import uuid
        unique_suffix = uuid.uuid4().hex[:6]
        save_filename = f"{clean_design}__{clean_color}_{unique_suffix}.jpg"
        save_path = PRESET_SAREES_DIR / save_filename
        
        # Save image
        pil_img.save(save_path, format="JPEG", quality=95)
        
        # Re-index similarity search engine
        predictor.similarity_engine._index_reference_sarees()
        
        return {
            "success": True,
            "message": "Saree successfully added to library!",
            "id": save_path.stem,
            "filename": save_filename,
            "design": assigned_design,
            "color": assigned_color,
            "image_url": f"/presets/{save_filename}",
            "prediction": pred_result
        }
    except ImageValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add saree: {str(e)}")



@router.get("/benchmark")
async def get_benchmark_report():
    """Returns evaluation metrics and color-invariance stability benchmarks."""
    from evaluation.metrics import evaluate_model, run_color_invariance_stress_test
    try:
        eval_metrics = evaluate_model()
        stress_test = run_color_invariance_stress_test()
        return {
            "evaluation_metrics": eval_metrics,
            "color_invariance_stress_test": stress_test
        }
    except Exception as e:
        return {
            "status": "pending_or_partial",
            "message": f"Metrics calculation error: {str(e)}"
        }
