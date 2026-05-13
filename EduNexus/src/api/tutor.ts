import apiClient from './client'
import type { ChatRequest, ChatResponse, ConversationHistory } from '@/types/tutor'

export async function askQuestion(payload: ChatRequest): Promise<ChatResponse> {
  const { data } = await apiClient.post<ChatResponse>('/tutor/chat', payload)
  return data
}

export async function getConversationHistory(limit: number = 10): Promise<ConversationHistory[]> {
  const { data } = await apiClient.get<ConversationHistory[]>(`/tutor/history?limit=${limit}`)
  return data
}