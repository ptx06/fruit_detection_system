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

class HistoryListOut(BaseModel):
    records: List[DetectionRecordOut]
    total: int

@router.get("", response_model=HistoryListOut)
def get_history_list(
    skip: int = 0,
    limit: int = 20,
    keyword: Optional[str] = None,
    fruit_type: Optional[str] = None,
    maturity: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    query = db.query(DetectionRecord).filter(DetectionRecord.user_id == current_user.id)
    
    # 按文件名搜索
    if keyword:
        query = query.filter(DetectionRecord.original_filename.like(f"%{keyword}%"))
    
    # 按水果类型筛选
    if fruit_type:
        query = query.filter(DetectionRecord.result_json.contains([{"fruit_type": fruit_type}]))
    
    # 按成熟度筛选（匹配实际的英文标签）
    if maturity:
        # 将前端传递的简化标签映射到实际的成熟度标签
        maturity_mapping = {
            'unripe': ['unripe apple', 'unripe banana', 'unripe orange'],
            'ripe': ['freshapples', 'freshbanana', 'freshoranges'],
            'overripe': ['rottenapples', 'rottenbanana', 'rottenoranges']
        }
        if maturity in maturity_mapping:
            # 使用 OR 查询匹配多个可能的标签
            from sqlalchemy import or_
            or_conditions = []
            for label in maturity_mapping[maturity]:
                or_conditions.append(DetectionRecord.result_json.contains([{"maturity": label}]))
            query = query.filter(or_(*or_conditions))
    
    # 按日期范围筛选
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
            query = query.filter(DetectionRecord.created_at >= start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
            query = query.filter(DetectionRecord.created_at <= end)
        except ValueError:
            pass
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    records = query\
        .order_by(DetectionRecord.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    # 返回结果包含总数
    return {"records": records, "total": total}

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