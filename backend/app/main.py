from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as detection_router
from app.utils.logger import setup_logger

# 初始化日志
setup_logger()

app = FastAPI(
    title="水果成熟度分级系统 API",
    description="基于 YOLOv11 + MobileNetV2 的两阶段检测分类系统",
    version="1.0.0"
)

# 配置 CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(detection_router, prefix="/api/v1", tags=["detection"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}