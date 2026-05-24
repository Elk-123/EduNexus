/**
 * Agent协调器 - 负责管理所有Agent的执行流程
 */
import { AgentConfig, AgentContext, AgentExecutionResult, AgentStatus } from '../types';
import { BaseAgent } from '../base/BaseAgent';

export class AgentCoordinator {
  private agents: Map<string, BaseAgent> = new Map();
  private agentStates: Map<string, AgentStatus> = new Map();

  /**
   * 注册Agent
   */
  registerAgent(agent: BaseAgent): void {
    const config = agent.getConfig();
    this.agents.set(config.id, agent);
    this.agentStates.set(config.id, {
      agentId: config.id,
      status: 'idle',
      lastUpdated: new Date(),
      successCount: 0,
      failureCount: 0
    });
  }

  /**
   * 执行Agent流水线
   */
  async executePipeline(topic: string, context?: Record<string, any>): Promise<AgentExecutionResult[]> {
    const results: AgentExecutionResult[] = [];
    const executionContext: AgentContext = {
      taskId: this.generateTaskId(),
      topic,
      context
    };

    // 按照特定顺序执行Agent
    const agentIds = ['manager', 'professor', 'architect', 'examiner', 'director', 'hacker', 'reviewer'];

    for (const agentId of agentIds) {
      const agent = this.agents.get(agentId);
      if (!agent) {
        console.warn(`Agent ${agentId} not found`);
        continue;
      }

      try {
        // 更新Agent状态
        this.updateAgentStatus(agentId, 'running');

        const startTime = Date.now();
        const result = await agent.execute(executionContext);
        const endTime = Date.now();

        result.duration = endTime - startTime;

        results.push(result);

        // 更新成功计数
        if (result.status === 'success') {
          this.incrementSuccessCount(agentId);
        } else {
          this.incrementFailureCount(agentId);
        }

        // 更新Agent状态
        this.updateAgentStatus(agentId, result.status === 'success' ? 'success' : 'error');

      } catch (error) {
        console.error(`Error executing agent ${agentId}:`, error);
        this.updateAgentStatus(agentId, 'error');
        results.push({
          agentId,
          status: 'failed',
          error: error instanceof Error ? error.message : String(error),
          duration: 0
        });
      }
    }

    return results;
  }

  /**
   * 获取Agent状态
   */
  getAgentStatus(agentId: string): AgentStatus | undefined {
    return this.agentStates.get(agentId);
  }

  /**
   * 获取所有Agent状态
   */
  getAllAgentStatuses(): AgentStatus[] {
    return Array.from(this.agentStates.values());
  }

  /**
   * 更新Agent状态
   */
  private updateAgentStatus(agentId: string, status: AgentStatus['status']): void {
    const agentStatus = this.agentStates.get(agentId);
    if (agentStatus) {
      agentStatus.status = status;
      agentStatus.lastUpdated = new Date();
    }
  }

  /**
   * 增加成功计数
   */
  private incrementSuccessCount(agentId: string): void {
    const agentStatus = this.agentStates.get(agentId);
    if (agentStatus) {
      agentStatus.successCount++;
    }
  }

  /**
   * 增加失败计数
   */
  private incrementFailureCount(agentId: string): void {
    const agentStatus = this.agentStates.get(agentId);
    if (agentStatus) {
      agentStatus.failureCount++;
    }
  }

  /**
   * 生成任务ID
   */
  private generateTaskId(): string {
    return `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}