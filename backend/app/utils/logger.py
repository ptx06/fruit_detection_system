import logging
import sys
from app.config import LOG_LEVEL

def setup_logger():
    """配置全局日志格式和级别"""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    # 可选：降低第三方库日志冗余
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("ultralytics").setLevel(logging.WARNING)