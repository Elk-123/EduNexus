import apiClient from './client'
import type { GenerateRequest, TaskStatusResponse, GeneratedResource, AgentChatRequest, AgentChatResponse } from '@/types/factory'

export async function generateContent(payload: GenerateRequest): Promise<{ task_id: string; status: string }> {
  const { data } = await apiClient.post('/factory/generate', payload)
  return data
}

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
