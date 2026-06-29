/**
 * Agent基类抽象定义
 */
import { AgentConfig, AgentContext, AgentExecutionResult, AgentStatus, AgentStatusValue } from '../types';

export abstract class BaseAgent {
  public readonly config: AgentConfig;
  public readonly systemPrompt: string;

  /** 内部状态追踪 */
  protected _state: AgentStatus = {
    agentId: '',
    status: AgentStatusValue.IDLE,
    lastUpdated: new Date(),
    successCount: 0,
    failureCount: 0,
  };

  /** 取消控制器 */
  protected _abortController: AbortController = new AbortController();

  constructor(config: AgentConfig) {
    this.config = config;
    this._state.agentId = config.id;
    this.systemPrompt = this._buildSystemPrompt();
  }

  // ── 公共接口 ─────────────────────────────────────────────

  getConfig(): AgentConfig {
    return this.config;
  }

  getSystemPrompt(): string {
    return this.systemPrompt;
  }

  abstract execute(context: AgentContext): Promise<AgentExecutionResult>;

  getStatus(): AgentStatus {
    return { ...this._state, lastUpdated: new Date() };
  }

  interrupt(): void {
    this._abortController.abort();
    this._state.status = AgentStatusValue.IDLE;
  }

  get isStopped(): boolean {
    return this._abortController.signal.aborted;
  }

  // ── 内部方法 ─────────────────────────────────────────────

  protected _recordSuccess(task?: string): void {
    this._state.successCount++;
    this._state.status = AgentStatusValue.IDLE;
    this._state.lastUpdated = new Date();
    if (task) this._state.currentTask = task;
  }

  protected _recordFailure(task?: string): void {
    this._state.failureCount++;
    this._state.status = AgentStatusValue.ERROR;
    this._state.lastUpdated = new Date();
    if (task) this._state.currentTask = task;
  }

  protected _buildSystemPrompt(): string {
    return (
      `You are a ${this.config.role} agent. ` +
      `ALWAYS output thought process in <thought> tags BEFORE any tool call or final answer.\n` +
      `Example: <thought>Need to search for academic papers on {topic}</thought>`
    );
  }
}
