from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
from app.api.endpoints import router as detection_router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.history import router as history_router
from app.api.dashboard import router as dashboard_router
from app.api.system import router as system_router
from app.api.profile import router as profile_router
from app.api.settings import router as settings_router
from app.api.announcements import router as announcements_router
from app.api.feedback import router as feedback_router
from app.utils.logger import setup_logger
from app.database import engine, Base
from app.models import user  # 导入模型以创建表
from app.models import audit_log  # 导入审计日志模型以创建表
from app.models import announcement  # 导入公告模型以创建表
from app.models import feedback  # 导入反馈模型以创建表



# 确保上传目录存在
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
(UPLOAD_DIR / "avatars").mkdir(parents=True, exist_ok=True)

# 创建数据库表（如果不存在）
Base.metadata.create_all(bind=engine)

setup_logger()

app = FastAPI(
    title="水果成熟度分级系统 API",
    description="基于 YOLOv11 + MobileNetV2 的两阶段检测分类系统",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件服务
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# 注册路由
app.include_router(auth_router, prefix="/api/v1")
app.include_router(detection_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")
app.include_router(announcements_router, prefix="/api/v1")
app.include_router(feedback_router, prefix="/api/v1")
@app.get("/health")
async def health_check():
    return {"status": "ok"}