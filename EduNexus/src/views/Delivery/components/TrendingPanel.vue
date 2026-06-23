<script setup lang="ts">
import {
  TrendingUp,
  Github,
  MessageSquare,
  ExternalLink,
  Star,
  Flame,
  Newspaper,
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
    case 'HackerNews': return Newspaper
    default: return Flame
  }
}

const sourceColor = (source: string) => {
  switch (source) {
    case 'GitHub': return 'text-white'
    case 'StackOverflow': return 'text-orange-400'
    case 'Arxiv': return 'text-blue-400'
    case 'HackerNews': return 'text-amber-400'
    default: return 'text-zinc-400'
  }
}

const sourceBg = (source: string) => {
  switch (source) {
    case 'GitHub': return 'bg-white/10'
    case 'StackOverflow': return 'bg-orange-500/20'
    case 'Arxiv': return 'bg-blue-500/20'
    case 'HackerNews': return 'bg-amber-500/20'
    default: return 'bg-zinc-800'
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
        <h4 class="font-bold text-white text-sm">科技行业趋势</h4>
        <span class="text-[10px] text-zinc-600">· {{ props.items.length }} 条</span>
      </div>
      <span class="text-[10px] text-zinc-500 uppercase font-bold tracking-widest">Trending</span>
    </div>

    <!-- Trend List — scrollable -->
    <div class="space-y-3">
      <a
        v-for="(item, idx) in props.items"
        :key="idx"
        :href="item.url"
        target="_blank"
        rel="noopener noreferrer"
        class="group block"
      >
        <div class="flex items-start gap-3 py-2">
          <!-- 序号 -->
          <span
            class="text-[11px] font-mono font-bold shrink-0 w-5 text-right"
            :class="idx < 3 ? 'text-orange-500' : 'text-zinc-600'"
          >{{ idx + 1 }}</span>

          <!-- 内容 -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <div :class="['p-0.5 rounded', sourceBg(item.source)]">
                <component :is="sourceIcon(item.source)" :size="10" :class="sourceColor(item.source)" />
              </div>
              <span class="text-[9px] font-bold text-zinc-500 uppercase tracking-tighter">{{ item.source }}</span>
            </div>
            <h5 class="text-xs font-medium text-zinc-300 group-hover:text-blue-400 transition-colors leading-snug line-clamp-2">
              {{ item.title }}
            </h5>
          </div>

          <ExternalLink :size="11" class="text-zinc-700 group-hover:text-zinc-400 shrink-0 mt-1" />
        </div>

        <!-- 底部 meta -->
        <div class="flex items-center justify-between ml-8 pb-2 border-b border-zinc-800/40 last:border-0 last:pb-0">
          <Badge variant="outline" class="text-[9px] py-0 h-4 bg-zinc-900/50 border-zinc-800 text-zinc-500 font-normal">
            #{{ item.tag }}
          </Badge>
          <div class="flex items-center gap-1 text-[10px] text-zinc-600">
            <Star v-if="item.source === 'GitHub'" :size="10" />
            {{ item.meta }}
          </div>
        </div>
      </a>
    </div>

    <!-- Footer -->
    <div class="pt-1">
      <div class="rounded-2xl bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-white/5 p-3">
        <p class="text-[10px] text-zinc-400 leading-tight">
          💡 <span class="text-zinc-200">AI Insight:</span>
          本周 MoE 架构和状态空间模型 (SSM) 热度持续上升，可能与你的学习路径产生交叉。
        </p>
      </div>
    </div>
  </div>
</template>

