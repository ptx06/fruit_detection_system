from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict

from app.database import get_db
from app.api.auth import get_current_user_dependency
from app.models.user import User
from app.models.detection import DetectionRecord

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])

@router.get("/stats")
def get_dashboard_stats(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    user_id = current_user.id

    # 总检测次数
    total_detections = db.query(func.count(DetectionRecord.id))\
        .filter(DetectionRecord.user_id == user_id)\
        .scalar() or 0

    # 总水果数量
    total_fruits = db.query(func.sum(DetectionRecord.fruit_count))\
        .filter(DetectionRecord.user_id == user_id)\
        .scalar() or 0

    # 各水果种类分布（从 result_json 中统计）
    # 因为 result_json 是 JSON 字段，在 MySQL 中可以用 JSON 函数，但为了跨数据库兼容，我们查出所有记录的 result_json，在 Python 中聚合。
    records = db.query(DetectionRecord.result_json)\
        .filter(DetectionRecord.user_id == user_id)\
        .all()

    fruit_type_counts = defaultdict(int)
    maturity_counts = defaultdict(int)
    daily_counts = defaultdict(int)  # 近7天每日检测次数

    # 计算近7天的日期范围
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=6)

    # 处理每条记录的 JSON 数据
    for (result_json,) in records:
        if not result_json:
            continue
        for item in result_json:
            fruit_type = item.get("fruit_type")
            maturity = item.get("maturity")
            if fruit_type:
                fruit_type_counts[fruit_type] += 1
            if maturity:
                maturity_counts[maturity] += 1

    # 获取近7天的检测记录（按日期分组计数）
    daily_records = db.query(
        func.date(DetectionRecord.created_at).label("date"),
        func.count(DetectionRecord.id).label("count")
    ).filter(
        and_(
            DetectionRecord.user_id == user_id,
            func.date(DetectionRecord.created_at) >= seven_days_ago,
            func.date(DetectionRecord.created_at) <= today
        )
    ).group_by(func.date(DetectionRecord.created_at)).all()

    # 补全缺失的日期，确保图表连续
    date_list = [(seven_days_ago + timedelta(days=i)).isoformat() for i in range(7)]
    daily_data = {date: 0 for date in date_list}
    for date, count in daily_records:
        daily_data[date.isoformat()] = count

    return {
        "total_detections": total_detections,
        "total_fruits": total_fruits,
        "fruit_distribution": dict(fruit_type_counts),
        "maturity_distribution": dict(maturity_counts),
        "daily_trend": [{"date": d, "count": daily_data[d]} for d in date_list]
    }