from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from app.database import get_db
from app.api.auth import get_current_user_dependency
from app.models.user import User
from app.models.detection import DetectionRecord
from app.utils.logger import log_action

router = APIRouter()

@router.post("/ai/summary")
async def generate_ai_summary(
    request_data: dict,
    request: Request,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    try:
        # 解析请求参数
        start_date = request_data.get('start_date')
        end_date = request_data.get('end_date')
        fruit_types = request_data.get('fruit_types', [])
        maturity_levels = request_data.get('maturity_levels', [])
        
        # 构建查询
        query = db.query(DetectionRecord).filter(DetectionRecord.user_id == current_user.id)
        
        # 日期过滤
        if start_date:
            start = datetime.fromisoformat(start_date)
            query = query.filter(DetectionRecord.created_at >= start)
        if end_date:
            end = datetime.fromisoformat(end_date)
            query = query.filter(DetectionRecord.created_at <= end)
        
        # 执行查询
        records = query.all()
        
        # 分析数据
        total_detections = len(records)
        total_fruits = sum(record.fruit_count for record in records)
        
        # 统计水果类型分布
        fruit_distribution = {}
        maturity_distribution = {}
        
        for record in records:
            for detection in record.result_json:
                fruit_type = detection.get('fruit_type', 'unknown')
                maturity = detection.get('maturity', 'unknown')
                
                # 水果类型统计
                if fruit_type in fruit_distribution:
                    fruit_distribution[fruit_type] += 1
                else:
                    fruit_distribution[fruit_type] = 1
                
                # 成熟度统计
                if maturity in maturity_distribution:
                    maturity_distribution[maturity] += 1
                else:
                    maturity_distribution[maturity] = 1
        
        # 找出最常见的水果类型和成熟度
        most_common_fruit = max(fruit_distribution, key=fruit_distribution.get) if fruit_distribution else '无'
        most_common_maturity = max(maturity_distribution, key=maturity_distribution.get) if maturity_distribution else '无'
        
        # 生成总结
        summary = f"在所选时间段内，您共进行了 {total_detections} 次检测，检测到 {total_fruits} 个水果。"
        summary += f" 最常见的水果类型是 {most_common_fruit}，最常见的成熟度是 {most_common_maturity}。"
        
        # 生成关键洞察
        key_insights = []
        if fruit_distribution:
            key_insights.append(f"您检测的水果中，{most_common_fruit} 的数量最多，占比 {round(fruit_distribution[most_common_fruit] / total_fruits * 100, 1)}%")
        if maturity_distribution:
            key_insights.append(f"您检测的水果中，{most_common_maturity} 的成熟度占比最高，占比 {round(maturity_distribution[most_common_maturity] / total_fruits * 100, 1)}%")
        if total_detections > 0:
            avg_fruits_per_detection = round(total_fruits / total_detections, 1)
            key_insights.append(f"平均每次检测到 {avg_fruits_per_detection} 个水果")
        
        # 生成建议
        recommendations = []
        if not fruit_types:
            recommendations.append("您可以尝试检测更多种类的水果，以获得更全面的分析")
        if not maturity_levels:
            recommendations.append("建议关注不同成熟度的水果，以优化您的检测策略")
        recommendations.append("定期检测可以帮助您更好地了解水果的成熟度变化趋势")
        
        # 记录操作日志
        log_action(current_user.id, current_user.username, "AI 分析", "生成水果检测分析报告", request)
        
        # 返回结果
        return JSONResponse({
            "code": 200,
            "message": "success",
            "data": {
                "summary": summary,
                "key_insights": key_insights,
                "recommendations": recommendations,
                "statistics": {
                    "total_detections": total_detections,
                    "total_fruits": total_fruits,
                    "most_common_fruit": most_common_fruit,
                    "most_common_maturity": most_common_maturity
                }
            }
        })
        
    except Exception as e:
        raise HTTPException(500, f"生成分析报告失败: {str(e)}")