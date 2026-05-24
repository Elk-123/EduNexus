"""
Agent协调器 - 负责管理所有Agent的执行流程
"""
import uuid
from typing import List, Dict, Any
from . import (
    AgentConfig, AgentContext, AgentExecutionResult, AgentStatusInfo,
    AgentStatus, AgentType
)
from ..base.BaseAgent import BaseAgent

class AgentCoordinator:
    """Agent协调器"""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_states: Dict[str, AgentStatusInfo] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """注册Agent"""
        config = agent.get_config()
        self.agents[config.id] = agent
        self.agent_states[config.id] = AgentStatusInfo(
            agent_id=config.id,
            status=AgentStatus.IDLE,
            last_updated=datetime.now(),
            success_count=0,
            failure_count=0
        )

    def execute_pipeline(self, topic: str, context: Dict[str, Any] = None) -> List[AgentExecutionResult]:
        """执行Agent流水线"""
        results: List[AgentExecutionResult] = []
        execution_context = AgentContext(
            task_id=self._generate_task_id(),
            topic=topic,
            context=context
        )

        # 按照特定顺序执行Agent
        agent_order = [
            AgentType.MANAGER,
            AgentType.PROFESSOR,
            AgentType.ARCHITECT,
            AgentType.EXAMINER,
            AgentType.DIRECTOR,
            AgentType.HACKER,
            AgentType.REVIEWER
        ]

        for agent_type in agent_order:
            agent = self.agents.get(agent_type.value)
            if not agent:
                print(f"Agent {agent_type.value} not found")
                continue

            try:
                # 更新Agent状态
                self._update_agent_status(agent_type.value, AgentStatus.RUNNING)

                start_time = datetime.now()
                result = agent.execute(execution_context)
                end_time = datetime.now()

                result.duration = int((end_time - start_time).total_seconds() * 1000)

                results.append(result)

                # 更新成功/失败计数
                if result.status == AgentStatus.SUCCESS:
                    self._increment_success_count(agent_type.value)
                else:
                    self._increment_failure_count(agent_type.value)

                # 更新Agent状态
                self._update_agent_status(agent_type.value, result.status)

            except Exception as error:
                print(f"Error executing agent {agent_type.value}: {error}")
                self._update_agent_status(agent_type.value, AgentStatus.ERROR)
                results.append(AgentExecutionResult(
                    agent_id=agent_type.value,
                    status=AgentStatus.ERROR,
                    error=str(error),
                    duration=0
                ))

        return results

    def get_agent_status(self, agent_id: str) -> AgentStatusInfo:
        """获取Agent状态"""
        return self.agent_states.get(agent_id)

    def get_all_agent_statuses(self) -> List[AgentStatusInfo]:
        """获取所有Agent状态"""
        return list(self.agent_states.values())

    def _update_agent_status(self, agent_id: str, status: AgentStatus) -> None:
        """更新Agent状态"""
        agent_status = self.agent_states.get(agent_id)
        if agent_status:
            agent_status.status = status
            agent_status.last_updated = datetime.now()

    def _increment_success_count(self, agent_id: str) -> None:
        """增加成功计数"""
        agent_status = self.agent_states.get(agent_id)
        if agent_status:
            agent_status.success_count += 1

    def _increment_failure_count(self, agent_id: str) -> None:
        """增加失败计数"""
        agent_status = self.agent_states.get(agent_id)
        if agent_status:
            agent_status.failure_count += 1

    def _generate_task_id(self) -> str:
        """生成任务ID"""
        return f"task_{uuid.uuid4().hex[:12]}"