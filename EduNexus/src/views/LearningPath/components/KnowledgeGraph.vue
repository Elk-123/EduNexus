<!-- components/KnowledgeGraph.vue -->
<script setup lang="ts">
defineProps<{ highlightInjected: boolean }>()
</script>

<template>
  <div class="w-full h-full flex items-center justify-center p-10">
    <svg width="600" height="400" viewBox="0 0 600 400" class="drop-shadow-2xl">
      <!-- 定义箭头 -->
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
        </marker>
      </defs>

      <!-- 连接线 -->
      <g stroke="#333" stroke-width="2" fill="none" marker-end="url(#arrowhead)">
        <path d="M100,200 L200,200" />
        <path d="M300,200 L400,200" />
        <!-- 动态插入的路径 -->
        <path v-if="highlightInjected" d="M100,200 Q250,50 400,200" stroke="#3b82f6" stroke-dasharray="5,5" class="animate-dash" />
      </g>

      <!-- 节点 -->
      <!-- 节点 1: 线性代数 (基础) -->
      <g transform="translate(50,175)">
        <rect width="100" height="50" rx="8" fill="#1a1a1a" stroke="#333" />
        <text x="50" y="30" fill="#666" font-size="10" text-anchor="middle">线性代数基础</text>
        <circle cx="100" cy="25" r="3" fill="#22c55e" />
      </g>

      <!-- 节点 2: 矩阵运算 (插入节点) -->
      <g v-if="highlightInjected" transform="translate(200,70)" class="animate-bounce-subtle">
        <rect width="100" height="50" rx="8" fill="#1e1e1e" stroke="#3b82f6" stroke-width="2" />
        <text x="50" y="30" fill="#3b82f6" font-size="10" text-anchor="middle" font-weight="bold">矩阵运算强化</text>
        <text x="50" y="45" fill="#1d4ed8" font-size="8" text-anchor="middle">Planner 动态插入</text>
      </g>

      <!-- 节点 3: 神经网络架构 -->
      <g transform="translate(400,175)">
        <rect width="120" height="50" rx="8" fill="#1a1a1a" stroke="#3b82f6" stroke-width="1" />
        <text x="60" y="30" fill="#fff" font-size="10" text-anchor="middle">Transformer 架构</text>
        <circle cx="0" cy="25" r="3" fill="#3b82f6" />
      </g>
    </svg>
  </div>
</template>

<style scoped>
@keyframes dash {
  to { stroke-dashoffset: -20; }
}
.animate-dash {
  animation: dash 1s linear infinite;
}
@keyframes bounce-subtle {
  0%, 100% { transform: translate(200, 70); }
  50% { transform: translate(200, 65); }
}
.animate-bounce-subtle {
  animation: bounce-subtle 2s ease-in-out infinite;
}
</style>