import apiClient from './client'
import type { TodayResource, ResourceProgress, TrendingItem, ResourceDetail } from '@/types/resources'

export async function getTodayResources(): Promise<TodayResource[]> {
  const { data } = await apiClient.get('/resources/today')
  return data
}

export async function getResourceDetail(resourceId: string): Promise<ResourceDetail> {
  const { data } = await apiClient.get(`/resources/${resourceId}`)
  return data
}

export async function updateProgress(resourceId: string, payload: ResourceProgress): Promise<void> {
  await apiClient.put(`/resources/${resourceId}/progress`, payload)
}

export async function getTrending(): Promise<TrendingItem[]> {
  const { data } = await apiClient.get('/resources/trending')
  return data
}
