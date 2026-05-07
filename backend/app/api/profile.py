from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
import os
from pathlib import Path

from app.database import get_db
from app.api.auth import get_current_user_dependency
from app.models.user import User
from app.models.detection import DetectionRecord
from pydantic import BaseModel

router = APIRouter(prefix="/profile", tags=["个人中心"])

# 确保上传目录存在
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads" / "avatars"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class ProfileStatsOut(BaseModel):
    total_detections: int
    total_fruits: int
    recent_detections: List[dict]

class ProfileUpdate(BaseModel):
    username: str
    bio: str = ""

class ProfileOut(BaseModel):
    username: str
    role: str
    created_at: datetime
    bio: str = ""
    avatar: str = ""

class AvatarOut(BaseModel):
    avatar: str

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

@router.put("", response_model=ProfileOut)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """更新用户资料"""
    current_user.username = profile_data.username
    current_user.bio = profile_data.bio
    db.commit()
    db.refresh(current_user)
    
    return ProfileOut(
        username=current_user.username,
        role=current_user.role,
        created_at=current_user.created_at,
        bio=current_user.bio or "",
        avatar=current_user.avatar or ""
    )

@router.post("/avatar", response_model=AvatarOut)
async def upload_avatar(
    avatar: UploadFile = File(...),
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """上传头像"""
    # 读取文件内容
    content = await avatar.read()
    
    # 1. 文件大小限制（2MB）
    MAX_FILE_SIZE = 2 * 1024 * 1024
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过 2MB")
    
    # 2. 通过 Magic Number 验证文件类型并确定扩展名
    # JPEG: \xff\xd8\xff, PNG: \x89PNG\r\n\x1a\n, GIF: GIF87a/GIF89a
    magic_number = content[:8]
    if magic_number.startswith(b'\xff\xd8\xff'):
        file_ext = 'jpg'
    elif magic_number.startswith(b'\x89PNG'):
        file_ext = 'png'
    elif magic_number.startswith(b'GIF87a') or magic_number.startswith(b'GIF89a'):
        file_ext = 'gif'
    else:
        raise HTTPException(status_code=400, detail="无效的图片文件格式")
    
    # 3. 生成安全的文件名（使用 uuid 避免路径遍历攻击）
    import uuid
    file_name = f"{current_user.id}_{uuid.uuid4().hex}.{file_ext}"
    file_path = UPLOAD_DIR / file_name
    
    # 4. 删除旧头像（如果存在）
    if current_user.avatar:
        old_avatar_name = current_user.avatar.split("/")[-1]
        old_avatar_path = UPLOAD_DIR / old_avatar_name
        if old_avatar_path.exists():
            old_avatar_path.unlink()
    
    # 5. 保存文件
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 6. 更新用户头像路径
    avatar_url = f"/uploads/avatars/{file_name}"
    current_user.avatar = avatar_url
    db.commit()
    
    return AvatarOut(avatar=avatar_url)