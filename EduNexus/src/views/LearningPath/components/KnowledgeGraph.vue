<script setup lang="ts">
import type { KnowledgeNode } from '@/types/graph'

const props = defineProps<{
  nodes: KnowledgeNode[]
  activeId: string
}>()

function getNodeX(index: number, total: number): number {
  if (total <= 1) return 300
  return 40 + (index * (520 / (total - 1)))
}

function getNodeY(node: KnowledgeNode): number {
  if (node.type === 'injected') return 80
  return 180
}

function getNodeColor(node: KnowledgeNode): string {
  switch (node.status) {
    case 'completed': return '#22c55e'
    case 'active': return '#3b82f6'
    default: return '#52525b'  // pending
  }
}

function getNodeBgColor(node: KnowledgeNode): string {
  switch (node.status) {
    case 'active': return '#1a2236'
    default: return '#1a1a1a'
  }
}

function getNodeStrokeColor(node: KnowledgeNode): string {
  switch (node.status) {
    case 'active': return '#3b82f6'
    case 'completed': return '#333'
    default: return '#27272a'
  }
}

function getNodeTextColor(node: KnowledgeNode): string {
  switch (node.status) {
    case 'completed': return '#666'
    case 'active': return '#fff'
    default: return '#52525b'
  }
}


</script>

<template>
  <div class="w-full h-full flex items-center justify-center p-10">
    <svg width="600" height="400" viewBox="0 0 600 400" class="drop-shadow-2xl">
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
        </marker>
      </defs>

      <!-- 连接线 -->
      <g stroke="#333" stroke-width="2" fill="none" marker-end="url(#arrowhead)">
        <line
          v-for="(_, i) in nodes.slice(0, -1)"
          :key="`edge-${i}`"
          :x1="getNodeX(i, nodes.length) + 60"
          :y1="getNodeY(nodes[i]) + 25"
          :x2="getNodeX(i + 1, nodes.length)"
          :y2="getNodeY(nodes[i + 1]) + 25"
          :stroke="nodes[i].type === 'injected' || nodes[i + 1].type === 'injected' ? '#3b82f6' : '#333'"
          :stroke-dasharray="nodes[i].type === 'injected' || nodes[i + 1].type === 'injected' ? '5,5' : 'none'"
        />
      </g>

      <!-- 节点 -->
      <g
        v-for="(node, index) in nodes"
        :key="node.id"
        :transform="`translate(${getNodeX(index, nodes.length)}, ${getNodeY(node)})`"
        :class="node.status === 'active' ? 'animate-pulse-subtle' : ''"
      >
        <rect
          :width="node.label.length > 8 ? 130 : 100"
          height="50"
          rx="8"
          :fill="getNodeBgColor(node)"
          :stroke="getNodeStrokeColor(node)"
          :stroke-width="node.type === 'injected' ? 2 : 1"
        />
        <text
          :x="(node.label.length > 8 ? 130 : 100) / 2"
          y="22"
          :fill="getNodeTextColor(node)"
          font-size="10"
          text-anchor="middle"
          :font-weight="node.status === 'active' ? 'bold' : 'normal'"
        >{{ node.label }}</text>
        <circle
          v-if="node.type === 'injected'"
          :cx="(node.label.length > 8 ? 130 : 100) / 2"
          cy="40"
          r="3"
          :fill="getNodeColor(node)"
        />
        <text
          v-if="node.type === 'injected'"
          :x="(node.label.length > 8 ? 130 : 100) / 2"
          y="42"
          fill="#1d4ed8"
          font-size="7"
          text-anchor="middle"
        >AI INJECTED</text>
        <circle
          v-else
          :cx="0"
          cy="25"
          r="3"
          :fill="getNodeColor(node)"
        />
      </g>

      <!-- 空状态 -->
      <text
        v-if="nodes.length === 0"
        x="300" y="200"
        fill="#52525b"
        font-size="14"
        text-anchor="middle"
      >规划中...</text>
    </svg>
  </div>
</template>

<style scoped>
@keyframes pulse-subtle {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
.animate-pulse-subtle {
  animation: pulse-subtle 2s ease-in-out infinite;
}
</style>
