from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.disease_record import DiseaseDetection
from models.yield_record import YieldPrediction
from models.user import User
from utils.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_dashboard_stats(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        disease_records = db.query(DiseaseDetection).filter(DiseaseDetection.user_id == user.id).all()
        yield_records = db.query(YieldPrediction).filter(YieldPrediction.user_id == user.id).all()

        total_detections = len(disease_records)
        diseases_found = sum(1 for r in disease_records if not r.is_healthy)
        total_yield_preds = len(yield_records)
        avg_confidence = (
            sum(r.confidence_score for r in disease_records) / total_detections
            if total_detections > 0 else 0.0
        )

        return {
            "total_detections": total_detections,
            "diseases_found": diseases_found,
            "total_yield_predictions": total_yield_preds,
            "avg_confidence": round(avg_confidence * 100, 1),
            "healthy_plants": total_detections - diseases_found
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
def get_recent_activity(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        disease_records = db.query(DiseaseDetection).filter(
            DiseaseDetection.user_id == user.id
        ).order_by(DiseaseDetection.created_at.desc()).limit(5).all()

        yield_records = db.query(YieldPrediction).filter(
            YieldPrediction.user_id == user.id
        ).order_by(YieldPrediction.created_at.desc()).limit(5).all()

        activities = []
        for r in disease_records:
            activities.append({
                "id": r.id,
                "type": "disease",
                "icon": "leaf",
                "crop": r.crop_type,
                "result": r.disease_name,
                "is_healthy": r.is_healthy,
                "confidence": r.confidence_score,
                "created_at": r.created_at.isoformat()
            })
        for r in yield_records:
            activities.append({
                "id": r.id,
                "type": "yield",
                "icon": "trending-up",
                "crop": r.crop_type,
                "result": f"{r.predicted_yield:.1f} q/acre",
                "is_healthy": None,
                "confidence": None,
                "created_at": r.created_at.isoformat()
            })

        activities.sort(key=lambda x: x["created_at"], reverse=True)
        return {"recent_activity": activities[:10]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charts/disease")
def get_disease_chart(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        records = db.query(DiseaseDetection).filter(DiseaseDetection.user_id == user.id).all()
        disease_count = {}
        for r in records:
            key = "Healthy" if r.is_healthy else r.disease_name
            disease_count[key] = disease_count.get(key, 0) + 1

        chart_data = [{"name": k, "value": v} for k, v in
                      sorted(disease_count.items(), key=lambda x: -x[1])]
        return {"chart_data": chart_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charts/yield")
def get_yield_chart(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        records = db.query(YieldPrediction).filter(
            YieldPrediction.user_id == user.id
        ).order_by(YieldPrediction.created_at.asc()).limit(20).all()

        chart_data = [
            {
                "date": r.created_at.strftime("%b %d"),
                "yield": r.predicted_yield,
                "crop": r.crop_type
            }
            for r in records
        ]
        return {"chart_data": chart_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
