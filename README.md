# 水果成熟度分级系统

基于 YOLOv11 + MobileNetV2 的两阶段深度学习水果成熟度检测系统，集成用户管理、历史记录、数据可视化、系统管理等完整功能，适用于果园精准采摘与产后分级的智能化场景。

## ✨ 功能特点

### 核心业务
- **用户认证**：JWT 令牌认证，支持注册、登录、登出。
- **水果检测**：上传图片，自动定位苹果、香蕉、橘子并识别成熟度等级。
- **检测历史**：所有检测记录保存至数据库，支持分页查看与详情回溯。
- **批量检测**：一次上传多张图片，并发推理并汇总结果。
- **数据导出**：一键导出检测历史为 CSV 文件。

### 管理与监控
- **仪表盘统计**：ECharts 可视化展示总检测数、水果分布、成熟度占比、近7天趋势。
- **用户管理**（管理员）：查看所有用户、修改角色、删除用户。
- **模型信息面板**：实时展示当前使用的模型版本、准确率及更新时间。
- **日志审计**：记录用户登录、检测、导出等关键操作，满足安全审计需求。

### 体验与扩展
- **个人中心**：查看个人信息、修改密码、个人检测统计。
- **图片标注可视化**：在原图上绘制检测框与标签，直观展示识别结果。
- **系统设置**（管理员）：动态调整检测置信度与 IOU 阈值，即时生效。

## 🛠️ 技术栈

| 模块     | 技术选型                                                     |
| -------- | ------------------------------------------------------------ |
| 前端     | Vue 3 + TypeScript + Vite + Element Plus + ECharts + Pinia   |
| 后端     | FastAPI + PyTorch + SQLAlchemy + MySQL                       |
| 深度学习 | Ultralytics YOLOv11 + torchvision MobileNetV2                |
| 数据库   | MySQL 8.0                                                    |
| 部署     | 支持 Docker（可选）                                          |

## 📁 项目结构

```
fruit-maturity-system/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/                # 路由接口 (auth, detect, history, admin, dashboard, settings...)
│   │   ├── models/             # SQLAlchemy 数据库模型 & PyTorch 模型封装
│   │   ├── services/           # 推理服务（两阶段级联）
│   │   ├── schemas/            # Pydantic 数据校验
│   │   ├── utils/              # 工具函数（图像处理、日志、配置管理）
│   │   ├── config.py           # 全局配置
│   │   ├── database.py         # 数据库连接与会话
│   │   └── main.py             # 应用入口
│   ├── weights/                # 训练好的模型权重文件
│   │   ├── best.pt             # YOLOv11 检测模型
│   │   ├── apple_best_model.pth
│   │   ├── banana_best_model.pth
│   │   └── orange_best_model.pth
│   ├── config/                 # 动态配置文件
│   │   └── settings.json
│   ├── uploads/                # 用户上传的图片存储目录
│   ├── requirements.txt        # Python 依赖
│   └── run.py                  # 启动脚本
├── frontend/                   # Vue3 前端
│   ├── src/
│   │   ├── api/                # Axios 请求封装
│   │   ├── components/         # 公共组件（如图片标注组件）
│   │   ├── views/              # 页面视图（登录、仪表盘、检测、历史、管理等）
│   │   ├── stores/             # Pinia 状态管理
│   │   ├── router/             # Vue Router 路由配置
│   │   └── App.vue
│   ├── package.json
│   └── vite.config.ts
├── docs/                       # 文档资源（可选）
├── .gitignore
└── README.md
```

## 🚀 快速启动

### 环境要求
- Python 3.9
- Node.js 18+
- MySQL 8.0 (已安装并运行)
- CUDA (可选，用于 GPU 加速)

### 1. 克隆仓库
```bash
git clone https://github.com/yourusername/fruit-maturity-system.git
cd fruit-maturity-system
```

### 2. 后端配置与启动

#### 2.1 创建 Python 虚拟环境
```bash
cd backend
conda create -n fruit-system python=3.10
conda activate fruit-system
```

#### 2.2 安装依赖
```bash
pip install -r requirements.txt
```

#### 2.3 配置数据库
- 在 MySQL 中创建数据库 `fruit_system`。
- 复制 `.env.example` 为 `.env`，填写数据库连接信息（用户名、密码等）。
- 数据库表会在首次启动时自动创建。

#### 2.4 放置模型权重
将训练好的模型文件放入 `backend/weights/` 目录：
- `best.pt` (YOLOv11)
- `apple_best_model.pth`
- `banana_best_model.pth`
- `orange_best_model.pth`

#### 2.5 启动后端服务
```bash
python run.py
```
服务将运行在 `http://localhost:8000`，API 文档访问 `http://localhost:8000/docs`。

### 3. 前端配置与启动

#### 3.1 安装依赖
```bash
cd frontend
npm install
```

#### 3.2 启动开发服务器
```bash
npm run dev
```
前端将运行在 `http://localhost:5173`，已配置代理转发 `/api` 到后端。

### 4. 访问系统
浏览器打开 `http://localhost:5173`，注册账号并登录。首次使用可将第一个注册用户的 `role` 字段在数据库中改为 `admin` 以获得管理员权限。

## 📦 Docker 部署（可选）

后端已包含 `Dockerfile`，可根据需要构建镜像。前端也可单独构建静态文件部署。

## 📝 配置说明

- 后端主要配置文件：`backend/app/config.py`（静态配置）和 `backend/config/settings.json`（动态设置）。
- 成熟度标签映射：在 `config.py` 中的 `MATURITY_LABELS` 字典中定义，请根据实际训练标签调整。
- 数据库连接：通过环境变量或 `.env` 文件配置。

## 📊 模型说明

本系统采用两阶段级联架构，解决单阶段模型同时进行定位与分类的特征冲突问题：
1. **YOLOv11**：负责在果园复杂背景下精准定位苹果、香蕉、橘子，并输出类别。
2. **MobileNetV2**：对裁剪后的果实区域进行成熟度三分类（如新鲜、腐烂、未熟等）。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request。在提交 PR 前请确保代码符合项目风格并通过测试。

## 📄 许可证

本项目采用 MIT 许可证，详情参见 [LICENSE](LICENSE) 文件。

**作者**：JiahaoYu  
**时间**：2026 年 4 月