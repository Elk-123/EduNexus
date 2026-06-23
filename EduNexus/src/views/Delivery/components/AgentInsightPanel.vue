<!-- src/views/Delivery/components/AgentInsightPanel.vue -->
<script setup lang="ts">
import { Brain, ShieldCheck, Zap } from 'lucide-vue-next';
</script>

<template>
  <div class="space-y-6 sticky top-8">
    <div class="rounded-3xl border border-zinc-800 bg-zinc-900/20 p-6 space-y-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center border border-blue-500/30">
          <Brain class="text-blue-500" :size="20" />
        </div>
        <div>
          <h4 class="font-bold text-white text-sm">Planner Agent</h4>
          <span class="text-[10px] text-emerald-400 font-mono tracking-tighter">ONLINE</span>
        </div>
      </div>
      <p class="text-[11px] text-zinc-400 bg-white/5 p-3 rounded-xl border border-white/5 leading-relaxed">
        "检测到你对 Transformer 注意力机制的理解已达标，已将 CNN 卷积网络解锁并推送到你的学习流中。"
      </p>
      <div class="grid grid-cols-2 gap-2">
        <div class="p-3 rounded-xl bg-zinc-900 border border-zinc-800 text-center">
          <Zap :size="14" class="mx-auto mb-1 text-orange-400" />
          <div class="text-[10px] text-zinc-500 uppercase font-medium">专注度</div>
          <div class="text-xs font-bold text-white">高强度</div>
        </div>
        <div class="p-3 rounded-xl bg-zinc-900 border border-zinc-800 text-center">
          <ShieldCheck :size="14" class="mx-auto mb-1 text-blue-400" />
          <div class="text-[10px] text-zinc-500 uppercase font-medium">掌握度</div>
          <div class="text-xs font-bold text-white">82%</div>
        </div>
      </div>
    </div>
  </div>
</template>
