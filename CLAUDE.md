# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中工作时提供指导。

## 常用命令

### 前端
- **开发服务器**: `cd EduNexus && npm run dev`
- **构建**: `cd EduNexus && npm run build`（执行 vue-tsc + vite build）
- **预览**: `cd EduNexus && npm run preview`
- **类型检查**: `cd EduNexus && npx vue-tsc --noEmit`

### 后端
- **conda**: `conda activate edunexus`
- **启动服务**: `cd backend && uvicorn app.main:app --reload --port 8001`
- **初始化数据库**: `cd backend && python -m app.seed`
- **Docker (PostgreSQL + Redis)**: `cd backend && docker-compose up -d`

## 项目概述

**EduNexus** 是一个 Vue 3 + TypeScript + Vite 的多智能体 AI 教育平台，采用暗色主题、Google AI Studio 风格 UI。平台实现了**五大核心模块**——多个专业 AI 智能体协同工作，完成从学生画像构建、内容生成、学习路径规划、资源推送到智能辅导与评估的完整教育闭环。

**当前阶段**: v1.0.0 前后端已全面完成，用于竞赛实机演示。v2.0.0 下一代 Agent 引擎在 `agents/` 目录中隔离开发中，目标是从 Prompt 驱动升级为具备 Tool Use、Memory、自主规划能力的类 Claude Code 智能体系统。

> **版本策略**: v1.0.0 代码保持稳定不变，v2.0.0 开发仅限 `backend/app/agents/` 和 `EduNexus/src/agents/` 目录。

---

## 前端技术栈

- **框架**: Vue 3.5.32（Composition API，`<script setup lang="ts">`）
- **构建**: Vite 8.0.10 + vue-tsc 3.2.7 + TypeScript 6.0.2
- **路由**: vue-router 4.6.4（createWebHistory 模式）
- **样式**: Tailwind CSS 3.4.19 + autoprefixer 10.5.0 + postcss 8.5.13，纯暗色主题，CSS 变量
- **UI 组件**: shadcn-vue（基于 reka-ui 2.9.7、class-variance-authority 0.7.1、clsx 2.1.1、tailwind-merge 3.5.0）
- **图标**: lucide-vue-next 1.0.0
- **工具库**: @vueuse/core 14.3.0、@tanstack/vue-table 8.21.3
- **状态管理**: Pinia 3.0.4（authStore、profileStore、factoryStore、learningStore、deliveryStore、tutorStore、assessmentStore）
- **HTTP 客户端**: axios 1.16.0（`src/api/client.ts`，自动注入 JWT Token + Token 自动刷新 + 统一错误处理）
- **推荐 IDE 扩展**: Vue.volar（不要使用 Vetur）

## 后端技术栈

- **运行时**: Python 3.12+ / FastAPI（原生 async/await）
- **数据库**: PostgreSQL（pgvector 扩展）+ SQLAlchemy async
- **AI/LLM**: Google Gemini API（gemma-3-27b / gemini-2.5-flash）
- **实时通信**: FastAPI 内置 WebSocket
- **认证**: JWT（python-jose）+ bcrypt 密码哈希
- **部署**: Docker Compose（PostgreSQL:5433 + Redis:6379）

---

## 前端目录结构

```
EduNexus/
├── src/
│   ├── main.ts                          # 应用入口（createApp + Pinia + Router）
│   ├── App.vue                          # 根组件（仅含 <router-view />）
│   ├── style.css                        # Tailwind 指令 + 全局暗色样式 + Inter 字体
│   ├── env.d.ts                         # .vue 模块类型声明
│   ├── router/index.ts                  # 路由定义（7 条路由，/tutor 和 /assessment 未注册）
│   ├── api/                             # ★ API 客户端层（已实现）
│   │   ├── client.ts                    # axios 实例 + JWT 拦截器
│   │   ├── auth.ts                      # login(), register()
│   │   ├── profile.ts                   # submitOnboarding(), getMyProfile()
│   │   ├── factory.ts                   # generateContent(), getTaskStatus(), getTaskResources(), chatWithAgent()
│   │   ├── graph.ts                     # planPath(), getGraph(), getPersonalizedPath(), getNodeResources()
│   │   ├── resources.ts                 # getTodayResources(), getResourceDetail(), updateProgress(), getTrending()
│   │   └── websocket.ts                 # EduNexusWebSocket 类（自动重连 + 心跳 + 事件分发）
│   ├── types/                           # ★ TypeScript 类型定义（已实现）
│   │   ├── api.ts                       # ApiError, PaginatedResponse<T>
│   │   ├── auth.ts                      # User, LoginRequest, RegisterRequest, AuthResponse
│   │   ├── profile.ts                   # OnboardingSubmission, ProfileDimensions, ProfileResponse
│   │   ├── factory.ts                   # GenerateRequest, TaskStatusResponse, GeneratedResource, AgentChatRequest/Response, AgentLogEntry
│   │   ├── graph.ts                     # KnowledgeNode, KnowledgeEdge, PathPlanRequest/Response, KnowledgeGraphData
│   │   └── resources.ts                 # TodayResource, ResourceProgress, TrendingItem, ResourceDetail
│   ├── stores/                          # ★ Pinia 状态管理（已实现）
│   │   ├── authStore.ts                 # token/user/isLoggedIn/isOnboarded + localStorage 持久化
│   │   ├── profileStore.ts              # profileData/version + fetchProfile()
│   │   ├── factoryStore.ts              # 生成任务状态 + WebSocket 实时事件 + 轮询兜底 + 资源加载
│   │   ├── learningStore.ts             # 图谱节点/边 + 阶段分组 + plan()
│   │   └── deliveryStore.ts             # 今日资源 + 热点 + fetchAll() + updateResourceProgress()
│   ├── layouts/
│   │   └── DashboardLayout.vue          # 主布局（SidebarProvider + 侧边栏 + 顶栏 + 内容区）
│   ├── components/
│   │   ├── AppSidebar.vue               # 侧边栏导航（6 个菜单项 + 个人信息弹窗 + 退出登录）
│   │   ├── HelloWorld.vue               # 遗留的 Vite 脚手架文件（未使用，可删除）
│   │   └── ui/                          # shadcn-vue 组件库（~23 个组件系列）
│   │       ├── alert/ avatar/ badge/ breadcrumb/ button/ card/
│   │       ├── dialog/ dropdown-menu/ input/ label/ popover/
│   │       ├── process/                 # ★ 新增：Process 进度组件
│   │       ├── progress/ scroll-area/ separator/ sheet/
│   │       ├── sidebar/ skeleton/ tabs/ tooltip/
│   ├── views/
│   │   ├── LoginView.vue                # 登录页
│   │   ├── RegisterView.vue             # 注册页
│   │   ├── OnboardingView.vue           # 破冰对话式画像构建
│   │   ├── HomeView.vue                 # 仪表盘首页
│   │   ├── ContentFactory/              # 模块二：多智能体内容生成工作台
│   │   │   ├── index.vue                # 工作台主控
│   │   │   └── components/
│   │   │       ├── TopicInput.vue       # 主题关键词输入
│   │   │       ├── AgentStatusCard.vue  # 智能体状态卡片
│   │   │       ├── AgentTerminal.vue    # 日志终端
│   │   │       ├── ResourceDisplay.vue  # 5 标签页资源预览
│   │   │       └── AgentDetailView.vue  # 专家深度研讨室
│   │   ├── LearningPath/                # 模块三：学习路径规划
│   │   │   ├── index.vue                # 规划引擎主控
│   │   │   ├── types.ts                 # 类型定义（遗留，主类型已迁移至 src/types/graph.ts）
│   │   │   └── components/
│   │   │       └── KnowledgeGraph.vue   # SVG 交互式 DAG 图谱
│   │   └── Delivery/                    # 模块四（资源推送）
│   │       ├── index.vue                # 双栏布局
│   │       └── components/
│   │           ├── DeliveryHeader.vue   # 日期 + 进度条
│   │           ├── ResourceTimeline.vue # 资源时间线
│   │           ├── AgentInsightPanel.vue # 智能体状态面板
│   │           └── TrendingPanel.vue    # 行业热点面板
│   └── lib/
│       └── utils.ts                     # cn() 工具函数（clsx + twMerge）、valueUpdater
├── .env                                 # VITE_API_BASE_URL + VITE_WS_BASE_URL
├── components.json                      # shadcn-vue 配置
├── tailwind.config.js                   # Tailwind 配置
├── vite.config.ts                       # Vite 配置（@ 别名指向 ./src）
└── tsconfig*.json                       # TypeScript 配置
```

## 后端目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 入口 + CORS + lifespan 自动建表
│   ├── config.py                  # pydantic-settings 配置（DB/Gemini/JWT）
│   ├── seed.py                    # 测试数据种子（test@edunexus.com / 123456）
│   ├── api/
│   │   ├── deps.py                # 依赖注入（get_db, get_current_user via JWT）
│   │   └── v1/
│   │       ├── api.py             # 路由聚合器
│   │       ├── auth.py            # POST /register, POST /login
│   │       ├── profile.py         # POST /onboarding, GET /me
│   │       ├── factory.py         # POST /generate, GET /status/{id}, GET /resources/{id}, POST /agent/{id}/chat, WS /stream/{id}
│   │       ├── graph.py           # POST /plan, GET /{courseId}, GET /path/{studentId}, GET /node/{id}/resources
│   │       └── resources.py       # GET /today, GET /trending, GET /{id}, PUT /{id}/progress
│   ├── models/
│   │   ├── student.py             # Student（id, email, username, hashed_password, onboarding_completed）
│   │   ├── profile.py             # StudentProfile（profile_data JSON, raw_responses, version）
│   │   ├── factory.py             # GenerationTask（topic, status, agents_status）, GeneratedResource（agent_type, resource_type, content JSON）
│   │   └── graph.py               # KnowledgeGraph（title, nodes JSON, edges JSON, analysis_summary, version）
│   ├── schemas/
│   │   ├── auth.py                # UserCreate, UserLogin, UserResponse, Token
│   │   ├── profile.py             # OnboardingSubmission, ProfileDimensions, ProfileResponse
│   │   ├── factory.py             # GenerateRequest, TaskStatusResponse, ResourceResponse, AgentChatRequest/Response
│   │   ├── graph.py               # PathPlanRequest/Response, KnowledgeGraphResponse, KnowledgeNodeSchema, KnowledgeEdgeSchema, NodeResourcesResponse
│   │   └── resources.py           # TodayResourceResponse, ResourceDetailResponse, ProgressUpdateRequest, TrendingItem
│   ├── services/
│   │   ├── agent_orchestrator.py  # 多智能体流水线（Manager → 5专家并行 → Reviewer）+ WS 广播
│   │   ├── content_generator.py   # Gemini 调用 + 6 种 agent prompt + fallback mock
│   │   ├── profile_analyzer.py    # Gemini 分析破冰数据 → 6 维度画像 + fallback
│   │   └── path_planner.py        # Gemini 规划学习路径 → DAG nodes/edges + fallback
│   └── core/
│       ├── config.py              # Settings（DB URL, Gemini API key, JWT 密钥）
│       ├── database.py            # SQLAlchemy async engine + session
│       ├── security.py            # JWT access/refresh token + bcrypt 哈希
│       └── websocket.py           # WebSocketManager（按 task_id 分组广播）
├── .env                           # 后端环境变量
├── docker-compose.yml             # PostgreSQL:5433 + Redis:6379
└── requirements.txt               # fastapi, uvicorn, sqlalchemy, asyncpg, pydantic, google-generativeai, etc.
```

---

## 路由表

| 路径 | 名称 | 布局 | 组件 | 状态 |
|------|------|--------|-----------|--------|
| `/login` | `login` | 无（独立页面） | LoginView | ✅ 已完成 |
| `/register` | `register` | 无（独立页面） | RegisterView | ✅ 已完成 |
| `/onboarding` | `onboarding` | 无（独立页面） | OnboardingView | ✅ 已完成 |
| `/` | `home` | DashboardLayout | HomeView | ✅ 已完成 |
| `/factory` | `content-factory` | DashboardLayout | ContentFactory/index.vue | ✅ 已完成 |
| `/path` | `learning-path` | DashboardLayout | LearningPath/index.vue | ✅ 已完成 |
| `/delivery` | `resource-delivery` | DashboardLayout | Delivery/index.vue | ✅ 已完成 |
| `/tutor` | `tutor` | DashboardLayout | Tutor/index.vue | ✅ 已完成 |
| `/assessment` | `assessment` | DashboardLayout | Assessment/index.vue | ✅ 已完成 |

---

## 各界面后端 I/O 详表

> 以下记录每个界面实际调用/需要的后端 API，包含完整的请求和响应结构，方便调整后端定位。

### 1. 登录页（LoginView.vue）

| 方向 | 内容 |
|------|------|
| **请求** | `POST /api/v1/auth/login` — `{ email: string, password: string }` |
| **响应** | `{ access_token: string, refresh_token: string, token_type: "bearer", user: { id: UUID, email: string, username: string, onboarding_completed: boolean, created_at: datetime } }` |
| **前端处理** | authStore.setAuth() → 存入 localStorage，路由跳转（onboarded→/，未→/onboarding） |

### 2. 注册页（RegisterView.vue）

| 方向 | 内容 |
|------|------|
| **请求** | `POST /api/v1/auth/register` — `{ email: string, username: string, password: string }` |
| **响应** | 同 login 响应结构 |
| **前端处理** | authStore.setAuth() → 存入 localStorage，跳转 /onboarding |

### 3. 破冰画像页（OnboardingView.vue）

| 方向 | 内容 |
|------|------|
| **请求** | `POST /api/v1/profile/onboarding` — `{ responses: { knowledge_base: string[], cognitive_style: string[], learning_goals: string[], time_distribution: string[], notes: string[] } }` |
| **响应** | `{ student_id: UUID, profile_data: { knowledge_base_score: int(0-100), cognitive_style: string, error_preference: string, learning_goals: string, focus_duration: int(min), stress_resistance: int(0-100) }, version: int }` |
| **前端处理** | 调用 submitOnboarding() → profileStore.setProfile() → authStore.setOnboardingCompleted() → 路由跳转 / |
| **后端逻辑** | ProfileAnalyzer 调用 Gemini，将 4 维度原始数据转化为 6 维度结构化画像。Gemini 不可用时返回 fallback 默认值（50分/均衡型/30min） |

### 4. 仪表盘首页（HomeView.vue）

| 方向 | 内容 |
|------|------|
| **需要的数据** | ① 学生画像 `GET /api/v1/profile/me` ② 智能体状态（无直接 API，可从 factory/latest task 推断） ③ 评估摘要（已完成 API 对接） |
| **当前状态** | 已完成数据对接：profileStore.fetchProfile() 获取真实画像数据，6维卡片动态渲染，评估诊断由 `/assessment/stats` API 提供 |

### 5. 内容工厂（ContentFactory/index.vue）★ 核心模块

| 方向 | 内容 |
|------|------|
| **触发生成** | `POST /api/v1/factory/generate` — `{ topic: string }` |
| **触发响应** | `{ task_id: UUID, status: "running" }` |
| **实时推送** | `WS /api/v1/factory/stream/:taskId?token=xxx` |
| **WS 事件** | `{ type: "agent_status", agent: string, status: "running"/"success", timestamp: string }` |
| | `{ type: "agent_log", agent: string, message: string, type: "info"/"success"/"warn", timestamp: string }` |
| | `{ type: "task_complete", taskId: string, status: "completed" }` |
| | `{ type: "error", message: string }` |
| **轮询兜底** | `GET /api/v1/factory/status/:taskId` — `{ id: UUID, topic: string, status: string, agents_status: Dict, created_at: datetime }` |
| **获取资源** | `GET /api/v1/factory/resources/:taskId` — `[{ id, task_id, agent_type, resource_type, content: Dict, status }]` |
| **智能体对话** | `POST /api/v1/factory/agent/:agentId/chat` — `{ message: string }` → `{ reply: string, agent_type: string }` |
| **前端处理** | factoryStore.startGeneration() → WebSocket 连接 + 3s 轮询 → task_complete 时加载资源列表 |
| **后端流水线** | Manager 分析 1.2s → 5 专家并行（Professor/Architect/Examiner/Director/Hacker）→ Reviewer 审核 → 全程 WS 广播 |
| **资源产出格式** | professor: `{ title, sections: [{heading, body}] }` |
| | architect: `{ mindmap: { root, children: [{name, children}] } }` |
| | examiner: `{ questions: [{question, options[], answer, explanation}] }` |
| | director: `{ scenes: [{scene_number, title, visual, voiceover, duration_seconds}] }` |
| | hacker: `{ title, description, code, expected_output, exercises[] }` |
| | reviewer: `{ hallucination_risk: "low"/"medium"/"high", quality_score: int, suggestions[], difficulty_assessment: string }` |

### 6. 学习路径规划（LearningPath/index.vue）

| 方向 | 内容 |
|------|------|
| **规划路径** | `POST /api/v1/graph/plan` — `{ goal: string }` |
| **规划响应** | `{ graph_id: UUID, title: string, nodes: [{id, label, type:"standard"/"injected", proficiency: float(0-1), status:"completed"/"active"/"pending"}], edges: [{from, to, isDynamic: bool}], analysis_summary: string }` |
| **查图谱** | `GET /api/v1/graph/:courseId` — `{ id, course_id, title, nodes[], edges[], version }` |
| **查个人路径** | `GET /api/v1/graph/path/:studentId` — 同上结构 |
| **节点资源** | `GET /api/v1/graph/node/:nodeId/resources` — `{ node_id: string, resources: [{id, agent_type, resource_type, content, status}] }` |
| **前端处理** | learningStore.plan(goal) → 存储节点/边 → computed 自动按 status 分组为 phases → KnowledgeGraph.vue 渲染 |
| **后端逻辑** | PathPlanner 调用 Gemini 生成 4-6 个 DAG 节点。若学生画像薄弱（knowledge_base<60），自动插入 type="injected" 的补充节点。Gemini 不可用时返回 fallback 路径 |

### 7. 资源推送（Delivery/index.vue）

| 方向 | 内容 |
|------|------|
| **今日资源** | `GET /api/v1/resources/today` — `[{ id: UUID, resource_type: "video"/"document"/"code"/"quiz", title: string, description: string, status: "completed"/"current"/"locked", ai_reason: string|null, duration: string }]` |
| **热点** | `GET /api/v1/resources/trending` — `[{ source: string, title: string, meta: string, tag: string }]` |
| **资源详情** | `GET /api/v1/resources/:resourceId` — `{ id, agent_type, resource_type, content: Dict, status }` |
| **更新进度** | `PUT /api/v1/resources/:resourceId/progress` — `{ status: string, progress_percentage: float, time_spent: int }` → `{ message, resource_id, status }` |
| **前端处理** | deliveryStore.fetchAll() → todayResources + trendingItems → 组件渲染 |
| **后端逻辑** | /today 从 GeneratedResource 表取最近 10 条，映射 resource_type，第 1 条标 current、其余标 completed。/trending 返回硬编码 3 条热点 |

### 8. 智能指导（/tutor）— 已完成

| 方向 | 内容 |
|------|------|
| **提问** | `POST /api/v1/tutor/chat` — `{ message: string, context?: string }` → `{ reply: string, message_id: string, agent_type: string, timestamp: string }` |
| **历史记录** | `GET /api/v1/tutor/history?limit=10` — `[{ id, topic, preview, timestamp, message_count }]` |
| **前端处理** | TutorStore 管理对话状态，WebSocket 实时更新（已实现客户端对话），支持快捷问题提问 |
| **后端逻辑** | 先返回响应，后续可集成 Gemini API 实现更智能的问答 |

### 9. 学习效果评估（/assessment）— 已完成

| 方向 | 内容 |
|------|------|
| **周学情报告** | `GET /api/v1/assessment/weekly` — `{ study_hours, completed_courses, average_score, knowledge_mastery, week_start, week_end }` |
| **学习统计** | `GET /api/v1/assessment/stats` — `{ subjects, scores, trend }`（用于雷达图展示） |
| **历史记录** | `GET /api/v1/assessment/history?limit=10` — `[{ id, title, type, completed_at, score, duration }]` |
| **前端处理** | AssessmentStore 管理评估数据，HomeView 动态渲染 6 维画像和诊断结论，Assessment 页面展示详细统计 |

---

## 后端已实现 API 端点（与原规划的差异）

### 已实现

| 方法 | 端点 | 状态 | 与原规划差异 |
|------|------|------|-------------|
| `POST` | `/api/v1/auth/register` | ✅ | 无差异 |
| `POST` | `/api/v1/auth/login` | ✅ | 无差异 |
| `POST` | `/api/v1/profile/onboarding` | ✅ | 端点一致，响应结构已确定 |
| `GET` | `/api/v1/profile/me` | ✅ | ⚠️ 原规划为 `GET /profile`，实际为 `GET /profile/me` |
| `POST` | `/api/v1/factory/generate` | ✅ | 无差异 |
| `GET` | `/api/v1/factory/status/:taskId` | ✅ | 无差异 |
| `GET` | `/api/v1/factory/resources/:taskId` | ✅ | 无差异 |
| `WS` | `/api/v1/factory/stream/:taskId` | ✅ | 无差异 |
| `POST` | `/api/v1/factory/agent/:agentId/chat` | ✅ | 无差异 |
| `POST` | `/api/v1/graph/plan` | ✅ | 无差异 |
| `GET` | `/api/v1/graph/:courseId` | ✅ | 无差异 |
| `GET` | `/api/v1/graph/path/:studentId` | ✅ | 无差异 |
| `GET` | `/api/v1/graph/node/:nodeId/resources` | ✅ | 无差异 |
| `GET` | `/api/v1/resources/today` | ✅ | 无差异 |
| `GET` | `/api/v1/resources/trending` | ✅ | ⚠️ 当前返回硬编码 3 条，未对接外部 API |
| `GET` | `/api/v1/resources/:resourceId` | ✅ | 无差异 |
| `PUT` | `/api/v1/resources/:resourceId/progress` | ✅ | 无差异 |
| `POST` | `/api/v1/tutor/chat` | ✅ | 新增端点，原规划为 `ask` |
| `GET` | `/api/v1/tutor/history` | ✅ | 新增端点，返回对话历史 |
| `GET` | `/api/v1/assessment/weekly` | ✅ | 新增端点，周学情报告 |
| `GET` | `/api/v1/assessment/stats` | ✅ | 新增端点，学习统计 |
| `GET` | `/api/v1/assessment/history` | ✅ | 新增端点，历史记录 |
| `GET` | `/health` | ✅ | 健康检查，原规划无 |

### 新增实现（超出原规划）

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/api/v1/auth/refresh` | Token 刷新机制已实现，自动失效重试 |
| 全局异常处理 | `/api/v1/*` | 统一错误响应格式，包含 error_id 和 timestamp |

---

## 数据库表结构（实际实现）

| 表 | 字段 | 说明 |
|------|------|------|
| **students** | id(UUID PK), email(UNIQUE), username, hashed_password, is_active, onboarding_completed, created_at | 用户表 |
| **student_profiles** | id(UUID PK), student_id(FK UNIQUE), profile_data(JSON: 6维度), raw_responses(JSON: 原始对话), version, created_at, updated_at | 画像表 |
| **generation_tasks** | id(UUID PK), student_id(FK), topic, status(pending/running/completed/failed), agents_status(JSON), created_at, updated_at | 生成任务表 |
| **generated_resources** | id(UUID PK), task_id(FK), student_id(FK), agent_type, resource_type, content(JSON), status, created_at | 生成资源表（复用为学习进度表） |
| **knowledge_graphs** | id(UUID PK), student_id(FK), course_id(nullable), title, nodes(JSON), edges(JSON), proficiency_data(JSON), analysis_summary, version, created_at | 知识图谱表 |

### 新增的数据库表
- **tutor_conversations**: 辅导对话记录（实现中）
- **assessment_reports**: 评估报告（通过 GeneratedResource 表实现）

---

## 环境变量

### 前端 (`EduNexus/.env`)
```
VITE_API_BASE_URL=http://localhost:8001/api/v1
VITE_WS_BASE_URL=ws://localhost:8001/api/v1
```

### 后端 (`backend/.env`)
```
PROJECT_NAME=EduNexus
SECRET_KEY=your-super-secret-key-change-it-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=edunexus_password
POSTGRES_DB=edunexus
POSTGRES_PORT=5433
DATABASE_URL=postgresql+asyncpg://postgres:edunexus_password@localhost:5433/edunexus
GOOGLE_API_KEY=<your-key>
GEMINI_MODEL=gemma-3-27b
```

---

## UI 设计系统

- **背景色**: `#0b0b0b`，叠加微弱的点状/线状网格纹理
- **卡片样式**: rounded-2xl / rounded-3xl / rounded-[2.5rem]，zinc/gray/blue 色系，毛玻璃 backdrop-blur 效果
- **顶栏**: 固定定位 + 毛玻璃模糊，包含 SidebarTrigger + 搜索输入框
- **滚动条**: 6px 深色自定义样式（#303134）
- **字体**: Inter 字体族，通过 Google Fonts 加载
- **组件库**: shadcn-vue "new-york" 风格，Zinc 基准色
- **按钮主色**: blue-600，带 shadow-xl shadow-blue-900/40
- **卡片底色**: #131314 / #141414，边框 #303134 / white/5

### shadcn-vue 组件模式
- 每个组件在 `src/components/ui/` 下拥有独立目录
- 使用 `<script setup lang="ts">`，结合 reka-ui 的 `Primitive` 实现多态渲染
- 变体样式通过 `class-variance-authority`（cva）定义
- `index.ts` 桶文件统一导出组件和变体类型
- 使用 `@/lib/utils` 中的 `cn()` 合并类名

### 路径别名
- `@/` 映射到 `./src/`（在 vite.config.ts 和 tsconfig 中均有配置）

---

## 开发规范与约定

### 编写新代码时

- 统一使用 `<script setup lang="ts">`，禁止 Options API
- 路由级页面放在 `src/views/功能名/index.vue`，子组件放在 `src/views/功能名/components/`
- 共享组件放在 `src/components/`
- 禁止默认导出（default export）——使用具名导出 `defineProps<>()` 和 `defineEmits<>()`
- 类型定义放在 `src/types/` 独立文件中，避免内联类型
- Store 放在 `src/stores/`，组合式函数放在 `src/composables/`
- API 调用放在 `src/api/`，组件不直接调用 HTTP 客户端
- 所有条件类名合并使用 `@/lib/utils` 中的 `cn()`
- 遵循现有暗色主题视觉风格 — #0b0b0b 背景、rounded-2xl 卡片、zinc 色系

### 文件命名
- Vue 组件: PascalCase（如 `KnowledgeGraph.vue`）
- TypeScript 模块: camelCase（如 `utils.ts`）
- 目录: views 下用 PascalCase，components 下用 PascalCase 或 kebab-case

### 前后端协作约定

- 每个前端 `src/types/` 中的接口，对应后端 `schemas/` 中的 Pydantic 模型
- 修改类型定义时，两端必须同步更新
- API 端点统一使用 `/api/v1/` 前缀
- 所有端点（除 login/register）需要 JWT 认证（Bearer Token）
- WebSocket 端点同样需要 Token 验证（连接时通过 query param 传递：`?token=xxx`）
- 分页响应格式：`{ data: T[], total: number, page: number, page_size: number }`
- 错误响应格式：`{ detail: string }`（FastAPI HTTPException 标准格式）


---

## ★ v2.0.0 Agent 引擎（开发中）

> **关键原则**: v1.0.0 代码用于竞赛实机演示，保持不变。v2.0.0 的 agents 模块是完全隔离的下一代引擎，所有修改仅限于 `agents/` 文件夹内。

### v1.0.0 vs v2.0.0 架构对照

| 维度 | v1.0.0 (演示系统，稳定) | v2.0.0 Agent 引擎 (开发中) |
|------|------------------------|--------------------------|
| **LLM 驱动** | 字符串 Prompt + DeepSeek API (`LLMGateway`) | LangChain + Google Gemini (`LangChainUtils`) |
| **Agent 形态** | `ContentGenerator` 中的字典+函数字段 | OOP 类 (`BaseAgent` 子类，含 config/state/interrupt) |
| **编排方式** | `AgentOrchestrator` (asyncio.gather 并行 + WS 紧耦合) | `AgentCoordinator` (顺序流水线，纯业务逻辑) |
| **工具调用** | 无 | `tools/` 目录 (academic_search, markdown_generator 雏形) |
| **状态管理** | DB 字段 `agents_status` JSON | 内存态 `AgentStatusInfo` 对象，含 success/failure 计数 |
| **WebSocket** | 编排器内直接调用 `ws_manager.broadcast()` | 未接入（协调器与传输层解耦） |
| **集成状态** | 生产运行，API 路由直接引用 | 完全隔离，未被任何 v1.0.0 代码 import |
| **目标** | 稳定演示 | 类 Claude Code 的完善 Agent 系统 |

### 后端 agents 模块结构

```
backend/app/agents/
├── __init__.py                  # 桶文件，导出全部 Agent、Coordinator、类型
├── README.md                    # 模块技术文档
├── EXAMPLE_INTEGRATION.md       # 集成示例代码（API/WS/异步）
├── base/
│   └── BaseAgent.py             # 抽象基类 (execute/get_status/interrupt/_build_system_prompt)
├── coordinator/
│   └── AgentCoordinator.py      # 流水线编排：注册Agent → 顺序执行 → 状态追踪
├── implementations/
│   ├── ManagerAgent.py          # 主控中枢：任务分解、执行优先级规划
│   ├── ProfessorAgent.py        # 教授：学术性结构化教学内容
│   ├── ArchitectAgent.py        # 架构师：思维导图/知识结构树
│   ├── ExaminerAgent.py         # 考官：选择题+简答题评估材料
│   ├── DirectorAgent.py         # 导演：视频脚本(场景/旁白/时长)
│   ├── HackerAgent.py           # 极客：代码示例+编程练习
│   └── ReviewerAgent.py         # 审查员：幻觉风险/质量评分/改进建议
├── types/
│   └── __init__.py              # AgentStatus/AgentType Enum, AgentConfig/Context/Result/ExecutionResult/StatusInfo dataclass
├── tools/
│   ├── academic_search.py       # AcademicSearchTool: 学术检索（当前返回 mock）
│   └── markdown_generator.py    # MarkdownGeneratorTool: 内容→Markdown
└── utils/
    └── LangChainUtils.py        # LangChain 封装：模型初始化/Prompt模板/RunnableSequence
```

### 前端 agents 模块结构

```
EduNexus/src/agents/
├── index.ts                     # 桶文件
├── README.md                    # 模块技术文档
├── EXAMPLE_INTEGRATION.md       # 与 ContentFactory 集成的示例代码
├── base/
│   └── BaseAgent.ts             # 抽象基类 (execute/getStatus/interrupt)
├── coordinator/
│   └── AgentCoordinator.ts      # 流水线编排 (TS 版，async executePipeline)
├── implementations/
│   ├── ManagerAgent.ts          # 7 个 Agent 实现（TS 版，结构与后端同构）
│   ├── ProfessorAgent.ts
│   ├── ArchitectAgent.ts
│   ├── ExaminerAgent.ts
│   ├── DirectorAgent.ts
│   ├── HackerAgent.ts
│   └── ReviewerAgent.ts
├── types/
│   └── index.ts                 # AgentConfig/Context/Result/ExecutionResult/Status 接口
└── utils/
    └── LangChainUtils.ts        # @langchain/google-genai 封装
```

### 核心类型体系

```
AgentConfig      { id, name, role, capabilities[], timeout }
AgentContext     { task_id, topic, context?, user_input? }
AgentResult      { content, type, timestamp, quality_score?, log[] }
AgentExecutionResult { agent_id, status: AgentStatus, result?, error?, duration }
AgentStatusInfo  { agent_id, status, last_updated, current_task?, success_count, failure_count }
AgentStatus      Enum: idle | running | success | error
AgentType        Enum: manager | professor | architect | examiner | director | hacker | reviewer
```

### 流水线执行流程

```
AgentCoordinator.execute_pipeline(topic)
  → 生成 task_id
  → 按序遍历 [manager, professor, architect, examiner, director, hacker, reviewer]
  → 对每个 Agent:
      1. update_status(running)
      2. agent.execute(context)  → AgentExecutionResult
      3. update_status(success/error)
      4. 记录 duration, 累加 success/failure count
  → 返回 List[AgentExecutionResult]
```

### v2.0.0 迭代路线

> 从 Prompt 驱动到类 Claude Code 的演进路径。

| 阶段 | 目标 | 关键特征 |
|------|------|----------|
| **Phase 0** (当前) | OOP 骨架搭建 | BaseAgent 抽象、7 个 Agent 实现、Coordinator 顺序编排、LangChainUtils 基础封装 |
| **Phase 1** | Tool Use 能力 | Agent 可调用工具 (academic_search, code_exec, web_search)，实现 ReAct 循环 |
| **Phase 2** | 异步 + 并行 | Coordinator 支持 asyncio.gather 并行执行专家 Agent，接入 WebSocket 广播 |
| **Phase 3** | Memory 机制 | 短期对话记忆 + 长期学生画像记忆，Agent 可查询历史上下文 |
| **Phase 4** | 自主规划 | Manager Agent 具备动态任务分解能力，可根据主题自动选择参与的 Agent |
| **Phase 5** | 反思与自愈 | Agent 执行失败后自动重试/回退，Reviewer 结果反馈给上游 Agent 重新生成 |
| **Phase 6** | 多模态输出 | Agent 直接生成图表(SVG/Mermaid)、代码可执行沙箱、视频分镜可视化 |
| **Phase 7** | 生产集成 | 替换 v1.0.0 的 ContentGenerator + AgentOrchestrator，接入 FastAPI 路由 |

### 开发约束

1. **v1.0.0 代码不可修改** — `backend/app/services/`、`backend/app/api/`、`EduNexus/src/views/`、`EduNexus/src/stores/` 等全部保持原样
2. **修改仅限 agents/ 目录** — `backend/app/agents/` 和 `EduNexus/src/agents/` 是 v2.0.0 的专属开发区域
3. **前端 agents 模块为 TS 同构实现** — 用于未来可能的客户端侧 Agent 编排或可视化，当前不参与实际请求链路
4. **ProfessorAgent.py 存在语法错误** — 第 40-46 行有未缩进的 `<thought>` 标签伪代码和未定义变量 (`search_results`, `json`)，这是预留的 Tool Use 开发占位，Phase 1 时需修复
5. **BaseAgent.py 存在重复行** — 第 13-15 行 `self.system_prompt = self._build_system_prompt()` 重复 3 次，`interrupt()` 方法缺少 `pass`/实现，需后续清理
6. **LangChainUtils 使用同步 invoke** — 后端 `execute_chain` 应改为 `ainvoke` 以适配 FastAPI 异步模型
