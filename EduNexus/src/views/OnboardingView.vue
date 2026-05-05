<!-- src/views/OnboardingView.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Check, ChevronRight, MessageSquare, Sparkles, Send, BrainCircuit, Target, Clock, Cpu } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'

const router = useRouter()

// 维度定义
const steps = [
  {
    id: 'knowledge',
    title: '知识基础',
    question: '你好！我是你的教育导师。在开始旅程前，告诉我你目前最擅长或已经接触过的领域？',
    description: '这能帮助我为你匹配最合适的课程深度与难度。',
    icon: BrainCircuit,
    options: ['Python 编程', '高等数学', '线性代数', '数据结构', '前端开发', '机器学习基础', '后端架构', '自动化测试', '计算机网络']
  },
  {
    id: 'style',
    title: '认知风格',
    question: '当你学习新概念时，哪种方式让你觉得最轻松？',
    description: '不同的认知偏好决定了我会为你生成的教学内容形式。',
    icon: Cpu,
    options: ['视觉驱动（图表与视频）', '代码实践（边写边学）', '理论推导（深入底层原理）', '案例教学（从实际项目入手）']
  },
  {
    id: 'goals',
    title: '学习目标',
    question: '设定一个明确的目标能让我们走得更远，你现在的重心是？',
    description: '目标是智能体优化路径的核心权重。',
    icon: Target,
    options: ['期末考试保过', '考研/深造准备', '大厂求职实战', '兴趣驱动探索', '技能竞赛获奖', '零基础快速上手']
  },
  {
    id: 'time',
    title: '时间分布',
    question: '你的学习节奏通常是怎样的？',
    description: '我会根据你的时间碎片程度推送任务。',
    icon: Clock,
    options: ['碎片化（单次 20min）', '沉浸式（单次 2h+）', '周末突击型', '每日定时定量', '不定期弹性学习']
  }
]

const currentStepIndex = ref(0)
const selectedOptions = ref<string[]>([])
const customInput = ref('')
const isAnalyzing = ref(false)
const currentStep = computed(() => steps[currentStepIndex.value])
const progressPercent = computed(() => ((currentStepIndex.value + 1) / steps.length) * 100)

const toggleOption = (opt: string) => {
  const index = selectedOptions.value.indexOf(opt)
  if (index > -1) {
    selectedOptions.value.splice(index, 1)
  } else {
    selectedOptions.value.push(opt)
  }
}

const handleNext = () => {
  if (currentStepIndex.value < steps.length - 1) {
    currentStepIndex.value++
    selectedOptions.value = []
    customInput.value = ''
  } else {
    isAnalyzing.value = true
    setTimeout(() => {
      router.push('/') 
    }, 2800)
  }
}

const getClass = (...classes: any[]) => classes.filter(Boolean).join(' ')
</script>

<template>
  <div class="min-h-screen bg-[#060606] text-slate-200 flex flex-col items-center justify-center p-6 font-sans overflow-hidden relative">
    
    <!-- 背景层 (类 Login 界面的高级感设计) -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <!-- 动态渐变球 -->
      <div class="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-blue-600/10 blur-[120px] rounded-full animate-pulse"></div>
      <div class="absolute bottom-[-10%] left-[-5%] w-[600px] h-[600px] bg-purple-600/10 blur-[150px] rounded-full"></div>
      
      <!-- 网格纹理 -->
      <div class="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay"></div>
      <div class="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>
    </div>

    <div class="w-full max-w-4xl z-10 transition-all duration-500">
      
      <!-- 顶部进度与标题 -->
      <div class="mb-16 space-y-4">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-slate-900 rounded-lg border border-slate-800">
            <component :is="currentStep.icon" class="w-5 h-5 text-blue-400" />
          </div>
          <div class="flex-1">
            <div class="flex justify-between text-[11px] text-slate-500 uppercase tracking-[0.3em] font-bold mb-2">
              <span>Dimension: {{ currentStep.title }}</span>
              <span>Step {{ currentStepIndex + 1 }} / {{ steps.length }}</span>
            </div>
            <div class="h-[3px] w-full bg-slate-900 rounded-full overflow-hidden">
              <div 
                class="h-full bg-gradient-to-r from-blue-600 to-indigo-400 transition-all duration-1000 ease-in-out shadow-[0_0_10px_rgba(37,99,235,0.5)]" 
                :style="{ width: `${progressPercent}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="!isAnalyzing" class="space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
        <!-- Agent 对话区 (更显著、更大) -->
        <div class="flex items-start gap-8">
          <div class="relative group">
            <div class="absolute -inset-1 bg-gradient-to-tr from-blue-600 to-cyan-400 rounded-2xl blur opacity-30 group-hover:opacity-60 transition duration-500"></div>
            <div class="relative w-16 h-16 rounded-2xl bg-slate-950 flex items-center justify-center shrink-0 border border-white/10">
              <Sparkles class="w-8 h-8 text-blue-400" />
            </div>
          </div>
          <div class="space-y-4">
            <h2 class="text-4xl font-semibold text-slate-50 leading-[1.2] tracking-tight">
              {{ currentStep.question }}
            </h2>
            <p class="text-slate-400 text-lg font-light leading-relaxed max-w-2xl">
              {{ currentStep.description }}
            </p>
          </div>
        </div>

        <!-- 选项卡片 (Grid 间距加大，卡片更大) -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
          <button
            v-for="(opt, index) in currentStep.options"
            :key="opt"
            @click="toggleOption(opt)"
            :style="{ animationDelay: `${index * 50}ms` }"
            :class="getClass(
              'group relative p-6 rounded-2xl border text-left transition-all duration-300 animate-in fade-in zoom-in-95',
              selectedOptions.includes(opt) 
                ? 'bg-blue-600/10 border-blue-500/60 ring-1 ring-blue-500/60 shadow-[0_0_30px_rgba(37,99,235,0.1)]' 
                : 'bg-slate-900/40 border-slate-800/50 hover:border-slate-600 hover:bg-slate-800/40'
            )"
          >
            <div class="flex justify-between items-start">
              <span :class="getClass('text-base font-medium tracking-wide transition-colors', selectedOptions.includes(opt) ? 'text-blue-300' : 'text-slate-300 group-hover:text-slate-100')">
                {{ opt }}
              </span>
              <div v-if="selectedOptions.includes(opt)" class="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center shadow-lg">
                <Check class="w-3 h-3 text-white" />
              </div>
            </div>
          </button>
        </div>

        <!-- 输入框 (更长、更精致) -->
        <div class="relative group mt-12">
          <div class="absolute -inset-0.5 bg-gradient-to-r from-blue-500/30 via-indigo-500/30 to-purple-500/30 rounded-2xl blur-md opacity-0 group-focus-within:opacity-100 transition duration-700"></div>
          <div class="relative flex items-center bg-slate-900/60 border border-white/5 rounded-2xl px-6 py-4 backdrop-blur-xl">
            <MessageSquare class="w-6 h-6 text-slate-500 mr-4" />
            <input 
              v-model="customInput"
              placeholder="或者用你自己的方式描述..."
              class="bg-transparent border-none focus:ring-0 text-slate-100 w-full placeholder:text-slate-600 text-lg h-12 outline-none font-light"
              @keyup.enter="handleNext"
            />
            <Button 
              size="icon" 
              variant="ghost" 
              class="ml-2 w-12 h-12 rounded-xl hover:bg-blue-500/20 text-blue-400 transition-all"
              @click="handleNext"
            >
              <Send class="w-5 h-5" />
            </Button>
          </div>
        </div>

        <!-- 底部导航 -->
        <div class="flex justify-end items-center pt-8 gap-6">
          <span class="text-slate-600 text-sm font-light italic">按 Enter 键快速继续</span>
          <Button 
            @click="handleNext"
            class="bg-white text-black hover:bg-slate-200 px-12 py-8 rounded-2xl font-bold text-lg group shadow-2xl shadow-blue-500/10 transition-all active:scale-95"
          >
            下一步
            <ChevronRight class="ml-2 w-6 h-6 group-hover:translate-x-1 transition-transform" />
          </Button>
        </div>
      </div>

      <!-- 分析中状态 -->
      <div v-else class="flex flex-col items-center justify-center py-32 space-y-10 animate-in fade-in duration-1000">
        <div class="relative">
          <div class="w-32 h-32 border-[2px] border-blue-500/10 rounded-full"></div>
          <div class="absolute inset-0 w-32 h-32 border-[2px] border-blue-500 rounded-full border-t-transparent animate-[spin_1.5s_linear_infinite]"></div>
          <div class="absolute inset-0 w-32 h-32 border-[2px] border-purple-500 rounded-full border-b-transparent animate-[spin_2s_linear_infinite_reverse] opacity-50"></div>
          <Sparkles class="absolute inset-0 m-auto w-12 h-12 text-blue-400 animate-pulse" />
        </div>
        <div class="text-center space-y-4">
          <h3 class="text-3xl font-medium text-slate-50 tracking-tight">正在构建多代理学习画像</h3>
          <p class="text-slate-500 max-w-md mx-auto text-lg font-light leading-relaxed">
            基于导师对话，我们正在为您分配最优的学习路径、交互逻辑与反馈模型...
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 针对 Tailwind 不包含的动画进行微调 */
@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin-slow {
  animation: spin-slow 8s linear infinite;
}

input::placeholder {
  transition: opacity 0.3s ease;
}

input:focus::placeholder {
  opacity: 0.3;
}
</style>