from ultralytics import YOLO
import numpy as np
from typing import List, Tuple
from app.config import DETECTION_MODEL_PATH, DEVICE

class YOLODetector:
    def __init__(self):
        self.model = YOLO(str(DETECTION_MODEL_PATH))
        self.model.to(DEVICE)
        # 类别映射，需根据你的训练数据调整
        self.class_names = {0: "apple", 1: "banana", 2: "orange"}

    def detect(self, image: np.ndarray, conf_thres=0.25, iou_thres=0.45) -> List[dict]:
        """
        对输入图像进行目标检测
        返回: 列表，每个元素包含 bbox, confidence, class_id, class_name
        """
        results = self.model(image, conf=conf_thres, iou=iou_thres, verbose=False)
        detections = []
        if results[0].boxes is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            confs = results[0].boxes.conf.cpu().numpy()
            cls_ids = results[0].boxes.cls.cpu().numpy().astype(int)
            for box, conf, cls_id in zip(boxes, confs, cls_ids):
                detections.append({
                    "bbox": box.tolist(),          # [x1, y1, x2, y2]
                    "confidence": float(conf),
                    "class_id": int(cls_id),
                    "class_name": self.class_names.get(cls_id, "unknown")
                })
        return detections