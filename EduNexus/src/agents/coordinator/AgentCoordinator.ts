/**
 * Agent协调器 - 负责管理所有Agent的执行流程，支持上下文累积传递
 */
import { AgentContext, AgentExecutionResult, AgentStatus, AgentStatusValue, ExecutionStatus } from '../types';
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
      status: AgentStatusValue.IDLE,
      lastUpdated: new Date(),
      successCount: 0,
      failureCount: 0
    });
    console.log(`[AgentCoordinator] Registered agent: ${config.id} (${config.name})`);
  }

  /**
   * 执行Agent流水线（异步），支持上下文累积
   *
   * 每个Agent成功后，其输出被累积到 executionContext.context，
   * 下游Agent可以引用上游的输出。
   *
   * @returns { results, accumulatedContext, taskId }
   */
  async executePipeline(
    topic: string,
    initialContext?: Record<string, any>
  ): Promise<{
    results: AgentExecutionResult[];
    accumulatedContext: Record<string, any>;
    taskId: string;
  }> {
    const results: AgentExecutionResult[] = [];
    const taskId = this.generateTaskId();

    // 累积上下文：key=agentId, value=该Agent产出的content
    const accumulated: Record<string, any> = initialContext ? { ...initialContext } : {};

    const executionContext: AgentContext = {
      taskId,
      topic,
      context: accumulated
    };

    // 按照特定顺序执行Agent
    const agentIds = ['manager', 'professor', 'architect', 'examiner', 'director', 'hacker', 'reviewer'];

    for (const agentId of agentIds) {
      const agent = this.agents.get(agentId);
      if (!agent) {
        console.warn(`[AgentCoordinator] Agent ${agentId} not registered, skipping`);
        continue;
      }

      try {
        this.updateAgentStatus(agentId, AgentStatusValue.RUNNING);

        const startTime = Date.now();
        const result = await agent.execute(executionContext);
        const endTime = Date.now();

        // 使用协调器测量的墙钟时间（毫秒）
        result.duration = endTime - startTime;
        results.push(result);

        // 更新状态
        if (result.status === ExecutionStatus.SUCCESS) {
          this.incrementSuccessCount(agentId);
          // ★ 核心：将成功Agent的输出累积到上下文
          if (result.result?.content) {
            accumulated[agentId] = result.result.content;
            executionContext.context = { ...accumulated };
          }
        } else {
          this.incrementFailureCount(agentId);
        }

        this.updateAgentStatus(
          agentId,
          result.status === ExecutionStatus.SUCCESS ? AgentStatusValue.SUCCESS : AgentStatusValue.ERROR
        );

        console.log(
          `[AgentCoordinator] Agent ${agentId} completed: status=${result.status} duration=${result.duration}ms`
        );

      } catch (error) {
        console.error(`[AgentCoordinator] Error executing agent ${agentId}:`, error);
        this.updateAgentStatus(agentId, AgentStatusValue.ERROR);
        results.push({
          agentId,
          status: ExecutionStatus.ERROR,
          error: error instanceof Error ? error.message : String(error),
          duration: 0
        });
      }
    }

    return { results, accumulatedContext: accumulated, taskId };
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
  private updateAgentStatus(agentId: string, status: AgentStatusValue): void {
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
    return `task_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
  }
}
