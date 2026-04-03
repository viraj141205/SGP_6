from database import Base
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime


class DiseaseDetection(Base):
    __tablename__ = "disease_detections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_filename = Column(String, nullable=False)
    image_path = Column(String, nullable=True)
    crop_type = Column(String, nullable=False)
    disease_name = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    severity = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    treatment_plan = Column(Text, nullable=True)  # JSON string
    preventive_measures = Column(Text, nullable=True)  # JSON string
    is_healthy = Column(Boolean, default=False)
    is_demo_mode = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="disease_records")
