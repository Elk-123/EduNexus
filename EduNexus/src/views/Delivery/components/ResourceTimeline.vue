<script setup lang="ts">
import { ref } from 'vue';
import { Play, FileText, Code, CheckSquare, Lock, Sparkles, ArrowRight } from 'lucide-vue-next';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

const resources = ref([
  { id: 'res-1', type: 'video', title: '线性代数补丁：张量与矩阵乘法', duration: '15:00', status: 'completed', aiReason: '检测到你在“反向传播”练习中对权重维度感到困惑。', description: '快速回顾深度学习中最高频使用的矩阵运算技巧。' },
  { id: 'res-2', type: 'document', title: '深度神经网络架构概览', duration: '10 min read', status: 'current', aiReason: '核心理论节选，重点阅读标注的第 3/5/8 页。', description: '理解层（Layers）、激活函数（Activation）与损失函数（Loss）的关系。' },
  { id: 'res-3', type: 'code', title: '实战：构建你的第一个感知机', duration: '30 min', status: 'locked', description: '使用 Python 和 NumPy 动手实现感知机的前向传播。' }
]);

const getIcon = (type: string) => {
  switch (type) {
    case 'video': return Play;
    case 'document': return FileText;
    case 'code': return Code;
    case 'quiz': return CheckSquare;
    default: return FileText;
  }
};
</script>

<template>
  <div class="relative">
    <div class="absolute left-8 top-0 bottom-0 w-[1px] bg-gradient-to-b from-blue-500 via-zinc-800 to-transparent"></div>
    <div class="space-y-12">
      <div v-for="item in resources" :key="item.id" class="relative pl-20 group">
        <div :class="cn('absolute left-4 top-0 w-8 h-8 rounded-full border-2 flex items-center justify-center z-10', 
          item.status === 'completed' ? 'bg-emerald-500 border-emerald-500 text-black' : 
          item.status === 'current' ? 'bg-blue-600 border-blue-600 text-white animate-pulse' : 
          'bg-zinc-900 border-zinc-700 text-zinc-600')">
          <component :is="item.status === 'locked' ? Lock : getIcon(item.type)" :size="14" />
        </div>
        <div :class="cn('rounded-3xl border p-6 bg-zinc-900/40 border-zinc-800 transition-all', item.status === 'current' && 'border-blue-500/50 bg-zinc-900/80')">
          <div class="flex flex-col md:flex-row gap-6">
            <div class="w-full md:w-40 h-24 rounded-2xl bg-zinc-800 flex items-center justify-center">
              <component :is="getIcon(item.type)" :size="24" class="text-zinc-600" />
            </div>
            <div class="flex-grow">
              <Badge variant="outline" class="mb-2 uppercase text-[9px] tracking-widest">{{ item.type }}</Badge>
              <h3 :class="cn('text-xl font-bold mb-1', item.status === 'locked' ? 'text-zinc-600' : 'text-white')">{{ item.title }}</h3>
              <p class="text-sm text-zinc-500 line-clamp-2 mb-4">{{ item.description }}</p>
              <div v-if="item.aiReason" class="bg-indigo-500/5 border border-indigo-500/10 rounded-xl p-3 flex items-start gap-3">
                <Sparkles :size="12" class="text-indigo-400 mt-1" />
                <p class="text-xs text-indigo-300/80 italic"><span class="font-bold not-italic">Planner Insight: </span>{{ item.aiReason }}</p>
              </div>
            </div>
            <div class="flex flex-col justify-end">
              <Button :disabled="item.status === 'locked'" :variant="item.status === 'completed' ? 'outline' : 'default'" class="rounded-full gap-2">
                {{ item.status === 'completed' ? '回顾' : '开始' }} <ArrowRight :size="14" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>