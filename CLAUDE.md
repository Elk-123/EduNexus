# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中工作时提供指导。

## 常用命令

- **开发服务器**: `cd EduNexus && npm run dev`
- **构建**: `cd EduNexus && npm run build`（执行 vue-tsc + vite build）
- **预览**: `cd EduNexus && npm run preview`
- **类型检查**: `cd EduNexus && npx vue-tsc --noEmit`

## 项目架构

**EduNexus** 是一个 Vue 3 + TypeScript + Vite 的教育管理平台，采用暗色主题、Google AI Studio 风格的 UI。项目实现了**多智能体 AI 教育系统**——多个专业 AI 智能体协同工作，生成学习资源、规划个性化课程并评估学生学习进展。

项目目前为**纯前端**阶段，使用 Mock 数据（尚未接入后端）。开发遵循**前端先行**策略：先构建并验证完整的 UI、交互和数据流，再实现后端 API。

### 技术栈
- **框架**: Vue 3（Composition API，`<script setup lang="ts">`）
- **构建**: Vite 8 + vue-tsc 3 + TypeScript 6
- **路由**: vue-router 4（createWebHistory 模式）
- **样式**: Tailwind CSS 3 + autoprefixer + postcss，纯暗色主题，CSS 变量
- **UI 组件**: shadcn-vue（基于 reka-ui、class-variance-authority、clsx、tailwind-merge）
- **图标**: lucide-vue-next
- **工具库**: @vueuse/core
- **状态管理**: 暂无（仅使用局部 `ref`/`reactive`）。待全局状态需求明确后引入 Pinia
- **HTTP 客户端**: 尚未配置（axios/fetch）。所有数据通过 `setTimeout` 模拟
- **推荐 IDE 扩展**: Vue.volar（不要使用 Vetur）

### 目录结构

```
EduNexus/
├── src/
│   ├── main.ts                          # 应用入口 — 创建 Vue 实例，安装路由，挂载
│   ├── App.vue                          # 根组件（仅含 <router-view />）
│   ├── style.css                        # Tailwind 指令 + 全局暗色样式
│   ├── env.d.ts                         # .vue 模块类型声明
│   ├── router/index.ts                  # 路由定义
│   ├── layouts/
│   │   └── DashboardLayout.vue          # 主认证布局（侧边栏 + 顶栏 + 内容区）
│   ├── views/
│   │   ├── LoginView.vue                # 登录页（未认证）
│   │   ├── RegisterView.vue             # 注册页（未认证）
│   │   ├── OnboardingView.vue           # 多步骤引导向导，含智能体对话
│   │   ├── HomeView.vue                 # 仪表盘首页 — DAG 图谱、智能体状态、画像、诊断
│   │   ├── MainView.vue                 # （未使用）旧版原型页面
│   │   ├── ContentFactory/
│   │   │   ├── index.vue                # 多智能体内容生成工作台
│   │   │   └── components/
│   │   │       ├── AgentTerminal.vue    # （占位）智能体执行日志/终端
│   │   │       ├── TopicInput.vue       # （占位）主题关键词输入
│   │   │       ├── ResourceDisplay.vue  # （占位）生成资源预览
│   │   │       └── AgentStatusCard.vue  # （占位）单个智能体状态卡片
│   │   └── LearningPath/
│   │       ├── index.vue                # 学习路径规划器（DAG + 资源时间线）
│   │       └── components/
│   │           ├── KnowledgeGraph.vue   # SVG 交互式 DAG 图谱（含动画）
│   │           ├── ResourceStream.vue   # 学习资源垂直时间线
│   │           └── PathPlanner.vue      # （占位）路径规划控制面板
│   ├── components/
│   │   ├── AppSidebar.vue               # 侧边栏导航（含个人信息弹窗）
│   │   ├── HelloWorld.vue               # 遗留的 Vite 脚手架文件（未使用，可删除）
│   │   └── ui/                          # shadcn-vue 组件库（20+ 组件系列）
│   └── lib/
│       └── utils.ts                     # cn() 工具函数（clsx + twMerge）、valueUpdater
├── components.json                      # shadcn-vue 配置
├── tailwind.config.js                   # Tailwind 配置（shadcn-vue 主题 + 侧边栏 Token）
├── vite.config.ts                       # Vite 配置（@ 别名指向 ./src）
└── tsconfig*.json                       # TypeScript 配置（app + node 引用）
```

### 路由表

| 路径 | 名称 | 布局 | 组件 | 状态 |
|------|------|--------|-----------|--------|
| `/login` | `login` | 无（独立页面） | LoginView | 已完成 |
| `/register` | `register` | 无（独立页面） | RegisterView | 已完成 |
| `/onboarding` | `onboarding` | 无（独立页面） | OnboardingView | 已完成（懒加载） |
| `/` | `home` | DashboardLayout | HomeView | 已完成 |
| `/factory` | `content-factory` | DashboardLayout | ContentFactory/index.vue | 开发中（懒加载） |
| `/path` | `learning-path` | DashboardLayout | LearningPath/index.vue | 开发中（懒加载） |

### 导航结构

侧边栏（`AppSidebar.vue`）包含 4 个主导航项：
- **Playground** → `/`（HomeView 仪表盘，默认选中项）
- **Course Management** → 尚未绑定路由
- **Student List** → 尚未绑定路由
- **Data Analytics** → 尚未绑定路由

完整导航层级（所有已在路由中注册，但侧边栏尚未全部体现）：

```
/login                    → LoginView
/register                 → RegisterView
/onboarding               → OnboardingView
/                         → DashboardLayout → HomeView
/factory                  → DashboardLayout → ContentFactory/index.vue
/path                     → DashboardLayout → LearningPath/index.vue
```

### UI 设计系统

所有页面遵循统一的暗色主题规范：
- **背景色**: `#0b0b0b`，叠加微弱的点状网格纹理
- **卡片样式**: rounded-2xl / rounded-3xl，zinc/gray/blue 色系，毛玻璃 backdrop-blur 效果
- **顶栏**: 固定定位 + 毛玻璃模糊，包含 SidebarTrigger + 搜索输入框
- **滚动条**: 6px 深色自定义样式
- **字体**: Inter 字体族，通过 Google Fonts 加载
- **组件库**: shadcn-vue "new-york" 风格，Zinc 基准色

### shadcn-vue 组件模式
- 每个组件在 `src/components/ui/` 下拥有独立目录
- 使用 `<script setup lang="ts">`，结合 reka-ui 的 `Primitive` 实现多态渲染
- 变体样式通过 `class-variance-authority`（cva）定义
- `index.ts` 桶文件统一导出组件和变体类型
- 使用 `@/lib/utils` 中的 `cn()` 合并类名

### 路径别名
- `@/` 映射到 `./src/`（在 vite.config.ts 和 tsconfig 中均有配置）

---

## 核心系统模块

平台围绕五大核心模块构建，共同组成完整的 AI 驱动自适应学习系统。

### 模块一：对话式学习画像自主构建（动态画像）

**目标**: 以自然语言对话取代传统表单，构建丰富的 6 维度学生画像。

**交互流程**: 学生首次登录时，**"破冰智能体（Ice-breaker Agent）"** 模拟资深导师，与学生进行 3-5 轮自然语言对话，通过开放式问题了解学生的背景、偏好和目标。

**6 维画像特征**（通过 Prompt 工程提取）：
1. **知识基础** — 如：Python 熟练度、线性代数基础
2. **认知风格** — 视觉驱动型 vs. 代码实践型 vs. 理论推导型
3. **易错点偏好** — 如：逻辑边界条件易错、数学公式推导困难
4. **学习目标** — 期末保过 vs. 考研深造 vs. 项目实战
5. **专注度与时间碎片化** — 单次学习时长 20 分钟 vs. 2 小时
6. **当前情绪抗压值** — 根据对话语气判定，决定是否推送高难度挑战题

**存储与更新**:
- 画像以 JSON 格式存储
- 每次测验、答疑或内容交互后，后台触发增量更新（"随学随新"）

**前端现状**: `OnboardingView.vue` 已实现 4 步向导式流程。需要改造为对话式聊天 UI 以匹配破冰智能体的交互方式。

### 模块二：多智能体协同资源生成（内容制造车间）★ 核心亮点

**目标**: 构建一个"内容制造车间（Content Factory）"，由一名主控智能体（Manager）协调多名专家智能体（Experts），基于统一主题（如"梯度下降算法"）协作生成 5 种以上学习资源。

**智能体阵容**:

| 智能体 | 角色 | 产出物 | 关键约束 |
|-------|------|--------|-----------------|
| **教授智能体**（Professor） | 内容作者 | 专业课程讲解文档 | 必须调用 RAG 提取标准教材内容，确保零幻觉 |
| **架构师智能体**（Architect） | 知识结构化 | 知识点思维导图 | 输出 **Mermaid 格式**代码，前端自动渲染为交互式图表 |
| **考官智能体**（Examiner） | 出题专家 | 选择题、填空题等多种题型 | 生成 **JSON 格式**题目；难度依据学生画像校准 |
| **导演智能体**（Director） | 多媒体创作 | 视频/动画脚本及分镜内容 | 对接多模态大模型，将抽象概念转为动画演示或分镜图解 |
| **极客智能体**（Hacker） | 实操达人 | 代码实验 & Jupyter Notebook 模板 | 结合业务场景生成可运行的 Python 代码，附带详细注释 |
| **审查智能体**（Reviewer） | 质量守门人 | 审核报告 | 对所有生成内容进行幻觉检查；不合格则打回重做 |

**流水线流程**:
1. 学生输入主题关键词（如："梯度下降算法"）
2. Manager 协调各专家并行/并发生成内容
3. 所有产出经过 Reviewer 幻觉检查
4. 合格资源组装为多标签页资源包，推送给学生

**前端现状**: `ContentFactory/index.vue` 已搭建工作台框架（主题输入区、智能体状态侧边栏、多标签页预览区）。四个子组件（`AgentTerminal`、`TopicInput`、`ResourceDisplay`、`AgentStatusCard`）均为空占位文件。

### 模块三：个性化学习路径规划与资源推送

**目标**: 构建基于 DAG 的知识图谱引擎，动态为学生规划个性化学习路径。

**核心组件**:

- **知识图谱引擎**: 后端将课程（如《人工智能导论》）建模为**有向无环图（DAG）**，节点间以前置关系相连。
- **规划智能体动态路由**: 若学生画像显示"线性代数"基础薄弱，规划智能体会在"深度学习"章节前，自动插入"矩阵运算基础"的补充学习节点。
- **多模态卡片推送**: 资源按规划顺序以卡片式 UI 流式推送——**先看视频概念 → 再读文档精读 → 然后实操代码 → 最后随堂测试**。

**前端现状**: `LearningPath/index.vue` 包含 SVG 交互式 DAG 图谱（`KnowledgeGraph.vue`，含动画节点和动态注入路径），以及垂直资源时间线组件（`ResourceStream.vue`）。`PathPlanner.vue` 为空占位文件。

### 模块四：智能辅导 ★ 加分项

**目标**: 导师智能体（Tutor Agent）提供多模态问答，支持多样化输入和丰富输出。

- **输入**: 支持学生上传报错截图、公式照片、甚至语音提问
- **处理**: 调用视觉大模型（OCR + 图文理解）分析问题
- **输出**: 文字解答 + 动态生成解题流程图（Mermaid）+ 相关短视频讲解链接

**前端现状**: 尚未实现。

### 模块五：学习效果评估与自适应难度 ★ 加分项

**目标**: 数据驱动的每周诊断报告与自动难度调节（自适应学习系统 ALS）。

- **无感数据采集**: 后台记录学生视频停留时长、测验得分率、代码运行报错次数，无需学生主动操作。
- **评估智能体深度评估**: 每周生成一份《学情诊断报告》，以雷达图展示各项能力维度，附带关键洞察和行动建议。
- **自适应难度**: 基于评估结果，自动上调/下调下周课程难度。

**前端现状**: `HomeView.vue` 中已有评估诊断区域，包含模拟雷达图数据。尚无双真实数据采集管道。

---

## 实现方案：前端先行开发

项目采用**前端先行**策略：用 Mock 数据构建并验证完整 UI 后，再进行后端开发。这确保用户体验、数据流和组件架构在设计阶段不依赖 API 约束即可充分验证。

### 前端实现路线图

#### 第一阶段：基础搭建（已完成）
- [x] 项目脚手架（Vite + Vue 3 + TypeScript + Tailwind）
- [x] shadcn-vue 组件库集成
- [x] 暗色主题设计系统 + CSS 变量
- [x] 路由配置（含懒加载）
- [x] DashboardLayout（侧边栏 + 顶栏）
- [x] AppSidebar（导航 + 个人信息弹窗）
- [x] LoginView + RegisterView（表单 UI）

#### 第二阶段：核心页面（进行中）
- [ ] **OnboardingView** — 从 4 步表单改造为对话式聊天 UI（对接破冰智能体）
- [ ] **HomeView** — 增强 DAG 可视化、多智能体状态实时轮询模拟、6 维雷达图
- [ ] **ContentFactory** — 实现全部 4 个占位子组件（AgentTerminal、TopicInput、ResourceDisplay、AgentStatusCard）
- [ ] **LearningPath** — 实现 PathPlanner 控制面板和 DAG 交互逻辑

#### 第三阶段：状态管理与数据层
- [ ] 搭建 Pinia Store：
  - `useProfileStore` — 学生画像（6 维度）、引导状态
  - `useContentStore` — 生成资源、智能体流水线状态
  - `useLearningStore` — 知识图谱节点、学习进度、资源队列
  - `useAuthStore` — 认证 Token、用户信息、登录状态
- [ ] 在 `src/types/` 中定义所有数据模型的 TypeScript 接口
- [ ] 创建与接口类型匹配的 Mock 数据工厂

#### 第四阶段：高级功能
- [ ] **模块四（智能辅导）** — 聊天界面（含文件/图片上传）、代码块渲染、Mermaid 图表渲染
- [ ] **模块五（学习评估）** — 雷达图组件、每周报告页面、数据仪表盘

### 后端实现方案（后续）

#### API 设计
- **RESTful API**，带版本号的端点（`/api/v1/`）
- **WebSocket** — 智能体状态实时更新和内容生成流式推送
- **SSE（Server-Sent Events）** — AI 回复流式传输（聊天、内容生成）

#### 核心 API 端点

| 领域 | 端点 | 说明 |
|--------|-----------|-------------|
| **认证** | `POST /auth/login`、`POST /auth/register`、`POST /auth/refresh` | JWT 认证 |
| **画像** | `GET /profile`、`PUT /profile`、`POST /profile/onboarding` | 学生画像增删改查 + 引导对话 |
| **内容工厂** | `POST /factory/generate`、`GET /factory/status/:taskId`、`WS /factory/stream/:taskId` | 触发内容生成、查询状态、流式推送智能体日志 |
| **知识图谱** | `GET /graph/:courseId`、`GET /graph/path/:studentId` | 获取课程 DAG、获取个性化学习路径 |
| **学习资源** | `GET /resources/:type`、`GET /resources/recommend` | 按类型获取生成资源 |
| **辅导** | `POST /tutor/ask`、`WS /tutor/chat` | 多模态问答（流式响应） |
| **评估** | `GET /assessment/weekly/:studentId`、`GET /assessment/stats` | 每周报告、学习分析数据 |

#### 后端技术栈（建议）
- **运行时**: Python（FastAPI）—— AI/ML 生态集成能力强
- **数据库**: PostgreSQL（关系型数据）+ Redis（缓存、任务队列）
- **AI/LLM**: OpenAI 兼容 API 网关、RAG 管线（LangChain/LlamaIndex）、多模态模型集成
- **任务队列**: Celery + Redis 处理异步内容生成
- **实时通信**: FastAPI 内置 WebSocket 支持

#### 核心数据模型

```
Student（学生）
  - id, email, password_hash, created_at
  - profile: JSON（6 维画像数据）
  - onboarding_completed: boolean

KnowledgeGraph（知识图谱）
  - id, course_id
  - nodes: JSON（DAG 节点结构）
  - edges: JSON（前置关系边）

GeneratedResource（生成资源）
  - id, student_id, topic, agent_type, resource_type
  - content: JSON
  - status: enum(pending | generating | reviewing | approved | rejected)
  - created_at, reviewed_at

LearningProgress（学习进度）
  - id, student_id, resource_id, interaction_type
  - duration_seconds, score, error_count
  - timestamp

AssessmentReport（评估报告）
  - id, student_id, week_start, week_end
  - metrics: JSON（雷达图数据、得分、洞察）
  - difficulty_adjustment: enum(up | maintain | down)
```

### 前后端集成策略

1. **先定义共享的 TypeScript 接口** — `src/types/` 中的类型与后端数据模型精确对应
2. **创建 API 客户端层** 于 `src/api/`，包含类型化的请求/响应处理器
3. **Mock 全部端点** — 使用 MSW（Mock Service Worker）或简单 Mock Handler，使前端无需后端即可完整运行
4. **替换 Mock 为真实 API** — 仅需更改 base URL，由于接口契约一致，无需修改前端代码

---

## 开发规范与约定

### 编写新代码时

- 统一使用 `<script setup lang="ts">`，禁止 Options API
- 路由级页面放在 `src/views/功能名/index.vue`，子组件放在 `src/views/功能名/components/`
- 共享组件放在 `src/components/`
- 禁止默认导出（default export）——使用具名导出 `defineProps<>()` 和 `defineEmits<>()`
- 类型定义放在 `src/types/` 独立文件中（待引入后），避免内联类型
- 组合式函数/Store 放在 `src/stores/` 或 `src/composables/`
- 所有条件类名合并使用 `@/lib/utils` 中的 `cn()`
- 遵循现有暗色主题视觉风格 — #0b0b0b 背景、rounded-2xl 卡片、zinc 色系

### 文件命名
- Vue 组件: PascalCase（如 `KnowledgeGraph.vue`）
- TypeScript 模块: camelCase（如 `utils.ts`）
- 目录: views 下用 PascalCase，components 下用 PascalCase 或 kebab-case
