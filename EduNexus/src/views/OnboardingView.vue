<!-- src/views/OnboardingView.vue -->
<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  Check, ChevronRight, Sparkles, Send,
  BrainCircuit, Target, Clock, Cpu, User, Bot,
  Paperclip, X, RotateCcw, Save, Plus, MessageSquareQuote
} from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { submitOnboarding } from '@/api/profile'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

// 消息模型
interface Message {
  id: string
  role: 'agent' | 'user'
  content: string
  timestamp: Date
  options?: string[]
  attachments?: string[]
}

interface ProfileData {
  knowledge: string[]
  style: string[]
  goals: string[]
  time: string[]
  notes: string[]
}

const dimensions = [
  { id: 'knowledge', title: '知识基础', icon: BrainCircuit, question: '你好！我是 EduNexus 的首席破冰导师。很高兴能陪伴你开启这段学习旅程。首先，能告诉我你目前最擅长或已经接触过的领域吗？', options: ['Python 编程', '高等数学', '线性代数', '数据结构', '前端开发', '机器学习基础', '后端架构', '计算机网络'] },
  { id: 'style', title: '认知风格', icon: Cpu, question: '明白了。每个人学习的方式都不同，当你遇到一个全新的复杂概念时，哪种方式让你觉得最容易理解？', options: ['视觉驱动（图表与视频）', '代码实践（边写边学）', '理论推导（深挖底层原理）', '案例教学（从实际项目入手）'] },
  { id: 'goals', title: '学习目标', icon: Target, question: '目标是最好的指南针。你目前的学习重心是偏向考试突破，还是实际能力的提升？', options: ['期末考试保过', '考研/深造准备', '大厂求职实战', '兴趣驱动探索', '技能竞赛获奖'] },
  { id: 'time', title: '时间分布', icon: Clock, question: '最后，谈谈你的学习节奏吧。你通常习惯长时间沉浸，还是利用碎片化时间学习？', options: ['碎片化（单次 20min）', '沉浸式（单次 2h+）', '周末突击型', '每日定时定量'] }
]

const messages = ref<Message[]>([])
const currentStepIndex = ref(0)
const userInput = ref('')
const tempSelections = ref<string[]>([])
const isTyping = ref(false)
const isAnalyzing = ref(false)
const isReviewing = ref(false)
const isSubmitting = ref(false)
const submitError = ref('')
const scrollAnchor = ref<HTMLElement | null>(null)
const newTagInputs = ref<Record<string, string>>({})

const profileData = ref<ProfileData>({
  knowledge: [],
  style: [],
  goals: [],
  time: [],
  notes: []
})

// --- 自动滚动逻辑 ---
const scrollToBottom = () => {
  nextTick(() => {
    if (scrollAnchor.value) {
      scrollAnchor.value.scrollIntoView({ behavior: 'smooth', block: 'end' })
    }
  })
}

watch(() => messages.value.length, () => scrollToBottom())
watch(isTyping, (val) => { if (val) scrollToBottom() })

const agentSpeak = async (content: string, options?: string[]) => {
  isTyping.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  messages.value.push({ id: Date.now().toString(), role: 'agent', content, timestamp: new Date(), options: options || [] })
  isTyping.value = false
}

const toggleOption = (opt: string) => {
  const index = tempSelections.value.indexOf(opt)
  if (index > -1) tempSelections.value.splice(index, 1)
  else tempSelections.value.push(opt)
}

const handleSendMessage = async () => {
  if (isTyping.value) return
  const hasText = userInput.value.trim().length > 0
  const hasAttachments = tempSelections.value.length > 0
  const currentDimId = dimensions[currentStepIndex.value].id as keyof ProfileData
  
  if (!hasText && !hasAttachments) profileData.value[currentDimId].push(`默认`)
  if (hasAttachments) profileData.value[currentDimId] = [...new Set([...profileData.value[currentDimId], ...tempSelections.value])]
  if (hasText) {
    const text = userInput.value.trim()
    if (text.length > 15) profileData.value.notes.push(text)
    else profileData.value[currentDimId].push(text)
  }

  messages.value.push({
    id: Date.now().toString(),
    role: 'user',
    content: hasText ? userInput.value : `已选定${dimensions[currentStepIndex.value].title}`,
    attachments: [...tempSelections.value],
    timestamp: new Date()
  })

  userInput.value = ''
  tempSelections.value = []

  if (currentStepIndex.value < dimensions.length - 1) {
    currentStepIndex.value++
    await agentSpeak(dimensions[currentStepIndex.value].question, dimensions[currentStepIndex.value].options)
  } else {
    isAnalyzing.value = true
    await new Promise(resolve => setTimeout(resolve, 1500))
    isAnalyzing.value = false
    isReviewing.value = true
  }
}

const addTag = (dim: keyof ProfileData) => {
  const val = newTagInputs.value[dim]?.trim()
  if (val) {
    (profileData.value[dim] as string[]).push(val)
    newTagInputs.value[dim] = ''
  }
}

const removeTag = (dim: keyof ProfileData, idx: number) => {
  (profileData.value[dim] as string[]).splice(idx, 1)
}

const handleEnterSystem = async () => {
  if (isSubmitting.value) return
  isSubmitting.value = true
  submitError.value = ''
  try {
    const onboardingPayload = {
      responses: {
        knowledge_base: profileData.value.knowledge,
        cognitive_style: profileData.value.style,
        learning_goals: profileData.value.goals,
        time_distribution: profileData.value.time,
        notes: profileData.value.notes,
      },
    }
    await submitOnboarding(onboardingPayload)
    authStore.setOnboardingCompleted()
    router.push('/')
  } catch (e: any) {
    submitError.value = e?.response?.data?.detail || '画像提交失败，请重试'
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  agentSpeak(dimensions[0].question, dimensions[0].options)
})

const progressPercent = computed(() => ((currentStepIndex.value + 1) / dimensions.length) * 100)
</script>

<template>
  <div class="min-h-screen bg-[#060606] text-slate-200 flex flex-col items-center font-sans overflow-hidden relative">
    
    <!-- 背景层 (保持不变) -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none opacity-40">
      <div class="absolute top-[-10%] right-[-5%] w-[800px] h-[800px] bg-blue-600/10 blur-[150px] rounded-full"></div>
      <div class="absolute bottom-[-10%] left-[-5%] w-[800px] h-[800px] bg-indigo-600/10 blur-[150px] rounded-full"></div>
      <div class="absolute inset-0 bg-[linear-gradient(to_right,#80808008_1px,transparent_1px),linear-gradient(to_bottom,#80808008_1px,transparent_1px)] bg-[size:50px_50px]"></div>
    </div>

    <!-- 1. 对话阶段 -->
    <template v-if="!isReviewing">
      <!-- 固定的顶部进度条 -->
      <div class="w-full max-w-5xl z-20 px-6 pt-10 shrink-0">
        <div class="flex items-center justify-between mb-3 px-1">
          <div class="flex items-center gap-3">
            <Sparkles class="w-4 h-4 text-blue-400" />
            <span class="text-xs text-slate-400 uppercase tracking-[0.3em] font-bold">Ice-breaker Protocol</span>
          </div>
          <span class="text-[10px] text-slate-500 font-mono tracking-widest">{{ Math.round(progressPercent) }}% PROFILED</span>
        </div>
        <div class="h-[2px] w-full bg-slate-900 rounded-full overflow-hidden">
          <div class="h-full bg-gradient-to-r from-blue-600 to-indigo-400 transition-all duration-1000" :style="{ width: `${progressPercent}%` }"></div>
        </div>
      </div>

      <!-- 核心对话容器：整体向下对齐 -->
      <div class="flex-1 w-full max-w-6xl flex flex-col z-10 overflow-hidden justify-end">
        <ScrollArea class="flex-1">
          <!-- 这里使用 min-h-full 和 flex-col 让内部内容能撑开 -->
          <div class="flex flex-col min-h-[calc(100vh-200px)] px-8">
            <!-- 占位符：将内容推到底部 -->
            <div class="flex-1"></div>
            
            <div class="space-y-10 max-w-4xl mx-auto w-full py-8">
              <div v-for="msg in messages" :key="msg.id" 
                   :class="['flex w-full animate-in fade-in slide-in-from-bottom-4 duration-700', msg.role === 'user' ? 'justify-end' : 'justify-start']">
                <div :class="['flex gap-6 max-w-[90%]', msg.role === 'user' ? 'flex-row-reverse' : 'flex-row']">
                  <div :class="['w-11 h-11 rounded-2xl flex items-center justify-center shrink-0 border transition-all duration-500', 
                               msg.role === 'agent' ? 'bg-slate-950 border-blue-500/30 shadow-lg' : 'bg-blue-600 border-blue-400 shadow-xl shadow-blue-600/20']">
                    <Bot v-if="msg.role === 'agent'" class="w-6 h-6 text-blue-400" />
                    <User v-else class="w-6 h-6 text-white" />
                  </div>

                  <div :class="['flex flex-col gap-3', msg.role === 'user' ? 'items-end' : 'items-start']">
                    <div :class="['px-6 py-5 rounded-3xl text-[17px] leading-relaxed shadow-sm tracking-wide', 
                                 msg.role === 'agent' ? 'bg-slate-900/80 border border-white/5 text-slate-200 backdrop-blur-md' : 'bg-blue-600 text-white font-medium']">
                      {{ msg.content }}
                    </div>
                    <!-- 附件 -->
                    <div v-if="msg.attachments && msg.attachments.length > 0" class="flex flex-wrap gap-2 pt-1">
                      <div v-for="tag in msg.attachments" :key="tag" class="flex items-center gap-2 px-4 py-2 bg-slate-900/60 border border-white/10 rounded-xl text-xs text-slate-300 backdrop-blur-sm">
                        <Paperclip class="w-3.5 h-3.5 text-blue-400" /> {{ tag }}
                      </div>
                    </div>
                    <!-- 选项 -->
                    <div v-if="msg.role === 'agent' && msg.options && msg.options.length > 0 && messages[messages.length-1].id === msg.id" 
                         class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mt-4 w-full animate-in fade-in zoom-in-95 duration-500">
                      <button v-for="opt in msg.options" :key="opt" @click="toggleOption(opt)"
                        :class="['group relative p-5 rounded-2xl border transition-all duration-300 text-left',
                          tempSelections.includes(opt) ? 'bg-blue-600/10 border-blue-500 ring-1 ring-blue-500 shadow-lg shadow-blue-500/10' : 'bg-slate-900/40 border-slate-800 hover:border-slate-600 hover:bg-slate-900/60']">
                        <div class="flex items-center justify-between">
                          <span :class="['text-sm font-medium tracking-wide', tempSelections.includes(opt) ? 'text-blue-200' : 'text-slate-400 group-hover:text-slate-200']">{{ opt }}</span>
                          <div v-if="tempSelections.includes(opt)" class="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center animate-in zoom-in"><Check class="w-3 h-3 text-white" /></div>
                          <ChevronRight v-else class="w-4 h-4 text-slate-600 opacity-0 group-hover:opacity-100 transition-all group-hover:translate-x-1" />
                        </div>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <!-- Typing -->
              <div v-if="isTyping" class="flex justify-start animate-in fade-in duration-300">
                <div class="flex gap-6">
                  <div class="w-11 h-11 rounded-2xl bg-slate-950 border border-blue-500/30 flex items-center justify-center shadow-lg"><Bot class="w-6 h-6 text-blue-400" /></div>
                  <div class="px-6 py-5 rounded-3xl bg-slate-900/80 border border-white/5 flex gap-1.5 backdrop-blur-md">
                    <span class="w-2 h-2 bg-blue-500/60 rounded-full animate-bounce"></span>
                    <span class="w-2 h-2 bg-blue-500/60 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                    <span class="w-2 h-2 bg-blue-500/60 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                  </div>
                </div>
              </div>
              <!-- 锚点 -->
              <div ref="scrollAnchor" class="h-2 w-full"></div>
            </div>
          </div>
        </ScrollArea>

        <!-- 底部输入区：现在它和上面的消息紧挨着，共同在底部对齐 -->
        <div class="px-8 pb-10 pt-2 bg-gradient-to-t from-[#060606] via-[#060606] to-transparent shrink-0">
          <div class="max-w-4xl mx-auto">
            <div v-if="tempSelections.length > 0" class="flex flex-wrap gap-2 mb-4 animate-in slide-in-from-bottom-2">
              <div v-for="sel in tempSelections" :key="sel" class="flex items-center gap-2 px-4 py-2 bg-blue-600/20 border border-blue-500/40 rounded-xl text-xs text-blue-200 shadow-lg backdrop-blur-md">
                <Paperclip class="w-3.5 h-3.5" /> {{ sel }}
                <button @click="toggleOption(sel)" class="hover:text-white ml-1 p-0.5 rounded-full hover:bg-blue-500/30 transition-colors"><X class="w-3 h-3" /></button>
              </div>
            </div>
            <div class="relative group">
              <div class="absolute -inset-1 bg-gradient-to-r from-blue-600/20 via-indigo-500/20 to-purple-600/20 rounded-[24px] blur-xl opacity-0 group-focus-within:opacity-100 transition duration-1000"></div>
              <div class="relative flex items-center bg-slate-900/80 border border-white/10 rounded-3xl px-6 py-4 backdrop-blur-2xl shadow-2xl">
                <input v-model="userInput" placeholder="与导师进一步交流，或点击上方选项直接回车..." class="bg-transparent border-none focus:ring-0 text-slate-200 w-full placeholder:text-slate-700 text-lg outline-none font-light" @keyup.enter="handleSendMessage" />
                <Button size="icon" :class="['ml-4 w-12 h-12 rounded-2xl transition-all duration-500 shadow-lg', (userInput.trim() || tempSelections.length > 0) ? 'bg-blue-600 text-white hover:bg-blue-500' : 'bg-slate-800 text-slate-500 cursor-not-allowed']" @click="handleSendMessage">
                  <Send class="w-5 h-5" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 2. 画像预览阶段 (保持您满意的尺寸) -->
    <template v-else>
      <div class="flex-1 w-full max-w-7xl z-20 flex flex-col p-8 animate-in fade-in zoom-in-95 duration-700 overflow-hidden">
        <div class="text-center mt-4 mb-8 space-y-3">
          <div class="inline-flex items-center gap-2 px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full">
            <Sparkles class="w-3 h-3 text-blue-400" />
            <span class="text-[10px] font-bold text-blue-400 tracking-widest uppercase">Profile Verification</span>
          </div>
          <h2 class="text-4xl font-semibold text-white tracking-tight">确认您的学习基因</h2>
          <p class="text-slate-400 text-base font-light">您可以快速增减标签，完善您的个性化学习画像。</p>
        </div>

        <ScrollArea class="flex-1 px-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <div v-for="dim in dimensions" :key="dim.id" class="bg-slate-900/40 border border-white/5 backdrop-blur-xl p-6 rounded-2xl flex flex-col min-h-[260px] group transition-all hover:border-white/10 hover:bg-slate-900/60">
              <div class="flex items-center gap-3 mb-5">
                <div class="p-2.5 bg-slate-950 rounded-xl border border-white/5 shadow-inner">
                  <component :is="dim.icon" class="w-5 h-5 text-blue-400" />
                </div>
                <h4 class="text-base font-medium text-slate-200">{{ dim.title }}</h4>
              </div>
              <div class="flex flex-wrap gap-2 mb-4 flex-1 content-start">
                <Badge v-for="(tag, idx) in profileData[dim.id as keyof ProfileData]" :key="idx" 
                       variant="secondary" class="px-2.5 py-1.5 bg-slate-800/80 border border-white/5 text-slate-300 rounded-md text-[12px] group/tag transition-all hover:bg-slate-700">
                  {{ tag }}
                  <X @click="removeTag(dim.id as keyof ProfileData, idx)" class="ml-2 w-3 h-3 cursor-pointer text-red-500 opacity-0 group-hover/tag:opacity-100 transition-all" />
                </Badge>
              </div>
              <div class="mt-auto flex items-center gap-2">
                <Input v-model="newTagInputs[dim.id]" placeholder="添加特征..." class="bg-slate-950/50 border-slate-800 rounded-lg h-9 text-[12px] focus:ring-1 focus:ring-blue-500/50" @keyup.enter="addTag(dim.id as keyof ProfileData)" />
                <Button size="icon" variant="secondary" class="h-9 w-9 shrink-0 rounded-lg hover:bg-blue-600 hover:text-white transition-colors" @click="addTag(dim.id as keyof ProfileData)">
                  <Plus class="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>

          <div class="bg-slate-900/40 border border-white/5 backdrop-blur-xl p-7 rounded-2xl mb-6 transition-all hover:border-white/10">
             <div class="flex items-center gap-3 mb-5">
              <div class="p-2.5 bg-slate-950 rounded-xl border border-white/5">
                <MessageSquareQuote class="w-5 h-5 text-indigo-400" />
              </div>
              <h4 class="text-base font-medium text-slate-200">个性化偏好补充</h4>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
              <div v-for="(note, idx) in profileData.notes" :key="idx" class="relative p-4 bg-slate-950/40 border border-white/5 rounded-xl text-[13px] text-slate-400 italic leading-relaxed group/note">
                "{{ note }}"
                <X @click="profileData.notes.splice(idx, 1)" class="absolute top-3 right-3 w-3.5 h-3.5 cursor-pointer text-red-500 opacity-0 group-hover/note:opacity-100 transition-all" />
              </div>
              <div v-if="profileData.notes.length === 0" class="text-slate-600 italic text-sm py-10 text-center border border-dashed border-slate-800 rounded-xl">
                暂无额外备注。
              </div>
            </div>
            <div class="flex gap-3">
              <Input v-model="newTagInputs['notes']" placeholder="补充更多个性化描述..." class="bg-slate-950/50 border-slate-800 rounded-xl h-12 text-sm" @keyup.enter="addTag('notes')" />
              <Button variant="secondary" class="h-12 px-6 rounded-xl text-xs font-bold" @click="addTag('notes')">添加描述</Button>
            </div>
          </div>
        </ScrollArea>

        <div class="flex items-center justify-center gap-6 py-6 mt-auto border-t border-white/5 shrink-0">
          <Button variant="ghost" @click="isReviewing = false; currentStepIndex = 0; messages = []; agentSpeak(dimensions[0].question, dimensions[0].options)" 
                  class="h-14 px-8 rounded-xl text-slate-500 hover:text-white transition-all text-sm">
            <RotateCcw class="w-4 h-4 mr-2" /> 重新开始
          </Button>
          <Button @click="handleEnterSystem" :disabled="isSubmitting" class="h-14 px-12 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold text-base shadow-xl shadow-blue-600/20 active:scale-95 transition-all disabled:opacity-50">
            {{ isSubmitting ? '正在保存...' : '这就是我的学习基因，进入系统' }} <Save class="ml-2 w-5 h-5" />
          </Button>
        </div>
      </div>
    </template>

    <!-- 分析遮罩 (保持不变) -->
    <div v-if="isAnalyzing" class="fixed inset-0 z-50 bg-[#060606]/95 backdrop-blur-2xl flex flex-col items-center justify-center p-6 text-center animate-in fade-in duration-500">
      <div class="relative mb-8 scale-110">
        <div class="w-24 h-24 border-2 border-blue-500/10 rounded-full"></div>
        <div class="absolute inset-0 w-24 h-24 border-2 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
        <count-sparkles class="absolute inset-0 m-auto w-8 h-8 text-blue-400 animate-pulse" />
      </div>
      <h3 class="text-2xl font-light text-slate-50 mb-3 tracking-tight">正在构建学习基因画像...</h3>
      <p class="text-slate-500 text-xs font-light">Neuro-Processing Engine Active</p>
    </div>

  </div>
</template>

<style scoped>
:deep([data-radix-scroll-area-viewport]) {
  scrollbar-width: none;
  -ms-overflow-style: none;
  display: flex;
  flex-direction: column;
}
:deep([data-radix-scroll-area-viewport]::-webkit-scrollbar) {
  display: none;
}

input::placeholder {
  font-weight: 300;
  letter-spacing: 0.05em;
  opacity: 0.4;
}
</style>