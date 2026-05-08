<script setup lang="ts">
import { computed } from 'vue'
import { Badge } from '@/components/ui/badge'

interface Agent {
  id: string
  name: string
  role: string
  status: 'idle' | 'running' | 'success' | 'error'
  icon: any
  color: string
}

const props = defineProps<{
  agent: Agent
}>()

// 根据状态计算边框和背景样式
const statusClasses = computed(() => {
  switch (props.agent.status) {
    case 'running':
      return 'bg-blue-500/10 border-blue-500/40 ring-1 ring-blue-500/20 shadow-[0_0_15px_rgba(59,130,246,0.1)]'
    case 'success':
      return 'bg-green-500/5 border-green-500/20 opacity-90'
    case 'error':
      return 'bg-red-500/10 border-red-500/40'
    default:
      return 'bg-white/5 border-transparent hover:border-white/10 opacity-60'
  }
})
</script>

<template>
  <div 
    :class="[
      'p-3 rounded-xl border transition-all duration-500 relative overflow-hidden group',
      statusClasses
    ]"
  >
    <!-- 运行中的背景扫描动画 -->
    <div 
      v-if="agent.status === 'running'" 
      class="absolute inset-0 bg-gradient-to-r from-transparent via-blue-500/5 to-transparent -translate-x-full animate-[shimmer_2s_infinite]"
    ></div>

    <div class="flex items-center gap-3 relative z-10">
      <!-- 图标容器 -->
      <div 
        :class="[
          'p-2 rounded-lg bg-black/40 transition-transform duration-500',
          agent.status === 'running' ? 'scale-110 shadow-lg' : '',
          agent.color
        ]"
      >
        <component 
          :is="agent.icon" 
          :class="['h-4 w-4', agent.status === 'running' ? 'animate-pulse' : '']" 
        />
      </div>

      <!-- 文字信息 -->
      <div class="flex-1 min-w-0">
        <div class="text-[13px] font-medium leading-none mb-1.5 flex items-center gap-2">
          {{ agent.name }}
          <span v-if="agent.status === 'running'" class="flex gap-0.5">
            <span class="w-0.5 h-0.5 rounded-full bg-current animate-bounce"></span>
            <span class="w-0.5 h-0.5 rounded-full bg-current animate-bounce [animation-delay:0.2s]"></span>
          </span>
        </div>
        <div class="text-[10px] text-slate-500 font-mono tracking-wider uppercase">{{ agent.role }}</div>
      </div>

      <!-- 状态标签 -->
      <transition name="scale">
        <Badge 
          v-if="agent.status === 'success'" 
          class="bg-green-500/20 text-green-400 border-none h-5 text-[9px] px-1.5 font-bold"
        >
          READY
        </Badge>
      </transition>
      
      <!-- 错误显示 -->
      <div v-if="agent.status === 'error'" class="h-2 w-2 rounded-full bg-red-500 shadow-[0_0_8px_#ef4444]"></div>
    </div>
  </div>
</template>

<style scoped>
@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}

.scale-enter-active, .scale-leave-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.scale-enter-from, .scale-leave-to {
  transform: scale(0);
  opacity: 0;
}
</style>