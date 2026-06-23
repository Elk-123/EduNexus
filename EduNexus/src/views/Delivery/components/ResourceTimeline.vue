<script setup lang="ts">
import { Play, FileText, Code, CheckSquare, Sparkles, Clock } from 'lucide-vue-next'
import { cn } from '@/lib/utils'
import type { TodayResource } from '@/types/resources'

defineProps<{
  resources: TodayResource[]
  isLoading?: boolean
}>()

const getIcon = (type: string) => {
  switch (type) {
    case 'video': return Play
    case 'document': return FileText
    case 'code': return Code
    case 'quiz': return CheckSquare
    default: return FileText
  }
}
</script>

<template>
  <div class="relative">
    <!-- 时间线竖线 -->
    <div class="absolute left-4 top-0 bottom-0 w-px bg-gradient-to-b from-blue-500/50 via-zinc-700 to-transparent"></div>

    <div class="space-y-8">
      <!-- Loading skeleton -->
      <div v-if="isLoading && resources.length === 0" class="space-y-6 pl-12">
        <div v-for="i in 3" :key="i" class="h-28 bg-zinc-900/40 rounded-2xl animate-pulse"></div>
      </div>

      <!-- Empty state -->
      <div v-else-if="!isLoading && resources.length === 0" class="text-center py-16 pl-12">
        <p class="text-zinc-500 text-sm">暂无推送资源，请先在内容工厂生成内容</p>
      </div>

      <!-- 资源列表 -->
      <a
        v-for="item in resources"
        :key="item.id"
        :href="item.url"
        target="_blank"
        rel="noopener noreferrer"
        class="relative pl-12 group block"
      >
        <!-- 时间线节点 -->
        <div
          :class="cn(
            'absolute left-1.5 top-3 w-5 h-5 rounded-full border-2 flex items-center justify-center z-10 transition-all',
            item.status === 'completed'
              ? 'bg-emerald-500/20 border-emerald-500'
              : item.status === 'current'
                ? 'bg-blue-500/20 border-blue-400 shadow-[0_0_12px_rgba(96,165,250,0.4)]'
                : 'bg-zinc-800 border-zinc-700'
          )"
        >
          <div
            :class="cn(
              'w-1.5 h-1.5 rounded-full',
              item.status === 'completed' ? 'bg-emerald-400' :
              item.status === 'current' ? 'bg-blue-400 animate-pulse' :
              'bg-zinc-600'
            )"
          ></div>
        </div>

        <!-- 内容卡片 -->
        <div
          :class="cn(
            'rounded-2xl border p-5 transition-all hover:border-zinc-600',
            item.status === 'current'
              ? 'bg-blue-500/5 border-blue-500/20'
              : item.status === 'locked'
                ? 'bg-zinc-900/20 border-zinc-800/50 opacity-60'
                : 'bg-zinc-900/20 border-zinc-800/50'
          )"
        >
          <!-- 标题 -->
          <h3
            :class="cn(
              'text-base font-bold mb-2 group-hover:text-blue-400 transition-colors',
              item.status === 'locked' ? 'text-zinc-600' : 'text-white'
            )"
          >
            {{ item.title }}
          </h3>

          <!-- 描述 -->
          <p class="text-sm text-zinc-400 leading-relaxed line-clamp-2 mb-3">
            {{ item.description }}
          </p>

          <!-- 底部：时长 + AI 推荐理由 -->
          <div class="flex items-center gap-4 text-xs text-zinc-500">
            <span class="flex items-center gap-1">
              <Clock :size="11" />
              {{ item.duration }}
            </span>
            <span v-if="item.status === 'current'" class="text-blue-400 font-medium">当前学习</span>
            <span v-else-if="item.status === 'completed'" class="text-emerald-500">已完成</span>
          </div>

          <!-- AI 洞察 -->
          <div
            v-if="item.ai_reason"
            class="mt-3 bg-indigo-500/5 border border-indigo-500/10 rounded-xl p-3 flex items-start gap-2"
          >
            <Sparkles :size="12" class="text-indigo-400 mt-0.5 shrink-0" />
            <p class="text-xs text-indigo-300/80 leading-relaxed">
              <span class="font-bold text-indigo-300">AI Insight: </span>{{ item.ai_reason }}
            </p>
          </div>
        </div>
      </a>
    </div>
  </div>
</template>
