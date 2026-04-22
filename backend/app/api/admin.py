from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.api.auth import get_current_user_dependency
from app.models.user import User
from app.models.audit_log import AuditLog
from app.utils.logger import log_action

router = APIRouter(prefix="/admin", tags=["管理员"])


# 响应模型
class UserOut(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime


class UpdateRoleRequest(BaseModel):
    role: str  # 'admin' 或 'user'


# 权限验证依赖
def require_admin(current_user: User = Depends(get_current_user_dependency)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    return current_user


# 获取所有用户列表（仅管理员）
@router.get("/users", response_model=List[UserOut])
def list_users(
        admin: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users


# 修改用户角色
@router.put("/users/{user_id}/role")
def update_user_role(
        user_id: int,
        req: UpdateRoleRequest,
        request: Request = None,
        admin: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    if req.role not in ['admin', 'user']:
        raise HTTPException(status_code=400, detail="无效的角色")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 不允许修改自己的角色（防止把自己降级后无法操作）
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="不能修改自己的角色")

    user.role = req.role
    db.commit()
    
    # 记录操作日志
    log_action(admin.id, admin.username, "修改角色", f"将用户 {user.username} 的角色修改为 {req.role}", request)
    
    return {"message": "角色更新成功"}


# 删除用户
@router.delete("/users/{user_id}")
def delete_user(
        user_id: int,
        request: Request = None,
        admin: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    # 记录被删除用户的用户名
    deleted_username = user.username
    
    db.delete(user)
    db.commit()
    
    # 记录操作日志
    log_action(admin.id, admin.username, "删除用户", f"删除用户 {deleted_username}", request)
    
    return {"message": "用户删除成功"}


# 审计日志响应模型
class AuditLogOut(BaseModel):
    id: int
    username: str
    action: str
    details: Optional[str]
    ip_address: Optional[str]
    created_at: datetime


# 查看审计日志
@router.get("/logs", response_model=List[AuditLogOut])
def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs