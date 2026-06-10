# EduNexus 内容工厂 Agent 集群设计文档



---

## 目录

- [1. 设计总览](#1-设计总览)
- [2. A2A 协议 —— Agent 间通信架构](#2-a2a-协议--agent-间通信架构)
- [3. Agent 集群拓扑与角色设定](#3-agent-集群拓扑与角色设定)
- [4. 共享基础设施](#4-共享基础设施)
- [5. Agent 内部设计 —— 逐一拆解](#5-agent-内部设计--逐一拆解)
  - [5.1 Manager Agent — 主控中枢](#51-manager-agent--主控中枢)
  - [5.2 Professor Agent — 教授](#52-professor-agent--教授)
  - [5.3 Architect Agent — 架构师](#53-architect-agent--架构师)
  - [5.4 Examiner Agent — 考官](#54-examiner-agent--考官)
  - [5.5 Director Agent — 导演](#55-director-agent--导演)
  - [5.6 Hacker Agent — 极客](#56-hacker-agent--极客)
  - [5.7 Reviewer Agent — 审查员](#57-reviewer-agent--审查员)
- [6. 跨切面设计](#6-跨切面设计)
- [7. 演进路线图](#7-演进路线图)

---

## 1. 设计总览

### 1.1 集群定位

EduNexus 内容工厂的 Agent 集群是一个**任务驱动、流水线编排、松耦合协作**的多智能体系统。用户输入一个学习主题，7 个专业 Agent 通过 A2A 协议协同工作，在 30-60 秒内产出覆盖讲授、导图、测验、视频、代码、审核的完整教学资源包。

### 1.2 架构全景图

```
                           用户输入 (topic)
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                     A2A Message Bus                           │
│         (WebSocket + Redis Pub/Sub + PostgreSQL Outbox)       │
│                                                               │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌──────────┐  │
│   │ Manager │───→│Professor│───→│ Reviewer│    │  Shared   │  │
│   │  (🧠)   │    │  (📄)   │    │  (🔍)   │    │  Memory   │  │
│   └────┬────┘    └─────────┘    └──────────┘    │  (🗃️)    │  │
│        │                                        └──────────┘  │
│        │ 分解任务                                              │
│        ├────→ Architect (🗺️)                                 │
│        ├────→ Examiner  (📝)                                 │
│        ├────→ Director  (🎬)                                 │
│        └────→ Hacker    (💻)                                  │
│                                                               │
│   ┌─────────────────────────────────────────────────────┐    │
│   │              共享工具层 (Tool Registry)               │    │
│   │  AcademicSearch │ CodeExecutor │ WebSearch │ Canvas  │    │
│   └─────────────────────────────────────────────────────┘    │
│                                                               │
│   ┌─────────────────────────────────────────────────────┐    │
│   │              技能库 (Skill Library)                   │    │
│   │  ContentStructureSkill │ QuestionDesignSkill         │    │
│   │  MindmapLayoutSkill    │ ScriptWritingSkill          │    │
│   │  CodeReviewSkill       │ HallucinationDetectSkill    │    │
│   └─────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────┘
```

### 1.3 从现状到设计目标

| 维度 | v1.0  | v2.0 (代码骨架) | **v2.1 设计目标 (本文档)** |
|------|------------|----------------|--------------------------|
| 通信方式 | 无 A2A，编排器直接调用函数 | 协调器顺序调用 execute() | **A2A Message Bus + 事件驱动** |
| 上下文管理 | 零工程——每次调用传全量 | 无 | **分层上下文：全局 / 会话 / Agent 级** |
| MCP | 无 | 无 | **标准 MCP Client 集成，Tool Registry** |
| Tool Use | 无（纯 Prompt 生成） | 2 个 Mock 工具 | **ReAct 循环 + 6+ 生产级工具** |
| Skills | 无 | 无 | **可组合 Skill 库，Prompt+Tool 模板化** |
| 思维链 | 无 | `<thought>` 伪标签 | **结构化 CoT：Observe→Think→Act→Reflect** |
| 提示词工程 | 硬编码 f-string | 固定模板 | **分层模板 + 动态组装 + Few-Shot + 画像注入** |

---

## 2. A2A 协议 —— Agent 间通信架构

> A2A (Agent-to-Agent) 是 Google 提出的开放协议，定义了 AI Agent 之间安全、标准化通信的方式。EduNexus 的 Agent 集群基于 A2A 协议精神设计，同时针对教育内容生成的特定场景做了领域适配。

### 2.1 协议选型

EduNexus 采用 **三层通信架构**，每层服务于不同的通信需求：

```
┌─────────────────────────────────────────────────────┐
│                   Layer 1: 控制面                      │
│              A2A Task 协议 (gRPC-like)                │
│   ● Agent 发现 (Agent Discovery)                      │
│   ● 任务委托 (Task Delegation)                        │
│   ● 能力声明 (Capability Card)                        │
│   ● 状态同步 (Status Sync)                            │
└─────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────┐
│                   Layer 2: 数据面                      │
│                Shared Context Store                   │
│   ● 全局上下文 (GlobalContext) — 学生画像 + 主题       │
│   ● 会话上下文 (SessionContext) — 本次生成任务          │
│   ● Agent 上下文 (AgentContext) — 单个 Agent 输入/输出  │
│   ● 制品存储 (Artifact Store) — 中间产物共享           │
└─────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────┐
│                   Layer 3: 事件面                      │
│           Event Bus (WebSocket + Redis)               │
│   ● Agent 状态变更事件                                 │
│   ● 日志推送事件                                       │
│   ● 制品就绪事件                                       │
│   ● 异常/回滚事件                                      │
└─────────────────────────────────────────────────────┘
```

### 2.2 Agent Card — 能力声明

每个 Agent 在启动时向集群注册自己的 **Agent Card**，声明能力、输入输出契约和支持的工具。Agent Card 是集群内部的服务发现机制——Manager 通过查询注册表获知当前可用的专家 Agent 及其能力边界，从而做出正确的调度决策。

**Agent Card 包含的字段**：

| 类别 | 字段 | 类型 | 说明 |
|------|------|------|------|
| **身份** | `agent_id` | string | 唯一标识，如 `"professor"` |
| | `agent_name` | string | 人类可读名称，如 "教授智能体" |
| | `agent_role` | string | 角色简述，如 "学术内容生成专家" |
| | `version` | string | Agent 版本号，支持灰度升级 |
| **能力** | `capabilities` | string[] | 能力标签列表，如 `["structured_content", "academic_writing"]` |
| | `input_schema` | JSON Schema | 输入数据格式约束 |
| | `output_schema` | JSON Schema | 输出数据格式约束 |
| | `supported_tools` | string[] | 可调用的 MCP 工具 ID 列表 |
| **编排** | `priority` | int (1-10) | 执行优先级，数字越大越优先 |
| | `dependencies` | string[] | 上游依赖 Agent ID 列表 |
| | `max_parallel` | int | 最大并行实例数 |
| | `timeout_ms` | int | 单次执行超时 (毫秒) |
| **质量** | `quality_gates` | string[] | 质量门槛标签，如 `["hallucination_check", "format_validation"]` |
| | `fallback_agent` | string\|null | 不可用时的降级 Agent ID，null 表示不可降级 |

**集群注册表（以 Manager 和 Professor 为例）**：

| Agent ID | 能力标签 | 依赖 | 工具 | 优先级 | 超时 |
|----------|---------|------|------|--------|------|
| `manager` | task_decomposition, priority_planning, resource_scheduling | 无 | web_search, profile_query | 10 | 15s |
| `professor` | structured_content, academic_writing, knowledge_explanation | manager | academic_search, markdown_generator, profile_query | 8 | 45s |
| `architect` | knowledge_structuring, hierarchical_organization | manager | mindmap_renderer, profile_query | 7 | 30s |
| `examiner` | assessment_design, knowledge_evaluation | manager | academic_search, profile_query | 7 | 30s |
| `director` | multimedia_design, script_writing | manager | web_search, profile_query | 6 | 35s |
| `hacker` | code_generation, experiment_design | manager | academic_search, code_executor, profile_query | 6 | 45s |
| `reviewer` | quality_assessment, fact_checking, hallucination_detection | 全部专家 | web_search, academic_search, profile_query | 5 | 30s |

> **设计考量**: Manager 优先级最高（10）且无依赖，确保调度者首先就位。Professor 优先级次之（8），因为其余 4 个专家都直接或间接依赖其产出。Reviewer 优先级最低（5），必须等全部专家完成后才能执行。

### 2.3 A2A 消息格式

集群内所有 Agent 通信使用统一的 JSON 消息信封：

```json
{
  "envelope": {
    "message_id": "msg_7f3a2b_001",
    "correlation_id": "task_abc123",
    "timestamp": "2026-06-09T10:30:00.123Z",
    "ttl_ms": 30000
  },
  "sender": {
    "agent_id": "manager",
    "agent_role": "主控中枢"
  },
  "receiver": {
    "agent_id": "professor",
    "agent_role": "教授"
  },
  "type": "task.delegate",
  "payload": {
    "instruction": "请以「梯度下降算法的几何解释」为主题生成结构化讲义",
    "context_ref": "ctx://session/task_abc123/manager.output",
    "constraints": {
      "min_sections": 4,
      "max_sections": 8,
      "target_audience": "intermediate",
      "format": "structured_document"
    }
  },
  "callback": {
    "on_success": "reviewer.receive_artifact",
    "on_failure": "manager.handle_agent_failure"
  }
}
```

**消息类型枚举**：

| Type | 方向 | 说明 |
|------|------|------|
| `task.delegate` | Manager → Expert | 任务委托：Manager 将子任务分配给专家 |
| `task.status` | Expert → Manager | 状态报告：专家汇报执行进度 |
| `artifact.ready` | Expert → Bus | 制品就绪：专家产出物已存入共享存储 |
| `artifact.request` | Any → Any | 制品请求：请求上游 Agent 的产出 |
| `review.feedback` | Reviewer → Expert | 审核反馈：Reviewer 提出修改建议 |
| `review.approved` | Reviewer → Manager | 审核通过：质量门槛全部满足 |
| `error.retry` | Manager → Expert | 重试指令：要求 Agent 重新执行 |
| `error.escalate` | Expert → Manager | 异常上报：Agent 无法自行恢复 |

### 2.4 任务委托流程 (A2A Task Lifecycle)

```
Manager                        Expert Agent                   Reviewer
   │                                │                             │
   │──── task.delegate ────────────→│                             │
   │     {instruction, context_ref, │                             │
   │      constraints, callback}    │                             │
   │                                │                             │
   │←─── task.status (ack) ────────│                             │
   │     {status: "accepted"}       │                             │
   │                                │                             │
   │                         ┌──────┴──────┐                      │
   │                         │  ReAct Loop  │                      │
   │                         │ Think→Act→   │                      │
   │                         │ Observe→     │                      │
   │                         │ Reflect      │                      │
   │                         └──────┬──────┘                      │
   │                                │                             │
   │←─── task.status (progress) ───│                             │
   │     {progress: 0.6,            │                             │
   │      current_step: "writing"}  │                             │
   │                                │                             │
   │                         ┌──────┴──────┐                      │
   │                         │ 产出存入      │                      │
   │                         │ Shared Store │                      │
   │                         └──────┬──────┘                      │
   │                                │                             │
   │←─── artifact.ready ──────────│                              │
   │     {artifact_ref, metadata}  │                              │
   │                                │                             │
   │─────────────────────────────────────────────────────────────→│
   │                    review.delegate {artifact_ref}            │
   │                                │                             │
   │                                │←── review.feedback ────────│
   │                                │    {suggestions[]}          │
   │                                │                             │
   │                         ┌──────┴──────┐                      │
   │                         │ 根据反馈修改  │                      │
   │                         └──────┬──────┘                      │
   │                                │                             │
   │←─── artifact.ready (v2) ──────│                              │
   │                                │                             │
   │                                │←── review.approved ────────│
   │                                │                             │
   │←─── task.status (done) ───────│                              │
   │     {status: "completed",      │                             │
   │      metrics: {...}}           │                             │
```

### 2.5 上下文引用机制

为避免消息体中携带大量重复数据，A2A 消息中的 `context_ref` 使用 URI 格式引用共享存储中的数据：

```
ctx://{scope}/{task_id}/{agent_id}.{field}
```

**引用示例**：

| URI | 解析 |
|-----|------|
| `ctx://global/profile` | 全局学生画像数据 |
| `ctx://session/task_abc123/topic` | 当前任务的原始主题 |
| `ctx://session/task_abc123/manager.output` | Manager Agent 的完整产出 |
| `ctx://session/task_abc123/professor.output.sections[0]` | Professor 产出第一章 |
| `ctx://session/task_abc123/architect.output.mindmap` | Architect 的思维导图 |

上下文存储引擎负责按需加载、缓存和序列化这些引用。

---

## 3. Agent 集群拓扑与角色设定

### 3.1 集群拓扑图

```
                          ┌──────────────┐
                          │   用户请求     │
                          │  { topic }    │
                          └──────┬───────┘
                                 │
                                 ▼
                     ┌─────────────────────┐
                     │     MANAGER 🧠       │
                     │   (主控中枢·调度者)    │
                     │                      │
                     │  ● 主题语义分析       │
                     │  ● 任务图生成         │
                     │  ● 专家调度决策       │
                     │  ● 全局质量把关       │
                     └──────────┬──────────┘
                                │
                  ┌─────────────┼─────────────┐
                  │             │             │
                  ▼             ▼             ▼
     ┌─────────────────┐  ┌──────────┐  ┌──────────────┐
     │ Task Plan        │  │ Priority │  │ Constraints  │
     │ (子任务分解)      │  │ Queue   │  │ (画像约束)     │
     └────────┬────────┘  └────┬─────┘  └──────┬───────┘
              │                │                │
              └────────────────┼────────────────┘
                               │
               ┌───────────────┼───────────────┐
               │               │               │
    ┌──────────┴──┐  ┌────────┴───┐  ┌────────┴──────┐
    │  📄 阶段 1   │  │  🗺️🖊️ 阶段 2 │  │  🎬💻 阶段 3  │
    │  PROFESSOR  │  │ ARCH+EXAM  │  │ DIR+HACKER   │
    │  (先行者)    │  │ (并行)      │  │ (并行)        │
    └──────┬──────┘  └─────┬──────┘  └──────┬───────┘
           │               │               │
           │        ┌──────┴──────┐        │
           │        │             │        │
           │        ▼             ▼        │
           │   ┌─────────┐ ┌──────────┐   │
           │   │ARCHITECT│ │EXAMINER  │   │
           │   │  (🗺️)   │ │  (📝)    │   │
           │   └─────────┘ └──────────┘   │
           │                              │
           │                     ┌────────┴──────┐
           │                     │               │
           │                     ▼               ▼
           │               ┌──────────┐  ┌───────────┐
           │               │ DIRECTOR │  │  HACKER   │
           │               │  (🎬)    │  │  (💻)     │
           │               └──────────┘  └───────────┘
           │                     │               │
           └─────────────────────┼───────────────┘
                                 │
                                 ▼
                     ┌─────────────────────┐
                     │    REVIEWER 🔍       │
                     │  (质量审查·守门人)    │
                     │                      │
                     │  ● 幻觉风险检测       │
                     │  ● 内容一致性校验      │
                     │  ● 质量标准评分       │
                     │  ● 改进建议生成       │
                     └─────────────────────┘
```

### 3.2 角色设定矩阵

| Agent | 角色原型 | 认知风格 | 专业领域 | 产出物 | 典型思维模式 |
|-------|---------|---------|---------|--------|------------|
| **Manager** | 教育总监 | 系统性·全局观 | 课程设计、教学管理 | 任务分解图 | "这个主题应该从哪几个维度展开？各维度之间的依赖关系是什么？" |
| **Professor** | 大学教授 | 学术性·结构化 | 学科知识、概念讲解 | 📄 结构化讲义 | "如何用从具体到抽象的方式让学生理解这个概念？" |
| **Architect** | 知识架构师 | 结构性·层级化 | 知识图谱、概念关系 | 🗺️ 思维导图 | "这些概念之间的父子关系、依赖关系和横向关联是怎样的？" |
| **Examiner** | 考试设计专家 | 诊断性·评估型 | 测评设计、能力诊断 | 📝 测验题库 | "怎样的题目能有效区分学生是真懂还是假懂？" |
| **Director** | 教育视频导演 | 创意性·叙事型 | 多媒体教学、分镜设计 | 🎬 视频脚本 | "这个抽象概念的最佳视觉隐喻是什么？怎样的叙事节奏最吸引人？" |
| **Hacker** | 实战技术专家 | 实践性·工程型 | 编程、实验设计 | 💻 代码实验 | "能不能写一段能跑的代码让学生亲手验证这个概念？" |
| **Reviewer** | 学术审稿人 | 批判性·严谨型 | 质量评估、事实核查 | 🔍 审核报告 | "这段话有没有事实错误？引用的理论是否准确？" |

### 3.3 执行依赖图 (DAG)

```
                    ┌─────────┐
                    │ MANAGER │
                    └────┬────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
              ▼          ▼          ▼
        ┌──────────┐ ┌────────┐ ┌────────┐
        │PROFESSOR │ │EXAMINER│ │ARCHITECT│   ← Wave 1: 内容先行
        │  (必选)   │ │(依赖P) │ │(依赖P)  │
        └────┬─────┘ └───┬────┘ └───┬─────┘
             │           │          │
             │    ┌──────┘    ┌─────┘
             │    │           │
             ▼    ▼           ▼
        ┌────────┐      ┌──────────┐
        │ HACKER │      │ DIRECTOR │      ← Wave 2: 基于内容二次创作
        │(依赖P) │      │(依赖A+P) │
        └───┬────┘      └────┬─────┘
            │                │
            └────────┬───────┘
                     │
                     ▼
              ┌──────────┐
              │ REVIEWER │                  ← Wave 3: 全局审查
              └──────────┘

依赖说明:
  P = Professor 产出 (基础讲义)
  A = Architect 产出 (思维导图)
  → 箭头表示 "必须先完成"
  → 无箭头连接的同级 Agent 可并行执行
```

### 3.4 并行策略

| 阶段 | 并行组 | 并行数 | 依赖条件 |
|------|--------|--------|---------|
| Wave 0 | Manager | 1 | 无（独立） |
| Wave 1 | Professor + Architect + Examiner | 3 | Manager 完成 |
| Wave 2 | Director + Hacker | 2 | Professor 完成 (Hacker) / Professor + Architect 完成 (Director) |
| Wave 3 | Reviewer | 1 | 全部专家完成 |

---

## 4. 共享基础设施

在深入每个 Agent 的内部设计之前，先定义所有 Agent 共同依赖的基础设施组件。

### 4.1 上下文工程 (Context Engineering)

> **定义**: 上下文工程是系统化管理 LLM 输入信息的技术，通过分层组织、动态组装和精确裁剪来最大化模型的推理质量。

#### 4.1.1 三层上下文模型

```
┌─────────────────────────────────────────────────┐
│              Layer 0: GlobalContext              │
│         全局上下文 (跨任务持久化)                  │
│                                                  │
│  ● student_profile      学生六维画像 (持久)       │
│  ● learning_history     近期学习历史 (3个月)      │
│  ● knowledge_graph      已掌握知识图谱            │
│  ● preferences          学习偏好设置              │
│                                                  │
│  生命周期: 整个会话 / TTL = 24h                   │
│  大小限制: ~8K tokens                             │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────┐
│             Layer 1: SessionContext              │
│          会话上下文 (单次任务内共享)               │
│                                                  │
│  ● task_id             当前任务 ID              │
│  ● topic               原始用户输入主题           │
│  ● manager_plan        Manager 的任务分解方案     │
│  ● constraints         生成约束 (难度/风格/语言)  │
│  ● artifact_registry   已产出制品索引            │
│                                                  │
│  生命周期: 单次生成任务                           │
│  大小限制: ~4K tokens                             │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────┐
│             Layer 2: AgentContext                │
│         Agent 级上下文 (每个 Agent 私有)          │
│                                                  │
│  ● upstream_artifacts  上游 Agent 产出引用       │
│  ● tool_call_history   本次执行中工具调用历史     │
│  ● thought_trail       思维链轨迹                │
│  ● working_memory      工作记忆 (中间计算结果)    │
│  ● retry_count         重试计数                  │
│                                                  │
│  生命周期: 单次 Agent 执行                        │
│  大小限制: ~16K tokens                            │
└─────────────────────────────────────────────────┘
```

#### 4.1.2 上下文组装策略

每个 Agent 执行前，ContextAssembler 模块根据以下规则动态组装上下文。核心思想是**按需供给**——Agent 不需要看到所有信息，只看与当前任务最相关的部分。

**组装原则**：

| 原则 | 说明 |
|------|------|
| **优先级覆盖** | AgentContext > SessionContext > GlobalContext，越靠近 Agent 的上下文优先级越高，可覆盖上层同名字段 |
| **Token 预算** | 总计不超过 16K tokens：GlobalContext ≤ 30%、SessionContext ≤ 25%、AgentContext ≤ 45% |
| **相关性裁剪** | 超预算时按优先级降级：① 只保留与当前主题向量相似度 > 0.6 的画像维度 ② 只保留直接上游，跳过间接引用 ③ 工具调用历史去重并摘要压缩 |
| **结构化注入** | 所有上下文统一使用 XML 标签格式注入 Prompt，模型更容易区分不同来源的信息 |

**组装流程**：

```
ContextAssembler.assemble(agent_card, session, profile, upstream_refs)
        │
        ├── Phase 1: 维度选择
        │   输入: 完整学生画像 + Agent 能力标签
        │   逻辑: 根据 Agent 的能力需求，只选取相关的画像维度
        │   例: Examiner 需要 knowledge_base_score → 保留
        │       Examiner 不需要 cognitive_style → 裁剪
        │
        ├── Phase 2: 制品解析
        │   输入: upstream_refs (如 ["ctx://session/.../professor.output"])
        │   逻辑: 通过 ctx:// URI 从 Shared Store 按需加载上游产出
        │   裁剪: 只加载直接依赖，跳过传递依赖
        │
        └── Phase 3: 格式化注入
            将选中的内容按三层 XML 结构组装为最终上下文字符串
```

#### 4.1.3 上下文注入模板

```xml
<context>
  <!-- 全局层：学生画像 -->
  <global_context>
    <student_profile>
      <knowledge_base_score>75</knowledge_base_score>
      <cognitive_style>实践型 · 视觉偏好</cognitive_style>
      <learning_goals>求职导向 · 深度学习专精</learning_goals>
      <focus_duration>45min</focus_duration>
      <stress_resistance>72</stress_resistance>
    </student_profile>
  </global_context>

  <!-- 会话层：当前任务信息 -->
  <session_context>
    <task_id>task_abc123</task_id>
    <topic>梯度下降算法的几何解释</topic>
    <manager_plan>
      <phase id="1" agent="professor">生成基础讲义</phase>
      <phase id="2" agent="architect">构建思维导图</phase>
      <phase id="3" agent="examiner">设计测验题</phase>
    </manager_plan>
    <target_audience>有一定微积分和线性代数基础的学习者</target_audience>
  </session_context>

  <!-- Agent 层：上游产出引用 -->
  <agent_context>
    <upstream_artifact agent="professor" ref="ctx://session/task_abc123/professor.output">
      <summary>已生成4个章节的讲义，涵盖梯度定义、几何意义、优化过程和变体</summary>
      <key_concepts>["梯度", "方向导数", "学习率", "局部最优"]</key_concepts>
    </upstream_artifact>
    <instruction>
      请基于 Professor 的内容，构建梯度下降的知识结构思维导图。
    </instruction>
  </agent_context>
</context>
```

### 4.2 MCP (Model Context Protocol)

> **MCP** 是 Anthropic 提出的开放标准协议，定义了 AI 模型与外部工具/数据源之间的标准化交互方式。EduNexus 的 Agent 集群通过 MCP 集成工具。

#### 4.2.1 MCP 架构

```
┌──────────────────────────────────────────────┐
│                 MCP Client                    │
│         (Agent 内部的 MCP 连接器)              │
│                                               │
│  ● 工具发现 (list_tools)                       │
│  ● 资源访问 (read_resource)                    │
│  ● 提示模板 (get_prompt)                       │
│  ● 安全沙箱 (Sandbox)                          │
└──────────────────┬───────────────────────────┘
                   │
       ┌───────────┼───────────┐
       │           │           │
       ▼           ▼           ▼
┌────────────┐ ┌──────────┐ ┌──────────────┐
│ MCP Server │ │MCP Server│ │ MCP Server   │
│ Academic   │ │ Code     │ │ Web          │
│ Search     │ │ Executor │ │ Search       │
└──────┬─────┘ └────┬─────┘ └──────┬───────┘
       │            │              │
       ▼            ▼              ▼
┌────────────┐ ┌──────────┐ ┌──────────────┐
│ Arxiv API  │ │ Sandbox  │ │ Bing/Google  │
│ Semantic   │ │ Container│ │ Search API   │
│ Scholar    │ │ (Docker) │ │              │
└────────────┘ └──────────┘ └──────────────┘
```

#### 4.2.2 Tool Registry (工具注册表)

集群维护一个全局工具注册表，每个工具通过独立的 MCP Server 提供能力。Agent 根据自身 `supported_tools` 列表获取对应工具的调用权限。

**学术检索工具** `academic_search`

| 属性 | 值 |
|------|-----|
| 功能 | 检索学术论文和教材资料，支持 Arxiv、Semantic Scholar、Wikipedia 多数据源 |
| MCP Server | `academic-search-server` |
| 关键参数 | `query` (检索词), `source` (arxiv/semantic_scholar/wikipedia), `max_results` (默认 5) |
| 返回 | 论文列表，含标题、摘要、URL、年份 |
| 限制 | 速率 10 次/分钟，超时 15s |

**代码执行工具** `code_executor`

| 属性 | 值 |
|------|-----|
| 功能 | 在 Docker 沙箱中安全执行 Python 代码并返回 stdout/stderr/exit_code |
| MCP Server | `code-executor-server` |
| 关键参数 | `code` (Python 源码), `timeout_seconds` (默认 30), `dependencies` (pip 包列表) |
| 安全约束 | 必须启用沙箱，网络隔离，无文件系统写入权限 |
| 限制 | 超时 60s |

**网络搜索工具** `web_search`

| 属性 | 值 |
|------|-----|
| 功能 | 搜索互联网获取最新信息，用于事实核查和补充资料 |
| MCP Server | `web-search-server` |
| 关键参数 | `query` (检索词), `region` (默认 zh-CN) |
| 返回 | 搜索结果列表，含标题、摘要、URL、来源 |
| 限制 | 速率 30 次/分钟，超时 10s |

**画像查询工具** `profile_query`

| 属性 | 值 |
|------|-----|
| 功能 | 查询当前学生的六维学习画像，支持按维度过滤 |
| MCP Server | `internal-db-server` |
| 关键参数 | `dimension` (all/knowledge/cognitive/goals) |
| 返回 | 对应维度的画像数据 |
| 限制 | 内部工具，超时 2s |

**内容格式化工具** `markdown_generator`

| 属性 | 值 |
|------|-----|
| 功能 | 将结构化 JSON 内容按模板渲染为格式化 Markdown |
| MCP Server | `content-formatter-server` |
| 关键参数 | `content` (结构化数据), `template` (lecture/quiz/script/report) |
| 返回 | 格式化后的 Markdown 字符串 |
| 限制 | 超时 5s |

**可视化渲染工具** `mindmap_renderer`

| 属性 | 值 |
|------|-----|
| 功能 | 将 JSON 思维导图结构渲染为 Mermaid 代码或 SVG 图形 |
| MCP Server | `visualization-server` |
| 关键参数 | `mindmap_data` (树形结构), `output_format` (mermaid/svg/json) |
| 返回 | Mermaid 代码字符串或 SVG 数据 |
| 限制 | 超时 5s |

#### 4.2.3 MCP Client 职责

Agent 内部的 MCP Client 是工具调用的统一入口，封装了 5 项核心职责：

```
                    ┌─────────────┐
                    │  MCP Client  │
                    └──────┬──────┘
                           │
    ┌──────────┬───────────┼───────────┬──────────┐
    │          │           │           │          │
    ▼          ▼           ▼           ▼          ▼
┌───────┐ ┌───────┐ ┌──────────┐ ┌───────┐ ┌──────────┐
│权限检查│ │参数校验│ │缓存+限流  │ │MCP调用│ │结果标准化 │
└───────┘ └───────┘ └──────────┘ └───────┘ └──────────┘
```

| 职责 | 说明 |
|------|------|
| **权限检查** | 根据 Agent Card 的 `supported_tools` 白名单，拒绝越权调用 |
| **参数校验** | 根据工具注册表中的参数 Schema 校验输入，不合规参数提前拦截 |
| **缓存+限流** | 相同(工具, 参数)的调用 5 分钟内复用缓存结果；超出速率限制的调用排队等待 |
| **MCP 调用** | 通过指定 MCP Server 执行实际工具调用，支持重试和超时控制 |
| **结果标准化** | 无论底层数据源格式如何，统一返回结构化结果，并记录到 Agent 执行轨迹中 |

此外，MCP Client 负责将工具定义转换为 **OpenAI Function Calling 兼容的 JSON Schema**，注入到 LLM 请求中，使 Agent 能够自主决策何时调用哪个工具。

### 4.3 Skills 技能系统

> **Skills** 是比 Tool 更高层的抽象——一个 Skill 封装了完成特定任务所需的 Prompt 模板 + 工具调用序列 + 输出格式约束，是可复用的"能力模块"。

#### 4.3.1 Skill 模型

Skill 是比 Tool 更高层的抽象——它封装了完成特定任务所需的**完整能力包**，包含三个核心要素：

```
┌─────────────────────────────────────────────┐
│                 Skill 能力包                  │
│                                              │
│  ┌─────────────────────────────────────┐    │
│  │  ① Prompt 扩展                       │    │
│  │     追加到 System Prompt 的行为指引    │    │
│  │     例: "按八段式结构生成内容"          │    │
│  └─────────────────────────────────────┘    │
│  ┌─────────────────────────────────────┐    │
│  │  ② 工具序列                          │    │
│  │     推荐的工具调用顺序和参数            │    │
│  │     例: 先 academic_search → 再生成    │    │
│  └─────────────────────────────────────┘    │
│  ┌─────────────────────────────────────┐    │
│  │  ③ 质量约束                          │    │
│  │     输出 JSON Schema + 校验规则       │    │
│  │     + Few-Shot 示例                  │    │
│  └─────────────────────────────────────┘    │
│                                              │
│  附加: required_capabilities (能力匹配门槛)    │
│        required_context (上下文需求清单)       │
└─────────────────────────────────────────────┘
```

**Skill 的触发方式**：Agent 执行时，系统扫描 Skill Library，将 `required_capabilities` 与 Agent 的 `capabilities` 做交集匹配。若匹配度超过 70%，该 Skill 被激活并注入到 Agent 的运行上下文中。Agent 在 CoT 的 Think 阶段可以自主选择使用哪些已激活的 Skill。

#### 4.3.2 Skill Library (技能库)

**① 内容结构化技能 `structured_content_creation`**

| 属性 | 内容 |
|------|------|
| **激活条件** | Agent 具备 `academic_writing` + `knowledge_explanation` 能力 |
| **行为指引** | 按引言→前置知识→核心概念→数学推导→直观理解→应用场景→常见误区→小结 八段式结构生成 |
| **推荐工具序列** | ① `academic_search` (Arxiv) → ② `academic_search` (Wikipedia) → ③ 内容撰写 → ④ `markdown_generator` |
| **输出校验** | 章节数 ≥ 4；每章正文 > 200 字；关键概念 ≥ 3 个 |
| **Few-Shot 示例** | 输入 "反向传播算法" → 输出 5 章结构化讲义 + 4 个关键概念 |
| **适用 Agent** | Professor |

**② 测验设计技能 `quiz_design`**

| 属性 | 内容 |
|------|------|
| **激活条件** | Agent 具备 `assessment_design` + `knowledge_evaluation` 能力 |
| **行为指引** | 按 Bloom 分类法设计：记忆层 (概念定义) → 理解层 (自我解释) → 应用层 (场景应用) → 分析层 (比较对比，可选) |
| **推荐工具序列** | ① `profile_query` (获取知识基础评分定难度) → ② 逐题设计 |
| **输出校验** | 题目数 ≥ 3；每题 4 个选项；正确答案在 0-3 范围内 |
| **适用 Agent** | Examiner |

**③ 思维导图构建技能 `mindmap_construction`**

| 属性 | 内容 |
|------|------|
| **激活条件** | Agent 具备 `knowledge_structuring` + `hierarchical_organization` 能力 |
| **行为指引** | 根节点=主题 → 一级分支=核心维度(3-4) → 二级=子概念 → 三级=细节/例子；同级节点保持相同抽象层次 |
| **推荐工具序列** | ① `profile_query` (认知风格) → ② 构建 JSON 结构 → ③ `mindmap_renderer` (Mermaid) |
| **适用 Agent** | Architect |

**④ 代码实验设计技能 `code_lab_design`**

| 属性 | 内容 |
|------|------|
| **激活条件** | Agent 具备 `code_generation` + `experiment_design` 能力 |
| **行为指引** | 渐进式 (简单→复杂) + 可视化 (matplotlib) + 完整可运行 + 中文注释 + 参数修改入口 |
| **推荐工具序列** | ① `academic_search` (GitHub 参考) → ② 编写代码 → ③ ★ `code_executor` (沙箱验证) → ④ 修正 → ⑤ 设计扩展练习 |
| **输出校验** | 代码 > 200 字符；沙箱执行成功 (exit_code=0) |
| **适用 Agent** | Hacker |

**⑤ 幻觉检测技能 `hallucination_detection`**

| 属性 | 内容 |
|------|------|
| **激活条件** | Agent 具备 `quality_assessment` + `fact_checking` 能力 |
| **行为指引** | 五维评分体系：事实准确性 + 内容一致性 + 教学有效性 + 完整性 + 幻觉风险；对高风险区域 (公式/定义/人名/代码) 重点审查并交叉验证 |
| **推荐工具序列** | ① `web_search` (定义交叉验证) → ② `academic_search` (Wikipedia 对照) → ③ 逐项打分 → ④ 生成改进建议 |
| **适用 Agent** | Reviewer

#### 4.3.3 Skill 执行模型

```
Agent 收到任务
      │
      ▼
┌──────────────────┐
│  1. 能力匹配      │  Agent 的能力标签 ∩ Skill 的 required_capabilities
│                  │  匹配度 > 70% → 可使用此 Skill
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  2. Skill 加载    │  加载 Skill 的 system_prompt_addition + tool_sequence
│                  │  合并到 Agent 的工作上下文中
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  3. 上下文注入    │  将 required_context 注入 Prompt
│                  │  注入 few_shot_examples 到历史消息
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  4. ReAct 执行    │  按照 tool_sequence 引导执行工具调用
│                  │  实际调用由 Agent 自主决定 (可跳过/重排)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  5. 输出校验      │  按 validation_rules 校验产出格式
│                  │  不通过 → 自动重试或标记异常
└──────────────────┘
```

### 4.4 思维链 (Chain of Thought)

> **CoT** 是一种提示技术，引导模型在执行过程中显式展示推理步骤。EduNexus 采用结构化的四阶段思维链模型。

#### 4.4.1 Observe-Think-Act-Reflect (OTAR) 循环

```
        ┌──────────────────────────────────────┐
        │            OTAR 思维循环               │
        │                                       │
        │  ┌─────────┐                          │
        │  │ OBSERVE │  观察                     │
        │  │ 观察阶段 │  ● 读取上下文              │
        │  │         │  ● 分析上游产出            │
        │  └────┬────┘  ● 识别信息缺口            │
        │       │                               │
        │       ▼                               │
        │  ┌─────────┐                          │
        │  │  THINK  │  思考                     │
        │  │ 思考阶段 │  ● 分解子任务             │
        │  │         │  ● 选择 Skill             │
        │  └────┬────┘  ● 决定是否需要工具        │
        │       │                               │
        │       ▼                               │
        │  ┌─────────┐                          │
        │  │   ACT   │  行动                     │
        │  │ 行动阶段 │  ● 调用 Tool             │
        │  │         │  ● 生成内容               │
        │  └────┬────┘  ● 写入共享存储           │
        │       │                               │
        │       ▼                               │
        │  ┌─────────┐                          │
        │  │ REFLECT │  反思                     │
        │  │ 反思阶段 │  ● 自检产出质量           │
        │  │         │  ● 对比约束条件           │
        │  └────┬────┘  ● 决定是否重新 Act       │
        │       │                               │
        │       │ 质量不满足 → 回到 OBSERVE       │
        │       │ 质量满足   → 输出结果           │
        └───────┴──────────────────────────────┘
```

#### 4.4.2 结构化 CoT 注入模板

```xml
<thinking_protocol>
  你必须在每次回复中遵循以下思维协议。你的思考过程用 <thought> 标签包裹，
  最终输出用 <output> 标签包裹。

  <phase name="observe">
    1. 列出你从 <context> 中获取到的关键信息
    2. 识别任何信息缺口或不确定点
    3. 说明这些信息如何影响你的任务执行
  </phase>

  <phase name="think">
    4. 将任务分解为 2-5 个具体步骤
    5. 对每一步，判断是需要 Tool Use 还是纯推理
    6. 选择最适合的 Skill（如有）
    7. 预估每步的 Token 消耗和耗时
  </phase>

  <phase name="act">
    8. 按步骤顺序执行：
       - 如需工具 → 输出 <tool_call>{"name": "...", "arguments": {...}}</tool_call>
       - 如需推理 → 在 <thought> 中阐述推理过程
    9. 将中间结果记录到工作记忆中
  </phase>

  <phase name="reflect">
    10. 对照约束条件检查产出
    11. 检查是否有事实错误、逻辑跳跃
    12. 如果质量不满足，说明哪里不足，回到 Observe 阶段
    13. 如果质量满足，输出 <output> 包裹的最终结果
  </phase>
</thinking_protocol>
```

### 4.5 提示词工程 (Prompt Engineering)

> EduNexus 采用**分层模板 + 动态组装**的提示词架构，确保每个 Agent 的 Prompt 既稳定可控又个性化适配。

#### 4.5.1 五层 Prompt 架构

```
┌─────────────────────────────────────────────┐
│ Layer 0: Base Identity (固定，不随任务变化)    │
│ ─────────────────────────────────────────── │
│ 角色定义 + 核心人格 + 输出语言 + 能力范围      │
│                                             │
│ "你是一位资深的教育学教授。你擅长用通俗易懂   │
│  的方式解释复杂概念。你的回答总是结构清晰。   │
│  你使用中文回答，代码注释也用中文。"           │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────┴────────────────────────┐
│ Layer 1: Skill Injection (根据匹配的Skill)    │
│ ─────────────────────────────────────────── │
│ 技能激活后的行为指引 + 工具序列                │
│                                             │
│ "你已激活 structured_content_creation 技能。  │
│  请按照 引言→前置→核心→推导→直观→应用→误区    │
│  →小结 的八段式结构生成内容。"                │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────┴────────────────────────┐
│ Layer 2: CoT Protocol (通用思维链协议)         │
│ ─────────────────────────────────────────── │
│ Observe-Think-Act-Reflect 循环规则            │
│ (见 4.4.2 节模板)                            │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────┴────────────────────────┐
│ Layer 3: Dynamic Constraints (任务级动态约束)  │
│ ─────────────────────────────────────────── │
│ 画像驱动的个性化参数 + 上游产出约束            │
│                                             │
│ "当前学生知识基础评分: 75/100                 │
│  认知风格: 实践型·视觉偏好                    │
│  请将内容难度控制在 intermediate 级别          │
│  多使用图示和代码示例，少用纯数学公式           │
│  参考 Professor 的第2章内容作为起点"           │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────┴────────────────────────┐
│ Layer 4: Few-Shot Examples (任务级示例)       │
│ ─────────────────────────────────────────── │
│ 针对当前任务类型的少量高质示例                 │
│                                             │
│ 示例输入: "反向传播算法"                      │
│ 示例输出: { title: "...", sections: [...] }  │
└─────────────────────────────────────────────┘
```

#### 4.5.2 画像注入策略

学生六维画像是 Prompt 个性化的核心驱动因素。不同画像维度影响 Prompt 的不同层面：

| 画像维度 | 影响的 Prompt 层面 | 低值策略 (0-40) | 中值策略 (40-70) | 高值策略 (70-100) |
|---------|-------------------|----------------|-----------------|-----------------|
| **knowledge_base_score** | 内容深度 | 从最基础概念开始，多用生活化类比 | 标准学术表述，适当引入专业术语 | 跳过基础回顾，直接进入高级理论和数学推导 |
| **cognitive_style** (视觉型) | 表达方式 | 多用可视化比喻和图表描述 | 文字与图示并重 | — |
| **cognitive_style** (实践型) | 示例类型 | 每个概念配可运行代码示例 | 重点概念配动手实验 | — |
| **cognitive_style** (理论型) | 推导深度 | — | 给出完整数学公式推导过程 | 增加定理证明和推导练习 |
| **focus_duration** | 内容长度 | 每章 ≤ 300 字，总章 ≤ 4 | 每章 300-500 字，总章 4-6 | 每章 500-800 字，总章 6-8 |
| **stress_resistance** | 测验难度 | 错误选项设计得更明显，降低挫败感 | 标准难度，正常迷惑项 | 提高迷惑项质量，增加挑战性 |
| **learning_goals** (求职导向) | 用例方向 | 使用面试常见问题和工业界实际场景 | 兼顾理论与应用 | — |

> **设计考量**: 画像注入不是简单的"拼接一段文字"，而是根据每个维度值触发对应的 Prompt 修改规则，确保生成的内容在难度、风格、长度、用例方向上与学生的实际状态对齐。这种个性化策略使得同一个主题 "梯度下降" 对不同学生可以产出完全不同深度和风格的讲义。

#### 4.5.3 分 Agent 的 Prompt 策略

| Agent | 核心 Prompt 策略 | 温度 | Max Tokens | 特殊设置 |
|-------|-----------------|------|------------|---------|
| **Manager** | Zero-Shot + 结构化输出格式约束 | 0.3 | 2000 | `response_format: json_object` |
| **Professor** | Few-Shot (2例) + 八段式结构 + 画像自适应 | 0.7 | 4000 | 无 |
| **Architect** | One-Shot + 层级约束 + JSON 强制 | 0.5 | 3000 | `response_format: json_object` |
| **Examiner** | Few-Shot (3例) + Bloom 分类法 + JSON 强制 | 0.5 | 3000 | `response_format: json_object` |
| **Director** | Few-Shot (1例) + 场景模板 + 资源引用 | 0.8 | 3000 | 允许较高创意温度 |
| **Hacker** | One-Shot + 代码规范 + 执行验证 | 0.4 | 4000 | `stop: ["\n\n\n"]` |
| **Reviewer** | Zero-Shot + 结构化评分维度 + JSON 强制 | 0.2 | 2000 | `response_format: json_object` |

---

## 5. Agent 内部设计 —— 逐一拆解

> 以下逐一介绍 7 个 Agent 的内部设计。每个 Agent 由六个维度构成：上下文工程、MCP 工具集成、技能激活、思维链策略、提示词模板、输出规格。

### 5.1 Manager Agent — 主控中枢

#### 5.1.1 定位

Manager 是整个集群的**入口和调度大脑**。它不直接生成教学内容，而是分析用户输入的主题，将其拆解为 5 个具有明确依赖关系的子任务，并生成执行计划供下游 Agent 遵循。

#### 5.1.2 上下文工程

```
Manager 上下文输入:
┌─────────────────────────────────────┐
│ GlobalContext                        │
│  ● student_profile (完整六维)        │ ← 影响难度判断和补充节点决策
│  ● knowledge_graph (已掌握节点)      │ ← 识别学生已有知识，避免重复
├─────────────────────────────────────┤
│ SessionContext                       │
│  ● topic (原始用户输入)              │
├─────────────────────────────────────┤
│ AgentContext (Manager 私有)          │
│  ● 无上游依赖 (集群入口)              │
└─────────────────────────────────────┘

Manager 上下文输出 (写入 SessionContext):
┌─────────────────────────────────────┐
│  ● manager_plan: {                  │
│      "phases": [...],               │
│      "dependencies": {...},         │
│      "constraints": {...}           │
│    }                                │
└─────────────────────────────────────┘
```

#### 5.1.3 MCP 工具集成

| 工具 | 用途 | 调用时机 |
|------|------|---------|
| `web_search` | 搜索主题的最新发展、确认概念边界 | 主题语义分析阶段 |
| `profile_query` | 获取学生画像，判断难度和注入节点 | 约束生成阶段 |

#### 5.1.4 技能激活

Manager 固定激活 `task_decomposition` 技能，该技能定义了 Manager 拆解主题的五层分析法：

```
主题分解的五层模型:

  概念层 (→ Professor)    结构层 (→ Architect)   评估层 (→ Examiner)
  "核心概念是什么？"       "概念间什么关系？"      "如何检验理解程度？"
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
          媒体层 (→ Director)           工程层 (→ Hacker)
          "如何用视频呈现？"            "如何用代码验证？"
```

**附加决策规则**：

| 条件 | 决策 |
|------|------|
| 学生 knowledge_base_score < 60 | 标记 `injection_node`，插入补充基础知识节点 |
| 主题涉及明确数学前提 | 标记 `recommend_math_review`，建议先复习相关数学 |

**推荐工具序列**：① `web_search` (检索主题概况，确认概念边界) → ② `profile_query` (获取完整画像，决定难度和注入策略)

#### 5.1.5 思维链策略

Manager 使用 **轻量 CoT**（单轮 OTA，无 Reflect 阶段，因为下游 Agent 会验证）：

```
OBSERVE: 主题语义 + 学生画像 + 知识图谱已掌握节点
   ↓
THINK:   拆解为 5 个子任务 + 判断依赖关系 + 决定是否注入补充节点
   ↓
ACT:     生成 JSON 格式的执行计划
```

#### 5.1.6 提示词模板

````
<system>
你是一位资深的教育总监 (Education Director)。你负责分析学习主题，制定多智能体协同教学计划。

{skill_injection}

{context_injection}

{thinking_protocol}

<output_format>
你的输出必须是一个严格的 JSON 对象：
```json
{
  "title": "主题的正式名称",
  "difficulty_assessment": "beginner|intermediate|advanced",
  "phases": [
    {
      "phase_id": 1,
      "agent": "professor",
      "instruction": "具体任务描述",
      "dependencies": [],
      "estimated_tokens": 3000
    }
  ],
  "injection_nodes": [
    {
      "label": "补充知识点名称",
      "reason": "因为学生 XXX 基础薄弱",
      "target_agent": "professor"
    }
  ],
  "global_constraints": {
    "language": "zh-CN",
    "code_language": "python",
    "max_total_tokens": 15000
  }
}
```
</output_format>
</system>
````

---

### 5.2 Professor Agent — 教授

#### 5.2.1 定位

Professor 是集群的**内容基石**。它生成结构化的学术讲义，其他 Agent（Architect、Examiner、Hacker）都直接或间接依赖其产出。因此 Professor 在 Wave 1 首先执行。

#### 5.2.2 上下文工程

```
Professor 上下文输入:
┌─────────────────────────────────────┐
│ GlobalContext                        │
│  ● student_profile.knowledge_base    │ ← 决定内容深度
│  ● student_profile.cognitive_style   │ ← 决定表达方式
│  ● student_profile.learning_goals    │ ← 决定用例方向
├─────────────────────────────────────┤
│ SessionContext                       │
│  ● topic                             │
│  ● manager_plan (phase 1 的指令)     │
│  ● global_constraints                │
├─────────────────────────────────────┤
│ AgentContext                         │
│  ● 无上游产出依赖                     │
│  ● injection_nodes (如有)            │ ← Manager 标记的补充节点
└─────────────────────────────────────┘
```

#### 5.2.3 MCP 工具集成

| 工具 | 用途 | 调用时机 |
|------|------|---------|
| `academic_search` | 搜索 Arxiv/Wikipedia 验证概念准确性 | 写每个章节前 |
| `markdown_generator` | 将结构化 JSON 转为 Markdown | 全部章节写完后 |
| `profile_query` | 获取画像以调整难度 | 开始前 |

#### 5.2.4 技能激活

Professor 固定激活 `structured_content_creation` 技能（见 4.3.2 节完整定义）。

#### 5.2.5 思维链策略

Professor 使用 **完整 OTAR 循环**，最多 3 次 Reflect→Observe 迭代：

```
OBSERVE → 读取主题、画像、Manager 指令、injection_nodes
   ↓
THINK   → 决定章节结构 (4-8 章)、每章的关键概念
          检查画像 → 确定难度、表达风格、是否需要数学推导
   ↓
ACT     → 对每个章节:
           1. academic_search 验证概念 (可选)
           2. 撰写章节内容
           3. 检查与下游 Agent 的信息传递完整性
          全部完成后 → markdown_generator 格式化
   ↓
REFLECT → 自检:
           1. 章节数满足? (≥4)
           2. 每章 > 200 字?
           3. 概念定义准确? (对照搜索结果)
           4. 对下游 Agent 信息充分?
          ❌ 不满足 → 回到 OBSERVE 补全
          ✅ 满足 → 输出 + 写入 shared_store
```

#### 5.2.6 提示词模板

````
<system>
你是一位资深的教育学教授，有 20 年以上的教学经验。你擅长用深入浅出的方式解释复杂概念。

{cot_protocol}

{skill_injection}

{profile_aware_instruction}

<content_guidelines>
1. 每个章节应该让学生读完产生"原来如此"的感觉
2. 数学公式使用 LaTeX 语法包裹
3. 代码示例使用 ```python ``` 代码块
4. 概念之间要有逻辑递进关系
5. 关键术语用 **粗体** 标注
</content_guidelines>

<output_format>
严格按照以下 JSON Schema 输出:
```json
{
  "title": "string",
  "estimated_reading_time_minutes": int,
  "target_audience": "beginner|intermediate|advanced",
  "sections": [
    {
      "heading": "章节标题",
      "body": "详细正文 (Markdown 格式)",
      "key_takeaway": "一句话要点",
      "related_concepts": ["相关概念1"]
    }
  ],
  "key_concepts": [
    {"term": "概念名", "definition": "一句话定义"}
  ],
  "further_reading": [
    {"title": "推荐阅读", "url": "链接", "reason": "推荐理由"}
  ]
}
```
</output_format>
</system>
````

---

### 5.3 Architect Agent — 架构师

#### 5.3.1 定位

Architect 负责将 Professor 的线性讲义转化为**层级化的树形知识结构**（思维导图/概念图）。它在 Wave 1 与 Professor 可部分并行，但需要 Professor 的 sections 列表来确定节点范围。

#### 5.3.2 上下文工程

```
Architect 上下文输入:
┌─────────────────────────────────────┐
│ GlobalContext                        │
│  ● student_profile.cognitive_style   │ ← 视觉型→增强可视化
├─────────────────────────────────────┤
│ SessionContext                       │
│  ● topic                             │
│  ● manager_plan                      │
├─────────────────────────────────────┤
│ AgentContext                         │
│  ● upstream: professor.output        │ ← 核心输入
│    - sections[].heading              │ ← 用作节点标签
│    - key_concepts                    │ ← 用作关系锚点
└─────────────────────────────────────┘
```

#### 5.3.3 MCP 工具集成

| 工具 | 用途 |
|------|------|
| `mindmap_renderer` | 将 JSON 结构转为 Mermaid 代码或 SVG |
| `profile_query` | 查询认知风格 |

#### 5.3.4 技能激活

激活 `mindmap_construction` 技能（见 4.3.2 节）。

#### 5.3.5 思维链策略

```
OBSERVE → 解析 Professor 的 sections 和 key_concepts
   ↓
THINK   → 识别主题的核心维度 (3-4 个一级分支)
          为每个维度分配对应的章节
          确定二级/三级节点 (概念→子概念→例子)
          判断是否需要增加跨分支的关联边
   ↓
ACT     → 构建树形 JSON
          → mindmap_renderer 生成 Mermaid
   ↓
REFLECT → 检查: 每个一级分支 ≥ 2 个二级节点?
          每个节点标签 ≤ 15 个字符?
          覆盖了 Professor 的所有 key_concepts?
```

#### 5.3.6 提示词模板

````
<system>
你是一位知识架构师 (Knowledge Architect)。你将教学内容转化为清晰的层级化思维导图。

关键原则:
- 同级节点保持相同的抽象层次
- 节点命名简洁 (≤ 15 个中文字符)
- 从抽象到具体，从核心到外围
- 识别并标注跨分支的概念关联

{skill_injection}

<output_format>
```json
{
  "mindmap": {
    "root": "主题名",
    "children": [
      {
        "name": "一级分支",
        "children": [
          {
            "name": "二级节点",
            "children": [
              {"name": "三级细节/例子"}
            ]
          }
        ]
      }
    ]
  },
  "cross_links": [
    {"from": "节点A", "to": "节点B", "relation": "关联描述"}
  ],
  "mermaid_code": "graph TD\\n  A[主题] --> B[分支1]\\n ..."
}
```
</output_format>
</system>
````

---

### 5.4 Examiner Agent — 考官

#### 5.4.1 定位

Examiner 基于 Professor 的讲义设计**高区分度测验题**。它在 Wave 1 执行，依赖 Professor 的产出。

#### 5.4.2 上下文工程

| 层级 | 内容 | 用途 |
|------|------|------|
| GlobalContext | profile.knowledge_base_score | 决定题目难度锚点 |
| SessionContext | topic, manager_plan | 题目范围约束 |
| AgentContext | professor.output.sections + key_concepts | 出题原材料 |

#### 5.4.3 MCP 工具集成

| 工具 | 用途 |
|------|------|
| `profile_query` | 获取知识基础分数，决定难度 |
| `academic_search` | 搜索类似主题的经典考题作为参考 |

#### 5.4.4 技能激活

激活 `quiz_design` 技能（见 4.3.2 节，含 Bloom 分类法）。

#### 5.4.5 思维链策略

```
OBSERVE → 读取 Professor 的 key_concepts 和 sections 正文
   ↓
THINK   → 确定每个 key_concept 对应 Bloom 哪一层
          知识基础 < 40 → 侧重记忆+理解层
          知识基础 40-70 → 侧重理解+应用层
          知识基础 > 70 → 增加分析层和综合层
   ↓
ACT     → 逐题设计：
          1. 题干 (精确无歧义)
          2. 4 个选项 (1 正解 + 3 迷惑项)
          3. 解析 (解释为什么对、为什么错)
   ↓
REFLECT → 检查: 正解是否确实正确? 迷惑项是否足够迷惑?
          每题是否对应一个明确的知识点?
```

#### 5.4.6 提示词模板

````
<system>
你是一位专业的考试设计专家 (Examination Designer)，精通 Bloom 教育目标分类法。

{skill_injection}

<design_principles>
1. 迷惑项 (distractor) 应来自常见的概念混淆、计算错误、理解偏差
2. 每道题考查一个明确的知识点，不混合多个概念
3. 解析部分必须包含"为什么正确答案是对的"和"为什么其他选项是错的"
4. 难度递进：第1题简单→第3题较难
</design_principles>

<output_format>
```json
{
  "questions": [
    {
      "question": "题目描述",
      "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
      "answer": 0,
      "explanation": "详细解析",
      "bloom_level": "remember|understand|apply|analyze",
      "tested_concept": "考查的知识点"
    }
  ],
  "difficulty_summary": "整体难度说明"
}
```
</output_format>
</system>
````

---

### 5.5 Director Agent — 导演

#### 5.5.1 定位

Director 将教学内容转化为**视频分镜脚本**，包含画面描述、旁白台词、时长估算和资源推荐。它在 Wave 2 执行，依赖 Professor (内容) 和 Architect (结构)。

#### 5.5.2 上下文工程

| 层级 | 内容 | 用途 |
|------|------|------|
| GlobalContext | profile.cognitive_style, profile.focus_duration | 决定视频节奏和时长分配 |
| SessionContext | topic, manager_plan | 主题约束 |
| AgentContext | professor.output (内容来源), architect.output (结构来源) | 分镜素材 |

#### 5.5.3 MCP 工具集成

| 工具 | 用途 |
|------|------|
| `web_search` | 搜索 YouTube/Bilibili 相关视频资源作为推荐 |
| `profile_query` | 获取专注时长，决定总视频时长 |

#### 5.5.4 技能激活

激活 `script_writing` 技能。

#### 5.5.5 思维链策略

```
OBSERVE → 读取 Professor 讲义 (核心内容) + Architect 思维导图 (叙事结构)
   ↓
THINK   → 确定视频总时长 (基于 focus_duration)
          确定场景数 (3-5 个)
          每个场景对应思维导图的一个一级分支
          寻找最佳视觉隐喻
   ↓
ACT     → 逐场景撰写:
          1. 场景标题 + 编号
          2. 画面描述 (视觉元素、动画效果)
          3. 旁白台词 (口语化，节奏感)
          4. 时长估算
          5. web_search 推荐相关视频资源
   ↓
REFLECT → 检查: 场景间逻辑连贯? 总时长 ≤ focus_duration?
          旁白是否口语化? 视觉描述是否可执行?
```

#### 5.5.6 提示词模板

````
<system>
你是一位教育视频导演 (Educational Video Director)。你将教学内容转化为生动、可执行的视频分镜脚本。

<principles>
1. 每个场景有明确的"钩子"——开场 3 秒内抓住注意力
2. 旁白是口语，不是书面语。读出来要自然
3. 视觉描述要具体，让动画师能直接照着做
4. 总时长控制在学生专注时长的 80% 以内
</principles>

<output_format>
```json
{
  "scenes": [
    {
      "scene_number": 1,
      "title": "场景标题",
      "visual": "画面描述 (构图、颜色、动画、文字)",
      "voiceover": "旁白台词 (口语化)",
      "duration_seconds": 45,
      "resources": [
        {
          "type": "video",
          "title": "推荐视频标题",
          "url": "https://...",
          "description": "推荐理由",
          "platform": "YouTube|Bilibili",
          "duration": "10:00"
        }
      ]
    }
  ],
  "total_duration_seconds": 240,
  "recommended_music_mood": "配乐情绪建议",
  "production_notes": "制作备注"
}
```
</output_format>
</system>
````

---

### 5.6 Hacker Agent — 极客

#### 5.6.1 定位

Hacker 设计**可运行的代码实验**，让学生通过动手实践来验证和巩固理论。在 Wave 2 执行，依赖 Professor 的内容。

#### 5.6.2 上下文工程

| 层级 | 内容 | 用途 |
|------|------|------|
| GlobalContext | profile.knowledge_base_score | 决定代码复杂度 |
| SessionContext | topic, manager_plan | 主题约束 |
| AgentContext | professor.output.sections + key_concepts | 确定实验覆盖哪些概念 |

#### 5.6.3 MCP 工具集成

| 工具 | 用途 |
|------|------|
| `academic_search` | 搜索 GitHub 上的相关实现参考 |
| `code_executor` | ★ 核心工具：在沙箱中执行生成的代码，验证可运行性和输出正确性 |
| `profile_query` | 获取知识基础评分 |

#### 5.6.4 技能激活

激活 `code_lab_design` 技能（见 4.3.2 节）。

#### 5.6.5 思维链策略

```
OBSERVE → 读取 Professor 的 key_concepts 和关键公式/算法
   ↓
THINK   → 选择最核心的 1-2 个概念做代码实验
          确定编程语言 (默认 Python)
          确定实验结构: 库导入 → 核心实现 → 可视化 → 参数实验
   ↓
ACT     → 1. academic_search 找参考实现
          2. 编写完整代码 (含中文注释)
          3. ★ code_executor 沙箱执行验证
          4. 根据执行结果修正代码
          5. 设计 2-3 个扩展练习
   ↓
REFLECT → 检查: 代码能跑通? 输出正确? 注释完整?
          核心概念被代码覆盖? 扩展练习有意义?
          ❌ 代码不运行 → 修正后重新 ACT
```

#### 5.6.6 提示词模板

````
<system>
你是一位实战派技术专家 (Hands-on Technologist)。你通过可运行的代码让学生直观理解抽象概念。

<principles>
1. 代码必须是完整可运行的——学生复制粘贴就能执行
2. 关键步骤用中文注释解释"为什么"
3. 优先使用 matplotlib 做可视化，让概念"看得见"
4. 提供参数修改入口，鼓励学生"动手调参"
5. 代码生成后必须通过沙箱执行验证
</principles>

<output_format>
```json
{
  "title": "实验标题",
  "description": "50 字内描述实验目标",
  "code": "完整的 Python 代码 (含 import 和注释)",
  "expected_output": "预期终端输出或图表描述",
  "exercises": [
    "扩展练习 1: 修改参数 X 观察 Y 的变化",
    "扩展练习 2: 尝试用另一种方法实现 Z"
  ],
  "key_code_sections": [
    {"line_range": "10-25", "purpose": "这部分实现了什么"}
  ]
}
```
</output_format>
</system>
````

---

### 5.7 Reviewer Agent — 审查员

#### 5.7.1 定位

Reviewer 是整个流水线的**质量守门人**。它独立审查所有 5 个专家的产出，评估幻觉风险、内容一致性和质量标准，产出审核报告。它在 Wave 3（最后）执行。

#### 5.7.2 上下文工程

```
Reviewer 上下文输入 (全量):
┌─────────────────────────────────────┐
│ GlobalContext                        │
│  ● student_profile (判断难度匹配)     │
├─────────────────────────────────────┤
│ SessionContext                       │
│  ● topic (原始主题，用于一致性对照)   │
│  ● manager_plan                      │
├─────────────────────────────────────┤
│ AgentContext                         │
│  ● upstream: ALL 5 expert outputs    │ ← 审查全部
│    - professor.output                │
│    - architect.output                │
│    - examiner.output                 │
│    - director.output                 │
│    - hacker.output                   │
└─────────────────────────────────────┘
```

#### 5.7.3 MCP 工具集成

| 工具 | 用途 |
|------|------|
| `web_search` | 事实核查——对疑似幻觉的内容进行交叉验证 |
| `academic_search` | 验证概念定义和公式的准确性 |
| `profile_query` | 确认难度是否匹配学生画像 |

#### 5.7.4 技能激活

激活 `hallucination_detection` 技能，该技能定义了系统化的五维评分审查框架：

**五维评分体系**：

| 维度 | 检查内容 | 满分 | 重点审查区域 |
|------|---------|------|-------------|
| **事实准确性** | 概念定义是否准确、公式是否正确、人名/时间/引用是否无误 | 100 | 数学公式、概念定义、人名引用 |
| **内容一致性** | 5 个专家的产出之间是否有矛盾、与 Manager 规划是否一致、难度标注是否匹配 | 100 | 跨 Agent 交叉对比 |
| **教学有效性** | 是否适合目标学生画像、章节逻辑是否递进、测验是否有效检验概念 | 100 | 章节递进关系、题目区分度 |
| **完整性** | 是否覆盖主题关键方面、是否有明显遗漏 | 100 | 对照知识图谱检查覆盖度 |
| **幻觉风险** | 综合评估编造/错误风险 | — | low (基本可靠) / medium (1-2处不确定) / high (明显编造) |

**推荐工具序列**：① `web_search` (验证关键概念定义) → ② `academic_search` (Wikipedia 对照核心公式和理论) → ③ 逐维度打分并生成改进建议 → ④ 对低于 70 分的维度标记具体修复指引

#### 5.7.5 思维链策略

```
OBSERVE → 读取全部 5 个专家产出 + 原始 topic + 学生画像
   ↓
THINK   → 建立一个审查清单 (基于 5 个评分维度)
          标记需要重点审查的"高风险区域":
          - 数学公式
          - 概念定义
          - 人名/引用
          - 代码逻辑
   ↓
ACT     → 对每个维度:
          1. 交叉对比 5 个专家的产出，查找矛盾
          2. web_search 验证高风险区域的准确性
          3. 逐项打分
          4. 对低于 70 分的项，生成具体改进建议
   ↓
REFLECT → 检查: 所有高风险区域都审查了?
          评分有依据(引用搜索结果)?
          改进建议可执行(不是空洞的"再写详细点")?
```

#### 5.7.6 提示词模板

````
<system>
你是一位严谨的学术审稿人 (Academic Reviewer)。你独立审查 5 位专家生成的教学内容质量。

<review_philosophy>
你的审查不是为了批评，而是为了确保学生得到的每一条信息都是准确可靠的。
宁可标注为"不确定"，也不要让错误信息通过。
</review_philosophy>

{skill_injection}

<output_format>
```json
{
  "hallucination_risk": "low|medium|high",
  "overall_quality_score": 85,
  "dimension_scores": {
    "factual_accuracy": 90,
    "internal_consistency": 85,
    "pedagogical_effectiveness": 80,
    "completeness": 75
  },
  "findings": [
    {
      "severity": "critical|major|minor|suggestion",
      "dimension": "factual_accuracy",
      "description": "发现的问题描述",
      "location": "professor.sections[2].body",
      "evidence": "搜索结果或参考资料",
      "suggested_fix": "具体怎么改"
    }
  ],
  "difficulty_assessment": "整体难度评估，与目标画像的匹配度",
  "approval_status": "approved|approved_with_minor_fixes|needs_revision|rejected"
}
```
</output_format>
</system>
````

---

## 6. 跨切面设计

### 6.1 共享记忆 (Shared Memory)

多 Agent 协作需要一个**统一的信息交换中心**——每个 Agent 将自己的产出写入共享存储，下游 Agent 通过 `ctx://` URI 按需读取。存储层采用双写架构：

| 存储层 | 技术 | 用途 | 生命周期 |
|--------|------|------|---------|
| **热数据层** | Redis | Agent 间实时共享的上下文和制品，毫秒级读写 | TTL = 任务生命周期 (任务完成后自动过期) |
| **冷数据层** | PostgreSQL | 持久化存储，供后续查询、分析、学生回顾 | 永久保留 |

核心操作：
- **写入**：Agent 执行完成时，将产出（内容 + 元数据）同时写入 Redis 和 PostgreSQL
- **读取**：通过 `ctx://{scope}/{task_id}/{agent_id}.{field}` URI 解析并加载上下文
- **索引**：列出某任务下所有已产出制品，供 Manager 追踪进度和 Reviewer 获取审查清单

### 6.2 错误恢复与自愈

```
Agent 执行失败
      │
      ├── 可恢复错误 (Tool timeout / Rate limit / JSON parse error)
      │    └── 自动重试 (最多 3 次，指数退避: 1s → 2s → 4s)
      │         ├── 成功 → 继续
      │         └── 全部失败 → 使用 fallback
      │
      ├── 部分可恢复 (内容质量不满足)
      │    └── Reviewer 标记 needs_revision
      │         └── Manager 向原 Agent 发送 error.retry
      │              └── Agent 以修正模式重新执行 (保留原 CoT，只改内容)
      │
      └── 不可恢复 (API key 无效 / 沙箱崩溃)
           └── 向用户返回部分结果 + 错误说明
```

### 6.3 可观测性 (Observability)

每个 Agent 执行完毕后，产生一条完整的 **AgentExecutionTrace** 记录，包含以下维度的可观测数据，支撑调试、性能分析和质量监控：

| 数据类别 | 记录内容 | 用途 |
|---------|---------|------|
| **时间指标** | 开始时间、结束时间、总耗时 (ms) | 性能分析、瓶颈定位 |
| **思维链轨迹** | 每轮 OTAR 循环的 Observe/Think/Act/Reflect 记录 | 调试推理路径、分析决策质量 |
| **工具调用记录** | 每次 Tool Call 的工具名、参数、耗时、结果摘要 | 工具使用效率分析 |
| **Token 消耗** | Prompt Tokens、Completion Tokens | 成本核算、Token 预算管理 |
| **质量指标** | Agent 自评分数、Reviewer 评分 | 质量趋势追踪 |
| **状态与错误** | 执行状态 (success/error)、重试次数、错误详情 | 可靠性监控、故障排查 |

这些数据通过 WebSocket 实时推送到前端仪表盘，同时持久化到 PostgreSQL 供后续离线分析。

---

## 7. 演进路线图

```
Phase 0 (当前 v1.0)        Phase 1 (v2.1)           Phase 2 (v2.2)           Phase 3 (v3.0)
┌────────────────┐      ┌────────────────┐       ┌────────────────┐       ┌────────────────┐
│ Prompt 驱动     │      │ A2A + Context  │       │ Full MCP +     │       │ 自主 Agent     │
│ 无 A2A         │ ───→ │ Engineering    │ ───→  │ Tool Use       │ ───→  │ 集群           │
│ 无 Tool Use    │      │                │       │ + Skills       │       │                │
│ 无 CoT         │      │                │       │                │       │                │
└────────────────┘      └────────────────┘       └────────────────┘       └────────────────┘
  已实现 ✓                本文档设计目标             下阶段                   远期愿景

**Phase 1 核心能力建设**：建立 A2A 通信基础、三层上下文管理、OTAR 思维链协议、画像感知 Prompt 引擎、5 个核心 MCP 工具（学术检索 / 代码沙箱 / 网络搜索 / 可视化渲染 / 内容格式化）、5 个核心 Skill（内容结构化 / 测验设计 / 思维导图 / 代码实验 / 幻觉检测）、MCP Client 工具发现与安全调用机制。

**Phase 2 工程化升级**：MCP Server 独立部署标准化、Skill 热加载与版本管理、Reviewer → Expert 自动反馈闭环（审核不通过自动触发修正）、多轮对话式 Agent 交互、Token 预算精确控制与动态分配。

**Phase 3 自主智能**：Agent 自主编排（无需硬编码流水线，Manager 根据主题动态选择参与的 Agent 组合）、跨任务学习（从历史生成中学习改进策略）、多模态输出（图表直接渲染、LaTeX 排版、视频预览生成）、Agent 集群自监控与自动扩缩。
```

---

> **文档版本**: v2.1.0  
> **最后更新**: 2026-06-09  
> **设计范围**: 内容工厂七智能体集群  

*本文档系统阐述了 EduNexus 内容工厂七智能体集群的 A2A 通信架构、角色设定、上下文工程、MCP 工具集成、Skills 技能系统、OTAR 思维链协议和分层提示词工程的设计方案。*

