/**
 * Agent 模块结构化日志工具
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  agent: string;
  event: string;
  data?: any;
}

const LOG_PREFIX = '[EduNexus Agents]';

function formatLog(entry: LogEntry): string {
  const ts = new Date().toISOString().substring(11, 23);
  return `${ts} ${entry.level.toUpperCase().padEnd(5)} [${entry.agent}] ${entry.event}`;
}

export function logAgentEvent(agentId: string, event: string, data?: any): void {
  const entry: LogEntry = {
    timestamp: new Date().toISOString(),
    level: 'info',
    agent: agentId,
    event,
    data,
  };
  console.log(`${LOG_PREFIX} ${formatLog(entry)}`, data || '');
}

export function logAgentError(agentId: string, error: string | Error): void {
  const message = error instanceof Error ? error.message : error;
  const entry: LogEntry = {
    timestamp: new Date().toISOString(),
    level: 'error',
    agent: agentId,
    event: message,
  };
  console.error(`${LOG_PREFIX} ${formatLog(entry)}`);
}

export function logCoordinator(event: string, data?: any): void {
  const entry: LogEntry = {
    timestamp: new Date().toISOString(),
    level: 'info',
    agent: 'coordinator',
    event,
    data,
  };
  console.log(`${LOG_PREFIX} ${formatLog(entry)}`, data || '');
}
