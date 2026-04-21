import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO

def crop_region(image: np.ndarray, bbox: tuple) -> np.ndarray:
    """
    根据边界框裁剪图像区域
    bbox: (x1, y1, x2, y2) 格式
    """
    x1, y1, x2, y2 = map(int, bbox)
    return image[y1:y2, x1:x2]

def preprocess_for_classifier(crop_img: np.ndarray, target_size=(224, 224)):
    """
    对裁剪后的图像进行预处理，适配MobileNetV2输入
    返回: torch.Tensor 格式 (1, 3, H, W)
    """
    # 转换为RGB PIL图像
    crop_rgb = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(crop_rgb).resize(target_size, Image.BILINEAR)
    # 转为numpy并归一化
    img_np = np.array(pil_img).astype(np.float32) / 255.0
    # 标准化（ImageNet统计值）
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    img_np = (img_np - mean) / std
    # 调整维度 (H,W,C) -> (C,H,W) 并添加batch维度
    img_tensor = np.transpose(img_np, (2, 0, 1))
    return np.expand_dims(img_tensor, axis=0)

def pil_to_base64(pil_img: Image.Image, format="JPEG") -> str:
    """将PIL图像转为base64字符串，用于前端显示"""
    buffered = BytesIO()
    pil_img.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")