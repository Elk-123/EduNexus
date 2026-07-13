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

  /** 阶段标题映射（后端 Prompt 已约定 phase 1/2/3 对应三阶段） */
  const PHASE_LABELS: Record<number, { title: string }> = {
    1: { title: '第一阶段：基础储备' },
    2: { title: '第二阶段：核心掌握' },
    3: { title: '第三阶段：前沿进阶' },
  }

  const phases = computed<LearningPhase[]>(() => {
    if (nodes.value.length === 0) return []

    // 按 node.phase 分组（过滤掉 milestone 节点）
    const phaseMap: Record<number, KnowledgeNode[]> = {}

    for (const node of nodes.value) {
      if (node.type === 'milestone') continue
      const p = node.phase || 1
      if (!phaseMap[p]) phaseMap[p] = []
      phaseMap[p].push(node)
    }

    const phaseNumbers = Object.keys(phaseMap)
      .map(Number)
      .sort((a, b) => a - b)

    if (phaseNumbers.length === 0) return []

    const getStatus = (nodeList: KnowledgeNode[]) => {
      if (nodeList.some(n => n.status === 'active')) return 'current'
      if (nodeList.every(n => n.status === 'completed')) return 'completed'
      return 'locked'
    }

    return phaseNumbers.map(p => ({
      id: `phase${p}`,
      title: PHASE_LABELS[p]?.title || `第${p}阶段`,
      description:
        phaseMap[p]
          .map(n => n.label)
          .slice(0, 3)
          .join('、') + (phaseMap[p].length > 3 ? '...' : ''),
      status: getStatus(phaseMap[p]),
      nodes: phaseMap[p],
    }))
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

      // 调试：打印后端返回的节点信息（含 phase 字段）
      console.log("后端返回原始数据:", result.nodes.map(n => ({ id: n.id, label: n.label, type: n.type, phase: (n as any).phase })))
      console.log("后端返回原始 JSON:", JSON.stringify(result.nodes))
      console.log("后端返回 edges:", result.edges)

      // 默认选中第一个 active 阶段
      const activePhase = phases.value.find((p) => p.status === 'current')
      activePhaseId.value = activePhase?.id || phases.value[0]?.id || ''
      console.log("生成的 phases:", phases.value)
      console.log("选中的 activePhaseId:", activePhaseId.value)
    } catch (e: any) {
      error.value = e?.response?.data?.detail || '学习路径规划失败'
    } finally {
      isPlanning.value = false
    }
  }

  function selectPhase(phaseId: string) {
    const phase = phases.value.find((p) => p.id === phaseId)
    if (phase) {
      activePhaseId.value = phaseId
    }
  }

  return { isPlanning, graphId, title, nodes, edges, analysisSummary, error,
           activePhaseId, phases, currentGraphNodes, plan, selectPhase }
})
