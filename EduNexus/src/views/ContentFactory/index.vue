<!-- src/views/ContentFactory/index.vue -->
<script setup lang="ts">
import { ref, reactive } from 'vue'
import { 
  BrainCircuit, FileText, GitFork, ClipboardCheck, Video, Code2, ShieldCheck 
} from 'lucide-vue-next'
import TopicInput from './components/TopicInput.vue'
import AgentTerminal from './components/AgentTerminal.vue'
import ResourceDisplay from './components/ResourceDisplay.vue'
import AgentStatusCard from './components/AgentStatusCard.vue'
import AgentDetailView from './components/AgentDetailView.vue'
import { Badge } from '@/components/ui/badge'

// 1. 状态定义
const isGenerating = ref(false)
const currentTopic = ref('')
const logs = ref<any[]>([])
const selectedAgent = ref<any>(null) // 控制深度对话弹窗

const agents = reactive([
  { id: 'manager', name: '主控中枢', role: 'Manager', status: 'idle', icon: BrainCircuit, color: 'text-purple-400' },
  { id: 'professor', name: '教授智能体', role: 'Professor', status: 'idle', icon: FileText, color: 'text-blue-400' },
  { id: 'architect', name: '架构师智能体', role: 'Architect', status: 'idle', icon: GitFork, color: 'text-orange-400' },
  { id: 'examiner', name: '考官智能体', role: 'Examiner', status: 'idle', icon: ClipboardCheck, color: 'text-pink-400' },
  { id: 'director', name: '导演智能体', role: 'Director', status: 'idle', icon: Video, color: 'text-cyan-400' },
  { id: 'hacker', name: '极客智能体', role: 'Hacker', status: 'idle', icon: Code2, color: 'text-green-400' },
  { id: 'reviewer', name: '质量审查', role: 'Reviewer', status: 'idle', icon: ShieldCheck, color: 'text-red-400' },
])

const addLog = (agent: string, message: string, type: 'info' | 'success' | 'warn' = 'info') => {
  logs.value.push({ id: Date.now() + Math.random(), agent, message, type })
}

// 2. 模拟多智能体流水线逻辑
const runWorkflow = async (topic: string) => {
  isGenerating.value = true
  currentTopic.value = topic
  logs.value = []
  agents.forEach(a => a.status = 'idle')

  // --- Step 1: Manager 分析 ---
  agents[0].status = 'running'
  addLog('Manager', `收到主题: "${topic}"，正在进行语义拆解...`, 'info')
  await new Promise(r => setTimeout(r, 1200))
  addLog('Manager', `拆解成功。已调度 5 名专家智能体并行生成资源。`, 'success')
  agents[0].status = 'success'

  // --- Step 2: Parallel Generation (并行模拟) ---
  const experts = agents.slice(1, 6)
  const taskPromises = experts.map(async (agent, index) => {
    agent.status = 'running'
    addLog(agent.role, `正在分析相关知识点...`, 'info')
    await new Promise(r => setTimeout(r, 1500 + index * 800))
    addLog(agent.role, `初步草案生成完成。`, 'success')
    agent.status = 'success'
  })

  await Promise.all(taskPromises)

  // --- Step 3: Reviewer 审核 ---
  agents[6].status = 'running'
  addLog('Reviewer', `正在检查幻觉并校准难度...`, 'info')
  await new Promise(r => setTimeout(r, 1500))
  addLog('Reviewer', `全量资源审核通过。`, 'success')
  agents[6].status = 'success'

  isGenerating.value = false
}

// 3. 点击智能体卡片进入详情
const handleAgentClick = (agent: any) => {
  if (agent.status === 'success') {
    selectedAgent.value = agent
  }
}
</script>

<template>
  <div class="flex flex-col h-full bg-[#0b0b0b] text-slate-200 overflow-hidden relative">
    <!-- 顶部输入 -->
    <header class="border-b border-white/5 py-10 px-6 bg-gradient-to-b from-blue-900/5 to-transparent">
      <TopicInput :isGenerating="isGenerating" @start="runWorkflow" />
    </header>

    <main class="flex-1 flex overflow-hidden p-6 gap-6">
      <!-- 左侧：工作台控制面板 -->
      <aside class="w-80 flex flex-col gap-6">
        <div class="bg-[#141414] border border-white/5 rounded-3xl p-5 flex-1 flex flex-col shadow-2xl relative overflow-hidden">
          <h3 class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-5 flex items-center gap-2 px-1">
            <span class="h-1.5 w-1.5 rounded-full bg-blue-500 animate-pulse"></span>
            专家集群状态
          </h3>
          
          <!-- 智能体列表 -->
          <div class="space-y-3 overflow-y-auto pr-1 custom-scrollbar">
            <AgentStatusCard 
              v-for="agent in agents" 
              :key="agent.id" 
              :agent="agent" 
              @click="handleAgentClick(agent)"
              :class="[
                agent.status === 'success' ? 'cursor-pointer hover:translate-x-1 active:scale-95 transition-all' : ''
              ]"
            />
          </div>

          <!-- 底部提示 -->
          <div v-if="!isGenerating && currentTopic" class="mt-4 p-3 bg-blue-500/5 rounded-xl border border-blue-500/10">
            <p class="text-[10px] text-blue-400/80 leading-relaxed">
              💡 点击带有 <span class="font-bold">READY/DONE</span> 标记的专家，可进入深度研讨室进行 1-on-1 对话。
            </p>
          </div>
        </div>

        <!-- 终端日志 -->
        <div class="h-60">
           <AgentTerminal :logs="logs" />
        </div>
      </aside>

      <!-- 右侧：主展示区 -->
      <section class="flex-1 min-w-0">
        <ResourceDisplay 
          :isGenerating="isGenerating" 
          :topic="currentTopic" 
        />
      </section>
    </main>

    <!-- 深度对话研讨室 (Overlay) -->
    <Transition
      enter-active-class="transition duration-500 ease-out"
      enter-from-class="opacity-0 translate-y-10 scale-95"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="transition duration-300 ease-in"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 translate-y-10 scale-95"
    >
      <AgentDetailView 
        v-if="selectedAgent" 
        :agent="selectedAgent" 
        :topic="currentTopic"
        @close="selectedAgent = null"
      />
    </Transition>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #222; border-radius: 10px; }
</style>