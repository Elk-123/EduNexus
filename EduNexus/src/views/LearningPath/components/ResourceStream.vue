<!-- components/ResourceStream.vue -->
<script setup lang="ts">
import { PlayCircle, FileText, Code2, CheckCircle2, Lock } from 'lucide-vue-next'

const resources = [
  {
    type: 'video',
    title: '矩阵运算与线性空间直观理解',
    duration: '12:45',
    status: 'current',
    agent: 'Director Agent',
    desc: '视频概念引入：通过几何变换理解矩阵乘法。'
  },
  {
    type: 'doc',
    title: '深度学习中的线性代数核心公式',
    status: 'locked',
    agent: 'Professor Agent',
    desc: '精读文档：掌握张量运算与梯度传播。'
  },
  {
    type: 'code',
    title: 'NumPy 矩阵实操工作坊',
    status: 'locked',
    agent: 'Hacker Agent',
    desc: '代码实操：在 Jupyter 环境中手动实现反向传播。'
  },
  {
    type: 'quiz',
    title: '全连接层数学基础能力自测',
    status: 'locked',
    agent: 'Examiner Agent',
    desc: '随堂测试：5道选择题，3道计算题。'
  }
]
</script>

<template>
  <div class="p-4 space-y-6">
    <div v-for="(item, index) in resources" :key="index" class="relative">
      <!-- 连线 -->
      <div v-if="index !== resources.length - 1" class="absolute left-5 top-10 bottom-[-24px] w-[1px] bg-white/10"></div>
      
      <div :class="[
        'relative z-10 flex gap-4 p-4 rounded-xl border transition-all duration-300',
        item.status === 'current' ? 'bg-blue-500/5 border-blue-500/30' : 'bg-white/5 border-white/5 opacity-50'
      ]">
        <div :class="[
          'w-10 h-10 rounded-full flex items-center justify-center shrink-0',
          item.status === 'current' ? 'bg-blue-500/20 text-blue-400' : 'bg-slate-800 text-slate-500'
        ]">
          <component :is="item.type === 'video' ? PlayCircle : item.type === 'doc' ? FileText : item.type === 'code' ? Code2 : CheckCircle2" class="h-5 w-5" />
        </div>
        
        <div class="flex-1">
          <div class="flex items-center justify-between mb-1">
            <span class="text-[10px] text-blue-400 font-mono uppercase tracking-widest">{{ item.agent }}</span>
            <Lock v-if="item.status === 'locked'" class="h-3 w-3 text-slate-600" />
          </div>
          <h3 class="text-sm font-medium text-slate-200 mb-2">{{ item.title }}</h3>
          <p class="text-xs text-slate-500 leading-relaxed mb-3">{{ item.desc }}</p>
          
          <div v-if="item.status === 'current'" class="flex gap-2">
            <button class="text-[10px] bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md transition-colors">
              立即开始学习
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>