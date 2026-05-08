# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中工作时提供指导。

## 常用命令

- **开发服务器**: `cd EduNexus && npm run dev`
- **构建**: `cd EduNexus && npm run build`（执行 vue-tsc + vite build）
- **预览**: `cd EduNexus && npm run preview`
- **类型检查**: `cd EduNexus && npx vue-tsc --noEmit`

## 项目概述

**EduNexus** 是一个 Vue 3 + TypeScript + Vite 的多智能体 AI 教育平台，采用暗色主题、Google AI Studio 风格 UI。平台实现了**五大核心模块**——多个专业 AI 智能体协同工作，完成从学生画像构建、内容生成、学习路径规划、资源推送到智能辅导与评估的完整教育闭环。

**当前阶段**: 前端 UI 已全部开发完毕，使用 Mock 数据模拟全流程交互。下一步进入后端开发与前后端对接阶段。

### 技术栈
- **框架**: Vue 3（Composition API，`<script setup lang="ts">`）
- **构建**: Vite 8 + vue-tsc 3 + TypeScript 6
- **路由**: vue-router 4（createWebHistory 模式）
- **样式**: Tailwind CSS 3 + autoprefixer + postcss，纯暗色主题，CSS 变量
- **UI 组件**: shadcn-vue（基于 reka-ui、class-variance-authority、clsx、tailwind-merge）
- **图标**: lucide-vue-next
- **工具库**: @vueuse/core
- **状态管理**: 暂无（仅使用局部 `ref`/`reactive`）。待后端对接时引入 Pinia
- **HTTP 客户端**: 尚未配置（axios/fetch）。所有数据通过 `setTimeout` 模拟
- **推荐 IDE 扩展**: Vue.volar（不要使用 Vetur）

### 目录结构

```
EduNexus/
├── src/
│   ├── main.ts                          # 应用入口
│   ├── App.vue                          # 根组件（仅含 <router-view />）
│   ├── style.css                        # Tailwind 指令 + 全局暗色样式 + Inter 字体
│   ├── env.d.ts                         # .vue 模块类型声明
│   ├── router/index.ts                  # 路由定义（8 条路由）
│   ├── layouts/
│   │   └── DashboardLayout.vue          # 主布局（SidebarProvider + 侧边栏 + 顶栏 + 内容区）
│   ├── components/
│   │   ├── AppSidebar.vue               # 侧边栏导航（6 个菜单项 + 个人信息弹窗 + 退出登录）
│   │   ├── HelloWorld.vue               # 遗留的 Vite 脚手架文件（未使用，可删除）
│   │   └── ui/                          # shadcn-vue 组件库（~22 个组件系列）
│   │       ├── alert/                   # Alert, AlertDescription, AlertTitle
│   │       ├── avatar/                  # Avatar, AvatarFallback, AvatarImage
│   │       ├── badge/                   # Badge
│   │       ├── breadcrumb/              # Breadcrumb + 6 子组件
│   │       ├── button/                  # Button
│   │       ├── card/                    # Card + 5 子组件
│   │       ├── dialog/                  # Dialog + 8 子组件
│   │       ├── dropdown-menu/           # DropdownMenu + 13 子组件
│   │       ├── input/                   # Input
│   │       ├── label/                   # Label
│   │       ├── popover/                 # Popover, PopoverContent, PopoverTrigger
│   │       ├── progress/                # Progress（基于 reka-ui ProgressRoot）
│   │       ├── scroll-area/             # ScrollArea, ScrollBar
│   │       ├── separator/               # Separator
│   │       ├── sheet/                   # Sheet + 7 子组件
│   │       ├── sidebar/                 # 侧边栏全家桶（~25 个子组件 + utils.ts）
│   │       ├── skeleton/                # Skeleton
│   │       ├── tabs/                    # Tabs, TabsContent, TabsList, TabsTrigger
│   │       └── tooltip/                 # Tooltip + 3 子组件
│   ├── views/
│   │   ├── LoginView.vue                # 登录页（表单 UI 完整）
│   │   ├── RegisterView.vue             # 注册页（4 字段表单，含图标前缀）
│   │   ├── OnboardingView.vue           # 破冰对话式画像构建（聊天 UI + 4 维度 + 画像预览）
│   │   ├── HomeView.vue                 # 仪表盘首页 — DAG 图谱、智能体状态、6 维画像、诊断
│   │   ├── ContentFactory/              # 模块二：多智能体内容生成工作台
│   │   │   ├── index.vue                # 工作台主控（流水线逻辑 + 7 智能体调度 + AgentDetailView 弹窗）
│   │   │   └── components/
│   │   │       ├── TopicInput.vue       # 主题关键词输入（渐变边框 + 快捷建议）
│   │   │       ├── AgentStatusCard.vue  # 单个智能体状态卡片（4 种状态样式 + 动画）
│   │   │       ├── AgentTerminal.vue    # 多智能体生命周期日志终端（自动滚动）
│   │   │       ├── ResourceDisplay.vue  # 5 标签页资源预览（文档/脑图/测验/视频脚本/代码）
│   │   │       └── AgentDetailView.vue  # 专家深度研讨室（全屏 Overlay 左右分栏对话）
│   │   ├── LearningPath/                # 模块三：个性化学习路径规划
│   │   │   ├── index.vue                # 规划引擎主控（阶段 Roadmap + 画像分析浮窗 + 加载动画）
│   │   │   ├── types.ts                 # 类型定义（KnowledgeNode, KnowledgeEdge, LearningResource）
│   │   │   └── components/
│   │   │       └── KnowledgeGraph.vue   # SVG 交互式 DAG 图谱（节点 + 连线 + 动态注入 + 动画）
│   │   └── Delivery/                    # 新增：资源推送视图
│   │       ├── index.vue                # 双栏布局（左侧资源流 + 右侧智能体/热点面板）
│   │       └── components/
│   │           ├── DeliveryHeader.vue   # 日期 + 课程标题 + 进度条（45%）
│   │           ├── ResourceTimeline.vue # 垂直资源时间线（含 Planner Insight AI 推理标签）
│   │           ├── AgentInsightPanel.vue # Planner Agent 状态卡片（ONLINE + 专注度/掌握度指标）
│   │           └── TrendingPanel.vue    # 行业热点面板（GitHub/StackOverflow/Arxiv + AI Insight）
│   └── lib/
│       └── utils.ts                     # cn() 工具函数（clsx + twMerge）、valueUpdater
├── components.json                      # shadcn-vue 配置（new-york 风格，zinc 基准色）
├── tailwind.config.js                   # Tailwind 配置（shadcn-vue 主题 + 侧边栏 Token）
├── vite.config.ts                       # Vite 配置（@ 别名指向 ./src）
└── tsconfig*.json                       # TypeScript 配置（app + node 引用）
```

### 路由表

| 路径 | 名称 | 布局 | 组件 | 状态 |
|------|------|--------|-----------|--------|
| `/login` | `login` | 无（独立页面） | LoginView | ✅ 完成 |
| `/register` | `register` | 无（独立页面） | RegisterView | ✅ 完成 |
| `/onboarding` | `onboarding` | 无（独立页面） | OnboardingView | ✅ 完成（懒加载） |
| `/` | `home` | DashboardLayout | HomeView | ✅ 完成 |
| `/factory` | `content-factory` | DashboardLayout | ContentFactory/index.vue | ✅ 完成（懒加载） |
| `/path` | `learning-path` | DashboardLayout | LearningPath/index.vue | ✅ 完成（懒加载） |
| `/delivery` | `resource-delivery` | DashboardLayout | Delivery/index.vue | ✅ 完成（懒加载） |

### 导航结构

侧边栏（`AppSidebar.vue`）包含 6 个导航项：

| 菜单项 | 图标 | 路由 | 状态 |
|--------|------|------|------|
| 控制台首页 | LayoutDashboard | `/` | ✅ 已路由 |
| 资源生成 | Factory | `/factory` | ✅ 已路由 |
| 学习路径规划 | Route | `/path` | ✅ 已路由 |
| 资源推送 | Send | `/delivery` | ✅ 已路由 |
| 智能指导 | MessageSquareQuote | `/tutor` | ⚠️ 路由未注册 |
| 学习效果评估 | BarChart3 | `/assessment` | ⚠️ 路由未注册 |

### UI 设计系统

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

## 前端五大模块实现详情

### 模块一：对话式学习画像自主构建（OnboardingView.vue）

**已完成**: 完整的对话式破冰引导流程，替代了原有的 4 步表单向导。

- **交互流程**: 破冰智能体（Ice-breaker Agent）通过 4 轮自然语言对话收集学生画像
  - 第 1 轮：知识基础（Python、高数、线代等 8 个可多选选项）
  - 第 2 轮：认知风格（视觉/代码实践/理论推导/案例教学）
  - 第 3 轮：学习目标（期末/考研/求职/兴趣/竞赛）
  - 第 4 轮：时间分布（碎片化/沉浸式/周末突击/每日定时）
- **技术要点**:
  - 消息气泡 UI（agent/user 双色区分，agent=深色卡片，user=蓝色卡片）
  - 多选标签系统（点击切换选择态 + 底部已选标签展示 + X 移除）
  - 自动滚动到最新消息 + 打字动画（3 点弹跳 BOT 思考态）
  - 4 步线性进度条（渐变色 + 百分比）
  - 对话完成后进入画像预览阶段（4 列卡片 + 标签增删 + 自由备注补充）
  - 分析过渡动画（全屏旋转加载 + 模糊背景遮罩）
- **当前 Mock**: 全部对话和选项为前端硬编码，画像数据存储在局部 `ref<ProfileData>` 中
- **待对接**: 画像数据需发送至 `POST /api/v1/profile/onboarding`，支持从后端加载历史画像

### 模块二：多智能体协同资源生成（ContentFactory/）★ 核心亮点

**已完成**: 完整的 7 智能体流水线工作台。

- **7 个智能体**:
  | 智能体 | 角色 | 图标 | 颜色 | 产出物 |
  |-------|------|------|------|--------|
  | Manager | 主控中枢 | BrainCircuit | purple | 任务调度 |
  | Professor | 教授 | FileText | blue | 课程文档 |
  | Architect | 架构师 | GitFork | orange | Mermaid 思维导图 |
  | Examiner | 考官 | ClipboardCheck | pink | JSON 测验题 |
  | Director | 导演 | Video | cyan | 视频分镜脚本 |
  | Hacker | 极客 | Code2 | green | Python 代码实验 |
  | Reviewer | 质量审查 | ShieldCheck | red | 幻觉检查报告 |
- **流水线逻辑** (`runWorkflow` in index.vue):
  1. Manager 接收主题 → 语义拆解（1.2s）
  2. 5 个专家并行生成（Professor/Architect/Examiner/Director/Hacker，1.5s~5.5s 错峰）
  3. Reviewer 审核全部产出（1.5s）→ 通过
- **子组件详情**:
  - `TopicInput.vue`: 渐变边框（blue→purple）输入框 + 3 个快捷建议标签（梯度下降/Transformer/React Fiber）
  - `AgentStatusCard.vue`: 4 种状态（idle=半透明/running=蓝色脉冲+shimmer/success=绿色边框+READY标签/error=红色），点击 success 态卡片可打开 AgentDetailView
  - `AgentTerminal.vue`: 终端风格日志面板（红黄绿三色圆点 + `[Agent] message` 格式），自动滚动到底部
  - `ResourceDisplay.vue`: 5 标签页（文档/脑图/测验/视频脚本/代码实验），未开始时显示空状态引导，生成中显示旋转加载
  - `AgentDetailView.vue`: 全屏 z-50 Overlay 带 Transition 动画，左栏展示专家产出内容（根据角色不同渲染），右栏对话式聊天（含打字动画 bounce dots），对话输入框支持 enter 发送
- **当前 Mock**: `runWorkflow` 使用 `setTimeout` 串行模拟。`ResourceDisplay` 内嵌 Mock 题目（2 道单选题）和代码（numpy 梯度计算）
- **待对接**: 需 WebSocket 实时推送各智能体状态，替换 `setTimeout` 为真实异步任务轮询。AgentDetailView 对话需对接 `POST /api/v1/factory/agent/:agentId/chat`

### 模块三：个性化学习路径规划（LearningPath/）

**已完成**: 基于 DAG 的交互式路径规划器，替代了旧版 ResourceStream + PathPlanner 组件。

- **UI 结构**:
  - 顶部 Header：搜索输入框（预填 "Transformer Architecture"）+ "重新规划"按钮（含 loading spinner）
  - 左侧主区域：SVG 知识图谱（`KnowledgeGraph.vue`）+ AI 画像分析浮窗（可关闭，含 X 按钮）
  - 右侧 Roadmap 侧边栏（380px）：标题 + 总进度条（32%）+ 4 个阶段卡片列表
- **交互逻辑**:
  - 输入学习目标 → Planner Agent 分析（2s loading 全屏遮罩 + 旋转动画）
  - 分析浮窗标注薄弱维度（如"线性代数掌握度仅 0.42"）并说明 AI 注入节点
  - 点击阶段卡片切换左侧图谱节点（active 状态蓝色高亮 + 左侧激活条）
  - locked 阶段灰色不可点击（opacity-40 grayscale pointer-events-none）
  - AI 注入节点（STEP 2）琥珀色标签 "AI INJECTED" + 弹跳动画
- **类型定义** (`types.ts`):
  - `KnowledgeNode`: id, label, x, y, type (standard|injected), proficiency (0-1), status, resources
  - `KnowledgeEdge`: from, to, isDynamic?
  - `LearningResource`: id, agentName, type (video|document|code|quiz), title, description, status
- **当前 Mock**: 4 个阶段（线性代数准备→矩阵运算强化→Transformer 核心架构→模型训练微调），各阶段知识点为硬编码
- **待对接**: 知识图谱数据从 `GET /api/v1/graph/:courseId` 加载，动态路径从 `GET /api/v1/graph/path/:studentId` 获取

### 模块四：智能辅导（待开发）

- **侧边栏已预留** `MessageSquareQuote` → `/tutor` 路由
- **路由尚未注册**，页面组件尚未创建
- **预期功能**: 多模态问答（支持图片/代码/公式上传）、流式 AI 回复（SSE/WebSocket）、Mermaid 图表渲染、代码块语法高亮

### 模块五：学习效果评估（待开发）

- **侧边栏已预留** `BarChart3` → `/assessment` 路由
- **路由尚未注册**，页面组件尚未创建
- **HomeView 中已有占位内容**:
  - 6 维画像卡片（知识基础 85、认知风格"视觉型"、易错偏好"逻辑边界"、学习目标"项目实战"、专注时长"45min"、抗压值 72）
  - Assessor Agent 诊断摘要（"线性代数掌握度提升 15%，梯度爆炸问题停留超 45 分钟"）
  - 装饰性雷达图占位（BrainCircuit 图标 + 蓝色圆形）

### 新增：资源推送（Delivery/）

**已完成**: 个性化学习资源推送视图。

- **UI 结构**: 12 列网格布局（max-w-6xl）
  - 左侧（8 列）：DeliveryHeader + "个人专属学习流 Live Feed" 标题 + ResourceTimeline
  - 右侧（4 列）：AgentInsightPanel（sticky）+ TrendingPanel
- **子组件**:
  - `DeliveryHeader.vue`: 日期（Calendar 图标 + "2024年3月28日"）+ 课程标题 + 今日进度（Progress 组件 45% + emerald 色百分比）
  - `ResourceTimeline.vue`: 左侧渐变时间线（蓝→灰→透明），3 个资源卡片（video 已完成/document 当前/code 锁定），含 Planner Insight 蓝色提示框（AI 推理原因）+ 开始/回顾按钮
  - `AgentInsightPanel.vue`: sticky top-8，Planner Agent ONLINE（绿色），Planner 推理引言，专注度/掌握度双指标卡片
  - `TrendingPanel.vue`: GitHub（Meta-Llama-3.1）/StackOverflow（WebAssembly）/Arxiv（KAN）热点列表 + "AI Insight" 底部推荐
- **当前 Mock**: 3 个资源 + 3 个热点为硬编码
- **待对接**: 资源列表从 `GET /api/v1/resources/today` 获取，进度从 `PUT /api/v1/resources/:id/progress` 同步，热点从 `GET /api/v1/resources/trending` 获取

### 仪表盘首页（HomeView.vue）

**已完成**: Bento 布局仪表盘，聚合展示各模块核心状态。

- **布局**: 12 列网格 Bento 风格
  - 顶部：Ice-breaker 反馈问候 + 抗压值/专注度快速指标卡片
  - 左侧大卡片（8 列）：动态规划路径 DAG 展示区（4 节点 + 虚线连接 + 蓝色脉动当前节点 + 灰色锁定未来节点）
  - 右侧卡片（4 列）：内容制造车间 5 智能体状态列表 + "进入沉浸式学习模式" 按钮
  - 左下卡片（4 列）：6 维自主画像网格 + "随学随新" 提示
  - 右下卡片（8 列）：Assessor Agent 诊断摘要 + 操作按钮 + 装饰性雷达图占位
- **当前 Mock**: 5 个智能体（2 Completed/2 Generating/1 Pending），6 维画像数据硬编码
- **待对接**: 仪表盘数据应从多个 API 聚合（profile + factory status + assessment summary）

---

## 后端实现方案

### API 设计原则

- **RESTful API**，带版本号的端点（`/api/v1/`）
- **WebSocket** — 智能体状态实时更新和内容生成流式推送
- **SSE（Server-Sent Events）** — AI 回复流式传输（聊天、内容生成）
- 所有请求/响应体使用 JSON 格式
- 认证使用 JWT Bearer Token（`Authorization: Bearer <token>`）

### 核心 API 端点

#### 认证

| 方法 | 端点 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| `POST` | `/api/v1/auth/register` | 用户注册 | `{email, password, username}` | `{access_token, refresh_token, user}` |
| `POST` | `/api/v1/auth/login` | 用户登录 | `{email, password}` | `{access_token, refresh_token, user}` |
| `POST` | `/api/v1/auth/refresh` | 刷新 Token | `{refresh_token}` | `{access_token}` |

#### 画像（模块一）

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/v1/profile` | 获取当前学生画像（6 维度 JSON） |
| `PUT` | `/api/v1/profile` | 更新画像数据 |
| `POST` | `/api/v1/profile/onboarding` | 提交破冰对话结果，触发画像生成 |
| `GET` | `/api/v1/profile/history` | 获取画像变更历史 |

#### 内容工厂（模块二）

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/api/v1/factory/generate` | 提交主题，触发多智能体生成任务 |
| `GET` | `/api/v1/factory/status/:taskId` | 查询生成任务状态（含各智能体进度） |
| `GET` | `/api/v1/factory/resources/:taskId` | 获取生成完成的资源包 |
| `WS` | `/api/v1/factory/stream/:taskId` | WebSocket 实时推送智能体执行日志 |
| `POST` | `/api/v1/factory/agent/:agentId/chat` | 与指定专家智能体对话 |

#### 知识图谱与学习路径（模块三）

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/v1/graph/:courseId` | 获取课程完整 DAG（节点 + 边） |
| `GET` | `/api/v1/graph/path/:studentId` | 获取该学生的个性化学习路径 |
| `POST` | `/api/v1/graph/plan` | 根据目标主题触发路径规划 |
| `GET` | `/api/v1/graph/node/:nodeId/resources` | 获取某知识节点关联的学习资源 |

#### 资源推送（Delivery）

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/v1/resources/today` | 获取今日推送资源列表 |
| `GET` | `/api/v1/resources/:resourceId` | 获取单个资源详情 |
| `PUT` | `/api/v1/resources/:resourceId/progress` | 更新资源学习进度 |
| `GET` | `/api/v1/resources/trending` | 获取行业热点 |

#### 智能辅导（模块四）

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/api/v1/tutor/ask` | 提交问题（支持文本 + 图片/文件 base64） |
| `WS` | `/api/v1/tutor/chat` | WebSocket 流式对话 |
| `GET` | `/api/v1/tutor/history` | 获取历史对话记录 |

#### 评估（模块五）

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/v1/assessment/weekly` | 获取本周学情诊断报告 |
| `GET` | `/api/v1/assessment/stats` | 获取学习统计数据（雷达图数据） |
| `GET` | `/api/v1/assessment/history` | 获取历史评估报告列表 |

#### WebSocket 事件协议

**内容工厂流水线推送** (`/api/v1/factory/stream/:taskId`):
```json
// 服务端 → 客户端
{ "type": "agent_status", "agent": "Professor", "status": "running", "timestamp": "..." }
{ "type": "agent_log", "agent": "Professor", "message": "正在检索相关教材...", "level": "info" }
{ "type": "agent_status", "agent": "Professor", "status": "success", "timestamp": "..." }
{ "type": "task_complete", "taskId": "...", "resources": [...] }
{ "type": "error", "agent": "Professor", "message": "RAG 检索超时" }
```

**辅导对话流式推送** (`/api/v1/tutor/chat`):
```json
// 客户端 → 服务端
{ "type": "question", "content": "什么是梯度下降？", "attachments": [] }
// 服务端 → 客户端
{ "type": "token", "content": "梯度" }
{ "type": "token", "content": "下降" }
{ "type": "done" }
```

### 后端技术栈建议

- **运行时**: Python 3.12+ / FastAPI — AI/ML 生态集成能力强，原生 async/await
- **数据库**: PostgreSQL 16（关系型数据）+ pgvector（向量检索用于 RAG）
- **缓存/队列**: Redis（缓存 + Celery Broker）
- **AI/LLM**: OpenAI 兼容 API 网关 + LangChain/LlamaIndex（RAG 管线）
- **实时通信**: FastAPI 内置 WebSocket + SSE 支持
- **文件存储**: MinIO / S3（多模态上传文件）
- **部署**: Docker Compose + Nginx 反向代理

### 核心数据模型（SQL 表结构）

- **students**: id (UUID PK), email (UNIQUE), password_hash, username, onboarding_completed, created_at, updated_at
- **student_profiles**: id, student_id (FK), profile_data (JSONB: 6 维度), version, created_at
- **knowledge_graphs**: id, course_id, title, nodes (JSONB), edges (JSONB), version, created_at
- **generation_tasks**: id, student_id (FK), topic, status (pending/running/completed/failed), agents_status (JSONB), created_at
- **generated_resources**: id, student_id (FK), task_id (FK), topic, agent_type, resource_type, content (JSONB), status (pending/generating/reviewing/approved/rejected), reviewed_by, created_at
- **learning_progress**: id, student_id (FK), resource_id (FK), interaction_type, duration_seconds, score, error_count, timestamp
- **assessment_reports**: id, student_id (FK), week_start, week_end, metrics (JSONB), difficulty_adjustment (up/maintain/down), created_at
- **tutor_conversations**: id, student_id (FK), messages (JSONB), created_at

### 后端项目结构建议

```
backend/
├── app/
│   ├── main.py                    # FastAPI 应用入口 + CORS 配置
│   ├── config.py                  # 配置管理（环境变量、数据库 URL）
│   ├── models/                    # SQLAlchemy ORM 模型
│   │   ├── student.py
│   │   ├── profile.py
│   │   ├── knowledge_graph.py
│   │   ├── resource.py
│   │   └── assessment.py
│   ├── schemas/                   # Pydantic 请求/响应模式
│   │   ├── auth.py
│   │   ├── profile.py
│   │   ├── factory.py
│   │   ├── graph.py
│   │   └── assessment.py
│   ├── api/v1/                    # 路由处理器
│   │   ├── auth.py
│   │   ├── profile.py
│   │   ├── factory.py
│   │   ├── graph.py
│   │   ├── resources.py
│   │   ├── tutor.py
│   │   └── assessment.py
│   ├── api/deps.py                # 依赖注入（get_db, get_current_user）
│   ├── services/                  # 业务逻辑层
│   │   ├── agent_orchestrator.py  # 多智能体调度引擎（Manager 协调逻辑）
│   │   ├── profile_analyzer.py    # 画像分析（Prompt 工程提取 6 维度）
│   │   ├── content_generator.py   # 内容生成（调用 LLM）
│   │   ├── reviewer.py            # 幻觉检查 + 质量审核
│   │   ├── path_planner.py        # 学习路径规划（DAG 拓扑排序 + 动态注入）
│   │   └── assessor.py            # 学情评估（雷达图数据计算）
│   ├── core/                      # 核心基础设施
│   │   ├── security.py            # JWT 生成/验证 + bcrypt 密码哈希
│   │   ├── database.py            # SQLAlchemy async engine + session
│   │   ├── redis.py               # Redis 客户端封装
│   │   └── websocket.py           # WebSocket 连接管理器（房间/广播）
│   └── tasks/                     # Celery 异步任务
│       ├── generation.py          # 内容生成异步任务
│       └── assessment.py          # 周报自动生成任务
├── alembic/                       # 数据库迁移脚本
├── tests/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 前后端对接策略（下一步行动）

### 1. 定义共享 TypeScript 接口（`src/types/`）

在 `src/types/` 中创建与后端 Pydantic Schema 精确对应的 TS 类型。这是前后端契约的基础。

需要创建的类型文件：
- `src/types/auth.ts` — User, LoginRequest, RegisterRequest, AuthResponse
- `src/types/profile.ts` — ProfileData, ProfileDimension, OnboardingSubmission
- `src/types/factory.ts` — GenerationTask, AgentStatus, GeneratedResource, LogEntry, ResourceType
- `src/types/graph.ts` — 迁移 LearningPath/types.ts 至此
- `src/types/resources.ts` — DeliveryResource, TrendingItem, ResourceProgress
- `src/types/assessment.ts` — AssessmentReport, RadarData, WeeklyStats
- `src/types/api.ts` — 通用响应包装 `ApiResponse<T>`, 分页 `PaginatedResponse<T>`

### 2. 搭建 API 客户端层（`src/api/`）

```
src/api/
├── client.ts           # 基础 HTTP 客户端（封装 fetch/axios，自动附加 JWT Token）
├── auth.ts             # login(), register(), refreshToken()
├── profile.ts          # getProfile(), updateProfile(), submitOnboarding()
├── factory.ts          # generate(), getTaskStatus(), getResources(), chatWithAgent()
├── graph.ts            # getGraph(), getPersonalizedPath(), planPath()
├── resources.ts        # getTodayResources(), getResource(), updateProgress(), getTrending()
├── tutor.ts            # askQuestion(), getHistory()
├── assessment.ts       # getWeeklyReport(), getStats(), getHistory()
└── websocket.ts        # WebSocket 管理器（自动重连 + 心跳 + 消息分发）
```

### 3. 引入状态管理 Pinia（`src/stores/`）

在引入真实 API 之前或同步进行，将组件内局部状态迁移到 Pinia Store：

```
src/stores/
├── authStore.ts        # 认证 Token、用户信息、登录状态、onboarding 完成标志
├── profileStore.ts     # 6 维度画像数据、引导对话状态
├── factoryStore.ts     # 当前生成任务、智能体状态列表、生成资源、终端日志
├── learningStore.ts    # 知识图谱节点/边、学习路径阶段、当前选中阶段
├── deliveryStore.ts    # 今日推送资源、学习进度、热点数据
└── assessmentStore.ts  # 评估报告、雷达图数据、历史记录
```

### 4. 逐步替换 Mock 为真实 API（按模块优先级）

| 优先级 | 模块 | 替换方式 |
|--------|------|----------|
| 1 | 认证 | `setTimeout` → `POST /api/v1/auth/login` |
| 2 | 画像 | OnboardingView 提交 → `POST /api/v1/profile/onboarding`，HomeView 从 `GET /api/v1/profile` 加载 |
| 3 | 内容工厂 | `setTimeout` 流水线 → `POST /api/v1/factory/generate` + `WS /api/v1/factory/stream/:taskId` |
| 4 | 学习路径 | 硬编码 phases → `POST /api/v1/graph/plan` + `GET /api/v1/graph/path/:studentId` |
| 5 | 资源推送 | 硬编码资源 → `GET /api/v1/resources/today` + `GET /api/v1/resources/trending` |
| 6 | 辅导 & 评估 | 同步开发前端页面 + 后端 API（目前路由未注册、页面未创建） |

### 5. 环境变量配置

```
.env.development:
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/api/v1

.env.production:
VITE_API_BASE_URL=https://api.edunexus.com/api/v1
VITE_WS_URL=wss://api.edunexus.com/api/v1
```

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
- 错误响应格式：`{ error: { code: string, message: string, details?: any } }`
