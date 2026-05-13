import apiClient from './client'
import type { WeeklyReport, StatsData, HistoryRecord } from '@/types/assessment'

export async function getWeeklyReport(): Promise<WeeklyReport> {
  const { data } = await apiClient.get<WeeklyReport>('/assessment/weekly')
  return data
}

export async function getLearningStats(): Promise<StatsData> {
  const { data } = await apiClient.get<StatsData>('/assessment/stats')
  return data
}

export async function getHistory(limit: number = 10): Promise<HistoryRecord[]> {
  const { data } = await apiClient.get<HistoryRecord[]>(`/assessment/history?limit=${limit}`)
  return data
}