import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import io

from app.services.inference import InferenceService
from app.utils.image_utils import pil_to_base64

router = APIRouter()
inference_service = InferenceService()

@router.post("/detect")
async def detect_fruit_maturity(file: UploadFile = File(...)):
    # 验证文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "仅支持图片格式")

    try:
        # 读取上传的图片
        contents = await file.read()
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
        img_np = np.array(pil_img)
        # OpenCV使用BGR格式，但YOLO接受RGB numpy数组，我们直接传入RGB即可
        # Ultralytics YOLO内部会自动处理

        # 执行推理
        results = inference_service.process(img_np)

        # 将原始图片转为base64便于前端展示（可选）
        img_base64 = pil_to_base64(pil_img)

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