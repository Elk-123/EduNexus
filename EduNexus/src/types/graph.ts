export interface KnowledgeNode {
  phase: number
  id: string
  label: string
  type: 'standard' | 'injected' | 'milestone'
  proficiency: number
  status: 'completed' | 'active' | 'pending'
}

export interface KnowledgeEdge {
  from: string
  to: string
  isDynamic?: boolean
}

export interface PathPlanRequest {
  goal: string
}

export interface PathPlanResponse {
  graph_id: string
  title: string
  nodes: KnowledgeNode[]
  edges: KnowledgeEdge[]
  analysis_summary: string
}

export interface KnowledgeGraphData {
  id: string
  course_id: string | null
  title: string
  nodes: KnowledgeNode[]
  edges: KnowledgeEdge[]
  version: number
}
