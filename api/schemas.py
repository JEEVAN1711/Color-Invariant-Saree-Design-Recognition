from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    device: str
    classes_count: int
    model_loaded: bool


class ClassRanking(BaseModel):
    class_name: str
    probability: float
    percentage: float


class SimilarDesign(BaseModel):
    design: str
    color: str
    filename: str
    image_url: str
    similarity_score: float
    match_percentage: float


class PredictionResponse(BaseModel):
    success: bool
    filename: str
    predicted_design: str
    confidence: float
    confidence_percentage: float
    class_rankings: List[ClassRanking]
    embedding_sample: List[float]
    embedding_dim: int
    visual_stages: Dict[str, str]
    similar_designs: List[SimilarDesign]
    recolored_image: Optional[str] = None
    applied_color_hex: Optional[str] = None
    applied_hue_shift: Optional[float] = None


class PresetSareeItem(BaseModel):
    id: str
    design: str
    color_theme: str
    filename: str
    image_url: str


class RecolorRequest(BaseModel):
    preset_filename: Optional[str] = None
    target_hex: Optional[str] = None
    hue_shift_deg: Optional[float] = None
