from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class DetectionRecord(Base):
    __tablename__ = "detection_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    image_path = Column(String(500), nullable=False)
    original_filename = Column(String(255))
    result_json = Column(JSON)
    fruit_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())