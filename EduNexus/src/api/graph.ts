import apiClient from './client'
import type { PathPlanRequest, PathPlanResponse, KnowledgeGraphData } from '@/types/graph'

export async function planPath(payload: PathPlanRequest): Promise<PathPlanResponse> {
  const { data } = await apiClient.post('/graph/plan', payload)
  return data
}

export async function getGraph(courseId: string): Promise<KnowledgeGraphData> {
  const { data } = await apiClient.get(`/graph/${courseId}`)
  return data
}

export async function getPersonalizedPath(studentId: string): Promise<KnowledgeGraphData> {
  const { data } = await apiClient.get(`/graph/path/${studentId}`)
  return data
}

export async function getNodeResources(nodeId: string): Promise<{ node_id: string; resources: any[] }> {
  const { data } = await apiClient.get(`/graph/node/${nodeId}/resources`)
  return data
}
