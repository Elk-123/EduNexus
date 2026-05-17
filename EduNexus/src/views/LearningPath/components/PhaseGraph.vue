<script setup lang="ts">
import type { KnowledgeNode, KnowledgeEdge } from '@/types/graph'

const props = defineProps<{
  nodes: KnowledgeNode[]
  edges: KnowledgeEdge[]
}>()

// 按阶段分组节点
const nodesByPhase = computed(() => {
  const result = {
    phase1: [] as KnowledgeNode[],
    phase2: [] as KnowledgeNode[],
    phase3: [] as KnowledgeNode[]
  }

  props.nodes.forEach(node => {
    if (node.type === 'milestone') return

    if (node.id.includes('math') || node.id.includes('python') ||
        node.id.includes('ai-math') || node.id.includes('ai-prog') ||
        node.id.includes('ai-la') || node.id.includes('ai-calc') ||
        node.id.includes('ai-stat') || node.id.includes('ai-python') ||
        node.id.includes('ai-libs')) {
      result.phase1.push(node)
    } else if (node.id.includes('ml') || node.id.includes('cv') ||
               node.id.includes('nlp') || node.id.includes('audio') ||
               node.id.includes('ai-ml') || node.id.includes('ai-sup') ||
               node.id.includes('ai-unsup') || node.id.includes('ai-dl') ||
               node.id.includes('ai-frame') || node.id.includes('ai-cv') ||
               node.id.includes('ai-nlp') || node.id.includes('ai-audio')) {
      result.phase2.push(node)
    } else if (node.id.includes('transformer') || node.id.includes('llm') ||
               node.id.includes('app') || node.id.includes('tech') ||
               node.id.includes('ops') || node.id.includes('rag') ||
               node.id.includes('agent') || node.id.includes('ft') ||
               node.id.includes('rlhf') || node.id.includes('quant') ||
               node.id.includes('mlops') ||
               node.id.includes('ai-transformer') || node.id.includes('ai-llm') ||
               node.id.includes('ai-app') || node.id.includes('ai-tech') ||
               node.id.includes('ai-ops') || node.id.includes('ai-rag') ||
               node.id.includes('ai-agent') || node.id.includes('ai-ft') ||
               node.id.includes('ai-rlhf') || node.id.includes('ai-quant') ||
               node.id.includes('ai-mlops')) {
      result.phase3.push(node)
    }
  })

  return result
})

// 计算节点位置
const getNodePosition = (node: KnowledgeNode, index: number, total: number, phase: number) => {
  const ySpacing = 60
  const startY = 100
  const y = startY + index * ySpacing

  return { x: 400, y }
}

// 渲染flowchart
const renderFlowchart = () => {
  const phases = []

  // 第一阶段
  if (nodesByPhase.value.phase1.length > 0) {
    phases.push({
      title: '第一阶段：基础储备',
      nodes: nodesByPhase.value.phase1,
      y: 100
    })
  }

  // 第二阶段
  if (nodesByPhase.value.phase2.length > 0) {
    phases.push({
      title: '第二阶段：核心模型',
      nodes: nodesByPhase.value.phase2,
      y: 250
    })
  }

  // 第三阶段
  if (nodesByPhase.value.phase3.length > 0) {
    phases.push({
      title: '第三阶段：前沿进阶',
      nodes: nodesByPhase.value.phase3,
      y: 400
    })
  }

  return phases
}

const flowchartData = computed(() => renderFlowchart())
</script>

<template>
  <div class="w-full h-full flex items-center justify-center p-10">
    <svg width="800" height="650" viewBox="0 0 800 650" class="drop-shadow-2xl">
      <!-- 背景 -->
      <rect width="800" height="650" fill="#0b0b0b"/>

      <!-- 阶段标题 -->
      <g v-for="(phase, phaseIndex) in flowchartData" :key="phaseIndex">
        <text x="400" :y="phase.y - 30" text-anchor="middle" fill="#60a5fa" font-size="16" font-weight="bold">
          {{ phase.title }}
        </text>

        <!-- 开始节点 -->
        <g :transform="`translate(${phase.nodes.length > 0 ? 50 : 350}, ${phase.y + 20})`">
          <rect width="120" height="40" rx="20" fill="#1e293b" stroke="#3b82f6" stroke-width="2"/>
          <text x="60" y="25" text-anchor="middle" fill="#60a5fa" font-size="12">开始学习</text>
        </g>

        <!-- 连接线：开始到第一个节点 -->
        <path
          v-if="phase.nodes.length > 0"
          :d="`M 170 ${phase.y + 40} L 170 ${phase.y + 40} L 220 ${phase.y + 40}`"
          stroke="#666" stroke-width="2" fill="none" marker-end="url(#arrowhead)"
        />

        <!-- 节点 -->
        <g v-for="(node, nodeIndex) in phase.nodes" :key="node.id" :transform="`translate(220, ${phase.y + nodeIndex * 60})`">
          <rect width="120" height="40" rx="8" :fill="node.status === 'completed' ? '#0f172a' : node.status === 'active' ? '#1e293b' : '#1a1a1a'"
                :stroke="node.status === 'completed' ? '#22c55e' : node.status === 'active' ? '#3b82f6' : '#4b5563'"
                stroke-width="1"/>
          <text x="60" y="25" text-anchor="middle" :fill="node.status === 'completed' ? '#666' : '#fff'" font-size="12">
            {{ node.label }}
          </text>
        </g>

        <!-- 连接线：节点间 -->
        <g v-if="phase.nodes.length > 1">
          <path
            v-for="(_, i) in phase.nodes.slice(0, -1)"
            :d="`M 340 ${phase.y + 40 + i * 60} L 340 ${phase.y + 100 + i * 60} L 220 ${phase.y + 100 + i * 60} L 220 ${phase.y + 40 + (i + 1) * 60}`"
            stroke="#666" stroke-width="1.5" fill="none" marker-end="url(#arrowhead)"
          />
        </g>

        <!-- 结束节点 -->
        <g v-if="phase.nodes.length > 0" :transform="`translate(340, ${phase.y + (phase.nodes.length - 1) * 60 + 40})`">
          <rect width="120" height="40" rx="20" fill="#1e293b" stroke="#22c55e" stroke-width="2"/>
          <text x="60" y="25" text-anchor="middle" fill="#22c55e" font-size="12">阶段完成</text>
        </g>

        <!-- 阶段间连接 -->
        <path
          v-if="phaseIndex < flowchartData.length - 1"
          :d="`M 400 ${phase.y + phase.nodes.length * 60 + 80} L 400 ${phase.y + phase.nodes.length * 60 + 120} L 400 ${flowchartData[phaseIndex + 1].y + 20}`"
          stroke="#666" stroke-width="1" fill="none" marker-end="url(#arrowhead)" stroke-dasharray="5,5"
        />
      </g>

      <!-- 箭头标记 -->
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="#666" />
        </marker>
      </defs>
    </svg>
  </div>
</template>