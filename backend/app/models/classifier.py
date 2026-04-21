import torch
import torch.nn as nn
from torchvision import models
import numpy as np
from typing import Tuple
from app.config import CLASSIFIER_PATHS, NUM_CLASSES, DEVICE, MATURITY_LABELS   # 新增导入

class FruitMaturityClassifier:
    def __init__(self, fruit_type: str):
        self.device = DEVICE
        self.fruit_type = fruit_type.lower()
        self.model = self._build_model()
        self.model.load_state_dict(torch.load(CLASSIFIER_PATHS[self.fruit_type], map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        # 从配置文件读取该水果对应的成熟度标签
        self.maturity_labels = MATURITY_LABELS.get(self.fruit_type, ["class0", "class1", "class2"])

    def _build_model(self):
        model = models.mobilenet_v2(pretrained=False)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, NUM_CLASSES)
        return model

    def predict(self, image_tensor: np.ndarray) -> Tuple[int, str, float]:
        with torch.no_grad():
            tensor = torch.from_numpy(image_tensor).float().to(self.device)
            outputs = self.model(tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            conf, pred = torch.max(probs, 1)
            class_id = pred.item()
            # 使用动态标签
            label = self.maturity_labels[class_id] if class_id < len(self.maturity_labels) else "unknown"
            return class_id, label, conf.item()