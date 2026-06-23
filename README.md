<div align="center">

# ⚖️ 智链解纷

### China-ASEAN Cross-Border Commercial Dispute Online Resolution Platform

**中国-东盟跨境商事纠纷在线解决平台**

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue-3.4-42b883.svg?logo=vue.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg?logo=fastapi&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg?logo=mysql&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6.svg?logo=typescript&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-24-2496ED.svg?logo=docker&logoColor=white)

<br>

**为企业搭建的跨境商事纠纷一站式在线解决平台，覆盖从立案到结案的完整业务闭环**

[快速开始](#-快速启动) · [功能特性](#-功能特性) · [技术架构](#-技术架构) · [API 文档](#-api-文档) · [部署指南](#-部署指南)

</div>

---

## 📌 项目概述

**智链解纷** 是一个面向中国与东盟国家中小微企业的跨境商事纠纷在线解决平台（ODR）。平台整合了在线协商、视频调解、电子签章、区块链存证等核心能力，为企业提供高效、低成本、可追溯的跨境纠纷解决方案。

### 核心价值

| 维度 | 传统方式 | 智链解纷 |
|------|----------|----------|
| 时间成本 | 数月甚至数年 | 数天至数周 |
| 沟通效率 | 跨时区反复协调 | 7×24 在线协商 |
| 费用 | 高额律师费、差旅费 | 平台化低成本 |
| 证据管理 | 纸质材料易丢失 | 区块链存证可追溯 |
| 语言障碍 | 需专业翻译 | 多语言界面支持 |

---

## ✨ 功能特性

### 🏢 企业注册与认证
- 企业信用代码自动验证
- 多角色权限体系（管理员 / 企业用户 / 调解员）
- 管理员审核机制，确保入驻企业真实性

### 📁 案件全生命周期管理
- 一键创建纠纷案件，自动分配调解员
- 案件状态实时追踪：待受理 → 协商中 → 调解中 → 已结案
- 案件文档在线管理与归档

### 💬 实时在线协商
- WebSocket 实时聊天，支持文字、图片、语音消息
- 协商记录自动归档，作为后续调解依据
- 双方可随时发起或结束协商

### 🎥 视频调解
- 集成 Agora RTC SDK，支持多人视频会议
- 含 Mock 模式，无需真实 API Key 即可本地测试
- 调解全程录制，支持回放

### 📄 电子签章
- 协商备忘录、和解协议在线签署
- 短信验证码确认签署意愿
- 签署文件自动生成 PDF 存档

### 🔒 区块链存证
- 关键操作自动 SHA-256 哈希 + 时间戳存证
- 链接第三方区块链存证 API（含 Mock 实现）
- 存证编号可独立验证

### 🔔 多渠道通知
- 站内消息通知（实时推送）
- 邮件通知（可选）
- 短信通知（可选）

### 🌐 多语言支持
- 中文 / 英文界面，预留越南语、泰语扩展
- 前端 i18n 国际化，后端用户语言偏好存储

---

## 🛠 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Vue 3)                     │
│  Vue 3 + TypeScript + Element Plus + Pinia + Vue Router  │
│              vue-i18n · echarts · nprogress               │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP / WebSocket
┌─────────────────────┴───────────────────────────────────┐
│                    Backend (FastAPI)                      │
│     Python 3.11 + FastAPI + PyMySQL + bcrypt             │
│     JWT 认证 · RBAC 权限 · WebSocket · REST API          │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   ┌────┴────┐  ┌─────┴─────┐  ┌───┴───┐
   │ MySQL   │  │  Redis    │  │ Nginx │
   │ 8.0     │  │  7        │  │ 反代  │
   └─────────┘  └───────────┘  └───────┘
```

### 技术栈明细

| 层次 | 技术 | 用途 |
|------|------|------|
| **前端框架** | Vue 3.4 + TypeScript | 响应式 UI 构建 |
| **UI 组件库** | Element Plus | 企业级组件 |
| **状态管理** | Pinia | 全局状态 |
| **路由** | Vue Router 4 | SPA 路由 |
| **国际化** | vue-i18n | 多语言 |
| **图表** | ECharts | 数据可视化 |
| **后端框架** | FastAPI | 高性能异步 API |
| **数据库** | MySQL 8.0 | 数据持久化 |
| **ORM** | PyMySQL | 数据库连接 |
| **实时通信** | WebSocket | 在线协商 |
| **身份认证** | JWT (Access + Refresh Token) | 接口鉴权 |
| **密码加密** | bcrypt | 安全存储 |
| **敏感字段** | AES-256-CBC | 手机号/身份证加密 |
| **视频会议** | Agora RTC SDK (Mock) | 视频调解 |
| **容器化** | Docker + Docker Compose | 一键部署 |
| **反向代理** | Nginx | 负载均衡 & 静态资源 |

---

## 📁 项目结构

```
Web-Projects-Online-Dispute/
├── backend/                          # FastAPI 后端
│   ├── app/
│   │   ├── main.py                   # 应用入口
│   │   ├── core/                     # 核心模块
│   │   │   ├── config.py             # 环境配置
│   │   │   ├── database.py           # 数据库连接
│   │   │   ├── security.py           # 密码加密 & JWT
│   │   │   ├── deps.py               # 依赖注入
│   │   │   └── redis_client.py       # Redis 客户端
│   │   ├── models/
│   │   │   └── models.py             # 数据模型定义
│   │   ├── api/v1/endpoints/         # REST API 路由
│   │   │   ├── auth.py               # 认证接口
│   │   │   ├── cases.py              # 案件管理
│   │   │   ├── negotiation.py        # 在线协商
│   │   │   ├── mediation.py          # 视频调解
│   │   │   ├── evidence.py           # 电子存证
│   │   │   ├── notifications.py      # 消息通知
│   │   │   ├── admin.py              # 管理后台
│   │   │   ├── enterprises.py        # 企业管理
│   │   │   └── users.py              # 用户管理
│   │   ├── websocket/
│   │   │   └── handler.py            # WebSocket 处理
│   │   └── services/                 # 业务服务层
│   │       ├── agora_service.py      # 视频会议
│   │       ├── notification_service.py # 通知服务
│   │       ├── timestamp_service.py  # 时间戳存证
│   │       ├── pdf_service.py        # PDF 生成
│   │       └── storage_service.py    # 文件存储
│   ├── migrations/
│   │   ├── init.sql                  # 数据库建表
│   │   └── seed.py                   # 初始数据
│   ├── uploads/                      # 用户上传文件
│   ├── logs/                         # 服务日志
│   ├── requirements.txt              # Python 依赖
│   ├── demo_server.py                # 本地开发服务器
│   ├── init_db.py                    # 数据库初始化
│   └── Dockerfile                    # 后端镜像
│
├── frontend/                         # Vue 3 前端
│   ├── src/
│   │   ├── api/                      # API 请求封装
│   │   │   ├── http.ts               # Axios 实例 & 拦截器
│   │   │   └── index.ts              # 接口定义
│   │   ├── stores/                   # Pinia 状态管理
│   │   │   ├── auth.ts               # 认证状态
│   │   │   └── notification.ts       # 通知状态
│   │   ├── router/
│   │   │   └── index.ts              # 路由配置
│   │   ├── i18n/
│   │   │   └── index.ts              # 国际化配置
│   │   ├── layouts/                  # 布局组件
│   │   │   ├── MainLayout.vue        # 企业用户布局
│   │   │   ├── AdminLayout.vue       # 管理员布局
│   │   │   ├── MediatorLayout.vue    # 调解员布局
│   │   │   └── AuthLayout.vue        # 登录注册布局
│   │   ├── views/                    # 页面组件
│   │   │   ├── auth/                 # 登录 & 注册
│   │   │   ├── admin/                # 管理员页面
│   │   │   ├── cases/                # 案件管理
│   │   │   ├── mediator/             # 调解员工作台
│   │   │   ├── mediation/            # 视频调解
│   │   │   └── negotiation/          # 在线协商
│   │   ├── assets/styles/
│   │   │   └── main.scss             # 全局样式
│   │   ├── App.vue                   # 根组件
│   │   └── main.ts                   # 入口文件
│   ├── package.json                  # Node 依赖
│   ├── vite.config.ts                # Vite 构建配置
│   ├── tsconfig.json                 # TypeScript 配置
│   └── Dockerfile                    # 前端镜像
│
├── nginx/                            # Nginx 配置
│   └── conf.d/
│       └── zjfl.conf                 # 反向代理配置
│
├── docker-compose.yml                # Docker 编排
├── deploy.sh                         # 一键部署脚本
├── start.ps1                         # Windows 启动脚本
├── .env.example                      # 环境变量模板
└── README.md                         # 项目说明
```

---

## 🚀 快速启动

### 方式一：Windows 一键启动（推荐本地开发）

```powershell
# 确保 MySQL 8.0 已安装并运行
# 确保 Python 3.11+ 和 Node.js 18+ 已安装

# 1. 克隆项目
git clone https://github.com/XOXO1018/Web-Projects-Online-Dispute.git
cd Web-Projects-Online-Dispute

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 修改数据库密码等配置

# 3. 一键启动（含数据库初始化）
.\start.ps1 -seed

# 4. 仅启动服务（不初始化数据库）
.\start.ps1
```

启动后访问：
- 🌐 前端页面：http://localhost:5173
- 📖 API 文档：http://localhost:8000/api/docs

### 方式二：Docker Compose 一键部署

```bash
# 1. 配置环境变量
cp .env.example .env
vim .env  # 修改密码和密钥

# 2. 一键部署
chmod +x deploy.sh
./deploy.sh

# 3. 或手动启动
docker-compose up -d

# 查看日志
docker-compose logs -f backend
```

### 方式三：手动分别启动

**后端：**
```bash
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py

# 启动后端
python demo_server.py
```

**前端：**
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## ⚙️ 环境变量

复制 `.env.example` 为 `.env` 并根据实际情况修改：

| 变量 | 说明 | 默认值 | 必填 |
|------|------|--------|------|
| `DB_HOST` | MySQL 主机 | localhost | ✅ |
| `DB_PORT` | MySQL 端口 | 3306 | ✅ |
| `DB_USER` | MySQL 用户 | root | ✅ |
| `DB_PASSWORD` | MySQL 密码 | - | ✅ |
| `DB_NAME` | 数据库名 | zjfl | ✅ |
| `APP_SECRET_KEY` | 应用密钥 | - | ✅ |
| `JWT_SECRET_KEY` | JWT 签名密钥 | - | ✅ |
| `AES_KEY` | 敏感字段加密密钥 (32字节) | - | ✅ |
| `AGORA_APP_ID` | Agora 视频会议 AppID | 留空使用Mock | ❌ |
| `SMTP_HOST` | 邮件服务器 | 留空不发送 | ❌ |
| `DEMO_MODE` | 演示模式（注册免审核） | false | ❌ |

---

## 👤 默认账号

| 角色 | 邮箱 | 密码 | 说明 |
|------|------|------|------|
| 平台管理员 | `admin@zjfl.com` | `admin123` | 管理后台，首次登录强制改密 |
| 演示企业 | `demo@zjfl.com` | `Demo@12345` | 企业端完整功能 |
| 调解员 | `mediator_li@zjfl.com` | `Mediator@123` | 调解员工作台 |
| 调解员 | `mediator_chen@zjfl.com` | `Mediator@123` | 调解员工作台 |

---

## 🖥️ 系统界面

平台支持三种角色独立界面：

### 管理员后台
- 平台数据仪表盘（ECharts 可视化）
- 企业审核与管理
- 调解员管理
- 案件全局视图
- 系统设置

### 企业用户端
- 个人仪表盘与待办事项
- 一键创建纠纷案件
- 在线协商（实时聊天）
- 案件进度追踪
- 通知中心

### 调解员工作台
- 待受理案件列表
- 调解排期管理
- 视频调解会议室
- 调解记录与备忘录
- 个人档案管理

---

## 📖 API 文档

后端提供完整的 OpenAPI 3.0 文档：

| 文档 | 地址 |
|------|------|
| Swagger UI | http://localhost:8000/api/docs |
| ReDoc | http://localhost:8000/api/redoc |
| OpenAPI JSON | http://localhost:8000/api/openapi.json |

### 主要 API 模块

| 模块 | 路径前缀 | 说明 |
|------|----------|------|
| 认证 | `/api/v1/auth` | 登录、注册、Token 刷新 |
| 案件 | `/api/v1/cases` | 案件 CRUD、状态流转 |
| 协商 | `/api/v1/negotiation` | 在线聊天、消息记录 |
| 调解 | `/api/v1/mediation` | 视频会议、调解记录 |
| 存证 | `/api/v1/evidence` | 文件上传、区块链存证 |
| 通知 | `/api/v1/notifications` | 站内消息、邮件、短信 |
| 管理 | `/api/v1/admin` | 用户管理、系统设置 |

---

## 🔒 安全机制

| 安全措施 | 实现方式 |
|----------|----------|
| 密码存储 | bcrypt 哈希 (cost=12) |
| 敏感字段 | AES-256-CBC 加密 (手机号、身份证) |
| 接口鉴权 | JWT Access Token + Refresh Token |
| 权限控制 | RBAC 角色权限，数据隔离 |
| 防暴力破解 | 图形验证码 |
| CORS | 白名单域名 |
| 生产环境 | 强制 HTTPS + 防火墙 |

---

## 🔌 第三方服务 Mock 说明

以下功能在无 API Key 时自动使用 Mock 实现，开箱即用：

| 功能 | Mock 行为 | 配置真实服务 |
|------|-----------|-------------|
| 视频会议 | 本地摄像头预览 | 设置 `AGORA_APP_ID` |
| 区块链存证 | 返回随机存证编号 | 设置 `TIMESTAMP_API_KEY` |
| 短信验证码 | 演示模式直接显示在页面 | 配置阿里云短信服务 |
| 电子签章 | 点击确认即签署成功 | 对接法大大 / e签宝 |
| 邮件通知 | 记录到日志文件 | 设置 `SMTP_HOST` |

> **签署验证码演示：** 使用 `123456` 作为验证码

---

## 📦 部署到云服务器

### 生产环境配置

```bash
# 1. 修改生产配置
vim .env
# DEMO_MODE=false
# 修改所有默认密码和密钥
# 配置真实的第三方服务 API Key

# 2. 配置 SSL 证书
mkdir -p nginx/ssl
cp your_cert.pem nginx/ssl/cert.pem
cp your_key.pem nginx/ssl/key.pem

# 3. 启动服务
docker-compose up -d

# 4. 查看状态
docker-compose ps
docker-compose logs -f backend
```

### Nginx 反向代理

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate     /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/v1/ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 🗺️ 路线图

### V1.0 (当前版本)
- [x] 企业注册与认证
- [x] 案件全生命周期管理
- [x] 在线协商 (WebSocket)
- [x] 视频调解 (Agora Mock)
- [x] 电子签章 (Mock)
- [x] 区块链存证 (Mock)
- [x] 多角色权限体系
- [x] 中英文双语界面
- [x] Docker 一键部署

### V2.0 (规划中)
- [ ] 对接真实仲裁机构 API
- [ ] 越南语、泰语界面
- [ ] 移动端 App (React Native)
- [ ] AI 辅助调解建议
- [ ] 多企业成员管理与邀请
- [ ] 数据分析与报告导出

---

## 🤝 贡献指南

欢迎参与项目开发！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 发起 Pull Request

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

<div align="center">

**智链解纷** © 2026 — 助力中国-东盟贸易畅通无阻 🌏

</div>
