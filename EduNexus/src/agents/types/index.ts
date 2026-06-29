/**
 * Agent模块类型定义
 */

// ─── Status Constants ───────────────────────────────────────────

/** Agent 运行时状态 */
export const AgentStatusValue = {
  IDLE: 'idle',
  RUNNING: 'running',
  SUCCESS: 'success',
  ERROR: 'error',
} as const;
export type AgentStatusValue = (typeof AgentStatusValue)[keyof typeof AgentStatusValue];

/** Agent 执行结果状态 */
export const ExecutionStatus = {
  SUCCESS: 'success',
  FAILED: 'failed',
  ERROR: 'error',
  TIMEOUT: 'timeout',
} as const;
export type ExecutionStatus = (typeof ExecutionStatus)[keyof typeof ExecutionStatus];

// ─── Interfaces ─────────────────────────────────────────────────

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
  timeout: number;  // 改为 required，默认 30000
}

export interface AgentContext {
  /** 当前任务ID */
  taskId: string;
  /** 当前话题 */
  topic: string;
  /** 当前上下文数据（累积上游 Agent 输出） */
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
  status: ExecutionStatus;
  /** 结果 */
  result?: AgentResult;
  /** 错误信息 */
  error?: string;
  /** 执行耗时（毫秒） */
  duration: number;
}

export interface AgentStatus {
  /** Agent ID */
  agentId: string;
  /** 运行时状态 */
  status: AgentStatusValue;
  /** 最后更新时间 */
  lastUpdated: Date;
  /** 当前任务 */
  currentTask?: string;
  /** 成功次数 */
  successCount: number;
  /** 失败次数 */
  failureCount: number;
}
