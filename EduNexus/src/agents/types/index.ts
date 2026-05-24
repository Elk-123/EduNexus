/**
 * Agent模块类型定义
 */

export interface AgentConfig {
  /** Agent唯一标识符 */
  id: string;
  /** Agent名称 */
  name: string;
  /** Agent角色描述 */
  role: string;
  /** Agent能力描述 */
  capabilities: string[];
  /** Agent执行超时时间（毫秒） */
  timeout?: number;
}

export interface AgentContext {
  /** 当前任务ID */
  taskId: string;
  /** 当前话题 */
  topic: string;
  /** 当前上下文数据 */
  context?: Record<string, any>;
  /** 用户输入 */
  userInput?: string;
}

export interface AgentResult {
  /** 生成的内容 */
  content: any;
  /** 生成的类型 */
  type: string;
  /** 生成时间 */
  timestamp: Date;
  /** 生成质量评分 */
  qualityScore?: number;
  /** 生成过程日志 */
  log?: string[];
}

export interface AgentExecutionResult {
  /** Agent ID */
  agentId: string;
  /** 执行状态 */
  status: 'success' | 'failed' | 'timeout';
  /** 结果 */
  result?: AgentResult;
  /** 错误信息 */
  error?: string;
  /** 执行耗时 */
  duration: number;
}

export interface AgentStatus {
  /** Agent ID */
  agentId: string;
  /** 状态 */
  status: 'idle' | 'running' | 'success' | 'error';
  /** 最后更新时间 */
  lastUpdated: Date;
  /** 当前任务 */
  currentTask?: string;
  /** 成功次数 */
  successCount: number;
  /** 失败次数 */
  failureCount: number;
}