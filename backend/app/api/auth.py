from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserInfo
from app.utils.auth import get_password_hash, verify_password, create_access_token, decode_access_token, \
    ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

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
def login(user_data: UserLogin, db: Session = Depends(get_db)):
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
        "created_at": user.created_at.isoformat()
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