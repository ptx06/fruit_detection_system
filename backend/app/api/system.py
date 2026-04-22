from fastapi import APIRouter
from app.config import MODEL_INFO

router = APIRouter(prefix="/system", tags=["系统信息"])

@router.get("/model-info")
def get_model_info():
    return MODEL_INFO