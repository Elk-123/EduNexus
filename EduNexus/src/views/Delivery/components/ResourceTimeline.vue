<script setup lang="ts">
import { Play, FileText, Code, CheckSquare, Lock, Sparkles, ArrowRight } from 'lucide-vue-next'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import type { TodayResource } from '@/types/resources'
import type { ResourceProgress } from '@/types/resources'

defineProps<{
  resources: TodayResource[]
  isLoading?: boolean
}>()

const emit = defineEmits<{
  'update-progress': [resourceId: string, progress: ResourceProgress]
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

const handleStart = (item: TodayResource) => {
  if (item.status === 'locked') return
  if (item.status === 'current') {
    emit('update-progress', item.id, { status: 'completed', progress_percentage: 100, time_spent: 0 })
  }
}
</script>

<template>
  <div class="relative">
    <div class="absolute left-8 top-0 bottom-0 w-[1px] bg-gradient-to-b from-blue-500 via-zinc-800 to-transparent"></div>
    <div class="space-y-12">
      <!-- Loading skeleton -->
      <div v-if="isLoading && resources.length === 0" class="space-y-6 px-4">
        <div v-for="i in 3" :key="i" class="h-32 bg-zinc-900/40 rounded-3xl animate-pulse"></div>
      </div>

      <!-- Empty state -->
      <div v-else-if="!isLoading && resources.length === 0" class="text-center py-16">
        <p class="text-zinc-500 text-sm">暂无推送资源，请先在内容工厂生成内容</p>
      </div>

      <div v-for="item in resources" :key="item.id" class="relative pl-20 group">
        <div :class="cn('absolute left-4 top-0 w-8 h-8 rounded-full border-2 flex items-center justify-center z-10',
          item.status === 'completed' ? 'bg-emerald-500 border-emerald-500 text-black' :
          item.status === 'current' ? 'bg-blue-600 border-blue-600 text-white animate-pulse' :
          'bg-zinc-900 border-zinc-700 text-zinc-600')">
          <component :is="item.status === 'locked' ? Lock : getIcon(item.resource_type)" :size="14" />
        </div>
        <div :class="cn('rounded-3xl border p-6 bg-zinc-900/40 border-zinc-800 transition-all', item.status === 'current' && 'border-blue-500/50 bg-zinc-900/80')">
          <div class="flex flex-col md:flex-row gap-6">
            <div class="w-full md:w-40 h-24 rounded-2xl bg-zinc-800 flex items-center justify-center">
              <component :is="getIcon(item.resource_type)" :size="24" class="text-zinc-600" />
            </div>
            <div class="flex-grow">
              <Badge variant="outline" class="mb-2 uppercase text-[9px] tracking-widest">{{ item.resource_type }}</Badge>
              <h3 :class="cn('text-xl font-bold mb-1', item.status === 'locked' ? 'text-zinc-600' : 'text-white')">{{ item.title }}</h3>
              <p class="text-sm text-zinc-500 line-clamp-2 mb-4">{{ item.description }}</p>
              <div v-if="item.ai_reason" class="bg-indigo-500/5 border border-indigo-500/10 rounded-xl p-3 flex items-start gap-3">
                <Sparkles :size="12" class="text-indigo-400 mt-1" />
                <p class="text-xs text-indigo-300/80 italic"><span class="font-bold not-italic">Planner Insight: </span>{{ item.ai_reason }}</p>
              </div>
            </div>
            <div class="flex flex-col justify-end">
              <Button
                :disabled="item.status === 'locked'"
                :variant="item.status === 'completed' ? 'outline' : 'default'"
                class="rounded-full gap-2"
                @click="handleStart(item)"
              >
                {{ item.status === 'completed' ? '回顾' : '开始' }} <ArrowRight :size="14" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>