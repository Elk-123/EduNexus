# EduNexus API 接口文档 v1.0.0

> **EduNexus** — 多智能体 AI 教育平台  
> 基于 FastAPI + PostgreSQL + Google Gemini / DeepSeek 构建  
> 提供从学生画像构建、内容生成、学习路径规划到资源推送、智能辅导、学习评估的完整教育闭环 API

---

## 目录

- [1. 概述](#1-概述)
- [2. 快速开始](#2-快速开始)
- [3. 认证体系](#3-认证体系)
- [4. 通用规范](#4-通用规范)
- [5. 接口列表](#5-接口列表)
  - [5.1 认证模块 (Auth)](#51-认证模块-auth)
  - [5.2 画像模块 (Profile)](#52-画像模块-profile)
  - [5.3 内容工厂 (Factory)](#53-内容工厂-factory)
  - [5.4 学习路径 (Graph)](#54-学习路径-graph)
  - [5.5 资源推送 (Resources)](#55-资源推送-resources)
  - [5.6 智能辅导 (Tutor)](#56-智能辅导-tutor)
  - [5.7 学习评估 (Assessment)](#57-学习评估-assessment)
  - [5.8 系统 (System)](#58-系统-system)
- [6. WebSocket 实时通信](#6-websocket-实时通信)
- [7. 多智能体流水线架构](#7-多智能体流水线架构)
- [8. 错误处理](#8-错误处理)
- [9. 数据库模型](#9-数据库模型)
- [10. 附录](#10-附录)

---

## 1. 概述

### 1.1 平台简介

EduNexus 是一个基于多智能体协同工作的 AI 教育平台。平台模拟一个完整的教育团队——从管理者 (Manager) 到教授 (Professor)、架构师 (Architect)、考官 (Examiner)、导演 (Director)、极客 (Hacker) 和审查员 (Reviewer)，七个专业 AI Agent 各司其职，协同完成从学生画像构建到个性化内容生成的完整教育闭环。

### 1.2 技术架构

```
┌─────────────────────────────────────────────────────┐
│                    前端 (Vue 3)                       │
│              EduNexus/src/                           │
│         🌐 暗色主题 · Google AI Studio 风格 UI        │
└────────────────────┬────────────────────────────────┘
                     │ HTTP / WebSocket
                     │ JWT Bearer Token
┌────────────────────┴────────────────────────────────┐
│                 API 网关 (FastAPI)                    │
│              backend/app/api/v1/                     │
│    ┌──────┬──────┬──────┬──────┬──────┬──────┐      │
│    │ Auth │Profile│Factory│Graph │Resrc │Tutor │      │
│    └──────┴──────┴──────┴──────┴──────┴──────┘      │
│    ┌──────────────────────────────────────────┐      │
│    │        Assessment · WebSocket            │      │
│    └──────────────────────────────────────────┘      │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────┐
│              服务层 (Services)                        │
│  ┌─────────────────┐  ┌──────────────────────────┐  │
│  │ AgentOrchestrator│  │ ContentGenerator         │  │
│  │ (多Agent流水线)   │  │ (Gemini API + Fallback)  │  │
│  └─────────────────┘  └──────────────────────────┘  │
│  ┌─────────────────┐  ┌──────────────────────────┐  │
│  │ ProfileAnalyzer │  │ PathPlanner              │  │
│  │ (DeepSeek 驱动)  │  │ (学习路径DAG生成)         │  │
│  └─────────────────┘  └──────────────────────────┘  │
└────────────────────┬────────────────────────────────┘
                     │ Async Session
┌────────────────────┴────────────────────────────────┐
│              数据层 (PostgreSQL + pgvector)            │
│   students · student_profiles · generation_tasks    │
│   generated_resources · knowledge_graphs            │
└─────────────────────────────────────────────────────┘
```

### 1.3 核心特性

| 特性 | 说明 |
|------|------|
| **多智能体协同** | 7 个专业 AI Agent 并行协作，Manager 调度 → 5 专家并行生成 → Reviewer 审核 |
| **实时推送** | WebSocket 实时推送 Agent 状态、生成日志、任务进度 |
| **双模型驱动** | Google Gemini (内容生成) + DeepSeek (破冰对话)，双模型冗余保障 |
| **JWT 双 Token** | Access Token (60min) + Refresh Token (7天) 自动刷新机制 |
| **AI 降级兜底** | 所有 AI 调用均有 fallback 机制，确保服务可用性 |
| **自动建表** | 应用启动时通过 SQLAlchemy async 自动创建所有表结构 |

---

## 2. 快速开始

### 2.1 环境要求

| 组件 | 版本要求 |
|------|---------|
| Python | 3.12+ |
| PostgreSQL | 15+ (含 pgvector 扩展) |
| Node.js | 20+ |

### 2.2 启动后端

```bash
# 1. 进入后端目录
cd backend

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动 Docker 服务 (PostgreSQL + Redis)
docker-compose up -d

# 4. 配置环境变量 (.env)
# 填入 GOOGLE_API_KEY 和 DEEPSEEK_API_KEY

# 5. 启动开发服务器
uvicorn app.main:app --reload --port 8001
```

### 2.3 访问 API 文档

启动后可访问自动生成的交互式文档：

| 文档类型 | 地址 |
|---------|------|
| Swagger UI | [http://localhost:8001/docs](http://localhost:8001/docs) |
| ReDoc | [http://localhost:8001/redoc](http://localhost:8001/redoc) |
| 健康检查 | [http://localhost:8001/health](http://localhost:8001/health) |

### 2.4 测试账号

| 邮箱 | 密码 |
|------|------|
| `test@edunexus.com` | `123456` |

---

## 3. 认证体系

### 3.1 认证流程

```
用户注册/登录 → 获取 Access Token + Refresh Token
                    │
    ┌───────────────┴───────────────┐
    │                               │
    ▼                               ▼
Access Token (60min)         Refresh Token (7天)
用于请求认证接口              用于刷新 Access Token
放在 Authorization Header    调用 POST /auth/refresh
```

### 3.2 请求认证方式

所有需要认证的接口（除注册/登录外）必须在请求头中携带 JWT Token：

```http
Authorization: Bearer <access_token>
```

WebSocket 连接通过查询参数传递 Token：

```
ws://localhost:8001/api/v1/factory/stream/{task_id}?token=<access_token>
```

### 3.3 Token 自动刷新

前端 `src/api/client.ts` 已实现基于 axios 拦截器的自动 Token 刷新机制：
- 当请求返回 401 时，自动调用 `/auth/refresh` 获取新的 Access Token
- 刷新成功后自动重试原请求
- 刷新失败则清除登录状态，跳转登录页

---

## 4. 通用规范

### 4.1 基础 URL

```
http://localhost:8001/api/v1
```

### 4.2 请求头

| 头部 | 值 | 说明 |
|------|-----|------|
| `Content-Type` | `application/json` | 请求体为 JSON 格式 |
| `Authorization` | `Bearer <token>` | JWT 认证令牌（需要认证的接口） |

### 4.3 响应格式

**成功响应**：直接返回数据对象或数组。

**分页响应**：
```json
{
  "data": [...],
  "total": 100,
  "page": 1,
  "page_size": 10
}
```

**错误响应**：
```json
{
  "detail": "错误描述信息",
  "error_id": "ERR-20260511143022",
  "timestamp": "2026-05-11T14:30:22.123456"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `detail` | string/array | 错误详情描述 |
| `error_id` | string | 唯一错误追踪 ID，格式 `ERR-YYYYMMDDHHmmssfff` |
| `timestamp` | string | 错误发生时间 (ISO 8601) |

### 4.4 HTTP 状态码

| 状态码 | 含义 | 场景 |
|--------|------|------|
| `200` | 成功 | GET/PUT 操作成功 |
| `201` | 已创建 | POST 创建资源成功 |
| `400` | 请求错误 | 参数校验失败、业务逻辑错误 |
| `401` | 未认证 | Token 缺失、过期或无效 |
| `404` | 未找到 | 资源不存在 |
| `422` | 验证错误 | 请求体格式不符合 Schema |
| `500` | 服务器错误 | 数据库操作失败 |
| `503` | 服务不可用 | AI 服务暂时不可用 |

---

## 5. 接口列表

### 5.1 认证模块 (Auth)

> **Tag**: `auth`  
> **Base URL**: `/api/v1/auth`

#### 5.1.1 用户注册

```http
POST /api/v1/auth/register
```

**请求体**：

```json
{
  "email": "student@example.com",
  "username": "张三",
  "password": "secure_password"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `email` | EmailStr | ✅ | 用户邮箱，全局唯一 |
| `username` | string | ✅ | 用户名，用于界面展示 |
| `password` | string | ✅ | 登录密码，通过 bcrypt 哈希存储 |

**响应** (200):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "student@example.com",
    "username": "张三",
    "onboarding_completed": false,
    "created_at": "2026-05-11T10:30:00"
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `access_token` | string | 访问令牌，有效期 60 分钟 |
| `refresh_token` | string | 刷新令牌，有效期 7 天 |
| `token_type` | string | 固定值 `"bearer"` |
| `user.id` | UUID | 用户唯一标识 |
| `user.onboarding_completed` | bool | 是否已完成破冰画像 |
| `user.created_at` | datetime | 注册时间 |

**错误码**：

| 状态码 | detail | 触发条件 |
|--------|--------|---------|
| `400` | `The user with this email already exists.` | 邮箱已被注册 |

---

#### 5.1.2 用户登录

```http
POST /api/v1/auth/login
```

**请求体**：

```json
{
  "email": "student@example.com",
  "password": "secure_password"
}
```

**响应** (200):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "student@example.com",
    "username": "张三",
    "onboarding_completed": true,
    "created_at": "2026-05-11T10:30:00"
  }
}
```

**错误码**：

| 状态码 | detail | 触发条件 |
|--------|--------|---------|
| `400` | `Incorrect email or password` | 邮箱或密码错误 |

---

#### 5.1.3 刷新 Token

```http
POST /api/v1/auth/refresh
```

**请求体**：

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**响应** (200):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "refreshed@example.com",
    "username": "RefreshedUser",
    "onboarding_completed": true,
    "created_at": "2026-05-11T00:00:00"
  }
}
```

**错误码**：

| 状态码 | detail | 触发条件 |
|--------|--------|---------|
| `401` | `Invalid refresh token` | Refresh Token 无效或已过期 |

---

### 5.2 画像模块 (Profile)

> **Tag**: `profile`  
> **Base URL**: `/api/v1/profile`  
> **认证**: ✅ 需要 JWT

#### 5.2.1 破冰对话 (AI 驱动)

```http
POST /api/v1/profile/onboarding/chat
```

通过 DeepSeek API 驱动的智能对话，逐轮收集学生的学习背景、认知风格、学习目标和时间分配四个维度的信息。

**请求体**：

```json
{
  "messages": [
    {
      "role": "user",
      "content": "我主要学习 Python 和机器学习"
    },
    {
      "role": "assistant",
      "content": "了解了！你目前在 Python 和机器学习方面..."
    }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `messages[].role` | string | ✅ | `"user"` 或 `"assistant"` |
| `messages[].content` | string | ✅ | 消息内容 |

**响应** (200):

```json
{
  "message": "很好！现在让我了解一下你的学习时间安排...",
  "options": ["每天 2-4 小时深度工作", "碎片化时间学习", "仅在周末有整块时间"],
  "phase": "questioning",
  "collected_data": null
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `message` | string | AI 下一轮对话消息 |
| `options` | string[] | 可选快捷回复选项 |
| `phase` | string | 对话阶段：`"questioning"` 或 `"summarizing"` |
| `collected_data` | object/null | 已收集的四维数据（总结阶段时返回） |

**对话阶段说明**：

```
questioning (提问阶段)
  │  AI 逐维度提问，收集: knowledge_base, cognitive_style,
  │  learning_goals, time_distribution
  │
  ▼
summarizing (总结阶段)
  │  AI 汇总收集到的数据，生成结构化画像
  │  collected_data 字段返回完整四维数据
  │
  ▼
  POST /onboarding → 提交给 AI 分析引擎
```

---

#### 5.2.2 提交破冰数据 & 生成画像

```http
POST /api/v1/profile/onboarding
```

将收集到的四维原始数据提交给 AI 分析引擎，生成六维结构化学习画像并存入数据库。

**请求体**：

```json
{
  "responses": {
    "knowledge_base": ["Python", "Linear Algebra", "Machine Learning"],
    "cognitive_style": ["Code Practice", "Visual Learning"],
    "learning_goals": ["Job Hunting", "Master Deep Learning"],
    "time_distribution": ["Deep Work", "Weekend Intensive"],
    "notes": ["额外备注信息..."]
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `responses.knowledge_base` | string[] | ✅ | 已有知识基础列表 |
| `responses.cognitive_style` | string[] | ✅ | 认知风格偏好 |
| `responses.learning_goals` | string[] | ✅ | 学习目标 |
| `responses.time_distribution` | string[] | ✅ | 时间分配方式 |
| `responses.notes` | string[] | 否 | 额外备注 |

**响应** (200):

```json
{
  "student_id": "550e8400-e29b-41d4-a716-446655440000",
  "profile_data": {
    "knowledge_base_score": 75,
    "cognitive_style": "实践型 · 视觉偏好",
    "error_preference": "概念理解类错误",
    "learning_goals": "求职导向 · 深度学习专精",
    "focus_duration": 45,
    "stress_resistance": 72
  },
  "version": 1
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `profile_data.knowledge_base_score` | int | 知识基础评分 (0-100) |
| `profile_data.cognitive_style` | string | 认知风格标签 |
| `profile_data.error_preference` | string | 易错偏好分析 |
| `profile_data.learning_goals` | string | 学习目标简述 |
| `profile_data.focus_duration` | int | 建议专注时长 (分钟) |
| `profile_data.stress_resistance` | int | 抗压能力值 (0-100) |
| `version` | int | 画像版本号，每次更新递增 |

**六维画像说明**：

```
  knowledge_base_score    cognitive_style     error_preference
        (0-100)            (风格标签)          (易错偏好)
            ┌─────┬───────────┬───────────┬──────────┐
            │     │           │           │          │
            ▼     ▼           ▼           ▼          ▼
        [ 知识基础 ]  [ 认知风格 ]  [ 易错偏好 ]  [ 学习目标 ]
        [ 专注时长 ]  [ 抗压能力 ]
            ▲          ▲
            │          │
     focus_duration  stress_resistance
        (min)          (0-100)
```

**AI 降级**：当 DeepSeek API 不可用时，返回默认画像：
- `knowledge_base_score`: 50
- `cognitive_style`: "均衡型"
- `focus_duration`: 30

---

#### 5.2.3 获取我的画像

```http
GET /api/v1/profile/me
```

**响应** (200):

```json
{
  "student_id": "550e8400-e29b-41d4-a716-446655440000",
  "profile_data": {
    "knowledge_base_score": 75,
    "cognitive_style": "实践型 · 视觉偏好",
    "error_preference": "概念理解类错误",
    "learning_goals": "求职导向 · 深度学习专精",
    "focus_duration": 45,
    "stress_resistance": 72
  },
  "version": 1
}
```

**错误码**：

| 状态码 | detail | 触发条件 |
|--------|--------|---------|
| `404` | `尚未创建个人画像，请先完成破冰流程。` | 用户未完成破冰 |

---

#### 5.2.4 更新我的画像

```http
PUT /api/v1/profile/me
```

请求体格式同 `POST /onboarding`。若 AI 分析成功则更新六维画像，失败则仅更新原始数据并保留原画像。

**错误码**：

| 状态码 | detail | 触发条件 |
|--------|--------|---------|
| `404` | `尚未创建个人画像，请先完成破冰流程。` | 用户无画像记录 |

---

### 5.3 内容工厂 (Factory) ★ 核心模块

> **Tag**: `factory`  
> **Base URL**: `/api/v1/factory`  
> **认证**: ✅ 需要 JWT

内容工厂是 EduNexus 的核心模块。用户输入一个学习主题，系统自动启动多智能体流水线，由 7 个专业 AI Agent 分工协作，生成覆盖讲授、思维导图、测验、视频脚本、代码实验和审核报告的完整教学资源包。

#### 5.3.1 触发生成任务

```http
POST /api/v1/factory/generate
```

**请求体**：

```json
{
  "topic": "梯度下降算法的几何解释"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `topic` | string | ✅ | 学习主题，支持中英文，建议具体而非宽泛 |

**响应** (200):

```json
{
  "task_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "running"
}
```

**执行流程**：

```
POST /generate
  │
  ▼
┌────────────────────────────────────────────────────────────┐
│  1. 创建 GenerationTask (status=pending)                    │
│  2. 返回 task_id 给前端                                     │
│  3. 后台启动 asyncio Task                                   │
│      │                                                      │
│      ▼                                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           AgentOrchestrator.run_pipeline()           │  │
│  │                                                      │  │
│  │  Manager Agent (1.2s)                                │  │
│  │    │  分析主题 → 拆解任务 → 制定执行计划              │  │
│  │    │                                                  │  │
│  │    └─── 5 专家并行执行 ───                            │  │
│  │    │                                                  │  │
│  │    ├── Professor Agent  → 📄 结构化讲义 (document)    │  │
│  │    ├── Architect Agent  → 🗺️ 思维导图 (mindmap)      │  │
│  │    ├── Examiner Agent   → 📝 测验评估 (quiz)          │  │
│  │    ├── Director Agent   → 🎬 视频脚本 (video_script)  │  │
│  │    └── Hacker Agent     → 💻 代码实验 (code_lab)      │  │
│  │                                                      │  │
│  │  Reviewer Agent                                      │  │
│  │    → 🔍 审核报告 (review_report)                     │  │
│  │    → 幻觉风险评估 + 质量评分 + 改进建议                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  全程通过 WebSocket 实时推送状态和日志                       │
└────────────────────────────────────────────────────────────┘
```

---

#### 5.3.2 查询任务状态

```http
GET /api/v1/factory/status/{task_id}
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | UUID | ✅ | 任务 ID |

**响应** (200):

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "topic": "梯度下降算法的几何解释",
  "status": "completed",
  "agents_status": {
    "manager": "success",
    "professor": "success",
    "architect": "success",
    "examiner": "success",
    "director": "success",
    "hacker": "success",
    "reviewer": "success"
  },
  "created_at": "2026-05-11T14:30:00"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | UUID | 任务唯一 ID |
| `topic` | string | 学习主题 |
| `status` | string | 任务状态：`pending` / `running` / `completed` / `failed` |
| `agents_status` | object | 各 Agent 执行状态，key 为 Agent 名称，value 为 `idle` / `running` / `success` / `error` |
| `created_at` | datetime | 创建时间 |

---

#### 5.3.3 获取任务资源列表

```http
GET /api/v1/factory/resources/{task_id}
```

**响应** (200):

```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "task_id": "660e8400-e29b-41d4-a716-446655440001",
    "agent_type": "professor",
    "resource_type": "document",
    "content": {
      "title": "梯度下降算法的几何解释",
      "sections": [
        {
          "heading": "1. 引言：为什么需要梯度下降",
          "body": "在机器学习中，我们经常需要..."
        },
        {
          "heading": "2. 梯度的几何意义",
          "body": "梯度是一个向量，指向函数值增长最快的方向..."
        }
      ]
    },
    "status": "completed"
  }
]
```

**各 Agent 产出的 content 格式**：

```typescript
// Professor (document) - 结构化讲义
{
  "title": "string",
  "sections": [
    { "heading": "章节标题", "body": "章节正文" }
  ]
}

// Architect (mindmap) - 思维导图
{
  "mindmap": {
    "root": "根节点名称",
    "children": [
      {
        "name": "分支名",
        "children": [
          { "name": "子节点", "children": [] }
        ]
      }
    ]
  }
}

// Examiner (quiz) - 测验题库
{
  "questions": [
    {
      "question": "题目",
      "options": ["A", "B", "C", "D"],
      "answer": "正确答案",
      "explanation": "解析"
    }
  ]
}

// Director (video_script) - 视频脚本
{
  "scenes": [
    {
      "scene_number": 1,
      "title": "场景标题",
      "visual": "画面描述",
      "voiceover": "旁白台词",
      "duration_seconds": 30
    }
  ]
}

// Hacker (code_lab) - 代码实验
{
  "title": "实验标题",
  "description": "实验说明",
  "code": "print('Hello World')",
  "expected_output": "期望输出",
  "exercises": ["扩展练习1", "扩展练习2"]
}

// Reviewer (review_report) - 审核报告
{
  "hallucination_risk": "low",
  "quality_score": 92,
  "suggestions": ["改进建议1", "改进建议2"],
  "difficulty_assessment": "中等偏难，适合有一定基础的学习者"
}
```

---

#### 5.3.4 获取最新生成任务

```http
GET /api/v1/factory/latest
```

返回当前用户最近一次创建的任务状态。响应格式同 [5.3.2 查询任务状态](#532-查询任务状态)。

---

#### 5.3.5 与智能体对话

```http
POST /api/v1/factory/agent/{agent_id}/chat
```

与指定的智能体进行深度对话，用于对已生成内容进行追问、修改或深入讨论。

**路径参数**：

| 参数 | 类型 | 可选值 |
|------|------|--------|
| `agent_id` | string | `professor` / `architect` / `examiner` / `director` / `hacker` / `reviewer` |

**请求体**：

```json
{
  "message": "请用更简单的例子重新解释梯度下降"
}
```

**响应** (200):

```json
{
  "reply": "关于「请用更简单的例子重新解释梯度下降」，作为professor智能体，我认为：...",
  "agent_type": "professor"
}
```

---

#### 5.3.6 WebSocket 实时流 (详见第 6 章)

```http
WS /api/v1/factory/stream/{task_id}?token=<jwt_token>
```

---

### 5.4 学习路径 (Graph)

> **Tag**: `graph`  
> **Base URL**: `/api/v1/graph`  
> **认证**: ✅ 需要 JWT

学习路径模块将学习目标转化为可视化的知识图谱（DAG 有向无环图），帮助学生系统性地规划学习路线。系统根据学生画像自动判断是否需要插入补充节点。

#### 5.4.1 规划学习路径

```http
POST /api/v1/graph/plan
```

**请求体**：

```json
{
  "goal": "Transformer Architecture"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `goal` | string | ✅ | 学习目标 |

**响应** (200):

```json
{
  "graph_id": "880e8400-e29b-41d4-a716-446655440003",
  "title": "Transformer 架构学习路径",
  "nodes": [
    {
      "id": "node-1",
      "label": "注意力机制基础",
      "type": "standard",
      "proficiency": 0.8,
      "status": "completed"
    },
    {
      "id": "node-2",
      "label": "自注意力 (Self-Attention)",
      "type": "standard",
      "proficiency": 0.5,
      "status": "active"
    },
    {
      "id": "inject-1",
      "label": "线性代数复习：矩阵乘法",
      "type": "injected",
      "proficiency": 0.0,
      "status": "pending"
    },
    {
      "id": "node-3",
      "label": "多头注意力 (Multi-Head)",
      "type": "standard",
      "proficiency": 0.0,
      "status": "pending"
    }
  ],
  "edges": [
    { "from": "node-1", "to": "node-2", "isDynamic": false },
    { "from": "inject-1", "to": "node-2", "isDynamic": true },
    { "from": "node-2", "to": "node-3", "isDynamic": false }
  ],
  "analysis_summary": "基于你的学习画像（知识基础 75 分），规划了从注意力机制基础到 Transformer 完整架构的 4 阶段学习路径。注意到你的线性代数基础较弱（分值 < 60），已自动插入补充节点。"
}
```

**节点类型说明**：

| type | 含义 | 触发条件 |
|------|------|---------|
| `standard` | 标准节点 | 正常学习路径节点 |
| `injected` | 补充节点 | 当学生画像薄弱 (knowledge_base < 60) 时自动插入 |

**节点状态说明**：

| status | 含义 |
|--------|------|
| `completed` | 已完成（proficiency ≥ 0.8） |
| `active` | 正在学习（0 < proficiency < 0.8） |
| `pending` | 待学习（proficiency = 0） |

**DAG 可视化示意**：

```
  [node-1] completed ──→ [node-2] active ──→ [node-3] pending
                              ▲
                              │ (isDynamic: true)
                              │
                       [inject-1] pending
                       (补充节点·线性代数)
```

**AI 降级**：当 Gemini API 不可用时，返回预置的默认路径（含 4 个节点的基础线性路径）。

---

#### 5.4.2 获取课程图谱

```http
GET /api/v1/graph/{course_id}
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `course_id` | string | ✅ | 课程标识符 |

**响应** (200):

```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "course_id": "cs-ml-101",
  "title": "Transformer 架构学习路径",
  "nodes": [...],
  "edges": [...],
  "version": 1
}
```

---

#### 5.4.3 获取个人学习路径

```http
GET /api/v1/graph/path/{student_id}
```

获取指定学生的最新学习路径。

**响应**：同 [5.4.2](#542-获取课程图谱)。

---

#### 5.4.4 获取节点资源

```http
GET /api/v1/graph/node/{node_id}/resources
```

获取与某知识节点关联的学习资源列表。

**响应** (200):

```json
{
  "node_id": "node-1",
  "resources": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "agent_type": "professor",
      "resource_type": "document",
      "content": { "title": "注意力机制详解" },
      "status": "completed"
    }
  ]
}
```

---

### 5.5 资源推送 (Resources)

> **Tag**: `resources`  
> **Base URL**: `/api/v1/resources`  
> **认证**: ✅ 需要 JWT

资源推送模块为学生提供每日个性化学习资源推荐和行业热点追踪。

#### 5.5.1 今日推荐资源

```http
GET /api/v1/resources/today
```

**响应** (200):

```json
[
  {
    "id": "ai-1",
    "resource_type": "document",
    "title": "Large Language Models: A Survey",
    "description": "全面介绍大语言模型的发展历程、架构变体和未来方向，涵盖 Transformer 到 GPT-4 的演进",
    "status": "current",
    "ai_reason": "基于你的学习画像，推荐从 LLM 核心理论入手，为后续实践打基础",
    "duration": "20 min read",
    "url": "https://arxiv.org/abs/2302.07142"
  },
  {
    "id": "ai-2",
    "resource_type": "video",
    "title": "Transformer 架构深度解析",
    "description": "逐层讲解 Transformer 的 Self-Attention 机制、位置编码和多头注意力原理",
    "status": "completed",
    "ai_reason": "理解架构是实现高效推理的前提",
    "duration": "15 min",
    "url": "https://huggingface.co/learn/deep-rl-course/unit0/introduction"
  }
]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `resource_type` | string | 资源类型：`video` / `document` / `code` / `quiz` |
| `status` | string | 学习状态：`current` / `completed` / `locked` |
| `ai_reason` | string | AI 推荐理由 |
| `duration` | string | 预估学习时长 |

**资源状态流转**：

```
locked (锁定) → current (当前) → completed (已完成)
```

---

#### 5.5.2 获取行业热点

```http
GET /api/v1/resources/trending
```

从 HackerNews、GitHub、Arxiv 聚合 CS 领域热点内容，API 不可用时使用 mock 数据。

**响应** (200):

```json
[
  {
    "source": "HackerNews",
    "title": "Rust 内存安全机制深度解析",
    "meta": "Top story · 856 points",
    "tag": "Systems",
    "url": "https://news.ycombinator.com/news"
  },
  {
    "source": "GitHub",
    "title": "vllm: 大模型推理性能提升 24 倍",
    "meta": "72k stars",
    "tag": "AI/ML",
    "url": "https://github.com/vllm-project/vllm"
  },
  {
    "source": "Arxiv",
    "title": "Mixture of Experts 前沿研究综述",
    "meta": "Hot in cs.LG",
    "tag": "Research",
    "url": "https://arxiv.org/list/cs.AI/recent"
  }
]
```

**数据源**：

| 数据源 | API | 说明 |
|--------|-----|------|
| HackerNews | hn.algolia.com/api | 实时科技讨论 |
| GitHub | api.github.com/search | 热门开源仓库 |
| Arxiv | export.arxiv.org/api | 最新 AI 论文 |

---

#### 5.5.3 获取资源详情

```http
GET /api/v1/resources/{resource_id}
```

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `resource_id` | UUID | ✅ | 资源 ID |

**响应** (200):

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "agent_type": "professor",
  "resource_type": "document",
  "content": {
    "title": "梯度下降算法详解",
    "sections": [{ "heading": "...", "body": "..." }]
  },
  "status": "completed"
}
```

---

#### 5.5.4 更新学习进度

```http
PUT /api/v1/resources/{resource_id}/progress
```

**请求体**：

```json
{
  "status": "completed",
  "progress_percentage": 100.0,
  "time_spent": 25
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `status` | string | ✅ | 学习状态：`not_started` / `in_progress` / `completed` |
| `progress_percentage` | float | 否 | 进度百分比 (0-100) |
| `time_spent` | int | 否 | 已花费时间 (分钟) |

**响应** (200):

```json
{
  "message": "进度已更新",
  "resource_id": "770e8400-e29b-41d4-a716-446655440002",
  "status": "completed"
}
```

---

### 5.6 智能辅导 (Tutor)

> **Tag**: `tutor`  
> **Base URL**: `/api/v1/tutor`  
> **认证**: ✅ 需要 JWT

智能辅导模块提供 AI 导师对话功能，支持基于关键词匹配的智能问答。

#### 5.6.1 向 AI 导师提问

```http
POST /api/v1/tutor/chat
```

**请求体**：

```json
{
  "message": "如何理解微积分中的极限概念？",
  "context": "我目前在学习高等数学基础课程"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message` | string | ✅ | 提问内容 |
| `context` | string | 否 | 上下文背景信息 |

**响应** (200):

```json
{
  "reply": "微积分是数学的重要分支。理解微积分的关键在于掌握极限的概念...",
  "message_id": "1715434200.123",
  "agent_type": "tutor",
  "timestamp": "2026-05-11T14:35:00"
}
```

**支持的关键词领域**：

| 关键词 | 领域 |
|--------|------|
| 微积分 / 导数 / 积分 | 微积分 |
| 线性代数 / 矩阵 / 向量 | 线性代数 |
| 编程 / 代码 / 程序 | 编程 |
| 学习 / 方法 / 效率 | 学习方法 |
| 考试 / 准备 / 复习 | 考试准备 |

---

#### 5.6.2 获取对话历史

```http
GET /api/v1/tutor/history?limit=10
```

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `limit` | int | 否 | 10 | 返回的历史记录条数上限 |

**响应** (200):

```json
[
  {
    "id": "1",
    "topic": "微积分基础",
    "preview": "如何理解微积分的基本概念？",
    "timestamp": "2024-05-11T10:30:00",
    "message_count": 5
  }
]
```

---

### 5.7 学习评估 (Assessment)

> **Tag**: `assessment`  
> **Base URL**: `/api/v1/assessment`  
> **认证**: ✅ 需要 JWT

学习评估模块提供周学情报告、学习统计（雷达图数据）和学习历史记录。

#### 5.7.1 周学情报告

```http
GET /api/v1/assessment/weekly
```

**响应** (200):

```json
{
  "study_hours": 12.5,
  "completed_courses": 3,
  "average_score": 85,
  "knowledge_mastery": 72.5,
  "week_start": "2026-05-04T00:00:00",
  "week_end": "2026-05-11T00:00:00"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `study_hours` | float | 本周学习总时长 (小时) |
| `completed_courses` | int | 已完成课程数 |
| `average_score` | int | 测验平均分 |
| `knowledge_mastery` | float | 知识点掌握率 (%) |
| `week_start` | string | 统计周期起始日期 |
| `week_end` | string | 统计周期截止日期 |

**计算逻辑**：

```
study_hours     = 本周生成资源数 × 15min / 60
completed_courses = COUNT(completed tasks, last 7d)
average_score   = 85 (默认值)
knowledge_mastery = (completed_nodes / total_nodes) × 100%
```

---

#### 5.7.2 学习统计数据 (雷达图)

```http
GET /api/v1/assessment/stats
```

返回最近 30 天的学习数据，用于前端渲染雷达图。

**响应** (200):

```json
{
  "subjects": ["数学", "物理", "编程", "英语", "逻辑", "创意"],
  "scores": [85, 60, 92, 45, 78, 30],
  "trend": [
    ["2026-05-01", 3],
    ["2026-05-03", 5],
    ["2026-05-05", 2]
  ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `subjects` | string[] | 学科名称列表 |
| `scores` | int[] | 各学科得分 (0-100，已标准化) |
| `trend` | array | 学习趋势 (日期, 资源创建数量) |

**六维雷达图示意**：

```
              数学 (85)
               /\
              /  \
   创意(30)  /    \  物理(60)
           /   📊  \
          /        \
   逻辑(78)────────  编程(92)
          \        /
           \      /
            \    /
            英语(45)
```

---

#### 5.7.3 学习历史记录

```http
GET /api/v1/assessment/history?limit=10
```

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `limit` | int | 否 | 10 | 返回条数上限 |

**响应** (200):

```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "title": "梯度下降算法详解",
    "type": "document",
    "completed_at": "2026-05-11T14:35:00",
    "score": 0,
    "duration": "10 min read"
  }
]
```

---

### 5.8 系统 (System)

#### 5.8.1 健康检查

```http
GET /health
```

无需认证。用于服务可用性探测。

**响应** (200):

```json
{
  "status": "healthy"
}
```

---

## 6. WebSocket 实时通信

### 6.1 连接端点

```
ws://localhost:8001/api/v1/factory/stream/{task_id}?token=<jwt_access_token>
```

### 6.2 认证方式

Token 通过 URL 查询参数传递，服务端通过 `python-jose` 验证 JWT 签名和有效期。

### 6.3 心跳机制

| 方向 | 消息 | 说明 |
|------|------|------|
| Client → Server | `ping` | 客户端心跳 |
| Server → Client | `pong` | 服务端心跳响应 |

### 6.4 服务端推送事件

#### 事件一：智能体状态变更

```json
{
  "type": "agent_status",
  "agent": "professor",
  "status": "running",
  "timestamp": "2026-05-11T14:30:01"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | string | 固定值 `"agent_status"` |
| `agent` | string | Agent 名称：`manager` / `professor` / `architect` / `examiner` / `director` / `hacker` / `reviewer` |
| `status` | string | 状态：`running` / `success` / `error` |
| `timestamp` | string | 事件时间戳 |

#### 事件二：智能体日志

```json
{
  "type": "agent_log",
  "agent": "professor",
  "message": "正在生成「梯度下降」的讲义大纲...",
  "log_type": "info",
  "timestamp": "2026-05-11T14:30:02"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | string | 固定值 `"agent_log"` |
| `agent` | string | Agent 名称 |
| `message` | string | 日志内容 |
| `log_type` | string | 日志级别：`info` / `success` / `warn` |
| `timestamp` | string | 事件时间戳 |

#### 事件三：任务完成

```json
{
  "type": "task_complete",
  "taskId": "660e8400-e29b-41d4-a716-446655440001",
  "status": "completed"
}
```

#### 事件四：错误通知

```json
{
  "type": "error",
  "message": "Gemini API 调用超时，已使用降级策略"
}
```

### 6.5 前端轮询兜底

当 WebSocket 连接失败时，前端自动切换为 3 秒间隔的 HTTP 轮询：

```
GET /api/v1/factory/status/{task_id}   (每 3 秒)
```

任务完成后停止轮询，调用 `GET /api/v1/factory/resources/{task_id}` 获取资源列表。

### 6.6 完整通信时序图

```
Client                          Server
  │                                │
  │──── WS connect (token) ───────→│  JWT 验证
  │←─── connected ──────────────── │
  │                                │
  │                                │  │ Manager 开始分析
  │←─── agent_status (manager) ──  │  │
  │←─── agent_log (manager) ─────  │  │
  │                                │  │
  │                                │  │ 5 专家并行执行
  │←─── agent_status (professor) ──│  │
  │←─── agent_log (professor) ─── │  │
  │←─── agent_status (architect) ──│  │
  │←─── agent_log (architect) ─── │  │
  │←─── agent_status (examiner) ── │  │
  │←─── agent_log (examiner) ──── │  │
  │                                │  │
  │──── ping ──────────────────────→│  (心跳)
  │←─── pong ───────────────────── │
  │                                │  │
  │                                │  │ Reviewer 审核完成
  │←─── task_complete ──────────── │  │
  │                                │
  │─── GET /resources/{taskId} ───→│  获取最终资源
  │←─── [Resource[], ...] ──────── │
  │                                │
  │─── × WS disconnect ───────────→│
```

---

## 7. 多智能体流水线架构

### 7.1 Agent 角色定义

| Agent | 角色 | 产出类型 | 核心能力 |
|-------|------|---------|---------|
| **Manager** | 主控中枢 | 任务分解计划 | 分析主题 → 拆解子任务 → 规划执行优先级 |
| **Professor** | 教授 | 📄 document | 结构化讲义、章节划分、学术性内容 |
| **Architect** | 架构师 | 🗺️ mindmap | 思维导图、知识结构树、概念关系图 |
| **Examiner** | 考官 | 📝 quiz | 选择题 + 简答题、答案 + 详细解析 |
| **Director** | 导演 | 🎬 video_script | 视频分镜脚本 (场景/画面/旁白/时长) |
| **Hacker** | 极客 | 💻 code_lab | 代码示例、编程实验、扩展练习 |
| **Reviewer** | 审查员 | 🔍 review_report | 幻觉风险/质量评分/难度评估/改进建议 |

### 7.2 流水线执行流程

```
                     POST /generate { topic }
                            │
                            ▼
              ┌─────────────────────────┐
              │   Manager Agent (1.2s)   │
              │   任务分析 + 拆解 + 规划   │
              └────────────┬────────────┘
                           │
         ┌─────────────────┼─────────────────┬─────────────────┬─────────────────┐
         │                 │                 │                 │                 │
         ▼                 ▼                 ▼                 ▼                 ▼
   ┌──────────┐    ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
   │Professor │    │Architect │     │Examiner  │     │Director  │     │  Hacker  │
   │  讲义    │    │ 思维导图  │     │  测验    │     │ 视频脚本  │     │ 代码实验  │
   └────┬─────┘    └────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
        │               │               │               │               │
        └───────────────┼───────────────┼───────────────┼───────────────┘
                        │               │               │
                        └───────────────┼───────────────┘
                                        │
                                        ▼
                              ┌──────────────────┐
                              │  Reviewer Agent   │
                              │  质量审核 + 评分    │
                              │  幻觉风险 + 建议    │
                              └──────────────────┘
                                        │
                                        ▼
                              ┌──────────────────┐
                              │  7 个 Resource      │
                              │  全部写入数据库      │
                              │  WebSocket 推送完成  │
                              └──────────────────┘
```

### 7.3 v2.0.0 Agent 引擎 (开发中)

> v2.0.0 Agent 引擎在 `backend/app/agents/` 目录中隔离开发，目标是升级为类 Claude Code 的智能体系统。

| 维度 | v1.0.0 (当前) | v2.0.0 (开发中) |
|------|-------------|----------------|
| **LLM 驱动** | 字符串 Prompt + DeepSeek | LangChain + Google Gemini |
| **Agent 形态** | 字典 + 函数字段 | OOP 类 (`BaseAgent` 子类) |
| **编排方式** | asyncio.gather 并行 | AgentCoordinator 顺序流水线 |
| **工具调用** | 无 | `tools/` 目录 (学术检索、Markdown 生成) |
| **状态管理** | DB `agents_status` JSON | 内存态 `AgentStatusInfo` 对象 |

**v2.0.0 迭代路线**：

```
Phase 0 (当前)  Phase 1     Phase 2      Phase 3     Phase 4-7
  OOP骨架    →  Tool Use  →  异步并行  →  Memory  →  自主规划/反思/多模态
```

---

## 8. 错误处理

### 8.1 全局异常处理架构

EduNexus 实现了统一的全局异常处理器，所有未捕获异常都会经过规范化处理：

```
Exception
  │
  ├── HTTPException ─────→ 透传 status_code + detail
  │
  ├── RequestValidationError → 422 参数校验失败
  │
  ├── SQLAlchemyError ───→ 500 数据库操作失败
  │
  ├── Exception (通用) ──→ 503 AI 服务暂不可用
  │
  └── 未处理异常 ────────→ 500 服务器内部错误
```

### 8.2 错误响应格式

所有错误响应均包含调试用 `error_id` 和 `timestamp`：

```json
{
  "detail": "具体错误描述，可能是 string 或 array",
  "error_id": "ERR-20260511143022123",
  "timestamp": "2026-05-11T14:30:22.123456"
}
```

### 8.3 AI 服务降级策略

| 场景 | 降级策略 |
|------|---------|
| Gemini API 不可用 | `ContentGenerator` 返回结构化 mock 数据 |
| DeepSeek API 不可用 | `ProfileAnalyzer` 返回默认画像 (50分/均衡型/30min) |
| HackerNews API 不可用 | `GET /trending` 使用内置 fallback 数据 |
| Arxiv API 不可用 | `GET /trending` 使用内置 fallback 数据 |

---

## 9. 数据库模型

### 9.1 ER 图

```
┌──────────────┐       ┌──────────────────┐
│   students    │       │ student_profiles  │
├──────────────┤       ├──────────────────┤
│ id (PK, UUID)│──1:1──│ student_id (FK)   │
│ email        │       │ profile_data (JSON)│
│ username     │       │ raw_responses     │
│ password     │       │ version           │
│ onboarding   │       └──────────────────┘
│ created_at   │
└──────┬───────┘
       │
       │ 1:N
       ├──────────────────────────────┐
       │                              │
       ▼                              ▼
┌──────────────────┐      ┌──────────────────┐
│ generation_tasks  │      │ knowledge_graphs  │
├──────────────────┤      ├──────────────────┤
│ id (PK, UUID)    │      │ id (PK, UUID)    │
│ student_id (FK)  │      │ student_id (FK)  │
│ topic            │      │ course_id        │
│ status           │      │ title            │
│ agents_status    │      │ nodes (JSON)     │
│ created_at       │      │ edges (JSON)     │
└────────┬─────────┘      │ analysis_summary │
         │                │ version          │
         │ 1:N            └──────────────────┘
         ▼
┌──────────────────┐
│generated_resources│
├──────────────────┤
│ id (PK, UUID)    │
│ task_id (FK)     │
│ student_id (FK)  │
│ agent_type       │
│ resource_type    │
│ content (JSON)   │
│ status           │
└──────────────────┘
```

### 9.2 表结构详解

#### students (用户表)

| 列 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| `id` | UUID | PK | 用户唯一标识 |
| `email` | String | UNIQUE, NOT NULL | 邮箱 |
| `username` | String | NOT NULL | 用户名 |
| `hashed_password` | String | NOT NULL | bcrypt 哈希密码 |
| `is_active` | Boolean | DEFAULT true | 账户激活状态 |
| `onboarding_completed` | Boolean | DEFAULT false | 是否完成破冰画像 |
| `created_at` | DateTime | DEFAULT now() | 注册时间 |

#### student_profiles (画像表)

| 列 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| `id` | UUID | PK | 记录 ID |
| `student_id` | UUID | FK→students, UNIQUE | 关联用户 |
| `profile_data` | JSON | NOT NULL | 六维结构化画像 |
| `raw_responses` | JSON | NULLABLE | 原始破冰对话数据 |
| `version` | Integer | DEFAULT 1 | 画像版本号 |
| `created_at` | DateTime | DEFAULT now() | 创建时间 |
| `updated_at` | DateTime | ON UPDATE | 更新时间 |

#### generation_tasks (生成任务表)

| 列 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| `id` | UUID | PK | 任务 ID |
| `student_id` | UUID | FK→students | 创建者 |
| `topic` | String | NOT NULL | 学习主题 |
| `status` | String | DEFAULT 'pending' | pending/running/completed/failed |
| `agents_status` | JSON | DEFAULT {} | 各 Agent 执行状态 |
| `created_at` | DateTime | DEFAULT now() | 创建时间 |
| `updated_at` | DateTime | ON UPDATE | 更新时间 |

#### generated_resources (生成资源表)

| 列 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| `id` | UUID | PK | 资源 ID |
| `task_id` | UUID | FK→generation_tasks | 所属任务 |
| `student_id` | UUID | FK→students | 所属用户 |
| `agent_type` | String | NOT NULL | 生成 Agent |
| `resource_type` | String | NOT NULL | document/mindmap/quiz/video_script/code_lab/review_report |
| `content` | JSON | DEFAULT {} | 资源内容 |
| `status` | String | DEFAULT 'pending' | 资源状态 |
| `created_at` | DateTime | DEFAULT now() | 创建时间 |

#### knowledge_graphs (知识图谱表)

| 列 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| `id` | UUID | PK | 图谱 ID |
| `student_id` | UUID | FK→students | 所属用户 |
| `course_id` | String | NULLABLE | 课程标识 |
| `title` | String | NOT NULL | 图谱标题 |
| `nodes` | JSON | NOT NULL | 节点数组 |
| `edges` | JSON | NOT NULL | 边数组 |
| `analysis_summary` | Text | NULLABLE | AI 分析摘要 |
| `version` | Integer | DEFAULT 1 | 版本号 |
| `created_at` | DateTime | DEFAULT now() | 创建时间 |

---

## 10. 附录

### 10.1 接口速查表

| # | 方法 | 端点 | 认证 | 说明 |
|---|------|------|------|------|
| 1 | `POST` | `/api/v1/auth/register` | ❌ | 用户注册 |
| 2 | `POST` | `/api/v1/auth/login` | ❌ | 用户登录 |
| 3 | `POST` | `/api/v1/auth/refresh` | ❌ | 刷新 Token |
| 4 | `POST` | `/api/v1/profile/onboarding/chat` | ✅ | AI 破冰对话 |
| 5 | `POST` | `/api/v1/profile/onboarding` | ✅ | 提交破冰数据 |
| 6 | `GET` | `/api/v1/profile/me` | ✅ | 获取我的画像 |
| 7 | `PUT` | `/api/v1/profile/me` | ✅ | 更新我的画像 |
| 8 | `POST` | `/api/v1/factory/generate` | ✅ | ★ 触发生成任务 |
| 9 | `GET` | `/api/v1/factory/status/{id}` | ✅ | 查询任务状态 |
| 10 | `GET` | `/api/v1/factory/resources/{id}` | ✅ | 获取任务资源 |
| 11 | `GET` | `/api/v1/factory/latest` | ✅ | 获取最新任务 |
| 12 | `POST` | `/api/v1/factory/agent/{id}/chat` | ✅ | 与智能体对话 |
| 13 | `WS` | `/api/v1/factory/stream/{id}` | ✅ | WebSocket 实时流 |
| 14 | `POST` | `/api/v1/graph/plan` | ✅ | 规划学习路径 |
| 15 | `GET` | `/api/v1/graph/{course_id}` | ✅ | 获取课程图谱 |
| 16 | `GET` | `/api/v1/graph/path/{student_id}` | ✅ | 获取个人路径 |
| 17 | `GET` | `/api/v1/graph/node/{id}/resources` | ✅ | 获取节点资源 |
| 18 | `GET` | `/api/v1/resources/today` | ✅ | 今日推荐资源 |
| 19 | `GET` | `/api/v1/resources/trending` | ✅ | 行业热点 |
| 20 | `GET` | `/api/v1/resources/{id}` | ✅ | 资源详情 |
| 21 | `PUT` | `/api/v1/resources/{id}/progress` | ✅ | 更新学习进度 |
| 22 | `POST` | `/api/v1/tutor/chat` | ✅ | 向 AI 导师提问 |
| 23 | `GET` | `/api/v1/tutor/history` | ✅ | 对话历史 |
| 24 | `GET` | `/api/v1/assessment/weekly` | ✅ | 周学情报告 |
| 25 | `GET` | `/api/v1/assessment/stats` | ✅ | 学习统计 (雷达图) |
| 26 | `GET` | `/api/v1/assessment/history` | ✅ | 学习历史记录 |
| 27 | `GET` | `/health` | ❌ | 健康检查 |

### 10.2 Agent 产出类型映射

| Agent | resource_type | content 结构 | 前端渲染方式 |
|-------|--------------|-------------|-------------|
| Professor | `document` | `{ title, sections[] }` | 多章节文档阅读器 |
| Architect | `mindmap` | `{ mindmap: { root, children[] } }` | SVG 交互式思维导图 |
| Examiner | `quiz` | `{ questions[] }` | 选择题/简答题交互 |
| Director | `video_script` | `{ scenes[] }` | 分镜脚本时间线 |
| Hacker | `code_lab` | `{ title, code, exercises[] }` | 代码编辑器 + 运行 |
| Reviewer | `review_report` | `{ hallucination_risk, quality_score, suggestions[] }` | 审核报告面板 |

### 10.3 环境变量参考

```ini
# 服务基础配置
PROJECT_NAME=EduNexus
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# 数据库
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=edunexus_password
POSTGRES_DB=edunexus
POSTGRES_PORT=5433
DATABASE_URL=postgresql+asyncpg://postgres:edunexus_password@localhost:5433/edunexus

# AI 模型
GOOGLE_API_KEY=<your-gemini-api-key>
GEMINI_MODEL=gemini-2.5-flash
DEEPSEEK_API_KEY=<your-deepseek-api-key>
DEEPSEEK_MODEL=deepseek-chat

# 演示模式 (跳过真实LLM调用)
DEMO_MODE=false
```

### 10.4 技术亮点总结

| 亮点 | 说明 |
|------|------|
| **多智能体协同** | 7 个 AI Agent 各司其职，Manager 调度 + 5 专家并行 + Reviewer 审核 |
| **实时推送** | WebSocket 全程推送 Agent 状态和日志，轮询兜底保障可靠性 |
| **双模型冗余** | Gemini 主模型 + DeepSeek 辅助 + AI 降级 fallback 三级保障 |
| **JWT 双 Token** | Access + Refresh Token，前端 axios 拦截器自动无感刷新 |
| **统一错误处理** | 全局异常处理器，分级错误码，含 error_id 追踪 |
| **画像驱动** | 六维学习画像贯穿全流程，影响内容工厂、路径规划、资源推送 |
| **自动化运维** | 启动时自动建表，Docker 一键部署 |
| **学术聚合** | 实时对接 HackerNews + GitHub + Arxiv 三大数据源 |

---

> **文档版本**: v1.0.0  
> **最后更新**: 2026-05-11  
> **维护团队**: EduNexus  
> **许可证**: 竞赛使用

*本文档基于实际代码审查生成，所有接口定义、请求/响应格式、状态码和错误处理均与后端 `backend/app/api/v1/` 实现保持一致。*
