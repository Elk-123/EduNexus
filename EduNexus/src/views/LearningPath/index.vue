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
  Lock,
  PlayCircle
} from 'lucide-vue-next'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

// --- 数据结构定义 ---
interface Node {
  id: string;
  label: string;
  type: 'standard' | 'injected';
  status: 'completed' | 'active' | 'pending';
}

interface LearningPhase {
  id: string;
  title: string;
  description: string;
  status: 'completed' | 'current' | 'locked';
  nodes: Node[]; // 该阶段对应的图谱节点
}

// --- 状态管理 ---
const customGoal = ref('Transformer Architecture')
const isPlanning = ref(false)
const showAnalysis = ref(true)
const activePhaseId = ref('p2') // 默认选中第二阶段

// 模拟全流程数据：大课题的所有阶段
const phases = ref<LearningPhase[]>([
  {
    id: 'p1',
    title: '线性代数与微积分准备',
    description: 'Transformer 基础数学门槛补齐',
    status: 'completed',
    nodes: [
      { id: 'math-1', label: '张量运算', type: 'standard', status: 'completed' },
      { id: 'math-2', label: '偏导数链式法则', type: 'standard', status: 'completed' }
    ]
  },
  {
    id: 'p2',
    title: '矩阵运算强化 (AI 注入)',
    description: '针对画像弱点生成的专项强化',
    status: 'current',
    nodes: [
      { id: 'math-base', label: '线性代数基础', type: 'standard', status: 'completed' },
      { id: 'matrix-boost', label: '矩阵运算强化', type: 'injected', status: 'active' },
      { id: 'transformer-entry', label: '初步特征提取', type: 'standard', status: 'pending' }
    ]
  },
  {
    id: 'p3',
    title: 'Transformer 核心架构',
    description: '多头注意力与位置编码实现',
    status: 'locked',
    nodes: [
      { id: 'attn', label: 'Self-Attention', type: 'standard', status: 'pending' },
      { id: 'mha', label: 'Multi-Head Attention', type: 'standard', status: 'pending' },
      { id: 'pos', label: 'Positional Encoding', type: 'standard', status: 'pending' }
    ]
  },
  {
    id: 'p4',
    title: '模型训练与微调',
    description: '损失函数选择与优化器配置',
    status: 'locked',
    nodes: [
      { id: 'train', label: '训练循环', type: 'standard', status: 'pending' },
      { id: 'finetune', label: '下游任务微调', type: 'standard', status: 'pending' }
    ]
  }
])

// 计算属性：当前左侧展示的图谱数据
const currentGraphNodes = computed(() => {
  return phases.value.find(p => p.id === activePhaseId.value)?.nodes || []
})

// --- 交互逻辑 ---

// 1. 模拟 AI 规划过程
const handlePlan = () => {
  if (!customGoal.value) return
  isPlanning.value = true
  showAnalysis.value = false // 重置分析弹窗
  
  setTimeout(() => {
    // 模拟根据输入改变数据逻辑
    console.log("Planning for:", customGoal.value)
    isPlanning.value = false
    showAnalysis.value = true
    activePhaseId.value = 'p2' // 重置到建议节点
  }, 2000)
}

// 2. 关闭画像分析弹窗
const closeAnalysis = () => {
  showAnalysis.value = false
}

// 3. 切换阶段
const selectPhase = (phaseId: string) => {
  if (phases.value.find(p => p.id === phaseId)?.status === 'locked') return
  activePhaseId.value = phaseId
}

onMounted(() => {
  // 初始加载动画
  handlePlan()
})
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
      <!-- 左侧：局部知识图谱 (SVG Graph) -->
      <section class="flex-1 relative border-r border-white/5 bg-dot-pattern overflow-hidden">
        <!-- AI 诊断浮窗 (可关闭) -->
        <transition name="fade-slide">
          <div v-if="showAnalysis" class="absolute top-6 left-6 z-20">
            <div class="group relative bg-[#0f0f0f]/90 border border-blue-500/40 backdrop-blur-xl w-80 p-4 rounded-2xl shadow-2xl">
              <button 
                @click="closeAnalysis"
                class="absolute top-2 right-2 p-1 rounded-full hover:bg-white/10 transition-colors"
              >
                <X class="h-3 w-3 text-slate-500" />
              </button>
              
              <div class="flex items-start gap-3">
                <div class="p-2 bg-blue-500/10 rounded-lg">
                  <Info class="h-4 w-4 text-blue-400" />
                </div>
                <div>
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-bold text-blue-400">画像分析报告</span>
                    <span class="text-[9px] bg-blue-500/20 px-1 rounded text-blue-300 uppercase">Analysis</span>
                  </div>
                  <p class="text-[11px] text-slate-300 mt-2 leading-relaxed">
                    发现您在 <span class="text-blue-300 font-bold italic">线性代数</span> 维度的掌握度仅为 0.42。
                    系统已在当前阶段自动插入了 <span class="text-amber-400">矩阵运算强化</span> 模块，确保后续 Transformer 学习顺利。
                  </p>
                </div>
              </div>
            </div>
          </div>
        </transition>

        <!-- 加载遮罩 -->
        <div v-if="isPlanning" class="absolute inset-0 z-10 bg-black/40 backdrop-blur-sm flex flex-col items-center justify-center">
          <div class="relative">
             <div class="w-16 h-16 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin"></div>
             <Sparkles class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-6 w-6 text-blue-400 animate-pulse" />
          </div>
          <p class="mt-4 text-sm font-medium text-blue-400 tracking-tighter">PLANNER AGENT IS THINKING...</p>
        </div>

        <!-- 图谱组件 -->
        <KnowledgeGraph 
          :nodes="currentGraphNodes" 
          :active-id="activePhaseId" 
        />
        
        <!-- 图例 -->
        <div class="absolute bottom-6 left-6 flex items-center gap-6 bg-black/40 px-4 py-2 rounded-full border border-white/5 backdrop-blur-md">
          <div class="flex items-center gap-2 text-[10px] text-slate-400 font-bold uppercase tracking-wider">
            <div class="w-2 h-2 rounded-full bg-blue-500"></div> 基础路径
          </div>
          <div class="flex items-center gap-2 text-[10px] text-slate-400 font-bold uppercase tracking-wider">
            <div class="w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.4)]"></div> AI 建议强化
          </div>
        </div>
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
              activePhaseId === phase.id ? 'bg-blue-600/10 border-blue-500/40 ring-1 ring-blue-500/20' : 'bg-[#141414] border-white/5 hover:border-white/20',
              phase.status === 'locked' ? 'opacity-40 grayscale pointer-events-none' : ''
            ]"
          >
            <!-- 状态图标 -->
            <div class="absolute top-4 right-4">
               <CheckCircle2 v-if="phase.status === 'completed'" class="h-4 w-4 text-green-500" />
               <PlayCircle v-else-if="phase.status === 'current'" class="h-4 w-4 text-blue-400 animate-pulse" />
               <Lock v-else class="h-4 w-4 text-slate-600" />
            </div>

            <div class="flex items-center gap-3 mb-2">
              <span :class="[
                'text-[10px] font-bold px-1.5 py-0.5 rounded',
                activePhaseId === phase.id ? 'bg-blue-600 text-white' : 'bg-white/5 text-slate-500'
              ]">STEP {{ index + 1 }}</span>
              <span v-if="phase.id === 'p2'" class="text-[9px] bg-amber-500/20 text-amber-500 px-1.5 rounded font-black tracking-tighter">AI INJECTED</span>
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