from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserInfo
from app.utils.auth import get_password_hash, verify_password, create_access_token, decode_access_token, \
    ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.logger_audit import log_action
from fastapi import Request

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer()


# 注册
@router.post("/register", response_model=TokenResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 创建新用户
    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(username=user_data.username, password_hash=hashed_pwd, role="user")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 生成token
    access_token = create_access_token(data={"sub": new_user.username, "role": new_user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": new_user.username,
        "role": new_user.role
    }


# 登录
@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db), request:Request = None):
    # 查找用户
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 生成token
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role
    }
    log_action(user.id, user.username, "登录", f"用户登录成功", request)

# 获取当前用户信息（需要认证）
@router.get("/me", response_model=UserInfo)
def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效或过期的令牌")

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="无效令牌")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "created_at": user.created_at.isoformat(),
        "bio": user.bio or "",
        "avatar": user.avatar or ""
    }


# 依赖项：获取当前用户（用于其他API保护）
async def get_current_user_dependency(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效或过期的令牌")
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user

# 依赖项：要求管理员权限
async def require_admin(current_user: User = Depends(get_current_user_dependency)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


# 修改密码
@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db),
    request: Request = None
):
    # 验证旧密码
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="旧密码错误")
    
    # 更新密码
    current_user.password_hash = get_password_hash(req.new_password)
    db.commit()
    
    # 记录日志
    log_action(current_user.id, current_user.username, "修改密码", "用户修改了密码", request)
    return {"message": "密码修改成功"}