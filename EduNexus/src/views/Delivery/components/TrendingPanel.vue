<script setup lang="ts">
import {
  TrendingUp,
  Github,
  MessageSquare,
  ExternalLink,
  Star,
  Flame
} from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'
import type { TrendingItem } from '@/types/resources'

const props = withDefaults(defineProps<{
  items?: TrendingItem[]
}>(), {
  items: () => [],
})

const sourceIcon = (source: string) => {
  switch (source) {
    case 'GitHub': return Github
    case 'StackOverflow': return MessageSquare
    case 'Arxiv': return TrendingUp
    default: return Flame
  }
}

const sourceColor = (source: string) => {
  switch (source) {
    case 'GitHub': return 'text-white'
    case 'StackOverflow': return 'text-orange-400'
    case 'Arxiv': return 'text-blue-400'
    default: return 'text-zinc-400'
  }
}
</script>

<template>
  <div class="rounded-3xl border border-zinc-800 bg-zinc-900/20 p-6 space-y-5">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <div class="p-1.5 bg-orange-500/20 rounded-lg">
          <Flame class="text-orange-500" :size="16" />
        </div>
        <h4 class="font-bold text-white text-sm">行业热点 (Trending)</h4>
      </div>
      <button class="text-[10px] text-zinc-500 hover:text-zinc-300 transition-colors uppercase font-bold tracking-widest">
        查看全部
      </button>
    </div>

    <!-- Trend List -->
    <div class="space-y-4">
      <div
        v-for="(item, idx) in props.items"
        :key="idx"
        class="group cursor-pointer space-y-2"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="flex-grow space-y-1">
            <div class="flex items-center gap-2">
              <component :is="sourceIcon(item.source)" :size="12" :class="sourceColor(item.source)" class="opacity-70" />
              <span class="text-[10px] font-bold text-zinc-500 uppercase tracking-tighter">{{ item.source }}</span>
            </div>
            <h5 class="text-xs font-medium text-zinc-300 group-hover:text-blue-400 transition-colors leading-snug">
              {{ item.title }}
            </h5>
          </div>
          <ExternalLink :size="12" class="text-zinc-700 group-hover:text-zinc-400 mt-1" />
        </div>

        <div class="flex items-center justify-between border-b border-zinc-800/50 pb-3 last:border-0 last:pb-0" :class="{ 'border-0 pb-0': idx === props.items.length - 1 }">
          <Badge variant="outline" class="text-[9px] py-0 h-4 bg-zinc-900/50 border-zinc-800 text-zinc-500 font-normal">
            #{{ item.tag }}
          </Badge>
          <div class="flex items-center gap-1 text-[10px] text-zinc-600">
            <Star v-if="item.source === 'GitHub'" :size="10" />
            {{ item.meta }}
          </div>
        </div>
      </div>
    </div>

    <!-- Footer Action -->
    <div class="pt-2">
      <div class="rounded-2xl bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-white/5 p-3">
        <p class="text-[10px] text-zinc-400 leading-tight">
          💡 <span class="text-zinc-200">AI Insight:</span> 
          根据你的关注点，我们发现 WebAssembly 可能与你下周的学习任务相关。
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 悬停微动效 */
.group:hover h5 {
  text-decoration: underline;
  text-underline-offset: 4px;
}
</style>