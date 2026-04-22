from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime

from app.database import get_db
from app.api.auth import get_current_user_dependency
from app.models.user import User
from app.models.detection import DetectionRecord
from pydantic import BaseModel

router = APIRouter(prefix="/profile", tags=["个人中心"])

class ProfileStatsOut(BaseModel):
    total_detections: int
    total_fruits: int
    recent_detections: List[dict]

@router.get("/stats", response_model=ProfileStatsOut)
def get_profile_stats(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    user_id = current_user.id
    
    total_detections = db.query(func.count(DetectionRecord.id))\
        .filter(DetectionRecord.user_id == user_id).scalar() or 0
    
    total_fruits = db.query(func.sum(DetectionRecord.fruit_count))\
        .filter(DetectionRecord.user_id == user_id).scalar() or 0
    
    recent = db.query(DetectionRecord)\
        .filter(DetectionRecord.user_id == user_id)\
        .order_by(DetectionRecord.created_at.desc())\
        .limit(5).all()
    
    recent_list = []
    for rec in recent:
        recent_list.append({ 
            "id": rec.id,
            "original_filename": rec.original_filename,
            "fruit_count": rec.fruit_count,
            "created_at": rec.created_at.isoformat() if rec.created_at else ""
        })
    
    return {
        "total_detections": total_detections,
        "total_fruits": total_fruits,
        "recent_detections": recent_list
    }