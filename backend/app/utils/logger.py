import logging
import sys
from app.config import LOG_LEVEL
from app.database import SessionLocal
from app.models.audit_log import AuditLog
from fastapi import Request

def setup_logger():
    """配置全局日志格式和级别"""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    # 可选：降低第三方库日志冗余
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("ultralytics").setLevel(logging.WARNING)

def log_action(user_id: int, username: str, action: str, details: str, request: Request):
    """记录用户操作日志"""
    db = SessionLocal()
    try:
        ip_address = request.client.host if request.client else None
        log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            details=details,
            ip_address=ip_address
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logging.error(f"记录日志失败: {str(e)}")
    finally:
        db.close()