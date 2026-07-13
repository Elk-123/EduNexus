export interface GenerateRequest {
  topic: string
}

export interface TaskStatusResponse {
  id: string
  topic: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  agents_status: Record<string, string>
  created_at: string
}

export interface GeneratedResource {
  id: string
  task_id: string
  agent_type: string
  resource_type: 'document' | 'mindmap' | 'quiz' | 'video_script' | 'code_lab' | 'review_report'
  content: Record<string, any>
  status: string
}

export interface AgentChatRequest {
  message: string
  task_id?: string  // 关联的 pipeline 任务ID，用于后端加载该 agent 的已生成内容
  context?: string  // 前端传递的上下文（v2 pipeline 或自定义上下文文本）
}

export interface AgentChatResponse {
  reply: string
  agent_type: string
}

export interface AgentLogEntry {
  type: string
  agent: string
  message: string
  timestamp: string
}
