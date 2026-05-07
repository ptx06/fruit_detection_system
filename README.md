# 水果成熟度分级系统

基于 **YOLOv11 + MobileNetV2** 的两阶段深度学习水果成熟度检测系统，为果园精准采摘与产后分级提供智能化解决方案。

---

## 🌐 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        前端应用层 (Vue 3)                           │
│  ┌─────────────┬─────────────┬─────────────┬─────────────────────┐ │
│  │  检测页面   │  历史记录   │   仪表盘    │    系统管理         │ │
│  └─────────────┴─────────────┴─────────────┴─────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP/REST API
┌──────────────────────────────▼──────────────────────────────────────┐
│                        后端服务层 (FastAPI)                         │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┬────────┐ │
│  │  Auth    │ Detect   │ History  │Dashboard │  Admin   │ System │ │
│  │  API     │  API     │  API     │   API    │  API     │  API   │ │
│  └────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┴───┬────┘ │
│       │          │          │          │          │          │      │
│       ▼          ▼          ▼          ▼          ▼          ▼      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Inference Service                          │  │
│  │   ┌─────────────────────┐  ┌─────────────────────────────┐   │  │
│  │   │    YOLOv11 Detector │→ │ MobileNetV2 Classifiers     │   │  │
│  │   │  (定位苹果/香蕉/橘子)│  │ (成熟度三分类: 新鲜/腐烂/未熟)│   │  │
│  │   └─────────────────────┘  └─────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ SQLAlchemy
┌──────────────────────────────▼──────────────────────────────────────┐
│                        数据存储层 (MySQL)                           │
│  ┌──────────────┬──────────────┬──────────────┬─────────────────┐   │
│  │   users      │ detections   │  audit_log   │  announcements  │   │
│  │              │  _records    │              │                 │   │
│  └──────────────┴──────────────┴──────────────┴─────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 功能模块

### 核心业务模块

| 模块 | 功能描述 | API 端点 |
|------|----------|----------|
| **用户认证** | JWT令牌认证，支持注册、登录、登出 | `/api/v1/auth/*` |
| **水果检测** | 单张图片上传检测，返回定位框与成熟度 | `/api/v1/detect` |
| **批量检测** | 一次上传多张图片，并发推理汇总结果 | `/api/v1/detect/batch` |
| **检测历史** | 分页查看检测记录，支持详情回溯 | `/api/v1/history/*` |
| **数据导出** | 一键导出检测历史为CSV文件 | `/api/v1/history/export` |

### 管理监控模块

| 模块       | 功能描述 | 权限要求 |
|----------|----------|----------|
| **控制台**  | ECharts可视化统计（检测数、水果分布、成熟度占比、趋势） | 所有用户 |
| **用户管理** | 查看/修改/删除用户，角色分配 | 管理员 |
| **模型面板** | 展示模型版本、准确率、更新时间 | 所有用户 |
| **日志审计** | 记录登录、检测、导出等关键操作 | 管理员 |
| **系统设置** | 动态调整置信度、IOU阈值 | 管理员 |
| **公告管理** | 创建、编辑、发布系统公告 | 管理员 |

### 用户体验模块

| 模块 | 功能描述 |
|------|----------|
| **个人中心** | 查看个人信息、修改密码、个人检测统计 |
| **反馈功能** | 用户提交反馈意见 |

---

## 🔬 核心算法设计

### 两阶段级联架构

系统采用两阶段级联架构，解决单阶段模型同时进行定位与分类的特征冲突问题：

```
输入图像 → YOLOv11检测 → 裁剪目标区域 → MobileNetV2分类 → 输出结果
```

#### 阶段一：YOLOv11 目标检测

| 参数 | 说明 |
|------|------|
| 模型 | YOLOv11n |
| 检测目标 | 苹果、香蕉、橘子 |
| 输出 | 边界框 (x1,y1,x2,y2)、置信度、类别 |
| 配置 | 置信度阈值、IOU阈值可动态调整 |

**检测流程**（`backend/app/models/detector.py`）：
1. 加载YOLOv11模型权重
2. 推理获取检测框
3. 解析边界框坐标和类别信息

#### 阶段二：MobileNetV2 成熟度分类

| 参数 | 说明 |
|------|------|
| 模型 | MobileNetV2 (微调) |
| 分类目标 | 新鲜、腐烂、未熟 |
| 输入 | 裁剪后的水果区域 (224x224) |
| 输出 | 类别ID、类别名称、置信度 |

**分类流程**（`backend/app/models/classifier.py`）：
1. 根据水果类型加载对应分类器
2. 预处理图像为张量
3. 前向传播获取概率分布
4. 返回最高置信度的分类结果

#### 推理服务整合

`InferenceService`（`backend/app/services/inference.py`）作为核心调度器：

```python
def process(image):
    # Step 1: YOLO检测水果目标
    detections = detector.detect(image)
    
    # Step 2: 裁剪每个目标区域
    # Step 3: 调用对应分类器进行成熟度判断
    # 返回结构化结果
```

---

## 🛠️ 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue | 3.x |
| 前端语言 | TypeScript | - |
| 构建工具 | Vite | 6.x |
| UI组件 | Element Plus | - |
| 可视化 | ECharts | - |
| 状态管理 | Pinia | - |
| 后端框架 | FastAPI | 0.100+ |
| 深度学习 | PyTorch | 2.x |
| 目标检测 | Ultralytics YOLO | 8.3+ |
| 数据库 | MySQL | 8.0+ |
| ORM | SQLAlchemy | 2.x |
| 认证 | JWT | PyJWT |

---

## 📁 项目结构

```
fruit_detection_system/
├── backend/                              # FastAPI 后端
│   ├── app/
│   │   ├── api/                          # REST API 路由
│   │   │   ├── auth.py                   # 用户认证
│   │   │   ├── endpoints.py              # 检测接口
│   │   │   ├── history.py                # 历史记录
│   │   │   ├── dashboard.py              # 数据仪表盘
│   │   │   ├── admin.py                  # 管理员功能
│   │   │   ├── system.py                 # 系统状态
│   │   │   ├── settings.py               # 系统设置
│   │   │   ├── announcements.py          # 公告管理
│   │   │   ├── feedback.py               # 用户反馈
│   │   │   └── ai.py                     # AI相关
│   │   ├── models/                       # 数据模型
│   │   │   ├── detector.py               # YOLOv11检测器
│   │   │   ├── classifier.py             # MobileNetV2分类器
│   │   │   ├── user.py                   # 用户模型
│   │   │   ├── detection.py              # 检测记录模型
│   │   │   └── ...                       # 其他模型
│   │   ├── services/                     # 业务服务
│   │   │   └── inference.py              # 推理服务
│   │   ├── schemas/                      # Pydantic 校验
│   │   ├── utils/                        # 工具函数
│   │   │   ├── image_utils.py            # 图像处理
│   │   │   ├── logger.py                 # 日志记录
│   │   │   ├── auth.py                   # 认证工具
│   │   │   └── settings_manager.py       # 配置管理
│   │   ├── config.py                     # 静态配置
│   │   ├── database.py                   # 数据库连接
│   │   └── main.py                       # 应用入口
│   ├── weights/                          # 模型权重
│   │   ├── best.pt                       # YOLOv11检测模型
│   │   ├── apple_best_model.pth          # 苹果分类器
│   │   ├── banana_best_model.pth         # 香蕉分类器
│   │   └── orange_best_model.pth         # 橘子分类器
│   ├── uploads/                          # 上传文件存储
│   ├── config/settings.json              # 动态配置
│   ├── requirements.txt                  # Python依赖
│   ├── run.py                            # 启动脚本
│   └── Dockerfile                        # Docker配置
├── frontend/                             # Vue 3 前端
├── docs/                                 # 文档资源
└── .gitignore
```

---

## 🚀 快速启动

### 环境要求

- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- CUDA 11.8+（可选，GPU加速）

### 1. 克隆项目

```bash
git clone <repository-url>
cd fruit_detection_system
```

### 2. 后端配置

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置数据库
# 在MySQL中创建数据库: CREATE DATABASE fruit_system CHARACTER SET utf8mb4;
# 配置 .env 文件（复制 utils/.env 模板）

# 启动服务
python run.py
```

后端服务运行在 `http://localhost:8000`，API文档访问 `http://localhost:8000/docs`

### 3. 前端配置

```bash
cd frontend
npm install
npm run dev
```

前端运行在 `http://localhost:5173`

### 4. 初始配置

首次启动后，注册账号并将数据库中用户的 `role` 字段设置为 `admin` 以获得管理员权限。

---

## ⚙️ 配置说明

### 模型配置

`backend/app/config.py`：

```python
# 模型权重路径
CLASSIFIER_PATHS = {
    "apple": "weights/apple_best_model.pth",
    "banana": "weights/banana_best_model.pth",
    "orange": "weights/orange_best_model.pth"
}

# 成熟度标签映射
MATURITY_LABELS = {
    "apple": ["freshapples", "rottenapples", "unripe apple"],
    "banana": ["freshbanana", "rottenbanana", "unripe banana"],
    "orange": ["freshoranges", "rottenoranges", "unripe orange"]
}
```

### 动态设置

`backend/config/settings.json`：

```json
{
    "conf_threshold": 0.25,
    "iou_threshold": 0.45
}
```

---

## 📊 模型性能

| 模型 | 类型 | 准确率 | 更新时间 |
|------|------|--------|----------|
| YOLOv11 | 检测模型 | mAP@0.5: 0.92 | 2026-04-20 |
| MobileNetV2 (Apple) | 分类模型 | 96.5% | 2026-04-18 |
| MobileNetV2 (Banana) | 分类模型 | 94.2% | 2026-04-18 |
| MobileNetV2 (Orange) | 分类模型 | 95.8% | 2026-04-18 |

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request。在提交 PR 前请确保：
1. 代码符合项目风格
2. 通过现有测试用例
3. 添加必要的文档注释

---

## 📄 许可证

本项目采用 MIT 许可证。

---

**作者**：JiahaoYu  
**时间**：2026年5月