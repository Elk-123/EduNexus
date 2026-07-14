import apiClient from './client'
import type {
  ChatRequest, ChatResponse, ConversationHistory,
  SolveRequest, SolveResponse,
} from '@/types/tutor'

// ── 文本聊天 ──

export async function askQuestion(payload: ChatRequest): Promise<ChatResponse> {
  const { data } = await apiClient.post<ChatResponse>('/tutor/chat', payload)
  return data
}

// ── AI 搜题（图片解题）──

export async function solveProblem(payload: SolveRequest): Promise<SolveResponse> {
  const { data } = await apiClient.post<SolveResponse>('/tutor/solve', payload)
  return data
}

// ── 对话历史 ──

export async function getConversationHistory(limit: number = 10): Promise<ConversationHistory[]> {
  const { data } = await apiClient.get<ConversationHistory[]>(`/tutor/history?limit=${limit}`)
  return data
}
