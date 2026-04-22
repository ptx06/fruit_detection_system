from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.api.auth import get_current_user_dependency, require_admin
from app.models.user import User
from app.utils.settings_manager import load_settings, save_settings

router = APIRouter(prefix="/settings", tags=["系统设置"])

class DetectionSettings(BaseModel):
    conf_threshold: float
    iou_threshold: float

class SystemSettings(BaseModel):
    detection: DetectionSettings

@router.get("", response_model=SystemSettings)
def get_settings(admin: User = Depends(require_admin)):
    """获取当前系统设置（仅管理员）"""
    return load_settings()

@router.put("")
def update_settings(settings: SystemSettings, admin: User = Depends(require_admin)):
    """更新系统设置（仅管理员）"""
    # 简单校验
    if not (0.01 <= settings.detection.conf_threshold <= 1.0):
        raise HTTPException(400, "置信度阈值必须在0.01~1.0之间")
    if not (0.01 <= settings.detection.iou_threshold <= 1.0):
        raise HTTPException(400, "IOU阈值必须在0.01~1.0之间")
    
    save_settings(settings.dict())
    return {"message": "设置已更新"}