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
    if (nodes.value.length === 0) return []

    // 先检测是否是 AI 专用路径（有 ai- 前缀的节点）
    const isAiPath = nodes.value.some(n => n.id.startsWith('ai-'))

    // 如果不是 AI 路径，全部放在一个阶段
    if (!isAiPath) {
      const standardNodes = nodes.value.filter(n => n.type !== 'milestone')
      if (standardNodes.length === 0) return []

      const getStatus = () => {
        if (standardNodes.some(n => n.status === 'active')) return 'current'
        if (standardNodes.every(n => n.status === 'completed')) return 'completed'
        return 'locked'
      }

      return [{
        id: 'all',
        title: '学习路径',
        description: standardNodes.map(n => n.label).join(' → '),
        status: getStatus(),
        nodes: standardNodes
      }]
    }

    // AI 路径：按阶段分组
    const phase1Nodes: KnowledgeNode[] = []
    const phase2Nodes: KnowledgeNode[] = []
    const phase3Nodes: KnowledgeNode[] = []

    for (const node of nodes.value) {
      if (node.type === 'milestone') continue

      const id = node.id.toLowerCase()

      // 第一阶段：基础（精确匹配 ai- 前缀）
      if (id.includes('ai-math') || id.includes('ai-prog') || id.includes('ai-python') ||
          id.includes('ai-la') || id.includes('ai-calc') || id.includes('ai-stat') || id.includes('ai-libs')) {
        phase1Nodes.push(node)
      }
      // 第二阶段：核心
      else if (id.includes('ai-ml') || id.includes('ai-sup') || id.includes('ai-unsup') ||
               id.includes('ai-dl') || id.includes('ai-frame') || id.includes('ai-cv') ||
               id.includes('ai-nlp') || id.includes('ai-audio')) {
        phase2Nodes.push(node)
      }
      // 第三阶段：前沿
      else if (id.includes('ai-transformer') || id.includes('ai-llm') || id.includes('ai-app') ||
               id.includes('ai-tech') || id.includes('ai-ops') || id.includes('ai-rag') ||
               id.includes('ai-agent') || id.includes('ai-ft') || id.includes('ai-rlhf') ||
               id.includes('ai-quant') || id.includes('ai-mlops')) {
        phase3Nodes.push(node)
      }
    }

    const result: LearningPhase[] = []

    const getStatus = (nodeList: KnowledgeNode[]) => {
      if (nodeList.some(n => n.status === 'active')) return 'current'
      if (nodeList.every(n => n.status === 'completed')) return 'completed'
      return 'locked'
    }

    if (phase1Nodes.length > 0) {
      result.push({
        id: 'phase1',
        title: '第一阶段：基础储备',
        description: phase1Nodes.map(n => n.label).slice(0, 3).join('、') + (phase1Nodes.length > 3 ? '...' : ''),
        status: getStatus(phase1Nodes),
        nodes: phase1Nodes
      })
    }

    if (phase2Nodes.length > 0) {
      result.push({
        id: 'phase2',
        title: '第二阶段：核心模型',
        description: phase2Nodes.map(n => n.label).slice(0, 3).join('、') + (phase2Nodes.length > 3 ? '...' : ''),
        status: getStatus(phase2Nodes),
        nodes: phase2Nodes
      })
    }

    if (phase3Nodes.length > 0) {
      result.push({
        id: 'phase3',
        title: '第三阶段：前沿进阶',
        description: phase3Nodes.map(n => n.label).slice(0, 3).join('、') + (phase3Nodes.length > 3 ? '...' : ''),
        status: getStatus(phase3Nodes),
        nodes: phase3Nodes
      })
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

      // 调试：打印后端返回的节点信息
      console.log("后端返回原始数据:", result.nodes.map(n => ({ id: n.id, label: n.label, type: n.type })))
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
