export interface ChatRequest {
  message: string
  context?: string
}

export interface ChatResponse {
  reply: string
  message_id: string
  agent_type: string
  timestamp: string
}

export interface Message {
  id: string
  content: string
  role: 'user' | 'ai'
  timestamp: string
  agent_type?: string
}

export interface ConversationHistory {
  id: string
  topic: string
  preview: string
  timestamp: string
  message_count: number
}