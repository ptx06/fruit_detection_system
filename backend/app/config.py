import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
WEIGHTS_DIR = BASE_DIR / "weights"
DETECTION_MODEL_PATH = WEIGHTS_DIR / "best.pt"

CLASSIFIER_PATHS = {
    "apple": WEIGHTS_DIR / "apple_best_model.pth",
    "banana": WEIGHTS_DIR / "banana_best_model.pth",
    "orange": WEIGHTS_DIR / "orange_best_model.pth"
}

# 每种水果对应的成熟度标签列表（顺序必须与训练时类别索引一致）
MATURITY_LABELS = {
    "apple": ["freshapples", "rottenapples", "unripe apple"],   # 示例，根据实际修改
    "banana": ["freshbanana", "rottenbanana", "unripe banana"],
    "orange": ["freshoranges", "rottenoranges", "unripe orange"]
}

NUM_CLASSES = 3   # 所有分类器都是三分类
DEVICE = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
LOG_LEVEL = "INFO"