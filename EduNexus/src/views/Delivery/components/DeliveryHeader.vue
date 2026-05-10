<script setup lang="ts">
import { computed } from 'vue'
import { Calendar } from 'lucide-vue-next'
import { Progress } from '@/components/ui/progress'

interface DeliveryHeaderProps {
  courseTitle: string
  progress: number
}

const props = withDefaults(defineProps<DeliveryHeaderProps>(), {
  courseTitle: '加载中...',
  progress: 0,
})

const today = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 · 学习计划`
})
</script>

<template>
  <div class="relative overflow-hidden rounded-[2rem] border border-zinc-800 bg-zinc-900/40 p-8 backdrop-blur-md">
    <div class="absolute -top-24 -right-24 w-64 h-64 bg-blue-600/10 rounded-full blur-[80px]"></div>
    <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
      <div class="space-y-2">
        <div class="flex items-center gap-2 text-blue-400 text-sm font-medium">
          <Calendar :size="16" />
          <span>{{ today }}</span>
        </div>
        <h1 class="text-3xl font-bold text-white tracking-tight">{{ props.courseTitle }}</h1>
        <p class="text-zinc-400 max-w-lg">Planner Agent 根据你的学习画像动态调整了今日路径。</p>
      </div>
      <div class="flex flex-col items-end gap-3 min-w-[200px]">
        <div class="flex justify-between w-full text-sm">
          <span class="text-zinc-500 text-xs font-bold uppercase tracking-wider">今日进度</span>
          <span class="text-emerald-400 font-mono">{{ props.progress }}%</span>
        </div>
        <Progress :model-value="props.progress" class="h-2 w-full bg-zinc-800" />
      </div>
    </div>
  </div>
</template>