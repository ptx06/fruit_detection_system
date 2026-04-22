from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional          # 新增 Optional 导入
from app.database import get_db
from app.models.detection import DetectionRecord
from app.api.auth import get_current_user_dependency
from app.models.user import User
from pydantic import BaseModel
from datetime import datetime
import os
import base64

from app.utils.logger import log_action

from fastapi.responses import StreamingResponse
import io
import csv


router = APIRouter(prefix="/history", tags=["历史记录"])

class DetectionRecordOut(BaseModel):
    id: int
    original_filename: str
    fruit_count: int
    created_at: datetime
    image_base64: Optional[str] = None   # 修改处

class DetectionDetailOut(DetectionRecordOut):
    result_json: list

@router.get("", response_model=List[DetectionRecordOut])
def get_history_list(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    records = db.query(DetectionRecord)\
        .filter(DetectionRecord.user_id == current_user.id)\
        .order_by(DetectionRecord.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return records

@router.get("/{record_id}", response_model=DetectionDetailOut)
def get_history_detail(
    record_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    record = db.query(DetectionRecord)\
        .filter(DetectionRecord.id == record_id, DetectionRecord.user_id == current_user.id)\
        .first()
    if not record:
        raise HTTPException(404, "记录不存在")

    image_base64 = None
    if os.path.exists(record.image_path):
        with open(record.image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")

    return {
        "id": record.id,
        "original_filename": record.original_filename,
        "fruit_count": record.fruit_count,
        "created_at": record.created_at,
        "result_json": record.result_json,
        "image_base64": image_base64
    }


@router.get("/export/csv")
def export_history_csv(
        request: Request = None,
        current_user: User = Depends(get_current_user_dependency),
        db: Session = Depends(get_db)
):
    records = db.query(DetectionRecord) \
        .filter(DetectionRecord.user_id == current_user.id) \
        .order_by(DetectionRecord.created_at.desc()) \
        .all()

    output = io.StringIO()
    writer = csv.writer(output)

    # 写入 UTF-8 BOM 头（解决 Excel 中文乱码）
    output.write('\ufeff')

    writer.writerow(["记录ID", "文件名", "检测时间", "水果总数", "检测详情"])

    for rec in records:
        details = []
        if rec.result_json:
            for item in rec.result_json:
                fruit = item.get('fruit_type', '')
                maturity = item.get('maturity', '')
                details.append(f"{fruit}({maturity})")
        detail_str = "; ".join(details)
        writer.writerow([
            rec.id,
            rec.original_filename or "",
            rec.created_at.isoformat() if rec.created_at else "",
            rec.fruit_count or 0,
            detail_str
        ])

    output.seek(0)
    
    # 记录操作日志
    log_action(current_user.id, current_user.username, "导出", "导出检测历史CSV", request)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=fruit_detection_history.csv"}
    )