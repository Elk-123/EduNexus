<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  BrainCircuit, Sparkles,
  ChevronRight, FileText,
  CheckCircle2, AlertCircle,
  Video, Code, HelpCircle, GitFork,
  Calendar
} from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/authStore'
import { useDeliveryStore } from '@/stores/deliveryStore'

const router = useRouter()
const authStore = useAuthStore()
const deliveryStore = useDeliveryStore()

const userName = computed(() => authStore.user?.username || '同学')

const resourceTypes = [
  {
    id: 'document',
    name: '系统文档',
    icon: FileText,
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
    description: '深度学习资料，系统化知识整理',
    url: '/factory?tab=professor'
  },
  {
    id: 'mindmap',
    name: '知识图谱',
    icon: GitFork,
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
    description: '可视化知识结构，掌握核心关联',
    url: '/factory?tab=architect'
  },
  {
    id: 'quiz',
    name: '实战测验',
    icon: HelpCircle,
    color: 'text-amber-500',
    bgColor: 'bg-amber-500/10',
    description: '随堂练习，检验学习成果',
    url: '/factory?tab=examiner'
  },
  {
    id: 'video',
    name: '视频教程',
    icon: Video,
    color: 'text-rose-500',
    bgColor: 'bg-rose-500/10',
    description: '生动讲解，直观理解概念',
    url: '/factory?tab=director'
  },
  {
    id: 'code',
    name: '代码实验',
    icon: Code,
    color: 'text-emerald-500',
    bgColor: 'bg-emerald-500/10',
    description: '动手实践，深入理解原理',
    url: '/factory?tab=hacker'
  },
]

const getResourceIcon = (type: string) => {
  switch (type) {
    case 'video': return Video
    case 'code': return Code
    case 'quiz': return HelpCircle
    default: return FileText
  }
}

const getResourceIconColor = (type: string) => {
  switch (type) {
    case 'video': return 'bg-rose-500/10 text-rose-500'
    case 'code': return 'bg-emerald-500/10 text-emerald-500'
    case 'quiz': return 'bg-amber-500/10 text-amber-500'
    default: return 'bg-blue-500/10 text-blue-500'
  }
}

const fallbackResources = [
  { title: 'Transformer 注意力机制', resource_type: 'document', description: '深入理解注意力机制的核心概念' },
  { title: '知识图谱导论', resource_type: 'mindmap', description: '可视化知识结构导图' },
  { title: '机器学习基础测试', resource_type: 'quiz', description: '3道选择题检验学习成果' },
  { title: 'Python 神经网络实战', resource_type: 'code', description: '动手实现简单的神经网络' },
]

onMounted(() => {
  deliveryStore.fetchAll()
})
</script>

<template>
  <div class="space-y-8 pb-10">
    <!-- 1. 顶部：欢迎标题 -->
    <section>
      <h1 class="text-4xl font-bold text-white tracking-tight">
        你好, {{ userName }} <span class="text-zinc-500 text-2xl font-normal">/ 准备好开始今天的学习了吗？</span>
      </h1>
    </section>

    <!-- 2. 中间主要内容：Bento 布局 -->
    <div class="grid grid-cols-12 gap-6">
      
      <!-- 左侧：知识图谱动态路由 (三阶段展示) -->
      <div class="col-span-12 lg:col-span-8 bg-[#131314] border border-[#303134] rounded-[2.5rem] p-8 relative overflow-hidden group">
        <div class="flex justify-between items-start mb-8">
          <div>
            <h3 class="text-xl font-bold text-white flex items-center gap-2">
              <BrainCircuit class="w-5 h-5 text-blue-500" />
              动态规划路径：人工智能导论
            </h3>
            <p class="text-zinc-500 text-sm mt-1">基础储备 → 核心模型 → 前沿进阶</p>
          </div>
          <Button variant="outline" class="rounded-xl border-[#303134] bg-transparent text-xs" @click="router.push('/path')">查看全量图谱</Button>
        </div>

        <!-- 三阶段节点展示 -->
        <div class="flex items-center justify-between px-16 py-10 relative">
          <!-- 背景连接线 -->
          <div class="absolute top-1/2 left-32 right-32 h-1 bg-gradient-to-r from-emerald-500/30 via-blue-500/50 to-zinc-700/30 -translate-y-1/2 z-0 rounded-full"></div>

          <!-- 阶段一：基础储备 -->
          <div class="flex flex-col items-center gap-4 z-10">
            <div class="w-14 h-14 rounded-full bg-emerald-600/20 border-2 border-emerald-500 flex items-center justify-center text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.3)]">
              <CheckCircle2 class="w-7 h-7" />
            </div>
            <div class="text-center">
              <span class="text-sm font-bold text-emerald-400">基础储备</span>
              <p class="text-[10px] text-zinc-500 mt-1">数学 · 编程 · 线代</p>
            </div>
          </div>

          <!-- 阶段二：核心模型 -->
          <div class="flex flex-col items-center gap-4 z-10">
            <div class="w-16 h-16 rounded-full bg-blue-600 border-4 border-blue-900/50 flex items-center justify-center text-white shadow-[0_0_30px_rgba(37,99,235,0.4)] animate-pulse">
              <BrainCircuit class="w-8 h-8" />
            </div>
            <div class="text-center">
              <span class="text-sm font-bold text-white underline underline-offset-4 decoration-blue-500">核心模型</span>
              <p class="text-[10px] text-zinc-500 mt-1">ML · DL · CV · NLP</p>
            </div>
          </div>

          <!-- 阶段三：前沿进阶 -->
          <div class="flex flex-col items-center gap-4 z-10 opacity-60">
            <div class="w-14 h-14 rounded-full bg-[#0b0b0b] border border-zinc-700 flex items-center justify-center text-zinc-500">
              <ChevronRight class="w-7 h-7" />
            </div>
            <div class="text-center">
              <span class="text-xs font-medium text-zinc-400">前沿进阶</span>
              <p class="text-[10px] text-zinc-600 mt-1">LLM · RAG · Agent</p>
            </div>
          </div>
        </div>

        <!-- 提示：路径设计说明 -->
        <div class="mt-8 bg-blue-500/5 border border-blue-500/10 rounded-2xl p-4 flex items-start gap-3">
          <AlertCircle class="w-5 h-5 text-blue-500 shrink-0 mt-0.5" />
          <p class="text-xs text-blue-200/70 leading-relaxed">
            按照三大阶段设计：数学编程打基础，机器学习学核心，大模型进前沿。
          </p>
        </div>
      </div>

      <!-- 右侧：内容制造车间状态 (Multi-Agent Status) -->
      <div class="col-span-12 lg:col-span-4 bg-[#131314] border border-[#303134] rounded-[2.5rem] p-8 flex flex-col">
        <h3 class="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <Sparkles class="w-5 h-5 text-purple-500" />
          内容制造车间
        </h3>

        <div class="grid grid-cols-2 gap-3 flex-1">
          <div
            v-for="resource in resourceTypes"
            :key="resource.id"
            @click="router.push(resource.url)"
            class="flex flex-col items-center justify-center gap-2 p-4 rounded-2xl bg-[#0b0b0b]/50 border border-[#303134] hover:border-zinc-700 hover:bg-[#0b0b0b] transition-all cursor-pointer group"
          >
            <div :class="`p-3 rounded-xl ${resource.bgColor} group-hover:scale-110 transition-transform`">
              <component :is="resource.icon" :class="`w-6 h-6 ${resource.color}`" />
            </div>
            <div class="text-center">
              <span class="text-xs font-medium text-zinc-300 group-hover:text-white transition-colors">{{ resource.name }}</span>
              <p class="text-[10px] text-zinc-500 mt-1 group-hover:text-zinc-400 transition-colors">{{ resource.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 下方左侧：资源推送预览 -->
      <div class="col-span-12 lg:col-span-4 bg-[#131314] border border-[#303134] rounded-[2.5rem] p-8 flex flex-col">
        <h3 class="text-lg font-bold text-white mb-6 flex items-center gap-2">
          <Calendar class="w-5 h-5 text-orange-500" />
          今日资源推荐
        </h3>

        <!-- 真实数据或 fallback 预览 -->
        <div class="space-y-3 flex-1">
          <template v-if="deliveryStore.todayResources.length > 0">
            <div
              v-for="(item, idx) in deliveryStore.todayResources.slice(0, 4)"
              :key="idx"
              @click="router.push('/delivery')"
              class="flex items-center gap-3 p-3 rounded-xl bg-[#0b0b0b] border border-[#202022] hover:border-zinc-700 transition-all cursor-pointer group"
            >
              <div :class="`p-2 rounded-lg ${getResourceIconColor(item.resource_type)}`">
                <component :is="getResourceIcon(item.resource_type)" class="w-4 h-4" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-bold text-zinc-200 truncate">{{ item.title }}</p>
                <p class="text-[10px] text-zinc-500">{{ item.resource_type }}</p>
              </div>
              <ChevronRight class="w-4 h-4 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
            </div>
          </template>
          <template v-else>
            <div
              v-for="(item, idx) in fallbackResources"
              :key="idx"
              @click="router.push('/delivery')"
              class="flex items-center gap-3 p-3 rounded-xl bg-[#0b0b0b] border border-[#202022] hover:border-zinc-700 transition-all cursor-pointer group"
            >
              <div :class="`p-2 rounded-lg ${getResourceIconColor(item.resource_type)}`">
                <component :is="getResourceIcon(item.resource_type)" class="w-4 h-4" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-bold text-zinc-200 truncate">{{ item.title }}</p>
                <p class="text-[10px] text-zinc-500">{{ item.description }}</p>
              </div>
              <ChevronRight class="w-4 h-4 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
            </div>
          </template>
        </div>

        <Button variant="outline" class="w-full mt-4 rounded-xl border-[#303134] bg-transparent text-xs" @click="router.push('/delivery')">
          查看全部资源
        </Button>
      </div>

      <!-- 下方右侧：学情诊断报告摘要 -->
      <div class="col-span-12 lg:col-span-8 bg-[#131314] border border-[#303134] rounded-[2.5rem] p-8 flex flex-col md:flex-row items-center gap-8">
        <div class="flex-1">
          <h3 class="text-xl font-bold text-white mb-2 underline decoration-blue-500 decoration-4 underline-offset-4">Assessor Agent 诊断</h3>
          <p class="text-zinc-400 text-sm leading-relaxed mb-6">
            本周你对线性代数的掌握程度提升了 <span class="text-emerald-500 font-bold">15%</span>，但在代码实操部分的"梯度爆炸"问题上停留超过 45 分钟。建议开启 <span class="text-blue-400">Tutor Agent</span> 专项答疑。
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