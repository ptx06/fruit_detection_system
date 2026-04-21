from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as detection_router
from app.api.auth import router as auth_router
from app.utils.logger import setup_logger
from app.database import engine, Base
from app.models import user  # 导入模型以创建表

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

# 注册路由
app.include_router(auth_router, prefix="/api/v1")
app.include_router(detection_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok"}