<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { 
  Network, 
  Sparkles, 
  Zap, 
  ChevronRight,
  Info
} from 'lucide-vue-next'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import PathPlanner from './components/PathPlanner.vue'
import ResourceStream from './components/ResourceStream.vue'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

const currentStage = ref('optimizing') // optimizing, ready
const showInjectedNode = ref(false)

// 模拟 Planner Agent 的决策过程
const runPlanner = () => {
  currentStage.value = 'optimizing'
  setTimeout(() => {
    showInjectedNode.value = true
    currentStage.value = 'ready'
  }, 2000)
}

onMounted(() => {
  runPlanner()
})
</script>

<template>
  <div class="flex flex-col h-full bg-[#0b0b0b] overflow-hidden">
    <!-- 顶部状态栏：规划智能体提示 -->
    <div class="p-4 border-b border-white/5 bg-[#0f0f0f]/50 backdrop-blur-md flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="p-2 bg-blue-500/20 rounded-lg">
          <Network class="h-5 w-5 text-blue-400" />
        </div>
        <div>
          <h2 class="text-sm font-semibold text-slate-200">学习路径规划中枢</h2>
          <p class="text-[11px] text-slate-500 uppercase tracking-tighter">Current Goal: Transformer Architecture</p>
        </div>
      </div>
      
      <div class="flex items-center gap-3">
         <div v-if="currentStage === 'optimizing'" class="flex items-center gap-2 text-xs text-amber-400 animate-pulse">
            <Sparkles class="h-3 w-3" />
            Planner Agent 正在分析学生画像...
         </div>
         <Button variant="outline" size="sm" class="border-white/10 hover:bg-white/5 text-xs h-8" @click="runPlanner">
           重新规划
         </Button>
      </div>
    </div>

    <div class="flex-1 flex overflow-hidden">
      <!-- 左侧：DAG 知识图谱预览 -->
      <section class="flex-[1.5] relative border-r border-white/5 bg-dot-pattern">
        <div class="absolute top-4 left-4 z-10">
          <Alert class="bg-black/60 border-blue-500/30 backdrop-blur-md w-64">
            <Info class="h-4 w-4 text-blue-400" />
            <AlertTitle class="text-xs text-blue-400 font-bold">画像分析</AlertTitle>
            <AlertDescription class="text-[11px] text-slate-400">
              检测到“线性代数”掌握度较低（0.42），已动态插入补全节点。
            </AlertDescription>
          </Alert>
        </div>
        <KnowledgeGraph :highlight-injected="showInjectedNode" />
      </section>

      <!-- 右侧：资源推送流 -->
      <aside class="flex-1 flex flex-col bg-[#0f0f0f]">
        <div class="p-4 border-b border-white/5 flex items-center justify-between">
          <span class="text-xs font-bold text-slate-500 uppercase">精准推送流</span>
          <Zap class="h-3 w-3 text-amber-500" />
        </div>
        <div class="flex-1 overflow-y-auto custom-scrollbar">
          <ResourceStream />
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.bg-dot-pattern {
  background-image: radial-gradient(circle, #333 1px, transparent 1px);
  background-size: 30px 30px;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #222;
  border-radius: 10px;
}
</style>