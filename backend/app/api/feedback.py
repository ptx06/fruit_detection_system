from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.api.auth import get_current_user_dependency, require_admin
from app.models.user import User
from app.models.feedback import Feedback, FeedbackStatus
from app.database import get_db

router = APIRouter(prefix="/feedback", tags=["反馈管理"])

class FeedbackBase(BaseModel):
    title: str
    content: str

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackUpdate(BaseModel):
    status: FeedbackStatus
    admin_reply: Optional[str] = None

class FeedbackResponse(FeedbackBase):
    id: int
    user_id: int
    status: FeedbackStatus
    admin_reply: Optional[str] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

@router.post("", response_model=FeedbackResponse)
async def create_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """提交反馈（所有用户）"""
    db_feedback = Feedback(
        title=feedback.title,
        content=feedback.content,
        user_id=current_user.id
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

@router.get("", response_model=List[FeedbackResponse])
async def get_feedback(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """获取反馈列表（用户只能看到自己的，管理员可以看到所有）"""
    if current_user.role == "admin":
        feedbacks = db.query(Feedback).order_by(Feedback.created_at.desc()).offset(skip).limit(limit).all()
    else:
        feedbacks = db.query(Feedback).filter(Feedback.user_id == current_user.id).order_by(Feedback.created_at.desc()).offset(skip).limit(limit).all()
    return feedbacks

@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback_detail(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """获取反馈详情"""
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")
    # 检查权限：只有反馈的创建者或管理员可以查看
    if feedback.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限查看此反馈")
    return feedback

@router.put("/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
    feedback_id: int,
    feedback_update: FeedbackUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """更新反馈（仅管理员）"""
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")
    feedback.status = feedback_update.status
    if feedback_update.admin_reply is not None:
        feedback.admin_reply = feedback_update.admin_reply
    db.commit()
    db.refresh(feedback)
    return feedback

@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """删除反馈（仅反馈创建者或管理员）"""
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")
    # 检查权限：只有反馈的创建者或管理员可以删除
    if feedback.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限删除此反馈")
    db.delete(feedback)
    db.commit()
    return {"message": "反馈已删除"}