import hashlib
import secrets
import hmac
import base64
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

# ====================== 密码哈希（使用 PBKDF2） ======================
ITERATIONS = 100000        # PBKDF2 迭代次数
SALT_LENGTH = 16           # 盐长度（字节）
HASH_NAME = 'sha256'       # 哈希算法
KEY_LENGTH = 32            # 输出哈希长度（字节）

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    hashed_password 格式：pbkdf2_sha256$迭代次数$salt(base64)$hash(base64)
    """
    try:
        algo, iters, salt_b64, stored_hash_b64 = hashed_password.split('$')
        iterations = int(iters)
        salt = base64.b64decode(salt_b64)
        stored_hash = base64.b64decode(stored_hash_b64)
    except Exception:
        return False

    new_hash = hashlib.pbkdf2_hmac(
        HASH_NAME,
        plain_password.encode('utf-8'),
        salt,
        iterations,
        dklen=len(stored_hash)
    )
    return hmac.compare_digest(new_hash, stored_hash)

def get_password_hash(password: str) -> str:
    """生成密码哈希字符串"""
    salt = secrets.token_bytes(SALT_LENGTH)
    hash_bytes = hashlib.pbkdf2_hmac(
        HASH_NAME,
        password.encode('utf-8'),
        salt,
        ITERATIONS,
        dklen=KEY_LENGTH
    )
    salt_b64 = base64.b64encode(salt).decode('ascii')
    hash_b64 = base64.b64encode(hash_bytes).decode('ascii')
    return f"pbkdf2_{HASH_NAME}${ITERATIONS}${salt_b64}${hash_b64}"

# ====================== JWT 令牌管理 ======================
SECRET_KEY = "your-secret-key-change-in-production"   # 生产环境请务必更换为随机字符串
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24   # 24 小时

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """生成 JWT 访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """解码 JWT 令牌，无效或过期返回 None"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None