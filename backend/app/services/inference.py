import cv2
import numpy as np
from typing import List, Dict, Any
from app.models.detector import YOLODetector
from app.models.classifier import FruitMaturityClassifier
from app.utils.image_utils import crop_region, preprocess_for_classifier

class InferenceService:
    def __init__(self):
        # 懒加载模型，避免启动时加载所有分类器
        self.detector = YOLODetector()
        self.classifiers = {}

    def _get_classifier(self, fruit_type: str):
        if fruit_type not in self.classifiers:
            self.classifiers[fruit_type] = FruitMaturityClassifier(fruit_type)
        return self.classifiers[fruit_type]

    def process(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        主推理流程：
        1. YOLO检测水果目标
        2. 裁剪每个目标区域
        3. 调用对应水果类型的分类器进行成熟度判断
        返回结构化结果列表
        """
        # Step 1: 检测
        detections = self.detector.detect(image)

        results = []
        for det in detections:
            fruit_type = det["class_name"]
            bbox = det["bbox"]

            # Step 2: 裁剪区域
            crop_img = crop_region(image, bbox)
            if crop_img.size == 0:
                continue

            # Step 3: 预处理并分类
            tensor = preprocess_for_classifier(crop_img)
            classifier = self._get_classifier(fruit_type)
            maturity_id, maturity_name, maturity_conf = classifier.predict(tensor)

            # 组装结果
            results.append({
                "bbox": bbox,
                "fruit_type": fruit_type,
                "fruit_conf": det["confidence"],
                "maturity": maturity_name,
                "maturity_id": maturity_id,
                "maturity_conf": maturity_conf
            })

        return results