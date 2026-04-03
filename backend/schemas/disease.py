from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DiseaseDetectionResponse(BaseModel):
    id: int
    crop_type: str
    disease_name: str
    is_healthy: bool
    confidence: float
    severity: str
    severity_color: str
    description: str
    symptoms: List[str]
    treatment: List[str]
    prevention: List[str]
    is_demo_mode: bool
    image_path: Optional[str] = None
    original_filename: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DiseaseHistoryItem(BaseModel):
    id: int
    crop_type: str
    disease_name: str
    is_healthy: bool
    confidence_score: float
    severity: str
    original_filename: str
    image_path: Optional[str] = None
    is_demo_mode: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DiseaseStatsResponse(BaseModel):
    disease_distribution: List[dict]
    total_scans: int
    healthy_count: int
    diseased_count: int
