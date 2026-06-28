<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Sparkles, ArrowRight, BrainCircuit,
  Target, Clock, Cpu, Layers, Microscope
} from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { useProfileStore } from '@/stores/profileStore'
import type { ProfileDimensions } from '@/types/profile'

const router = useRouter()
const profileStore = useProfileStore()

const isVisible = ref(false)

// Demo fallback data for offline/demo mode
const demoProfile: ProfileDimensions = {
  knowledge_base_score: 72,
  cognitive_style: '文档阅读型',
  error_preference: '适度试错型',
  learning_goals: '掌握 Transformer 架构与 LLM 原理，进阶 AI 工程师',
  focus_duration: 45,
  stress_resistance: 78,
}

const profile = computed<ProfileDimensions>(() => {
  return profileStore.profileData ?? demoProfile
})

function getKnowledgeLevel(score: number): string {
  if (score >= 80) return '扎实 · 可直接进入进阶学习'
  if (score >= 60) return '良好 · 具备核心基础，个别领域可加强'
  if (score >= 40) return '一般 · 建议从基础模块系统学习'
  return '薄弱 · 适合从头构建知识体系'
}

function getFocusLevel(minutes: number): string {
  if (minutes >= 60) return '深度专注型 · 适合长时段深度学习'
  if (minutes >= 30) return '中等专注型 · 适合分段式学习'
  return '短时高效型 · 适合微学习模块'
}

function getResearchDepth(score: number): string {
  if (score >= 80) return '前沿探索型 · 具备独立研究能力，可挑战顶会论文'
  if (score >= 60) return '深入理解型 · 能复现经典模型，追踪前沿动态'
  if (score >= 40) return '应用导向型 · 注重工程落地，适合项目驱动学习'
  return '入门探索型 · 建议先夯实基础再深入'
}

// Dimension display config
const dimensionConfig = computed(() => [
  {
    key: 'knowledge_base_score',
    title: '知识基础',
    subtitle: 'Knowledge Base',
    icon: BrainCircuit,
    color: 'blue',
    score: profile.value.knowledge_base_score,
    maxScore: 100,
    type: 'gauge' as const,
    description: getKnowledgeLevel(profile.value.knowledge_base_score),
    tags: ['Python编程', '线性代数', '数据结构基础'],
  },
  {
    key: 'cognitive_style',
    title: '认知风格',
    subtitle: 'Cognitive Style',
    icon: Cpu,
    color: 'purple',
    value: '文档阅读型 — 偏好通过系统化文档与教程进行学习，善于从结构化材料中提取知识框架',
    type: 'text' as const,
  },
  {
    key: 'learning_goals',
    title: '学习目标',
    subtitle: 'Learning Goals',
    icon: Target,
    color: 'emerald',
    value: (profile.value.learning_goals) + ' · 实习 · 竞赛',
    type: 'text' as const,
  },
  {
    key: 'focus_duration',
    title: '专注时长',
    subtitle: 'Focus Duration',
    icon: Clock,
    color: 'cyan',
    score: profile.value.focus_duration,
    maxScore: 90,
    unit: '分钟',
    type: 'gauge' as const,
    description: getFocusLevel(profile.value.focus_duration),
  },
  {
    key: 'tech_preference',
    title: '技术偏好',
    subtitle: 'Tech Stack',
    icon: Layers,
    color: 'orange',
    value: 'Python 技术栈为主，熟悉 PyTorch 深度学习框架，正在学习 Transformer 与 LangChain 生态',
    type: 'text' as const,
  },
  {
    key: 'research_depth',
    title: '研究深度',
    subtitle: 'Research Depth',
    icon: Microscope,
    color: 'teal',
    score: 65,
    maxScore: 100,
    type: 'gauge' as const,
    description: getResearchDepth(65),
  },
])

const colorMap: Record<string, { bg: string; border: string; text: string; ring: string; bar: string }> = {
  blue:    { bg: 'bg-blue-500/5',   border: 'border-blue-500/20',   text: 'text-blue-400',    ring: 'stroke-blue-500',    bar: 'bg-blue-500' },
  purple:  { bg: 'bg-purple-500/5', border: 'border-purple-500/20', text: 'text-purple-400',  ring: 'stroke-purple-500',  bar: 'bg-purple-500' },
  emerald: { bg: 'bg-emerald-500/5',border: 'border-emerald-500/20',text: 'text-emerald-400', ring: 'stroke-emerald-500', bar: 'bg-emerald-500' },
  cyan:    { bg: 'bg-cyan-500/5',   border: 'border-cyan-500/20',   text: 'text-cyan-400',    ring: 'stroke-cyan-500',    bar: 'bg-cyan-500' },
  orange:  { bg: 'bg-orange-500/5', border: 'border-orange-500/20', text: 'text-orange-400',  ring: 'stroke-orange-500',  bar: 'bg-orange-500' },
  teal:    { bg: 'bg-teal-500/5',   border: 'border-teal-500/20',   text: 'text-teal-400',    ring: 'stroke-teal-500',    bar: 'bg-teal-500' },
}

// Gauge ring calculation
function gaugeRadius(score: number, max: number): number {
  return (score / max) * 100
}

// Particle data for celebration effect
const particles = Array.from({ length: 30 }, (_, i) => ({
  id: i,
  x: Math.random() * 100,
  delay: Math.random() * 3,
  duration: 2 + Math.random() * 3,
  size: 2 + Math.random() * 4,
  color: ['#3b82f6', '#8b5cf6', '#10b981', '#06b6d4', '#f97316', '#14b8a6'][i % 6],
}))

onMounted(() => {
  requestAnimationFrame(() => {
    isVisible.value = true
  })
})

function enterSystem() {
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen bg-[#060606] text-slate-200 flex flex-col items-center font-sans overflow-hidden relative">

    <!-- 背景层 -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-[-15%] left-[-10%] w-[900px] h-[900px] bg-blue-600/8 blur-[180px] rounded-full"></div>
      <div class="absolute bottom-[-15%] right-[-10%] w-[900px] h-[900px] bg-purple-600/8 blur-[180px] rounded-full"></div>
      <div class="absolute top-[30%] left-[40%] w-[500px] h-[500px] bg-teal-600/5 blur-[150px] rounded-full"></div>
      <div class="absolute inset-0 bg-[linear-gradient(to_right,#80808006_1px,transparent_1px),linear-gradient(to_bottom,#80808006_1px,transparent_1px)] bg-[size:60px_60px]"></div>
    </div>

    <!-- 庆祝粒子 -->
    <div class="fixed inset-0 pointer-events-none z-10">
      <div
        v-for="p in particles"
        :key="p.id"
        class="absolute rounded-full animate-float"
        :style="{
          left: p.x + '%',
          top: '-10px',
          width: p.size + 'px',
          height: p.size + 'px',
          backgroundColor: p.color,
          animationDelay: p.delay + 's',
          animationDuration: p.duration + 's',
          opacity: 0,
        }"
      ></div>
    </div>

    <!-- 主内容 -->
    <div class="relative z-20 w-full max-w-6xl mx-auto px-6 py-10 flex flex-col items-center">

      <!-- ===== 1. 顶部：祝贺标题 ===== -->
      <div
        :class="[
          'text-center space-y-5 mb-12 transition-all duration-1000',
          isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
        ]"
      >
        <div class="inline-flex items-center gap-2 px-4 py-1.5 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-teal-500/10 border border-blue-500/20 rounded-full">
          <Sparkles class="w-3.5 h-3.5 text-blue-400 animate-pulse" />
          <span class="text-[10px] font-bold text-blue-300 tracking-[0.3em] uppercase">AI Analysis Complete</span>
          <Sparkles class="w-3.5 h-3.5 text-purple-400 animate-pulse" />
        </div>

        <div class="space-y-3">
          <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight">
            <span class="bg-gradient-to-r from-blue-400 via-purple-400 to-teal-400 bg-clip-text text-transparent">
              你的学习基因已构建完成
            </span>
          </h1>
          <p class="text-zinc-500 text-lg font-light max-w-xl mx-auto">
            AI 深度分析了你的学习偏好、知识储备与认知特征，为你量身打造专属学习画像
          </p>
        </div>
      </div>

      <!-- ===== 2. 主卡片：6 维画像 ===== -->
      <div
        :class="[
          'w-full bg-[#0d0d0e] border border-[#202022] rounded-[3rem] p-8 md:p-10 mb-10 transition-all duration-1000 delay-300',
          'shadow-2xl shadow-blue-500/5',
          isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
        ]"
      >
        <!-- 6 维卡片网格 -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          <div
            v-for="(dim, idx) in dimensionConfig"
            :key="dim.key"
            :class="[
              'relative rounded-2xl border p-5 transition-all duration-700',
              'hover:scale-[1.02] hover:shadow-lg',
              colorMap[dim.color].bg,
              colorMap[dim.color].border,
              isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6',
            ]"
            :style="{ transitionDelay: (400 + idx * 100) + 'ms' }"
          >
            <div :class="['absolute top-0 right-0 w-16 h-16 rounded-bl-2xl -mr-2 -mt-2 opacity-30', colorMap[dim.color].bg]"></div>

            <!-- 头部 -->
            <div class="flex items-center gap-2.5 mb-4 relative z-10">
              <div :class="['p-2 rounded-xl border', colorMap[dim.color].bg, colorMap[dim.color].border]">
                <component :is="dim.icon" :class="['w-4 h-4', colorMap[dim.color].text]" />
              </div>
              <div>
                <p class="text-sm font-semibold text-white">{{ dim.title }}</p>
                <p class="text-[9px] text-zinc-600 uppercase tracking-wider">{{ dim.subtitle }}</p>
              </div>
            </div>

            <!-- Gauge 类型 -->
            <template v-if="dim.type === 'gauge'">
              <div class="flex items-end gap-4 relative z-10">
                <div class="relative w-20 h-20 shrink-0">
                  <svg class="w-20 h-20 -rotate-90" viewBox="0 0 64 64">
                    <circle cx="32" cy="32" r="28" fill="none" stroke="currentColor" class="text-zinc-800" stroke-width="5" />
                    <circle
                      cx="32" cy="32" r="28"
                      fill="none"
                      :class="colorMap[dim.color].ring"
                      stroke-width="5"
                      stroke-linecap="round"
                      :stroke-dasharray="(gaugeRadius(dim.score!, dim.maxScore!) / 100) * 175.93 + ' ' + (175.93 - (gaugeRadius(dim.score!, dim.maxScore!) / 100) * 175.93)"
                      class="transition-all duration-[1500ms] ease-out"
                    />
                  </svg>
                  <div class="absolute inset-0 flex flex-col items-center justify-center">
                    <span :class="['text-xl font-bold', colorMap[dim.color].text]">{{ dim.score }}</span>
                    <span v-if="dim.unit" class="text-[8px] text-zinc-500 -mt-0.5">{{ dim.unit }}</span>
                  </div>
                </div>
                <div class="flex-1 pb-1">
                  <p class="text-xs font-medium text-zinc-300">{{ dim.description }}</p>
                  <div class="mt-2 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                    <div
                      :class="['h-full rounded-full shadow-[0_0_8px_currentColor] transition-all duration-[1500ms] ease-out', colorMap[dim.color].bar]"
                      :style="{ width: gaugeRadius(dim.score!, dim.maxScore!) + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
              <!-- 知识标签 -->
              <div v-if="dim.tags" class="flex flex-wrap gap-1.5 mt-3 relative z-10">
                <span
                  v-for="tag in dim.tags"
                  :key="tag"
                  :class="['px-2.5 py-0.5 text-[10px] rounded-md border', colorMap[dim.color].bg, colorMap[dim.color].border, colorMap[dim.color].text]"
                >{{ tag }}</span>
              </div>
            </template>

            <!-- Text 类型 -->
            <template v-else>
              <div class="relative z-10">
                <p :class="['text-sm font-medium leading-relaxed', colorMap[dim.color].text]">
                  {{ dim.value }}
                </p>
                <div class="mt-3 flex items-center gap-1.5">
                  <span class="w-1 h-1 rounded-full bg-zinc-600"></span>
                  <span class="text-[10px] text-zinc-600">AI 自动识别</span>
                </div>
              </div>
            </template>
          </div>
        </div>

        <!-- 底部 AI 洞察总结 -->
        <div class="mt-8 p-5 bg-gradient-to-r from-blue-500/5 via-transparent to-teal-500/5 border border-white/5 rounded-2xl">
          <p class="text-xs text-zinc-500 uppercase tracking-wider mb-2">AI 综合洞察</p>
          <p class="text-sm text-zinc-400 leading-relaxed">
            基于你的 <span class="text-blue-300 font-medium">{{ profile.knowledge_base_score }}分</span> 知识基础与
            <span class="text-purple-300 font-medium">{{ profile.cognitive_style }}</span> 认知偏好，
            系统已自动生成 <span class="text-cyan-300 font-medium">自适应学习路径</span> 与
            <span class="text-emerald-300 font-medium">专属内容推荐</span>。
            你的 Python 和数据结构基础扎实，建议在<span class="text-white">实习项目</span>和<span class="text-white">学科竞赛</span>中强化实战能力。
          </p>
        </div>
      </div>

      <!-- ===== 3. 底部 CTA ===== -->
      <div
        :class="[
          'text-center space-y-5 transition-all duration-1000 delay-[1200ms]',
          isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
        ]"
      >
        <Button
          @click="enterSystem"
          class="h-16 px-14 text-lg font-bold rounded-2xl bg-gradient-to-r from-blue-600 via-blue-500 to-purple-600 hover:from-blue-500 hover:via-blue-400 hover:to-purple-500 text-white shadow-2xl shadow-blue-500/30 hover:shadow-blue-400/40 transition-all duration-500 active:scale-95 group"
        >
          <Sparkles class="w-5 h-5 mr-3 group-hover:animate-spin" />
          进入 EduNexus
          <ArrowRight class="w-5 h-5 ml-3 group-hover:translate-x-1.5 transition-transform" />
        </Button>
        <p class="text-zinc-600 text-xs">
          点击进入系统，AI 将自动为你规划专属学习路径
        </p>
      </div>

    </div>
  </div>
</template>

<style scoped>
@keyframes float-up {
  0% {
    transform: translateY(0) scale(1);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 0;
  }
  100% {
    transform: translateY(-100vh) scale(0.5);
    opacity: 0;
  }
}

.animate-float {
  animation: float-up linear infinite;
}
</style>
