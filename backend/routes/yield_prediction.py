import json
import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.yield_record import YieldPrediction
from models.user import User
from schemas.yield_pred import YieldPredictionInput
from utils.auth import get_current_user
from utils.response import paginated_response
from ml.model_loader import get_yield_predictor

router = APIRouter(prefix="/api/yield", tags=["yield"])

SUPPORTED_CROPS = [
    "Rice", "Wheat", "Maize", "Cotton", "Sugarcane", "Soybean", "Tomato",
    "Potato", "Onion", "Mustard", "Groundnut", "Sunflower", "Bajra", "Jowar",
    "Barley", "Chickpea", "Lentil", "Mango", "Banana", "Grapes", "Turmeric", "Ginger"
]

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan",
    "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
    "Uttarakhand", "West Bengal", "Other"
]


@router.get("/crops")
def get_crops():
    return {"crops": SUPPORTED_CROPS}


@router.get("/regions")
def get_regions():
    return {"regions": INDIAN_STATES}


@router.post("/predict")
def predict_yield(
    input_data: YieldPredictionInput,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.email == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        predictor = get_yield_predictor()
        data_dict = input_data.model_dump()
        result = predictor.predict(data_dict)

        record = YieldPrediction(
            user_id=user.id,
            crop_type=input_data.crop_type,
            region=input_data.region,
            season=input_data.season,
            area_acres=input_data.area_acres,
            soil_type=input_data.soil_type,
            soil_ph=input_data.soil_ph,
            nitrogen=input_data.nitrogen,
            phosphorus=input_data.phosphorus,
            potassium=input_data.potassium,
            rainfall=input_data.rainfall,
            temperature=input_data.temperature,
            humidity=input_data.humidity,
            predicted_yield=result["predicted_yield"],
            avg_yield_for_crop=result["avg_yield_for_crop"],
            confidence_lower=result["confidence_lower"],
            confidence_upper=result["confidence_upper"],
            recommendations=json.dumps(result["recommendations"]),
            is_demo_mode=result["is_demo_mode"]
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        return {
            "id": record.id,
            "crop_type": input_data.crop_type,
            "predicted_yield": result["predicted_yield"],
            "yield_unit": result["yield_unit"],
            "confidence_lower": result["confidence_lower"],
            "confidence_upper": result["confidence_upper"],
            "avg_yield_for_crop": result["avg_yield_for_crop"],
            "yield_comparison": result["yield_comparison"],
            "performance_rating": result["performance_rating"],
            "recommendations": result["recommendations"],
            "model_used": result["model_used"],
            "is_demo_mode": result["is_demo_mode"],
            "created_at": record.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/history")
def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    search: str = Query(None),
    season: str = Query(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.email == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        query = db.query(YieldPrediction).filter(YieldPrediction.user_id == user.id)
        if search:
            query = query.filter(
                (YieldPrediction.crop_type.ilike(f"%{search}%")) |
                (YieldPrediction.region.ilike(f"%{search}%"))
            )
        if season:
            query = query.filter(YieldPrediction.season == season)

        total = query.count()
        records = query.order_by(YieldPrediction.created_at.desc()) \
                       .offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for r in records:
            items.append({
                "id": r.id,
                "crop_type": r.crop_type,
                "region": r.region,
                "season": r.season,
                "area_acres": r.area_acres,
                "predicted_yield": r.predicted_yield,
                "confidence_lower": r.confidence_lower,
                "confidence_upper": r.confidence_upper,
                "is_demo_mode": r.is_demo_mode,
                "created_at": r.created_at.isoformat()
            })
        return paginated_response(items, total, page, page_size)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
def get_stats(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        records = db.query(YieldPrediction).filter(YieldPrediction.user_id == user.id) \
                    .order_by(YieldPrediction.created_at.asc()).all()

        trend_data = [
            {"date": r.created_at.strftime("%b %d"), "yield": r.predicted_yield, "crop": r.crop_type}
            for r in records[-20:]
        ]

        avg_yield = sum(r.predicted_yield for r in records) / len(records) if records else 0

        crop_counts = {}
        for r in records:
            crop_counts[r.crop_type] = crop_counts.get(r.crop_type, 0) + 1

        top_crops = [{"crop": k, "count": v} for k, v in
                     sorted(crop_counts.items(), key=lambda x: -x[1])[:5]]

        return {
            "trend_data": trend_data,
            "avg_predicted_yield": round(avg_yield, 2),
            "total_predictions": len(records),
            "top_crops": top_crops
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{record_id}")
def get_record(record_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == current_user["sub"]).first()
        record = db.query(YieldPrediction).filter(
            YieldPrediction.id == record_id,
            YieldPrediction.user_id == user.id
        ).first()
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        return {
            "id": record.id,
            "crop_type": record.crop_type,
            "region": record.region,
            "season": record.season,
            "area_acres": record.area_acres,
            "soil_type": record.soil_type,
            "soil_ph": record.soil_ph,
            "nitrogen": record.nitrogen,
            "phosphorus": record.phosphorus,
            "potassium": record.potassium,
            "rainfall": record.rainfall,
            "temperature": record.temperature,
            "humidity": record.humidity,
            "predicted_yield": record.predicted_yield,
            "avg_yield_for_crop": record.avg_yield_for_crop,
            "confidence_lower": record.confidence_lower,
            "confidence_upper": record.confidence_upper,
            "recommendations": json.loads(record.recommendations or "[]"),
            "is_demo_mode": record.is_demo_mode,
            "created_at": record.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{record_id}")
def delete_record(record_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == current_user["sub"]).first()
        record = db.query(YieldPrediction).filter(
            YieldPrediction.id == record_id,
            YieldPrediction.user_id == user.id
        ).first()
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        db.delete(record)
        db.commit()
        return {"message": "Record deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
