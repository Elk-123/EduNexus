export interface WeeklyReport {
  study_hours: number
  completed_courses: number
  average_score: number
  knowledge_mastery: number
  week_start: string
  week_end: string
}

export interface StatsData {
  subjects: string[]
  scores: number[]
  trend: Array<[string, number]>
}

export interface HistoryRecord {
  id: string
  title: string
  type: string
  completed_at: string
  score: number
  duration: string
}