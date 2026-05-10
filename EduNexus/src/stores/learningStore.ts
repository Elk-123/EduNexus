import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { planPath } from '@/api/graph'
import type { KnowledgeNode, KnowledgeEdge } from '@/types/graph'

export interface LearningPhase {
  id: string
  title: string
  description: string
  status: 'completed' | 'current' | 'locked'
  nodes: KnowledgeNode[]
}

export const useLearningStore = defineStore('learning', () => {
  const isPlanning = ref(false)
  const graphId = ref<string | null>(null)
  const title = ref('')
  const nodes = ref<KnowledgeNode[]>([])
  const edges = ref<KnowledgeEdge[]>([])
  const analysisSummary = ref('')
  const error = ref<string | null>(null)
  const activePhaseId = ref<string>('')

  const phases = computed<LearningPhase[]>(() => {
    const phaseMap = new Map<string, KnowledgeNode[]>()

    // 简单分组：按 status 字段聚类
    for (const node of nodes.value) {
      const key = node.status
      if (!phaseMap.has(key)) phaseMap.set(key, [])
      phaseMap.get(key)!.push(node)
    }

    const result: LearningPhase[] = []
    let idx = 1
    const statusOrder: Array<'completed' | 'active' | 'pending'> = ['completed', 'active', 'pending']
    const statusLabels: Record<string, string> = {
      completed: '已完成阶段',
      active: '当前学习阶段',
      pending: '待解锁阶段',
    }

    for (const status of statusOrder) {
      const group = phaseMap.get(status)
      if (group && group.length > 0) {
        result.push({
          id: `p${idx}`,
          title: `${statusLabels[status]} (${group.length} 个知识点)`,
          description: group.map((n) => n.label).join('、'),
          status: status === 'completed' ? 'completed' : status === 'active' ? 'current' : 'locked',
          nodes: group,
        })
        idx++
      }
    }
    return result
  })

  const currentGraphNodes = computed(() => {
    const phase = phases.value.find((p) => p.id === activePhaseId.value)
    return phase?.nodes || nodes.value
  })

  async function plan(goal: string) {
    isPlanning.value = true
    error.value = null
    try {
      const result = await planPath({ goal })
      graphId.value = result.graph_id
      title.value = result.title
      nodes.value = result.nodes
      edges.value = result.edges
      analysisSummary.value = result.analysis_summary

      // 默认选中第一个 active 阶段
      const activePhase = phases.value.find((p) => p.status === 'current')
      activePhaseId.value = activePhase?.id || phases.value[0]?.id || ''
    } catch (e: any) {
      error.value = e?.response?.data?.detail || '学习路径规划失败'
    } finally {
      isPlanning.value = false
    }
  }

  function selectPhase(phaseId: string) {
    const phase = phases.value.find((p) => p.id === phaseId)
    if (phase && phase.status !== 'locked') {
      activePhaseId.value = phaseId
    }
  }

  return { isPlanning, graphId, title, nodes, edges, analysisSummary, error,
           activePhaseId, phases, currentGraphNodes, plan, selectPhase }
})
