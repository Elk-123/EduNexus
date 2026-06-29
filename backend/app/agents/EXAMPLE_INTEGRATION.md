# Agent模块使用示例

以下是如何在EduNexus后端系统中使用新创建的Agent模块的示例代码。

## 1. 在后端API中的集成示例

```python
# backend/app/api/v1/factory.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..deps import get_current_user
from ....agents import (
    AgentCoordinator, 
    LangChainUtils, 
    ManagerAgent, 
    ProfessorAgent, 
    ArchitectAgent, 
    ExaminerAgent, 
    DirectorAgent, 
    HackerAgent, 
    ReviewerAgent,
    AgentExecutionResult
)
from ....schemas.factory import GenerateRequest, TaskStatusResponse, ResourceResponse

router = APIRouter(prefix="/factory", tags=["factory"])

# 初始化DeepSeek LangChain模型
LangChainUtils.initialize_model(os.getenv("DEEPSEEK_API_KEY"), "deepseek-chat")

# 创建Agent协调器
agent_coordinator = AgentCoordinator()

# 注册所有Agent
agent_coordinator.register_agent(ManagerAgent())
agent_coordinator.register_agent(ProfessorAgent())
agent_coordinator.register_agent(ArchitectAgent())
agent_coordinator.register_agent(ExaminerAgent())
agent_coordinator.register_agent(DirectorAgent())
agent_coordinator.register_agent(HackerAgent())
agent_coordinator.register_agent(ReviewerAgent())

@router.post("/generate", response_model=TaskStatusResponse)
async def generate_content(request: GenerateRequest, current_user = Depends(get_current_user)):
    """
    生成内容的主接口
    """
    try:
        # 执行Agent流水线
        results = agent_coordinator.execute_pipeline(request.topic)
        
        # 处理结果并保存到数据库
        # 这里可以根据实际需求将结果保存到数据库
        
        # 返回任务状态
        return TaskStatusResponse(
            id="task_" + str(uuid.uuid4()),
            topic=request.topic,
            status="completed",
            agents_status={result.agent_id: result.status.value for result in results}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成内容失败: {str(e)}")

@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str, current_user = Depends(get_current_user)):
    """
    获取任务状态
    """
    # 实现从数据库获取任务状态的逻辑
    pass

@router.get("/resources/{task_id}", response_model=List[ResourceResponse])
async def get_task_resources(task_id: str, current_user = Depends(get_current_user)):
    """
    获取任务资源
    """
    # 实现从数据库获取任务资源的逻辑
    pass
```

## 2. Agent状态管理示例

```python
# backend/app/services/agent_manager.py
from typing import List
from ..agents import AgentStatusInfo, AgentCoordinator

class AgentManager:
    """Agent管理器"""
    
    def __init__(self, coordinator: AgentCoordinator):
        self.coordinator = coordinator
    
    def get_all_agent_statuses(self) -> List[AgentStatusInfo]:
        """获取所有Agent状态"""
        return self.coordinator.get_all_agent_statuses()
    
    def get_agent_status(self, agent_id: str) -> AgentStatusInfo:
        """获取指定Agent状态"""
        return self.coordinator.get_agent_status(agent_id)
    
    def reset_agent_status(self, agent_id: str) -> None:
        """重置Agent状态"""
        # 实现状态重置逻辑
        pass
```

## 3. 集成后的优势

通过集成Agent模块，我们获得了以下增强功能：

1. **更好的结构化输出**：每个Agent专注于特定领域，输出更加专业化
2. **更强的协作能力**：Agent之间可以更好地协作和共享信息
3. **更高的可扩展性**：新增Agent类型非常容易，只需继承BaseAgent
4. **更灵活的任务编排**：通过AgentCoordinator可以灵活地改变执行顺序和流程
5. **更完善的错误处理**：每个Agent都有独立的错误处理和恢复机制
6. **更好的性能控制**：支持超时控制和中断机制

## 4. 配置和部署

为了使Agent模块正常工作，需要在环境变量中添加必要的配置：

```bash
# .env 文件
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-chat
```

然后在项目启动时初始化：

```python
# backend/app/main.py
from app.agents.utils import LangChainUtils

# 初始化DeepSeek LangChain
LangChainUtils.initialize_model(os.getenv("DEEPSEEK_API_KEY"))
```

## 5. WebSocket集成示例

由于EduNexus项目使用WebSocket进行实时通信，我们也可以将Agent执行过程通过WebSocket推送给前端：

```python
# backend/app/core/websocket.py
from typing import Dict, List
from fastapi import WebSocket
from ..agents import AgentExecutionResult, AgentStatus

class AgentWebSocketManager:
    """Agent WebSocket管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, task_id: str, websocket: WebSocket):
        """建立WebSocket连接"""
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        self.active_connections[task_id].append(websocket)
    
    def disconnect(self, task_id: str, websocket: WebSocket):
        """断开WebSocket连接"""
        if task_id in self.active_connections:
            self.active_connections[task_id].remove(websocket)
    
    async def send_agent_status(self, task_id: str, agent_id: str, status: AgentStatus, message: str = ""):
        """发送Agent状态更新"""
        if task_id in self.active_connections:
            for websocket in self.active_connections[task_id]:
                await websocket.send_json({
                    "type": "agent_status",
                    "agent": agent_id,
                    "status": status.value,
                    "message": message
                })
    
    async def send_agent_log(self, task_id: str, agent_id: str, message: str, level: str = "info"):
        """发送Agent日志"""
        if task_id in self.active_connections:
            for websocket in self.active_connections[task_id]:
                await websocket.send_json({
                    "type": "agent_log",
                    "agent": agent_id,
                    "message": message,
                    "type": level
                })
```

## 6. 异步执行支持

考虑到Agent可能需要较长时间执行，我们可以将其设计为异步执行：

```python
# backend/app/services/async_agent_executor.py
import asyncio
from ..agents import AgentCoordinator, AgentExecutionResult

class AsyncAgentExecutor:
    """异步Agent执行器"""
    
    def __init__(self, coordinator: AgentCoordinator):
        self.coordinator = coordinator
    
    async def execute_pipeline_async(self, topic: str, context: dict = None) -> List[AgentExecutionResult]:
        """异步执行Agent流水线"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.coordinator.execute_pipeline, topic, context)
```

这个Agent模块完全独立于现有代码，可以在不影响当前功能的情况下进行集成和测试。它提供了一个即插即用的解决方案，可以轻松集成到任何需要智能内容生成的后端服务中。