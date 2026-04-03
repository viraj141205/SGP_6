from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class YieldPredictionInput(BaseModel):
    crop_type: str
    region: Optional[str] = "Unknown"
    season: Optional[str] = "Kharif"
    area_acres: Optional[float] = Field(default=1.0, gt=0)
    soil_type: Optional[str] = "Loam"
    soil_ph: Optional[float] = Field(default=6.5, ge=0, le=14)
    nitrogen: Optional[float] = Field(default=60.0, ge=0)
    phosphorus: Optional[float] = Field(default=40.0, ge=0)
    potassium: Optional[float] = Field(default=40.0, ge=0)
    rainfall: Optional[float] = Field(default=800.0, ge=0)
    temperature: Optional[float] = Field(default=25.0)
    humidity: Optional[float] = Field(default=65.0, ge=0, le=100)


class YieldPredictionResponse(BaseModel):
    id: int
    crop_type: str
    predicted_yield: float
    yield_unit: str
    confidence_lower: float
    confidence_upper: float
    avg_yield_for_crop: float
    yield_comparison: str
    performance_rating: str
    recommendations: List[str]
    model_used: str
    is_demo_mode: bool
    created_at: datetime

    class Config:
        from_attributes = True


class YieldHistoryItem(BaseModel):
    id: int
    crop_type: str
    region: Optional[str]
    season: Optional[str]
    area_acres: Optional[float]
    predicted_yield: float
    confidence_lower: Optional[float]
    confidence_upper: Optional[float]
    is_demo_mode: bool
    created_at: datetime

    class Config:
        from_attributes = True


class YieldStatsResponse(BaseModel):
    trend_data: List[dict]
    avg_predicted_yield: float
    total_predictions: int
    top_crops: List[dict]
