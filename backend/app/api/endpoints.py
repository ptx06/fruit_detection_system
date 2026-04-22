import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from PIL import Image
import io
import os
import uuid
from datetime import datetime
import json

from concurrent.futures import ThreadPoolExecutor
import asyncio

from app.services.inference import InferenceService
from app.utils.image_utils import pil_to_base64
from app.utils.logger import log_action
from app.api.auth import get_current_user_dependency
from app.models.user import User
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.detection import DetectionRecord

router = APIRouter()
inference_service = InferenceService()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/detect")
async def detect_fruit_maturity(
    file: UploadFile = File(...),
    request: Request = None,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "仅支持图片格式")

    try:
        contents = await file.read()
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
        img_np = np.array(pil_img)

        # 推理
        results = inference_service.process(img_np)
        img_base64 = pil_to_base64(pil_img)

        # 保存图片到本地
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        filename = f"{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(contents)

        # 保存记录到数据库
        record = DetectionRecord(
            user_id=current_user.id,
            image_path=file_path,
            original_filename=file.filename,
            result_json=results,
            fruit_count=len(results)
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        # 记录操作日志
        log_action(current_user.id, current_user.username, "检测", f"检测图片: {file.filename}", request)

        return JSONResponse({
            "code": 200,
            "message": "success",
            "data": {
                "record_id": record.id,
                "image_base64": img_base64,
                "detections": results,
                "count": len(results)
            }
        })
    except Exception as e:
        raise HTTPException(500, f"推理失败: {str(e)}")






# 批量检测接口
@router.post("/detect/batch")
async def detect_batch(
        files: list[UploadFile] = File(...),
        current_user: User = Depends(get_current_user_dependency),
        db: Session = Depends(get_db)
):
    if len(files) > 10:  # 限制最多10张
        raise HTTPException(400, "单次最多上传10张图片")

    executor = ThreadPoolExecutor(max_workers=4)
    results = []

    async def process_one(file: UploadFile):
        try:
            contents = await file.read()
            pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
            img_np = np.array(pil_img)

            # 推理
            detections = inference_service.process(img_np)

            # 保存图片
            file_ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
            filename = f"{uuid.uuid4().hex}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as f:
                f.write(contents)

            # 保存记录
            record = DetectionRecord(
                user_id=current_user.id,
                image_path=file_path,
                original_filename=file.filename,
                result_json=detections,
                fruit_count=len(detections)
            )
            db.add(record)
            db.commit()
            db.refresh(record)

            return {
                "filename": file.filename,
                "success": True,
                "record_id": record.id,
                "fruit_count": len(detections),
                "detections": detections
            }
        except Exception as e:
            return {
                "filename": file.filename,
                "success": False,
                "error": str(e)
            }

    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(executor, asyncio.ensure_future, process_one(file)) for file in files]
    # 简化处理：实际使用 asyncio.gather
    # 由于 run_in_executor 配合 async 较复杂，改用同步方式在线程池中运行整个批处理
    # 这里采用更简单的方式：逐个处理，但可以后续优化为真正并发
    # 为了快速实现，我们改为顺序处理：
    results = []
    for file in files:
        res = await process_one(file)
        results.append(res)

    return JSONResponse({
        "code": 200,
        "message": "批量检测完成",
        "data": results
    })