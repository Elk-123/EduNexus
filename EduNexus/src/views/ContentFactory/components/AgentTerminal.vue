<!-- src/views/ContentFactory/components/AgentTerminal.vue -->
<script setup lang="ts">
import { onUpdated, ref } from 'vue'

interface Log {
  id: number
  agent: string
  message: string
  type: 'info' | 'success' | 'warn'
}

defineProps<{ logs: Log[] }>()
const scrollRef = ref<HTMLElement | null>(null)

onUpdated(() => {
  if (scrollRef.value) {
    scrollRef.value.scrollTop = scrollRef.value.scrollHeight
  }
})
</script>

<template>
  <div class="flex flex-col h-full bg-black/40 border border-white/5 rounded-xl overflow-hidden font-mono text-xs">
    <div class="bg-white/5 px-3 py-2 flex items-center justify-between border-b border-white/5">
      <span class="text-slate-500 uppercase tracking-tighter">Multi-Agent Lifecycle Logs</span>
      <div class="flex gap-1.5">
        <div class="h-2 w-2 rounded-full bg-red-500/50"></div>
        <div class="h-2 w-2 rounded-full bg-yellow-500/50"></div>
        <div class="h-2 w-2 rounded-full bg-green-500/50"></div>
      </div>
    </div>
    <div ref="scrollRef" class="flex-1 p-3 overflow-y-auto space-y-1.5 scroll-smooth custom-scrollbar">
      <div v-for="log in logs" :key="log.id" class="flex gap-2">
        <span class="text-blue-500/70">[{{ log.agent }}]</span>
        <span :class="[
          log.type === 'success' ? 'text-green-400' : 
          log.type === 'warn' ? 'text-yellow-400' : 'text-slate-400'
        ]">
          {{ log.message }}
        </span>
      </div>
      <div v-if="logs.length === 0" class="text-slate-700 italic">等待任务启动...</div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #222; border-radius: 4px; }
</style>