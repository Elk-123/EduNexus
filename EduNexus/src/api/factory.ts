import apiClient from './client'
import type { GenerateRequest, TaskStatusResponse, GeneratedResource, AgentChatRequest, AgentChatResponse } from '@/types/factory'

// ═══════════════════════════════════════════════════════════════
//  [已注释] v1.0 API 调用 — 保留兼容
// ═══════════════════════════════════════════════════════════════
// export async function generateContent(payload: GenerateRequest): Promise<{ task_id: string; status: string }> {
//   const { data } = await apiClient.post('/factory/generate', payload)
//   return data
// }

export async function getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
  const { data } = await apiClient.get(`/factory/status/${taskId}`)
  return data
}

export async function getTaskResources(taskId: string): Promise<GeneratedResource[]> {
  const { data } = await apiClient.get(`/factory/resources/${taskId}`)
  return data
}

export async function chatWithAgent(agentId: string, payload: AgentChatRequest): Promise<AgentChatResponse> {
  const { data } = await apiClient.post(`/factory/agent/${agentId}/chat`, payload)
  return data
}

// ═══════════════════════════════════════════════════════════════
//  v2.0 API — 使用 agents/ 文件夹的新实现
// ═══════════════════════════════════════════════════════════════

export interface V2GenerateResponse {
  task_id: string
  topic: string
  status: string
  message: string
}

export interface V2AgentResult {
  agent_id: string
  status: string
  duration: number
  error?: string
}

export interface V2PipelineResult {
  type: 'v2_result'
  results: V2AgentResult[]
  accumulated_context: Record<string, any>
  markdown_report: string
  timestamp: string
}

/** 调用后端 v2.0 Agent 管道 */
export async function generateV2(topic: string): Promise<V2GenerateResponse> {
  const { data } = await apiClient.post('/factory/generate-v2', { topic })
  return data
}
