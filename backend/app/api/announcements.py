from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.api.auth import get_current_user_dependency, require_admin
from app.models.user import User
from app.models.announcement import Announcement
from app.database import get_db

router = APIRouter(prefix="/announcements", tags=["公告管理"])

class AnnouncementBase(BaseModel):
    title: str
    content: str

class AnnouncementCreate(AnnouncementBase):
    pass

class AnnouncementResponse(AnnouncementBase):
    id: int
    created_by: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

@router.get("", response_model=List[AnnouncementResponse])
async def get_announcements(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """获取公告列表（所有用户可见）"""
    announcements = db.query(Announcement).order_by(Announcement.created_at.desc()).offset(skip).limit(limit).all()
    return announcements

@router.post("", response_model=AnnouncementResponse)
async def create_announcement(
    announcement: AnnouncementCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """创建公告（仅管理员）"""
    db_announcement = Announcement(
        title=announcement.title,
        content=announcement.content,
        created_by=admin.id
    )
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)
    return db_announcement

@router.delete("/{announcement_id}")
async def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """删除公告（仅管理员）"""
    db_announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not db_announcement:
        raise HTTPException(status_code=404, detail="公告不存在")
    db.delete(db_announcement)
    db.commit()
    return {"message": "公告已删除"}