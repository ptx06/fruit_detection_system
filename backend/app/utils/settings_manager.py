import json
import os
from pathlib import Path

SETTINGS_FILE = Path(__file__).parent.parent.parent / "config" / "settings.json"

def load_settings():
    """加载设置"""
    if not SETTINGS_FILE.exists():
        default_settings = {
            "detection": {
                "conf_threshold": 0.25,
                "iou_threshold": 0.45
            }
        }
        save_settings(default_settings)
        return default_settings
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_settings(settings: dict):
    """保存设置"""
    os.makedirs(SETTINGS_FILE.parent, exist_ok=True)
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

def get_detection_params():
    """获取检测参数"""
    settings = load_settings()
    return settings.get("detection", {"conf_threshold": 0.25, "iou_threshold": 0.45})