# EduNexus Agent模块技术文档

## 概述

本模块是EduNexus平台的后端Agent化核心组件，基于Python和LangChain框架实现，将原有的基于Prompt驱动的内容生成系统升级为具备自主决策、协同工作的智能体系统。

## 模块结构

```
backend/app/agents/
├── base/                 # 基础抽象类
│   └── BaseAgent.py      # Agent基类
├── coordinator/          # Agent协调器
│   └── AgentCoordinator.py # Agent协调与流程管理
├── implementations/      # 具体Agent实现
│   ├── ManagerAgent.py   # 主控中枢
│   ├── ProfessorAgent.py # 教授智能体
│   ├── ArchitectAgent.py # 架构师智能体
│   ├── ExaminerAgent.py  # 考官智能体
│   ├── DirectorAgent.py  # 导演智能体
│   ├── HackerAgent.py    # 极客智能体
│   └── ReviewerAgent.py  # 质量审查
├── types/                # 类型定义
│   └── __init__.py       # 所有类型定义
└── utils/                # 工具类
    └── LangChainUtils.py # LangChain集成工具
```

## 核心组件介绍

### 1. BaseAgent 抽象类
所有Agent都继承自BaseAgent抽象类，提供了统一的接口定义和基础功能。

### 2. AgentCoordinator 协调器
负责管理7个智能体的执行流程，协调它们之间的协作关系，确保任务按正确的顺序执行。

### 3. 7个具体智能体实现

#### ManagerAgent (主控中枢)
- 负责任务规划和流程协调
- 将复杂主题分解为子任务
- 确定各智能体的执行顺序

#### ProfessorAgent (教授智能体)
- 生成学术性的、结构化的教学内容
- 输出章节式的详细内容
- 提供关键概念解释

#### ArchitectAgent (架构师智能体)
- 生成思维导图和知识结构图
- 构建知识的层级关系
- 提供可视化结构

#### ExaminerAgent (考官智能体)
- 生成测验题目和评估材料
- 设计选择题和简答题
- 提供考试评估标准

#### DirectorAgent (导演智能体)
- 生成视频脚本和多媒体内容
- 设计视频场景和旁白
- 提供制作指导

#### HackerAgent (极客智能体)
- 生成代码示例和编程练习
- 提供可运行的代码片段
- 设计编程练习题目

#### ReviewerAgent (质量审查)
- 对所有生成内容进行质量审查
- 评估内容准确性和完整性
- 提供改进建议

### 4. LangChainUtils 工具类
封装了LangChain的核心功能，包括模型初始化、提示模板创建和链式调用执行。

## 使用方法

### 1. 初始化LangChain模型
```python
from app.agents.utils import LangChainUtils

# 初始化DeepSeek模型
LangChainUtils.initialize_model('YOUR_DEEPSEEK_API_KEY', 'deepseek-chat')
```

### 2. 创建并注册Agent
```python
from app.agents import (
    AgentCoordinator, 
    ManagerAgent, 
    ProfessorAgent, 
    ArchitectAgent, 
    ExaminerAgent, 
    DirectorAgent, 
    HackerAgent, 
    ReviewerAgent
)

# 创建Agent协调器
coordinator = AgentCoordinator()

# 创建并注册各个Agent
coordinator.register_agent(ManagerAgent())
coordinator.register_agent(ProfessorAgent())
coordinator.register_agent(ArchitectAgent())
coordinator.register_agent(ExaminerAgent())
coordinator.register_agent(DirectorAgent())
coordinator.register_agent(HackerAgent())
coordinator.register_agent(ReviewerAgent())
```

### 3. 执行Agent流水线
```python
# 执行内容生成流水线
results = coordinator.execute_pipeline('Transformer架构中的注意机制')

# 处理结果
for result in results:
    print(f"Agent {result.agent_id} finished with status: {result.status}")
    if result.result:
        print('Generated content:', result.result.content)
```

## 特性

1. **模块化设计**：每个Agent职责单一，易于维护和扩展
2. **流程可控**：通过协调器管理执行顺序和依赖关系
3. **LangChain集成**：利用LangChain的强大功能实现智能推理
4. **状态跟踪**：提供完整的Agent状态监控和统计
5. **错误处理**：完善的异常处理和恢复机制
6. **性能优化**：支持超时控制和中断机制

## 配置说明

每个Agent都可以通过配置对象自定义行为：
- `id`: Agent唯一标识符
- `name`: Agent显示名称
- `role`: Agent角色描述
- `capabilities`: Agent能力列表
- `timeout`: 执行超时时间（毫秒）

## 集成建议

此模块可无缝集成到现有的EduNexus后端系统中，在内容生成API端点中调用，实现更智能的内容生成流程。

### 示例API集成

```python
# 在FastAPI路由中使用
from fastapi import APIRouter
from app.agents import AgentCoordinator, LangChainUtils

router = APIRouter(prefix="/agents", tags=["agents"])

# 初始化LangChain
LangChainUtils.initialize_model(os.getenv("DEEPSEEK_API_KEY"))

# 创建协调器
agent_coordinator = AgentCoordinator()
# 注册所有Agent...
```