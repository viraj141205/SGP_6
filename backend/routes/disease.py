import json
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models.disease_record import DiseaseDetection
from models.user import User
from utils.auth import get_current_user
from utils.image_processing import preprocess_image_for_model, save_uploaded_image, validate_image
from utils.response import paginated_response
from ml.model_loader import get_disease_predictor

router = APIRouter(prefix="/api/disease", tags=["disease"])


@router.post("/detect")
async def detect_disease(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.email == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files are accepted")

        contents = await file.read()
        validate_image(contents)

        img_array = preprocess_image_for_model(contents, target_size=(128, 128))
        predictor = get_disease_predictor()
        result = predictor.predict(img_array)

        image_path = save_uploaded_image(contents, file.filename or "upload.jpg",
                                         upload_dir=os.getenv("UPLOAD_DIR", "uploads"))

        record = DiseaseDetection(
            user_id=user.id,
            original_filename=file.filename or "upload.jpg",
            image_path=image_path,
            crop_type=result["crop_type"],
            disease_name=result["disease_name"],
            confidence_score=result["confidence"],
            severity=result["severity"],
            description=result["description"],
            treatment_plan=json.dumps(result["treatment"]),
            preventive_measures=json.dumps(result["prevention"]),
            is_healthy=result["is_healthy"],
            is_demo_mode=result["is_demo_mode"]
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        return {
            "id": record.id,
            "crop_type": result["crop_type"],
            "disease_name": result["disease_name"],
            "is_healthy": result["is_healthy"],
            "confidence": result["confidence"],
            "severity": result["severity"],
            "severity_color": result["severity_color"],
            "description": result["description"],
            "symptoms": result["symptoms"],
            "treatment": result["treatment"],
            "prevention": result["prevention"],
            "is_demo_mode": result["is_demo_mode"],
            "image_path": image_path,
            "original_filename": file.filename,
            "created_at": record.created_at.isoformat()
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@router.get("/history")
def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    search: str = Query(None),
    filter_type: str = Query(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.email == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        query = db.query(DiseaseDetection).filter(DiseaseDetection.user_id == user.id)

        if search:
            query = query.filter(
                (DiseaseDetection.crop_type.ilike(f"%{search}%")) |
                (DiseaseDetection.disease_name.ilike(f"%{search}%"))
            )
        if filter_type == "healthy":
            query = query.filter(DiseaseDetection.is_healthy == True)
        elif filter_type == "diseased":
            query = query.filter(DiseaseDetection.is_healthy == False)

        total = query.count()
        records = query.order_by(DiseaseDetection.created_at.desc()) \
                       .offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for r in records:
            items.append({
                "id": r.id,
                "crop_type": r.crop_type,
                "disease_name": r.disease_name,
                "is_healthy": r.is_healthy,
                "confidence_score": r.confidence_score,
                "severity": r.severity,
                "original_filename": r.original_filename,
                "image_path": r.image_path,
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

        records = db.query(DiseaseDetection).filter(DiseaseDetection.user_id == user.id).all()
        total = len(records)
        healthy = sum(1 for r in records if r.is_healthy)
        diseased = total - healthy

        disease_count = {}
        for r in records:
            if not r.is_healthy:
                disease_count[r.disease_name] = disease_count.get(r.disease_name, 0) + 1

        distribution = [{"name": k, "value": v} for k, v in
                        sorted(disease_count.items(), key=lambda x: -x[1])[:8]]

        return {
            "disease_distribution": distribution,
            "total_scans": total,
            "healthy_count": healthy,
            "diseased_count": diseased
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{record_id}")
def get_record(record_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == current_user["sub"]).first()
        record = db.query(DiseaseDetection).filter(
            DiseaseDetection.id == record_id,
            DiseaseDetection.user_id == user.id
        ).first()
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        return {
            "id": record.id,
            "crop_type": record.crop_type,
            "disease_name": record.disease_name,
            "is_healthy": record.is_healthy,
            "confidence_score": record.confidence_score,
            "severity": record.severity,
            "description": record.description,
            "treatment_plan": json.loads(record.treatment_plan or "[]"),
            "preventive_measures": json.loads(record.preventive_measures or "[]"),
            "original_filename": record.original_filename,
            "image_path": record.image_path,
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
        record = db.query(DiseaseDetection).filter(
            DiseaseDetection.id == record_id,
            DiseaseDetection.user_id == user.id
        ).first()
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        if record.image_path and os.path.exists(record.image_path):
            os.remove(record.image_path)
        db.delete(record)
        db.commit()
        return {"message": "Record deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
