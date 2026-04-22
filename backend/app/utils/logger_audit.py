from app.database import SessionLocal
from app.models.audit_log import AuditLog
from fastapi import Request

def log_action(user_id: int, username: str, action: str, details: str = None, request: Request = None):
    """记录审计日志"""
    db = SessionLocal()
    try:
        ip = request.client.host if request else None
        log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            details=details,
            ip_address=ip
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"审计日志记录失败: {e}")
    finally:
        db.close()