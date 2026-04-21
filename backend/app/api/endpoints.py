import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from PIL import Image
import io
import os
from datetime import datetime
import json

from app.services.inference import InferenceService
from app.utils.image_utils import pil_to_base64
from app.api.auth import get_current_user_dependency
from app.models.user import User
from app.database import get_db
from sqlalchemy.orm import Session
# from app.models.detection import DetectionRecord  # 第二步会创建，先注释或跳过

router = APIRouter()
inference_service = InferenceService()

# 配置上传图片保存目录
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/detect")
async def detect_fruit_maturity(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_dependency),  # 需要登录
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "仅支持图片格式")

    try:
        contents = await file.read()
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
        img_np = np.array(pil_img)

        # 执行推理
        results = inference_service.process(img_np)
        img_base64 = pil_to_base64(pil_img)

        # TODO: 第二步保存检测记录到数据库，暂时只返回结果

        return JSONResponse({
            "code": 200,
            "message": "success",
            "data": {
                "image_base64": img_base64,
                "detections": results,
                "count": len(results)
            }
        })
    except Exception as e:
        raise HTTPException(500, f"推理失败: {str(e)}")