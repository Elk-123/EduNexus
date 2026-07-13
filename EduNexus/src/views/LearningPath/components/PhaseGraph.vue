<script setup lang="ts">
import type { KnowledgeNode, KnowledgeEdge } from '@/types/graph'
import { computed } from 'vue'

const props = defineProps<{
  nodes: KnowledgeNode[]
  edges: KnowledgeEdge[]
}>()

// ── 布局常量 ──────────────────────────────────────────────
const NODE_W = 160
const NODE_H = 44
const MILESTONE_W = 200
const LAYER_GAP = 80 // 层间垂直间距
const NODE_GAP_X = 24 // 同层节点水平间距
const TITLE_H = 36
const PAD_TOP = 16
const PAD_BOTTOM = 24
const PHASE_GAP = 40 // 阶段间垂直间距
const SVG_W = 960
const MARGIN_X = 60

const PHASE_LABELS: Record<number, string> = {
  1: '第一阶段：基础储备',
  2: '第二阶段：核心掌握',
  3: '第三阶段：前沿进阶',
}

// ── 类型 ──────────────────────────────────────────────────
interface LayoutNode {
  id: string
  label: string
  type: string
  status: string
  phase: number
  x: number // 节点左上角 X
  y: number // 节点左上角 Y（SVG 绝对坐标）
  w: number // 节点宽度
  h: number // 节点高度
  cx: number // 中心 X
  cy: number // 中心 Y
  layer: number
}

interface PhaseLayout {
  phase: number
  title: string
  nodes: LayoutNode[]
  milestoneNode: LayoutNode | null
  yTitle: number
  yStart: number // 节点区起始 Y
  yEnd: number // 节点区结束 Y（含 padding）
}

// ── 核心：三阶段 DAG 拓扑布局 ─────────────────────────────
const phaseLayouts = computed<PhaseLayout[]>(() => {
  if (props.nodes.length === 0) return []

  // 1. 按 phase 分组
  const groups: Record<number, KnowledgeNode[]> = {}
  for (const n of props.nodes) {
    const p = n.phase || 1
    if (!groups[p]) groups[p] = []
    groups[p].push(n)
  }
  const phaseNums = Object.keys(groups).map(Number).sort((a, b) => a - b)
  if (phaseNums.length === 0) return []

  // 2. 逐阶段做拓扑分层布局
  let cursorY = 30
  const layouts: PhaseLayout[] = []

  for (const p of phaseNums) {
    const allNodes = groups[p]
    const nodeIdSet = new Set(allNodes.map(n => n.id))
    // 邻接表（仅限阶段内边）
    const fwd: Record<string, string[]> = {}
    const rev: Record<string, string[]> = {}
    for (const n of allNodes) {
      fwd[n.id] = []
      rev[n.id] = []
    }
    for (const e of props.edges) {
      if (nodeIdSet.has(e.from) && nodeIdSet.has(e.to)) {
        fwd[e.from].push(e.to)
        rev[e.to].push(e.from)
      }
    }

    // 拓扑排序 → 层号
    const layer: Record<string, number> = {}
    const queue: string[] = []

    for (const n of allNodes) {
      if (rev[n.id].length === 0) {
        layer[n.id] = 0
        queue.push(n.id)
      }
    }
    if (queue.length === 0 && allNodes.length > 0) {
      layer[allNodes[0].id] = 0
      queue.push(allNodes[0].id)
    }

    const visited = new Set<string>()
    while (queue.length > 0) {
      const id = queue.shift()!
      visited.add(id)
      for (const nb of fwd[id]) {
        const nl = layer[id] + 1
        if (layer[nb] === undefined || nl > layer[nb]) {
          layer[nb] = nl
          if (!queue.includes(nb)) queue.push(nb)
        }
      }
    }
    for (const n of allNodes) {
      if (!visited.has(n.id)) layer[n.id] = 0
    }

    // 按层分组
    const layerMap: Record<number, KnowledgeNode[]> = {}
    for (const n of allNodes) {
      const l = layer[n.id]
      if (!layerMap[l]) layerMap[l] = []
      layerMap[l].push(n)
    }
    const sortedLayers = Object.keys(layerMap).map(Number).sort((a, b) => a - b)

    // 计算每个节点的坐标
    const titleY = cursorY
    cursorY += TITLE_H + PAD_TOP

    const layoutNodes: LayoutNode[] = []
    for (const l of sortedLayers) {
      const items = layerMap[l]
      const totalW = items.length * NODE_W + (items.length - 1) * NODE_GAP_X
      const startX = (SVG_W - totalW) / 2

      items.forEach((n, i) => {
        const w = n.type === 'milestone' ? MILESTONE_W : NODE_W
        const h = NODE_H
        const x = startX + i * (NODE_W + NODE_GAP_X) + (NODE_W - w) / 2
        layoutNodes.push({
          id: n.id,
          label: n.label,
          type: n.type,
          status: n.status,
          phase: p,
          x,
          y: cursorY,
          w,
          h,
          cx: x + w / 2,
          cy: cursorY + h / 2,
          layer: l,
        })
      })
      cursorY += NODE_H + LAYER_GAP
    }

    cursorY += PAD_BOTTOM
    const yEnd = cursorY
    cursorY += PHASE_GAP

    layouts.push({
      phase: p,
      title: PHASE_LABELS[p] ?? `第${p}阶段`,
      nodes: layoutNodes,
      milestoneNode: layoutNodes.find(n => n.type === 'milestone') ?? null,
      yTitle: titleY,
      yStart: titleY + TITLE_H + PAD_TOP,
      yEnd,
    })
  }

  return layouts
})

// ── SVG 动态高度 ──────────────────────────────────────────
const svgHeight = computed(() => {
  const last = phaseLayouts.value.at(-1)
  return last ? last.yEnd + 20 : 600
})

// ── 节点坐标快速索引 ──────────────────────────────────────
const posMap = computed(() => {
  const m = new Map<string, LayoutNode>()
  for (const lay of phaseLayouts.value) {
    for (const n of lay.nodes) m.set(n.id, n)
  }
  return m
})

// ── 阶段内边 ──────────────────────────────────────────────
function getPhaseEdges(layout: PhaseLayout): KnowledgeEdge[] {
  const ids = new Set(layout.nodes.map(n => n.id))
  return props.edges.filter(e => ids.has(e.from) && ids.has(e.to))
}

// ── 阶段间边 ──────────────────────────────────────────────
const interPhaseEdges = computed(() => {
  const allIds = new Set(props.nodes.map(n => n.id))
  // from 和 to 在不同阶段 且 两端都存在
  const result: { from: string; to: string; fromPhase: number; toPhase: number }[] = []
  for (const e of props.edges) {
    if (!allIds.has(e.from) || !allIds.has(e.to)) continue
    const fn = posMap.value.get(e.from)
    const tn = posMap.value.get(e.to)
    if (!fn || !tn) continue
    if (fn.phase !== tn.phase) {
      result.push({ from: e.from, to: e.to, fromPhase: fn.phase, toPhase: tn.phase })
    }
  }
  return result
})

// ── 正交连线路径 ──────────────────────────────────────────
function edgePath(fromId: string, toId: string): string {
  const f = posMap.value.get(fromId)
  const t = posMap.value.get(toId)
  if (!f || !t) return ''

  const x1 = f.cx
  const y1 = f.cy + f.h / 2 // 底部中心
  const x2 = t.cx
  const y2 = t.cy - t.h / 2 // 顶部中心
  const my = (y1 + y2) / 2

  return `M ${x1} ${y1} L ${x1} ${my} L ${x2} ${my} L ${x2} ${y2}`
}

// ── 节点颜色 ──────────────────────────────────────────────
function nodeColors(status: string, type: string) {
  if (type === 'milestone') {
    return {
      fill: '#1a1a0f',
      stroke: '#eab308',
      text: '#facc15',
    }
  }
  if (type === 'injected') {
    return {
      fill: status === 'completed' ? '#0f172a' : status === 'active' ? '#1e1e1a' : '#1a1a1a',
      stroke: status === 'completed' ? '#22c55e' : status === 'active' ? '#f59e0b' : '#78350f',
      text: status === 'completed' ? '#666' : status === 'active' ? '#fbbf24' : '#92400e',
    }
  }
  // standard
  const m = {
    completed: { fill: '#0f172a', stroke: '#22c55e', text: '#4ade80' },
    active: { fill: '#1e293b', stroke: '#3b82f6', text: '#fff' },
    pending: { fill: '#1a1a1a', stroke: '#4b5563', text: '#a1a1aa' },
  }
  return m[status as keyof typeof m] ?? m.pending
}
</script>

<template>
  <div class="w-full h-full overflow-auto custom-scrollbar">
    <svg
      :width="SVG_W"
      :height="svgHeight"
      :viewBox="`0 0 ${SVG_W} ${svgHeight}`"
      class="block mx-auto"
    >
      <!-- 背景 -->
      <rect width="100%" height="100%" fill="#0b0b0b" />

      <!-- 箭头定义 -->
      <defs>
        <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill="#666" />
        </marker>
        <marker id="arrow-inter" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill="#f59e0b" />
        </marker>
      </defs>

      <g v-for="layout in phaseLayouts" :key="layout.phase">
        <!-- 阶段背景 -->
        <rect
          :x="MARGIN_X / 2"
          :y="layout.yTitle"
          :width="SVG_W - MARGIN_X"
          :height="layout.yEnd - layout.yTitle"
          rx="16"
          fill="#0d0d0d"
          stroke="#ffffff08"
          stroke-width="1"
        />

        <!-- 阶段标题 -->
        <text
          :x="SVG_W / 2"
          :y="layout.yTitle + 24"
          text-anchor="middle"
          fill="#60a5fa"
          font-size="15"
          font-weight="700"
        >{{ layout.title }}</text>

        <!-- 阶段内连线 -->
        <path
          v-for="e in getPhaseEdges(layout)"
          :key="`${e.from}-${e.to}`"
          :d="edgePath(e.from, e.to)"
          stroke="#555"
          stroke-width="1.5"
          fill="none"
          marker-end="url(#arrow)"
        />

        <!-- 节点 -->
        <g v-for="n in layout.nodes" :key="n.id">
          <!-- milestone 用菱形，其他用圆角矩形 -->
          <template v-if="n.type === 'milestone'">
            <polygon
              :points="`${n.cx},${n.y - 4} ${n.x + n.w + 4},${n.cy} ${n.cx},${n.y + n.h + 4} ${n.x - 4},${n.cy}`"
              :fill="nodeColors(n.status, n.type).fill"
              :stroke="nodeColors(n.status, n.type).stroke"
              stroke-width="2"
            />
          </template>
          <template v-else>
            <rect
              :x="n.x"
              :y="n.y"
              :width="n.w"
              :height="n.h"
              rx="10"
              :fill="nodeColors(n.status, n.type).fill"
              :stroke="nodeColors(n.status, n.type).stroke"
              stroke-width="1.5"
            />
          </template>
          <text
            :x="n.cx"
            :y="n.cy + 5"
            text-anchor="middle"
            :fill="nodeColors(n.status, n.type).text"
            font-size="12"
            font-weight="500"
          >{{ n.label }}</text>
        </g>
      </g>

      <!-- 阶段间连线（虚线 + 金色） -->
      <path
        v-for="ie in interPhaseEdges"
        :key="`inter-${ie.from}-${ie.to}`"
        :d="edgePath(ie.from, ie.to)"
        stroke="#f59e0b"
        stroke-width="1.5"
        stroke-dasharray="6,4"
        fill="none"
        marker-end="url(#arrow-inter)"
      />
    </svg>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #252525;
  border-radius: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
</style>
