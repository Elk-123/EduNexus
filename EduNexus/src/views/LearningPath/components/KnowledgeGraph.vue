<script setup lang="ts">
import { computed } from 'vue'
import type { KnowledgeNode, KnowledgeEdge } from '@/types/graph'

const props = defineProps<{
  nodes: KnowledgeNode[]
  edges: KnowledgeEdge[]
  activeId?: string
  phaseName?: string
}>()

interface NodeWithPosition extends KnowledgeNode {
  layer: number
  x: number
  y: number
  width: number
  height: number
}

const nodeWidth = 160
const nodeHeight = 50
const layerSpacing = 100
const nodeSpacing = 20

const graphNodes = computed<NodeWithPosition[]>(() => {
  const standardNodes = props.nodes.filter(n => n.type !== 'milestone')
  if (standardNodes.length === 0) return []

  // 构建邻接表
  const adj: Record<string, string[]> = {}
  const reverseAdj: Record<string, string[]> = {}
  const nodeSet = new Set(standardNodes.map(n => n.id))

  standardNodes.forEach(n => {
    adj[n.id] = []
    reverseAdj[n.id] = []
  })

  props.edges.forEach(edge => {
    if (nodeSet.has(edge.from) && nodeSet.has(edge.to)) {
      adj[edge.from].push(edge.to)
      reverseAdj[edge.to].push(edge.from)
    }
  })

  // 拓扑排序计算层级
  const layers: Record<string, number> = {}
  const visited = new Set<string>()
  const queue: string[] = []

  standardNodes.forEach(n => {
    if (reverseAdj[n.id].length === 0) {
      layers[n.id] = 0
      queue.push(n.id)
    }
  })

  if (queue.length === 0 && standardNodes.length > 0) {
    layers[standardNodes[0].id] = 0
    queue.push(standardNodes[0].id)
  }

  while (queue.length > 0) {
    const nodeId = queue.shift()!
    visited.add(nodeId)

    adj[nodeId].forEach(neighborId => {
      const newLayer = layers[nodeId] + 1
      if (layers[neighborId] === undefined || newLayer > layers[neighborId]) {
        layers[neighborId] = newLayer
        queue.push(neighborId)
      }
    })
  }

  standardNodes.forEach(n => {
    if (!visited.has(n.id)) {
      layers[n.id] = 0
    }
  })

  // 按层级分组
  const layerGroups: Record<number, KnowledgeNode[]> = {}
  Object.entries(layers).forEach(([id, layer]) => {
    const node = standardNodes.find(n => n.id === id)
    if (node) {
      if (!layerGroups[layer]) layerGroups[layer] = []
      layerGroups[layer].push(node)
    }
  })

  // 计算每个节点的位置（从上到下布局，同层水平分布）
  const result: NodeWithPosition[] = []
  const svgWidth = 900
  const svgHeight = 600
  const maxLayer = Math.max(...Object.keys(layerGroups).map(Number), 0)

  Object.entries(layerGroups).forEach(([layerStr, nodesInLayer]) => {
    const layer = parseInt(layerStr)
    const layerWidth = nodesInLayer.length * nodeWidth + (nodesInLayer.length - 1) * nodeSpacing
    const startX = (svgWidth - layerWidth) / 2
    const startY = 80 + layer * (nodeHeight + layerSpacing)

    nodesInLayer.forEach((node, index) => {
      result.push({
        ...node,
        layer,
        x: startX + index * (nodeWidth + nodeSpacing),
        y: startY,
        width: nodeWidth,
        height: nodeHeight
      })
    })
  })

  return result
})

const displayPhaseName = computed(() => {
  return props.phaseName || '学习路径'
})

// 获取正交线路径
const getEdgePath = (edge: KnowledgeEdge) => {
  const fromNode = graphNodes.value.find(n => n.id === edge.from)
  const toNode = graphNodes.value.find(n => n.id === edge.to)

  if (!fromNode || !toNode) return ''

  const startX = fromNode.x + fromNode.width / 2
  const startY = fromNode.y + fromNode.height
  const endX = toNode.x + toNode.width / 2
  const endY = toNode.y

  const midY = (startY + endY) / 2

  return `M ${startX} ${startY} L ${startX} ${midY} L ${endX} ${midY} L ${endX} ${endY}`
}
</script>

<template>
  <div class="w-full h-full flex items-center justify-center">
    <svg width="100%" height="100%" viewBox="0 0 900 600" preserveAspectRatio="xMidYMid meet">
      <!-- 背景 -->
      <rect width="900" height="600" fill="#0b0b0b"/>

      <!-- 标题 -->
      <text x="450" y="40" text-anchor="middle" fill="#60a5fa" font-size="24" font-weight="bold">{{ displayPhaseName }}</text>

      <!-- 连接线 -->
      <path
        v-for="edge in edges"
        :key="`${edge.from}-${edge.to}`"
        :d="getEdgePath(edge)"
        stroke="#666"
        stroke-width="2"
        fill="none"
      />

      <!-- 节点 -->
      <g v-for="node in graphNodes" :key="node.id">
        <rect
          :x="node.x"
          :y="node.y"
          :width="node.width"
          :height="node.height"
          :rx="10"
          :fill="node.status === 'completed' ? '#0f172a' : node.status === 'active' ? '#1e293b' : '#1a1a1a'"
          :stroke="node.status === 'completed' ? '#22c55e' : node.status === 'active' ? '#3b82f6' : '#4b5563'"
          stroke-width="2"
        />
        <text
          :x="node.x + node.width / 2"
          :y="node.y + node.height / 2 + 5"
          text-anchor="middle"
          :fill="node.status === 'completed' ? '#22c55e' : '#fff'"
          font-size="14"
          font-weight="500"
        >
          {{ node.label }}
        </text>
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