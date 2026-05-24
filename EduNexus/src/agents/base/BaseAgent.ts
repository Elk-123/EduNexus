/**
 * Agent基类抽象定义
 */
import { AgentConfig, AgentContext, AgentResult, AgentExecutionResult } from './index';

export abstract class BaseAgent {
  protected config: AgentConfig;

  constructor(config: AgentConfig) {
    this.config = config;
  }

  /**
   * 获取Agent配置
   */
  getConfig(): AgentConfig {
    return this.config;
  }

  /**
   * 执行Agent任务
   */
  abstract execute(context: AgentContext): Promise<AgentExecutionResult>;

  /**
   * 获取Agent状态
   */
  abstract getStatus(): Promise<AgentStatus>;

  /**
   * 中断Agent执行
   */
  abstract interrupt(): void;
}