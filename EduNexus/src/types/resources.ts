export interface TodayResource {
  id: string
  resource_type: 'video' | 'document' | 'code' | 'quiz'
  title: string
  description: string
  status: 'completed' | 'current' | 'locked'
  ai_reason?: string
  duration: string
  url?: string  // 点击跳转链接
}

export interface ResourceProgress {
  status: string
  progress_percentage: number
  time_spent: number
}

export interface TrendingItem {
  source: string
  title: string
  meta: string
  tag: string
  url: string  // 点击跳转链接
}

export interface ResourceDetail {
  id: string
  agent_type: string
  resource_type: string
  content: Record<string, any>
  status: string
}
