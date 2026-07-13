<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import {
  Network,
  Sparkles,
  Zap,
  Info,
  RefreshCw,
  X,
  Search,
  CheckCircle2,
  PlayCircle
} from 'lucide-vue-next'
import PhaseGraph from './components/PhaseGraph.vue'
import { Button } from '@/components/ui/button'
import { useLearningStore } from '@/stores/learningStore'
import type { KnowledgeNode } from '@/types/graph'

const learningStore = useLearningStore()

const customGoal = ref('人工智能')
const showAnalysis = ref(true)

const isPlanning = computed(() => learningStore.isPlanning)
const phases = computed(() => learningStore.phases)
const activePhaseId = ref<string>('')

const analysisSummary = computed(() => learningStore.analysisSummary)

const handlePlan = () => {
  if (!customGoal.value) return
  showAnalysis.value = true
  learningStore.plan(customGoal.value)
  console.log("Nodes count:", learningStore.nodes.length)
  console.log("Phases count:", learningStore.phases.length)
}

const closeAnalysis = () => {
  showAnalysis.value = false
}

const selectPhase = (phaseId: string) => {
  activePhaseId.value = phaseId
  learningStore.selectPhase(phaseId)
}

const hasInjectedNodes = (nodes: KnowledgeNode[]) => {
  return nodes.some(n => n.type === 'injected')
}

onMounted(() => {
  handlePlan()
})

// 监听phases变化，默认选中第一个阶段
watch(phases, (newPhases: any[]) => {
  if (newPhases.length > 0 && !activePhaseId.value) {
    activePhaseId.value = newPhases[0].id
    learningStore.selectPhase(newPhases[0].id)
  }
}, { immediate: true })
</script>

<template>
  <div class="flex flex-col h-full bg-[#0b0b0b] text-slate-200 overflow-hidden font-sans">
    <!-- 顶部导航 & 规划输入框 -->
    <header class="p-4 border-b border-white/5 bg-[#0d0d0d] flex items-center justify-between z-30 shadow-2xl">
      <div class="flex items-center gap-4">
        <div class="p-2 bg-blue-600/20 rounded-lg border border-blue-500/30">
          <Network class="h-5 w-5 text-blue-400" />
        </div>
        <div>
          <h2 class="text-sm font-bold tracking-tight">智能路径规划引擎</h2>
          <p class="text-[10px] text-slate-500 uppercase tracking-widest font-medium">EduNexus Multi-Agent Planner</p>
        </div>
      </div>
      
      <!-- 重新规划输入区 -->
      <div class="flex items-center gap-2 bg-[#161616] p-1 rounded-xl border border-white/5 w-[450px]">
        <div class="flex-1 flex items-center px-3 gap-2">
          <Search class="h-4 w-4 text-slate-500" />
          <input 
            v-model="customGoal"
            placeholder="输入你想学习的目标 (例如: 卷积神经网络原理)"
            class="bg-transparent border-none outline-none text-xs w-full text-slate-300 placeholder:text-slate-600 h-8"
            @keyup.enter="handlePlan"
          />
        </div>
        <Button 
          variant="default" 
          size="sm" 
          class="bg-blue-600 hover:bg-blue-500 text-white text-xs h-8 px-4 rounded-lg transition-all active:scale-95"
          @click="handlePlan"
          :disabled="isPlanning"
        >
          <RefreshCw v-if="isPlanning" class="h-3 w-3 mr-2 animate-spin" />
          <Sparkles v-else class="h-3 w-3 mr-2" />
          重新规划
        </Button>
      </div>
    </header>

    <main class="flex-1 flex overflow-hidden">
      <!-- 左侧：知识图谱 (SVG Graph) -->
      <section class="flex-1 relative border-r border-white/5 bg-dot-pattern overflow-hidden">
        <!-- 加载遮罩 -->
        <div v-if="isPlanning" class="absolute inset-0 z-10 bg-black/40 backdrop-blur-sm flex flex-col items-center justify-center">
          <div class="relative">
             <div class="w-16 h-16 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin"></div>
             <Sparkles class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-6 w-6 text-blue-400 animate-pulse" />
          </div>
          <p class="mt-4 text-sm font-medium text-blue-400 tracking-tighter">PLANNER AGENT IS THINKING...</p>
        </div>

        <!-- 三阶段流程图 -->
        <PhaseGraph
          :nodes="learningStore.nodes"
          :edges="learningStore.edges"
        />
      </section>

      <!-- 右侧：全流程大阶段展示 (Roadmap) -->
      <aside class="w-[380px] flex flex-col bg-[#0d0d0d] shadow-[-10px_0_30px_rgba(0,0,0,0.5)] z-20">
        <div class="p-6 border-b border-white/5 bg-[#0f0f0f]">
          <div class="flex items-center justify-between mb-1">
            <span class="text-[10px] font-black text-slate-500 uppercase tracking-widest">Mastery Roadmap</span>
            <Zap class="h-4 w-4 text-amber-500 fill-amber-500/20" />
          </div>
          <h3 class="text-lg font-bold text-slate-100 line-clamp-1">{{ customGoal }}</h3>
          <div class="mt-4 h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
             <div class="h-full bg-blue-600 w-1/3 transition-all duration-1000 shadow-[0_0_10px_rgba(37,99,235,0.5)]"></div>
          </div>
          <p class="text-[10px] text-slate-500 mt-2 font-medium">当前总进度: 32% (预计还需 4.5 小时)</p>
        </div>

        <div class="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-3">
          <!-- 阶段卡片列表 -->
          <div 
            v-for="(phase, index) in phases" 
            :key="phase.id"
            @click="selectPhase(phase.id)"
            :class="[
              'group relative p-4 rounded-2xl border transition-all cursor-pointer overflow-hidden',
              activePhaseId === phase.id ? 'bg-blue-600/10 border-blue-500/40 ring-1 ring-blue-500/20' : 'bg-[#141414] border-white/5 hover:border-white/20'
            ]"
          >
            <!-- 状态图标 -->
            <div class="absolute top-4 right-4">
               <CheckCircle2 v-if="phase.status === 'completed'" class="h-4 w-4 text-green-500" />
               <PlayCircle v-else-if="phase.status === 'current'" class="h-4 w-4 text-blue-400 animate-pulse" />
               <div v-else class="h-4 w-4 rounded-full border-2 border-slate-600" />
            </div>

            <div class="flex items-center gap-3 mb-2">
              <span :class="[
                'text-[10px] font-bold px-1.5 py-0.5 rounded',
                activePhaseId === phase.id ? 'bg-blue-600 text-white' : 'bg-white/5 text-slate-500'
              ]">STEP {{ index + 1 }}</span>
              <span v-if="hasInjectedNodes(phase.nodes)" class="text-[9px] bg-amber-500/20 text-amber-500 px-1.5 rounded font-black tracking-tighter">AI INJECTED</span>
            </div>

            <h4 :class="['text-xs font-bold mb-1 transition-colors', activePhaseId === phase.id ? 'text-blue-300' : 'text-slate-300']">
              {{ phase.title }}
            </h4>
            <p class="text-[10px] text-slate-500 leading-normal">{{ phase.description }}</p>

            <!-- 装饰线 (左侧激活条) -->
            <div v-if="activePhaseId === phase.id" class="absolute left-0 top-0 bottom-0 w-1 bg-blue-500"></div>
          </div>
        </div>

        <div class="p-4 bg-[#0a0a0a] border-t border-white/5">
          <Button class="w-full bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10 text-xs py-5 rounded-xl">
             查看完整诊断报告
          </Button>
        </div>
      </aside>
    </main>
  </div>
</template>

<style scoped>
.bg-dot-pattern {
  background-image: radial-gradient(circle, #252525 1px, transparent 1px);
  background-size: 40px 40px;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #1a1a1a;
  border-radius: 10px;
}

/* 动画效果 */
.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.fade-slide-enter-from, .fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px) scale(0.95);
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>