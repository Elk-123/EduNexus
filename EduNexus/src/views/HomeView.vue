<script setup lang="ts">
import { ref } from 'vue'
import { 
  BrainCircuit, Sparkles, Zap, Activity, 
  ChevronRight, Play, FileText, Code2, 
  Map, Lightbulb, CheckCircle2, AlertCircle 
} from 'lucide-vue-next'
import { Button } from '@/components/ui/button'

// 模拟多智能体工厂状态
const agentResources = [
  { name: '教授 (Professor)', task: '讲解文档', status: 'Completed', icon: FileText, color: 'text-blue-500' },
  { name: '架构师 (Architect)', task: '思维导图', status: 'Generating', icon: Map, color: 'text-emerald-500' },
  { name: '考官 (Examiner)', task: '自适应测验', status: 'Pending', icon: CheckCircle2, color: 'text-amber-500' },
  { name: '导演 (Director)', task: '多模态分镜', status: 'Completed', icon: Play, color: 'text-purple-500' },
  { name: '极客 (Hacker)', task: '实操案例', status: 'Generating', icon: Code2, color: 'text-pink-500' },
]

// 模拟动态画像 6 维度
const profileDimensions = [
  { label: '知识基础', value: 85 },
  { label: '认知风格', value: '视觉型', isTag: true },
  { label: '易错偏好', value: '逻辑边界', isTag: true },
  { label: '学习目标', value: '项目实战', isTag: true },
  { label: '专注时长', value: '45min' },
  { label: '抗压值', value: 72 },
]
</script>

<template>
  <div class="space-y-8 pb-10">
    <!-- 1. 顶部：破冰智能体反馈 & 核心指标 -->
    <section class="flex flex-col md:flex-row gap-6 items-end justify-between">
      <div>
        <div class="flex items-center gap-2 text-blue-500 mb-2">
          <Sparkles class="w-4 h-4" />
          <span class="text-xs font-bold uppercase tracking-[0.2em]">Ice-breaker Agent Feedback</span>
        </div>
        <h1 class="text-4xl font-bold text-white tracking-tight">
          你好, 同学 <span class="text-zinc-500 text-2xl font-normal">/ 准备好开始今天的“梯度下降”探索了吗？</span>
        </h1>
      </div>
      <!-- 快速状态指标 -->
      <div class="flex gap-4">
        <div class="bg-[#131314] border border-[#303134] px-4 py-2 rounded-2xl flex items-center gap-3">
          <Activity class="w-4 h-4 text-orange-500" />
          <div>
            <p class="text-[10px] text-zinc-500 uppercase tracking-wider">当前抗压值</p>
            <p class="text-sm font-bold text-white">72% (稳定)</p>
          </div>
        </div>
        <div class="bg-[#131314] border border-[#303134] px-4 py-2 rounded-2xl flex items-center gap-3">
          <Zap class="w-4 h-4 text-yellow-500" />
          <div>
            <p class="text-[10px] text-zinc-500 uppercase tracking-wider">专注度等级</p>
            <p class="text-sm font-bold text-white">High (A)</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 2. 中间主要内容：Bento 布局 -->
    <div class="grid grid-cols-12 gap-6">
      
      <!-- 左侧：知识图谱动态路由 (DAG 展示区) -->
      <div class="col-span-12 lg:col-span-8 bg-[#131314] border border-[#303134] rounded-[2.5rem] p-8 relative overflow-hidden group">
        <div class="flex justify-between items-start mb-8">
          <div>
            <h3 class="text-xl font-bold text-white flex items-center gap-2">
              <BrainCircuit class="w-5 h-5 text-blue-500" />
              动态规划路径：人工智能导论
            </h3>
            <p class="text-zinc-500 text-sm mt-1">Planner Agent 已根据你的“线代基础”自动插入补充节点</p>
          </div>
          <Button variant="outline" class="rounded-xl border-[#303134] bg-transparent text-xs">查看全量图谱</Button>
        </div>

        <!-- 模拟 DAG 节点展示 -->
        <div class="flex items-center justify-between px-10 py-10 relative">
          <!-- 背景线 -->
          <div class="absolute top-1/2 left-20 right-20 h-px bg-dashed bg-zinc-800 -translate-y-1/2 z-0"></div>
          
          <div class="flex flex-col items-center gap-3 z-10 opacity-50">
            <div class="w-12 h-12 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center text-zinc-500">
              <CheckCircle2 class="w-6 h-6" />
            </div>
            <span class="text-xs font-medium">线性代数</span>
          </div>

          <div class="flex flex-col items-center gap-3 z-10">
            <div class="w-16 h-16 rounded-full bg-blue-600 border-4 border-blue-900/50 flex items-center justify-center text-white shadow-[0_0_30px_rgba(37,99,235,0.4)] animate-pulse">
              <Activity class="w-8 h-8" />
            </div>
            <span class="text-sm font-bold text-white underline underline-offset-8 decoration-blue-500">梯度下降算法</span>
          </div>

          <div class="flex flex-col items-center gap-3 z-10">
            <div class="w-12 h-12 rounded-full bg-[#0b0b0b] border border-zinc-800 flex items-center justify-center text-zinc-700">
              <ChevronRight class="w-6 h-6" />
            </div>
            <span class="text-xs font-medium text-zinc-600">反向传播</span>
          </div>

          <div class="flex flex-col items-center gap-3 z-10">
            <div class="w-12 h-12 rounded-full bg-[#0b0b0b] border border-zinc-800 flex items-center justify-center text-zinc-700">
              <ChevronRight class="w-6 h-6" />
            </div>
            <span class="text-xs font-medium text-zinc-600">神经网络</span>
          </div>
        </div>

        <!-- 悬浮提示：动态路由逻辑说明 -->
        <div class="mt-8 bg-blue-500/5 border border-blue-500/10 rounded-2xl p-4 flex items-start gap-3">
          <AlertCircle class="w-5 h-5 text-blue-500 shrink-0 mt-0.5" />
          <p class="text-xs text-blue-200/70 leading-relaxed">
            检测到当前节点难度较大，已由 <span class="text-blue-400 font-bold">Hacker Agent</span> 自动生成配套代码实验室。
          </p>
        </div>
      </div>

      <!-- 右侧：内容制造车间状态 (Multi-Agent Status) -->
      <div class="col-span-12 lg:col-span-4 bg-[#131314] border border-[#303134] rounded-[2.5rem] p-8 flex flex-col">
        <h3 class="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <Sparkles class="w-5 h-5 text-purple-500" />
          内容制造车间
        </h3>
        
        <div class="space-y-4 flex-1">
          <div v-for="agent in agentResources" :key="agent.name" 
            class="flex items-center justify-between p-4 rounded-2xl bg-[#0b0b0b]/50 border border-[#303134] hover:border-zinc-700 transition-all cursor-pointer">
            <div class="flex items-center gap-4">
              <div :class="`p-2 rounded-lg bg-zinc-900 ${agent.color}`">
                <component :is="agent.icon" class="w-5 h-5" />
              </div>
              <div>
                <p class="text-sm font-bold text-zinc-200">{{ agent.name }}</p>
                <p class="text-[10px] text-zinc-500">{{ agent.task }}</p>
              </div>
            </div>
            <div class="flex flex-col items-end">
              <span v-if="agent.status === 'Completed'" class="text-[10px] text-emerald-500 font-bold uppercase tracking-tighter italic">Ready</span>
              <span v-else class="flex items-center gap-1">
                <span class="w-1.5 h-1.5 bg-blue-500 rounded-full animate-ping"></span>
                <span class="text-[10px] text-zinc-600 font-bold uppercase">Work...</span>
              </span>
            </div>
          </div>
        </div>

        <Button class="w-full mt-6 bg-white text-black hover:bg-zinc-200 rounded-xl h-12 font-bold transition-all active:scale-95">
          进入沉浸式学习模式
        </Button>
      </div>

      <!-- 下方左侧：6 维画像雷达图占位 -->
      <div class="col-span-12 lg:col-span-4 bg-[#131314] border border-[#303134] rounded-[2.5rem] p-8">
        <h3 class="text-lg font-bold text-white mb-6">自主画像 (Ice-breaker Result)</h3>
        <div class="grid grid-cols-2 gap-4">
          <div v-for="dim in profileDimensions" :key="dim.label" class="bg-[#0b0b0b] p-3 rounded-xl border border-[#202022]">
            <p class="text-[10px] text-zinc-500 uppercase font-bold">{{ dim.label }}</p>
            <p v-if="!dim.isTag" class="text-xl font-bold text-white mt-1">{{ dim.value }}</p>
            <p v-else class="text-xs font-bold text-blue-400 mt-2 bg-blue-500/10 px-2 py-1 rounded inline-block">{{ dim.value }}</p>
          </div>
        </div>
        <div class="mt-6 p-4 bg-zinc-900/50 rounded-2xl border border-zinc-800 italic text-[11px] text-zinc-500 leading-relaxed text-center">
          "画像将随着你的每一次答疑和练习实时演化"
        </div>
      </div>

      <!-- 下方右侧：学情诊断报告摘要 -->
      <div class="col-span-12 lg:col-span-8 bg-[#131314] border border-[#303134] rounded-[2.5rem] p-8 flex flex-col md:flex-row items-center gap-8">
        <div class="flex-1">
          <h3 class="text-xl font-bold text-white mb-2 underline decoration-blue-500 decoration-4 underline-offset-4">Assessor Agent 诊断</h3>
          <p class="text-zinc-400 text-sm leading-relaxed mb-6">
            本周你对线性代数的掌握程度提升了 <span class="text-emerald-500 font-bold">15%</span>，但在代码实操部分的“梯度爆炸”问题上停留超过 45 分钟。建议开启 <span class="text-blue-400">Tutor Agent</span> 专项答疑。
          </p>
          <div class="flex gap-4">
            <Button size="sm" class="rounded-lg bg-blue-600">生成周报 PDF</Button>
            <Button size="sm" variant="ghost" class="text-zinc-400">查看历史曲线</Button>
          </div>
        </div>
        <!-- 装饰性元素：雷达图占位 -->
        <div class="w-48 h-48 bg-blue-500/5 rounded-full border border-blue-500/10 flex items-center justify-center">
           <BrainCircuit class="w-20 h-20 text-blue-500/20" />
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* 虚线背景动画 */
.bg-dashed {
  background-image: linear-gradient(to right, #303134 50%, transparent 50%);
  background-size: 10px 1px;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(37,99,235,0.4); }
  70% { box-shadow: 0 0 0 20px rgba(37,99,235,0); }
  100% { box-shadow: 0 0 0 0 rgba(37,99,235,0); }
}

.animate-pulse {
  animation: pulse 2s infinite;
}
</style>  