// ── 文本聊天 ──

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

// ── AI 搜题（图片解题）──

export interface SolveRequest {
  /** base64 编码的题目图片（可含 data:image/...;base64, 前缀） */
  image_base64: string
  /** 附加文字说明 */
  message?: string
}

export interface SolveStep {
  /** 步骤标题，如 "Step 1：审题与分析" */
  title: string
  /** 步骤内容，每个元素是一行文本 */
  content: string[]
}

export interface SolveResponse {
  /** 解题步骤列表 */
  steps: SolveStep[]
  /** 最终结论总结 */
  summary: string
  /** OCR / 识别出的原始题目文本 */
  raw_text?: string
}

// ── 对话历史 ──

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
